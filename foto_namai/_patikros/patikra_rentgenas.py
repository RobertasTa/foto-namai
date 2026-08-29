# patikra_rentgenas.py - ARCHYVO RENTGENAS (4f p. 3, 2026-08-29).
#
# Tikrinam: skaicius is zinomos tiesos DB, LINIJA LAIKE su imties
# filtru (mazas triuksmingas metas linijos NEgriauna), bedaciu
# skaiciavima, praleistu katalogu skyriu, abi kalbas ir GUI langa.
# SABOTAZO kontrole viduje: isjungus imties filtra linija dingsta.
# LEISTI is foto_namai: <venv python> -u _patikros\patikra_rentgenas.py

import os
import sys
import tempfile
from pathlib import Path

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import indeksas    # noqa: E402
import kalba       # noqa: E402
import rentgenas   # noqa: E402

KLAIDOS = []


def chk(pavadinimas, salyga, detale=""):
    if not salyga:
        KLAIDOS.append("FAIL %s %s" % (pavadinimas, detale))


def _irasyti(con, lid, kelias, datetaken, patikima, saltinis,
             tipas="foto", dydis=1000):
    con.execute(
        "INSERT INTO failai (lentyna_id, santykinis_kelias, vardas, dydis,"
        " mtime, datetaken, patikima_data, datos_saltinis, turinio_tipas,"
        " busena) VALUES (?,?,?,?,?,?,?,?,?,'SUINDEKSUOTAS')",
        (lid, kelias, kelias.split("\\")[-1], dydis, 1.0, datetaken,
         patikima, saltinis, tipas))


def main():
    # --- 1. linija_nuo grynas ------------------------------------------
    # 2005 bloga (10 %), 2010/2012 geros, 2015 - MAZA imtis su 0 % -
    # imties filtras ja ignoruoja, linija lieka 2010.
    metai = [(2005, 30, 3), (2008, 10, 10), (2010, 25, 20),
             (2012, 40, 36), (2015, 5, 0)]
    chk("linija_2010", rentgenas.linija_nuo(metai) == 2010,
        rentgenas.linija_nuo(metai))
    chk("linija_nera", rentgenas.linija_nuo([(2005, 30, 3)]) is None)
    chk("linija_tuscia", rentgenas.linija_nuo([]) is None)

    # SABOTAZO kontrole: isjungus imties filtra (MIN_METU_IMTIS=1)
    # triuksmingas 2015 linija sugriauna -> filtras tikrai dirba.
    tikras = rentgenas.MIN_METU_IMTIS
    rentgenas.MIN_METU_IMTIS = 1
    chk("sabotazas_filtras_dirba", rentgenas.linija_nuo(metai) != 2010,
        "filtras nieko nekeicia - patikra teatras")
    rentgenas.MIN_METU_IMTIS = tikras

    # --- 2. duomenys + ataskaita is zinomos tiesos DB ------------------
    with tempfile.TemporaryDirectory(prefix="fn_rentgeno_") as tmp:
        con = indeksas.atidaryti(Path(tmp) / "i.db")
        lid = indeksas.registruoti_lentyna(con, "RENTGENO-T", "Lentyna A")
        eil_nr = [0]

        def kel(pref):
            eil_nr[0] += 1
            return "%s\\f%04d.jpg" % (pref, eil_nr[0])

        for kiek, pat_kiek, m in ((30, 3, 2005), (10, 10, 2008),
                                  (25, 20, 2010), (40, 36, 2012),
                                  (5, 0, 2015)):
            for i in range(kiek):
                pat = 1 if i < pat_kiek else 0
                _irasyti(con, lid, kel("m%d" % m),
                         "%d-06-01T12:00:00" % m, pat,
                         "exif" if pat else "mtime")
        for i in range(12):     # be datos (TIESA "-")
            _irasyti(con, lid, kel("bedatis"), None, None, None,
                     tipas="neatpazintas", dydis=0)
        con.commit()

        d = rentgenas.duomenys(con)
        chk("viso", d["viso"] == 122, d["viso"])
        chk("bedaciu", d["bedaciu"] == 53, d["bedaciu"])   # 41 mtime + 12
        chk("neatpazinta", d["neatpazinta"] == 12, d["neatpazinta"])
        chk("linija_is_db", d["linija_nuo"] == 2010, d["linija_nuo"])
        chk("lentynos_kiek", len(d["lentynos"]) == 1
            and d["lentynos"][0][1] == 122, d["lentynos"])

        praleisti = [("E:\\Backup senas", "kopiju pasaulis"),
                     ("E:\\System Volume Information", "juodasis sarasas")]
        for lang, zymes in (
                ("lt", ("KAS TAVO ARCHYVE", "Nuo ~2010", "53 (43.4 %)",
                        "Backup senas", "darbo zona", "UNDO",
                        "Lentyna `Lentyna A`")),
                ("en", ("WHAT IS IN YOUR ARCHIVE", "From ~2010",
                        "53 (43.4 %)", "Backup senas", "work zone",
                        "UNDO", "Shelf `Lentyna A`"))):
            kalba.LANG = lang
            md = rentgenas.ataskaita_md(con, praleisti)
            for z in zymes:
                chk("%s ataskaitoje: %s" % (lang, z), z in md, md[:200])
            chk("%s metu lentele" % lang, "| 2012 | 40 | 90 %" in md)
        kalba.LANG = "lt"

        # be praleistu - skyriaus nera
        md = rentgenas.ataskaita_md(con, [])
        chk("be_praleistu_skyriaus", "saugikliai" not in md)
        con.close()

    # --- 3. GUI langas -------------------------------------------------
    from PyQt6.QtWidgets import (QApplication, QPlainTextEdit,
                                 QPushButton)

    app = QApplication.instance() or QApplication([])
    import gui_langas
    with tempfile.TemporaryDirectory(prefix="fn_rentgeno_gui_") as tmp:
        win = gui_langas.MainWindow(db_kelias=Path(tmp) / "i.db",
                                    testinis=True)
        dlg = win.paruosti_rentgeno_langa("RENTGENO TEKSTAS 123")
        lauk = dlg.findChild(QPlainTextEdit, "rentgeno_tekstas")
        chk("gui_teksto_laukas", lauk is not None)
        if lauk:
            chk("gui_tekstas", lauk.toPlainText() == "RENTGENO TEKSTAS 123")
            chk("gui_read_only", lauk.isReadOnly())
        chk("gui_saugoti_mygtukas",
            dlg.findChild(QPushButton, "btn_rentgeno_saugoti") is not None)
        chk("gui_antraste", dlg.windowTitle() == kalba.t("Archyvo rentgenas"))
        dlg.deleteLater()
        win.close()

    if KLAIDOS:
        for k in KLAIDOS:
            print(k)
        print("PATIKRA: FAIL (%d klaidu)" % len(KLAIDOS))
        return 1
    print("PATIKRA: OK (rentgenas: linija laike + imties filtras +"
          " ataskaita LT/EN + praleisti katalogai + GUI langas)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
