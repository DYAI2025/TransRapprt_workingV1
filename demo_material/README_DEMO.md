# TransRapport MVP - Demo-Materialien

Dieser Ordner enthält Demo-Materialien und Beispiele für TransRapport MVP.

## 📁 Inhalt

### Beispiel-Exports
- `beispiel_transkript.txt` - Beispiel eines Text-Exports
- `beispiel_transkript.md` - Beispiel eines Markdown-Exports mit Marker-Analyse
- `beispiel_session.json` - Beispiel einer gespeicherten Sitzung

### Demo-Szenarien
- `demo_szenario_1.md` - Kurze Therapiesitzung mit verschiedenen Emotionen
- `demo_szenario_2.md` - Längere Sitzung mit Pausen-Analyse
- `demo_szenario_3.md` - Beispiel für prosodische Auffälligkeiten

## 🎯 Verwendung der Demo-Materialien

### 1. Beispiel-Session laden
1. Kopieren Sie `beispiel_session.json` in den `sessions/` Ordner
2. Starten Sie TransRapport MVP
3. Gehen Sie zu "Datei → Sitzung laden..."
4. Wählen Sie die Beispiel-Session aus

### 2. Export-Beispiele ansehen
- Öffnen Sie die `.txt` und `.md` Dateien, um zu sehen, wie Exporte aussehen
- Vergleichen Sie die verschiedenen Formate
- Beachten Sie die therapeutischen Hinweise in den Markdown-Exporten

### 3. Demo-Szenarien durchspielen
- Lesen Sie die Szenario-Beschreibungen
- Sprechen Sie die Beispieltexte in TransRapport MVP
- Beobachten Sie, wie die Marker reagieren

## 🧪 Test-Phrasen für Marker-System

### Emotionen testen
```
Fröhlich: "Ich bin heute wirklich glücklich und voller Energie!"
Traurig: "Es fällt mir schwer, darüber zu sprechen... ich fühle mich so niedergeschlagen."
Ärgerlich: "Das macht mich wirklich wütend! Das ist völlig unfair!"
Ängstlich: "Ich mache mir große Sorgen... was wenn etwas Schlimmes passiert?"
Ruhig: "Ich fühle mich entspannt und ausgeglichen heute."
```

### Pausen testen
```
Kurze Pausen: "Ich denke... ja, das stimmt."
Mittlere Pausen: "Das ist schwierig zu erklären... [2-3 Sekunden] ... ich weiß nicht recht."
Lange Pausen: "Wenn ich ehrlich bin... [5+ Sekunden] ... das ist sehr persönlich."
```

### Prosody testen
```
Hohe Tonlage: "Wirklich? Das ist ja fantastisch!" (aufgeregt sprechen)
Tiefe Tonlage: "Ich bin sehr müde heute." (monoton, tief sprechen)
Variabel: "Erst war ich traurig, dann wurde ich wütend, und jetzt bin ich verwirrt!"
```

## 📊 Erwartete Marker-Ergebnisse

### Emotionen
- **Positive Äußerungen** → happy, excited (Valenz > 0.5)
- **Negative Äußerungen** → sad, angry, anxious (Valenz < -0.3)
- **Neutrale Äußerungen** → neutral, calm (Valenz ≈ 0)

### Pausen
- **Kurze Pausen** (< 1.5s) → Grün
- **Mittlere Pausen** (1.5-3s) → Orange  
- **Lange Pausen** (> 3s) → Rot

### Prosody
- **Pitch**: 80-400 Hz (normale Sprechstimme)
- **Energie**: Höhere Werte bei lauter/emotionaler Sprache
- **Stabilität**: Niedrigere Werte bei emotionaler Erregung

## 🎬 Demo-Ablauf für Präsentationen

### 5-Minuten Demo
1. **Start** (30s): Anwendung öffnen, Mikrofon auswählen
2. **Live-Transkription** (2min): Verschiedene Emotionen sprechen
3. **Marker-Visualisierung** (1min): Plots und Statistiken zeigen
4. **Session-Management** (1min): Sitzung speichern
5. **Export** (30s): Als Markdown exportieren und zeigen

### 15-Minuten Demo
1. **Einführung** (2min): Features und Zielgruppe erklären
2. **Installation** (2min): Kurz die Einfachheit zeigen
3. **Live-Demo** (5min): Ausführliche Transkription mit Markern
4. **Session-Management** (2min): Speichern, laden, verwalten
5. **Export und Analyse** (3min): Verschiedene Formate, therapeutische Hinweise
6. **Datenschutz** (1min): Offline-Betrieb betonen

## 🔍 Troubleshooting für Demos

### Wenn Mikrofon nicht funktioniert
- Backup: Verwenden Sie vorbereitete Session-Dateien
- Alternative: Sprechen Sie in ein anderes Gerät und laden Sie die Session

### Wenn Marker nicht reagieren
- Sprechen Sie emotionaler und deutlicher
- Machen Sie bewusst längere Pausen
- Variieren Sie Tonhöhe und Lautstärke

### Wenn Transkription schlecht ist
- Prüfen Sie Mikrofon-Einstellungen
- Sprechen Sie näher zum Mikrofon
- Reduzieren Sie Hintergrundgeräusche
- Wechseln Sie zu einem größeren Modell

## 📝 Demo-Notizen

### Wichtige Punkte zu betonen
- ✅ **Vollständig offline** - keine Daten verlassen den Computer
- ✅ **DSGVO-konform** - entwickelt für therapeutische Anwendungen
- ✅ **Einfache Installation** - keine IT-Kenntnisse erforderlich
- ✅ **Therapeutisch relevant** - ATO→SEM Marker-System
- ✅ **Professionelle Exports** - für Dokumentation geeignet

### Häufige Fragen
**Q: Wie genau ist die Emotionserkennung?**
A: Das System erkennt grundlegende emotionale Tendenzen. Es ist als Unterstützung gedacht, nicht als Diagnose-Tool.

**Q: Werden Daten in die Cloud übertragen?**
A: Nein, alle Daten bleiben lokal auf Ihrem Computer. Keine Internetverbindung nach der Installation erforderlich.

**Q: Kann ich eigene Marker hinzufügen?**
A: Das aktuelle MVP fokussiert auf bewährte ATO→SEM Marker. Erweiterungen sind für zukünftige Versionen geplant.

**Q: Wie lange dauert die Installation?**
A: Ca. 15-30 Minuten, abhängig von der Internetgeschwindigkeit für das Whisper-Modell.

---

**Viel Erfolg bei Ihrer Demo!**
