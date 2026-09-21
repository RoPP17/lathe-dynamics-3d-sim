"""
Vista de Resistencia Mecánica: Torsión en Eje y Chaveta (C19) y Mecánica del Contrapunto (C20).
Incluye:
- Gráficas funcionales analíticas de esfuerzo cortante radial τ(r) y fuerza axial F(x).
- Diagramas técnicos 2D interactivos con acotado de ingeniería y vectores de fuerza.
- Diagrama de Cuerpo Libre (DCL) general del husillo y rotor con equilibrio dinámico.
- Fórmulas y variables completamente compiladas en Unicode y HTML enriquecido.
"""

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QGridLayout, QLabel,
    QGroupBox, QFrame, QSplitter, QScrollArea, QPushButton
)
from PyQt6.QtCore import Qt
import pyqtgraph as pg
import numpy as np
from physics.models import LatheParameters
from physics.mechanics import LatheMechanics
from .diagrams import (
    ShaftKeywayDiagramWidget,
    TailstockMechanismDiagramWidget,
    LatheFBDDiagramWidget
)


class MechanicsViewWidget(QWidget):
    """Panel visual e interactivo de resistencia mecánica y diagramas técnicos."""

    def __init__(self, params: LatheParameters, parent=None):
        super().__init__(parent)
        self.params = params.copy()

        # Layout principal con scroll para adaptación fluida a cualquier resolución
        root_layout = QVBoxLayout(self)
        root_layout.setContentsMargins(0, 0, 0, 0)
        root_layout.setSpacing(0)

        scroll = QScrollArea(self)
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.Shape.NoFrame)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        scroll.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)

        content_widget = QWidget()
        main_layout = QVBoxLayout(content_widget)
        main_layout.setContentsMargins(10, 10, 10, 10)
        main_layout.setSpacing(10)

        splitter = QSplitter(Qt.Orientation.Vertical)

        # ----------------------------------------------------------------------
        # SECCIÓN 1: CÁLCULO 19 - TORSIÓN DE EJE Y VERIFICACIÓN DE CHAVETA
        # ----------------------------------------------------------------------
        box_c19 = QGroupBox("CÁLCULO 19: TORSIÓN DEL HUSILLO Y VERIFICACIÓN DE LA CHAVETA (Mₜ = 0.800 N·m)")
        c19_layout = QHBoxLayout(box_c19)
        c19_layout.setContentsMargins(8, 14, 8, 8)
        c19_layout.setSpacing(10)

        # 1. Gráfico pyqtgraph de distribución radial de cortante tau(r)
        self.plot_tau = pg.PlotWidget(title="<b style='color:#0098ff;'>Distribución Radial del Esfuerzo Cortante &tau;(r)</b>")
        self.plot_tau.setLabel('left', 'Cortante &tau;', units='MPa')
        self.plot_tau.setLabel('bottom', 'Radio r', units='mm')
        self.plot_tau.showGrid(x=True, y=True, alpha=0.3)
        self.plot_tau.setMinimumWidth(260)
        c19_layout.addWidget(self.plot_tau, stretch=3)

        # 2. Diagrama 2D de la sección transversal y chavetero con botón de zoom HD
        c19_diag_col = QVBoxLayout()
        c19_diag_col.setSpacing(4)
        self.diagram_c19 = ShaftKeywayDiagramWidget()
        btn_zoom_c19 = QPushButton("🔍 Ampliar Sección y Chavetero C19 (Detalle HD)")
        btn_zoom_c19.setStyleSheet("""
            QPushButton {
                background-color: #202430;
                border: 1px solid #0098ff;
                color: #00e5ff;
                font-size: 11px;
                font-weight: bold;
                padding: 4px 8px;
                border-radius: 4px;
            }
            QPushButton:hover {
                background-color: #0078d4;
                color: #ffffff;
            }
        """)
        btn_zoom_c19.clicked.connect(self.diagram_c19.open_zoom_dialog)
        c19_diag_col.addWidget(self.diagram_c19)
        c19_diag_col.addWidget(btn_zoom_c19)
        c19_layout.addLayout(c19_diag_col, stretch=4)

        # 3. Panel numérico de esfuerzos mecánicos compilados
        frame_c19 = QFrame()
        frame_c19.setStyleSheet("background-color: #202024; border-radius: 6px; padding: 6px; border: 1px solid #33333e;")
        f19_layout = QGridLayout(frame_c19)
        f19_layout.setSpacing(4)

        res_c19 = LatheMechanics.calc_19_torsion_eje_chaveta(
            self.params.M_torsion_diseno, self.params.d_eje, self.params.L_eje,
            self.params.b_chaveta, self.params.h_chaveta, self.params.l_chaveta,
            self.params.Kt_chaveta, self.params.G_acero
        )

        f19_layout.addWidget(QLabel("<b>Momento Polar de Inercia (J):</b>"), 0, 0)
        f19_layout.addWidget(QLabel(f"<span style='color:#00e5ff;'>{res_c19['J_m4']:.4e} m⁴</span>"), 0, 1)

        f19_layout.addWidget(QLabel("<b>Cortante Nominal (&tau;<sub>nom</sub>):</b>"), 1, 0)
        f19_layout.addWidget(QLabel(f"{res_c19['tau_nom_MPa']:.3f} MPa"), 1, 1)

        f19_layout.addWidget(QLabel("<b>Cortante Máx. Chavetero (&tau;<sub>máx</sub>):</b>"), 2, 0)
        f19_layout.addWidget(QLabel(f"<b style='color:#69f0ae; font-size:13px;'>{res_c19['tau_max_MPa']:.3f} MPa</b> (Kt = 1.6)"), 2, 1)

        f19_layout.addWidget(QLabel("<b>Cortante en Chaveta (&tau;<sub>chaveta</sub>):</b>"), 3, 0)
        f19_layout.addWidget(QLabel(f"{res_c19['tau_key_MPa']:.3f} MPa"), 3, 1)

        f19_layout.addWidget(QLabel("<b>Aplastamiento Lateral (&sigma;<sub>aplast</sub>):</b>"), 4, 0)
        f19_layout.addWidget(QLabel(f"{res_c19['sigma_aplast_MPa']:.3f} MPa"), 4, 1)

        f19_layout.addWidget(QLabel("<b>Deformación Angular (&phi;):</b>"), 5, 0)
        f19_layout.addWidget(QLabel(f"{res_c19['phi_rad']:.2e} rad ({res_c19['phi_deg']:.5f}°)"), 5, 1)

        lbl_note_c19 = QLabel(
            "<i>* Acero AISI 1018: Límite de fluencia S<sub>y</sub> = 370 MPa, S<sub>sy</sub> &asymp; 213 MPa.<br/>"
            "Factor de Seguridad: FS = S<sub>sy</sub> / &tau;<sub>máx</sub> = 213 / 0.950 &gt; 220.</i>"
        )
        lbl_note_c19.setStyleSheet("color: #888894; font-size: 11px;")
        f19_layout.addWidget(lbl_note_c19, 6, 0, 1, 2)

        c19_layout.addWidget(frame_c19, stretch=3)
        splitter.addWidget(box_c19)

        # ----------------------------------------------------------------------
        # SECCIÓN 2: CÁLCULO 20 - MECÁNICA DEL CONTRAPUNTO
        # ----------------------------------------------------------------------
        box_c20 = QGroupBox("CÁLCULO 20: MECÁNICA HELICOIDAL DE FIJACIÓN DEL CONTRAPUNTO (x = 1.5 mm)")
        c20_layout = QHBoxLayout(box_c20)
        c20_layout.setContentsMargins(8, 14, 8, 8)
        c20_layout.setSpacing(10)

        # 1. Gráfico pyqtgraph de fuerza axial elástica vs avance F(x)
        self.plot_f_axial = pg.PlotWidget(title="<b style='color:#0098ff;'>Fuerza Axial de Apriete vs Avance F(x) = F₀ + k&middot;x</b>")
        self.plot_f_axial.setLabel('left', 'Fuerza Axial F', units='N')
        self.plot_f_axial.setLabel('bottom', 'Avance Axial x', units='mm')
        self.plot_f_axial.showGrid(x=True, y=True, alpha=0.3)
        self.plot_f_axial.setMinimumWidth(260)
        c20_layout.addWidget(self.plot_f_axial, stretch=3)

        # 2. Diagrama 2D cinemático del mecanismo helicoidal con botón de zoom HD
        c20_diag_col = QVBoxLayout()
        c20_diag_col.setSpacing(4)
        self.diagram_c20 = TailstockMechanismDiagramWidget()
        btn_zoom_c20 = QPushButton("🔍 Ampliar Mecanismo Contrapunto C20 (Detalle HD)")
        btn_zoom_c20.setStyleSheet("""
            QPushButton {
                background-color: #242218;
                border: 1px solid #ffd54f;
                color: #ffd54f;
                font-size: 11px;
                font-weight: bold;
                padding: 4px 8px;
                border-radius: 4px;
            }
            QPushButton:hover {
                background-color: #b28900;
                color: #ffffff;
            }
        """)
        btn_zoom_c20.clicked.connect(self.diagram_c20.open_zoom_dialog)
        c20_diag_col.addWidget(self.diagram_c20)
        c20_diag_col.addWidget(btn_zoom_c20)
        c20_layout.addLayout(c20_diag_col, stretch=4)

        # 3. Panel numérico de contrapunto compilado
        frame_c20 = QFrame()
        frame_c20.setStyleSheet("background-color: #202024; border-radius: 6px; padding: 6px; border: 1px solid #33333e;")
        f20_layout = QGridLayout(frame_c20)
        f20_layout.setSpacing(4)

        res_c20 = LatheMechanics.calc_20_mecanica_contrapunto(
            self.params.F0_cp, self.params.k_cp, self.params.x_cp,
            self.params.p_cp, self.params.r_volante
        )

        f20_layout.addWidget(QLabel("<b>Precarga Inicial (F₀):</b>"), 0, 0)
        f20_layout.addWidget(QLabel(f"{self.params.F0_cp:.1f} N"), 0, 1)

        f20_layout.addWidget(QLabel("<b>Fuerza Axial de Apriete (F<sub>final</sub>):</b>"), 1, 0)
        f20_layout.addWidget(QLabel(f"<b style='color:#00e5ff; font-size:13px;'>{res_c20['F_final_N']:.1f} N</b>"), 1, 1)

        f20_layout.addWidget(QLabel("<b>Trabajo Elástico Acumulado (U<sub>axial</sub>):</b>"), 2, 0)
        f20_layout.addWidget(QLabel(f"{res_c20['U_axial_J']:.4f} J"), 2, 1)

        f20_layout.addWidget(QLabel("<b>Vueltas de Volante (N = x/p):</b>"), 3, 0)
        f20_layout.addWidget(QLabel(f"{res_c20['N_vueltas_rev']:.2f} rev ({res_c20['angulo_volante_deg']:.0f}°)"), 3, 1)

        f20_layout.addWidget(QLabel("<b>Par Torsor Resistente (M):</b>"), 4, 0)
        f20_layout.addWidget(QLabel(f"{res_c20['M_torsor_Nm']:.4f} N·m"), 4, 1)

        f20_layout.addWidget(QLabel("<b>Fuerza Manual en Llanta (F<sub>mano</sub>):</b>"), 5, 0)
        f20_layout.addWidget(QLabel(f"<b style='color:#69f0ae; font-size:13px;'>{res_c20['F_mano_N']:.2f} N</b> (~{res_c20['F_mano_gf']:.0f} gf)"), 5, 1)

        lbl_note_c20 = QLabel(
            "<i>* Volante manual r<sub>v</sub> = 60 mm, husillo rosca M14x2 (p = 2 mm/rev).<br/>"
            "Esfuerzo ergonómico muy suave: menos de 300 gramos-fuerza.</i>"
        )
        lbl_note_c20.setStyleSheet("color: #888894; font-size: 11px;")
        f20_layout.addWidget(lbl_note_c20, 6, 0, 1, 2)

        c20_layout.addWidget(frame_c20, stretch=3)
        splitter.addWidget(box_c20)

        # ----------------------------------------------------------------------
        # SECCIÓN 3: DIAGRAMA DE CUERPO LIBRE INTEGRAL (DCL)
        # ----------------------------------------------------------------------
        box_dcl = QGroupBox("DIAGRAMA DE CUERPO LIBRE (DCL) — EQUILIBRIO DINÁMICO DEL HUSILLO Y ROTOR")
        dcl_layout = QVBoxLayout(box_dcl)
        dcl_layout.setContentsMargins(8, 12, 8, 8)
        dcl_layout.setSpacing(6)

        self.diagram_dcl = LatheFBDDiagramWidget()
        btn_zoom_dcl = QPushButton("🔍 Ampliar Diagrama de Cuerpo Libre DCL en Pantalla Completa (Detalle HD)")
        btn_zoom_dcl.setStyleSheet("""
            QPushButton {
                background-color: #1a2820;
                border: 1px solid #69f0ae;
                color: #69f0ae;
                font-size: 11px;
                font-weight: bold;
                padding: 5px 12px;
                border-radius: 4px;
            }
            QPushButton:hover {
                background-color: #007e33;
                color: #ffffff;
            }
        """)
        btn_zoom_dcl.clicked.connect(self.diagram_dcl.open_zoom_dialog)

        dcl_layout.addWidget(self.diagram_dcl)
        dcl_layout.addWidget(btn_zoom_dcl)
        splitter.addWidget(box_dcl)

        main_layout.addWidget(splitter)
        scroll.setWidget(content_widget)
        root_layout.addWidget(scroll)

        # Dibujar curvas en pyqtgraph
        self._plot_c19(res_c19)
        self._plot_c20()

    def _plot_c19(self, res_c19):
        r_mm = np.linspace(0.0, 9.5, 100)
        tau_r = res_c19['tau_nom_MPa'] * (r_mm / 9.5)
        self.plot_tau.plot(r_mm, tau_r, pen=pg.mkPen('#00b0ff', width=2.5))
        # Punto en el borde exterior
        self.plot_tau.plot([9.5], [res_c19['tau_nom_MPa']], pen=None, symbol='o', symbolBrush='#ff3d00', symbolSize=8)

    def _plot_c20(self):
        x_mm = np.linspace(0.0, 1.5, 100)
        F_axial = self.params.F0_cp + self.params.k_cp * (x_mm * 1e-3)
        self.plot_f_axial.plot(x_mm, F_axial, pen=pg.mkPen('#ff9100', width=2.5))
        self.plot_f_axial.plot([1.5], [575.0], pen=None, symbol='o', symbolBrush='#00e676', symbolSize=8)
