"""
Pantalla de Análisis y Gráficas Sincronizadas en Tiempo Real (pyqtgraph).
Incluye:
- Cursor vertical temporal sincronizado con t_sim.
- Franjas cromáticas de fases operativas (Arranque, Régimen, Torneado, Desbalance, Parada).
- Líneas de referencia teórica con valores nominales del Avance 2.
- Retícula interactiva (Crosshair) para inspección de coordenadas al pasar el mouse.
- Exportador de captura gráfica en alta resolución PNG (1920x1080).
"""

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QComboBox, QPushButton,
    QLabel, QFileDialog, QMessageBox
)
from PyQt6.QtCore import Qt, QPointF
from PyQt6.QtGui import QColor
import pyqtgraph as pg
import numpy as np
from simulation.engine import SimulationEngine
from config.constants import (
    MOTOR_VELOCIDAD_NOMINAL_RPM,
    MOTOR_VELOCIDAD_NOMINAL_RAD_S,
    CORTE_FUERZA_TANGENCIAL_N,
    DESBALANCE_FUERZA_NOMINAL_N,
    MOTOR_POTENCIA_NOMINAL_W
)


class SynchronizedPlotsWidget(QWidget):
    """Visualizador avanzado de curvas dinámicas en tiempo real con fases y retícula."""

    def __init__(self, engine: SimulationEngine, parent=None):
        super().__init__(parent)
        self.engine = engine

        # Configuración estética de pyqtgraph
        pg.setConfigOption('background', '#16161a')
        pg.setConfigOption('foreground', '#d0d0d8')
        pg.setConfigOption('antialias', True)

        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(10, 10, 10, 10)
        main_layout.setSpacing(8)

        # ----------------------------------------------------------------------
        # Barra Superior de Control de Visualización
        # ----------------------------------------------------------------------
        top_bar = QHBoxLayout()

        lbl_select = QLabel("Variable Dinámica:")
        lbl_select.setStyleSheet("font-weight: bold; color: #0098ff;")
        self.combo_view = QComboBox()
        self.combo_view.addItems([
            "1. Velocidad Angular ω(t) y Régimen n(t)",
            "2. Rapidez Tangencial Periférica v(t)",
            "3. Aceleraciones Normal aₙ(t), Tangencial aₜ(t) y Total a(t)",
            "4. Balance de Potencias Mecánicas P(total) = P(corte) + P(pérdidas)",
            "5. Fuerza Centrífuga por Desbalance Fᵤ(t)",
            "6. Desplazamiento Angular θ(t) y Vueltas N(t)",
            "7. Panel Cuádruple Simultáneo (Multi-Variable)"
        ])
        self.combo_view.currentIndexChanged.connect(self._on_view_changed)

        self.btn_export = QPushButton("📸 Exportar PNG HD")
        self.btn_export.clicked.connect(self.export_current_plot)

        # Indicador de inspección interactiva (Mouse-over Crosshair)
        self.lbl_inspection = QLabel("📍 Cursor: Apunte a la curva")
        self.lbl_inspection.setStyleSheet(
            "font-family: 'Consolas', monospace; font-size: 12px; color: #ffd600; background-color: #222228; padding: 4px 8px; border-radius: 4px;"
        )

        # Indicador de tiempo físico actual
        self.lbl_time_info = QLabel("t = 0.000 s")
        self.lbl_time_info.setStyleSheet(
            "font-family: 'Consolas', monospace; font-size: 14px; color: #00e5ff; font-weight: bold; background-color: #1a2332; padding: 4px 8px; border-radius: 4px; border: 1px solid #0098ff;"
        )

        self.btn_toggle_stretch = QPushButton("↔ Ajustado / Extendido")
        self.btn_toggle_stretch.setToolTip("Alterna entre ancho compacto centrado y ancho completo de pantalla")
        self.btn_toggle_stretch.clicked.connect(self._toggle_plot_stretch)
        self.is_stretched = False

        top_bar.addWidget(lbl_select)
        top_bar.addWidget(self.combo_view)
        top_bar.addSpacing(10)
        top_bar.addWidget(self.btn_export)
        top_bar.addWidget(self.btn_toggle_stretch)
        top_bar.addSpacing(15)
        top_bar.addWidget(self.lbl_inspection)
        top_bar.addStretch()
        top_bar.addWidget(self.lbl_time_info)

        main_layout.addLayout(top_bar)

        # Contenedor gráfico principal centrado con dimensiones equilibradas
        graph_center_layout = QHBoxLayout()
        graph_center_layout.setContentsMargins(0, 0, 0, 0)
        graph_center_layout.setSpacing(0)

        self.plot_card = QWidget()
        card_layout = QVBoxLayout(self.plot_card)
        card_layout.setContentsMargins(0, 0, 0, 0)

        self.plot_layout = pg.GraphicsLayoutWidget()
        self.plot_layout.setStyleSheet("border: 1px solid #2d2d34; border-radius: 6px;")
        card_layout.addWidget(self.plot_layout)

        # Dimensiones compactas de ingeniería por defecto
        self.plot_card.setMaximumWidth(1200)
        self.plot_card.setMaximumHeight(650)

        graph_center_layout.addStretch(1)
        graph_center_layout.addWidget(self.plot_card, stretch=10)
        graph_center_layout.addStretch(1)

        main_layout.addLayout(graph_center_layout)

        # Estructuras de control
        self.plots: list[pg.PlotItem] = []
        self.v_lines: list[pg.InfiniteLine] = []
        self.crosshair_v: pg.InfiniteLine | None = None
        self.crosshair_h: pg.InfiniteLine | None = None
        self.curves: dict = {}

        # Conectar evento del mouse en la escena gráfica para crosshair
        self.plot_layout.scene().sigMouseMoved.connect(self._on_mouse_moved)

        # Construir vista inicial
        self._build_current_view()

    def _on_view_changed(self):
        self._build_current_view()
        self.update_plots()

    def _add_phase_bands(self, p: pg.PlotItem):
        """Agrega franjas cromáticas translúcidas indicando las fases del ciclo."""
        esc = getattr(self.engine, 'escenario', getattr(self.engine, 'scenario_name', 'CICLO_COMPLETO'))
        if esc != "CICLO_COMPLETO":
            return

        phases = [
            (0.0, 2.0, QColor(0, 130, 255, 30), "ARRANQUE"),
            (2.0, 5.0, QColor(0, 230, 180, 20), "RÉGIMEN"),
            (5.0, 11.0, QColor(255, 160, 0, 28), "TORNEADO (Fc=20N)"),
            (11.0, 15.0, QColor(255, 40, 60, 28), "DESBALANCE (Fu=14.3N)"),
            (15.0, 18.5, QColor(170, 80, 255, 22), "PARADA LIBRE")
        ]

        for t0, t1, color, name in phases:
            region = pg.LinearRegionItem(values=(t0, t1), brush=color, movable=False)
            region.setZValue(-10) # Enviar al fondo detrás de las curvas
            for line in region.lines:
                line.setPen(pg.mkPen(color.darker(150), width=0.5, style=Qt.PenStyle.DotLine))
            p.addItem(region)

    def _add_benchmark_ref(self, p: pg.PlotItem, y_val: float, label_text: str, color="#ffea00"):
        """Dibuja una línea horizontal punteada de referencia teórica del Avance 2."""
        ref_line = pg.InfiniteLine(
            pos=y_val, angle=0, movable=False,
            pen=pg.mkPen(color, width=1.2, style=Qt.PenStyle.DashDotLine),
            label=f" Ref: {label_text}",
            labelOpts={'position': 0.92, 'color': color, 'fill': (20, 20, 25, 180)}
        )
        p.addItem(ref_line)

    def _build_current_view(self):
        """Reconstruye el diseño de curvas y cursores según la vista seleccionada."""
        self.plot_layout.clear()
        self.plots.clear()
        self.v_lines.clear()
        self.curves.clear()
        self.crosshair_v = None
        self.crosshair_h = None

        idx = self.combo_view.currentIndex()

        if idx == 0:
            # 1. Velocidad Angular ω(t)
            p = self.plot_layout.addPlot(
                title="<b style='color:#0098ff; font-size:13px;'>Velocidad Angular ω(t) y Giro n(t) — Cálculos 1, 3, 17</b>"
            )
            p.setLabel('left', 'Velocidad Angular ω', units='rad/s')
            p.setLabel('bottom', 'Tiempo de Simulación t', units='s')
            p.showGrid(x=True, y=True, alpha=0.3)
            p.addLegend(offset=(10, 10))

            self._add_phase_bands(p)
            self._add_benchmark_ref(p, MOTOR_VELOCIDAD_NOMINAL_RAD_S, "ω(nom) = 178.02 rad/s (1700 rpm)")

            c_omega = p.plot(pen=pg.mkPen('#00b0ff', width=2.8), name='ω(t) [rad/s]')
            self.curves['omega'] = c_omega

            self._setup_crosshair(p)
            self._add_vline_to_plot(p)
            self.plots.append(p)

        elif idx == 1:
            # 2. Rapidez Tangencial Periférica v(t)
            p = self.plot_layout.addPlot(
                title="<b style='color:#0098ff; font-size:13px;'>Rapidez Tangencial Periférica v(t) = ω·R — Cálculos 1 y 5</b>"
            )
            p.setLabel('left', 'Rapidez Periférica v', units='m/s')
            p.setLabel('bottom', 'Tiempo de Simulación t', units='s')
            p.showGrid(x=True, y=True, alpha=0.3)
            p.addLegend(offset=(10, 10))

            self._add_phase_bands(p)
            self._add_benchmark_ref(p, 7.121, "v(nom) = 7.12 m/s (R = 40 mm)")

            c_v = p.plot(pen=pg.mkPen('#ff9100', width=2.8), name='v(t) [m/s]')
            self.curves['v'] = c_v

            self._setup_crosshair(p)
            self._add_vline_to_plot(p)
            self.plots.append(p)

        elif idx == 2:
            # 3. Aceleraciones aₙ(t), aₜ(t) y total
            p = self.plot_layout.addPlot(
                title="<b style='color:#0098ff; font-size:13px;'>Aceleraciones Normal aₙ(t), Tangencial aₜ(t) y Total — Cálculos 2 y 10</b>"
            )
            p.setLabel('left', 'Aceleración', units='m/s²')
            p.setLabel('bottom', 'Tiempo de Simulación t', units='s')
            p.showGrid(x=True, y=True, alpha=0.3)
            p.addLegend(offset=(10, 10))

            self._add_phase_bands(p)
            self._add_benchmark_ref(p, 1267.7, "aₙ(nom) = 1267.7 m/s²", color="#ff5252")

            c_an = p.plot(pen=pg.mkPen('#ff3d00', width=2.6), name='aₙ(t) Centrípeta [m/s²]')
            c_at = p.plot(pen=pg.mkPen('#00e676', width=2.2), name='aₜ(t) Tangencial [m/s²]')
            c_atot = p.plot(pen=pg.mkPen('#e040fb', width=1.8, style=Qt.PenStyle.DashLine), name='|a(t)| Resultante [m/s²]')

            self.curves['an'] = c_an
            self.curves['at'] = c_at
            self.curves['atot'] = c_atot

            self._setup_crosshair(p)
            self._add_vline_to_plot(p)
            self.plots.append(p)

        elif idx == 3:
            # 4. Potencias Mecánicas P(t)
            p = self.plot_layout.addPlot(
                title="<b style='color:#0098ff; font-size:13px;'>Balance de Potencia Mecánica P(total) = P(corte) + P(pérdidas) — Cálculo 13</b>"
            )
            p.setLabel('left', 'Potencia', units='W')
            p.setLabel('bottom', 'Tiempo de Simulación t', units='s')
            p.showGrid(x=True, y=True, alpha=0.3)
            p.addLegend(offset=(10, 10))

            self._add_phase_bands(p)
            self._add_benchmark_ref(p, 200.86, "P(torneado) = 200.86 W")
            self._add_benchmark_ref(p, MOTOR_POTENCIA_NOMINAL_W, "P(nom) = 735.5 W (1 CV)", color="#64ffda")

            c_Ptot = p.plot(pen=pg.mkPen('#ffffff', width=2.8), name='P(total) [W]')
            c_Pcorte = p.plot(pen=pg.mkPen('#2979ff', width=2.2), name='P(corte) útil [W]')
            c_Ploss = p.plot(pen=pg.mkPen('#ff6d00', width=2.0), name='P(pérdidas) [W]')

            self.curves['P_total'] = c_Ptot
            self.curves['P_corte'] = c_Pcorte
            self.curves['P_loss'] = c_Ploss

            self._setup_crosshair(p)
            self._add_vline_to_plot(p)
            self.plots.append(p)

        elif idx == 4:
            # 5. Fuerza centrífuga por desbalance Fᵤ(t)
            p = self.plot_layout.addPlot(
                title="<b style='color:#0098ff; font-size:13px;'>Fuerza Centrífuga por Desbalance Excéntrico Fᵤ(t) = mᵤ·e·ω² — Cálculo 11</b>"
            )
            p.setLabel('left', 'Fuerza Centrífuga Fᵤ', units='N')
            p.setLabel('bottom', 'Tiempo de Simulación t', units='s')
            p.showGrid(x=True, y=True, alpha=0.3)
            p.addLegend(offset=(10, 10))

            self._add_phase_bands(p)
            self._add_benchmark_ref(p, 1.2677, "Fᵤ(nom) = 1.27 N (mᵤ=20g, e=2mm)", color="#ff1744")

            c_Fu = p.plot(pen=pg.mkPen('#ff1744', width=2.8), name='Fᵤ(t) [N]')
            self.curves['Fu'] = c_Fu

            self._setup_crosshair(p)
            self._add_vline_to_plot(p)
            self.plots.append(p)

        elif idx == 5:
            # 6. Desplazamiento angular theta(t)
            p = self.plot_layout.addPlot(
                title="<b style='color:#0098ff; font-size:13px;'>Desplazamiento Angular θ(t) y Vueltas N(t) — Cálculos 3, 4, 18</b>"
            )
            p.setLabel('left', 'Ángulo Girado θ', units='rad')
            p.setLabel('bottom', 'Tiempo de Simulación t', units='s')
            p.showGrid(x=True, y=True, alpha=0.3)
            p.addLegend(offset=(10, 10))

            self._add_phase_bands(p)

            c_th = p.plot(pen=pg.mkPen('#00e5ff', width=2.8), name='θ(t) [rad]')
            self.curves['theta'] = c_th

            self._setup_crosshair(p)
            self._add_vline_to_plot(p)
            self.plots.append(p)

        elif idx == 6:
            # 7. Panel Cuádruple Simultáneo (2x2)
            # Fila 1, Columna 1: omega(t)
            p1 = self.plot_layout.addPlot(0, 0, title="ω(t) [rad/s]")
            p1.showGrid(x=True, y=True, alpha=0.25)
            self._add_phase_bands(p1)
            self.curves['omega'] = p1.plot(pen=pg.mkPen('#00b0ff', width=2.2))
            self._add_vline_to_plot(p1)
            self.plots.append(p1)

            # Fila 1, Columna 2: v(t)
            p2 = self.plot_layout.addPlot(0, 1, title="v(t) [m/s]")
            p2.showGrid(x=True, y=True, alpha=0.25)
            self._add_phase_bands(p2)
            self.curves['v'] = p2.plot(pen=pg.mkPen('#ff9100', width=2.2))
            self._add_vline_to_plot(p2)
            self.plots.append(p2)

            # Fila 2, Columna 1: aₙ(t)
            p3 = self.plot_layout.addPlot(1, 0, title="aₙ(t) [m/s²]")
            p3.showGrid(x=True, y=True, alpha=0.25)
            self._add_phase_bands(p3)
            self.curves['an'] = p3.plot(pen=pg.mkPen('#ff3d00', width=2.2))
            self._add_vline_to_plot(p3)
            self.plots.append(p3)

            # Fila 2, Columna 2: P_total(t)
            p4 = self.plot_layout.addPlot(1, 1, title="Potencia Total P(t) [W]")
            p4.showGrid(x=True, y=True, alpha=0.25)
            self._add_phase_bands(p4)
            self.curves['P_total'] = p4.plot(pen=pg.mkPen('#2979ff', width=2.2))
            self._add_vline_to_plot(p4)
            self.plots.append(p4)

    def _setup_crosshair(self, p: pg.PlotItem):
        """Inicializa las líneas ortogonales de la retícula de inspección."""
        self.crosshair_v = pg.InfiniteLine(angle=90, movable=False, pen=pg.mkPen('#888899', width=1, style=Qt.PenStyle.DotLine))
        self.crosshair_h = pg.InfiniteLine(angle=0, movable=False, pen=pg.mkPen('#888899', width=1, style=Qt.PenStyle.DotLine))
        p.addItem(self.crosshair_v, ignoreBounds=True)
        p.addItem(self.crosshair_h, ignoreBounds=True)

    def _on_mouse_moved(self, point: QPointF):
        """Actualiza la posición del crosshair y la etiqueta de coordenadas."""
        if not self.plots or self.crosshair_v is None:
            return
        active_plot = self.plots[0]
        vb = active_plot.vb
        if active_plot.sceneBoundingRect().contains(point):
            mouse_pt = vb.mapSceneToView(point)
            t_val = mouse_pt.x()
            y_val = mouse_pt.y()
            self.crosshair_v.setPos(t_val)
            self.crosshair_h.setPos(y_val)
            self.lbl_inspection.setText(f"📍 t = {t_val:5.3f} s  |  y = {y_val:6.2f}")

    def _add_vline_to_plot(self, plot_item: pg.PlotItem):
        """Agrega un cursor vertical móvil amarillo indicando el t_sim actual."""
        v_line = pg.InfiniteLine(
            pos=0.0,
            angle=90,
            movable=False,
            pen=pg.mkPen('#ffd600', width=2.0, style=Qt.PenStyle.DashLine)
        )
        plot_item.addItem(v_line)
        self.v_lines.append(v_line)

    def update_plots(self):
        """Actualiza las curvas de datos y la posición del cursor vertical con t_sim."""
        eng = self.engine
        t_cur = eng.t_sim
        self.lbl_time_info.setText(f"t = {t_cur:6.3f} s")

        # Posicionar cursor vertical en el tiempo actual de simulación
        for line in self.v_lines:
            line.setValue(t_cur)

        # Actualizar historial numérico
        t_data = eng.history_t
        if not t_data:
            return

        if 'omega' in self.curves:
            self.curves['omega'].setData(t_data, eng.history_omega)
        if 'v' in self.curves:
            self.curves['v'].setData(t_data, eng.history_v)
        if 'an' in self.curves:
            self.curves['an'].setData(t_data, eng.history_an)
        if 'at' in self.curves:
            self.curves['at'].setData(t_data, eng.history_at)
        if 'atot' in self.curves:
            self.curves['atot'].setData(t_data, eng.history_atot)
        if 'P_total' in self.curves:
            self.curves['P_total'].setData(t_data, eng.history_P_total)
        if 'P_corte' in self.curves:
            self.curves['P_corte'].setData(t_data, eng.history_P_corte)
        if 'P_loss' in self.curves:
            self.curves['P_loss'].setData(t_data, eng.history_P_loss)
        if 'Fu' in self.curves:
            self.curves['Fu'].setData(t_data, eng.history_Fu)
        if 'theta' in self.curves:
            self.curves['theta'].setData(t_data, eng.history_theta)

    def export_current_plot(self):
        """Exporta la vista gráfica actual a un archivo de imagen de alta fidelidad."""
        filepath, _ = QFileDialog.getSaveFileName(
            self, "Guardar Gráfica en Alta Resolución",
            "grafica_simulador_torno_alta_resolucion.png", "Imágenes PNG (*.png)"
        )
        if filepath:
            try:
                import pyqtgraph.exporters
                exporter = pyqtgraph.exporters.ImageExporter(self.plot_layout.scene())
                exporter.parameters()['width'] = 1920
                exporter.export(filepath)
                QMessageBox.information(
                    self, "Exportación Exitosa",
                    f"Gráfica en alta resolución guardada correctamente en:\n{filepath}"
                )
            except Exception as e:
                QMessageBox.warning(self, "Error de Exportación", f"No se pudo guardar la imagen: {e}")

    def _toggle_plot_stretch(self):
        """Alterna entre la vista compacta/centrada y la vista de ancho extendido."""
        self.is_stretched = not self.is_stretched
        if self.is_stretched:
            self.plot_card.setMaximumWidth(16777215)
            self.plot_card.setMaximumHeight(16777215)
            self.btn_toggle_stretch.setText("↔ Vista Centrada / Reducida")
        else:
            self.plot_card.setMaximumWidth(1200)
            self.plot_card.setMaximumHeight(650)
            self.btn_toggle_stretch.setText("↔ Ajustado / Extendido")
