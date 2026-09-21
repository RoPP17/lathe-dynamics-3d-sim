"""
Panel de Modo Experimental y Recálculo Paramétrico en Cascada.
Permite modificar parámetros operativos y observar la respuesta del torno.
Incluye:
- Presets de escenarios mecánicos (Pino base, Madera dura, Desbalance severo, Alta velocidad, Desbaste pesado).
- Controles numéricos con límites físicos seguros.
- Tabla comparativa de recálculo en cascada con evaluación de delta (Δ) y porcentaje.
"""

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QGridLayout, QLabel,
    QDoubleSpinBox, QSpinBox, QPushButton, QGroupBox, QTableWidget,
    QTableWidgetItem, QHeaderView, QMessageBox
)
from PyQt6.QtCore import Qt, pyqtSignal
from physics.models import LatheParameters
from config.constants import *


class ExperimentalModeWidget(QWidget):
    """Interfaz para experimentación paramétrica y análisis de sensibilidad."""

    parameters_changed = pyqtSignal(LatheParameters)

    def __init__(self, current_params: LatheParameters, parent=None):
        super().__init__(parent)
        self.baseline_params = LatheParameters() # Caso oficial Avance 2
        self.exp_params = current_params.copy()

        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(12, 12, 12, 12)
        main_layout.setSpacing(10)

        # ----------------------------------------------------------------------
        # 1. Presets de Ingeniería Rápidos (One-Click)
        # ----------------------------------------------------------------------
        presets_box = QGroupBox("PRESETS DE INGENIERÍA RÁPIDOS")
        p_layout = QHBoxLayout(presets_box)
        p_layout.setContentsMargins(8, 12, 8, 8)
        p_layout.setSpacing(8)

        btn_pre_base = QPushButton("🌲 Pino Radiata (Caso Base)")
        btn_pre_base.setToolTip("Carga parámetros nominales oficiales del Avance 2")
        btn_pre_base.clicked.connect(self.restore_baseline)

        btn_pre_hardwood = QPushButton("🌳 Madera Dura (Roble Fc=45N)")
        btn_pre_hardwood.setToolTip("Madera de alta densidad y mayor resistencia al corte")
        btn_pre_hardwood.clicked.connect(lambda: self._load_preset(1500, 2.5, 45.0, 1.5, 20.0, 2.0, 3.8))

        btn_pre_unbalance = QPushButton("⚠️ Desbalance Severo (mu=60g)")
        btn_pre_unbalance.setToolTip("Nudo excéntrico de alta masa que induce fuertes vibraciones")
        btn_pre_unbalance.clicked.connect(lambda: self._load_preset(1700, 2.0, 20.0, 2.5, 60.0, 5.0, 3.5))

        btn_pre_hispeed = QPushButton("⚡ Alta Velocidad (2500 RPM)")
        btn_pre_hispeed.setToolTip("Acabado fino superficial a alta velocidad de corte")
        btn_pre_hispeed.clicked.connect(lambda: self._load_preset(2500, 3.0, 12.0, 1.0, 10.0, 1.0, 4.5))

        btn_pre_heavycut = QPushButton("🪓 Desbaste Pesado (Fc=65N)")
        btn_pre_heavycut.setToolTip("Corte agresivo con alto avance radial y demanda de potencia")
        btn_pre_heavycut.clicked.connect(lambda: self._load_preset(1200, 1.8, 65.0, 8.0, 25.0, 2.5, 3.0))

        p_layout.addWidget(btn_pre_base)
        p_layout.addWidget(btn_pre_hardwood)
        p_layout.addWidget(btn_pre_unbalance)
        p_layout.addWidget(btn_pre_hispeed)
        p_layout.addWidget(btn_pre_heavycut)
        main_layout.addWidget(presets_box)

        # ----------------------------------------------------------------------
        # 2. Controles de Parámetros Operativos Editables
        # ----------------------------------------------------------------------
        inputs_box = QGroupBox("PARÁMETROS OPERATIVOS EDITABLES")
        i_layout = QGridLayout(inputs_box)
        i_layout.setContentsMargins(10, 14, 10, 10)
        i_layout.setSpacing(10)

        # 2.1 Velocidad nominal n (rpm)
        i_layout.addWidget(QLabel("Velocidad Nominal (n):"), 0, 0)
        self.spin_n = QSpinBox()
        self.spin_n.setRange(500, 3500)
        self.spin_n.setSingleStep(50)
        self.spin_n.setValue(int(self.exp_params.n_nom))
        self.spin_n.setSuffix(" rpm")
        i_layout.addWidget(self.spin_n, 0, 1)

        # 2.2 Tiempo de aceleración dt_arranque (s)
        i_layout.addWidget(QLabel("Tiempo de Arranque (Δt_arr):"), 0, 2)
        self.spin_dt_arr = QDoubleSpinBox()
        self.spin_dt_arr.setRange(0.4, 8.0)
        self.spin_dt_arr.setSingleStep(0.25)
        self.spin_dt_arr.setValue(self.exp_params.dt_arranque)
        self.spin_dt_arr.setSuffix(" s")
        i_layout.addWidget(self.spin_dt_arr, 0, 3)

        # 2.3 Fuerza de corte Fc (N)
        i_layout.addWidget(QLabel("Fuerza de Corte (Fc):"), 1, 0)
        self.spin_fc = QDoubleSpinBox()
        self.spin_fc.setRange(2.0, 150.0)
        self.spin_fc.setSingleStep(5.0)
        self.spin_fc.setValue(self.exp_params.Fc)
        self.spin_fc.setSuffix(" N")
        i_layout.addWidget(self.spin_fc, 1, 1)

        # 2.4 Avance radial fr (um/rev)
        i_layout.addWidget(QLabel("Avance Radial (fr):"), 1, 2)
        self.spin_fr = QDoubleSpinBox()
        self.spin_fr.setRange(0.5, 30.0)
        self.spin_fr.setSingleStep(0.5)
        self.spin_fr.setValue(self.exp_params.fr * 1e6)
        self.spin_fr.setSuffix(" µm/rev")
        i_layout.addWidget(self.spin_fr, 1, 3)

        # 2.5 Masa excéntrica mu (g)
        i_layout.addWidget(QLabel("Masa Excéntrica (mu):"), 2, 0)
        self.spin_mu = QDoubleSpinBox()
        self.spin_mu.setRange(0.0, 200.0)
        self.spin_mu.setSingleStep(5.0)
        self.spin_mu.setValue(self.exp_params.mu * 1000.0)
        self.spin_mu.setSuffix(" g")
        i_layout.addWidget(self.spin_mu, 2, 1)

        # 2.6 Excentricidad e (mm)
        i_layout.addWidget(QLabel("Radio Excentricidad (e):"), 2, 2)
        self.spin_e = QDoubleSpinBox()
        self.spin_e.setRange(0.0, 15.0)
        self.spin_e.setSingleStep(0.5)
        self.spin_e.setValue(self.exp_params.e_desbalance * 1000.0)
        self.spin_e.setSuffix(" mm")
        i_layout.addWidget(self.spin_e, 2, 3)

        # 2.7 Tiempo de parada libre (s)
        i_layout.addWidget(QLabel("Tiempo Parada Libre (Δt_stop):"), 3, 0)
        self.spin_dt_stop = QDoubleSpinBox()
        self.spin_dt_stop.setRange(0.8, 10.0)
        self.spin_dt_stop.setSingleStep(0.5)
        self.spin_dt_stop.setValue(self.exp_params.dt_parada)
        self.spin_dt_stop.setSuffix(" s")
        i_layout.addWidget(self.spin_dt_stop, 3, 1)

        main_layout.addWidget(inputs_box)

        # Botonera de acciones
        btn_layout = QHBoxLayout()
        self.btn_apply = QPushButton("⚡ APLICAR CAMBIOS Y RECALCULAR FÍSICA")
        self.btn_apply.setObjectName("btnPrimary")
        self.btn_apply.clicked.connect(self.apply_changes)

        self.btn_reset = QPushButton("↺ RESTAURAR CASO BASE (AVANCE 2)")
        self.btn_reset.clicked.connect(self.restore_baseline)

        btn_layout.addWidget(self.btn_apply)
        btn_layout.addWidget(self.btn_reset)
        btn_layout.addStretch()
        main_layout.addLayout(btn_layout)

        # ----------------------------------------------------------------------
        # 3. Tabla Comparativa: Caso Base vs Modo Experimental
        # ----------------------------------------------------------------------
        diff_box = QGroupBox("IMPACTO EN LAS VARIABLES DINÁMICAS (RECÁLCULO EN CASCADA)")
        d_layout = QVBoxLayout(diff_box)
        d_layout.setContentsMargins(8, 12, 8, 8)

        self.table_diff = QTableWidget()
        self.table_diff.setColumnCount(6)
        self.table_diff.setHorizontalHeaderLabels([
            "Variable Dinámica", "Símbolo", "Caso Base (Avance 2)",
            "Modo Experimental", "Diferencia (Δ)", "Variación (%)"
        ])
        self.table_diff.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.table_diff.verticalHeader().setVisible(False)
        d_layout.addWidget(self.table_diff)

        main_layout.addWidget(diff_box)

        # Actualizar tabla inicial
        self._update_comparison_table()

    def _load_preset(self, n: int, dt_arr: float, fc: float, fr: float, mu: float, e: float, dt_stop: float):
        """Carga un preset en los controles y aplica inmediatamente el recálculo."""
        self.spin_n.setValue(n)
        self.spin_dt_arr.setValue(dt_arr)
        self.spin_fc.setValue(fc)
        self.spin_fr.setValue(fr)
        self.spin_mu.setValue(mu)
        self.spin_e.setValue(e)
        self.spin_dt_stop.setValue(dt_stop)
        self.apply_changes(show_msg=False)

    def apply_changes(self, show_msg: bool = True):
        """Aplica los nuevos parámetros y recalcula la física completa."""
        self.exp_params.n_nom = float(self.spin_n.value())
        self.exp_params.dt_arranque = float(self.spin_dt_arr.value())
        self.exp_params.Fc = float(self.spin_fc.value())
        self.exp_params.fr = float(self.spin_fr.value()) * 1e-6
        self.exp_params.mu = float(self.spin_mu.value()) * 1e-3
        self.exp_params.e_desbalance = float(self.spin_e.value()) * 1e-3
        self.exp_params.dt_parada = float(self.spin_dt_stop.value())

        self._update_comparison_table()
        self.parameters_changed.emit(self.exp_params)
        if show_msg:
            QMessageBox.information(
                self, "Recálculo Completado",
                "Modelo físico y parámetros de simulación actualizados exitosamente."
            )

    def restore_baseline(self, show_msg: bool = True):
        """Restaura los valores nominales oficiales del Caso Avance 2."""
        self.exp_params = self.baseline_params.copy()
        self.spin_n.setValue(int(self.exp_params.n_nom))
        self.spin_dt_arr.setValue(self.exp_params.dt_arranque)
        self.spin_fc.setValue(self.exp_params.Fc)
        self.spin_fr.setValue(self.exp_params.fr * 1e6)
        self.spin_mu.setValue(self.exp_params.mu * 1000.0)
        self.spin_e.setValue(self.exp_params.e_desbalance * 1000.0)
        self.spin_dt_stop.setValue(self.exp_params.dt_parada)

        self._update_comparison_table()
        self.parameters_changed.emit(self.exp_params)
        if show_msg:
            QMessageBox.information(
                self, "Caso Base Restaurado",
                "Se han restablecido los parámetros oficiales originales del Avance 2."
            )

    def _update_comparison_table(self):
        """Calcula el delta en cascada para las magnitudes dinámicas fundamentales."""
        p_base = self.baseline_params
        p_exp = self.exp_params

        # Caso Base
        w_b = p_base.omega_nom
        v_b = w_b * p_base.R0
        an_b = (w_b ** 2) * p_base.R0
        at_b = (w_b / p_base.dt_arranque) * p_base.R0
        Fu_b = p_base.mu * p_base.e_desbalance * (w_b ** 2)
        Ptot_b = p_base.Fc * v_b + p_base.b_viscoso * (w_b ** 2)
        Pc_b = p_base.Fc * v_b
        tau_b = p_base.M_torsion_diseno * (p_base.d_eje / 2.0) / ((math.pi * (p_base.d_eje**4)) / 32.0) / 1e6

        # Modo Experimental
        w_e = p_exp.omega_nom
        v_e = w_e * p_exp.R0
        an_e = (w_e ** 2) * p_exp.R0
        at_e = (w_e / p_exp.dt_arranque) * p_exp.R0
        Fu_e = p_exp.mu * p_exp.e_desbalance * (w_e ** 2)
        Ptot_e = p_exp.Fc * v_e + p_exp.b_viscoso * (w_e ** 2)
        Pc_e = p_exp.Fc * v_e
        M_exp = p_exp.Fc * p_exp.R0
        tau_e = M_exp * (p_exp.d_eje / 2.0) / ((math.pi * (p_exp.d_eje**4)) / 32.0) / 1e6

        items = [
            ("Velocidad angular de régimen", "ω", w_b, w_e, "rad/s"),
            ("Velocidad tangencial periférica", "v", v_b, v_e, "m/s"),
            ("Aceleración normal centrípeta", "aₙ", an_b, an_e, "m/s²"),
            ("Aceleración tangencial media", "aₜ", at_b, at_e, "m/s²"),
            ("Fuerza centrífuga de desbalance", "Fᵤ", Fu_b, Fu_e, "N"),
            ("Potencia útil de mecanizado", "P(corte)", Pc_b, Pc_e, "W"),
            ("Potencia total demandada", "P(total)", Ptot_b, Ptot_e, "W"),
            ("Esfuerzo cortante torsional nominal", "τ(nom)", tau_b, tau_e, "MPa")
        ]

        self.table_diff.setRowCount(len(items))
        for row, (name, sym, val_b, val_e, unit) in enumerate(items):
            diff = val_e - val_b
            pct = (diff / val_b * 100.0) if val_b != 0 else 0.0

            it_name = QTableWidgetItem(name)
            it_sym = QTableWidgetItem(sym); it_sym.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            it_base = QTableWidgetItem(f"{val_b:.4g} {unit}"); it_base.setTextAlignment(Qt.AlignmentFlag.AlignRight)
            it_exp = QTableWidgetItem(f"{val_e:.4g} {unit}"); it_exp.setTextAlignment(Qt.AlignmentFlag.AlignRight)
            it_diff = QTableWidgetItem(f"{diff:+.4g} {unit}"); it_diff.setTextAlignment(Qt.AlignmentFlag.AlignRight)
            it_pct = QTableWidgetItem(f"{pct:+.2f}%"); it_pct.setTextAlignment(Qt.AlignmentFlag.AlignRight)

            if abs(pct) > 0.01:
                color = Qt.GlobalColor.cyan if pct > 0 else Qt.GlobalColor.yellow
                it_pct.setForeground(color)

            self.table_diff.setItem(row, 0, it_name)
            self.table_diff.setItem(row, 1, it_sym)
            self.table_diff.setItem(row, 2, it_base)
            self.table_diff.setItem(row, 3, it_exp)
            self.table_diff.setItem(row, 4, it_diff)
            self.table_diff.setItem(row, 5, it_pct)
