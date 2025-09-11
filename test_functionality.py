#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
TransRapport MVP - Funktionalitäts-Test
Testet alle wichtigen Komponenten der Anwendung
"""

import os
import sys
import json
from datetime import datetime

def test_imports():
    """Teste alle wichtigen Imports"""
    print("🔍 Teste Imports...")
    
    try:
        from exporter import TranscriptExporter
        print("  ✓ TranscriptExporter")
        
        from session_manager import SessionManager
        print("  ✓ SessionManager")
        
        from marker_system import MarkerSystem
        print("  ✓ MarkerSystem")
        
        from live_transcriber import LiveTranscriber
        print("  ✓ LiveTranscriber")
        
        from audio import AudioManager
        print("  ✓ AudioManager")
        
        return True
    except ImportError as e:
        print(f"  ❌ Import-Fehler: {e}")
        return False

def test_session_management():
    """Teste Session-Management"""
    print("\n📁 Teste Session-Management...")
    
    try:
        from session_manager import SessionManager
        
        session_manager = SessionManager()
        
        # Session erstellen
        session = session_manager.create_session("Test-Session")
        print(f"  ✓ Session erstellt: {session['name']}")
        
        # Session speichern
        filepath = session_manager.save_session(session)
        print(f"  ✓ Session gespeichert: {os.path.basename(filepath)}")
        
        # Session laden
        loaded_session = session_manager.load_session(filepath)
        if loaded_session and loaded_session['name'] == session['name']:
            print("  ✓ Session erfolgreich geladen")
        else:
            print("  ❌ Session-Laden fehlgeschlagen")
            return False
        
        # Aufräumen
        os.remove(filepath)
        print("  ✓ Test-Session gelöscht")
        
        return True
    except Exception as e:
        print(f"  ❌ Session-Management Fehler: {e}")
        return False

def test_export_functionality():
    """Teste Export-Funktionalität"""
    print("\n📄 Teste Export-Funktionalität...")
    
    try:
        from exporter import TranscriptExporter
        
        exporter = TranscriptExporter()
        
        # Test-Daten
        test_transcript = "Dies ist ein Test-Transkript für die Export-Funktionalität."
        test_session_data = {
            'start_time': datetime.now().isoformat(),
            'duration': '0:05:00',
            'language': 'de',
            'markers_summary': {
                'emotions': {'neutral': 80.0, 'positive': 20.0},
                'pauses': {'count': 3, 'avg_duration': 1.5, 'max_duration': 2.1},
                'prosody': {'avg_pitch': 180.0, 'avg_energy': 0.15}
            }
        }
        
        # Text-Export testen
        txt_path = exporter.export_to_txt(test_transcript, test_session_data, "test_export.txt")
        if os.path.exists(txt_path):
            print("  ✓ Text-Export erfolgreich")
            os.remove(txt_path)
        else:
            print("  ❌ Text-Export fehlgeschlagen")
            return False
        
        # Markdown-Export testen
        md_path = exporter.export_to_markdown(test_transcript, test_session_data, "test_export.md")
        if os.path.exists(md_path):
            print("  ✓ Markdown-Export erfolgreich")
            os.remove(md_path)
        else:
            print("  ❌ Markdown-Export fehlgeschlagen")
            return False
        
        return True
    except Exception as e:
        print(f"  ❌ Export-Funktionalität Fehler: {e}")
        return False

def test_marker_system():
    """Teste Marker-System"""
    print("\n🎯 Teste Marker-System...")
    
    try:
        from marker_system import MarkerSystem
        import numpy as np
        
        marker_system = MarkerSystem()
        print("  ✓ MarkerSystem initialisiert")
        
        # Test-Audio-Daten (Dummy)
        test_audio = np.random.randn(16000).astype(np.float32) * 0.1  # 1 Sekunde bei 16kHz
        
        marker_system.start()
        markers = marker_system.process_audio_chunk(test_audio)
        marker_system.stop()
        
        if markers and 'timestamp' in markers:
            print("  ✓ Audio-Chunk verarbeitet")
            print(f"    - Emotion: {markers.get('affect', {}).get('emotion', 'N/A')}")
            print(f"    - Pause: {markers.get('tempo', {}).get('pause_duration', 0):.1f}s")
            print(f"    - Pitch: {markers.get('prosody', {}).get('pitch_mean', 0):.0f} Hz")
        else:
            print("  ❌ Marker-Verarbeitung fehlgeschlagen")
            return False
        
        return True
    except Exception as e:
        print(f"  ❌ Marker-System Fehler: {e}")
        return False

def test_directories():
    """Teste Verzeichnisstruktur"""
    print("\n📂 Teste Verzeichnisstruktur...")
    
    required_dirs = ['sessions', 'exports', 'demo_material']
    
    for dir_name in required_dirs:
        if os.path.exists(dir_name):
            print(f"  ✓ {dir_name}/ vorhanden")
        else:
            print(f"  ❌ {dir_name}/ fehlt")
            return False
    
    # Demo-Materialien prüfen
    demo_files = [
        'demo_material/README_DEMO.md',
        'demo_material/beispiel_transkript.txt',
        'demo_material/beispiel_transkript.md',
        'demo_material/beispiel_session.json'
    ]
    
    for file_path in demo_files:
        if os.path.exists(file_path):
            print(f"  ✓ {file_path} vorhanden")
        else:
            print(f"  ❌ {file_path} fehlt")
            return False
    
    return True

def test_demo_session():
    """Teste Demo-Session laden"""
    print("\n🎬 Teste Demo-Session...")
    
    try:
        from session_manager import SessionManager
        
        demo_session_path = 'demo_material/beispiel_session.json'
        
        if not os.path.exists(demo_session_path):
            print("  ❌ Demo-Session nicht gefunden")
            return False
        
        session_manager = SessionManager()
        demo_session = session_manager.load_session(demo_session_path)
        
        if demo_session:
            print(f"  ✓ Demo-Session geladen: {demo_session['name']}")
            print(f"    - Transkript-Länge: {len(demo_session.get('transcript', ''))} Zeichen")
            print(f"    - Marker-Daten: {len(demo_session.get('markers_data', {}).get('emotions', []))} Datenpunkte")
            return True
        else:
            print("  ❌ Demo-Session konnte nicht geladen werden")
            return False
            
    except Exception as e:
        print(f"  ❌ Demo-Session Fehler: {e}")
        return False

def main():
    """Haupttest-Funktion"""
    print("🚀 TransRapport MVP - Funktionalitäts-Test")
    print("=" * 50)
    
    tests = [
        ("Imports", test_imports),
        ("Verzeichnisstruktur", test_directories),
        ("Session-Management", test_session_management),
        ("Export-Funktionalität", test_export_functionality),
        ("Marker-System", test_marker_system),
        ("Demo-Session", test_demo_session)
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        try:
            if test_func():
                passed += 1
            else:
                print(f"\n❌ Test '{test_name}' fehlgeschlagen")
        except Exception as e:
            print(f"\n❌ Test '{test_name}' mit Ausnahme fehlgeschlagen: {e}")
    
    print("\n" + "=" * 50)
    print(f"📊 Test-Ergebnis: {passed}/{total} Tests bestanden")
    
    if passed == total:
        print("🎉 Alle Tests erfolgreich! TransRapport MVP ist bereit.")
        return True
    else:
        print("⚠️  Einige Tests fehlgeschlagen. Bitte Probleme beheben.")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
