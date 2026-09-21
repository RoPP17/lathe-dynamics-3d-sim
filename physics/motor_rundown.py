"""
Módulo de Motor de Inducción y Parada Libre / Run-Down.
Cálculos: 6, 17, 18.
"""

import math
from typing import Dict


class LatheMotorRundown:
    """Implementación de la máquina de inducción y el régimen de frenado libre."""

    # --------------------------------------------------------------------------
    # CÁLCULO 6: Velocidad Sincrónica y Deslizamiento del Motor
    # --------------------------------------------------------------------------
    @staticmethod
    def calc_06_sincrona_y_deslizamiento(f_hz: float, polos: int, n_rpm: float) -> Dict[str, float]:
        """
        Cálculo 6:
        n_s = 120 * f / p
        s = (n_s - n) / n_s
        """
        ns = 120.0 * f_hz / polos
        slip = (ns - n_rpm) / ns if ns > 0 else 0.0
        return {
            "n_s_rpm": ns,
            "slip_frac": slip,
            "slip_pct": slip * 100.0
        }

    # --------------------------------------------------------------------------
    # CÁLCULO 17: Coeficiente de Pérdidas Viscosas en Parada Libre (Run-Down)
    # --------------------------------------------------------------------------
    @staticmethod
    def calc_17_perdidas_viscosas_arranque(dt_stop_s: float, I_tot_kgm2: float,
                                           omega_reg_rad_s: float,
                                           Ta_arranque_s: float = 2.0,
                                           criterio_stop: float = 100.0,
                                           tau_arr_s: float = None) -> Dict[str, float]:
        """
        Cálculo 17:
        tau_stop = dt_stop / ln(criterio_stop)   [criterio 100 -> al 1% de velocidad: 0.65144 s]
        b = I_tot / tau_stop
        U_perd = integral_0^Ta b*omega(t)^2 dt
               = b * omega_reg^2 * [Ta - 2*tau*(1 - exp(-Ta/tau)) + (tau/2)*(1 - exp(-2*Ta/tau))]
        Nota técnica: en el desarrollo manual de avance2.tex (Ec. 920), se evaluó con
        tau = tau_stop = 0.65144 s arrojando [2.0 - 1.2423 + 0.3250] = 63.27 J.
        Si se pasa tau_arr_s explícito, utiliza la constante de aceleración.
        """
        tau_stop = dt_stop_s / math.log(criterio_stop)
        b = I_tot_kgm2 / tau_stop

        # Si no se provee tau_arr_s, se evalúa con tau_stop conforme al desarrollo de avance2.tex
        tau_eval = tau_stop if tau_arr_s is None else tau_arr_s
        exp_1 = math.exp(-Ta_arranque_s / tau_eval)
        exp_2 = math.exp(-2.0 * Ta_arranque_s / tau_eval)

        bracket = Ta_arranque_s - 2.0 * tau_eval * (1.0 - exp_1) + 0.5 * tau_eval * (1.0 - exp_2)
        U_perd = b * (omega_reg_rad_s ** 2) * bracket

        return {
            "tau_stop_s": tau_stop,
            "b_viscoso_Nms": b,
            "U_perd_J": U_perd
        }

    # --------------------------------------------------------------------------
    # CÁLCULO 18: Vueltas Remanentes y Par Disipativo en Parada Libre
    # --------------------------------------------------------------------------
    @staticmethod
    def calc_18_rundown_remanente(omega_0_rad_s: float, tau_stop_s: float,
                                  b_viscoso_Nms: float) -> Dict[str, float]:
        """
        Cálculo 18:
        theta_inf = omega_0 * tau_stop
        N_inf = theta_inf / (2*pi)
        M_loss_0 = b * omega_0
        """
        theta_inf = omega_0_rad_s * tau_stop_s
        N_inf = theta_inf / (2.0 * math.pi)
        M_loss_0 = b_viscoso_Nms * omega_0_rad_s
        return {
            "theta_inf_rad": theta_inf,
            "N_inf_rev": N_inf,
            "M_loss_0_Nm": M_loss_0
        }

    @staticmethod
    def eval_decay_at_time(t_s: float, omega_0_rad_s: float, tau_stop_s: float) -> Dict[str, float]:
        """
        Evolución temporal del frenado libre:
        omega(t) = omega_0 * exp(-t / tau_stop)
        theta(t) = omega_0 * tau_stop * [1 - exp(-t / tau_stop)]
        N(t) = theta(t) / (2*pi)
        """
        exp_t = math.exp(-t_s / tau_stop_s) if tau_stop_s > 0 else 0.0
        w_t = omega_0_rad_s * exp_t
        th_t = omega_0_rad_s * tau_stop_s * (1.0 - exp_t)
        N_t = th_t / (2.0 * math.pi)
        return {
            "omega_t_rad_s": w_t,
            "rpm_t": w_t * 60.0 / (2.0 * math.pi),
            "theta_t_rad": th_t,
            "N_t_rev": N_t
        }
