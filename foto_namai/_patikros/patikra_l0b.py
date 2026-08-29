# patikra_l0b.py - EXIF atsargines datos (4e L0b) + sporthealth skirtukas.
#
# Matavimas 2026-08-27: dump'e +4 failai turejo TIK DateTime (ModifyDate,
# CozyMag) ir +3 sporthealth varda su '-' skirtuku. Sprendimai (Claude,
# Roberto delegavimu 08-28): atsargines EXIF datos eina PO vardo su
# saltiniu "exif_kita" (ModifyDate gali buti taisymo data - stiprus
# vardas laimi); sablonas 4 priima [_-] skirtuka.
# Sintetiniai failai su piexif - tikras exif_skaitymas kelias, ne mock'ai.
# LEISTI is foto_namai: <venv python> -u _patikros\patikra_l0b.py

import sys
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import piexif                    # noqa: E402
from PIL import Image            # noqa: E402

import exif_skaitymas            # noqa: E402
from datos_variklis import data_is_vardo, isspresti_data   # noqa: E402

KLAIDOS = []


def chk(pavadinimas, salyga, detale=""):
    if salyga:
        print("  OK   %s" % pavadinimas)
    else:
        KLAIDOS.append(pavadinimas)
        print("  FAIL %s %s" % (pavadinimas, detale))


def _foto(kelias, exif_dict):
    img = Image.new("RGB", (32, 24), (120, 90, 60))
    img.save(kelias, "JPEG", exif=piexif.dump(exif_dict))


print("== L0b: EXIF atsargines datos ==")
with tempfile.TemporaryDirectory() as tmp:
    tmp = Path(tmp)

    # 1. Tik ModifyDate (0th DateTime) - CozyMag atvejis
    f1 = tmp / "cozy.jpg"
    _foto(f1, {"0th": {piexif.ImageIFD.DateTime: b"2017:12:26 17:27:57"}})
    ex = exif_skaitymas.skaityti(f1)
    chk("modifydate_perskaityta",
        ex["exif_iso"] is None
        and ex["exif_kita_iso"] == "2017-12-26T17:27:57", ex)

    # 2. Tik DateTimeDigitized - laimi pries ModifyDate
    f2 = tmp / "digi.jpg"
    _foto(f2, {"0th": {piexif.ImageIFD.DateTime: b"2020:01:01 00:00:00"},
               "Exif": {piexif.ExifIFD.DateTimeDigitized:
                        b"2015:06:24 18:30:00"}})
    ex = exif_skaitymas.skaityti(f2)
    chk("digitized_pirmiau", ex["exif_kita_iso"] == "2015-06-24T18:30:00", ex)

    # 3. Yra DateTimeOriginal - atsargines NESKAITOMOS (kaina 0 tvarkingiems)
    f3 = tmp / "orig.jpg"
    _foto(f3, {"0th": {piexif.ImageIFD.DateTime: b"2020:01:01 00:00:00"},
               "Exif": {piexif.ExifIFD.DateTimeOriginal:
                        b"2019:03-05 10:00:00".replace(b"-", b":")}})
    ex = exif_skaitymas.skaityti(f3)
    chk("original_uztenka",
        ex["exif_iso"] == "2019-03-05T10:00:00"
        and ex["exif_kita_iso"] is None, ex)

print("== PNG vidiniai laukai (4e p. 6+11 verdiktas: vietoj ExifTool) ==")
from PIL.PngImagePlugin import PngInfo   # noqa: E402

with tempfile.TemporaryDirectory() as tmp:
    tmp = Path(tmp)

    def _png(vardas, raktas, reiksme, itxt=False):
        img = Image.new("RGB", (16, 16), (10, 20, 30))
        info = PngInfo()
        if itxt:
            info.add_itxt(raktas, reiksme)
        else:
            info.add_text(raktas, reiksme)
        kelias = tmp / vardas
        img.save(kelias, "PNG", pnginfo=info)
        return exif_skaitymas.skaityti(kelias)

    ex = _png("iso.png", "Creation Time", "2006-09-14 13:35:45")
    chk("png_creation_time_iso",
        ex["exif_kita_iso"] == "2006-09-14T13:35:45", ex)

    ex = _png("rfc.png", "Creation Time", "14 September 2006 13:35:45")
    chk("png_creation_time_rfc",
        ex["exif_kita_iso"] == "2006-09-14T13:35:45", ex)

    ex = _png("xmp.png", "XML:com.adobe.xmp",
              '<x:xmpmeta><rdf:Description xmp:CreateDate='
              '"2009-08-28T10:00:00"/></x:xmpmeta>', itxt=True)
    chk("png_xmp_createdate",
        ex["exif_kita_iso"] == "2009-08-28T00:00:00", ex)

    ex = _png("uz_rezio.png", "Creation Time", "1901-01-01 00:00:00")
    chk("png_rezis_atmeta", ex["exif_kita_iso"] is None, ex)

    ex = _png("siuksles.png", "Creation Time", "vakar vakare")
    chk("png_siuksles_none", ex["exif_kita_iso"] is None, ex)

print("== Hierarchija: exif -> vardas -> exif_kita -> aplankas -> mtime ==")
chk("kita_gelbeja",
    isspresti_data(None, "CM171226-172757001.jpg", "Aplankas",
                   "2026-08-13T00:00:00",
                   exif_kita_iso="2017-12-26T17:27:57")
    == ("2017-12-26T17:27:57", "exif_kita", True))
chk("vardas_laimi_pries_kita",
    isspresti_data(None, "IMG-20230318-WA0006.jpg", "Aplankas",
                   "2026-08-13T00:00:00",
                   exif_kita_iso="2017-12-26T17:27:57")
    == ("2023-03-18", "vardas", True))
chk("orig_laimi_pries_viska",
    isspresti_data("2019-03-05T10:00:00", "IMG-20230318-WA0006.jpg",
                   "Aplankas", "x", exif_kita_iso="2017-12-26T17:27:57")
    == ("2019-03-05T10:00:00", "exif", True))
chk("be_kita_senas_kelias",
    isspresti_data(None, "bevardis.jpg", "Aplankas 2015",
                   "2026-08-13T00:00:00")[1] == "aplankas")

print("== Sporthealth [_-] skirtukas (matavimas +3) ==")
chk("sporthealth_bruksnys",
    data_is_vardo("sporthealth-1-20201015-060701.jpg")
    == "2020-10-15T06:07:01")
chk("senas_pabraukimas_veikia",
    data_is_vardo("20150612_130000.jpg") == "2015-06-12T13:00:00")
chk("whatsapp_nepakito",
    data_is_vardo("IMG-20230318-WA0006.jpg") == "2023-03-18")

if KLAIDOS:
    print("PATIKRA RAUDONA: %d klaidos" % len(KLAIDOS))
    sys.exit(1)
print("PATIKRA ZALIA (15/15)")
