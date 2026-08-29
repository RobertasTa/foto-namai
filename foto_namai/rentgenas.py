"""rentgenas.py - ARCHYVO RENTGENAS (PLANAS 4f p. 3, VIZIJA v1.0 p. 1).

A pakopos veidas: kiek failu, is kur datos (sluoksniu derlius), kiek be
patikimos datos (kelias i _UNDATED), LINIJA LAIKE ismatuota SIAME
archyve ("nuo ~YYYY tavo datos patikimos") ir praleisti backup
katalogai MATOMAI (masto egzamino V2 verdiktas 2026-08-29: gyvame
diske ju buvo 56 - zmogus turi zinoti, ko neperziurejom).

Nulines rizikos ataskaita: nieko nekilnoja, tik skaito indeksa.
Zero Qt - GUI langa apvynios gui_langas, tekstas formuojamas cia
per t() (kliurka 16: zmogui skirtas tekstas - jo kalba).
"""

import models
from kalba import t

# Metai su maziau kadru - triuksmas (pavieniai skenai/parsisiuntimai),
# i linijos laike sprendima ju netraukiam, lenteleje vis tiek rodom.
MIN_METU_IMTIS = 20
# Patikimu datu dalis, nuo kurios metai laikomi "patikimais".
LINIJOS_SLENKSTIS = 0.7


def duomenys(con):
    """Rentgeno skaiciai is indekso. Grazina dict (Zero Qt, be teksto)."""
    viso, baitai = con.execute(
        "SELECT COUNT(*), COALESCE(SUM(dydis), 0) FROM failai").fetchone()
    lentynos = con.execute(
        "SELECT l.vardas_zmogui, COUNT(f.id), COALESCE(SUM(f.dydis), 0)"
        " FROM lentynos l LEFT JOIN failai f ON f.lentyna_id = l.id"
        " GROUP BY l.id ORDER BY l.id").fetchall()
    sluoksniai = con.execute(
        "SELECT COALESCE(datos_saltinis, '(nera)'), COUNT(*) FROM failai"
        " GROUP BY 1 ORDER BY 2 DESC").fetchall()
    bedaciu = con.execute(
        "SELECT COUNT(*) FROM failai WHERE datetaken IS NULL"
        " OR COALESCE(patikima_data, 0) = 0").fetchone()[0]
    neatpazinta = con.execute(
        "SELECT COUNT(*) FROM failai WHERE turinio_tipas = 'neatpazintas'"
    ).fetchone()[0]
    metai = con.execute(
        "SELECT CAST(substr(datetaken, 1, 4) AS INTEGER) AS m, COUNT(*),"
        " SUM(CASE WHEN patikima_data = 1 THEN 1 ELSE 0 END)"
        " FROM failai WHERE datetaken IS NOT NULL"
        " GROUP BY m ORDER BY m").fetchall()
    return {"viso": viso, "baitai": baitai, "lentynos": lentynos,
            "sluoksniai": sluoksniai, "bedaciu": bedaciu,
            "neatpazinta": neatpazinta, "metai": metai,
            "linija_nuo": linija_nuo(metai)}


def linija_nuo(metai):
    """LINIJA LAIKE: anksciausi metai, nuo kuriu VISI velesni metai su
    pakankama imtimi (>= MIN_METU_IMTIS kadru) turi >= LINIJOS_SLENKSTIS
    patikimu datu. None - tokios ribos archyve nera (arba imtys per
    mazos). metai = [(metai, kiek, patikimu), ...] didejancia tvarka."""
    imtys = [(m, kiek, pat) for m, kiek, pat in metai
             if kiek >= MIN_METU_IMTIS and m is not None]
    for i, (m, _, _) in enumerate(imtys):
        if all(pat / kiek >= LINIJOS_SLENKSTIS
               for _, kiek, pat in imtys[i:]):
            return m
    return None


def ataskaita_md(con, praleisti=None):
    """KAS_TAVO_ARCHYVE ataskaitos tekstas (markdown, vartotojo kalba).

    praleisti - [(kelias, priezastis), ...] is ka tik ivykusio
    indeksavimo (skeneris ju i DB neraso); None/[] - skyrius
    praleidziamas.
    """
    d = duomenys(con)
    viso = d["viso"]
    eil = [t("# KAS TAVO ARCHYVE - rentgeno ataskaita"),
           "",
           t("Programa: PHOTO home (FOTO namai). Nieko nekilnojau -"
             " tik perskaiciau ir suskaiciavau."),
           "",
           t("## Kiek ir kur"),
           ""]
    eil.append(t("- Is viso indekse: **%d failu, %s**.")
               % (viso, models.dydis_tekstu(d["baitai"])))
    for vardas, kiek, baitai in d["lentynos"]:
        eil.append(t("- Lentyna `%s`: %d failu, %s.")
                   % (vardas, kiek, models.dydis_tekstu(baitai)))
    if d["neatpazinta"]:
        eil.append(t("- Neatpazinto turinio (0 baitu, netikri .jpg):"
                     " %d - ju nejudinsiu.") % d["neatpazinta"])

    eil += ["", t("## Is kur tavo datos (sluoksniu derlius)"), ""]
    for salt, kiek in d["sluoksniai"]:
        eil.append("- `%-12s` %8d  (%.1f %%)"
                   % (salt, kiek, kiek * 100.0 / viso if viso else 0))
    eil += ["",
            t("BE PATIKIMOS DATOS (kelias i _UNDATED): **%d (%.1f %%)**."
              " Tai ne siukslynas - tai darbo zona: failai sveiki, tik ju"
              " fotografavimo data dar neissiaiskinta.")
            % (d["bedaciu"], d["bedaciu"] * 100.0 / viso if viso else 0)]

    eil += ["", t("## Linija laike"), ""]
    if d["linija_nuo"] is not None:
        eil.append(t("**Nuo ~%d tavo datos patikimos.** Senesni kadrai -"
                     " priesistore: ten datu metaduomenys reti, ir kaip"
                     " tik ten programa dirba labiausiai.")
                   % d["linija_nuo"])
    else:
        eil.append(t("Aiskios ribos, nuo kada datos patikimos, siame"
                     " archyve nesimato - patikimu datu dalis svyruoja."))
    eil += ["", t("| Metai | Kadru | Patikima data |"), "|---|---|---|"]
    for m, kiek, pat in d["metai"]:
        eil.append("| %s | %d | %.0f %% |"
                   % (m, kiek, pat * 100.0 / kiek if kiek else 0))

    if praleisti:
        eil += ["", t("## Ko neperziurejau (saugikliai)"), ""]
        eil.append(t("Sie katalogai praleisti TYCIA (backup/kopiju"
                     " pasaulis, sisteminiai, nuorodos) - jei nori juos"
                     " itraukti, pridek kaip atskira saltini:"))
        eil.append("")
        for kelias, priezastis in praleisti[:200]:
            eil.append("- `%s` (%s)" % (kelias, priezastis))
        if len(praleisti) > 200:
            eil.append(t("- ... ir dar %d.") % (len(praleisti) - 200))

    eil += ["",
            t("Ataskaita sukurta A pakopoje (zvalgyba): ne vienas failas"
              " nepajudintas. Tvarkymas (B pakopa) - tik tavo ranka, su"
              " UNDO."),
            ""]
    return "\n".join(eil)
