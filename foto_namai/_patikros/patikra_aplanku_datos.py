# patikra_aplanku_datos.py - aplanku parserio defektai is TIKRO archyvo
# (MATAVIMO_ATASKAITA 8.7: NAMU\NUOTRAUKOS\2007_03_23 gyvi failai, 08-28).
#
# Defektas (a): "2007_03_23" nematomas IS VISO - pabraukimas yra \w,
#   todel \b riba nesusidaro ir nei YYYY-MM, nei metu sablonas nesuveikia;
#   failai gultu i _UNDATED, nors data uzrasyta ant aplanko.
# Defektas (b): "2007-03-23" parsiriamas kaip 2007-03, bet dienos
#   likutis "-23" tampa renginio ETIKETE (archyve gautusi "2007\03 -23").
# Vaistas: (a0) sablonas YYYY[-_.]MM[[-_.]DD] pries senuosius; senieji
# elgesiai (etiketes, gryni metai, 2015\06) NEPAKITE.
# LEISTI is foto_namai: <venv python> -u _patikros\patikra_aplanku_datos.py

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from datos_variklis import data_is_aplanko   # noqa: E402

KLAIDOS = []


def chk(pavadinimas, gauta, laukta):
    if gauta == laukta:
        print("  OK   %-38s -> %s" % (pavadinimas, (gauta,)))
    else:
        KLAIDOS.append(pavadinimas)
        print("  FAIL %-38s -> %s (laukta %s)" % (pavadinimas, (gauta,),
                                                  (laukta,)))


print("== Defektas (a): pabraukimu formatas ==")
chk("2007_03_23", data_is_aplanko(r"NAMU\NUOTRAUKOS\2007_03_23"),
    (2007, 3, None))
chk("gilus kelias (Roberto gyvas)",
    data_is_aplanko(r"NAMU\NUOTRAUKOS\2007_03_23\A REKLAMA\New Folder"),
    (2007, 3, None))
chk("2010.03 kelione", data_is_aplanko(r"Foto\2010.03 kelione"),
    (2010, 3, "kelione"))

print("== Defektas (b): dienos likutis nebe etikete ==")
chk("2007-03-23", data_is_aplanko(r"NUOTRAUKOS\2007-03-23"),
    (2007, 3, None))
chk("2015-06-24 Jonines", data_is_aplanko(r"F\2015-06-24 Jonines"),
    (2015, 6, "Jonines"))

print("== Senieji elgesiai nepakite ==")
chk("2015-06 Jonines", data_is_aplanko(r"F\2015-06 Jonines"),
    (2015, 6, "Jonines"))
chk("Atostogos 2015", data_is_aplanko(r"F\Atostogos 2015"),
    (2015, None, "Atostogos"))
chk("2015 gryni metai", data_is_aplanko(r"F\2015"), (2015, None, None))
chk("2015 su menesio pakatalogiu", data_is_aplanko(r"F\2015\06"),
    (2015, 6, None))
chk("be datos", data_is_aplanko(r"F\Seni dokumentai"), None)

print("== Saugikliai (ne datos) ==")
chk("2007_99 ne menuo (zinoma riba: pabrauktas metas lieka None)",
    data_is_aplanko(r"F\2007_99"), None)
chk("1234_05 ne metai", data_is_aplanko(r"F\1234_05"), None)
chk("20150612_130000 vientisas", data_is_aplanko(r"F\20150612_130000"),
    None)

if KLAIDOS:
    print("PATIKRA RAUDONA: %d klaidos" % len(KLAIDOS))
    sys.exit(1)
print("PATIKRA ZALIA (13/13)")
