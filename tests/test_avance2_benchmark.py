"""
Prueba oficial de validación del Caso Base Avance 2.
Verifica que los 20 cálculos físicos del simulador reproduzcan
los valores analíticos del documento oficial avance2.tex dentro de tolerancia.
"""

import pytest
from physics.models import LatheParameters
from validation.validator import LatheValidator


def test_avance2_all_20_calculations_benchmark():
    """Valida los 20 cálculos numéricos oficiales del informe."""
    params = LatheParameters()
    results = LatheValidator.evaluate_all(params)

    assert len(results) == 20, "Deben evaluarse exactamente 20 cálculos."

    failed_calculations = []
    print("\n" + "=" * 80)
    print("REPORTE DE VALIDACIÓN CASO AVANCE 2 (20 CÁLCULOS)")
    print("=" * 80)
    for r in results:
        status_str = "APROBADO" if r.aprobado else "FALLIDO"
        print(f"[C{r.calc_num:02d}] {r.titulo:40s} | Ana: {r.valor_analitico:10.5g} | Sim: {r.valor_simulado:10.5g} {r.unidad_si:6s} | Err: {r.error_relativo_pct:6.3f}% (tol ±{r.tolerancia_pct:.2f}%) -> {status_str}")
        if not r.aprobado:
            failed_calculations.append(
                f"C{r.calc_num} ({r.titulo}): analitico={r.valor_analitico}, "
                f"simulado={r.valor_simulado}, error_rel={r.error_relativo_pct:.4f}%, "
                f"tolerancia={r.tolerancia_pct:.4f}%"
            )

    print("=" * 80)
    total_aprobados = sum(1 for r in results if r.aprobado)
    print(f"Total Aprobados: {total_aprobados}/20 ({total_aprobados/20*100:.1f}%)")
    print("=" * 80 + "\n")

    assert len(failed_calculations) == 0, f"Cálculos fuera de tolerancia: {failed_calculations}"
