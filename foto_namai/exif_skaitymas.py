"""exif_skaitymas.py - EXIF skaitymas per Pillow (E2 dalis 2; PIPELINE 2c).

OKF_Pillow/OKF_piexif guard'u taisykles:
- with Image.open (lazy + handle!), getexif() naujas API;
- DateTimeOriginal - EXIF IFD viduje, formatas "YYYY:MM:DD HH:MM:SS"
  (dvitaskiai datoje!); sugadintas EXIF = kasdienybe -> try/except VISADA,
  nepavyko = krentam zemyn datos hierarchija, programa NIEKADA nekrenta;
- GPS - DMS racionalai + Ref raides;
- HEIC tik su pillow-heif; jo nera/neuzsikrauna -> graceful degradation
  (failai eina vardu/mtime hierarchija, PLANAS 4b.1);
- dekompresijos bombos (panoramos) - gaudomos bendru except.
Zero Qt. Originalu EXIF NIEKADA nerasom (v1 principas).
"""

import re
from datetime import datetime

from PIL import ExifTags, Image

try:
    from pillow_heif import register_heif_opener
    register_heif_opener()
    HEIC_VEIKIA = True
except Exception:
    HEIC_VEIKIA = False

_MAKE = 271
_MODEL = 272
_ORIENTACIJA = 274

_TUSCIA = {"exif_iso": None, "exif_kita_iso": None,
           "turi_kameros_exif": False, "kamera": None,
           "plotis": None, "aukstis": None, "orientacija": None,
           "lat": None, "lon": None, "blob": None}


_PNG_XMP_DATOS = re.compile(
    r'(?:photoshop:DateCreated|xmp:CreateDate|exif:DateTimeOriginal|'
    r'xmp:ModifyDate|tiff:DateTime)\s*(?:=\s*"|>)\s*'
    r'(\d{4})-(\d{2})-(\d{2})')


def _png_data_iso(info):
    """PNG vidiniai laukai (4e p. 6+11 verdiktas 2026-08-28): 'Creation
    Time' tEXt ir XMP paketas iTXt viduje. Tikro archyvo matavimas: ~390
    failu, del kuriu kitaip butu reikeje ExifTool priklausomybes.
    Grazina ISO arba None; rezis 1990-2035 kaip visur."""
    v = info.get("Creation Time")
    if isinstance(v, bytes):
        v = v.decode("latin1", "ignore")
    if isinstance(v, str) and v.strip():
        v = v.strip()
        # ISO/EXIF stiliai + PNG spec rekomenduojamas RFC 1123
        for pj, fmt in ((v[:19], "%Y-%m-%d %H:%M:%S"),
                        (v[:19], "%Y:%m:%d %H:%M:%S"),
                        (v[:10], "%Y-%m-%d"),
                        (v, "%d %B %Y %H:%M:%S %z"),
                        (v, "%d %B %Y %H:%M:%S"),
                        (v, "%d %b %Y %H:%M:%S")):
            try:
                dt = datetime.strptime(pj, fmt)
                if 1990 <= dt.year <= 2035:
                    return dt.replace(tzinfo=None).isoformat()
            except ValueError:
                continue
    x = info.get("XML:com.adobe.xmp")
    if isinstance(x, bytes):
        x = x.decode("utf-8", "replace")
    if isinstance(x, str):
        m = _PNG_XMP_DATOS.search(x)
        if m:
            y, mo, dy = int(m.group(1)), int(m.group(2)), int(m.group(3))
            if 1990 <= y <= 2035 and 1 <= mo <= 12 and 1 <= dy <= 31:
                return "%04d-%02d-%02dT00:00:00" % (y, mo, dy)
    return None


def _data_iso(reiksme):
    """EXIF data "YYYY:MM:DD HH:MM:SS" -> ISO arba None (siuksles atmetam)."""
    if isinstance(reiksme, bytes):
        reiksme = reiksme.decode("ascii", errors="ignore")
    if not isinstance(reiksme, str):
        return None
    try:
        return datetime.strptime(reiksme.strip(),
                                 "%Y:%m:%d %H:%M:%S").isoformat()
    except ValueError:
        return None


def _dms_i_laipsnius(dms, ref):
    """GPS DMS racionalai -> desimtainiai laipsniai su zenklu pagal Ref."""
    laipsniai = float(dms[0]) + float(dms[1]) / 60.0 + float(dms[2]) / 3600.0
    if isinstance(ref, bytes):
        ref = ref.decode("ascii", errors="ignore")
    return -laipsniai if ref in ("S", "W") else laipsniai


def skaityti(kelias):
    """Failo EXIF + matmenys vienu atidarymu. Grazina dict (zr. _TUSCIA
    raktus); bet kokia klaida -> kiek pavyko, likusi dalis None."""
    rez = dict(_TUSCIA)
    try:
        with Image.open(kelias) as img:
            rez["plotis"], rez["aukstis"] = img.size
            rez["blob"] = img.info.get("exif")
            try:
                exif = img.getexif()
                make = exif.get(_MAKE)
                model = exif.get(_MODEL)
                if make or model:
                    rez["turi_kameros_exif"] = True
                    # Kliurka 9 (gyvas ADATA testas 2026-08-13): EXIF
                    # eilutes buna su NUL uodegom ('Canon...\x00\x00') -
                    # ta pati kamera paieskoje skildavo i kelis variantus.
                    dalys = []
                    for x in (make, model):
                        if not x:
                            continue
                        if not isinstance(x, str):
                            x = x.decode("ascii", "ignore")
                        x = x.strip("\x00 \t\r\n")
                        if x:
                            dalys.append(x)
                    rez["kamera"] = " ".join(dalys) or None
                rez["orientacija"] = exif.get(_ORIENTACIJA)
                ifd = exif.get_ifd(ExifTags.IFD.Exif)
                rez["exif_iso"] = _data_iso(
                    ifd.get(ExifTags.Base.DateTimeOriginal))
                if rez["exif_iso"] is None:
                    # L0b (4e, matavimas 08-27 +4): atsargines EXIF datos,
                    # kai DateTimeOriginal nera - Digitized, tada DateTime
                    # (306, ModifyDate). Kur ideti hierarchijoje, sprendzia
                    # datos_variklis.isspresti_data (po vardo).
                    rez["exif_kita_iso"] = (
                        _data_iso(ifd.get(ExifTags.Base.DateTimeDigitized))
                        or _data_iso(exif.get(306)))
                gps = exif.get_ifd(ExifTags.IFD.GPSInfo)
                if gps and 2 in gps and 4 in gps:
                    try:
                        rez["lat"] = _dms_i_laipsnius(gps[2], gps.get(1, "N"))
                        rez["lon"] = _dms_i_laipsnius(gps[4], gps.get(3, "E"))
                    except (TypeError, ValueError, ZeroDivisionError,
                            IndexError):
                        pass
            except Exception:
                pass   # sugadintas EXIF - matmenys lieka, datos kris zemyn
            # PNG sluoksnis: kai EXIF datu nera, o failas PNG - vidiniai
            # tekstiniai laukai (ta pati exif_kita_iso vieta hierarchijoje:
            # "kiti failo VIDINIAI metaduomenys", po vardo).
            try:
                if (rez["exif_iso"] is None
                        and rez["exif_kita_iso"] is None
                        and img.format == "PNG"):
                    rez["exif_kita_iso"] = _png_data_iso(img.info)
            except Exception:
                pass
    except Exception:
        pass   # neatidaromas failas - viskas None, skambintojas zymes
    return rez
