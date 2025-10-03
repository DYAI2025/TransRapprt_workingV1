
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
TransRapport MVP - Audio-Management
Mikrofon-Erkennung und Audio-Stream-Verwaltung für Live-Transkription
"""

import numpy as np
import sounddevice as sd
import queue
from datetime import datetime
import time
from typing import List, Dict, Optional

class AudioManager:
    """Verwaltet Audio-Eingabe und Mikrofon-Erkennung für Live-Transkription"""
    
    def __init__(self, sample_rate: int = 16000, channels: int = 1, dtype=np.float32):
        self.sample_rate = sample_rate
        self.channels = channels
        self.dtype = dtype
        self.stream = None
        self.audio_queue = queue.Queue(maxsize=100)  # Begrenzte Queue-Größe
        self.is_recording = False
        self.blocksize = 1024  # Samples pro Block
        
    def get_input_devices(self) -> List[Dict]:
        """Verfügbare Eingabe-Geräte (Mikrofone) auflisten"""
        try:
            devices = sd.query_devices()
            input_devices = []
            
            for i, device in enumerate(devices):
                if device['max_input_channels'] > 0:
                    input_devices.append({
                        'index': i,
                        'name': device['name'],
                        'channels': device['max_input_channels'],
                        'sample_rate': device['default_samplerate']
                    })
            
            return input_devices
            
        except Exception as e:
            print(f"Fehler beim Abrufen der Audio-Geräte: {e}")
            return []
    
    def get_default_input_device(self) -> Optional[Dict]:
        """Standard-Eingabegerät ermitteln"""
        try:
            default_device = sd.query_devices(kind='input')
            return {
                'index': sd.default.device[0] if sd.default.device[0] is not None else 0,
                'name': default_device['name'],
                'channels': default_device['max_input_channels'],
                'sample_rate': default_device['default_samplerate']
            }
        except Exception as e:
            print(f"Fehler beim Abrufen des Standard-Geräts: {e}")
            return None
    
    def audio_callback(self, indata, frames, time, status):
        """Callback-Funktion für Audio-Stream (optimiert für Live-Transkription)"""
        if status:
            print(f"Audio-Status: {status}")
        
        if self.is_recording:
            try:
                # Audio-Daten normalisieren und in Queue einreihen
                audio_data = indata.copy().astype(self.dtype)
                
                # Mono-Konvertierung falls nötig
                if audio_data.ndim > 1:
                    audio_data = np.mean(audio_data, axis=1)
                
                # Queue-Überlauf vermeiden
                if not self.audio_queue.full():
                    self.audio_queue.put(audio_data)
                else:
                    # Älteste Daten entfernen wenn Queue voll
                    try:
                        self.audio_queue.get_nowait()
                        self.audio_queue.put(audio_data)
                    except queue.Empty:
                        pass
                        
            except Exception as e:
                print(f"Fehler im Audio-Callback: {e}")
    
    def start_recording(self, device_index: Optional[int] = None):
        """Audio-Aufnahme für Live-Transkription starten - REPARIERT"""
        try:
            if self.is_recording:
                return
            
            # Gerät auswählen
            if device_index is None:
                device_index = sd.default.device[0]
            
            # KRITISCHER FIX: Adaptive Kanal-Erkennung
            device_info = sd.query_devices(device_index, 'input')
            max_channels = int(device_info['max_input_channels'])
            
            print(f"🎤 Gerät {device_index}: {device_info['name']}")
            print(f"📊 Max Kanäle: {max_channels}, Angefragt: {self.channels}")
            
            # Adaptive Kanal-Anpassung
            if max_channels < self.channels:
                print(f"⚠️  Kanäle reduziert: {self.channels} → {max_channels}")
                self.channels = max_channels
            
            # ERWEITERTE Fallback-Strategie für PortAudio-Fehler
            fallback_configs = [
                # (channels, blocksize, latency)
                (self.channels, self.blocksize, 'low'),
                (1, self.blocksize, 'low'),  # Mono fallback
                (max_channels, self.blocksize, 'low'),
                (1, 512, 'low'),  # Kleinere Blocksize
                (1, 2048, 'low'),  # Größere Blocksize
                (1, self.blocksize, 'high'),  # Höhere Latenz für Kompatibilität
                (1, 512, 'high'),  # Konservative Einstellungen
            ]
            
            for channels_to_try, blocksize, latency in fallback_configs:
                try:
                    print(f"🔄 Teste {channels_to_try} Kanal(e), Blocksize: {blocksize}, Latenz: {latency}...")
                    
                    # Queue leeren
                    while not self.audio_queue.empty():
                        try:
                            self.audio_queue.get_nowait()
                        except queue.Empty:
                            break
                    
                    # Audio-Stream erstellen (mit verschiedenen Fallback-Optionen)
                    self.stream = sd.InputStream(
                        device=device_index,
                        channels=channels_to_try,
                        samplerate=self.sample_rate,
                        dtype=self.dtype,
                        callback=self.audio_callback,
                        blocksize=blocksize,
                        latency=latency
                    )
                    
                    # Stream starten
                    self.stream.start()
                    self.is_recording = True
                    self.channels = channels_to_try  # Erfolgreich getestete Kanäle speichern
                    self.blocksize = blocksize  # Aktualisierte Blocksize speichern
                    
                    print(f"✅ Live-Audio-Aufnahme gestartet (Gerät: {device_index}, Kanäle: {channels_to_try}, Blocksize: {blocksize}, Sample Rate: {self.sample_rate})")
                    return  # Erfolgreich, Schleife verlassen
                    
                except Exception as channel_error:
                    print(f"❌ Konfiguration fehlgeschlagen: {channel_error}")
                    if self.stream:
                        try:
                            self.stream.close()
                        except:
                            pass
                        self.stream = None
                    continue
            
            # Alle Konfigurationen fehlgeschlagen
            raise Exception(f"Alle Audio-Konfigurationen fehlgeschlagen. PortAudio-Problem mit Gerät {device_index}.")
            
        except Exception as e:
            print(f"Fehler beim Starten der Audio-Aufnahme: {e}")
            raise
    
    def stop_recording(self):
        """Audio-Aufnahme stoppen"""
        try:
            if not self.is_recording:
                return
            
            self.is_recording = False
            
            if self.stream:
                self.stream.stop()
                self.stream.close()
                self.stream = None
            
            # Queue leeren
            while not self.audio_queue.empty():
                try:
                    self.audio_queue.get_nowait()
                except queue.Empty:
                    break
            
            print("Live-Audio-Aufnahme gestoppt")
            
        except Exception as e:
            print(f"Fehler beim Stoppen der Audio-Aufnahme: {e}")
            raise
    
    def get_audio_data(self, timeout: float = 0.1) -> Optional[np.ndarray]:
        """Audio-Daten aus der Queue abrufen (für Live-Transkription)"""
        try:
            return self.audio_queue.get(timeout=timeout)
        except queue.Empty:
            return None
    
    def get_audio_level(self) -> float:
        """Aktuellen Audio-Pegel ermitteln (für Visualisierung)"""
        try:
            # Alle verfügbaren Audio-Daten sammeln
            audio_chunks = []
            while True:
                try:
                    chunk = self.audio_queue.get_nowait()
                    audio_chunks.append(chunk)
                except queue.Empty:
                    break
            
            if audio_chunks:
                # Chunks wieder in Queue zurücklegen
                for chunk in audio_chunks:
                    if not self.audio_queue.full():
                        self.audio_queue.put(chunk)
                
                # RMS des letzten Chunks berechnen
                last_chunk = audio_chunks[-1]
                rms = np.sqrt(np.mean(last_chunk**2))
                return min(rms * 10.0, 1.0)  # Normalisieren auf 0-1
            
            return 0.0
            
        except Exception as e:
            print(f"Fehler bei Audio-Level-Berechnung: {e}")
            return 0.0
    
    def test_microphone(self, device_index: Optional[int] = None, duration: float = 2.0) -> bool:
        """Mikrofon testen"""
        try:
            print(f"Teste Mikrofon für {duration} Sekunden...")
            
            # Kurze Testaufnahme
            recording = sd.rec(
                int(duration * self.sample_rate),
                samplerate=self.sample_rate,
                channels=self.channels,
                device=device_index,
                dtype=self.dtype
            )
            sd.wait()
            
            # Prüfen ob Audio-Signal vorhanden
            max_amplitude = np.max(np.abs(recording))
            rms = np.sqrt(np.mean(recording**2))
            
            print(f"Maximale Amplitude: {max_amplitude:.4f}")
            print(f"RMS: {rms:.4f}")
            
            # Schwellenwert für float32 Audio
            return max_amplitude > 0.001 and rms > 0.0001
            
        except Exception as e:
            print(f"Fehler beim Testen des Mikrofons: {e}")
            return False
    
    def get_queue_size(self) -> int:
        """Aktuelle Größe der Audio-Queue"""
        return self.audio_queue.qsize()
    
    def is_queue_healthy(self) -> bool:
        """Prüfen ob Audio-Queue gesund ist (nicht überlaufen)"""
        return self.audio_queue.qsize() < self.audio_queue.maxsize * 0.8
