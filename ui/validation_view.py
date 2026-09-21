"""
Pantalla de Validación Analítica vs Simulación y Trazabilidad Académica.
Contiene:
- Tabla interactiva de los 20 cálculos físicos con error absoluto en notación científica rigurosa (× 10⁻ⁿ).
- Variables y fórmulas completamente compiladas en Unicode y HTML enriquecido (sin código crudo de LaTeX).
- Ficha técnica de trazabilidad académica con desglose de ecuaciones y tolerancias.
- Exportación a CSV y Markdown.
"""

import math
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QTableWidget, QTableWidgetItem,
    QHeaderView, QLabel, QTextBrowser, QPushButton, QGroupBox,
    QSplitter, QFileDialog, QMessageBox, QStyledItemDelegate,
    QStyleOptionViewItem, QStyle
)
from PyQt6.QtGui import QTextDocument, QPainter
from PyQt6.QtCore import Qt, QModelIndex, QSize
from validation.validator import LatheValidator, ValidationRow
from validation.exporter import LatheExporter
from physics.models import LatheParameters


class HTMLDelegate(QStyledItemDelegate):
    """Renderiza variables con formato matemático HTML (cursivas, subíndices, letras griegas)."""

    def paint(self, painter: QPainter, option: QStyleOptionViewItem, index: QModelIndex):
        options = QStyleOptionViewItem(option)
        self.initStyleOption(options, index)
        painter.save()

        # Dibujar fondo de selección del sistema
        if options.widget:
            options.widget.style().drawPrimitive(
                QStyle.PrimitiveElement.PE_PanelItemViewItem, options, painter, options.widget
            )

        doc = QTextDocument()
        doc.setDefaultFont(options.font)
        is_selected = bool(options.state & QStyle.StateFlag.State_Selected)
        color = "#ffffff" if is_selected else "#00e5ff"

        doc.setHtml(f"<div align='center' style='color:{color}; font-size:13px; font-weight:bold;'>{options.text}</div>")

        clip = options.rect
        offset_x = max(0.0, (clip.width() - doc.idealWidth()) / 2.0)
        offset_y = max(0.0, (clip.height() - doc.size().height()) / 2.0)
        painter.translate(clip.left() + offset_x, clip.top() + offset_y)
        doc.drawContents(painter)
        painter.restore()

    def sizeHint(self, option: QStyleOptionViewItem, index: QModelIndex) -> QSize:
        options = QStyleOptionViewItem(option)
        self.initStyleOption(options, index)
        doc = QTextDocument()
        doc.setDefaultFont(options.font)
        doc.setHtml(options.text)
        return QSize(int(doc.idealWidth()) + 20, max(int(doc.size().height()) + 8, 28))


def format_scientific_unicode(val: float, precision: int = 3) -> str:
    """
    Formatea un número en notación científica con potencias de 10 en Unicode.
    Ejemplo: 1.420 × 10⁻⁶  |  0.000 × 10⁰
    """
    if abs(val) < 1e-15:
        return f"0.000 × 10⁰"
    exp = int(math.floor(math.log10(abs(val))))
    coeff = val / (10.0 ** exp)

    # Diccionario de superíndices Unicode
    super_digits = {
        '0': '⁰', '1': '¹', '2': '²', '3': '³', '4': '⁴',
        '5': '⁵', '6': '⁶', '7': '⁷', '8': '⁸', '9': '⁹',
        '-': '⁻', '+': ''
    }
    exp_str = "".join(super_digits.get(ch, ch) for ch in str(exp))
    return f"{coeff:.{precision}f} × 10{exp_str}"


def format_scientific_html(val: float, precision: int = 3) -> str:
    """Formatea en HTML estándar con <sup> para renderizado en QTextBrowser."""
    if abs(val) < 1e-15:
        return "0.000 &times; 10<sup>0</sup>"
    exp = int(math.floor(math.log10(abs(val))))
    coeff = val / (10.0 ** exp)
    return f"{coeff:.{precision}f} &times; 10<sup>{exp}</sup>"


class ValidationViewWidget(QWidget):
    """Vista de validación rigurosa de los 20 cálculos frente a Avance 2."""

    def __init__(self, params: LatheParameters, parent=None):
        super().__init__(parent)
        self.params = params.copy()
        self.validation_rows: list[ValidationRow] = []

        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(12, 12, 12, 12)
        main_layout.setSpacing(10)

        # ----------------------------------------------------------------------
        # Barra Superior con Resumen y Exportaciones
        # ----------------------------------------------------------------------
        top_bar = QHBoxLayout()
        self.lbl_summary = QLabel("Evaluando cálculos...")
        self.lbl_summary.setStyleSheet("font-size: 13px; font-weight: bold; color: #ffffff;")

        self.btn_export_csv = QPushButton("📄 Exportar CSV")
        self.btn_export_csv.clicked.connect(self.export_csv)

        self.btn_export_md = QPushButton("📝 Exportar Markdown")
        self.btn_export_md.clicked.connect(self.export_markdown)

        top_bar.addWidget(self.lbl_summary)
        top_bar.addStretch()
        top_bar.addWidget(self.btn_export_csv)
        top_bar.addWidget(self.btn_export_md)
        main_layout.addLayout(top_bar)

        # ----------------------------------------------------------------------
        # Splitter Horizontal: Tabla (izq) y Ficha de Trazabilidad (der)
        # ----------------------------------------------------------------------
        splitter = QSplitter(Qt.Orientation.Horizontal)

        # 1. Tabla de Validación
        self.table = QTableWidget()
        self.table.setColumnCount(9)
        self.table.setHorizontalHeaderLabels([
            "N°", "Cálculo / Título", "Variable", "Analítico (Avance 2)",
            "Simulación", "Unidad", "Error Absoluto (|Δ|)", "Error Rel. (%)", "Estado"
        ])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Interactive)
        self.table.horizontalHeader().setStretchLastSection(True)
        self.table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.table.setSelectionMode(QTableWidget.SelectionMode.SingleSelection)
        self.table.itemSelectionChanged.connect(self._on_row_selected)
        self.table.setItemDelegateForColumn(2, HTMLDelegate(self.table))
        splitter.addWidget(self.table)

        # 2. Panel de Trazabilidad Académica
        card_box = QGroupBox("FICHA DE TRAZABILIDAD ACADÉMICA (COMPILACIÓN FORMAL)")
        card_layout = QVBoxLayout(card_box)
        card_layout.setContentsMargins(8, 14, 8, 8)

        self.doc_browser = QTextBrowser()
        self.doc_browser.setStyleSheet("""
            QTextBrowser {
                background-color: #1a1a1e;
                color: #d4d4dc;
                border: 1px solid #33333e;
                border-radius: 6px;
                padding: 12px;
                font-family: 'Segoe UI', sans-serif;
                font-size: 13px;
                line-height: 1.5;
            }
        """)
        card_layout.addWidget(self.doc_browser)
        splitter.addWidget(card_box)

        splitter.setStretchFactor(0, 65)
        splitter.setStretchFactor(1, 35)
        main_layout.addWidget(splitter)

        # Ejecutar evaluación inicial
        self.refresh_validation(self.params)

    def refresh_validation(self, params: LatheParameters):
        """Ejecuta la evaluación de los 20 cálculos y actualiza la tabla con notación científica."""
        self.params = params.copy()
        self.validation_rows = LatheValidator.evaluate_all(self.params)

        self.table.setRowCount(len(self.validation_rows))
        total = len(self.validation_rows)
        aprobados = 0

        for row_idx, r in enumerate(self.validation_rows):
            if r.aprobado:
                aprobados += 1

            # N°
            it_num = QTableWidgetItem(f"C{r.calc_num:02d}")
            it_num.setTextAlignment(Qt.AlignmentFlag.AlignCenter)

            # Título
            it_title = QTableWidgetItem(r.titulo)

            # Variable (Símbolo matemático compilado con cursivas y subíndices HTML)
            var_content = r.variable_html if r.variable_html else r.variable_simbolo
            it_var = QTableWidgetItem(var_content)
            it_var.setTextAlignment(Qt.AlignmentFlag.AlignCenter)

            # Analítico
            it_ana = QTableWidgetItem(f"{r.valor_analitico:.5g}")
            it_ana.setTextAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)

            # Simulado
            it_sim = QTableWidgetItem(f"{r.valor_simulado:.5g}")
            it_sim.setTextAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)

            # Unidad
            it_unit = QTableWidgetItem(r.unidad_si)
            it_unit.setTextAlignment(Qt.AlignmentFlag.AlignCenter)

            # Error Absoluto en Notación Científica (× 10⁻ⁿ)
            err_abs_str = format_scientific_unicode(r.error_absoluto, precision=3)
            it_eabs = QTableWidgetItem(err_abs_str)
            it_eabs.setTextAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)

            # Error Relativo %
            it_erel = QTableWidgetItem(f"{r.error_relativo_pct:.4f}%")
            it_erel.setTextAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)

            # Estado (Badge de aprobación)
            status_txt = "✅ CONFORME" if r.aprobado else "⚠️ REVISAR"
            it_status = QTableWidgetItem(status_txt)
            it_status.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            if r.aprobado:
                it_status.setForeground(Qt.GlobalColor.green)
            else:
                it_status.setForeground(Qt.GlobalColor.yellow)

            self.table.setItem(row_idx, 0, it_num)
            self.table.setItem(row_idx, 1, it_title)
            self.table.setItem(row_idx, 2, it_var)
            self.table.setItem(row_idx, 3, it_ana)
            self.table.setItem(row_idx, 4, it_sim)
            self.table.setItem(row_idx, 5, it_unit)
            self.table.setItem(row_idx, 6, it_eabs)
            self.table.setItem(row_idx, 7, it_erel)
            self.table.setItem(row_idx, 8, it_status)

        # Ajustar anchos de columnas
        self.table.resizeColumnToContents(0)
        self.table.resizeColumnToContents(2)
        self.table.resizeColumnToContents(5)
        self.table.resizeColumnToContents(6)
        self.table.resizeColumnToContents(7)
        self.table.resizeColumnToContents(8)

        # Resumen superior
        pct_aprob = (aprobados / total) * 100.0
        self.lbl_summary.setText(
            f"✅ Cálculos Conformes: {aprobados}/{total} ({pct_aprob:.1f}%) | "
            f"Tolerancia Rigurosa Máxima: ±0.10%"
        )

        # Seleccionar primera fila por defecto
        if self.validation_rows:
            self.table.selectRow(0)

    def _on_row_selected(self):
        """Muestra la ficha técnica detallada del cálculo seleccionado con fórmulas compiladas."""
        selected = self.table.selectedIndexes()
        if not selected:
            return
        row = selected[0].row()
        if row < 0 or row >= len(self.validation_rows):
            return

        r = self.validation_rows[row]

        # Formato científico HTML del error absoluto
        err_abs_html = format_scientific_html(r.error_absoluto, precision=4)

        # Ecuación compilada en HTML limpio
        eq_display = r.ecuacion_compilada if r.ecuacion_compilada else r.ecuacion_latex

        var_tech_badge = r.variable_html if r.variable_html else r.variable_simbolo

        html = f"""
        <div style='border-bottom: 2px solid #0098ff; padding-bottom: 6px; margin-bottom: 10px;'>
            <h3 style='color:#0098ff; margin:0px; font-size:16px;'>Cálculo {r.calc_num:02d}: {r.titulo}</h3>
            <span style='color:#00e5ff; font-size:11px; font-weight:bold;'>{r.unidad_tematica.upper()}</span>
        </div>

        <p style='margin: 4px 0px;'><b>Magnitud Física:</b> <span style='color:#ffffff;'>{r.variable_nombre}</span></p>
        <p style='margin: 4px 0px;'><b>Símbolo Técnico:</b> <span style='background-color:#262832; color:#00e5ff; font-size:16px; font-weight:bold; padding:3px 12px; border-radius:4px; border:1px solid #334455;'>{var_tech_badge}</span></p>

        <p style='margin: 8px 0px 4px 0px;'><b>Ecuación Matemática Compilada:</b></p>
        <div style='background-color:#222530; border-left: 4px solid #ffd54f; padding: 10px 14px; border-radius: 4px; font-size:15px; font-weight:bold; color:#ffd54f; margin-bottom: 12px; font-family:"Segoe UI", sans-serif;'>
            {eq_display}
        </div>

        <table style='width:100%; border-collapse:collapse; margin-top:6px; font-size:12px;'>
            <tr style='background-color:#222228;'>
                <td style='padding:6px; border:1px solid #33333c;'><b>Valor Teórico Analítico (Avance 2):</b></td>
                <td style='padding:6px; border:1px solid #33333c; text-align:right; color:#00e5ff; font-weight:bold; font-size:13px;'>{r.valor_analitico:.6g} {r.unidad_si}</td>
            </tr>
            <tr>
                <td style='padding:6px; border:1px solid #33333c;'><b>Valor Calculado Simulación 3D:</b></td>
                <td style='padding:6px; border:1px solid #33333c; text-align:right; color:#69f0ae; font-weight:bold; font-size:13px;'>{r.valor_simulado:.6g} {r.unidad_si}</td>
            </tr>
            <tr style='background-color:#222228;'>
                <td style='padding:6px; border:1px solid #33333c;'><b>Error Absoluto (|Δ|):</b></td>
                <td style='padding:6px; border:1px solid #33333c; text-align:right; color:#ffd54f; font-family:"Consolas"; font-weight:bold;'>{err_abs_html} {r.unidad_si}</td>
            </tr>
            <tr>
                <td style='padding:6px; border:1px solid #33333c;'><b>Error Relativo Porcentual:</b></td>
                <td style='padding:6px; border:1px solid #33333c; text-align:right; font-weight:bold; color:#a5d6a7;'>{r.error_relativo_pct:.4f}%</td>
            </tr>
            <tr style='background-color:#222228;'>
                <td style='padding:6px; border:1px solid #33333c;'><b>Tolerancia Normativa UTA:</b></td>
                <td style='padding:6px; border:1px solid #33333c; text-align:right; color:#888894;'>&plusmn;{r.tolerancia_pct:.2f}%</td>
            </tr>
            <tr>
                <td style='padding:6px; border:1px solid #33333c;'><b>Dictamen de Validación:</b></td>
                <td style='padding:6px; border:1px solid #33333c; text-align:right; font-weight:bold; color:{"#00e676" if r.aprobado else "#ffab00"};'>
                    {"✅ CONFORME Y VALIDADO" if r.aprobado else "⚠️ REVISIÓN REQUERIDA"}
                </td>
            </tr>
        </table>

        <div style='margin-top:12px; padding:8px 10px; background-color:#1e2028; border-radius:4px;'>
            <b style='color:#0098ff;'>Fundamento Físico y Trazabilidad:</b><br/>
            <span style='color:#c0c0c8; font-size:12px;'>{r.descripcion}</span>
        </div>

        <div style='margin-top:8px; padding:6px 10px; background-color:#161820; border-radius:4px; font-size:11px; color:#9fa8da;'>
            <b>Trazabilidad Académica:</b> Formulación analítica de la Cátedra de Dinámica (UTA) &bull; Tolerancia estricta &plusmn;{r.tolerancia_pct:.2f}%
        </div>
        """
        self.doc_browser.setHtml(html)

    def export_csv(self):
        """Exporta la tabla completa de validación a archivo CSV."""
        filepath, _ = QFileDialog.getSaveFileName(
            self, "Exportar Validación a CSV", "validacion_torno_avance2.csv", "Archivos CSV (*.csv)"
        )
        if filepath:
            try:
                LatheExporter.export_validation_to_csv(self.validation_rows, filepath)
                QMessageBox.information(self, "Exportación Completada", f"Archivo CSV generado en:\n{filepath}")
            except Exception as e:
                QMessageBox.warning(self, "Error al Exportar", f"Error: {e}")

    def export_markdown(self):
        """Exporta el reporte de validación en Markdown."""
        filepath, _ = QFileDialog.getSaveFileName(
            self, "Exportar Validación a Markdown", "reporte_validacion_torno.md", "Archivos Markdown (*.md)"
        )
        if filepath:
            try:
                LatheExporter.export_validation_to_markdown(self.validation_rows, filepath)
                QMessageBox.information(self, "Exportación Completada", f"Reporte Markdown generado en:\n{filepath}")
            except Exception as e:
                QMessageBox.warning(self, "Error al Exportar", f"Error: {e}")
