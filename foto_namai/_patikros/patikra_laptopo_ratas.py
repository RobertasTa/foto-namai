# patikra_laptopo_ratas.py - keturios kliurkos, rastos Roberto GYVAME rate
# ant SVETIMOS masinos (Win 11 laptopas, 2026-08-25). Visos keturios praejo
# pro 18 zaliu patikru, todel kiekvienai cia yra po sargyba.
#
#   17 - "Close" neverstas LT dialoguose (Qt standartinio mygtuko teksta
#        duoda pats Qt, o LT Qt vertimu pakete nera)
#   18 - "0.00 GB" 140 failams (~40 MB): sazininga, bet atrodo kaip nulis
#   19 - "Indexed DESKTOP-MAN disk D:: 140 files" - dvitaskis du kartus
#   20 - "D:/foto" salia "C:\\Users\\..." - Qt dialogas grazina pasvirus
#
# LEISTI is foto_namai:
#   QT_QPA_PLATFORM=offscreen <venv python> -u _patikros\patikra_laptopo_ratas.py

import os
import sys
from pathlib import Path

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")
os.environ["FOTONAMAI_LANG"] = "lt"

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

KLAIDOS = []


def chk(pavadinimas, salyga, detale=""):
    if not salyga:
        KLAIDOS.append("FAIL %s %s" % (pavadinimas, detale))


def tikrinti_18_dydzius():
    """Dydis zmogui: po 1 GB ribos NEBERODOM nuliniu GB."""
    import models
    # Roberto rato atvejis: 140 demo failu buvo ~40 MB -> rode "0.00 GB"
    chk("18_42MB", models.dydis_tekstu(42 * 1048576) == "42 MB",
        models.dydis_tekstu(42 * 1048576))
    chk("18_nera_nulinio_GB", "0.00 GB" != models.dydis_tekstu(42 * 1048576))
    # ribos
    chk("18_1GB", models.dydis_tekstu(1073741824) == "1.00 GB",
        models.dydis_tekstu(1073741824))
    chk("18_maziau_uz_MB", models.dydis_tekstu(5000).endswith("KB"),
        models.dydis_tekstu(5000))
    # dideli skaiciai lieka GB (E: diskas - 549 GB)
    chk("18_549GB", models.dydis_tekstu(549 * 1073741824).endswith("GB"))


def tikrinti_19_dvitaski():
    """Lentynos vardas PATS baigiasi dvitaskiu - formatas nededa antro.

    DEMESIO (spraga, pagauta rasant sia patikra): LT rezime t() grazina
    PATI RAKTA, todel t("...") tikrintu MANO eilute, o ne koda. Todel
    imam TIKRA zodyno rakta ir TIKRA gui_langas.py teksta."""
    from kalba import _EN
    vardas = "DESKTOP-MAN disk D:"          # tikras autovardas is rato

    raktai = [k for k in _EN if k.startswith("Indeksuota ")]
    chk("19_raktas_vienas", len(raktai) == 1, raktai)
    for raktas in raktai:
        for zyme, eil in (("lt", raktas), ("en", _EN[raktas])):
            chk("19_nera_dvigubo_" + zyme,
                "::" not in eil.format(vardas, 140, 0, 2, 0, 0),
                eil.format(vardas, 140, 0, 2, 0, 0))

    # Pats iskvietimas gui_langas.py - kad raktas ir kodas neissiskirtu
    saltinis = (Path(__file__).resolve().parent.parent
                / "gui_langas.py").read_text(encoding="utf-8")
    chk("19_kode_nera_dvitaskio", 'Indeksuota {}:' not in saltinis,
        "gui_langas.py tebeturi 'Indeksuota {}:'")


def tikrinti_20_kelia(win):
    """Qt dialogas grazina "D:/foto"; medyje turi atsidurti Windows stilius.

    Tikrinam MUSU koda, ne Path() elgesi: pakeiciam dialoga netikru, kuris
    grazina pasvirus brūksnius, ir ziurim, kas atsidure medyje."""
    from PyQt6.QtWidgets import QFileDialog
    tikrasis = QFileDialog.getExistingDirectory
    QFileDialog.getExistingDirectory = staticmethod(
        lambda *a, **kw: "D:/TESTAS_nuotraukos")
    try:
        pries = win._medis.topLevelItemCount()
        win._prideti_aplanka()
        chk("20_saltinis_prideta", win._medis.topLevelItemCount() > pries)
        if win._medis.topLevelItemCount() > pries:
            it = win._medis.topLevelItem(win._medis.topLevelItemCount() - 1)
            rodomas = it.text(0)
            chk("20_rodomas_be_pasviru", "/" not in rodomas, rodomas)
            kelias = it.data(0, getattr(
                __import__("gui_langas"), "_KELIO_ROLE"))
            chk("20_duomenys_be_pasviru", "/" not in str(kelias), kelias)
    finally:
        QFileDialog.getExistingDirectory = tikrasis


def tikrinti_17_mygtukus(win):
    """LT rezime NE VIENAS dialogo mygtukas negali likti angliskas.

    Rasta 5 vietose, todel tikrinam ir bendra vaista (isversti_mygtukus,
    klausti), ir tikrus dialogus. "OK" praleidziamas SAMONINGAI - zr.
    komentara gui_langas._MYGTUKU_RAKTAI."""
    from PyQt6.QtWidgets import QDialogButtonBox, QMessageBox
    import gui_langas
    from kalba import t

    ANGLISKI = ("Close", "Yes", "No", "Cancel")

    def svarus(tekstas):
        """Qt standartiniai mygtukai turi akceleratoriu: "&Yes", "&No".
        BE sito lyginimas su "Yes" NESUTAMPA ir patikra tampa teatru -
        pagauta sabotuojant 2026-08-25 (antra tokia spraga per diena)."""
        return tekstas.replace("&", "")

    chk("17_raktas_yra", t("Uzdaryti") != "Close",
        "LT rezime t('Uzdaryti') grazino Close")

    # a) bendras vaistas isverčia VISUS zodyno mygtukus
    deze = gui_langas.isversti_mygtukus(QDialogButtonBox(
        QDialogButtonBox.StandardButton.Close
        | QDialogButtonBox.StandardButton.Cancel
        | QDialogButtonBox.StandardButton.Yes
        | QDialogButtonBox.StandardButton.No))
    for btn in deze.buttons():
        chk("17_bendras_vaistas", svarus(btn.text()) not in ANGLISKI,
            btn.text())
    deze.deleteLater()

    # b) klausti() - Yes/No dialogas, kuris naudojamas 4 vietose
    pagauti = []
    tikrasis = QMessageBox.exec

    def netikras(self):
        pagauti.append([b.text() for b in self.buttons()])
        return QMessageBox.StandardButton.No

    QMessageBox.exec = netikras
    try:
        gui_langas.klausti(win, "T", "T")
    finally:
        QMessageBox.exec = tikrasis
    chk("17_klausti_iskvieste", len(pagauti) == 1, pagauti)
    for tekstai in pagauti:
        for tekstas in tekstai:
            chk("17_klausti_isversta", svarus(tekstas) not in ANGLISKI, tekstas)

    # c) tikri dialogai
    for vardas, kuriklis in (("apie", win._on_apie),
                             ("instrukcija", win._on_instrukcija)):
        dlg = _sukurti_dialoga(win, kuriklis)
        if dlg is None:
            chk("17_dialogas_" + vardas, False, "nepavyko sukurti")
            continue
        dezes = dlg.findChildren(QDialogButtonBox)
        chk("17_deze_" + vardas, len(dezes) == 1, len(dezes))
        for deze in dezes:
            for btn in deze.buttons():
                chk("17_isverstas_" + vardas, svarus(btn.text()) not in ANGLISKI,
                    btn.text())
                chk("17_lt_tekstas_" + vardas, svarus(btn.text()) == t("Uzdaryti"),
                    btn.text())
        dlg.deleteLater()


def tikrinti_23_skrinsotu_medi():
    """KLIURKA 23 (Roberto ratas su TIKRAIS duomenimis 2026-08-25): 6869
    skrinsotai nuejo i VIENA ploksti aplanka. Dabar - ta pati Metai\\Menuo
    taisykle kaip nuotraukoms; be patikimos datos lieka saknyje."""
    import models
    import tvarkytojas

    grupe = tvarkytojas._tikslo_grupe("2026-03-24T09:52:24", True,
                                      "skrinsotas", None)
    chk("23_su_data", grupe == models.GRUPE_SKRINSOTAI + "\\2026\\03", grupe)
    chk("23_nera_ploksčio", grupe != models.GRUPE_SKRINSOTAI, grupe)

    # be patikimos datos - saknyje (NE "_SCREENSHOTS\\_UNDATED": archyve
    # negali buti dvieju _UNDATED skirtingose vietose)
    be_datos = tvarkytojas._tikslo_grupe(None, False, "skrinsotas", None)
    chk("23_be_datos", be_datos == models.GRUPE_SKRINSOTAI, be_datos)
    nepatikima = tvarkytojas._tikslo_grupe("2026-03-24T09:52:24", False,
                                           "skrinsotas", None)
    chk("23_nepatikima", nepatikima == models.GRUPE_SKRINSOTAI, nepatikima)

    # etikete skrinsotams NETAIKOMA (butu "Screenshots" is aplanko vardo)
    su_etikete = tvarkytojas._tikslo_grupe("2026-03-24T09:52:24", True,
                                           "skrinsotas", "Screenshots")
    chk("23_be_etiketes", su_etikete == models.GRUPE_SKRINSOTAI + "\\2026\\03",
        su_etikete)

    # nuotrauku elgsena NEPAKITO
    foto = tvarkytojas._tikslo_grupe("2019-07-13T10:00:00", True, "foto", None)
    chk("23_foto_nepakito", foto == "2019\\07", foto)
    foto_et = tvarkytojas._tikslo_grupe("2019-07-13T10:00:00", True, "foto",
                                        "Atostogos Palanga")
    chk("23_foto_etikete", foto_et == "2019\\07 Atostogos Palanga", foto_et)
    chk("23_neatpazintas_nejudinamas",
        tvarkytojas._tikslo_grupe(None, False, "neatpazintas", None) is None)


def tikrinti_24_persidengiantys_saltiniai():
    """KLIURKA 24 (Roberto gyvas ratas 2026-08-25, rasta jam pridejus
    Pictures\\Screenshots PO Pictures): tas pats failas per du
    persidengiancius saltinius patekdavo i indeksa DU KARTUS, nes kelias
    buvo skaiciuojamas nuo SALTINIO, o ne nuo lentynos (tomo) saknies.
    Rezultatas: 13757 irasu vietoj 6887 ir "0 unchanged" vietoj 6869."""
    import shutil
    import tempfile
    import indeksas
    import indeksavimas

    darbinis = tempfile.mkdtemp(prefix="fn_k24_")
    try:
        tevas = Path(darbinis) / "Pictures"
        vaikas = tevas / "Screenshots"
        vaikas.mkdir(parents=True)
        # 1x1 PNG - tikras vaizdas, kad praeitu magic bytes patikra
        png = bytes.fromhex(
            "89504e470d0a1a0a0000000d494844520000000100000001080600000"
            "01f15c4890000000a49444154789c6360000002000100ffff03000006"
            "000557bfabd40000000049454e44ae426082")
        (vaikas / "Screenshot 2026-03-24 095224.png").write_bytes(png)
        (tevas / "IMG_0001.png").write_bytes(png)

        db = str(Path(darbinis) / "indeksas.db")
        con = indeksas.atidaryti(db)
        lid = indeksas.registruoti_lentyna(con, "K24-TEST", "Testas")

        st1 = indeksavimas.indeksuoti(str(tevas), con, lid, db)
        chk("24_pirmas_saltinis", st1["indeksuota"] == 2, st1["indeksuota"])

        # TAS PATS Roberto veiksmas: pridedam PAKATALOGI, jau esanti indekse
        st2 = indeksavimas.indeksuoti(str(vaikas), con, lid, db)
        chk("24_antras_nieko_naujo", st2["indeksuota"] == 0, st2)
        chk("24_atpazinta_kaip_nepakite",
            st2["nepakite_praleista"] == 1, st2)

        viso = con.execute("SELECT COUNT(*) FROM failai").fetchone()[0]
        chk("24_be_dubliu", viso == 2, viso)

        keliai = [r[0] for r in con.execute(
            "SELECT santykinis_kelias FROM failai ORDER BY 1")]
        chk("24_keliai_unikalus", len(set(keliai)) == len(keliai), keliai)
        # kelias TURI buti nuo tomo saknies - t.y. su "Pictures" viduje
        chk("24_kelias_nuo_tomo",
            all("Pictures" in k for k in keliai), keliai)

        # absoliutus kelias atkuriamas teisingai (GUI dbl-click grandine)
        saknis, kelias = con.execute(
            "SELECT saltinio_saknis, santykinis_kelias FROM failai"
            " WHERE vardas LIKE 'Screenshot%'").fetchone()
        chk("24_absoliutus_veikia", (Path(saknis) / kelias).exists(),
            str(Path(saknis) / kelias))
        con.close()

        # --- MIGRACIJA senoms bazems (liecia ZMONIU duomenis!) ---
        # Simuliuojam Roberto baze: tas pats failas dviem adresais,
        # user_version=3 (pries kliurkos 24 pataisa).
        db2 = str(Path(darbinis) / "sena.db")
        con = indeksas.atidaryti(db2)
        lid2 = indeksas.registruoti_lentyna(con, "K24-SENA", "Sena")
        anchor = Path(darbinis).anchor
        vidus = str((vaikas / "Screenshot 2026-03-24 095224.png")
                    .relative_to(tevas))
        for saltinis, kelias in ((str(tevas), vidus),
                                 (str(vaikas),
                                  "Screenshot 2026-03-24 095224.png")):
            con.execute(
                "INSERT INTO failai (lentyna_id, santykinis_kelias, vardas,"
                " dydis, mtime, busena, saltinio_saknis)"
                " VALUES (?,?,?,?,?,'SUINDEKSUOTAS',?)",
                (lid2, kelias, "Screenshot 2026-03-24 095224.png", 70, 1.0,
                 saltinis))
        con.execute("PRAGMA user_version = 3")
        con.commit()
        pries = con.execute("SELECT COUNT(*) FROM failai").fetchone()[0]
        chk("24_migr_pries", pries == 2, pries)
        con.close()

        indeksas.pasiimti_migraciju_valymus()      # nunulinam skaitliuka
        con = indeksas.atidaryti(db2)              # migracija ivyksta cia
        po = con.execute("SELECT COUNT(*) FROM failai").fetchone()[0]
        chk("24_migr_dublis_dingo", po == 1, po)
        chk("24_migr_versija",
            con.execute("PRAGMA user_version").fetchone()[0] == 4)
        chk("24_migr_suskaiciuota",
            indeksas.pasiimti_migraciju_valymus() == 1)
        likes = con.execute(
            "SELECT saltinio_saknis, santykinis_kelias FROM failai"
        ).fetchone()
        chk("24_migr_kelias_nuo_tomo", likes[0] == anchor, likes)
        chk("24_migr_kelias_pilnas", "Screenshots" in likes[1], likes)
        con.close()
    finally:
        shutil.rmtree(darbinis, ignore_errors=True)


def tikrinti_21_archyvo_antraste():
    """KLIURKA 21: antraste nebegali siusti zmogaus RASYTI naujo vardo -
    Windows dialogas taip aplanko nesukuria ("Path does not exist")."""
    from kalba import _EN
    raktai = [k for k in _EN if k.startswith("Archyvo aplankas:")]
    chk("21_nauja_antraste", len(raktai) == 1, raktai)
    chk("21_senos_nebera",
        not any(k.startswith("Pasirinkite NAUJA") for k in _EN),
        "kalba.py tebeturi sena antraste")
    saltinis = (Path(__file__).resolve().parent.parent
                / "gui_langas.py").read_text(encoding="utf-8")
    chk("21_kode_nebera", "Pasirinkite NAUJA" not in saltinis,
        "gui_langas.py tebeturi sena antraste")


def _sukurti_dialoga(win, kuriklis):
    """Dialogai modaliniai (exec) - pagaunam juos NEPALEIDE exec():
    laikinai pakeiciam QDialog.exec i tuscia funkcija ir pasiimam langa."""
    from PyQt6.QtWidgets import QDialog
    pagauti = []
    tikrasis = QDialog.exec

    def netikras(self):
        pagauti.append(self)
        return 0

    QDialog.exec = netikras
    try:
        kuriklis()
    finally:
        QDialog.exec = tikrasis
    return pagauti[0] if pagauti else None


def main():
    from PyQt6.QtWidgets import QApplication
    app = QApplication(sys.argv)
    import gui_langas

    tikrinti_18_dydzius()
    tikrinti_19_dvitaski()
    tikrinti_21_archyvo_antraste()
    tikrinti_23_skrinsotu_medi()
    tikrinti_24_persidengiantys_saltiniai()

    win = gui_langas.MainWindow()
    tikrinti_17_mygtukus(win)
    tikrinti_20_kelia(win)
    win.close()
    del app

    for k in KLAIDOS:
        print(k)
    if KLAIDOS:
        print("PATIKRA: FAIL (%d)" % len(KLAIDOS))
        sys.exit(1)
    print("PATIKRA: OK (laptopo ratas: 17 mygtukai, 18 dydziai,"
          " 19 dvitaskis, 20 bruksniai, 21 antraste, 23 skrinsotai,"
          " 24 persidengiantys saltiniai)")


if __name__ == "__main__":
    main()
