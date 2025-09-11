#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
TransRapport MVP - Marker-System Unit Test
Einfacher Test für das vereinfachte Marker-System (ATO→SEM)
"""

import numpy as np
import time
from marker_system import MarkerSystem
from datetime import datetime

def generate_test_audio(duration=10, sample_rate=16000, frequency=440):
    """Test-Audio generieren (Sinuswelle mit Rauschen)"""
    t = np.linspace(0, duration, int(sample_rate * duration))
    
    # Sinuswelle mit variierender Amplitude (simuliert Emotionen)
    amplitude_variation = 0.3 + 0.7 * np.sin(0.5 * t)  # Langsame Amplitude-Änderung
    audio = amplitude_variation * np.sin(2 * np.pi * frequency * t)
    
    # Rauschen hinzufügen
    noise = 0.1 * np.random.randn(len(audio))
    audio += noise
    
    # Pausen simulieren (Stille-Bereiche)
    pause_start = int(3 * sample_rate)
    pause_end = int(4 * sample_rate)
    audio[pause_start:pause_end] *= 0.05  # Sehr leise für Pause
    
    pause_start2 = int(7 * sample_rate)
    pause_end2 = int(8.5 * sample_rate)
    audio[pause_start2:pause_end2] *= 0.02  # Noch leisere Pause
    
    return audio.astype(np.float32)

def test_marker_system():
    """Marker-System testen"""
    print("=== TransRapport MVP - Marker-System Test ===")
    print()
    
    # Marker-System initialisieren
    marker_system = MarkerSystem(sample_rate=16000)
    
    # Test-Audio generieren
    print("Generiere Test-Audio (10 Sekunden)...")
    test_audio = generate_test_audio(duration=10)
    
    # Marker-System starten
    marker_system.start()
    print("Marker-System gestartet")
    print()
    
    # Audio in Chunks verarbeiten
    chunk_size = 1024  # Samples pro Chunk
    chunk_duration = chunk_size / 16000  # Sekunden pro Chunk
    
    print("Verarbeite Audio-Chunks...")
    print("=" * 50)
    
    for i in range(0, len(test_audio), chunk_size):
        chunk = test_audio[i:i + chunk_size]
        timestamp = datetime.now()
        
        # Chunk verarbeiten
        markers = marker_system.process_audio_chunk(chunk, timestamp)
        
        # Ergebnisse anzeigen (alle 2 Sekunden)
        if i % (chunk_size * 32) == 0:  # Etwa alle 2 Sekunden
            current_time = i / 16000
            print(f"Zeit: {current_time:.1f}s")
            print(f"  Emotion: {markers['affect']['emotion']} (Confidence: {markers['affect']['confidence']:.2f})")
            print(f"  Valenz: {markers['affect']['valence']:.2f}")
            print(f"  Pause: {markers['tempo']['pause_duration']:.2f}s")
            print(f"  Pitch: {markers['prosody']['pitch_mean']:.1f} Hz")
            print(f"  Energie: {markers['prosody']['energy_mean']:.3f}")
            print()
        
        # Simuliere Echtzeit-Verarbeitung
        time.sleep(0.001)
    
    # Test-Transkript verarbeiten
    print("Teste Transkript-Verarbeitung...")
    test_texts = [
        "Hallo, wie geht es Ihnen heute?",
        "Ich fühle mich nicht so gut.",
        "Das ist wirklich sehr interessant!",
        "Können Sie mir dabei helfen?"
    ]
    
    for text in test_texts:
        marker_system.process_transcript(text)
        print(f"Verarbeitet: '{text}'")
    
    print()
    
    # Zusammenfassung
    print("=== Zusammenfassung ===")
    emotion_summary = marker_system.get_emotion_summary()
    if emotion_summary:
        print("Emotionsverteilung:")
        for emotion, percentage in emotion_summary.items():
            print(f"  {emotion}: {percentage:.1f}%")
    
    prosody_trends = marker_system.get_prosody_trends()
    if prosody_trends:
        print("\nProsodische Trends:")
        print(f"  Pitch-Trend: {prosody_trends.get('pitch_trend', 0):.3f}")
        print(f"  Energie-Trend: {prosody_trends.get('energy_trend', 0):.3f}")
        print(f"  Pitch-Stabilität: {prosody_trends.get('pitch_stability', 0):.3f}")
        print(f"  Energie-Stabilität: {prosody_trends.get('energy_stability', 0):.3f}")
    
    # Marker-System stoppen
    marker_system.stop()
    print("\nMarker-System gestoppt")
    print("Test erfolgreich abgeschlossen!")

if __name__ == "__main__":
    try:
        test_marker_system()
    except Exception as e:
        print(f"Fehler beim Test: {e}")
        import traceback
        traceback.print_exc()
