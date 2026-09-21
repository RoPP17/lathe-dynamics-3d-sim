"""
Módulo de exportación de resultados y reportes de validación.
"""

import csv
import os
from typing import List
from .validator import ValidationRow


class LatheExporter:
    """Exporta resultados de validación y simulación a archivos locales."""

    @staticmethod
    def export_validation_to_csv(rows: List[ValidationRow], filepath: str) -> str:
        """Exporta la matriz de validación a formato CSV."""
        os.makedirs(os.path.dirname(os.path.abspath(filepath)), exist_ok=True)
        with open(filepath, mode="w", newline="", encoding="utf-8-sig") as f:
            writer = csv.writer(f)
            writer.writerow([
                "Cálculo N°", "Título", "Unidad Temática", "Variable",
                "Valor Analítico", "Valor Simulado", "Unidad",
                "Error Absoluto", "Error Relativo (%)", "Tolerancia (%)", "Estado"
            ])
            for r in rows:
                estado = "APROBADO" if r.aprobado else "REVISAR"
                writer.writerow([
                    r.calc_num,
                    r.titulo,
                    r.unidad_tematica,
                    r.variable_simbolo,
                    f"{r.valor_analitico:.6g}",
                    f"{r.valor_simulado:.6g}",
                    r.unidad_si,
                    f"{r.error_absoluto:.6e}",
                    f"{r.error_relativo_pct:.4f}%",
                    f"{r.tolerancia_pct:.2f}%",
                    estado
                ])
        return filepath

    @staticmethod
    def export_validation_to_markdown(rows: List[ValidationRow], filepath: str) -> str:
        """Exporta el reporte de validación en formato Markdown técnico."""
        os.makedirs(os.path.dirname(os.path.abspath(filepath)), exist_ok=True)
        total = len(rows)
        aprobados = sum(1 for r in rows if r.aprobado)

        lines = [
            "# Reporte de Validación Técnica — Simulador del Torno",
            "**Asignatura:** Dinámica — Universidad Técnica de Ambato (FICM)",
            f"**Cálculos Evaluados:** {total} | **Aprobados en Tolerancia:** {aprobados} ({aprobados/total*100:.1f}%)",
            "",
            "| N° | Cálculo | Variable | Analítico | Simulado | Error Rel. (%) | Tolerancia | Estado |",
            "|:---|:---|:---|:---|:---|:---|:---|:---|"
        ]

        for r in rows:
            badge = "✅ APROBADO" if r.aprobado else "⚠️ DIFERENCIA"
            lines.append(
                f"| **C{r.calc_num:02d}** | {r.titulo} | `{r.variable_simbolo}` | "
                f"{r.valor_analitico:.5g} {r.unidad_si} | {r.valor_simulado:.5g} {r.unidad_si} | "
                f"{r.error_relativo_pct:.3f}% | ±{r.tolerancia_pct:.2f}% | {badge} |"
            )

        with open(filepath, "w", encoding="utf-8") as f:
            f.write("\n".join(lines) + "\n")
        return filepath
