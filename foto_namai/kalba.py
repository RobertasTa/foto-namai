"""kalba.py - GUI kalbos sluoksnis (valytuvo v1.0 sablonas, PLANAS sprendimas 22).

Lietuviskas tekstas = zodyno raktas; t() grazina vertima arba pati rakta.

Kalbos parinkimo prioritetai:
  1. FOTONAMAI_LANG aplinkos kintamasis (testu izoliacija / prievarta)
  2. kalba.txt darbiniu failu kataloge (GUI pasirinkimas; portable rezime
     keliauja su flesiuku kartu su FotoNamai_portable.txt)
  3. OS kalba: lietuviska sistema -> LT, kitaip -> EN (LANG_LITHUANIAN 0x27).
Nauja kalba ateityje = zodynas + eilute combobox'e. Zero Qt priklausomybiu.
"""
import os
from pathlib import Path


def _issaugota_kalba():
    """Skaito GUI pasirinkima is kalba.txt (saugyklos data_dir)."""
    try:
        import saugykla
        v = (saugykla.data_dir() / "kalba.txt").read_text(
            encoding="utf-8").strip().lower()
        return v if v in ("lt", "en") else None
    except OSError:
        return None


def issaugoti_kalba(lang):
    """Iraso pasirinkima i kalba.txt; isigalioja perleidus programa.
    Meta OSError, jei irasyti nepavyko (pvz., read-only vieta)."""
    import saugykla
    d = saugykla.data_dir()
    d.mkdir(parents=True, exist_ok=True)
    (d / "kalba.txt").write_text(lang + "\n", encoding="utf-8")


def _os_kalba():
    """OS kalbos aptikimas pirmam paleidimui: lietuviska sistema -> lt."""
    try:
        import ctypes
        langid = ctypes.windll.kernel32.GetUserDefaultUILanguage()
        if (langid & 0x3FF) == 0x27:   # LANG_LITHUANIAN
            return "lt"
        return "en"
    except Exception:
        pass
    try:
        import locale
        loc = locale.getlocale()[0] or ""
        return "lt" if loc.lower().startswith("lt") else "en"
    except Exception:
        return "en"


_env = os.environ.get("FOTONAMAI_LANG")
if _env in ("lt", "en"):
    LANG = _env
else:
    LANG = _issaugota_kalba() or _os_kalba()

_EN = {
    # gui_langas (E3)
    # Vardas VIENODAS abiem kalbom (E8 sprendimas 2026-08-13: PhotoHome
    # GitHub'e uzimtas svetimo projekto; prekes zenklas - FOTO namai,
    # paieskai dirba angliskas paaiskinimas salia)
    "FOTO namai": "FOTO namai",
    # EN antrasteje vardas paliekamas, bet skliaustuose isverstas
    # (Roberto 2026-08-13, trecias primygtinis: "net meska atpazins,
    # kad FOTO = photo, houm = namai") - Photo Home cia yra vertimo
    # glosa, ne produkto vardas (PhotoHome kolizija negalioja).
    "FOTO namai - nuotrauku archyvo tvarkytojas":
        "FOTO namai (Photo Home) - home photo archive organizer",
    "Saltiniai (varneles - ka skenuoti):":
        "Sources (tick what to scan):",
    "Saltinis": "Source",
    "Failai": "Files",
    "Dydis": "Size",
    "Prideti aplanka...": "Add folder...",
    "Zvalgyba (kiek failu?)": "Estimate (how many files?)",
    "Indeksuoti pazymetus": "Index checked",
    "Atsaukti": "Cancel",
    "Zurnalas:": "Log:",
    "Indeksas: {}": "Index: {}",
    "Pasirinkite nuotrauku aplanka": "Choose a photo folder",
    "Nepazymeta nieko": "Nothing is checked",
    "Pazymeta: {} {}, ~{} failu, ~{:.1f} GB, ~{} min":
        "Checked: {} {}, ~{} files, ~{:.1f} GB, ~{} min",
    "Pazymeta: {} {} - ivercio dar nera, spauskite Zvalgyba":
        "Checked: {} {} - no estimate yet, press Estimate",
    "({} be zvalgybos ivercio)": "({} without an estimate yet)",
    # zinynas_vietos.json vardai/pastabos (EN rezime irgi verciami)
    "Atsisiuntimai (Downloads)": "Downloads",
    "Paveiksleliai (Pictures)": "Pictures",
    "OneDrive Paveiksleliai": "OneDrive Pictures",
    "Phone Link kesas": "Phone Link cache",
    "kopija, ne originalai": "copies, not originals",
    "Vyksta zvalgyba": "Estimating",
    "Zvalgyba: {} failu, {:.2f} GB, praleista {}":
        "Estimate: {} files, {:.2f} GB, skipped {}",
    "Naujas diskas - lentynos vardo paklausiu pries indeksavima.":
        "New disk - I will ask for a shelf name before indexing.",
    "Vienkartine bazes migracija: sutvarkyta {} irasu":
        "One-time database migration: tidied {} entries",
    "Lentynos krikstynos": "Shelf naming",
    "Sis kompiuterio diskas gaus lentynos varda.\nGalite palikti siuloma"
    " arba irasyti sava (iki 40 zenklu).":
        "This computer drive will get its shelf name.\nKeep the suggested"
        " one or type your own (up to 40 chars).",
    "Naujas diskas! Duokite lentynai varda, kuri atpazinsite po metu "
    "(iki 40 zenklu).\nPatarimas: uzklijuokite ant disko lipduka su "
    "siuo vardu.":
        "New disk! Give this shelf a name you will recognise a year from "
        "now (up to 40 chars).\nTip: put a sticker with this name on the "
        "physical disk.",
    "Vyksta indeksavimas": "Indexing",
    "Indeksuota {}: {} failu ({} nepakite, {} neatpazinta, {} ne medija,"
    " {} praleista)":
        "Indexed {}: {} files ({} unchanged, {} unrecognised, {} non-media,"
        " {} skipped)",
    "Baigta. Is viso suindeksuota {} failu.":
        "Done. {} files indexed in total.",
    "Atsaukiama - baigiama dabartine partija...":
        "Cancelling - finishing the current batch...",
    "Klaida: {}": "Error: {}",
    # Telefono gidas (2026-08-08: Phone Link kesas be failu - isimtas;
    # Roberto gyvi testai: belaidis Explorer langas rodo ne viska)
    "Kaip paimti is telefono?": "Get photos off a phone?",
    "Kaip paimti nuotraukas is telefono:\n\n"
    "1. Atsidarykite telefona Explorer'yje:\n"
    "   - jei telefonas jau matomas Explorer sarase\n"
    "     (Windows 11 + \"Link to Windows\" rodo ji ir be\n"
    "     laido) - galite bandyti is cia; DEMESIO: sis\n"
    "     belaidis langas dazniausiai rodo NE VISKA;\n"
    "   - patikimiausia: prijunkite USB laidu. Telefonas\n"
    "     PATS PAKLAUS \"USB rezimas?\" (langelis ekrane arba\n"
    "     pranesimu juostoje, JUSU TELEFONO kalba) -\n"
    "     pasirinkite \"Failu perdavimas\" (File Transfer).\n"
    "     NE \"Nuotrauku perdavimas\" - tas rodo tik DCIM,\n"
    "     be WhatsApp. Numatytasis buna \"tik krovimas\" -\n"
    "     todel neatsakius telefonas kompiuteryje atrodo\n"
    "     TUSCIAS. Matysite viska, dideli kiekiai eis greitai.\n"
    "2. Telefone: Internal storage. Nuotraukos:\n"
    "   DCIM\\Camera; skrinsotai: Pictures\\Screenshots\n"
    "   arba DCIM\\Screenshots (Xiaomi); WhatsApp:\n"
    "   Android\\media\\com.whatsapp\\WhatsApp\\Media.\n"
    "3. Nukopijuokite aplankus i kompiuteri ar isorini\n"
    "   diska (originalai telefone lieka).\n"
    "4. Cia spauskite \"Prideti aplanka...\" ir indeksuokite.\n\n"
    "Kodel reikia kopijos? Telefonas Explorer'yje - ne\n"
    "diskas, o \"langas\" i ji (be raides): programos jo\n"
    "tiesiogiai skenuoti negali. Dar vienas kelias -\n"
    "debesis: jei naudojate Google Photos / OneDrive, jie\n"
    "nuotraukas jau atsiuncia i kompiuterio aplanka - ta\n"
    "aplanka cia ir pridekite.":
        "How to get photos off your phone:\n\n"
        "1. Open the phone in Explorer:\n"
        "   - if the phone already shows up in Explorer\n"
        "     (Windows 11 + \"Link to Windows\" shows it even\n"
        "     without a cable) - you can try from there; NOTE:\n"
        "     this wireless view usually does NOT show everything;\n"
        "   - most reliable: connect a USB cable. The phone\n"
        "     ITSELF WILL ASK \"USB mode?\" (a dialog on its\n"
        "     screen or in the notification shade, in the\n"
        "     PHONE'S language) - pick \"File Transfer\".\n"
        "     NOT \"Photo transfer\" - that shows only DCIM,\n"
        "     no WhatsApp. The default is \"charging only\" -\n"
        "     until you answer, the phone looks EMPTY on the\n"
        "     computer. Then you see everything, fast.\n"
        "2. On the phone: Internal storage. Photos:\n"
        "   DCIM\\Camera; screenshots: Pictures\\Screenshots\n"
        "   or DCIM\\Screenshots (Xiaomi); WhatsApp:\n"
        "   Android\\media\\com.whatsapp\\WhatsApp\\Media.\n"
        "3. Copy the folders to your computer or an external\n"
        "   drive (originals stay on the phone).\n"
        "4. Here press \"Add folder...\" and index.\n\n"
        "Why a copy? A phone in Explorer is not a drive but a\n"
        "\"window\" into it (no drive letter): programs cannot\n"
        "scan it directly. One more path - the cloud: if you use\n"
        "Google Photos / OneDrive, they already download photos\n"
        "into a computer folder - just add that folder here.",
    # "Klausk DI" (Roberto ideja 2026-08-08: claude.ai, ne "bet kuris";
    # pats promptas - VISADA anglu k., kodo konstanta, ne zodyno irasas)
    "Neradote atsakymo? Klauskite DI": "No answer here? Ask the AI",
    "Kas ivyks paspaudus OK:\n\n"
    "1. Atsidarys interneto narsykle su DI padejejo\n"
    "   claude.ai puslapiu. Zinutes laukelyje jau bus\n"
    "   irasyta angliska pradzia - prisistatymas, kas per\n"
    "   programa ir kur jos kodas.\n"
    "2. NEISSIGASKITE raudono pranesimo virs zinutes -\n"
    "   claude.ai ji rodo visada, kai tekstas ateina per\n"
    "   nuoroda. Tai tik priminimas perskaityti, kas\n"
    "   siunciama.\n"
    "3. Zinutes gale, po zodziu \"My question:\", irasykite\n"
    "   SAVO klausima - galima lietuviskai! - ir spauskite\n"
    "   siuntimo mygtuka (rodykle). Klausti galima visko,\n"
    "   pvz.: \"kaip atsinaujinti programa i naujesne\n"
    "   versija? paaiskink zingsnis po zingsnio\".\n"
    "4. Jei DI atsakys angliskai - tiesiog paprasykite kita\n"
    "   zinute: \"atsakyk lietuviskai\", ir toliau bendraus\n"
    "   lietuviskai.\n\n"
    "Pastaba: claude.ai gali paprasyti prisijungti (nemokama\n"
    "paskyra). Niekas neissiunciama be jusu rankos.":
        "What happens after you press OK:\n\n"
        "1. Your web browser opens the claude.ai AI assistant.\n"
        "   The message box will already contain a prepared\n"
        "   opening - what the program is and where its code is.\n"
        "2. DO NOT be alarmed by the red notice above the\n"
        "   message - claude.ai always shows it when text\n"
        "   arrives via a link. It is just a reminder to read\n"
        "   what you are sending.\n"
        "3. At the end of the message, after \"My question:\",\n"
        "   TYPE YOUR question - any language works! - and\n"
        "   press the send button (the arrow). Ask anything,\n"
        "   e.g.: \"how do I update the app to the newest\n"
        "   version? explain it step by step\".\n"
        "4. If the AI answers in the wrong language - just ask\n"
        "   in the next message, e.g. \"answer in English\".\n\n"
        "Note: claude.ai may ask you to sign in (a free account).\n"
        "Nothing is sent without your hand.",
    # "?" pagalbos kampelis (sprendimas 37)
    "Pagalba": "Help",
    "Apie...": "About...",
    "Instrukcija": "Manual",
    "Apie programa": "About",
    "Nuotrauku savartyno tvarkytojas - nieko netrina, viskas su UNDO.":
        "Photo dump organizer - deletes nothing, everything has UNDO.",
    "Versija {v}": "Version {v}",
    "Kurejo puslapis:": "Author page:",
    "Nepavyko atidaryti: {}": "Could not open: {}",
    # E4 - namu archyvas
    "Namu archyvas (tvarkymas + UNDO):": "Home archive (organizing + UNDO):",
    "Kurti namu archyva...": "Build home archive...",
    "UNDO - grazinti viska atgal": "UNDO - put everything back",
    "Pasirinkite NAUJA/tuscia archyvo aplanka":
        "Choose a NEW/empty archive folder",
    "Aplankas netuscias": "Folder is not empty",
    "Namas statomas tusciame sklype - aplanke jau yra failu.\nTesti vis"
    " tiek? (Esami failai NEBUS liesti; sutampantis turinys bus"
    " praleistas.)":
        "The home is built on an empty plot - this folder already has"
        " files.\nContinue anyway? (Existing files will NOT be touched;"
        " identical content will be skipped.)",
    "Ruosiami pasiulymai": "Preparing proposals",
    "Nera ka tvarkyti - pirma suindeksuokite saltinius.":
        "Nothing to organize - index your sources first.",
    "Namu archyvo pasiulymas": "Home archive proposal",
    "Programa siulo tokia tvarka. Nuimkite varnele nuo grupiu, kuriu"
    " dabar nekelti:":
        "The app proposes this layout. Untick groups you do not want to"
        " move now:",
    "Grupe (aplankas archyve)": "Group (folder in the archive)",
    "Perkelti vietoj kopijuoti (originalai isnyks is saltiniu)":
        "Move instead of copy (originals will disappear from sources)",
    "Tvarkymas atsauktas pasiulymu lange.":
        "Organizing cancelled in the proposal window.",
    "Nepasirinkta ne viena grupe.": "No groups selected.",
    "Perziura (niekas dar nevykdoma)": "Preview (nothing is done yet)",
    "Bus {} ({} failu, {:.2f} GB) i:\n{}\n\nVykdyti?":
        "Will {} ({} files, {:.2f} GB) into:\n{}\n\nProceed?",
    "PERKELIAMA": "MOVE", "KOPIJUOJAMA": "COPY",
    "Tvarkymas atsauktas perziuroje.": "Organizing cancelled at preview.",
    "Vyksta tvarkymas": "Organizing",
    "Tvarkymas baigtas: {} sutvarkyta, {} dubliu praleista, {} jau buvo,"
    " {} klaidu.":
        "Organizing finished: {} placed, {} duplicates skipped, {} already"
        " there, {} errors.",
    "UNDO": "UNDO",
    "Grazinti VISKA atgal pagal UNDO zurnala?\nKopijos bus istrintos is"
    " archyvo, perkelti failai gris i vietas.":
        "Put EVERYTHING back according to the UNDO journal?\nCopies will"
        " be removed from the archive, moved files will return.",
    "Vyksta atstatymas": "Restoring",
    "UNDO baigtas: {} atstatyta, {} klaidu.":
        "UNDO finished: {} restored, {} errors.",
    # E5 - paieskos skirtukas
    "Tvarkymas": "Organize",
    "Paieska": "Search",
    "nuo YYYY-MM-DD": "from YYYY-MM-DD",
    "iki YYYY-MM-DD": "to YYYY-MM-DD",
    "Visi tipai": "All types",
    "Foto": "Photos",
    "Skrinsotai": "Screenshots",
    "Video": "Videos",
    "Ikonos": "Icons",
    "Dokumentai": "Documents",
    "Neatpazinti": "Unrecognised",
    "Visos lentynos": "All shelves",
    "Etikete (pvz. Jonines)": "Event label (e.g. Wedding)",
    "Kamera (pvz. Canon)": "Camera (e.g. Canon)",
    "Failo vardas": "File name",
    "Ieskoti": "Search",
    "- Issaugotos paieskos -": "- Saved searches -",
    "Issaugoti paieska...": "Save search...",
    "Issaugoti paieska": "Save search",
    "Trinti vaizda": "Delete saved search",
    "Duokite siai paieskai varda:": "Name this search:",
    "Paieska '{}' issaugota.": "Search '{}' saved.",
    "Vaizdas '{}' istrintas.": "Saved search '{}' deleted.",
    "Tuscios paieskos nesaugome - ivedkite bent viena filtra.":
        "An empty search cannot be saved - set at least one filter.",
    "Rasta: {} (rodoma {})": "Found: {} (showing {})",
    "Paieska: rasta {} irasu.": "Search: {} records found.",
    "Vyksta paieska": "Searching",
    "Ruosiamos miniatiuros": "Building thumbnails",
    "Miniatiuros paruostos ({}).": "Thumbnails ready ({}).",
    "Lentyna": "Shelf",
    # Lentynu sarasas is statuso mygtuko (Roberto zvilgsnis 2026-08-13)
    "Lentynos": "Shelves",
    "Spustelekite - lentynu sarasas": "Click for the shelf list",
    "Prijungta": "Connected",
    "Paskutini karta matyta": "Last seen",
    "Failu": "Files",
    "Taip": "Yes",
    "Ne": "No",
    "Uzdaryti": "Close",
    "Indekso dar nera - pirma suindeksuokite saltinius.":
        "No index yet - index your sources first.",
    "Neteisinga data '{}' - reikia YYYY-MM-DD":
        "Invalid date '{}' - use YYYY-MM-DD",
    "Lentyna '{}' siuo metu neprijungta - prijunkite diska ir"
    " pakartokite.":
        "Shelf '{}' is not connected right now - plug the disk in and"
        " try again.",
    "Failas nerastas: {}": "File not found: {}",
    "Atverti perziurykleje": "Open in viewer",
    "Parodyti Explorer'yje": "Reveal in Explorer",
    "Kopijuoti kelia": "Copy path",
    "Kelias nukopijuotas.": "Path copied.",
    "Dvigubas klikas - parodyti faila Explorer'yje. Perziurai naudokite"
    " megstama perziurykle.":
        "Double-click - reveal the file in Explorer. Use your favourite"
        " viewer for browsing.",
    "Sveiki sugrize! Indekse - {} {} ({} {}), paieska veikia is karto.":
        "Welcome back! The index holds {} {} ({} {}), search works"
        " right away.",
    # Zvilgsnio Nr. 2 pataisos (Roberto verdiktai 2026-08-07)
    "{} diskas {}": "{} disk {}",
    "Saltinis praleistas - krikstynos atsauktos.":
        "Source skipped - naming was cancelled.",
    "Indekse: {} {}, {} {}": "Index: {} {}, {} {}",
    "Indeksas tuscias": "Index is empty",
    # E5 - seimos DNR (kalba + portable)
    "Kalba": "Language",
    "Nepavyko issaugoti: {}": "Could not save: {}",
    "Kalba issaugota. Perleisti programa dabar?":
        "Language saved. Restart the program now?",
    "Kalba pritaikoma paleidus programa is naujo.":
        "The language is applied after the program restarts.",
    "Portable rezimas": "Portable mode",
    "Portable rezimas (viskas salia programos)":
        "Portable mode (everything next to the app)",
    "Ijungta: indeksas ir darbiniai failai saugomi salia programos"
    " (pvz., flesiuke).\nIsjungta (numatyta): vartotojo kataloge"
    " %LOCALAPPDATA%\\FotoNamai.":
        "On: the index and working files live next to the app (e.g. on a"
        " USB stick).\nOff (default): in the user folder"
        " %LOCALAPPDATA%\\FotoNamai.",
    "Nepavyko perjungti rezimo: {}": "Could not switch mode: {}",
    "Portable rezimas IJUNGTAS - duomenys salia programos.":
        "Portable mode is ON - data lives next to the app.",
    "Portable rezimas isjungtas - duomenys vartotojo kataloge.":
        "Portable mode is off - data lives in the user folder.",
}


def t(raktas):
    """Vertimas: LT rezime grazina rakta, EN - vertima (arba rakta, jei nera)."""
    if LANG == "en":
        return _EN.get(raktas, raktas)
    return raktas


# (vns, keli 2-9, daug 10-20/0, EN vns, EN dgs)
_KIEKIAI = {
    "saltinis": ("saltinis", "saltiniai", "saltiniu", "source", "sources"),
    "failas": ("failas", "failai", "failu", "file", "files"),
    "lentyna": ("lentyna", "lentynos", "lentynu", "shelf", "shelves"),
}


def kiekio_zodis(n, raktas):
    """Zodis pagal skaiciu (valytuvo '1 runs' gramatikos pamoka,
    Roberto radinys 2026-08-07 ir FOTO namuose)."""
    vns, keli, daug, en1, enn = _KIEKIAI[raktas]
    if LANG == "en":
        return en1 if n == 1 else enn
    if n % 10 == 1 and n % 100 != 11:
        return vns
    if n % 10 != 0 and not 11 <= n % 100 <= 19:
        return keli
    return daug


def saltinio_zodis(n):
    return kiekio_zodis(n, "saltinis")
