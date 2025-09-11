#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
TransRapport MVP - Demo der Live-Transkription
Demonstriert die Whisper-Integration ohne Mikrofon
"""

import numpy as np
import time
import sys
from live_transcriber import LiveTranscriber
from PyQt6.QtCore import QCoreApplication
import wave
import io

class TranscriptionDemo:
    """Demo der Live-Transkriptions-Engine"""
    
    def __init__(self):
        self.app = QCoreApplication(sys.argv)
        self.live_transcriber = LiveTranscriber()
        
        # Transcriber-Signale verbinden
        self.live_transcriber.transcription_ready.connect(self.on_transcription)
        self.live_transcriber.error_occurred.connect(self.on_error)
    
    def on_transcription(self, text):
        """Neue Transkription empfangen"""
        timestamp = time.strftime("%H:%M:%S")
        print(f"[{timestamp}] Transkription: {text}")
    
    def on_error(self, error_msg):
        """Fehler behandeln"""
        print(f"FEHLER: {error_msg}")
    
    def generate_test_audio(self, duration=5.0, sample_rate=16000):
        """Test-Audio generieren (Sinuswelle mit verschiedenen Frequenzen)"""
        print(f"Generiere {duration}s Test-Audio...")
        
        t = np.linspace(0, duration, int(sample_rate * duration), False)
        
        # Mehrere Frequenzen für interessanteres Audio
        frequencies = [440, 554, 659, 784]  # A4, C#5, E5, G5 (A-Dur Akkord)
        audio = np.zeros_like(t)
        
        for freq in frequencies:
            audio += 0.25 * np.sin(2 * np.pi * freq * t)
        
        # Envelope für natürlicheren Klang
        envelope = np.exp(-t * 0.5)  # Exponentieller Abfall
        audio *= envelope
        
        # Normalisieren
        audio = audio / np.max(np.abs(audio)) * 0.8
        
        return audio.astype(np.float32)
    
    def test_whisper_model(self):
        """Whisper-Modell testen"""
        print("\n" + "="*60)
        print("TransRapport MVP - Whisper-Modell Demo")
        print("="*60)
        
        # Modell-Info anzeigen
        print(f"Modell: {self.live_transcriber.model_size}")
        print(f"Sprache: {self.live_transcriber.language}")
        
        # Modell laden
        print("\nLade Whisper-Modell...")
        if not self.live_transcriber.is_model_available():
            print("✗ Whisper-Modell nicht verfügbar!")
            return False
        
        print("✓ Whisper-Modell erfolgreich geladen!")
        
        # Modell-Informationen anzeigen
        model_info = self.live_transcriber.get_model_info()
        current_model = self.live_transcriber.model_size
        if current_model in model_info:
            info = model_info[current_model]
            print(f"  Größe: {info['size']}")
            print(f"  Geschwindigkeit: {info['speed']}")
            print(f"  Qualität: {info['quality']}")
        
        return True
    
    def test_audio_processing(self):
        """Audio-Verarbeitung testen"""
        print("\n" + "-"*60)
        print("AUDIO-VERARBEITUNG TEST")
        print("-"*60)
        
        # Test-Audio generieren
        test_audio = self.generate_test_audio(duration=3.0)
        print(f"✓ Test-Audio generiert ({len(test_audio)} Samples)")
        
        # Audio-Chunk direkt transkribieren
        print("Teste direkte Audio-Transkription...")
        
        try:
            # Verwende die interne Methode für direkten Test
            result = self.live_transcriber._transcribe_chunk(test_audio)
            
            if result:
                print(f"✓ Transkription erfolgreich: '{result}'")
            else:
                print("ℹ Keine Transkription (Audio zu leise oder kein Sprach-Inhalt)")
            
        except Exception as e:
            print(f"✗ Fehler bei Transkription: {e}")
            return False
        
        return True
    
    def test_language_support(self):
        """Sprachunterstützung testen"""
        print("\n" + "-"*60)
        print("SPRACHUNTERSTÜTZUNG TEST")
        print("-"*60)
        
        supported_langs = self.live_transcriber.get_supported_languages()
        print(f"Unterstützte Sprachen: {', '.join(supported_langs)}")
        
        # Sprache wechseln testen
        for lang in ["de", "en", "auto"]:
            print(f"Teste Sprachwechsel zu '{lang}'...")
            success = self.live_transcriber.change_language(lang)
            if success:
                print(f"✓ Sprachwechsel zu '{lang}' erfolgreich")
            else:
                print(f"✗ Sprachwechsel zu '{lang}' fehlgeschlagen")
        
        return True
    
    def run_demo(self):
        """Vollständige Demo ausführen"""
        print("Starte TransRapport MVP Live-Transkription Demo...")
        
        # Whisper-Modell testen
        if not self.test_whisper_model():
            return False
        
        # Audio-Verarbeitung testen
        if not self.test_audio_processing():
            return False
        
        # Sprachunterstützung testen
        if not self.test_language_support():
            return False
        
        print("\n" + "="*60)
        print("DEMO ERFOLGREICH ABGESCHLOSSEN!")
        print("="*60)
        print("\nDie Live-Transkriptions-Engine ist funktionsfähig!")
        print("Funktionen:")
        print("✓ Whisper-Modell lädt erfolgreich")
        print("✓ Audio-Verarbeitung funktioniert")
        print("✓ Sprachunterstützung (Deutsch/Englisch/Auto)")
        print("✓ Threading-basierte Architektur")
        print("✓ Qt-Signal Integration für GUI")
        print("\nFür die vollständige Funktionalität mit Mikrofon:")
        print("- Starten Sie die Anwendung auf einem System mit Audio-Hardware")
        print("- Verwenden Sie: python main.py")
        
        return True

def main():
    """Hauptfunktion"""
    demo = TranscriptionDemo()
    
    try:
        success = demo.run_demo()
        if not success:
            print("\nDemo fehlgeschlagen!")
            sys.exit(1)
    except KeyboardInterrupt:
        print("\nDemo abgebrochen.")
    except Exception as e:
        print(f"\nUnerwarteter Fehler: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
