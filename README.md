# TransRapport MVP - Live-Transkription für Therapeuten

Eine Desktop-Anwendung für Live-Transkription mit therapeutischen Markern, entwickelt speziell für therapeutische Anwendungen mit Fokus auf Datenschutz und Offline-Betrieb.

## Features

### 🎤 Live-Transkription
- **Offline-Betrieb** mit Whisper (faster-whisper)
- **Echtzeit-Transkription** während der Sitzung
- **Mehrsprachig**: Deutsch, Englisch, Auto-Erkennung
- **Verschiedene Modellgrößen**: tiny, base, small, medium

### 🧠 Therapeutische Marker-Analyse (ATO→SEM)
- **Affect (Emotionen)**: Automatische Emotionserkennung aus Sprache
- **Tempo**: Pausen-Erkennung und Sprechgeschwindigkeit
- **Other Prosody**: Tonhöhe und Energie-Analyse
- **Live-Visualisierung** aller Marker während der Sitzung

### 💾 Session-Management
- **Sitzungen speichern und laden**
- **Vollständige Marker-Daten** werden mitgespeichert
- **Session-Übersicht** mit Details und Statistiken

### 📄 Export-Funktionalität
- **Text-Export** (.txt) mit Marker-Zusammenfassung
- **Markdown-Export** (.md) mit strukturierten Tabellen
- **Therapeutische Hinweise** basierend auf Marker-Analyse

### 🎨 Therapeutenfreundliche GUI
- **Minimalistische Oberfläche** für professionelle Nutzung
- **Live-Marker-Visualisierung** mit Plots und Statistiken
- **Audio-Pegel-Anzeige** für optimale Aufnahme
- **Intuitive Bedienung** mit Tastaturkürzeln

## Systemanforderungen

- **Python 3.8+**
- **FFmpeg** (für Audio-Verarbeitung)
- **Mikrofon** für Live-Aufnahme
- **4GB RAM** (empfohlen für base-Modell)
- **2GB freier Speicherplatz** (für Whisper-Modelle)

## Installation

### Schnellstart (Linux/Windows)

#### 1. Repository klonen oder herunterladen
```bash
git clone <repository-url>
cd transrapport_mvp
```

#### 2. Python Virtual Environment erstellen
```bash
python -m venv venv

# Windows
venv\Scripts\activate

# Linux/macOS
source venv/bin/activate
```

#### 3. Abhängigkeiten installieren
```bash
pip install -r requirements.txt
```

#### 4. FFmpeg installieren

**Windows:**
- FFmpeg von https://ffmpeg.org/download.html herunterladen
- Zu PATH hinzufügen

**Ubuntu/Debian:**
```bash
sudo apt update
sudo apt install ffmpeg
```

#### 5. Anwendung starten
```bash
python main.py
```

### 🍎 macOS-spezifische Installation

**macOS-Nutzer haben oft Probleme mit HDF5-Abhängigkeiten (PyTables) und PyQt-Installation.**

**→ Verwenden Sie die detaillierte [macOS-Installationsanleitung](docs/INSTALL_MACOS.md)**

Die macOS-Anleitung löst bekannte Probleme wie:
- `'H5public.h' file not found` Fehler
- PyTables Installation schlägt fehl
- PyQt6/pyqtgraph Wheel-Probleme
- Apple Silicon (M1/M2) Kompatibilität

**Kurz-Version für macOS:**
```bash
# HDF5 über Homebrew installieren
brew install hdf5 python ffmpeg

# HDF5-Pfad setzen
export HDF5_DIR=$(brew --prefix hdf5)

# macOS-spezifische requirements verwenden
pip install -r requirements_macos.txt
HDF5_DIR=$HDF5_DIR pip install tables
```

## Erste Schritte

### 1. Mikrofon einrichten
- Mikrofon anschließen und in den Einstellungen auswählen
- "Aktualisieren" klicken, um verfügbare Geräte zu laden
- Audio-Pegel prüfen (grüner Balken sollte bei Sprache ausschlagen)

### 2. Sprache und Modell wählen
- **Sprache**: Deutsch (empfohlen für deutsche Sitzungen)
- **Modell**: base (guter Kompromiss zwischen Geschwindigkeit und Qualität)

### 3. Live-Transkription starten
- "Live-Transkription starten" klicken
- Sprechen - Text erscheint in Echtzeit
- Marker werden automatisch analysiert und visualisiert

### 4. Sitzung verwalten
- **Neue Sitzung**: Strg+N
- **Sitzung speichern**: Strg+S
- **Sitzung laden**: Strg+O

### 5. Export
- **Datei → Exportieren → Als Text (.txt)**: Einfacher Textexport
- **Datei → Exportieren → Als Markdown (.md)**: Strukturierter Export mit Tabellen

## Therapeutische Marker

### Affect (Emotionen)
- **Erkannte Emotionen**: happy, sad, angry, excited, calm, anxious, neutral
- **Valenz-Werte**: -1 (negativ) bis +1 (positiv)
- **Confidence-Score**: Zuverlässigkeit der Erkennung

### Tempo (Pausen)
- **Pause-Erkennung**: Automatisch ab 600ms Stille
- **Sprechgeschwindigkeit**: Wörter pro Minute
- **Pause-Statistiken**: Durchschnitt, Maximum, Anzahl

### Prosody (Stimmmerkmale)
- **Tonhöhe (Pitch)**: Grundfrequenz in Hz
- **Energie (RMS)**: Lautstärke und Intensität
- **Stabilität**: Variabilität der Stimmmerkmale

## Datenschutz und Sicherheit

- ✅ **Vollständig offline** - keine Internetverbindung erforderlich
- ✅ **Lokale Speicherung** - alle Daten bleiben auf Ihrem Computer
- ✅ **Keine Cloud-Services** - keine Übertragung an externe Server
- ✅ **DSGVO-konform** - entwickelt für therapeutische Anwendungen

## Ordnerstruktur

```
transrapport_mvp/
├── main.py                 # Hauptanwendung
├── gui.py                  # Benutzeroberfläche
├── live_transcriber.py     # Live-Transkription
├── marker_system.py        # Therapeutische Marker
├── exporter.py            # Export-Funktionalität
├── session_manager.py     # Session-Management
├── audio.py               # Audio-Verarbeitung
├── config.ini             # Konfiguration
├── requirements.txt       # Python-Abhängigkeiten
├── sessions/              # Gespeicherte Sitzungen
├── exports/               # Exportierte Dateien
├── transcripts/           # Alte Transkripte (Legacy)
└── models/                # Whisper-Modelle (automatisch)
```

## Tastaturkürzel

- **Strg+N**: Neue Sitzung
- **Strg+O**: Sitzung laden
- **Strg+S**: Sitzung speichern
- **Strg+Q**: Anwendung beenden

## Fehlerbehebung

### Whisper-Modell wird nicht geladen
- Internetverbindung beim ersten Start erforderlich
- Modell wird automatisch heruntergeladen (ca. 74MB für base)
- Bei Problemen: `models/` Ordner löschen und neu starten

### Kein Mikrofon erkannt
- Mikrofon anschließen und "Aktualisieren" klicken
- Systemeinstellungen prüfen (Mikrofon-Berechtigung)
- Andere Anwendungen schließen, die das Mikrofon verwenden

### Schlechte Transkriptionsqualität
- Größeres Modell wählen (small oder medium)
- Näher zum Mikrofon sprechen
- Hintergrundgeräusche reduzieren
- Korrekte Sprache auswählen

### Performance-Probleme
- Kleineres Modell wählen (tiny)
- Andere Anwendungen schließen
- Mehr RAM verfügbar machen

## Technische Details

### Verwendete Technologien
- **faster-whisper**: Optimierte Whisper-Implementation
- **PyQt6**: Moderne GUI-Framework
- **librosa**: Audio-Analyse und Feature-Extraktion
- **webrtcvad**: Voice Activity Detection
- **pyqtgraph**: Echtzeit-Plots und Visualisierung
- **numpy**: Numerische Berechnungen

### Marker-Algorithmen
- **Emotionserkennung**: Spektrale Features + Regelbasierte Klassifikation
- **Pausen-Erkennung**: WebRTC VAD mit konfigurierbaren Schwellenwerten
- **Prosody-Analyse**: Pitch-Tracking und RMS-Energie mit librosa

## Support und Entwicklung

### Bekannte Limitationen
- Emotionserkennung ist vereinfacht (für MVP)
- Nur Mono-Audio unterstützt
- Deutsche und englische Sprache optimiert

### Geplante Features
- Erweiterte Emotionsmodelle
- Zusätzliche Sprachen
- Cloud-Synchronisation (optional)
- Erweiterte Statistiken

## Lizenz

Entwickelt für therapeutische Anwendungen. Alle Rechte vorbehalten.

---

**Version**: 1.0  
**Entwickelt**: 2025  
**Für**: Therapeutische Praxis mit Fokus auf Datenschutz
