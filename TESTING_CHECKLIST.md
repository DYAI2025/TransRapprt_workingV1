# TransRapport MVP - Manual Testing Checklist

## Pre-Launch Verification
- [ ] All dependencies installed (`pip list | grep -E "faster-whisper|PyQt6|librosa|sounddevice"`)
- [ ] PortAudio installed (`python -c "import sounddevice; print('OK')"`)
- [ ] Directories exist (sessions/, exports/, models/)
- [ ] Automated tests pass (`python test_functionality.py`)

## GUI Launch Test
- [ ] Application launches without errors: `python main.py`
- [ ] Dark theme loads correctly (dark background, white text)
- [ ] All UI elements visible and properly styled
- [ ] No console errors during startup

## Audio System Test
- [ ] Click "Aktualisieren" button to refresh microphone list
- [ ] At least one microphone detected
- [ ] Audio level indicator responds to sound (green bar moves)
- [ ] No PortAudio errors in console

## Live Transcription Test
- [ ] Select microphone from dropdown
- [ ] Click "Live-Transkription starten"
- [ ] Status changes to "Aufnahme läuft"
- [ ] Speak clearly in German or English
- [ ] Transcribed text appears in main text area within 3-5 seconds
- [ ] Text continues to update as you speak
- [ ] Click "Live-Transkription stoppen"
- [ ] Status returns to "Bereit"

## Marker System Test
- [ ] During transcription, emotion labels update
- [ ] Pause detection works (shows pause duration)
- [ ] Pitch values display in Hz
- [ ] Marker plots update (if plot_enabled=True)
- [ ] No infinite error loops in console
- [ ] Plot updates throttled (not overwhelming CPU)

## Session Management Test
- [ ] Click Datei → Neue Sitzung (or Ctrl+N)
- [ ] Enter session name in dialog
- [ ] Transcribe some test text
- [ ] Click Datei → Sitzung speichern (or Ctrl+S)
- [ ] Verify session file created in sessions/ directory
- [ ] Click Datei → Sitzung laden (or Ctrl+O)
- [ ] Select previously saved session
- [ ] Verify transcript and markers load correctly

## Export Test
- [ ] With transcript content present
- [ ] Click Datei → Exportieren → Als Text (.txt)
- [ ] Verify .txt file created in exports/
- [ ] Open file and verify content readable
- [ ] Click Datei → Exportieren → Als Markdown (.md)
- [ ] Verify .md file created with proper formatting
- [ ] Verify marker statistics included in export

## Performance Test
- [ ] Run 5+ minute transcription session
- [ ] Monitor CPU usage (should stabilize, not continuously increase)
- [ ] Monitor memory usage (should not grow unbounded)
- [ ] Check plot updates don't cause lag
- [ ] Verify no queue overflow errors

## Error Recovery Test
- [ ] Disconnect/reconnect microphone during recording
- [ ] Select invalid microphone and start recording (should show error)
- [ ] Stop recording multiple times rapidly
- [ ] Try loading corrupted session file
- [ ] Verify application doesn't crash, shows error dialogs

## Cross-Platform Test (if applicable)
- [ ] Test on Windows
- [ ] Test on macOS
- [ ] Test on Linux
- [ ] Verify folder opening works (`Datei → Öffne Sessions-Ordner`)
