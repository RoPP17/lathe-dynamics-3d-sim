"""
Motor de Simulación Temporal Desacoplado.
Gestiona el tiempo físico de simulación de forma independiente a la velocidad de reproducción.
"""

import math
from typing import Optional, Callable, List, Dict, Tuple
from physics.models import LatheParameters, DynamicState
from physics.kinematics import LatheKinematics
from physics.kinetics import LatheKinetics
from physics.motor_rundown import LatheMotorRundown


class SimulationEngine:
    """
    Motor físico de integración temporal.
    Gobernado estrictamente por las ecuaciones del Avance 2.
    """

    def __init__(self, params: Optional[LatheParameters] = None):
        self.params: LatheParameters = params.copy() if params else LatheParameters()

        # Control temporal
        self.t_sim: float = 0.0           # Tiempo físico de simulación (s)
        self.dt_integracion: float = 0.005 # Paso de cálculo numérico: 5 ms (200 Hz de física)
        self.playback_speed: float = 1.0  # Multiplicador visual (0.1x a 10x)

        # Estados de reproducción
        self.is_running: bool = False
        self.is_paused: bool = False

        # Escenario activo
        # 'ARRANQUE', 'REGIMEN', 'TORNEADO', 'DESBALANCE', 'PARADA', 'CICLO_COMPLETO'
        self.escenario: str = "CICLO_COMPLETO"

        # Tiempos de hitos para el escenario de CICLO COMPLETO
        self.t_fin_arranque: float = 2.0
        self.t_fin_regimen: float = 5.0
        self.t_fin_torneado: float = 11.0
        self.t_fin_desbalance: float = 15.0
        self.t_duracion_total_ciclo: float = 18.5

        # Radio actual dinámico
        self.R_actual: float = self.params.R0

        # Historial de estados para trazabilidad y gráficas sincronizadas
        # Guardamos puntos muestreados a ~50 Hz
        self.history_t: List[float] = []
        self.history_omega: List[float] = []
        self.history_rpm: List[float] = []
        self.history_v: List[float] = []
        self.history_at: List[float] = []
        self.history_an: List[float] = []
        self.history_atot: List[float] = []
        self.history_theta: List[float] = []
        self.history_rev: List[float] = []
        self.history_P_corte: List[float] = []
        self.history_P_loss: List[float] = []
        self.history_P_total: List[float] = []
        self.history_Fu: List[float] = []
        self.history_R: List[float] = []

        # Estado actual
        self.current_state: DynamicState = self._compute_state(0.0)
        self._record_history(self.current_state)

        # Callbacks opcionales para desacoplamiento de GUI
        self.on_state_updated: Optional[Callable[[DynamicState], None]] = None

    @property
    def scenario_name(self) -> str:
        """Alias para nombre del escenario activo."""
        return self.escenario

    def reset(self, escenario: Optional[str] = None):
        """Reinicia la simulación al instante t = 0 con el escenario seleccionado."""
        if escenario:
            self.escenario = escenario
        self.t_sim = 0.0
        self.is_running = False
        self.is_paused = False
        self.R_actual = self.params.R0

        self.history_t.clear()
        self.history_omega.clear()
        self.history_rpm.clear()
        self.history_v.clear()
        self.history_at.clear()
        self.history_an.clear()
        self.history_atot.clear()
        self.history_theta.clear()
        self.history_rev.clear()
        self.history_P_corte.clear()
        self.history_P_loss.clear()
        self.history_P_total.clear()
        self.history_Fu.clear()
        self.history_R.clear()

        self.current_state = self._compute_state(0.0)
        self._record_history(self.current_state)
        if self.on_state_updated:
            self.on_state_updated(self.current_state)

    def set_parameters(self, params: LatheParameters):
        """Actualiza los parámetros físicos del simulador."""
        self.params = params.copy()
        self.reset()

    def set_playback_speed(self, speed: float):
        """Ajusta la velocidad de reproducción sin alterar la física."""
        if speed > 0:
            self.playback_speed = speed

    def play(self):
        """Inicia o reanuda la simulación."""
        self.is_running = True
        self.is_paused = False

    def pause(self):
        """Pausa la simulación manteniendo el tiempo exacto."""
        self.is_paused = True

    def toggle_play_pause(self):
        """Alterna entre reproducción y pausa."""
        if not self.is_running:
            self.play()
        elif self.is_paused:
            self.is_paused = False
        else:
            self.pause()

    def stop(self):
        """Detiene y reinicia la simulación."""
        self.reset()

    def step_forward(self, dt_manual: Optional[float] = None):
        """Avanza un paso de tiempo discreto (útil para inspección paso a paso)."""
        dt = dt_manual if dt_manual is not None else self.dt_integracion
        self.t_sim += dt
        self._update()

    def step_backward(self, dt_manual: Optional[float] = None):
        """Retrocede un paso de tiempo discreto."""
        dt = dt_manual if dt_manual is not None else self.dt_integracion
        self.t_sim = max(0.0, self.t_sim - dt)
        self._update()

    def seek_time(self, t_target: float):
        """Salta a un tiempo de simulación específico (scrubbing de línea de tiempo)."""
        self.t_sim = max(0.0, t_target)
        self._update()

    def advance_real_time(self, real_dt_seconds: float):
        """
        Avanza la física en función del tiempo de reloj real transcurrido
        y el factor de velocidad de reproducción (playback_speed).
        """
        if not self.is_running or self.is_paused:
            return

        # Tiempo físico a avanzar
        sim_dt_to_advance = real_dt_seconds * self.playback_speed
        self.t_sim += sim_dt_to_advance

        # Límite máximo en ciclo completo
        if self.escenario == "CICLO_COMPLETO" and self.t_sim >= self.t_duracion_total_ciclo:
            self.t_sim = self.t_duracion_total_ciclo
            self.pause()
        elif self.escenario == "ARRANQUE" and self.t_sim >= self.params.dt_arranque:
            self.t_sim = self.params.dt_arranque
            self.pause()
        elif self.escenario == "PARADA" and self.t_sim >= self.params.dt_parada + 0.5:
            self.t_sim = self.params.dt_parada + 0.5
            self.pause()

        self._update()

    def _update(self):
        """Calcula el estado actual y lo almacena."""
        self.current_state = self._compute_state(self.t_sim)
        self._record_history(self.current_state)
        if self.on_state_updated:
            self.on_state_updated(self.current_state)

    def _compute_state(self, t: float) -> DynamicState:
        """Calcula todas las variables físicas según el escenario y el tiempo t."""
        p = self.params
        w_reg = p.omega_nom
        tau_arr = p.tau_arranque
        tau_stop = p.tau_stop
        b = p.b_viscoso

        fase = self.escenario
        omega = 0.0
        alpha = 0.0
        theta = 0.0
        R_curr = p.R0
        Fc_actual = 0.0
        m_dot = 0.0
        Freac = 0.0

        if self.escenario == "ARRANQUE":
            # Transitorio exponencial puro de arranque (Cálculo 3)
            if t <= p.dt_arranque:
                exp_t = math.exp(-t / tau_arr) if tau_arr > 0 else 0.0
                omega = w_reg * (1.0 - exp_t)
                alpha = (w_reg / tau_arr) * exp_t if tau_arr > 0 else 0.0
                theta = w_reg * (t - tau_arr * (1.0 - exp_t))
            else:
                omega = w_reg
                alpha = 0.0
                theta_arr_fin = w_reg * (p.dt_arranque - tau_arr * (1.0 - math.exp(-p.dt_arranque / tau_arr)))
                theta = theta_arr_fin + w_reg * (t - p.dt_arranque)
            fase = "ARRANQUE"

        elif self.escenario == "REGIMEN":
            # Régimen nominal constante (Cálculo 1)
            omega = w_reg
            alpha = 0.0
            theta = w_reg * t
            fase = "REGIMEN"

        elif self.escenario == "TORNEADO":
            # Desbaste radial continuo a velocidad nominal (Cálculo 9)
            omega = w_reg
            alpha = 0.0
            theta = w_reg * t
            res_c9 = LatheKinematics.calc_09_rebaje_radial(0.001, p.fr, p.n_nom)
            vr = res_c9["v_r_m_s"]
            # Reducción de hasta 1 mm (de 40 mm a 39 mm)
            delta_R = min(0.001, vr * t)
            R_curr = p.R0 - delta_R
            Fc_actual = p.Fc
            vc_inst = omega * R_curr
            res_c15 = LatheKinetics.calc_15_transporte_momento_viruta(p.rho_pieza, p.bw, p.tc, vc_inst, p.u_viruta)
            m_dot = res_c15["m_dot_kg_s"]
            Freac = res_c15["F_reac_N"]
            fase = "TORNEADO"

        elif self.escenario == "DESBALANCE":
            # Rotación en régimen con vector centrífugo de desbalance activo (Cálculo 11)
            omega = w_reg
            alpha = 0.0
            theta = w_reg * t
            fase = "DESBALANCE"

        elif self.escenario == "PARADA":
            # Frenado libre / Run-down (Cálculos 17 y 18)
            exp_stop = math.exp(-t / tau_stop) if tau_stop > 0 else 0.0
            omega = w_reg * exp_stop
            alpha = -(w_reg / tau_stop) * exp_stop if tau_stop > 0 else 0.0
            theta = w_reg * tau_stop * (1.0 - exp_stop)
            fase = "PARADA"

        elif self.escenario == "CICLO_COMPLETO":
            # Secuencia integrada: Arranque -> Régimen -> Torneado -> Desbalance -> Parada
            if t < self.t_fin_arranque:
                # 0.0 a 2.0 s: Arranque
                exp_t = math.exp(-t / tau_arr) if tau_arr > 0 else 0.0
                omega = w_reg * (1.0 - exp_t)
                alpha = (w_reg / tau_arr) * exp_t if tau_arr > 0 else 0.0
                theta = w_reg * (t - tau_arr * (1.0 - exp_t))
                fase = "ARRANQUE"

            elif t < self.t_fin_regimen:
                # 2.0 a 5.0 s: Régimen libre
                t_arr_fin = self.t_fin_arranque
                theta_base = w_reg * (t_arr_fin - tau_arr * (1.0 - math.exp(-t_arr_fin / tau_arr)))
                omega = w_reg
                alpha = 0.0
                theta = theta_base + w_reg * (t - t_arr_fin)
                fase = "REGIMEN"

            elif t < self.t_fin_torneado:
                # 5.0 a 11.0 s: Torneado / Mecanizado
                t_arr_fin = self.t_fin_arranque
                theta_base = w_reg * (t_arr_fin - tau_arr * (1.0 - math.exp(-t_arr_fin / tau_arr)))
                t_en_regimen = self.t_fin_regimen - self.t_fin_arranque
                theta_antes_torneado = theta_base + w_reg * t_en_regimen

                omega = w_reg
                alpha = 0.0
                t_corte_transcurrido = t - self.t_fin_regimen
                theta = theta_antes_torneado + w_reg * t_corte_transcurrido

                # Rebaje radial proporcional
                res_c9 = LatheKinematics.calc_09_rebaje_radial(0.001, p.fr, p.n_nom)
                vr = res_c9["v_r_m_s"]
                delta_R = min(0.001, vr * (t_corte_transcurrido * (1.0 / 6.0 * 14.1176))) # escalado para visualización completa
                R_curr = p.R0 - delta_R

                Fc_actual = p.Fc
                vc_inst = omega * R_curr
                res_c15 = LatheKinetics.calc_15_transporte_momento_viruta(p.rho_pieza, p.bw, p.tc, vc_inst, p.u_viruta)
                m_dot = res_c15["m_dot_kg_s"]
                Freac = res_c15["F_reac_N"]
                fase = "TORNEADO"

            elif t < self.t_fin_desbalance:
                # 11.0 a 15.0 s: Demostración de desbalance dinámico
                t_prev = self.t_fin_desbalance - self.t_fin_torneado
                omega = w_reg
                alpha = 0.0
                # Acumulación de theta continua
                theta = w_reg * t
                R_curr = p.R0 - 0.001 # mantiene el diámetro desbastado
                fase = "DESBALANCE"

            else:
                # 15.0 a 18.5 s: Parada libre (Run-down)
                t_rundown = t - self.t_fin_desbalance
                exp_stop = math.exp(-t_rundown / tau_stop) if tau_stop > 0 else 0.0
                omega = w_reg * exp_stop
                alpha = -(w_reg / tau_stop) * exp_stop if tau_stop > 0 else 0.0
                # Theta se acumula suavemente
                theta_base = w_reg * self.t_fin_desbalance
                theta_remanente = w_reg * tau_stop * (1.0 - exp_stop)
                theta = theta_base + theta_remanente
                R_curr = p.R0 - 0.001
                fase = "PARADA"

        # Cinemática puntual y aceleraciones
        v_perif = omega * R_curr
        v_corte = v_perif
        at = alpha * R_curr
        an = (omega ** 2) * R_curr
        res_c10 = LatheKinematics.calc_10_aceleracion_total(at, an)
        atot = res_c10["a_tot_m_s2"]
        beta_deg = res_c10["beta_deg"]
        s_arco = R_curr * theta
        rev = theta / (2.0 * math.pi)
        rpm = omega * 60.0 / (2.0 * math.pi)

        # Desbalance dinámico (Cálculo 11)
        res_c11 = LatheKinetics.calc_11_fuerza_desbalance(p.mu, p.e_desbalance, omega)
        Fu = res_c11["F_u_N"]
        # El vector de fuerza centrífuga gira solidario con la pieza a ángulo theta
        Fu_x = Fu * math.cos(theta)
        Fu_y = Fu * math.sin(theta)

        # Potencias y balances energéticos (Cálculos 12, 13, 14, 16)
        res_c13 = LatheKinetics.calc_13_potencias_y_eficiencia(Fc_actual, v_corte, b, omega)
        P_corte = res_c13["P_corte_W"]
        P_loss = res_c13["P_loss_W"]
        P_total = res_c13["P_total_W"]
        eficiencia_pct = res_c13["eficiencia_pct"]

        I_tot = p.I_tot
        H_O = I_tot * omega
        E_cin = 0.5 * I_tot * (omega ** 2)

        return DynamicState(
            t=t,
            fase=fase,
            omega=omega,
            rpm=rpm,
            alpha=alpha,
            theta=theta,
            rev=rev,
            R_actual=R_curr,
            D_actual=2.0 * R_curr,
            v_perif=v_perif,
            v_corte=v_corte,
            a_t=at,
            a_n=an,
            a_total=atot,
            beta_deg=beta_deg,
            s_arco=s_arco,
            F_desbalance=Fu,
            F_desbalance_x=Fu_x,
            F_desbalance_y=Fu_y,
            F_corte_actual=Fc_actual,
            m_dot_viruta=m_dot,
            F_reac_viruta=Freac,
            P_corte=P_corte,
            P_loss=P_loss,
            P_total=P_total,
            eficiencia_pct=eficiencia_pct,
            H_O=H_O,
            E_cinetica_rot=E_cin
        )

    def _record_history(self, state: DynamicState):
        """Almacena el estado para graficación sincronizada."""
        # Si saltamos en el tiempo (seek) hacia atrás, truncamos el historial posterior
        if self.history_t and state.t < self.history_t[-1]:
            idx = 0
            while idx < len(self.history_t) and self.history_t[idx] <= state.t:
                idx += 1
            self.history_t = self.history_t[:idx]
            self.history_omega = self.history_omega[:idx]
            self.history_rpm = self.history_rpm[:idx]
            self.history_v = self.history_v[:idx]
            self.history_at = self.history_at[:idx]
            self.history_an = self.history_an[:idx]
            self.history_atot = self.history_atot[:idx]
            self.history_theta = self.history_theta[:idx]
            self.history_rev = self.history_rev[:idx]
            self.history_P_corte = self.history_P_corte[:idx]
            self.history_P_loss = self.history_P_loss[:idx]
            self.history_P_total = self.history_P_total[:idx]
            self.history_Fu = self.history_Fu[:idx]
            self.history_R = self.history_R[:idx]

        # Solo registrar si está vacío o si avanzó al menos ~10 ms para mantener alta resolución
        if not self.history_t or (state.t - self.history_t[-1]) >= 0.010:
            self.history_t.append(state.t)
            self.history_omega.append(state.omega)
            self.history_rpm.append(state.rpm)
            self.history_v.append(state.v_perif)
            self.history_at.append(state.a_t)
            self.history_an.append(state.a_n)
            self.history_atot.append(state.a_total)
            self.history_theta.append(state.theta)
            self.history_rev.append(state.rev)
            self.history_P_corte.append(state.P_corte)
            self.history_P_loss.append(state.P_loss)
            self.history_P_total.append(state.P_total)
            self.history_Fu.append(state.F_desbalance)
            self.history_R.append(state.R_actual * 1000.0) # en mm

    def precalculate_full_scenario(self, dt_step: float = 0.010) -> Dict[str, List[float]]:
        """
        Precalcula las curvas completas del escenario actual para mostrarlas
        completas en el fondo de las gráficas sincronizadas.
        """
        t_max = self.t_duracion_total_ciclo if self.escenario == "CICLO_COMPLETO" else (
            self.params.dt_arranque if self.escenario == "ARRANQUE" else (
                self.params.dt_parada + 0.5 if self.escenario == "PARADA" else 10.0
            )
        )

        t_vals: List[float] = []
        w_vals: List[float] = []
        rpm_vals: List[float] = []
        v_vals: List[float] = []
        at_vals: List[float] = []
        an_vals: List[float] = []
        atot_vals: List[float] = []
        th_vals: List[float] = []
        Ptot_vals: List[float] = []
        Fu_vals: List[float] = []

        curr_t = 0.0
        while curr_t <= t_max:
            st = self._compute_state(curr_t)
            t_vals.append(st.t)
            w_vals.append(st.omega)
            rpm_vals.append(st.rpm)
            v_vals.append(st.v_perif)
            at_vals.append(st.a_t)
            an_vals.append(st.a_n)
            atot_vals.append(st.a_total)
            th_vals.append(st.theta)
            Ptot_vals.append(st.P_total)
            Fu_vals.append(st.F_desbalance)
            curr_t += dt_step

        return {
            "t": t_vals,
            "omega": w_vals,
            "rpm": rpm_vals,
            "v": v_vals,
            "at": at_vals,
            "an": an_vals,
            "atot": atot_vals,
            "theta": th_vals,
            "P_total": Ptot_vals,
            "Fu": Fu_vals
        }
