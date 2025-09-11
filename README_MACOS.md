# TransRapport MVP - macOS Quick Start

## 🚀 Automatische Installation (Empfohlen)

```bash
# 1. Terminal öffnen und zum TransRapport-Ordner navigieren
cd /pfad/zu/transrapport_mvp

# 2. Automatisches Installationsskript ausführen
./install_macos.sh
```

Das Skript installiert automatisch:
- ✅ Homebrew (falls nicht vorhanden)
- ✅ Xcode Command Line Tools
- ✅ Python, HDF5, FFmpeg über Homebrew
- ✅ Alle Python-Abhängigkeiten mit HDF5-Unterstützung
- ✅ Löst bekannte macOS-Probleme

## 🛠 Manuelle Installation

Falls das automatische Skript nicht funktioniert:

### 1. System-Abhängigkeiten
```bash
# Homebrew installieren
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"

# Abhängigkeiten installieren
brew install python hdf5 ffmpeg pkg-config
```

### 2. HDF5-Pfade setzen
```bash
# Für Apple Silicon (M1/M2)
export HDF5_DIR=/opt/homebrew/opt/hdf5

# Für Intel Macs
export HDF5_DIR=/usr/local/opt/hdf5
```

### 3. Python-Umgebung
```bash
python3 -m venv venv
source venv/bin/activate
pip install --upgrade pip setuptools wheel

# macOS-spezifische Requirements
pip install -r requirements_macos.txt
HDF5_DIR=$HDF5_DIR pip install tables
```

## 🎯 Anwendung starten

Nach erfolgreicher Installation:

```bash
# Option 1: Start-Script verwenden
./start_transrapport.command

# Option 2: Manuell starten
source venv/bin/activate
python main.py
```

## 🆘 Häufige Probleme

### "H5public.h file not found"
```bash
brew reinstall hdf5
export HDF5_DIR=$(brew --prefix hdf5)
pip uninstall tables && pip install --no-cache-dir tables
```

### PyQt6/pyqtgraph Probleme
```bash
brew install qt6
pip uninstall PyQt6 pyqtgraph
pip install PyQt6 pyqtgraph
```

### Apple Silicon (M1/M2) Probleme
```bash
# Architektur prüfen
python -c "import platform; print(platform.machine())"
# Sollte "arm64" zeigen

# HDF5-Architektur prüfen
file $(brew --prefix hdf5)/lib/libhdf5.dylib
# Sollte "arm64" enthalten
```

## 📚 Detaillierte Dokumentation

Für ausführliche Fehlerbehebung siehe:
- **[docs/INSTALL_MACOS.md](docs/INSTALL_MACOS.md)** - Vollständige macOS-Installationsanleitung
- **[README.md](README.md)** - Hauptdokumentation

## ✅ Installation testen

```bash
python -c "
import tables, pyqtgraph, PyQt6, librosa, faster_whisper
print('🎉 Alle Abhängigkeiten erfolgreich geladen!')
"
```

---

**Bei Problemen:** Führen Sie `./install_macos.sh` erneut aus oder konsultieren Sie die detaillierte Anleitung in `docs/INSTALL_MACOS.md`.
