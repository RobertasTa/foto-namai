"""smoke_langas.py - E0 patikra: tuscias langas pakyla <1 s.

Matuoja laika nuo proceso starto iki lango parodymo; langas pats
uzsidaro po 1.5 s. LEISTI: <venv python> -u _patikros\\smoke_langas.py
(is foto_namai katalogo).
"""

import sys
import time
from pathlib import Path

START = time.perf_counter()

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from PyQt6.QtCore import QTimer
from PyQt6.QtWidgets import QApplication

from gui_langas import MainWindow


def main():
    app = QApplication(sys.argv)
    win = MainWindow()
    win.show()
    app.processEvents()   # priverciam nupiesti pries matuojant
    uztruko = time.perf_counter() - START
    print("Langas ekrane per %.3f s (importai + konstravimas + show)" % uztruko)
    print("PATIKRA: %s (riba 1.0 s)" % ("OK" if uztruko < 1.0 else "PER LETAI"))
    QTimer.singleShot(1500, app.quit)
    app.exec()


if __name__ == "__main__":
    main()
