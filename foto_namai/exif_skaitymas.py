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

_TUSCIA = {"exif_iso": None, "turi_kameros_exif": False, "kamera": None,
           "plotis": None, "aukstis": None, "orientacija": None,
           "lat": None, "lon": None, "blob": None}


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
                rez["exif_iso"] = _data_iso(
                    exif.get_ifd(ExifTags.IFD.Exif).get(
                        ExifTags.Base.DateTimeOriginal))
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
    except Exception:
        pass   # neatidaromas failas - viskas None, skambintojas zymes
    return rez
