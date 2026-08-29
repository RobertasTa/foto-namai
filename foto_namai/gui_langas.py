"""gui_langas.py - FOTO namai pagrindinis langas (E3 skeletas).

Saltiniu varnelu medis su zvalgybos iverciais (sprendimai 6, 32), seansu
buhalterijos uzuomazga, zurnalas, laikrodukas + atsaukimas kiekvienam
darbui (gelezine taisykle 11). QThread gyvavimo ciklas - grieztai pagal
OKF pyqt6_threading_guard recepta (nuorodos ant self, quit+deleteLater,
jokio nulinimo; signalai TIK i bound metodus).

E5 dalis 2: paieskos skirtukas (sprendimas 29) - indekso uzklausos,
miniatiuru tinklelis, dbl-click -> Explorer, issaugotos paieskos;
kalbos combobox + portable varnele (seimos DNR) + seansu pasisveikinimas.
"""

import json
import os
import subprocess
import sys
from datetime import date
from pathlib import Path

from PyQt6.QtCore import QSize, QStandardPaths, Qt, QThread, QTimer
from PyQt6.QtGui import QColor, QFont, QIcon, QPainter, QPixmap
from PyQt6.QtWidgets import (QApplication, QCheckBox, QComboBox, QDialog,
                             QDialogButtonBox, QFileDialog, QFrame,
                             QHBoxLayout, QHeaderView,
                             QInputDialog, QLabel, QLineEdit, QListWidget,
                             QListWidgetItem, QMainWindow, QMessageBox,
                             QMenu, QPlainTextEdit, QPushButton,
                             QTableWidget, QTableWidgetItem, QTabWidget,
                             QTreeWidget, QTreeWidgetItem, QVBoxLayout,
                             QWidget)

import indeksas
import lentynos
import miniaturos
import models
import paieska
import redaktoriai
import saugykla
import stilius
import worker as workeriai
from kalba import kiekio_zodis, saltinio_zodis, t

_KELIO_ROLE = Qt.ItemDataRole.UserRole
_IVERCIO_ROLE = Qt.ItemDataRole.UserRole + 1


# --- macOS saka (2026-08-29): os.startfile ir explorer yra Windows-only.
# Platformu riba VIENOJE vietoje (SDF pamoka) - visi kvietimai eina per
# siuos du helperius.
def _atverti_os(kelias):
    """Failas OS numatyta programa (Windows startfile / macOS open)."""
    if sys.platform == "darwin":
        subprocess.Popen(["open", str(kelias)])
    else:
        os.startfile(str(kelias))


def _parodyti_tvarkykleje(kelias):
    """Parodyti faila su pazymejimu (Explorer /select / Finder open -R)."""
    if sys.platform == "darwin":
        subprocess.Popen(["open", "-R", str(kelias)])
    else:
        subprocess.Popen(["explorer", "/select,", str(kelias)])


# KLIURKA 17 (Roberto laptopo ratas 2026-08-25): Qt STANDARTINIU mygtuku
# teksta duoda pats Qt, o lietuvisku Qt vertimu pakete NERA - lietuviskuose
# languose kabojo "Close", "OK", "Cancel", "Yes", "No". Rasta 5 vietose is
# karto, todel vaistas VIENAS visiems, ne lopas kiekvienam dialogui.
# (Ta pati klaida gyvena ir SDF v1.4 - seimos spraga.)
# "OK" SAMONINGAI NEVERCIAM: QMessageBox.warning/.information yra STATINIAI
# metodai, ju mygtuko nepasieksim nekeiciant i instancinius (dar 4 vietos).
# Isvertus tik cia gautusi "Gerai" viename lange ir "OK" keturiuose - tai
# butu nenuoseklumas vietoj pataisymo. "OK" tarptautinis, "Close"/"Yes" - ne.
_MYGTUKU_RAKTAI = {
    "Cancel": "Atsaukti",
    "Close": "Uzdaryti",
    "Yes": "Taip",
    "No": "Ne",
}


def isversti_mygtukus(deze):
    """Isverciam VISUS standartinius mygtukus dezeje (QDialogButtonBox arba
    QMessageBox). Nezinomus paliekam kaip yra.

    DEMESIO: QMessageBox.button() ir QDialogButtonBox.button() reikalauja
    SAVO enum'o - reiksmes sutampa, bet PyQt6 tipai skirtingi ir svetimas
    enum'as meta TypeError. Todel zodyne laikom VARDUS, o enum'a imam pagal
    dezes tipa (pagauta patikros 2026-08-25 - butu sulauzę visus klausti()
    dialogus: UNDO, perziura, archyvo kurimas)."""
    enumas = (QMessageBox.StandardButton if isinstance(deze, QMessageBox)
              else QDialogButtonBox.StandardButton)
    for vardas, raktas in _MYGTUKU_RAKTAI.items():
        btn = deze.button(getattr(enumas, vardas))
        if btn is not None:
            btn.setText(t(raktas))
    return deze


def klausti(tevas, antraste, tekstas, numatytasis_taip=True):
    """QMessageBox.question pakaitalas su ISVERSTAIS mygtukais.
    Grazina True, jei zmogus paspaude "Taip"."""
    dlg = QMessageBox(tevas)
    dlg.setIcon(QMessageBox.Icon.Question)
    dlg.setWindowTitle(antraste)
    dlg.setText(tekstas)
    dlg.setStandardButtons(QMessageBox.StandardButton.Yes
                           | QMessageBox.StandardButton.No)
    dlg.setDefaultButton(QMessageBox.StandardButton.Yes if numatytasis_taip
                         else QMessageBox.StandardButton.No)
    isversti_mygtukus(dlg)
    return dlg.exec() == QMessageBox.StandardButton.Yes


def paruosti_vardo_dialoga(tevas, antraste, paaiskinimas, siulymas,
                           riba=models.LENTYNOS_VARDO_RIBA):
    """Krikstynu dialogas su KIETA riba lauke (KLIURKA 12, Roberto radinys
    ir jo sprendimas 2026-08-23): anksciau laukas leisdavo rasyti kiek nori,
    o programa TYLIAI nukirpdavo iki 40 - tas pats tylus perrasymas, kuri
    prikisame konkurentams. Dabar 41-as zenklas paprasciausiai nebesiveda:
    zmogus tai pajunta pirstais, be jokio papildomo langelio.
    Atskirta nuo exec() todel, kad patikra galetu patikrinti riba
    nepaleisdama modalinio lango."""
    dlg = QInputDialog(tevas)
    dlg.setWindowTitle(antraste)
    dlg.setLabelText(paaiskinimas)
    dlg.setTextValue(siulymas)          # laukas gimsta cia - tik po to findChild
    laukas = dlg.findChild(QLineEdit)
    if laukas is not None:
        laukas.setMaxLength(riba)
    return dlg


def klausti_vardo(tevas, antraste, paaiskinimas, siulymas):
    """Grazina (tekstas, ok) - toks pat kontraktas kaip QInputDialog.getText."""
    dlg = paruosti_vardo_dialoga(tevas, antraste, paaiskinimas, siulymas)
    ok = dlg.exec() == QDialog.DialogCode.Accepted
    return dlg.textValue(), ok


class PasiulymuDialogas(QDialog):
    """Sprendimas 25: programa SIULO plana lentele, zmogus zymi/koreguoja.
    NIEKAS nevykdoma - tik pasirinkimas. Grazina grupes per pasirinktos()."""

    def __init__(self, grupes, tevas=None):
        super().__init__(tevas)
        self.setWindowTitle(t("Namu archyvo pasiulymas"))
        self.resize(720, 480)
        stulpas = QVBoxLayout(self)
        stulpas.addWidget(QLabel(
            t("Programa siulo tokia tvarka. Nuimkite varnele nuo grupiu,"
              " kuriu dabar nekelti:")))
        self._lentele = QTableWidget(len(grupes), 3)
        self._lentele.setHorizontalHeaderLabels(
            [t("Grupe (aplankas archyve)"), t("Failai"), t("Dydis")])
        self._lentele.setColumnWidth(0, 380)
        self._lentele.setEditTriggers(
            QTableWidget.EditTrigger.NoEditTriggers)
        for i, g in enumerate(grupes):
            it = QTableWidgetItem(g["grupe"])
            it.setFlags(it.flags() | Qt.ItemFlag.ItemIsUserCheckable)
            it.setCheckState(Qt.CheckState.Checked)
            self._lentele.setItem(i, 0, it)
            self._lentele.setItem(
                i, 1, QTableWidgetItem(str(g["failai"])))
            self._lentele.setItem(
                i, 2, QTableWidgetItem(models.dydis_tekstu(g["baitai"])))
        stulpas.addWidget(self._lentele)
        self._perkelti = QCheckBox(
            t("Perkelti vietoj kopijuoti (originalai isnyks is saltiniu)"))
        stulpas.addWidget(self._perkelti)
        mygtukai = isversti_mygtukus(QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok
            | QDialogButtonBox.StandardButton.Cancel))
        mygtukai.accepted.connect(self.accept)
        mygtukai.rejected.connect(self.reject)
        stulpas.addWidget(mygtukai)

    def pasirinktos(self):
        rez = []
        for i in range(self._lentele.rowCount()):
            it = self._lentele.item(i, 0)
            if it.checkState() == Qt.CheckState.Checked:
                rez.append(it.text())
        return rez

    def rezimas(self):
        return "perkelti" if self._perkelti.isChecked() else "kopijuoti"


class LentynuDialogas(QDialog):
    """Lentynu sarasas (Roberto zvilgsnis 2026-08-13: '2 lentynos' kampe
    be vardu - neinformatyvu; tooltip 20-ciai lentynu netiktu, tad info
    tekstas paverstas MYGTUKU, kuris atidaro si langa su slinktimi)."""

    def __init__(self, eilutes, tevas=None):
        super().__init__(tevas)
        self.setWindowTitle(t("Lentynos"))
        self.resize(760, 400)
        stulpas = QVBoxLayout(self)
        lentele = QTableWidget(len(eilutes), 4)
        lentele.setHorizontalHeaderLabels([
            t("Lentyna"), t("Prijungta"),
            t("Paskutini karta matyta"), t("Failu")])
        lentele.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        lentele.verticalHeader().setVisible(False)
        lentele.setWordWrap(False)
        for i, (vardas, prijungta, matyta, failu) in enumerate(eilutes):
            reiksmes = (vardas,
                        t("Taip") if prijungta else t("Ne"),
                        (matyta or "").replace("T", " ")[:16],
                        str(failu))
            for j, tekstas in enumerate(reiksmes):
                lentele.setItem(i, j, QTableWidgetItem(tekstas))
        # 0 tempiasi su langu; 1-3 TAMPOMI ranka (Interactive - Roberto
        # pastaba: ResizeToContents stulpelius uzrakina) su pradiniais
        # plociais, kad antrastes ir datos tilptu is karto
        antraste = lentele.horizontalHeader()
        antraste.setSectionResizeMode(0, QHeaderView.ResizeMode.Stretch)
        for stulpelis, plotis in ((1, 95), (2, 185), (3, 70)):
            antraste.setSectionResizeMode(
                stulpelis, QHeaderView.ResizeMode.Interactive)
            lentele.setColumnWidth(stulpelis, plotis)
        self._lentele = lentele
        stulpas.addWidget(lentele)
        btn = QPushButton(t("Uzdaryti"))
        btn.setObjectName("btn_close")
        btn.clicked.connect(self.accept)
        eil = QHBoxLayout()
        eil.addStretch(1)
        eil.addWidget(btn)
        stulpas.addLayout(eil)


class MainWindow(QMainWindow):
    def __init__(self, db_kelias=None, testinis=False):
        super().__init__()
        self._testinis = testinis
        self._db_kelias = (Path(db_kelias) if db_kelias
                           else saugykla.data_dir() / "indeksas.db")
        self._thread = None
        self._worker = None
        # Spr. 45 KARTOTEKOS FONAS - atskiras slot'as, kad paieskos/skenai
        # jo nelauktu (pyqt6_threading_guard receptas galioja ir jam)
        self._fono_thread = None
        self._fono_worker = None
        self._sekundes = 0
        self._darbo_tekstas = ""
        self._laikrodis = QTimer(self)
        self._laikrodis.setInterval(1000)
        self._laikrodis.timeout.connect(self._tiksi)
        # Kartotekos fonas startuoja pats, kai langas jau gyvas (5 s) -
        # tik jei indeksas egzistuoja; testiniame rezime nelenda
        if not testinis:
            QTimer.singleShot(5000, self._fonas_start)

        self.setWindowTitle("PHOTO home")
        # Ikona - GPT draugo piesinys 2026-08-07 (_darbal\ikonos, gamyba
        # per _darbal\ikona_gamyba.py); _MEIPASS guard busimam exe.
        ikona = Path(getattr(sys, "_MEIPASS",
                             Path(__file__).resolve().parent)) / "ikona.ico"
        if ikona.exists():
            self.setWindowIcon(QIcon(str(ikona)))
        self.resize(1050, 680)
        self._statyti_ui()
        self._statyti_overlay()
        self._auto_aptikimas()
        self._atnaujinti_suma()
        self._pasisveikinimas()
        self._atnaujinti_indekso_busena()

    # ------------------------------------------------------------- UI statyba
    def _statyti_ui(self):
        centras = QWidget()
        stulpas = QVBoxLayout(centras)

        virsus = QHBoxLayout()
        antraste = QLabel(t("PHOTO home (FOTO namai) - nuotrauku"
                            " archyvo tvarkytojas"))
        antraste.setStyleSheet(stilius.ANTRASTE)
        virsus.addWidget(antraste, stretch=1)
        virsus.addWidget(self._statyti_pagalbos_mygtuka(),
                         alignment=Qt.AlignmentFlag.AlignTop)
        stulpas.addLayout(virsus)

        # Kalbos combobox - skirtuku juostos desiniajame kampe (Roberto
        # pastaba 2026-08-13 per E8 smoke, patikslinta gyvai: tame
        # paciame aukstyje kaip Tvarkymas/Paieska; apacioje tarp veiksmo
        # mygtuku jis pasimesdavo, EN vartotojas jo nerasdavo).
        self._cmb_kalba = QComboBox()
        self._cmb_kalba.addItem("Lietuvių", "lt")   # ASCII kode
        self._cmb_kalba.addItem("English", "en")
        from kalba import LANG as _dabartine_kalba
        self._cmb_kalba.setCurrentIndex(1 if _dabartine_kalba == "en" else 0)
        self._cmb_kalba.setToolTip(
            t("Kalba pritaikoma paleidus programa is naujo."))
        self._cmb_kalba.currentIndexChanged.connect(self._on_kalba_changed)

        # Du skirtukai (E5): A pakopos Tvarkymas + Paieska (sprendimas 29)
        tvarkymas = QWidget()
        stulpas_t = QVBoxLayout(tvarkymas)

        stulpas_t.addWidget(QLabel(t("Saltiniai (varneles - ka skenuoti):")))
        self._medis = QTreeWidget()
        self._medis.setColumnCount(3)
        self._medis.setHeaderLabels([t("Saltinis"), t("Failai"), t("Dydis")])
        self._medis.setColumnWidth(0, 560)
        self._medis.itemChanged.connect(self._on_item_changed)
        stulpas_t.addWidget(self._medis, stretch=3)

        self._suma = QLabel("")
        self._suma.setStyleSheet(stilius.STATUSAS)
        stulpas_t.addWidget(self._suma)

        eilute = QHBoxLayout()
        self._btn_prideti = QPushButton(t("Prideti aplanka..."))
        self._btn_prideti.setObjectName("btn_preview")
        self._btn_prideti.clicked.connect(self._prideti_aplanka)
        eilute.addWidget(self._btn_prideti)
        # Telefonas: Windows ji rodo ne kaip diska (MTP), skenuoti
        # tiesiogiai negalim - saziningas gidas vietoj apgaulingo
        # saltinio (Phone Link keso pamoka 2026-08-08: nuotraukos DB
        # viduje, dauguma be turinio - is auto-aptikimo isimtas).
        self._btn_telefonas = QPushButton(t("Kaip paimti is telefono?"))
        self._btn_telefonas.clicked.connect(self._telefono_gidas)
        eilute.addWidget(self._btn_telefonas)
        self._btn_zvalgyba = QPushButton(t("Zvalgyba (kiek failu?)"))
        self._btn_zvalgyba.setObjectName("btn_scan")
        self._btn_zvalgyba.clicked.connect(self._zvalgyba_start)
        eilute.addWidget(self._btn_zvalgyba)
        self._btn_indeksuoti = QPushButton(t("Indeksuoti pazymetus"))
        self._btn_indeksuoti.setObjectName("btn_clear_all")
        self._btn_indeksuoti.clicked.connect(self._indeksuoti_start)
        eilute.addWidget(self._btn_indeksuoti)
        self._btn_atsaukti = QPushButton(t("Atsaukti"))
        self._btn_atsaukti.setObjectName("btn_close")
        self._btn_atsaukti.setEnabled(False)
        self._btn_atsaukti.clicked.connect(self._atsaukti)
        eilute.addWidget(self._btn_atsaukti)
        eilute.addStretch(1)
        stulpas_t.addLayout(eilute)

        # B pakopa (VIZIJA "Dvi pakopos"): startuoja TIK mygtuku.
        # Atskirta linija + antraste (Roberto pastaba 2026-08-08: visi
        # mygtukai vienoje kruvoje - neaisku, kurie tarnauja saltiniu
        # medziui, kurie archyvui; SDF grupavimo pavyzdys).
        stulpas_t.addSpacing(8)
        linija = QFrame()
        linija.setFrameShape(QFrame.Shape.HLine)
        linija.setStyleSheet("color: #c5cbe0;")
        stulpas_t.addWidget(linija)
        stulpas_t.addWidget(QLabel(t("Namu archyvas (tvarkymas + UNDO):")))
        eilute2 = QHBoxLayout()
        self._btn_archyvas = QPushButton(t("Kurti namu archyva..."))
        self._btn_archyvas.setObjectName("btn_clear_all")
        self._btn_archyvas.clicked.connect(self._archyvas_start)
        eilute2.addWidget(self._btn_archyvas)
        self._btn_undo = QPushButton(t("UNDO - grazinti viska atgal"))
        self._btn_undo.setObjectName("btn_close")
        self._btn_undo.clicked.connect(self._undo_start)
        eilute2.addWidget(self._btn_undo)
        eilute2.addStretch(1)
        if sys.platform == "darwin":
            # macOS SAUGIKLIS (2026-08-29): B pakopa kilnoja ORIGINALUS,
            # o Mac buildas dar ne karto nematytas gyvai - iki pirmo gyvo
            # Mac testuotojo tvarkymas uzrakintas; A pakopa (indeksas,
            # paieska, rentgenas) nieko nekeicia ir veikia pilnai.
            uzrakto_tekstas = t(
                "macOS beta: tvarkymas isjungtas, kol neturime gyvo Mac"
                " testuotojo - katalogas ir paieska veikia pilnai.")
            self._btn_archyvas.setEnabled(False)
            self._btn_undo.setEnabled(False)
            self._btn_archyvas.setToolTip(uzrakto_tekstas)
            self._btn_undo.setToolTip(uzrakto_tekstas)

        # Kalbos combobox iskeltas i virsu prie "?" (Roberto pastaba
        # 2026-08-13); portable varneles GUI NEBERA (Roberto verdiktas
        # 2026-08-07: kompo irankis su DB; saugykla.py mechanizmas lieka).
        stulpas_t.addLayout(eilute2)

        self._tabs = QTabWidget()
        self._tabs.addTab(tvarkymas, t("Tvarkymas"))
        self._tabs.addTab(self._statyti_paieskos_tab(), t("Paieska"))
        # Kalba gyvena skirtuku eiluteje (enum pilnu keliu - OKF guard)
        self._tabs.setCornerWidget(self._cmb_kalba,
                                   Qt.Corner.TopRightCorner)
        # Zurnalas po skirtukais TEMPIAMAS uz krasto (Roberto gyvas demo
        # 2026-08-29: "gal galima pele uz krasto paemus zurnala
        # susimazinti? kad daugiau vietos miniatiuroms") - QSplitter
        from PyQt6.QtWidgets import QSplitter
        self._zurnalas = QPlainTextEdit()
        self._zurnalas.setReadOnly(True)
        apacia = QWidget()
        ap_stulpas = QVBoxLayout(apacia)
        ap_stulpas.setContentsMargins(0, 0, 0, 0)
        ap_stulpas.addWidget(QLabel(t("Zurnalas:")))
        ap_stulpas.addWidget(self._zurnalas)
        spl = QSplitter(Qt.Orientation.Vertical)
        spl.addWidget(self._tabs)
        spl.addWidget(apacia)
        spl.setStretchFactor(0, 5)
        spl.setStretchFactor(1, 1)
        spl.setCollapsible(0, False)   # skirtuku nesuploji netycia
        # Rankenele APCIUOPIAMA (Roberto demo 2 pastaba: "pele ant ribos
        # uzvedi - zenkliukas atsiranda"): storesne + matoma juostele
        # Rankenele RYSKI (Roberto demo 2026-08-29: "kaip Excel'yje -
        # pele ant ribos uzvedi ir tempi"): per visa ploti, "grip"
        # taskeliai centre, uzvedus - paryskeja (Qt kursoriu i SplitV
        # keicia pats). Ankstesnis margin 40% ja pasleps subtiliai.
        spl.setHandleWidth(10)
        spl.setStyleSheet(
            "QSplitter::handle:vertical {"
            " background: #d7dce8;"
            " border-top: 1px solid #b3bcd0;"
            " border-bottom: 1px solid #b3bcd0;"
            " image: none; }"
            "QSplitter::handle:vertical:hover { background: #aab6d4; }")
        stulpas.addWidget(spl, stretch=7)

        # Statuso juosta lango apacioje (Roberto pastaba 2026-08-07:
        # progresas mygtuku eiluteje nusikirpdavo; cia visas plotis ir
        # matosi is ABIEJU skirtuku). Kaireje - kas vyksta dabar,
        # desiniajame kampe - indekso turtas.
        apacia = QHBoxLayout()
        self._busena = QLabel("")
        self._busena.setStyleSheet(stilius.STATUSAS)
        apacia.addWidget(self._busena, stretch=1)
        # Indekso turtas - MYGTUKAS (Roberto zvilgsnis 2026-08-13):
        # tekstas informuoja, paspaudimas atidaro lentynu sarasa
        self._indekso_busena = QPushButton("")
        self._indekso_busena.setObjectName("btn_lentynos")
        self._indekso_busena.setStyleSheet(stilius.STATUSAS)
        self._indekso_busena.setCursor(Qt.CursorShape.PointingHandCursor)
        self._indekso_busena.setToolTip(t("Spustelekite - lentynu sarasas"))
        self._indekso_busena.clicked.connect(self._lentynu_langas)
        apacia.addWidget(self._indekso_busena)
        stulpas.addLayout(apacia)

        self.setCentralWidget(centras)
        # Vienas sarasas visiems darbo metu isjungiamiems mygtukams
        self._darbo_mygtukai = (
            self._btn_prideti, self._btn_zvalgyba, self._btn_indeksuoti,
            self._btn_archyvas, self._btn_undo, self._btn_ieskoti,
            self._btn_vaizda_saugoti, self._btn_vaizda_trinti)
        app = QApplication.instance()
        if app is not None:
            app.setStyleSheet(stilius.APP_QSS)   # galioja ir dialogams
        self._log(t("Indeksas: {}").format(self._db_kelias))

    # ---- "?" pagalbos kampelis (PLANAS sprendimas 37 - nuo gimimo;
    # etalonas SDF db8c0a6: winget/Store vartotojas README negauna,
    # tad instrukcija gyvena PACIOJE programoje) ----
    @staticmethod
    def _res_kelias(vardas):
        """Resurso kelias: salia .py arba _MEIPASS exe builde."""
        return Path(getattr(sys, "_MEIPASS",
                            Path(__file__).resolve().parent)) / vardas

    def _statyti_pagalbos_mygtuka(self):
        b = QPushButton("?")
        b.setObjectName("btn_help")
        b.setFixedSize(26, 26)
        b.setToolTip(t("Pagalba"))
        meniu = QMenu(b)
        meniu.addAction(t("Apie..."), self._on_apie)
        meniu.addAction(t("Instrukcija"), self._on_instrukcija)
        meniu.addAction(t("Neradote atsakymo? Klauskite DI"),
                        self._on_klausk_di)
        b.setMenu(meniu)
        return b

    def _on_klausk_di(self, klausimas=None):
        """Atidaro claude.ai su paruostu promptu (Roberto ideja
        2026-08-08): programa rase Claude, tad claude.ai atsakys
        tiksliausiai - variklis tas pats. claude.ai/new?q= tik
        UZPILDO lauka - siuncia pats vartotojas, tinklas TIK cia
        (offline DNR kaip GitHub nuorodos Apie lange).
        Pries narsykle - paaiskinamasis langas su logotipu
        (Roberto 2026-08-08: instrukcija 'net mociutems' - raudona
        juosta, kur rasyti klausima, kaip pakeisti kalba)."""
        import urllib.parse
        import webbrowser
        dlg = QMessageBox(self)
        dlg.setWindowTitle(t("Neradote atsakymo? Klauskite DI"))
        ico = self._res_kelias("ikona.ico")
        if ico.exists():
            dlg.setIconPixmap(QIcon(str(ico)).pixmap(64, 64))
        dlg.setText(t(
            "Kas ivyks paspaudus OK:\n\n"
            "1. Atsidarys interneto narsykle su DI padejejo\n"
            "   claude.ai puslapiu. Zinutes laukelyje jau bus\n"
            "   irasyta angliska pradzia - prisistatymas, kas per\n"
            "   programa ir kur jos kodas.\n"
            "2. NEISSIGASKITE raudono pranesimo virs zinutes -\n"
            "   claude.ai ji rodo visada, kai tekstas ateina per\n"
            "   nuoroda. Tai tik priminimas perskaityti, kas\n"
            "   siunciama.\n"
            "3. Zinutes gale, po zodziu \"My question:\", irasykite\n"
            "   SAVO klausima - galima lietuviskai! - ir spauskite\n"
            "   siuntimo mygtuka (rodykle). Klausti galima visko,\n"
            "   pvz.: \"kaip atsinaujinti programa i naujesne\n"
            "   versija? paaiskink zingsnis po zingsnio\".\n"
            "4. Jei DI atsakys angliskai - tiesiog paprasykite kita\n"
            "   zinute: \"atsakyk lietuviskai\", ir toliau bendraus\n"
            "   lietuviskai.\n\n"
            "Pastaba: claude.ai gali paprasyti prisijungti (nemokama\n"
            "paskyra). Niekas neissiunciama be jusu rankos."))
        dlg.setStandardButtons(QMessageBox.StandardButton.Ok
                               | QMessageBox.StandardButton.Cancel)
        isversti_mygtukus(dlg)          # kliurka 17
        if dlg.exec() != QMessageBox.StandardButton.Ok:
            return
        # Promptas VISADA anglu k. (Roberto patikslinimas 2026-08-08:
        # LLM su anglu draugauja geriausiai; kalba pokalbyje vartotojas
        # persijungs pats - jokiu papildomu nurodymu nededam).
        # 2026-08-22 SDF gyvo testo pamoka: be tiesioginio paminejimo
        # debesinis skaito TIK README ir brief'o neatranda.
        promptas = (
            'Hi! I am using the app "PHOTO home" (FOTO namai) - a home'
            " photo archive organizer. Its source code is public:"
            " https://github.com/RobertasTa/foto-namai."
            " Please FIRST read your briefing from the author:"
            " https://raw.githubusercontent.com/RobertasTa/"
            "foto-namai/master/AI_CONSULTANT_BRIEF.md"
            " - then the program's code and README, and answer my question"
            " in plain, human language - no programmer jargon."
            " My question: ")
        # Telefono klaidos langas (2026-08-28) paduoda paruosta klausima -
        # vartotojui liks tik spausti siuntima (arba papildyti savais
        # zodziais). klausimas gali ateiti ir kaip QAction checked=False -
        # guard'as praleidzia tik tikra teksta.
        if isinstance(klausimas, str) and klausimas:
            promptas += klausimas
        webbrowser.open("https://claude.ai/new?q="
                        + urllib.parse.quote(promptas))

    def _on_apie(self):
        """Apie... langelis (SDF receptas): logo, pavadinimas, aprasas,
        versija, GitHub nuoroda. Tinklas TIK paspaudus nuoroda."""
        dlg = QDialog(self)
        dlg.setWindowTitle(t("Apie programa"))
        lay = QVBoxLayout(dlg)
        virsus = QHBoxLayout()
        logo = QLabel()
        ico = self._res_kelias("ikona.ico")
        if ico.exists():
            logo.setPixmap(QIcon(str(ico)).pixmap(64, 64))
        virsus.addWidget(logo, alignment=Qt.AlignmentFlag.AlignTop)
        info = QVBoxLayout()
        pavadinimas = QLabel("PHOTO home (FOTO namai)")
        pavadinimas.setStyleSheet("font-size: 14pt; font-weight: bold;")
        info.addWidget(pavadinimas)
        info.addWidget(QLabel(
            t("Nuotrauku savartyno tvarkytojas - nieko netrina,"
              " viskas su UNDO.")))
        info.addWidget(QLabel(t("Versija {v}").format(v=models.VERSIJA)))
        autoriai = QLabel("Robertas & Claude")
        autoriai.setStyleSheet("color: #5a5e6b;")
        info.addWidget(autoriai)
        virsus.addLayout(info)
        lay.addLayout(virsus)
        # Repo nuoroda (vardas isspretas 2026-08-13: foto-namai);
        # ryski melyna + bold, kad matytusi jog spaudziama (SDF pamoka)
        nuoroda = QLabel(
            t("Kurejo puslapis:") + ' <a href="https://github.com/'
            'RobertasTa/foto-namai" style="color:#2f7ce0;'
            'font-weight:bold;">GitHub</a>')
        nuoroda.setOpenExternalLinks(True)
        lay.addWidget(nuoroda)
        mygtukai = isversti_mygtukus(
            QDialogButtonBox(QDialogButtonBox.StandardButton.Close))
        mygtukai.rejected.connect(dlg.reject)
        lay.addWidget(mygtukai)
        dlg.exec()

    def _on_instrukcija(self):
        """Instrukcija: ikeptas README (LT/EN pagal GUI kalba) rodomas
        pacios programos lange su slinktimi - JOKIO Notepad (SDF pamoka:
        atsidarydavo tuscias), jokiu failu kopiju diske, jokio tinklo."""
        from PyQt6.QtGui import QFont
        from kalba import LANG
        vardas = "README.txt" if LANG == "lt" else "README-en.txt"
        try:
            tekstas = self._res_kelias(vardas).read_text(
                encoding="utf-8", errors="replace")
        except OSError as e:
            QMessageBox.warning(
                self, t("Pagalba"), t("Nepavyko atidaryti: {}").format(e))
            return
        dlg = QDialog(self)
        dlg.setWindowTitle(t("Instrukcija"))
        lay = QVBoxLayout(dlg)
        rodinys = QPlainTextEdit(tekstas)
        rodinys.setReadOnly(True)
        # Monospace - kad README ASCII antrastes lygiuotusi
        rodinys.setFont(QFont("Consolas", 10))
        lay.addWidget(rodinys)
        mygtukai = isversti_mygtukus(
            QDialogButtonBox(QDialogButtonBox.StandardButton.Close))
        mygtukai.rejected.connect(dlg.reject)
        lay.addWidget(mygtukai)
        dlg.resize(780, 560)
        dlg.exec()

    def _statyti_overlay(self):
        """Didelis "vyksta darbas" uzrasas lango viduryje (valytuvo
        receptas; Roberto pastaba 2026-08-07: ne visi pazvelgs i apacios
        juosta). Modeless QFrame vaikas, NE dialogas. Apacios juosta
        lieka detalems (skaiciai, kampas)."""
        from PyQt6.QtWidgets import QFrame
        self._overlay = QFrame(self)
        self._overlay.setObjectName("darbo_overlay")
        self._overlay.setStyleSheet(
            "QFrame#darbo_overlay { background-color: #ffffff;"
            " border: 3px solid #b0b0b0; border-radius: 14px; }")
        eil = QHBoxLayout(self._overlay)
        eil.setContentsMargins(28, 18, 28, 18)
        eil.setSpacing(12)
        self._overlay_tekstas = QLabel("")
        self._overlay_tekstas.setStyleSheet(
            "font-size: 18px; font-weight: bold; color: #222; border: none;")
        eil.addWidget(self._overlay_tekstas)
        self._overlay_spin = QLabel("|")
        self._overlay_spin.setStyleSheet(
            "font-size: 18px; font-weight: bold; color: #3c4e99;"
            " border: none;")
        eil.addWidget(self._overlay_spin)
        self._overlay.hide()
        self._spin_kadrai = "|/-\\"
        self._spin_i = 0
        self._spin_laikrodis = QTimer(self)
        self._spin_laikrodis.setInterval(120)
        self._spin_laikrodis.timeout.connect(self._spin_tiksi)

    def _spin_tiksi(self):
        self._spin_i = (self._spin_i + 1) % len(self._spin_kadrai)
        self._overlay_spin.setText(self._spin_kadrai[self._spin_i])

    def _overlay_pozicija(self):
        self._overlay.adjustSize()
        self._overlay.move((self.width() - self._overlay.width()) // 2,
                           (self.height() - self._overlay.height()) // 3)

    def resizeEvent(self, event):
        super().resizeEvent(event)
        ov = getattr(self, "_overlay", None)
        if ov is not None and ov.isVisible():
            self._overlay_pozicija()

    def _statyti_paieskos_tab(self):
        """Paieskos skirtukas (sprendimas 29): filtrai -> miniatiuru
        TINKLELIS -> dbl-click Explorer; issaugotos paieskos-vaizdai.
        NE vartytuvas - perziurai Memories/IrfanView (riba nubrezta)."""
        w = QWidget()
        stulpas = QVBoxLayout(w)

        f1 = QHBoxLayout()
        self._p_nuo = QLineEdit()
        self._p_nuo.setPlaceholderText(t("nuo YYYY-MM-DD"))
        self._p_nuo.setMaximumWidth(130)
        f1.addWidget(self._p_nuo)
        self._p_iki = QLineEdit()
        self._p_iki.setPlaceholderText(t("iki YYYY-MM-DD"))
        self._p_iki.setMaximumWidth(130)
        f1.addWidget(self._p_iki)
        self._p_tipas = QComboBox()
        for reiksme, tekstas in (
                ("", t("Visi tipai")), ("foto", t("Foto")),
                ("skrinsotas", t("Skrinsotai")), ("video", t("Video")),
                ("ikona", t("Ikonos")), ("dokumentas", t("Dokumentai")),
                ("neatpazintas", t("Neatpazinti"))):
            self._p_tipas.addItem(tekstas, reiksme)
        f1.addWidget(self._p_tipas)
        self._p_lentyna = QComboBox()
        f1.addWidget(self._p_lentyna)
        f1.addStretch(1)
        stulpas.addLayout(f1)

        f2 = QHBoxLayout()
        self._p_etikete = QLineEdit()
        self._p_etikete.setPlaceholderText(t("Etikete (pvz. Jonines)"))
        f2.addWidget(self._p_etikete)
        self._p_kamera = QLineEdit()
        self._p_kamera.setPlaceholderText(t("Kamera (pvz. Canon)"))
        f2.addWidget(self._p_kamera)
        self._p_vardas = QLineEdit()
        self._p_vardas.setPlaceholderText(t("Failo vardas"))
        f2.addWidget(self._p_vardas)
        self._btn_ieskoti = QPushButton(t("Ieskoti"))
        self._btn_ieskoti.setObjectName("btn_scan")
        self._btn_ieskoti.clicked.connect(self._paieska_start)
        f2.addWidget(self._btn_ieskoti)
        stulpas.addLayout(f2)

        f3 = QHBoxLayout()
        self._p_vaizdai = QComboBox()
        self._p_vaizdai.setMinimumWidth(220)
        self._p_vaizdai.activated.connect(self._on_vaizdas_pasirinktas)
        f3.addWidget(self._p_vaizdai)
        self._btn_vaizda_saugoti = QPushButton(t("Issaugoti paieska..."))
        self._btn_vaizda_saugoti.setObjectName("btn_preview")
        self._btn_vaizda_saugoti.clicked.connect(self._issaugoti_vaizda)
        f3.addWidget(self._btn_vaizda_saugoti)
        self._btn_vaizda_trinti = QPushButton(t("Trinti vaizda"))
        self._btn_vaizda_trinti.clicked.connect(self._trinti_vaizda)
        f3.addWidget(self._btn_vaizda_trinti)
        f3.addStretch(1)
        self._p_info = QLabel("")
        self._p_info.setStyleSheet(stilius.STATUSAS)
        self._p_info.hide()   # tuscias melynas langelis nekabo (Roberto akis)
        f3.addWidget(self._p_info)
        stulpas.addLayout(f3)

        self._rezultatai = QListWidget()
        self._rezultatai.setViewMode(QListWidget.ViewMode.IconMode)
        self._rezultatai.setIconSize(
            QSize(miniaturos.DYDIS, miniaturos.DYDIS))
        self._rezultatai.setGridSize(
            QSize(miniaturos.DYDIS + 24, miniaturos.DYDIS + 56))
        self._rezultatai.setResizeMode(QListWidget.ResizeMode.Adjust)
        self._rezultatai.setMovement(QListWidget.Movement.Static)
        self._rezultatai.setUniformItemSizes(True)
        self._rezultatai.setWordWrap(False)
        # Skrolas EILUTEMIS, ne pikseliais - kad nesustotu per puse eiles
        # (Roberto gyvas demo 2026-08-29: "puse vienos matau puse kitos")
        self._rezultatai.setVerticalScrollMode(
            QListWidget.ScrollMode.ScrollPerItem)
        self._rezultatai.itemDoubleClicked.connect(
            self._on_rezultatas_dblclick)
        # Desinys klavisas (Roberto pasiulymas 2026-08-07; TempCleaner
        # "Kas tai?" meniu tradicija)
        self._rezultatai.setContextMenuPolicy(
            Qt.ContextMenuPolicy.CustomContextMenu)
        self._rezultatai.customContextMenuRequested.connect(
            self._rezultatu_meniu)
        stulpas.addWidget(self._rezultatai, stretch=1)

        pastaba = QLabel(t("Dvigubas klikas - parodyti faila Explorer'yje."
                           " Perziurai naudokite megstama perziurykle."))
        pastaba.setStyleSheet(stilius.LEGENDA)
        stulpas.addWidget(pastaba)

        # Pilka vietoklio plytele, kol worker'is pagamins miniatiura
        self._placeholder = QPixmap(miniaturos.DYDIS, miniaturos.DYDIS)
        self._placeholder.fill(QColor("#dfe3ec"))
        self._p_itemai = {}
        self._lentynu_combo_pildyti()
        self._vaizdu_combo_pildyti()
        return w

    # -------------------------------------------------------------- saltiniai
    def _auto_aptikimas(self):
        """Zinomu savartynu vietu siulymas (sprendimas 19) - tik esancios."""
        zinynas = Path(__file__).resolve().parent / "zinynas_vietos.json"
        try:
            vietos = json.loads(zinynas.read_text(encoding="utf-8"))
        except (OSError, ValueError):
            return
        for v in vietos:
            kelias = os.path.expandvars(v["kelias"])
            if "%" not in kelias and Path(kelias).is_dir():
                # Vardai/pastabos per t() - EN rezime irgi isversti
                pastaba = v.get("pastaba", "")
                self._prideti_saltini(t(v["vardas"]), kelias,
                                      pastaba=t(pastaba) if pastaba else "")

    def prideti_saltini(self, vardas, kelias, pazymetas=False):
        """Viesas API (ir testams): prideda saltini i medi."""
        it = self._prideti_saltini(vardas, kelias)
        if pazymetas:
            it.setCheckState(0, Qt.CheckState.Checked)
        return it

    def _prideti_saltini(self, vardas, kelias, pastaba=""):
        tekstas = vardas + ("  [%s]" % pastaba if pastaba else "")
        it = QTreeWidgetItem([tekstas + "  -  " + str(kelias), "", ""])
        it.setFlags(it.flags() | Qt.ItemFlag.ItemIsUserCheckable)
        it.setCheckState(0, Qt.CheckState.Unchecked)
        it.setData(0, _KELIO_ROLE, str(kelias))
        self._medis.addTopLevelItem(it)
        return it

    def _prideti_aplanka(self):
        kelias = QFileDialog.getExistingDirectory(
            self, t("Pasirinkite nuotrauku aplanka"))
        if kelias:
            # KLIURKA 20: Qt dialogas VISADA grazina "D:/foto", o sisteminiai
            # saltiniai ateina "C:\Users\..." - medyje kabojo abu stiliai
            # salia (Roberto laptopo ratas 2026-08-25)
            kelias = str(Path(kelias))
            # Disko saknis (E:/) aplanko vardo neturi - vardu tampa
            # etikete arba "Diskas E:" (Roberto kliurka Nr. 5, 2026-08-08:
            # medyje kabojo tuscias "- E:/")
            vardas = Path(kelias).name
            if not vardas:
                vardas = lentynos.siulomas_vardas(kelias)
            it = self._prideti_saltini(vardas, kelias)
            it.setCheckState(0, Qt.CheckState.Checked)

    def _pazymeti_irasai(self):
        rez = []
        saknis = self._medis.invisibleRootItem()
        for i in range(saknis.childCount()):
            it = saknis.child(i)
            if it.checkState(0) == Qt.CheckState.Checked:
                rez.append(it)
        return rez

    # -------------------------------------------------- varnelu SUMOS eilute
    def _on_item_changed(self, _it, _stulpelis):
        self._atnaujinti_suma()

    def _atnaujinti_suma(self):
        """Sprendimas 32: bendras pazymetu ivertis gyvai zymint."""
        irasai = self._pazymeti_irasai()
        if not irasai:
            self._suma.setText(t("Nepazymeta nieko"))
            return
        failai = 0
        baitai = 0
        med_failai = 0
        med_baitai = 0
        be_ivercio = 0
        for it in irasai:
            iv = it.data(0, _IVERCIO_ROLE)
            if iv is None:
                be_ivercio += 1
            else:
                failai += iv["failai"]
                baitai += iv["baitai"]
                # Seni ivertis be medijos lauku (pries 2026-08-13) -
                # konservatyviai imam visus failus
                med_failai += iv.get("medijos_failai", iv["failai"])
                med_baitai += iv.get("medijos_baitai", iv["baitai"])
        zodis = saltinio_zodis(len(irasai))
        if be_ivercio == len(irasai):
            # Ivercio nera ne vienam - nuliu nerodome (Roberto pastaba
            # 2026-08-07: "~0 files ~0.0 GB" pries zvalgyba klaidina)
            self._suma.setText(
                t("Pazymeta: {} {} - ivercio dar nera, spauskite"
                  " Zvalgyba").format(len(irasai), zodis))
            return
        # Kalibruota 2026-08-13 (saltas HDD benchmark + gyvas E: testas:
        # 58 665 medijos failai, prognoze 2235 s vs tikras 2234 s):
        # laika lemia TIK MEDIJOS baitai (sha256 skaito viska) + fiksuotas
        # kastas medijos failui (HDD seek); ne medija praleidziama
        # neskaitant, jos kaina ~0.
        sekundes = (med_failai * models.IVERTIS_MS_FAILUI / 1000.0
                    + med_baitai / (models.IVERTIS_MB_PER_S * 1048576.0))
        minutes = max(1, int(round(sekundes / 60.0)))
        tekstas = t("Pazymeta: {} {}, ~{} failu, ~{}, ~{} min").format(
            len(irasai), zodis, failai, models.dydis_tekstu(baitai), minutes)
        if be_ivercio:
            tekstas += " " + t("({} be zvalgybos ivercio)").format(be_ivercio)
        self._suma.setText(tekstas)

    # ------------------------------------------------- QThread receptas (OKF)
    def _paleisti_worker(self, naujas_worker):
        """pyqt6_threading_guard receptas: stop senam, sviezios instancijos
        ANT self, started->run, done/error->quit, finished->deleteLater."""
        if self._worker is not None:
            try:
                self._worker.stop()
            except RuntimeError:
                pass
        if self._thread is not None:
            try:
                if self._thread.isRunning():
                    self._thread.quit()
                    self._thread.wait(1000)
            except RuntimeError:
                pass
        self._worker = naujas_worker
        self._thread = QThread()
        naujas_worker.moveToThread(self._thread)
        self._thread.started.connect(naujas_worker.run)
        naujas_worker.done.connect(self._thread.quit)
        naujas_worker.error_signal.connect(self._thread.quit)
        self._thread.finished.connect(naujas_worker.deleteLater)
        self._thread.finished.connect(self._thread.deleteLater)
        self._thread.start()

    # ------------------------------------------------- kartotekos fonas (45)
    def _fonas_start(self):
        """A2 fonas: tyliai pildo kartoteka, kad atjungus diska miniatiuros
        liktu. Atskiras slot'as - pagrindinio worker'io neuzima; jei jau
        sukasi arba indekso dar nera - nieko nedaro."""
        if not self._db_kelias.exists():
            return
        if self._fono_thread is not None:
            try:
                if self._fono_thread.isRunning():
                    return
            except RuntimeError:
                pass
        w = workeriai.KartotekosFonas(self._db_kelias)
        w.progresas.connect(self._fonas_progresas)
        w.done.connect(self._fonas_done)
        w.error_signal.connect(self._fonas_klaida)
        self._fono_worker = w
        self._fono_thread = QThread()
        w.moveToThread(self._fono_thread)
        self._fono_thread.started.connect(w.run)
        w.done.connect(self._fono_thread.quit)
        w.error_signal.connect(self._fono_thread.quit)
        self._fono_thread.finished.connect(w.deleteLater)
        self._fono_thread.finished.connect(self._fono_thread.deleteLater)
        self._fono_thread.start(QThread.Priority.LowestPriority)

    def _fonas_progresas(self, tekstas):
        self._log(t("Kartoteka pildosi: {}").format(tekstas))

    def _fonas_done(self, n):
        if n:
            self._log(t("Kartoteka pasipilde: +{} miniatiuru.").format(n))

    def _fonas_klaida(self, klaida):
        # Fonas niekada netrukdo darbui - klaida tik i zurnala
        self._log(t("Kartotekos fonas sustojo: {}").format(klaida))

    def closeEvent(self, event):
        """Fonas ir worker'iai tvarkingai sustabdomi (guard receptas)."""
        for w, th in ((self._fono_worker, self._fono_thread),
                      (self._worker, self._thread)):
            if w is not None:
                try:
                    w.stop()
                except RuntimeError:
                    pass
            if th is not None:
                try:
                    if th.isRunning():
                        th.quit()
                        th.wait(2000)
                except RuntimeError:
                    pass
        super().closeEvent(event)

    # --------------------------------------------------------------- zvalgyba
    def _zvalgyba_start(self):
        irasai = self._pazymeti_irasai()
        if not irasai:
            self._log(t("Nepazymeta nieko"))
            return
        self._zv_taikiniai = {}
        self._zv_uzuominos = set()
        saltiniai = []
        for i, it in enumerate(irasai):
            self._zv_taikiniai[i] = it
            saltiniai.append((i, it.data(0, _KELIO_ROLE)))
        w = workeriai.ZvalgybosWorker(saltiniai)
        w.vienas.connect(self._on_zv_vienas)
        w.done.connect(self._on_zv_done)
        w.error_signal.connect(self._on_klaida)
        self._pradeti_darba(t("Vyksta zvalgyba"))
        self._paleisti_worker(w)

    def _on_zv_vienas(self, payload):
        sid, rez = payload
        it = self._zv_taikiniai.get(sid)
        if it is None:
            return
        it.setData(0, _IVERCIO_ROLE, rez)
        it.setText(1, "{:,}".format(rez["failai"]).replace(",", " "))
        it.setText(2, models.dydis_tekstu(rez["baitai"]))
        self._log(t("Zvalgyba: {} failu, {}, praleista {}").format(
            rez["failai"], models.dydis_tekstu(rez["baitai"]),
            rez["praleista_n"]))
        # UX slifas 2026-08-13 (Roberto pastaba - krikstynu momento
        # lukestis): apie nauja diska pasakome jau zvalgyboje, kad
        # dialogas pries indeksavima nebutu staigmena.
        kelias = it.data(0, _KELIO_ROLE)
        if kelias:
            serial, _e, _f = lentynos.volume_info(kelias)
            if (serial and serial not in self._zv_uzuominos
                    and self._zinomas_lentynos_vardas(serial) is None):
                self._zv_uzuominos.add(serial)
                self._log(t("Naujas diskas - lentynos vardo paklausiu"
                            " pries indeksavima."))

    def _on_zv_done(self, _viso):
        self._baigti_darba()
        self._atnaujinti_suma()

    def _telefono_gidas(self):
        """Gidas LIEKA mokytoju (Roberto 2026-08-28: zmogus turi zinoti,
        ka telefone atlikti), bet gauna mygtuka 'Jungti telefona' -
        v1.0 VINIS (PLANAS 4b2): programa pati aptinka, zvalgo ir
        kopijuoja per Shell COM (telefonas.py). Roberto gyvas testas
        2026-08-08: vartotojas sedi prisijunges per Bluetooth/Phone Link
        ir galvoja 'tai kam man laidas?' - todel atskira pastraipa,
        kodel BT/PL neuztenka."""
        dlg = QMessageBox(self)
        dlg.setIcon(QMessageBox.Icon.Information)
        dlg.setWindowTitle(t("Kaip paimti is telefono?"))
        dlg.setText(
            t("Kaip paimti nuotraukas is telefono:\n\n"
              "1. Atsidarykite telefona Explorer'yje:\n"
              "   - jei telefonas jau matomas Explorer sarase\n"
              "     (Windows 11 + \"Link to Windows\" rodo ji ir be\n"
              "     laido) - galite bandyti is cia; DEMESIO: sis\n"
              "     belaidis langas dazniausiai rodo NE VISKA;\n"
              "   - patikimiausia: prijunkite USB laidu. Telefonas\n"
              "     PATS PAKLAUS \"USB rezimas?\" (langelis ekrane arba\n"
              "     pranesimu juostoje, JUSU TELEFONO kalba) -\n"
              "     pasirinkite \"Failu perdavimas\" (File Transfer).\n"
              "     NE \"Nuotrauku perdavimas\" - tas rodo tik DCIM,\n"
              "     be WhatsApp. Numatytasis buna \"tik krovimas\" -\n"
              "     todel neatsakius telefonas kompiuteryje atrodo\n"
              "     TUSCIAS. Matysite viska, dideli kiekiai eis greitai.\n"
              "2. Telefone: Internal storage. Nuotraukos:\n"
              "   DCIM\\Camera; skrinsotai: Pictures\\Screenshots\n"
              "   arba DCIM\\Screenshots (Xiaomi); WhatsApp:\n"
              "   Android\\media\\com.whatsapp\\WhatsApp\\Media.\n"
              "3. Nukopijuokite aplankus i kompiuteri ar isorini\n"
              "   diska (originalai telefone lieka).\n"
              "4. Cia spauskite \"Prideti aplanka...\" ir indeksuokite.\n\n"
              "Kodel reikia kopijos? Telefonas Explorer'yje - ne\n"
              "diskas, o \"langas\" i ji (be raides): programos jo\n"
              "tiesiogiai skenuoti negali. Dar vienas kelias -\n"
              "debesis: jei naudojate Google Photos / OneDrive, jie\n"
              "nuotraukas jau atsiuncia i kompiuterio aplanka - ta\n"
              "aplanka cia ir pridekite."))
        dlg.setInformativeText(
            t("ARBA leiskite programai padaryti tai PACIAI: atlikite"
              " 1 zingsni (laidas + \"Failu perdavimas\"), UZDARYKITE"
              " Explorer langa su telefonu (telefona vienu metu mato tik"
              " viena programa) ir spauskite \"Jungti telefona\" -"
              " programa pati suras nuotrauku vietas, nukopijuos ir"
              " prides i saltinius. Is telefono TIK skaitoma - nieko"
              " netrinam ir nerasom."))
        jungti = dlg.addButton(t("Jungti telefona"),
                               QMessageBox.ButtonRole.AcceptRole)
        dlg.addButton(t("Uzdaryti"), QMessageBox.ButtonRole.RejectRole)
        dlg.exec()
        if dlg.clickedButton() is jungti:
            self._telefonas_start()

    # ------------------------------------------ telefonas (v1.0 VINIS)
    def _telefonas_start(self):
        w = workeriai.TelefonoZvalgybosWorker()
        w.done.connect(self._on_telefono_zvalgyba)
        w.error_signal.connect(self._on_telefono_klaida_tekstas)
        self._pradeti_darba(t("Ieskomas telefonas"))
        self._paleisti_worker(w)

    def _on_telefono_klaida_tekstas(self, tekstas):
        self._baigti_darba()
        self._log(t("Telefono klaida: {}").format(tekstas))
        self._telefono_klaida()

    def _on_telefono_zvalgyba(self, payload):
        telefonai, z = payload
        self._baigti_darba()
        vietos = [v for v in (z or {}).get("vietos", []) if v["kiek"] > 0]
        if not telefonai or z is None or z.get("klaida") or not vietos:
            self._telefono_klaida()
            return
        vardas = telefonai[0]["vardas"]
        self._log(t("Rastas telefonas: {} ({} nuotrauku vietu)").format(
            vardas, len(vietos)))
        dlg = TelefonoDialogas(vardas, vietos, self)
        if dlg.exec() != QDialog.DialogCode.Accepted:
            self._log(t("Telefono kopija atsaukta."))
            return
        keliai = dlg.pasirinkti()
        tikslas = dlg.tikslas()
        if not keliai or not tikslas:
            self._log(t("Telefono kopija atsaukta."))
            return
        Path(tikslas).mkdir(parents=True, exist_ok=True)
        self._telefono_tikslas = str(tikslas)
        self._telefono_vardas = vardas
        w = workeriai.TelefonoKopijosWorker(vardas, keliai, tikslas)
        w.zurnalas.connect(self._log)
        w.progresas.connect(self._on_ind_progresas)
        w.done.connect(self._on_telefono_kopija_done)
        w.error_signal.connect(self._on_telefono_klaida_tekstas)
        self._pradeti_darba(t("Kopijuojama is telefono"))
        self._paleisti_worker(w)

    def _on_telefono_kopija_done(self, rezultatas):
        viso, praleista = rezultatas
        self._baigti_darba()
        self._log(t("Telefonas baigtas: tiksle {} failu"
                    " ({} praleista kaip jau turimi).").format(
            viso, praleista))
        # KLIURKA 26 (Roberto gyvas ratas 2026-08-28): pakartotine kopija
        # i ta pati aplanka pridedavo ANTRA vienoda saltinio eilute -
        # pirma patikrinam, ar kelias jau medyje.
        esamas = None
        for i in range(self._medis.topLevelItemCount()):
            it = self._medis.topLevelItem(i)
            if it.data(0, _KELIO_ROLE) == self._telefono_tikslas:
                esamas = it
                break
        if esamas is None:
            esamas = self._prideti_saltini(
                self._telefono_vardas, self._telefono_tikslas,
                pastaba=t("is telefono"))
        esamas.setCheckState(0, Qt.CheckState.Checked)
        self._log(t("Aplankas pridetas prie saltiniu - spauskite"
                    " \"Indeksuoti pazymetus\"."))

    def _telefono_klaida(self):
        """Roberto 2026-08-28: nepavykus - langas su paaiskinimu ir
        keliu pas claude.ai konsultacija (spr. 40 mechanizmas)."""
        dlg = QMessageBox(self)
        dlg.setIcon(QMessageBox.Icon.Warning)
        dlg.setWindowTitle(t("Telefono nerandu"))
        dlg.setText(t(
            "Nepavyko pamatyti telefono nuotrauku. Dazniausios"
            " priezastys:\n\n"
            "1. Telefonas neatsake i \"USB rezimas?\" klausima -\n"
            "   pasirinkite \"Failu perdavimas\" (File Transfer)\n"
            "   TELEFONO ekrane. Numatytasis buna \"tik krovimas\".\n"
            "2. Telefona naudoja kita programa - uzdarykite Explorer\n"
            "   langa su telefonu ir bandykite dar karta (telefona\n"
            "   vienu metu mato tik viena programa).\n"
            "3. Ekranas uzrakintas - atrakinkite ir perkiskite laida.\n"
            "4. Laidas tik krovimo - pabandykite kita laida.\n"
            "5. Senas telefonas gali apsimesti CD-ROM ir siulyti\n"
            "   diegti savo programa - nediekite, tiesiog perkiskite\n"
            "   laida i kita lizda."))
        klausk = dlg.addButton(t("Klausti DI"),
                               QMessageBox.ButtonRole.HelpRole)
        dlg.addButton(t("Uzdaryti"), QMessageBox.ButtonRole.RejectRole)
        dlg.exec()
        if dlg.clickedButton() is klausk:
            self._on_klausk_di(klausimas=(
                "I connected my Android phone with a USB cable and chose"
                " File Transfer mode, but the app still cannot see the"
                " phone or its photos. What should I check step by step?"))

    # ------------------------------------------------------------ indeksavimas
    def _zinomas_lentynos_vardas(self, serial):
        """Jau registruotos lentynos vardas is indekso arba None."""
        if not self._db_kelias.exists():
            return None
        try:
            con = indeksas.atidaryti_ro(self._db_kelias)
            eil = con.execute(
                "SELECT vardas_zmogui FROM lentynos"
                " WHERE volume_serial=?", (serial,)).fetchone()
            con.close()
            return eil[0] if eil else None
        except Exception:
            return None

    def _lentynos_paruosimas(self, kelias):
        """Lentynos tapatybe pries indeksavima (sprendimas 30; Roberto
        pataisa 2026-08-08 'keistuoliu juk buna'): zinoma lentyna
        atpazistama pagal serial ir jos vardas NELIECIAMAS; naujam
        diskui - krikstynu dialogas SU pasiulymu abiem tipams.

        KLIURKA 25 (Roberto gyvas ratas 2026-08-28): Cancel semantika
        dabar VIENODA visiems diskams - praleisti saltini si karta.
        Senoji spr. 38 dalis "vidiniam Cancel = lieka pasiulymas"
        ATSAUKTA: pats Robertas paspaude Cancel tikedamasis atsaukti,
        o indeksavimas prasidejo - mygtukas melavo lukesciui."""
        serial, etikete, fs = lentynos.volume_info(kelias)
        if serial is None:
            serial = "KELIAS:" + str(Path(kelias).anchor or kelias)
        vidinis = lentynos.disko_tipas(kelias) == "fixed"
        vardas = self._zinomas_lentynos_vardas(serial)
        if vardas is None:
            siulymas = (lentynos.autovardas_vidinis(kelias) if vidinis
                        else lentynos.siulomas_vardas(kelias))
            if self._testinis:
                vardas = siulymas
            elif vidinis:
                tekstas, ok = klausti_vardo(
                    self, t("Lentynos krikstynos"),
                    t("Sis kompiuterio diskas gaus lentynos varda.\n"
                      "Galite palikti siuloma arba irasyti sava "
                      "(iki 40 zenklu)."),
                    siulymas)
                if not ok:
                    return None   # kliurka 25: Cancel = praleisti saltini
                vardas = tekstas.strip()[:40] or siulymas
            else:
                tekstas, ok = klausti_vardo(
                    self, t("Lentynos krikstynos"),
                    t("Naujas diskas! Duokite lentynai varda, kuri "
                      "atpazinsite po metu (iki 40 zenklu).\nPatarimas: "
                      "uzklijuokite ant disko lipduka su siuo vardu."),
                    siulymas)
                if not ok:
                    return None   # Cancel = sio saltinio neindeksuoti
                vardas = tekstas.strip()[:40] or siulymas
        return {"kelias": str(kelias), "serial": serial, "vardas": vardas,
                "etikete": etikete, "fs": fs,
                "talpa": lentynos.talpa_baitais(kelias)}

    def _indeksuoti_start(self):
        irasai = self._pazymeti_irasai()
        if not irasai:
            self._log(t("Nepazymeta nieko"))
            return
        saltiniai = []
        for it in irasai:
            s = self._lentynos_paruosimas(it.data(0, _KELIO_ROLE))
            if s is None:
                self._log(t("Saltinis praleistas - krikstynos atsauktos."))
                continue
            saltiniai.append(s)
        if not saltiniai:
            return
        w = workeriai.IndeksavimoWorker(self._db_kelias, saltiniai)
        w.zurnalas.connect(self._log)
        w.progresas.connect(self._on_ind_progresas)
        w.done.connect(self._on_ind_done)
        w.error_signal.connect(self._on_klaida)
        self._pradeti_darba(t("Vyksta indeksavimas"))
        self._paleisti_worker(w)

    def _on_ind_progresas(self, tekstas):
        self._busena.setText("%s  %s  (%s)" % (self._darbo_tekstas,
                                               self._mmss(), tekstas))

    def _on_ind_done(self, payload):
        suvestine, kopijos, rentgeno_md = payload
        self._baigti_darba()
        viso = 0
        for vardas, stat in suvestine:
            viso += stat["indeksuota"]
            self._log(t("Indeksuota {} - {} failu ({} nepakite, {} neatpazinta,"
                        " {} ne medija, {} praleista)").format(
                vardas, stat["indeksuota"], stat["nepakite"],
                stat["neatpazinta"], stat.get("ne_medija", 0),
                stat["praleista_n"]))
            # 4e p. 7/8: bedaciu gelbejimas matomas zurnale
            if stat.get("kaimynyste") or stat.get("partijos"):
                self._log(t("[{}] be datos likusiems: kaimynyste +{},"
                            " mtime partijos +{} - failai gavo kaimynu"
                            " medianos data.").format(
                    vardas, stat.get("kaimynyste", 0),
                    stat.get("partijos", 0)))
        self._log(t("Baigta. Is viso suindeksuota {} failu.").format(viso))
        self._lentynu_combo_pildyti()   # naujos lentynos matomos paieskoje
        self._atnaujinti_indekso_busena()
        # Spr. 45: nauji irasai -> kartotekos fonas pasipildo pats
        QTimer.singleShot(2000, self._fonas_start)
        # 4f p. 3 (2026-08-29): ARCHYVO RENTGENAS - A pakopos veidas.
        # Rodomas PIRMAS (jis atsakymas "kas mano archyve"), kopiju
        # langas po jo. Testinese sesijose tekstas pasiekiamas per
        # self._rentgeno_md (patikroms - be modalinio lango).
        self._rentgeno_md = rentgeno_md
        if rentgeno_md and not self._testinis:
            self.paruosti_rentgeno_langa(rentgeno_md).exec()
        # 4e p. 2 (2026-08-28): kopiju langas jau A pakopos pabaigoje -
        # patogiausias momentas nueiti i SDF yra PRIES kraustymasi.
        # Pries-vykdymo vartai (spr. 44) LIEKA - cia tik ankstyvas
        # informavimas; nuo lango nuovargio saugo salyga "tik kai
        # kopiju skaicius pasikeite nuo paskutinio parodymo sioje
        # sesijoje".
        if kopijos:
            self._log(t("Kopiju suvestine: ~{} failai galimai kartojasi"
                        " (~{}). Patarimas: pirma Smart Duplicate Finder,"
                        " tada archyvo kurimas.").format(
                kopijos[0], models.dydis_tekstu(kopijos[1])))
            if (not self._testinis
                    and kopijos[0] != getattr(self, "_kopiju_pranesta",
                                              None)):
                self._kopiju_pranesta = kopijos[0]
                langas, _ = self.paruosti_kopiju_langa(
                    *kopijos, po_indeksavimo=True)
                langas.exec()

    # ------------------------------------------- B pakopa: namu archyvas (E4)
    def _archyvas_start(self, _=False, tikslo_kelias=None):
        """Kraustymasis: tikslo lentyna -> pasiulymai -> perziura ->
        vykdymas. tikslo_kelias parametras - testams (be dialogu)."""
        if tikslo_kelias is None:
            # KLIURKA 21 (Roberto laptopo ratas 2026-08-25): antrastė sakė
            # "pasirinkite NAUJA aplanka", zmogus iraso varda i "Folder:"
            # lauka - ir Windows atsako "Path does not exist". Dialogas
            # NAUJO aplanko irasant varda nesukuria, reikia jo "New folder"
            # mygtuko. Antraste dabar nukreipia i mygtuka, ne i lauka.
            tikslo_kelias = QFileDialog.getExistingDirectory(
                self, t("Archyvo aplankas: pasirinkite tuscia arba sukurkite"
                        " nauja dialogo mygtuku"))
            if not tikslo_kelias:
                return
        tikslas = Path(tikslo_kelias)
        if any(tikslas.iterdir()) and not self._testinis:
            if not klausti(
                    self, t("Aplankas netuscias"),
                    t("Namas statomas tusciame sklype - aplanke jau yra failu."
                      "\nTesti vis tiek? (Esami failai NEBUS liesti;"
                      " sutampantis turinys bus praleistas.)")):
                return
        self._archyvo_tikslas = str(tikslas)
        w = workeriai.PlanavimoWorker(self._db_kelias)
        w.done.connect(self._on_planas_done)
        w.error_signal.connect(self._on_klaida)
        self._pradeti_darba(t("Ruosiami pasiulymai"))
        self._paleisti_worker(w)

    def _klausti_del_kopiju(self, kiek, baitai):
        """Parodo kopiju langa. True = testi, False = sustoti."""
        langas, testi = self.paruosti_kopiju_langa(kiek, baitai)
        langas.exec()
        return langas.clickedButton() is testi

    def paruosti_kopiju_langa(self, kiek, baitai, po_indeksavimo=False):
        """Kopiju langas: pasakom VISKA ir duodam iseiti (spr. 27b tesinys).

        Grazina (langas, testi_mygtukas). Tekstas sako tris dalykus: ka
        laikom kopija, ko NEMATOM (panasiu - tam yra SDF) ir kad kopijos
        pasirinkimas gali nesutapti su zmogaus pasirinkimu. Atskirta nuo
        exec() - patikra tikrina teksta nepaleisdama modalinio lango.

        po_indeksavimo=True (4e p. 2, 2026-08-28): informacinis variantas
        A pakopos pabaigai - vietoj "Testi/Sustoti" vienas "Supratau"
        (nieko nevykdom, tik pasakom ANKSTI, kol patogiausia nueiti i
        SDF); testi_mygtukas tada None.
        """
        dydis = models.dydis_tekstu(baitai)  # kliurka 18 - viena vieta visiems
        langas = QMessageBox(self)
        langas.setIcon(QMessageBox.Icon.Question)
        langas.setWindowTitle(t("Yra kopiju"))
        langas.setText(
            t("Panasu, kad ~%d failai kartojasi (vienodo dydzio, ~%s).")
            % (kiek, dydis))
        langas.setInformativeText(
            t("Skaicius - ivertis pagal vienoda failo dydi; pries"
              " keldamas i archyva turini patikrinsiu baitas i baita,"
              " tad tikras kopiju skaicius gali buti kiek mazesnis.")
            + "\n\n"
            + t("Kopijomis laikau tik IDENTISKUS baitas i baita failus."
              " Panasiu nematau: jei nuotrauka apkarpyta, patamsinta ar"
              " sumazinta (pvz. persiusta per zinute), man tai atskiras"
              " failas - ir i archyva keliaus visos jos versijos. Tokias"
              " randa Smart Duplicate Finder, nes jis lygina vaizda, ne"
              " baitus.")
            + "\n\n"
            + (t("Patogiausias momentas kopijoms susitvarkyti - DABAR,"
                 " pries kuriant namu archyva: susitvarkykite su Smart"
                 " Duplicate Finder (github.com/RobertasTa/"
                 "smart-duplicate-finder) ir suindeksuokite is naujo,"
                 " arba tiesiog teskite - pries kuriant archyva ispesiu"
                 " dar karta.")
               if po_indeksavimo else
               t("Jei tesi: keliausiu po viena kiekvieno turinio kopija."
                 " Kuria butent - pasirinksiu pagal patikimesne data, ir"
                 " ji gali tureti kita varda ar kita aplanka nei ta,"
                 " kuria butum pasirinkes tu.")
               + "\n\n"
               + t("Jei nori pasirinkti pats: sustok, susitvarkyk kopijas su"
                   " Smart Duplicate Finder (github.com/RobertasTa/"
                   "smart-duplicate-finder) ir paleisk PHOTO home is"
                   " naujo.")))
        if po_indeksavimo:
            langas.addButton(t("Supratau"), QMessageBox.ButtonRole.AcceptRole)
            return langas, None
        testi = langas.addButton(t("Testi"),
                                 QMessageBox.ButtonRole.AcceptRole)
        langas.addButton(t("Sustoti"), QMessageBox.ButtonRole.RejectRole)
        return langas, testi

    def paruosti_rentgeno_langa(self, tekstas):
        """ARCHYVO RENTGENAS (4f p. 3, 2026-08-29): A pakopos veidas -
        nulines rizikos ataskaita po indeksavimo (nieko nekilnota, tik
        perskaityta). Atskirta nuo exec() - patikra tikrina turini
        nepaleisdama modalinio lango."""
        dlg = QDialog(self)
        dlg.setWindowTitle(t("Archyvo rentgenas"))
        dlg.resize(680, 560)
        stulpas = QVBoxLayout(dlg)
        lauk = QPlainTextEdit(dlg)
        lauk.setObjectName("rentgeno_tekstas")
        lauk.setReadOnly(True)
        # Lygiuotems lentelems (sluoksniai, metai) - lygiaplotis sriftas
        lauk.setFont(QFont("Consolas"))
        lauk.setPlainText(tekstas)
        stulpas.addWidget(lauk)
        eilute = QHBoxLayout()
        saugoti = QPushButton(t("Issaugoti ataskaita..."))
        saugoti.setObjectName("btn_rentgeno_saugoti")
        saugoti.clicked.connect(
            lambda _=False, tks=tekstas: self._rentgena_saugoti(tks))
        gerai = QPushButton(t("Gerai"))
        gerai.setDefault(True)
        gerai.clicked.connect(dlg.accept)
        eilute.addWidget(saugoti)
        eilute.addStretch(1)
        eilute.addWidget(gerai)
        stulpas.addLayout(eilute)
        return dlg

    def _rentgena_saugoti(self, tekstas):
        """Rentgeno .md issaugojimas ten, kur zmogus pasirinks
        (dalinamasis - r/DataHoarder gyvena stat skrinais)."""
        # KLIURKA 27 (Roberto gyvas ratas 2026-08-29): vien failo vardas
        # be katalogo dialoga atidarydavo darbo kataloge (exe atveju -
        # programos viduriuose). Numatytoji vieta - Documents.
        dok = QStandardPaths.writableLocation(
            QStandardPaths.StandardLocation.DocumentsLocation) \
            or str(Path.home())
        kelias, _ = QFileDialog.getSaveFileName(
            self, t("Issaugoti ataskaita..."),
            str(Path(dok) / "KAS_TAVO_ARCHYVE.md"),
            "Markdown (*.md)")
        if not kelias:
            return
        try:
            Path(kelias).write_text(tekstas, encoding="utf-8")
            self._log(t("Rentgeno ataskaita issaugota: {}").format(kelias))
        except OSError as e:
            self._log(t("Nepavyko issaugoti ataskaitos: {}").format(e))

    def _on_planas_done(self, payload):
        grupes, kopijos = payload
        self._baigti_darba()
        if not grupes:
            self._log(t("Nera ka tvarkyti - pirma suindeksuokite saltinius."))
            return
        # KOPIJU langas (Roberto sprendimas 2026-08-23): anksciau apie
        # kopijas buvo TIK eilute zurnale - "ispet ispejo, o galimybes
        # nueiti susitvarkyti nedave". Dabar zmogus mato, ka programa
        # darys, ir gali sustoti. Programa uz ji NESIRENKA.
        if kopijos and not self._testinis:
            if not self._klausti_del_kopiju(*kopijos):
                self._log(t("Sustabdyta - kopijas galite susitvarkyti su"
                            " Smart Duplicate Finder."))
                return
        if self._testinis:
            pasirinktos = [g["grupe"] for g in grupes]
            rezimas = "kopijuoti"
        else:
            dlg = PasiulymuDialogas(grupes, self)
            if dlg.exec() != QDialog.DialogCode.Accepted:
                self._log(t("Tvarkymas atsauktas pasiulymu lange."))
                return
            pasirinktos = dlg.pasirinktos()
            rezimas = dlg.rezimas()
            if not pasirinktos:
                self._log(t("Nepasirinkta ne viena grupe."))
                return
            failu = sum(g["failai"] for g in grupes
                        if g["grupe"] in pasirinktos)
            baitai = sum(g["baitai"] for g in grupes
                         if g["grupe"] in pasirinktos)
            if not klausti(
                    self, t("Perziura (niekas dar nevykdoma)"),
                    t("Bus {} ({} failu, {}) i:\n{}\n\nVykdyti?").format(
                        t("PERKELIAMA") if rezimas == "perkelti"
                        else t("KOPIJUOJAMA"),
                        failu, models.dydis_tekstu(baitai),
                        self._archyvo_tikslas)):
                self._log(t("Tvarkymas atsauktas perziuroje."))
                return
        w = workeriai.VykdymoWorker(self._db_kelias, self._archyvo_tikslas,
                                    pasirinktos, rezimas)
        w.progresas.connect(self._on_vykdymo_progresas)
        w.done.connect(self._on_vykdymo_done)
        w.error_signal.connect(self._on_klaida)
        self._pradeti_darba(t("Vyksta tvarkymas"))
        self._paleisti_worker(w)

    def _on_vykdymo_progresas(self, stat):
        self._busena.setText("%s  %s  (%d)" % (
            self._darbo_tekstas, self._mmss(), stat.get("sutvarkyta", 0)))

    def _on_vykdymo_done(self, stat):
        self._baigti_darba()
        self._log(t("Tvarkymas baigtas: {} sutvarkyta, {} dubliu praleista,"
                    " {} jau buvo, {} klaidu.").format(
            stat["sutvarkyta"], stat["praleista_dubliai"],
            stat["praleista_jau_yra"], stat["klaidos"]))

    def _undo_start(self):
        if not self._testinis:
            if not klausti(
                    self, t("UNDO"),
                    t("Grazinti VISKA atgal pagal UNDO zurnala?\nKopijos bus"
                      " istrintos is archyvo, perkelti failai gris i vietas.")):
                return
        w = workeriai.AtstatymoWorker(self._db_kelias)
        w.done.connect(self._on_undo_done)
        w.error_signal.connect(self._on_klaida)
        self._pradeti_darba(t("Vyksta atstatymas"))
        self._paleisti_worker(w)

    def _on_undo_done(self, stat):
        self._baigti_darba()
        self._log(t("UNDO baigtas: {} atstatyta, {} klaidu.").format(
            stat["atstatyta"], stat["klaidos"]))

    # ---------------------------------------------------- E5: paieska (29)
    def _pasisveikinimas(self):
        """Seansu buhalterijos pasisveikinimas (sprendimas 7 uzuomazga).
        Pirmam paleidimui (tuscias indeksas) - Quick start takas
        (4f p. 4): trys zingsniai + "ne baito" pazadas pirmame ekrane."""
        failu = lentynu = 0
        if self._db_kelias.exists():
            try:
                con = indeksas.atidaryti_ro(self._db_kelias)
                failu = con.execute(
                    "SELECT COUNT(*) FROM failai").fetchone()[0]
                lentynu = con.execute(
                    "SELECT COUNT(*) FROM lentynos").fetchone()[0]
                con.close()
            except Exception:
                return
        if failu:
            self._log(t("Sveiki sugrize! Indekse - {} {} ({} {}),"
                        " paieska veikia is karto.").format(
                failu, kiekio_zodis(failu, "failas"),
                lentynu, kiekio_zodis(lentynu, "lentyna")))
        else:
            self._log(t("Pirmas kartas? Takas paprastas:"))
            self._log(t("  1. Prijunkite telefona arba pazymekite aplanka"
                        " ir spauskite Indeksuoti - siame zingsnyje"
                        " programa failus tik SKAITO."))
            self._log(t("  2. Gausite ARCHYVO RENTGENA: kas jusu"
                        " archyve, is kur datos, kiek liko be ju."))
            self._log(t("  3. Jei panorekite - namu archyvas Metai\\"
                        "Menuo tvarka, o kiekvienas zingsnis su UNDO."))
            self._log(t("PAZADAS: ne vienas baitas jusu failuose"
                        " nekeiciamas; tvarkymas - tik kopijos arba"
                        " perkelimas su pilnu UNDO."))

    def _atnaujinti_indekso_busena(self):
        """Desinysis apacios kampas: kiek turto indekse (visada matosi)."""
        failu = lentynu = 0
        if self._db_kelias.exists():
            try:
                con = indeksas.atidaryti_ro(self._db_kelias)
                failu = con.execute(
                    "SELECT COUNT(*) FROM failai").fetchone()[0]
                lentynu = con.execute(
                    "SELECT COUNT(*) FROM lentynos").fetchone()[0]
                con.close()
            except Exception as e:
                # Tyli klaida cia reiske melaginga "Indeksas tuscias"
                # (E8 smoke radinys 2026-08-13) - klaida rodoma zurnale.
                self._log("Indekso skaitymo klaida: %r" % (e,))
        if failu:
            self._indekso_busena.setText(t("Indekse: {} {}, {} {}").format(
                failu, kiekio_zodis(failu, "failas"),
                lentynu, kiekio_zodis(lentynu, "lentyna")))
        else:
            self._indekso_busena.setText(t("Indeksas tuscias"))

    def _lentynu_langas(self):
        """Statuso mygtukas -> lentynu sarasas su gyva prijungimo busena
        (prijungta tikrinama PAGAL SERIAL cia ir dabar, ne is DB lauko -
        DB 'prijungta' rasomas tik registruojant, tad butu pasenes)."""
        eilutes = []
        if self._db_kelias.exists():
            try:
                con = indeksas.atidaryti_ro(self._db_kelias)
                duom = con.execute(
                    "SELECT l.vardas_zmogui, l.volume_serial,"
                    " l.paskutini_karta_matyta, COUNT(f.id)"
                    " FROM lentynos l"
                    " LEFT JOIN failai f ON f.lentyna_id = l.id"
                    " GROUP BY l.id ORDER BY l.vardas_zmogui").fetchall()
                con.close()
            except Exception as e:
                self._log(t("Klaida: {}").format(e))
                return
            esami = self._prijungti_serialai()
            eilutes = [(v, s in esami, m, f) for v, s, m, f in duom]
        dlg = LentynuDialogas(eilutes, self)
        dlg.exec()

    @staticmethod
    def _prijungti_serialai():
        """GYVAS dabar prijungtu tomu serialu rinkinys (DB 'prijungta'
        laukas rasomas tik registruojant - pasenes; kliurka 8, Roberto
        gyvas testas 2026-08-13: istraukus diska dbl-click rode
        'Failas nerastas' vietoj 'Lentyna neprijungta')."""
        esami = set()
        for raide in "ABCDEFGHIJKLMNOPQRSTUVWXYZ":
            root = raide + ":\\"
            if os.path.exists(root):
                s = lentynos.volume_info(root)[0]
                if s:
                    esami.add(s)
        return esami

    def _lentynu_combo_pildyti(self):
        self._p_lentyna.blockSignals(True)
        self._p_lentyna.clear()
        self._p_lentyna.addItem(t("Visos lentynos"), None)
        if self._db_kelias.exists():
            try:
                con = indeksas.atidaryti_ro(self._db_kelias)
                for lid, vardas in con.execute(
                        "SELECT id, vardas_zmogui FROM lentynos"
                        " ORDER BY vardas_zmogui"):
                    self._p_lentyna.addItem(vardas, lid)
                con.close()
            except Exception:
                pass
        self._p_lentyna.blockSignals(False)

    def _vaizdu_combo_pildyti(self):
        self._p_vaizdai.blockSignals(True)
        self._p_vaizdai.clear()
        self._p_vaizdai.addItem(t("- Issaugotos paieskos -"), None)
        if self._db_kelias.exists():
            try:
                con = indeksas.atidaryti_ro(self._db_kelias)
                for vid, vardas in paieska.vaizdu_sarasas(con):
                    self._p_vaizdai.addItem(vardas, vid)
                con.close()
            except Exception:
                pass
        self._p_vaizdai.blockSignals(False)

    def _p_filtrai(self):
        """Filtru dict is lauku; neteisinga data -> None (su zurnalu)."""
        filtrai = {}
        for raktas, laukas in (("data_nuo", self._p_nuo),
                               ("data_iki", self._p_iki),
                               ("etikete", self._p_etikete),
                               ("kamera", self._p_kamera),
                               ("vardas", self._p_vardas)):
            v = laukas.text().strip()
            if v:
                filtrai[raktas] = v
        for raktas in ("data_nuo", "data_iki"):
            if raktas in filtrai:
                try:
                    date.fromisoformat(filtrai[raktas])
                except ValueError:
                    self._log(t("Neteisinga data '{}' - reikia"
                                " YYYY-MM-DD").format(filtrai[raktas]))
                    return None
        tipas = self._p_tipas.currentData()
        if tipas:
            filtrai["tipas"] = tipas
        lid = self._p_lentyna.currentData()
        if lid is not None:
            filtrai["lentyna_id"] = lid
        return filtrai

    def _nustatyti_filtrus(self, filtrai):
        self._p_nuo.setText(filtrai.get("data_nuo", ""))
        self._p_iki.setText(filtrai.get("data_iki", ""))
        self._p_etikete.setText(filtrai.get("etikete", ""))
        self._p_kamera.setText(filtrai.get("kamera", ""))
        self._p_vardas.setText(filtrai.get("vardas", ""))
        idx = self._p_tipas.findData(filtrai.get("tipas", ""))
        self._p_tipas.setCurrentIndex(idx if idx >= 0 else 0)
        idx = self._p_lentyna.findData(filtrai.get("lentyna_id"))
        self._p_lentyna.setCurrentIndex(idx if idx >= 0 else 0)

    def _paieska_start(self, _=False, filtrai=None):
        """filtrai parametras - testams ir issaugotoms paieskoms."""
        if not self._db_kelias.exists():
            self._log(t("Indekso dar nera - pirma suindeksuokite"
                        " saltinius."))
            return
        if filtrai is None:
            filtrai = self._p_filtrai()
            if filtrai is None:
                return
        w = workeriai.PaieskosWorker(self._db_kelias, filtrai)
        w.done.connect(self._on_paieska_done)
        w.error_signal.connect(self._on_klaida)
        self._pradeti_darba(t("Vyksta paieska"))
        self._paleisti_worker(w)

    def _on_paieska_done(self, payload):
        eiles, kiek = payload
        self._baigti_darba()
        # Pildymo greitaveika (OKF performance guard, pritaikyta sarasui)
        self._rezultatai.setUpdatesEnabled(False)
        self._rezultatai.clear()
        self._p_itemai = {}
        uzduotys = []
        vietoklis = QIcon(self._placeholder)
        for r in eiles:
            data_txt = (r["datetaken"] or "")[:10]
            it = QListWidgetItem(vietoklis,
                                 "%s\n%s" % (r["vardas"], data_txt))
            it.setData(_KELIO_ROLE, r)
            it.setToolTip("%s\n%s: %s\n%s" % (
                r["santykinis_kelias"], t("Lentyna"),
                r["lentynos_vardas"], r["datetaken"] or ""))
            self._rezultatai.addItem(it)
            self._p_itemai[r["id"]] = it
            # Spr. 45: uzduotis VISIEMS (ir atjungtu lentynu) - worker'is
            # pirma ziuri i kartotekos sandeli, tik miss'a gamina is disko
            kelias = (str(Path(r["saltinio_saknis"])
                          / r["santykinis_kelias"])
                      if r.get("saltinio_saknis") else None)
            uzduotys.append((r["id"], kelias, r["mtime"]))
        self._rezultatai.setUpdatesEnabled(True)
        self._p_info.setText(t("Rasta: {} (rodoma {})").format(
            kiek, len(eiles)))
        self._p_info.show()
        self._log(t("Paieska: rasta {} irasu.").format(kiek))
        if uzduotys:
            w = workeriai.MiniatiuruWorker(uzduotys)
            w.vienas.connect(self._on_min_vienas)
            w.progresas.connect(self._on_ind_progresas)
            w.done.connect(self._on_min_done)
            w.error_signal.connect(self._on_klaida)
            self._pradeti_darba(t("Ruosiamos miniatiuros"))
            self._paleisti_worker(w)

    def _on_min_vienas(self, payload):
        # Spr. 45: payload = (fileid, jpeg_bytes) - is kartotekos sandelio
        fileid, jpeg = payload
        it = self._p_itemai.get(fileid)
        if it is not None and jpeg:
            pm = QPixmap()
            if pm.loadFromData(jpeg, "JPEG"):
                it.setIcon(QIcon(self._kvadratine(pm)))

    @staticmethod
    def _kvadratine(pm):
        """Miniatiura permatomo DYDIS kvadrato centre. Qt 6.11 QIcon
        nekvadratini pixmapa istampo i langeli proporciju nepaisydamas
        (Roberto radinys 2026-08-08), o mazesnes uz langeli dar ir
        isputo i mosle - todel kvadrata komponuojam patys: proporcijos
        isliekamos, mazi vaizdai lieka naturalaus dydzio.
        Nuo 2026-08-29 ima QPixmap (bytes ateina is sandelio, ne is kelio)."""
        d = miniaturos.DYDIS
        if pm.isNull() or (pm.width() == d and pm.height() == d):
            return pm
        if pm.width() > d or pm.height() > d:
            pm = pm.scaled(d, d, Qt.AspectRatioMode.KeepAspectRatio,
                           Qt.TransformationMode.SmoothTransformation)
        kv = QPixmap(d, d)
        kv.fill(Qt.GlobalColor.transparent)
        p = QPainter(kv)
        p.drawPixmap((d - pm.width()) // 2, (d - pm.height()) // 2, pm)
        p.end()
        return kv

    def _on_min_done(self, n):
        self._baigti_darba()
        self._log(t("Miniatiuros paruostos ({}).").format(n))

    def _rezultato_kelias(self, r):
        """Pilnas failo kelias is paieskos iraso arba None."""
        if r.get("saltinio_saknis"):
            return Path(r["saltinio_saknis"]) / r["santykinis_kelias"]
        return None

    def _pranesti_neprieinama(self, r, kelias):
        """Kliurka 8: prijungimas tikrinamas GYVAI pagal serial (DB
        laukas pasenes), o zinute ISSOKA langeliu - Robertas tyliu
        zurnalo eiluciu nepastebejo (jo lukestis = dialogas)."""
        serial = r.get("volume_serial")
        if serial:
            gyvai = serial in self._prijungti_serialai()
        else:
            gyvai = bool(r.get("prijungta"))
        if not gyvai:
            zinute = t("Lentyna '{}' siuo metu neprijungta - prijunkite"
                       " diska ir pakartokite.").format(r["lentynos_vardas"])
        else:
            zinute = t("Failas nerastas: {}").format(kelias)
        self._log(zinute)
        if not self._testinis:
            QMessageBox.information(self, t("Lentyna"), zinute)

    def _on_rezultatas_dblclick(self, it):
        """Sprendimas 29: dbl-click -> Explorer su pazymejimu; neprijungtai
        lentynai - paaiskinimas (sprendimas 30, paieska veikia ir jai)."""
        r = it.data(_KELIO_ROLE)
        kelias = self._rezultato_kelias(r)
        if kelias is not None and kelias.exists():
            _parodyti_tvarkykleje(kelias)
        else:
            self._pranesti_neprieinama(r, kelias)

    def _redaktoriu_pagalba(self):
        """Spr. 4d: PRIES atidarant INI - paaiskinamasis langas su OK/Atsaukti
        ir "Klausk DI" (Roberto 2026-08-29: "ne bet kuris vartotojas supras,
        ka keisti; jei neaisku - per klaustuka pas autoriu"). OK atidaro/
        sukuria faila, "Klausk DI" nuveda pas autoriu su paruostu klausimu."""
        dlg = QMessageBox(self)
        dlg.setWindowTitle(t("Megstami redaktoriai"))
        ico = self._res_kelias("ikona.ico")
        if ico.exists():
            dlg.setIconPixmap(QIcon(str(ico)).pixmap(64, 64))
        dlg.setText(t(
            "Cia galite nurodyti savo megstamas programas, kuriomis"
            " atidarysite nuotrauka desiniu klavisu (pvz. Photoshop,"
            " GIMP, Paint).\n\n"
            "Paspaudus OK atsidarys tekstinis failas. Kiekviena programa"
            " rasoma dviem eilutemis:\n\n"
            "   [Photoshop]\n"
            "   kelias = C:\\Program Files\\...\\Photoshop.exe\n\n"
            "Lauztiniuose skliaustuose - pavadinimas, kuri matysite meniu."
            " Kelia paprasciausia nukopijuoti is Explorer adreso juostos"
            " ir iklijuoti - dvigubu bruksniu NEREIKIA.\n\n"
            "Issaugokite faila (Ctrl+S) ir uzdarykite - naujos programos"
            " meniu atsiras is karto.\n\n"
            "Jei neaisku - paspauskite \"Klausk DI\" ir autoriaus"
            " padejejas paaiskins."))
        dlg.setStandardButtons(QMessageBox.StandardButton.Ok
                               | QMessageBox.StandardButton.Cancel)
        b_di = dlg.addButton(t("Klausk DI"),
                             QMessageBox.ButtonRole.HelpRole)
        isversti_mygtukus(dlg)          # kliurka 17
        dlg.exec()
        pasp = dlg.clickedButton()
        if pasp is b_di:
            self._on_klausk_di(klausimas=(
                "How do I add my favorite editor (like Photoshop) to the"
                " right-click menu? Explain step by step in plain words."))
            return
        if dlg.standardButton(pasp) == QMessageBox.StandardButton.Ok:
            ini = redaktoriai.uztikrinti_faila()
            _atverti_os(ini)
            self._log(t("Redaktoriu failas: {}").format(ini))

    def _rezultatu_meniu(self, pozicija):
        """Desinys klavisas ant rezultato: sistemine perziurykle /
        Explorer / kelio kopija. Perziura - OS numatyta programa
        (os.startfile), ne musu vartytuvas (sprendimo 29 riba)."""
        it = self._rezultatai.itemAt(pozicija)
        if it is None:
            return
        r = it.data(_KELIO_ROLE)
        kelias = self._rezultato_kelias(r)
        meniu = QMenu(self)
        a_perziura = meniu.addAction(t("Atverti perziurai"))
        # Spr. 4d: vartotojo megstami redaktoriai (INI) - kiekvienas atskiru
        # punktu. "Namai, ne dirbtuves": mes neredaguojam, tik atiduodam.
        red_veiksmai = {}
        for vardas, red_kelias in redaktoriai.sarasas():
            veiksmas = meniu.addAction(t("Atverti su {}").format(vardas))
            red_veiksmai[veiksmas] = red_kelias
        a_redaktoriai = meniu.addAction(t("Prideti/keisti redaktorius..."))
        meniu.addSeparator()
        a_explorer = meniu.addAction(t("Parodyti Explorer'yje"))
        a_kopijuoti = meniu.addAction(t("Kopijuoti kelia"))
        pasirinktas = meniu.exec(self._rezultatai.mapToGlobal(pozicija))
        if pasirinktas is None:
            return
        if pasirinktas == a_kopijuoti:
            QApplication.clipboard().setText(
                str(kelias) if kelias else r["santykinis_kelias"])
            self._log(t("Kelias nukopijuotas."))
            return
        if pasirinktas == a_redaktoriai:
            self._redaktoriu_pagalba()
            return
        if kelias is None or not kelias.exists():
            self._pranesti_neprieinama(r, kelias)
            return
        if pasirinktas in red_veiksmai:
            ok, klaida = redaktoriai.atverti(red_veiksmai[pasirinktas], kelias)
            if not ok:
                self._log(t("Nepavyko atverti redaktoriuje: {}").format(
                    klaida))
            return
        if pasirinktas == a_perziura:
            _atverti_os(kelias)
        else:
            _parodyti_tvarkykleje(kelias)

    def _issaugoti_vaizda(self):
        filtrai = self._p_filtrai()
        if filtrai is None:
            return
        if not filtrai:
            self._log(t("Tuscios paieskos nesaugome - ivedkite bent viena"
                        " filtra."))
            return
        vardas, ok = QInputDialog.getText(
            self, t("Issaugoti paieska"), t("Duokite siai paieskai varda:"))
        vardas = vardas.strip() if ok else ""
        if not vardas:
            return
        try:
            con = indeksas.atidaryti(self._db_kelias)
            paieska.issaugoti_vaizda(con, vardas, filtrai)
            con.close()
        except Exception as e:
            self._log(t("Klaida: {}").format(e))
            return
        self._vaizdu_combo_pildyti()
        self._log(t("Paieska '{}' issaugota.").format(vardas))

    def _trinti_vaizda(self):
        vid = self._p_vaizdai.currentData()
        if vid is None:
            return
        vardas = self._p_vaizdai.currentText()
        try:
            con = indeksas.atidaryti(self._db_kelias)
            paieska.trinti_vaizda(con, vid)
            con.close()
        except Exception as e:
            self._log(t("Klaida: {}").format(e))
            return
        self._vaizdu_combo_pildyti()
        self._log(t("Vaizdas '{}' istrintas.").format(vardas))

    def _on_vaizdas_pasirinktas(self, _idx):
        vid = self._p_vaizdai.currentData()
        if vid is None:
            return
        filtrai = None
        try:
            con = indeksas.atidaryti_ro(self._db_kelias)
            filtrai = paieska.vaizdo_filtrai(con, vid)
            con.close()
        except Exception:
            pass
        if filtrai is None:
            return
        self._nustatyti_filtrus(filtrai)
        self._paieska_start(filtrai=filtrai)

    # ------------------------------- seimos DNR: kalba + portable (22-23)
    def _on_kalba_changed(self, _idx):
        """Valytuvo receptas: irasom kalba.txt + siulom perleisti dabar."""
        from kalba import issaugoti_kalba
        try:
            issaugoti_kalba(self._cmb_kalba.currentData())
        except OSError as e:
            QMessageBox.warning(
                self, t("Kalba"), t("Nepavyko issaugoti: {}").format(e))
            return
        if self._testinis:
            return
        if klausti(self, t("Kalba"),
                   t("Kalba issaugota. Perleisti programa dabar?")):
            self._perleisti_programa()

    def _perleisti_programa(self):
        """Nauja kopija + sios uzdarymas. PyInstaller onefile _MEI spastas
        (valytuvo pamoka) mums negresia - onedir, bet env vis tiek valomas."""
        env = {k: v for k, v in os.environ.items()
               if k != "_MEIPASS2" and not k.startswith("_PYI")}
        if getattr(sys, "frozen", False):
            subprocess.Popen(
                [sys.executable], env=env,
                cwd=str(Path(sys.executable).resolve().parent))
        else:
            subprocess.Popen([sys.executable] + sys.argv, env=env)
        QApplication.instance().quit()

    # ------------------------------------------------------- laikrodukas etc.
    def _mmss(self):
        return "%02d:%02d" % (self._sekundes // 60, self._sekundes % 60)

    def _tiksi(self):
        self._sekundes += 1
        self._busena.setText("%s  %s" % (self._darbo_tekstas, self._mmss()))
        self._overlay_tekstas.setText(
            "%s  %s" % (self._darbo_tekstas, self._mmss()))

    def _pradeti_darba(self, tekstas):
        self._darbo_tekstas = tekstas
        self._sekundes = 0
        self._busena.setText(tekstas + "  00:00")
        self._laikrodis.start()
        self._overlay_tekstas.setText(tekstas + "  00:00")
        self._overlay_pozicija()
        self._overlay.show()
        self._overlay.raise_()
        self._spin_laikrodis.start()
        for b in self._darbo_mygtukai:
            b.setEnabled(False)
        self._btn_atsaukti.setEnabled(True)
        self._log(tekstas + "...")

    def _baigti_darba(self):
        self._laikrodis.stop()
        self._busena.setText("")
        self._spin_laikrodis.stop()
        self._overlay.hide()
        for b in self._darbo_mygtukai:
            b.setEnabled(True)
        self._btn_atsaukti.setEnabled(False)

    def _atsaukti(self):
        if self._worker is not None:
            try:
                self._worker.stop()
            except RuntimeError:
                pass
        self._log(t("Atsaukiama - baigiama dabartine partija..."))

    def _on_klaida(self, tekstas):
        self._baigti_darba()
        self._log(t("Klaida: {}").format(tekstas))

    def _log(self, tekstas):
        self._zurnalas.appendPlainText(tekstas)


class TelefonoDialogas(QDialog):
    """v1.0 VINIS: telefono zvalgybos rezultatai - ka kopijuoti ir kur.

    Varneles rastoms medijos vietoms (pazymetos, kur failu > 0) + tikslo
    aplankas kompiuteryje (siulomas Pictures pakatalogis su telefono
    vardu ir data; "programa siulo, zmogus sprendzia" - spr. 25 DNR).
    """

    def __init__(self, telefono_vardas, vietos, parent=None):
        super().__init__(parent)
        self.setWindowTitle(t("Paimti is telefono"))
        self.setMinimumWidth(520)
        isdest = QVBoxLayout(self)
        isdest.addWidget(QLabel(t("Telefonas: {}").format(telefono_vardas)))
        isdest.addWidget(QLabel(t("Ka kopijuoti (rastos nuotrauku vietos):")))
        self._varneles = []
        for v in vietos:
            cb = QCheckBox("%s  (%s: %d)" % (v["kelias"], t("elementu"),
                                             v["kiek"]))
            cb.setChecked(v["kiek"] > 0)
            cb.setProperty("kelias", v["kelias"])
            isdest.addWidget(cb)
            self._varneles.append(cb)
        isdest.addWidget(QLabel(t("I kuri aplanka kompiuteryje:")))
        eilute = QHBoxLayout()
        siulymas = str(Path.home() / "Pictures"
                       / ("Telefonas %s %s" % (telefono_vardas.strip()[:30],
                                               date.today().isoformat())))
        self._tikslas = QLineEdit(siulymas)
        eilute.addWidget(self._tikslas, 1)
        parinkti = QPushButton(t("Parinkti..."))
        parinkti.clicked.connect(self._parinkti)
        eilute.addWidget(parinkti)
        isdest.addLayout(eilute)
        isdest.addWidget(QLabel(t("Is telefono TIK skaitoma - originalai"
                                  " jame lieka nepaliesti.")))
        mygtukai = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok
                                    | QDialogButtonBox.StandardButton.Cancel)
        isversti_mygtukus(mygtukai)     # kliurka 17
        mygtukai.accepted.connect(self.accept)
        mygtukai.rejected.connect(self.reject)
        isdest.addWidget(mygtukai)

    def _parinkti(self):
        kelias = QFileDialog.getExistingDirectory(
            self, t("I kuri aplanka kompiuteryje:"))
        if kelias:
            self._tikslas.setText(str(Path(kelias)))

    def pasirinkti(self):
        return [cb.property("kelias") for cb in self._varneles
                if cb.isChecked()]

    def tikslas(self):
        return self._tikslas.text().strip()
