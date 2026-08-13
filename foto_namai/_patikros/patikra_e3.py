# patikra_e3.py - E3 GUI patikra offscreen: zvalgyba + indeksavimas per
# tikrus QThread workerius ant poligono (67 failai). LEISTI is foto_namai:
# <venv python> -u _patikros\patikra_e3.py

import os
import sys
import tempfile
import time
from pathlib import Path

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")
os.environ["FOTONAMAI_LANG"] = "lt"

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from PyQt6.QtWidgets import QApplication

import gui_langas
import indeksas

SAVARTYNAS = (Path(__file__).resolve().parent.parent.parent
              / "_poligonas" / "SAVARTYNAS")

KLAIDOS = []


def chk(pavadinimas, salyga, detale=""):
    if not salyga:
        KLAIDOS.append("FAIL %s %s" % (pavadinimas, detale))


def laukti(app, win, sekundes=120):
    """Sukam event loop kol darbininko gija baigsis (polling - saugu ir
    tada, kai darbas baige anksciau, nei prisijungtume prie signalo)."""
    galas = time.time() + sekundes
    while time.time() < galas:
        app.processEvents()
        th = win._thread
        try:
            if th is None or not th.isRunning():
                for _ in range(10):
                    app.processEvents()
                return True
        except RuntimeError:
            return True
        time.sleep(0.02)
    return False


def main():
    app = QApplication([])
    with tempfile.TemporaryDirectory(prefix="fotonamai_e3_") as tmp:
        db = Path(tmp) / "indeksas.db"
        win = gui_langas.MainWindow(db_kelias=db, testinis=True)

        it = win.prideti_saltini("Poligonas", str(SAVARTYNAS),
                                 pazymetas=True)
        chk("suma_pradzia",
            "1 saltinis - ivercio dar nera" in win._suma.text(),
            win._suma.text())

        # --- zvalgyba ---
        win._zvalgyba_start()
        chk("zv_baige", laukti(app, win))
        iv = it.data(0, gui_langas._IVERCIO_ROLE)
        chk("zv_failai", iv is not None and iv["failai"] == 67, iv)
        chk("zv_medyje", it.text(1) == "67", it.text(1))
        chk("zv_suma", "~67 failu" in win._suma.text(), win._suma.text())
        chk("zv_mygtukai", win._btn_indeksuoti.isEnabled())

        # --- indeksavimas ---
        win._indeksuoti_start()
        chk("ind_baige", laukti(app, win))
        z = win._zurnalas.toPlainText()
        chk("ind_zurnalas", "Is viso suindeksuota 67" in z, z[-300:])

        con = indeksas.atidaryti_ro(db)
        kiek = con.execute("SELECT COUNT(*) FROM failai").fetchone()[0]
        lent = con.execute("SELECT COUNT(*) FROM lentynos").fetchone()[0]
        con.close()
        chk("db_failai", kiek == 67, kiek)
        chk("db_lentynos", lent == 1, lent)

        # --- pakartotinis indeksavimas: viskas nepakite ---
        win._indeksuoti_start()
        chk("ind2_baige", laukti(app, win))
        z = win._zurnalas.toPlainText()
        chk("ind2_nepakite", "67 nepakite" in z, z[-300:])

        win.close()

    if KLAIDOS:
        for k in KLAIDOS:
            print(k)
        print("PATIKRA: FAIL (%d klaidu)" % len(KLAIDOS))
        sys.exit(1)
    print("PATIKRA: OK (E3 GUI: zvalgyba + indeksavimas + inkrementas)")


if __name__ == "__main__":
    main()
