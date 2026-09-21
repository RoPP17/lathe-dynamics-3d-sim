"""
Panel de Instrumentación Digital y Telemetría Técnica en Tiempo Real.
Diseñado con contenedor autoajustable y QScrollArea fluida para garantizar
que ningún elemento se comprima o mutile en pantalla completa o resoluciones escaladas.
"""

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QGridLayout, QLabel,
    QGroupBox, QCheckBox, QFrame, QProgressBar, QScrollArea
)
from PyQt6.QtCore import Qt
from physics.models import DynamicState
from config.constants import MOTOR_POTENCIA_NOM_W


class TelemetryCard(QFrame):
    """Tarjeta digital de telemetría con tamaño mínimo protegido contra compresión."""

    def __init__(self, title: str, unit: str, parent=None):
        super().__init__(parent)
        self.setFrameShape(QFrame.Shape.StyledPanel)
        self.setMinimumHeight(54)
        self.setStyleSheet("""
            QFrame {
                background-color: #202024;
                border: 1px solid #32323a;
                border-radius: 5px;
                padding: 3px;
            }
        """)
        layout = QVBoxLayout(self)
        layout.setContentsMargins(6, 4, 6, 4)
        layout.setSpacing(2)

        self.lbl_title = QLabel(title.upper())
        self.lbl_title.setStyleSheet("font-size: 9px; color: #888894; font-weight: bold; letter-spacing: 0.5px;")

        val_layout = QHBoxLayout()
        val_layout.setContentsMargins(0, 0, 0, 0)
        val_layout.setSpacing(4)
        self.lbl_value = QLabel("0.00")
        self.lbl_value.setStyleSheet("font-family: 'Consolas', monospace; font-size: 15px; font-weight: bold; color: #00e5ff;")

        self.lbl_unit = QLabel(unit)
        self.lbl_unit.setStyleSheet("font-size: 11px; color: #9999a4; font-weight: normal;")
        val_layout.addWidget(self.lbl_value)
        val_layout.addWidget(self.lbl_unit)
        val_layout.addStretch()

        layout.addWidget(self.lbl_title)
        layout.addLayout(val_layout)

    def set_value(self, val_str: str, color: str = "#00e5ff"):
        self.lbl_value.setText(val_str)
        self.lbl_value.setStyleSheet(f"font-family: 'Consolas', monospace; font-size: 15px; font-weight: bold; color: {color};")


class DashboardPanel(QWidget):
    """Panel lateral de control e instrumentación física con protección contra compresión."""

    def __init__(self, parent=None):
        super().__init__(parent)
        # Rango elástico de anchura que responde perfectamente tanto en ventana normal como en pantalla completa
        self.setMinimumWidth(330)
        self.setMaximumWidth(420)

        # Layout raíz del widget
        root_layout = QVBoxLayout(self)
        root_layout.setContentsMargins(0, 0, 0, 0)
        root_layout.setSpacing(0)

        # ScrollArea técnica integrada para proteger todas las tarjetas dinámicas
        scroll = QScrollArea(self)
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.Shape.NoFrame)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        scroll.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        scroll.setStyleSheet("""
            QScrollArea {
                background-color: transparent;
                border: none;
            }
            QScrollBar:vertical {
                background: #141418;
                width: 6px;
                margin: 0px;
            }
            QScrollBar::handle:vertical {
                background: #33333e;
                border-radius: 3px;
                min-height: 25px;
            }
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
                height: 0px;
            }
        """)

        content_widget = QWidget()
        main_layout = QVBoxLayout(content_widget)
        main_layout.setContentsMargins(8, 8, 8, 8)
        main_layout.setSpacing(8)

        # ----------------------------------------------------------------------
        # 1. Estado de Operación Actual
        # ----------------------------------------------------------------------
        phase_box = QGroupBox("ESTADO DE OPERACIÓN")
        p_layout = QVBoxLayout(phase_box)
        p_layout.setContentsMargins(8, 12, 8, 8)

        self.lbl_fase = QLabel("RÉGIMEN ESTABLE NOMINAL")
        self.lbl_fase.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.lbl_fase.setStyleSheet("""
            background-color: #004d40;
            color: #4db6ac;
            font-size: 11px;
            font-weight: bold;
            padding: 6px;
            border-radius: 4px;
            border: 1px solid #00796b;
        """)
        p_layout.addWidget(self.lbl_fase)
        main_layout.addWidget(phase_box)

        # ----------------------------------------------------------------------
        # 2. Utilización de Potencia del Motor (P = 735.5 W / 1 CV)
        # ----------------------------------------------------------------------
        power_box = QGroupBox("DEMANDA DE POTENCIA DEL MOTOR")
        pw_layout = QVBoxLayout(power_box)
        pw_layout.setContentsMargins(8, 12, 8, 8)
        pw_layout.setSpacing(4)

        self.lbl_power_header = QLabel("Potencia: 0.0 W / 735.5 W (0.0%)")
        self.lbl_power_header.setStyleSheet("font-size: 11px; color: #d0d0d8; font-weight: bold;")
        pw_layout.addWidget(self.lbl_power_header)

        self.bar_power = QProgressBar()
        self.bar_power.setRange(0, 100)
        self.bar_power.setValue(0)
        self.bar_power.setTextVisible(False)
        self.bar_power.setFixedHeight(12)
        self.bar_power.setStyleSheet("""
            QProgressBar {
                background-color: #1a1a1e;
                border: 1px solid #33333c;
                border-radius: 4px;
            }
            QProgressBar::chunk {
                background-color: #00e676;
                border-radius: 3px;
            }
        """)
        pw_layout.addWidget(self.bar_power)

        self.lbl_power_margin = QLabel("Margen de Reserva: 100.0%  |  FS = ∞")
        self.lbl_power_margin.setStyleSheet("font-size: 10px; color: #888894;")
        pw_layout.addWidget(self.lbl_power_margin)

        main_layout.addWidget(power_box)

        # ----------------------------------------------------------------------
        # 3. Alerta Dinámica de Desbalance y Vibraciones
        # ----------------------------------------------------------------------
        self.frame_alert = QFrame()
        self.frame_alert.setStyleSheet("""
            QFrame {
                background-color: #1a1e24;
                border: 1px solid #293845;
                border-radius: 4px;
                padding: 4px;
            }
        """)
        alert_layout = QVBoxLayout(self.frame_alert)
        alert_layout.setContentsMargins(6, 6, 6, 6)
        alert_layout.setSpacing(2)

        self.lbl_alert_title = QLabel("✓ BALANCE DINÁMICO ESTABLE")
        self.lbl_alert_title.setStyleSheet("font-size: 10px; font-weight: bold; color: #4db6ac;")
        self.lbl_alert_desc = QLabel("Fᵤ < 0.1 N | Vibración despreciable")
        self.lbl_alert_desc.setStyleSheet("font-size: 10px; color: #888892;")
        alert_layout.addWidget(self.lbl_alert_title)
        alert_layout.addWidget(self.lbl_alert_desc)
        main_layout.addWidget(self.frame_alert)

        # ----------------------------------------------------------------------
        # 4. Telemetría Física Digital (10 Tarjetas)
        # ----------------------------------------------------------------------
        telemetry_box = QGroupBox("TELEMETRÍA DINÁMICA (10 PARÁMETROS)")
        t_layout = QGridLayout(telemetry_box)
        t_layout.setContentsMargins(6, 12, 6, 6)
        t_layout.setSpacing(5)

        self.card_rpm = TelemetryCard("Velocidad de Giro", "rpm")
        self.card_omega = TelemetryCard("Velocidad Angular (ω)", "rad/s")
        self.card_v = TelemetryCard("Rapidez Tangencial (v)", "m/s")
        self.card_an = TelemetryCard("Acel. Normal (aₙ)", "m/s²")
        self.card_at = TelemetryCard("Acel. Tangencial (aₜ)", "m/s²")
        self.card_atot = TelemetryCard("Acel. Resultante (a)", "m/s²")
        self.card_Fu = TelemetryCard("Fuerza Desbalance (Fᵤ)", "N")
        self.card_Ptot = TelemetryCard("Potencia Demandada (P)", "W")
        self.card_eff = TelemetryCard("Eficiencia Útil (η)", "%")
        self.card_rev = TelemetryCard("Vueltas Acumuladas (N)", "rev")

        t_layout.addWidget(self.card_rpm, 0, 0)
        t_layout.addWidget(self.card_omega, 0, 1)
        t_layout.addWidget(self.card_v, 1, 0)
        t_layout.addWidget(self.card_an, 1, 1)
        t_layout.addWidget(self.card_at, 2, 0)
        t_layout.addWidget(self.card_atot, 2, 1)
        t_layout.addWidget(self.card_Fu, 3, 0)
        t_layout.addWidget(self.card_Ptot, 3, 1)
        t_layout.addWidget(self.card_eff, 4, 0)
        t_layout.addWidget(self.card_rev, 4, 1)

        main_layout.addWidget(telemetry_box)

        # ----------------------------------------------------------------------
        # 5. Capas de Vectores 3D en el Espacio
        # ----------------------------------------------------------------------
        vectors_box = QGroupBox("CAPAS DE VECTORES 3D")
        v_layout = QVBoxLayout(vectors_box)
        v_layout.setContentsMargins(8, 12, 8, 6)
        v_layout.setSpacing(5)

        self.chk_vel = QCheckBox("Velocidad Tangencial  v⃗ (C01)")
        self.chk_at = QCheckBox("Acel. Tangencial  a⃗ₜ (C02)")
        self.chk_an = QCheckBox("Acel. Normal  a⃗ₙ (C02)")
        self.chk_atot = QCheckBox("Acel. Resultante  a⃗ (C10)")
        self.chk_Fu = QCheckBox("Fuerza Desbalance  F⃗ᵤ (C11)")
        self.chk_Fc = QCheckBox("Fuerza de Corte  F⃗꜀ (C13)")
        self.chk_viruta = QCheckBox("Reacción Viruta  F⃗(reac) (C15)")

        self.chk_vel.setChecked(True)
        self.chk_at.setChecked(True)
        self.chk_an.setChecked(True)
        self.chk_atot.setChecked(False)
        self.chk_Fu.setChecked(True)
        self.chk_Fc.setChecked(True)
        self.chk_viruta.setChecked(True)

        v_layout.addWidget(self.chk_vel)
        v_layout.addWidget(self.chk_at)
        v_layout.addWidget(self.chk_an)
        v_layout.addWidget(self.chk_atot)
        v_layout.addWidget(self.chk_Fu)
        v_layout.addWidget(self.chk_Fc)
        v_layout.addWidget(self.chk_viruta)

        main_layout.addWidget(vectors_box)
        main_layout.addStretch()

        scroll.setWidget(content_widget)
        root_layout.addWidget(scroll)

    def update_telemetry(self, st: DynamicState):
        """Actualiza la instrumentación y las lecturas en tiempo real."""
        # 1. Indicador de fase operativa
        phase_colors = {
            "ARRANQUE": ("#162a38", "#38bdf8", "1. ARRANQUE EXPONENCIAL"),
            "REGIMEN": ("#06382b", "#34d399", "2. RÉGIMEN ESTABLE NOMINAL"),
            "TORNEADO": ("#3d2407", "#fbbf24", "3. TORNEADO / MECANIZADO"),
            "DESBALANCE": ("#3b1111", "#f87171", "4. DESBALANCE DINÁMICO (Fu)"),
            "PARADA": ("#23242c", "#a5b4fc", "5. PARADA LIBRE (RUN-DOWN)")
        }
        bg, fg, label_txt = phase_colors.get(st.fase, ("#222", "#ccc", st.fase))
        self.lbl_fase.setText(label_txt)
        self.lbl_fase.setStyleSheet(f"""
            background-color: {bg};
            color: {fg};
            font-size: 11px;
            font-weight: bold;
            padding: 5px;
            border-radius: 4px;
            border: 1px solid {fg};
        """)

        # 2. Barra de utilización de potencia
        p_pct = min(100.0, (st.P_total / MOTOR_POTENCIA_NOM_W) * 100.0) if MOTOR_POTENCIA_NOM_W > 0 else 0.0
        self.bar_power.setValue(int(p_pct))
        self.lbl_power_header.setText(f"Potencia: {st.P_total:5.1f} W / {MOTOR_POTENCIA_NOM_W:.1f} W ({p_pct:4.1f}%)")

        margin_pct = max(0.0, 100.0 - p_pct)
        fs_str = f"{MOTOR_POTENCIA_NOM_W / st.P_total:.2f}" if st.P_total > 1.0 else "∞"
        self.lbl_power_margin.setText(f"Margen: {margin_pct:4.1f}%  |  FS Motor = {fs_str}")

        chunk_color = "#00e676" if p_pct < 60 else ("#ffab00" if p_pct < 85 else "#ff1744")
        self.bar_power.setStyleSheet(f"""
            QProgressBar {{
                background-color: #1a1a1e;
                border: 1px solid #33333c;
                border-radius: 4px;
            }}
            QProgressBar::chunk {{
                background-color: {chunk_color};
                border-radius: 3px;
            }}
        """)

        # 3. Alerta de desbalance centrífugo
        if st.F_desbalance > 2.0:
            reac = st.F_desbalance / 2.0
            self.frame_alert.setStyleSheet("QFrame { background-color: #3b1111; border: 1px solid #f87171; border-radius: 4px; padding: 4px; }")
            self.lbl_alert_title.setText("⚠️ ALERTA DE VIBRACIÓN EXCÉNTRICA")
            self.lbl_alert_title.setStyleSheet("font-size: 10px; font-weight: bold; color: #f87171;")
            self.lbl_alert_desc.setText(f"Fu = {st.F_desbalance:.2f} N | Carga en apoyos R = {reac:.2f} N")
            self.lbl_alert_desc.setStyleSheet("font-size: 10px; color: #fca5a5;")
        else:
            self.frame_alert.setStyleSheet("QFrame { background-color: #1a1e24; border: 1px solid #293845; border-radius: 4px; padding: 4px; }")
            self.lbl_alert_title.setText("✓ BALANCE DINÁMICO ESTABLE")
            self.lbl_alert_title.setStyleSheet("font-size: 10px; font-weight: bold; color: #4db6ac;")
            self.lbl_alert_desc.setText("Fu < 0.1 N | Vibración despreciable")
            self.lbl_alert_desc.setStyleSheet("font-size: 10px; color: #888892;")

        # 4. Actualización de tarjetas de telemetría
        self.card_rpm.set_value(f"{st.rpm:6.1f}")
        self.card_omega.set_value(f"{st.omega:6.2f}")
        self.card_v.set_value(f"{st.v_perif:5.2f}")
        self.card_an.set_value(f"{st.a_n:6.1f}", color="#ff5252")
        self.card_at.set_value(f"{st.a_t:5.2f}", color="#69f0ae")
        self.card_atot.set_value(f"{st.a_total:6.1f}", color="#e040fb")
        self.card_Fu.set_value(f"{st.F_desbalance:5.2f}", color="#ff1744")
        self.card_Ptot.set_value(f"{st.P_total:6.1f}")
        self.card_eff.set_value(f"{st.eficiencia_pct:5.1f}")
        self.card_rev.set_value(f"{st.rev:6.2f}")
