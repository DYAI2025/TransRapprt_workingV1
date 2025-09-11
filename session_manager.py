#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
TransRapport MVP - Sitzungsmanagement
Speichern und Laden von kompletten Sitzungen mit Transkripten und Markern
"""

import os
import json
import pickle
from datetime import datetime
from typing import Dict, List, Optional, Any
import numpy as np

class SessionManager:
    """Klasse für Sitzungsmanagement"""
    
    def __init__(self):
        self.sessions_dir = "sessions"
        os.makedirs(self.sessions_dir, exist_ok=True)
    
    def create_session(self, session_name: Optional[str] = None) -> Dict:
        """
        Neue Sitzung erstellen
        
        Args:
            session_name: Optionaler Name für die Sitzung
            
        Returns:
            Session-Dictionary
        """
        if session_name is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            session_name = f"Sitzung_{timestamp}"
        
        session = {
            'id': datetime.now().strftime("%Y%m%d_%H%M%S_%f"),
            'name': session_name,
            'created_at': datetime.now().isoformat(),
            'start_time': None,
            'end_time': None,
            'duration': None,
            'language': 'de',
            'model_size': 'base',
            'transcript': '',
            'markers_data': {
                'timestamps': [],
                'emotions': [],
                'pauses': [],
                'pitch': [],
                'energy': []
            },
            'markers_summary': {},
            'audio_settings': {},
            'notes': ''
        }
        
        return session
    
    def save_session(self, session: Dict, filename: Optional[str] = None) -> str:
        """
        Sitzung speichern
        
        Args:
            session: Session-Dictionary
            filename: Optionaler Dateiname
            
        Returns:
            Pfad zur gespeicherten Datei
        """
        if filename is None:
            filename = f"session_{session['id']}.json"
        
        filepath = os.path.join(self.sessions_dir, filename)
        
        # Session für JSON serialisierbar machen
        session_copy = self._prepare_session_for_json(session.copy())
        
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(session_copy, f, indent=2, ensure_ascii=False)
        
        return filepath
    
    def load_session(self, filepath: str) -> Optional[Dict]:
        """
        Sitzung laden
        
        Args:
            filepath: Pfad zur Session-Datei
            
        Returns:
            Session-Dictionary oder None bei Fehler
        """
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                session = json.load(f)
            
            # Numpy Arrays wiederherstellen
            session = self._restore_session_from_json(session)
            
            return session
            
        except Exception as e:
            print(f"Fehler beim Laden der Sitzung: {e}")
            return None
    
    def list_sessions(self) -> List[Dict]:
        """
        Alle verfügbaren Sitzungen auflisten
        
        Returns:
            Liste mit Session-Informationen
        """
        sessions = []
        
        for filename in os.listdir(self.sessions_dir):
            if filename.endswith('.json'):
                filepath = os.path.join(self.sessions_dir, filename)
                try:
                    with open(filepath, 'r', encoding='utf-8') as f:
                        session_data = json.load(f)
                    
                    sessions.append({
                        'filename': filename,
                        'filepath': filepath,
                        'id': session_data.get('id', ''),
                        'name': session_data.get('name', filename),
                        'created_at': session_data.get('created_at', ''),
                        'duration': session_data.get('duration', ''),
                        'language': session_data.get('language', 'de')
                    })
                    
                except Exception as e:
                    print(f"Fehler beim Lesen der Session-Datei {filename}: {e}")
        
        # Nach Erstellungsdatum sortieren (neueste zuerst)
        sessions.sort(key=lambda x: x['created_at'], reverse=True)
        
        return sessions
    
    def delete_session(self, filepath: str) -> bool:
        """
        Sitzung löschen
        
        Args:
            filepath: Pfad zur Session-Datei
            
        Returns:
            True bei Erfolg, False bei Fehler
        """
        try:
            os.remove(filepath)
            return True
        except Exception as e:
            print(f"Fehler beim Löschen der Sitzung: {e}")
            return False
    
    def update_session_transcript(self, session: Dict, transcript_text: str) -> Dict:
        """
        Transkript in Sitzung aktualisieren
        
        Args:
            session: Session-Dictionary
            transcript_text: Neuer Transkriptionstext
            
        Returns:
            Aktualisierte Session
        """
        session['transcript'] = transcript_text
        return session
    
    def update_session_markers(self, session: Dict, markers_data: Dict) -> Dict:
        """
        Marker-Daten in Sitzung aktualisieren
        
        Args:
            session: Session-Dictionary
            markers_data: Marker-Daten
            
        Returns:
            Aktualisierte Session
        """
        session['markers_data'] = markers_data
        
        # Marker-Zusammenfassung generieren
        session['markers_summary'] = self._generate_markers_summary(markers_data)
        
        return session
    
    def start_session(self, session: Dict) -> Dict:
        """
        Sitzung starten (Zeitstempel setzen)
        
        Args:
            session: Session-Dictionary
            
        Returns:
            Aktualisierte Session
        """
        session['start_time'] = datetime.now().isoformat()
        return session
    
    def end_session(self, session: Dict) -> Dict:
        """
        Sitzung beenden (Zeitstempel und Dauer setzen)
        
        Args:
            session: Session-Dictionary
            
        Returns:
            Aktualisierte Session
        """
        end_time = datetime.now()
        session['end_time'] = end_time.isoformat()
        
        if session['start_time']:
            start_time = datetime.fromisoformat(session['start_time'])
            duration = end_time - start_time
            session['duration'] = str(duration).split('.')[0]  # Ohne Mikrosekunden
        
        return session
    
    def _prepare_session_for_json(self, session: Dict) -> Dict:
        """Session für JSON-Serialisierung vorbereiten"""
        # Numpy Arrays zu Listen konvertieren
        if 'markers_data' in session:
            for key, value in session['markers_data'].items():
                if isinstance(value, np.ndarray):
                    session['markers_data'][key] = value.tolist()
                elif isinstance(value, list):
                    # Sicherstellen, dass alle Elemente JSON-serialisierbar sind
                    session['markers_data'][key] = [
                        float(x) if isinstance(x, (np.floating, np.integer)) else x 
                        for x in value
                    ]
        
        return session
    
    def _restore_session_from_json(self, session: Dict) -> Dict:
        """Session aus JSON wiederherstellen"""
        # Listen zurück zu Numpy Arrays konvertieren falls nötig
        if 'markers_data' in session:
            for key, value in session['markers_data'].items():
                if isinstance(value, list) and value:
                    # Nur konvertieren wenn numerische Daten
                    if all(isinstance(x, (int, float)) for x in value):
                        session['markers_data'][key] = np.array(value)
        
        return session
    
    def _generate_markers_summary(self, markers_data: Dict) -> Dict:
        """Marker-Zusammenfassung generieren"""
        summary = {}
        
        try:
            # Emotionen-Zusammenfassung
            if 'emotions' in markers_data and markers_data['emotions']:
                emotions = markers_data['emotions']
                if isinstance(emotions, list) and emotions:
                    # Vereinfachte Emotionsverteilung (hier müsste eine echte Klassifikation stehen)
                    # Für Demo-Zwecke nehmen wir Valenz-Werte und mappen sie zu Emotionen
                    emotion_counts = {'neutral': 0, 'positive': 0, 'negative': 0}
                    
                    for valence in emotions:
                        if valence > 0.3:
                            emotion_counts['positive'] += 1
                        elif valence < -0.3:
                            emotion_counts['negative'] += 1
                        else:
                            emotion_counts['neutral'] += 1
                    
                    total = sum(emotion_counts.values())
                    if total > 0:
                        summary['emotions'] = {
                            emotion: (count / total) * 100 
                            for emotion, count in emotion_counts.items()
                        }
            
            # Pausen-Zusammenfassung
            if 'pauses' in markers_data and markers_data['pauses']:
                pauses = [p for p in markers_data['pauses'] if p > 0]
                if pauses:
                    summary['pauses'] = {
                        'count': len(pauses),
                        'avg_duration': float(np.mean(pauses)),
                        'max_duration': float(np.max(pauses)),
                        'min_duration': float(np.min(pauses))
                    }
            
            # Prosody-Zusammenfassung
            prosody_summary = {}
            
            if 'pitch' in markers_data and markers_data['pitch']:
                valid_pitch = [p for p in markers_data['pitch'] if p > 0]
                if valid_pitch:
                    prosody_summary['avg_pitch'] = float(np.mean(valid_pitch))
                    prosody_summary['pitch_stability'] = float(1.0 / (1.0 + np.var(valid_pitch)))
            
            if 'energy' in markers_data and markers_data['energy']:
                energy_values = [e for e in markers_data['energy'] if e > 0]
                if energy_values:
                    prosody_summary['avg_energy'] = float(np.mean(energy_values))
                    prosody_summary['energy_stability'] = float(1.0 / (1.0 + np.var(energy_values)))
            
            if prosody_summary:
                summary['prosody'] = prosody_summary
                
        except Exception as e:
            print(f"Fehler bei Marker-Zusammenfassung: {e}")
        
        return summary
    
    def export_session_summary(self, session: Dict, format: str = 'txt') -> str:
        """
        Session-Zusammenfassung exportieren
        
        Args:
            session: Session-Dictionary
            format: Export-Format ('txt' oder 'md')
            
        Returns:
            Pfad zur exportierten Datei
        """
        from exporter import TranscriptExporter
        
        exporter = TranscriptExporter()
        
        if format == 'md':
            return exporter.export_to_markdown(
                session.get('transcript', ''),
                session
            )
        else:
            return exporter.export_to_txt(
                session.get('transcript', ''),
                session
            )
    
    def get_sessions_directory(self) -> str:
        """Gibt das Sessions-Verzeichnis zurück"""
        return os.path.abspath(self.sessions_dir)
