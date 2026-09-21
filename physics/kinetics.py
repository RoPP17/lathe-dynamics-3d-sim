"""
Módulo de Cinética (Unidades 3 y 4 del Sílabo de Dinámica).
Cálculos: 11, 12, 13, 14, 15, 16.
"""

import math
from typing import Dict


class LatheKinetics:
    """Implementación rigurosa de las relaciones cinéticas, fuerzas y energías del torno."""

    # --------------------------------------------------------------------------
    # CÁLCULO 11: Fuerza Centrífuga por Desbalance Inercial Excéntrico
    # --------------------------------------------------------------------------
    @staticmethod
    def calc_11_fuerza_desbalance(mu_kg: float, e_m: float, omega_rad_s: float) -> Dict[str, float]:
        """
        Cálculo 11:
        F_u = mu * e * omega^2
        frecuencia_hz = omega / (2*pi)
        """
        Fu = mu_kg * e_m * (omega_rad_s ** 2)
        frec_hz = omega_rad_s / (2.0 * math.pi)
        return {
            "F_u_N": Fu,
            "frecuencia_hz": frec_hz,
            "reaccion_apoyo_N": -Fu
        }

    # --------------------------------------------------------------------------
    # CÁLCULO 12: Principio del Trabajo y la Energía para Partícula Periférica
    # --------------------------------------------------------------------------
    @staticmethod
    def calc_12_trabajo_energia_particula(m_particula_kg: float, v_m_s: float) -> Dict[str, float]:
        """
        Cálculo 12:
        T1 + sum U_{1-2} = T2
        U_{1-2} = Delta T = 0.5 * m * v^2
        """
        U_1_2 = 0.5 * m_particula_kg * (v_m_s ** 2)
        return {
            "U_1_2_J": U_1_2,
            "U_1_2_mJ": U_1_2 * 1000.0
        }

    # --------------------------------------------------------------------------
    # CÁLCULO 13: Potencia de Corte, Disipación Viscosa y Eficiencia Mecánica
    # --------------------------------------------------------------------------
    @staticmethod
    def calc_13_potencias_y_eficiencia(Fc_N: float, vc_m_s: float,
                                       b_viscoso_nms: float,
                                       omega_rad_s: float) -> Dict[str, float]:
        """
        Cálculo 13:
        P_corte = Fc * vc
        P_loss = b * omega^2
        P_total = P_corte + P_loss
        eficiencia = P_corte / P_total
        """
        P_corte = Fc_N * vc_m_s
        P_loss = b_viscoso_nms * (omega_rad_s ** 2)
        P_total = P_corte + P_loss
        eficiencia = P_corte / P_total if P_total > 0 else 0.0
        return {
            "P_corte_W": P_corte,
            "P_loss_W": P_loss,
            "P_total_W": P_total,
            "eficiencia_frac": eficiencia,
            "eficiencia_pct": eficiencia * 100.0
        }

    # --------------------------------------------------------------------------
    # CÁLCULO 14: Principio del Impulso y Cantidad de Movimiento Angular
    # --------------------------------------------------------------------------
    @staticmethod
    def calc_14_impulso_angular(I_tot_kgm2: float, omega_rad_s: float,
                                delta_t_s: float) -> Dict[str, float]:
        """
        Cálculo 14:
        Delta H_O = I_tot * omega
        M_medio = Delta H_O / delta_t
        """
        Delta_H_O = I_tot_kgm2 * omega_rad_s
        M_medio = Delta_H_O / delta_t_s if delta_t_s > 0 else 0.0
        return {
            "Delta_H_O_Nms": Delta_H_O,
            "M_medio_Nm": M_medio
        }

    # --------------------------------------------------------------------------
    # CÁLCULO 15: Reacción Inercial por Transporte Convectivo en Virutas
    # --------------------------------------------------------------------------
    @staticmethod
    def calc_15_transporte_momento_viruta(rho_kg_m3: float, bw_m: float,
                                          tc_m: float, vc_m_s: float,
                                          u_m_s: float) -> Dict[str, float]:
        """
        Cálculo 15:
        m_dot = rho * bw * tc * vc
        F_reac = m_dot * u
        """
        m_dot = rho_kg_m3 * bw_m * tc_m * vc_m_s
        F_reac = m_dot * u_m_s
        return {
            "m_dot_kg_s": m_dot,
            "m_dot_g_s": m_dot * 1000.0,
            "F_reac_N": F_reac
        }

    # --------------------------------------------------------------------------
    # CÁLCULO 16: Momento de Inercia de Masa Compuesto del Rotor
    # --------------------------------------------------------------------------
    @staticmethod
    def calc_16_inercia_compuesta(m_pieza_kg: float, R_pieza_m: float,
                                  m_plato_kg: float, R_plato_m: float) -> Dict[str, float]:
        """
        Cálculo 16:
        I_pieza = 0.5 * m_pieza * R_pieza^2
        I_plato = 0.5 * m_plato * R_plato^2
        I_tot = I_pieza + I_plato
        """
        I_pieza = 0.5 * m_pieza_kg * (R_pieza_m ** 2)
        I_plato = 0.5 * m_plato_kg * (R_plato_m ** 2)
        I_tot = I_pieza + I_plato
        return {
            "I_pieza_kgm2": I_pieza,
            "I_plato_kgm2": I_plato,
            "I_tot_kgm2": I_tot,
            "pct_inercia_plato": (I_plato / I_tot * 100.0) if I_tot > 0 else 0.0
        }
