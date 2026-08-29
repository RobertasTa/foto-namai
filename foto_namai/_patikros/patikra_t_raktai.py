"""t() raktu sargyba (KLIURKA 28 pamoka, 2026-08-29): kiekvienas kode
kvieciamas t("...") raktas PRIVALO tureti EN zodyno irasa - kitaip EN
rezime vartotojas mato lietuviska teksta (mygtukas "Klausk DI" vietoj
"Ask AI" redaktoriu dialoge, Roberto gyvas radinys demo rate).

Metodas - AST, ne regex: ast automatiskai sujungia gretimas string
literalas, tad pagaunami ir daugiaeiliai raktai.
"""

import ast
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

# Raktai, kuriems vertimo TYCIA nera (LT tekstas sutampa su EN).
# Pildyti tik samoningai - kiekvienas irasas cia reiskia "perziurejau,
# tai ne trukstamas vertimas".
ISIMTYS = set()


def surinkti_raktus():
    """Visi t("...") kvietimai su konstantiniu pirmu argumentu."""
    raktai = {}   # raktas -> pirma rasta vieta (failas:eilute)
    for p in sorted(ROOT.glob("*.py")):
        medis = ast.parse(p.read_text(encoding="utf-8"), filename=p.name)
        for node in ast.walk(medis):
            if (isinstance(node, ast.Call)
                    and isinstance(node.func, ast.Name)
                    and node.func.id == "t" and node.args
                    and isinstance(node.args[0], ast.Constant)
                    and isinstance(node.args[0].value, str)):
                raktai.setdefault(
                    node.args[0].value, "%s:%d" % (p.name, node.lineno))
    return raktai


def main():
    import kalba
    raktai = surinkti_raktus()
    if len(raktai) < 50:
        print("ITARTINA: rasta tik %d t() raktu - AST rinkimas suluzo?"
              % len(raktai))
        print("PATIKRA: BLOGAI")
        sys.exit(1)
    bedos = [(r, vieta) for r, vieta in sorted(raktai.items())
             if r not in kalba._EN and r not in ISIMTYS]
    if bedos:
        print("RAKTAI BE EN VERTIMO (%d):" % len(bedos))
        for r, vieta in bedos[:20]:
            print("  %s  <- %r" % (vieta, r[:60]))
        print("PATIKRA: BLOGAI")
        sys.exit(1)
    print("PATIKRA: OK (visi %d t() raktai turi EN vertima)" % len(raktai))


if __name__ == "__main__":
    main()
