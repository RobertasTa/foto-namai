# patikra_e5.py - paieska.py teisejas (E5 dalis 2).
# Savarankiskas: pats susikuria in-memory DB su fikstUromis, jokiu
# priklausomybiu nuo projekto moduliu. ASCII only.

import sqlite3
import sys
from datetime import date
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import paieska  # noqa: E402

_SCHEMA = """
CREATE TABLE lentynos (
    id INTEGER PRIMARY KEY,
    vardas_zmogui TEXT NOT NULL,
    volume_serial TEXT NOT NULL UNIQUE,
    prijungta INTEGER NOT NULL DEFAULT 0
);
CREATE TABLE failai (
    id INTEGER PRIMARY KEY,
    lentyna_id INTEGER NOT NULL REFERENCES lentynos(id),
    santykinis_kelias TEXT NOT NULL,
    vardas TEXT NOT NULL,
    dydis INTEGER NOT NULL,
    mtime REAL NOT NULL,
    datetaken TEXT,
    dayid INTEGER,
    datos_saltinis TEXT,
    patikima_data INTEGER,
    turinio_tipas TEXT,
    renginio_etikete TEXT,
    kamera TEXT,
    saltinio_saknis TEXT
);
CREATE TABLE vaizdai (
    id INTEGER PRIMARY KEY,
    vardas TEXT NOT NULL,
    uzklausa TEXT NOT NULL
);
"""


def _ord(iso):
    return date.fromisoformat(iso).toordinal()


_FAILAI = [
    # id, lentyna, kelias, vardas, dydis, mtime, datetaken, dayid,
    # saltinis, patikima, tipas, etikete, kamera
    (1, 1, "2015\\Jonines\\IMG_0001.jpg", "IMG_0001.jpg", 1000, 1.0,
     "2015-06-24T18:30:00", _ord("2015-06-24"), "exif", 1, "foto",
     "Jonines", "Canon EOS 70D"),
    (2, 1, "2015\\Jonines\\IMG_0002.jpg", "IMG_0002.jpg", 1100, 2.0,
     "2015-06-25T10:00:00", _ord("2015-06-25"), "exif", 1, "foto",
     "Jonines", "NIKON D3200"),
    (3, 2, "2019 jura\\P100.jpg", "P100.jpg", 1200, 3.0,
     "2019-07-01T12:00:00", _ord("2019-07-01"), "vardas", 1, "foto",
     "jura", "Canon PowerShot A10"),
    (4, 1, "Screenshots\\Screenshot_20210105.png",
     "Screenshot_20210105.png", 500, 4.0,
     "2021-01-05T09:00:00", _ord("2021-01-05"), "vardas", 1,
     "skrinsotas", None, None),
    (5, 1, "keisti\\keistas.bin", "keistas.bin", 10, 5.0,
     None, None, None, None, "neatpazintas", None, None),
    (6, 2, "skenai\\scan_001.jpg", "scan_001.jpg", 2000, 6.0,
     "2015-06-24T08:00:00", _ord("2015-06-24"), "exif", 1,
     "dokumentas", None, "CanoScan LiDE"),
    (7, 1, "akcijos\\50%_nuolaida.jpg", "50%_nuolaida.jpg", 300, 7.0,
     "2020-05-05T00:00:00", _ord("2020-05-05"), "aplankas", 1, "foto",
     None, None),
    (8, 1, "akcijos\\50 procentu.jpg", "50 procentu.jpg", 310, 8.0,
     "2020-06-06T00:00:00", _ord("2020-06-06"), "mtime", 0, "foto",
     None, None),
]


def _db():
    con = sqlite3.connect(":memory:")
    con.executescript(_SCHEMA)
    con.execute("INSERT INTO lentynos VALUES (1,'Meskos kompas','SER1',1)")
    con.execute("INSERT INTO lentynos VALUES (2,'Raudonas WD','SER2',0)")
    con.executemany(
        "INSERT INTO failai (id, lentyna_id, santykinis_kelias, vardas,"
        " dydis, mtime, datetaken, dayid, datos_saltinis, patikima_data,"
        " turinio_tipas, renginio_etikete, kamera, saltinio_saknis)"
        " VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,'D:\\\\poligonas')",
        _FAILAI)
    con.commit()
    return con


_OK = 0
_FAIL = 0


def _t(salyga, zinute):
    global _OK, _FAIL
    if salyga:
        _OK += 1
    else:
        _FAIL += 1
        print("FAIL: " + zinute)


def _idai(rez):
    return [r["id"] for r in rez]


def main():
    con = _db()

    # --- be filtru: viskas, rikiavimas datetaken DESC, be datos gale ---
    _t(paieska.ieskoti_kiek(con, {}) == 8, "kiek {} turi buti 8")
    visi = paieska.ieskoti(con, {})
    _t(_idai(visi) == [4, 8, 7, 3, 2, 1, 6, 5],
       "rikiavimas: datetaken DESC, None gale, lygioms - id; gauta %r"
       % _idai(visi))

    # --- grazinamu irasu laukai ---
    r0 = visi[0]
    for raktas in ("id", "lentyna_id", "lentynos_vardas", "prijungta",
                   "santykinis_kelias", "saltinio_saknis", "vardas",
                   "dydis", "mtime", "datetaken", "datos_saltinis",
                   "patikima_data", "turinio_tipas", "renginio_etikete",
                   "kamera"):
        _t(raktas in r0, "iraso rakto truksta: " + raktas)
    _t(r0["id"] == 4 and r0["lentynos_vardas"] == "Meskos kompas"
       and r0["prijungta"] == 1, "pirmo iraso laukai neteisingi")
    r3 = [r for r in visi if r["id"] == 3][0]
    _t(r3["lentynos_vardas"] == "Raudonas WD" and r3["prijungta"] == 0,
       "JOIN lentynos_vardas/prijungta id=3")

    # --- datos rezis (dayid) ---
    _t(paieska.ieskoti_kiek(con, {"data_nuo": "2015-06-25"}) == 5,
       "data_nuo 2015-06-25 turi buti 5 (be #1 #6 ir be #5 be datos)")
    _t(_idai(paieska.ieskoti(con, {"data_nuo": "2015-06-24",
                                   "data_iki": "2015-06-24"})) == [1, 6],
       "viena diena 2015-06-24 -> [1, 6]")
    _t(paieska.ieskoti_kiek(con, {"data_iki": "2016-01-01"}) == 3,
       "data_iki 2016-01-01 turi buti 3")
    _t(paieska.ieskoti_kiek(con, {"data_nuo": "2030-01-01"}) == 0,
       "data_nuo ateityje -> 0")

    # --- etikete (fragmentas, be raidziu dydzio) ---
    _t(_idai(paieska.ieskoti(con, {"etikete": "jonines"})) == [2, 1],
       "etikete 'jonines' -> [2, 1]")
    _t(_idai(paieska.ieskoti(con, {"etikete": "JUR"})) == [3],
       "etikete 'JUR' -> [3]")

    # --- kamera (fragmentas) ---
    _t(_idai(paieska.ieskoti(con, {"kamera": "canon"})) == [3, 1],
       "kamera 'canon' -> [3, 1] (CanoScan NE!)")
    _t(_idai(paieska.ieskoti(con, {"kamera": "nikon"})) == [2],
       "kamera 'nikon' -> [2]")

    # --- tipas (tikslus) ir lentyna ---
    _t(_idai(paieska.ieskoti(con, {"tipas": "skrinsotas"})) == [4],
       "tipas skrinsotas -> [4]")
    _t(paieska.ieskoti_kiek(con, {"tipas": "foto"}) == 5,
       "tipas foto -> 5")
    _t(_idai(paieska.ieskoti(con, {"lentyna_id": 2})) == [3, 6],
       "lentyna_id 2 -> [3, 6]")

    # --- vardas + LIKE ekranavimas ---
    _t(_idai(paieska.ieskoti(con, {"vardas": "screenshot"})) == [4],
       "vardas 'screenshot' -> [4]")
    _t(_idai(paieska.ieskoti(con, {"vardas": "50"})) == [8, 7],
       "vardas '50' -> [8, 7]")
    _t(_idai(paieska.ieskoti(con, {"vardas": "50%"})) == [7],
       "vardas '50%%' turi rasti TIK #7 (%% ekranuojamas, ne wildcard!)")
    _t(_idai(paieska.ieskoti(con, {"vardas": "_nuolaida"})) == [7],
       "vardas '_nuolaida' -> [7] (_ ekranuojamas)")

    # --- kombinacijos ---
    _t(_idai(paieska.ieskoti(con, {"etikete": "jonines",
                                   "kamera": "canon"})) == [1],
       "etikete+kamera -> [1]")
    _t(_idai(paieska.ieskoti(con, {"data_nuo": "2015-01-01",
                                   "data_iki": "2015-12-31",
                                   "lentyna_id": 1})) == [2, 1],
       "datos rezis + lentyna 1 -> [2, 1]")

    # --- tusti filtrai ignoruojami ---
    _t(paieska.ieskoti_kiek(con, {"data_nuo": "", "data_iki": "",
                                  "etikete": "", "kamera": "",
                                  "vardas": "", "tipas": "",
                                  "lentyna_id": None}) == 8,
       "tusti filtrai = jokio filtro")

    # --- limit / offset ---
    _t(_idai(paieska.ieskoti(con, {}, limit=3)) == [4, 8, 7],
       "limit 3 -> [4, 8, 7]")
    _t(_idai(paieska.ieskoti(con, {}, limit=3, offset=3)) == [3, 2, 1],
       "limit 3 offset 3 -> [3, 2, 1]")

    # --- issaugotos paieskos (vaizdai) ---
    f1 = {"etikete": "jonines", "tipas": "foto"}
    vid = paieska.issaugoti_vaizda(con, "Jonines foto", f1)
    _t(isinstance(vid, int), "issaugoti_vaizda grazina int id")
    _t(paieska.vaizdo_filtrai(con, vid) == f1,
       "vaizdo_filtrai roundtrip sutampa")
    f2 = {"kamera": "canon"}
    vid2 = paieska.issaugoti_vaizda(con, "Jonines foto", f2)
    _t(vid2 == vid, "tas pats vardas -> tas pats id (upsert)")
    _t(paieska.vaizdo_filtrai(con, vid) == f2,
       "upsert atnaujino filtrus")
    vid3 = paieska.issaugoti_vaizda(con, "Akcijos", {"vardas": "50"})
    sar = paieska.vaizdu_sarasas(con)
    _t(sar == [(vid3, "Akcijos"), (vid, "Jonines foto")],
       "vaizdu_sarasas rikiuotas pagal varda; gauta %r" % (sar,))
    paieska.trinti_vaizda(con, vid3)
    _t(paieska.vaizdu_sarasas(con) == [(vid, "Jonines foto")],
       "trinti_vaizda istrina")
    _t(paieska.vaizdo_filtrai(con, 99999) is None,
       "nezinomas vaizdo id -> None")

    # --- SQL injekcijos higiena: kabute filtre nesulauzo uzklausos ---
    try:
        paieska.ieskoti(con, {"vardas": "x' OR '1'='1"})
        _t(paieska.ieskoti_kiek(con, {"vardas": "x' OR '1'='1"}) == 0,
           "kabutes filtre = paprastas tekstas, ne SQL")
    except sqlite3.OperationalError:
        _t(False, "kabute filtre sulauzo SQL - parametrai ne per ?")

    print("Patikru: %d OK, %d FAIL" % (_OK, _FAIL))
    if _FAIL == 0:
        print("PATIKRA: OK")
    else:
        print("PATIKRA: FAIL")
        sys.exit(1)


if __name__ == "__main__":
    main()
