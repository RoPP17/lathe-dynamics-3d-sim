"""
Pruebas automatizadas de las funcionalidades avanzadas:
- Presets rápidos de Modo Experimental
- Barra de utilización de potencia y alerta de desbalance en Dashboard
- Retícula y bandas de fase en Gráficas Sincronizadas
- Modo Presentación HUD
"""

import sys
import pytest
from PyQt6.QtWidgets import QApplication
from PyQt6.QtCore import QPointF
from physics.models import LatheParameters, DynamicState
from simulation.engine import SimulationEngine
from ui.dashboard_panel import DashboardPanel
from ui.experimental_mode import ExperimentalModeWidget
from ui.synchronized_plots import SynchronizedPlotsWidget
from ui.main_window import MainWindow


@pytest.fixture(scope="module")
def qapp():
    app = QApplication.instance()
    if app is None:
        app = QApplication(sys.argv)
    yield app


def test_experimental_presets(qapp):
    params = LatheParameters()
    exp_widget = ExperimentalModeWidget(params)

    # Preset Roble
    exp_widget._load_preset(1500, 2.5, 45.0, 1.5, 20.0, 2.0, 3.8)
    assert exp_widget.exp_params.n_nom == 1500
    assert exp_widget.exp_params.Fc == 45.0
    assert exp_widget.table_diff.rowCount() == 8

    # Preset Desbalance Severo
    exp_widget._load_preset(1700, 2.0, 20.0, 2.5, 60.0, 5.0, 3.5)
    assert exp_widget.exp_params.mu == pytest.approx(0.060, rel=1e-3)
    assert exp_widget.exp_params.e_desbalance == pytest.approx(0.005, rel=1e-3)

    # Restaurar Base
    exp_widget.restore_baseline(show_msg=False)
    assert exp_widget.exp_params.n_nom == 1700
    assert exp_widget.exp_params.Fc == 20.0


def test_dashboard_power_and_alerts(qapp):
    panel = DashboardPanel()

    # Estado con baja potencia y balanceado
    st1 = DynamicState(t=3.0, omega=178.02, rpm=1700.0, P_total=58.4, F_desbalance=0.05)
    panel.update_telemetry(st1)
    assert panel.bar_power.value() < 20
    assert "BALANCE" in panel.lbl_alert_title.text()

    # Estado con desbalance y corte pesado
    st2 = DynamicState(t=12.0, omega=178.02, rpm=1700.0, P_total=680.0, F_desbalance=14.33)
    panel.update_telemetry(st2)
    assert panel.bar_power.value() > 80
    assert "ALERTA" in panel.lbl_alert_title.text()


def test_synchronized_plots_features(qapp):
    params = LatheParameters()
    engine = SimulationEngine(params)
    plots_widget = SynchronizedPlotsWidget(engine)

    # Simular datos
    for _ in range(20):
        engine.advance_real_time(0.05)
    plots_widget.update_plots()

    # Probar cambio a todas las vistas
    for i in range(7):
        plots_widget.combo_view.setCurrentIndex(i)
        assert len(plots_widget.plots) > 0

    # Probar movimiento de cursor de inspección (crosshair)
    plots_widget._on_mouse_moved(QPointF(50.0, 50.0))
    assert "Cursor" in plots_widget.lbl_inspection.text() or "t =" in plots_widget.lbl_inspection.text()


def test_presentation_hud_toggle(qapp):
    window = MainWindow()

    # Activar presentación
    window._enter_presentation_mode()
    assert window.presentation_widget.is_active is True
    assert window.top_toolbar.isHidden()
    assert window.dashboard.isHidden()

    # Salir de presentación
    window._exit_presentation_mode()
    assert window.presentation_widget.is_active is False
    assert not window.top_toolbar.isHidden()
    assert not window.dashboard.isHidden()
