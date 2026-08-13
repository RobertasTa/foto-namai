# patikra_e2.py - E2 varikliuku teisejas (raso Claude, mergyte NELIECIA).
# Leisti is projekto saknies: PYTHONPATH= ./.venv/Scripts/python.exe _patikros/patikra_e2.py

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

KLAIDOS = []


def chk(pavadinimas, gauta, laukta):
    if gauta != laukta:
        KLAIDOS.append("FAIL %s: gauta %r, laukta %r" % (pavadinimas, gauta, laukta))


def main():
    from datos_variklis import data_is_vardo, data_is_aplanko, isspresti_data
    from turinio_tipas import magic_formatas, klasifikuoti

    # --- data_is_vardo ---
    chk("wa", data_is_vardo("IMG-20250114-WA0001.jpg"), "2025-01-14")
    chk("wa_vid", data_is_vardo("VID-20231201-WA0042.mp4"), "2023-12-01")
    chk("scr_minus", data_is_vardo("Screenshot_20250302-101533.png"),
        "2025-03-02T10:15:33")
    chk("scr_under", data_is_vardo("Screenshot_20240715_083000.png"),
        "2024-07-15T08:30:00")
    chk("pxl", data_is_vardo("PXL_20230817_142233123.jpg"),
        "2023-08-17T14:22:33")
    chk("bendras_dt", data_is_vardo("20191231_235959.jpg"),
        "2019-12-31T23:59:59")
    chk("bendras_iso", data_is_vardo("atostogos 2020-07-15 papludimys.jpg"),
        "2020-07-15")
    chk("nera", data_is_vardo("IMG_1234.jpg"), None)
    chk("dsc_nera", data_is_vardo("DSC_0042.jpg"), None)
    chk("men13", data_is_vardo("IMG-20251341-WA0001.jpg"), None)
    chk("vas30", data_is_vardo("IMG-20250230-WA0001.jpg"), None)
    chk("blogas_laikas", data_is_vardo("Screenshot_20250302-256099.png"),
        "2025-03-02")
    chk("seni_metai", data_is_vardo("photo_19891231_120000.jpg"), None)

    # --- data_is_aplanko ---
    chk("apl_etik_metai", data_is_aplanko(r"D:\Foto\Jonines 2015"),
        (2015, None, "Jonines"))
    chk("apl_metai_etik", data_is_aplanko(r"D:\Foto\2019 jura"),
        (2019, None, "jura"))
    chk("apl_ymm", data_is_aplanko(r"D:\Foto\2015-06 Jonines"),
        (2015, 6, "Jonines"))
    chk("apl_metai_men", data_is_aplanko(r"D:\Foto\2021\12"),
        (2021, 12, None))
    chk("apl_nera", data_is_aplanko(r"D:\Foto\Nuotraukos"), None)
    chk("apl_gilyn", data_is_aplanko(r"D:\Foto\Kaledos 2021\geriausios"),
        (2021, None, "Kaledos"))
    chk("apl_sistema", data_is_aplanko(r"C:\Users\User\Pictures"), None)
    chk("apl_2050", data_is_aplanko(r"D:\Foto\metai 2050"), None)

    # --- isspresti_data ---
    chk("h_exif", isspresti_data("2015-06-24T18:30:00",
        "IMG-20250114-WA0001.jpg", r"D:\Foto\2019 jura",
        "2025-08-01T00:00:00"),
        ("2015-06-24T18:30:00", "exif", True))
    chk("h_vardas", isspresti_data(None, "IMG-20250114-WA0001.jpg",
        r"D:\Foto\2019 jura", "2025-08-01T00:00:00"),
        ("2025-01-14", "vardas", True))
    chk("h_apl_men", isspresti_data(None, "IMG_1234.jpg",
        r"D:\Foto\2015-06 Jonines", "2025-08-01T00:00:00"),
        ("2015-06-01", "aplankas", True))
    chk("h_apl_metai", isspresti_data(None, "IMG_1234.jpg",
        r"D:\Foto\2019 jura", "2025-08-01T00:00:00"),
        ("2019-01-01", "aplankas", True))
    chk("h_mtime", isspresti_data(None, "IMG_1234.jpg",
        r"D:\Foto\Nuotraukos", "2025-08-01T12:00:00"),
        ("2025-08-01T12:00:00", "mtime", False))

    # --- magic_formatas ---
    chk("m_jpeg", magic_formatas(b"\xff\xd8\xff\xe0\x00\x10JFIF"), "jpeg")
    chk("m_png", magic_formatas(b"\x89PNG\r\n\x1a\n\x00\x00"), "png")
    chk("m_gif", magic_formatas(b"GIF89a\x01\x00"), "gif")
    chk("m_bmp", magic_formatas(b"BM8\x00\x00\x00"), "bmp")
    chk("m_tiff_ii", magic_formatas(b"II*\x00\x08\x00"), "tiff")
    chk("m_tiff_mm", magic_formatas(b"MM\x00*\x00\x08"), "tiff")
    chk("m_webp", magic_formatas(b"RIFF\x10\x00\x00\x00WEBPVP8 "), "webp")
    chk("m_heic", magic_formatas(b"\x00\x00\x00\x18ftypheic\x00\x00\x00\x00"),
        "heic")
    chk("m_tuscia", magic_formatas(b""), None)
    chk("m_trumpa", magic_formatas(b"\xff"), None)
    chk("m_tekstas", magic_formatas(b"tekstas cia guli"), None)

    # --- klasifikuoti ---
    chk("k_neatp", klasifikuoti(None, False, 100, 100, "x.jpg"),
        "neatpazintas")
    chk("k_foto", klasifikuoti("jpeg", True, 4032, 3024, "IMG_001.jpg"),
        "foto")
    chk("k_dok", klasifikuoti("jpeg", True, 2480, 3508, "scan_sutartis.jpg"),
        "dokumentas")
    chk("k_exif_pries_raiska",
        klasifikuoti("jpeg", True, 1920, 1080, "IMG_001.jpg"), "foto")
    chk("k_skrin_raiska", klasifikuoti("png", False, 1920, 1080, "pav.png"),
        "skrinsotas")
    chk("k_skrin_apsukta", klasifikuoti("png", False, 1080, 1920, "pav.png"),
        "skrinsotas")
    chk("k_skrin_vardas",
        klasifikuoti("jpeg", False, 500, 500, "Screenshot_saugykla.jpg"),
        "skrinsotas")
    chk("k_ikona_png", klasifikuoti("png", False, 64, 64, "icon.png"),
        "ikona")
    chk("k_ikona_gif", klasifikuoti("gif", False, 200, 150, "anim.gif"),
        "ikona")
    chk("k_maza_jpeg", klasifikuoti("jpeg", False, 200, 150, "maza.jpg"),
        "foto")
    chk("k_wa_foto",
        klasifikuoti("jpeg", False, 3000, 2000, "IMG-20250114-WA0001.jpg"),
        "foto")

    if KLAIDOS:
        for k in KLAIDOS:
            print(k)
        print("PATIKRA: FAIL (%d klaidu is 45)" % len(KLAIDOS))
        sys.exit(1)
    print("PATIKRA: OK (45 patikros)")


if __name__ == "__main__":
    main()
