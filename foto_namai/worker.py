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

from PyQt6.QtCore import QObject, pyqtSignal, pyqtSlot

import ataskaita
import indeksas
from kalba import t
import indeksavimas
import miniaturos
import paieska
import skeneris
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
    done = pyqtSignal(object)        # [(vardas, stat_dict), ...]
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
                }))
            self.done.emit(suvestine)
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
            self.done.emit((grupes, ataskaita.sdf_siulymas(con)))
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
    """E5: miniatiuru gamyba TIK rodomiems rezultatams (sprendimas 14)."""

    vienas = pyqtSignal(object)      # (fileid, keso_kelias_str | None)
    progresas = pyqtSignal(str)
    done = pyqtSignal(object)        # kiek apdorota
    error_signal = pyqtSignal(str)

    def __init__(self, uzduotys):
        """uzduotys: [(fileid, abs_kelias_str, mtime)] - snapshot is GUI."""
        super().__init__()
        self._uzduotys = list(uzduotys)
        self._stop = False

    def stop(self):
        self._stop = True

    @pyqtSlot()
    def run(self):
        try:
            n = 0
            for fileid, kelias, mtime in self._uzduotys:
                if self._stop:
                    break
                kk = miniaturos.miniatiura(kelias, mtime)
                n += 1
                self.vienas.emit((fileid, str(kk) if kk else None))
                if n % 20 == 0:
                    self.progresas.emit(str(n))
            self.done.emit(n)
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
