# patikra_telefonas.py - v1.0 VINIS: telefono aptikimas/zvalgyba/kopija.
#
# Gyvo telefono patikroje NERA (Roberto ratas bus atskirai) - tikrinam
# visa logika su INJEKTUOTOMIS PS isvestimis (dukrytes teisejo receptas):
# aptikimo filtrai, zvalgybos/kopijos parseriai, PS komandu turinys,
# TelefonoDialogas struktura ir visu nauju tekstu EN poros.
# LEISTI is foto_namai: <venv python> -u _patikros\patikra_telefonas.py

import os
import sys
from pathlib import Path

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import kalba       # noqa: E402
import telefonas   # noqa: E402

KLAIDOS = []


def chk(pavadinimas, salyga, detale=""):
    if salyga:
        print("  OK   %s" % pavadinimas)
    else:
        KLAIDOS.append(pavadinimas)
        print("  FAIL %s %s" % (pavadinimas, str(detale)[:90]))


print("== Aptikimas (injektuotas WPD CSV) ==")
CSV = '"Status","FriendlyName","InstanceId"\r\n' \
      '"OK","Xiaomi 12T Pro","USB\\VID_2717&PID_FF40\\ABC123"\r\n' \
      '"OK","Xiaomi 12T Pro","USB\\VID_2717&PID_FF40\\ABC123"\r\n' \
      '"Unknown","HONOR 6X","USB\\VID_12D1&PID_107E\\XYZ"\r\n' \
      '"OK","ADATA NH13","SWD\\WPDBUSENUM\\_??_USBSTOR#Disk"\r\n'
rasta = telefonas.rasti_telefonus(CSV)
chk("vienas_telefonas", len(rasta) == 1, rasta)
chk("vardas", rasta and rasta[0]["vardas"] == "Xiaomi 12T Pro", rasta)
chk("diskas_isfiltruotas", all("ADATA" not in r["vardas"] for r in rasta))
chk("neprijungtas_isfiltruotas",
    all("HONOR" not in r["vardas"] for r in rasta))
chk("tuscia_tuscia", telefonas.rasti_telefonus("") == [])
chk("siuksles_tuscia", telefonas.rasti_telefonus("ne csv \x00 tekstas") == [])

print("== Zvalgybos komanda ir parseris ==")
kom = telefonas.zvalgybos_komanda('Xiaomi "12T"')
chk("komandoje_vardas_be_kabuciu", 'Xiaomi 12T' in kom and '""' not in kom)
chk("komandoje_dcim", '"DCIM"' in kom)
chk("komandoje_whatsapp", "com.whatsapp" in kom)
IS = ("ATMINTIS\tInternal storage\n"
      "VIETA\tInternal storage\tDCIM\t2\n"
      "VIETA\tInternal storage\tPictures\t15\n"
      "VIETA\tInternal storage\tAndroid/media/com.whatsapp/WhatsApp/Media\t3\n"
      "BAIGTA\n")
z = telefonas.isskirstyti_zvalgyba(IS)
chk("zvalgyba_atmintys", z["atmintys"] == ["Internal storage"], z)
chk("zvalgyba_vietos", len(z["vietos"]) == 3 and
    z["vietos"][1] == {"atmintis": "Internal storage",
                       "kelias": "Pictures", "kiek": 15}, z)
chk("zvalgyba_be_klaidos", z["klaida"] is None, z)
chk("zvalgyba_klaida", telefonas.isskirstyti_zvalgyba(
    "KLAIDA nerastas\n")["klaida"] == "nerastas")
chk("zvalgyba_nutruko", telefonas.isskirstyti_zvalgyba(
    "ATMINTIS\tX\n")["klaida"] == "nutruko")
chk("zvalgyba_tuscia", telefonas.isskirstyti_zvalgyba("")["klaida"]
    == "tuscia")

print("== Kopijos komanda ir parseris ==")
kom = telefonas.kopijos_komanda("Xiaomi 12T Pro",
                                [("DCIM",), "Pictures/Screenshots"],
                                r"C:\Tikslas")
chk("kopija_tikslas", r'C:\Tikslas' in kom)
chk("kopija_keliai", '"DCIM"' in kom and '"Pictures/Screenshots"' in kom)
chk("kopija_idempotencija", "System.Size" in kom and "Test-Path" in kom)
chk("parse_aplankas", telefonas.isskirstyti_kopija("APLANKAS\tDCIM")
    == ("aplankas", "DCIM"))
chk("parse_prog", telefonas.isskirstyti_kopija("PROG\t50\t25")
    == ("prog", (50, 25)))
chk("parse_laukiu", telefonas.isskirstyti_kopija("LAUKIU\t120")
    == ("laukiu", 120))
chk("parse_baigta", telefonas.isskirstyti_kopija("BAIGTA\t991\t102")
    == ("baigta", (991, 102)))
chk("parse_klaida", telefonas.isskirstyti_kopija("KLAIDA nerastas")
    == ("klaida", "nerastas"))
chk("parse_siuksle", telefonas.isskirstyti_kopija("bet koks tekstas")
    is None)

print("== PS argumentai (EncodedCommand) ==")
arg = telefonas.ps_argumentai("Write-Output \"labas\"")
chk("encoded_command", "-EncodedCommand" in arg and len(arg) == 5, arg)

print("== GUI: TelefonoDialogas ir gido mygtukai ==")
from PyQt6.QtWidgets import QApplication   # noqa: E402
import gui_langas                          # noqa: E402

app = QApplication.instance() or QApplication([])
VIETOS = [{"atmintis": "Internal storage", "kelias": "DCIM", "kiek": 850},
          {"atmintis": "Internal storage",
           "kelias": "Pictures/Screenshots", "kiek": 39}]
dlg = gui_langas.TelefonoDialogas("Xiaomi 12T Pro", VIETOS)
chk("dialogo_varneles", len(dlg._varneles) == 2)
chk("dialogo_pazymeta", dlg.pasirinkti()
    == ["DCIM", "Pictures/Screenshots"])
chk("dialogo_siulymas", "Xiaomi 12T Pro" in dlg.tikslas()
    and "Pictures" in dlg.tikslas(), dlg.tikslas())
dlg._varneles[0].setChecked(False)
chk("dialogo_atzymejimas", dlg.pasirinkti() == ["Pictures/Screenshots"])
dlg.deleteLater()

print("== KLIURKA 26: pakartotine kopija nedubliuoja saltinio ==")
import tempfile                            # noqa: E402

with tempfile.TemporaryDirectory() as tmp:
    win = gui_langas.MainWindow(db_kelias=Path(tmp) / "i.db",
                                testinis=True)
    pries = win._medis.topLevelItemCount()
    win._telefono_vardas = "Xiaomi 12T Pro"
    win._telefono_tikslas = str(Path(tmp) / "Archyvas")
    win._on_telefono_kopija_done((1242, 0))
    win._on_telefono_kopija_done((1242, 1242))
    po = win._medis.topLevelItemCount()
    chk("saltinis_pridetas_karta", po == pries + 1, (pries, po))
    win.close()

print("== Nauju tekstu EN poros (kliurkos 13/16 dvasia) ==")
raktai = [
    "Jungti telefona", "Ieskomas telefonas", "Telefono nerandu",
    "Klausti DI", "Paimti is telefono", "Kopijuojama is telefono",
    "Telefono kopija atsaukta.", "Kopijuojama: {}",
    "nukopijuota {}, praleista {}", "Parinkti...",
    "Ka kopijuoti (rastos nuotrauku vietos):",
    "I kuri aplanka kompiuteryje:",
]
sena = kalba.LANG
kalba.LANG = "en"
for r in raktai:
    chk("EN: " + r[:36], kalba.t(r) != r, "liko lietuviskas")
kalba.LANG = sena

if KLAIDOS:
    print("PATIKRA RAUDONA: %d klaidos" % len(KLAIDOS))
    sys.exit(1)
print("PATIKRA ZALIA (34/34)")
