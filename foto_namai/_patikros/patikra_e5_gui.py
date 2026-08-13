# patikra_e5_gui.py - E5 paieskos skirtuko patikra offscreen: indeksavimas
# ant poligono, paieska per tikra QThread cikla, miniatiuru kesas, filtru
# roundtrip, issaugotos paieskos combo, pasisveikinimas. LEISTI is foto_namai:
# <venv python> -u _patikros\patikra_e5_gui.py

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
import paieska
import saugykla

SAVARTYNAS = (Path(__file__).resolve().parent.parent.parent
              / "_poligonas" / "SAVARTYNAS")

KLAIDOS = []


def chk(pavadinimas, salyga, detale=""):
    if not salyga:
        KLAIDOS.append("FAIL %s %s" % (pavadinimas, detale))


def laukti(app, win, sekundes=180):
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
    with tempfile.TemporaryDirectory(prefix="fotonamai_e5_") as tmp:
        # Izoliacija: miniatiuru kesas ir kalba.txt i temp, ne i LOCALAPPDATA
        saugykla.data_dir = lambda: Path(tmp) / "data"

        import gui_langas   # po data_dir lopo - saugu ir taip, bet svaru
        db = Path(tmp) / "indeksas.db"
        win = gui_langas.MainWindow(db_kelias=db, testinis=True)

        # Poligone kameros EXIF NERA (generatorius Make/Model neraso) -
        # kameros grandinei atskiras sintetinis saltinis su tikru EXIF.
        import piexif
        from PIL import Image
        kameros_dir = Path(tmp) / "KAMEROS"
        kameros_dir.mkdir()
        img = Image.new("RGB", (640, 480), (120, 160, 200))
        exif_bytes = piexif.dump({
            "0th": {piexif.ImageIFD.Make: b"Canon",
                    piexif.ImageIFD.Model: b"EOS 70D"},
            "Exif": {piexif.ExifIFD.DateTimeOriginal:
                     b"2018:07:15 12:00:00"}})
        img.save(kameros_dir / "IMG_7001.jpg", "JPEG", exif=exif_bytes)
        # Sprendimas 36: ne medija NEindeksuojama - pdf turi buti praleistas
        (kameros_dir / "aprasymas.pdf").write_bytes(b"%PDF-1.4 fake")

        # --- suindeksuojam poligona + kameros saltini (E3 receptas) ---
        win.prideti_saltini("Poligonas", str(SAVARTYNAS), pazymetas=True)
        win.prideti_saltini("Kameros", str(kameros_dir), pazymetas=True)
        win._indeksuoti_start()
        chk("ind_baige", laukti(app, win))
        con = indeksas.atidaryti_ro(db)
        viso_db = con.execute("SELECT COUNT(*) FROM failai").fetchone()[0]
        skrinsotu_db = con.execute(
            "SELECT COUNT(*) FROM failai WHERE turinio_tipas='skrinsotas'"
        ).fetchone()[0]
        kamera_db = con.execute(
            "SELECT kamera, datetaken FROM failai WHERE kamera IS NOT NULL"
        ).fetchall()
        con.close()
        chk("ind_68", viso_db == 68, viso_db)
        chk("kamera_stulpelis",
            kamera_db == [("Canon EOS 70D", "2018-07-15T12:00:00")],
            kamera_db)
        chk("ne_medija_zurnale",
            "1 ne medija" in win._zurnalas.toPlainText(),
            "pdf turejo buti praleistas kaip ne medija")

        # Sprendimas 36 migracija: i DB ranka ikisus pdf irasa, kitas
        # atidarymas (user_version 0) ji isvalo
        con = indeksas.atidaryti(db)
        con.execute("PRAGMA user_version = 0")
        con.execute(
            "INSERT INTO failai (lentyna_id, santykinis_kelias, vardas,"
            " dydis, mtime, busena) VALUES (1, 'x\\senas.pdf', 'senas.pdf',"
            " 5, 1.0, 'SUINDEKSUOTAS')")
        con.commit()
        con.close()
        con = indeksas.atidaryti(db)
        liko = con.execute("SELECT COUNT(*) FROM failai"
                           " WHERE vardas='senas.pdf'").fetchone()[0]
        viso_po = con.execute("SELECT COUNT(*) FROM failai").fetchone()[0]
        con.close()
        chk("migracija_36", liko == 0 and viso_po == 68,
            "liko=%d viso=%d" % (liko, viso_po))

        # --- paieska be filtru ---
        win._paieska_start(filtrai={})
        chk("p_baige", laukti(app, win))          # paieska + miniatiuros
        chk("p_kiekis", win._rezultatai.count() == viso_db,
            win._rezultatai.count())
        chk("p_info", str(viso_db) in win._p_info.text(),
            win._p_info.text())

        # --- miniatiuru kesas atsirado (tikri jpg poligone yra) ---
        kesas = list((Path(tmp) / "data" / "miniatiuros").glob("*.jpg"))
        chk("miniatiuros", len(kesas) >= 10, len(kesas))

        # --- rikiavimas: pirmas rezultatas turi data, be datos - gale ---
        pirmas = win._rezultatai.item(0).data(gui_langas._KELIO_ROLE)
        paskutinis = win._rezultatai.item(
            win._rezultatai.count() - 1).data(gui_langas._KELIO_ROLE)
        chk("rikiavimas_pirmas", pirmas["datetaken"] is not None, pirmas)
        chk("rikiavimas_none_gale",
            paskutinis["datetaken"] is None
            or all(win._rezultatai.item(i).data(
                gui_langas._KELIO_ROLE)["datetaken"] is not None
                for i in range(win._rezultatai.count())),
            "yra irasu be datos, bet jie ne gale")

        # --- filtras tipas=skrinsotas per GUI worker ---
        win._paieska_start(filtrai={"tipas": "skrinsotas"})
        chk("p2_baige", laukti(app, win))
        chk("p2_skrinsotai", win._rezultatai.count() == skrinsotu_db,
            "%d != %d" % (win._rezultatai.count(), skrinsotu_db))

        # --- filtras kamera per GUI worker ---
        win._paieska_start(filtrai={"kamera": "canon"})
        chk("p3_baige", laukti(app, win))
        chk("p3_kamera", win._rezultatai.count() == 1,
            win._rezultatai.count())

        # --- filtru roundtrip: _nustatyti_filtrus -> _p_filtrai ---
        filtrai = {"data_nuo": "2015-01-01", "data_iki": "2020-12-31",
                   "etikete": "Jonines", "tipas": "foto"}
        win._nustatyti_filtrus(filtrai)
        chk("filtru_roundtrip", win._p_filtrai() == filtrai,
            win._p_filtrai())
        win._nustatyti_filtrus({})
        chk("filtru_isvalymas", win._p_filtrai() == {}, win._p_filtrai())

        # --- neteisinga data -> None + zurnalas ---
        win._nustatyti_filtrus({"data_nuo": "2015-99-99"})
        chk("bloga_data", win._p_filtrai() is None)
        chk("bloga_data_zurnale",
            "Neteisinga data" in win._zurnalas.toPlainText())
        win._nustatyti_filtrus({})

        # --- issaugotos paieskos: combo pildosi ---
        con = indeksas.atidaryti(db)
        paieska.issaugoti_vaizda(con, "Testinis vaizdas",
                                 {"tipas": "skrinsotas"})
        con.close()
        win._vaizdu_combo_pildyti()
        chk("vaizdu_combo", win._p_vaizdai.count() == 2,
            win._p_vaizdai.count())
        # pasirinkus vaizda - filtrai issideda ir paieska ivyksta
        win._p_vaizdai.setCurrentIndex(1)
        win._on_vaizdas_pasirinktas(1)
        chk("vaizdo_paieska_baige", laukti(app, win))
        chk("vaizdo_filtrai_gui",
            win._p_tipas.currentData() == "skrinsotas",
            win._p_tipas.currentData())
        chk("vaizdo_rezultatai", win._rezultatai.count() == skrinsotu_db,
            win._rezultatai.count())

        # --- lentynu combo (Visos + poligono ir temp tomu lentynos) ---
        chk("lentynu_combo", win._p_lentyna.count() >= 2,
            win._p_lentyna.count())

        win.close()

        # --- pasisveikinimas naujoje sesijoje ---
        win2 = gui_langas.MainWindow(db_kelias=db, testinis=True)
        chk("pasisveikinimas",
            "Sveiki sugrize" in win2._zurnalas.toPlainText(),
            win2._zurnalas.toPlainText()[:200])
        win2.close()

    if KLAIDOS:
        for k in KLAIDOS:
            print(k)
        print("PATIKRA: FAIL (%d klaidu)" % len(KLAIDOS))
        sys.exit(1)
    print("PATIKRA: OK (E5 GUI: paieska + miniatiuros + vaizdai +"
          " pasisveikinimas)")


if __name__ == "__main__":
    main()
