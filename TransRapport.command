#!/bin/bash

# TransRapport MVP - One-Click Launcher
# Doppelklick auf diese Datei startet TransRapport

export PATH="/opt/homebrew/bin:/usr/local/bin:$PATH"

APP_DIR="$HOME/Applications/TransRapport"
VENV_PYTHON="$APP_DIR/venv/bin/python"

echo "🚀 Starting TransRapport MVP..."
echo "==============================="

# Check if installation exists
if [ ! -d "$APP_DIR" ]; then
    echo "❌ Error: TransRapport installation not found at $APP_DIR"
    echo "Please make sure TransRapport is installed correctly."
    read -p "Press Enter to close..."
    exit 1
fi

if [ ! -f "$VENV_PYTHON" ]; then
    echo "❌ Error: Python virtual environment not found"
    echo "Please reinstall TransRapport."
    read -p "Press Enter to close..."
    exit 1
fi

# Navigate to the application directory
cd "$APP_DIR" || exit 1

# Check dependencies
if ! command -v ffmpeg &> /dev/null; then
    echo "⚠️  Warning: FFmpeg not found. Install with: brew install ffmpeg"
    echo "TransRapport may not work properly without FFmpeg."
    echo ""
fi

echo "✅ Starting TransRapport..."
echo "📍 Working directory: $APP_DIR"
echo "🐍 Using Python: $VENV_PYTHON"
echo ""

# Start the application
"$VENV_PYTHON" main.py

echo ""
echo "TransRapport beendet."
read -p "Drücken Sie Enter zum Schließen..."