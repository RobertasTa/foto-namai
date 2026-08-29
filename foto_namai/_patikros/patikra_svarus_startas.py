# patikra_svarus_startas.py - PIRMAS PALEIDIMAS SVARIOJE SISTEMOJE.
#
# KLIURKA 11 (2026-08-23, Roberto GUI ratas): kompiuteryje, kur
# %LOCALAPPDATA%\PhotoHome dar NEEGZISTUOJA, indeksavimas krito su
# "unable to open database file" - SQLite failo neegzistuojanciame
# kataloge nesukuria. Roberto masinoje kliurka buvo nematoma, nes tas
# katalogas ten guli nuo vardo migracijos; visos patikros arba paduodavo
# db_kelias, arba pacios susikurdavo kataloga. Reikejo TUSCIOS naujos
# vietos - ja netycia davė izoliacinis SKOLA_A gui testo bat'as.
#
# Si patikra saugo butent ta atveji: nauja masina, nulis pedsaku.
# LEISTI is foto_namai: <venv python> -u _patikros\patikra_svarus_startas.py

import os
import sys
import tempfile
import time
from pathlib import Path

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")
os.environ["FOTONAMAI_LANG"] = "lt"

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import indeksas   # noqa: E402

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
    # --- 1. DB lygis: atidaryti() svariame, dar nesukurtame kataloge ---
    with tempfile.TemporaryDirectory(prefix="fn_svarus_db_") as tmp:
        naujas = Path(tmp) / "PhotoHome" / "indeksas.db"
        chk("katalogo_pries_nebuvo", not naujas.parent.exists())
        try:
            con = indeksas.atidaryti(naujas)
            con.close()
            pavyko = True
        except Exception as e:
            pavyko = False
            chk("db_atsidare", False, repr(e))
        if pavyko:
            chk("db_failas_yra", naujas.exists(), str(naujas))

    # --- 2. GILUS kelias (keli lygiai is karto) ---
    with tempfile.TemporaryDirectory(prefix="fn_svarus_gilus_") as tmp:
        gilus = Path(tmp) / "a" / "b" / "c" / "indeksas.db"
        try:
            con = indeksas.atidaryti(gilus)
            con.close()
            chk("gilus_kelias", gilus.exists(), str(gilus))
        except Exception as e:
            chk("gilus_kelias", False, repr(e))

    # --- 3. TIKRAS kelias: GUI su data_dir i neegzistuojancia vieta ---
    # Butent taip elgiasi pirmas paleidimas naujoje masinoje: langas
    # gimsta, zmogus prideda aplanka ir spaudzia "Indeksuoti".
    from PyQt6.QtWidgets import QApplication

    import saugykla

    app = QApplication([])
    with tempfile.TemporaryDirectory(prefix="fn_svarus_gui_") as tmp:
        tuscia = Path(tmp) / "AppData" / "PhotoHome"     # NEEGZISTUOJA
        saugykla.data_dir = lambda: tuscia
        chk("gui_data_dir_pries_nebuvo", not tuscia.exists())

        import gui_langas
        win = gui_langas.MainWindow(testinis=True)   # kelias is data_dir!

        saltinis = Path(tmp) / "SALTINIS"
        saltinis.mkdir()
        from PIL import Image
        Image.new("RGB", (40, 30), (200, 120, 60)).save(
            str(saltinis / "nuotrauka.jpg"), "JPEG")

        win.prideti_saltini("Testas", str(saltinis), pazymetas=True)
        win._indeksuoti_start()
        chk("gui_indeksavimas_baige", laukti(app, win))

        zurnalas = win._zurnalas.toPlainText()
        chk("gui_be_db_klaidos", "unable to open database" not in zurnalas,
            zurnalas[-300:])
        chk("gui_db_sukurta", (tuscia / "indeksas.db").exists(),
            "nera %s" % (tuscia / "indeksas.db"))

        try:
            con = indeksas.atidaryti_ro(tuscia / "indeksas.db")
            kiek = con.execute("SELECT COUNT(*) FROM failai").fetchone()[0]
            con.close()
            chk("gui_failas_indekse", kiek == 1, "indekse %d" % kiek)
        except Exception as e:
            # Be pataisos DB cia isvis neegzistuoja - verdiktas turi likti
            # skaitomas sarasas, ne zalias Traceback.
            chk("gui_failas_indekse", False, repr(e))

    if KLAIDOS:
        print("\n".join(KLAIDOS))
        print("NEPAVYKO: %d" % len(KLAIDOS))
        return 1
    print("OK - svarios sistemos pirmas paleidimas veikia"
          " (DB lygis, gilus kelias, GUI ratas)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
