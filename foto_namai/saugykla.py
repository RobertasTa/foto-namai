"""saugykla.py - kur gyvena programos darbiniai failai (portable vs kompiuteris).

Valytuvo v1.0 sablonas (PLANAS sprendimas 23) su seimos remonto pamoka
(sprendimas 33): zymeklis PREFIKSUOTAS - FotoNamai_portable.txt, NE
portable.txt (SDF ir TempCleaner kolizija viename flesiuko aplanke!).

- zymeklio NERA (numatyta): darbiniai failai -> %LOCALAPPDATA%/FotoNamai.
- zymeklis YRA: darbiniai failai -> _darbal salia exe (keliauja su flesiuku).

Darbiniuose failuose gyvens: indeksas.db, kalba.txt, zurnalas, miniatiuru
kesas. Laikini failai (jei ju prireiks) - TIK %TEMP%/FotoNamai/ pakatalogyje,
ne palaidi %TEMP% saknyje (sprendimas 33).
"""

import os
import shutil
import sys
from pathlib import Path

# 2026-08-13 (Roberto galutinis vardo verdiktas pries v1.0 leidima,
# kol pasaulyje nera ne vieno vartotojo duomenu): PhotoHome visur -
# exe, duomenu katalogas, zymeklis. FotoNamai liko tik repo varde.
PORTABLE_MARKER = "PhotoHome_portable.txt"
APP_DIRNAME = "PhotoHome"


def exe_dir():
    """Katalogas salia exe (frozen) arba salia .py failu (dev)."""
    if getattr(sys, "frozen", False):
        return Path(sys.executable).resolve().parent
    return Path(__file__).resolve().parent


def is_portable():
    return (exe_dir() / PORTABLE_MARKER).exists()


def _sistemos_baze():
    """OS vartotojo duomenu bazine vieta (macOS zvalgyba 2026-08-29:
    ten LOCALAPPDATA nera - naudojama Application Support)."""
    if sys.platform == "darwin":
        return str(Path.home() / "Library" / "Application Support")
    return os.environ.get("LOCALAPPDATA")


def data_dir():
    """Darbiniu failu katalogas pagal rezima (nekuriamas - kuria rasytojai)."""
    if is_portable():
        return exe_dir() / "_darbal"
    base = _sistemos_baze()
    if base:
        return Path(base) / APP_DIRNAME
    return exe_dir() / "_darbal"   # atsarga sistemoms be LOCALAPPDATA


def set_portable(on):
    """Perjungia rezima: zymeklis + darbiniu failu perkelimas + pedsaku valymas.

    Ijungiant: zymeklis sukuriamas, darbiniai failai perkeliami i _darbal
    salia exe, %LOCALAPPDATA%/FotoNamai istrinamas (pedsaku nelieka).
    Isjungiant: zymeklis nuimamas, failai grizta i %LOCALAPPDATA%.
    Grazina (ok, klaidos_tekstas) - pvz., read-only flesiukas -> (False, ...).
    """
    marker = exe_dir() / PORTABLE_MARKER
    try:
        sena = data_dir()                     # dabartine vieta (senas rezimas)
        if on:
            marker.write_text("portable\n", encoding="utf-8")
        elif marker.exists():
            marker.unlink()
        nauja = data_dir()                    # nauja vieta (rezimas jau naujas)
        if sena != nauja and sena.is_dir():
            nauja.mkdir(parents=True, exist_ok=True)
            # Keliami ir pakatalogiai (E5: miniatiuru kesas), ne tik failai
            for f in sena.iterdir():
                shutil.move(str(f), str(nauja / f.name))
        if on:
            # Pedsaku valymas: programa pati po saves susitvarko
            base = _sistemos_baze()
            if base:
                shutil.rmtree(Path(base) / APP_DIRNAME, ignore_errors=True)
        else:
            # Tuscias _darbal salia exe nebereikalingas
            try:
                (exe_dir() / "_darbal").rmdir()
            except OSError:
                pass   # netuscias ar nera - paliekam
        return True, ""
    except OSError as e:
        return False, str(e)
