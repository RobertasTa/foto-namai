# -*- coding: utf-8 -*-
"""patikra_unix_ms.py - Unix ms vardo sablonas (PLANAS 4e punktas 1).

Tikrina data_is_vardo 6-a sablona: 13 skaitmenu Unix ms zyme varde.
Lokalus laikas - lyginam per ta pati fromtimestamp, kad testas nepriklausytu
nuo masinos laiko juostos.
"""

import sys
from datetime import datetime
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))

from foto_namai.datos_variklis import data_is_vardo

KLAIDOS = []

def tikrinti(pav, gauta, laukta):
    if gauta == laukta:
        print("  OK   %s -> %s" % (pav, gauta))
    else:
        KLAIDOS.append(pav)
        print("  FAIL %s -> %s (laukta %s)" % (pav, gauta, laukta))

def ms_iso(ms):
    return datetime.fromtimestamp(ms / 1000).strftime("%Y-%m-%dT%H:%M:%S")

print("== Unix ms sablonas ==")

# 1. Grynas 13 skaitmenu vardas (Roberto pavyzdys is POZYMIU_KAUPIMAS)
tikrinti("1564686877912.jpg", data_is_vardo("1564686877912.jpg"),
         ms_iso(1564686877912))

# 2. Su priesaga (sijoy sensoriaus stilius is dump'o)
tikrinti("1775113451563_100.JPG", data_is_vardo("1775113451563_100.JPG"),
         ms_iso(1775113451563))

# 3. 12 skaitmenu - NE zyme
tikrinti("156468687791.jpg", data_is_vardo("156468687791.jpg"), None)

# 4. 14 skaitmenu - NE zyme (13 su kaimynu skaitmeniu neatsiskiria)
tikrinti("15646868779123.jpg", data_is_vardo("15646868779123.jpg"), None)

# 5. 13 skaitmenu uz rezio (2286 m.) - atmetama
tikrinti("9999999999999.jpg", data_is_vardo("9999999999999.jpg"), None)

# 6. 13 skaitmenu per senas (1971 m.) - atmetama
tikrinti("0031536000000.jpg", data_is_vardo("0031536000000.jpg"), None)

# 7. PRIORITETAS: WhatsApp vardas laimi pries unix ms (sablonu eile)
tikrinti("IMG-20230318-WA0006_1564686877912.jpg",
         data_is_vardo("IMG-20230318-WA0006_1564686877912.jpg"),
         "2023-03-18")

# 8. Senieji sablonai nepaliesti (regresijos sarasas is patikra_e2 dvasios)
tikrinti("IMG-20230318-WA0006.jpg", data_is_vardo("IMG-20230318-WA0006.jpg"),
         "2023-03-18")
tikrinti("Screenshot_20250218-100533.png",
         data_is_vardo("Screenshot_20250218-100533.png"),
         "2025-02-18T10:05:33")
tikrinti("20150612_130000.jpg", data_is_vardo("20150612_130000.jpg"),
         "2015-06-12T13:00:00")
tikrinti("atostogos 2015-06-12.jpg", data_is_vardo("atostogos 2015-06-12.jpg"),
         "2015-06-12")
tikrinti("bevardis.jpg", data_is_vardo("bevardis.jpg"), None)

if KLAIDOS:
    print("PATIKRA RAUDONA: %d klaidos" % len(KLAIDOS))
    sys.exit(1)
print("PATIKRA ZALIA (12/12)")
