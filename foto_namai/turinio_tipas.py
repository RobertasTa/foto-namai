"""
turinio_tipas.py - Failo formato atpazinimas is antrastes ir deterministine
tipu klasifikacija. TIK stdlib.

E2 (PLANAS sprendimai 5, 28): magic bytes, ne galune; "duru skambucio"
klasifikacija be ML. Parase mergyte (lokalus Hermes agentas) 2026-08-07
pagal UZDUOTIS.md; patikrinta teiseju patikra_e2.py (45/45) ir Claude
perziura.
"""


EKRANAI = {
    (1920, 1080), (1366, 768), (2560, 1440), (3840, 2160),
    (1280, 720), (1536, 864), (1440, 900), (750, 1334),
    (828, 1792), (1080, 1920), (1080, 2340), (1080, 2400),
    (1170, 2532), (1440, 3200),
}


def magic_formatas(antraste):
    """Failo formatas is pirmu baitu. Grazina 'jpeg'|'png'|... arba None."""
    if not antraste or len(antraste) < 2:
        return None

    # JPEG: FF D8 FF
    if len(antraste) >= 3 and antraste[0:3] == b'\xff\xd8\xff':
        return "jpeg"

    # GIF: 'GIF87a' or 'GIF89a' (pirmieji 6 baitai prasideda 'GIF')
    if antraste[0:6] in (b'GIF87a', b'GIF89a'):
        return "gif"

    # PNG: 89 50 4E 47 0D 0A 1A 0A (8 baitai)
    if len(antraste) >= 8 and antraste[0:8] == b'\x89PNG\r\n\x1a\n':
        return "png"

    # BMP: pirmi 2 baitai 'BM'
    if antraste[0:2] == b'BM':
        return "bmp"

    # TIFF: 'II*\x00' arba 'MM\x00*' (pirmieji 4 baitai)
    if len(antraste) >= 4:
        if antraste[0:4] in (b'II*\x00', b'MM\x00*'):
            return "tiff"

    # WEBP: 'RIFF' + baituose 8..12 yra 'WEBP'
    if len(antraste) >= 12 and antraste[0:4] == b'RIFF':
        if antraste[8:12] == b'WEBP':
            return "webp"

    # HEIC: baituose 4..8 yra 'ftyp', baituose 8..12 - vienas is heic/heix/hevc/mif1/msf1/heif
    if len(antraste) >= 12 and antraste[4:8] == b'ftyp':
        brand = antraste[8:12].decode('ascii', errors='ignore').lower()
        if brand in ('heic', 'heix', 'hevc', 'mif1', 'msf1', 'heif'):
            return "heic"
        # E4 papildymas (Claude): kiti ftyp brand'ai - mp4/mov seima
        # (iPhone Live MOV = 'qt  '); tvarkomi pagal varda+mtime (4b.1)
        return "video"

    # AVI: 'RIFF' + 8..12 'AVI ' (E4 papildymas)
    if len(antraste) >= 12 and antraste[0:4] == b'RIFF' \
            and antraste[8:12] == b'AVI ':
        return "video"

    return None


def klasifikuoti(formatas, turi_kameros_exif, plotis, aukstis, vardas):
    """Deterministine tipu klasifikacija. Pirmas suveikes taisykle laimi."""
    # 1. Neatpazintas formatas
    if formatas is None:
        return "neatpazintas"

    # 1b. Video (E4 papildymas) - be EXIF gylio, datos is vardo/mtime
    if formatas == "video":
        return "video"

    # 2. Kameros EXIF - stipriausias signalas
    if turi_kameros_exif:
        if "scan" in vardas.lower():
            return "dokumentas"
        return "foto"

    vrd = vardas.lower()

    # 3. Skrinsotas: vardas prasideda 'screenshot' ARBA raiska (arba apsuukta) ekrane
    if vrd.startswith("screenshot"):
        return "skrinsotas"
    if (plotis, aukstis) in EKRANAI or (aukstis, plotis) in EKRANAI:
        return "skrinsotas"

    # 4. Ikona: tik PNG/GIF ir maza raiska
    if formatas in ("png", "gif") and max(plotis, aukstis) <= 256:
        return "ikona"

    # 5. Numatytoji: foto
    return "foto"
