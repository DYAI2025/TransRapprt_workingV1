# TransRapport MVP - Production Deployment Guide

## System Requirements for Production

### Hardware
- **CPU**: 2+ cores recommended for real-time transcription
- **RAM**: 8GB minimum, 16GB recommended
- **Storage**: 5GB free space (includes models)
- **Microphone**: USB or built-in microphone with proper drivers

### Software Dependencies
- **Python**: 3.8+ (tested with 3.12)
- **PortAudio**: System library for audio I/O
- **FFmpeg**: Audio processing and codec support
- **Operating System**: Windows 10+, macOS 10.14+, or Linux (Ubuntu 20.04+)

## Pre-Deployment Checklist

### 1. System Dependencies Installation

**Ubuntu/Debian:**
```bash
sudo apt-get update
sudo apt-get install -y python3 python3-pip python3-venv portaudio19-dev ffmpeg
```

**macOS:**
```bash
brew install python portaudio ffmpeg
```

**Windows:**
- Install Python from python.org
- Install FFmpeg and add to PATH
- PortAudio is included with sounddevice package

### 2. Application Setup

```bash
# Clone repository
git clone https://github.com/DYAI2025/TransRapprt_workingV1.git
cd TransRapprt_workingV1

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Reinstall sounddevice to link with PortAudio
pip install --force-reinstall sounddevice

# Create required directories
mkdir -p sessions exports transcripts models

# Verify installation
python test_functionality.py
```

### 3. Initial Configuration

Edit `config.ini` for production settings:
```ini
[DEFAULT]
language = de
sample_rate = 16000
theme = dark
model_size = base

[PRODUCTION]
enable_logging = True
log_level = INFO
log_file = transrapport.log
auto_save_interval = 300  # seconds
```

### 4. First-Run Model Download

On first launch, Whisper models will be downloaded:
- **base model**: ~74MB (recommended for production)
- **small model**: ~244MB (better quality)
- Requires internet connection only for initial download
- Models cached in `./models/` directory

## Verification Testing

### Automated Tests
```bash
python test_functionality.py
```
Expected output: "🎉 Alle Tests erfolgreich! TransRapport MVP ist bereit."

### Manual GUI Testing
1. Launch application: `python main.py`
2. Verify dark theme loads correctly
3. Check microphone detection (click "Aktualisieren")
4. Start recording and verify audio level indicator responds
5. Speak and verify transcription appears in real-time
6. Check marker visualizations update (emotion, pause, pitch plots)
7. Save a test session and verify it can be reloaded
8. Export session and verify output files

### Audio System Testing
Test the 7-stage audio fallback system:
```bash
python -c "from audio import AudioManager; am = AudioManager(); devices = am.get_input_devices(); print(f'Found {len(devices)} input devices'); am.test_microphone()"
```

## Known Issues and Workarounds

### Plot System
- Plot updates are throttled to 10 Hz to prevent CPU overload
- Automatically disables after 10 consecutive errors
- Can be manually disabled by setting `plot_enabled = False` in GUI

### Audio Compatibility
- System tries 7 different configurations if initial setup fails
- Supports mono and stereo microphones
- Adapts block size and latency automatically

### Performance Tuning
For slower systems:
- Use `tiny` model instead of `base`
- Increase `plot_update_rate` in gui.py (e.g., 200ms)
- Reduce `max_data_points` for visualization

## Production Monitoring

### Logging
Application logs to console by default. For production:
1. Enable file logging in config.ini
2. Monitor `transrapport.log` for errors
3. Set up log rotation

### Health Checks
Monitor these indicators:
- Audio queue size (should stay below 80%)
- Transcription latency (should be < 3 seconds)
- Plot update errors (should be 0)
- Memory usage (should stabilize after warmup)

## Security and Privacy

### Data Protection
- ✅ All processing done locally (offline after model download)
- ✅ No data sent to external servers
- ✅ Session files stored locally in `sessions/` directory
- ✅ GDPR compliant for therapeutic use

### Access Control
- Application runs with user permissions
- No special privileges required
- Session files readable only by user (Unix permissions)

## Troubleshooting

### "PortAudio library not found"
```bash
# Linux
sudo apt-get install portaudio19-dev
pip install --force-reinstall sounddevice

# macOS  
brew install portaudio
pip install --force-reinstall sounddevice
```

### "No module named 'librosa'"
```bash
pip install librosa webrtcvad
```

### Plot System Errors
If plots cause issues, disable in code:
```python
# In gui.py, line ~67
self.plot_enabled = False
```

## Support

For issues not covered here, check:
- KRITISCHE_FEHLER_ANALYSE.md for known issues
- README.md for general documentation
- GitHub issues for community support
