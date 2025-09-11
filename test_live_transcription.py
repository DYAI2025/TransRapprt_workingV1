#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
TransRapport MVP - Test der Live-Transkription (Konsolen-Version)
Testet die Live-Transkriptions-Engine ohne GUI
"""

import time
import signal
import sys
from audio import AudioManager
from live_transcriber import LiveTranscriber
from PyQt6.QtCore import QCoreApplication

class ConsoleTranscriptionTest:
    """Konsolen-Test für Live-Transkription"""
    
    def __init__(self):
        self.app = QCoreApplication(sys.argv)
        self.audio_manager = AudioManager()
        self.live_transcriber = LiveTranscriber()
        self.is_running = False
        
        # Signal-Handler für sauberes Beenden
        signal.signal(signal.SIGINT, self.signal_handler)
        
        # Transcriber-Signale verbinden
        self.live_transcriber.transcription_ready.connect(self.on_transcription)
        self.live_transcriber.error_occurred.connect(self.on_error)
    
    def signal_handler(self, signum, frame):
        """Signal-Handler für Ctrl+C"""
        print("\n\nBeende Live-Transkription...")
        self.stop()
        sys.exit(0)
    
    def on_transcription(self, text):
        """Neue Transkription empfangen"""
        timestamp = time.strftime("%H:%M:%S")
        print(f"[{timestamp}] {text}")
    
    def on_error(self, error_msg):
        """Fehler behandeln"""
        print(f"FEHLER: {error_msg}")
    
    def list_audio_devices(self):
        """Audio-Geräte auflisten"""
        print("Verfügbare Audio-Geräte:")
        devices = self.audio_manager.get_input_devices()
        
        if not devices:
            print("  Keine Mikrofone gefunden!")
            return False
        
        for i, device in enumerate(devices):
            print(f"  {i}: {device['name']} ({device['channels']} Kanäle)")
        
        return True
    
    def test_microphone(self, device_index=None):
        """Mikrofon testen"""
        print(f"\nTeste Mikrofon (Index: {device_index})...")
        success = self.audio_manager.test_microphone(device_index, duration=3.0)
        
        if success:
            print("✓ Mikrofon funktioniert!")
        else:
            print("✗ Mikrofon-Test fehlgeschlagen!")
        
        return success
    
    def start(self, device_index=None):
        """Live-Transkription starten"""
        print("\n" + "="*60)
        print("TransRapport MVP - Live-Transkription Test")
        print("="*60)
        
        # Audio-Geräte auflisten
        if not self.list_audio_devices():
            return False
        
        # Mikrofon testen
        if not self.test_microphone(device_index):
            print("Warnung: Mikrofon-Test fehlgeschlagen, versuche trotzdem...")
        
        # Whisper-Modell prüfen
        print(f"\nLade Whisper-Modell '{self.live_transcriber.model_size}'...")
        if not self.live_transcriber.is_model_available():
            print("Fehler: Whisper-Modell nicht verfügbar!")
            return False
        
        print("✓ Whisper-Modell geladen!")
        
        # Audio-Aufnahme starten
        print(f"\nStarte Audio-Aufnahme (Gerät: {device_index})...")
        try:
            self.audio_manager.start_recording(device_index)
            print("✓ Audio-Aufnahme gestartet!")
        except Exception as e:
            print(f"✗ Fehler beim Starten der Audio-Aufnahme: {e}")
            return False
        
        # Live-Transkription starten
        print("Starte Live-Transkription...")
        success = self.live_transcriber.start_transcription(self.audio_manager)
        
        if not success:
            print("✗ Fehler beim Starten der Live-Transkription!")
            self.audio_manager.stop_recording()
            return False
        
        print("✓ Live-Transkription gestartet!")
        print("\n" + "-"*60)
        print("SPRECHEN SIE JETZT - Die Transkription erscheint hier:")
        print("(Drücken Sie Ctrl+C zum Beenden)")
        print("-"*60)
        
        self.is_running = True
        
        # Event-Loop starten
        try:
            self.app.exec()
        except KeyboardInterrupt:
            pass
        
        return True
    
    def stop(self):
        """Live-Transkription stoppen"""
        if not self.is_running:
            return
        
        self.is_running = False
        
        print("Stoppe Live-Transkription...")
        self.live_transcriber.stop_transcription()
        
        print("Stoppe Audio-Aufnahme...")
        self.audio_manager.stop_recording()
        
        print("✓ Live-Transkription beendet!")
        
        # Event-Loop beenden
        self.app.quit()

def main():
    """Hauptfunktion"""
    test = ConsoleTranscriptionTest()
    
    # Standard-Mikrofon verwenden (None = Standard)
    device_index = None
    
    # Kommandozeilen-Argument für Geräte-Index
    if len(sys.argv) > 1:
        try:
            device_index = int(sys.argv[1])
            print(f"Verwende Mikrofon-Index: {device_index}")
        except ValueError:
            print("Ungültiger Geräte-Index. Verwende Standard-Mikrofon.")
    
    # Test starten
    success = test.start(device_index)
    
    if not success:
        print("\nTest fehlgeschlagen!")
        sys.exit(1)

if __name__ == "__main__":
    main()
