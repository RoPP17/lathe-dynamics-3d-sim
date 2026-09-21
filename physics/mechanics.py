"""
Módulo de Resistencia Mecánica, Torsión de Eje, Chaveta y Mecánica de Contrapunto.
Cálculos: 19, 20.
"""

import math
from typing import Dict


class LatheMechanics:
    """Implementación de la resistencia de materiales aplicada al husillo y mecanismo del contrapunto."""

    # --------------------------------------------------------------------------
    # CÁLCULO 19: Esfuerzo Torsional en el Eje y Verificación de la Chaveta
    # --------------------------------------------------------------------------
    @staticmethod
    def calc_19_torsion_eje_chaveta(Mt_Nm: float, d_eje_m: float, L_eje_m: float,
                                    b_chaveta_m: float, h_chaveta_m: float,
                                    l_chaveta_m: float, Kt: float,
                                    G_Pa: float) -> Dict[str, float]:
        """
        Cálculo 19:
        J = pi * d^4 / 32
        tau_nom = 16 * Mt / (pi * d^3)
        tau_max = Kt * tau_nom
        tau_key = 2 * Mt / (d * b * l)
        sigma_aplast = 4 * Mt / (d * h * l)
        phi_rad = Mt * L_eje / (J * G)
        """
        J = math.pi * (d_eje_m ** 4) / 32.0
        tau_nom = 16.0 * Mt_Nm / (math.pi * (d_eje_m ** 3))
        tau_max = Kt * tau_nom
        tau_key = (2.0 * Mt_Nm) / (d_eje_m * b_chaveta_m * l_chaveta_m)
        sigma_aplast = (4.0 * Mt_Nm) / (d_eje_m * h_chaveta_m * l_chaveta_m)
        phi_rad = (Mt_Nm * L_eje_m) / (J * G_Pa)
        phi_deg = math.degrees(phi_rad)

        return {
            "J_m4": J,
            "tau_nom_Pa": tau_nom,
            "tau_nom_MPa": tau_nom * 1e-6,
            "tau_max_Pa": tau_max,
            "tau_max_MPa": tau_max * 1e-6,
            "tau_key_Pa": tau_key,
            "tau_key_MPa": tau_key * 1e-6,
            "sigma_aplast_Pa": sigma_aplast,
            "sigma_aplast_MPa": sigma_aplast * 1e-6,
            "phi_rad": phi_rad,
            "phi_deg": phi_deg
        }

    # --------------------------------------------------------------------------
    # CÁLCULO 20: Mecánica Helicoidal de Fijación del Contrapunto y Esfuerzo Manual
    # --------------------------------------------------------------------------
    @staticmethod
    def calc_20_mecanica_contrapunto(F0_N: float, k_N_m: float, x_m: float,
                                     p_m_rev: float, r_volante_m: float) -> Dict[str, float]:
        """
        Cálculo 20:
        F_final = F0 + k * x
        U_axial = F0 * x + 0.5 * k * x^2
        N_vueltas = x / p
        M_torsor = U_axial / (2 * pi * N_vueltas)
        F_mano = M_torsor / r_volante
        """
        F_final = F0_N + k_N_m * x_m
        U_axial = F0_N * x_m + 0.5 * k_N_m * (x_m ** 2)
        N_vueltas = x_m / p_m_rev
        theta_volante_rad = 2.0 * math.pi * N_vueltas

        M_torsor = U_axial / theta_volante_rad if theta_volante_rad > 0 else 0.0
        F_mano = M_torsor / r_volante_m if r_volante_m > 0 else 0.0

        return {
            "F_final_N": F_final,
            "U_axial_J": U_axial,
            "N_vueltas_rev": N_vueltas,
            "angulo_volante_deg": N_vueltas * 360.0,
            "M_torsor_Nm": M_torsor,
            "F_mano_N": F_mano,
            "F_mano_gf": F_mano * (1000.0 / 9.80665)
        }
