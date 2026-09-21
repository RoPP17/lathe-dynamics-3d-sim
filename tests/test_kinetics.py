"""Pruebas unitarias de cinética (Cálculos 11, 12, 13, 14, 15, 16)."""
import math
import pytest
from physics.models import LatheParameters
from physics.kinetics import LatheKinetics


def test_calc_11_fuerza_desbalance():
    p = LatheParameters()
    res = LatheKinetics.calc_11_fuerza_desbalance(p.mu, p.e_desbalance, p.omega_nom)
    assert math.isclose(res["F_u_N"], 1.2677, rel_tol=1e-3)


def test_calc_12_trabajo_energia():
    v = 7.1209
    res = LatheKinetics.calc_12_trabajo_energia_particula(0.001, v)
    assert math.isclose(res["U_1_2_J"], 0.02535, rel_tol=1e-3)


def test_calc_13_potencia_eficiencia():
    p = LatheParameters()
    vc = 7.1209
    res = LatheKinetics.calc_13_potencias_y_eficiencia(p.Fc, vc, p.b_viscoso, p.omega_nom)
    assert math.isclose(res["P_corte_W"], 142.4180, rel_tol=1e-3)
    assert math.isclose(res["P_loss_W"], 58.4381, rel_tol=1e-3)
    assert math.isclose(res["P_total_W"], 200.8561, rel_tol=1e-3)
    assert math.isclose(res["eficiencia_pct"], 70.91, rel_tol=2e-3)


def test_calc_14_impulso_angular():
    p = LatheParameters()
    res = LatheKinetics.calc_14_impulso_angular(p.I_tot, p.omega_nom, p.dt_arranque)
    assert math.isclose(res["Delta_H_O_Nms"], 0.21380, rel_tol=1e-3)
    assert math.isclose(res["M_medio_Nm"], 0.1069, rel_tol=1e-3)


def test_calc_15_reaccion_viruta():
    p = LatheParameters()
    vc = 7.1209
    res = LatheKinetics.calc_15_transporte_momento_viruta(p.rho_pieza, p.bw, p.tc, vc, p.u_viruta)
    assert math.isclose(res["m_dot_kg_s"], 8.9011e-3, rel_tol=1e-3)
    assert math.isclose(res["F_reac_N"], 0.0534, rel_tol=1e-3)


def test_calc_16_inercia_compuesta():
    p = LatheParameters()
    res = LatheKinetics.calc_16_inercia_compuesta(p.m_pieza, p.R0, p.m_plato, p.R_plato)
    assert math.isclose(res["I_pieza_kgm2"], 5.0264e-4, rel_tol=1e-3)
    assert math.isclose(res["I_plato_kgm2"], 6.9832e-4, rel_tol=1e-3)
    assert math.isclose(res["I_tot_kgm2"], 1.20097e-3, rel_tol=1e-4)
