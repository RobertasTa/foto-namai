"""
datos_variklis.py - Data ekstrakcija is failo vardu, aplanku ir hierarchinio
prioritetu sprendimas. TIK stdlib (re, calendar, datetime).

E2 (PLANAS sprendimas 3): hierarchija EXIF -> failo vardas -> aplanko
vardas -> mtime SU ZYMA "nepatikima"; rezultatas visada su datos_saltinis.
Parase mergyte (lokalus Hermes agentas) 2026-08-07 pagal UZDUOTIS.md;
patikrinta teiseju patikra_e2.py (45/45) ir Claude perziura.
"""

import re
import calendar


def _validate_date(year, month, day):
    """Patikrina, ar data galioja: metai 1990-2035, menesis 1-12, diena tikra."""
    if not (1990 <= year <= 2035):
        return False
    if not (1 <= month <= 12):
        return False
    max_day = calendar.monthrange(year, month)[1]
    return 1 <= day <= max_day


def _validate_time(hour, minute, second):
    """Patikrina, ar laikas galioja."""
    return 0 <= hour < 24 and 0 <= minute < 60 and 0 <= second < 60


def _format_iso(year, month, day):
    """Sudaro 'YYYY-MM-DD' tekstas."""
    return "%04d-%02d-%02d" % (year, month, day)


def data_is_vardo(vardas):
    # 1. WhatsApp: IMG-YYYYMMDD-WA... / VID-YYYYMMDD-WA... -> tik data
    m = re.search(r'(?:IMG|VID)-(\d{8})-WA', vardas)
    if m:
        d = m.group(1)
        y, mo, dy = int(d[0:4]), int(d[4:6]), int(d[6:8])
        if _validate_date(y, mo, dy):
            return _format_iso(y, mo, dy)

    # 2. Skrinsotai: Screenshot_YYYYMMDD-HHMMSS / Screenshot_YYYYMMDD_HHMMSS
    m = re.search(r'Screenshot_(\d{8})[_-](\d{6})', vardas)
    if m:
        d, t = m.group(1), m.group(2)
        y, mo, dy = int(d[0:4]), int(d[4:6]), int(d[6:8])
        h, mi, s = int(t[0:2]), int(t[2:4]), int(t[4:6])
        if _validate_date(y, mo, dy):
            if _validate_time(h, mi, s):
                return "%sT%02d:%02d:%02d" % (_format_iso(y, mo, dy), h, mi, s)
            else:
                return _format_iso(y, mo, dy)

    # 3. Google Pixel: PXL_YYYYMMDD_HHMMSS... (palei sekundes gali buti daugiau skaitmenu)
    m = re.search(r'PXL_(\d{8})_(\d{6})', vardas)
    if m:
        d, t = m.group(1), m.group(2)
        y, mo, dy = int(d[0:4]), int(d[4:6]), int(d[6:8])
        h, mi, s = int(t[0:2]), int(t[2:4]), int(t[4:6])
        if _validate_date(y, mo, dy):
            if _validate_time(h, mi, s):
                return "%sT%02d:%02d:%02d" % (_format_iso(y, mo, dy), h, mi, s)
            else:
                return _format_iso(y, mo, dy)

    # 4. Bendras: YYYYMMDD_HHMMSS bet kur varde
    m = re.search(r'(\d{4})(\d{2})(\d{2})_(\d{2})(\d{2})(\d{2})', vardas)
    if m:
        y, mo, dy = int(m.group(1)), int(m.group(2)), int(m.group(3))
        h, mi, s = int(m.group(4)), int(m.group(5)), int(m.group(6))
        if _validate_date(y, mo, dy):
            if _validate_time(h, mi, s):
                return "%sT%02d:%02d:%02d" % (_format_iso(y, mo, dy), h, mi, s)
            else:
                return _format_iso(y, mo, dy)

    # 5. Bendras: YYYY-MM-DD bet kur varde
    m = re.search(r'(\d{4})-(\d{2})-(\d{2})', vardas)
    if m:
        y, mo, dy = int(m.group(1)), int(m.group(2)), int(m.group(3))
        if _validate_date(y, mo, dy):
            return _format_iso(y, mo, dy)

    return None


def data_is_aplanko(aplanko_kelias):
    """Data is teviniu aplanku. Grazina (metai, menesis|None, etikete|None) arba None."""
    # Skaidyk kelius abipusiais brusniais
    parts = aplanko_kelias.replace('\\', '/').split('/')
    parts = [p for p in parts if p]

    # Nuo giliausio auksto.link saknies
    for i in range(len(parts) - 1, -1, -1):
        seg = parts[i].strip()

        # SPECIALIS atvejis: grynas menesis 01-12, teginis segmentas - gryni metai
        pure_month_m = re.match(r'^0*(\d{1,2})$', seg)
        if pure_month_m:
            mval = int(pure_month_m.group(1))
            if 1 <= mval <= 12 and i > 0:
                parent_seg = parts[i - 1].strip()
                ym = re.match(r'^(\d{4})$', parent_seg)
                if ym:
                    year = int(ym.group(1))
                    if 1990 <= year <= 2035:
                        return (year, mval, None)

        # (a) Ieskoti YYYY-MM pora
        ymm_m = re.search(r'\b(\d{4})-(\d{2})\b', seg)
        if ymm_m:
            year, month = int(ymm_m.group(1)), int(ymm_m.group(2))
            if 1990 <= year <= 2035 and 1 <= month <= 12:
                label = seg.replace(ymm_m.group(0), '', 1).strip()
                return (year, month, label or None)

        # (b) Iskirti atskira 4 skaitmenu metu tokena
        year_m = re.search(r'\b([12]\d{3})\b', seg)
        if year_m:
            year = int(year_m.group(1))
            if 1990 <= year <= 2035:
                label = seg.replace(year_m.group(1), '', 1).strip()
                return (year, None, label or None)

    return None


def isspresti_data(exif_iso, failo_vardas, aplanko_kelias, mtime_iso):
    """
    Hierarchinis datos sprendimas: EXIF -> vardas -> aplankas -> mtime.
    Grazina (datetaken_iso, saltinis, patikima).
    """
    # 1. EXIF
    if exif_iso is not None:
        return (exif_iso, "exif", True)

    # 2. Failo vardas
    vard_result = data_is_vardo(failo_vardas)
    if vard_result is not None:
        return (vard_result, "vardas", True)

    # 3. Aplankas
    apl_result = data_is_aplanko(aplanko_kelias)
    if apl_result is not None:
        year, month, _label = apl_result
        if month is not None:
            iso = "%04d-%02d-01" % (year, month)
        else:
            iso = "%04d-01-01" % year
        return (iso, "aplankas", True)

    # 4. mtime kaip paskutinis resiorus
    return (mtime_iso, "mtime", False)
