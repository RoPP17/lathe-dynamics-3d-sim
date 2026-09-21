"""
Estilos y temas profesionales de interfaz gráfica (Dark Engineering / CAE Theme).
"""

ENGINEERING_DARK_STYLE = """
QMainWindow {
    background-color: #1a1a1c;
    color: #e0e0e0;
    font-family: 'Segoe UI', 'Arial', sans-serif;
    font-size: 13px;
}

QWidget {
    background-color: #1e1e20;
    color: #d8d8d8;
    font-family: 'Segoe UI', 'Arial', sans-serif;
}

QTabWidget::pane {
    border: 1px solid #2d2d30;
    background-color: #1e1e20;
    top: -1px;
}

QTabBar::tab {
    background-color: #252528;
    color: #a0a0a0;
    border: 1px solid #2d2d30;
    border-bottom-color: #2d2d30;
    border-top-left-radius: 4px;
    border-top-right-radius: 4px;
    padding: 8px 18px;
    margin-right: 2px;
    font-weight: 600;
}

QTabBar::tab:selected {
    background-color: #1e1e20;
    color: #0098ff;
    border-top: 2px solid #0098ff;
    border-bottom: 1px solid #1e1e20;
}

QTabBar::tab:hover:!selected {
    background-color: #2e2e32;
    color: #ffffff;
}

QGroupBox {
    border: 1px solid #333338;
    border-radius: 6px;
    margin-top: 14px;
    padding-top: 14px;
    font-weight: bold;
    color: #0098ff;
}

QGroupBox::title {
    subcontrol-origin: margin;
    subcontrol-position: top left;
    padding: 0 8px;
    left: 12px;
    background-color: #1e1e20;
}

QPushButton {
    background-color: #2a2a2e;
    color: #e0e0e0;
    border: 1px solid #3e3e44;
    border-radius: 4px;
    padding: 6px 14px;
    font-weight: 600;
    min-height: 24px;
}

QPushButton:hover {
    background-color: #383840;
    border-color: #0098ff;
    color: #ffffff;
}

QPushButton:pressed {
    background-color: #1a1a1c;
    border-color: #0077cc;
}

QPushButton:disabled {
    background-color: #222224;
    color: #666666;
    border-color: #2c2c30;
}

QPushButton#btnPrimary {
    background-color: #0078d4;
    border-color: #0063b1;
    color: #ffffff;
}

QPushButton#btnPrimary:hover {
    background-color: #1084e3;
    border-color: #0098ff;
}

QPushButton#btnDanger {
    background-color: #c42b1c;
    border-color: #a82315;
    color: #ffffff;
}

QPushButton#btnDanger:hover {
    background-color: #d83b2b;
}

QPushButton#btnSuccess {
    background-color: #107c41;
    border-color: #0e6b37;
    color: #ffffff;
}

QPushButton#btnSuccess:hover {
    background-color: #168a4a;
}

QSlider::groove:horizontal {
    border: 1px solid #333338;
    height: 6px;
    background: #28282c;
    border-radius: 3px;
}

QSlider::sub-page:horizontal {
    background: #0078d4;
    border-radius: 3px;
}

QSlider::handle:horizontal {
    background: #e0e0e0;
    border: 1px solid #555555;
    width: 16px;
    margin-top: -5px;
    margin-bottom: -5px;
    border-radius: 8px;
}

QSlider::handle:horizontal:hover {
    background: #ffffff;
    border-color: #0098ff;
}

QTableWidget {
    background-color: #1a1a1c;
    border: 1px solid #2d2d30;
    gridline-color: #2a2a2e;
    color: #dcdcdc;
    selection-background-color: #264f78;
    selection-color: #ffffff;
}

QHeaderView::section {
    background-color: #252528;
    color: #a0a0a0;
    padding: 6px;
    border: 1px solid #2d2d30;
    font-weight: bold;
}

QScrollBar:vertical {
    border: none;
    background: #1e1e20;
    width: 10px;
    margin: 0px;
}

QScrollBar::handle:vertical {
    background: #3a3a40;
    min-height: 20px;
    border-radius: 5px;
}

QScrollBar::handle:vertical:hover {
    background: #505058;
}

QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
    height: 0px;
}

QLabel {
    color: #d0d0d0;
}

QLabel#lblDigitalValue {
    font-family: 'Consolas', 'Courier New', monospace;
    font-size: 16px;
    font-weight: bold;
    color: #00e5ff;
}

QLabel#lblDigitalTitle {
    font-size: 11px;
    color: #888890;
    text-transform: uppercase;
}

QComboBox, QSpinBox, QDoubleSpinBox {
    background-color: #252528;
    border: 1px solid #383840;
    border-radius: 4px;
    padding: 4px 8px;
    color: #e0e0e0;
    font-family: 'Consolas', 'Segoe UI', sans-serif;
}

QComboBox:hover, QSpinBox:hover, QDoubleSpinBox:hover {
    border-color: #0098ff;
}

QCheckBox {
    color: #d0d0d0;
    spacing: 8px;
}

QCheckBox::indicator {
    width: 16px;
    height: 16px;
    border: 1px solid #44444c;
    border-radius: 3px;
    background: #252528;
}

QCheckBox::indicator:checked {
    background: #0078d4;
    border-color: #0098ff;
}
"""
