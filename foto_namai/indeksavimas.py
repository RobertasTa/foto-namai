"""indeksavimas.py - PIPELINE 2 konvejeris: failo kelione a-e (E2 dalis 2).

Kiekvienam failui: a) inkrementiskumo patikra (nepakites -> praleisti);
b) magic bytes (formatas tikras ar apsimetelis, sprendimas 28);
c) EXIF (exif_skaitymas, try/except viduje); d) hash (perkelimo saugai,
sprendimas 27); e) irasu partija i DB kas partijos_dydis su disko sargu
(sprendimai 9-10). Zero Qt - E3 worker'is si modulį tik apvynios gija.

Aplanko datos/etiketes skaiciuojamos is SANTYKINIO kelio lentynoje -
kelias virs lentynos saknies programai neegzistuoja (sprendimas 30).
"""

import shutil
from datetime import datetime
from pathlib import Path

import datos_variklis
import exif_skaitymas
import hashai
import indeksas
import skeneris
import turinio_tipas
from models import MEDIJOS_GALUNES, MIN_LAISVA_VIETA_MB

# Formatai, kuriems verta atidaryti Pillow (kitiems EXIF neieskom)
_VAIZDU_FORMATAI = {"jpeg", "png", "gif", "bmp", "tiff", "webp", "heic"}


class DiskoSargoKlaida(RuntimeError):
    """Per mazai laisvos vietos DB diske - partija nestumiama."""


def _disko_sargas(db_kelias):
    laisva_mb = shutil.disk_usage(Path(db_kelias).parent).free / 1048576
    if laisva_mb < MIN_LAISVA_VIETA_MB:
        raise DiskoSargoKlaida(
            "liko %.0f MB (riba %d MB)" % (laisva_mb, MIN_LAISVA_VIETA_MB))


def _apdoroti(saknis, lentyna_id, r):
    """Vieno failo kelione b-d. Grazina irasa irasyti_partija formatu."""
    kelias = Path(saknis) / r["santykinis_kelias"]
    mtime_iso = datetime.fromtimestamp(r["mtime"]).isoformat(
        timespec="seconds")
    santykinis_aplankas = str(Path(r["santykinis_kelias"]).parent)

    antraste = b""
    if r["dydis"] > 0:
        try:
            with open(kelias, "rb") as f:
                antraste = f.read(32)
        except OSError:
            pass
    formatas = turinio_tipas.magic_formatas(antraste)

    ex = exif_skaitymas.skaityti(kelias) if formatas in _VAIZDU_FORMATAI \
        else dict(exif_skaitymas._TUSCIA)

    try:
        h = hashai.failo_hash(kelias) if r["dydis"] > 0 else None
    except OSError:
        h = None

    etikete = (datos_variklis.data_is_aplanko(santykinis_aplankas)
               or (None, None, None))[2]

    if r["dydis"] == 0:
        # 0 baitu - indeksuojam fakta, bet datos nesprendziame (TIESA "-")
        datetaken, saltinis, patikima, tipas = None, None, None, "neatpazintas"
    else:
        datetaken, saltinis, patikima = datos_variklis.isspresti_data(
            ex["exif_iso"], r["vardas"], santykinis_aplankas, mtime_iso)
        tipas = turinio_tipas.klasifikuoti(
            formatas, ex["turi_kameros_exif"],
            ex["plotis"] or 0, ex["aukstis"] or 0, r["vardas"])

    return {
        "lentyna_id": lentyna_id,
        "saltinio_saknis": str(saknis),
        "santykinis_kelias": r["santykinis_kelias"],
        "vardas": r["vardas"],
        "dydis": r["dydis"],
        "mtime": r["mtime"],
        "hash": h,
        "exif_blob": ex["blob"],
        "datetaken": datetaken,
        "dayid": indeksas.dayid_is_iso(datetaken) if datetaken else None,
        "datos_saltinis": saltinis,
        "patikima_data": (1 if patikima else 0) if patikima is not None
                         else None,
        "turinio_tipas": tipas,
        "kamera": ex["kamera"],
        "renginio_etikete": etikete,
        "lat": ex["lat"],
        "lon": ex["lon"],
        "busena": "SUINDEKSUOTAS",
    }


def indeksuoti(saknis, con, lentyna_id, db_kelias, stop=None, progress=None,
               partijos_dydis=500):
    """Pilnas saltinio indeksavimas. Grazina statistika. Atsaukiama bet
    kada (stop) - kas irasyta, lieka; kita sesija tesia (inkrementiskumas).
    progress(kiek_apdorota) kvieciamas po kiekvienos partijos."""
    stat = {"indeksuota": 0, "nepakite_praleista": 0, "neatpazinta": 0,
            "ne_medija": 0, "praleista": []}
    partija = []

    def _stumti():
        if not partija:
            return
        _disko_sargas(db_kelias)
        indeksas.irasyti_partija(con, partija)
        stat["indeksuota"] += len(partija)
        partija.clear()
        if progress is not None:
            progress(stat["indeksuota"])

    for rusis, r in skeneris.gylis(saknis, stop=stop):
        if rusis == "praleista":
            stat["praleista"].append(r)
            continue
        # Sprendimas 36: ne medija (pdf/exe/zip/muzika) NEindeksuojama -
        # FOTO namai yra nuotrauku tvarkytojas, ne failu inventorius.
        if Path(r["vardas"]).suffix.lower() not in MEDIJOS_GALUNES:
            stat["ne_medija"] += 1
            continue
        if indeksas.ar_nepakites(con, lentyna_id, r["santykinis_kelias"],
                                 r["dydis"], r["mtime"]):
            stat["nepakite_praleista"] += 1
            continue
        irasas = _apdoroti(saknis, lentyna_id, r)
        if irasas["turinio_tipas"] == "neatpazintas":
            stat["neatpazinta"] += 1
        partija.append(irasas)
        if len(partija) >= partijos_dydis:
            _stumti()
    _stumti()
    indeksas.kurti_indeksus(con)
    return stat
