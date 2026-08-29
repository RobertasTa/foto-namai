# patikra_kopiju_langas.py - KOPIJU langas ir kliurka 13 (lokalizacija).
#
# Roberto radiniai gyvame rate 2026-08-23:
#   (a) apie kopijas buvo TIK eilute zurnale - "ispet ispejo, o galimybes
#       nueiti susitvarkyti dubliu nedave"; dabar langas su Testi/Sustoti;
#   (b) KLIURKA 13: tas sakinys buvo kietai lietuviskas ir EN vartotojui
#       rodydavosi lietuviskai.
# Tikrinam: skaiciavima, abi kalbas ir tai, kad langas TIKRAI turi tuos
# tris dalykus, del kuriu jis ir daromas (identiskumas / panasiu nematau /
# pasirinksiu pati).
# LEISTI is foto_namai: <venv python> -u _patikros\patikra_kopiju_langas.py

import os
import sys
import tempfile
from pathlib import Path

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import ataskaita   # noqa: E402
import indeksas    # noqa: E402
import kalba       # noqa: E402

KLAIDOS = []


def chk(pavadinimas, salyga, detale=""):
    if not salyga:
        KLAIDOS.append("FAIL %s %s" % (pavadinimas, detale))


def _irasyti(con, lentyna_id, kelias, dydis, hash_reiksme):
    con.execute(
        "INSERT INTO failai (lentyna_id, santykinis_kelias, vardas, dydis,"
        " mtime, hash, busena) VALUES (?,?,?,?,?,?,'SUINDEKSUOTAS')",
        (lentyna_id, kelias, kelias.split("\\")[-1], dydis, 1.0,
         hash_reiksme))


def main():
    # --- 1. kopiju skaiciavimas (spr. 27, 2026-08-29: DYDZIO ivertis) --
    # A1 hash nuimtas - indeksavimas hash neberaso, tad kopiju_info
    # privalo veikti su hash=None. SABOTAZAS: jei uzklausa liktu
    # "GROUP BY hash ... hash IS NOT NULL", su None grazintu 0 ir
    # kopiju_kiekis kristu.
    with tempfile.TemporaryDirectory(prefix="fn_kopijos_") as tmp:
        db = Path(tmp) / "indeksas.db"
        con = indeksas.atidaryti(db)
        lid = indeksas.registruoti_lentyna(con, "KOPIJU-TESTAS", "Testas")

        # 3 vienodo dydzio failai (2 pertekliniai) po 1 MB, BE hash
        for i in range(3):
            _irasyti(con, lid, "a\\foto%d.jpg" % i, 1048576, None)
        # 2 vienodo dydzio failai (1 perteklinis) po 2 MB, BE hash
        for i in range(2):
            _irasyti(con, lid, "b\\kita%d.jpg" % i, 2097152, None)
        # unikalaus dydzio - i skaiciu nepatenka
        _irasyti(con, lid, "c\\viena.jpg", 4194304, None)
        con.commit()

        info = ataskaita.kopiju_info(con, riba=1)
        chk("info_nera_None", info is not None)
        if info:
            kiek, baitai = info
            chk("kopiju_kiekis", kiek == 3, kiek)          # 2 + 1
            chk("kopiju_baitai", baitai == 2 * 1048576 + 2097152, baitai)

        # 0 baitu failai vienodo "dydzio", bet NE kandidatai
        _irasyti(con, lid, "d\\tuscia1.jpg", 0, None)
        _irasyti(con, lid, "d\\tuscia2.jpg", 0, None)
        con.commit()
        info = ataskaita.kopiju_info(con, riba=1)
        chk("nulio_baitu_neskaiciuoja", info == (3, 2 * 1048576 + 2097152),
            info)

        # Ivertis IS VIRSAUS: vienodo dydzio SKIRTINGAS turinys (hash
        # zinomi ir skiriasi) vis tiek skaiciuojamas kandidatu - todel
        # GUI tekste "~" ir "galimai".
        _irasyti(con, lid, "e\\kita_a.jpg", 3145728, "hashDDD")
        _irasyti(con, lid, "e\\kita_b.jpg", 3145728, "hashEEE")
        con.commit()
        info = ataskaita.kopiju_info(con, riba=1)
        chk("dydzio_ivertis_is_virsaus", info is not None and info[0] == 4,
            info)

        # riba: 4 kandidatai, riba 5 -> tylime
        chk("riba_veikia", ataskaita.kopiju_info(con, riba=5) is None)
        con.close()

    # --- 2. KLIURKA 13: abi kalbos ------------------------------------
    raktai = [
        "Yra kopiju",
        "Panasu, kad ~%d failai kartojasi (vienodo dydzio, ~%s).",
        "Skaicius - ivertis pagal vienoda failo dydi; pries keldamas i"
        " archyva turini patikrinsiu baitas i baita, tad tikras kopiju"
        " skaicius gali buti kiek mazesnis.",
        "Testi",
        "Sustoti",
        "Supratau",
        "Sustabdyta - kopijas galite susitvarkyti su Smart Duplicate"
        " Finder.",
        "Kopiju suvestine: ~{} failai galimai kartojasi (~{}). Patarimas:"
        " pirma Smart Duplicate Finder, tada archyvo kurimas.",
    ]
    kalba.LANG = "en"
    for r in raktai:
        chk("EN vertimas: " + r[:34], kalba.t(r) != r, "liko lietuviskas")
    kalba.LANG = "lt"
    for r in raktai:
        chk("LT tekstas: " + r[:34], kalba.t(r) == r)

    # --- 3. langas sako VISUS tris dalykus (abiem kalbom) -------------
    from PyQt6.QtWidgets import QApplication, QMessageBox

    app = QApplication.instance() or QApplication([])
    for lang, zymes, a_zymes in (
            ("lt", ("IDENTISKUS", "Panasiu nematau",
                    "pasirinksiu pagal patikimesne data",
                    "Smart Duplicate Finder", "ivertis"),
             ("DABAR", "smart-duplicate-finder", "ispesiu dar karta")),
            ("en", ("IDENTICAL", "Similar", "more reliable date",
                    "Smart Duplicate Finder", "estimate"),
             ("NOW", "smart-duplicate-finder", "warn you once more"))):
        kalba.LANG = lang
        import gui_langas
        with tempfile.TemporaryDirectory(prefix="fn_kopijos_gui_") as tmp:
            win = gui_langas.MainWindow(db_kelias=Path(tmp) / "i.db",
                                        testinis=True)
            langas, testi = win.paruosti_kopiju_langa(284, 1503238553)
            visas = langas.text() + "\n" + langas.informativeText()
            for z in zymes:
                chk("%s tekste: %s" % (lang, z), z in visas, visas[:120])
            chk("%s dydis GB" % lang, "1.40 GB" in visas, langas.text())
            chk("%s kiekis" % lang, "284" in visas, langas.text())
            mygtukai = [b.text() for b in langas.buttons()]
            chk("%s du mygtukai" % lang, len(mygtukai) == 2, mygtukai)
            chk("%s testi mygtukas" % lang, testi in langas.buttons())
            chk("%s testi ne Sustoti" % lang,
                testi.text() != [b for b in langas.buttons()
                                 if b is not testi][0].text())
            langas.deleteLater()
            # 4e p. 2: informacinis variantas A pakopos pabaigai
            langas_a, testi_a = win.paruosti_kopiju_langa(
                284, 1503238553, po_indeksavimo=True)
            visas_a = langas_a.text() + "\n" + langas_a.informativeText()
            for z in a_zymes:
                chk("%s A-gale tekste: %s" % (lang, z), z in visas_a,
                    visas_a[:120])
            chk("%s A-gale vienas mygtukas" % lang,
                len(langas_a.buttons()) == 1,
                [b.text() for b in langas_a.buttons()])
            chk("%s A-gale be Testi" % lang, testi_a is None)
            langas_a.deleteLater()
            win.close()
    kalba.LANG = "lt"

    # --- 4. KLIURKA 16: .md failai archyve - vartotojo kalba -----------
    import indeksavimas
    import tvarkytojas
    poligonas = (Path(__file__).resolve().parent.parent.parent
                 / "_poligonas" / "SAVARTYNAS")
    for lang, zymes in (("lt", ("KAIP SUTVARKYTA", "Taisykles",
                                "UNDO zurnalas")),
                        ("en", ("HOW THIS ARCHIVE IS SORTED", "Rules",
                                "UNDO log"))):
        kalba.LANG = lang
        with tempfile.TemporaryDirectory(prefix="fn_md_") as tmp:
            import shutil
            saltinis = Path(tmp) / "S"
            shutil.copytree(poligonas, saltinis)
            archyvas = Path(tmp) / "A"
            archyvas.mkdir()
            db = Path(tmp) / "i.db"
            con = indeksas.atidaryti(db)
            lid = indeksas.registruoti_lentyna(con, "MD-%s" % lang, "S")
            indeksavimas.indeksuoti(saltinis, con, lid, db)
            tvarkytojas.siulyti_plana(con)
            tvarkytojas.patvirtinti_plana(con)
            tvarkytojas.vykdyti(con, db, archyvas, rezimas="kopijuoti")
            k1 = ataskaita.kaip_sutvarkyta_md(con, archyvas)
            k2 = ataskaita.undo_zurnalas_md(con, archyvas)
            tekstas = (k1.read_text(encoding="utf-8")
                       + k2.read_text(encoding="utf-8"))
            for z in zymes:
                chk("%s .md: %s" % (lang, z), z in tekstas, tekstas[:90])
            # aplanku vardai .md faile LIEKA angliski abiem kalbom (spr. 43)
            chk("%s .md aplankai angliski" % lang,
                "_SCREENSHOTS" in tekstas or "_UNDATED" in tekstas,
                tekstas[:200])
            con.close()
    kalba.LANG = "lt"

    if KLAIDOS:
        for k in KLAIDOS:
            print(k)
        print("PATIKRA: FAIL (%d klaidu)" % len(KLAIDOS))
        return 1
    print("PATIKRA: OK (kopiju langas + .md failai vartotojo kalba)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
