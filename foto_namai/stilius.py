"""stilius.py - dovanu SEIMOS vizitine kortele (Roberto pasiulymas,
Claude sprendimas 2026-08-07: vienodas veidas visose dovanose).

Kilme - Smart Duplicate Finder / Temp Cleaner APP_QSS: apvalinti 10px
mygtukai su 3D gradientu ir hover; GINTARINIS pagrindinis veiksmas
(btn_scan), MELYNAS informacinis (btn_preview), ZALIAS vykdomasis
(btn_clear_all), RAUDONAS pavojingas/uzdarymo (btn_close); melyna
antrastes juosta #3c4e99. Kopijuojama i kiekviena dovana (savarankiski
paketai), objectName zodynas VIENODAS visoje seimoje.

SEIMOS TAISYKLE: jokio setStyleSheet ant QCheckBox - ismusa natyvu
piesima (Roberto radinys, juoda varnele).
"""

APP_QSS = """
QPushButton {
    background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
        stop:0 #ffffff, stop:1 #e4e6ee);
    border: 1px solid #b6bac8;
    border-radius: 10px;
    padding: 9px 14px;
    font-weight: 600;
    color: #2c2f38;
}
QPushButton:hover {
    background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
        stop:0 #f3f7ff, stop:1 #d6e2f8);
    border: 1px solid #5b8def;
    color: #123a7a;
}
QPushButton:pressed {
    background: #c9d7f0;
    border: 1px solid #3c6fd8;
    padding-top: 11px; padding-bottom: 7px;
}
QPushButton:disabled {
    background: #ededf1; border: 1px solid #d3d3da; color: #a0a0ab;
}
QPushButton#btn_scan {
    background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
        stop:0 #ffd35c, stop:1 #f0a53a);
    border: 1px solid #d18a1f;
    color: #4a2c00;
}
QPushButton#btn_scan:hover {
    background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
        stop:0 #ffe08a, stop:1 #f7b551);
    border: 1px solid #b97613;
}
QPushButton#btn_scan:pressed {
    background: #e29a2e; border: 1px solid #a56508;
    padding-top: 11px; padding-bottom: 7px;
}
QPushButton#btn_scan:disabled {
    background: #ededf1; border: 1px solid #d3d3da; color: #a0a0ab;
}
QPushButton#btn_preview {
    background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
        stop:0 #7fb3f2, stop:1 #3d7bd8);
    border: 1px solid #2b62b5;
    color: #ffffff;
}
QPushButton#btn_preview:hover {
    background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
        stop:0 #9cc6f8, stop:1 #5590e6);
    border: 1px solid #1f4f9c;
}
QPushButton#btn_preview:pressed {
    background: #3568b8; border: 1px solid #1a4485;
    padding-top: 11px; padding-bottom: 7px;
}
QPushButton#btn_clear_all {
    background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
        stop:0 #8fd694, stop:1 #4d9e55);
    border: 1px solid #3a7e41;
    color: #ffffff;
}
QPushButton#btn_clear_all:hover {
    background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
        stop:0 #a8e2ac, stop:1 #62b26a);
    border: 1px solid #2d6633;
}
QPushButton#btn_clear_all:pressed {
    background: #47924f; border: 1px solid #245229;
    padding-top: 11px; padding-bottom: 7px;
}
QPushButton#btn_close {
    background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
        stop:0 #ef8a8a, stop:1 #cf3e3e);
    border: 1px solid #a82f2f;
    color: #ffffff;
}
QPushButton#btn_close:hover {
    background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
        stop:0 #f4a5a5, stop:1 #d95252);
    border: 1px solid #8c2626;
}
QPushButton#btn_close:pressed {
    background: #b83030; border: 1px solid #7a2020;
    padding-top: 11px; padding-bottom: 7px;
}
QPushButton#btn_help {
    border-radius: 13px;
    padding: 0px;
    font-weight: 700;
}
QPushButton#btn_help::menu-indicator { image: none; width: 0px; }
QSlider::groove:horizontal {
    height: 6px; background: #dfe3ec; border-radius: 3px;
}
QSlider::handle:horizontal {
    width: 16px; margin: -6px 0; border-radius: 8px;
    background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
        stop:0 #ffd35c, stop:1 #f0a53a);
    border: 1px solid #d18a1f;
}
"""

# Antrastes juosta (melyna #3c4e99, baltas pastorintas tekstas)
ANTRASTE = ("font-weight: bold; font-size: 16px; color: #ffffff;"
            "background-color: #3c4e99; padding: 8px; border-radius: 6px;")

# Gyvos informacijos juosta (RYSKI, ne pilka - Roberto taisykle)
STATUSAS = ("padding: 5px 8px; color: #1a3e6e; font-size: 12px;"
            "font-weight: bold; background-color: #eaf1fb;"
            "border: 1px solid #b9cdec; border-radius: 4px;")

# Antraeile pagalbine informacija (legenda, pastabos)
LEGENDA = ("padding: 4px 8px; color: #666; font-size: 11px;"
           "background-color: #f8f8f8; border: 1px solid #ddd;"
           "border-radius: 4px;")
