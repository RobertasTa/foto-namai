"""hashai.py - turinio hash (E2).

SVARBU (sprendimas 27): NE dublikatu medziokle - tam yra Smart Duplicate
Finder! Hash tarnauja tik: (a) PERKELIMO SAUGAI - to paties turinio nekelti
i tiksla antra karta; (b) mandagiam SIULYMUI "radau ~N dublikatu - pirma
SDF (nuoroda), tada tvarkymas".
"""

import hashlib

_GABALAS = 1024 * 1024


def failo_hash(kelias):
    """Srautinis sha256 (RAM nepriklauso nuo failo dydzio).
    OSError kyla aukstyn - skambintojas zymi KLAIDA/PRALEISTA."""
    h = hashlib.sha256()
    with open(kelias, "rb") as f:
        while True:
            gabalas = f.read(_GABALAS)
            if not gabalas:
                break
            h.update(gabalas)
    return h.hexdigest()
