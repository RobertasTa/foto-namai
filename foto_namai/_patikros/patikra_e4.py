# patikra_e4.py - E4 tvarkytojo patikros: planas -> dry-run -> vykdymas
# (kopijavimas, dubliu sauga, kolizija, nutraukimas+tesinys) -> UNDO.
# Viskas tempfile poligone. LEISTI is foto_namai:
# <venv python> -u _patikros\patikra_e4.py

import shutil
import sys
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import piexif
from PIL import Image

import indeksas
import indeksavimas
import models
import tvarkytojas

POLIGONAS = (Path(__file__).resolve().parent.parent.parent
             / "_poligonas" / "SAVARTYNAS")

KLAIDOS = []


def chk(pavadinimas, salyga, detale=""):
    if not salyga:
        KLAIDOS.append("FAIL %s %s" % (pavadinimas, detale))


def main():
    with tempfile.TemporaryDirectory(prefix="fotonamai_e4_",
                                     ignore_cleanup_errors=True) as tmp:
        tmp = Path(tmp)
        saltinis = tmp / "SALTINIS"
        archyvas = tmp / "ARCHYVAS"
        archyvas.mkdir()
        shutil.copytree(POLIGONAS, saltinis)

        # Live pora: IMG_7777.JPG (EXIF 2020-05) + IMG_7777.MOV (ftyp qt)
        img = Image.new("RGB", (60, 40), (10, 10, 200))
        exif = piexif.dump({"Exif": {
            piexif.ExifIFD.DateTimeOriginal: b"2020:05:05 10:00:00"}})
        img.save(str(saltinis / "IMG_7777.JPG"), "JPEG", exif=exif)
        (saltinis / "IMG_7777.MOV").write_bytes(
            b"\x00\x00\x00\x14ftypqt  " + b"\x00" * 100)

        # Kolizija su KITU turiniu tiksle (namas ne visai tuscias)
        (archyvas / "2023" / "03").mkdir(parents=True)
        (archyvas / "2023" / "03" / "IMG-20230318-WA0006.jpg").write_bytes(
            b"visai kitas turinys")

        db = tmp / "indeksas.db"
        con = indeksas.atidaryti(db)
        lid = indeksas.registruoti_lentyna(con, "E4-TEST", "Saltinis")
        indeksavimas.indeksuoti(saltinis, con, lid, db)

        # --- Live poros ---
        poru = tvarkytojas.suporuoti_live(con)
        chk("live_poru", poru == 1, poru)

        # --- planas ---
        grupes = tvarkytojas.siulyti_plana(con)
        pagal_varda = {g["grupe"]: g for g in grupes}
        # KLIURKA 23 (2026-08-25): skrinsotai nebeguli VIENAME ploksciame
        # aplanke - jie skirstomi _SCREENSHOTS\Metai\Menuo. Todel cia
        # sumuojam per visas skrinsotu pogrupes, o ne imam viena eilute.
        skr_failai = sum(
            g["failai"] for g in grupes
            if g["grupe"] == models.GRUPE_SKRINSOTAI
            or g["grupe"].startswith(models.GRUPE_SKRINSOTAI + "\\"))
        chk("gr_skrinsotai", skr_failai == 8, skr_failai)
        chk("gr_skrinsotai_medyje",
            any(g["grupe"].startswith(models.GRUPE_SKRINSOTAI + "\\")
                for g in grupes),
            [g["grupe"] for g in grupes])
        chk("gr_nepatikimos", pagal_varda.get(models.GRUPE_NEPATIKIMOS, {}).get(
            "failai") == 7, pagal_varda.get(models.GRUPE_NEPATIKIMOS))
        chk("gr_live", pagal_varda.get("2020\\05", {}).get("failai") == 2,
            pagal_varda.get("2020\\05"))
        chk("gr_dubliai",
            pagal_varda.get("2024\\06", {}).get("failai", 0) >= 8,
            pagal_varda.get("2024\\06"))   # 8 dubliu failai + atsitiktiniai
                                           # EXIF to paties menesio
        viso_plane = sum(g["failai"] for g in grupes)
        chk("plano_apimtis", viso_plane == 67, viso_plane)

        # --- patvirtinimas + dry-run ---
        n = tvarkytojas.patvirtinti_plana(con)
        chk("patvirtinta", n == 67, n)
        per = tvarkytojas.perziura(con)
        chk("perziura", per["failai"] == 67, per["failai"])

        # --- vykdymas su NUTRAUKIMU po pirmos partijos ---
        flag = {"stop": False}

        def _prog(_s):
            flag["stop"] = True

        stat1 = tvarkytojas.vykdyti(con, db, archyvas,
                                    stop=lambda: flag["stop"],
                                    progress=_prog, partijos_dydis=20)
        apdorota1 = (stat1["sutvarkyta"] + stat1["praleista_dubliai"]
                     + stat1["praleista_jau_yra"] + stat1["klaidos"])
        chk("nutraukimas", apdorota1 <= 20, stat1)

        # --- TESINYS be stop - baigia liku darba ---
        stat2 = tvarkytojas.vykdyti(con, db, archyvas)
        sutvarkyta = stat1["sutvarkyta"] + stat2["sutvarkyta"]
        dubliai = stat1["praleista_dubliai"] + stat2["praleista_dubliai"]
        klaidu = stat1["klaidos"] + stat2["klaidos"]
        chk("sutvarkyta", sutvarkyta == 63, (stat1, stat2))
        chk("dubliu_sauga", dubliai == 4, dubliai)
        chk("be_klaidu", klaidu == 0, (stat1, stat2))

        # --- archyvo struktura ---
        chk("arch_live_mov", (archyvas / "2020" / "05"
                              / "IMG_7777.MOV").exists())
        # kliurka 23: rekursyviai - jie dabar guli _SCREENSHOTS\Metai\Menuo
        chk("arch_skrinsotai",
            len(list((archyvas / models.GRUPE_SKRINSOTAI)
                     .rglob("*.png"))) == 8)
        chk("arch_skrinsotu_medis",
            any(p.is_dir() for p in
                (archyvas / models.GRUPE_SKRINSOTAI).iterdir()),
            "skrinsotai tebeguli ploksciai")
        chk("arch_kolizija",
            (archyvas / "2023" / "03" / "IMG-20230318-WA0006-2.jpg").exists())
        chk("arch_kolizija_orig",
            (archyvas / "2023" / "03" / "IMG-20230318-WA0006.jpg")
            .read_bytes() == b"visai kitas turinys")
        arch_failu = sum(1 for f in archyvas.rglob("*") if f.is_file())
        chk("arch_kiekis", arch_failu == 64, arch_failu)   # 63 + kolizinis

        # --- originalai nepaliesti (kopijavimo rezimas) ---
        salt_failu = sum(1 for f in saltinis.rglob("*") if f.is_file())
        chk("originalai_sveiki", salt_failu == 69, salt_failu)

        # --- UNDO ---
        undo_stat = tvarkytojas.atstatyti(con)
        chk("undo_kiekis", undo_stat["atstatyta"] == 63, undo_stat)
        chk("undo_be_klaidu", undo_stat["klaidos"] == 0, undo_stat)
        po_undo = sum(1 for f in archyvas.rglob("*") if f.is_file())
        chk("undo_archyvas_tuscias", po_undo == 1, po_undo)  # liko kolizinis
        chk("undo_kolizinis_gyvas",
            (archyvas / "2023" / "03" / "IMG-20230318-WA0006.jpg").exists())
        salt_po = sum(1 for f in saltinis.rglob("*") if f.is_file())
        chk("undo_originalai", salt_po == 69, salt_po)
        # KLIURKA 14 (2026-08-23): anksciau cia buvo tikrinama, kad po UNDO
        # lieka 63 ATSTATYTAS irasai - tai buvo KLAIDINGO elgesio tvirtinimas.
        # Toks indeksas nebeleisdavo tvarkyti antra karta ("Nothing to
        # organize"). Dabar UNDO grazina failus i darbine busena, o istorija
        # gyvena undo lenteleje. Pilnas dvieju ratu testas -
        # patikra_ratas_du_kartus.py.
        atstatyta_zurnale = con.execute(
            "SELECT COUNT(*) FROM undo WHERE atstatyta=1").fetchone()[0]
        chk("undo_zurnalas", atstatyta_zurnale == 63, atstatyta_zurnale)
        chk("undo_busenos_grazintos",
            con.execute("SELECT COUNT(*) FROM failai"
                        " WHERE busena='ATSTATYTAS'").fetchone()[0] == 0)
        chk("undo_vel_galima_tvarkyti",
            con.execute("SELECT COUNT(*) FROM failai"
                        " WHERE busena='SUINDEKSUOTAS'").fetchone()[0] >= 63)

        con.close()

    if KLAIDOS:
        for k in KLAIDOS:
            print(k)
        print("PATIKRA: FAIL (%d klaidu)" % len(KLAIDOS))
        sys.exit(1)
    print("PATIKRA: OK (E4: planas, dry-run, vykdymas, dubliu sauga,"
          " kolizija, nutraukimas+tesinys, pilnas UNDO)")


if __name__ == "__main__":
    main()
