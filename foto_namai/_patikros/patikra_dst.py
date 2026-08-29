# patikra_dst.py - DST/laiko juostos idempotencijos patikra (2026-08-22).
# Kilme: Camera Bits forumo t=14873 - Photo Mechanic po perejimo i vasaros
# laika persisiunte VISA kortele, nes ju "ar jau turiu?" raktas remiasi
# mtime lokaliu laiku. Musu rizika: FAT32/exFAT lentynos diske laiko LOKALU
# laika, todel po DST suolio to PATIES failo st_mtime pasislenka lygiai
# +-3600 s (arba +-7200 s) -> ar_nepakites sakytu "pakito" -> beprasmis
# pilnas lentynos perindeksavimas dukart per metus.
# Lūkestis: dydis sutampa + poslinkis LYGIAI 1h/2h (+-2 s) = NEPAKITES.
# LEISTI: <venv python> -u _patikros\patikra_dst.py  (is foto_namai katalogo)

import sys
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import indeksas

KLAIDOS = []


def chk(pavadinimas, salyga, detale=""):
    if not salyga:
        KLAIDOS.append("FAIL %s %s" % (pavadinimas, detale))


def main():
    with tempfile.TemporaryDirectory(prefix="fotonamai_dst_") as tmp:
        db = Path(tmp) / "indeksas.db"
        con = indeksas.atidaryti(db)
        lid = indeksas.registruoti_lentyna(con, "DST-TEST-1234", "DST testas")

        mtime = 1755855600.0  # bazine epocha (reiksme nesvarbi)
        irasas = {
            "lentyna_id": lid,
            "santykinis_kelias": "2019 jura/IMG_100.jpg",
            "vardas": "IMG_100.jpg",
            "dydis": 12345,
            "mtime": mtime,
            "busena": "yra",
        }
        indeksas.irasyti_partija(con, [irasas])

        kel, dyd = irasas["santykinis_kelias"], irasas["dydis"]

        # 1) bazine elgsena nekeista (regresija)
        chk("tas_pats_mtime", indeksas.ar_nepakites(con, lid, kel, dyd, mtime))
        chk("fat_2s_granuliacija",
            indeksas.ar_nepakites(con, lid, kel, dyd, mtime + 1.9))
        chk("kitas_dydis_pakites",
            not indeksas.ar_nepakites(con, lid, kel, dyd + 1, mtime))
        chk("nezinomas_failas",
            not indeksas.ar_nepakites(con, lid, "nera/tokio.jpg", dyd, mtime))

        # 2) DST poslinkiai - tas pats failas NETURI tapti "pakitusiu"
        for poslinkis in (3600, -3600, 7200, -7200):
            chk("dst_%+d" % poslinkis,
                indeksas.ar_nepakites(con, lid, kel, dyd, mtime + poslinkis),
                "poslinkis %+d s laikomas pakitimu" % poslinkis)
        # FAT 2 s granuliacija ANT DST poslinkio
        chk("dst_3600_su_granuliacija",
            indeksas.ar_nepakites(con, lid, kel, dyd, mtime + 3600 + 1.9))

        # 3) tikri pakitimai LIEKA pakitimais
        for poslinkis in (1800, 300, 5400, 3610, 10800):
            chk("tikras_pakitimas_%+d" % poslinkis,
                not indeksas.ar_nepakites(con, lid, kel, dyd,
                                          mtime + poslinkis),
                "poslinkis %+d s praleistas kaip nepakites" % poslinkis)

        con.close()

    if KLAIDOS:
        print("\n".join(KLAIDOS))
        print("PATIKRA RAUDONA: %d klaidos" % len(KLAIDOS))
        return 1
    print("patikra_dst OK")
    return 0


if __name__ == "__main__":
    sys.exit(main())
