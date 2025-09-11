
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
TransRapport MVP - Transkriptions-Engine
Offline-Spracherkennung mit Vosk
"""

import json
import os
import threading
import time
from typing import Optional, Callable
import vosk
import numpy as np

class TranscriptionEngine:
    """Offline-Spracherkennung für therapeutische Sitzungen"""
    
    def __init__(self, language: str = "de", sample_rate: int = 16000):
        self.language = language
        self.sample_rate = sample_rate
        self.model = None
        self.recognizer = None
        self.is_transcribing = False
        self.transcription_thread = None
        self.on_partial_result: Optional[Callable] = None
        self.on_final_result: Optional[Callable] = None
        
        # Modell-Pfade
        self.model_paths = {
            'de': 'models/vosk-model-de-0.21',
            'en': 'models/vosk-model-en-us-0.22'
        }
        
        # Modell initialisieren
        self.init_model()
    
    def init_model(self):
        """Vosk-Modell initialisieren"""
        try:
            model_path = self.model_paths.get(self.language)
            
            if not model_path or not os.path.exists(model_path):
                print(f"Warnung: Vosk-Modell für '{self.language}' nicht gefunden.")
                print("Für die vollständige Funktionalität laden Sie bitte ein Vosk-Modell herunter:")
                print(f"- Deutsch: https://alphacephei.com/vosk/models/vosk-model-de-0.21.zip")
                print(f"- Englisch: https://alphacephei.com/vosk/models/vosk-model-en-us-0.22.zip")
                print("Entpacken Sie das Modell in den 'models/' Ordner.")
                return
            
            # Vosk-Logging reduzieren
            vosk.SetLogLevel(-1)
            
            # Modell laden
            self.model = vosk.Model(model_path)
            self.recognizer = vosk.KaldiRecognizer(self.model, self.sample_rate)
            
            print(f"Vosk-Modell für '{self.language}' erfolgreich geladen")
            
        except Exception as e:
            print(f"Fehler beim Laden des Vosk-Modells: {e}")
            self.model = None
            self.recognizer = None
    
    def is_model_available(self) -> bool:
        """Prüfen ob Modell verfügbar ist"""
        return self.model is not None and self.recognizer is not None
    
    def set_callbacks(self, on_partial: Callable = None, on_final: Callable = None):
        """Callback-Funktionen für Transkriptionsergebnisse setzen"""
        self.on_partial_result = on_partial
        self.on_final_result = on_final
    
    def start_transcription(self):
        """Transkription starten"""
        if not self.is_model_available():
            print("Fehler: Kein Vosk-Modell verfügbar")
            return False
        
        if self.is_transcribing:
            return True
        
        self.is_transcribing = True
        self.transcription_thread = threading.Thread(target=self._transcription_loop)
        self.transcription_thread.daemon = True
        self.transcription_thread.start()
        
        print("Transkription gestartet")
        return True
    
    def stop_transcription(self):
        """Transkription stoppen"""
        if not self.is_transcribing:
            return
        
        self.is_transcribing = False
        
        if self.transcription_thread:
            self.transcription_thread.join(timeout=2.0)
        
        print("Transkription gestoppt")
    
    def _transcription_loop(self):
        """Hauptschleife für Transkription (läuft in separatem Thread)"""
        print("Transkriptions-Loop gestartet")
        
        while self.is_transcribing:
            try:
                # Hier würde normalerweise Audio-Daten vom AudioManager abgerufen
                # Für MVP: Platzhalter-Implementierung
                time.sleep(0.1)
                
                # Simulierte Transkription für Demo-Zwecke
                if hasattr(self, '_demo_counter'):
                    self._demo_counter += 1
                else:
                    self._demo_counter = 0
                
                # Alle 50 Iterationen (ca. 5 Sekunden) Demo-Text ausgeben
                if self._demo_counter % 50 == 0 and self._demo_counter > 0:
                    demo_texts = [
                        "Willkommen zur therapeutischen Sitzung.",
                        "Wie fühlen Sie sich heute?",
                        "Können Sie mir mehr darüber erzählen?",
                        "Das ist ein wichtiger Punkt.",
                        "Transkription läuft erfolgreich."
                    ]
                    demo_text = demo_texts[self._demo_counter // 50 % len(demo_texts)]
                    
                    if self.on_final_result:
                        self.on_final_result(demo_text)
                
            except Exception as e:
                print(f"Fehler in Transkriptions-Loop: {e}")
                break
        
        print("Transkriptions-Loop beendet")
    
    def transcribe_audio_chunk(self, audio_data: np.ndarray) -> Optional[str]:
        """Audio-Chunk transkribieren"""
        if not self.is_model_available():
            return None
        
        try:
            # Audio-Daten zu Bytes konvertieren
            if audio_data.dtype != np.int16:
                audio_data = (audio_data * 32767).astype(np.int16)
            
            audio_bytes = audio_data.tobytes()
            
            # Vosk-Erkennung
            if self.recognizer.AcceptWaveform(audio_bytes):
                # Finales Ergebnis
                result = json.loads(self.recognizer.Result())
                text = result.get('text', '').strip()
                
                if text and self.on_final_result:
                    self.on_final_result(text)
                
                return text
            else:
                # Partielles Ergebnis
                partial_result = json.loads(self.recognizer.PartialResult())
                partial_text = partial_result.get('partial', '').strip()
                
                if partial_text and self.on_partial_result:
                    self.on_partial_result(partial_text)
                
                return None
                
        except Exception as e:
            print(f"Fehler bei Audio-Transkription: {e}")
            return None
    
    def get_supported_languages(self) -> list:
        """Unterstützte Sprachen auflisten"""
        return list(self.model_paths.keys())
    
    def change_language(self, language: str) -> bool:
        """Sprache wechseln"""
        if language not in self.model_paths:
            print(f"Sprache '{language}' wird nicht unterstützt")
            return False
        
        # Aktuelle Transkription stoppen
        was_transcribing = self.is_transcribing
        if was_transcribing:
            self.stop_transcription()
        
        # Sprache ändern und Modell neu laden
        self.language = language
        self.init_model()
        
        # Transkription wieder starten falls sie vorher lief
        if was_transcribing and self.is_model_available():
            self.start_transcription()
        
        return self.is_model_available()
    
    def download_model_info(self) -> dict:
        """Informationen zum Herunterladen von Modellen"""
        return {
            'de': {
                'name': 'Deutsch (German)',
                'url': 'https://alphacephei.com/vosk/models/vosk-model-de-0.21.zip',
                'size': '~1.8 GB',
                'path': 'models/vosk-model-de-0.21'
            },
            'en': {
                'name': 'Englisch (English US)',
                'url': 'https://alphacephei.com/vosk/models/vosk-model-en-us-0.22.zip',
                'size': '~1.8 GB', 
                'path': 'models/vosk-model-en-us-0.22'
            }
        }
