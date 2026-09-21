"""Módulo de interfaz gráfica de usuario."""
from .main_window import MainWindow
from .dashboard_panel import DashboardPanel
from .synchronized_plots import SynchronizedPlotsWidget
from .validation_view import ValidationViewWidget
from .experimental_mode import ExperimentalModeWidget
from .mechanics_view import MechanicsViewWidget
from .presentation_mode import PresentationModeWidget

__all__ = [
    "MainWindow",
    "DashboardPanel",
    "SynchronizedPlotsWidget",
    "ValidationViewWidget",
    "ExperimentalModeWidget",
    "MechanicsViewWidget",
    "PresentationModeWidget"
]
