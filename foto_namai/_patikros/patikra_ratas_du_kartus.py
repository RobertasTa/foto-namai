# patikra_ratas_du_kartus.py - KLIURKA 14: ar po UNDO galima tvarkyti VEL.
#
# Roberto gyvas ratas 2026-08-23: sutvarkius archyva ir paspaudus UNDO,
# antras bandymas tvarkyti sake "Nothing to organize", nors indekse gulejo
# 991 failas. Priezastis: UNDO grazindavo failus i vieta diske, bet indekse
# palikdavo ATSTATYTAS/PRALEISTAS, o planas ima tik SUINDEKSUOTAS.
# Perindeksavimas nepadeda - failai nepakite ("991 unchanged").
#
# Sena patikra_e4 tikrino, kad UNDO atstate failus DISKE ir kad archyvas
# tuscias - bet niekada nebande TVARKYTI ANTRA KARTA. Zmogus tai padaro
# natoraliai, o testas - ne. Cia butent tas ratas.
# LEISTI is foto_namai: <venv python> -u _patikros\patikra_ratas_du_kartus.py

import shutil
import sys
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import ataskaita       # noqa: E402
import indeksas        # noqa: E402
import indeksavimas    # noqa: E402
import tvarkytojas     # noqa: E402

POLIGONAS = (Path(__file__).resolve().parent.parent.parent
             / "_poligonas" / "SAVARTYNAS")

KLAIDOS = []


def chk(pavadinimas, salyga, detale=""):
    if not salyga:
        KLAIDOS.append("FAIL %s %s" % (pavadinimas, detale))


def busenos(con):
    return dict(con.execute(
        "SELECT busena, COUNT(*) FROM failai GROUP BY busena"))


def ratas(con, db, archyvas):
    """Vienas pilnas ratas: planas -> patvirtinimas -> vykdymas."""
    tvarkytojas.suporuoti_live(con)
    grupes = tvarkytojas.siulyti_plana(con)
    suplanuota = tvarkytojas.patvirtinti_plana(con)
    stat = tvarkytojas.vykdyti(con, db, archyvas, rezimas="kopijuoti")
    # kaip daro VykdymoWorker - ataskaitos archyvo saknyje
    ataskaita.kaip_sutvarkyta_md(con, archyvas)
    ataskaita.undo_zurnalas_md(con, archyvas)
    return grupes, suplanuota, stat


def main():
    with tempfile.TemporaryDirectory(prefix="fotonamai_2x_",
                                     ignore_cleanup_errors=True) as tmp:
        tmp = Path(tmp)
        saltinis = tmp / "SALTINIS"
        shutil.copytree(POLIGONAS, saltinis)
        db = tmp / "indeksas.db"
        con = indeksas.atidaryti(db)
        lid = indeksas.registruoti_lentyna(con, "2X-TEST", "Saltinis")
        indeksavimas.indeksuoti(saltinis, con, lid, db)

        # ================= PIRMAS RATAS =================
        archyvas1 = tmp / "ARCHYVAS1"
        archyvas1.mkdir()
        # Zmogaus tuscias aplankas, buves archyve PRIES tvarkyma - UNDO
        # valymas jo liesti NETURI (jis ne musu, ir mes nezinom, kam jis).
        (archyvas1 / "SVETIMAS").mkdir()
        grupes1, suplanuota1, stat1 = ratas(con, db, archyvas1)
        chk("1_suplanuota", suplanuota1 > 0, suplanuota1)
        chk("1_sutvarkyta", stat1["sutvarkyta"] > 0, stat1)
        chk("1_be_klaidu", stat1["klaidos"] == 0, stat1)
        failu_archyve1 = len([p for p in archyvas1.rglob("*")
                              if p.is_file() and p.suffix != ".md"])
        chk("1_archyve_failai", failu_archyve1 == stat1["sutvarkyta"],
            "%d vs %d" % (failu_archyve1, stat1["sutvarkyta"]))

        # ================= UNDO =========================
        undo = tvarkytojas.atstatyti(con)
        chk("undo_atstate", undo["atstatyta"] == stat1["sutvarkyta"], undo)
        chk("undo_be_klaidu", undo["klaidos"] == 0, undo)
        liko = [p for p in archyvas1.rglob("*")
                if p.is_file() and p.suffix != ".md"]
        chk("undo_archyvas_tuscias", not liko, len(liko))

        # --- KLIURKA 15: po UNDO neturi likti ir tusciu kataloriu ---
        katalogai = [p for p in archyvas1.rglob("*") if p.is_dir()]
        chk("undo_nera_tusciu_kataloqu",
            not [p for p in katalogai if p.name != "SVETIMAS"],
            [p.name for p in katalogai][:6])
        chk("undo_saknis_gyva", archyvas1.is_dir())
        chk("undo_md_liko",
            (archyvas1 / "KAIP_SUTVARKYTA.md").exists())
        # SVETIMAS aplankas buvo sukurtas PRIES tvarkyma - jo neliesti!
        chk("undo_svetimas_nepaliestas", (archyvas1 / "SVETIMAS").is_dir())

        # --- ESME: indeksas turi buti grazintas i darbine busena ---
        b = busenos(con)
        chk("po_undo_nera_ATSTATYTAS", "ATSTATYTAS" not in b, b)
        chk("po_undo_nera_PRALEISTAS", "PRALEISTAS" not in b, b)
        chk("po_undo_yra_SUINDEKSUOTAS", b.get("SUINDEKSUOTAS", 0) > 0, b)
        chk("po_undo_nera_tikslo_kelio",
            con.execute("SELECT COUNT(*) FROM failai WHERE tikslo_kelias"
                        " IS NOT NULL").fetchone()[0] == 0,
            con.execute("SELECT COUNT(*) FROM failai WHERE tikslo_kelias"
                        " IS NOT NULL").fetchone()[0])

        # ================= ANTRAS RATAS =================
        # Zmogus bando dar karta - PERINDEKSAVIMAS NEKVIECIAMAS, nes failai
        # diske nepakite (butent taip Robertas ir darė).
        archyvas2 = tmp / "ARCHYVAS2"
        archyvas2.mkdir()
        grupes2, suplanuota2, stat2 = ratas(con, db, archyvas2)
        chk("2_grupes_tokios_pat",
            sorted(g["grupe"] for g in grupes2)
            == sorted(g["grupe"] for g in grupes1),
            "%d vs %d grupiu" % (len(grupes2), len(grupes1)))
        chk("2_suplanuota_tiek_pat", suplanuota2 == suplanuota1,
            "%d vs %d" % (suplanuota2, suplanuota1))
        chk("2_sutvarkyta_tiek_pat",
            stat2["sutvarkyta"] == stat1["sutvarkyta"],
            "%d vs %d" % (stat2["sutvarkyta"], stat1["sutvarkyta"]))
        chk("2_dubliai_tiek_pat",
            stat2["praleista_dubliai"] == stat1["praleista_dubliai"],
            "%d vs %d" % (stat2["praleista_dubliai"],
                          stat1["praleista_dubliai"]))
        chk("2_be_klaidu", stat2["klaidos"] == 0, stat2)
        failu_archyve2 = len([p for p in archyvas2.rglob("*")
                              if p.is_file() and p.suffix != ".md"])
        chk("2_archyve_tiek_pat", failu_archyve2 == failu_archyve1,
            "%d vs %d" % (failu_archyve2, failu_archyve1))

        # --- ir antras UNDO turi veikti taip pat ---
        undo2 = tvarkytojas.atstatyti(con)
        chk("undo2_atstate", undo2["atstatyta"] == stat2["sutvarkyta"], undo2)
        liko2 = [p for p in archyvas2.rglob("*")
                 if p.is_file() and p.suffix != ".md"]
        chk("undo2_archyvas_tuscias", not liko2, len(liko2))
        chk("undo2_busenos_grazintos",
            busenos(con).get("SUINDEKSUOTAS", 0) > 0, busenos(con))

        # --- saltinis per abu ratus nepaliestas ---
        saltinyje = len([p for p in saltinis.rglob("*") if p.is_file()])
        chk("saltinis_sveikas", saltinyje == 67, saltinyje)
        con.close()

    if KLAIDOS:
        for k in KLAIDOS:
            print(k)
        print("PATIKRA: FAIL (%d klaidu)" % len(KLAIDOS))
        return 1
    print("PATIKRA: OK (tvarkymas -> UNDO -> TAS PATS tvarkymas antra karta)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
