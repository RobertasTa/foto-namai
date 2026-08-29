"""miniaturos.py - tingus miniatiuru kesas (E5; PLANAS sprendimas 14).

Miniatiuros generuojamos TIK rodomiems failams (ne visai bibliotekai) ir
kesuojamos data_dir()/miniatiuros - antra karta tik grazinamas kelias.

OKF_Pillow foto guard'o taisykles, kuriu LAIKOMES:
- with Image.open (lazy + handle, masiniame darbe kitaip "Too many open files");
- JPEG draft("RGB", dydis) PRIES load - dekoduoja sumazinta, keliskart greiciau;
- ImageOps.exif_transpose PRIES thumbnail - telefonu gulscios nuotraukos;
- thumbnail() laiko proporcijas pats (resize - ne);
- P/RGBA/LA i JPEG nesirasys - convert("RGB") pries save;
- dekompresijos bombos (panoramos) / sugadinti failai / ne vaizdai -
  bendras except -> None, programa NIEKADA nekrenta.
Zero Qt - GUI worker'is si moduli tik apvynios gija.
"""

import hashlib
from pathlib import Path

from PIL import Image, ImageOps

import exif_skaitymas  # noqa: F401  (salutinis efektas: pillow-heif registracija)
import saugykla

DYDIS = 256   # kvadrato krastine px; 192->256 2026-08-29 (spr. 45
              # kartoteka: pamatuota ant 300 tikru foto - 6,8 KB/vnt,
              # atpazinimas akimi + HiDPI nusvere; senas 192 failu kesas
              # tiesiog regeneruosis, nes DYDIS yra keso rakte)


def keso_katalogas():
    return saugykla.data_dir() / "miniatiuros"


def _keso_kelias(kelias, mtime):
    """Keso raktas is kelio + mtime + dydzio: pasikeites failas -> nauja
    miniatiura, senoji lieka kaip slamstas (valymas - v1.x TODO)."""
    raktas = hashlib.sha1(
        ("%s|%d|%d" % (str(kelias).lower(), int(mtime), DYDIS))
        .encode("utf-8", "replace")).hexdigest()
    return keso_katalogas() / (raktas + ".jpg")


def miniatiura(kelias, mtime):
    """Grazina miniatiuros JPEG kelia (Path) arba None (video / sugadintas /
    ne vaizdas / HEIC be pillow-heif). Saugu kviesti bet kokiam failui."""
    kk = _keso_kelias(kelias, mtime)
    if kk.exists():
        return kk
    try:
        with Image.open(kelias) as img:
            if img.format == "JPEG":
                img.draft("RGB", (DYDIS, DYDIS))
            img = ImageOps.exif_transpose(img)
            img.thumbnail((DYDIS, DYDIS))
            if img.mode not in ("RGB", "L"):
                img = img.convert("RGB")
            kk.parent.mkdir(parents=True, exist_ok=True)
            img.save(kk, "JPEG", quality=80)
        return kk
    except Exception:
        return None
