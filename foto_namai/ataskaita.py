"""ataskaita.py - KAIP_SUTVARKYTA.md ir buhalterija (E5; .md DNR spr. 20).

Archyvo saknyje - zmogui skaitomas paaiskinimas: taisykles, statistika,
"sia diena pries X metu" (nulis kainos, smagu), data. Salia - UNDO
zurnalas zmogui. Zero Qt.
"""

from datetime import date, datetime
from pathlib import Path

from indeksas import dayid_i_iso


def _dabar():
    return datetime.now().isoformat(timespec="seconds")


def kaip_sutvarkyta_md(con, tikslo_saknis):
    """Generuoja/atnaujina KAIP_SUTVARKYTA.md archyvo saknyje."""
    eil = ["# KAIP SUTVARKYTA - sio archyvo taisykles",
           "",
           "Sutvarkyta programa **FOTO namai** (Claude's Gifts to the"
           " World).",
           "Atnaujinta: %s" % _dabar(),
           "",
           "## Taisykles",
           "",
           "- Nuotraukos guli pagal data: `Metai\\Menuo` arba"
           " `Metai\\Menuo Renginys` (renginio vardas - is originalaus"
           " aplanko pavadinimo).",
           "- Kiekvienos nuotraukos data nustatyta sia tvarka: EXIF ->"
           " failo vardas -> aplanko vardas -> failo mtime.",
           "- `_SKRINSOTAI` - ekrano nuotraukos (atpazintos be ML: nera"
           " kameros EXIF + ekrano raiska / vardas).",
           "- `_NEPATIKIMOS_DATOS` - failai, kuriu datos saltinis tik"
           " mtime (kopijavimo pedsakas, ne fotografavimo data).",
           "- Neatpazinto turinio failai (0 baitu, netikri .jpg) is vietos"
           " NEJUDINTI.",
           "- Dublikatai (tas pats turinys) i archyva keliami TIK viena"
           " karta.",
           "",
           "## Statistika"]
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
        eil.append("- `%s` - %d failu, %.1f MB" % (g, kiek,
                                                   (baitai or 0) / 1048576))
    praleista = con.execute(
        "SELECT COUNT(*) FROM failai WHERE busena='PRALEISTAS'"
    ).fetchone()[0]
    eil += ["",
            "Is viso: **%d failu, %.2f GB**; praleista (dubliai/jau buvo):"
            " %d." % (viso_f, viso_b / 1073741824, praleista)]

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
                "## Sia diena pries X metu",
                "",
                "Sios dienos kadru turite is: %s." % ", ".join(
                    str(m) for m in sorted(metai_su_kadrais))]

    eil += ["",
            "Pilna atsaukimo istorija - [UNDO_ZURNALAS.md]"
            "(UNDO_ZURNALAS.md). Programoje mygtukas"
            " \"UNDO - grazinti viska atgal\" veikia bet kada.",
            ""]
    kelias = Path(tikslo_saknis) / "KAIP_SUTVARKYTA.md"
    kelias.write_text("\n".join(eil), encoding="utf-8")
    return kelias


def undo_zurnalas_md(con, tikslo_saknis, riba=5000):
    """Zmogui skaitomas UNDO zurnalas archyvo saknyje."""
    eil = ["# UNDO zurnalas - kas is kur atkeliavo",
           "",
           "| Laikas | Rezimas | Is kur | I kur |",
           "|---|---|---|---|"]
    eiles = con.execute(
        "SELECT laikas, rezimas, is_kur, i_kur FROM undo WHERE atstatyta=0"
        " ORDER BY id LIMIT ?", (riba + 1,)).fetchall()
    for laikas, rezimas, is_kur, i_kur in eiles[:riba]:
        eil.append("| %s | %s | %s | %s |" % (laikas, rezimas, is_kur,
                                              i_kur))
    if len(eiles) > riba:
        eil.append("")
        eil.append("(rodoma pirmi %d irasu; pilnas sarasas -"
                   " indeksas.db undo lenteleje)" % riba)
    kelias = Path(tikslo_saknis) / "UNDO_ZURNALAS.md"
    kelias.write_text("\n".join(eil), encoding="utf-8")
    return kelias


def sdf_siulymas(con, riba=4):
    """Mandagus SDF siulymas (spr. 27b): daug vienodo hash failu ->
    rekomenduojam pirma Smart Duplicate Finder. Grazina teksta arba None."""
    dubliu = con.execute(
        "SELECT COALESCE(SUM(kiek - 1), 0) FROM (SELECT COUNT(*) AS kiek"
        " FROM failai WHERE hash IS NOT NULL AND busena IN"
        " ('SUINDEKSUOTAS','SUPLANUOTAS') GROUP BY hash HAVING kiek > 1)"
    ).fetchone()[0]
    if dubliu >= riba:
        return ("Radau ~%d dublikatu. Rekomenduojame pirma perzureti juos"
                " su Smart Duplicate Finder (github.com/RobertasTa/"
                "smart-duplicate-finder), tada tvarkyti archyva." % dubliu)
    return None
