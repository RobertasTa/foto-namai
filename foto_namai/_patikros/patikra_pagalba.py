# patikra_pagalba.py - "?" kampelio patikra (PLANAS sprendimas 37).
# Offscreen: mygtukas yra, meniu 2 punktai, README LT/EN randami ir
# neturiu, abieju kalbu raktai zodyne. LEISTI is foto_namai:
# QT_QPA_PLATFORM=offscreen <venv python> -u _patikros\patikra_pagalba.py

import os
import sys
from pathlib import Path

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")
os.environ["FOTONAMAI_LANG"] = "lt"

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from PyQt6.QtWidgets import QApplication, QPushButton

KLAIDOS = []


def chk(pavadinimas, salyga, detale=""):
    if not salyga:
        KLAIDOS.append("FAIL %s %s" % (pavadinimas, detale))


def main():
    app = QApplication(sys.argv)
    import gui_langas
    import models
    win = gui_langas.MainWindow()

    # mygtukas su seimos objectName ir meniu is 2 punktu
    btn = win.findChild(QPushButton, "btn_help")
    chk("btn_help_yra", btn is not None)
    if btn is not None:
        chk("btn_meniu", btn.menu() is not None)
        if btn.menu() is not None:
            veiksmu = [a.text() for a in btn.menu().actions()]
            chk("meniu_punktai", len(veiksmu) == 3, veiksmu)

    # README abiem kalbom yra salia kodo ir netusti; juose - versija
    for vardas in ("README.txt", "README-en.txt"):
        kelias = win._res_kelias(vardas)
        chk("yra_" + vardas, kelias.exists(), kelias)
        if kelias.exists():
            tekstas = kelias.read_text(encoding="utf-8")
            chk("netuscias_" + vardas, len(tekstas) > 1000, len(tekstas))
            chk("versija_" + vardas, ("v" + models.VERSIJA) in tekstas)

    # kalbos raktai isversti (EN zodyne yra visi nauji raktai)
    from kalba import _EN
    for raktas in ("Pagalba", "Apie...", "Instrukcija", "Apie programa",
                   "Versija {v}", "Kurejo puslapis:",
                   "Nepavyko atidaryti: {}"):
        chk("kalbos_raktas", raktas in _EN, raktas)

    win.close()
    del app
    for k in KLAIDOS:
        print(k)
    if KLAIDOS:
        print("PATIKRA: FAIL (%d)" % len(KLAIDOS))
        sys.exit(1)
    print("PATIKRA: OK (pagalbos kampelis: mygtukas + meniu + README x2"
          " + kalbos raktai)")


if __name__ == "__main__":
    main()
