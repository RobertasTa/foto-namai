# patikra_sluoksnis3.py - L3 kaimynyste + L3b mtime partijos (4e p. 7/8).
#
# Algoritmas produktizuotas 2026-08-29 is matavimo skripto (+132/+587
# ant tikro archyvo). Tikrinam: mediana, savartyno saugikli (span>31 d.
# atmetamas), min inkaru ribas, "spejimas ne inkaras" (kaimynystes
# rezultatas nemaitina kito spejimo), partijos tarpo ribą (300 s) ir
# idempotencija. SABOTAZO kontrole viduje: isjungus span saugikli
# savartynas "isgelbejamas" - saugiklis tikrai dirba.
# LEISTI is foto_namai: <venv python> -u _patikros\patikra_sluoksnis3.py

import sys
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import indeksas     # noqa: E402
import sluoksnis3   # noqa: E402

KLAIDOS = []


def chk(pavadinimas, salyga, detale=""):
    if not salyga:
        KLAIDOS.append("FAIL %s %s" % (pavadinimas, detale))


def _irasyti(con, lid, kelias, mtime, datetaken, patikima, saltinis):
    con.execute(
        "INSERT INTO failai (lentyna_id, santykinis_kelias, vardas, dydis,"
        " mtime, datetaken, patikima_data, datos_saltinis, turinio_tipas,"
        " busena) VALUES (?,?,?,?,?,?,?,?,'foto','SUINDEKSUOTAS')",
        (lid, kelias, kelias.split("\\")[-1], 1000, mtime, datetaken,
         patikima, saltinis))


def _eilute(con, kelias):
    return con.execute(
        "SELECT datetaken, datos_saltinis, patikima_data, dayid"
        " FROM failai WHERE santykinis_kelias=?", (kelias,)).fetchone()


def main():
    with tempfile.TemporaryDirectory(prefix="fn_l3_") as tmp:
        con = indeksas.atidaryti(Path(tmp) / "i.db")
        lid = indeksas.registruoti_lentyna(con, "L3-TESTAS", "Testas")

        # A: vienalytis aplankas - 4 inkarai birzelio menesyje (mtime
        # issibarste >300 s, kad nesusidarytu netycine partija)
        for i, d in enumerate(("2015-06-01", "2015-06-05", "2015-06-10",
                               "2015-06-20")):
            _irasyti(con, lid, "A\\inkaras%d.jpg" % i, 10000.0 + i * 1000,
                     d + "T10:00:00", 1, "exif")
        _irasyti(con, lid, "A\\bedatis1.jpg", 15000.0,
                 "2020-01-01T00:00:00", 0, "mtime")
        _irasyti(con, lid, "A\\bedatis2.jpg", 16000.0,
                 "2020-01-02T00:00:00", 0, "mtime")

        # B: savartynas - 3 inkarai per 2,5 metu (span saugiklis atmeta)
        for i, d in enumerate(("2015-01-01", "2016-01-01", "2017-06-01")):
            _irasyti(con, lid, "B\\inkaras%d.jpg" % i, 30000.0 + i * 1000,
                     d + "T10:00:00", 1, "exif")
        _irasyti(con, lid, "B\\bedatis.jpg", 50000.0,
                 "2020-02-01T00:00:00", 0, "mtime")

        # C: tik 2 inkarai - per mazai kaimynystei
        for i in range(2):
            _irasyti(con, lid, "C\\inkaras%d.jpg" % i, 70000.0 + i * 1000,
                     "2018-03-0%dT10:00:00" % (i + 1), 1, "exif")
        _irasyti(con, lid, "C\\bedatis.jpg", 80000.0,
                 "2020-03-01T00:00:00", 0, "mtime")

        # E: 2 tikri inkarai + 1 "kaimynyste" spejimas - spejimas
        # inkaru NELAIKOMAS, tad kaimynystei per mazai
        for i in range(2):
            _irasyti(con, lid, "E\\inkaras%d.jpg" % i, 90000.0 + i * 1000,
                     "2019-05-0%dT10:00:00" % (i + 1), 1, "exif")
        _irasyti(con, lid, "E\\spejimas.jpg", 95000.0,
                 "2019-05-03T12:00:00", 1, "kaimynyste")
        _irasyti(con, lid, "E\\bedatis.jpg", 96000.0,
                 "2020-05-01T00:00:00", 0, "mtime")

        # PARTIJA: 2 inkarai + bedatis is aplanko D per 200 s;
        # antras bedatis 400 s toliau - uz partijos ribos
        _irasyti(con, lid, "P\\inkaras0.jpg", 1000.0,
                 "2017-08-01T10:00:00", 1, "exif")
        _irasyti(con, lid, "P\\inkaras1.jpg", 1100.0,
                 "2017-08-05T10:00:00", 1, "exif")
        _irasyti(con, lid, "D\\bedatis.jpg", 1200.0,
                 "2020-04-01T00:00:00", 0, "mtime")
        _irasyti(con, lid, "D\\toli.jpg", 1600.0,
                 "2020-04-02T00:00:00", 0, "mtime")
        con.commit()

        kiek_l3, kiek_l3b = sluoksnis3.taikyti(con, lid)
        chk("l3_kiekis", kiek_l3 == 2, kiek_l3)
        chk("l3b_kiekis", kiek_l3b == 1, kiek_l3b)

        # A bedaciai: mediana = sorted(4 inkarai)[2] = 2015-06-10
        for k in ("A\\bedatis1.jpg", "A\\bedatis2.jpg"):
            eil = _eilute(con, k)
            chk("A mediana " + k, eil[0] == "2015-06-10T12:00:00", eil)
            chk("A saltinis " + k, eil[1] == "kaimynyste", eil)
            chk("A patikima " + k, eil[2] == 1, eil)
            chk("A dayid " + k, eil[3] is not None
                and indeksas.dayid_i_iso(eil[3]) == "2015-06-10", eil)

        # B savartynas - NEliestas
        eil = _eilute(con, "B\\bedatis.jpg")
        chk("B_saugiklis", eil[1] == "mtime" and eil[2] == 0, eil)
        # C per mazai inkaru - NEliestas
        eil = _eilute(con, "C\\bedatis.jpg")
        chk("C_min_inkarai", eil[1] == "mtime" and eil[2] == 0, eil)
        # E spejimas ne inkaras - NEliestas
        eil = _eilute(con, "E\\bedatis.jpg")
        chk("E_spejimas_ne_inkaras", eil[1] == "mtime" and eil[2] == 0,
            eil)
        # Partija: D\bedatis gavo 2 inkaru mediana (sorted[1] = 08-05)
        eil = _eilute(con, "D\\bedatis.jpg")
        chk("P_partija", eil[0] == "2017-08-05T12:00:00"
            and eil[1] == "partija" and eil[2] == 1, eil)
        # Uz partijos tarpo (400 s) - NEliestas
        eil = _eilute(con, "D\\toli.jpg")
        chk("P_tarpas", eil[1] == "mtime" and eil[2] == 0, eil)

        # Idempotencija: antras paleidimas nieko nebekeicia
        chk("idempotencija", sluoksnis3.taikyti(con, lid) == (0, 0))

        # SABOTAZO kontrole: isjungus span saugikli savartynas B
        # "isgelbejamas" - vadinasi, saugiklis tikrai laiko svori
        tikras = sluoksnis3.MAX_SPAN_DIENOMIS
        sluoksnis3.MAX_SPAN_DIENOMIS = 10000
        s_l3, _ = sluoksnis3.taikyti(con, lid)
        chk("sabotazas_span_dirba", s_l3 > 0,
            "span saugiklio isjungimas nieko nekeicia - teatras")
        sluoksnis3.MAX_SPAN_DIENOMIS = tikras
        con.close()

    if KLAIDOS:
        for k in KLAIDOS:
            print(k)
        print("PATIKRA: FAIL (%d klaidu)" % len(KLAIDOS))
        return 1
    print("PATIKRA: OK (sluoksnis3: kaimynystes mediana + savartyno/"
          "imties saugikliai + spejimas-ne-inkaras + partijos tarpas +"
          " idempotencija)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
