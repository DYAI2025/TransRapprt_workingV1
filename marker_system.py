
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
TransRapport MVP - Vereinfachtes Marker-System (ATO→SEM)
Therapeutisch relevante Standard-Marker für Emotionserkennung und Sprechpausen
"""

import numpy as np
import librosa
import webrtcvad
import threading
import queue
from typing import Dict, List, Optional, Tuple
from datetime import datetime, timedelta
from PyQt6.QtCore import QObject, pyqtSignal
import warnings
warnings.filterwarnings("ignore", category=UserWarning)

class MarkerSystem(QObject):
    """
    Vereinfachtes Marker-System für therapeutische Analyse
    ATO → SEM: Affect (Emotion), Tempo (Pausen), Other prosody (Pitch/Energy)
    """
    
    # Qt-Signale für Live-Visualisierung
    markers_updated = pyqtSignal(dict)  # Neue Marker-Daten
    emotion_detected = pyqtSignal(str, float)  # Emotion, Confidence
    pause_detected = pyqtSignal(float)  # Pause-Dauer in Sekunden
    prosody_updated = pyqtSignal(dict)  # Prosodische Features
    
    def __init__(self, sample_rate: int = 16000):
        super().__init__()
        self.sample_rate = sample_rate
        self.is_active = False
        
        # Audio-Buffer für Analyse
        self.audio_buffer = []
        self.buffer_duration = 2.0  # Sekunden
        self.buffer_size = int(self.sample_rate * self.buffer_duration)
        
        # VAD für Pause-Erkennung
        self.vad = webrtcvad.Vad(2)  # Aggressivität 0-3 (2 = mittel)
        
        # Pause-Tracking
        self.last_speech_time = None
        self.silence_start = None
        self.min_pause_duration = 0.6  # Minimum 600ms für therapeutisch relevante Pause
        
        # Emotion-Tracking (vereinfacht)
        self.emotion_history = []
        self.emotion_window_size = 5
        
        # Prosodische Features
        self.pitch_history = []
        self.energy_history = []
        self.feature_window_size = 10
        
        # Marker-Ausgabe
        self.current_markers = {
            'timestamp': None,
            'affect': {'emotion': 'neutral', 'confidence': 0.0, 'valence': 0.0},
            'tempo': {'pause_duration': 0.0, 'speech_rate': 0.0},
            'prosody': {'pitch_mean': 0.0, 'pitch_var': 0.0, 'energy_mean': 0.0, 'energy_var': 0.0}
        }
        
        print("Marker-System initialisiert (ATO→SEM)")
    
    def start(self):
        """Marker-System aktivieren"""
        self.is_active = True
        self.last_speech_time = datetime.now()
        print("Marker-System gestartet")
    
    def stop(self):
        """Marker-System deaktivieren"""
        self.is_active = False
        self.audio_buffer = []
        self.emotion_history = []
        self.pitch_history = []
        self.energy_history = []
        print("Marker-System gestoppt")
    
    def process_audio_chunk(self, audio_data: np.ndarray, timestamp: datetime = None) -> Dict:
        """
        Audio-Chunk verarbeiten und Marker extrahieren
        
        Args:
            audio_data: Audio-Daten als numpy array (float32, mono)
            timestamp: Zeitstempel des Chunks
            
        Returns:
            Dict mit aktuellen Markern
        """
        if not self.is_active:
            return self.current_markers
        
        if timestamp is None:
            timestamp = datetime.now()
        
        # Audio-Daten zum Buffer hinzufügen
        self.audio_buffer.extend(audio_data.flatten())
        
        # Buffer-Größe begrenzen
        if len(self.audio_buffer) > self.buffer_size:
            self.audio_buffer = self.audio_buffer[-self.buffer_size:]
        
        # Genug Daten für Analyse?
        if len(self.audio_buffer) < self.sample_rate:  # Mindestens 1 Sekunde
            return self.current_markers
        
        # Audio-Daten für Analyse vorbereiten
        audio_segment = np.array(self.audio_buffer[-self.sample_rate:], dtype=np.float32)
        
        # 1. AFFECT: Emotion aus Audio-Features ableiten
        emotion_data = self._analyze_emotion(audio_segment)
        
        # 2. TEMPO: Pausen-Erkennung
        pause_data = self._analyze_pauses(audio_data, timestamp)
        
        # 3. PROSODY: Pitch und Energy Features
        prosody_data = self._analyze_prosody(audio_segment)
        
        # Marker zusammenführen
        self.current_markers = {
            'timestamp': timestamp,
            'affect': emotion_data,
            'tempo': pause_data,
            'prosody': prosody_data
        }
        
        # Signale senden
        self.markers_updated.emit(self.current_markers)
        
        return self.current_markers
    
    def process_transcript(self, text: str, timestamp: datetime = None):
        """
        Transkript verarbeiten für zusätzliche Marker-Informationen
        
        Args:
            text: Transkribierter Text
            timestamp: Zeitstempel
        """
        if not self.is_active or not text.strip():
            return
        
        if timestamp is None:
            timestamp = datetime.now()
        
        # Speech Rate schätzen (Wörter pro Minute)
        word_count = len(text.split())
        if word_count > 0:
            # Geschätzte Sprechzeit basierend auf durchschnittlicher Sprechgeschwindigkeit
            estimated_duration = word_count / 2.5  # ~150 WPM = 2.5 WPS
            speech_rate = word_count / (estimated_duration / 60) if estimated_duration > 0 else 0
            
            # Tempo-Daten aktualisieren
            if 'tempo' in self.current_markers:
                self.current_markers['tempo']['speech_rate'] = speech_rate
        
        # Speech detected - Reset pause tracking
        self.last_speech_time = timestamp
        if self.silence_start is not None:
            self.silence_start = None
    
    def _analyze_emotion(self, audio_segment: np.ndarray) -> Dict:
        """
        Vereinfachte Emotionserkennung basierend auf Audio-Features
        
        Returns:
            Dict mit Emotion, Confidence und Valence
        """
        try:
            # Grundlegende Audio-Features extrahieren
            rms = np.sqrt(np.mean(audio_segment**2))
            zcr = np.mean(librosa.feature.zero_crossing_rate(audio_segment)[0])
            
            # Spectral Features
            stft = librosa.stft(audio_segment, n_fft=512, hop_length=256)
            spectral_centroids = librosa.feature.spectral_centroid(S=np.abs(stft))[0]
            spectral_rolloff = librosa.feature.spectral_rolloff(S=np.abs(stft))[0]
            
            # Vereinfachte Emotionsklassifikation basierend auf Features
            emotion, confidence, valence = self._classify_emotion_simple(
                rms, zcr, np.mean(spectral_centroids), np.mean(spectral_rolloff)
            )
            
            # Emotion History für Glättung
            self.emotion_history.append((emotion, confidence))
            if len(self.emotion_history) > self.emotion_window_size:
                self.emotion_history.pop(0)
            
            # Geglättete Emotion
            smoothed_emotion = self._smooth_emotion()
            
            emotion_data = {
                'emotion': smoothed_emotion['emotion'],
                'confidence': smoothed_emotion['confidence'],
                'valence': valence
            }
            
            # Signal senden
            self.emotion_detected.emit(emotion_data['emotion'], emotion_data['confidence'])
            
            return emotion_data
            
        except Exception as e:
            print(f"Fehler bei Emotionsanalyse: {e}")
            return {'emotion': 'neutral', 'confidence': 0.0, 'valence': 0.0}
    
    def _classify_emotion_simple(self, rms: float, zcr: float, spectral_centroid: float, spectral_rolloff: float) -> Tuple[str, float, float]:
        """
        Vereinfachte Emotionsklassifikation für therapeutische Zwecke
        
        Returns:
            (emotion, confidence, valence)
        """
        # Normalisierte Features
        energy_level = min(rms * 100, 1.0)  # 0-1
        activity_level = min(zcr * 10, 1.0)  # 0-1
        brightness = min(spectral_centroid / 4000, 1.0)  # 0-1
        
        # Therapeutisch relevante Emotionskategorien - KALIBRIERT
        if energy_level > 0.85 and activity_level > 0.8:
            if brightness > 0.7:
                emotion = 'excited'  # Aufgeregt/Aktiviert
                valence = 0.8
            else:
                emotion = 'angry'    # Ärgerlich/Aggressiv - höhere Schwelle
                valence = -0.6
        elif energy_level < 0.3:
            if activity_level < 0.3:
                emotion = 'sad'      # Traurig/Niedergeschlagen
                valence = -0.7
            else:
                emotion = 'calm'     # Ruhig/Entspannt
                valence = 0.3
        elif brightness > 0.7 and energy_level > 0.4:
            emotion = 'happy'        # Fröhlich/Positiv
            valence = 0.9
        elif activity_level > 0.7:
            emotion = 'anxious'      # Ängstlich/Nervös
            valence = -0.4
        else:
            emotion = 'neutral'      # Neutral
            valence = 0.0
        
        # Confidence basierend auf Feature-Klarheit
        confidence = min((energy_level + activity_level + brightness) / 3 * 1.5, 1.0)
        
        return emotion, confidence, valence
    
    def _smooth_emotion(self) -> Dict:
        """Emotion über Zeit glätten"""
        if not self.emotion_history:
            return {'emotion': 'neutral', 'confidence': 0.0}
        
        # Häufigste Emotion in letzten N Frames
        emotions = [e[0] for e in self.emotion_history]
        confidences = [e[1] for e in self.emotion_history]
        
        # Gewichteter Durchschnitt (neuere Frames haben mehr Gewicht)
        weights = np.linspace(0.5, 1.0, len(emotions))
        
        emotion_counts = {}
        for i, emotion in enumerate(emotions):
            if emotion not in emotion_counts:
                emotion_counts[emotion] = 0
            emotion_counts[emotion] += weights[i] * confidences[i]
        
        # Emotion mit höchstem gewichteten Score
        best_emotion = max(emotion_counts.items(), key=lambda x: x[1])
        
        return {
            'emotion': best_emotion[0],
            'confidence': min(best_emotion[1] / len(emotions), 1.0)
        }
    
    def _analyze_pauses(self, audio_data: np.ndarray, timestamp: datetime) -> Dict:
        """
        Pausen-Analyse mit WebRTC VAD
        
        Returns:
            Dict mit Pause-Informationen
        """
        try:
            # Audio für VAD vorbereiten (16kHz, 16-bit PCM)
            audio_int16 = (audio_data * 32767).astype(np.int16)
            
            # VAD auf 30ms Frames anwenden
            frame_duration = 30  # ms
            frame_size = int(self.sample_rate * frame_duration / 1000)
            
            speech_detected = False
            
            # Frames analysieren
            for i in range(0, len(audio_int16) - frame_size, frame_size):
                frame = audio_int16[i:i + frame_size].tobytes()
                
                if len(frame) == frame_size * 2:  # 16-bit = 2 bytes per sample
                    if self.vad.is_speech(frame, self.sample_rate):
                        speech_detected = True
                        break
            
            current_pause_duration = 0.0
            
            if speech_detected:
                # Sprache erkannt - Pause beenden
                if self.silence_start is not None:
                    pause_duration = (timestamp - self.silence_start).total_seconds()
                    if pause_duration >= self.min_pause_duration:
                        current_pause_duration = pause_duration
                        self.pause_detected.emit(pause_duration)
                    self.silence_start = None
                
                self.last_speech_time = timestamp
                
            else:
                # Keine Sprache - Pause beginnen/fortsetzen
                if self.silence_start is None:
                    self.silence_start = timestamp
                elif self.last_speech_time is not None:
                    current_pause_duration = (timestamp - self.silence_start).total_seconds()
            
            return {
                'pause_duration': current_pause_duration,
                'speech_rate': self.current_markers.get('tempo', {}).get('speech_rate', 0.0)
            }
            
        except Exception as e:
            print(f"Fehler bei Pausen-Analyse: {e}")
            return {'pause_duration': 0.0, 'speech_rate': 0.0}
    
    def _analyze_prosody(self, audio_segment: np.ndarray) -> Dict:
        """
        Prosodische Features: Pitch und Energy
        
        Returns:
            Dict mit prosodischen Features
        """
        try:
            # Pitch-Extraktion mit librosa
            pitches, magnitudes = librosa.piptrack(
                y=audio_segment, 
                sr=self.sample_rate,
                threshold=0.1,
                fmin=80,   # Minimum F0 für Sprache
                fmax=400   # Maximum F0 für Sprache
            )
            
            # Pitch-Werte extrahieren
            pitch_values = []
            for t in range(pitches.shape[1]):
                index = magnitudes[:, t].argmax()
                pitch = pitches[index, t]
                if pitch > 0:
                    pitch_values.append(pitch)
            
            # Energy (RMS)
            rms_frames = librosa.feature.rms(y=audio_segment, frame_length=512, hop_length=256)[0]
            energy_values = rms_frames[rms_frames > 0]
            
            # Statistiken berechnen
            pitch_mean = np.mean(pitch_values) if pitch_values else 0.0
            pitch_var = np.var(pitch_values) if len(pitch_values) > 1 else 0.0
            energy_mean = np.mean(energy_values) if len(energy_values) > 0 else 0.0
            energy_var = np.var(energy_values) if len(energy_values) > 1 else 0.0
            
            # History für Trend-Analyse
            self.pitch_history.append(pitch_mean)
            self.energy_history.append(energy_mean)
            
            if len(self.pitch_history) > self.feature_window_size:
                self.pitch_history.pop(0)
            if len(self.energy_history) > self.feature_window_size:
                self.energy_history.pop(0)
            
            prosody_data = {
                'pitch_mean': float(pitch_mean),
                'pitch_var': float(pitch_var),
                'energy_mean': float(energy_mean),
                'energy_var': float(energy_var)
            }
            
            # Signal senden
            self.prosody_updated.emit(prosody_data)
            
            return prosody_data
            
        except Exception as e:
            print(f"Fehler bei Prosody-Analyse: {e}")
            return {
                'pitch_mean': 0.0,
                'pitch_var': 0.0,
                'energy_mean': 0.0,
                'energy_var': 0.0
            }
    
    def get_current_markers(self) -> Dict:
        """Aktuelle Marker abrufen"""
        return self.current_markers.copy()
    
    def get_emotion_summary(self) -> Dict:
        """Zusammenfassung der Emotionen über Zeit"""
        if not self.emotion_history:
            return {}
        
        emotions = [e[0] for e in self.emotion_history]
        emotion_counts = {}
        
        for emotion in emotions:
            emotion_counts[emotion] = emotion_counts.get(emotion, 0) + 1
        
        total = len(emotions)
        emotion_percentages = {
            emotion: (count / total) * 100 
            for emotion, count in emotion_counts.items()
        }
        
        return emotion_percentages
    
    def get_prosody_trends(self) -> Dict:
        """Prosodische Trends über Zeit"""
        if len(self.pitch_history) < 2 or len(self.energy_history) < 2:
            return {}
        
        # Trend-Berechnung (einfache lineare Regression)
        x = np.arange(len(self.pitch_history))
        
        pitch_trend = np.polyfit(x, self.pitch_history, 1)[0] if len(self.pitch_history) > 1 else 0
        energy_trend = np.polyfit(x, self.energy_history, 1)[0] if len(self.energy_history) > 1 else 0
        
        return {
            'pitch_trend': float(pitch_trend),
            'energy_trend': float(energy_trend),
            'pitch_stability': float(1.0 / (1.0 + np.var(self.pitch_history))),
            'energy_stability': float(1.0 / (1.0 + np.var(self.energy_history)))
        }
