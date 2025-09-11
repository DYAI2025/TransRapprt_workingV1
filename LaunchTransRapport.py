#!/usr/bin/env python3
"""
TransRapport MVP - Python Launcher
Alternative One-Click-Lösung
"""

import os
import sys
import subprocess
import tkinter as tk
from tkinter import messagebox

def launch_transrapport():
    """TransRapport starten"""
    app_dir = os.path.expanduser("~/Applications/TransRapport")
    venv_python = os.path.join(app_dir, "venv", "bin", "python")
    main_script = os.path.join(app_dir, "main.py")
    
    if not os.path.exists(venv_python):
        messagebox.showerror("Fehler", "Virtual Environment nicht gefunden!\nBitte TransRapport neu installieren.")
        return
    
    if not os.path.exists(main_script):
        messagebox.showerror("Fehler", "main.py nicht gefunden!\nBitte TransRapport neu installieren.")
        return
    
    try:
        # TransRapport im App-Verzeichnis starten
        os.chdir(app_dir)
        subprocess.Popen([venv_python, main_script])
        print("✅ TransRapport gestartet!")
    except Exception as e:
        messagebox.showerror("Fehler", f"Fehler beim Starten von TransRapport:\n{e}")

if __name__ == "__main__":
    # Verstecke das Hauptfenster
    root = tk.Tk()
    root.withdraw()
    
    launch_transrapport()
    
    # Beende das Launcher-Skript
    root.quit()