"""models.py - bendros konstantos ir duomenu strukturos (E0 skeletas).

E1 cia atsiras FotoIrasas/Lentyna dataclass'es ir busenu zodynas is
PIPELINE.md (RASTAS -> SUINDEKSUOTAS -> SUPLANUOTAS -> SUTVARKYTAS ...).
"""

# Programos versija (rodoma "Apie..." langelyje ir buduose)
VERSIJA = "1.0"

# Juodasis sarasas (PLANAS sprendimas 8, Nextcloud incidento pamoka):
# sitie katalogai NIEKADA neskenuojami - "kopiju pasauliai" ir sisteminiai.
JUODASIS_SARASAS = {
    "#snapshot",
    "#recycle",
    "$RECYCLE.BIN",
    "System Volume Information",
    ".git",
    "node_modules",
    "AppData",
    # Android miniatiuru kesas (kliurka 7, gyvas Xiaomi testas 2026-08-13:
    # 455 kesu failu butu uztersE _NEPATIKIMOS_DATOS)
    ".thumbnails",
}

# Disko vietos sargas (sprendimas 9): zemiau sios ribos rasymo partijos
# stabdomos su graziu pranesimu, ne tylia mirtimi.
MIN_LAISVA_VIETA_MB = 500

# Indeksavimo ivercio kalibravimas (E7 matavimas 2026-08-13, saltas HDD:
# 2013 failu/7,3 GB - 129 MB/s ir ~13,7 ms/failui seek'ams; konservatyviai
# HDD, nes SSD/keso atveju (1470 MB/s) tikras laikas tik maloniai trumpesnis).
IVERTIS_MS_FAILUI = 15
IVERTIS_MB_PER_S = 130

# Medijos galuniu sarasas (sprendimas 36, Roberto verdiktas 2026-08-07):
# FOTO namai indeksuoja TIK medija - pdf/exe/zip/muzika "nieko bendro su
# paveiksliukais neturi". Apsimeteliai (.jpg su ne-vaizdo turiniu) LIEKA
# indekse kaip "neatpazinti" - sprendimo 28 spastu gaudymas nesikeicia.
MEDIJOS_GALUNES = {
    # vaizdai
    ".jpg", ".jpeg", ".jfif", ".png", ".gif", ".bmp", ".tif", ".tiff",
    ".webp", ".heic", ".heif",
    # RAW (indeksuojami pagal varda+mtime, be EXIF gylio - PLANAS 4b.1)
    ".cr2", ".cr3", ".nef", ".arw", ".dng", ".orf", ".rw2", ".raf",
    # video (seimos filmukai - pilnateisiai archyvo gyventojai)
    ".mp4", ".mov", ".avi", ".mkv", ".m4v", ".3gp", ".wmv", ".webm",
    ".mpg", ".mpeg", ".mts", ".m2ts",
}

# Failo busenu zodynas (PIPELINE.md - privalomas visiems moduliams):
# RASTAS -> SUINDEKSUOTAS -> SUPLANUOTAS -> SUTVARKYTAS; salutines -
# PRALEISTAS(priezastis), NEATPAZINTAS, ATSTATYTAS (undo), KLAIDA(priezastis).
BUSENOS = ("RASTAS", "SUINDEKSUOTAS", "SUPLANUOTAS", "SUTVARKYTAS",
           "PRALEISTAS", "NEATPAZINTAS", "ATSTATYTAS", "KLAIDA")
