# -*- coding: utf-8 -*-
"""PHOTO home GUI tekstai rusu kalba (raktas = lietuviskas tekstas).

Vertimai: mergyte (lokalus Qwen), 2026-08-30, porcijomis po 40.
Patikra: _darbal/vertimai_mergyte_2026-08-30/_patikros/patikra_vertimai.py
Perziurejo: Claude.
"""

_RU = {
    'PHOTO home (FOTO namai) - nuotrauku archyvo tvarkytojas':
        'PHOTO home (FOTO namai) — организатор домашнего архива фотографий',
    'Saltiniai (varneles - ka skenuoti):':
        'Источники (отметьте, что просканировать):',
    'Saltinis':
        'Источник',
    'Failai':
        'Файлы',
    'Dydis':
        'Размер',
    'Prideti aplanka...':
        'Добавить папку...',
    'Zvalgyba (kiek failu?)':
        'Оценка (сколько файлов?)',
    'Indeksuoti pazymetus':
        'Индексировать отмеченные',
    'Atsaukti':
        'Отмена',
    'Zurnalas:':
        'Журнал:',
    'Indeksas: {}':
        'Индекс: {}',
    'Pasirinkite nuotrauku aplanka':
        'Выберите папку с фотографиями',
    'Nepazymeta nieko':
        'Ничего не отмечено',
    'Pazymeta: {} {}, ~{} failu, ~{}, ~{} min':
        'Отмечено: {} {}, ~{} файлов, ~{}, ~{} мин',
    'Pazymeta: {} {} - ivercio dar nera, spauskite Zvalgyba':
        'Отмечено: {} {} — оценки пока нет, нажмите «Оценка»',
    '({} be zvalgybos ivercio)':
        '({} пока без оценки)',
    'Atsisiuntimai (Downloads)':
        'Загрузки (Downloads)',
    'Paveiksleliai (Pictures)':
        'Изображения (Pictures)',
    'OneDrive Paveiksleliai':
        'Изображения OneDrive',
    'Phone Link kesas':
        'Кэш Phone Link',
    'kopija, ne originalai':
        'копии, а не оригиналы',
    'Vyksta zvalgyba':
        'Выполняется оценка',
    'Zvalgyba: {} failu, {}, praleista {}':
        'Оценка: {} файлов, {}, пропущено {}',
    'Naujas diskas - lentynos vardo paklausiu pries indeksavima.':
        'Новый диск — перед индексацией я спрошу имя полки.',
    'Vienkartine bazes migracija: sutvarkyta {} irasu':
        'Одноразовая миграция базы: приведено в порядок {} записей',
    'Lentynos krikstynos':
        'Имя полки',
    'Sis kompiuterio diskas gaus lentynos varda.\nGalite palikti siuloma arba irasyti sava (iki 40 zenklu).':
        'Диск этого компьютера получит имя полки.\nМожно оставить предложенное или ввести своё (до 40 символов).',
    'Naujas diskas! Duokite lentynai varda, kuri atpazinsite po metu (iki 40 zenklu).\nPatarimas: uzklijuokite ant disko lipduka su siuo vardu.':
        'Новый диск! Дайте этой полке имя, которое вы узнаете через год (до 40 символов).\nСовет: наклейте на сам диск стикер с этим именем.',
    'Vyksta indeksavimas':
        'Идёт индексация',
    'Indeksuota {} - {} failu ({} nepakite, {} neatpazinta, {} ne medija, {} praleista)':
        'Индексировано {} - {} файлов ({} без изменений, {} не распознано, {} не медиа, {} пропущено)',
    'Baigta. Is viso suindeksuota {} failu.':
        'Готово. Всего проиндексировано {} файлов.',
    'Atsaukiama - baigiama dabartine partija...':
        'Отмена — завершаем текущую партию...',
    'Klaida: {}':
        'Ошибка: {}',
    'Kaip paimti is telefono?':
        'Как перенести фото с телефона?',
    'Kaip paimti nuotraukas is telefono:\n\n1. Atsidarykite telefona Explorer\'yje:\n   - jei telefonas jau matomas Explorer sarase\n     (Windows 11 + "Link to Windows" rodo ji ir be\n     laido) - galite bandyti is cia; DEMESIO: sis\n     belaidis langas dazniausiai rodo NE VISKA;\n   - patikimiausia: prijunkite USB laidu. Telefonas\n     PATS PAKLAUS "USB rezimas?" (langelis ekrane arba\n     pranesimu juostoje, JUSU TELEFONO kalba) -\n     pasirinkite "Failu perdavimas" (File Transfer).\n     NE "Nuotrauku perdavimas" - tas rodo tik DCIM,\n     be WhatsApp. Numatytasis buna "tik krovimas" -\n     todel neatsakius telefonas kompiuteryje atrodo\n     TUSCIAS. Matysite viska, dideli kiekiai eis greitai.\n2. Telefone: Internal storage. Nuotraukos:\n   DCIM\\Camera; skrinsotai: Pictures\\Screenshots\n   arba DCIM\\Screenshots (Xiaomi); WhatsApp:\n   Android\\media\\com.whatsapp\\WhatsApp\\Media.\n3. Nukopijuokite aplankus i kompiuteri ar isorini\n   diska (originalai telefone lieka).\n4. Cia spauskite "Prideti aplanka..." ir indeksuokite.\n\nKodel reikia kopijos? Telefonas Explorer\'yje - ne\ndiskas, o "langas" i ji (be raides): programos jo\ntiesiogiai skenuoti negali. Dar vienas kelias -\ndebesis: jei naudojate Google Photos / OneDrive, jie\nnuotraukas jau atsiuncia i kompiuterio aplanka - ta\naplanka cia ir pridekite.':
        'Как перенести фото с телефона:\n\n1. Откройте телефон в Explorer:\n   - если телефон уже виден в списке Explorer\n     (Windows 11 + "Link to Windows" показывает его даже\n     без кабеля) — можно попробовать отсюда; ВНИМАНИЕ:\n     этот беспроводной вид обычно показывает НЕ ВСЁ;\n   - надёжнее всего: подключите USB-кабель. Телефон\n     САМ СПРОСИТ "Режим USB?" (диалоговое окно на экране\n     или в шторке уведомлений, ЯЗЫК ВАШЕГО ТЕЛЕФОНА) —\n     выберите "Передача файлов" (File Transfer).\n     НЕ "Передача фото" — там будет только DCIM,\n     без WhatsApp. По умолчанию стоит "только зарядка" —\n     пока вы не ответите, телефон в компьютере будет\n     выглядеть ПУСТЫМ. После этого увидите всё, большие\n     объёмы пойдут быстро.\n2. На телефоне: Internal storage. Фото:\n   DCIM\\Camera; скриншоты: Pictures\\Screenshots\n   или DCIM\\Screenshots (Xiaomi); WhatsApp:\n   Android\\media\\com.whatsapp\\WhatsApp\\Media.\n3. Скопируйте папки на компьютер или внешний\n   диск (оригиналы останутся на телефоне).\n4. Здесь нажмите "Добавить папку..." и проиндексируйте.\n\nЗачем нужна копия? Телефон в Explorer — не\nдиск, а "окно" в него (без буквы диска): программы\nне могут сканировать его напрямую. Ещё один путь —\nоблако: если вы используете Google Photos / OneDrive, они\nуже скачивают фото в папку на компьютере — именно\nэту папку можно добавить здесь.',
    'Neradote atsakymo? Klauskite DI':
        'Не нашли ответ? Спросите ИИ',
    'Klausk DI':
        'Спросить ИИ',
    'macOS beta: tvarkymas isjungtas, kol neturime gyvo Mac testuotojo - katalogas ir paieska veikia pilnai.':
        'macOS beta: сортировка отключена, пока у нас нет живого тестировщика на Mac — каталог и поиск работают полностью.',
    'Kas ivyks paspaudus OK:\n\n1. Atsidarys interneto narsykle su DI padejejo\n   claude.ai puslapiu. Zinutes laukelyje jau bus\n   irasyta angliska pradzia - prisistatymas, kas per\n   programa ir kur jos kodas.\n2. NEISSIGASKITE raudono pranesimo virs zinutes -\n   claude.ai ji rodo visada, kai tekstas ateina per\n   nuoroda. Tai tik priminimas perskaityti, kas\n   siunciama.\n3. Zinutes gale, po zodziu "My question:", irasykite\n   SAVO klausima - galima lietuviskai! - ir spauskite\n   siuntimo mygtuka (rodykle). Klausti galima visko,\n   pvz.: "kaip atsinaujinti programa i naujesne\n   versija? paaiskink zingsnis po zingsnio".\n4. Jei DI atsakys angliskai - tiesiog paprasykite kita\n   zinute: "atsakyk lietuviskai", ir toliau bendraus\n   lietuviskai.\n\nPastaba: claude.ai gali paprasyti prisijungti (nemokama\npaskyra). Niekas neissiunciama be jusu rankos.':
        'Что будет после нажатия OK:\n\n1. Откроется веб-браузер с ИИ-помощником\n   на странице claude.ai. В поле сообщения уже будет\n   написана готовая заставка — представление, что за\n   программа и где её код.\n2. НЕ БОЙТЕСЬ красного уведомления над сообщением —\n   claude.ai показывает его всегда, когда текст приходит\n   по ссылке. Это просто напоминание прочитать, что\n   вы отправляете.\n3. В конце сообщения, после слов "My question:", напишите\n   СВОЙ вопрос — можно по-русски! — и нажмите\n   кнопку отправки (стрелку). Спрашивать можно о чём\n   угодно, например: "как обновить программу до\n   последней версии? объясни по шагам".\n4. Если ИИ ответит не на том языке — просто напишите\n   в следующем сообщении: "ответь по-русски", и дальше\n   общение пойдёт по-русски.\n\nПримечание: claude.ai может попросить войти (бесплатный\nаккаунт). Ничего не отправляется без вашего участия.',
    'Pagalba':
        'Справка',
    'Apie...':
        'О программе...',
    'Instrukcija':
        'Инструкция',
    'Apie programa':
        'О программе',
    'Nuotrauku savartyno tvarkytojas - nieko netrina, viskas su UNDO.':
        'Организатор накопленных фото — ничего не удаляет, у всего есть UNDO.',
    'Versija {v}':
        'Версия {v}',
    'Kurejo puslapis:':
        'Страница автора:',
    'Nepavyko atidaryti: {}':
        'Не удалось открыть: {}',
    'Namu archyvas (tvarkymas + UNDO):':
        'Домашний архив (организация + UNDO):',
    'Kurti namu archyva...':
        'Создать домашний архив...',
    'UNDO - grazinti viska atgal':
        'UNDO — вернуть всё назад',
    'Archyvo aplankas: pasirinkite tuscia arba sukurkite nauja dialogo mygtuku':
        'Папка архива: выберите пустую или создайте новую кнопкой в диалоге',
    'Aplankas netuscias':
        'Папка не пуста',
    'Namas statomas tusciame sklype - aplanke jau yra failu.\nTesti vis tiek? (Esami failai NEBUS liesti; sutampantis turinys bus praleistas.)':
        'Дом строится на пустом участке — в папке уже есть файлы.\nПродолжить? (Существующие файлы НЕ будут трогаться; совпадающий контент будет пропущен.)',
    'Ruosiami pasiulymai':
        'Подготовка предложений',
    'Nera ka tvarkyti - pirma suindeksuokite saltinius.':
        'Нечего разбирать — сначала проиндексируйте источники.',
    'Namu archyvo pasiulymas':
        'Предложение по домашнему архиву',
    'Programa siulo tokia tvarka. Nuimkite varnele nuo grupiu, kuriu dabar nekelti:':
        'Программа предлагает такой порядок. Снимите отметку с групп, которые сейчас не переносить:',
    'Grupe (aplankas archyve)':
        'Группа (папка в архиве)',
    'Perkelti vietoj kopijuoti (originalai isnyks is saltiniu)':
        'Переместить вместо копирования (оригиналы исчезнут из источников)',
    'Tvarkymas atsauktas pasiulymu lange.':
        'Организация отменена в окне предложений.',
    'Nepasirinkta ne viena grupe.':
        'Не выбрана ни одна группа.',
    'Perziura (niekas dar nevykdoma)':
        'Предпросмотр (ничего ещё не выполнено)',
    'Bus {} ({} failu, {}) i:\n{}\n\nVykdyti?':
        'Будет {} ({} файлов, {}) в:\n{}\n\nВыполнить?',
    'PERKELIAMA':
        'ПЕРЕМЕЩЕНИЕ',
    'KOPIJUOJAMA':
        'КОПИРОВАНИЕ',
    'Tvarkymas atsauktas perziuroje.':
        'Организация отменена на предпросмотре.',
    'Vyksta tvarkymas':
        'Выполняется организация',
    'Tvarkymas baigtas: {} sutvarkyta, {} dubliu praleista, {} jau buvo, {} klaidu.':
        'Организация завершена: {} размещено, {} дубликатов пропущено, {} уже было, {} ошибок.',
    'UNDO':
        'UNDO',
    'Grazinti VISKA atgal pagal UNDO zurnala?\nKopijos bus istrintos is archyvo, perkelti failai gris i vietas.':
        'Вернуть ВСЁ назад по журналу UNDO?\nКопии будут удалены из архива, перемещённые файлы вернутся на места.',
    'Vyksta atstatymas':
        'Выполняется восстановление',
    'UNDO baigtas: {} atstatyta, {} klaidu.':
        'UNDO завершён: {} восстановлено, {} ошибок.',
    'Tvarkymas':
        'Организация',
    'Paieska':
        'Поиск',
    'nuo YYYY-MM-DD':
        'с YYYY-MM-DD',
    'iki YYYY-MM-DD':
        'по YYYY-MM-DD',
    'Visi tipai':
        'Все типы',
    'Foto':
        'Фото',
    'Skrinsotai':
        'Скриншоты',
    'Video':
        'Видео',
    'Ikonos':
        'Иконки',
    'Dokumentai':
        'Документы',
    'Neatpazinti':
        'Нераспознанные',
    'Visos lentynos':
        'Все полки',
    'Etikete (pvz. Jonines)':
        'Метка события (например, Свадьба)',
    'Kamera (pvz. Canon)':
        'Камера (например, Canon)',
    'Failo vardas':
        'Имя файла',
    'Ieskoti':
        'Поиск',
    '- Issaugotos paieskos -':
        '- Сохранённые поиски -',
    'Issaugoti paieska...':
        'Сохранить поиск...',
    'Issaugoti paieska':
        'Сохранить поиск',
    'Trinti vaizda':
        'Удалить сохранённый поиск',
    'Duokite siai paieskai varda:':
        'Назовите этот поиск:',
    "Paieska '{}' issaugota.":
        "Поиск '{}' сохранён.",
    "Vaizdas '{}' istrintas.":
        "Сохранённый поиск '{}' удалён.",
    'Tuscios paieskos nesaugome - ivedkite bent viena filtra.':
        'Пустой поиск не сохраняется — задайте хотя бы один фильтр.',
    'Rasta: {} (rodoma {})':
        'Найдено: {} (показано {})',
    'Paieska: rasta {} irasu.':
        'Поиск: найдено {} записей.',
    'Vyksta paieska':
        'Выполняется поиск',
    'Ruosiamos miniatiuros':
        'Формируются миниатюры',
    'Miniatiuros paruostos ({}).':
        'Миниатюры готовы ({}).',
    'Kartoteka pildosi: {}':
        'Каталог заполняется: {}',
    'Kartoteka pasipilde: +{} miniatiuru.':
        'Каталог пополнился: +{} миниатюр.',
    'Kartotekos fonas sustojo: {}':
        'Фоновое наполнение каталога остановлено: {}',
    'Atverti su {}':
        'Открыть в {}',
    'Atverti perziurai':
        'Открыть для просмотра',
    'Prideti/keisti redaktorius...':
        'Добавить/изменить редакторы...',
    'Redaktoriu failas: {}':
        'Файл редакторов: {}',
    'Nepavyko atverti redaktoriuje: {}':
        'Не удалось открыть в редакторе: {}',
    'Megstami redaktoriai':
        'Избранные редакторы',
    'Cia galite nurodyti savo megstamas programas, kuriomis atidarysite nuotrauka desiniu klavisu (pvz. Photoshop, GIMP, Paint).\n\nPaspaudus OK atsidarys tekstinis failas. Kiekviena programa rasoma dviem eilutemis:\n\n   [Photoshop]\n   kelias = C:\\Program Files\\...\\Photoshop.exe\n\nLauztiniuose skliaustuose - pavadinimas, kuri matysite meniu. Kelia paprasciausia nukopijuoti is Explorer adreso juostos ir iklijuoti - dvigubu bruksniu NEREIKIA.\n\nIssaugokite faila (Ctrl+S) ir uzdarykite - naujos programos meniu atsiras is karto.\n\nJei neaisku - paspauskite "Klausk DI" ir autoriaus padejejas paaiskins.':
        'Здесь можно указать любимые программы, которыми вы будете открывать фото правой кнопкой мыши (например, Photoshop, GIMP, Paint).\n\nПосле нажатия OK откроется текстовый файл. Каждая программа пишется двумя строками:\n\n   [Photoshop]\n   kelias = C:\\Program Files\\...\\Photoshop.exe\n\nВ квадратных скобках — имя, которое вы увидите в меню. Путь проще всего скопировать из адресной строки Explorer и вставить — двойные обратные слеши НЕ нужны.\n\nСохраните файл (Ctrl+S) и закройте его — новые программы сразу появятся в меню.\n\nЕсли что-то непонятно, нажмите "Спросить ИИ" — и помощник автора всё объяснит.',
    'Lentyna':
        'Полка',
    'Lentynos':
        'Полки',
    'Spustelekite - lentynu sarasas':
        'Нажмите — список полок',
    'Prijungta':
        'Подключен',
    'Paskutini karta matyta':
        'Последний раз виден',
    'Failu':
        'Файлы',
    'Taip':
        'Да',
    'Ne':
        'Нет',
    'Uzdaryti':
        'Закрыть',
    'Indekso dar nera - pirma suindeksuokite saltinius.':
        'Индекса ещё нет - сначала проиндексируйте источники.',
    "Neteisinga data '{}' - reikia YYYY-MM-DD":
        "Неверная дата '{}' - нужен формат YYYY-MM-DD",
    "Lentyna '{}' siuo metu neprijungta - prijunkite diska ir pakartokite.":
        "Полка '{}' сейчас не подключена - подключите диск и повторите.",
    'Failas nerastas: {}':
        'Файл не найден: {}',
    'Atverti perziurykleje':
        'Открыть в просмотрщике',
    "Parodyti Explorer'yje":
        'Показать в Explorer',
    'Kopijuoti kelia':
        'Копировать путь',
    'Kelias nukopijuotas.':
        'Путь скопирован.',
    "Dvigubas klikas - parodyti faila Explorer'yje. Perziurai naudokite megstama perziurykle.":
        'Двойной щелчок - показать файл в Explorer. Для просмотра используйте любимый просмотрщик.',
    'Sveiki sugrize! Indekse - {} {} ({} {}), paieska veikia is karto.':
        'С возвращение! В индексе: {} {} ({} {}), поиск работает сразу.',
    '{} diskas {}':
        'диск {}, {}',
    'Saltinis praleistas - krikstynos atsauktos.':
        'Источник пропущен - проименование отменено.',
    'Indekse: {} {}, {} {}':
        'В индексе: {} {}, {} {}',
    'Indeksas tuscias':
        'Индекс пуст',
    'Kalba':
        'Язык',
    'Nepavyko issaugoti: {}':
        'Не удалось сохранить: {}',
    'Kalba issaugota. Perleisti programa dabar?':
        'Язык сохранён. Перезапустить программу сейчас?',
    'Kalba pritaikoma paleidus programa is naujo.':
        'Язык будет применён после перезапуска программы.',
    'Portable rezimas':
        'Портативный режим',
    'Portable rezimas (viskas salia programos)':
        'Портативный режим (всё рядом с программой)',
    'Ijungta: indeksas ir darbiniai failai saugomi salia programos (pvz., flesiuke).\nIsjungta (numatyta): vartotojo kataloge %LOCALAPPDATA%\\PhotoHome.':
        'Вкл.: индекс и рабочие файлы хранятся рядом с программой (например, на флешке).\nВыкл. (по умолчанию): в папке пользователя %LOCALAPPDATA%\\PhotoHome.',
    'Nepavyko perjungti rezimo: {}':
        'Не удалось переключить режим: {}',
    'Portable rezimas IJUNGTAS - duomenys salia programos.':
        'Портативный режим ВКЛЮЧЁН - данные хранятся рядом с программой.',
    'Portable rezimas isjungtas - duomenys vartotojo kataloge.':
        'Портативный режим выключен - данные хранятся в папке пользователя.',
    'Yra kopiju':
        'Обнаружены копии',
    'Panasu, kad ~%d failai kartojasi (vienodo dydzio, ~%s).':
        'Похоже, ~%d файлов повторяются (одинаковый размер, ~%s).',
    'Skaicius - ivertis pagal vienoda failo dydi; pries keldamas i archyva turini patikrinsiu baitas i baita, tad tikras kopiju skaicius gali buti kiek mazesnis.':
        'Это оценка по одинаковому размеру файлов; перед переносом в архив я проверю содержимое побайтно, поэтому реальных копий может оказаться немного меньше.',
    'Kopijomis laikau tik IDENTISKUS baitas i baita failus. Panasiu nematau: jei nuotrauka apkarpyta, patamsinta ar sumazinta (pvz. persiusta per zinute), man tai atskiras failas - ir i archyva keliaus visos jos versijos. Tokias randa Smart Duplicate Finder, nes jis lygina vaizda, ne baitus.':
        'Копиями я считаю только байт-в-байт ИДЕНТИЧНЫЕ файлы. Похожие я не вижу: если фото обрезано, затемнено или уменьшено (например, отправлено в мессенджере), это для меня отдельный файл - и в архив попадут все его версии. Такие находит Smart Duplicate Finder, потому что он сравнивает изображение, а не байты.',
    'Jei tesi: keliausiu po viena kiekvieno turinio kopija. Kuria butent - pasirinksiu pagal patikimesne data, ir ji gali tureti kita varda ar kita aplanka nei ta, kuria butum pasirinkes tu.':
        'Если продолжить: я оставлю по одной копии каждого содержимого. Которую именно - выберу по более достоверной дате, и у неё может быть другое имя или папка, чем та, которую выбрали бы вы.',
    'Patogiausias momentas kopijoms susitvarkyti - DABAR, pries kuriant namu archyva: susitvarkykite su Smart Duplicate Finder (github.com/RobertasTa/smart-duplicate-finder) ir suindeksuokite is naujo, arba tiesiog teskite - pries kuriant archyva ispesiu dar karta.':
        'Лучший момент разобраться с копиями - СЕЙЧАС, до создания домашнего архива: наведите порядок с помощью Smart Duplicate Finder (github.com/RobertasTa/smart-duplicate-finder) и проиндексируйте заново, или просто продолжайте - я ещё раз предупрежу перед созданием архива.',
    'Supratau':
        'Понятно',
    'Kopiju suvestine: ~{} failai galimai kartojasi (~{}). Patarimas: pirma Smart Duplicate Finder, tada archyvo kurimas.':
        'Сводка по копиям: ~{} файлов, возможно, повторяются (~{}). Совет: сначала Smart Duplicate Finder, затем создание архива.',
    'Jei nori pasirinkti pats: sustok, susitvarkyk kopijas su Smart Duplicate Finder (github.com/RobertasTa/smart-duplicate-finder) ir paleisk PHOTO home is naujo.':
        'Если хотите выбрать сами: остановитесь, разберитесь с копиями с помощью Smart Duplicate Finder (github.com/RobertasTa/smart-duplicate-finder) и запустите PHOTO home заново.',
    'Testi':
        'Продолжить',
    'Sustoti':
        'Остановить',
    'Pirmas kartas? Takas paprastas:':
        'Первый раз? Путь простой:',
    '  1. Prijunkite telefona arba pazymekite aplanka ir spauskite Indeksuoti - siame zingsnyje programa failus tik SKAITO.':
        '1. Подключите телефон или отметьте папку и нажмите «Проиндексировать» - на этом шаге программа только ЧИТАЕТ файлы.',
    '  2. Gausite ARCHYVO RENTGENA: kas jusu archyve, is kur datos, kiek liko be ju.':
        '2. Получите РЕНТГЕН АРХИВА: что в вашем архиве, откуда даты и сколько файлов осталось без дат.',
    '  3. Jei panorekite - namu archyvas Metai\\Menuo tvarka, o kiekvienas zingsnis su UNDO.':
        '3. Если захотите - домашний архив в порядке Год\\Мес, каждый шаг с UNDO.',
    'PAZADAS: ne vienas baitas jusu failuose nekeiciamas; tvarkymas - tik kopijos arba perkelimas su pilnu UNDO.':
        'ОБЕЩАНИЕ: ни один байт в ваших файлах не изменяется; наведение порядка - только копирование или перемещение с полным UNDO.',
    '[{}] be datos likusiems: kaimynyste +{}, mtime partijos +{} - failai gavo kaimynu medianos data.':
        '[{}] без даты оставшимся: соседи +{}, батчи mtime +{} - файлы получили медианную дату соседей.',
    '- Daliai failu be savo datos data priskirta is APLINKOS: vienalyciame aplanke - kaimynu mediana (`kaimynyste`), kartu atkeliavusiu failu grupeje - partijos mediana (`partija`).':
        '- Часть файлов без собственной даты получила дату из ОКРУЖЕНИЯ: в однородной папке - медиана соседей (`kaimynyste`), в группе файлов, пришедших вместе - медиана батча (`partija`).',
    'Archyvo rentgenas':
        'Рентген архива',
    'Issaugoti ataskaita...':
        'Сохранить отчёт...',
    'Gerai':
        'OK',
    'Rentgeno ataskaita issaugota: {}':
        'Отчёт рентгена сохранён: {}',
    'Nepavyko issaugoti ataskaitos: {}':
        'Не удалось сохранить отчёт: {}',
    '# KAS TAVO ARCHYVE - rentgeno ataskaita':
        '# ЧТО В ВАШЕМ АРХИВЕ - отчёт рентгена',
    'Programa: PHOTO home (FOTO namai). Nieko nekilnojau - tik perskaiciau ir suskaiciavau.':
        'Программа: PHOTO home (FOTO namai). Ничего не перемещалось - только чтение и подсчёт.',
    '## Kiek ir kur':
        '## Сколько и где',
    '- Is viso indekse: **%d failu, %s**.':
        '- Всего в индексе: **%d файлов, %s**.',
    '- Lentyna `%s`: %d failu, %s.':
        '- Полка `%s`: %d файлов, %s.',
    '- Neatpazinto turinio (0 baitu, netikri .jpg): %d - ju nejudinsiu.':
        '- Нераспознанное содержимое (0 байт, фальшивые .jpg): %d - я их не трону.',
    '## Is kur tavo datos (sluoksniu derlius)':
        '## Откуда ваши даты (урожай по слоям)',
    'BE PATIKIMOS DATOS (kelias i _UNDATED): **%d (%.1f %%)**. Tai ne siukslynas - tai darbo zona: failai sveiki, tik ju fotografavimo data dar neissiaiskinta.':
        'БЕЗ НАДЁЖНОЙ ДАТЫ (путь в _UNDATED): **%d (%.1f %%)**. Это не свалка - это рабочая зона: файлы целы, только дата съёмки ещё не определена.',
    '## Linija laike':
        '## Линия времени',
    '**Nuo ~%d tavo datos patikimos.** Senesni kadrai - priesistore: ten datu metaduomenys reti, ir kaip tik ten programa dirba labiausiai.':
        '**От ~%d ваши даты надёжны.** Более ранние кадры - преистория: там метаданные с датами редки, и именно там программа работает больше всего.',
    'Aiskios ribos, nuo kada datos patikimos, siame archyve nesimato - patikimu datu dalis svyruoja.':
        'Чёткой границы, с каких дат даты надёжны, в этом архиве не видно - доля надёжных дат колеблется.',
    '| Metai | Kadru | Patikima data |':
        '| Год | Кадры | Надёжная дата |',
    '## Ko neperziurejau (saugikliai)':
        '## Что я не рассматривал (страховка)',
    'Sie katalogai praleisti TYCIA (backup/kopiju pasaulis, sisteminiai, nuorodos) - jei nori juos itraukti, pridek kaip atskira saltini:':
        'Эти каталоги пропущены НАЦЕЛЕНО (мир резервных копий, системные папки, ссылки) - если хотите их включить, добавьте как отдельный источник:',
    '- ... ir dar %d.':
        '- ... и ещё %d.',
    'Ataskaita sukurta A pakopoje (zvalgyba): ne vienas failas nepajudintas. Tvarkymas (B pakopa) - tik tavo ranka, su UNDO.':
        'Отчёт создан на этапе A (разведка): ни один файл не перемещён. Наведение порядка (этап B) - только вашей рукой, с UNDO.',
    'Sustabdyta - kopijas galite susitvarkyti su Smart Duplicate Finder.':
        'Остановлено - копиями можно разобраться с помощью Smart Duplicate Finder.',
    '# KAIP SUTVARKYTA - sio archyvo taisykles':
        '# КАК НАВЕДЁН ПОРЯДОК - правила этого архива',
    "Sutvarke programa **PHOTO home (FOTO namai)** (Claude's Gifts to the World).":
        "Порядок наведена программой **PHOTO home (FOTO namai)** (Claude's Gifts to the World).",
    'Atnaujinta: ':
        'Обновлено:',
    '## Taisykles':
        '## Правила',
    '- Nuotraukos guli pagal data: `Metai\\Menuo` arba `Metai\\Menuo Renginys` (renginio vardas - is originalaus aplanko pavadinimo).':
        '- Фотографии размещены по дате: `Год\\Мес` или `Год\\Мес событие` (имя события - из названия исходной папки).',
    '- Kiekvienos nuotraukos data nustatyta sia tvarka: EXIF -> failo vardas -> aplanko vardas -> failo mtime.':
        '- Дата каждого фото определена в таком порядке: EXIF -> имя файла -> имя папки -> mtime файла.',
    '- `%s` - ekrano nuotraukos (atpazintos be ML: nera kameros EXIF + ekrano raiska / vardas); jos irgi skirstomos pagal `Metai\\Menuo`, o be patikimos datos lieka saknyje.':
        '- `%s` - скриншоты (распознаны без ML: нет EXIF камеры + разрешение экрана / имя); они тоже сортируются по `Год\\Мес`, а без надёжной даты остаются в корне.',
    '- `%s` - failai, kuriu datos saltinis tik mtime (kopijavimo pedsakas, ne fotografavimo data).':
        '- `%s` - файлы, у которых единственный источник даты - mtime (след копирования, а не дата съёмки).',
    '- SVARBU: `%s` yra DARBO ZONA, ne siukslynas. Failai joje sveiki ir nepaliesti - tiesiog ju datu dar neissiaiskinom. Naujos programos versijos ismoksta nauju atpazinimo budu ir parusiuoja sia lentyna is vidaus (pvz. `%s\\2015\\06`) - prie siu failu dar bus griztama.':
        '- ВАЖНО: `%s` - РАБОЧАЯ ЗОНА, а не свалка. Файлы в ней целы и не тронуты - мы просто ещё не определили их даты. Новые версии программы осваивают новые способы распознавания и приводят эту полку в порядок изнутри (например, `%s\\2015\\06`) - к этим файлам ещё вернёмся.',
    '- Neatpazinto turinio failai (0 baitu, netikri .jpg) is vietos NEJUDINTI.':
        '- Файлы с нераспознанным содержимым (0 байт, фальшивые .jpg) не перемещены.',
    '- Dublikatai (tas pats turinys) i archyva keliami TIK viena karta.':
        '- Дубликаты (идентичное содержимое) попадают в архив ТОЛЬКО один раз.',
    '## Statistika':
        '## Статистика',
    '- `%s` - %d failu, %s':
        '- `%s` - %d файлов, %s',
    'Is viso: **%d failu, %s**; praleista (dubliai/jau buvo): %d.':
        'Всего: **%d файлов, %s**; пропущено (дубликаты/уже были): %d.',
    '## Sia diena pries X metu':
        '## Этот день X лет назад',
    'Sios dienos kadru turite is: %s.':
        'Кадры этого дня у вас есть за: %s.',
    'Pilna atsaukimo istorija - [UNDO_ZURNALAS.md](UNDO_ZURNALAS.md). Programoje mygtukas "UNDO - grazinti viska atgal" veikia bet kada.':
        'Полная история отмены - [UNDO_ZURNALAS.md](UNDO_ZURNALAS.md). В программе кнопка "UNDO - вернуть всё назад" работает в любой момент.',
    '# UNDO zurnalas - kas is kur atkeliavo':
        '# Журнал UNDO - что откуда пришло',
    '| Laikas | Rezimas | Is kur | I kur |':
        '| Время | Режим | Откуда | Куда |',
    '(rodoma pirmi %d irasu; pilnas sarasas - indeksas.db undo lenteleje)':
        '(показаны первые %d записей; полный список - в таблице undo базы indeksas.db)',
    'ARBA leiskite programai padaryti tai PACIAI: atlikite 1 zingsni (laidas + "Failu perdavimas"), UZDARYKITE Explorer langa su telefonu (telefona vienu metu mato tik viena programa) ir spauskite "Jungti telefona" - programa pati suras nuotrauku vietas, nukopijuos ir prides i saltinius. Is telefono TIK skaitoma - nieko netrinam ir nerasom.':
        'ИЛИ позвольте программе сделать это САМОЙ: выполните шаг 1 (кабель + "Передача файлов"), ЗАКРОЙТЕ окно Explorer с телефоном (телефон в один момент видит только одна программа) и нажмите "Подключить телефон" - программа сама найдёт места с фотографиями, скопирует их и добавит папку в источники. Из телефона ТОЛЬКО чтение - ничего не удаляется и не записывается.',
    'Jungti telefona':
        'Подключить телефон',
    'Ieskomas telefonas':
        'Поиск телефона',
    'Telefono klaida: {}':
        'Ошибка телефона: {}',
    'Rastas telefonas: {} ({} nuotrauku vietu)':
        'Телефон найден: {} ({} мест с фотографиями)',
    'Telefono kopija atsaukta.':
        'Копирование с телефона отменено.',
    'Kopijuojama is telefono':
        'Копирование с телефона',
    'Telefonas baigtas: tiksle {} failu ({} praleista kaip jau turimi).':
        'Телефон обработан: всего {} файлов ({} пропущено как уже имеющиеся).',
    'is telefono':
        'из телефона',
    'Aplankas pridetas prie saltiniu - spauskite "Indeksuoti pazymetus".':
        'Папка добавлена в источники - нажмите "Indeksuoti pazymetus".',
    'Telefono nerandu':
        'Не нахожу телефон',
    'Nepavyko pamatyti telefono nuotrauku. Dazniausios priezastys:\n\n1. Telefonas neatsake i "USB rezimas?" klausima -\n   pasirinkite "Failu perdavimas" (File Transfer)\n   TELEFONO ekrane. Numatytasis buna "tik krovimas".\n2. Telefona naudoja kita programa - uzdarykite Explorer\n   langa su telefonu ir bandykite dar karta (telefona\n   vienu metu mato tik viena programa).\n3. Ekranas uzrakintas - atrakinkite ir perkiskite laida.\n4. Laidas tik krovimo - pabandykite kita laida.\n5. Senas telefonas gali apsimesti CD-ROM ir siulyti\n   diegti savo programa - nediekite, tiesiog perkiskite\n   laida i kita lizda.':
        'Не удалось увидеть фотографии телефона. Самые частые причины:\n\n1. Телефон не ответил на вопрос "Режим USB?" -\n   выберите "Передача файлов" (File Transfer)\n   на ЭКРАНЕ ТЕЛЕФОНА. По умолчанию обычно "только зарядка".\n2. Телефоном пользуется другая программа - закройте окно\n   Explorer с телефоном и попробуйте ещё раз (телефон\n   в один момент видит только одна программа).\n3. Экран заблокирован - разблокируйте и переткните кабель.\n4. Кабель только для зарядки - попробуйте другой кабель.\n5. Старый телефон может притвориться CD-ROM и предложить\n   установить свою программу - не устанавливайте, просто переткните\n   кабель в другой порт.',
    'Klausti DI':
        'Спросить ИИ',
    'Paimti is telefono':
        'Взять с телефона',
    'Telefonas: {}':
        'Телефон: {}',
    'Ka kopijuoti (rastos nuotrauku vietos):':
        'Что копировать (найдены места с фотографиями):',
    'elementu':
        'элементов',
    'I kuri aplanka kompiuteryje:':
        'В какую папку на компьютере:',
    'Parinkti...':
        'Выбрать...',
    'Is telefono TIK skaitoma - originalai jame lieka nepaliesti.':
        'Из телефона ТОЛЬКО чтение - оригиналы на нём остаются нетронутыми.',
    'Kopijuojama: {}':
        'Копирование: {}',
    'nukopijuota {}, praleista {}':
        'скопировано {}, пропущено {}',
    'baigiama... tiksle {} failu':
        'завершение... всего {} файлов',
    'Telefonas dingo kopijos metu: {}':
        'Телефон исчез во время копирования: {}',
    'Kopija nutraukta - dalis failu jau kompiuteryje, telefonas nepaliestas.':
        'Копирование прервано - часть файлов уже на компьютере, телефон не тронут.',
    'Kopija nutruko be rezultato - patikrinkite laida ir bandykite dar karta.':
        'Копирование оборвалось без результата - проверьте кабель и попробуйте ещё раз.',
}
