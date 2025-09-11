#!/bin/bash
# TransRapport MVP - macOS Installation Script
# Automatisiert die Installation für macOS mit HDF5-Abhängigkeiten

set -e  # Exit on any error

echo "🍎 TransRapport MVP - macOS Installation"
echo "======================================="
echo ""

# Farben für Output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Funktionen
print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# System-Check
print_status "Prüfe macOS-System..."

# macOS Version prüfen
MACOS_VERSION=$(sw_vers -productVersion)
print_status "macOS Version: $MACOS_VERSION"

# Architektur prüfen (Intel vs Apple Silicon)
ARCH=$(uname -m)
print_status "Architektur: $ARCH"

if [[ "$ARCH" == "arm64" ]]; then
    HOMEBREW_PREFIX="/opt/homebrew"
    print_status "Apple Silicon (M1/M2) erkannt"
else
    HOMEBREW_PREFIX="/usr/local"
    print_status "Intel Mac erkannt"
fi

# Homebrew prüfen/installieren
print_status "Prüfe Homebrew Installation..."
if ! command -v brew &> /dev/null; then
    print_warning "Homebrew nicht gefunden. Installiere Homebrew..."
    /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
    
    # Homebrew zum PATH hinzufügen
    echo "eval \"\$(${HOMEBREW_PREFIX}/bin/brew shellenv)\"" >> ~/.zshrc
    eval "$(${HOMEBREW_PREFIX}/bin/brew shellenv)"
else
    print_success "Homebrew bereits installiert"
fi

# Xcode Command Line Tools prüfen
print_status "Prüfe Xcode Command Line Tools..."
if ! xcode-select -p &> /dev/null; then
    print_warning "Xcode Command Line Tools nicht gefunden. Installiere..."
    xcode-select --install
    echo "Bitte warten Sie, bis die Xcode Command Line Tools Installation abgeschlossen ist."
    echo "Drücken Sie Enter, um fortzufahren..."
    read
else
    print_success "Xcode Command Line Tools bereits installiert"
fi

# System-Abhängigkeiten installieren
print_status "Installiere System-Abhängigkeiten über Homebrew..."

# Python installieren/aktualisieren
brew install python

# HDF5 installieren (kritisch für PyTables)
brew install hdf5

# FFmpeg für Audio-Verarbeitung
brew install ffmpeg

# Weitere nützliche Tools
brew install pkg-config

print_success "System-Abhängigkeiten installiert"

# HDF5-Pfade setzen
print_status "Setze HDF5-Umgebungsvariablen..."

HDF5_DIR="${HOMEBREW_PREFIX}/opt/hdf5"
export HDF5_DIR="$HDF5_DIR"
export CPPFLAGS="-I${HDF5_DIR}/include"
export LDFLAGS="-L${HDF5_DIR}/lib"

print_status "HDF5_DIR: $HDF5_DIR"

# Umgebungsvariablen dauerhaft speichern
if ! grep -q "HDF5_DIR" ~/.zshrc; then
    print_status "Füge HDF5-Variablen zu ~/.zshrc hinzu..."
    echo "" >> ~/.zshrc
    echo "# TransRapport MVP - HDF5 Pfade" >> ~/.zshrc
    echo "export HDF5_DIR=\"${HDF5_DIR}\"" >> ~/.zshrc
    echo "export CPPFLAGS=\"-I${HDF5_DIR}/include\"" >> ~/.zshrc
    echo "export LDFLAGS=\"-L${HDF5_DIR}/lib\"" >> ~/.zshrc
fi

# Virtual Environment erstellen
print_status "Erstelle Python Virtual Environment..."

if [ -d "venv" ]; then
    print_warning "Virtual Environment bereits vorhanden. Lösche altes venv..."
    rm -rf venv
fi

python3 -m venv venv
source venv/bin/activate

# Pip aktualisieren
print_status "Aktualisiere pip, setuptools und wheel..."
pip install --upgrade pip setuptools wheel

# Python-Abhängigkeiten installieren
print_status "Installiere Python-Abhängigkeiten..."

# Zuerst die macOS-spezifische requirements.txt
if [ -f "requirements_macos.txt" ]; then
    print_status "Verwende requirements_macos.txt..."
    pip install -r requirements_macos.txt
else
    print_warning "requirements_macos.txt nicht gefunden. Verwende requirements.txt..."
    pip install -r requirements.txt
fi

# PyTables separat mit HDF5-Pfad installieren
print_status "Installiere PyTables mit HDF5-Unterstützung..."
HDF5_DIR="$HDF5_DIR" pip install --no-cache-dir tables==3.9.2

print_success "Python-Abhängigkeiten installiert"

# Installation testen
print_status "Teste Installation..."

python -c "
try:
    import tables
    print('✅ PyTables:', tables.__version__)
except ImportError as e:
    print('❌ PyTables Import-Fehler:', e)
    exit(1)

try:
    import pyqtgraph
    print('✅ pyqtgraph:', pyqtgraph.__version__)
except ImportError as e:
    print('❌ pyqtgraph Import-Fehler:', e)
    exit(1)

try:
    import PyQt6
    print('✅ PyQt6 erfolgreich importiert')
except ImportError as e:
    print('❌ PyQt6 Import-Fehler:', e)
    exit(1)

try:
    import librosa
    print('✅ librosa:', librosa.__version__)
except ImportError as e:
    print('❌ librosa Import-Fehler:', e)
    exit(1)

try:
    import faster_whisper
    print('✅ faster-whisper erfolgreich importiert')
except ImportError as e:
    print('❌ faster-whisper Import-Fehler:', e)
    exit(1)

print('\\n🎉 Alle kritischen Abhängigkeiten erfolgreich installiert!')
"

if [ $? -eq 0 ]; then
    print_success "Installation erfolgreich abgeschlossen!"
else
    print_error "Installation-Test fehlgeschlagen. Siehe Fehlermeldungen oben."
    exit 1
fi

# Desktop-Verknüpfung erstellen
print_status "Erstelle Start-Script..."

cat > start_transrapport.command << 'EOF'
#!/bin/bash
cd "$(dirname "$0")"
source venv/bin/activate
python main.py
EOF

chmod +x start_transrapport.command

print_success "Start-Script 'start_transrapport.command' erstellt"

# Abschluss-Informationen
echo ""
echo "🎉 Installation abgeschlossen!"
echo "================================"
echo ""
echo "Nächste Schritte:"
echo "1. Anwendung starten:"
echo "   ./start_transrapport.command"
echo "   oder:"
echo "   source venv/bin/activate && python main.py"
echo ""
echo "2. Mikrofon-Berechtigungen:"
echo "   Systemeinstellungen → Sicherheit & Datenschutz → Mikrofon"
echo "   Terminal und Python zu erlaubten Apps hinzufügen"
echo ""
echo "3. Bei Problemen:"
echo "   - Siehe docs/INSTALL_MACOS.md für detaillierte Fehlerbehebung"
echo "   - Prüfe HDF5-Installation: brew list hdf5"
echo "   - Teste Imports: python -c \"import tables; import pyqtgraph\""
echo ""
echo "Installierte Versionen:"
echo "- macOS: $MACOS_VERSION ($ARCH)"
echo "- Python: $(python --version)"
echo "- HDF5: $(brew list --versions hdf5 | head -1)"
echo "- Homebrew Prefix: $HOMEBREW_PREFIX"
echo ""
print_success "TransRapport MVP ist bereit für die Nutzung!"
