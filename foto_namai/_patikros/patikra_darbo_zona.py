# patikra_darbo_zona.py - KAIP_SUTVARKYTA "darbo zona, ne siukslynas"
# (PLANAS 4e punktas 4; POZYMIU_KAUPIMAS 5 sk. SALYGA).
#
# Pazadas: zmogus, pamates _UNDATED su tukstanciais failu, PRIVALO is
# ataskaitos suzinoti tris dalykus: (a) tai darbo zona, ne siukslynas;
# (b) failai sveiki ir nepaliesti; (c) prie ju dar bus griztama (naujos
# versijos gilina lentyna is vidaus). Tikrinam LT ir EN (kliurkos 13/16
# dvasia - .md failai zmogaus kalba).
# LEISTI is foto_namai: <venv python> -u _patikros\patikra_darbo_zona.py

import sys
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import ataskaita   # noqa: E402
import indeksas    # noqa: E402
import kalba       # noqa: E402

KLAIDOS = []


def chk(pavadinimas, salyga, detale=""):
    if salyga:
        print("  OK   %s" % pavadinimas)
    else:
        KLAIDOS.append(pavadinimas)
        print("  FAIL %s %s" % (pavadinimas, detale))


print("== KAIP_SUTVARKYTA: darbo zona, ne siukslynas ==")
with tempfile.TemporaryDirectory() as tmp:
    db = Path(tmp) / "indeksas.db"
    con = indeksas.atidaryti(db)
    archyvas = Path(tmp) / "archyvas"
    archyvas.mkdir()

    sena_kalba = kalba.LANG
    try:
        kalba.LANG = "lt"
        ataskaita.kaip_sutvarkyta_md(con, archyvas)
        lt = (archyvas / "KAIP_SUTVARKYTA.md").read_text(encoding="utf-8")
        chk("lt_darbo_zona", "DARBO ZONA, ne siukslynas" in lt)
        chk("lt_failai_sveiki", "sveiki ir nepaliesti" in lt)
        chk("lt_bus_griztama", "dar bus griztama" in lt)
        chk("lt_gylio_pavyzdys", "_UNDATED\\2015\\06" in lt)

        kalba.LANG = "en"
        ataskaita.kaip_sutvarkyta_md(con, archyvas)
        en = (archyvas / "KAIP_SUTVARKYTA.md").read_text(encoding="utf-8")
        chk("en_darbo_zona", "WORK AREA, not a junk pile" in en)
        chk("en_failai_sveiki", "intact and untouched" in en)
        chk("en_bus_griztama", "will be revisited" in en)
        chk("en_be_lietuvisku", "siukslynas" not in en,
            "EN ataskaitoje liko lietuviskas tekstas (kliurkos 13/16)")
    finally:
        kalba.LANG = sena_kalba
        con.close()

if KLAIDOS:
    print("PATIKRA RAUDONA: %d klaidos" % len(KLAIDOS))
    sys.exit(1)
print("PATIKRA ZALIA (8/8)")
