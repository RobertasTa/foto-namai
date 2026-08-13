# patikra_e4_gui.py - E4 GUI patikra offscreen: pilna B pakopa per
# workerius (planas -> vykdymas -> UNDO) testiniu rezimu (be dialogu).
# LEISTI is foto_namai: <venv python> -u _patikros\patikra_e4_gui.py

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

SAVARTYNAS = (Path(__file__).resolve().parent.parent.parent
              / "_poligonas" / "SAVARTYNAS")

KLAIDOS = []


def chk(pavadinimas, salyga, detale=""):
    if not salyga:
        KLAIDOS.append("FAIL %s %s" % (pavadinimas, detale))


def laukti_kol(app, salyga, sekundes=120):
    galas = time.time() + sekundes
    while time.time() < galas:
        app.processEvents()
        if salyga():
            for _ in range(10):
                app.processEvents()
            return True
        time.sleep(0.02)
    return False


def main():
    app = QApplication([])
    with tempfile.TemporaryDirectory(prefix="fotonamai_e4gui_",
                                     ignore_cleanup_errors=True) as tmp:
        tmp = Path(tmp)
        db = tmp / "indeksas.db"
        archyvas = tmp / "ARCHYVAS"
        archyvas.mkdir()
        win = gui_langas.MainWindow(db_kelias=db, testinis=True)
        win.prideti_saltini("Poligonas", str(SAVARTYNAS), pazymetas=True)

        win._indeksuoti_start()
        chk("ind", laukti_kol(app, lambda: "Is viso suindeksuota 67"
                              in win._zurnalas.toPlainText()))

        win._archyvas_start(tikslo_kelias=str(archyvas))
        chk("tvarkymas", laukti_kol(app, lambda: "Tvarkymas baigtas"
                                    in win._zurnalas.toPlainText()))
        z = win._zurnalas.toPlainText()
        # 67 - 2 neatpazinti - 4 dubliai = 61 (be E4 variklio testo Live poros)
        chk("tv_skaiciai", "61 sutvarkyta, 4 dubliu praleista" in z,
            z[-250:])
        arch_failu = sum(1 for f in archyvas.rglob("*") if f.is_file())
        chk("tv_archyvas", arch_failu == 63, arch_failu)  # 61 + 2 .md
        chk("tv_md", (archyvas / "KAIP_SUTVARKYTA.md").exists())

        win._undo_start()
        chk("undo", laukti_kol(app, lambda: "UNDO baigtas"
                               in win._zurnalas.toPlainText()))
        z = win._zurnalas.toPlainText()
        chk("undo_skaiciai", "61 atstatyta, 0 klaidu" in z, z[-250:])
        po_undo = sum(1 for f in archyvas.rglob("*") if f.is_file())
        chk("undo_tuscia", po_undo == 2, po_undo)  # liko tik .md ataskaitos

        win.close()

    if KLAIDOS:
        for k in KLAIDOS:
            print(k)
        print("PATIKRA: FAIL (%d klaidu)" % len(KLAIDOS))
        sys.exit(1)
    print("PATIKRA: OK (E4 GUI: planas -> vykdymas -> UNDO per workerius)")


if __name__ == "__main__":
    main()
