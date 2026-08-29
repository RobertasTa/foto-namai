# patikra_e6_egzaminas.py - E6 EGZAMINAS: pilnas galas-i-gala poligono
# testas TIESA.md failo tikslumu, kaip buvo vertinami konkurentai
# (MRImageSorter 34/67, PhotoMove Free 38/67). Skirtumas nuo E2 egzamino:
# ten tikrintas INDEKSAS, cia - GALUTINE ARCHYVO STRUKTURA po viso
# konvejerio (skenas -> indeksas -> planas -> vykdymas), plius UNDO iki
# nulio, ataskaitos ir originalu sveikata.
#
# Musu taisykliu tiesa (PLANAS sprendimai 26/27/28):
#   EXIF + vardo failai      -> Metai\Men\vardas (TIESA.md menuo)
#   Screenshot PNG           -> _SKRINSOTAI\ (data zinoma, bet atskirai)
#   mtime + sugadintas EXIF  -> _NEPATIKIMOS_DATOS\ (nemaisiyti su patikimais)
#   dublikatai (Copy poros)  -> NEKOPIJUOJAMI antra karta (hash sauga)
#   0 baitu / netikras .jpg  -> NEJUDINAMI (lieka saltinyje)
# Kiekvienas is 67 failu duoda 1 taska, jei apdorotas pagal tiesa.
# LEISTI is foto_namai: <venv python> -u _patikros\patikra_e6_egzaminas.py

import re
import shutil
import sys
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import ataskaita
import indeksas
import indeksavimas
import models
import tvarkytojas

POLIGONAS = Path(__file__).resolve().parent.parent.parent / "_poligonas"
SAVARTYNAS = POLIGONAS / "SAVARTYNAS"

KLAIDOS = []


def chk(pavadinimas, salyga, detale=""):
    if not salyga:
        KLAIDOS.append("FAIL %s %s" % (pavadinimas, detale))


def skaityti_tiesa():
    eilutes = (POLIGONAS / "TIESA.md").read_text(encoding="utf-8").splitlines()
    tiesa = []
    for e in eilutes:
        m = re.match(r"- `(.+?)` -> \*\*(.+?)\*\* \((.+)\)$", e.strip())
        if m:
            tiesa.append(m.groups())
    return tiesa


def laukiama_vieta(santykinis, data, saltinio_tekstas):
    """TIESA irasas -> (laukiamas kelias archyve ARBA None jei nejudinti)."""
    vardas = santykinis.split("\\")[-1]
    if saltinio_tekstas.startswith("DUBLIKATAS"):
        return "DUBLIS"                     # specialus: neturi buti archyve
    if saltinio_tekstas.startswith("0 baitu") \
            or saltinio_tekstas.startswith("ne-JPEG"):
        return None                         # nejudinti, lieka saltinyje
    if vardas.lower().startswith("screenshot"):
        # KLIURKA 23 (2026-08-25): skrinsotai skirstomi _SCREENSHOTS\Metai\
        # Menuo - ta pati taisykle kaip nuotraukoms. Poligono skrinsotai
        # datas turi vardu (Screenshot_YYYYMMDD-...), tad patenka i medi.
        metai, men = data.split("-")
        return "%s\\%s\\%s\\%s" % (models.GRUPE_SKRINSOTAI, metai, men,
                                   vardas)
    if saltinio_tekstas.startswith("mtime") \
            or "mtime atsarga" in saltinio_tekstas:
        return models.GRUPE_NEPATIKIMOS + "\\" + vardas
    metai, men = data.split("-")
    return "%s\\%s\\%s" % (metai, men, vardas)


def main():
    tiesa = skaityti_tiesa()
    if len(tiesa) != 67:
        print("PATIKRA: FAIL - TIESA.md turi %d irasu" % len(tiesa))
        sys.exit(1)

    with tempfile.TemporaryDirectory(prefix="fotonamai_e6_",
                                     ignore_cleanup_errors=True) as tmp:
        tmp = Path(tmp)
        saltinis = tmp / "SALTINIS"
        archyvas = tmp / "ARCHYVAS"
        archyvas.mkdir()
        shutil.copytree(SAVARTYNAS, saltinis)
        pries = {str(f.relative_to(saltinis)): f.stat().st_size
                 for f in saltinis.rglob("*") if f.is_file()}

        # --- pilnas konvejeris, kaip GUI mygtukai ---
        db = tmp / "indeksas.db"
        con = indeksas.atidaryti(db)
        lid = indeksas.registruoti_lentyna(con, "E6-EGZAMINAS", "Saltinis")
        indeksavimas.indeksuoti(saltinis, con, lid, db)
        tvarkytojas.suporuoti_live(con)
        tvarkytojas.siulyti_plana(con)
        tvarkytojas.patvirtinti_plana(con)
        stat = tvarkytojas.vykdyti(con, db, archyvas)   # numatytasis: kopijuoti
        ataskaita.kaip_sutvarkyta_md(con, archyvas)
        ataskaita.undo_zurnalas_md(con, archyvas)

        # --- vertinimas failas-po-failo pries TIESA ---
        gerai = 0
        for santykinis, data, saltinio_tekstas in tiesa:
            vieta = laukiama_vieta(santykinis, data, saltinio_tekstas)
            if vieta == "DUBLIS":
                # dublio kopijos archyve buti NETURI (nei jokio -2 vardo)
                vardas = santykinis.split("\\")[-1]
                yra = list(archyvas.rglob(vardas.replace(".JPG", "*.JPG")))
                if not yra:
                    gerai += 1
                else:
                    KLAIDOS.append("DUBLIS nukopijuotas: %s -> %s"
                                   % (santykinis, yra))
            elif vieta is None:
                # spastai: failas NEJUDINTAS, liko saltinyje, archyve jo nera
                if (saltinis / santykinis).exists() \
                        and not list(archyvas.rglob(
                            santykinis.split("\\")[-1])):
                    gerai += 1
                else:
                    KLAIDOS.append("spastas isjudintas: %s" % santykinis)
            else:
                if (archyvas / vieta).exists():
                    gerai += 1
                else:
                    KLAIDOS.append("nerasta archyve: %s (laukta %s)"
                                   % (santykinis, vieta))

        chk("vykdymo_klaidos", stat["klaidos"] == 0, stat)
        chk("dubliu_sauga", stat["praleista_dubliai"] == 4, stat)

        # --- ataskaitos zmogui (sprendimas 20: .md DNR) ---
        chk("kaip_sutvarkyta", (archyvas / "KAIP_SUTVARKYTA.md").exists())
        chk("undo_zurnalas_md", (archyvas / "UNDO_ZURNALAS.md").exists())

        # --- originalai sveiki (kopijavimo rezimas) ---
        po = {str(f.relative_to(saltinis)): f.stat().st_size
              for f in saltinis.rglob("*") if f.is_file()}
        chk("originalai_sveiki", pries == po)

        # --- UNDO: archyvas issivalo iki nulio nuotrauku ---
        undo_stat = tvarkytojas.atstatyti(con)
        liko = [f for f in archyvas.rglob("*")
                if f.is_file() and f.suffix.lower() != ".md"]
        chk("undo_iki_nulio", not liko, liko[:5])
        # atstatyta = kiek sutvarkyta (61: 67 - 4 dubliai - 2 nejudinti)
        chk("undo_grazinta",
            undo_stat.get("atstatyta", 0) == stat["sutvarkyta"] == 61,
            (undo_stat, stat["sutvarkyta"]))
        con.close()

    for k in KLAIDOS:
        print(k)
    print("E6 EGZAMINAS: %d/67 (konkurentai: MRImageSorter 34/67,"
          " PhotoMove Free 38/67)" % gerai)
    if KLAIDOS or gerai != 67:
        print("PATIKRA: FAIL (%d klaidu)" % len(KLAIDOS))
        sys.exit(1)
    print("PATIKRA: OK (E6: galas-i-gala + UNDO + ataskaitos + originalai)")


if __name__ == "__main__":
    main()
