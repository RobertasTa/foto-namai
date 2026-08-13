"""indeksas.py - SQLite indeksas (E1, PLANAS sprendimai 1, 10, 18, 24, 30).

OKF_sqlite3 guard'o taisykles, kuriu LAIKOMES:
- jungtis gimsta TOJE gijoje, kuri ja naudos (worker'io run() viduje
  kviecia atidaryti(); GUI skaitymui - atidaryti_ro());
- WAL + synchronous NORMAL - testinumas ir gyvas GUI indeksavimo metu;
  portable kopijavimui imti indeksas.db + -wal + -shm ARBA pries tai close();
- atomines partijos per irasyti_partija (BEGIN + executemany + commit);
- datos TIK TEXT ISO + dayid INT (Py3.12 datetime adapteriai deprecated);
- parametrai TIK per ?, PRAGMA foreign_keys=ON kiekvienai jungciai;
- keliai saugomi str, santykiniai lentynoje (ne absoliutus!).
"""

import sqlite3
from datetime import date, datetime

DB_VARDAS = "indeksas.db"

_SCHEMA = """
CREATE TABLE IF NOT EXISTS lentynos (
    id INTEGER PRIMARY KEY,
    vardas_zmogui TEXT NOT NULL CHECK (length(vardas_zmogui) <= 40),
    volume_serial TEXT NOT NULL UNIQUE,
    etikete TEXT,
    fs TEXT,
    talpa_baitais INTEGER,
    paskutini_karta_matyta TEXT,
    prijungta INTEGER NOT NULL DEFAULT 0
);
CREATE TABLE IF NOT EXISTS failai (
    id INTEGER PRIMARY KEY,
    lentyna_id INTEGER NOT NULL REFERENCES lentynos(id),
    santykinis_kelias TEXT NOT NULL COLLATE NOCASE,
    vardas TEXT NOT NULL,
    dydis INTEGER NOT NULL,
    mtime REAL NOT NULL,
    hash TEXT,
    exif_blob BLOB,
    datetaken TEXT,
    dayid INTEGER,
    datos_saltinis TEXT,
    patikima_data INTEGER,
    turinio_tipas TEXT,
    kamera TEXT,
    renginio_etikete TEXT,
    lat REAL,
    lon REAL,
    live_pora_id INTEGER,
    busena TEXT NOT NULL DEFAULT 'RASTAS',
    aprasas TEXT,
    tikslo_kelias TEXT,
    saltinio_saknis TEXT,
    UNIQUE (lentyna_id, santykinis_kelias)
);
CREATE TABLE IF NOT EXISTS vektoriai (
    fileid INTEGER NOT NULL REFERENCES failai(id),
    modelis TEXT NOT NULL,
    dim INTEGER NOT NULL,
    vektorius BLOB NOT NULL,
    PRIMARY KEY (fileid, modelis)
);
CREATE TABLE IF NOT EXISTS seansai (
    id INTEGER PRIMARY KEY,
    pradzia TEXT NOT NULL,
    pabaiga TEXT,
    aprasymas TEXT
);
CREATE TABLE IF NOT EXISTS undo (
    id INTEGER PRIMARY KEY,
    seanso_id INTEGER REFERENCES seansai(id),
    fileid INTEGER REFERENCES failai(id),
    is_kur TEXT NOT NULL,
    i_kur TEXT NOT NULL,
    hash TEXT,
    rezimas TEXT,
    laikas TEXT NOT NULL,
    atstatyta INTEGER NOT NULL DEFAULT 0
);
CREATE TABLE IF NOT EXISTS vaizdai (
    id INTEGER PRIMARY KEY,
    vardas TEXT NOT NULL,
    uzklausa TEXT NOT NULL
);
"""


def dayid_is_iso(iso_tekstas):
    """Dienos kibirelis (sprendimas 18): proleptines Grigaliaus dienos
    ordinalas - grupavimui be datu aritmetikos uzklausose."""
    return datetime.fromisoformat(iso_tekstas).date().toordinal()


def dayid_i_iso(dayid):
    return date.fromordinal(dayid).isoformat()


def atidaryti(db_kelias):
    """Rasymo jungtis. KVIESTI toje gijoje, kuri ja naudos (guard 1)."""
    con = sqlite3.connect(str(db_kelias))
    con.execute("PRAGMA journal_mode=WAL")
    con.execute("PRAGMA synchronous=NORMAL")
    con.execute("PRAGMA foreign_keys=ON")
    con.executescript(_SCHEMA)
    # Migracijos dev bazems, sukurtoms pries E4 (naujose stulpeliai jau yra)
    for alter in ("ALTER TABLE failai ADD COLUMN tikslo_kelias TEXT",
                  "ALTER TABLE failai ADD COLUMN saltinio_saknis TEXT",
                  "ALTER TABLE failai ADD COLUMN kamera TEXT",
                  "ALTER TABLE undo ADD COLUMN rezimas TEXT"):
        try:
            con.execute(alter)
        except sqlite3.OperationalError:
            pass   # stulpelis jau yra
    _migracija_36(con)
    _migracija_siuksles(con)
    _migracija_kameros(con)
    con.commit()
    return con


# UX slifas 2026-08-13 (Roberto pastaba - tyli migracija): migracijos
# susumuoja istrintus irasus cia, o IndeksavimoWorker po atidarymo
# pasiima suma ir iraso zurnalo eilute. Skaitytojas nusinulina pats.
_MIGRACIJU_VALYMAI = [0]


def pasiimti_migraciju_valymus():
    """Grazina ir nunulina migraciju istrintu irasu suma."""
    n = _MIGRACIJU_VALYMAI[0]
    _MIGRACIJU_VALYMAI[0] = 0
    return n


def _migracija_36(con):
    """Vienkartinis valymas (sprendimas 36): pries si sprendima indeksuoti
    ne-medijos irasai (pdf/exe/zip...) ismetami. Vykdoma karta per baze
    (PRAGMA user_version), ne kiekviena atidaryma."""
    from models import MEDIJOS_GALUNES
    if con.execute("PRAGMA user_version").fetchone()[0] >= 1:
        return
    salygos = " AND ".join(
        "lower(vardas) NOT LIKE '%%%s'" % g for g in sorted(MEDIJOS_GALUNES))
    # Saugiklis: UNDO zurnale minimu failu nekliudom (ju ir neturetu buti -
    # ne medija niekada netvarkoma, bet atsarga gudresne uz gaila)
    cur = con.execute("DELETE FROM failai WHERE " + salygos +
                      " AND id NOT IN (SELECT fileid FROM undo"
                      " WHERE fileid IS NOT NULL)")
    _MIGRACIJU_VALYMAI[0] += max(cur.rowcount, 0)
    con.execute("PRAGMA user_version = 1")


def _migracija_siuksles(con):
    """Vienkartinis valymas (kliurkos 6/7, gyvas Xiaomi testas 2026-08-13):
    senose bazese jau suindeksuoti Android siuksliadezes .trashed-* failai
    ir .thumbnails keso irasai ismetami - skeneris ju neberanda, tad
    inkrementiskumas ju niekada nebeatnaujintu. UNDO minimi irasai
    saugomi (sprendimo 36 saugiklio pavyzdys)."""
    if con.execute("PRAGMA user_version").fetchone()[0] >= 2:
        return
    cur = con.execute(
        "DELETE FROM failai WHERE (lower(vardas) LIKE '.trashed-%'"
        " OR lower(santykinis_kelias) LIKE '.thumbnails\\%'"
        " OR lower(santykinis_kelias) LIKE '%\\.thumbnails\\%')"
        " AND id NOT IN (SELECT fileid FROM undo"
        " WHERE fileid IS NOT NULL)")
    _MIGRACIJU_VALYMAI[0] += max(cur.rowcount, 0)
    con.execute("PRAGMA user_version = 2")


def _migracija_kameros(con):
    """Vienkartinis valymas (kliurka 9, gyvas ADATA testas 2026-08-13):
    senose bazese kameros lauke like EXIF NUL uodegos ('Canon...\\x00') -
    ta pati kamera paieskos filtre skildavo i kelis variantus. Valymas
    Python'e (SQLite TRIM su NUL nepatikimas)."""
    if con.execute("PRAGMA user_version").fetchone()[0] >= 3:
        return
    pataisyta = 0
    for fid, kam in con.execute(
            "SELECT id, kamera FROM failai WHERE kamera IS NOT NULL"
    ).fetchall():
        svarus = kam.replace("\x00", "").strip() or None
        if svarus != kam:
            con.execute("UPDATE failai SET kamera=? WHERE id=?",
                        (svarus, fid))
            pataisyta += 1
    _MIGRACIJU_VALYMAI[0] += pataisyta
    con.execute("PRAGMA user_version = 3")


def atidaryti_ro(db_kelias):
    """Read-only jungtis GUI skaitymui (mode=ro per URI, guard 1)."""
    con = sqlite3.connect("file:%s?mode=ro" % str(db_kelias), uri=True)
    con.execute("PRAGMA foreign_keys=ON")
    return con


def registruoti_lentyna(con, volume_serial, vardas_zmogui, etikete=None,
                        fs=None, talpa_baitais=None, dabar_iso=None):
    """Lentynos upsert pagal volume_serial (sprendimas 30: tapatybe ant
    serial, vardas tik zmogui). Grazina lentynos id."""
    dabar = dabar_iso or datetime.now().isoformat(timespec="seconds")
    eil = con.execute("SELECT id FROM lentynos WHERE volume_serial=?",
                      (volume_serial,)).fetchone()
    if eil:
        # vardas_zmogui irgi atnaujinamas: GUI paduoda arba esama DB varda
        # (isoriniai diskai), arba autovarda (vidiniai - Roberto verdiktas
        # 2026-08-07, senos "Diskas C:" lentynos persivadina pacios)
        con.execute(
            "UPDATE lentynos SET vardas_zmogui=?, etikete=?, fs=?,"
            " talpa_baitais=?, paskutini_karta_matyta=?, prijungta=1"
            " WHERE id=?",
            (vardas_zmogui[:40], etikete, fs, talpa_baitais, dabar, eil[0]))
        con.commit()
        return eil[0]
    kur = con.execute(
        "INSERT INTO lentynos (vardas_zmogui, volume_serial, etikete, fs,"
        " talpa_baitais, paskutini_karta_matyta, prijungta)"
        " VALUES (?,?,?,?,?,?,1)",
        (vardas_zmogui[:40], volume_serial, etikete, fs, talpa_baitais, dabar))
    con.commit()
    return kur.lastrowid


def ar_nepakites(con, lentyna_id, santykinis_kelias, dydis, mtime):
    """Inkrementiskumas (sprendimas 1): ar failas jau indekse ir nepakites
    (dydis + mtime sutampa)? Tada indeksavimo faze ji PRALEIDZIA."""
    eil = con.execute(
        "SELECT dydis, mtime FROM failai WHERE lentyna_id=?"
        " AND santykinis_kelias=?",
        (lentyna_id, santykinis_kelias)).fetchone()
    return bool(eil) and eil[0] == dydis and abs(eil[1] - mtime) < 2.0


_IRASO_LAUKAI = ("lentyna_id", "santykinis_kelias", "vardas", "dydis",
                 "mtime", "hash", "exif_blob", "datetaken", "dayid",
                 "datos_saltinis", "patikima_data", "turinio_tipas",
                 "kamera", "renginio_etikete", "lat", "lon", "busena",
                 "saltinio_saknis")


def irasyti_partija(con, irasai):
    """Atomine partija (sprendimas 10, guard 3): BEGIN + executemany +
    commit. irasai - list[dict] su _IRASO_LAUKAI raktais (truksta ->
    None). UPSERT pagal (lentyna_id, santykinis_kelias) - perindeksavimas
    atnaujina. Nutraukus pries commit - nieko neiraso (rollback saugus)."""
    if not irasai:
        return 0
    eiles = [tuple(r.get(k) for k in _IRASO_LAUKAI) for r in irasai]
    con.execute("BEGIN")
    con.executemany(
        "INSERT INTO failai (%s) VALUES (%s)"
        " ON CONFLICT(lentyna_id, santykinis_kelias) DO UPDATE SET "
        "vardas=excluded.vardas, dydis=excluded.dydis, mtime=excluded.mtime,"
        "hash=excluded.hash, exif_blob=excluded.exif_blob,"
        "datetaken=excluded.datetaken, dayid=excluded.dayid,"
        "datos_saltinis=excluded.datos_saltinis,"
        "patikima_data=excluded.patikima_data,"
        "turinio_tipas=excluded.turinio_tipas,"
        "kamera=excluded.kamera,"
        "renginio_etikete=excluded.renginio_etikete,"
        "lat=excluded.lat, lon=excluded.lon, busena=excluded.busena,"
        "saltinio_saknis=excluded.saltinio_saknis"
        % (",".join(_IRASO_LAUKAI), ",".join("?" * len(_IRASO_LAUKAI))),
        eiles)
    con.commit()
    return len(eiles)


def kurti_indeksus(con):
    """Antriniai indeksai PO masinio INSERT (guard 3), idempotentiska."""
    con.executescript("""
        CREATE INDEX IF NOT EXISTS ix_failai_dayid ON failai(dayid);
        CREATE INDEX IF NOT EXISTS ix_failai_hash ON failai(hash);
        CREATE INDEX IF NOT EXISTS ix_failai_busena ON failai(busena);
        CREATE INDEX IF NOT EXISTS ix_failai_etikete
            ON failai(renginio_etikete);
    """)
    con.commit()
