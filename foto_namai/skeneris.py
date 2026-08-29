"""skeneris.py - 2 faziu skenas (E1, PLANAS sprendimai 8, 11; PIPELINE 1-2).

Faze 1 ZVALGYBA: TIK vardai/dydziai/mtime, jokio turinio skaitymo ->
ivertis prie varneles. Faze 2 GYLIS (gylis()) - generatorius indeksavimo
fazei. Saugikliai ABIEJOSE fazese (Nextcloud incidento pamokos):
- juodasis sarasas (models.JUODASIS_SARASAS, case-insensitive);
- simlinku ir junction NESEKAM (ciklu ir "kopiju pasauliu" apsauga);
- snapshot/backup katalogai -> PRALEISTA su priezastimi, gilyn nelendam;
- klaidos (permission ir pan.) -> PRALEISTA, ne griutis;
- stop() veliava tikrinama kas kataloga - atsaukiama bet kada.
"""

import os
import re
from pathlib import Path

from models import JUODASIS_SARASAS, MEDIJOS_GALUNES

# "Kopiju pasaulio" pozymiai katalogo varde (praleidziam su pranesimu)
_KOPIJU_SABLONAS = re.compile(r"backup|atsargin|kopij", re.IGNORECASE)

_JUODAS_MAZOSIOMIS = {v.lower() for v in JUODASIS_SARASAS}


def _katalogo_verdiktas(vardas):
    """None = lysti gilyn; kitaip - praleidimo priezasties tekstas."""
    if vardas.lower() in _JUODAS_MAZOSIOMIS:
        return "juodasis sarasas"
    if _KOPIJU_SABLONAS.search(vardas):
        return "kopiju pasaulis (backup/snapshot)"
    return None


def _eiti(saknis, stop=None, progress=None):
    """Bendras perejimas abiem fazems: yield ('failas', DirEntry) arba
    ('praleista', (kelias, priezastis)). Iteratyvus (be rekursijos ribu)."""
    krepsys = [str(saknis)]
    while krepsys:
        if stop is not None and stop():
            return
        katalogas = krepsys.pop()
        try:
            with os.scandir(katalogas) as ejiklis:
                for irasas in ejiklis:
                    try:
                        if irasas.is_dir(follow_symlinks=False):
                            if irasas.is_symlink() or irasas.is_junction():
                                yield ("praleista",
                                       (irasas.path, "symlink/junction"))
                                continue
                            priezastis = _katalogo_verdiktas(irasas.name)
                            if priezastis:
                                yield ("praleista", (irasas.path, priezastis))
                                continue
                            krepsys.append(irasas.path)
                        elif irasas.is_file(follow_symlinks=False):
                            # Android/MIUI siuksliadeze (kliurka 6, gyvas
                            # Xiaomi testas 2026-08-13): vartotojo ISTRINTI
                            # failai i indeksa/archyva nekeliauja.
                            if irasas.name.lower().startswith(".trashed-"):
                                yield ("praleista",
                                       (irasas.path,
                                        "Android siuksliadeze (.trashed)"))
                                continue
                            yield ("failas", irasas)
                    except OSError as e:
                        yield ("praleista", (irasas.path, "klaida: %s" % e))
        except OSError as e:
            yield ("praleista", (katalogas, "klaida: %s" % e))
        if progress is not None:
            progress(katalogas)


def zvalgyba(saknis, stop=None, progress=None):
    """Faze 1: greitas ivertis (failu kiekis, baitai) + praleidimu sarasas.
    Jokio turinio skaitymo - tik scandir stat (PIPELINE 1).

    Medija skaiciuojama ATSKIRAI (kalibravimo pamoka 2026-08-13, gyvas E:
    testas: 866k failu, bet tik 59k medijos - indeksavimas turini skaito
    tik medijai, tad trukmes ivertis pagal visus failus melavo 8 kartus).
    """
    failai = 0
    baitai = 0
    medijos_failai = 0
    medijos_baitai = 0
    praleista = []
    for rusis, reiksme in _eiti(saknis, stop=stop, progress=progress):
        if rusis == "failas":
            failai += 1
            try:
                dydis = reiksme.stat(follow_symlinks=False).st_size
            except OSError:
                continue
            baitai += dydis
            galune = os.path.splitext(reiksme.name)[1].lower()
            if galune in MEDIJOS_GALUNES:
                medijos_failai += 1
                medijos_baitai += dydis
        else:
            praleista.append(reiksme)
    return {"failai": failai, "baitai": baitai,
            "medijos_failai": medijos_failai,
            "medijos_baitai": medijos_baitai, "praleista": praleista}


def gylis(saknis, stop=None, progress=None, atskaitos_saknis=None):
    """Faze 2: generatorius indeksavimui - kiekvienam failui dict su
    santykiniu keliu lentynoje (sprendimas 30: NE absoliutus!), vardu,
    dydziu, mtime. Praleidimai -> ('praleista', ...) irasai kaip zvalgyboje.

    KLIURKA 24 (Roberto gyvas ratas 2026-08-25): kelias buvo skaiciuojamas
    nuo SALTINIO saknies, nors sprendimas 30 sako "santykinis kelias
    LENTYNOJE". Todel tas pats failas, pasiektas per du persidengiancius
    saltinius (Pictures ir Pictures\\Screenshots), gaudavo DU skirtingus
    "adresus", upsert ju nesutapatindavo ir indekse atsirasdavo dublis:
    13757 irasu vietoj 6887, "0 unchanged" vietoj 6869.
    `atskaitos_saknis` = lentynos (tomo) saknis, pvz. "C:\\". Be jos
    elgiames kaip anksciau - to reikia patikroms su laikinais katalogais."""
    saknis = Path(saknis)
    atskaita = Path(atskaitos_saknis) if atskaitos_saknis else saknis
    for rusis, reiksme in _eiti(saknis, stop=stop, progress=progress):
        if rusis == "failas":
            try:
                st = reiksme.stat(follow_symlinks=False)
            except OSError as e:
                yield ("praleista", (reiksme.path, "klaida: %s" % e))
                continue
            yield ("failas", {
                "santykinis_kelias":
                    str(Path(reiksme.path).relative_to(atskaita)),
                "vardas": reiksme.name,
                "dydis": st.st_size,
                "mtime": st.st_mtime,
            })
        else:
            yield (rusis, reiksme)
