"""Higienos sargyba (SDF pamoka 2026-08-13, ta pacia diena rasta ir FOTO
namuose - kirilicos 'e' skeneris.py komentare): jokiu kirilicos
apsimeteliu raidziu saltiniuose. ASCII-only sablonas, kad sargyba
nepagautu pati saves (SDF run 31679235066 anekdotas).
"""

import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
CYRILLIC = re.compile("[\\u0400-\\u04ff]")
TIKRINAMOS = {".py", ".txt", ".json", ".spec"}

# 2026-08-30 (RU/DE kalbos): yra vietu, kur kirilica ne apsimetelis, o
# turinys. Bet leidziama SIAURAI - tik siuose failuose IR tik teksto
# eilutese (tarp kabuciu). Komentare ar kode kirilica lieka klaida net
# cia, nes butent ten homoglifas ir pavojingas.
KIRILICA_LEIDZIAMA = {
    "kalba_ru.py",      # visas rusu zodynas
    "kalba.py",         # _KIEKIAI_RU daugiskaitos formos
    "gui_langas.py",    # kalbu sarasas
}
TEKSTO_EILUTE = re.compile(r'"[^"]*"|\'[^\']*\'')


def main():
    bedos = []
    for p in ROOT.rglob("*"):
        if (not p.is_file() or p.suffix.lower() not in TIKRINAMOS
                or ".venv" in p.parts or ".git" in p.parts
                or "__pycache__" in p.parts):
            continue
        try:
            tekstas = p.read_text(encoding="utf-8", errors="ignore")
        except OSError:
            continue
        leidziama = p.name in KIRILICA_LEIDZIAMA
        for i, eilute in enumerate(tekstas.splitlines(), 1):
            # Leidziamuose failuose kirilica teksto eilutese yra turinys;
            # tikrinam tik tai, kas lieka isemus kabutes.
            tikrinama = TEKSTO_EILUTE.sub("", eilute) if leidziama else eilute
            m = CYRILLIC.search(tikrinama)
            if m:
                bedos.append("%s:%d U+%04X" % (
                    p.relative_to(ROOT), i, ord(m.group())))
    if bedos:
        print("KIRILICOS APSIMETELIAI (%d):" % len(bedos))
        for b in bedos[:20]:
            print("  " + b)
        print("PATIKRA: BLOGAI")
        sys.exit(1)
    print("PATIKRA: OK (kirilicos saltiniuose nera)")


if __name__ == "__main__":
    main()
