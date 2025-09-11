
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
TransRapport MVP - Haupteinstiegspunkt
Eine therapeutenfreundliche Desktop-Anwendung für Live-Transkription
"""

import sys
import os
from PyQt6.QtWidgets import QApplication
from PyQt6.QtCore import QTranslator, QLocale
from gui import TransRapportMainWindow

def main():
    """Hauptfunktion - startet die TransRapport Anwendung"""
    app = QApplication(sys.argv)
    
    # App-Eigenschaften setzen
    app.setApplicationName("TransRapport MVP")
    app.setApplicationVersion("1.0.0")
    app.setOrganizationName("TransRapport")
    
    # Hauptfenster erstellen und anzeigen
    window = TransRapportMainWindow()
    window.show()
    
    # Event-Loop starten
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
