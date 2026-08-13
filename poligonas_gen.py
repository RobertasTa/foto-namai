# poligonas_gen.py - FOTO namai sintetinis testu poligonas (Claude, 2026-08-06).
# Generuoja dirbtini foto savartyna su ZINOMAIS teisingais atsakymais -
# konkurentu testams ir busimo variklio patikroms.
#
# Struktura -> _poligonas\SAVARTYNAS (chaosas) + TIESA.md (kas kur turi atsidurti).
# LEISTI: <dubliu venv python> -u poligonas_gen.py

import os
import random
import shutil
import sys
import time
from datetime import datetime
from pathlib import Path

import piexif
from PIL import Image, ImageDraw

CIA = Path(__file__).resolve().parent
POLIGONAS = CIA / "_poligonas"
DUMP = POLIGONAS / "SAVARTYNAS"

random.seed(20260806)   # atkartojamumas

if POLIGONAS.exists():
    shutil.rmtree(POLIGONAS)
DUMP.mkdir(parents=True)

TIESA = []   # (failas, laukiama_data, saltinis)

def foto(spalva, tekstas, dydis=(640, 480)):
    img = Image.new("RGB", dydis, spalva)
    d = ImageDraw.Draw(img)
    d.text((20, 20), tekstas, fill="white")
    return img

def su_exif(kelias, img, data_str, mtime=None):
    """JPG su EXIF DateTimeOriginal; mtime - atskirai (gali konfliktuoti)."""
    exif = piexif.dump({"Exif": {
        piexif.ExifIFD.DateTimeOriginal: data_str.encode()}})
    kelias.parent.mkdir(parents=True, exist_ok=True)
    img.save(str(kelias), "JPEG", exif=exif, quality=88)
    if mtime is not None:
        os.utime(kelias, (mtime, mtime))

def be_exif(kelias, img, mtime, fmt="JPEG"):
    kelias.parent.mkdir(parents=True, exist_ok=True)
    img.save(str(kelias), fmt)
    os.utime(kelias, (mtime, mtime))

def ts(y, m, d, h=12):
    return time.mktime((y, m, d, h, 0, 0, 0, 0, -1))

# --- 1. Normalus fotoaparato JPG su EXIF (30 vnt, 2019-2025) -----------------
for i in range(30):
    y = random.choice([2019, 2020, 2021, 2022, 2023, 2024, 2025])
    m = random.randint(1, 12)
    d = random.randint(1, 28)
    img = foto((random.randint(30, 200), random.randint(30, 200), 120),
               f"IMG {y}-{m:02d}-{d:02d} #{i}")
    p = DUMP / f"DSC_{4000+i}.JPG"
    su_exif(p, img, f"{y}:{m:02d}:{d:02d} 14:3{i % 10}:00",
            mtime=ts(2026, 8, 1))   # mtime SVIEZIAS (kopijuota) - EXIF turi laimeti
    TIESA.append((p.name, f"{y}-{m:02d}", "EXIF DateTimeOriginal"))

# --- 2. WhatsApp stilius: BE EXIF, data VARDE (12 vnt) -----------------------
for i in range(12):
    y = random.choice([2023, 2024, 2025])
    m = random.randint(1, 12)
    d = random.randint(1, 28)
    img = foto((20, 120, 60), f"WA {y}{m:02d}{d:02d}")
    p = DUMP / f"IMG-{y}{m:02d}{d:02d}-WA{i:04d}.jpg"
    be_exif(p, img, ts(2026, 7, 30))   # mtime melagingas - vardas turi laimeti
    TIESA.append((p.name, f"{y}-{m:02d}", "vardas (WhatsApp)"))

# --- 3. Screenshot stilius: PNG be EXIF, data varde (8 vnt) ------------------
for i in range(8):
    y, m, d = 2025, random.randint(1, 12), random.randint(1, 28)
    img = foto((60, 60, 60), f"Screenshot {y}-{m:02d}-{d:02d}")
    p = DUMP / f"Screenshot_{y}{m:02d}{d:02d}-10{i:02d}33.png"
    be_exif(p, img, ts(2026, 7, 30), fmt="PNG")
    TIESA.append((p.name, f"{y}-{m:02d}", "vardas (Screenshot)"))

# --- 4. Be EXIF ir be datos varde: tik mtime (6 vnt) -------------------------
for i in range(6):
    y, m = random.choice([(2021, 3), (2022, 7), (2024, 11)]), 0
    y, m = y[0], y[1]
    img = foto((150, 90, 30), f"mtime only #{i}")
    p = DUMP / f"nuotrauka ({i}).jpg"
    be_exif(p, img, ts(y, m, 15))
    TIESA.append((p.name, f"{y}-{m:02d}", "mtime (nieko kito nera)"))

# --- 5. DUBLIKATAI: tas pats turinys skirtingose vietose (4 poros) -----------
for i in range(4):
    img = foto((200, 40, 40), f"DUBLIS {i}")
    orig = DUMP / f"DSC_9{i:03d}.JPG"
    su_exif(orig, img, f"2024:06:1{i} 09:00:00", mtime=ts(2026, 8, 1))
    kopija = DUMP / "Senas telefonas" / f"DSC_9{i:03d} - Copy.JPG"
    kopija.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(orig, kopija)
    TIESA.append((orig.name, "2024-06", "EXIF; turi DUBLIKATA Senas telefonas\\"))
    TIESA.append(("Senas telefonas\\" + kopija.name, "2024-06", "DUBLIKATAS (nekopijuoti antra karta)"))

# --- 6. Spastai: sugadintas EXIF, 0 baitu, ne-nuotrauka ----------------------
blogas = DUMP / "IMG_broken.jpg"
img = foto((90, 0, 90), "broken exif")
img.save(str(blogas), "JPEG", exif=b"Exif\x00\x00SUGADINTA")
os.utime(blogas, (ts(2023, 9, 9), ts(2023, 9, 9)))
TIESA.append((blogas.name, "2023-09", "sugadintas EXIF -> mtime atsarga"))

(DUMP / "tuscias.jpg").write_bytes(b"")
TIESA.append(("tuscias.jpg", "-", "0 baitu - praleisti, nekristi"))

netikra = DUMP / "ne_nuotrauka.jpg"
netikra.write_text("cia tekstas, ne JPEG", encoding="utf-8")
os.utime(netikra, (ts(2022, 2, 2), ts(2022, 2, 2)))
TIESA.append((netikra.name, "2022-02", "ne-JPEG turinys .jpg varde - nekristi"))

# --- TIESA.md ----------------------------------------------------------------
eil = ["# Poligono TIESA - kur kas TURI atsidurti (Metai-Menuo)\n"]
for vardas, data, saltinis in sorted(TIESA):
    eil.append(f"- `{vardas}` -> **{data}** ({saltinis})")
eil.append(f"\nViso failu: {len(TIESA)} (su dublikatais).")
eil.append("Sugeneruota poligonas_gen.py 2026-08-06; random.seed(20260806).")
(POLIGONAS / "TIESA.md").write_text("\n".join(eil), encoding="utf-8")

n = sum(1 for _ in DUMP.rglob("*") if _.is_file())
print(f"[BAIGTA] {DUMP} - {n} failu; TIESA.md - {len(TIESA)} irasu")
