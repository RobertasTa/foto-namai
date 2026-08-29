"""ataskaita.py - KAIP_SUTVARKYTA.md ir buhalterija (E5; .md DNR spr. 20).

Archyvo saknyje - zmogui skaitomas paaiskinimas: taisykles, statistika,
"sia diena pries X metu" (nulis kainos, smagu), data. Salia - UNDO
zurnalas zmogui. Zero Qt.
"""

from datetime import date, datetime
from pathlib import Path

import models
from indeksas import dayid_i_iso
from kalba import t   # KLIURKA 16: .md failai zmogui - jo kalba


def _dabar():
    return datetime.now().isoformat(timespec="seconds")


def kaip_sutvarkyta_md(con, tikslo_saknis):
    """Generuoja/atnaujina KAIP_SUTVARKYTA.md archyvo saknyje."""
    eil = [t("# KAIP SUTVARKYTA - sio archyvo taisykles"),
           "",
           t("Sutvarke programa **PHOTO home (FOTO namai)** (Claude's"
             " Gifts to the World)."),
           t("Atnaujinta: ") + _dabar(),
           "",
           t("## Taisykles"),
           "",
           t("- Nuotraukos guli pagal data: `Metai\\Menuo` arba"
             " `Metai\\Menuo Renginys` (renginio vardas - is originalaus"
             " aplanko pavadinimo)."),
           t("- Kiekvienos nuotraukos data nustatyta sia tvarka: EXIF ->"
             " failo vardas -> aplanko vardas -> failo mtime."),
           t("- Daliai failu be savo datos data priskirta is APLINKOS:"
             " vienalyciame aplanke - kaimynu mediana (`kaimynyste`),"
             " kartu atkeliavusiu failu grupeje - partijos mediana"
             " (`partija`)."),
           t("- `%s` - ekrano nuotraukos (atpazintos be ML: nera"
             " kameros EXIF + ekrano raiska / vardas); jos irgi skirstomos"
             " pagal `Metai\\Menuo`, o be patikimos datos lieka saknyje.")
           % models.GRUPE_SKRINSOTAI,
           t("- `%s` - failai, kuriu datos saltinis tik"
             " mtime (kopijavimo pedsakas, ne fotografavimo data).")
           % models.GRUPE_NEPATIKIMOS,
           t("- SVARBU: `%s` yra DARBO ZONA, ne siukslynas. Failai joje"
             " sveiki ir nepaliesti - tiesiog ju datu dar neissiaiskinom."
             " Naujos programos versijos ismoksta nauju atpazinimo budu ir"
             " parusiuoja sia lentyna is vidaus (pvz. `%s\\2015\\06`) -"
             " prie siu failu dar bus griztama.")
           % (models.GRUPE_NEPATIKIMOS, models.GRUPE_NEPATIKIMOS),
           t("- Neatpazinto turinio failai (0 baitu, netikri .jpg) is"
             " vietos NEJUDINTI."),
           t("- Dublikatai (tas pats turinys) i archyva keliami TIK viena"
             " karta."),
           "",
           t("## Statistika")]
    grupes = con.execute(
        "SELECT substr(tikslo_kelias, 1, length(tikslo_kelias)"
        " - length(vardas) - 1) AS g, COUNT(*), SUM(dydis) FROM failai"
        " WHERE busena='SUTVARKYTAS' GROUP BY g ORDER BY g").fetchall()
    viso_f = 0
    viso_b = 0
    eil.append("")
    for g, kiek, baitai in grupes:
        viso_f += kiek
        viso_b += baitai or 0
        eil.append(t("- `%s` - %d failu, %s")
                   % (g, kiek, models.dydis_tekstu(baitai or 0)))
    praleista = con.execute(
        "SELECT COUNT(*) FROM failai WHERE busena='PRALEISTAS'"
    ).fetchone()[0]
    eil += ["",
            t("Is viso: **%d failu, %s**; praleista (dubliai/jau"
              " buvo): %d.") % (viso_f, models.dydis_tekstu(viso_b),
                                praleista)]

    # "Sia diena pries X metu" - is dayid, nulis papildomos kainos
    siandien = date.today()
    metai_su_kadrais = []
    for (d,) in con.execute(
            "SELECT DISTINCT dayid FROM failai WHERE dayid IS NOT NULL"):
        try:
            dt = date.fromordinal(d)
        except (ValueError, OverflowError):
            continue
        if (dt.month, dt.day) == (siandien.month, siandien.day) \
                and dt.year < siandien.year:
            metai_su_kadrais.append(dt.year)
    if metai_su_kadrais:
        eil += ["",
                t("## Sia diena pries X metu"),
                "",
                t("Sios dienos kadru turite is: %s.") % ", ".join(
                    str(m) for m in sorted(metai_su_kadrais))]

    eil += ["",
            t("Pilna atsaukimo istorija - [UNDO_ZURNALAS.md]"
              "(UNDO_ZURNALAS.md). Programoje mygtukas"
              " \"UNDO - grazinti viska atgal\" veikia bet kada."),
            ""]
    kelias = Path(tikslo_saknis) / "KAIP_SUTVARKYTA.md"
    kelias.write_text("\n".join(eil), encoding="utf-8")
    return kelias


def undo_zurnalas_md(con, tikslo_saknis, riba=5000):
    """Zmogui skaitomas UNDO zurnalas archyvo saknyje."""
    eil = [t("# UNDO zurnalas - kas is kur atkeliavo"),
           "",
           t("| Laikas | Rezimas | Is kur | I kur |"),
           "|---|---|---|---|"]
    eiles = con.execute(
        "SELECT laikas, rezimas, is_kur, i_kur FROM undo WHERE atstatyta=0"
        " ORDER BY id LIMIT ?", (riba + 1,)).fetchall()
    for laikas, rezimas, is_kur, i_kur in eiles[:riba]:
        eil.append("| %s | %s | %s | %s |" % (laikas, rezimas, is_kur,
                                              i_kur))
    if len(eiles) > riba:
        eil.append("")
        eil.append(t("(rodoma pirmi %d irasu; pilnas sarasas -"
                     " indeksas.db undo lenteleje)") % riba)
    kelias = Path(tikslo_saknis) / "UNDO_ZURNALAS.md"
    kelias.write_text("\n".join(eil), encoding="utf-8")
    return kelias


def kopiju_info(con, riba=4):
    """Kiek failu GALIMAI kartojasi ir kiek vietos jie uzima (spr. 27b).

    Grazina (kiek, baitai) arba None, jei kopiju maziau uz riba. TEKSTO
    CIA NEBERA (kliurka 13, Roberto radinys 2026-08-23: sakinys buvo
    kietai lietuviskas ir EN vartotojui rodydavosi lietuviskai) - teksta
    formuoja GUI per t(), o sis modulis lieka Zero-Qt ir be kalbu.

    A1 hash nuemus (spr. 27, 2026-08-29) indeksavimas turinio nebeskaito,
    tad tikslaus hash cia nebera - skaiciuojame IVERTI pagal vienoda DYDI
    (ta pati SDF pirmos fazes logika: same-size = kandidatai). Langas
    informacinis, tekstas sako "~galimai"; tikra baitas-i-baita patikra
    lieka vykdyme (tvarkytojas.vykdyti hash garantija).

    Skaiciuojame PERTEKLIU: kiekvienoje vienodo dydzio grupeje viena
    kopija keliaus i archyva, likusios (kiek - 1) bus praleistos.
    """
    eil = con.execute(
        "SELECT COALESCE(SUM(kiek - 1), 0), COALESCE(SUM(baitai), 0) FROM"
        " (SELECT COUNT(*) AS kiek, (COUNT(*) - 1) * dydis AS baitai"
        "  FROM failai WHERE dydis > 0 AND busena IN"
        "  ('SUINDEKSUOTAS','SUPLANUOTAS') GROUP BY dydis HAVING kiek > 1)"
    ).fetchone()
    kiek, baitai = int(eil[0] or 0), int(eil[1] or 0)
    if kiek >= riba:
        return kiek, baitai
    return None
