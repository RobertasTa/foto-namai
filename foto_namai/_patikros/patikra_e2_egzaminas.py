# patikra_e2_egzaminas.py - E2 EGZAMINAS: pilnas poligono indeksavimas
# pries TIESA.md failo tikslumu (dubliu dovanos metodas). Konkurentai:
# MRImageSorter 34/67, PhotoMove Free 38/67. LEISTI is foto_namai:
# <venv python> -u _patikros\patikra_e2_egzaminas.py

import re
import sys
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import indeksas
import indeksavimas

POLIGONAS = Path(__file__).resolve().parent.parent.parent / "_poligonas"
SAVARTYNAS = POLIGONAS / "SAVARTYNAS"


def skaityti_tiesa():
    """TIESA.md -> [(vardas, laukiama YYYY-MM arba '-', saltinio tekstas)]."""
    eilutes = (POLIGONAS / "TIESA.md").read_text(encoding="utf-8").splitlines()
    tiesa = []
    for e in eilutes:
        m = re.match(r"- `(.+?)` -> \*\*(.+?)\*\* \((.+)\)$", e.strip())
        if m:
            tiesa.append(m.groups())
    return tiesa


def lauktas_saltinis(tekstas):
    """TIESA saltinio aprasas -> laukiamas datos_saltinis indekse."""
    if tekstas.startswith("EXIF") or tekstas.startswith("DUBLIKATAS"):
        return "exif"
    if tekstas.startswith("vardas"):
        return "vardas"
    if tekstas.startswith("mtime") or "mtime atsarga" in tekstas \
            or tekstas.startswith("ne-JPEG"):
        return "mtime"
    if tekstas.startswith("0 baitu"):
        return None
    raise ValueError("nezinomas TIESA saltinis: %s" % tekstas)


def main():
    tiesa = skaityti_tiesa()
    if len(tiesa) != 67:
        print("PATIKRA: FAIL - TIESA.md turi %d irasu, laukta 67" % len(tiesa))
        sys.exit(1)

    klaidos = []
    with tempfile.TemporaryDirectory(prefix="fotonamai_egz_") as tmp:
        db = Path(tmp) / "indeksas.db"
        con = indeksas.atidaryti(db)
        lid = indeksas.registruoti_lentyna(con, "POLIGONAS-TEST", "Poligonas")
        stat = indeksavimas.indeksuoti(SAVARTYNAS, con, lid, db)
        print("Indeksuota: %d; nepakite: %d; neatpazinta: %d; praleista: %d"
              % (stat["indeksuota"], stat["nepakite_praleista"],
                 stat["neatpazinta"], len(stat["praleista"])))

        gerai = 0
        for vardas, laukta_data, saltinio_tekstas in tiesa:
            eil = con.execute(
                "SELECT datetaken, datos_saltinis, patikima_data, hash"
                " FROM failai WHERE lentyna_id=? AND santykinis_kelias=?",
                (lid, vardas)).fetchone()
            if eil is None:
                klaidos.append("NERASTA indekse: %s" % vardas)
                continue
            datetaken, saltinis, patikima, h = eil
            l_salt = lauktas_saltinis(saltinio_tekstas)
            if laukta_data == "-":
                if datetaken is None and saltinis is None:
                    gerai += 1
                else:
                    klaidos.append("%s: laukta be datos, gauta %r/%r"
                                   % (vardas, datetaken, saltinis))
                continue
            if datetaken is None or datetaken[:7] != laukta_data:
                klaidos.append("%s: data %r, laukta %s"
                               % (vardas, datetaken, laukta_data))
                continue
            if saltinis != l_salt:
                klaidos.append("%s: saltinis %r, lauktas %r"
                               % (vardas, saltinis, l_salt))
                continue
            if l_salt == "mtime" and patikima != 0:
                klaidos.append("%s: mtime turi buti NEPATIKIMA zyma"
                               % vardas)
                continue
            if l_salt in ("exif", "vardas") and patikima != 1:
                klaidos.append("%s: %s turi buti patikima" % (vardas, l_salt))
                continue
            gerai += 1

        # Dublikatu poros: tas pats turinys -> tas pats hash (sprendimas 27a)
        for i in range(4):
            orig = con.execute(
                "SELECT hash FROM failai WHERE santykinis_kelias=?",
                ("DSC_9%03d.JPG" % i,)).fetchone()
            kop = con.execute(
                "SELECT hash FROM failai WHERE santykinis_kelias=?",
                ("Senas telefonas\\DSC_9%03d - Copy.JPG" % i,)).fetchone()
            if not (orig and kop and orig[0] and orig[0] == kop[0]):
                klaidos.append("dublio pora %d: hash nesutampa" % i)

        con.close()

    for k in klaidos:
        print("FAIL", k)
    print("EGZAMINAS: %d/67 (konkurentai: 34/67 ir 38/67)" % gerai)
    if klaidos:
        print("PATIKRA: FAIL (%d klaidu)" % len(klaidos))
        sys.exit(1)
    print("PATIKRA: OK")


if __name__ == "__main__":
    main()
