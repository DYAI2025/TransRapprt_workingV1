#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
TransRapport MVP - Export-Funktionalität
Exportiert Transkripte und Sitzungsdaten in verschiedene Formate
"""

import os
import json
from datetime import datetime
from typing import Dict, List, Optional
import numpy as np

class TranscriptExporter:
    """Klasse für Export von Transkripten und Sitzungsdaten"""
    
    def __init__(self):
        self.export_dir = "exports"
        os.makedirs(self.export_dir, exist_ok=True)
    
    def export_to_txt(self, transcript_text: str, session_data: Optional[Dict] = None, 
                      filename: Optional[str] = None) -> str:
        """
        Transkript als einfache Textdatei exportieren
        
        Args:
            transcript_text: Der Transkriptionstext
            session_data: Optionale Sitzungsdaten mit Markern
            filename: Optionaler Dateiname
            
        Returns:
            Pfad zur erstellten Datei
        """
        if filename is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"transkript_{timestamp}.txt"
        
        filepath = os.path.join(self.export_dir, filename)
        
        with open(filepath, 'w', encoding='utf-8') as f:
            # Header
            f.write("=" * 60 + "\n")
            f.write("TransRapport MVP - Transkript Export\n")
            f.write("=" * 60 + "\n")
            f.write(f"Exportiert am: {datetime.now().strftime('%d.%m.%Y um %H:%M:%S')}\n")
            f.write("\n")
            
            # Sitzungsinfo falls verfügbar
            if session_data:
                f.write("SITZUNGSINFORMATIONEN:\n")
                f.write("-" * 30 + "\n")
                if 'start_time' in session_data:
                    f.write(f"Sitzungsbeginn: {session_data['start_time']}\n")
                if 'duration' in session_data:
                    f.write(f"Dauer: {session_data['duration']}\n")
                if 'language' in session_data:
                    f.write(f"Sprache: {session_data['language']}\n")
                f.write("\n")
            
            # Transkript
            f.write("TRANSKRIPT:\n")
            f.write("-" * 30 + "\n")
            f.write(transcript_text)
            f.write("\n\n")
            
            # Marker-Zusammenfassung falls verfügbar
            if session_data and 'markers_summary' in session_data:
                f.write("MARKER-ZUSAMMENFASSUNG:\n")
                f.write("-" * 30 + "\n")
                markers = session_data['markers_summary']
                
                if 'emotions' in markers:
                    f.write("Emotionen:\n")
                    for emotion, percentage in markers['emotions'].items():
                        f.write(f"  - {emotion.capitalize()}: {percentage:.1f}%\n")
                    f.write("\n")
                
                if 'pauses' in markers:
                    f.write("Pausen-Statistiken:\n")
                    f.write(f"  - Anzahl Pausen: {markers['pauses'].get('count', 0)}\n")
                    f.write(f"  - Durchschnittliche Pause: {markers['pauses'].get('avg_duration', 0):.1f}s\n")
                    f.write(f"  - Längste Pause: {markers['pauses'].get('max_duration', 0):.1f}s\n")
                    f.write("\n")
                
                if 'prosody' in markers:
                    f.write("Prosodische Features:\n")
                    f.write(f"  - Durchschnittliche Tonhöhe: {markers['prosody'].get('avg_pitch', 0):.0f} Hz\n")
                    f.write(f"  - Durchschnittliche Energie: {markers['prosody'].get('avg_energy', 0):.3f}\n")
                    f.write("\n")
        
        return filepath
    
    def export_to_markdown(self, transcript_text: str, session_data: Optional[Dict] = None,
                          filename: Optional[str] = None) -> str:
        """
        Transkript als Markdown-Datei exportieren
        
        Args:
            transcript_text: Der Transkriptionstext
            session_data: Optionale Sitzungsdaten mit Markern
            filename: Optionaler Dateiname
            
        Returns:
            Pfad zur erstellten Datei
        """
        if filename is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"transkript_{timestamp}.md"
        
        filepath = os.path.join(self.export_dir, filename)
        
        with open(filepath, 'w', encoding='utf-8') as f:
            # Header
            f.write("# TransRapport MVP - Transkript Export\n\n")
            f.write(f"**Exportiert am:** {datetime.now().strftime('%d.%m.%Y um %H:%M:%S')}\n\n")
            
            # Sitzungsinfo falls verfügbar
            if session_data:
                f.write("## Sitzungsinformationen\n\n")
                if 'start_time' in session_data:
                    f.write(f"- **Sitzungsbeginn:** {session_data['start_time']}\n")
                if 'duration' in session_data:
                    f.write(f"- **Dauer:** {session_data['duration']}\n")
                if 'language' in session_data:
                    f.write(f"- **Sprache:** {session_data['language']}\n")
                f.write("\n")
            
            # Transkript
            f.write("## Transkript\n\n")
            f.write("```\n")
            f.write(transcript_text)
            f.write("\n```\n\n")
            
            # Marker-Analyse falls verfügbar
            if session_data and 'markers_summary' in session_data:
                f.write("## Therapeutische Marker-Analyse\n\n")
                markers = session_data['markers_summary']
                
                # Emotionen
                if 'emotions' in markers:
                    f.write("### Emotionsverlauf\n\n")
                    f.write("| Emotion | Anteil |\n")
                    f.write("|---------|--------|\n")
                    for emotion, percentage in sorted(markers['emotions'].items(), 
                                                    key=lambda x: x[1], reverse=True):
                        f.write(f"| {emotion.capitalize()} | {percentage:.1f}% |\n")
                    f.write("\n")
                
                # Pausen
                if 'pauses' in markers:
                    f.write("### Pausen-Analyse\n\n")
                    f.write("| Metrik | Wert |\n")
                    f.write("|--------|------|\n")
                    f.write(f"| Anzahl Pausen | {markers['pauses'].get('count', 0)} |\n")
                    f.write(f"| Durchschnittliche Pause | {markers['pauses'].get('avg_duration', 0):.1f}s |\n")
                    f.write(f"| Längste Pause | {markers['pauses'].get('max_duration', 0):.1f}s |\n")
                    f.write("\n")
                
                # Prosodische Features
                if 'prosody' in markers:
                    f.write("### Prosodische Features\n\n")
                    f.write("| Feature | Wert |\n")
                    f.write("|---------|------|\n")
                    f.write(f"| Durchschnittliche Tonhöhe | {markers['prosody'].get('avg_pitch', 0):.0f} Hz |\n")
                    f.write(f"| Durchschnittliche Energie | {markers['prosody'].get('avg_energy', 0):.3f} |\n")
                    if 'pitch_stability' in markers['prosody']:
                        f.write(f"| Tonhöhen-Stabilität | {markers['prosody']['pitch_stability']:.2f} |\n")
                    if 'energy_stability' in markers['prosody']:
                        f.write(f"| Energie-Stabilität | {markers['prosody']['energy_stability']:.2f} |\n")
                    f.write("\n")
                
                # Therapeutische Interpretation
                f.write("### Therapeutische Hinweise\n\n")
                f.write(self._generate_therapeutic_insights(markers))
        
        return filepath
    
    def _generate_therapeutic_insights(self, markers: Dict) -> str:
        """Generiert therapeutische Hinweise basierend auf Markern"""
        insights = []
        
        # Emotionsanalyse
        if 'emotions' in markers:
            emotions = markers['emotions']
            dominant_emotion = max(emotions.items(), key=lambda x: x[1])
            
            if dominant_emotion[1] > 50:
                insights.append(f"**Dominante Emotion:** {dominant_emotion[0].capitalize()} "
                              f"({dominant_emotion[1]:.1f}% der Sitzung)")
            
            negative_emotions = sum(emotions.get(e, 0) for e in ['sad', 'angry', 'anxious'])
            if negative_emotions > 40:
                insights.append("**Hinweis:** Erhöhter Anteil negativer Emotionen erkannt")
        
        # Pausen-Analyse
        if 'pauses' in markers:
            pauses = markers['pauses']
            avg_pause = pauses.get('avg_duration', 0)
            max_pause = pauses.get('max_duration', 0)
            
            if avg_pause > 2.0:
                insights.append("**Sprechverhalten:** Längere Pausen könnten auf Nachdenklichkeit "
                              "oder emotionale Verarbeitung hindeuten")
            
            if max_pause > 5.0:
                insights.append(f"**Auffällige Pause:** Sehr lange Pause von {max_pause:.1f}s erkannt")
        
        # Prosodische Auffälligkeiten
        if 'prosody' in markers:
            prosody = markers['prosody']
            
            if prosody.get('pitch_stability', 1.0) < 0.3:
                insights.append("**Stimmverhalten:** Unregelmäßige Tonhöhe könnte auf emotionale "
                              "Erregung hindeuten")
            
            if prosody.get('avg_energy', 0) < 0.1:
                insights.append("**Stimmverhalten:** Niedrige Sprechenergie erkannt")
        
        if not insights:
            insights.append("Keine besonderen Auffälligkeiten in den therapeutischen Markern erkannt.")
        
        return "\n".join(f"- {insight}" for insight in insights) + "\n"
    
    def get_export_directory(self) -> str:
        """Gibt das Export-Verzeichnis zurück"""
        return os.path.abspath(self.export_dir)
