# patikra_kopijos_rinkimas.py - 4e p. 3: kuria kopija imti (2026-08-28).
#
# Buvo: is vienodo hash kopiju laimedavo PIRMA indeksavimo eileje -
# atsitiktinumas; pasirinkus plikaja (be EXIF, per messenger), failas be
# reikalo guldavo i _UNDATED. Dabar: vykdymo eile ORDER BY patikima_data
# DESC - patikimos datos kopija archyvuojama, plikoji praleidziama kaip
# dublikatas. Spr. 44 langas nesikeicia.
# Sabotazo testas: be ORDER BY laimi zemesnio id (plikoji) kopija -
# patikra krenta.
# LEISTI is foto_namai: <venv python> -u _patikros\patikra_kopijos_rinkimas.py

import sys
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import hashai       # noqa: E402
import indeksas     # noqa: E402
import tvarkytojas  # noqa: E402

KLAIDOS = []


def chk(pavadinimas, salyga, detale=""):
    if salyga:
        print("  OK   %s" % pavadinimas)
    else:
        KLAIDOS.append(pavadinimas)
        print("  FAIL %s %s" % (pavadinimas, detale))


print("== Kopijos rinkimas pagal patikima data ==")
with tempfile.TemporaryDirectory() as tmp:
    tmp = Path(tmp)
    saltinis = tmp / "saltinis"
    (saltinis / "A").mkdir(parents=True)
    (saltinis / "B").mkdir(parents=True)
    turinys = b"\xff\xd8\xff\xe0" + b"foto turinys vienodas" * 50
    (saltinis / "A" / "foto.jpg").write_bytes(turinys)
    (saltinis / "B" / "foto_kopija.jpg").write_bytes(turinys)
    h = hashai.failo_hash(saltinis / "A" / "foto.jpg")

    db = tmp / "indeksas.db"
    con = indeksas.atidaryti(db)
    lid = indeksas.registruoti_lentyna(con, "KOPIJU-TESTAS", "Saltinis")

    def _irasyti(santykinis, vardas, patikima, tikslas):
        con.execute(
            "INSERT INTO failai (lentyna_id, saltinio_saknis,"
            " santykinis_kelias, vardas, dydis, mtime, hash,"
            " patikima_data, busena, tikslo_kelias) VALUES"
            " (?,?,?,?,?,?,?,?, 'SUPLANUOTAS', ?)",
            (lid, str(saltinis), santykinis, vardas, len(turinys), 1.0,
             h, patikima, tikslas))

    # PLIKOJI kopija saveikai su senu elgesiu ITYCIA gauna ZEMESNI id
    _irasyti(r"B\foto_kopija.jpg", "foto_kopija.jpg", 0,
             r"_UNDATED\foto_kopija.jpg")
    _irasyti(r"A\foto.jpg", "foto.jpg", 1, r"2015\06\foto.jpg")
    con.commit()

    archyvas = tmp / "archyvas"
    stat = tvarkytojas.vykdyti(con, db, archyvas)

    b1 = con.execute("SELECT busena FROM failai WHERE vardas='foto.jpg'"
                     ).fetchone()[0]
    b2 = con.execute("SELECT busena, aprasas FROM failai WHERE"
                     " vardas='foto_kopija.jpg'").fetchone()
    chk("patikima_sutvarkyta", b1 == "SUTVARKYTAS", b1)
    chk("plikoji_praleista", b2[0] == "PRALEISTAS", b2)
    chk("praleidimo_priezastis_dublikatas", "dublikatas" in (b2[1] or ""),
        b2)
    chk("archyve_datuota_vieta", (archyvas / "2015" / "06" / "foto.jpg"
                                  ).exists())
    chk("undated_svarus", not (archyvas / "_UNDATED"
                               / "foto_kopija.jpg").exists())
    chk("statistika", stat["sutvarkyta"] == 1
        and stat["praleista_dubliai"] == 1, stat)
    con.close()

if KLAIDOS:
    print("PATIKRA RAUDONA: %d klaidos" % len(KLAIDOS))
    sys.exit(1)
print("PATIKRA ZALIA (6/6)")
