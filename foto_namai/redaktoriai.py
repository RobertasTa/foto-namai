"""redaktoriai.py - vartotojo MEGSTAMU redaktoriu sarasas (spr. 4d,
2026-08-29). "Namai, ne dirbtuves": mes NEREDAGUOJAM, bet desiniu klavisu
atiduodam faila i JO mylima irankį (Photoshop, Corel, GIMP, Affinity...).

Formatas INI (ne JSON!): Windows keliai JSON'e reikalautu dvigubu bruksniu,
o vartotojas klijuoja is Explorer TIESIAI. INI atlaidus, o sekcijos vardas
pats tampa meniu punktu:

    [Photoshop]
    kelias = C:\\Program Files\\Adobe\\Photoshop.exe

    [Corel]
    kelias = C:\\Program Files\\Corel\\CorelDRAW.exe

Failas gyvena NAMU puseje (saugykla.data_dir()/redaktoriai.ini), kad
portable rezime keliautu su flesiuku ir butu VARTOTOJO, ne musu. Pirma
karta sukuriamas su UZKOMENTUOTU pavyzdziu (spr. 4d 1-as klausimas -
kad zmogus nesusidurtu su tyliu nieku).

Zero Qt.
"""
import configparser
import subprocess
import sys
from pathlib import Path

import saugykla

FAILAS = "redaktoriai.ini"

_PAVYZDYS = """\
; PHOTO home - jusu megstami redaktoriai.
; Kiekviena [sekcija] taps atskiru desinio klaviso meniu punktu.
; Kelia kopijuokite TIESIAI is Explorer adreso juostos - dvigubu
; bruksniu NEREIKIA.
;
; Nuimkite ; nuo pavyzdziu arba iraskite savo:
;
; [Photoshop]
; kelias = C:\\Program Files\\Adobe\\Adobe Photoshop 2026\\Photoshop.exe
;
; [Nuotrauku perziura]
; kelias = C:\\Windows\\System32\\mspaint.exe
;
; PASTABA: Lightroom Classic failo kaip argumento NEPRIIMA (dirba per
; kataloga), tad ji cia irasyti nera prasmes. Photoshop, GIMP, Affinity,
; IrfanView, Paint - priima.
"""


def _kelias():
    return saugykla.data_dir() / FAILAS


def uztikrinti_faila():
    """Sukuria pavyzdini INI, jei jo dar nera. Grazina Path.
    Saugu kviesti bet kada (read-only vieta -> tyliai praleidzia)."""
    p = _kelias()
    if not p.exists():
        try:
            p.parent.mkdir(parents=True, exist_ok=True)
            p.write_text(_PAVYZDYS, encoding="utf-8")
        except OSError:
            pass
    return p


def sarasas():
    """[(vardas, kelias_str)] is INI - tik sekcijos su ESAMU 'kelias' failu.
    Neteisingi/nesami keliai praleidziami TYLIAI (vartotojo failas, ne musu -
    nekrentam ir nekaltinam). Tuscias sarasas = punktu meniu nerodom."""
    p = _kelias()
    if not p.is_file():
        return []
    cp = configparser.ConfigParser()
    try:
        # utf-8-SIG: Notepad ir PowerShell issaugo INI su BOM zyme, o be sio
        # BOM patenka i pirma eilute ir configparser meta "no section
        # headers" - saraso nebus (Roberto gyvas demo 2026-08-29: meniu
        # neberode redaktoriu, nors INI teisingas). utf-8-sig nuima BOM ir
        # veikia ir be jo.
        cp.read(p, encoding="utf-8-sig")
    except (configparser.Error, OSError):
        return []
    rez = []
    for sekcija in cp.sections():
        kelias = (cp[sekcija].get("kelias") or "").strip().strip('"')
        if kelias and Path(kelias).is_file():
            rez.append((sekcija, kelias))
    return rez


def atverti(redaktoriaus_kelias, failo_kelias):
    """Paleidzia redaktoriu su failu. Grazina (ok, klaidos_tekstas).
    macOS - 'open -a' (platformu riba VIENOJE vietoje, spr. 4d 3-as)."""
    try:
        if sys.platform == "darwin":
            subprocess.Popen(["open", "-a", str(redaktoriaus_kelias),
                              str(failo_kelias)])
        else:
            subprocess.Popen([str(redaktoriaus_kelias), str(failo_kelias)])
        return True, ""
    except OSError as e:
        return False, str(e)
