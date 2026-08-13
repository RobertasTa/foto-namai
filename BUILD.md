# FOTO namai - statybos receptas (E8)

## Aplinka

- Python 3.13 venv `.venv` (PyQt6 6.11, Pillow 12.3, piexif, pillow-heif,
  PyInstaller 6.21).
- Build VISADA per `python -m PyInstaller` (venv shim'ai luze - seimos
  pamoka) is repo saknies:

```
.venv\Scripts\python.exe -m PyInstaller FotoNamai.spec --noconfirm
```

## Kas gaunasi

`dist\FotoNamai\` - onedir paketas (PLANAS sprendimas 15: NE onefile):

- `FotoNamai.exe` + `_internal\` (DLL, Qt, ikona, README.txt/-en.txt,
  zinynas_vietos.json - visi datas per sys._MEIPASS guard).
- ~131 MB nespausta (PyQt6); zip suspaudzia gerokai.

## Zip flesiukui / Release asset

```
Compress-Archive -Path "dist\FotoNamai" -DestinationPath "dist\FotoNamai-v1.0-win64.zip" -Force
```

Vartotojui: issipakuoji kur nori, leidi FotoNamai.exe. Duomenys -
%LOCALAPPDATA%\FotoNamai; portable rezimas - tuscias
`FotoNamai_portable.txt` SALIA exe (sprendimas 33 - prefiksuotas vardas!).

## Smoke po build'o (privalomas)

1. `dist\FotoNamai\FotoNamai.exe` - langas per ~1-2 s, ikona taskbar'e.
2. "?" -> Apie (versija!) ir Instrukcija (README LT; perjungus kalba - EN).
3. Zvalgyba ant nedidelio aplanko + paieska su miniatiuromis.
4. Jei krenta be pranesimo - perbuild su console=True spec'e ir
   paleisti is cmd (OKF_PyInstaller guard Rule 5).

## Pries Release (is _PUBLIKAVIMO_BUSENA.md ceklisto)

- README.md skrinai daromi TIK release diena ir TIK is to exe, kuris
  keliauja i asset'a (SDF pamoka - skrinai turi atitikti parsisiunciama).
- Galutinis vardas/repo vardas - PLANAS 4b.3 (spresti su Robertu).
- sha256 uzsirasyti PRIES winget manifesta.
