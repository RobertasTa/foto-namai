# patikra_kliurka25.py - krikstynu Cancel VIENODAS visiems diskams.
#
# KLIURKA 25 (Roberto gyvas ratas 2026-08-28): vidiniam diskui paspaudes
# Cancel jis tikejosi atsaukti operacija, o indeksavimas prasidejo su
# autovardu (spr. 38 "lieka pasiulymas"). Dabar Cancel = praleisti
# saltini si karta - kaip isimamam. OK su savo vardu / tusciu lauku
# veikia kaip anksciau.
# LEISTI is foto_namai: <venv python> -u _patikros\patikra_kliurka25.py

import os
import sys
import tempfile
from pathlib import Path

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from PyQt6.QtWidgets import QApplication   # noqa: E402

import gui_langas   # noqa: E402

KLAIDOS = []


def chk(pavadinimas, salyga, detale=""):
    if salyga:
        print("  OK   %s" % pavadinimas)
    else:
        KLAIDOS.append(pavadinimas)
        print("  FAIL %s %s" % (pavadinimas, detale))


print("== KLIURKA 25: krikstynu Cancel = praleisti saltini ==")
app = QApplication.instance() or QApplication([])
with tempfile.TemporaryDirectory(prefix="fn_k25_") as tmp:
    tmp = Path(tmp)
    saltinis = tmp / "Foto"
    saltinis.mkdir()
    win = gui_langas.MainWindow(db_kelias=tmp / "i.db", testinis=False)
    originalus = gui_langas.klausti_vardo
    try:
        # 1. Cancel (ok=False) - saltinis PRALEIDZIAMAS (gruzina None),
        #    nesvarbu kad diskas vidinis (fixed)
        gui_langas.klausti_vardo = lambda *a, **k: ("", False)
        chk("cancel_praleidzia_vidini",
            win._lentynos_paruosimas(str(saltinis)) is None)

        # 2. OK su savo vardu - vardas imamas
        gui_langas.klausti_vardo = lambda *a, **k: ("Mano diskas", True)
        s = win._lentynos_paruosimas(str(saltinis))
        chk("ok_savas_vardas", s is not None and s["vardas"] == "Mano diskas",
            s)

        # 3. OK su tusciu lauku - lieka siulomas autovardas
        gui_langas.klausti_vardo = lambda *a, **k: ("", True)
        s = win._lentynos_paruosimas(str(saltinis))
        chk("ok_tuscias_lieka_siulymas",
            s is not None and s["vardas"], s)
    finally:
        gui_langas.klausti_vardo = originalus
        win.close()

if KLAIDOS:
    print("PATIKRA RAUDONA: %d klaidos" % len(KLAIDOS))
    sys.exit(1)
print("PATIKRA ZALIA (3/3)")
