# patikra_e7_siuksles.py - kliurkos 6/7 (gyvas Xiaomi testas 2026-08-13):
# (6) .trashed-* failai (Android/MIUI siuksliadeze) NEindeksuojami -
#     praleidziami su priezastimi "Android siuksliadeze (.trashed)";
# (7) .thumbnails katalogas (Android miniatiuru kesas) - juodajame sarase;
# (m) senos bazes issivalo vienkartine migracija (PRAGMA user_version=2),
#     UNDO minimi irasai apsaugoti.
# LEISTI is foto_namai: <venv python> -u _patikros\patikra_e7_siuksles.py

import sys
import tempfile
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import indeksas
import indeksavimas
import skeneris

KLAIDOS = []


def chk(pavadinimas, salyga, detale=""):
    if not salyga:
        KLAIDOS.append("FAIL %s %s" % (pavadinimas, detale))


# Minimalus tikras JPEG (magic bytes uztenka klasifikacijai "foto"/dydis>0)
_JPEG = bytes.fromhex("ffd8ffe000104a46494600") + b"\x00" * 64 + b"\xff\xd9"


def main():
    with tempfile.TemporaryDirectory(prefix="fotonamai_e7s_",
                                     ignore_cleanup_errors=True) as tmp:
        tmp = Path(tmp)
        saltinis = tmp / "SALTINIS"
        (saltinis / ".thumbnails").mkdir(parents=True)
        (saltinis / "Poaplankis" / ".thumbnails").mkdir(parents=True)

        (saltinis / "normali.jpg").write_bytes(_JPEG)
        (saltinis / ".trashed-1788075627-istrinta.jpg").write_bytes(_JPEG)
        (saltinis / ".Trashed-999-didziosiom.JPG").write_bytes(_JPEG)
        (saltinis / ".thumbnails" / "kesas1.jpg").write_bytes(_JPEG)
        (saltinis / "Poaplankis" / ".thumbnails" / "kesas2.jpg").write_bytes(_JPEG)
        (saltinis / "Poaplankis" / "kita.jpg").write_bytes(_JPEG)

        # --- 1. Zvalgyba: mato 2 failus, praleidimai su priezastim ---
        z = skeneris.zvalgyba(saltinis)
        chk("zvalgyba failai", z["failai"] == 2, z)
        priezastys = [p[1] for p in z["praleista"]]
        chk("zvalgyba .trashed x2",
            priezastys.count("Android siuksliadeze (.trashed)") == 2,
            priezastys)
        chk("zvalgyba .thumbnails x2 (juodasis)",
            sum(1 for p in z["praleista"]
                if p[1] == "juodasis sarasas"
                and p[0].lower().endswith(".thumbnails")) == 2,
            z["praleista"])

        # --- 2. Indeksavimas: i DB tik 2 normalus failai ---
        db = tmp / "indeksas.db"
        con = indeksas.atidaryti(db)
        lid = indeksas.registruoti_lentyna(con, "E7-SIUKSLES", "Testas")
        stat = indeksavimas.indeksuoti(saltinis, con, lid, db)
        chk("indeksuota 2", stat["indeksuota"] == 2, stat)
        vardai = {e[0] for e in con.execute("SELECT vardas FROM failai")}
        chk("indekse tik normalus", vardai == {"normali.jpg", "kita.jpg"},
            vardai)
        con.close()

        # --- 3. Migracija: sena baze su siuksliu irasais issivalo ---
        db2 = tmp / "sena.db"
        con = indeksas.atidaryti(db2)
        lid = indeksas.registruoti_lentyna(con, "SENA", "Migracija")
        dabar = time.time()
        eilutes = [
            ("gera.jpg", "gera.jpg"),
            (".trashed-123-sena.jpg", ".trashed-123-sena.jpg"),
            ("kesas.jpg", ".thumbnails\\kesas.jpg"),
            ("kesas2.jpg", "Sub\\.thumbnails\\kesas2.jpg"),
            ("undo_saugomas.jpg", ".trashed-777-undo.jpg"),
        ]
        for vardas, kelias in eilutes:
            con.execute(
                "INSERT INTO failai (lentyna_id, santykinis_kelias, vardas,"
                " dydis, mtime, busena) VALUES (?,?,?,?,?, 'SUINDEKSUOTAS')",
                (lid, kelias, vardas, 100, dabar))
        fid = con.execute(
            "SELECT id FROM failai WHERE vardas='undo_saugomas.jpg'"
        ).fetchone()[0]
        con.execute(
            "INSERT INTO undo (fileid, is_kur, i_kur, laikas)"
            " VALUES (?, 'a', 'b', 'dabar')", (fid,))
        # Kliurka 9: kamera su EXIF NUL uodega (gyvas ADATA radinys)
        con.execute("UPDATE failai SET kamera=? WHERE vardas='gera.jpg'",
                    ("Canon Canon EOS 400D DIGITAL\x00\x00\x00",))
        con.execute("PRAGMA user_version = 1")   # simuliuojam sena baze
        con.commit()
        con.close()

        con = indeksas.atidaryti(db2)   # atidarymas paleidzia migracijas
        liko = {e[0] for e in con.execute("SELECT vardas FROM failai")}
        chk("migracija istryne siuksles",
            liko == {"gera.jpg", "undo_saugomas.jpg"}, liko)
        kam = con.execute("SELECT kamera FROM failai WHERE vardas='gera.jpg'"
                          ).fetchone()[0]
        chk("kameru migracija nukirpo NUL uodega",
            kam == "Canon Canon EOS 400D DIGITAL", repr(kam))
        # 4 = pridejus _migracija_keliai (kliurka 24, 2026-08-25)
        chk("user_version=4 (visos migracijos)",
            con.execute("PRAGMA user_version").fetchone()[0] == 4)
        chk("migraciju skaitliukas >= 3",
            indeksas.pasiimti_migraciju_valymus() >= 3)
        con.close()

    if KLAIDOS:
        print("\n".join(KLAIDOS))
        print("PATIKRA: FAIL (%d)" % len(KLAIDOS))
        sys.exit(1)
    print("PATIKRA: OK (kliurkos 6/7: .trashed praleidimas, .thumbnails"
          " juodasis sarasas, senu baziu migracija su UNDO saugikliu)")


if __name__ == "__main__":
    main()
