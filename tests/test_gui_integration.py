"""Prueba de integración de GUI e inicialización completa sin pantalla (offscreen)."""
import os
import sys

# Forzar modo offscreen para pruebas en entorno sin monitor
os.environ["QT_QPA_PLATFORM"] = "offscreen"

import pytest
from PyQt6.QtWidgets import QApplication
from ui.main_window import MainWindow
from physics.models import LatheParameters


def test_main_window_lifecycle():
    app = QApplication.instance()
    if app is None:
        app = QApplication(sys.argv)

    window = MainWindow()
    assert window is not None
    assert window.windowTitle() != ""
    assert not window.windowIcon().isNull(), "El icono de la ventana debe estar cargado correctamente."

    # Probar carga del caso base oficial en modo silencioso para pruebas
    window.load_case_avance2(show_msg=False)
    assert window.engine.escenario == "CICLO_COMPLETO"

    # Probar avance temporal
    for _ in range(10):
        window.engine.step_forward(0.016)

    st = window.engine.current_state
    assert st.t > 0
    assert st.omega > 0

    # Probar cambio de pestañas
    for i in range(window.tab_widget.count()):
        window.tab_widget.setCurrentIndex(i)

    # Probar cambio a modo presentación y regreso
    window._enter_presentation_mode()
    assert window.stacked_widget.currentIndex() == 1
    window._exit_presentation_mode()
    assert window.stacked_widget.currentIndex() == 0

    # Probar cambio de escenarios
    for esc_idx in range(6):
        window._on_scenario_changed(esc_idx)

    # Probar cambio de velocidad
    for sp_idx in range(7):
        window._on_speed_changed(sp_idx)

    print("Integración de GUI y OpenGL validada exitosamente en modo offscreen.")
