"""telefonas.py - telefonu aptikimas ir MTP kopija per Shell COM
(v1.0 VINIS - PLANAS 4b2, Roberto sprendimas 2026-08-22).

Konkurentu matavimas 2026-08-28 (MTP_telefono_skaitymas.md): telefono
tiesiogiai neima NE VIENAS is 6 tikrintu irankiu - tai musu isskirtinumas.

Kelias - PowerShell subprocesas su Shell.Application COM: nulis nauju
priklausomybiu, receptas irodytas gyvai 2026-08-13 (_darbal\\
mtp_kopija_xiaomi.ps1, 1137 failai / 4,96 GB, Xiaomi + Honor).

Taisykles:
- I TELEFONA NE VIENO BAITO (Photo Mechanic ardymo taisykle) - tik
  skaitom ir kopijuojam I kompiuteri;
- MTP prieiga ISSKIRTINE - viena programa vienu metu (jei Explorer
  atidarytas ties telefonu, mes jo nematysim);
- idempotencija: failas praleidziamas, jei tiksle jau yra tokiu paciu
  vardu ir dydziu (PM rakto kelias+dydis supaprastinimas - mtime per
  Shell COM nepatikimai pasiekiamas);
- zvalgom ne tik DCIM: skrinsotai ir WhatsApp guli kitur (pamoka Nr. 3).

Aptikimo dalis - mergytes darbas 2026-08-23 (teisejas 41/41), adaptuota.
Zero Qt; niekada nekrenta - klaidos grazina tuscius sarasus/False.
"""

import base64
import csv
import io
import re
import subprocess
import sys

# ------------------------------------------------------------- aptikimas
# (mergytes telefonai.py branduolys; PS uzklausa FIKSUOTA)

_PS_WPD = (
    "Get-PnpDevice -Class WPD | Select-Object Status,FriendlyName,InstanceId"
    " | ConvertTo-Csv -NoTypeInformation"
)
_VID_RE = re.compile(r"VID_([0-9A-Fa-f]{4})")


def ps_argumentai(komanda):
    """PowerShell argumentai su -EncodedCommand (daugiaeiliai skriptai
    su kabutemis keliauja saugiai, be shell'o interpretacijos)."""
    koduota = base64.b64encode(komanda.encode("utf-16-le")).decode("ascii")
    return ["powershell", "-NoProfile", "-NonInteractive",
            "-EncodedCommand", koduota]


def _paleisti_ps(komanda, laikas_s=60.0):
    """PowerShell subprocesas be lango; klaida -> "". Niekada nekrenta."""
    kwargs = {"capture_output": True, "text": True, "timeout": laikas_s,
              "encoding": "utf-8", "errors": "replace"}
    if sys.platform == "win32":
        kwargs["creationflags"] = getattr(subprocess, "CREATE_NO_WINDOW",
                                          0x08000000)
    try:
        proc = subprocess.run(ps_argumentai(komanda), **kwargs)
    except Exception:
        return ""
    # stdout grazinam ir esant klaidos kodui: zvalgybos skriptas pats
    # iseina su exit 1 PO "KLAIDA nerastas" eilutes - zinute svarbesne
    # uz koda (parseriai atlaiko bet koki turini).
    return proc.stdout or ""


def rasti_telefonus(csv_tekstas=None):
    """Prijungti MTP telefonai/kameros: [{vardas, prijungtas}].

    Filtras: tik USB\\ InstanceId (SWD\\WPDBUSENUM = diskai/tomai, ne
    telefonai). csv_tekstas parametras - patikroms be tikro telefono.
    """
    if csv_tekstas is None:
        csv_tekstas = _paleisti_ps(_PS_WPD, laikas_s=15.0)
    sujungta, eile = {}, []
    if not (csv_tekstas or "").strip():
        return []
    try:
        for row in csv.DictReader(io.StringIO(csv_tekstas)):
            try:
                vardas = (row.get("FriendlyName") or "").strip()
                iid = (row.get("InstanceId") or "").strip()
                status = (row.get("Status") or "").strip()
                if not vardas or not iid.startswith("USB\\"):
                    continue
                # Dublikatu sujungimas SU OR (mergytes originalo logika;
                # gyva kliurka 2026-08-28: perjungus USB rezima lieka
                # senas 'Unknown' irasas TUO PACIU id salia naujo 'OK' -
                # pametus OR telefonas dingdavo is saraso).
                raktas = (vardas, iid.rsplit("\\", 1)[-1])
                ok = status.upper() == "OK"
                if raktas in sujungta:
                    if ok:
                        sujungta[raktas]["prijungtas"] = True
                else:
                    sujungta[raktas] = {"vardas": vardas, "prijungtas": ok}
                    eile.append(raktas)
            except Exception:
                continue
    except Exception:
        pass
    rezultatas = [sujungta[k] for k in eile]
    rezultatas.sort(key=lambda d: (not d["prijungtas"], d["vardas"]))
    return [r for r in rezultatas if r["prijungtas"]]


# ------------------------------------------------------------- zvalgyba

# Zinomos medijos vietos (pamoka Nr. 3: NE tik DCIM). Kelias segmentais
# nuo vidines atminties saknies.
ZINOMOS_VIETOS = [
    ("DCIM",),
    ("Pictures",),
    ("Movies",),
    ("Download",),
    ("Android", "media", "com.whatsapp", "WhatsApp", "Media"),
    ("Android", "media", "org.telegram.messenger"),
    ("Android", "media", "com.viber.voip"),
]

_PS_ZVALGYBA_SABLONAS = r'''
$ErrorActionPreference = "SilentlyContinue"
[Console]::OutputEncoding = [System.Text.Encoding]::UTF8
$shell = New-Object -ComObject Shell.Application
$phone = $shell.Namespace(17).Items() | Where-Object {{ $_.Name -eq "{vardas}" }}
if (-not $phone) {{ Write-Output "KLAIDA nerastas"; exit 1 }}
$stores = @($phone.GetFolder.Items())
if ($stores.Count -eq 0) {{ Write-Output "KLAIDA tuscias"; exit 2 }}
foreach ($store in $stores) {{
  $root = $store.GetFolder
  if (-not $root) {{ continue }}
  Write-Output ("ATMINTIS`t" + $store.Name)
  foreach ($kelias in @({keliai})) {{
    $f = $root
    $ok = $true
    foreach ($s in $kelias.Split("/")) {{
      $it = $f.ParseName($s)
      if (-not $it) {{ $ok = $false; break }}
      $f = $it.GetFolder
      if (-not $f) {{ $ok = $false; break }}
    }}
    if ($ok) {{
      $n = @($f.Items()).Count
      Write-Output ("VIETA`t" + $store.Name + "`t" + $kelias + "`t" + $n)
    }}
  }}
}}
Write-Output "BAIGTA"
'''


def zvalgybos_komanda(telefono_vardas):
    """PS komanda zvalgybai (atskirta, kad patikros matytu turini)."""
    keliai = ", ".join('"%s"' % "/".join(v) for v in ZINOMOS_VIETOS)
    return _PS_ZVALGYBA_SABLONAS.format(
        vardas=telefono_vardas.replace('"', ""), keliai=keliai)


def isskirstyti_zvalgyba(tekstas):
    """PS zvalgybos isvestis -> {"atmintys": [...], "vietos": [
    {"atmintis","kelias","kiek"}], "klaida": None|tekstas}."""
    rez = {"atmintys": [], "vietos": [], "klaida": None}
    if not (tekstas or "").strip():
        rez["klaida"] = "tuscia"
        return rez
    baigta = False
    for eil in tekstas.splitlines():
        eil = eil.strip()
        if eil.startswith("KLAIDA"):
            rez["klaida"] = eil.split(" ", 1)[-1]
        elif eil.startswith("ATMINTIS\t"):
            rez["atmintys"].append(eil.split("\t", 1)[1])
        elif eil.startswith("VIETA\t"):
            dalys = eil.split("\t")
            if len(dalys) == 4:
                try:
                    rez["vietos"].append({"atmintis": dalys[1],
                                          "kelias": dalys[2],
                                          "kiek": int(dalys[3])})
                except ValueError:
                    continue
        elif eil == "BAIGTA":
            baigta = True
    if not baigta and rez["klaida"] is None:
        rez["klaida"] = "nutruko"
    return rez


def zvalgyti(telefono_vardas):
    """Gyva zvalgyba (per PS). GUI naudoja is workerio."""
    return isskirstyti_zvalgyba(
        _paleisti_ps(zvalgybos_komanda(telefono_vardas), laikas_s=180.0))


# ---------------------------------------------------------------- kopija

_PS_KOPIJA_SABLONAS = r'''
$ErrorActionPreference = "SilentlyContinue"
[Console]::OutputEncoding = [System.Text.Encoding]::UTF8
$DEST = "{tikslas}"
New-Item -ItemType Directory -Force $DEST | Out-Null
$shell = New-Object -ComObject Shell.Application
$phone = $shell.Namespace(17).Items() | Where-Object {{ $_.Name -eq "{vardas}" }}
if (-not $phone) {{ Write-Output "KLAIDA nerastas"; exit 1 }}

function Kopijuok($folder, $destDir) {{
  New-Item -ItemType Directory -Force $destDir | Out-Null
  $destNs = $shell.Namespace($destDir)
  foreach ($it in @($folder.Items())) {{
    if ($it.IsFolder) {{
      Kopijuok $it.GetFolder (Join-Path $destDir $it.Name)
    }} else {{
      # idempotencija: vardas+dydis jau yra -> praleidziam
      $vietinis = Join-Path $destDir $it.Name
      if ((Test-Path $vietinis) -and
          ((Get-Item $vietinis -Force).Length -eq $it.ExtendedProperty("System.Size"))) {{
        $script:praleista++
      }} else {{
        $destNs.CopyHere($it, 20)
        $script:kopijuota++
      }}
      if ((($script:kopijuota + $script:praleista) % 25) -eq 0) {{
        Write-Output ("PROG`t" + $script:kopijuota + "`t" + $script:praleista)
      }}
    }}
  }}
}}

$script:kopijuota = 0
$script:praleista = 0
foreach ($store in @($phone.GetFolder.Items())) {{
  $root = $store.GetFolder
  if (-not $root) {{ continue }}
  foreach ($kelias in @({keliai})) {{
    $f = $root
    $ok = $true
    foreach ($s in $kelias.Split("/")) {{
      $it = $f.ParseName($s)
      if (-not $it) {{ $ok = $false; break }}
      $f = $it.GetFolder
      if (-not $f) {{ $ok = $false; break }}
    }}
    if ($ok) {{
      Write-Output ("APLANKAS`t" + $kelias)
      Kopijuok $f (Join-Path $DEST ($kelias.Replace("/", "\")))
    }}
  }}
}}
# CopyHere asinchroniskas - laukiam kol failu kiekis tiksle stabilizuosis
$prev = -1
for ($i = 0; $i -lt 240; $i++) {{
  Start-Sleep -Seconds 3
  $dabar = (Get-ChildItem -Recurse -File -Force $DEST | Measure-Object).Count
  if ($dabar -eq $prev) {{ break }}
  $prev = $dabar
  Write-Output ("LAUKIU`t" + $dabar)
}}
$galutinis = (Get-ChildItem -Recurse -File -Force $DEST | Measure-Object).Count
Write-Output ("BAIGTA`t" + $galutinis + "`t" + $script:praleista)
'''


def kopijos_komanda(telefono_vardas, keliai, tikslas):
    """PS komanda kopijai. keliai - segmentu tuple sarasas (kaip
    ZINOMOS_VIETOS elementai) arba 'a/b' tekstai."""
    tekstai = []
    for k in keliai:
        tekstai.append(k if isinstance(k, str) else "/".join(k))
    return _PS_KOPIJA_SABLONAS.format(
        vardas=telefono_vardas.replace('"', ""),
        tikslas=str(tikslas).replace('"', ""),
        keliai=", ".join('"%s"' % t for t in tekstai))


def isskirstyti_kopija(eilute):
    """Viena kopijos PS isvesties eilute -> (tipas, duomenys) arba None.
    Tipai: 'aplankas' (kelias), 'prog' (kopijuota, praleista),
    'laukiu' (kiek), 'baigta' (viso, praleista), 'klaida' (tekstas)."""
    eil = (eilute or "").strip()
    if eil.startswith("APLANKAS\t"):
        return ("aplankas", eil.split("\t", 1)[1])
    if eil.startswith("PROG\t"):
        d = eil.split("\t")
        try:
            return ("prog", (int(d[1]), int(d[2])))
        except (IndexError, ValueError):
            return None
    if eil.startswith("LAUKIU\t"):
        try:
            return ("laukiu", int(eil.split("\t")[1]))
        except (IndexError, ValueError):
            return None
    if eil.startswith("BAIGTA\t"):
        d = eil.split("\t")
        try:
            return ("baigta", (int(d[1]), int(d[2])))
        except (IndexError, ValueError):
            return None
    if eil.startswith("KLAIDA"):
        return ("klaida", eil.split(" ", 1)[-1])
    return None
