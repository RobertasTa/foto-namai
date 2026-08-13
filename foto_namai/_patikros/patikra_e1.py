# patikra_e1.py - E1 patikros: skeneris (saugikliai) + indeksas (atomika).
# Viskas dirbtiniame tempfile poligone (seimos taisykle). LEISTI:
# <venv python> -u _patikros\patikra_e1.py  (is foto_namai katalogo)

import subprocess
import sys
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import indeksas
import skeneris

KLAIDOS = []


def chk(pavadinimas, salyga, detale=""):
    if not salyga:
        KLAIDOS.append("FAIL %s %s" % (pavadinimas, detale))


def main():
    with tempfile.TemporaryDirectory(prefix="fotonamai_e1_") as tmp:
        tmp = Path(tmp)

        # --- poligonas skeneriui ---
        saknis = tmp / "SAVARTYNAS"
        (saknis / "2015 jura").mkdir(parents=True)
        (saknis / "2015 jura" / "IMG_001.jpg").write_bytes(b"x" * 100)
        (saknis / "2015 jura" / "IMG_002.jpg").write_bytes(b"y" * 200)
        (saknis / "node_modules").mkdir()
        (saknis / "node_modules" / "smukstas.js").write_bytes(b"z" * 999)
        (saknis / "Backup senas").mkdir()
        (saknis / "Backup senas" / "kopija.jpg").write_bytes(b"k" * 50)
        (saknis / "palaidas.png").write_bytes(b"p" * 10)

        # junction i ISORINI kataloga su failu - skeneris NETURI sekti
        isorinis = tmp / "ISORINIS"
        isorinis.mkdir()
        (isorinis / "uz_ribos.jpg").write_bytes(b"u" * 7777)
        junction = saknis / "nuoroda"
        r = subprocess.run(
            ["cmd", "/c", "mklink", "/J", str(junction), str(isorinis)],
            capture_output=True)
        junction_yra = r.returncode == 0

        # --- zvalgyba ---
        z = skeneris.zvalgyba(saknis)
        chk("zvalgyba_failai", z["failai"] == 3, "gauta %d" % z["failai"])
        chk("zvalgyba_baitai", z["baitai"] == 310, "gauta %d" % z["baitai"])
        priezastys = {p for _, p in z["praleista"]}
        chk("zvalgyba_juodas", "juodasis sarasas" in priezastys, priezastys)
        chk("zvalgyba_backup",
            "kopiju pasaulis (backup/snapshot)" in priezastys, priezastys)
        if junction_yra:
            chk("zvalgyba_junction", "symlink/junction" in priezastys,
                priezastys)
        else:
            print("PASTABA: mklink /J nepavyko - junction patikra praleista")

        # --- gylis ---
        failai = {}
        for rusis, reiksme in skeneris.gylis(saknis):
            if rusis == "failas":
                failai[reiksme["santykinis_kelias"]] = reiksme
        chk("gylis_kiekis", len(failai) == 3, sorted(failai))
        chk("gylis_santykinis", "2015 jura\\IMG_001.jpg" in failai,
            sorted(failai))
        chk("gylis_dydis",
            failai.get("2015 jura\\IMG_002.jpg", {}).get("dydis") == 200)

        # --- stop veliava ---
        kiek = sum(1 for _ in skeneris.gylis(saknis, stop=lambda: True))
        chk("stop_veliava", kiek == 0, "gauta %d" % kiek)

        # --- indeksas: schema, WAL, lentynos upsert ---
        db = tmp / "indeksas.db"
        con = indeksas.atidaryti(db)
        wal = con.execute("PRAGMA journal_mode").fetchone()[0]
        chk("wal", wal == "wal", wal)
        l1 = indeksas.registruoti_lentyna(con, "ABCD-1234", "Bandomoji",
                                          etikete="TEST")
        l2 = indeksas.registruoti_lentyna(con, "ABCD-1234", "Kitas vardas")
        chk("lentyna_upsert", l1 == l2, (l1, l2))

        # --- partijos irasymas + inkrementiskumas ---
        irasai = [{"lentyna_id": l1,
                   "santykinis_kelias": k,
                   "vardas": v["vardas"],
                   "dydis": v["dydis"],
                   "mtime": v["mtime"],
                   "busena": "SUINDEKSUOTAS"} for k, v in failai.items()]
        n = indeksas.irasyti_partija(con, irasai)
        chk("partija_n", n == 3, n)
        chk("nepakites_taip",
            indeksas.ar_nepakites(con, l1, "2015 jura\\IMG_001.jpg",
                                  100, irasai[0]["mtime"] if irasai else 0)
            or indeksas.ar_nepakites(
                con, l1, "2015 jura\\IMG_001.jpg", 100,
                failai["2015 jura\\IMG_001.jpg"]["mtime"]))
        chk("nepakites_ne",
            not indeksas.ar_nepakites(con, l1, "2015 jura\\IMG_001.jpg",
                                      100, failai["2015 jura\\IMG_001.jpg"]
                                      ["mtime"] + 999))
        # upsert - perindeksavus nesidubliuoja
        indeksas.irasyti_partija(con, irasai)
        kiek_db = con.execute("SELECT COUNT(*) FROM failai").fetchone()[0]
        chk("upsert_be_dubliu", kiek_db == 3, kiek_db)

        # --- nutraukimo sauga: nekomituota jungtis nieko nepalieka ---
        con2 = indeksas.atidaryti(db)
        con2.execute("BEGIN")
        con2.execute(
            "INSERT INTO failai (lentyna_id, santykinis_kelias, vardas,"
            " dydis, mtime) VALUES (?,?,?,?,?)",
            (l1, "laikinas.jpg", "laikinas.jpg", 1, 1.0))
        con2.close()   # be commit - auto-rollback
        kiek_db = con.execute("SELECT COUNT(*) FROM failai").fetchone()[0]
        chk("nutraukimas_atomika", kiek_db == 3, kiek_db)

        # --- dayid ---
        d = indeksas.dayid_is_iso("2015-06-24T18:30:00")
        chk("dayid_roundtrip", indeksas.dayid_i_iso(d) == "2015-06-24")

        indeksas.kurti_indeksus(con)
        con.close()

    if KLAIDOS:
        for k in KLAIDOS:
            print(k)
        print("PATIKRA: FAIL (%d klaidu)" % len(KLAIDOS))
        sys.exit(1)
    print("PATIKRA: OK (E1 skeneris + indeksas)")


if __name__ == "__main__":
    main()
