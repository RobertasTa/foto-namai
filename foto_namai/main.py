"""main.py - FOTO namai paleidimas.

GUI-first taisykle (PLANAS sprendimas 15): langas ekrane per ~1 s, sunkios
bibliotekos (Pillow, EXIF, hash) kraunamos tik varikliui prireikus - jokiu
ju importu siame faile ar gui_langas virsuje.
"""

import ctypes
import sys

from PyQt6.QtWidgets import QApplication

from gui_langas import MainWindow


def main():
    # Windows taskbar rodo musu ikona, ne python.exe: procesas prisistato
    # savo AppUserModelID (be sito ikona atsiras tik exe builde).
    try:
        ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(
            "ClaudeGifts.FotoNamai")
    except Exception:
        pass
    app = QApplication(sys.argv)
    win = MainWindow()
    app.setWindowIcon(win.windowIcon())   # galioja ir dialogams
    win.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
