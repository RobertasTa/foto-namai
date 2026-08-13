import sys
sys.path.insert(0, ".")
import skeneris
z = skeneris.zvalgyba(r"..\_poligonas\SAVARTYNAS")
print("failai:", z["failai"], "baitai:", z["baitai"], "praleista:", len(z["praleista"]))
