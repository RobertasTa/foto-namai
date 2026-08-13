"""paieska.py - indekso uzklausos ir issaugotos paieskos (E5, sprendimas 29).

Pure SQL module, no Qt, no network. Only stdlib: sqlite3, json, datetime.

Parase mergyte (lokalus Hermes agentas) pagal _mergyte_e5/UZDUOTIS.md
spec'a, teisejas 47/47 (patikra_e5). Claude perziuros pataisa: filtru
salygos is JOIN ON perkeltos i WHERE (INNER JOIN'ui semantika ta pati,
bet LEFT JOIN'ui butu spastas).

Sauga: visos reiksmes TIK per ? parametrus; LIKE fragmentai ekranuojami
(\\ % _) ir naudojamas ESCAPE - vartotojo "50%" yra pazodinis tekstas,
ne wildcard.
"""

import json
import sqlite3
from datetime import date


def _escape_like(value):
    """Escape LIKE wildcard chars so user input is treated literally."""
    return value.replace('\\', '\\\\').replace('%', '\\%').replace('_', '\\_')


def _build_where(filtrai):
    """Build WHERE clause fragments and parameter list from filters dict.

    Returns (clauses_list, params_list).
    """
    clauses = []
    params = []

    if filtrai.get("data_nuo"):
        ordinal = date.fromisoformat(filtrai["data_nuo"]).toordinal()
        clauses.append("f.dayid >= ?")
        params.append(ordinal)

    if filtrai.get("data_iki"):
        ordinal = date.fromisoformat(filtrai["data_iki"]).toordinal()
        clauses.append("f.dayid <= ?")
        params.append(ordinal)

    if filtrai.get("etikete"):
        escaped = _escape_like(filtrai["etikete"])
        clauses.append("f.renginio_etikete LIKE ? ESCAPE '\\'")
        params.append("%" + escaped + "%")

    if filtrai.get("kamera"):
        escaped = _escape_like(filtrai["kamera"])
        clauses.append("f.kamera LIKE ? ESCAPE '\\'")
        params.append("%" + escaped + "%")

    if filtrai.get("vardas"):
        escaped = _escape_like(filtrai["vardas"])
        clauses.append("f.vardas LIKE ? ESCAPE '\\'")
        params.append("%" + escaped + "%")

    if filtrai.get("tipas"):
        clauses.append("f.turinio_tipas = ?")
        params.append(filtrai["tipas"])

    if filtrai.get("lentyna_id") is not None:
        clauses.append("f.lentyna_id = ?")
        params.append(filtrai["lentyna_id"])

    return clauses, params


def ieskoti(con, filtrai, limit=500, offset=0):
    """Search files with optional filters. Returns list[dict]."""
    cols = (
        "f.id, f.lentyna_id, l.vardas_zmogui AS lentynos_vardas,"
        " l.prijungta, l.volume_serial,"
        " f.santykinis_kelias, f.saltinio_saknis,"
        " f.vardas, f.dydis, f.mtime, f.datetaken,"
        " f.datos_saltinis, f.patikima_data, f.turinio_tipas,"
        " f.renginio_etikete, f.kamera"
    )

    sql = ("SELECT " + cols
           + " FROM failai f JOIN lentynos l ON l.id = f.lentyna_id")

    clauses, params = _build_where(filtrai)
    if clauses:
        sql += " WHERE " + " AND ".join(clauses)

    sql += " ORDER BY f.datetaken IS NULL, f.datetaken DESC, f.id"
    sql += " LIMIT ? OFFSET ?"
    params.extend([limit, offset])

    old_factory = con.row_factory
    con.row_factory = sqlite3.Row
    rows = con.execute(sql, params).fetchall()
    con.row_factory = old_factory

    key_list = [
        "id", "lentyna_id", "lentynos_vardas", "prijungta",
        "volume_serial",
        "santykinis_kelias", "saltinio_saknis", "vardas",
        "dydis", "mtime", "datetaken", "datos_saltinis",
        "patikima_data", "turinio_tipas", "renginio_etikete", "kamera"
    ]

    return [dict((k, row[k]) for k in key_list) for row in rows]


def ieskoti_kiek(con, filtrai):
    """Count matching files. Returns int."""
    clauses, params = _build_where(filtrai)
    sql = "SELECT COUNT(*) FROM failai f JOIN lentynos l ON l.id = f.lentyna_id"
    if clauses:
        sql += " WHERE " + " AND ".join(clauses)

    return con.execute(sql, params).fetchone()[0]


def issaugoti_vaizda(con, vardas, filtrai):
    """Save or update a saved search view. Returns int id."""
    uzklausa = json.dumps(filtrai)

    # Check if a view with this name already exists
    row = con.execute(
        "SELECT id FROM vaizdai WHERE vardas = ?", (vardas,)
    ).fetchone()

    if row:
        vid = row[0]
        con.execute(
            "UPDATE vaizdai SET uzklausa = ? WHERE id = ?",
            (uzklausa, vid)
        )
        con.commit()
        return vid

    cur = con.execute(
        "INSERT INTO vaizdai (vardas, uzklausa) VALUES (?, ?)",
        (vardas, uzklausa)
    )
    con.commit()
    return cur.lastrowid


def vaizdu_sarasas(con):
    """List saved search views. Returns list of (id, vardas) tuples."""
    cur = con.execute("SELECT id, vardas FROM vaizdai ORDER BY vardas")
    return cur.fetchall()


def vaizdo_filtrai(con, vaizdo_id):
    """Get filter dict for a saved view by id. Returns dict or None."""
    row = con.execute(
        "SELECT uzklausa FROM vaizdai WHERE id = ?", (vaizdo_id,)
    ).fetchone()

    if row is None:
        return None

    try:
        return json.loads(row[0])
    except (json.JSONDecodeError, TypeError):
        return None


def trinti_vaizda(con, vaizdo_id):
    """Delete a saved view by id."""
    con.execute("DELETE FROM vaizdai WHERE id = ?", (vaizdo_id,))
    con.commit()
