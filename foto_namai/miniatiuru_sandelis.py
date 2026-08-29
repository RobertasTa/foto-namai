"""miniatiuru_sandelis.py - KARTOTEKOS sandelis (spr. 45, 2026-08-29).

Suindeksuotu nuotrauku miniatiuros gyvena NAMU puseje (data_dir()/
miniatiuros.db, SQLite BLOB - kaip OPTI vaizdeliai DB) ir todel rodomos
ir tada, kai lentyna ATJUNGTA. Roberto formuluote (produkto tiesa):
"koks katalogas, jei negali bent miniatiuros parodyti? ieskosi -
atsirinksi tik pagal vaizda."

Kartu tai "vieno skaitymo" (spr. 27 patikslinimo) pamatas A2 fonui:
`is_bytes()` gamina miniatiura is ATMINTYJE jau perskaityto failo,
tad tas pats disko skaitymas duoda ir hash, ir miniatiura.

Atskiras nuo indekso DB samoningai: 400k x ~8 KB = keli GB, kurie
neturi puesti pagrindines DB ir jos atsarginiu kopiju. Spr. 14
(tingus failu kesas miniaturos.py) lieka greitajam prijungtos
lentynos keliui; sandelis - atjungtoms lentynoms ir fonui.

Zero Qt - GUI worker'is si moduli tik apvynios gija.
"""

import sqlite3
from datetime import datetime
from io import BytesIO
from pathlib import Path

from PIL import Image, ImageOps

import exif_skaitymas  # noqa: F401  (salutinis efektas: pillow-heif registracija)
import saugykla

# 256 (ne 192): pamatuota 2026-08-29 ant 300 tikru ADATA foto - 6,8 vs
# 4,5 KB (x1,52; 400k -> 2,6 GB vs 1,7 GB), o kartotekos esme yra
# atpazinimas AKIMI ("ar tai TA nuotrauka?") + HiDPI ekranai. Skaitymo
# greitis pamatuotas: 500 atsitiktiniu BLOB ~3,5 ms. Saugykla TIK DB
# (Roberto argumentas: katalogo vartotojas netycia nesugadins).
DYDIS = 256
KOKYBE = 80

_SCHEMA = """
CREATE TABLE IF NOT EXISTS miniatiuros (
    fileid INTEGER PRIMARY KEY,
    mtime REAL NOT NULL,
    jpeg BLOB NOT NULL,
    sukurta TEXT NOT NULL
);
"""

# Vaizdiniai turinio tipai, kuriems fonas gamina miniatiuras (video - ne:
# ju kadrą trauktume tik su ffmpeg klasės priklausomybe - ne v1)
VAIZDO_TIPAI = ("foto", "skrinsotas", "ikona", "dokumentas")


def numatytas_kelias():
    return saugykla.data_dir() / "miniatiuros.db"


def atidaryti(db_kelias=None):
    """Rasymo/skaitymo jungtis. KVIESTI toje gijoje, kuri ja naudos
    (PYQT6_THREADING_GUARD - kaip indeksas.atidaryti)."""
    kelias = Path(db_kelias) if db_kelias else numatytas_kelias()
    # Kliurkos 11 pamoka: SQLite katalogo pats nesusikuria
    if kelias.parent and not kelias.parent.exists():
        kelias.parent.mkdir(parents=True, exist_ok=True)
    con = sqlite3.connect(str(kelias))
    con.execute("PRAGMA journal_mode=WAL")
    con.execute("PRAGMA synchronous=NORMAL")
    # Du rasytojai (rodymo worker'is + fonas) gali susitikti - WAL leidzia
    # viena rasytoja vienu metu, tad antrasis LAUKIA, o ne krenta
    # "database is locked" (gyvas Roberto demo radinys 2026-08-29 nakti)
    con.execute("PRAGMA busy_timeout=15000")
    con.executescript(_SCHEMA)
    return con


def gauti(con, fileid, mtime):
    """JPEG bytes arba None. mtime nesutampa -> None (failas pasikeites,
    miniatiura pasenusi; fonas pagamins nauja)."""
    eil = con.execute("SELECT mtime, jpeg FROM miniatiuros WHERE fileid=?",
                      (fileid,)).fetchone()
    if eil is None:
        return None
    if abs(eil[0] - mtime) > 2.0:   # FAT 2 s granuliacijos tolerancija
        return None
    return eil[1]


def irasyti(con, fileid, mtime, jpeg_bytes):
    con.execute(
        "INSERT INTO miniatiuros (fileid, mtime, jpeg, sukurta) "
        "VALUES (?,?,?,?) ON CONFLICT(fileid) DO UPDATE SET "
        "mtime=excluded.mtime, jpeg=excluded.jpeg, sukurta=excluded.sukurta",
        (fileid, mtime, jpeg_bytes,
         datetime.now().isoformat(timespec="seconds")))


def kiek(con):
    return con.execute("SELECT COUNT(*) FROM miniatiuros").fetchone()[0]


def is_bytes(data):
    """Miniatiuros JPEG bytes is atmintyje esancio vaizdo failo turinio.
    None - sugadintas / ne vaizdas / per keistas (programa NIEKADA nekrenta;
    OKF_Pillow guard: draft pries load, exif_transpose, bombos -> except)."""
    if not data:
        return None
    try:
        with Image.open(BytesIO(data)) as img:
            if img.format == "JPEG":
                img.draft("RGB", (DYDIS, DYDIS))
            img = ImageOps.exif_transpose(img)
            img.thumbnail((DYDIS, DYDIS))
            if img.mode not in ("RGB", "L"):
                img = img.convert("RGB")
            buf = BytesIO()
            img.save(buf, "JPEG", quality=KOKYBE)
            return buf.getvalue()
    except Exception:
        return None


def is_failo(kelias):
    """Patogumo kelias GUI vienetiniam atvejui (fonas naudoja is_bytes,
    kad skaitymas butu VIENAS su hash)."""
    try:
        with open(kelias, "rb") as f:
            return is_bytes(f.read())
    except OSError:
        return None


def trukstami(indekso_con, sandelio_con, limit=500):
    """Sarasas [(fileid, lentyna_id, saltinio_saknis, santykinis_kelias,
    mtime)] vaizdu, kuriems sandelyje NERA galiojancios miniatiuros.
    A2 fono worker'io meniu; limit - partijos dydis."""
    turimi = {fid: mt for fid, mt in
              sandelio_con.execute("SELECT fileid, mtime FROM miniatiuros")}
    rez = []
    q = ("SELECT id, lentyna_id, saltinio_saknis, santykinis_kelias, mtime "
         "FROM failai WHERE turinio_tipas IN (%s)"
         % ",".join("?" * len(VAIZDO_TIPAI)))
    for fid, lid, saknis, kelias, mt in indekso_con.execute(q, VAIZDO_TIPAI):
        senas = turimi.get(fid)
        if senas is not None and abs(senas - mt) <= 2.0:
            continue
        rez.append((fid, lid, saknis, kelias, mt))
        if len(rez) >= limit:
            break
    return rez
