"""
Diagramas Técnicos de Ingeniería Mecánica en 2D (QPainter).
Incluye:
1. Diagrama de Esfuerzos en Eje y Chaveta (Cálculo 19): Sección transversal con chavetero,
   distribución de cortante, fuerza tangencial F(chaveta) y áreas resistentes.
2. Diagrama Cinemático del Mecanismo del Contrapunto (Cálculo 20): Volante manual,
   husillo roscado de avance axial, cono morse y fuerza elástica.
3. Diagrama de Cuerpo Libre (DCL) del Conjunto Husillo-Pieza: Equilibrio dinámico,
   par motor, par resistente de corte, desbalance rotatorio y reacciones en apoyos A y B.
4. DiagramZoomDialog: Ventana modal de inspección en alta resolución (HD) con click directo.
"""

import math
from PyQt6.QtWidgets import (
    QWidget, QDialog, QVBoxLayout, QHBoxLayout, QLabel,
    QPushButton, QTextBrowser
)
from PyQt6.QtCore import Qt, QPointF, QRectF
from PyQt6.QtGui import (
    QPainter, QColor, QPen, QBrush, QFont, QPolygonF
)


class ShaftKeywayDiagramWidget(QWidget):
    """Diagrama técnico de la sección transversal del eje con chaveta según norma DIN 6885."""

    def __init__(self, is_zoom: bool = False, parent=None):
        super().__init__(parent)
        self.is_zoom = is_zoom
        self.setMinimumSize(360, 260)
        if not self.is_zoom:
            self.setCursor(Qt.CursorShape.PointingHandCursor)
            self.setToolTip("🔍 Haz clic para ampliar este diagrama en Alta Definición (HD)")

    def mousePressEvent(self, event):
        if not self.is_zoom and event.button() == Qt.MouseButton.LeftButton:
            self.open_zoom_dialog()
        else:
            super().mousePressEvent(event)

    def open_zoom_dialog(self):
        dlg = DiagramZoomDialog("C19", self.window())
        dlg.exec()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        # Fondo técnico oscuro
        painter.fillRect(self.rect(), QColor("#1c1c22"))

        w = self.width()
        h = self.height()
        cx = w / 2.0
        cy = h / 2.0 + 6.0

        scale = min(w / 75.0, h / 65.0)  # escala visual en px por mm
        r_shaft = 9.5 * scale           # d = 19 mm -> r = 9.5 mm
        b_key = 6.0 * scale             # ancho chaveta = 6 mm
        h_key = 6.0 * scale             # alto chaveta = 6 mm
        t_slot = 3.5 * scale            # profundidad chavetero = 3.5 mm

        # 1. Ejes de simetría (línea punteada)
        pen_axis = QPen(QColor("#4e5264"), 1.0, Qt.PenStyle.DashDotLine)
        painter.setPen(pen_axis)
        painter.drawLine(int(cx - r_shaft - 25), int(cy), int(cx + r_shaft + 25), int(cy))
        painter.drawLine(int(cx), int(cy - r_shaft - 35), int(cx), int(cy + r_shaft + 25))

        # 2. Sección circular del eje (Acero AISI 1018)
        pen_shaft = QPen(QColor("#00e5ff"), 2.2)
        brush_shaft = QBrush(QColor("#222c38"))
        painter.setPen(pen_shaft)
        painter.setBrush(brush_shaft)
        painter.drawEllipse(QPointF(cx, cy), r_shaft, r_shaft)

        # 3. Alojamiento del chavetero fresado en el eje
        pen_slot = QPen(QColor("#ff9100"), 1.8)
        brush_slot = QBrush(QColor("#18181e"))
        painter.setPen(pen_slot)
        painter.setBrush(brush_slot)
        rect_slot = QRectF(cx - b_key / 2.0, cy - r_shaft, b_key, t_slot)
        painter.drawRect(rect_slot)

        # 4. Chaveta prismática (DIN 6885 Forma A, 6x6 mm)
        pen_key = QPen(QColor("#69f0ae"), 2.0)
        brush_key = QBrush(QColor("#184435"))
        painter.setPen(pen_key)
        painter.setBrush(brush_key)
        rect_key = QRectF(cx - b_key / 2.0, cy - r_shaft - (h_key - t_slot), b_key, h_key)
        painter.drawRect(rect_key)

        # 5. Plano de esfuerzo cortante en la chaveta (Línea discontinua amarilla sobre plano de cizalladura)
        pen_shear = QPen(QColor("#ffd54f"), 2.2, Qt.PenStyle.DashLine)
        painter.setPen(pen_shear)
        painter.drawLine(int(cx - b_key / 2.0), int(cy - r_shaft), int(cx + b_key / 2.0), int(cy - r_shaft))

        # 6. Flecha de Momento Torsor Mt = 0.800 N·m (Ubicada con holgura en el cuadrante inferior derecho)
        pen_torque = QPen(QColor("#00b0ff"), 2.2)
        painter.setPen(pen_torque)
        painter.setBrush(Qt.BrushStyle.NoBrush)
        arc_r = r_shaft + 22
        painter.drawArc(int(cx - arc_r), int(cy - arc_r), int(arc_r * 2), int(arc_r * 2), -40 * 16, 75 * 16)

        # Cabeza de flecha del momento torsor
        ang_rad = math.radians(35)
        ax = cx + arc_r * math.cos(ang_rad)
        ay = cy - arc_r * math.sin(ang_rad)
        arrow = QPolygonF([QPointF(ax, ay), QPointF(ax + 9, ay - 2), QPointF(ax + 4, ay + 7)])
        painter.setBrush(QColor("#00b0ff"))
        painter.drawPolygon(arrow)

        # 7. Flecha de Fuerza Tangencial sobre la chaveta F(chaveta) = 84.2 N
        pen_f = QPen(QColor("#ff3d00"), 2.5)
        painter.setPen(pen_f)
        fx_start = cx - b_key / 2.0 - 32
        fy_mid = cy - r_shaft + t_slot / 2.0
        painter.drawLine(int(fx_start), int(fy_mid), int(cx - b_key / 2.0), int(fy_mid))
        f_head = QPolygonF([
            QPointF(cx - b_key / 2.0, fy_mid),
            QPointF(cx - b_key / 2.0 - 7, fy_mid - 4),
            QPointF(cx - b_key / 2.0 - 7, fy_mid + 4)
        ])
        painter.setBrush(QColor("#ff3d00"))
        painter.drawPolygon(f_head)

        # 8. Rótulos y cotas técnicas sin colisiones
        painter.setFont(QFont("Segoe UI", 9, QFont.Weight.Bold))
        painter.setPen(QColor("#ffffff"))
        painter.drawText(QRectF(0, 6, w, 20), Qt.AlignmentFlag.AlignCenter, "SECCIÓN TRANSVERSAL DEL HUSILLO (d = 19 mm)")

        # Momento torsor
        painter.setFont(QFont("Segoe UI", 8, QFont.Weight.Bold))
        painter.setPen(QColor("#00b0ff"))
        painter.drawText(int(cx + arc_r + 6), int(cy + 6), "Par Torsor Mₜ = 0.800 N·m")

        # Fuerza en chaveta (desplazada ampliamente hacia la izquierda para evitar solapamiento con la chaveta)
        painter.setPen(QColor("#ff5252"))
        f_text = "F(chaveta) = 84.2 N"
        fm = painter.fontMetrics()
        tw = fm.horizontalAdvance(f_text)
        tx = int(max(10, cx - b_key / 2.0 - 45 - tw))
        painter.drawText(tx, int(fy_mid - 8), f_text)

        # Chaveta
        painter.setPen(QColor("#69f0ae"))
        painter.drawText(int(cx + b_key / 2.0 + 8), int(cy - r_shaft - 4), "Chaveta DIN 6885 (6×6 mm)")

        # Pie con resultados de esfuerzo
        painter.setFont(QFont("Segoe UI", 8))
        painter.setPen(QColor("#ffd54f"))
        painter.drawText(
            QRectF(10, h - 26, w - 20, 20),
            Qt.AlignmentFlag.AlignCenter,
            "τ(nom) = 0.594 MPa   |   τ(máx) = 0.950 MPa (Kt = 1.6)   |   FS > 220"
        )


class TailstockMechanismDiagramWidget(QWidget):
    """Diagrama técnico cinemático del mecanismo helicoidal del contrapunto (Cálculo 20)."""

    def __init__(self, is_zoom: bool = False, parent=None):
        super().__init__(parent)
        self.is_zoom = is_zoom
        self.setMinimumSize(360, 260)
        if not self.is_zoom:
            self.setCursor(Qt.CursorShape.PointingHandCursor)
            self.setToolTip("🔍 Haz clic para ampliar este diagrama en Alta Definición (HD)")

    def mousePressEvent(self, event):
        if not self.is_zoom and event.button() == Qt.MouseButton.LeftButton:
            self.open_zoom_dialog()
        else:
            super().mousePressEvent(event)

    def open_zoom_dialog(self):
        dlg = DiagramZoomDialog("C20", self.window())
        dlg.exec()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        painter.fillRect(self.rect(), QColor("#1c1c22"))

        w = self.width()
        h = self.height()
        cy = h / 2.0 + 4.0

        # Posiciones horizontales adaptativas
        margin = 35.0
        span = w - 70.0
        x_handwheel = margin + span * 0.12
        x_screw_start = margin + span * 0.22
        x_screw_end = margin + span * 0.46
        x_quill_start = x_screw_end
        x_quill_end = margin + span * 0.74
        x_center_tip = margin + span * 0.85

        # Eje de simetría horizontal
        painter.setPen(QPen(QColor("#4e5264"), 1.0, Qt.PenStyle.DashDotLine))
        painter.drawLine(15, int(cy), int(w - 15), int(cy))

        # 1. Volante Manual (Radio rv = 60 mm)
        painter.setPen(QPen(QColor("#00e5ff"), 2.0))
        painter.setBrush(QBrush(QColor("#222834")))
        painter.drawRect(QRectF(x_handwheel - 10, cy - 48, 14, 96))
        # Centro del volante
        painter.setBrush(QBrush(QColor("#455a64")))
        painter.drawRect(QRectF(x_handwheel + 4, cy - 16, 12, 32))

        # Manija del volante
        painter.setBrush(QBrush(QColor("#d32f2f")))
        painter.drawRect(QRectF(x_handwheel - 22, cy - 46, 12, 8))

        # Flecha de fuerza manual F(mano) = 2.85 N
        painter.setPen(QPen(QColor("#ff5252"), 2.2))
        painter.drawLine(int(x_handwheel - 16), int(cy - 68), int(x_handwheel - 16), int(cy - 48))
        f_arr = QPolygonF([
            QPointF(x_handwheel - 16, cy - 48),
            QPointF(x_handwheel - 20, cy - 56),
            QPointF(x_handwheel - 12, cy - 56)
        ])
        painter.setBrush(QColor("#ff5252"))
        painter.drawPolygon(f_arr)

        # 2. Husillo Roscado (Paso p = 2 mm/rev, Rosca métrica M14)
        painter.setPen(QPen(QColor("#ffd54f"), 1.5))
        painter.setBrush(QBrush(QColor("#332a15")))
        painter.drawRect(QRectF(x_screw_start, cy - 9, x_screw_end - x_screw_start, 18))
        # Filetes de rosca helicoidal
        painter.setPen(QPen(QColor("#ffe082"), 1.2))
        for rx in range(int(x_screw_start) + 6, int(x_screw_end) - 6, 8):
            painter.drawLine(rx, int(cy - 9), rx + 4, int(cy + 9))

        # 3. Caña telescópica (Quill d = 32 mm)
        painter.setPen(QPen(QColor("#90caf9"), 2.0))
        painter.setBrush(QBrush(QColor("#1e2a38")))
        painter.drawRect(QRectF(x_quill_start, cy - 18, x_quill_end - x_quill_start, 36))

        # Graduaciones milimétricas de la caña
        painter.setPen(QPen(QColor("#ffffff"), 1.0))
        for mx in range(int(x_quill_start) + 6, int(x_quill_end) - 6, 6):
            painter.drawLine(mx, int(cy - 18), mx, int(cy - 12))

        # 4. Punto giratorio cónico a 60° (Live Center)
        cone = QPolygonF([
            QPointF(x_quill_end, cy - 16),
            QPointF(x_center_tip, cy),
            QPointF(x_quill_end, cy + 16)
        ])
        painter.setPen(QPen(QColor("#e0e0e0"), 2.0))
        painter.setBrush(QBrush(QColor("#546e7a")))
        painter.drawPolygon(cone)

        # 5. Madera de sujeción (Extremo derecho)
        painter.setPen(QPen(QColor("#8d6e63"), 1.8))
        painter.setBrush(QBrush(QColor("#4e342e")))
        painter.drawRect(QRectF(x_center_tip + 3, cy - 35, 26, 70))

        # 6. Flecha de Fuerza Axial de Apriete F(axial) = 575 N
        painter.setPen(QPen(QColor("#00e676"), 2.5))
        painter.drawLine(int(x_center_tip + 2), int(cy), int(x_center_tip + 32), int(cy))
        fa_arr = QPolygonF([
            QPointF(x_center_tip + 32, cy),
            QPointF(x_center_tip + 24, cy - 4),
            QPointF(x_center_tip + 24, cy + 4)
        ])
        painter.setBrush(QColor("#00e676"))
        painter.drawPolygon(fa_arr)

        # 7. Textos y especificaciones sin colisiones
        painter.setFont(QFont("Segoe UI", 9, QFont.Weight.Bold))
        painter.setPen(QColor("#ffffff"))
        painter.drawText(QRectF(0, 6, w, 20), Qt.AlignmentFlag.AlignCenter, "MECANISMO HELICOIDAL DEL CONTRAPUNTO (C20)")

        painter.setFont(QFont("Segoe UI", 8, QFont.Weight.Bold))
        painter.setPen(QColor("#ff5252"))
        painter.drawText(int(max(10, x_handwheel - 45)), int(cy - 72), "F(mano) = 2.85 N")

        painter.setPen(QColor("#ffd54f"))
        painter.drawText(int(x_screw_start + 4), int(cy + 34), "Rosca M14x2 (p = 2 mm)")
        painter.drawText(int(x_screw_start + 4), int(cy + 48), "Par M = 0.171 N·m")

        painter.setPen(QColor("#69f0ae"))
        painter.drawText(int(x_quill_end - 15), int(cy - 34), "F(axial) = 575.0 N")

        painter.setFont(QFont("Segoe UI", 8))
        painter.setPen(QColor("#90caf9"))
        painter.drawText(
            QRectF(10, h - 26, w - 20, 20),
            Qt.AlignmentFlag.AlignCenter,
            "Avance x = 1.5 mm   |   Giro N = 0.75 rev (270°)   |   Trabajo U = 0.806 J"
        )


class LatheFBDDiagramWidget(QWidget):
    """Diagrama de Cuerpo Libre (DCL) completo del conjunto husillo, plato y pieza de madera."""

    def __init__(self, is_zoom: bool = False, parent=None):
        super().__init__(parent)
        self.is_zoom = is_zoom
        self.setMinimumSize(520, 280)
        if not self.is_zoom:
            self.setCursor(Qt.CursorShape.PointingHandCursor)
            self.setToolTip("🔍 Haz clic para ampliar este diagrama en Alta Definición (HD)")

    def mousePressEvent(self, event):
        if not self.is_zoom and event.button() == Qt.MouseButton.LeftButton:
            self.open_zoom_dialog()
        else:
            super().mousePressEvent(event)

    def open_zoom_dialog(self):
        dlg = DiagramZoomDialog("DCL", self.window())
        dlg.exec()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        painter.fillRect(self.rect(), QColor("#1c1c22"))

        w = self.width()
        h = self.height()
        cy = h / 2.0 + 8.0

        # Eje de rotación (longitudinal X)
        painter.setPen(QPen(QColor("#4e5264"), 1.2, Qt.PenStyle.DashDotLine))
        painter.drawLine(20, int(cy), int(w - 20), int(cy))

        # Geometría esquemática adaptativa
        margin = 35.0
        span = w - 70.0
        x_m = margin + span * 0.05
        x_brg_a = margin + span * 0.18
        x_brg_b = margin + span * 0.33
        x_plato = margin + span * 0.44
        x_wood_start = margin + span * 0.48
        x_cut = margin + span * 0.65
        x_unb = margin + span * 0.77
        x_wood_end = margin + span * 0.89
        x_tail = margin + span * 0.94

        # Eje del husillo de acero
        painter.setPen(QPen(QColor("#90a4ae"), 2.0))
        painter.setBrush(QBrush(QColor("#263238")))
        painter.drawRect(QRectF(x_m, cy - 8, x_plato - x_m, 16))

        # Plato de arrastre
        painter.setPen(QPen(QColor("#00e5ff"), 2.0))
        painter.setBrush(QBrush(QColor("#1e3a4b")))
        painter.drawRect(QRectF(x_plato, cy - 26, 16, 52))

        # Pieza de madera cilíndrica (R = 40 mm)
        painter.setPen(QPen(QColor("#d7ccc8"), 1.8))
        painter.setBrush(QBrush(QColor("#4e342e")))
        painter.drawRect(QRectF(x_wood_start, cy - 22, x_wood_end - x_wood_start, 44))

        # Apoyos A y B (Rodamientos de soporte)
        for bx, name in [(x_brg_a, "A"), (x_brg_b, "B")]:
            painter.setPen(QPen(QColor("#ffb74d"), 1.5))
            painter.setBrush(QBrush(QColor("#3e2723")))
            painter.drawRect(QRectF(bx - 7, cy - 14, 14, 28))
            # Flecha de reacción en apoyo
            painter.setPen(QPen(QColor("#ff9800"), 2.0))
            painter.drawLine(int(bx), int(cy + 36), int(bx), int(cy + 14))
            arr = QPolygonF([QPointF(bx, cy + 14), QPointF(bx - 4, cy + 20), QPointF(bx + 4, cy + 20)])
            painter.setBrush(QColor("#ff9800"))
            painter.drawPolygon(arr)
            painter.setFont(QFont("Consolas", 9, QFont.Weight.Bold))
            painter.drawText(int(bx - 10), int(cy + 49), f"R({name})")

        # Vector Par Motor en extremo izquierdo
        painter.setPen(QPen(QColor("#00e676"), 2.2))
        painter.setBrush(Qt.BrushStyle.NoBrush)
        painter.drawArc(int(x_m - 16), int(cy - 20), 38, 38, 40 * 16, 120 * 16)
        painter.setBrush(QColor("#00e676"))
        arr_m = QPolygonF([QPointF(x_m + 3, cy - 20), QPointF(x_m + 10, cy - 25), QPointF(x_m + 10, cy - 15)])
        painter.drawPolygon(arr_m)
        painter.setFont(QFont("Segoe UI", 8, QFont.Weight.Bold))
        painter.drawText(int(x_m - 24), int(cy - 36), "M(motor)")

        # Vector Fuerza de Corte (Tangencial)
        painter.setPen(QPen(QColor("#2979ff"), 2.5))
        painter.drawLine(int(x_cut), int(cy - 44), int(x_cut), int(cy - 22))
        fc_arr = QPolygonF([QPointF(x_cut, cy - 22), QPointF(x_cut - 4, cy - 30), QPointF(x_cut + 4, cy - 30)])
        painter.setBrush(QColor("#2979ff"))
        painter.drawPolygon(fc_arr)
        painter.drawText(int(x_cut - 16), int(cy - 48), "F(corte) = 20 N")

        # Vector Fuerza de Desbalance Excéntrico
        painter.setPen(QPen(QColor("#ff1744"), 2.5))
        painter.drawLine(int(x_unb), int(cy), int(x_unb), int(cy - 40))
        fu_arr = QPolygonF([QPointF(x_unb, cy - 40), QPointF(x_unb - 4, cy - 32), QPointF(x_unb + 4, cy - 32)])
        painter.setBrush(QColor("#ff1744"))
        painter.drawPolygon(fu_arr)
        painter.drawText(int(x_unb - 18), int(cy - 44), "F(desb) = 1.27 N")

        # Vector de empuje axial del contrapunto
        painter.setPen(QPen(QColor("#ffd54f"), 2.5))
        painter.drawLine(int(x_tail + 30), int(cy), int(x_wood_end), int(cy))
        ft_arr = QPolygonF([QPointF(x_wood_end, cy), QPointF(x_wood_end + 7, cy - 4), QPointF(x_wood_end + 7, cy + 4)])
        painter.setBrush(QColor("#ffd54f"))
        painter.drawPolygon(ft_arr)
        painter.drawText(int(x_wood_end + 6), int(cy - 8), "F(axial) = 575 N")

        # Rótulo de título del DCL
        painter.setFont(QFont("Segoe UI", 10, QFont.Weight.Bold))
        painter.setPen(QColor("#ffffff"))
        painter.drawText(QRectF(0, 6, w, 22), Qt.AlignmentFlag.AlignCenter, "DIAGRAMA DE CUERPO LIBRE INTEGRAL DEL HUSILLO Y ROTOR (DCL)")

        # Ecuaciones dinámicas de gobierno compiladas
        painter.setFont(QFont("Consolas", 8, QFont.Weight.Bold))
        painter.setPen(QColor("#80deea"))
        painter.drawText(
            QRectF(10, h - 26, w - 20, 20),
            Qt.AlignmentFlag.AlignCenter,
            "Σ M = I · α = M(mot) − F(c)·R − b·ω   |   Σ F = R(A) + R(B) − F(c) − F(u) = 0"
        )


class DiagramZoomDialog(QDialog):
    """Ventana modal de inspección en Alta Resolución (HD) de diagramas técnicos."""

    def __init__(self, diagram_key: str, parent=None):
        super().__init__(parent)
        self.diagram_key = diagram_key
        titles = {
            "C19": "Cálculo 19 — Sección Transversal del Husillo y Chavetero DIN 6885",
            "C20": "Cálculo 20 — Cinemática y Mecánica Helicoidal del Contrapunto",
            "DCL": "Diagrama de Cuerpo Libre (DCL) — Equilibrio Dinámico del Torno"
        }
        self.setWindowTitle(f"Inspección Técnica en Alta Definición (HD) — {titles.get(diagram_key, 'Diagrama')}")
        self.resize(1000, 640)
        self.setStyleSheet("""
            QDialog {
                background-color: #14151b;
                color: #ffffff;
            }
        """)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(16, 14, 16, 14)
        layout.setSpacing(12)

        # Encabezado
        header_layout = QHBoxLayout()
        lbl_title = QLabel(f"<b>{titles.get(diagram_key, 'Diagrama Técnico')}</b>")
        lbl_title.setStyleSheet("font-size: 15px; color: #00e5ff;")

        btn_close = QPushButton("✖ Cerrar [ESC]")
        btn_close.setStyleSheet("""
            QPushButton {
                background-color: #2c2d38;
                color: #ffffff;
                font-weight: bold;
                padding: 5px 14px;
                border-radius: 4px;
                border: 1px solid #444455;
            }
            QPushButton:hover {
                background-color: #d32f2f;
                border-color: #ff5252;
            }
        """)
        btn_close.clicked.connect(self.accept)

        header_layout.addWidget(lbl_title)
        header_layout.addStretch()
        header_layout.addWidget(btn_close)
        layout.addLayout(header_layout)

        # Diagrama a gran escala
        if diagram_key == "C19":
            diagram_widget = ShaftKeywayDiagramWidget(is_zoom=True)
        elif diagram_key == "C20":
            diagram_widget = TailstockMechanismDiagramWidget(is_zoom=True)
        else:
            diagram_widget = LatheFBDDiagramWidget(is_zoom=True)

        diagram_widget.setMinimumHeight(380)
        layout.addWidget(diagram_widget, stretch=5)

        # Ficha técnica detallada explicativa
        browser = QTextBrowser()
        browser.setStyleSheet("""
            QTextBrowser {
                background-color: #1b1c24;
                color: #d8d8e2;
                border: 1px solid #333344;
                border-radius: 6px;
                padding: 10px;
                font-family: 'Segoe UI', sans-serif;
                font-size: 12px;
            }
        """)
        browser.setFixedHeight(140)

        if diagram_key == "C19":
            info_html = """
            <b style='color:#0098ff;'>MEMORIA TÉCNICA — CÁLCULO 19: TORSIÓN EN HUSILLO Y VERIFICACIÓN DE CHAVETA</b><br/>
            • <b>Norma de Chaveta:</b> DIN 6885 Forma A (Ancho <i>b</i> = 6 mm, Alto <i>h</i> = 6 mm, Longitud <i>L</i> = 20 mm).<br/>
            • <b>Material Husillo:</b> Acero AISI 1018 laminado en frío (<i>S</i><sub>y</sub> = 370 MPa, <i>S</i><sub>sy</sub> &asymp; 213 MPa, <i>G</i> = 79.3 GPa).<br/>
            • <b>Esfuerzo Cortante Nominal:</b> &tau;<sub>nom</sub> = 16&middot;<i>M</i><sub>t</sub> / (&pi;&middot;<i>d</i>&sup3;) = 0.594 MPa.<br/>
            • <b>Concentración de Esfuerzos:</b> <i>K</i><sub>t</sub> = 1.6 &rarr; &tau;<sub>máx</sub> = <i>K</i><sub>t</sub> &middot; &tau;<sub>nom</sub> = <b>0.950 MPa</b>.<br/>
            • <b>Factor de Seguridad a Fluencia:</b> <i>FS</i> = <i>S</i><sub>sy</sub> / &tau;<sub>máx</sub> = 213 / 0.950 = <b>224.2</b> (&gt;&gt; 2.5 requerido, condición hiper-segura).
            """
        elif diagram_key == "C20":
            info_html = """
            <b style='color:#0098ff;'>MEMORIA TÉCNICA — CÁLCULO 20: MECANISMO HELICOIDAL DEL CONTRAPUNTO</b><br/>
            • <b>Geometría Helicoidal:</b> Husillo de potencia rosca métrica ISO M14x2 (Paso <i>p</i> = 2.0 mm/rev, Radio medio <i>r</i><sub>m</sub> = 6.35 mm).<br/>
            • <b>Avance Axial de Fijación:</b> &Delta;<i>x</i> = 1.50 mm &rarr; Giro requerido del volante: <i>N</i> = &Delta;<i>x</i> / <i>p</i> = <b>0.75 vueltas (270&deg;)</b>.<br/>
            • <b>Carga Axial Inducida:</b> <i>F</i><sub>axial</sub> = <i>F</i><sub>0</sub> + <i>k</i>&middot;&Delta;<i>x</i> = 500 + (50 N/mm &middot; 1.5 mm) = <b>575.0 N</b>.<br/>
            • <b>Energía Elástica Almacenada:</b> <i>U</i><sub>axial</sub> = &frac12;&middot;(<i>F</i><sub>0</sub> + <i>F</i><sub>final</sub>)&middot;&Delta;<i>x</i> = <b>0.806 J</b>.<br/>
            • <b>Ergonomía de Operación:</b> Volante <i>r</i><sub>v</sub> = 60 mm &rarr; Fuerza muscular requerida: <i>F</i><sub>mano</sub> = <b>2.85 N (~290 gf)</b>.
            """
        else:
            info_html = """
            <b style='color:#0098ff;'>MEMORIA TÉCNICA — DIAGRAMA DE CUERPO LIBRE INTEGRAL (DCL)</b><br/>
            • <b>Equilibrio Rotacional:</b> &Sigma; <i>M</i><sub>x</sub> = <i>I</i><sub>tot</sub> &middot; &alpha; = <i>M</i><sub>motor</sub> &minus; <i>F</i><sub>corte</sub>&middot;<i>R</i> &minus; <i>b</i>&middot;&omega;.<br/>
            • <b>Fuerza de Desbalance Centrífugo:</b> <i>F</i><sub>u</sub>(<i>t</i>) = <i>m</i><sub>u</sub> &middot; <i>e</i> &middot; &omega;&sup2; = 0.020 kg &middot; 0.002 m &middot; (178.02 rad/s)&sup2; = <b>1.27 N</b>.<br/>
            • <b>Reacciones Dinámicas en Rodamientos:</b> Apoyo A (<i>x</i> = 90 mm) y Apoyo B (<i>x</i> = 150 mm) absorben las componentes de corte y desbalance.<br/>
            • <b>Retención Axial del Contrapunto:</b> <i>F</i><sub>a</sub> = 575 N aplicada en el extremo derecho garantiza que la madera no pandee ni deslice.
            """

        browser.setHtml(info_html)
        layout.addWidget(browser, stretch=2)
