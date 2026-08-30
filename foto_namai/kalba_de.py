# -*- coding: utf-8 -*-
"""PHOTO home GUI tekstai vokieciu kalba (raktas = lietuviskas tekstas).

Vertimai: mergyte (lokalus Qwen), 2026-08-30, porcijomis po 40.
Patikra: _darbal/vertimai_mergyte_2026-08-30/_patikros/patikra_vertimai.py
Perziurejo: Claude.
"""

_DE = {
    'PHOTO home (FOTO namai) - nuotrauku archyvo tvarkytojas':
        'PHOTO home (FOTO namai) – Ihr Fotoarchiv-Organisator',
    'Saltiniai (varneles - ka skenuoti):':
        'Quellen (Haken setzen – was gescannt werden soll):',
    'Saltinis':
        'Quelle',
    'Failai':
        'Dateien',
    'Dydis':
        'Größe',
    'Prideti aplanka...':
        'Ordner hinzufügen...',
    'Zvalgyba (kiek failu?)':
        'Schätzung (wie viele Dateien?)',
    'Indeksuoti pazymetus':
        'Markierte indexieren',
    'Atsaukti':
        'Abbrechen',
    'Zurnalas:':
        'Protokoll:',
    'Indeksas: {}':
        'Index: {}',
    'Pasirinkite nuotrauku aplanka':
        'Fotoordner auswählen',
    'Nepazymeta nieko':
        'Nichts ist markiert',
    'Pazymeta: {} {}, ~{} failu, ~{}, ~{} min':
        'Markiert: {} {}, ~{} Dateien, ~{}, ~{} Min.',
    'Pazymeta: {} {} - ivercio dar nera, spauskite Zvalgyba':
        'Markiert: {} {} – noch keine Schätzung, bitte «Schätzung» drücken',
    '({} be zvalgybos ivercio)':
        '({} noch ohne Schätzung)',
    'Atsisiuntimai (Downloads)':
        'Downloads',
    'Paveiksleliai (Pictures)':
        'Pictures',
    'OneDrive Paveiksleliai':
        'OneDrive Pictures',
    'Phone Link kesas':
        'Zwischenspeicher von Phone Link',
    'kopija, ne originalai':
        'Kopien, keine Originale',
    'Vyksta zvalgyba':
        'Schätzung läuft',
    'Zvalgyba: {} failu, {}, praleista {}':
        'Schätzung: {} Dateien, {}, {} übersprungen',
    'Naujas diskas - lentynos vardo paklausiu pries indeksavima.':
        'Neue Festplatte – ich frage vor dem Indexieren nach einem Regalnamen.',
    'Vienkartine bazes migracija: sutvarkyta {} irasu':
        'Einmalige Datenbank-Migration: {} Einträge aufgeräumt',
    'Lentynos krikstynos':
        'Regal benennen',
    'Sis kompiuterio diskas gaus lentynos varda.\nGalite palikti siuloma arba irasyti sava (iki 40 zenklu).':
        'Die Festplatte dieses Computers bekommt ihren Regalnamen.\nSie können den Namen beibehalten oder selbst einen eingeben (max. 40 Zeichen).',
    'Naujas diskas! Duokite lentynai varda, kuri atpazinsite po metu (iki 40 zenklu).\nPatarimas: uzklijuokite ant disko lipduka su siuo vardu.':
        'Neue Festplatte! Geben Sie diesem Regal einen Namen, den Sie auch nach einer Weile noch wiedererkennen (max. 40 Zeichen).\nTipp: Kleben Sie auf die physische Festplatte einen Aufkleber mit diesem Namen.',
    'Vyksta indeksavimas':
        'Indexierung läuft',
    'Indeksuota {} - {} failu ({} nepakite, {} neatpazinta, {} ne medija, {} praleista)':
        'Indexiert: {} – {} Dateien ({} unverändert, {} nicht erkannt, {} keine Medien, {} übersprungen)',
    'Baigta. Is viso suindeksuota {} failu.':
        'Fertig. Insgesamt {} Dateien indexiert.',
    'Atsaukiama - baigiama dabartine partija...':
        'Wird abgebrochen – die laufende Charge wird beendet...',
    'Klaida: {}':
        'Fehler: {}',
    'Kaip paimti is telefono?':
        'Fotos vom Smartphone holen?',
    'Kaip paimti nuotraukas is telefono:\n\n1. Atsidarykite telefona Explorer\'yje:\n   - jei telefonas jau matomas Explorer sarase\n     (Windows 11 + "Link to Windows" rodo ji ir be\n     laido) - galite bandyti is cia; DEMESIO: sis\n     belaidis langas dazniausiai rodo NE VISKA;\n   - patikimiausia: prijunkite USB laidu. Telefonas\n     PATS PAKLAUS "USB rezimas?" (langelis ekrane arba\n     pranesimu juostoje, JUSU TELEFONO kalba) -\n     pasirinkite "Failu perdavimas" (File Transfer).\n     NE "Nuotrauku perdavimas" - tas rodo tik DCIM,\n     be WhatsApp. Numatytasis buna "tik krovimas" -\n     todel neatsakius telefonas kompiuteryje atrodo\n     TUSCIAS. Matysite viska, dideli kiekiai eis greitai.\n2. Telefone: Internal storage. Nuotraukos:\n   DCIM\\Camera; skrinsotai: Pictures\\Screenshots\n   arba DCIM\\Screenshots (Xiaomi); WhatsApp:\n   Android\\media\\com.whatsapp\\WhatsApp\\Media.\n3. Nukopijuokite aplankus i kompiuteri ar isorini\n   diska (originalai telefone lieka).\n4. Cia spauskite "Prideti aplanka..." ir indeksuokite.\n\nKodel reikia kopijos? Telefonas Explorer\'yje - ne\ndiskas, o "langas" i ji (be raides): programos jo\ntiesiogiai skenuoti negali. Dar vienas kelias -\ndebesis: jei naudojate Google Photos / OneDrive, jie\nnuotraukas jau atsiuncia i kompiuterio aplanka - ta\naplanka cia ir pridekite.':
        'So holen Sie Fotos vom Smartphone:\n\n1. Öffnen Sie das Smartphone im Explorer:\n   – Wenn es im Explorer schon erscheint\n     (Windows 11 + «Link to Windows» zeigt es sogar\n     ohne Kabel) – können Sie es dort\n     versuchen; ACHTUNG: diese Drahtlossicht zeigt\n     meist NICHT ALLES;\n   – Am zuverlässigsten: USB-Kabel anschließen.\n     Das Smartphone WIRD SELBST FRAGEN «USB-Modus?»\n     (Dialog auf dem Display oder in der\n     Benachrichtigungsleiste, in der Sprache\n     IHRES Smartphones) – bitte wählen Sie\n     «Dateitransfer» (File Transfer).\n     NICHT «Fototransfer» – dort erscheinen nur\n     DCIM, kein WhatsApp. Standardmäßig ist «Nur\n     Laden» eingestellt – deshalb wirkt das Smartphone\n     im COMPUTER LEER, bis Sie antworten. Danach ist\n     alles sichtbar, große Mengen laufen schnell.\n2. Am Smartphone: Interner Speicher.\n   Fotos: DCIM\\Camera; Screenshots:\n   Pictures\\Screenshots oder DCIM\\Screenshots\n   (Xiaomi); WhatsApp:\n   Android\\media\\com.whatsapp\\WhatsApp\\Media.\n3. Kopieren Sie die Ordner auf den Computer oder die\n   externe Festplatte (die Originale bleiben auf dem\n   Smartphone).\n4. Hier bitte «Ordner hinzufügen...» klicken und\n   indexieren.\n\nWarum eine Kopie? Das Smartphone im Explorer ist\nkeine Festplatte, sondern ein «Fenster» dazu (ohne\nLaufwerksbuchstabe): Programme können es nicht\ndirekt scannen. Ein weiterer Weg – die Cloud: Bei\nVerwendung von Google Photos / OneDrive werden Fotos\nbereits in einen Ordner auf dem Computer\nheruntergeladen – diesen Ordner bitte hier hinzufügen.',
    'Neradote atsakymo? Klauskite DI':
        'Keine Antwort gefunden? Fragen Sie die KI',
    'Klausk DI':
        'KI fragen',
    'macOS beta: tvarkymas isjungtas, kol neturime gyvo Mac testuotojo - katalogas ir paieska veikia pilnai.':
        'macOS-Beta: die Sortierung ist deaktiviert, bis wir einen echten Mac-Tester haben – Katalog und Suche funktionieren vollständig.',
    'Kas ivyks paspaudus OK:\n\n1. Atsidarys interneto narsykle su DI padejejo\n   claude.ai puslapiu. Zinutes laukelyje jau bus\n   irasyta angliska pradzia - prisistatymas, kas per\n   programa ir kur jos kodas.\n2. NEISSIGASKITE raudono pranesimo virs zinutes -\n   claude.ai ji rodo visada, kai tekstas ateina per\n   nuoroda. Tai tik priminimas perskaityti, kas\n   siunciama.\n3. Zinutes gale, po zodziu "My question:", irasykite\n   SAVO klausima - galima lietuviskai! - ir spauskite\n   siuntimo mygtuka (rodykle). Klausti galima visko,\n   pvz.: "kaip atsinaujinti programa i naujesne\n   versija? paaiskink zingsnis po zingsnio".\n4. Jei DI atsakys angliskai - tiesiog paprasykite kita\n   zinute: "atsakyk lietuviskai", ir toliau bendraus\n   lietuviskai.\n\nPastaba: claude.ai gali paprasyti prisijungti (nemokama\npaskyra). Niekas neissiunciama be jusu rankos.':
        'Was nach dem Drücken von OK passiert:\n\n1. Es öffnet sich der Browser mit der KI-Hilfe der\n   Seite claude.ai. Im Nachrichtenfeld steht bereits die\n   vorbereitete Anrede – Vorstellung, um welche App es\n   sich handelt und wo ihr Quellcode liegt.\n2. ERSCHRECKEN Sie nicht über die rote Mitteilung über\n   dem Nachrichtenfeld – claude.ai zeigt sie immer, wenn\n   Text über einen Link ankommt. Das ist nur eine\n   Erinnerung, zu lesen, was gesendet wird.\n3. Am Ende der Nachricht, nach dem Text «My question:»,\n   schreiben Sie IHRE Frage – auf jeder Sprache! – und\n   drücken Sie die Absenden-Taste (Pfeil). Fragen Sie\n   alles, z. B.: «Wie aktualisiere ich die App auf die\n   neueste Version? Bitte schrittweise erklären».\n4. Falls die KI in der falschen Sprache antwortet –\n   schreiben Sie einfach in der nächsten Nachricht\n   «Auf Deutsch antworten», dann läuft das Gespräch\n   auf Deutsch weiter.\n\nHinweis: claude.ai kann zur Anmeldung auffordern\n(kostenloses Konto). Ohne Ihr Zutun wird nichts\nabgesendet.',
    'Pagalba':
        'Hilfe',
    'Apie...':
        'Info...',
    'Instrukcija':
        'Bedienungsanleitung',
    'Apie programa':
        'Über die App',
    'Nuotrauku savartyno tvarkytojas - nieko netrina, viskas su UNDO.':
        'Organisator für Ihre Fotosammlung – löscht nichts, alles mit UNDO.',
    'Versija {v}':
        'Version {v}',
    'Kurejo puslapis:':
        'Seiten des Autors:',
    'Nepavyko atidaryti: {}':
        'Konnte nicht geöffnet werden: {}',
    'Namu archyvas (tvarkymas + UNDO):':
        'Heimarchiv (Sortierung + UNDO):',
    'Kurti namu archyva...':
        'Heimarchiv anlegen...',
    'UNDO - grazinti viska atgal':
        'UNDO – alles zurücksetzen',
    'Archyvo aplankas: pasirinkite tuscia arba sukurkite nauja dialogo mygtuku':
        'Archivordner: einen leeren wählen oder mit der Schaltfläche im Dialog neu anlegen',
    'Aplankas netuscias':
        'Ordner ist nicht leer',
    'Namas statomas tusciame sklype - aplanke jau yra failu.\nTesti vis tiek? (Esami failai NEBUS liesti; sutampantis turinys bus praleistas.)':
        'Das Haus wird auf einem leeren Grundstück gebaut – dieser Ordner ist bereits gefüllt.\nTrotzdem fortfahren? (Vorhandene Dateien werden NICHT berührt; identische Inhalte werden übersprungen.)',
    'Ruosiami pasiulymai':
        'Vorschläge werden vorbereitet',
    'Nera ka tvarkyti - pirma suindeksuokite saltinius.':
        'Nichts zum Sortieren – bitte zuerst die Quellen indexieren.',
    'Namu archyvo pasiulymas':
        'Vorschlag fürs Heimarchiv',
    'Programa siulo tokia tvarka. Nuimkite varnele nuo grupiu, kuriu dabar nekelti:':
        'Die App schlägt diese Zuordnung vor. Entfernen Sie die Haken bei den Gruppen, die Sie jetzt nicht verschieben möchten:',
    'Grupe (aplankas archyve)':
        'Gruppe (Ordner im Archiv)',
    'Perkelti vietoj kopijuoti (originalai isnyks is saltiniu)':
        'Verschieben statt Kopieren (die Originale verschwinden dann aus den Quellen)',
    'Tvarkymas atsauktas pasiulymu lange.':
        'Sortierung im Vorschlagsdialog abgebrochen.',
    'Nepasirinkta ne viena grupe.':
        'Keine Gruppe gewählt.',
    'Perziura (niekas dar nevykdoma)':
        'Vorschau (noch nichts ausgeführt)',
    'Bus {} ({} failu, {}) i:\n{}\n\nVykdyti?':
        'Wird {} ({} Dateien, {}) verschoben nach:\n{}\n\nFortsetzen?',
    'PERKELIAMA':
        'WIRD VERSCHOBEN',
    'KOPIJUOJAMA':
        'WIRD KOPIERT',
    'Tvarkymas atsauktas perziuroje.':
        'Sortierung in der Vorschau abgebrochen.',
    'Vyksta tvarkymas':
        'Sortierung läuft',
    'Tvarkymas baigtas: {} sutvarkyta, {} dubliu praleista, {} jau buvo, {} klaidu.':
        'Sortierung fertig: {} einsortiert, {} Duplikate übersprungen, {} bereits vorhanden, {} Fehler.',
    'UNDO':
        'UNDO',
    'Grazinti VISKA atgal pagal UNDO zurnala?\nKopijos bus istrintos is archyvo, perkelti failai gris i vietas.':
        'WIRKLICH ALLES zurücksetzen, gem. dem UNDO-Protokoll?\nDie Kopien werden aus dem Archiv entfernt, die verschobenen Dateien kommen zurück.',
    'Vyksta atstatymas':
        'Wiederherstellung läuft',
    'UNDO baigtas: {} atstatyta, {} klaidu.':
        'UNDO beendet: {} wiederhergestellt, {} Fehler.',
    'Tvarkymas':
        'Sortierung',
    'Paieska':
        'Suche',
    'nuo YYYY-MM-DD':
        'von YYYY-MM-DD',
    'iki YYYY-MM-DD':
        'bis YYYY-MM-DD',
    'Visi tipai':
        'Alle Typen',
    'Foto':
        'Fotos',
    'Skrinsotai':
        'Screenshots',
    'Video':
        'Video',
    'Ikonos':
        'Symbole',
    'Dokumentai':
        'Dokumente',
    'Neatpazinti':
        'Nicht erkannt',
    'Visos lentynos':
        'Alle Regale',
    'Etikete (pvz. Jonines)':
        'Anlass-Label (z. B. Hochzeit)',
    'Kamera (pvz. Canon)':
        'Kamera (z. B. Canon)',
    'Failo vardas':
        'Dateiname',
    'Ieskoti':
        'Suchen',
    '- Issaugotos paieskos -':
        '- Gespeicherte Suchen -',
    'Issaugoti paieska...':
        'Suche speichern...',
    'Issaugoti paieska':
        'Suche speichern',
    'Trinti vaizda':
        'Gespeicherte Suche löschen',
    'Duokite siai paieskai varda:':
        'Name für diese Suche:',
    "Paieska '{}' issaugota.":
        'Suche „{}“ gespeichert.',
    "Vaizdas '{}' istrintas.":
        'Gespeicherte Suche „{}“ gelöscht.',
    'Tuscios paieskos nesaugome - ivedkite bent viena filtra.':
        'Leere Suchen können nicht gespeichert werden – bitte mindestens einen Filter setzen.',
    'Rasta: {} (rodoma {})':
        'Gefunden: {} (angezeigt: {})',
    'Paieska: rasta {} irasu.':
        'Suche: {} Einträge gefunden.',
    'Vyksta paieska':
        'Suche läuft',
    'Ruosiamos miniatiuros':
        'Miniaturansichten werden erstellt',
    'Miniatiuros paruostos ({}).':
        'Miniaturansichten bereit ({}).',
    'Kartoteka pildosi: {}':
        'Der Katalog füllt sich: {}',
    'Kartoteka pasipilde: +{} miniatiuru.':
        'Katalog aufgebaut: +{} Miniaturansichten.',
    'Kartotekos fonas sustojo: {}':
        'Hintergrund-Aufbau des Katalogs gestoppt: {}',
    'Atverti su {}':
        'Öffnen mit {}',
    'Atverti perziurai':
        'Zum Ansehen öffnen',
    'Prideti/keisti redaktorius...':
        'Bearbeiter hinzufügen/ändern...',
    'Redaktoriu failas: {}':
        'Datei der Bearbeiter: {}',
    'Nepavyko atverti redaktoriuje: {}':
        'Konnte im Editor nicht geöffnet werden: {}',
    'Megstami redaktoriai':
        'Bevorzugte Bearbeiter',
    'Cia galite nurodyti savo megstamas programas, kuriomis atidarysite nuotrauka desiniu klavisu (pvz. Photoshop, GIMP, Paint).\n\nPaspaudus OK atsidarys tekstinis failas. Kiekviena programa rasoma dviem eilutemis:\n\n   [Photoshop]\n   kelias = C:\\Program Files\\...\\Photoshop.exe\n\nLauztiniuose skliaustuose - pavadinimas, kuri matysite meniu. Kelia paprasciausia nukopijuoti is Explorer adreso juostos ir iklijuoti - dvigubu bruksniu NEREIKIA.\n\nIssaugokite faila (Ctrl+S) ir uzdarykite - naujos programos meniu atsiras is karto.\n\nJei neaisku - paspauskite "Klausk DI" ir autoriaus padejejas paaiskins.':
        'Hier können Sie Ihre Lieblingsprogramme auflisten, mit denen Sie per Rechtsklick ein Foto öffnen (z. B. Photoshop, GIMP, Paint).\n\nNach OK wird eine Textdatei geöffnet. Jedes Programm benötigt zwei Zeilen:\n\n   [Photoshop]\n   kelias = C:\\Program Files\\...\\Photoshop.exe\n\nIn den eckigen Klammern der Name, den Sie im Menü sehen. Den Pfad am einfachsten aus der Adressleiste des Explorer kopieren und einfügen – doppelte Backslashes sind NICHT nötig.\n\nDie Datei speichern (Strg+S) und schließen – die neuen Programme erscheinen dann sofort im Menü.\n\nWenn etwas unklar ist – bitte «KI fragen» drücken, der Assistent des Autors erklärt es.',
    'Lentyna':
        'Regal',
    'Lentynos':
        'Regale',
    'Spustelekite - lentynu sarasas':
        'Klick – Liste der Regale',
    'Prijungta':
        'Verbunden',
    'Paskutini karta matyta':
        'Zuletzt gesehen',
    'Failu':
        'Dateien',
    'Taip':
        'Ja',
    'Ne':
        'Nein',
    'Uzdaryti':
        'Schließen',
    'Indekso dar nera - pirma suindeksuokite saltinius.':
        'Noch kein Index – bitte zuerst die Quellen indexieren.',
    "Neteisinga data '{}' - reikia YYYY-MM-DD":
        'Ungültiges Datum „{}“ – bitte das Format YYYY-MM-DD verwenden',
    "Lentyna '{}' siuo metu neprijungta - prijunkite diska ir pakartokite.":
        'Das Regal „{}“ ist gerade nicht verbunden – bitte die Festplatte anschließen und noch einmal versuchen.',
    'Failas nerastas: {}':
        'Datei nicht gefunden: {}',
    'Atverti perziurykleje':
        'Im Bildbetrachter öffnen',
    "Parodyti Explorer'yje":
        'Im Explorer anzeigen',
    'Kopijuoti kelia':
        'Pfad kopieren',
    'Kelias nukopijuotas.':
        'Pfad kopiert.',
    "Dvigubas klikas - parodyti faila Explorer'yje. Perziurai naudokite megstama perziurykle.":
        'Doppelklick – die Datei im Explorer anzeigen. Zum Ansehen Ihren Lieblingsbetrachter verwenden.',
    'Sveiki sugrize! Indekse - {} {} ({} {}), paieska veikia is karto.':
        'Willkommen zurück! Im Index: {} {} ({} {}), die Suche funktioniert sofort.',
    '{} diskas {}':
        '{} Laufwerk {}',
    'Saltinis praleistas - krikstynos atsauktos.':
        'Quelle übersprungen – die Benennung wurde abgebrochen.',
    'Indekse: {} {}, {} {}':
        'Index: {} {}, {} {}',
    'Indeksas tuscias':
        'Der Index ist leer',
    'Kalba':
        'Sprache',
    'Nepavyko issaugoti: {}':
        'Speichern fehlgeschlagen: {}',
    'Kalba issaugota. Perleisti programa dabar?':
        'Sprache gespeichert. Jetzt neu starten?',
    'Kalba pritaikoma paleidus programa is naujo.':
        'Die Sprache wird wirksam, wenn die App neu gestartet wird.',
    'Portable rezimas':
        'Portable-Modus',
    'Portable rezimas (viskas salia programos)':
        'Portable-Modus (alles neben der App)',
    'Ijungta: indeksas ir darbiniai failai saugomi salia programos (pvz., flesiuke).\nIsjungta (numatyta): vartotojo kataloge %LOCALAPPDATA%\\PhotoHome.':
        'An: Index- und Arbeitsdateien liegen neben der App (z. B. auf einem USB-Stick).\nAus (Standard): im Benutzerordner %LOCALAPPDATA%\\PhotoHome.',
    'Nepavyko perjungti rezimo: {}':
        'Moduswechsel fehlgeschlagen: {}',
    'Portable rezimas IJUNGTAS - duomenys salia programos.':
        'PORTABLE-MODUS AKTIV – die Daten liegen neben der App.',
    'Portable rezimas isjungtas - duomenys vartotojo kataloge.':
        'Portable-Modus deaktiviert – die Daten liegen im Benutzerordner.',
    'Yra kopiju':
        'Es gibt Kopien',
    'Panasu, kad ~%d failai kartojasi (vienodo dydzio, ~%s).':
        'Es sieht so aus, als ob ~%d Dateien doppelt vorkommen (gleiche Größe, ~%s).',
    'Skaicius - ivertis pagal vienoda failo dydi; pries keldamas i archyva turini patikrinsiu baitas i baita, tad tikras kopiju skaicius gali buti kiek mazesnis.':
        'Die Zahl ist eine Schätzung nach der Dateigröße; vor dem Verschieben in das Archiv wird der Inhalt Byte für Byte geprüft – die echte Anzahl der Kopien kann etwas kleiner sein.',
    'Kopijomis laikau tik IDENTISKUS baitas i baita failus. Panasiu nematau: jei nuotrauka apkarpyta, patamsinta ar sumazinta (pvz. persiusta per zinute), man tai atskiras failas - ir i archyva keliaus visos jos versijos. Tokias randa Smart Duplicate Finder, nes jis lygina vaizda, ne baitus.':
        'Als Kopien zähle ich nur bytefürbyte IDENTISCHE Dateien. Ähnliche erkenne ich nicht: Wenn ein Foto beschnitten, abgedunkelt oder verkleinert wurde (z. B. über einen Messenger gesendet), ist es für mich eine eigene Datei – und all ihre Versionen wandern in das Archiv. So etwas findet Smart Duplicate Finder, denn er vergleicht das Bild, nicht die Bytes.',
    'Jei tesi: keliausiu po viena kiekvieno turinio kopija. Kuria butent - pasirinksiu pagal patikimesne data, ir ji gali tureti kita varda ar kita aplanka nei ta, kuria butum pasirinkes tu.':
        'Wenn Sie fortfahren: von jedem Inhalt wandert genau eine Kopie in das Archiv. Welche genau, wird nach dem zuverlässigeren Datum entschieden – sie kann einen anderen Namen oder einen anderen Ordner haben als die, die Sie selbst gewählt hätten.',
    'Patogiausias momentas kopijoms susitvarkyti - DABAR, pries kuriant namu archyva: susitvarkykite su Smart Duplicate Finder (github.com/RobertasTa/smart-duplicate-finder) ir suindeksuokite is naujo, arba tiesiog teskite - pries kuriant archyva ispesiu dar karta.':
        'Der beste Moment, sich um die Kopien zu kümmern, ist JETZT, vor dem Aufbau des Heimarchivs: Aufräumen mit Smart Duplicate Finder (github.com/RobertasTa/smart-duplicate-finder) und neu indexieren – oder einfach weitermachen, bevor das Archiv gebaut wird, warne ich noch einmal.',
    'Supratau':
        'Verstanden',
    'Kopiju suvestine: ~{} failai galimai kartojasi (~{}). Patarimas: pirma Smart Duplicate Finder, tada archyvo kurimas.':
        'Zusammenfassung der Kopien: ~{} Dateien kommen möglicherweise doppelt vor (~{}). Tipp: zuerst Smart Duplicate Finder, dann das Archiv aufbauen.',
    'Jei nori pasirinkti pats: sustok, susitvarkyk kopijas su Smart Duplicate Finder (github.com/RobertasTa/smart-duplicate-finder) ir paleisk PHOTO home is naujo.':
        'Wenn Sie es sich selbst auswählen möchten: stoppen, die Kopien mit Smart Duplicate Finder aufräumen (github.com/RobertasTa/smart-duplicate-finder) und PHOTO home neu starten.',
    'Testi':
        'Weiter',
    'Sustoti':
        'Anhalten',
    'Pirmas kartas? Takas paprastas:':
        'Zum ersten Mal? Der Weg ist einfach:',
    '  1. Prijunkite telefona arba pazymekite aplanka ir spauskite Indeksuoti - siame zingsnyje programa failus tik SKAITO.':
        '1. Smartphone verbinden oder Ordner markieren und «Indexieren» – in diesem Schritt LIEST die App die Dateien nur.',
    '  2. Gausite ARCHYVO RENTGENA: kas jusu archyve, is kur datos, kiek liko be ju.':
        '2. Sie erhalten die ARCHIV-RÖNTGENAUFNAHME: was in Ihrem Archiv ist, woher die Daten stammen, wie viele ohne Datum bleiben.',
    '  3. Jei panorekite - namu archyvas Metai\\Menuo tvarka, o kiekvienas zingsnis su UNDO.':
        '3. Wenn gewünscht – ein Heimarchiv in der Struktur Jahr\\Monat, jeder Schritt mit UNDO.',
    'PAZADAS: ne vienas baitas jusu failuose nekeiciamas; tvarkymas - tik kopijos arba perkelimas su pilnu UNDO.':
        'VERSICHERUNG: kein einziges Byte Ihrer Dateien wird verändert; die Sortierung erfolgt nur durch Kopieren oder Verschieben, vollständig mit UNDO.',
    '[{}] be datos likusiems: kaimynyste +{}, mtime partijos +{} - failai gavo kaimynu medianos data.':
        '[{}] ohne Datum geblieben: Nachbarschaft +{}, Charge nach mtime +{} – die Dateien haben das Median-Datum ihrer Nachbarn erhalten.',
    '- Daliai failu be savo datos data priskirta is APLINKOS: vienalyciame aplanke - kaimynu mediana (`kaimynyste`), kartu atkeliavusiu failu grupeje - partijos mediana (`partija`).':
        '- Einige Dateien ohne eigenes Datum haben eines aus der UMGEBUNG erhalten: in einem homogenen Ordner – das Median der Nachbarn (`kaimynyste`), in einer Gruppe von Dateien, die zusammen angekommen sind – das Median der Charge (`partija`).',
    'Archyvo rentgenas':
        'Archiv-Röntgen',
    'Issaugoti ataskaita...':
        'Bericht speichern...',
    'Gerai':
        'OK',
    'Rentgeno ataskaita issaugota: {}':
        'Röntgenbericht gespeichert: {}',
    'Nepavyko issaugoti ataskaitos: {}':
        'Der Bericht konnte nicht gespeichert werden: {}',
    '# KAS TAVO ARCHYVE - rentgeno ataskaita':
        '# WAS IN IHREM ARCHIV IST – Röntgenbericht',
    'Programa: PHOTO home (FOTO namai). Nieko nekilnojau - tik perskaiciau ir suskaiciavau.':
        'App: PHOTO home (FOTO namai). Nichts wurde bewegt – nur gelesen und gezählt.',
    '## Kiek ir kur':
        '## Wie viele und wo',
    '- Is viso indekse: **%d failu, %s**.':
        '- In Summe im Index: **%d Dateien, %s**.',
    '- Lentyna `%s`: %d failu, %s.':
        '- Regal `%s`: %d Dateien, %s.',
    '- Neatpazinto turinio (0 baitu, netikri .jpg): %d - ju nejudinsiu.':
        '- Nicht erkannter Inhalt (0 Bytes, fingierte .jpg): %d – die werden nicht bewegt.',
    '## Is kur tavo datos (sluoksniu derlius)':
        '## Woher Ihre Daten stammen (Ebenen-Ernte)',
    'BE PATIKIMOS DATOS (kelias i _UNDATED): **%d (%.1f %%)**. Tai ne siukslynas - tai darbo zona: failai sveiki, tik ju fotografavimo data dar neissiaiskinta.':
        'OHNE ZUVERLÄSSIGES DATUM (Ziel: _UNDATED): **%d (%.1f %%)**. Keine Schrotthalde, sondern eine Arbeitszone: die Dateien sind gesund, nur ihr Aufnahmedatum ist noch nicht geklärt.',
    '## Linija laike':
        '## Zeitleiste',
    '**Nuo ~%d tavo datos patikimos.** Senesni kadrai - priesistore: ten datu metaduomenys reti, ir kaip tik ten programa dirba labiausiai.':
        '**Ab ca. %d sind Ihre Daten zuverlässig.** Ältere Aufnahmen sind Uralter: dort sind Datums-Metadaten selten, und genau dort arbeitet die App am härtesten.',
    'Aiskios ribos, nuo kada datos patikimos, siame archyve nesimato - patikimu datu dalis svyruoja.':
        'Eine klare Grenze, ab wann die Daten zuverlässig sind, ist in diesem Archiv nicht sichtbar – der Anteil zuverlässiger Daten schwankt.',
    '| Metai | Kadru | Patikima data |':
        '| Jahr | Aufnahmen | Zuverlässiges Datum |',
    '## Ko neperziurejau (saugikliai)':
        '## Was nicht angeschaut wurde (Sicherheitsgrenzen)',
    'Sie katalogai praleisti TYCIA (backup/kopiju pasaulis, sisteminiai, nuorodos) - jei nori juos itraukti, pridek kaip atskira saltini:':
        'Diese Verzeichnisse wurden BEWUSST übersprungen (Backup-/Kopienwelt, Systemordner, Links) – wenn Sie sie einbeziehen möchten, fügen Sie sie als eigene Quelle hinzu:',
    '- ... ir dar %d.':
        '- ... und %d weitere.',
    'Ataskaita sukurta A pakopoje (zvalgyba): ne vienas failas nepajudintas. Tvarkymas (B pakopa) - tik tavo ranka, su UNDO.':
        'Dieser Bericht wurde in Stufe A (Erkundung) erstellt: keine einzige Datei wurde bewegt. Die Sortierung (Stufe B) erfolgt nur durch Ihre Hand, mit UNDO.',
    'Sustabdyta - kopijas galite susitvarkyti su Smart Duplicate Finder.':
        'Angehalten – die Kopien können Sie mit Smart Duplicate Finder aufräumen.',
    '# KAIP SUTVARKYTA - sio archyvo taisykles':
        '# SO WURDE SORTIERT – die Regeln dieses Archivs',
    "Sutvarke programa **PHOTO home (FOTO namai)** (Claude's Gifts to the World).":
        'Sortiert mit **PHOTO home (FOTO namai)** (Claudas Geschenke an die Welt).',
    'Atnaujinta: ':
        'Aktualisiert:',
    '## Taisykles':
        '## Regeln',
    '- Nuotraukos guli pagal data: `Metai\\Menuo` arba `Metai\\Menuo Renginys` (renginio vardas - is originalaus aplanko pavadinimo).':
        '- Die Fotos liegen nach Datum: `Jahr\\Monat` oder `Jahr\\Monat Anlass` (der Anlass stammt vom Namen des Originalordners).',
    '- Kiekvienos nuotraukos data nustatyta sia tvarka: EXIF -> failo vardas -> aplanko vardas -> failo mtime.':
        '- Das Datum jedes Fotos wurde in dieser Reihenfolge ermittelt: EXIF -> Dateiname -> Ordnernahme -> mtime der Datei.',
    '- `%s` - ekrano nuotraukos (atpazintos be ML: nera kameros EXIF + ekrano raiska / vardas); jos irgi skirstomos pagal `Metai\\Menuo`, o be patikimos datos lieka saknyje.':
        '- `%s` – Screenshots (ohne ML erkannt: kein Kamer-EXIF + Bildschirmauflösung/Name); sie werden ebenfalls nach `Jahr\\Monat` einsortiert, ohne zuverlässiges Datum bleiben sie im Stammordner.',
    '- `%s` - failai, kuriu datos saltinis tik mtime (kopijavimo pedsakas, ne fotografavimo data).':
        '- `%s` – Dateien, deren einziges Datum die mtime ist (Kopierspur, kein Aufnahmedatum).',
    '- SVARBU: `%s` yra DARBO ZONA, ne siukslynas. Failai joje sveiki ir nepaliesti - tiesiog ju datu dar neissiaiskinom. Naujos programos versijos ismoksta nauju atpazinimo budu ir parusiuoja sia lentyna is vidaus (pvz. `%s\\2015\\06`) - prie siu failu dar bus griztama.':
        '- WICHTIG: `%s` ist eine ARBEITSZONE und keine Schrotthalde. Die Dateien darin sind vollständig intakt und unangetastet – ihre Daten sind nur noch nicht geklärt. Neuere Versionen der App lernen neue Erkennungsmethoden und sortieren dieses Regal von innerhalb weiter aus (z. B. `%s\\2015\\06`) – auf diese Dateien kommt man zurück.',
    '- Neatpazinto turinio failai (0 baitu, netikri .jpg) is vietos NEJUDINTI.':
        '- Dateien mit nicht erkanntem Inhalt (0 Bytes, fingierte .jpg) wurden NICHT verschoben.',
    '- Dublikatai (tas pats turinys) i archyva keliami TIK viena karta.':
        '- Duplikate (gleicher Inhalt) werden NUR EINMAL in das Archiv einsortiert.',
    '## Statistika':
        '## Statistik',
    '- `%s` - %d failu, %s':
        '- `%s` – %d Dateien, %s',
    'Is viso: **%d failu, %s**; praleista (dubliai/jau buvo): %d.':
        'In Summe: **%d Dateien, %s**; übersprungen (Duplikate/bereits vorhanden): %d.',
    '## Sia diena pries X metu':
        '## An diesem Tag vor X Jahren',
    'Sios dienos kadru turite is: %s.':
        'Aufnahmen von diesem Tag haben Sie aus: %s.',
    'Pilna atsaukimo istorija - [UNDO_ZURNALAS.md](UNDO_ZURNALAS.md). Programoje mygtukas "UNDO - grazinti viska atgal" veikia bet kada.':
        'Die komplette UNDO-Historie – [UNDO_ZURNALAS.md](UNDO_ZURNALAS.md). Der Knopf „UNDO – alles zurücksetzen“ in der App funktioniert jederzeit.',
    '# UNDO zurnalas - kas is kur atkeliavo':
        '# UNDO-Protokoll – was kam von wo her',
    '| Laikas | Rezimas | Is kur | I kur |':
        '| Zeit | Modus | Von | Nach |',
    '(rodoma pirmi %d irasu; pilnas sarasas - indeksas.db undo lenteleje)':
        '(die ersten %d Einträge werden angezeigt; die komplette Liste in der undo-Tabelle von indeksas.db)',
    'ARBA leiskite programai padaryti tai PACIAI: atlikite 1 zingsni (laidas + "Failu perdavimas"), UZDARYKITE Explorer langa su telefonu (telefona vienu metu mato tik viena programa) ir spauskite "Jungti telefona" - programa pati suras nuotrauku vietas, nukopijuos ir prides i saltinius. Is telefono TIK skaitoma - nieko netrinam ir nerasom.':
        'ODER lassen Sie die App es SELBST TUN: führen Sie Schritt 1 aus (Kabel + «Dateitransfer»), SCHLIESSEN Sie das Explorer-Fenster mit dem Smartphone (das Smartphone wird gleichzeitig nur von einer App gesehen) und drücken Sie «Smartphone verbinden» – die App findet die Fotoorte selbst, kopiert sie und fügt die Quelle hinzu. Das SMARTPHONE wird NUR GELESEN – nichts wird gelöscht oder geschrieben.',
    'Jungti telefona':
        'Smartphone verbinden',
    'Ieskomas telefonas':
        'Smartphone wird gesucht',
    'Telefono klaida: {}':
        'Smartphone-Fehler: {}',
    'Rastas telefonas: {} ({} nuotrauku vietu)':
        'Smartphone gefunden: {} ({} Fotoorte)',
    'Telefono kopija atsaukta.':
        'Kopie vom Smartphone abgebrochen.',
    'Kopijuojama is telefono':
        'Wird vom Smartphone kopiert',
    'Telefonas baigtas: tiksle {} failu ({} praleista kaip jau turimi).':
        'Smartphone fertig: {} Dateien im Ziel ({} übersprungen, weil bereits vorhanden).',
    'is telefono':
        'vom Smartphone',
    'Aplankas pridetas prie saltiniu - spauskite "Indeksuoti pazymetus".':
        'Der Ordner wurde zu den Quellen hinzugefügt – bitte «Markierte indexieren» drücken.',
    'Telefono nerandu':
        'Smartphone nicht sichtbar',
    'Nepavyko pamatyti telefono nuotrauku. Dazniausios priezastys:\n\n1. Telefonas neatsake i "USB rezimas?" klausima -\n   pasirinkite "Failu perdavimas" (File Transfer)\n   TELEFONO ekrane. Numatytasis buna "tik krovimas".\n2. Telefona naudoja kita programa - uzdarykite Explorer\n   langa su telefonu ir bandykite dar karta (telefona\n   vienu metu mato tik viena programa).\n3. Ekranas uzrakintas - atrakinkite ir perkiskite laida.\n4. Laidas tik krovimo - pabandykite kita laida.\n5. Senas telefonas gali apsimesti CD-ROM ir siulyti\n   diegti savo programa - nediekite, tiesiog perkiskite\n   laida i kita lizda.':
        'Die Fotos vom Smartphone konnten nicht gelesen werden. Die häufigsten Gründe:\n\n1. Das Smartphone hat die Frage «USB-Modus?» nicht beantwortet –\n   wählen Sie auf dem SMARTPHONE-Display «Dateitransfer»\n   (File Transfer). Standardmäßig ist «nur Laden».\n2. Eine andere App nutzt das Smartphone gerade – schließen\n   Sie das Explorer-Fenster mit dem Smartphone und versuchen\n   Sie es erneut (das Smartphone wird gleichzeitig nur von\n   einer App gesehen).\n3. Das Display ist gesperrt – entsperren und das Kabel neu\n   anschließen.\n4. Das Kabel ist ein Ladekabel – bitte ein anderes Kabel\n   testen.\n5. Ältere Smartphones können sich als CD-ROM ausgeben und\n   ihre eigene Software anbieten – bitte nicht installieren,\n   das Kabel einfach in einen anderen Port stecken.',
    'Klausti DI':
        'KI fragen',
    'Paimti is telefono':
        'Vom Smartphone holen',
    'Telefonas: {}':
        'Smartphone: {}',
    'Ka kopijuoti (rastos nuotrauku vietos):':
        'Was kopiert werden soll (gefundene Fotoorte):',
    'elementu':
        'Elemente',
    'I kuri aplanka kompiuteryje:':
        'In welchen Ordner auf dem Computer:',
    'Parinkti...':
        'Durchsuchen...',
    'Is telefono TIK skaitoma - originalai jame lieka nepaliesti.':
        'Das SMARTPHONE wird NUR GELESEN – die Originale bleiben dort unangetastet.',
    'Kopijuojama: {}':
        'Kopieren: {}',
    'nukopijuota {}, praleista {}':
        '{} kopiert, {} übersprungen',
    'baigiama... tiksle {} failu':
        'wird abgeschlossen... am Ende {} Dateien',
    'Telefonas dingo kopijos metu: {}':
        'Das Smartphone ist während des Kopierens verschwunden: {}',
    'Kopija nutraukta - dalis failu jau kompiuteryje, telefonas nepaliestas.':
        'Kopie abgebrochen – einige Dateien liegen bereits auf dem Computer, das Smartphone wurde nicht berührt.',
    'Kopija nutruko be rezultato - patikrinkite laida ir bandykite dar karta.':
        'Die Kopie endete ohne Ergebnis – bitte das Kabel prüfen und noch einmal versuchen.',
}
