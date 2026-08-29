"""worker.py - QThread darbininkai (E3; valytuvo receptas, sprendimas 22).

GELEZINE taisykle (sprendimas 11): kiekvienas veiksmas >2 s eina per
darbininka + MM:SS + progresas + atsaukimas.

OKF threading guard'u taisykles, kuriu LAIKOMES:
- signalai gyvena WORKERIO klaseje; worker->GUI jungtys TIK i bound
  QObject metodus (ne lambda/closure!);
- GUI reiksmes paduodamos KONSTRUKTORIUJE (snapshot pagrindineje gijoje);
- payload per pyqtSignal(object) su atsietais dict/tuple;
- sqlite jungtis gimsta run() VIDUJE - darbininko gijoje (OKF_sqlite3 1);
- gyvavimo ciklas (moveToThread, quit, deleteLater, nuorodos ant self,
  jokio nulinimo) - GUI puseje pagal pyqt6_threading_guard recepta.
"""

import sqlite3
from pathlib import Path

from PyQt6.QtCore import QObject, pyqtSignal, pyqtSlot

import ataskaita
import indeksas
from kalba import t
import indeksavimas
import miniaturos
import miniatiuru_sandelis as msand
import paieska
import rentgenas
import skeneris
import telefonas
import tvarkytojas


class ZvalgybosWorker(QObject):
    """Faze 1 pazymetiems saltiniams: kiekiai/GB be turinio skaitymo."""

    vienas = pyqtSignal(object)      # (saltinio_id, {"failai","baitai","praleista_n"})
    done = pyqtSignal(object)        # visu suvestine dict
    error_signal = pyqtSignal(str)

    def __init__(self, saltiniai):
        """saltiniai: [(saltinio_id, kelias_str)] - snapshot is GUI."""
        super().__init__()
        self._saltiniai = saltiniai
        self._stop = False

    def stop(self):
        self._stop = True

    @pyqtSlot()
    def run(self):
        try:
            viso = {}
            for sid, kelias in self._saltiniai:
                if self._stop:
                    break
                z = skeneris.zvalgyba(kelias, stop=lambda: self._stop)
                rez = {"failai": z["failai"], "baitai": z["baitai"],
                       "medijos_failai": z["medijos_failai"],
                       "medijos_baitai": z["medijos_baitai"],
                       "praleista_n": len(z["praleista"])}
                viso[sid] = rez
                self.vienas.emit((sid, rez))
            self.done.emit(viso)
        except Exception as e:
            self.error_signal.emit(str(e))


class IndeksavimoWorker(QObject):
    """Faze 2: pilnas pazymetu saltiniu indeksavimas i indeksas.db.

    saltiniai: [{"kelias","serial","vardas","etikete","fs","talpa"}] -
    lentynu krikstynos jau ivykusios GUI gijoje (dialogai ne cia!).
    """

    zurnalas = pyqtSignal(str)
    progresas = pyqtSignal(str)
    done = pyqtSignal(object)   # (suvestine, kopiju_info, rentgeno_md)
    error_signal = pyqtSignal(str)

    def __init__(self, db_kelias, saltiniai):
        super().__init__()
        self._db_kelias = str(db_kelias)
        self._saltiniai = saltiniai
        self._stop = False

    def stop(self):
        self._stop = True

    @pyqtSlot()
    def run(self):
        con = None
        try:
            con = indeksas.atidaryti(self._db_kelias)   # gimsta SIOJE gijoje
            # UX slifas 2026-08-13: vienkartines migracijos nebetylios
            n_migr = indeksas.pasiimti_migraciju_valymus()
            if n_migr:
                self.zurnalas.emit(t("Vienkartine bazes migracija:"
                                     " sutvarkyta {} irasu")
                                   .format(n_migr))
            suvestine = []
            praleisti = []   # rentgenui: (kelias, priezastis) is visu saltiniu
            for s in self._saltiniai:
                if self._stop:
                    break
                lid = indeksas.registruoti_lentyna(
                    con, s["serial"], s["vardas"], etikete=s.get("etikete"),
                    fs=s.get("fs"), talpa_baitais=s.get("talpa"))
                self.zurnalas.emit("[%s] %s" % (s["vardas"], s["kelias"]))

                def _prog(n, v=s["vardas"]):
                    self.progresas.emit("%s: %d" % (v, n))

                stat = indeksavimas.indeksuoti(
                    s["kelias"], con, lid, self._db_kelias,
                    stop=lambda: self._stop, progress=_prog)
                suvestine.append((s["vardas"], {
                    "indeksuota": stat["indeksuota"],
                    "nepakite": stat["nepakite_praleista"],
                    "neatpazinta": stat["neatpazinta"],
                    "ne_medija": stat["ne_medija"],
                    "praleista_n": len(stat["praleista"]),
                    "kaimynyste": stat.get("kaimynyste", 0),
                    "partijos": stat.get("partijos", 0),
                }))
                praleisti.extend(stat["praleista"])
            # 4e p. 2 (2026-08-28): kopiju suvestine jau A pakopos gale -
            # zmogus i SDF nueina PRIES kraustymasi, ne pusiaukeleje.
            # 4f p. 3 (2026-08-29): + ARCHYVO RENTGENAS - A pakopos
            # veidas; tekstas formuojamas cia, darbininko gijoje.
            rentgeno_md = rentgenas.ataskaita_md(con, praleisti) \
                if suvestine else None
            self.done.emit((suvestine, ataskaita.kopiju_info(con),
                            rentgeno_md))
        except indeksavimas.DiskoSargoKlaida as e:
            self.error_signal.emit("DISKO SARGAS: " + str(e))
        except Exception as e:
            self.error_signal.emit(str(e))
        finally:
            if con is not None:
                con.close()


class PlanavimoWorker(QObject):
    """E4 pirmas zingsnis fone: Live poros + grupiu pasiulymai is indekso."""

    done = pyqtSignal(object)        # grupiu sarasas dialogui
    error_signal = pyqtSignal(str)

    def __init__(self, db_kelias):
        super().__init__()
        self._db_kelias = str(db_kelias)
        self._stop = False

    def stop(self):
        self._stop = True

    @pyqtSlot()
    def run(self):
        con = None
        try:
            con = indeksas.atidaryti(self._db_kelias)
            tvarkytojas.suporuoti_live(con)
            grupes = tvarkytojas.siulyti_plana(con)
            self.done.emit((grupes, ataskaita.kopiju_info(con)))
        except Exception as e:
            self.error_signal.emit(str(e))
        finally:
            if con is not None:
                con.close()


class VykdymoWorker(QObject):
    """E4 vykdymas: patvirtintos grupes -> kopijavimas/perkelimas su UNDO."""

    progresas = pyqtSignal(object)   # stat dict
    done = pyqtSignal(object)        # galutinis stat
    error_signal = pyqtSignal(str)

    def __init__(self, db_kelias, tikslo_saknis, grupes, rezimas):
        super().__init__()
        self._db_kelias = str(db_kelias)
        self._tikslas = str(tikslo_saknis)
        self._grupes = list(grupes) if grupes is not None else None
        self._rezimas = rezimas
        self._stop = False

    def stop(self):
        self._stop = True

    @pyqtSlot()
    def run(self):
        con = None
        try:
            con = indeksas.atidaryti(self._db_kelias)
            tvarkytojas.patvirtinti_plana(con, self._grupes)
            stat = tvarkytojas.vykdyti(
                con, self._db_kelias, self._tikslas,
                rezimas=self._rezimas, stop=lambda: self._stop,
                progress=self.progresas.emit)
            # .md DNR (spr. 20): ataskaitos archyvo saknyje po vykdymo
            ataskaita.kaip_sutvarkyta_md(con, self._tikslas)
            ataskaita.undo_zurnalas_md(con, self._tikslas)
            self.done.emit(stat)
        except indeksavimas.DiskoSargoKlaida as e:
            self.error_signal.emit("DISKO SARGAS: " + str(e))
        except Exception as e:
            self.error_signal.emit(str(e))
        finally:
            if con is not None:
                con.close()


class PaieskosWorker(QObject):
    """E5: indekso uzklausa fone read-only jungtimi (sprendimas 29)."""

    done = pyqtSignal(object)        # (eiles, kiek_viso)
    error_signal = pyqtSignal(str)

    def __init__(self, db_kelias, filtrai, limit=500):
        super().__init__()
        self._db_kelias = str(db_kelias)
        self._filtrai = dict(filtrai)
        self._limit = limit
        self._stop = False

    def stop(self):
        self._stop = True

    @pyqtSlot()
    def run(self):
        con = None
        try:
            con = indeksas.atidaryti_ro(self._db_kelias)
            eiles = paieska.ieskoti(con, self._filtrai, limit=self._limit)
            kiek = paieska.ieskoti_kiek(con, self._filtrai)
            self.done.emit((eiles, kiek))
        except Exception as e:
            self.error_signal.emit(str(e))
        finally:
            if con is not None:
                con.close()


class MiniatiuruWorker(QObject):
    """Rodomu rezultatu miniatiuros (spr. 14 -> spr. 45 KARTOTEKA):
    PIRMA ziurima i sandeli (todel atjungtos lentynos irgi rodo vaizda!),
    o miss'as prijungtame diske gaminamas ir IS KARTO idedamas i sandeli -
    rodymas pats pildo kartoteka. Payload dabar JPEG BYTES, ne kelio str
    (2026-08-29)."""

    vienas = pyqtSignal(object)      # (fileid, jpeg_bytes | None)
    progresas = pyqtSignal(str)
    done = pyqtSignal(object)        # kiek apdorota
    error_signal = pyqtSignal(str)

    def __init__(self, uzduotys, sandelio_db=None):
        """uzduotys: [(fileid, abs_kelias_str|None, mtime)] - snapshot is
        GUI (kelias None/nesamas = atjungta lentyna, rodom tik is sandelio).
        sandelio_db - perrasymas patikroms."""
        super().__init__()
        self._uzduotys = list(uzduotys)
        self._sandelio_db = sandelio_db
        self._stop = False

    def stop(self):
        self._stop = True

    @pyqtSlot()
    def run(self):
        try:
            sand = msand.atidaryti(self._sandelio_db)  # sitos gijos jungtis
            n = 0
            try:
                for fileid, kelias, mtime in self._uzduotys:
                    if self._stop:
                        break
                    b = msand.gauti(sand, fileid, mtime)
                    if b is None and kelias:
                        p = Path(kelias)
                        if p.is_file():
                            try:
                                with open(p, "rb") as f:
                                    b = msand.is_bytes(f.read())
                            except OSError:
                                b = None
                            if b:
                                # Uzrakintas sandelis (fonas raso) NIEKADA
                                # nezlugdo RODYMO - miniatiura vis tiek
                                # parodoma, o irasys fonas savo ruoztu
                                try:
                                    msand.irasyti(sand, fileid, mtime, b)
                                except sqlite3.OperationalError:
                                    pass
                    n += 1
                    self.vienas.emit((fileid, b))
                    if n % 20 == 0:
                        try:
                            sand.commit()
                        except sqlite3.OperationalError:
                            pass
                        self.progresas.emit(str(n))
                try:
                    sand.commit()
                except sqlite3.OperationalError:
                    pass
            finally:
                sand.close()
            self.done.emit(n)
        except Exception as e:
            self.error_signal.emit(str(e))


class KartotekosFonas(QObject):
    """A2 FONAS (spr. 45 + spr. 27 "vieno skaitymo"): tyliai pildo
    kartotekos sandeli visu indekso vaizdu miniatiuromis, kad atjungus
    diska kartoteka jau butu pilna. Dirba tik su PRIJUNGTOMIS lentynomis
    (saltinio saknis pasiekiama); nepavykusius (sugadinti/dingę failai)
    isimena sesijai, kad nesisuktu ratu. Gyvena ATSKIROJE gijoje nuo
    pagrindinio worker'iu slot'o - paieskos/skenai jo nelaukia.

    Efektyvumas: vienas kursorius per failai.id (ne pilnas anti-join kas
    partija) + turimu miniatiuru aibe RAM'e, pildoma rasant."""

    progresas = pyqtSignal(str)      # "+N" kas 1000
    done = pyqtSignal(object)        # kiek pagaminta si karta
    error_signal = pyqtSignal(str)

    def __init__(self, indekso_db, sandelio_db=None, partija=300):
        super().__init__()
        self._idx_db = str(indekso_db)
        self._sandelio_db = sandelio_db
        self._partija = partija
        self._stop = False

    def stop(self):
        self._stop = True

    @pyqtSlot()
    def run(self):
        try:
            idx = sqlite3.connect("file:%s?mode=ro" % self._idx_db,
                                  uri=True)
            sand = msand.atidaryti(self._sandelio_db)
            pagaminta = 0
            try:
                turimi = {fid: mt for fid, mt in sand.execute(
                    "SELECT fileid, mtime FROM miniatiuros")}
                q = ("SELECT id, saltinio_saknis, santykinis_kelias, mtime "
                     "FROM failai WHERE id > ? AND turinio_tipas IN (%s) "
                     "ORDER BY id LIMIT ?"
                     % ",".join("?" * len(msand.VAIZDO_TIPAI)))
                pask_id = 0
                gyvos_saknys = {}    # saknis -> bool (vienas exists per saknį)
                while not self._stop:
                    eiles = idx.execute(
                        q, (pask_id, *msand.VAIZDO_TIPAI,
                            self._partija)).fetchall()
                    if not eiles:
                        break
                    for fid, saknis, kelias, mt in eiles:
                        pask_id = fid
                        if self._stop:
                            break
                        senas = turimi.get(fid)
                        if senas is not None and abs(senas - mt) <= 2.0:
                            continue
                        gyva = gyvos_saknys.get(saknis)
                        if gyva is None:
                            gyva = Path(saknis).exists()
                            gyvos_saknys[saknis] = gyva
                        if not gyva:
                            continue        # atjungta lentyna - kita karta
                        try:
                            with open(Path(saknis) / kelias, "rb") as f:
                                b = msand.is_bytes(f.read())
                        except OSError:
                            b = None
                        if b is None:
                            turimi[fid] = mt   # sesijos "nepavyko" zyme
                            continue
                        msand.irasyti(sand, fid, mt, b)
                        turimi[fid] = mt
                        pagaminta += 1
                        if pagaminta % 200 == 0:
                            sand.commit()
                        if pagaminta % 1000 == 0:
                            self.progresas.emit("+%d" % pagaminta)
                sand.commit()
            finally:
                sand.close()
                idx.close()
            self.done.emit(pagaminta)
        except Exception as e:
            self.error_signal.emit(str(e))


class AtstatymoWorker(QObject):
    """PILNAS UNDO pagal zurnala."""

    done = pyqtSignal(object)
    error_signal = pyqtSignal(str)

    def __init__(self, db_kelias):
        super().__init__()
        self._db_kelias = str(db_kelias)
        self._stop = False

    def stop(self):
        self._stop = True

    @pyqtSlot()
    def run(self):
        con = None
        try:
            con = indeksas.atidaryti(self._db_kelias)
            self.done.emit(tvarkytojas.atstatyti(
                con, stop=lambda: self._stop))
        except Exception as e:
            self.error_signal.emit(str(e))
        finally:
            if con is not None:
                con.close()


class TelefonoZvalgybosWorker(QObject):
    """v1.0 VINIS: telefono aptikimas + medijos vietu zvalgyba (Shell COM
    per PowerShell subprocesa - telefonas.py; MTP prieiga ISSKIRTINE,
    todel jei Explorer atidarytas ties telefonu, zvalgyba nieko neras)."""

    done = pyqtSignal(object)        # (telefonai, zvalgyba_dict|None)
    error_signal = pyqtSignal(str)

    def __init__(self):
        super().__init__()
        self._stop = False

    def stop(self):
        self._stop = True

    @pyqtSlot()
    def run(self):
        try:
            telefonai = telefonas.rasti_telefonus()
            if self._stop or not telefonai:
                self.done.emit((telefonai, None))
                return
            z = telefonas.zvalgyti(telefonai[0]["vardas"])
            self.done.emit((telefonai, z))
        except Exception as e:
            self.error_signal.emit(str(e))


class TelefonoKopijosWorker(QObject):
    """v1.0 VINIS: pazymetu telefono vietu kopija i kompiuteri.

    PS procesas srautu (Popen) - PROG/APLANKAS/LAUKIU eilutes virsta
    progreso signalais; stop() nutraukia procesa (i telefona nerasom
    NIEKO, tad nutraukimas saugus - liks dalis kopiju kompiuteryje).
    """

    zurnalas = pyqtSignal(str)
    progresas = pyqtSignal(str)
    done = pyqtSignal(object)        # (viso_faili_tiksle, praleista)
    error_signal = pyqtSignal(str)

    def __init__(self, telefono_vardas, keliai, tikslas):
        super().__init__()
        self._vardas = telefono_vardas
        self._keliai = list(keliai)
        self._tikslas = str(tikslas)
        self._stop = False
        self._proc = None

    def stop(self):
        self._stop = True
        p = self._proc
        if p is not None:
            try:
                p.kill()
            except Exception:
                pass

    @pyqtSlot()
    def run(self):
        import subprocess
        try:
            komanda = telefonas.kopijos_komanda(
                self._vardas, self._keliai, self._tikslas)
            kwargs = {"stdout": subprocess.PIPE,
                      "stderr": subprocess.DEVNULL,
                      "text": True, "encoding": "utf-8",
                      "errors": "replace"}
            import sys as _sys
            if _sys.platform == "win32":
                kwargs["creationflags"] = getattr(
                    subprocess, "CREATE_NO_WINDOW", 0x08000000)
            self._proc = subprocess.Popen(
                telefonas.ps_argumentai(komanda), **kwargs)
            rezultatas = None
            for eilute in self._proc.stdout:
                if self._stop:
                    break
                ivykis = telefonas.isskirstyti_kopija(eilute)
                if ivykis is None:
                    continue
                tipas, duom = ivykis
                if tipas == "aplankas":
                    self.zurnalas.emit(t("Kopijuojama: {}").format(duom))
                elif tipas == "prog":
                    self.progresas.emit(
                        t("nukopijuota {}, praleista {}").format(*duom))
                elif tipas == "laukiu":
                    self.progresas.emit(
                        t("baigiama... tiksle {} failu").format(duom))
                elif tipas == "baigta":
                    rezultatas = duom
                elif tipas == "klaida":
                    self.error_signal.emit(
                        t("Telefonas dingo kopijos metu: {}").format(duom))
                    return
            self._proc.wait(timeout=30)
            if self._stop:
                self.zurnalas.emit(t("Kopija nutraukta - dalis failu jau"
                                     " kompiuteryje, telefonas nepaliestas."))
                return
            if rezultatas is None:
                self.error_signal.emit(t("Kopija nutruko be rezultato -"
                                         " patikrinkite laida ir bandykite"
                                         " dar karta."))
                return
            self.done.emit(rezultatas)
        except Exception as e:
            self.error_signal.emit(str(e))
