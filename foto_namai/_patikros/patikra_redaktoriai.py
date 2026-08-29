# -*- coding: utf-8 -*-
# patikra_redaktoriai.py - spr. 4d megstami redaktoriai (2026-08-29).
# Tikrina: (1) uztikrinti_faila sukuria pavyzdi giliame kelyje; (2) sarasas
# grazina TIK sekcijas su ESAMU failu; (3) nesamas kelias praleidziamas
# tyliai; (4) sugadintas INI nekrenta; (5) Windows kelias be dvigubu
# bruksniu veikia; (6) SABOTAZAS: jei sarasas negrintu is-file patikros -
# pagautume (nesamas .exe patektu i meniu).
# ASCII isvestis. Exit 0 = OK, 1 = FAIL.
import sys
import tempfile
from pathlib import Path

CIA = Path(__file__).resolve().parent
sys.path.insert(0, str(CIA.parent))

import saugykla        # noqa: E402

KLAIDOS = []


def chk(pav, salyga, detales=""):
    print(("  OK  " if salyga else "  FAIL ") + pav
          + ("" if salyga else " " + str(detales)))
    if not salyga:
        KLAIDOS.append(pav)


def main():
    with tempfile.TemporaryDirectory() as tmp:
        saugykla.data_dir = lambda: Path(tmp) / "gilus" / "data"
        import redaktoriai as R
        import importlib
        importlib.reload(R)

        # 1. pavyzdinis failas
        p = R.uztikrinti_faila()
        chk("failas sukurtas giliame kelyje", p.exists(), p)
        chk("pavyzdys uzkomentuotas (nera aktyviu sekciju)",
            R.sarasas() == [], R.sarasas())

        # 2-3. tikras + nesamas redaktorius
        realus = Path(tmp) / "mano redaktorius.exe"   # tarpas varde - patikra
        realus.write_bytes(b"MZ")     # tik kad is_file() butu True
        p.write_text(
            "[Mano PS]\nkelias = %s\n\n"
            "[Nesamas]\nkelias = C:\\nera tokio\\x.exe\n" % realus,
            encoding="utf-8")
        s = R.sarasas()
        chk("sarasas grazina TIK esama", s == [("Mano PS", str(realus))], s)

        # 4. sugadintas INI nekrenta
        p.write_text("[be uzdaromo\nkelias = kazkas", encoding="utf-8")
        chk("sugadintas INI -> tuscias, ne griutis", R.sarasas() == [])

        # 5. Windows kelias be dvigubu bruksniu (JSON spastas, INI - ne)
        p.write_text("[Paint]\nkelias = %s\n" % realus, encoding="utf-8")
        chk("vienguba bruksniu kelias veikia",
            R.sarasas() == [("Paint", str(realus))])

        # 6. SABOTAZAS: nesamas kelias NETURI patekti i sarasa
        p.write_text("[Vaiduoklis]\nkelias = C:\\nera\\ghost.exe\n",
                     encoding="utf-8")
        chk("SABOTAZO kontrole: nesamas .exe i sarasa NEPATENKA",
            R.sarasas() == [])

        # kabuciu apvalymas (kai kas klijuoja su kabutem)
        p.write_text('[Q]\nkelias = "%s"\n' % realus, encoding="utf-8")
        chk("kabutes apie kelia nuimamos", R.sarasas() == [("Q", str(realus))])

        # BOM (Notepad/PowerShell issaugo utf-8 SU BOM) - Roberto gyvas
        # demo 2026-08-29: meniu neberode redaktoriu. Sargas privalo ta
        # pagauti - rasom su utf-8-sig (deda BOM), sarasas turi VEIKTI.
        p.write_text("[BOM PS]\nkelias = %s\n" % realus, encoding="utf-8-sig")
        chk("BOM (utf-8-sig) INI vis tiek perskaitomas",
            R.sarasas() == [("BOM PS", str(realus))], R.sarasas())

    if KLAIDOS:
        print("PATIKRA: FAIL (%d)" % len(KLAIDOS))
        return 1
    print("PATIKRA: OK (spr. 4d redaktoriai: pavyzdys, filtras pagal esama "
          "faila, sugadinto INI atsparumas, vienguba bruksniu keliai)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
