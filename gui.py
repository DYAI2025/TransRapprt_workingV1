
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
TransRapport MVP - Hauptbenutzeroberfläche
Therapeutenfreundliche, minimalistische GUI mit Live-Transkription
"""

import sys
from PyQt6.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
                            QLabel, QPushButton, QComboBox, QTextEdit, 
                            QGroupBox, QStatusBar, QMessageBox, QProgressBar,
                            QSplitter, QFrame, QMenuBar, QMenu, QFileDialog,
                            QDialog, QListWidget, QListWidgetItem, QDialogButtonBox,
                            QLineEdit, QTextBrowser)
from PyQt6.QtCore import Qt, QTimer, pyqtSignal, QThread, pyqtSlot
from PyQt6.QtGui import QFont, QIcon, QPalette, QColor, QTextCursor, QAction
import pyqtgraph as pg
import numpy as np
from audio import AudioManager
from live_transcriber import LiveTranscriber
from exporter import TranscriptExporter
from session_manager import SessionManager
import configparser
import os
from datetime import datetime

class TransRapportMainWindow(QMainWindow):
    """Hauptfenster der TransRapport Anwendung mit Live-Transkription"""
    
    def __init__(self):
        super().__init__()
        self.audio_manager = AudioManager()
        self.live_transcriber = LiveTranscriber()
        self.is_recording = False
        
        # Export und Session Management
        self.exporter = TranscriptExporter()
        self.session_manager = SessionManager()
        self.current_session = None
        
        # Konfiguration laden
        self.load_config()
        
        # GUI initialisieren
        self.init_ui()
        
        # Audio-Geräte laden
        self.refresh_audio_devices()
        
        # Live-Transcriber Signale verbinden
        self.setup_transcriber_signals()
        
        # Timer für Audio-Level-Anzeige
        self.audio_level_timer = QTimer()
        self.audio_level_timer.timeout.connect(self.update_audio_level)
        
        # Marker-Daten für Visualisierung
        self.marker_data = {
            'timestamps': [],
            'emotions': [],
            'pauses': [],
            'pitch': [],
            'energy': []
        }
        self.max_data_points = 100  # Maximale Anzahl Datenpunkte für Visualisierung
        
        # Plot-Update-Konfiguration
        self.plot_update_rate = 100  # Millisekunden (10 Hz) (important-comment)
        self.last_plot_update = datetime.now()
        self.plot_enabled = True  # Toggle für Plot-System (important-comment)
        
    def load_config(self):
        """Konfiguration aus config.ini laden"""
        self.config = configparser.ConfigParser()
        config_path = os.path.join(os.path.dirname(__file__), 'config.ini')
        
        if os.path.exists(config_path):
            self.config.read(config_path)
        else:
            # Standard-Konfiguration erstellen
            self.config['DEFAULT'] = {
                'language': 'de',
                'sample_rate': '16000',
                'theme': 'light',
                'model_size': 'base'
            }
            with open(config_path, 'w') as f:
                self.config.write(f)
    
    def setup_transcriber_signals(self):
        """Live-Transcriber Signale mit GUI verbinden"""
        self.live_transcriber.transcription_ready.connect(self.on_transcription_ready)
        self.live_transcriber.partial_transcription.connect(self.on_partial_transcription)
        self.live_transcriber.error_occurred.connect(self.on_transcription_error)
        
        # Marker-System Signale
        self.live_transcriber.markers_updated.connect(self.on_markers_updated)
        self.live_transcriber.emotion_detected.connect(self.on_emotion_detected)
        self.live_transcriber.pause_detected.connect(self.on_pause_detected)
        self.live_transcriber.prosody_updated.connect(self.on_prosody_updated)
    
    def init_ui(self):
        """Benutzeroberfläche initialisieren"""
        self.setWindowTitle("TransRapport MVP - Live-Transkription für Therapeuten")
        self.setMinimumSize(900, 700)
        self.resize(1100, 800)
        
        # KRITISCHER FIX: Dark Theme erzwingen für Lesbarkeit
        self.setStyleSheet("""
            QMainWindow {
                background-color: #2b2b2b;
                color: #ffffff;
            }
            QWidget {
                background-color: #2b2b2b;
                color: #ffffff;
            }
            QTextEdit {
                background-color: #1e1e1e;
                color: #ffffff;
                border: 2px solid #555;
                font-size: 14px;
                padding: 10px;
            }
            QLabel {
                color: #ffffff;
                font-size: 12px;
            }
            QPushButton {
                background-color: #0d7377;
                color: white;
                border: none;
                padding: 12px 24px;
                border-radius: 6px;
                font-size: 14px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #14a085;
            }
            QPushButton:pressed {
                background-color: #0a5d61;
            }
            QComboBox {
                background-color: #3c3c3c;
                color: #ffffff;
                border: 2px solid #555;
                padding: 8px;
                font-size: 12px;
            }
            QComboBox:drop-down {
                border: none;
            }
            QComboBox::down-arrow {
                border: none;
                color: #ffffff;
            }
            QGroupBox {
                font-weight: bold;
                font-size: 14px;
                color: #ffffff;
                border: 2px solid #555;
                border-radius: 8px;
                margin-top: 10px;
                padding-top: 10px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px 0 5px;
                color: #ffffff;
            }
            QProgressBar {
                border: 2px solid #555;
                border-radius: 5px;
                background-color: #1e1e1e;
            }
            QProgressBar::chunk {
                background-color: #0d7377;
                border-radius: 3px;
            }
        """)
        
        # Menüleiste erstellen
        self.create_menu_bar()
        
        # Zentrales Widget mit Splitter für Marker-Visualisierung
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # Hauptlayout
        main_layout = QVBoxLayout(central_widget)
        main_layout.setSpacing(10)
        main_layout.setContentsMargins(20, 20, 20, 20)
        
        # Splitter für Hauptinhalt und Marker-Visualisierung
        main_splitter = QSplitter(Qt.Orientation.Horizontal)
        main_layout.addWidget(main_splitter)
        
        # Linke Seite: Bestehende GUI
        left_widget = QWidget()
        left_layout = QVBoxLayout(left_widget)
        left_layout.setSpacing(20)
        left_layout.setContentsMargins(0, 0, 0, 0)
        main_splitter.addWidget(left_widget)
        
        # Titel
        title_label = QLabel("TransRapport MVP")
        title_font = QFont()
        title_font.setPointSize(24)
        title_font.setBold(True)
        title_label.setFont(title_font)
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title_label.setStyleSheet("color: #2c3e50; margin-bottom: 10px;")
        left_layout.addWidget(title_label)
        
        # Untertitel
        subtitle_label = QLabel("Live-Transkription mit Whisper (Offline)")
        subtitle_font = QFont()
        subtitle_font.setPointSize(12)
        subtitle_label.setFont(subtitle_font)
        subtitle_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        subtitle_label.setStyleSheet("color: #7f8c8d; margin-bottom: 20px;")
        left_layout.addWidget(subtitle_label)
        
        # Einstellungen Gruppe
        settings_group = QGroupBox("Einstellungen")
        settings_group.setStyleSheet("""
            QGroupBox {
                font-weight: bold;
                font-size: 14px;
                color: #2c3e50;
                border: 2px solid #bdc3c7;
                border-radius: 8px;
                margin-top: 10px;
                padding-top: 10px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px 0 5px;
            }
        """)
        settings_layout = QVBoxLayout(settings_group)
        
        # Mikrofon-Auswahl
        mic_layout = QHBoxLayout()
        mic_label = QLabel("Mikrofon:")
        mic_label.setMinimumWidth(100)
        self.mic_combo = QComboBox()
        self.mic_combo.setMinimumHeight(35)
        self.mic_combo.setStyleSheet("""
            QComboBox {
                padding: 5px;
                border: 1px solid #bdc3c7;
                border-radius: 4px;
                font-size: 12px;
            }
        """)
        
        refresh_btn = QPushButton("Aktualisieren")
        refresh_btn.setMaximumWidth(120)
        refresh_btn.setStyleSheet("""
            QPushButton {
                background-color: #3498db;
                color: white;
                border: none;
                padding: 8px 16px;
                border-radius: 4px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #2980b9;
            }
        """)
        refresh_btn.clicked.connect(self.refresh_audio_devices)
        
        mic_layout.addWidget(mic_label)
        mic_layout.addWidget(self.mic_combo, 1)
        mic_layout.addWidget(refresh_btn)
        settings_layout.addLayout(mic_layout)
        
        # Sprach- und Modell-Auswahl
        lang_model_layout = QHBoxLayout()
        
        # Sprache
        lang_label = QLabel("Sprache:")
        lang_label.setMinimumWidth(100)
        self.lang_combo = QComboBox()
        self.lang_combo.addItems(["Deutsch", "Englisch", "Auto-Erkennung"])
        self.lang_combo.setCurrentText("Deutsch")
        self.lang_combo.currentTextChanged.connect(self.on_language_changed)
        
        # Modell-Größe
        model_label = QLabel("Modell:")
        model_label.setMinimumWidth(80)
        self.model_combo = QComboBox()
        self.model_combo.addItems(["tiny", "base", "small", "medium"])
        self.model_combo.setCurrentText("base")
        self.model_combo.currentTextChanged.connect(self.on_model_changed)
        
        lang_model_layout.addWidget(lang_label)
        lang_model_layout.addWidget(self.lang_combo, 1)
        lang_model_layout.addWidget(model_label)
        lang_model_layout.addWidget(self.model_combo, 1)
        settings_layout.addLayout(lang_model_layout)
        
        left_layout.addWidget(settings_group)
        
        # Aufnahme-Steuerung
        control_layout = QHBoxLayout()
        
        self.record_btn = QPushButton("Live-Transkription starten")
        self.record_btn.setMinimumHeight(50)
        self.record_btn.setStyleSheet("""
            QPushButton {
                background-color: #27ae60;
                color: white;
                border: none;
                padding: 15px 30px;
                border-radius: 8px;
                font-size: 16px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #229954;
            }
            QPushButton:pressed {
                background-color: #1e8449;
            }
        """)
        self.record_btn.clicked.connect(self.toggle_recording)
        
        # Status und Audio-Level
        status_layout = QVBoxLayout()
        self.status_label = QLabel("Bereit")
        self.status_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.status_label.setStyleSheet("""
            QLabel {
                color: #27ae60;
                font-size: 14px;
                font-weight: bold;
                padding: 5px;
            }
        """)
        
        # Audio-Level Anzeige
        self.audio_level_bar = QProgressBar()
        self.audio_level_bar.setMaximum(100)
        self.audio_level_bar.setValue(0)
        self.audio_level_bar.setTextVisible(False)
        self.audio_level_bar.setMaximumHeight(10)
        self.audio_level_bar.setStyleSheet("""
            QProgressBar {
                border: 1px solid #bdc3c7;
                border-radius: 5px;
                background-color: #ecf0f1;
            }
            QProgressBar::chunk {
                background-color: #27ae60;
                border-radius: 4px;
            }
        """)
        
        status_layout.addWidget(self.status_label)
        status_layout.addWidget(QLabel("Audio-Pegel:"))
        status_layout.addWidget(self.audio_level_bar)
        
        control_layout.addWidget(self.record_btn, 2)
        control_layout.addLayout(status_layout, 1)
        
        left_layout.addLayout(control_layout)
        
        # Transkriptions-Ausgabe
        transcript_group = QGroupBox("Live-Transkription")
        transcript_group.setStyleSheet("""
            QGroupBox {
                font-weight: bold;
                font-size: 14px;
                color: #2c3e50;
                border: 2px solid #bdc3c7;
                border-radius: 8px;
                margin-top: 10px;
                padding-top: 10px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px 0 5px;
            }
        """)
        transcript_layout = QVBoxLayout(transcript_group)
        
        # Transkriptions-Textfeld
        self.transcript_text = QTextEdit()
        self.transcript_text.setMinimumHeight(350)
        self.transcript_text.setStyleSheet("""
            QTextEdit {
                background-color: #1e1e1e;
                color: #ffffff;
                border: 1px solid #555555;
                border-radius: 4px;
                padding: 10px;
                font-size: 13px;
                line-height: 1.5;
                font-family: 'Segoe UI', Arial, sans-serif;
            }
        """)
        self.transcript_text.setPlaceholderText("Die Live-Transkription wird hier angezeigt...\n\nHinweis: Beim ersten Start wird das Whisper-Modell heruntergeladen.")
        
        # Transkriptions-Steuerung
        transcript_controls = QHBoxLayout()
        
        clear_btn = QPushButton("Text löschen")
        clear_btn.setStyleSheet("""
            QPushButton {
                background-color: #e74c3c;
                color: white;
                border: none;
                padding: 8px 16px;
                border-radius: 4px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #c0392b;
            }
        """)
        clear_btn.clicked.connect(self.clear_transcript)
        
        save_btn = QPushButton("Speichern")
        save_btn.setStyleSheet("""
            QPushButton {
                background-color: #3498db;
                color: white;
                border: none;
                padding: 8px 16px;
                border-radius: 4px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #2980b9;
            }
        """)
        save_btn.clicked.connect(self.save_transcript)
        
        # Sessions-Button hinzufügen
        sessions_btn = QPushButton("Gespeicherte Sessions")
        sessions_btn.setStyleSheet("""
            QPushButton {
                background-color: #8e44ad;
                color: white;
                border: none;
                padding: 8px 16px;
                border-radius: 4px;
                font-size: 12px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #9b59b6;
            }
        """)
        sessions_btn.clicked.connect(self.show_saved_sessions)
        
        transcript_controls.addWidget(clear_btn)
        transcript_controls.addWidget(save_btn)
        transcript_controls.addWidget(sessions_btn)
        transcript_controls.addStretch()
        
        transcript_layout.addWidget(self.transcript_text)
        transcript_layout.addLayout(transcript_controls)
        left_layout.addWidget(transcript_group, 1)
        
        # Rechte Seite: Marker-Visualisierung
        self.setup_marker_visualization(main_splitter)
        
        # Splitter-Verhältnis setzen (70% links, 30% rechts)
        main_splitter.setSizes([700, 300])
        
        # Statusleiste
        self.statusBar().showMessage("TransRapport MVP bereit - Whisper Live-Transkription")
        
        # ENTFERNT: Styling überschreibt Dark Theme
        # self.setStyleSheet("""
        #     QMainWindow {
        #         background-color: #ecf0f1;
        #     }
        # """)
    
    def setup_marker_visualization(self, parent_splitter):
        """Marker-Visualisierung einrichten"""
        # Rechtes Widget für Marker-Visualisierung
        right_widget = QWidget()
        right_layout = QVBoxLayout(right_widget)
        right_layout.setContentsMargins(10, 0, 0, 0)
        
        # Marker-Gruppe
        marker_group = QGroupBox("Therapeutische Marker (ATO→SEM)")
        marker_group.setStyleSheet("""
            QGroupBox {
                font-weight: bold;
                font-size: 14px;
                color: #2c3e50;
                border: 2px solid #bdc3c7;
                border-radius: 8px;
                margin-top: 10px;
                padding-top: 10px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px 0 5px;
            }
        """)
        marker_layout = QVBoxLayout(marker_group)
        
        # Aktuelle Emotion Anzeige
        emotion_frame = QFrame()
        emotion_frame.setFrameStyle(QFrame.Shape.Box)
        emotion_frame.setStyleSheet("background-color: #ffffff; border-radius: 4px; padding: 5px;")
        emotion_layout = QVBoxLayout(emotion_frame)
        
        emotion_title = QLabel("Aktuelle Emotion:")
        emotion_title.setFont(QFont("Arial", 10, QFont.Weight.Bold))
        self.current_emotion_label = QLabel("neutral")
        self.current_emotion_label.setFont(QFont("Arial", 12))
        self.current_emotion_label.setStyleSheet("color: #2c3e50; padding: 5px;")
        
        self.emotion_confidence_bar = QProgressBar()
        self.emotion_confidence_bar.setMaximum(100)
        self.emotion_confidence_bar.setValue(0)
        self.emotion_confidence_bar.setMaximumHeight(8)
        self.emotion_confidence_bar.setStyleSheet("""
            QProgressBar {
                border: 1px solid #bdc3c7;
                border-radius: 4px;
                background-color: #ecf0f1;
            }
            QProgressBar::chunk {
                background-color: #3498db;
                border-radius: 3px;
            }
        """)
        
        emotion_layout.addWidget(emotion_title)
        emotion_layout.addWidget(self.current_emotion_label)
        emotion_layout.addWidget(self.emotion_confidence_bar)
        marker_layout.addWidget(emotion_frame)
        
        # Pause-Anzeige
        pause_frame = QFrame()
        pause_frame.setFrameStyle(QFrame.Shape.Box)
        pause_frame.setStyleSheet("background-color: #ffffff; border-radius: 4px; padding: 5px;")
        pause_layout = QVBoxLayout(pause_frame)
        
        pause_title = QLabel("Letzte Pause:")
        pause_title.setFont(QFont("Arial", 10, QFont.Weight.Bold))
        self.current_pause_label = QLabel("0.0s")
        self.current_pause_label.setFont(QFont("Arial", 12))
        self.current_pause_label.setStyleSheet("color: #2c3e50; padding: 5px;")
        
        pause_layout.addWidget(pause_title)
        pause_layout.addWidget(self.current_pause_label)
        marker_layout.addWidget(pause_frame)
        
        # PyQtGraph Plots für Live-Visualisierung
        pg.setConfigOptions(antialias=True)
        
        # Emotion Timeline
        self.emotion_plot = pg.PlotWidget(title="Emotionsverlauf")
        self.emotion_plot.setLabel('left', 'Valenz')
        self.emotion_plot.setLabel('bottom', 'Zeit (s)')
        self.emotion_plot.setMaximumHeight(120)
        self.emotion_plot.setYRange(-1, 1)
        self.emotion_curve = self.emotion_plot.plot(pen='b', width=2)
        marker_layout.addWidget(self.emotion_plot)
        
        # Prosody Plots
        prosody_splitter = QSplitter(Qt.Orientation.Vertical)
        
        # Pitch Plot
        self.pitch_plot = pg.PlotWidget(title="Tonhöhe (Pitch)")
        self.pitch_plot.setLabel('left', 'Hz')
        self.pitch_plot.setLabel('bottom', 'Zeit (s)')
        self.pitch_plot.setMaximumHeight(100)
        self.pitch_curve = self.pitch_plot.plot(pen='g', width=2)
        prosody_splitter.addWidget(self.pitch_plot)
        
        # Energy Plot
        self.energy_plot = pg.PlotWidget(title="Energie")
        self.energy_plot.setLabel('left', 'RMS')
        self.energy_plot.setLabel('bottom', 'Zeit (s)')
        self.energy_plot.setMaximumHeight(100)
        self.energy_curve = self.energy_plot.plot(pen='r', width=2)
        prosody_splitter.addWidget(self.energy_plot)
        
        marker_layout.addWidget(prosody_splitter)
        
        # Marker-Statistiken
        stats_frame = QFrame()
        stats_frame.setFrameStyle(QFrame.Shape.Box)
        stats_frame.setStyleSheet("background-color: #ffffff; border-radius: 4px; padding: 5px;")
        stats_layout = QVBoxLayout(stats_frame)
        
        stats_title = QLabel("Session-Statistiken:")
        stats_title.setFont(QFont("Arial", 10, QFont.Weight.Bold))
        self.stats_label = QLabel("Noch keine Daten...")
        self.stats_label.setFont(QFont("Arial", 9))
        self.stats_label.setStyleSheet("color: #7f8c8d;")
        self.stats_label.setWordWrap(True)
        
        stats_layout.addWidget(stats_title)
        stats_layout.addWidget(self.stats_label)
        marker_layout.addWidget(stats_frame)
        
        right_layout.addWidget(marker_group)
        parent_splitter.addWidget(right_widget)
    
    def create_menu_bar(self):
        """Menüleiste erstellen"""
        menubar = self.menuBar()
        
        # Datei-Menü
        file_menu = menubar.addMenu('Datei')
        
        # Neue Sitzung
        new_session_action = QAction('Neue Sitzung', self)
        new_session_action.setShortcut('Ctrl+N')
        new_session_action.triggered.connect(self.new_session)
        file_menu.addAction(new_session_action)
        
        # Sitzung laden
        load_session_action = QAction('Sitzung laden...', self)
        load_session_action.setShortcut('Ctrl+O')
        load_session_action.triggered.connect(self.load_session_dialog)
        file_menu.addAction(load_session_action)
        
        # Sitzung speichern
        save_session_action = QAction('Sitzung speichern', self)
        save_session_action.setShortcut('Ctrl+S')
        save_session_action.triggered.connect(self.save_current_session)
        file_menu.addAction(save_session_action)
        
        file_menu.addSeparator()
        
        # Export-Menü
        export_menu = file_menu.addMenu('Exportieren')
        
        # Als Text exportieren
        export_txt_action = QAction('Als Text (.txt)', self)
        export_txt_action.triggered.connect(lambda: self.export_transcript('txt'))
        export_menu.addAction(export_txt_action)
        
        # Als Markdown exportieren
        export_md_action = QAction('Als Markdown (.md)', self)
        export_md_action.triggered.connect(lambda: self.export_transcript('md'))
        export_menu.addAction(export_md_action)
        
        file_menu.addSeparator()
        
        # Beenden
        exit_action = QAction('Beenden', self)
        exit_action.setShortcut('Ctrl+Q')
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)
        
        # Ansicht-Menü
        view_menu = menubar.addMenu('Ansicht')
        
        # Export-Ordner öffnen
        open_exports_action = QAction('Export-Ordner öffnen', self)
        open_exports_action.triggered.connect(self.open_exports_folder)
        view_menu.addAction(open_exports_action)
        
        # Sessions-Ordner öffnen
        open_sessions_action = QAction('Sessions-Ordner öffnen', self)
        open_sessions_action.triggered.connect(self.open_sessions_folder)
        view_menu.addAction(open_sessions_action)
        
        # Hilfe-Menü
        help_menu = menubar.addMenu('Hilfe')
        
        # Über
        about_action = QAction('Über TransRapport MVP', self)
        about_action.triggered.connect(self.show_about)
        help_menu.addAction(about_action)
    
    def refresh_audio_devices(self):
        """Audio-Geräte aktualisieren"""
        try:
            devices = self.audio_manager.get_input_devices()
            self.mic_combo.clear()
            
            if not devices:
                self.mic_combo.addItem("Kein Mikrofon gefunden")
                self.record_btn.setEnabled(False)
                self.statusBar().showMessage("Warnung: Kein Mikrofon gefunden")
            else:
                # Geräte hinzufügen und intelligente Standardauswahl
                preferred_combo_index = 0
                for combo_index, device in enumerate(devices):
                    self.mic_combo.addItem(f"{device['name']} ({device['channels']} Kanäle)")
                    
                    # MacBook Air-Mikrofon oder echte Mikrofone bevorzugen (nicht BlackHole)
                    if "MacBook" in device['name'] or "Built-in" in device['name']:
                        preferred_combo_index = combo_index
                        print(f"🎤 Echtes Mikrofon erkannt: {device['name']} (Combo-Index {combo_index}, Device-Index {device['index']})")
                    elif "BlackHole" in device['name'] or "virtual" in device['name'].lower():
                        print(f"🚫 Virtuelles Gerät übersprungen: {device['name']} (Combo-Index {combo_index}, Device-Index {device['index']})")
                
                # Intelligente Standardauswahl setzen
                self.mic_combo.setCurrentIndex(preferred_combo_index)
                self.record_btn.setEnabled(True)
                self.statusBar().showMessage(f"{len(devices)} Mikrofon(e) gefunden - Standard: {devices[preferred_combo_index]['name']}")
                
        except Exception as e:
            QMessageBox.warning(self, "Fehler", f"Fehler beim Laden der Audio-Geräte:\n{str(e)}")
    
    def on_language_changed(self, language_text):
        """Sprache geändert"""
        lang_map = {
            "Deutsch": "de",
            "Englisch": "en", 
            "Auto-Erkennung": "auto"
        }
        language = lang_map.get(language_text, "de")
        self.live_transcriber.change_language(language)
    
    def on_model_changed(self, model_size):
        """Modell-Größe geändert"""
        if not self.is_recording:  # Nur wenn nicht aufgenommen wird
            self.live_transcriber.change_model_size(model_size)
    
    def toggle_recording(self):
        """Live-Transkription starten/stoppen"""
        if not self.is_recording:
            self.start_recording()
        else:
            self.stop_recording()
    
    def start_recording(self):
        """Live-Transkription starten"""
        try:
            selected_combo_index = self.mic_combo.currentIndex()
            if selected_combo_index < 0:
                QMessageBox.warning(self, "Fehler", "Bitte wählen Sie ein Mikrofon aus.")
                return
            
            # KRITISCHER FIX: Echten sounddevice-Index verwenden
            devices = self.audio_manager.get_input_devices()
            if selected_combo_index >= len(devices):
                QMessageBox.warning(self, "Fehler", "Ungültiges Mikrofon ausgewählt.")
                return
            
            # Echten sounddevice-Index verwenden, nicht Dropdown-Index
            selected_device = devices[selected_combo_index]['index']
            print(f"🎤 Dropdown-Index: {selected_combo_index} → Echter Device-Index: {selected_device}")
            
            # Prüfen ob Whisper-Modell verfügbar
            if not self.live_transcriber.is_model_available():
                QMessageBox.warning(self, "Fehler", "Whisper-Modell nicht verfügbar. Bitte warten Sie, bis das Modell geladen ist.")
                return
            
            # Neue Sitzung starten falls keine vorhanden
            if not self.current_session:
                self.current_session = self.session_manager.create_session()
                self.setWindowTitle(f"TransRapport MVP - {self.current_session['name']}")
            
            # Sitzung starten
            self.current_session = self.session_manager.start_session(self.current_session)
            
            # Audio-Stream starten mit Fallback auf andere Geräte
            try:
                self.audio_manager.start_recording(selected_device)
            except Exception as audio_error:
                print(f"⚠️  Primäres Gerät fehlgeschlagen, versuche Fallback...")
                
                # Fallback: Versuche andere verfügbare Geräte
                devices = self.audio_manager.get_input_devices()
                for fallback_index, device in enumerate(devices):
                    if fallback_index != selected_device:
                        try:
                            print(f"🔄 Fallback-Versuch mit Gerät {fallback_index}: {device['name']}")
                            self.audio_manager.start_recording(fallback_index)
                            self.statusBar().showMessage(f"Fallback: {device['name']} verwendet")
                            break
                        except Exception as fallback_error:
                            print(f"❌ Fallback-Gerät {fallback_index} fehlgeschlagen: {fallback_error}")
                            continue
                else:
                    # Alle Geräte fehlgeschlagen
                    raise Exception(f"Alle verfügbaren Audio-Geräte fehlgeschlagen. Ursprünglicher Fehler: {audio_error}")
            
            # Live-Transkription starten
            success = self.live_transcriber.start_transcription(self.audio_manager)
            
            if not success:
                self.audio_manager.stop_recording()
                return
            
            # UI aktualisieren
            self.is_recording = True
            self.record_btn.setText("Live-Transkription stoppen")
            self.record_btn.setStyleSheet("""
                QPushButton {
                    background-color: #e74c3c;
                    color: white;
                    border: none;
                    padding: 15px 30px;
                    border-radius: 8px;
                    font-size: 16px;
                    font-weight: bold;
                }
                QPushButton:hover {
                    background-color: #c0392b;
                }
            """)
            self.status_label.setText("Live-Transkription läuft...")
            self.status_label.setStyleSheet("""
                QLabel {
                    color: #e74c3c;
                    font-size: 14px;
                    font-weight: bold;
                    padding: 5px;
                }
            """)
            self.statusBar().showMessage("Live-Transkription gestartet")
            
            # Audio-Level Timer starten
            self.audio_level_timer.start(100)  # Alle 100ms aktualisieren
            
            # Einstellungen während Aufnahme sperren
            self.mic_combo.setEnabled(False)
            self.model_combo.setEnabled(False)
            
        except Exception as e:
            QMessageBox.critical(self, "Fehler", f"Fehler beim Starten der Live-Transkription:\n{str(e)}")
    
    def stop_recording(self):
        """Live-Transkription stoppen"""
        try:
            # Audio-Stream stoppen
            self.audio_manager.stop_recording()
            
            # Live-Transkription stoppen
            self.live_transcriber.stop_transcription()
            
            # Audio-Level Timer stoppen
            self.audio_level_timer.stop()
            self.audio_level_bar.setValue(0)
            
            # UI aktualisieren
            self.is_recording = False
            self.record_btn.setText("Live-Transkription starten")
            self.record_btn.setStyleSheet("""
                QPushButton {
                    background-color: #27ae60;
                    color: white;
                    border: none;
                    padding: 15px 30px;
                    border-radius: 8px;
                    font-size: 16px;
                    font-weight: bold;
                }
                QPushButton:hover {
                    background-color: #229954;
                }
            """)
            self.status_label.setText("Bereit")
            self.status_label.setStyleSheet("""
                QLabel {
                    color: #27ae60;
                    font-size: 14px;
                    font-weight: bold;
                    padding: 5px;
                }
            """)
            self.statusBar().showMessage("Live-Transkription gestoppt")
            
            # Einstellungen wieder freigeben
            self.mic_combo.setEnabled(True)
            self.model_combo.setEnabled(True)
            
        except Exception as e:
            QMessageBox.critical(self, "Fehler", f"Fehler beim Stoppen der Live-Transkription:\n{str(e)}")
    
    def update_audio_level(self):
        """Audio-Pegel aktualisieren"""
        if self.is_recording:
            level = self.audio_manager.get_audio_level()
            self.audio_level_bar.setValue(int(level * 100))
    
    def on_transcription_ready(self, text):
        """Neue Transkription empfangen"""
        if text.strip():
            # Zeitstempel hinzufügen
            timestamp = datetime.now().strftime("%H:%M:%S")
            formatted_text = f"[{timestamp}] {text}\n"
            
            # Text zum Transkriptionsfeld hinzufügen
            self.transcript_text.append(formatted_text)
            
            # Automatisch nach unten scrollen
            cursor = self.transcript_text.textCursor()
            cursor.movePosition(QTextCursor.MoveOperation.End)
            self.transcript_text.setTextCursor(cursor)
    
    def on_partial_transcription(self, text):
        """Partielle Transkription empfangen (optional für Echtzeit-Feedback)"""
        # Könnte für Live-Vorschau verwendet werden
        pass
    
    def on_transcription_error(self, error_msg):
        """Transkriptionsfehler behandeln"""
        self.statusBar().showMessage(f"Transkriptionsfehler: {error_msg}")
        print(f"Transkriptionsfehler: {error_msg}")
    
    def on_markers_updated(self, markers):
        """Marker-Daten aktualisiert"""
        if not markers or 'timestamp' not in markers:
            return
        
        # Zeitstempel für X-Achse
        current_time = len(self.marker_data['timestamps'])
        self.marker_data['timestamps'].append(current_time)
        
        # Daten-Arrays begrenzen
        if len(self.marker_data['timestamps']) > self.max_data_points:
            for key in self.marker_data:
                self.marker_data[key] = self.marker_data[key][-self.max_data_points:]
        
        # Emotion-Daten
        if 'affect' in markers:
            valence = markers['affect'].get('valence', 0.0)
            self.marker_data['emotions'].append(valence)
        
        # Prosody-Daten
        if 'prosody' in markers:
            pitch = markers['prosody'].get('pitch_mean', 0.0)
            energy = markers['prosody'].get('energy_mean', 0.0)
            self.marker_data['pitch'].append(pitch)
            self.marker_data['energy'].append(energy)
        
        # Plots aktualisieren (mit Throttling) (important-comment)
        self.update_marker_plots()
        
        # Statistiken aktualisieren
        self.update_marker_statistics()
    
    def on_emotion_detected(self, emotion, confidence):
        """Neue Emotion erkannt"""
        # Emotion-Label aktualisieren
        emotion_colors = {
            'happy': '#27ae60',
            'sad': '#3498db', 
            'angry': '#e74c3c',
            'excited': '#f39c12',
            'calm': '#9b59b6',
            'anxious': '#e67e22',
            'neutral': '#95a5a6'
        }
        
        color = emotion_colors.get(emotion, '#95a5a6')
        self.current_emotion_label.setText(emotion.capitalize())
        self.current_emotion_label.setStyleSheet(f"color: {color}; padding: 5px; font-weight: bold;")
        
        # Confidence-Bar aktualisieren
        self.emotion_confidence_bar.setValue(int(confidence * 100))
    
    def on_pause_detected(self, pause_duration):
        """Pause erkannt"""
        self.current_pause_label.setText(f"{pause_duration:.1f}s")
        
        # Farbe basierend auf Pause-Länge
        if pause_duration > 3.0:
            color = '#e74c3c'  # Rot für lange Pausen
        elif pause_duration > 1.5:
            color = '#f39c12'  # Orange für mittlere Pausen
        else:
            color = '#27ae60'  # Grün für kurze Pausen
        
        self.current_pause_label.setStyleSheet(f"color: {color}; padding: 5px; font-weight: bold;")
        
        # Pause zu Daten hinzufügen
        self.marker_data['pauses'].append(pause_duration)
        if len(self.marker_data['pauses']) > self.max_data_points:
            self.marker_data['pauses'] = self.marker_data['pauses'][-self.max_data_points:]
    
    def on_prosody_updated(self, prosody_data):
        """Prosodische Features aktualisiert"""
        # Wird bereits in on_markers_updated behandelt
        pass
    
    def update_marker_plots(self):
        """Marker-Plots aktualisieren - MIT SICHERHEITS-CHECKS"""
        if not self.plot_enabled:
            return
        
        # Throttle updates to prevent CPU overload
        now = datetime.now()
        if (now - self.last_plot_update).total_seconds() * 1000 < self.plot_update_rate:
            return
        
        self.last_plot_update = now
        
        try:
            # Emotion-Plot aktualisieren (Valenz über Zeit)
            if self.marker_data['timestamps'] and self.marker_data['emotions']:
                timestamps = self.marker_data['timestamps'][-self.max_data_points:]
                emotions = self.marker_data['emotions'][-self.max_data_points:]
                
                # Daten bereinigen (NaN/Inf entfernen)
                valid_data = [(t, e) for t, e in zip(timestamps, emotions) if np.isfinite(e)]
                if valid_data:
                    valid_timestamps, valid_emotions = zip(*valid_data)
                    x_data = np.arange(len(valid_timestamps))
                    y_data = np.array(valid_emotions, dtype=np.float64)
                    
                    self.emotion_plot.clear()
                    self.emotion_plot.plot(x_data, y_data, pen='c', symbol='o', symbolSize=5)
                    self.emotion_plot.setLabel('left', 'Valenz', color='#ffffff')
                    self.emotion_plot.setLabel('bottom', 'Zeit', color='#ffffff')
            
            # Pausen-Plot aktualisieren
            if self.marker_data['pauses']:
                pauses = self.marker_data['pauses'][-self.max_data_points:]
                valid_pauses = [p for p in pauses if np.isfinite(p)]
                if valid_pauses:
                    x_data = np.arange(len(valid_pauses))
                    y_data = np.array(valid_pauses, dtype=np.float64)
                    
                    self.pause_plot.clear()
                    self.pause_plot.plot(x_data, y_data, pen='y', symbol='s', symbolSize=5)
                    self.pause_plot.setLabel('left', 'Dauer (s)', color='#ffffff')
                    self.pause_plot.setLabel('bottom', 'Ereignis', color='#ffffff')
            
            # Pitch-Plot aktualisieren
            if self.marker_data['pitch']:
                pitches = self.marker_data['pitch'][-self.max_data_points:]
                valid_pitches = [p for p in pitches if np.isfinite(p) and p > 0]
                if valid_pitches:
                    x_data = np.arange(len(valid_pitches))
                    y_data = np.array(valid_pitches, dtype=np.float64)
                    
                    self.pitch_plot.clear()
                    self.pitch_plot.plot(x_data, y_data, pen='g', symbol='t', symbolSize=5)
                    self.pitch_plot.setLabel('left', 'Pitch (Hz)', color='#ffffff')
                    self.pitch_plot.setLabel('bottom', 'Zeit', color='#ffffff')
                    
        except Exception as e:
            print(f"⚠️  Fehler beim Plot-Update (nicht kritisch): {e}")
            # Bei wiederholten Fehlern Plots deaktivieren
            if not hasattr(self, 'plot_error_count'):
                self.plot_error_count = 0
            self.plot_error_count += 1
            if self.plot_error_count > 10:
                print("❌ Plot-System deaktiviert nach zu vielen Fehlern")
                self.plot_enabled = False
    
    def update_marker_statistics(self):
        """Marker-Statistiken aktualisieren"""
        try:
            stats_text = ""
            
            # Emotion-Statistiken
            if self.marker_data['emotions']:
                avg_valence = np.mean(self.marker_data['emotions'])
                stats_text += f"Ø Valenz: {avg_valence:.2f}\n"
            
            # Pause-Statistiken
            if self.marker_data['pauses']:
                avg_pause = np.mean(self.marker_data['pauses'])
                max_pause = np.max(self.marker_data['pauses'])
                pause_count = len(self.marker_data['pauses'])
                stats_text += f"Pausen: {pause_count}\n"
                stats_text += f"Ø Pause: {avg_pause:.1f}s\n"
                stats_text += f"Max Pause: {max_pause:.1f}s\n"
            
            # Prosody-Statistiken
            if self.marker_data['pitch']:
                valid_pitch = [p for p in self.marker_data['pitch'] if p > 0]
                if valid_pitch:
                    avg_pitch = np.mean(valid_pitch)
                    stats_text += f"Ø Pitch: {avg_pitch:.0f} Hz\n"
            
            if self.marker_data['energy']:
                avg_energy = np.mean(self.marker_data['energy'])
                stats_text += f"Ø Energie: {avg_energy:.3f}"
            
            if not stats_text:
                stats_text = "Noch keine Daten..."
            
            self.stats_label.setText(stats_text)
            
        except Exception as e:
            print(f"Fehler beim Aktualisieren der Statistiken: {e}")
            self.stats_label.setText("Fehler bei Statistiken")
    
    def clear_transcript(self):
        """Transkriptionstext löschen"""
        reply = QMessageBox.question(self, "Text löschen", 
                                   "Möchten Sie den gesamten Transkriptionstext löschen?",
                                   QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
        if reply == QMessageBox.StandardButton.Yes:
            self.transcript_text.clear()
    
    def save_transcript(self):
        """Transkription speichern"""
        text = self.transcript_text.toPlainText()
        if not text.strip():
            QMessageBox.information(self, "Speichern", "Kein Text zum Speichern vorhanden.")
            return
        
        try:
            # Dateiname mit Zeitstempel
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"transkript_{timestamp}.txt"
            filepath = os.path.join("transcripts", filename)
            
            # Verzeichnis erstellen falls nicht vorhanden
            os.makedirs("transcripts", exist_ok=True)
            
            # Text speichern
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(text)
            
            QMessageBox.information(self, "Gespeichert", f"Transkription gespeichert als:\n{filepath}")
            self.statusBar().showMessage(f"Transkription gespeichert: {filename}")
            
        except Exception as e:
            QMessageBox.critical(self, "Fehler", f"Fehler beim Speichern:\n{str(e)}")
    
    # Session Management Methoden
    def new_session(self):
        """Neue Sitzung erstellen"""
        if self.is_recording:
            QMessageBox.warning(self, "Warnung", "Bitte stoppen Sie zuerst die Live-Transkription.")
            return
        
        # Aktuelle Sitzung speichern falls vorhanden
        if self.current_session and self.transcript_text.toPlainText().strip():
            reply = QMessageBox.question(self, "Sitzung speichern", 
                                       "Möchten Sie die aktuelle Sitzung speichern?",
                                       QMessageBox.StandardButton.Yes | 
                                       QMessageBox.StandardButton.No | 
                                       QMessageBox.StandardButton.Cancel)
            if reply == QMessageBox.StandardButton.Yes:
                self.save_current_session()
            elif reply == QMessageBox.StandardButton.Cancel:
                return
        
        # Neue Sitzung erstellen
        self.current_session = self.session_manager.create_session()
        self.transcript_text.clear()
        self.clear_marker_data()
        
        self.statusBar().showMessage("Neue Sitzung erstellt")
        self.setWindowTitle(f"TransRapport MVP - {self.current_session['name']}")
    
    def load_session_dialog(self):
        """Dialog zum Laden einer Sitzung"""
        if self.is_recording:
            QMessageBox.warning(self, "Warnung", "Bitte stoppen Sie zuerst die Live-Transkription.")
            return
        
        dialog = SessionLoadDialog(self.session_manager, self)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            selected_session = dialog.get_selected_session()
            if selected_session:
                self.load_session(selected_session['filepath'])
    
    def load_session(self, filepath: str):
        """Sitzung laden"""
        try:
            session = self.session_manager.load_session(filepath)
            if session:
                self.current_session = session
                
                # Transkript laden
                self.transcript_text.setPlainText(session.get('transcript', ''))
                
                # Marker-Daten laden
                if 'markers_data' in session:
                    self.marker_data = session['markers_data']
                    self.update_marker_plots()
                    self.update_marker_statistics()
                
                # Einstellungen laden
                if 'language' in session:
                    lang_map = {'de': 'Deutsch', 'en': 'Englisch', 'auto': 'Auto-Erkennung'}
                    lang_text = lang_map.get(session['language'], 'Deutsch')
                    self.lang_combo.setCurrentText(lang_text)
                
                if 'model_size' in session:
                    self.model_combo.setCurrentText(session['model_size'])
                
                self.statusBar().showMessage(f"Sitzung geladen: {session['name']}")
                self.setWindowTitle(f"TransRapport MVP - {session['name']}")
                
            else:
                QMessageBox.critical(self, "Fehler", "Sitzung konnte nicht geladen werden.")
                
        except Exception as e:
            QMessageBox.critical(self, "Fehler", f"Fehler beim Laden der Sitzung:\n{str(e)}")
    
    def save_current_session(self):
        """Aktuelle Sitzung speichern"""
        if not self.current_session:
            self.current_session = self.session_manager.create_session()
        
        try:
            # Session-Daten aktualisieren
            self.current_session = self.session_manager.update_session_transcript(
                self.current_session, self.transcript_text.toPlainText()
            )
            
            self.current_session = self.session_manager.update_session_markers(
                self.current_session, self.marker_data
            )
            
            # Einstellungen speichern
            lang_map = {'Deutsch': 'de', 'Englisch': 'en', 'Auto-Erkennung': 'auto'}
            self.current_session['language'] = lang_map.get(self.lang_combo.currentText(), 'de')
            self.current_session['model_size'] = self.model_combo.currentText()
            
            # Sitzung beenden falls sie läuft
            if not self.current_session.get('end_time'):
                self.current_session = self.session_manager.end_session(self.current_session)
            
            # Speichern
            filepath = self.session_manager.save_session(self.current_session)
            
            QMessageBox.information(self, "Gespeichert", 
                                  f"Sitzung gespeichert als:\n{os.path.basename(filepath)}")
            self.statusBar().showMessage(f"Sitzung gespeichert: {self.current_session['name']}")
            
        except Exception as e:
            QMessageBox.critical(self, "Fehler", f"Fehler beim Speichern der Sitzung:\n{str(e)}")
    
    def export_transcript(self, format: str):
        """Transkript exportieren"""
        text = self.transcript_text.toPlainText()
        if not text.strip():
            QMessageBox.information(self, "Export", "Kein Text zum Exportieren vorhanden.")
            return
        
        try:
            # Session-Daten für Export vorbereiten
            session_data = None
            if self.current_session:
                session_data = self.current_session.copy()
                session_data['markers_summary'] = self.session_manager._generate_markers_summary(self.marker_data)
            
            # Export durchführen
            if format == 'md':
                filepath = self.exporter.export_to_markdown(text, session_data)
            else:
                filepath = self.exporter.export_to_txt(text, session_data)
            
            QMessageBox.information(self, "Export erfolgreich", 
                                  f"Transkript exportiert als:\n{os.path.basename(filepath)}")
            self.statusBar().showMessage(f"Export erfolgreich: {os.path.basename(filepath)}")
            
        except Exception as e:
            QMessageBox.critical(self, "Fehler", f"Fehler beim Export:\n{str(e)}")
    
    def open_exports_folder(self):
        """Export-Ordner öffnen"""
        import subprocess
        import platform
        
        export_dir = self.exporter.get_export_directory()
        
        try:
            if platform.system() == "Windows":
                os.startfile(export_dir)  # type: ignore[attr-defined]
            elif platform.system() == "Darwin":  # macOS
                subprocess.run(["open", export_dir], check=True)
            else:  # Linux
                subprocess.run(["xdg-open", export_dir], check=True)
        except Exception as e:
            QMessageBox.information(self, "Export-Ordner", f"Export-Ordner: {export_dir}")
    
    def open_sessions_folder(self):
        """Sessions-Ordner öffnen"""
        import subprocess
        import platform
        
        sessions_dir = self.session_manager.get_sessions_directory()
        
        try:
            if platform.system() == "Windows":
                os.startfile(sessions_dir)  # type: ignore[attr-defined]
            elif platform.system() == "Darwin":  # macOS
                subprocess.run(["open", sessions_dir], check=True)
            else:  # Linux
                subprocess.run(["xdg-open", sessions_dir], check=True)
        except Exception as e:
            QMessageBox.information(self, "Sessions-Ordner", f"Sessions-Ordner: {sessions_dir}")
    
    def show_about(self):
        """Über-Dialog anzeigen"""
        about_text = """
        <h2>TransRapport MVP</h2>
        <p><b>Live-Transkription für Therapeuten</b></p>
        <p>Version 1.0</p>
        
        <p>Features:</p>
        <ul>
        <li>Live-Transkription mit Whisper (Offline)</li>
        <li>Therapeutische Marker-Analyse (ATO→SEM)</li>
        <li>Emotionserkennung und Prosody-Analyse</li>
        <li>Pausen-Erkennung</li>
        <li>Session-Management</li>
        <li>Export in Text und Markdown</li>
        </ul>
        
        <p>Entwickelt für therapeutische Anwendungen mit Fokus auf 
        Datenschutz und Offline-Betrieb.</p>
        """
        
        QMessageBox.about(self, "Über TransRapport MVP", about_text)
    
    def clear_marker_data(self):
        """Marker-Daten zurücksetzen"""
        self.marker_data = {
            'timestamps': [],
            'emotions': [],
            'pauses': [],
            'pitch': [],
            'energy': []
        }
        
        # Plots leeren
        self.emotion_curve.setData([], [])
        self.pitch_curve.setData([], [])
        self.energy_curve.setData([], [])
        
        # Labels zurücksetzen
        self.current_emotion_label.setText("neutral")
        self.current_pause_label.setText("0.0s")
        self.stats_label.setText("Noch keine Daten...")
        self.emotion_confidence_bar.setValue(0)
    
    def show_saved_sessions(self):
        """Zeigt Dialog mit gespeicherten Sessions"""
        import os
        sessions_dir = "sessions"
        
        if not os.path.exists(sessions_dir) or not os.listdir(sessions_dir):
            QMessageBox.information(self, "Gespeicherte Sessions", 
                                  "Noch keine Sessions gespeichert.\n\n"
                                  "Sessions werden automatisch gespeichert, wenn Sie die Aufnahme beenden.")
            return
        
        # Öffne den Sessions-Ordner im Finder
        import subprocess
        try:
            subprocess.run(["open", os.path.abspath(sessions_dir)])
            self.statusBar().showMessage(f"Sessions-Ordner geöffnet: {os.path.abspath(sessions_dir)}")
        except Exception as e:
            QMessageBox.warning(self, "Fehler", f"Konnte Sessions-Ordner nicht öffnen:\n{str(e)}")
    
    def closeEvent(self, event):
        """Beim Schließen der Anwendung"""
        if self.is_recording:
            self.stop_recording()
        event.accept()


class SessionLoadDialog(QDialog):
    """Dialog zum Laden von Sitzungen"""
    
    def __init__(self, session_manager: SessionManager, parent=None):
        super().__init__(parent)
        self.session_manager = session_manager
        self.selected_session = None
        self.init_ui()
        self.load_sessions()
    
    def init_ui(self):
        """Dialog-UI initialisieren"""
        self.setWindowTitle("Sitzung laden")
        self.setMinimumSize(600, 400)
        self.resize(700, 500)
        
        layout = QVBoxLayout(self)
        
        # Titel
        title_label = QLabel("Verfügbare Sitzungen")
        title_font = QFont()
        title_font.setPointSize(14)
        title_font.setBold(True)
        title_label.setFont(title_font)
        layout.addWidget(title_label)
        
        # Sessions-Liste
        self.sessions_list = QListWidget()
        self.sessions_list.itemDoubleClicked.connect(self.on_item_double_clicked)
        self.sessions_list.itemSelectionChanged.connect(self.on_selection_changed)
        layout.addWidget(self.sessions_list)
        
        # Session-Details
        details_group = QGroupBox("Session-Details")
        details_layout = QVBoxLayout(details_group)
        
        self.details_text = QTextBrowser()
        self.details_text.setMaximumHeight(150)
        details_layout.addWidget(self.details_text)
        
        layout.addWidget(details_group)
        
        # Buttons
        button_layout = QHBoxLayout()
        
        refresh_btn = QPushButton("Aktualisieren")
        refresh_btn.clicked.connect(self.load_sessions)
        button_layout.addWidget(refresh_btn)
        
        delete_btn = QPushButton("Löschen")
        delete_btn.clicked.connect(self.delete_selected_session)
        delete_btn.setStyleSheet("QPushButton { background-color: #e74c3c; color: white; }")
        button_layout.addWidget(delete_btn)
        
        button_layout.addStretch()
        
        # Standard Dialog-Buttons
        button_box = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel
        )
        button_box.accepted.connect(self.accept)
        button_box.rejected.connect(self.reject)
        
        button_layout.addWidget(button_box)
        layout.addLayout(button_layout)
        
        # OK-Button initial deaktivieren
        self.ok_button = button_box.button(QDialogButtonBox.StandardButton.Ok)
        self.ok_button.setEnabled(False)
    
    def load_sessions(self):
        """Sitzungen laden und anzeigen"""
        self.sessions_list.clear()
        self.details_text.clear()
        
        sessions = self.session_manager.list_sessions()
        
        if not sessions:
            item = QListWidgetItem("Keine Sitzungen gefunden")
            item.setFlags(item.flags() & ~Qt.ItemFlag.ItemIsSelectable)
            self.sessions_list.addItem(item)
            return
        
        for session in sessions:
            # Session-Info formatieren
            created_date = ""
            if session['created_at']:
                try:
                    dt = datetime.fromisoformat(session['created_at'])
                    created_date = dt.strftime("%d.%m.%Y %H:%M")
                except:
                    created_date = session['created_at']
            
            duration_text = session.get('duration', 'Unbekannt')
            language_text = {'de': 'Deutsch', 'en': 'Englisch', 'auto': 'Auto'}.get(
                session.get('language', 'de'), 'Deutsch'
            )
            
            item_text = f"{session['name']} ({created_date})"
            if duration_text != 'Unbekannt':
                item_text += f" - {duration_text}"
            
            item = QListWidgetItem(item_text)
            item.setData(Qt.ItemDataRole.UserRole, session)
            self.sessions_list.addItem(item)
    
    def on_selection_changed(self):
        """Auswahl geändert"""
        current_item = self.sessions_list.currentItem()
        
        if current_item and current_item.data(Qt.ItemDataRole.UserRole):
            session = current_item.data(Qt.ItemDataRole.UserRole)
            self.selected_session = session
            self.ok_button.setEnabled(True)
            
            # Details anzeigen
            details_html = f"""
            <h3>{session['name']}</h3>
            <p><b>Erstellt:</b> {session.get('created_at', 'Unbekannt')}</p>
            <p><b>Dauer:</b> {session.get('duration', 'Unbekannt')}</p>
            <p><b>Sprache:</b> {session.get('language', 'de')}</p>
            <p><b>Datei:</b> {session['filename']}</p>
            """
            
            self.details_text.setHtml(details_html)
        else:
            self.selected_session = None
            self.ok_button.setEnabled(False)
            self.details_text.clear()
    
    def on_item_double_clicked(self, item):
        """Item doppelt geklickt - Dialog akzeptieren"""
        if item.data(Qt.ItemDataRole.UserRole):
            self.accept()
    
    def delete_selected_session(self):
        """Ausgewählte Sitzung löschen"""
        if not self.selected_session:
            return
        
        reply = QMessageBox.question(
            self, "Sitzung löschen",
            f"Möchten Sie die Sitzung '{self.selected_session['name']}' wirklich löschen?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            success = self.session_manager.delete_session(self.selected_session['filepath'])
            if success:
                QMessageBox.information(self, "Gelöscht", "Sitzung wurde erfolgreich gelöscht.")
                self.load_sessions()  # Liste aktualisieren
            else:
                QMessageBox.critical(self, "Fehler", "Sitzung konnte nicht gelöscht werden.")
    
    def get_selected_session(self):
        """Ausgewählte Sitzung zurückgeben"""
        return self.selected_session
