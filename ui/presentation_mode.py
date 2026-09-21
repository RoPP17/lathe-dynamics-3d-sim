"""
Modo Presentación de Alto Impacto para Defensa Académica y Grabación.
Diseñado como un HUD translúcido (Heads-Up Display) superpuesto directamente sobre el visor 3D,
optimizando el rendimiento, evitando reconstrucción de contextos OpenGL y ofreciendo tipografía
técnica visible a gran distancia.
"""

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QFrame, QComboBox
)
from PyQt6.QtCore import Qt, pyqtSignal, QObject
from visualization.gl_widget import LatheGLWidget
from simulation.engine import SimulationEngine
from physics.models import DynamicState


class PresentationHUDOverlay(QObject):
    """Controlador del HUD translúcido para presentaciones y defensa ante el docente."""

    exit_presentation = pyqtSignal()

    def __init__(self, engine: SimulationEngine, gl_widget: LatheGLWidget, parent=None):
        super().__init__(parent)
        self.engine = engine
        self.gl_widget = gl_widget
        self.is_active = False

        # ----------------------------------------------------------------------
        # 1. Barra Superior Flotante (Banner Académico UTA + Fase)
        # ----------------------------------------------------------------------
        self.top_hud = QFrame(self.gl_widget)
        self.top_hud.setStyleSheet("""
            QFrame {
                background-color: rgba(16, 20, 28, 0.88);
                border: 1px solid #0098ff;
                border-radius: 8px;
            }
        """)
        th_layout = QHBoxLayout(self.top_hud)
        th_layout.setContentsMargins(16, 6, 16, 6)

        lbl_proj = QLabel(
            "<b>SIMULADOR DINÁMICO 3D — TORNO DIDÁCTICO PARA MADERA</b><br/>"
            "<span style='color:#00e5ff; font-size:11px; font-weight:bold;'>UNIVERSIDAD TÉCNICA DE AMBATO</span> "
            "<span style='color:#a0a0b0; font-size:11px;'>| Asignatura: Dinámica | Avance 2</span>"
        )
        lbl_proj.setStyleSheet("color: #ffffff; font-size: 13px;")

        self.lbl_hud_fase = QLabel("RÉGIMEN NOMINAL")
        self.lbl_hud_fase.setStyleSheet("""
            background-color: #0078d4;
            color: #ffffff;
            font-weight: bold;
            font-size: 12px;
            padding: 5px 14px;
            border-radius: 4px;
        """)

        th_layout.addWidget(lbl_proj)
        th_layout.addStretch()
        th_layout.addWidget(self.lbl_hud_fase)

        # ----------------------------------------------------------------------
        # 2. HUD Lateral Flotante (Métricas Primarias con Consolas Grande)
        # ----------------------------------------------------------------------
        self.side_hud = QFrame(self.gl_widget)
        self.side_hud.setStyleSheet("""
            QFrame {
                background-color: rgba(16, 20, 28, 0.88);
                border: 1px solid #32323e;
                border-radius: 8px;
            }
        """)
        sh_layout = QVBoxLayout(self.side_hud)
        sh_layout.setContentsMargins(14, 12, 14, 12)
        sh_layout.setSpacing(6)

        lbl_head = QLabel("TELEMETRÍA PRIMARIA")
        lbl_head.setStyleSheet("font-size:10px; color:#888898; font-weight:bold; letter-spacing:1px;")
        sh_layout.addWidget(lbl_head)

        self.lbl_hud_t = QLabel("t :  0.000 s")
        self.lbl_hud_t.setStyleSheet("font-family:'Consolas'; font-size:17px; font-weight:bold; color:#00e5ff;")

        self.lbl_hud_rpm = QLabel("n :    0.0 rpm")
        self.lbl_hud_rpm.setStyleSheet("font-family:'Consolas'; font-size:16px; font-weight:bold; color:#ffffff;")

        self.lbl_hud_v = QLabel("v :   0.00 m/s")
        self.lbl_hud_v.setStyleSheet("font-family:'Consolas'; font-size:16px; font-weight:bold; color:#ff9100;")

        self.lbl_hud_an = QLabel("aₙ:    0.0 m/s²")
        self.lbl_hud_an.setStyleSheet("font-family:'Consolas'; font-size:15px; font-weight:bold; color:#ff5252;")

        self.lbl_hud_Fu = QLabel("Fᵤ:   0.00 N")
        self.lbl_hud_Fu.setStyleSheet("font-family:'Consolas'; font-size:15px; font-weight:bold; color:#ff1744;")

        self.lbl_hud_P = QLabel("P :    0.0 W")
        self.lbl_hud_P.setStyleSheet("font-family:'Consolas'; font-size:15px; font-weight:bold; color:#69f0ae;")

        sh_layout.addWidget(self.lbl_hud_t)
        sh_layout.addWidget(self.lbl_hud_rpm)
        sh_layout.addWidget(self.lbl_hud_v)
        sh_layout.addWidget(self.lbl_hud_an)
        sh_layout.addWidget(self.lbl_hud_Fu)
        sh_layout.addWidget(self.lbl_hud_P)

        # ----------------------------------------------------------------------
        # 3. Barra Inferior Flotante (Transporte, Escenarios y Salida)
        # ----------------------------------------------------------------------
        self.bottom_hud = QFrame(self.gl_widget)
        self.bottom_hud.setStyleSheet("""
            QFrame {
                background-color: rgba(16, 20, 28, 0.92);
                border: 1px solid #3c3c4a;
                border-radius: 8px;
            }
        """)
        bh_layout = QHBoxLayout(self.bottom_hud)
        bh_layout.setContentsMargins(14, 8, 14, 8)
        bh_layout.setSpacing(10)

        self.btn_play_pause = QPushButton("⏸ PAUSAR")
        self.btn_play_pause.setObjectName("btnPrimary")
        self.btn_play_pause.clicked.connect(self._on_play_pause)

        self.btn_restart = QPushButton("↺ REINICIAR")
        self.btn_restart.clicked.connect(self._on_restart)

        self.combo_escenarios = QComboBox()
        self.combo_escenarios.addItems([
            "CICLO_COMPLETO (Arranque→Régimen→Corte→Desbalance→Parada)",
            "ARRANQUE (0 a 2 s)",
            "REGIMEN (Nominal 1700 rpm)",
            "TORNEADO (Desbaste Fc=20N)",
            "DESBALANCE (Excentricidad Fu)",
            "PARADA (Run-down libre)"
        ])
        self.combo_escenarios.currentIndexChanged.connect(self._on_scenario_changed)

        self.combo_speed = QComboBox()
        self.combo_speed.addItems(["0.25x (Cámara lenta)", "0.50x", "1.00x (Tiempo Real)", "2.00x (Rápido)"])
        self.combo_speed.setCurrentIndex(2)
        self.combo_speed.currentIndexChanged.connect(self._on_speed_changed)

        self.btn_exit = QPushButton("✕ Salir de Presentación (Esc)")
        self.btn_exit.setStyleSheet("background-color: #d32f2f; color: white; font-weight: bold;")
        self.btn_exit.clicked.connect(self.exit_presentation.emit)

        bh_layout.addWidget(self.btn_play_pause)
        bh_layout.addWidget(self.btn_restart)
        bh_layout.addWidget(self.combo_escenarios)
        bh_layout.addWidget(self.combo_speed)
        bh_layout.addStretch()
        bh_layout.addWidget(self.btn_exit)

        self.gl_widget.resized_event.connect(self.reposition)

        # Ocultar por defecto en modo normal
        self.hide_overlay()

    def show_overlay(self):
        """Muestra los elementos del HUD flotante."""
        self.is_active = True
        self.top_hud.show()
        self.side_hud.show()
        self.bottom_hud.show()
        self.reposition(self.gl_widget.width(), self.gl_widget.height())

    def hide_overlay(self):
        """Oculta los elementos del HUD flotante."""
        self.is_active = False
        self.top_hud.hide()
        self.side_hud.hide()
        self.bottom_hud.hide()

    def reposition(self, w: int, h: int):
        """Ajusta las posiciones y tamaños del HUD cuando el visor 3D cambia de tamaño."""
        if not self.is_active:
            return
        top_w = min(780, w - 40)
        self.top_hud.setGeometry(20, 16, top_w, 54)
        self.side_hud.setGeometry(20, 80, 230, 235)

        hud_w = min(880, w - 40)
        self.bottom_hud.setGeometry((w - hud_w) // 2, max(100, h - 68), hud_w, 52)

    def update_presentation_state(self, st: DynamicState):
        """Actualiza el HUD en tiempo real con el estado dinámico."""
        if not self.is_active:
            return

        self.lbl_hud_t.setText(f"t :  {st.t:6.3f} s")
        self.lbl_hud_rpm.setText(f"n : {st.rpm:6.1f} rpm")
        self.lbl_hud_v.setText(f"v :  {st.v_perif:5.2f} m/s")
        self.lbl_hud_an.setText(f"aₙ: {st.a_n:6.1f} m/s²")
        self.lbl_hud_Fu.setText(f"Fᵤ:  {st.F_desbalance:5.2f} N")
        self.lbl_hud_P.setText(f"P :  {st.P_total:5.1f} W")

        phase_labels = {
            "ARRANQUE": ("#0078d4", "1. ARRANQUE EXPONENCIAL"),
            "REGIMEN": ("#00796b", "2. RÉGIMEN NOMINAL"),
            "TORNEADO": ("#e65100", "3. TORNEADO / CORTE"),
            "DESBALANCE": ("#c62828", "4. DESBALANCE DINÁMICO"),
            "PARADA": ("#4527a0", "5. PARADA LIBRE (RUN-DOWN)")
        }
        col, txt = phase_labels.get(st.fase, ("#333333", st.fase))
        self.lbl_hud_fase.setText(txt)
        self.lbl_hud_fase.setStyleSheet(f"""
            background-color: {col};
            color: #ffffff;
            font-weight: bold;
            font-size: 12px;
            padding: 5px 14px;
            border-radius: 4px;
        """)

        if self.engine.is_running and not self.engine.is_paused:
            self.btn_play_pause.setText("⏸ PAUSAR")
        else:
            self.btn_play_pause.setText("▶ REANUDAR")

    def _on_play_pause(self):
        self.engine.toggle_play_pause()
        if self.engine.is_running and not self.engine.is_paused:
            self.btn_play_pause.setText("⏸ PAUSAR")
        else:
            self.btn_play_pause.setText("▶ REANUDAR")

    def _on_restart(self):
        self.engine.stop()
        self.engine.play()

    def _on_scenario_changed(self, idx: int):
        esc_map = {
            0: "CICLO_COMPLETO",
            1: "ARRANQUE",
            2: "REGIMEN",
            3: "TORNEADO",
            4: "DESBALANCE",
            5: "PARADA"
        }
        self.engine.reset(esc_map.get(idx, "CICLO_COMPLETO"))
        self.engine.play()

    def _on_speed_changed(self, idx: int):
        speed_map = {0: 0.25, 1: 0.50, 2: 1.00, 3: 2.00}
        self.engine.set_playback_speed(speed_map.get(idx, 1.0))


# Alias de compatibilidad
PresentationModeWidget = PresentationHUDOverlay
