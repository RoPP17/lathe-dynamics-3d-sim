"""Pruebas unitarias de motor y frenado libre (Cálculos 6, 17, 18)."""
import math
import pytest
from physics.models import LatheParameters
from physics.motor_rundown import LatheMotorRundown


def test_calc_06_motor_sincrona_deslizamiento():
    p = LatheParameters()
    res = LatheMotorRundown.calc_06_sincrona_y_deslizamiento(p.freq, p.polos, p.n_nom)
    assert math.isclose(res["n_s_rpm"], 1800.0, rel_tol=1e-6)
    assert math.isclose(res["slip_pct"], 5.5556, rel_tol=1e-3)


def test_calc_17_perdidas_viscosas():
    p = LatheParameters()
    res = LatheMotorRundown.calc_17_perdidas_viscosas_arranque(
        p.dt_parada, p.I_tot, p.omega_nom, p.dt_arranque
    )
    assert math.isclose(res["tau_stop_s"], 0.65144, rel_tol=1e-3)
    assert math.isclose(res["b_viscoso_Nms"], 1.8436e-3, rel_tol=1e-3)
    assert math.isclose(res["U_perd_J"], 63.27, rel_tol=2e-3)


def test_calc_18_rundown_remanente():
    p = LatheParameters()
    b = 1.8436e-3
    tau = 0.65144
    res = LatheMotorRundown.calc_18_rundown_remanente(p.omega_nom, tau, b)
    assert math.isclose(res["theta_inf_rad"], 115.9715, rel_tol=1e-3)
    assert math.isclose(res["N_inf_rev"], 18.4574, rel_tol=2e-3)
    assert math.isclose(res["M_loss_0_Nm"], 0.3282, rel_tol=1e-3)
