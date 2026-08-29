"""sluoksnis3.py - L3 kaimynyste ir L3b mtime partijos (4e p. 7/8).

Produktizuota 2026-08-29 is _matavimas_sluoksniu\\matuok_sluoksnius.py -
ALGORITMAS TAS PATS, kuris 08-28 pamatuotas ant tikro archyvo
(+132 kaimynyste, +587 partijos; saugikliai teisingai atmete Autodesk
sample bibliotekas, zaidimu asset'us ir "alaus bokalo" savartynus).

Po-indeksavimo perejimas per VIENA lentyna (Zero Qt, be failu skaitymo):
  L3  KAIMYNYSTE: jei aplanko failai su PATIKIMA data (inkarai, >=3)
      telpa i <=31 d. span - aplankas vienalytis, ir jo bedaciai
      (mtime) gauna inkaru MEDIANOS diena. Issibarste inkarai =
      savartynas, praleidziam (sluoksnis PATS PASITIKRINA).
  L3b MTIME PARTIJOS: kas atkeliavo kartu (mtime tarpas <=300 s), tas
      gimines - partijos inkaru (>=2, span <=31 d.) mediana gelbsti
      likusius bedacius. Datos neduoda - duoda KILME.

Idempotencija ir dreifo sauga: isgelbeti failai gauna datos_saltinis
'kaimynyste'/'partija' ir patikima_data=1, bet INKARAIS NELAIKOMI
(spejimas negali maitinti kito spejimo) - antras paleidimas nieko
nebekeicia, inkrementiskai atsirade nauji inkarai gelbsti tik dar
neisgelbetus.
"""

from datetime import datetime
from pathlib import Path

MIN_INKARU_KAIMYNYSTEJE = 3
MIN_INKARU_PARTIJOJE = 2
MAX_SPAN_DIENOMIS = 31        # matavimo "grieztas" slenkstis (ne 92!)
PARTIJOS_TARPAS_S = 300

# Spejimu sluoksniai - niekada ne inkarai
_SPEJIMAI = ("kaimynyste", "partija")


def _diena(datetaken):
    try:
        return datetime.fromisoformat(datetaken).date()
    except (ValueError, TypeError):
        return None


def _span_d(dienos):
    return (max(dienos) - min(dienos)).days


def _mediana(dienos):
    return sorted(dienos)[len(dienos) // 2]


def _prirasyti(con, irasai, diena, saltinis):
    """Bedaciu israsymas: medianos diena (T12:00 - neutralus vidudienis,
    tikro laiko nezinom), saltinis atviru tekstu, patikima=1 (failas
    keliauja i Metai\\Menuo, nebe i _UNDATED). mtime stulpelis lieka -
    niekas neprarasta."""
    iso = diena.isoformat() + "T12:00:00"
    dayid = diena.toordinal()
    con.executemany(
        "UPDATE failai SET datetaken=?, dayid=?, datos_saltinis=?,"
        " patikima_data=1 WHERE id=?",
        [(iso, dayid, saltinis, ir["id"]) for ir in irasai])


def taikyti(con, lentyna_id):
    """L3 + L3b vienai lentynai. Grazina (kiek_kaimynyste, kiek_partija).

    Dirba tik su busena='SUINDEKSUOTAS' (suplanuoti/sutvarkyti
    nebejudinami) ir tik su patikima_data=0 taikiniais (0 baitu /
    neatpazintas turinys datos neturi ir jos negauna - TIESA '-')."""
    eiles = [dict(zip(("id", "kelias", "mtime", "datetaken",
                       "patikima", "saltinis"), e))
             for e in con.execute(
                 "SELECT id, santykinis_kelias, mtime, datetaken,"
                 " COALESCE(patikima_data, -1), datos_saltinis"
                 " FROM failai WHERE lentyna_id=? AND"
                 " busena='SUINDEKSUOTAS'", (lentyna_id,))]
    kiek_l3 = kiek_l3b = 0

    # --- L3 kaimynyste: aplankas -> inkarai/bedaciai ------------------
    pagal_aplanka = {}
    for ir in eiles:
        pagal_aplanka.setdefault(
            str(Path(ir["kelias"]).parent), []).append(ir)
    for grupe in pagal_aplanka.values():
        inkarai = [d for ir in grupe
                   if ir["patikima"] == 1 and ir["saltinis"] not in _SPEJIMAI
                   and (d := _diena(ir["datetaken"])) is not None]
        bedaciai = [ir for ir in grupe if ir["patikima"] == 0]
        if not bedaciai or len(inkarai) < MIN_INKARU_KAIMYNYSTEJE:
            continue
        if _span_d(inkarai) > MAX_SPAN_DIENOMIS:
            continue          # savartyno saugiklis: aplankas nevienalytis
        _prirasyti(con, bedaciai, _mediana(inkarai), "kaimynyste")
        for ir in bedaciai:   # kad L3b ju nebeimtu (ir ne inkarai!)
            ir["patikima"], ir["saltinis"] = 1, "kaimynyste"
        kiek_l3 += len(bedaciai)

    # --- L3b mtime partijos (visos lentynos mastu) --------------------
    rikiuoti = sorted(eiles, key=lambda ir: ir["mtime"])
    partija = []
    for ir in rikiuoti + [None]:          # None - paskutines uzdarymas
        if partija and (ir is None or
                        ir["mtime"] - partija[-1]["mtime"]
                        > PARTIJOS_TARPAS_S):
            inkarai = [d for p in partija
                       if p["patikima"] == 1 and p["saltinis"] not in
                       _SPEJIMAI and (d := _diena(p["datetaken"]))
                       is not None]
            bedaciai = [p for p in partija if p["patikima"] == 0]
            if (bedaciai and len(inkarai) >= MIN_INKARU_PARTIJOJE
                    and _span_d(inkarai) <= MAX_SPAN_DIENOMIS):
                _prirasyti(con, bedaciai, _mediana(inkarai), "partija")
                kiek_l3b += len(bedaciai)
            partija = []
        if ir is not None:
            partija.append(ir)

    con.commit()
    return kiek_l3, kiek_l3b
