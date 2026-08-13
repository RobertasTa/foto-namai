=====================================================================
  PHOTO HOME (FOTO namai) v1.0 - home photo archive organizer
  Robertas & Claude, 2026
=====================================================================

WHAT IS THIS?

  PHOTO home (originally "FOTO namai", Lithuanian for photo home)
  cleans up your photo
  "dump": it gathers photos and
  videos from several places (phone copies, Downloads, old drives),
  figures out WHEN each photo was taken, and lays everything out
  into a clean Year\Month structure. With full UNDO - everything
  can be put back with one button.

  The program deletes NOTHING and sends NOTHING to the internet.
  Everything happens only on your computer.

WHAT IT IS NOT

  It is not a viewer/gallery - use your favourite one for browsing
  (IrfanView, Windows Photos, etc.). PHOTO home is an ORGANIZER:
  its job is getting files into the right places.

TWO STAGES - THE SAFETY FOUNDATION

  A. HOME BOOK (index) - the first step, always safe.
     The program only READS your files and writes its own list
     (the index): where a file lives, when it was taken, whether
     the date is trustworthy. Your files are NOT touched.
     Search works with the index alone.

  B. MOVING DAY (home archive) - only when you press
     "Build home archive..." yourself. The program proposes a
     plan, you review and confirm it. The default mode is COPY
     (originals stay in place). And UNDO is always there.

GETTING STARTED (4 steps)

  1. On the "Organizing" tab tick what to scan (the program
     suggests known locations; "Add folder..." adds any other).
     Press the "Recon" button.
  2. WHERE TO SEE THE DURATION: the blue line BELOW the source
     list (above the buttons) shows the full price BEFORE you
     start: "Selected: N files, X GB, ~Y min". If it shows
     hours - feel free to leave it overnight.
  3. Press "Index selected" and wait: while working, a clock
     spins in the middle of the window, and finer progress is
     in the bar at the very bottom. Cancel any time without
     harm - next run continues from where it stopped.
  4. On the "Search" tab search by date, type, label, camera or
     file name. Double-click shows the file in Explorer.

HOW THE DATE IS RESOLVED

  In order of trust:
  1. EXIF (the date the camera wrote inside the photo);
  2. file name (IMG-20230318-WA0006.jpg, Screenshot_2025...);
  3. folder name ("Midsummer 2015" also becomes a search label);
  4. file mtime - but then the date is marked UNRELIABLE and such
     files go to a separate _NEPATIKIMOS_DATOS (unreliable dates)
     folder so they never mix with truly dated ones.

  Screenshots are recognized and placed into a separate
  _SKRINSOTAI folder - they are not "memories".
  Fake files (.jpg name but not an image; 0 bytes) are NOT
  moved; the journal explains why.
  Android trash files (.trashed-*) and thumbnail caches
  (.thumbnails) are SKIPPED: photos you deleted and the phone's
  internal copies never enter the index or the archive.

HOME MOVIES (VIDEO)

  Family videos are first-class citizens of the archive,
  indexed and organized together with photos: mp4, mov, avi,
  mkv, m4v, 3gp, wmv, webm, mpg/mpeg, mts/m2ts.
  A video's date comes from its file name (e.g. VID_20231113_...)
  or from mtime (then honestly labeled "unreliable") - v1 does
  not yet read video-internal metadata.
  iPhone "Live Photo" pairs (IMG_x.JPG + IMG_x.MOV) ALWAYS
  travel together when organizing - the pair is never split.
  Music and audio recordings (mp3, m4a...) are NOT indexed -
  this is a memories archive, not a file inventory.

SHELVES - SEVERAL DRIVES IN ONE INDEX

  WHAT IS A "SHELF"? Any place your files live - a storage:
  the computer's internal drive (C:, D:), an external USB drive,
  a flash stick, a camera memory card, a network (NAS) folder.
  Picture a cupboard with shelves: boxes of photos on each one.
  The program knows WHICH shelf every photo sits on - even when
  the shelf is taken out of the cupboard (drive disconnected).

  YOU NAME THE SHELVES YOURSELF. When a new drive appears, the
  program shows a dialog with its own suggestion (e.g. from the
  drive label, or "MY-PC drive C:") - keep it or type your own:
  "Red WD", "Mom's flash stick", "Old laptop". Tip for external
  drives: put a sticker with that name on the drive - no
  guessing a year later.

  Search also works for DISCONNECTED shelves - the program says:
  "file is on shelf 'Red WD', currently not connected; plug the
  drive in". Drive letters (E:, F:) may change freely - the
  drive is recognized by its internal serial, not the letter,
  so the name you gave never gets lost.

HOW TO GET PHOTOS OFF YOUR PHONE

  A phone in Explorer is not a drive but a "window" into it
  (no drive letter), so no program can scan it directly.
  Photos must be COPIED first:

  1. Open the phone in Explorer. On Windows 11 with "Link to
     Windows" the phone may show up even without a cable - you
     can try from there, BUT the wireless view usually does not
     show everything. Most reliable: USB cable. Once plugged
     in, the phone ITSELF WILL ASK "USB mode?" (a dialog on
     its screen or in the notification shade, in the PHONE'S
     language) - pick "File Transfer". NOT "Photo transfer" -
     that mode shows only DCIM, no WhatsApp. The default is
     "charging only" - until you answer, the phone looks
     EMPTY on the computer (not a malfunction). After picking
     you see everything, and large amounts copy faster.
     An old Huawei/Honor may pose as a CD drive "My CDROM"
     and offer to install HiSuite - close it, do NOT install:
     picking "Device file manager (MTP)" on the phone is
     enough. If the phone shows up but looks empty - unlock
     its screen and replug the cable into another USB port.
  2. Internal storage: photos in DCIM\Camera; screenshots in
     Pictures\Screenshots or DCIM\Screenshots (Xiaomi);
     WhatsApp - Android\media\com.whatsapp\WhatsApp\Media.
  3. Copy the folders to your computer or an external drive
     (originals stay untouched on the phone).
  4. In PHOTO home press "Add folder..." -> index.

  One more path - the cloud: Google Photos / OneDrive already
  download photos into a computer folder - just add that
  folder. The same guide lives in the app - the "Get photos
  off a phone?" button.
  Note: the Microsoft Phone Link photo cache is partial and
  stored inside an internal database, not as files - do not
  rely on it as a source.

DUPLICATES

  While organizing, the same content is never copied into the
  archive twice (checked by content, not by name). If there are
  many duplicates, the program will suggest running our family
  duplicate tool Smart Duplicate Finder first, then organizing.

WHERE THE PROGRAM KEEPS ITS DATA

  Index and settings: C:\Users\<you>\AppData\Local\PhotoHome\
  After organizing, two human-readable files appear in the
  archive root: KAIP_SUTVARKYTA.md (the rules used) and
  UNDO_ZURNALAS.md (what came from where).

  Portable mode (advanced): put an empty file named
  PhotoHome_portable.txt next to the program - all data will
  then travel with it (e.g. on a flash drive).

REQUIREMENTS AND NOTES

  - Windows 10 or newer (Win 7/8 will not work - Qt6 limit).
  - Your antivirus may warn about an unsigned program
    (SmartScreen "Unknown publisher") - normal for free tools
    without an expensive certificate. The code is open on GitHub.

DIDN'T FIND YOUR ANSWER IN THIS FILE?

  This program was written by Claude (the Anthropic AI) - so the
  best one to answer questions about it is... Claude itself:
  claude.ai. The app has a button for that: "?" -> "No answer
  here? Ask the AI" - it opens claude.ai with the question
  already started; you just type your question and hit send
  (nothing is sent without your hand). For example:

      "...My question: is it safe to point it at my photo
       folder? What exactly does 'Build home archive' do?"
      "...My question: how do I update the app to the newest
       version? explain it step by step."

  The code is public, so the AI reads the actual code and
  answers about how the program really works - no guessing.
  Any language works. NOTE: claude.ai will show a red caution
  banner above such text - that is their standard warning for
  ALL link-delivered prompts (read what you are sending, then
  send with confidence - the text is right there before your
  eyes). Other AI assistants work too - but the author will
  answer best.

FAMILY OF GIFTS (all free, no ads)

  1. Smart Duplicate Finder - duplicate file finder. Run it first.
  2. Temp Cleaner - temp file cleanup with explanations.
  3. PHOTO home (FOTO namai) - home photo archive organizer. This program.

  Author page: https://github.com/RobertasTa

=====================================================================
