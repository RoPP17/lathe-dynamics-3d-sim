"""Pruebas unitarias de cinemática (Cálculos 1, 2, 3, 4, 5, 7, 8, 9, 10)."""
import math
import pytest
from physics.models import LatheParameters
from physics.kinematics import LatheKinematics


def test_calc_01_velocidad_tangencial():
    p = LatheParameters()
    res = LatheKinematics.calc_01_velocidad_tangencial(p.n_nom, p.R0)
    assert math.isclose(res["omega_rad_s"], 178.0236, rel_tol=1e-4)
    assert math.isclose(res["v_m_s"], 7.1209, rel_tol=1e-4)


def test_calc_02_aceleraciones_intrinsecas():
    p = LatheParameters()
    w_nom = p.omega_nom
    res = LatheKinematics.calc_02_aceleraciones_intrinsecas(p.dt_arranque, p.R0, w_nom, 0.0)
    assert math.isclose(res["alpha_rad_s2"], 89.0118, rel_tol=1e-4)
    assert math.isclose(res["a_t_m_s2"], 3.5605, rel_tol=1e-4)
    assert math.isclose(res["a_n_m_s2"], 1267.6963, rel_tol=1e-4)


def test_calc_03_arranque_amortiguado():
    p = LatheParameters()
    res = LatheKinematics.calc_03_arranque_amortiguado(p.dt_arranque, p.tau_arranque, p.omega_nom)
    assert math.isclose(res["theta_rad"], 243.1383, rel_tol=1e-4)
    assert math.isclose(res["N_rev"], 38.70, rel_tol=2e-3)


def test_calc_04_longitud_barrida():
    p = LatheParameters()
    theta = 243.1383
    s = LatheKinematics.calc_04_longitud_barrida(p.R0, theta)
    assert math.isclose(s, 9.7255, rel_tol=1e-4)


def test_calc_05_velocidad_corte():
    p = LatheParameters()
    res = LatheKinematics.calc_05_velocidad_corte(2.0 * p.R0, p.n_nom)
    assert math.isclose(res["v_c_m_s"], 7.1209, rel_tol=1e-4)


def test_calc_07_campo_velocidades():
    p = LatheParameters()
    res = LatheKinematics.calc_07_campo_velocidades(p.omega_nom, [0.0, 0.010, 0.020, 0.030, 0.040])
    assert math.isclose(res[0.0], 0.0, abs_tol=1e-9)
    assert math.isclose(res[0.010], 1.7802, rel_tol=1e-3)
    assert math.isclose(res[0.020], 3.5605, rel_tol=1e-3)
    assert math.isclose(res[0.030], 5.3407, rel_tol=1e-3)
    assert math.isclose(res[0.040], 7.1209, rel_tol=1e-3)


def test_calc_08_velocidad_relativa():
    p = LatheParameters()
    res = LatheKinematics.calc_08_velocidad_relativa(p.omega_nom, 0.040, 0.020)
    assert math.isclose(res["v_Q_m_s"], 3.5605, rel_tol=1e-3)
    assert math.isclose(res["v_rel_m_s"], 3.5605, rel_tol=1e-3)
    assert math.isclose(res["v_A_m_s"], 7.1209, rel_tol=1e-3)


def test_calc_09_rebaje_radial():
    p = LatheParameters()
    res = LatheKinematics.calc_09_rebaje_radial(0.001, p.fr, p.n_nom)
    assert math.isclose(res["N_rev"], 400.0, rel_tol=1e-6)
    assert math.isclose(res["t_corte_s"], 14.1176, rel_tol=1e-3)


def test_calc_10_aceleracion_total():
    at = 3.5605
    an = 1267.6963
    res = LatheKinematics.calc_10_aceleracion_total(at, an)
    assert math.isclose(res["a_tot_m_s2"], 1267.7013, rel_tol=1e-4)
    assert math.isclose(res["beta_deg"], 0.1609, rel_tol=2e-3)
