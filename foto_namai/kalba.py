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
    # Vardo istorija 2026-08-13: galutinis Roberto verdiktas - programa
    # visur prisistato PHOTO home, o FOTO namai lieka skliaustuose kaip
    # gimimo vardas (LT ir EN antrastese vienodai).
    "PHOTO home (FOTO namai) - nuotrauku archyvo tvarkytojas":
        "PHOTO home (FOTO namai) - home photo archive organizer",
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
    "Pazymeta: {} {}, ~{} failu, ~{}, ~{} min":
        "Checked: {} {}, ~{} files, ~{}, ~{} min",
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
    "Zvalgyba: {} failu, {}, praleista {}":
        "Estimate: {} files, {}, skipped {}",
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
    # KLIURKA 19: buvo "Indeksuota {}: ..." ir lentynos vardas, kuris pats
    # baigiasi dvitaskiu ("DESKTOP-MAN disk D:"), duodavo "D:: 140 failu"
    "Indeksuota {} - {} failu ({} nepakite, {} neatpazinta, {} ne medija,"
    " {} praleista)":
        "Indexed {} - {} files ({} unchanged, {} unrecognised, {} non-media,"
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
    # KLIURKA 28 (Roberto gyvas demo ratas 2026-08-29): mygtukas
    # "Klausk DI" redaktoriu dialoge EN rezime rodydavo lietuviska rakta
    "Klausk DI": "Ask AI",
    # macOS saugiklis (2026-08-29): B pakopa uzrakinta iki gyvo Mac testuotojo
    "macOS beta: tvarkymas isjungtas, kol neturime gyvo Mac testuotojo"
    " - katalogas ir paieska veikia pilnai.":
        "macOS beta: organizing is disabled until we have a live Mac"
        " tester - the catalog and search work in full.",
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
    # KLIURKA 21: sena antraste ("pasirinkite NAUJA") siunte zmogu rasyti
    # varda i "Folder:" lauka, o Windows atsakydavo "Path does not exist"
    "Archyvo aplankas: pasirinkite tuscia arba sukurkite nauja dialogo"
    " mygtuku":
        "Archive folder: pick an empty one, or create a new one with the"
        " dialog's button",
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
    "Bus {} ({} failu, {}) i:\n{}\n\nVykdyti?":
        "Will {} ({} files, {}) into:\n{}\n\nProceed?",
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
    # Spr. 45 kartotekos fonas (2026-08-29)
    "Kartoteka pildosi: {}": "Catalog filling up: {}",
    "Kartoteka pasipilde: +{} miniatiuru.": "Catalog grew: +{} thumbnails.",
    "Kartotekos fonas sustojo: {}": "Catalog background stopped: {}",
    # Spr. 4d megstami redaktoriai (2026-08-29)
    "Atverti su {}": "Open with {}",
    "Atverti perziurai": "Open for viewing",
    "Prideti/keisti redaktorius...": "Add / edit editors...",
    "Redaktoriu failas: {}": "Editors file: {}",
    "Nepavyko atverti redaktoriuje: {}": "Could not open in editor: {}",
    "Megstami redaktoriai": "Favorite editors",
    "Cia galite nurodyti savo megstamas programas, kuriomis atidarysite nuotrauka desiniu klavisu (pvz. Photoshop, GIMP, Paint).\n\nPaspaudus OK atsidarys tekstinis failas. Kiekviena programa rasoma dviem eilutemis:\n\n   [Photoshop]\n   kelias = C:\\Program Files\\...\\Photoshop.exe\n\nLauztiniuose skliaustuose - pavadinimas, kuri matysite meniu. Kelia paprasciausia nukopijuoti is Explorer adreso juostos ir iklijuoti - dvigubu bruksniu NEREIKIA.\n\nIssaugokite faila (Ctrl+S) ir uzdarykite - naujos programos meniu atsiras is karto.\n\nJei neaisku - paspauskite \"Klausk DI\" ir autoriaus padejejas paaiskins.":
        "Here you can list your favorite programs for opening a photo from"
        " the right-click menu (e.g. Photoshop, GIMP, Paint).\n\n"
        "Pressing OK opens a text file. Each program takes two lines:\n\n"
        "   [Photoshop]\n"
        "   kelias = C:\\Program Files\\...\\Photoshop.exe\n\n"
        "In the square brackets goes the name you will see in the menu."
        " The easiest way is to copy the path from the Explorer address bar"
        " and paste it - no double backslashes needed.\n\n"
        "Save the file (Ctrl+S) and close it - new programs appear in the"
        " menu right away.\n\n"
        "If anything is unclear, press \"Ask AI\" and the author's assistant"
        " will explain.",
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
    " %LOCALAPPDATA%\\PhotoHome.":
        "On: the index and working files live next to the app (e.g. on a"
        " USB stick).\nOff (default): in the user folder"
        " %LOCALAPPDATA%\\PhotoHome.",
    "Nepavyko perjungti rezimo: {}": "Could not switch mode: {}",
    "Portable rezimas IJUNGTAS - duomenys salia programos.":
        "Portable mode is ON - data lives next to the app.",
    "Portable rezimas isjungtas - duomenys vartotojo kataloge.":
        "Portable mode is off - data lives in the user folder.",
    # --- KOPIJU langas (Roberto sprendimas 2026-08-23 per gyva rata:
    # "ispet ispejo, o galimybes nueiti susitvarkyti dubliu nedave").
    # Programa NESIRENKA uz zmogu - pasako, ka darys, ir duoda iseiti.
    "Yra kopiju": "There are copies",
    # Spr. 27 (2026-08-29): A1 hash nuimtas - skaicius yra dydzio
    # IVERTIS, tekstas nebemeluoja "tas pats turinys".
    "Panasu, kad ~%d failai kartojasi (vienodo dydzio, ~%s).":
        "It looks like ~%d files repeat (same size, ~%s).",
    "Skaicius - ivertis pagal vienoda failo dydi; pries keldamas i"
    " archyva turini patikrinsiu baitas i baita, tad tikras kopiju"
    " skaicius gali buti kiek mazesnis.":
        "The number is an estimate based on identical file size; before"
        " moving anything into the archive I verify the content byte for"
        " byte, so the real number of copies may be a bit smaller.",
    "Kopijomis laikau tik IDENTISKUS baitas i baita failus. Panasiu"
    " nematau: jei nuotrauka apkarpyta, patamsinta ar sumazinta (pvz."
    " persiusta per zinute), man tai atskiras failas - ir i archyva"
    " keliaus visos jos versijos. Tokias randa Smart Duplicate Finder,"
    " nes jis lygina vaizda, ne baitus.":
        "I treat only byte-for-byte IDENTICAL files as copies. Similar"
        " ones I do not see: if a photo was cropped, darkened or resized"
        " (for example sent through a messenger), to me it is a separate"
        " file - and every version of it will go into the archive. Those"
        " are found by Smart Duplicate Finder, because it compares the"
        " image, not the bytes.",
    # 4e p. 3 (2026-08-28): tekstas seka elgesi - kopija neberenkama
    # atsitiktinai, imama patikimesnes datos; senoji "pasirinksiu pati"
    # formuluote butu melavusi.
    "Jei tesi: keliausiu po viena kiekvieno turinio kopija. Kuria"
    " butent - pasirinksiu pagal patikimesne data, ir ji gali tureti"
    " kita varda ar kita aplanka nei ta, kuria butum pasirinkes tu.":
        "If you continue: I will place one copy of each content. Which"
        " one exactly - I will pick by the more reliable date, and it may"
        " have a different name or a different folder than the one you"
        " would have picked.",
    # 4e p. 2 (2026-08-28): informacinis variantas A pakopos pabaigai.
    "Patogiausias momentas kopijoms susitvarkyti - DABAR, pries kuriant"
    " namu archyva: susitvarkykite su Smart Duplicate Finder"
    " (github.com/RobertasTa/smart-duplicate-finder) ir suindeksuokite"
    " is naujo, arba tiesiog teskite - pries kuriant archyva ispesiu"
    " dar karta.":
        "The best moment to sort the copies out is NOW, before building"
        " the home archive: clean them up with Smart Duplicate Finder"
        " (github.com/RobertasTa/smart-duplicate-finder) and re-index,"
        " or simply carry on - I will warn you once more before the"
        " archive is built.",
    "Supratau": "Got it",
    "Kopiju suvestine: ~{} failai galimai kartojasi (~{}). Patarimas:"
    " pirma Smart Duplicate Finder, tada archyvo kurimas.":
        "Copies summary: ~{} files may repeat (~{}). Tip: Smart"
        " Duplicate Finder first, then build the archive.",
    "Jei nori pasirinkti pats: sustok, susitvarkyk kopijas su Smart"
    " Duplicate Finder (github.com/RobertasTa/smart-duplicate-finder)"
    " ir paleisk PHOTO home is naujo.":
        "If you want to pick yourself: stop, sort the copies out with"
        " Smart Duplicate Finder (github.com/RobertasTa/"
        "smart-duplicate-finder) and start PHOTO home again.",
    "Testi": "Continue",
    "Sustoti": "Stop",
    # --- Quick start takas pirmame ekrane (4f p. 4, 2026-08-29).
    "Pirmas kartas? Takas paprastas:": "First time? The path is simple:",
    "  1. Prijunkite telefona arba pazymekite aplanka"
    " ir spauskite Indeksuoti - siame zingsnyje"
    " programa failus tik SKAITO.":
        "  1. Connect a phone or tick a folder and press Index -"
        " in this step the program only READS your files.",
    "  2. Gausite ARCHYVO RENTGENA: kas jusu"
    " archyve, is kur datos, kiek liko be ju.":
        "  2. You will get an ARCHIVE X-RAY: what is in your archive,"
        " where the dates come from, how many are left without one.",
    "  3. Jei panorekite - namu archyvas Metai\\"
    "Menuo tvarka, o kiekvienas zingsnis su UNDO.":
        "  3. If you wish - a home archive in Year\\Month order,"
        " every step with UNDO.",
    "PAZADAS: ne vienas baitas jusu failuose"
    " nekeiciamas; tvarkymas - tik kopijos arba"
    " perkelimas su pilnu UNDO.":
        "PROMISE: not a single byte of your files is changed;"
        " organizing is only copying or moving with full UNDO.",
    # --- 4e p. 7/8 (2026-08-29): kaimynyste + mtime partijos.
    "[{}] be datos likusiems: kaimynyste +{},"
    " mtime partijos +{} - failai gavo kaimynu"
    " medianos data.":
        "[{}] for files left dateless: neighborhood +{},"
        " mtime batches +{} - files received their neighbors'"
        " median date.",
    "- Daliai failu be savo datos data priskirta is APLINKOS:"
    " vienalyciame aplanke - kaimynu mediana (`kaimynyste`),"
    " kartu atkeliavusiu failu grupeje - partijos mediana"
    " (`partija`).":
        "- Some files without a date of their own received one from"
        " their SURROUNDINGS: in a homogeneous folder - the neighbors'"
        " median (`kaimynyste`), in a group of files that arrived"
        " together - the batch median (`partija`).",
    # --- ARCHYVO RENTGENAS (4f p. 3, 2026-08-29): A pakopos veidas.
    "Archyvo rentgenas": "Archive X-ray",
    "Issaugoti ataskaita...": "Save report...",
    "Gerai": "OK",
    "Rentgeno ataskaita issaugota: {}": "X-ray report saved: {}",
    "Nepavyko issaugoti ataskaitos: {}": "Could not save the report: {}",
    "# KAS TAVO ARCHYVE - rentgeno ataskaita":
        "# WHAT IS IN YOUR ARCHIVE - X-ray report",
    "Programa: PHOTO home (FOTO namai). Nieko nekilnojau -"
    " tik perskaiciau ir suskaiciavau.":
        "Program: PHOTO home (FOTO namai). Nothing was moved -"
        " only read and counted.",
    "## Kiek ir kur": "## How much and where",
    "- Is viso indekse: **%d failu, %s**.":
        "- Total in the index: **%d files, %s**.",
    "- Lentyna `%s`: %d failu, %s.": "- Shelf `%s`: %d files, %s.",
    "- Neatpazinto turinio (0 baitu, netikri .jpg):"
    " %d - ju nejudinsiu.":
        "- Unrecognized content (0 bytes, fake .jpg):"
        " %d - I will not touch them.",
    "## Is kur tavo datos (sluoksniu derlius)":
        "## Where your dates come from (layer harvest)",
    "BE PATIKIMOS DATOS (kelias i _UNDATED): **%d (%.1f %%)**."
    " Tai ne siukslynas - tai darbo zona: failai sveiki, tik ju"
    " fotografavimo data dar neissiaiskinta.":
        "WITHOUT A RELIABLE DATE (headed for _UNDATED): **%d (%.1f %%)**."
        " This is not a junkyard - it is a work zone: the files are"
        " healthy, only their capture date is not figured out yet.",
    "## Linija laike": "## The line in time",
    "**Nuo ~%d tavo datos patikimos.** Senesni kadrai -"
    " priesistore: ten datu metaduomenys reti, ir kaip"
    " tik ten programa dirba labiausiai.":
        "**From ~%d your dates are reliable.** Older shots are"
        " prehistory: date metadata is rare there, and that is exactly"
        " where this program works hardest.",
    "Aiskios ribos, nuo kada datos patikimos, siame"
    " archyve nesimato - patikimu datu dalis svyruoja.":
        "No clear boundary of reliable dates is visible in this"
        " archive - the share of reliable dates fluctuates.",
    "| Metai | Kadru | Patikima data |":
        "| Year | Shots | Reliable date |",
    "## Ko neperziurejau (saugikliai)":
        "## What I did not look into (safety rails)",
    "Sie katalogai praleisti TYCIA (backup/kopiju"
    " pasaulis, sisteminiai, nuorodos) - jei nori juos"
    " itraukti, pridek kaip atskira saltini:":
        "These folders were skipped ON PURPOSE (backup/copy world,"
        " system folders, links) - if you want them included, add them"
        " as a separate source:",
    "- ... ir dar %d.": "- ... and %d more.",
    "Ataskaita sukurta A pakopoje (zvalgyba): ne vienas failas"
    " nepajudintas. Tvarkymas (B pakopa) - tik tavo ranka, su"
    " UNDO.":
        "This report was made in stage A (reconnaissance): not a single"
        " file was moved. Organizing (stage B) happens only by your"
        " hand, with UNDO.",
    "Sustabdyta - kopijas galite susitvarkyti su Smart Duplicate Finder.":
        "Stopped - you can sort the copies out with Smart Duplicate"
        " Finder.",
    # --- KLIURKA 16 (Roberto pastaba 2026-08-23 apie kalba failuose):
    # KAIP_SUTVARKYTA.md ir UNDO_ZURNALAS.md gule archyve VISADA
    # lietuviskai. Sie failai skirti ZMOGUI skaityti (ne programai
    # atpazinti), todel jie - vartotojo kalba. Aplanku vardai, kuriuos
    # programa turi atpazinti po metu, lieka angliski (spr. 43).
    "# KAIP SUTVARKYTA - sio archyvo taisykles":
        "# HOW THIS ARCHIVE IS SORTED - the rules",
    "Sutvarke programa **PHOTO home (FOTO namai)** (Claude's"
    " Gifts to the World).":
        "Sorted by **PHOTO home (FOTO namai)** (Claude's Gifts to the"
        " World).",
    "Atnaujinta: ": "Updated: ",
    "## Taisykles": "## Rules",
    "- Nuotraukos guli pagal data: `Metai\\Menuo` arba"
    " `Metai\\Menuo Renginys` (renginio vardas - is originalaus"
    " aplanko pavadinimo).":
        "- Photos are placed by date: `Year\\Month` or"
        " `Year\\Month Event` (the event name comes from the original"
        " folder name).",
    "- Kiekvienos nuotraukos data nustatyta sia tvarka: EXIF ->"
    " failo vardas -> aplanko vardas -> failo mtime.":
        "- Each photo's date was resolved in this order: EXIF -> file"
        " name -> folder name -> file mtime.",
    "- `%s` - ekrano nuotraukos (atpazintos be ML: nera"
    " kameros EXIF + ekrano raiska / vardas); jos irgi skirstomos"
    " pagal `Metai\\Menuo`, o be patikimos datos lieka saknyje.":
        "- `%s` - screenshots (recognised without ML: no camera EXIF +"
        " screen resolution / name); they are also filed by `Year\\Month`,"
        " and those without a trustworthy date stay in the root.",
    "- `%s` - failai, kuriu datos saltinis tik"
    " mtime (kopijavimo pedsakas, ne fotografavimo data).":
        "- `%s` - files whose only date source is mtime (a trace of"
        " copying, not the date the photo was taken).",
    "- SVARBU: `%s` yra DARBO ZONA, ne siukslynas. Failai joje"
    " sveiki ir nepaliesti - tiesiog ju datu dar neissiaiskinom."
    " Naujos programos versijos ismoksta nauju atpazinimo budu ir"
    " parusiuoja sia lentyna is vidaus (pvz. `%s\\2015\\06`) -"
    " prie siu failu dar bus griztama.":
        "- IMPORTANT: `%s` is a WORK AREA, not a junk pile. The files in"
        " it are intact and untouched - we simply have not worked out"
        " their dates yet. Newer versions of the program learn new"
        " recognition methods and sort this shelf from within (e.g."
        " `%s\\2015\\06`) - these files will be revisited.",
    "- Neatpazinto turinio failai (0 baitu, netikri .jpg) is"
    " vietos NEJUDINTI.":
        "- Files of unrecognised content (0 bytes, fake .jpg) were NOT"
        " moved.",
    "- Dublikatai (tas pats turinys) i archyva keliami TIK viena"
    " karta.":
        "- Duplicates (identical content) are placed into the archive"
        " ONLY once.",
    "## Statistika": "## Statistics",
    "- `%s` - %d failu, %s": "- `%s` - %d files, %s",
    "Is viso: **%d failu, %s**; praleista (dubliai/jau"
    " buvo): %d.":
        "In total: **%d files, %s**; skipped (duplicates/already"
        " there): %d.",
    "## Sia diena pries X metu": "## On this day, years ago",
    "Sios dienos kadru turite is: %s.":
        "You have shots from this day in: %s.",
    "Pilna atsaukimo istorija - [UNDO_ZURNALAS.md]"
    "(UNDO_ZURNALAS.md). Programoje mygtukas"
    " \"UNDO - grazinti viska atgal\" veikia bet kada.":
        "The full undo history is in [UNDO_ZURNALAS.md]"
        "(UNDO_ZURNALAS.md). The \"UNDO - put everything back\" button"
        " in the app works at any time.",
    "# UNDO zurnalas - kas is kur atkeliavo":
        "# UNDO log - what came from where",
    "| Laikas | Rezimas | Is kur | I kur |":
        "| Time | Mode | From | To |",
    "(rodoma pirmi %d irasu; pilnas sarasas -"
    " indeksas.db undo lenteleje)":
        "(showing the first %d entries; the full list is in the undo"
        " table of indeksas.db)",
    # --- TELEFONAS (v1.0 VINIS, 2026-08-28): gidas + jungimas + kopija.
    "ARBA leiskite programai padaryti tai PACIAI: atlikite"
    " 1 zingsni (laidas + \"Failu perdavimas\"), UZDARYKITE"
    " Explorer langa su telefonu (telefona vienu metu mato tik"
    " viena programa) ir spauskite \"Jungti telefona\" -"
    " programa pati suras nuotrauku vietas, nukopijuos ir"
    " prides i saltinius. Is telefono TIK skaitoma - nieko"
    " netrinam ir nerasom.":
        "OR let the app do it ITSELF: do step 1 (cable + \"File"
        " Transfer\"), CLOSE the Explorer window showing the phone"
        " (only one app can see the phone at a time) and press"
        " \"Connect the phone\" - the app will find the photo"
        " locations, copy them and add the folder to the sources."
        " The phone is READ-ONLY - nothing is deleted or written.",
    "Jungti telefona": "Connect the phone",
    "Ieskomas telefonas": "Looking for the phone",
    "Telefono klaida: {}": "Phone error: {}",
    "Rastas telefonas: {} ({} nuotrauku vietu)":
        "Phone found: {} ({} photo locations)",
    "Telefono kopija atsaukta.": "Phone copy cancelled.",
    "Kopijuojama is telefono": "Copying from the phone",
    "Telefonas baigtas: tiksle {} failu ({} praleista kaip jau turimi).":
        "Phone done: {} files in the folder ({} skipped as already"
        " there).",
    "is telefono": "from the phone",
    "Aplankas pridetas prie saltiniu - spauskite"
    " \"Indeksuoti pazymetus\".":
        "The folder was added to the sources - press \"Index"
        " selected\".",
    "Telefono nerandu": "Cannot see the phone",
    "Nepavyko pamatyti telefono nuotrauku. Dazniausios"
    " priezastys:\n\n"
    "1. Telefonas neatsake i \"USB rezimas?\" klausima -\n"
    "   pasirinkite \"Failu perdavimas\" (File Transfer)\n"
    "   TELEFONO ekrane. Numatytasis buna \"tik krovimas\".\n"
    "2. Telefona naudoja kita programa - uzdarykite Explorer\n"
    "   langa su telefonu ir bandykite dar karta (telefona\n"
    "   vienu metu mato tik viena programa).\n"
    "3. Ekranas uzrakintas - atrakinkite ir perkiskite laida.\n"
    "4. Laidas tik krovimo - pabandykite kita laida.\n"
    "5. Senas telefonas gali apsimesti CD-ROM ir siulyti\n"
    "   diegti savo programa - nediekite, tiesiog perkiskite\n"
    "   laida i kita lizda.":
        "Could not see the phone's photos. Most common reasons:\n\n"
        "1. The phone did not answer the \"USB mode?\" question -\n"
        "   choose \"File Transfer\" on the PHONE screen. The\n"
        "   default is usually \"charging only\".\n"
        "2. Another program is using the phone - close the Explorer\n"
        "   window showing the phone and try again (only one app\n"
        "   can see the phone at a time).\n"
        "3. The screen is locked - unlock it and replug the cable.\n"
        "4. The cable is charge-only - try another cable.\n"
        "5. An old phone may pretend to be a CD-ROM and offer its\n"
        "   own software - do not install it, just replug the cable\n"
        "   into another port.",
    "Klausti DI": "Ask AI",
    "Paimti is telefono": "Take from the phone",
    "Telefonas: {}": "Phone: {}",
    "Ka kopijuoti (rastos nuotrauku vietos):":
        "What to copy (photo locations found):",
    "elementu": "items",
    "I kuri aplanka kompiuteryje:": "Into which folder on the computer:",
    "Parinkti...": "Browse...",
    "Is telefono TIK skaitoma - originalai"
    " jame lieka nepaliesti.":
        "The phone is READ-ONLY - the originals on it stay untouched.",
    "Kopijuojama: {}": "Copying: {}",
    "nukopijuota {}, praleista {}": "copied {}, skipped {}",
    "baigiama... tiksle {} failu": "finishing... {} files in the folder",
    "Telefonas dingo kopijos metu: {}":
        "The phone disappeared during the copy: {}",
    "Kopija nutraukta - dalis failu jau"
    " kompiuteryje, telefonas nepaliestas.":
        "Copy cancelled - some files are already on the computer,"
        " the phone was not touched.",
    "Kopija nutruko be rezultato -"
    " patikrinkite laida ir bandykite"
    " dar karta.":
        "The copy stopped without a result - check the cable and try"
        " again.",
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
