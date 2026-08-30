"""models.py - bendros konstantos ir duomenu strukturos (E0 skeletas).

E1 cia atsiras FotoIrasas/Lentyna dataclass'es ir busenu zodynas is
PIPELINE.md (RASTAS -> SUINDEKSUOTAS -> SUPLANUOTAS -> SUTVARKYTAS ...).
"""

# Programos versija (rodoma "Apie..." langelyje ir buduose)
VERSIJA = "1.1"

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

# Specialiu archyvo aplanku vardai. ANGLISKI VISOMS KALBOMS - Roberto
# sprendimas 2026-08-23 (gyvas GUI ratas: "cia pavadinimai lietuviski, nors
# programa angliskai paleista"). Priezastis, kodel NE pagal GUI kalba:
# aplanko vardas gyvena DISKE, ne ekrane - persijungus kalba archyve
# atsirastu DU aplankai (_SKRINSOTAI ir _SCREENSHOTS) ir nuotraukos
# pasidalintu. Vardas privalo buti vienas ir fiksuotas visam archyvo
# gyvenimui. Lietuviska kilme lieka repo varde ir GUI antrasteje.
# NEKEISTI po pirmo isleidimo - vardai lieka zmoniu diskuose.
GRUPE_SKRINSOTAI = "_SCREENSHOTS"
GRUPE_NEPATIKIMOS = "_UNDATED"

# Lentynos vardo riba (sprendimas 30). TA PATI reiksme gyvena ir indekso
# schemoje: CHECK (length(vardas_zmogui) <= 40). Krikstynu laukas nuo
# 2026-08-23 (kliurka 12) su sia riba fiziskai neleidzia ivesti daugiau -
# anksciau tyliai nukirpdavo.
LENTYNOS_VARDO_RIBA = 40

# Indeksavimo ivercio kalibravimas (E7 matavimas 2026-08-13, saltas HDD:
# 2013 failu/7,3 GB - 129 MB/s ir ~13,7 ms/failui seek'ams; konservatyviai
# HDD, nes SSD/keso atveju (1470 MB/s) tikras laikas tik maloniai trumpesnis).
IVERTIS_MS_FAILUI = 15
IVERTIS_MB_PER_S = 130


def dydis_tekstu(baitai):
    """Baitai -> zmogui skaitomas dydis (KLIURKA 18, Roberto laptopo ratas
    2026-08-25): 140 failu rodydavo "0.00 GB" - sazininga, bet atrodo kaip
    nulis arba gedimas. Receptas jau gyveno kopiju lange, tik nebuvo
    pritaikytas kitur; dabar VIENA vieta visiems (GUI + ataskaita).
    Vienetai nera verciami - "MB"/"GB" vienodi visomis kalbomis."""
    if baitai >= 1073741824:
        return "%.2f GB" % (baitai / 1073741824.0)
    if baitai >= 1048576:
        return "%.0f MB" % (baitai / 1048576.0)
    return "%.0f KB" % (baitai / 1024.0)

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
