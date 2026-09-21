"""
Módulo de Cinemática (Unidades 1 y 2 del Sílabo de Dinámica).
Cálculos: 1, 2, 3, 4, 5, 7, 8, 9, 10.
"""

import math
from typing import Tuple, List, Dict
from .models import LatheParameters


class LatheKinematics:
    """Implementación rigurosa de las relaciones cinemáticas del torno."""

    # --------------------------------------------------------------------------
    # CÁLCULO 1: Vector Velocidad Tangencial en la Periferia
    # --------------------------------------------------------------------------
    @staticmethod
    def calc_01_velocidad_tangencial(n_rpm: float, R_m: float) -> Dict[str, float]:
        """
        Cálculo 1:
        omega = 2*pi*n / 60
        v = omega * R
        """
        omega = 2.0 * math.pi * n_rpm / 60.0
        v = omega * R_m
        return {
            "omega_rad_s": omega,
            "v_m_s": v,
            "v_m_min": v * 60.0
        }

    # --------------------------------------------------------------------------
    # CÁLCULO 2: Aceleraciones Intrínsecas Tangencial y Normal en el Arranque
    # --------------------------------------------------------------------------
    @staticmethod
    def calc_02_aceleraciones_intrinsecas(delta_t_s: float, R_m: float,
                                         omega_final_rad_s: float,
                                         omega_ini_rad_s: float = 0.0) -> Dict[str, float]:
        """
        Cálculo 2:
        alpha = (omega_final - omega_ini) / delta_t
        a_t = alpha * R
        a_n = omega_final^2 * R
        """
        alpha = (omega_final_rad_s - omega_ini_rad_s) / delta_t_s
        a_t = alpha * R_m
        a_n = (omega_final_rad_s ** 2) * R_m
        return {
            "alpha_rad_s2": alpha,
            "a_t_m_s2": a_t,
            "a_n_m_s2": a_n
        }

    # --------------------------------------------------------------------------
    # CÁLCULO 3: Desplazamiento Angular y Vueltas en Arranque Amortiguado
    # --------------------------------------------------------------------------
    @staticmethod
    def calc_03_arranque_amortiguado(t_s: float, tau_s: float,
                                    omega_reg_rad_s: float) -> Dict[str, float]:
        """
        Cálculo 3:
        omega(t) = omega_reg * (1 - exp(-t / tau))
        theta(t) = omega_reg * [t - tau * (1 - exp(-t / tau))]
        N = theta / (2*pi)
        """
        exp_factor = math.exp(-t_s / tau_s) if tau_s > 0 else 0.0
        omega_t = omega_reg_rad_s * (1.0 - exp_factor)
        theta_t = omega_reg_rad_s * (t_s - tau_s * (1.0 - exp_factor))
        N_vueltas = theta_t / (2.0 * math.pi)
        return {
            "omega_t_rad_s": omega_t,
            "theta_rad": theta_t,
            "N_rev": N_vueltas
        }

    # --------------------------------------------------------------------------
    # CÁLCULO 4: Longitud de Trayectoria Periférica Barrida
    # --------------------------------------------------------------------------
    @staticmethod
    def calc_04_longitud_barrida(R_m: float, theta_rad: float) -> float:
        """
        Cálculo 4:
        s_arco = R * theta
        """
        return R_m * theta_rad

    # --------------------------------------------------------------------------
    # CÁLCULO 5: Velocidad de Corte Estandarizada en Torneado
    # --------------------------------------------------------------------------
    @staticmethod
    def calc_05_velocidad_corte(D_m: float, n_rpm: float) -> Dict[str, float]:
        """
        Cálculo 5:
        v_c = pi * D * n / 60
        """
        vc = math.pi * D_m * n_rpm / 60.0
        return {
            "v_c_m_s": vc,
            "v_c_m_min": vc * 60.0
        }

    # --------------------------------------------------------------------------
    # CÁLCULO 7: Centro Instantáneo (CI) y Campo Lineal de Velocidades
    # --------------------------------------------------------------------------
    @staticmethod
    def calc_07_campo_velocidades(omega_rad_s: float, radios_m: List[float]) -> Dict[float, float]:
        """
        Cálculo 7:
        v(r) = omega * r
        Para r = 0 m (eje fijo), v = 0 (CI).
        """
        return {r: omega_rad_s * r for r in radios_m}

    # --------------------------------------------------------------------------
    # CÁLCULO 8: Velocidad Relativa Entre Puntos del Sólido Rígido
    # --------------------------------------------------------------------------
    @staticmethod
    def calc_08_velocidad_relativa(omega_rad_s: float, rA_m: float, rQ_m: float) -> Dict[str, float]:
        """
        Cálculo 8:
        v_Q = omega * rQ
        v_{A/Q} = omega * (rA - rQ)
        v_A = v_Q + v_{A/Q} = omega * rA
        """
        v_Q = omega_rad_s * rQ_m
        v_rel = omega_rad_s * (rA_m - rQ_m)
        v_A = v_Q + v_rel
        return {
            "v_Q_m_s": v_Q,
            "v_rel_m_s": v_rel,
            "v_A_m_s": v_A
        }

    # --------------------------------------------------------------------------
    # CÁLCULO 9: Cinemática de Reducción Radial de Diámetro en Pasada de Desbaste
    # --------------------------------------------------------------------------
    @staticmethod
    def calc_09_rebaje_radial(delta_R_m: float, fr_m_rev: float, n_rpm: float) -> Dict[str, float]:
        """
        Cálculo 9:
        N_rev = delta_R / fr
        v_r = fr * (n / 60)
        t_corte = delta_R / v_r = N_rev / (n / 60)
        """
        N_rev = delta_R_m / fr_m_rev
        rev_per_sec = n_rpm / 60.0
        v_r = fr_m_rev * rev_per_sec
        t_corte = delta_R_m / v_r
        return {
            "N_rev": N_rev,
            "v_r_m_s": v_r,
            "v_r_mm_min": v_r * 60000.0,
            "t_corte_s": t_corte
        }

    # --------------------------------------------------------------------------
    # CÁLCULO 10: Vector Aceleración Relativa y Aceleración Total del Sólido Rígido
    # --------------------------------------------------------------------------
    @staticmethod
    def calc_10_aceleracion_total(a_t_m_s2: float, a_n_m_s2: float) -> Dict[str, float]:
        """
        Cálculo 10:
        a_tot = sqrt(a_t^2 + a_n^2)
        beta_rad = arctan(a_t / a_n)
        beta_deg = beta_rad * 180 / pi
        """
        a_tot = math.sqrt(a_t_m_s2 ** 2 + a_n_m_s2 ** 2)
        beta_rad = math.atan2(a_t_m_s2, a_n_m_s2)
        beta_deg = math.degrees(beta_rad)
        return {
            "a_tot_m_s2": a_tot,
            "beta_rad": beta_rad,
            "beta_deg": beta_deg
        }
