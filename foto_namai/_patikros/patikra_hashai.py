import sys, hashlib, tempfile
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
import hashai
with tempfile.TemporaryDirectory() as tmp:
    f = Path(tmp) / "bandymas.bin"
    f.write_bytes(b"FOTO namai" * 1000)
    laukta = hashlib.sha256(b"FOTO namai" * 1000).hexdigest()
    gauta = hashai.failo_hash(f)
    print("PATIKRA:", "OK" if gauta == laukta else "FAIL (%s != %s)" % (gauta, laukta))
