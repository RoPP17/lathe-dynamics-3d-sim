"""
Pruebas de verificación de:
- Compilación matemática en tablas y fichas técnicas (HTMLDelegate y ausencia de LaTeX crudo).
- Diálogo de inspección HD de diagramas mecánicos (DiagramZoomDialog).
- Dimensionamiento ampliado de la barra superior de herramientas.
"""

import os
import sys
import pytest

os.environ["QT_QPA_PLATFORM"] = "offscreen"

from PyQt6.QtWidgets import QApplication
from physics.models import LatheParameters
from ui.validation_view import ValidationViewWidget, HTMLDelegate
from ui.diagrams import (
    ShaftKeywayDiagramWidget,
    TailstockMechanismDiagramWidget,
    LatheFBDDiagramWidget,
    DiagramZoomDialog
)
from ui.main_window import MainWindow


@pytest.fixture(scope="module")
def qapp():
    app = QApplication.instance()
    if app is None:
        app = QApplication(sys.argv)
    yield app


def test_validation_table_compilation(qapp):
    params = LatheParameters()
    widget = ValidationViewWidget(params)
    assert widget.table.rowCount() == 20
    assert isinstance(widget.table.itemDelegateForColumn(2), HTMLDelegate)

    # Verificar cada ficha técnica
    for r in range(20):
        widget.table.selectRow(r)
        html = widget.doc_browser.toHtml()
        assert "Cálculo" in html
        assert "Ecuación Matemática Compilada" in html
        # Comprobar que no hay backslashes de LaTeX crudo visible
        assert "<code>\\" not in html


def test_diagram_zoom_dialogs(qapp):
    for key in ["C19", "C20", "DCL"]:
        dlg = DiagramZoomDialog(key)
        assert dlg is not None
        assert dlg.windowTitle() != ""
        dlg.close()


def test_top_toolbar_sizing(qapp):
    win = MainWindow()
    assert win.combo_escenario.minimumWidth() >= 300
    assert win.combo_escenario.minimumHeight() >= 35
