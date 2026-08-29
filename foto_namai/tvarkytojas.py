"""tvarkytojas.py - pasiulymai -> dry-run -> vykdymas (E4; PIPELINE 3-6).

B pakopa "Kraustymasis": namas statomas TUSCIAME SKLYPE - saltiniu
struktura nekilnojama, viskas keliauja I tikslo lentyna (VIZIJA).
Principai: JOKIO trynimo; numatytasis rezimas KOPIJUOTI; pilnas UNDO;
testinumas (busena DB, ne atmintyje); perkelimo sauga per hash
(sprendimas 27a - to paties turinio nekelti antra karta); neatpazinti
failai NEJUDINAMI (sprendimas 28); Live poros keliauja kartu (spr. 17).
Zero Qt - GUI worker'iai si moduli tik apvynios.
"""

import os
import shutil
from datetime import datetime
from pathlib import Path, PureWindowsPath

import hashai
import models
from indeksavimas import DiskoSargoKlaida, _disko_sargas

_FOTO_TIPAI = ("foto", "dokumentas")


def _dabar():
    return datetime.now().isoformat(timespec="seconds")


# ---------------------------------------------------------------- Live poros
def suporuoti_live(con):
    """IMG_x.JPG + IMG_x.MOV (tas pats stem, tas pats aplankas) -> pora;
    live_pora_id abiem = foto id. Grazina poru skaiciu."""
    eiles = con.execute(
        "SELECT id, lentyna_id, santykinis_kelias, turinio_tipas"
        " FROM failai WHERE busena='SUINDEKSUOTAS'").fetchall()
    pagal_stem = {}
    for fid, lid, kelias, tipas in eiles:
        stem = str(PureWindowsPath(kelias).with_suffix("")).lower()
        pagal_stem.setdefault((lid, stem), []).append((fid, tipas))
    poru = 0
    for nariai in pagal_stem.values():
        fotos = [f for f, t in nariai if t in _FOTO_TIPAI]
        video = [f for f, t in nariai if t == "video"]
        if len(fotos) == 1 and len(video) == 1:
            con.execute("UPDATE failai SET live_pora_id=? WHERE id IN (?,?)",
                        (fotos[0], fotos[0], video[0]))
            poru += 1
    con.commit()
    return poru


# ------------------------------------------------------------------- planas
def _tikslo_grupe(datetaken, patikima, tipas, etikete):
    """Failo namu grupe (sprendimai 5, 26, 28). None = NEJUDINAMAS."""
    if tipas == "neatpazintas":
        return None
    if tipas == "skrinsotas":
        # KLIURKA 23 (Roberto gyvas ratas 2026-08-25 su TIKRAIS duomenimis):
        # jo Pictures kataloge buvo 6869 skrinsotai ir VISI nuejo i VIENA
        # ploksti aplanka - Explorer ji atidaro letai, o zmogui jis bevertis.
        # Anksciau to nesimate, nes testuose skrinsotu buvo 16-21.
        # Ta pati Metai\Menuo taisykle kaip nuotraukoms - kad vartotojui
        # NEREIKETU mokytis dvieju logiku. Etikete skrinsotams netaikoma
        # (ji butu "Screenshots" is aplanko vardo - beverte).
        # Be patikimos datos - lieka _SCREENSHOTS saknyje (be naujo
        # "_UNDATED po _SCREENSHOTS", kad nebutu dvieju _UNDATED archyve).
        if datetaken and patikima:
            return "%s\\%s\\%s" % (models.GRUPE_SKRINSOTAI,
                                   datetaken[:4], datetaken[5:7])
        return models.GRUPE_SKRINSOTAI
    if not datetaken or not patikima:
        return models.GRUPE_NEPATIKIMOS
    metai, menuo = datetaken[:4], datetaken[5:7]
    if etikete:
        return "%s\\%s %s" % (metai, menuo, etikete)
    return "%s\\%s" % (metai, menuo)


def siulyti_plana(con):
    """Kiekvienam SUINDEKSUOTAM failui - tikslo_kelias (grupe\\vardas).
    Live video seka savo foto grupe. Grazina grupiu suvestine dialogui:
    [{"grupe","failai","baitai"}], rikiuota malejancia failu tvarka."""
    eiles = con.execute(
        "SELECT id, vardas, dydis, datetaken, patikima_data, turinio_tipas,"
        " renginio_etikete, live_pora_id FROM failai"
        " WHERE busena='SUINDEKSUOTAS'").fetchall()
    irasai = {fid: {"grupe": _tikslo_grupe(datetaken, patikima, tipas,
                                           etikete),
                    "vardas": vardas, "dydis": dydis, "tipas": tipas,
                    "pora": pora}
              for fid, vardas, dydis, datetaken, patikima, tipas, etikete,
              pora in eiles}
    # Live video perima foto grupe (sprendimas 17) - viskas atmintyje
    for fid, r in irasai.items():
        if r["tipas"] == "video" and r["pora"] and r["pora"] != fid \
                and r["pora"] in irasai:
            r["grupe"] = irasai[r["pora"]]["grupe"]
    suvestine = {}
    atnaujinimai = []
    for fid, r in irasai.items():
        grupe, vardas, dydis = r["grupe"], r["vardas"], r["dydis"]
        if grupe is None:
            atnaujinimai.append((None, fid))
            continue
        atnaujinimai.append((grupe + "\\" + vardas, fid))
        s = suvestine.setdefault(grupe, {"grupe": grupe, "failai": 0,
                                         "baitai": 0})
        s["failai"] += 1
        s["baitai"] += dydis
    con.executemany("UPDATE failai SET tikslo_kelias=? WHERE id=?",
                    atnaujinimai)
    con.commit()
    return sorted(suvestine.values(), key=lambda s: -s["failai"])


def patvirtinti_plana(con, grupes=None):
    """Zmogaus varneles is pasiulymu dialogo -> busena SUPLANUOTAS.
    grupes=None - visos pasiulytos. Grazina suplanuotu skaiciu."""
    if grupes is None:
        kur = con.execute(
            "UPDATE failai SET busena='SUPLANUOTAS'"
            " WHERE busena='SUINDEKSUOTAS' AND tikslo_kelias IS NOT NULL")
    else:
        viso = 0
        for g in grupes:
            viso += con.execute(
                "UPDATE failai SET busena='SUPLANUOTAS'"
                " WHERE busena='SUINDEKSUOTAS' AND tikslo_kelias IS NOT NULL"
                " AND tikslo_kelias = ? || '\\' || vardas",
                (g,)).rowcount
        con.commit()
        return viso
    con.commit()
    return kur.rowcount


def perziura(con):
    """DRY-RUN is indekso kibireliu - nulis disko veiksmu (PIPELINE 5)."""
    eiles = con.execute(
        "SELECT tikslo_kelias, COUNT(*), SUM(dydis) FROM failai"
        " WHERE busena='SUPLANUOTAS' GROUP BY substr(tikslo_kelias, 1,"
        " length(tikslo_kelias) - length(vardas) - 1)").fetchall()
    grupes = []
    for kelias, kiek, baitai in eiles:
        grupe = str(PureWindowsPath(kelias).parent) if kelias else "?"
        grupes.append({"grupe": grupe, "failai": kiek, "baitai": baitai or 0})
    viso = con.execute("SELECT COUNT(*), SUM(dydis) FROM failai"
                       " WHERE busena='SUPLANUOTAS'").fetchone()
    return {"grupes": sorted(grupes, key=lambda g: -g["failai"]),
            "failai": viso[0], "baitai": viso[1] or 0}


# ------------------------------------------------------------------ vykdymas
def _unikalus(dst):
    """Kolizija su KITU turiniu -> vardas-2, vardas-3... (PIPELINE 6)."""
    if not dst.exists():
        return dst
    n = 2
    while True:
        kandidatas = dst.with_name("%s-%d%s" % (dst.stem, n, dst.suffix))
        if not kandidatas.exists():
            return kandidatas
        n += 1


def vykdyti(con, db_kelias, tikslo_saknis, rezimas="kopijuoti", stop=None,
            progress=None, partijos_dydis=200):
    """Vykdymas partijomis su UNDO (PIPELINE 6). Saltinio kelias imamas
    is failo saltinio_saknis (irasyta indeksavimo metu; jei disko raide
    pasikeite ir kelias neegzistuoja - KLAIDA "neprijungtas", tesiama;
    v1.x TODO: saknies atkurimas pagal lentynos serial). Nutruko - kita
    sesija mato busenas ir TESIA (kvieciam vykdyti dar karta)."""
    tikslo_saknis = Path(tikslo_saknis)
    seansas = con.execute(
        "INSERT INTO seansai (pradzia, aprasymas) VALUES (?, ?)",
        (_dabar(), "vykdymas: " + rezimas)).lastrowid
    con.commit()

    # Perkelimo sauga (27a): turinys, jau gyvenantis archyve
    zinomi_hash = {h for (h,) in con.execute(
        "SELECT hash FROM failai WHERE busena='SUTVARKYTAS'"
        " AND hash IS NOT NULL")}

    stat = {"sutvarkyta": 0, "praleista_dubliai": 0, "praleista_jau_yra": 0,
            "klaidos": 0}
    while True:
        if stop is not None and stop():
            break
        # 4e p. 3 (2026-08-28): patikimos datos failai vykdomi PIRMI, tad
        # is vienodo hash kopiju i archyva keliauja ta, kurios data
        # patikimesne (pvz. su EXIF), o ne atsitiktine indeksavimo eiles
        # pirmoji - plikoji kopija be reikalo nebeguldo failo i _UNDATED.
        # Spr. 44 langas nesikeicia: zmogus vis tiek ispejamas ir gali
        # sustoti; cia tik KURI kopija imama jam paspaudus "Testi".
        partija = con.execute(
            "SELECT id, saltinio_saknis, santykinis_kelias, tikslo_kelias,"
            " hash FROM failai WHERE busena='SUPLANUOTAS'"
            " ORDER BY patikima_data DESC, id LIMIT ?",
            (partijos_dydis,)).fetchall()
        if not partija:
            break
        _disko_sargas(tikslo_saknis)
        con.execute("BEGIN")
        for fid, saknis, santykinis, tikslas, h in partija:
            if stop is not None and stop():
                break
            src = Path(saknis) / santykinis if saknis else None
            if src is None or not src.exists():
                con.execute("UPDATE failai SET busena='KLAIDA', aprasas=?"
                            " WHERE id=?", ("saltinis neprijungtas/dingo",
                                            fid))
                stat["klaidos"] += 1
                continue
            # Spr. 27 patikslinimas (2026-08-29): hash GARANTUOJAMAS cia.
            # A pakopa jo nebeskaiciuoja (rentgenas greitas), A2 fonas
            # apskaiciuoja vaizdams; ko dar nera - apskaiciuojam DABAR is
            # saltinio ir irasom i indeksa (kad kitas seansas / zinomi_hash
            # ji rastu). Perkelimo sauga nesusilpneja NE PER BAITA.
            if h is None:
                try:
                    h = hashai.failo_hash(src)
                    con.execute("UPDATE failai SET hash=? WHERE id=?",
                                (h, fid))
                except OSError:
                    h = None      # neperskaitomas - guldom be dubliu saugos
            if h and h in zinomi_hash:
                con.execute("UPDATE failai SET busena='PRALEISTAS',"
                            " aprasas=? WHERE id=?",
                            ("dublikatas - toks turinys jau archyve", fid))
                stat["praleista_dubliai"] += 1
                continue
            dst = tikslo_saknis / tikslas
            dst.parent.mkdir(parents=True, exist_ok=True)
            if dst.exists():
                try:
                    if h and hashai.failo_hash(dst) == h:
                        con.execute(
                            "UPDATE failai SET busena='PRALEISTAS',"
                            " aprasas=? WHERE id=?", ("jau yra tiksle", fid))
                        stat["praleista_jau_yra"] += 1
                        if h:
                            zinomi_hash.add(h)
                        continue
                except OSError:
                    pass
                dst = _unikalus(dst)
            try:
                if rezimas == "perkelti":
                    shutil.move(str(src), str(dst))
                else:
                    shutil.copy2(str(src), str(dst))
            except OSError as e:
                con.execute("UPDATE failai SET busena='KLAIDA', aprasas=?"
                            " WHERE id=?", (str(e)[:200], fid))
                stat["klaidos"] += 1
                continue
            con.execute(
                "INSERT INTO undo (seanso_id, fileid, is_kur, i_kur, hash,"
                " rezimas, laikas) VALUES (?,?,?,?,?,?,?)",
                (seansas, fid, str(src), str(dst), h, rezimas, _dabar()))
            con.execute("UPDATE failai SET busena='SUTVARKYTAS' WHERE id=?",
                        (fid,))
            stat["sutvarkyta"] += 1
            if h:
                zinomi_hash.add(h)
        con.commit()   # atomine partija - nutraukimas saugus
        if progress is not None:
            progress(dict(stat))
    con.execute("UPDATE seansai SET pabaiga=? WHERE id=?",
                (_dabar(), seansas))
    con.commit()
    return stat


def atstatyti(con, stop=None, progress=None):
    """PILNAS UNDO pagal zurnala, atbuline tvarka (PIPELINE 6):
    kopija - istrinama kopija tiksle (hash patikrinus), perkelta -
    graZinama atgal. Grazina statistika."""
    stat = {"atstatyta": 0, "klaidos": 0}
    eiles = con.execute(
        "SELECT id, fileid, is_kur, i_kur, hash, rezimas FROM undo"
        " WHERE atstatyta=0 ORDER BY id DESC").fetchall()
    con.execute("BEGIN")
    for uid, fid, is_kur, i_kur, h, rezimas in eiles:
        if stop is not None and stop():
            break
        dst = Path(i_kur)
        try:
            if rezimas == "perkelti":
                Path(is_kur).parent.mkdir(parents=True, exist_ok=True)
                shutil.move(str(dst), is_kur)
            else:
                if dst.exists():
                    if h and hashai.failo_hash(dst) != h:
                        raise OSError("tikslo failas pakeistas - netrinam")
                    dst.unlink()
        except OSError as e:
            con.execute("UPDATE failai SET aprasas=? WHERE id=?",
                        ("undo klaida: " + str(e)[:150], fid))
            stat["klaidos"] += 1
            continue
        con.execute("UPDATE undo SET atstatyta=1 WHERE id=?", (uid,))
        con.execute("UPDATE failai SET busena='ATSTATYTAS' WHERE id=?",
                    (fid,))
        stat["atstatyta"] += 1
        if progress is not None and stat["atstatyta"] % 200 == 0:
            progress(dict(stat))
    con.commit()

    # KLIURKA 14 (Roberto gyvas ratas 2026-08-23): UNDO grazindavo failus
    # i vieta DISKE, bet indekse palikdavo juos "panaudotus" - visi likdavo
    # ATSTATYTAS/PRALEISTAS, o planas ima tik SUINDEKSUOTAS. Rezultatas:
    # zmogus, pasinaudojes UNDO, nebegalejo tvarkyti tu paciu nuotrauku
    # ("Nothing to organize", nors indekse 991 failas), o perindeksavimas
    # nepadeda - failai diske nepakite, tad skeneris teisingai sako
    # "991 unchanged". UNDO pazadas yra "grazinti VISKA atgal" - taip pat
    # ir programos galva, ne tik failus. ATSTATYTAS yra IVYKIS, ne busena;
    # istorija lieka undo lenteleje ir seansuose.
    # Grazinam TIK tada, kai zurnalas isvalytas iki galo (nutrauktas UNDO
    # palieka busenas ramybeje - kita sesija tesia).
    if not con.execute("SELECT 1 FROM undo WHERE atstatyta=0"
                       " LIMIT 1").fetchone():
        con.execute(
            "UPDATE failai SET busena='SUINDEKSUOTAS', tikslo_kelias=NULL"
            " WHERE busena IN ('ATSTATYTAS','PRALEISTAS','SUPLANUOTAS',"
            " 'KLAIDA')")
        con.commit()
        _isvalyti_tuscius(con)
    return stat


def _isvalyti_tuscius(con):
    """KLIURKA 15 (Roberto akys 2026-08-23: "katalogai yra, bet failu te
    nera"): po UNDO failai isnesami teisingai, bet lieka stoveti tuscias
    karkasas - 2017..2026 su visais menesiais, _SCREENSHOTS, _UNDATED.
    "Grazinti viska atgal" reiskia ir tai.

    SAUGIKLIAI (trynimas - pavojingiausias veiksmas programoje):
    - liecia TIK tuos katalogus, kuriuos PATI programa sukure - t. y.
      undo zurnalo tikslu tevus (ir ju tevus iki archyvo saknies).
      Zmogaus aplankas, buves archyve iki tvarkymo, NELIECIAMAS -
      pirma sio saugiklio versija ejo os.walk per visa archyva ir
      istrynė sveitima tuscia aplanka (pagavo patikra pries priimant);
    - salina tik TUSCIUS katalogus (rmdir, ne rmtree - jei kas viduje,
      OSError ir katalogas lieka);
    - archyvo saknies NELIECIA (ten KAIP_SUTVARKYTA.md ir zurnalas);
    - jokiu klaidu nekelia: nepavyko istrinti - paliekam ramybeje.
    """
    keliai = [k for (k,) in con.execute(
        "SELECT i_kur FROM undo WHERE i_kur IS NOT NULL") if k]
    if len(keliai) < 2:
        return 0
    try:
        saknis = Path(os.path.commonpath(keliai))
    except (ValueError, OSError):
        return 0                      # skirtingi diskai ir pan.
    if not saknis.is_dir():
        return 0
    # MUSU katalogai: kiekvieno tikslo tevai iki saknies (jos neitraukiant)
    musu = set()
    for k in keliai:
        p = Path(k).parent
        while p != saknis and saknis in p.parents:
            musu.add(p)
            p = p.parent
    istrinta = 0
    # Nuo giliausiu i virsu, kad istustejes tevas irgi kristu
    for p in sorted(musu, key=lambda x: len(x.parts), reverse=True):
        try:
            p.rmdir()                 # netuscias -> OSError, paliekam
            istrinta += 1
        except OSError:
            pass
    return istrinta
