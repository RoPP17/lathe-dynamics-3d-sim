"""
Ventana Principal de la Aplicación del Simulador Dinámico 3D del Torno.
Integra visualización 3D, telemetría, gráficas sincronizadas, validación analítica,
modo experimental, cálculo de torsión/contrapunto y modo presentación de alto impacto.
"""

import time
from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QTabWidget,
    QToolBar, QPushButton, QComboBox, QSlider, QLabel, QSplitter,
    QMessageBox
)
from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtGui import QIcon, QKeyEvent

from config.styles import ENGINEERING_DARK_STYLE
from physics.models import LatheParameters, DynamicState
from simulation.engine import SimulationEngine
from visualization.gl_widget import LatheGLWidget
from .dashboard_panel import DashboardPanel
from .synchronized_plots import SynchronizedPlotsWidget
from .validation_view import ValidationViewWidget
from .experimental_mode import ExperimentalModeWidget
from .mechanics_view import MechanicsViewWidget
from .presentation_mode import PresentationHUDOverlay


class MainWindow(QMainWindow):
    """Ventana principal del software de simulación dinámica."""

    def __init__(self):
        super().__init__()
        self.setWindowTitle("Simulador Dinámico 3D del Torno Didáctico para Madera — Dinámica UTA")
        self.resize(1380, 880)
        self.setStyleSheet(ENGINEERING_DARK_STYLE)

        # Configurar icono institucional / aplicativo
        import os
        res_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "resources")
        icon_path = os.path.join(res_dir, "icon.ico")
        if not os.path.exists(icon_path):
            icon_path = os.path.join(res_dir, "icon.png")
        if os.path.exists(icon_path):
            self.setWindowIcon(QIcon(icon_path))

        # 1. Parámetros y Motor Físico Central (Fuente Única de Verdad)
        self.params = LatheParameters()
        self.engine = SimulationEngine(self.params)

        # 2. Componentes de Visualización e Interfaz
        self.gl_widget = LatheGLWidget()
        self.dashboard = DashboardPanel()
        self.plots_widget = SynchronizedPlotsWidget(self.engine)
        self.validation_view = ValidationViewWidget(self.params)
        self.exp_widget = ExperimentalModeWidget(self.params)
        self.mechanics_view = MechanicsViewWidget(self.params)

        # HUD Overlay de Presentación montado sobre el visor 3D
        self.presentation_widget = PresentationHUDOverlay(self.engine, self.gl_widget)

        # Conectar vector toggles del dashboard con el visor OpenGL
        self.dashboard.chk_vel.stateChanged.connect(lambda s: self.gl_widget.set_vector_visibility("velocidad", s == 2))
        self.dashboard.chk_at.stateChanged.connect(lambda s: self.gl_widget.set_vector_visibility("acel_tang", s == 2))
        self.dashboard.chk_an.stateChanged.connect(lambda s: self.gl_widget.set_vector_visibility("acel_norm", s == 2))
        self.dashboard.chk_atot.stateChanged.connect(lambda s: self.gl_widget.set_vector_visibility("acel_total", s == 2))
        self.dashboard.chk_Fu.stateChanged.connect(lambda s: self.gl_widget.set_vector_visibility("desbalance", s == 2))
        self.dashboard.chk_Fc.stateChanged.connect(lambda s: self.gl_widget.set_vector_visibility("corte", s == 2))
        self.dashboard.chk_viruta.stateChanged.connect(lambda s: self.gl_widget.set_vector_visibility("viruta", s == 2))

        # Conectar recálculo de parámetros experimentales
        self.exp_widget.parameters_changed.connect(self._on_parameters_recalculated)

        # Conectar salida del HUD de modo presentación
        self.presentation_widget.exit_presentation.connect(self._exit_presentation_mode)

        # 3. Construir la Arquitectura de Pestañas
        self.tab_container = QWidget()
        tab_layout = QVBoxLayout(self.tab_container)
        tab_layout.setContentsMargins(0, 0, 0, 0)
        tab_layout.setSpacing(0)

        self.tab_widget = QTabWidget()

        # Tab 1: Simulación 3D + Telemetría
        tab1 = QWidget()
        t1_layout = QHBoxLayout(tab1)
        t1_layout.setContentsMargins(4, 4, 4, 4)
        t1_layout.setSpacing(6)
        self.splitter_t1 = QSplitter(Qt.Orientation.Horizontal)
        self.splitter_t1.addWidget(self.gl_widget)
        self.splitter_t1.addWidget(self.dashboard)
        self.splitter_t1.setCollapsible(0, False)
        self.splitter_t1.setCollapsible(1, False)
        self.splitter_t1.setStretchFactor(0, 8)
        self.splitter_t1.setStretchFactor(1, 2)
        self.splitter_t1.setSizes([980, 360])
        t1_layout.addWidget(self.splitter_t1)
        self.tab_widget.addTab(tab1, "🎮 Simulación 3D y Telemetría")

        # Tab 2: Gráficas Sincronizadas
        self.tab_widget.addTab(self.plots_widget, "📈 Análisis Gráfico Sincronizado")

        # Tab 3: Validación Numérica vs Avance 2
        self.tab_widget.addTab(self.validation_view, "📋 Validación Analítica (20 Cálculos)")

        # Tab 4: Modo Experimental
        self.tab_widget.addTab(self.exp_widget, "⚙️ Modo Experimental")

        # Tab 5: Torsión y Contrapunto (C19 y C20)
        self.tab_widget.addTab(self.mechanics_view, "🔩 Torsión y Contrapunto (C19/C20)")

        tab_layout.addWidget(self.tab_widget)
        self.setCentralWidget(self.tab_container)

        # 4. Construcción de Barras de Herramientas y Controles
        self._create_top_toolbar()
        self._create_bottom_timeline_bar()

        # 5. Temporizador de Alta Cadencia (60 FPS para física continua y renderizado)
        self.timer = QTimer(self)
        self.timer.setInterval(16) # ~16.6 ms (60 FPS)
        self.timer.timeout.connect(self._game_loop)
        self.last_clock_time = time.perf_counter()

        # Iniciar simulación
        self.timer.start()

    def _create_top_toolbar(self):
        """Crea la barra de herramientas superior con accesos directos de control."""
        self.top_toolbar = QToolBar("Control Maestro")
        self.top_toolbar.setMovable(False)
        self.addToolBar(Qt.ToolBarArea.TopToolBarArea, self.top_toolbar)

        # Presets principales
        btn_case_base = QPushButton("🏢 CASO AVANCE 2 (NOMINAL)")
        btn_case_base.setObjectName("btnPrimary")
        btn_case_base.setStyleSheet("font-size: 12px; font-weight: bold; min-height: 36px; padding: 4px 14px;")
        btn_case_base.setToolTip("Carga el escenario oficial y los parámetros originales del Avance 2")
        btn_case_base.clicked.connect(self.load_case_avance2)
        self.top_toolbar.addWidget(btn_case_base)

        self.top_toolbar.addSeparator()

        # Selector de Escenarios ampliado y destacado
        lbl_esc = QLabel("  Escenario Dinámico: ")
        lbl_esc.setStyleSheet("font-size: 12px; font-weight: bold; color: #00e5ff;")
        self.top_toolbar.addWidget(lbl_esc)

        self.combo_escenario = QComboBox()
        self.combo_escenario.setMinimumWidth(320)
        self.combo_escenario.setMinimumHeight(36)
        self.combo_escenario.setStyleSheet("""
            QComboBox {
                font-size: 12px;
                font-weight: bold;
                padding: 4px 10px;
                background-color: #1a2230;
                border: 1px solid #0098ff;
                border-radius: 5px;
                color: #ffffff;
            }
            QComboBox::drop-down {
                width: 24px;
            }
            QComboBox QAbstractItemView {
                background-color: #1a1a24;
                color: #ffffff;
                selection-background-color: #0078d4;
                font-size: 12px;
                padding: 4px;
            }
        """)
        self.combo_escenario.addItems([
            "1. CICLO COMPLETO (Secuencial)",
            "2. ARRANQUE (0 a 2.0 s)",
            "3. RÉGIMEN ESTABLE (1700 rpm)",
            "4. TORNEADO / DESBASTE",
            "5. DESBALANCE DINÁMICO (Fᵤ)",
            "6. PARADA LIBRE (Run-Down)"
        ])
        self.combo_escenario.currentIndexChanged.connect(self._on_scenario_changed)
        self.top_toolbar.addWidget(self.combo_escenario)

        self.top_toolbar.addSeparator()

        # Presets de Cámara 3D con mayor tamaño y separación
        lbl_vistas = QLabel("  Vistas 3D: ")
        lbl_vistas.setStyleSheet("font-size: 12px; font-weight: bold; color: #ffd54f;")
        self.top_toolbar.addWidget(lbl_vistas)

        btn_view_style = """
            QPushButton {
                font-size: 11px;
                font-weight: 600;
                min-width: 94px;
                min-height: 35px;
                padding: 4px 10px;
                margin: 0px 3px;
                background-color: #22242e;
                border: 1px solid #3c4252;
                border-radius: 4px;
                color: #e0e0ea;
            }
            QPushButton:hover {
                background-color: #2d3240;
                border-color: #0098ff;
                color: #ffffff;
            }
            QPushButton:pressed {
                background-color: #0078d4;
                color: #ffffff;
            }
        """

        btn_iso = QPushButton("📐 Isométrica")
        btn_iso.setStyleSheet(btn_view_style)
        btn_iso.clicked.connect(self.gl_widget.set_view_isometric)
        self.top_toolbar.addWidget(btn_iso)

        btn_front = QPushButton("👁️ Frontal")
        btn_front.setStyleSheet(btn_view_style)
        btn_front.clicked.connect(self.gl_widget.set_view_front)
        self.top_toolbar.addWidget(btn_front)

        btn_side = QPushButton("🔄 Lateral")
        btn_side.setStyleSheet(btn_view_style)
        btn_side.clicked.connect(self.gl_widget.set_view_side)
        self.top_toolbar.addWidget(btn_side)

        btn_top = QPushButton("⬇️ Superior")
        btn_top.setStyleSheet(btn_view_style)
        btn_top.clicked.connect(self.gl_widget.set_view_top)
        self.top_toolbar.addWidget(btn_top)

        btn_reset_cam = QPushButton("↺ Reset")
        btn_reset_cam.setStyleSheet(btn_view_style)
        btn_reset_cam.setToolTip("Restablece la orientación original de la cámara orbital")
        btn_reset_cam.clicked.connect(self.gl_widget.reset_camera)
        self.top_toolbar.addWidget(btn_reset_cam)

        self.top_toolbar.addSeparator()

        # Botón Modo Presentación
        btn_pres = QPushButton("🎬 MODO PRESENTACIÓN (F11)")
        btn_pres.setStyleSheet("""
            QPushButton {
                background-color: #5c2b8c;
                color: white;
                font-size: 12px;
                font-weight: bold;
                min-height: 36px;
                padding: 4px 14px;
                border-radius: 4px;
            }
            QPushButton:hover {
                background-color: #7236ad;
            }
        """)
        btn_pres.setToolTip("Maximiza la vista 3D en pantalla completa con HUD para defensa académica")
        btn_pres.clicked.connect(self._enter_presentation_mode)
        self.top_toolbar.addWidget(btn_pres)

    def _create_bottom_timeline_bar(self):
        """Crea la barra inferior con línea de tiempo y controles de transporte."""
        self.bottom_toolbar = QToolBar("Transporte y Línea de Tiempo")
        self.bottom_toolbar.setMovable(False)
        self.addToolBar(Qt.ToolBarArea.BottomToolBarArea, self.bottom_toolbar)

        # Botones de reproducción
        self.btn_play = QPushButton("▶ PLAY")
        self.btn_play.setObjectName("btnPrimary")
        self.btn_play.clicked.connect(self._toggle_play)
        self.bottom_toolbar.addWidget(self.btn_play)

        self.btn_pause = QPushButton("⏸ PAUSE")
        self.btn_pause.clicked.connect(self.engine.pause)
        self.bottom_toolbar.addWidget(self.btn_pause)

        self.btn_stop = QPushButton("⏹ STOP")
        self.btn_stop.setObjectName("btnDanger")
        self.btn_stop.clicked.connect(self.engine.stop)
        self.bottom_toolbar.addWidget(self.btn_stop)

        self.btn_step_back = QPushButton("◀ Paso")
        self.btn_step_back.clicked.connect(lambda: self.engine.step_backward(0.05))
        self.bottom_toolbar.addWidget(self.btn_step_back)

        self.btn_step_fwd = QPushButton("Paso ▶")
        self.btn_step_fwd.clicked.connect(lambda: self.engine.step_forward(0.05))
        self.bottom_toolbar.addWidget(self.btn_step_fwd)

        self.bottom_toolbar.addSeparator()

        # Selector de Velocidad de Reproducción
        self.bottom_toolbar.addWidget(QLabel(" Velocidad: "))
        self.combo_speed = QComboBox()
        self.combo_speed.addItems(["0.10x", "0.25x", "0.50x", "1.00x", "2.00x", "5.00x", "10.0x"])
        self.combo_speed.setCurrentIndex(3) # 1.00x por defecto
        self.combo_speed.currentIndexChanged.connect(self._on_speed_changed)
        self.bottom_toolbar.addWidget(self.combo_speed)

        self.bottom_toolbar.addSeparator()

        # Scrubbing Slider de Tiempo
        self.bottom_toolbar.addWidget(QLabel(" Línea de Tiempo: "))
        self.lbl_time = QLabel(" 0.00 s ")
        self.lbl_time.setStyleSheet("font-family:'Consolas'; font-size:13px; font-weight:bold; color:#00e5ff;")
        self.bottom_toolbar.addWidget(self.lbl_time)

        self.timeline_slider = QSlider(Qt.Orientation.Horizontal)
        self.timeline_slider.setRange(0, 1850) # 0 a 18.50 s en centésimas
        self.timeline_slider.setValue(0)
        self.timeline_slider.valueChanged.connect(self._on_slider_moved)
        self.bottom_toolbar.addWidget(self.timeline_slider)

        self.lbl_total_time = QLabel(" / 18.50 s ")
        self.lbl_total_time.setStyleSheet("font-family:'Consolas'; font-size:12px; color:#888890;")
        self.bottom_toolbar.addWidget(self.lbl_total_time)

    def _game_loop(self):
        """Bucle principal de sincronización temporal de la simulación a 60 FPS."""
        now = time.perf_counter()
        dt_real = now - self.last_clock_time
        self.last_clock_time = now

        # Evitar saltos temporales gigantes si la ventana estuvo minimizada
        dt_real = min(dt_real, 0.050)

        # 1. Avanzar la física en el motor temporal
        self.engine.advance_real_time(dt_real)
        st = self.engine.current_state

        # 2. Actualizar visualizador 3D
        self.gl_widget.update_simulation_state(st)

        # 3. Actualizar panel de telemetría lateral
        self.dashboard.update_telemetry(st)

        # 4. Actualizar línea de tiempo y gráficas sincronizadas
        self.lbl_time.setText(f" {st.t:5.2f} s ")
        if not self.timeline_slider.isSliderDown():
            self.timeline_slider.blockSignals(True)
            self.timeline_slider.setValue(int(st.t * 100))
            self.timeline_slider.blockSignals(False)

        # Actualizar gráficas en tiempo real si la pestaña de análisis está visible
        if self.tab_widget.currentIndex() == 1:
            self.plots_widget.update_plots()

        # Actualizar modo presentación si está activo
        if self.presentation_widget.is_active:
            self.presentation_widget.update_presentation_state(st)

        # Actualizar texto del botón play
        if self.engine.is_running and not self.engine.is_paused:
            self.btn_play.setText("⏸ PAUSE")
        else:
            self.btn_play.setText("▶ PLAY")

    def _toggle_play(self):
        self.engine.toggle_play_pause()

    def _on_slider_moved(self, value: int):
        """Scrubbing interactivo de la línea de tiempo."""
        t_target = value / 100.0
        self.engine.seek_time(t_target)
        self.plots_widget.update_plots()

    def _on_speed_changed(self, idx: int):
        speed_map = {0: 0.10, 1: 0.25, 2: 0.50, 3: 1.00, 4: 2.00, 5: 5.00, 6: 10.0}
        self.engine.set_playback_speed(speed_map.get(idx, 1.0))

    def _on_scenario_changed(self, idx: int):
        esc_map = {
            0: ("CICLO_COMPLETO", 18.5),
            1: ("ARRANQUE", 2.0),
            2: ("REGIMEN", 10.0),
            3: ("TORNEADO", 14.12),
            4: ("DESBALANCE", 10.0),
            5: ("PARADA", 3.5)
        }
        esc_nombre, t_dur = esc_map.get(idx, ("CICLO_COMPLETO", 18.5))
        self.engine.reset(esc_nombre)
        self.lbl_total_time.setText(f" / {t_dur:.2f} s ")
        self.timeline_slider.setRange(0, int(t_dur * 100))
        self.plots_widget._build_current_view()
        self.engine.play()

    def _on_parameters_recalculated(self, new_params: LatheParameters):
        """Manejador cuando el usuario aplica cambios en Modo Experimental."""
        self.params = new_params.copy()
        self.engine.set_parameters(self.params)
        self.validation_view.refresh_validation(self.params)
        self.plots_widget.update_plots()

    def load_case_avance2(self, show_msg: bool = True):
        """Carga oficial del CASO AVANCE 2."""
        self.params = LatheParameters()
        self.engine.set_parameters(self.params)
        self.validation_view.refresh_validation(self.params)
        self.combo_escenario.setCurrentIndex(0)
        self.combo_speed.setCurrentIndex(3) # 1.0x
        self.tab_widget.setCurrentIndex(0)
        self.engine.reset("CICLO_COMPLETO")
        self.engine.play()
        if show_msg:
            QMessageBox.information(
                self, "Caso Base Oficial",
                "Se ha cargado con éxito el CASO AVANCE 2 con todos los parámetros oficiales del proyecto."
            )

    def _enter_presentation_mode(self):
        """Activa la vista de presentación maximizada con HUD flotante."""
        self.top_toolbar.hide()
        self.bottom_toolbar.hide()
        self.dashboard.hide()
        self.tab_widget.tabBar().hide()
        self.tab_widget.setCurrentIndex(0) # Vista 3D
        self.presentation_widget.show_overlay()
        self.showFullScreen()

    def _exit_presentation_mode(self):
        """Sale de la vista de presentación y retorna a la interfaz completa."""
        self.presentation_widget.hide_overlay()
        self.dashboard.show()
        self.tab_widget.tabBar().show()
        self.top_toolbar.show()
        self.bottom_toolbar.show()
        self.showNormal()

    def keyPressEvent(self, event: QKeyEvent):
        """Accesos directos de teclado para docencia y defensa académica."""
        key = event.key()
        if key == Qt.Key.Key_F11:
            if self.presentation_widget.is_active:
                self._exit_presentation_mode()
            else:
                self._enter_presentation_mode()
        elif key == Qt.Key.Key_Escape:
            if self.presentation_widget.is_active:
                self._exit_presentation_mode()
        elif key == Qt.Key.Key_Space:
            self._toggle_play()
        elif key == Qt.Key.Key_R:
            self.engine.stop()
            self.engine.play()
        elif key == Qt.Key.Key_1:
            self.combo_escenario.setCurrentIndex(0)
        elif key == Qt.Key.Key_2:
            self.combo_escenario.setCurrentIndex(1)
        elif key == Qt.Key.Key_3:
            self.combo_escenario.setCurrentIndex(2)
        elif key == Qt.Key.Key_4:
            self.combo_escenario.setCurrentIndex(3)
        elif key == Qt.Key.Key_5:
            self.combo_escenario.setCurrentIndex(4)
        elif key == Qt.Key.Key_6:
            self.combo_escenario.setCurrentIndex(5)
        else:
            super().keyPressEvent(event)

    @property
    def stacked_widget(self):
        """Proxy de compatibilidad para modo presentación."""
        class _StackedProxy:
            def __init__(proxy_self, main_win):
                proxy_self.main_win = main_win
            def currentIndex(proxy_self):
                return 1 if proxy_self.main_win.presentation_widget.is_active else 0
            def setCurrentIndex(proxy_self, idx):
                if idx == 1:
                    proxy_self.main_win._enter_presentation_mode()
                else:
                    proxy_self.main_win._exit_presentation_mode()
        return _StackedProxy(self)
