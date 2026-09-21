"""Pruebas unitarias de mecánica, torsión y contrapunto (Cálculos 19, 20)."""
import math
import pytest
from physics.models import LatheParameters
from physics.mechanics import LatheMechanics


def test_calc_19_torsion_eje_chaveta():
    p = LatheParameters()
    res = LatheMechanics.calc_19_torsion_eje_chaveta(
        p.M_torsion_diseno, p.d_eje, p.L_eje,
        p.b_chaveta, p.h_chaveta, p.l_chaveta,
        p.Kt_chaveta, p.G_acero
    )
    assert math.isclose(res["J_m4"], 1.2794e-8, rel_tol=1e-3)
    assert math.isclose(res["tau_nom_MPa"], 0.5940, rel_tol=1e-3)
    assert math.isclose(res["tau_max_MPa"], 0.9504, rel_tol=1e-3)
    assert math.isclose(res["tau_key_MPa"], 0.5614, rel_tol=1e-3)
    assert math.isclose(res["sigma_aplast_MPa"], 1.1228, rel_tol=1e-3)
    assert math.isclose(res["phi_rad"], 3.17e-5, rel_tol=1e-2)


def test_calc_20_contrapunto():
    p = LatheParameters()
    res = LatheMechanics.calc_20_mecanica_contrapunto(
        p.F0_cp, p.k_cp, p.x_cp, p.p_cp, p.r_volante
    )
    assert math.isclose(res["F_final_N"], 575.0, rel_tol=1e-4)
    assert math.isclose(res["U_axial_J"], 0.8063, rel_tol=1e-3)
    assert math.isclose(res["N_vueltas_rev"], 0.75, rel_tol=1e-4)
    assert math.isclose(res["M_torsor_Nm"], 0.1711, rel_tol=2e-3)
    assert math.isclose(res["F_mano_N"], 2.8519, rel_tol=2e-3)
