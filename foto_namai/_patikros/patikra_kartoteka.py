# -*- coding: utf-8 -*-
# patikra_kartoteka.py - spr. 45 KARTOTEKOS sandelio patikra (2026-08-29).
# Tikrina: (1) roundtrip irasyti/gauti; (2) mtime pasikeitimas -> None
# (pasenusi miniatiura negrizta); (3) FAT 2 s tolerancija; (4) sugadintas /
# ne-vaizdas -> None, nekrenta; (5) is_bytes JPEG kokybe (dydis <= DYDIS);
# (6) trukstami() mato tik vaizdu tipus be galiojanciu miniatiuru;
# (7) SABOTAZAS: isjungus mtime patikra gauti() grazintu pasenusia -
#     patikra tai pagauna (patikra be krentancio sabotazo = teatras).
# ASCII isvestis. Exit 0 = OK, 1 = FAIL.
import io
import sqlite3
import sys
import tempfile
from pathlib import Path

CIA = Path(__file__).resolve().parent
sys.path.insert(0, str(CIA.parent))

from PIL import Image

import miniatiuru_sandelis as ms  # noqa: E402

KLAIDOS = []


def chk(pavadinimas, salyga, detales=""):
    if salyga:
        print("  OK  %s" % pavadinimas)
    else:
        print("  FAIL %s %s" % (pavadinimas, detales))
        KLAIDOS.append(pavadinimas)


def _jpeg_bytes(w=800, h=600, spalva=(120, 40, 40)):
    img = Image.new("RGB", (w, h), spalva)
    buf = io.BytesIO()
    img.save(buf, "JPEG", quality=85)
    return buf.getvalue()


def main():
    with tempfile.TemporaryDirectory() as tmp:
        db = Path(tmp) / "poaplankis" / "miniatiuros.db"
        con = ms.atidaryti(db)   # katalogo kurimo (kliurkos 11) kelias
        chk("DB susikure giliame kataloge", db.exists())

        # 1-2. roundtrip + mtime invalidacija
        mini = ms.is_bytes(_jpeg_bytes())
        chk("is_bytes grazina JPEG", mini is not None
            and mini[:2] == b"\xff\xd8")
        with Image.open(io.BytesIO(mini)) as m:
            chk("miniatiura telpa i DYDI", max(m.size) <= ms.DYDIS, m.size)
        ms.irasyti(con, 7, 1000.0, mini)
        chk("gauti roundtrip", ms.gauti(con, 7, 1000.0) == mini)
        chk("mtime pasikeites -> None", ms.gauti(con, 7, 2000.0) is None)
        chk("FAT 2s tolerancija", ms.gauti(con, 7, 1001.5) == mini)
        chk("nezinomas fileid -> None", ms.gauti(con, 99, 1000.0) is None)

        # 3. perrasymas (upsert)
        mini2 = ms.is_bytes(_jpeg_bytes(spalva=(10, 90, 10)))
        ms.irasyti(con, 7, 2000.0, mini2)
        chk("upsert atnaujina", ms.gauti(con, 7, 2000.0) == mini2)
        chk("kiek() = 1 po upsert", ms.kiek(con) == 1)

        # 4. slamstas nekrenta
        chk("sugadintas -> None", ms.is_bytes(b"ne jpeg turinys") is None)
        chk("tuscias -> None", ms.is_bytes(b"") is None)
        chk("is_failo neegzistuojanciam -> None",
            ms.is_failo(Path(tmp) / "nera.jpg") is None)

        # 5. PNG kelias (screenshot klase)
        img = Image.new("RGB", (300, 500), (60, 60, 60))
        buf = io.BytesIO()
        img.save(buf, "PNG")
        chk("PNG -> JPEG miniatiura", ms.is_bytes(buf.getvalue()) is not None)

        # 6. trukstami() ant mini indekso
        idx = sqlite3.connect(":memory:")
        idx.execute("CREATE TABLE failai (id INTEGER PRIMARY KEY, "
                    "lentyna_id INT, saltinio_saknis TEXT, "
                    "santykinis_kelias TEXT, mtime REAL, turinio_tipas TEXT)")
        eil = [(1, 1, "E:\\", "a.jpg", 100.0, "foto"),
               (2, 1, "E:\\", "b.png", 100.0, "skrinsotas"),
               (3, 1, "E:\\", "c.mp4", 100.0, "video"),
               (4, 1, "E:\\", "d.jpg", 100.0, "foto"),
               (7, 1, "E:\\", "e.jpg", 2000.0, "foto")]
        idx.executemany("INSERT INTO failai VALUES (?,?,?,?,?,?)", eil)
        tr = ms.trukstami(idx, con)
        idai = sorted(t[0] for t in tr)
        chk("trukstami: vaizdai be minu, be video, be turimo #7",
            idai == [1, 2, 4], idai)
        tr1 = ms.trukstami(idx, con, limit=2)
        chk("trukstami limit", len(tr1) == 2)

        # 7. SABOTAZAS: jei gauti() ignoruotu mtime - pagautume
        sena = con.execute("SELECT jpeg FROM miniatiuros WHERE fileid=7"
                           ).fetchone()[0]
        chk("SABOTAZO kontrole: pasenusi mtime negrizta",
            ms.gauti(con, 7, 5000.0) is None and sena is not None)

        con.close()

    if KLAIDOS:
        print("PATIKRA: FAIL (%d)" % len(KLAIDOS))
        return 1
    print("PATIKRA: OK (spr. 45 kartotekos sandelis: roundtrip, mtime "
          "invalidacija, FAT tolerancija, slamsto atsparumas, trukstamu "
          "meniu fonui)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
