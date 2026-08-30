; PHOTO home (FOTO namai) - Inno Setup instaliatorius
; Kam: Komi Store ir kiti katalogai priima TIK .exe/.msi (.zip - ne).
; Statyti: ISCC.exe PhotoHome.iss  (leisti is sio katalogo)
;
; SPRENDIMAI:
;  - Pakuojamas ONEDIR aplankas (dist\PhotoHome\ = exe + _internal),
;    sprendimas 15 NEPALIESTAS: langas atsidaro per ~1 s kaip ir buvo.
;    onefile cia ATMESTAS SAMONINGAI - jis kaskart isspakuotu 131 MB i temp
;    ir sulauzytu geleziene laikroduko taisykle butent naujam zmogui.
;  - PrivilegesRequired=lowest -> vartotojo profilis, JOKIO UAC lango.
;    Papildomai: portable jungiklis programoje toliau veikia, nes i savo
;    kataloga rasyti galima (Program Files butu neveikes be admin).
;  - Portable zip release'e LIEKA. Instaliatorius yra PAPILDOMAS kelias.
;  - AppId GUID FIKSUOTAS - NIEKADA nekeisti (kitaip senos versijos liks).

#define AppName      "PHOTO home"
#define AppVersion   "1.1"
#define AppExeName   "PhotoHome.exe"
#define AppUrl       "https://github.com/RobertasTa/foto-namai"

[Setup]
AppId={{F399E43E-F1F1-47BD-A288-83797A922DE1}
AppName={#AppName}
AppVersion={#AppVersion}
AppVerName={#AppName} {#AppVersion}
AppPublisher=Robertas & Claude (AI)
AppPublisherURL={#AppUrl}
AppSupportURL={#AppUrl}/issues
AppUpdatesURL={#AppUrl}/releases
DefaultDirName={autopf}\PHOTO home
DefaultGroupName=PHOTO home
DisableProgramGroupPage=yes
PrivilegesRequired=lowest
; PrivilegesRequiredOverridesAllowed=dialog NENAUDOJAMAS - zr. SDF skripta
; (2026-08-30 gyvas testas: langas issoka net su /VERYSILENT, winget uzstrigtu).
ArchitecturesAllowed=x64compatible
ArchitecturesInstallIn64BitMode=x64compatible
OutputDir=..\dist
OutputBaseFilename=PhotoHome-{#AppVersion}-setup
SetupIconFile=..\foto_namai\ikona.ico
UninstallDisplayIcon={app}\{#AppExeName}
Compression=lzma2/max
SolidCompression=yes
WizardStyle=modern
; LicenseFile SAMONINGAI nenaudojamas - zr. paaiskinima SDF skripte.

[Languages]
; TIK anglu - SAMONINGAI. Instaliatoriaus kalbos turi ATITIKTI programos
; kalbas: PHOTO home moka lietuviskai ir angliskai, daugiau nieko.
; 2026-08-30 Roberto gyvas testas: buvau ideje rusu - rusas butu pasirinkes
; rusiska diegima ir gaves programa, kurios nesupranta.
; Lietuviu Inno Setup rinkinyje nera (29 kalbos, musu tarp ju ne).
; Kai programa ismoks RU/DE - grazinti cia atitinkamas eilutes.
Name: "en"; MessagesFile: "compiler:Default.isl"

[Tasks]
Name: "desktopicon"; Description: "{cm:CreateDesktopIcon}"; GroupDescription: "{cm:AdditionalIcons}"; Flags: unchecked

[Files]
; Visas onedir aplankas: PhotoHome.exe + _internal\ (rekursyviai)
Source: "..\dist\PhotoHome\*"; DestDir: "{app}"; Flags: ignoreversion recursesubdirs createallsubdirs
Source: "..\_publikavimas\foto-namai\LICENSE"; DestDir: "{app}"; DestName: "LICENSE.txt"; Flags: ignoreversion

[Icons]
Name: "{group}\{#AppName}"; Filename: "{app}\{#AppExeName}"
Name: "{autodesktop}\{#AppName}"; Filename: "{app}\{#AppExeName}"; Tasks: desktopicon

[Run]
Filename: "{app}\{#AppExeName}"; Description: "{cm:LaunchProgram,{#AppName}}"; Flags: nowait postinstall skipifsilent

; PASTABA valymui: vartotojo duomenys gyvena %LOCALAPPDATA%\PhotoHome.
; Salinant programa jie NETRINAMI - tai vartotojo archyvo indeksas ir UNDO
; zurnalas. Netycinis ju istrynimas butu tiksliai tai, ko programa zada
; niekada nedaryti.
