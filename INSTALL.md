# TransRapport MVP - Installationsanleitung für Therapeuten

Diese Anleitung führt Sie Schritt für Schritt durch die Installation und Einrichtung von TransRapport MVP auf Ihrem Computer.

## 📋 Was Sie benötigen

### Hardware
- **Computer**: Windows 10/11, macOS 10.14+, oder Linux
- **RAM**: Mindestens 4GB (8GB empfohlen)
- **Speicherplatz**: 3GB frei verfügbar
- **Mikrofon**: USB-Mikrofon oder eingebautes Mikrofon
- **Internetverbindung**: Nur für die Installation erforderlich

### Software (wird automatisch installiert)
- Python 3.8 oder neuer
- FFmpeg für Audio-Verarbeitung
- Whisper-Sprachmodell (wird beim ersten Start heruntergeladen)

## 🚀 Schritt-für-Schritt Installation

### Schritt 1: Python installieren

#### Windows
1. Besuchen Sie https://www.python.org/downloads/
2. Laden Sie die neueste Python-Version herunter (3.8 oder neuer)
3. **Wichtig**: Aktivieren Sie "Add Python to PATH" während der Installation
4. Führen Sie die Installation durch

#### macOS
```bash
# Mit Homebrew (empfohlen)
brew install python

# Oder von python.org herunterladen
```

#### Linux (Ubuntu/Debian)
```bash
sudo apt update
sudo apt install python3 python3-pip python3-venv
```

### Schritt 2: TransRapport MVP herunterladen

1. Laden Sie das TransRapport MVP Archiv herunter
2. Entpacken Sie es in einen Ordner Ihrer Wahl (z.B. `C:\TransRapport` oder `~/TransRapport`)
3. Merken Sie sich den Pfad zu diesem Ordner

### Schritt 3: Installation vorbereiten

#### Windows
1. Drücken Sie `Windows + R`
2. Geben Sie `cmd` ein und drücken Sie Enter
3. Navigieren Sie zum TransRapport-Ordner:
   ```cmd
   cd C:\TransRapport\transrapport_mvp
   ```

#### macOS/Linux
1. Öffnen Sie das Terminal
2. Navigieren Sie zum TransRapport-Ordner:
   ```bash
   cd ~/TransRapport/transrapport_mvp
   ```

### Schritt 4: Virtuelle Umgebung erstellen

```bash
# Virtuelle Umgebung erstellen
python -m venv venv

# Windows: Aktivieren
venv\Scripts\activate

# macOS/Linux: Aktivieren
source venv/bin/activate
```

**Hinweis**: Sie sollten jetzt `(venv)` vor Ihrer Eingabeaufforderung sehen.

### Schritt 5: Abhängigkeiten installieren

```bash
pip install -r requirements.txt
```

**Das kann einige Minuten dauern.** Die Installation lädt alle benötigten Komponenten herunter.

### Schritt 5.5: PortAudio installieren (System-Abhängigkeit)

**WICHTIG**: TransRapport benötigt die PortAudio-Bibliothek für Audio-Aufnahme.

#### Windows
PortAudio ist normalerweise über pip-Abhängigkeiten enthalten, aber falls Fehler auftreten:
1. Laden Sie PortAudio von http://www.portaudio.com/download.html herunter
2. Installieren Sie es in Ihrem System

#### Ubuntu/Debian (Linux)
```bash
sudo apt-get update
sudo apt-get install portaudio19-dev
pip install --force-reinstall sounddevice
```

#### macOS
```bash
brew install portaudio
pip install --force-reinstall sounddevice
```

**Überprüfung**: Nach der Installation sollte folgender Befehl ohne Fehler laufen:
```bash
python -c "import sounddevice as sd; print(sd.query_devices())"
```

### Schritt 6: FFmpeg installieren

#### Windows
1. Besuchen Sie https://ffmpeg.org/download.html
2. Laden Sie die Windows-Version herunter
3. Entpacken Sie FFmpeg in einen Ordner (z.B. `C:\ffmpeg`)
4. Fügen Sie den `bin`-Ordner zu Ihrem PATH hinzu:
   - Systemsteuerung → System → Erweiterte Systemeinstellungen
   - Umgebungsvariablen → PATH bearbeiten
   - Neuen Pfad hinzufügen: `C:\ffmpeg\bin`

#### macOS
```bash
brew install ffmpeg
```

#### Linux
```bash
sudo apt install ffmpeg
```

### Schritt 7: Erste Ausführung

```bash
python main.py
```

**Beim ersten Start**:
- Das Whisper-Modell wird automatisch heruntergeladen (ca. 74MB)
- Dies kann einige Minuten dauern
- Eine Internetverbindung ist erforderlich

## 🎯 Erste Einrichtung

### 1. Mikrofon testen
1. Schließen Sie Ihr Mikrofon an
2. Starten Sie TransRapport MVP
3. Klicken Sie auf "Aktualisieren" neben der Mikrofon-Auswahl
4. Wählen Sie Ihr Mikrofon aus der Liste
5. Sprechen Sie - der grüne Balken sollte sich bewegen

### 2. Einstellungen anpassen
- **Sprache**: Wählen Sie "Deutsch" für deutsche Sitzungen
- **Modell**: "base" ist ein guter Kompromiss zwischen Geschwindigkeit und Qualität

### 3. Erste Testsitzung
1. Klicken Sie "Live-Transkription starten"
2. Sprechen Sie einige Sätze
3. Beobachten Sie die Live-Transkription und Marker
4. Klicken Sie "Live-Transkription stoppen"

## 📁 Ordner und Dateien verstehen

Nach der Installation finden Sie folgende wichtige Ordner:

```
TransRapport/
├── sessions/          # Ihre gespeicherten Sitzungen
├── exports/           # Exportierte Transkripte
├── models/            # Whisper-Sprachmodelle
└── transcripts/       # Legacy-Transkripte
```

## 🔧 Tägliche Nutzung

### Anwendung starten
1. Öffnen Sie die Eingabeaufforderung/Terminal
2. Navigieren Sie zum TransRapport-Ordner
3. Aktivieren Sie die virtuelle Umgebung:
   ```bash
   # Windows
   venv\Scripts\activate
   
   # macOS/Linux
   source venv/bin/activate
   ```
4. Starten Sie die Anwendung:
   ```bash
   python main.py
   ```

### Desktop-Verknüpfung erstellen (Windows)

1. Erstellen Sie eine neue Textdatei namens `TransRapport.bat`
2. Fügen Sie folgenden Inhalt ein:
   ```batch
   @echo off
   cd /d "C:\TransRapport\transrapport_mvp"
   call venv\Scripts\activate
   python main.py
   pause
   ```
3. Passen Sie den Pfad an Ihre Installation an
4. Speichern Sie die Datei
5. Erstellen Sie eine Verknüpfung auf dem Desktop

## 🆘 Häufige Probleme und Lösungen

### Problem: "Python nicht gefunden"
**Lösung**: 
- Stellen Sie sicher, dass Python installiert ist
- Prüfen Sie, ob Python zum PATH hinzugefügt wurde
- Verwenden Sie `python3` statt `python` auf macOS/Linux

### Problem: "pip nicht gefunden"
**Lösung**:
```bash
# Windows
python -m pip install --upgrade pip

# macOS/Linux
python3 -m pip install --upgrade pip
```

### Problem: "FFmpeg nicht gefunden"
**Lösung**:
- Installieren Sie FFmpeg wie in Schritt 6 beschrieben
- Starten Sie die Eingabeaufforderung neu
- Testen Sie mit: `ffmpeg -version`

### Problem: Mikrofon wird nicht erkannt
**Lösung**:
- Prüfen Sie die Systemeinstellungen für Mikrofon-Berechtigungen
- Schließen Sie andere Anwendungen, die das Mikrofon verwenden
- Klicken Sie "Aktualisieren" in TransRapport

### Problem: Schlechte Transkriptionsqualität
**Lösung**:
- Sprechen Sie näher zum Mikrofon
- Reduzieren Sie Hintergrundgeräusche
- Wählen Sie ein größeres Modell (small oder medium)
- Stellen Sie sicher, dass die richtige Sprache ausgewählt ist

### Problem: Anwendung ist langsam
**Lösung**:
- Wählen Sie ein kleineres Modell (tiny)
- Schließen Sie andere Anwendungen
- Stellen Sie sicher, dass genügend RAM verfügbar ist

## 📞 Support

### Vor dem Support-Kontakt
1. Prüfen Sie diese Installationsanleitung
2. Schauen Sie in die README.md für weitere Details
3. Notieren Sie sich die genaue Fehlermeldung
4. Notieren Sie sich Ihr Betriebssystem und die Python-Version

### Informationen sammeln
```bash
# Python-Version prüfen
python --version

# FFmpeg-Version prüfen
ffmpeg -version

# Installierte Pakete anzeigen
pip list
```

## 🔒 Datenschutz-Hinweise

- **Alle Daten bleiben lokal** auf Ihrem Computer
- **Keine Internetverbindung** nach der Installation erforderlich
- **Keine Cloud-Services** werden verwendet
- **DSGVO-konform** für therapeutische Anwendungen

## 📚 Weiterführende Informationen

### Empfohlene Mikrofone
- **USB-Mikrofone**: Audio-Technica ATR2100x-USB, Blue Yeti
- **Headset-Mikrofone**: Plantronics Voyager, Jabra Evolve
- **Eingebaute Mikrofone**: Funktionieren, aber externe sind besser

### Optimale Aufnahme-Bedingungen
- **Abstand**: 15-30cm zum Mikrofon
- **Umgebung**: Ruhiger Raum ohne Echo
- **Lautstärke**: Normale Sprechlautstärke
- **Hintergrund**: Minimale Nebengeräusche

### Backup und Sicherheit
- Sichern Sie regelmäßig den `sessions/` Ordner
- Exportieren Sie wichtige Sitzungen als Text/Markdown
- Bewahren Sie eine Kopie der Installation auf

---

**Bei Fragen zur Installation kontaktieren Sie den technischen Support.**

**Version**: 1.0  
**Letzte Aktualisierung**: Dezember 2024
