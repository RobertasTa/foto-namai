"""lentynos.py - fizines saugyklos tapatybe (E3, PLANAS sprendimas 30).

Lentynos tapatybe = volume serial (raidems E:/F: keiciantis atpazistama
automatiskai) + etikete. Vardas zmogui gyvena DB (indeksas.lentynos);
pervadinti saugu bet kada - tapatybe ant serial. Zero Qt.
"""

import ctypes
import os
import shutil
import sys
from pathlib import Path

from kalba import t

# --- macOS saka (2026-08-29, Roberto "darom ir mak"): tapatybe ne is
# GetVolumeInformationW (jo ten nera), o is diskutil VolumeUUID. Windows
# kelias zemiau NEPALIESTAS. Gyvai ant tikro Mac dar netikrinta - pirmas
# teisejas bus macos_zvalgyba workflow + gyvas Mac testuotojas.


def _mount_point(kelias):
    """Kelio tomo mount point (kylame tevais iki os.path.ismount)."""
    p = Path(kelias).resolve()
    while not os.path.ismount(str(p)):
        if p.parent == p:
            break
        p = p.parent
    return p


def _diskutil_plist(mount):
    import plistlib
    import subprocess
    try:
        r = subprocess.run(["diskutil", "info", "-plist", str(mount)],
                           capture_output=True, timeout=15)
        if r.returncode != 0 or not r.stdout:
            return None
        return plistlib.loads(r.stdout)
    except Exception:
        return None


def _volume_info_darwin(kelias):
    d = _diskutil_plist(_mount_point(kelias))
    if not d:
        return (None, None, None)
    uuid = d.get("VolumeUUID") or d.get("DiskUUID")
    fs = d.get("FilesystemUserVisibleName") or d.get("FilesystemType")
    return (uuid, d.get("VolumeName") or None, fs or None)


def _disko_tipas_darwin(kelias):
    mount = _mount_point(kelias)
    d = _diskutil_plist(mount)
    if not d:
        # diskutil tinklo mountu nepazista - fs tipa sako statvfs/mount
        try:
            import subprocess
            r = subprocess.run(["mount"], capture_output=True, text=True,
                               timeout=10)
            eil = [e for e in r.stdout.splitlines()
                   if " on %s (" % mount in e]
            if eil and any(x in eil[0] for x in
                           ("smbfs", "afpfs", "nfs", "webdav")):
                return "network"
        except Exception:
            pass
        return "kitas"
    if d.get("Internal") and not d.get("Ejectable"):
        return "fixed"
    return "removable"


def volume_info(kelias):
    """Grazina (serial_hex, etikete, fs) tomo, kuriame guli kelias.
    Nepavyko (pvz., UNC be teisiu) -> (None, None, None)."""
    if sys.platform == "darwin":
        return _volume_info_darwin(kelias)
    root = Path(kelias).anchor
    if not root:
        return (None, None, None)
    etikete = ctypes.create_unicode_buffer(261)
    fs = ctypes.create_unicode_buffer(261)
    serial = ctypes.c_uint32()
    try:
        ok = ctypes.windll.kernel32.GetVolumeInformationW(
            str(root), etikete, 261, ctypes.byref(serial),
            None, None, fs, 261)
    except Exception:
        return (None, None, None)
    if not ok:
        return (None, None, None)
    return ("%08X" % serial.value, etikete.value or None, fs.value or None)


def talpa_baitais(kelias):
    try:
        return shutil.disk_usage(str(kelias)).total
    except OSError:
        return None


def _usb_magistrale(root):
    """Ar tomas gyvena ant USB magistrales? USB HDD deziu spastas
    (rastas gyvai 2026-08-08 su Roberto ADATA NH13): GetDriveTypeW
    tokiam grazina DRIVE_FIXED, nors diskas ISORINIS - be sio
    patikrinimo jis gautu vidinio autovarda be lipduko patarimo.
    IOCTL_STORAGE_QUERY_PROPERTY -> STORAGE_DEVICE_DESCRIPTOR.BusType
    (7 = USB); handle atidaromas su desiredAccess=0 - uztenka
    metaduomenu uzklausai, admin teisiu nereikia."""
    INVALID_HANDLE = ctypes.c_void_p(-1).value
    k32 = ctypes.windll.kernel32
    h = k32.CreateFileW("\\\\.\\" + root.rstrip("\\/"), 0, 3, None, 3,
                        0, None)
    if h == INVALID_HANDLE:
        return False
    try:
        # STORAGE_PROPERTY_QUERY: PropertyId=0 (Device), QueryType=0
        uzkl = (ctypes.c_uint32 * 3)(0, 0, 0)
        atsak = ctypes.create_string_buffer(1024)
        grazinta = ctypes.c_uint32(0)
        ok = k32.DeviceIoControl(
            ctypes.c_void_p(h), 0x2D1400,   # IOCTL_STORAGE_QUERY_PROPERTY
            ctypes.byref(uzkl), ctypes.sizeof(uzkl),
            atsak, ctypes.sizeof(atsak), ctypes.byref(grazinta), None)
        if not ok or grazinta.value < 32:
            return False
        # BusType - DWORD ties offsetu 28 (po Version/Size/4xBYTE/5xDWORD)
        bus = int.from_bytes(atsak.raw[28:32], "little")
        return bus == 7                     # BusTypeUsb
    finally:
        k32.CloseHandle(ctypes.c_void_p(h))


def disko_tipas(kelias):
    """'fixed' / 'removable' / 'network' / 'kitas'. 'fixed' reiskia
    TIKRAI vidini diska: USB magistrales tomai (kad ir DRIVE_FIXED
    deze) laikomi 'removable' - jiems galioja isorinio disko
    krikstynos su lipduko patarimu (sprendimai 30/38).
    Roberto verdiktas 2026-08-07: krikstynu dialogas turi prasme TIK
    isimamiems/isoriniams diskams - vidiniam kompiuterio diskui vardas
    sudaromas automatiskai (nuo 2026-08-08 su patvirtinimo dialogu)."""
    if sys.platform == "darwin":
        return _disko_tipas_darwin(kelias)
    root = Path(kelias).anchor
    if not root:
        return "kitas"
    try:
        tipas = ctypes.windll.kernel32.GetDriveTypeW(str(root))
    except Exception:
        return "kitas"
    tipas = {3: "fixed", 2: "removable", 4: "network"}.get(tipas, "kitas")
    if tipas == "fixed":
        try:
            if _usb_magistrale(root):
                return "removable"
        except Exception:
            pass                            # abejones atveju - vidinis
    return tipas


def autovardas_vidinis(kelias):
    """Vidinio disko autovardas be dialogu: 'KOMPOVARDAS diskas C:'."""
    kompas = os.environ.get("COMPUTERNAME")
    if not kompas:
        import platform
        kompas = platform.node().split(".")[0] or "PC"
    if sys.platform == "darwin":
        raide = _mount_point(kelias).name or "/"
    else:
        raide = Path(kelias).anchor.rstrip("\\/")
    if not raide:
        return kompas[:40]
    return t("{} diskas {}").format(kompas, raide)[:40]


def siulomas_vardas(kelias):
    """Krikstynu siulymas (siulo, bet neverczia): etikete arba disko raide."""
    serial, etikete, _ = volume_info(kelias)
    if etikete:
        return etikete[:40]
    if sys.platform == "darwin":
        vardas = _mount_point(kelias).name
        return (vardas[:40] if vardas else "Lentyna")
    root = Path(kelias).anchor.rstrip("\\/")
    if root:
        return ("Diskas " + root)[:40]
    return "Lentyna"
