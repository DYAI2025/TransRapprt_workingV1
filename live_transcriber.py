
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
TransRapport MVP - Live-Transkriptions-Engine
Echtzeit-Spracherkennung mit faster-whisper für offline Deutsch/Englisch
"""

import threading
import queue
import time
import numpy as np
from typing import Optional, Callable
from faster_whisper import WhisperModel
import io
import wave
from PyQt6.QtCore import QObject, pyqtSignal
from marker_system import MarkerSystem

class LiveTranscriber(QObject):
    """Live-Transkriptions-Engine mit faster-whisper"""
    
    # Qt-Signale für GUI-Updates
    transcription_ready = pyqtSignal(str)  # Finaler Text
    partial_transcription = pyqtSignal(str)  # Partieller Text
    error_occurred = pyqtSignal(str)  # Fehlermeldungen
    
    # Marker-System Signale
    markers_updated = pyqtSignal(dict)  # Neue Marker-Daten
    emotion_detected = pyqtSignal(str, float)  # Emotion, Confidence
    pause_detected = pyqtSignal(float)  # Pause-Dauer
    prosody_updated = pyqtSignal(dict)  # Prosodische Features
    
    def __init__(self, language: str = "de", model_size: str = "base"):
        super().__init__()
        self.language = language
        self.model_size = model_size
        self.model = None
        self.is_transcribing = False
        self.transcription_thread = None
        self.audio_queue = queue.Queue()
        self.sample_rate = 16000
        self.chunk_duration = 3.0  # Sekunden pro Chunk
        self.chunk_size = int(self.sample_rate * self.chunk_duration)
        self.audio_buffer = []
        
        # Marker-System initialisieren
        self.marker_system = MarkerSystem(sample_rate=self.sample_rate)
        self._setup_marker_signals()
        
        # Modell initialisieren
        self.init_model()
    
    def _setup_marker_signals(self):
        """Marker-System Signale mit LiveTranscriber verbinden"""
        self.marker_system.markers_updated.connect(self.markers_updated.emit)
        self.marker_system.emotion_detected.connect(self.emotion_detected.emit)
        self.marker_system.pause_detected.connect(self.pause_detected.emit)
        self.marker_system.prosody_updated.connect(self.prosody_updated.emit)
    
    def init_model(self):
        """Whisper-Modell initialisieren"""
        try:
            print(f"Lade Whisper-Modell '{self.model_size}' für Sprache '{self.language}'...")
            
            # CPU-optimierte Konfiguration für offline Betrieb
            self.model = WhisperModel(
                self.model_size,
                device="cpu",
                compute_type="int8",  # Optimiert für CPU
                download_root="./models"  # Lokaler Modell-Cache
            )
            
            print(f"Whisper-Modell '{self.model_size}' erfolgreich geladen")
            return True
            
        except Exception as e:
            error_msg = f"Fehler beim Laden des Whisper-Modells: {e}"
            print(error_msg)
            self.error_occurred.emit(error_msg)
            return False
    
    def is_model_available(self) -> bool:
        """Prüfen ob Modell verfügbar ist"""
        return self.model is not None
    
    def start_transcription(self, audio_manager):
        """Live-Transkription starten"""
        if not self.is_model_available():
            error_msg = "Kein Whisper-Modell verfügbar"
            print(error_msg)
            self.error_occurred.emit(error_msg)
            return False
        
        if self.is_transcribing:
            return True
        
        self.audio_manager = audio_manager
        self.is_transcribing = True
        self.audio_buffer = []
        
        # Marker-System starten
        self.marker_system.start()
        
        # Transkriptions-Thread starten
        self.transcription_thread = threading.Thread(target=self._transcription_loop)
        self.transcription_thread.daemon = True
        self.transcription_thread.start()
        
        print("Live-Transkription gestartet")
        return True
    
    def stop_transcription(self):
        """Live-Transkription stoppen"""
        if not self.is_transcribing:
            return
        
        self.is_transcribing = False
        
        # Marker-System stoppen
        self.marker_system.stop()
        
        if self.transcription_thread:
            self.transcription_thread.join(timeout=3.0)
        
        # Queue und Buffer leeren
        while not self.audio_queue.empty():
            try:
                self.audio_queue.get_nowait()
            except queue.Empty:
                break
        
        self.audio_buffer = []
        print("Live-Transkription gestoppt")
    
    def _transcription_loop(self):
        """Hauptschleife für Live-Transkription - MIT DEBUG"""
        print("🚀 Live-Transkriptions-Loop gestartet")
        
        while self.is_transcribing:
            try:
                # Audio-Daten vom AudioManager abrufen
                audio_data = self.audio_manager.get_audio_data(timeout=0.1)
                
                if audio_data is not None:
                    print(f"📊 Audio empfangen: {len(audio_data)} samples, RMS: {np.sqrt(np.mean(audio_data**2)):.4f}")
                    
                    # Audio-Daten zum Buffer hinzufügen
                    self.audio_buffer.extend(audio_data.flatten())
                    
                    # Audio-Daten an Marker-System weiterleiten
                    try:
                        markers = self.marker_system.process_audio_chunk(audio_data.flatten())
                        print(f"🎯 Marker: {markers['affect']['emotion']}, Pitch: {markers['prosody']['pitch_mean']:.1f}Hz")
                    except Exception as marker_error:
                        print(f"❌ Marker-Fehler: {marker_error}")
                    
                    # Wenn genug Daten für einen Chunk vorhanden sind
                    if len(self.audio_buffer) >= self.chunk_size:
                        print(f"🎤 Transkribiere Chunk: {len(self.audio_buffer)} → {self.chunk_size} samples")
                        # Chunk extrahieren
                        chunk = np.array(self.audio_buffer[:self.chunk_size], dtype=np.float32)
                        self.audio_buffer = self.audio_buffer[self.chunk_size//2:]  # 50% Überlappung
                        
                        # Chunk zur Transkription einreihen
                        self.audio_queue.put(chunk)
                else:
                    print("⏳ Warte auf Audio-Daten...")
                
                # Transkription verarbeiten
                self._process_transcription_queue()
                
            except queue.Empty:
                continue
            except Exception as e:
                error_msg = f"Fehler in Transkriptions-Loop: {e}"
                print(error_msg)
                self.error_occurred.emit(error_msg)
                import traceback
                traceback.print_exc()
                time.sleep(0.5)
                continue
        
        print("Live-Transkriptions-Loop beendet")
    
    def _process_transcription_queue(self):
        """Transkriptions-Queue verarbeiten"""
        try:
            # Alle verfügbaren Audio-Chunks verarbeiten
            while not self.audio_queue.empty():
                try:
                    audio_chunk = self.audio_queue.get_nowait()
                    text = self._transcribe_chunk(audio_chunk)
                    
                    if text and text.strip():
                        # Text an Marker-System weiterleiten
                        self.marker_system.process_transcript(text.strip())
                        
                        # Signal an GUI senden
                        self.transcription_ready.emit(text.strip())
                        
                except queue.Empty:
                    break
                    
        except Exception as e:
            print(f"Fehler bei Transkriptions-Verarbeitung: {e}")
    
    def _transcribe_chunk(self, audio_chunk: np.ndarray) -> Optional[str]:
        """Audio-Chunk mit Whisper transkribieren - MIT DEBUG"""
        try:
            # Audio-Normalisierung
            if np.max(np.abs(audio_chunk)) > 0:
                audio_chunk = audio_chunk / np.max(np.abs(audio_chunk))
            
            # Stille-Erkennung (Skip sehr leise Chunks)
            rms = np.sqrt(np.mean(audio_chunk**2))
            print(f"🔊 Transkription RMS: {rms:.6f}")
            
            # DEBUGGING: Bei BlackHole (RMS=0) Test-Audio generieren
            if rms < 0.000001:  # BlackHole hat RMS von exakt 0.0000
                print(f"🔧 BlackHole erkannt (RMS: {rms:.6f}), generiere Test-Audio für Transkription...")
                # Sehr schwaches Rauschen für Whisper-Test hinzufügen
                audio_chunk = np.random.normal(0, 0.001, audio_chunk.shape).astype(np.float32)
                rms = np.sqrt(np.mean(audio_chunk**2))
                print(f"🎲 Test-Audio generiert (RMS: {rms:.6f})")
            elif rms < 0.001:  # Normaler Schwellenwert für echte Mikrofone
                print(f"❌ Audio zu leise (RMS: {rms:.6f} < 0.001), überspringe Transkription")
                return None
            
            print(f"✅ Audio verarbeitung (RMS: {rms:.6f}), starte Transkription...")
            
            # Whisper-Transkription
            segments, info = self.model.transcribe(
                audio_chunk,
                language=self.language,
                beam_size=1,  # Schneller für Live-Transkription
                best_of=1,
                temperature=0.0,
                condition_on_previous_text=False,
                vad_filter=True,  # Voice Activity Detection
                vad_parameters=dict(min_silence_duration_ms=500)
            )
            
            # Text aus Segmenten extrahieren
            text_parts = []
            for segment in segments:
                if segment.text.strip():
                    text_parts.append(segment.text.strip())
            
            result_text = " ".join(text_parts) if text_parts else None
            
            if result_text:
                print(f"📝 Transkription erfolgreich: '{result_text}'")
            else:
                print(f"🔇 Keine Transkription gefunden (Segmente: {len(list(segments))})")
            
            return result_text
            
        except Exception as e:
            print(f"Fehler bei Chunk-Transkription: {e}")
            return None
    
    def change_language(self, language: str) -> bool:
        """Sprache wechseln"""
        if language not in ["de", "en", "auto"]:
            print(f"Sprache '{language}' wird nicht unterstützt")
            return False
        
        # Transkription stoppen falls aktiv
        was_transcribing = self.is_transcribing
        audio_manager = getattr(self, 'audio_manager', None)
        
        if was_transcribing:
            self.stop_transcription()
        
        # Sprache ändern
        self.language = language
        
        # Transkription wieder starten falls sie vorher lief
        if was_transcribing and audio_manager:
            return self.start_transcription(audio_manager)
        
        return True
    
    def change_model_size(self, model_size: str) -> bool:
        """Modell-Größe wechseln"""
        valid_sizes = ["tiny", "base", "small", "medium", "large"]
        if model_size not in valid_sizes:
            print(f"Modell-Größe '{model_size}' ungültig. Verfügbar: {valid_sizes}")
            return False
        
        # Transkription stoppen falls aktiv
        was_transcribing = self.is_transcribing
        audio_manager = getattr(self, 'audio_manager', None)
        
        if was_transcribing:
            self.stop_transcription()
        
        # Modell-Größe ändern und neu laden
        self.model_size = model_size
        success = self.init_model()
        
        # Transkription wieder starten falls sie vorher lief
        if was_transcribing and audio_manager and success:
            return self.start_transcription(audio_manager)
        
        return success
    
    def get_supported_languages(self) -> list:
        """Unterstützte Sprachen auflisten"""
        return ["de", "en", "auto"]
    
    def get_model_info(self) -> dict:
        """Informationen über verfügbare Modelle"""
        return {
            "tiny": {"size": "~39 MB", "speed": "Sehr schnell", "quality": "Niedrig"},
            "base": {"size": "~74 MB", "speed": "Schnell", "quality": "Gut"},
            "small": {"size": "~244 MB", "speed": "Mittel", "quality": "Besser"},
            "medium": {"size": "~769 MB", "speed": "Langsam", "quality": "Sehr gut"},
            "large": {"size": "~1550 MB", "speed": "Sehr langsam", "quality": "Beste"}
        }
