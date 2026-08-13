# patikra_lentynu_langas.py - statuso mygtukas "Indekse: ..." atidaro
# lentynu sarasa (Roberto zvilgsnis 2026-08-13). Tikrinama offscreen:
# dialogo eilutes, GYVA prijungimo busena pagal serial (ne DB laukas),
# failu skaiciai, mygtuko objectName. LEISTI is foto_namai:
# <venv python> -u _patikros\patikra_lentynu_langas.py

import os
import sys
import tempfile
import time
from pathlib import Path

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")
os.environ["FOTONAMAI_LANG"] = "lt"

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from PyQt6.QtWidgets import QApplication

import indeksas
import lentynos
import saugykla

KLAIDOS = []


def chk(pavadinimas, salyga, detale=""):
    if not salyga:
        KLAIDOS.append("FAIL %s %s" % (pavadinimas, detale))


def main():
    app = QApplication([])
    with tempfile.TemporaryDirectory(prefix="fotonamai_lent_") as tmp:
        saugykla.data_dir = lambda: Path(tmp) / "data"
        import gui_langas

        db = Path(tmp) / "indeksas.db"
        con = indeksas.atidaryti(db)
        # Lentyna 1: TIKRAS C: serial (turi buti "prijungta")
        c_serial = lentynos.volume_info("C:\\")[0]
        lid1 = indeksas.registruoti_lentyna(con, c_serial, "Kompo diskas")
        # Lentyna 2: isgalvotas serial (turi buti "neprijungta")
        lid2 = indeksas.registruoti_lentyna(con, "DEADBEEF", "Stalciaus WD")
        dabar = time.time()
        for i in range(3):
            con.execute(
                "INSERT INTO failai (lentyna_id, santykinis_kelias, vardas,"
                " dydis, mtime, busena) VALUES (?,?,?,?,?, 'SUINDEKSUOTAS')",
                (lid1, "a\\f%d.jpg" % i, "f%d.jpg" % i, 10, dabar))
        con.execute(
            "INSERT INTO failai (lentyna_id, santykinis_kelias, vardas,"
            " dydis, mtime, busena) VALUES (?,?,?,?,?, 'SUINDEKSUOTAS')",
            (lid2, "b\\g.jpg", "g.jpg", 10, dabar))
        con.commit()
        con.close()

        win = gui_langas.MainWindow(db_kelias=db, testinis=True)

        chk("mygtuko objectName",
            win._indekso_busena.objectName() == "btn_lentynos")
        chk("mygtukas rodo turta",
            "2" in win._indekso_busena.text(), win._indekso_busena.text())

        pagauta = []
        orig_exec = gui_langas.LentynuDialogas.exec

        def _pagauti(self):
            lent = self._lentele
            for i in range(lent.rowCount()):
                pagauta.append(tuple(lent.item(i, j).text()
                                     for j in range(4)))
            return 1

        gui_langas.LentynuDialogas.exec = _pagauti
        win._indekso_busena.click()
        gui_langas.LentynuDialogas.exec = orig_exec

        chk("eiluciu 2", len(pagauta) == 2, pagauta)
        pagal_varda = {e[0]: e for e in pagauta}
        chk("kompo diskas yra", "Kompo diskas" in pagal_varda, pagauta)
        chk("stalciaus WD yra", "Stalciaus WD" in pagal_varda, pagauta)
        if len(pagal_varda) == 2:
            chk("kompo prijungta=Taip",
                pagal_varda["Kompo diskas"][1] == "Taip", pagauta)
            chk("WD prijungta=Ne",
                pagal_varda["Stalciaus WD"][1] == "Ne", pagauta)
            chk("kompo failu 3",
                pagal_varda["Kompo diskas"][3] == "3", pagauta)
            chk("WD failu 1",
                pagal_varda["Stalciaus WD"][3] == "1", pagauta)
        # --- kliurka 8: _pranesti_neprieinama tikrina GYVAI pagal serial ---
        win._zurnalas.clear()
        win._pranesti_neprieinama(
            {"volume_serial": "DEADBEEF", "prijungta": 1,
             "lentynos_vardas": "Stalciaus WD"}, Path("X:/nera.jpg"))
        chk("neprijungta zinute (nors DB prijungta=1)",
            "neprijungta" in win._zurnalas.toPlainText(),
            win._zurnalas.toPlainText())
        win._zurnalas.clear()
        win._pranesti_neprieinama(
            {"volume_serial": c_serial, "prijungta": 0,
             "lentynos_vardas": "Kompo diskas"}, Path("C:/tikrai_nera.jpg"))
        chk("failas nerastas zinute (diskas gyvai prijungtas)",
            "Failas nerastas" in win._zurnalas.toPlainText(),
            win._zurnalas.toPlainText())
        win.close()

    if KLAIDOS:
        for k in KLAIDOS:
            print(k)
        print("PATIKRA: FAIL (%d)" % len(KLAIDOS))
        sys.exit(1)
    print("PATIKRA: OK (lentynu mygtukas: objectName, tekstas, dialogas,"
          " gyva prijungimo busena pagal serial, failu skaiciai)")


if __name__ == "__main__":
    main()
