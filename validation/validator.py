"""
Motor de Validación Numérica y Comparación contra el Caso Base (Avance 2).
"""

from dataclasses import dataclass
from typing import List, Dict, Any
from physics.models import LatheParameters
from physics.kinematics import LatheKinematics
from physics.kinetics import LatheKinetics
from physics.motor_rundown import LatheMotorRundown
from physics.mechanics import LatheMechanics
from physics.benchmark import AVANCE2_BENCHMARK_LIST, CalculationBenchmark


@dataclass
class ValidationRow:
    calc_num: int
    titulo: str
    unidad_tematica: str
    variable_simbolo: str
    variable_nombre: str
    ecuacion_latex: str
    valor_analitico: float
    valor_simulado: float
    error_absoluto: float
    error_relativo_pct: float
    tolerancia_pct: float
    unidad_si: str
    aprobado: bool
    descripcion: str
    ecuacion_compilada: str = ""
    variable_html: str = ""


class LatheValidator:
    """Ejecuta y compara los 20 cálculos físicos frente al benchmark oficial."""

    @classmethod
    def evaluate_all(cls, params: LatheParameters) -> List[ValidationRow]:
        """Evalúa los 20 cálculos para un conjunto de parámetros dados."""
        rows: List[ValidationRow] = []

        # Valores base derivados
        omega_nom = params.omega_nom
        I_tot = params.I_tot
        b_viscoso = params.b_viscoso

        # C1: Velocidad tangencial
        res_c1 = LatheKinematics.calc_01_velocidad_tangencial(params.n_nom, params.R0)
        v_c1 = res_c1["v_m_s"]

        # C2: Aceleraciones intrínsecas
        res_c2 = LatheKinematics.calc_02_aceleraciones_intrinsecas(
            params.dt_arranque, params.R0, omega_nom, 0.0
        )
        an_c2 = res_c2["a_n_m_s2"]
        at_c2 = res_c2["a_t_m_s2"]

        # C3: Giro en arranque amortiguado
        res_c3 = LatheKinematics.calc_03_arranque_amortiguado(
            params.dt_arranque, params.tau_arranque, omega_nom
        )
        theta_c3 = res_c3["theta_rad"]

        # C4: Longitud de trayectoria barrida
        s_c4 = LatheKinematics.calc_04_longitud_barrida(params.R0, theta_c3)

        # C5: Velocidad de corte estandarizada
        res_c5 = LatheKinematics.calc_05_velocidad_corte(2.0 * params.R0, params.n_nom)
        vc_c5 = res_c5["v_c_m_s"]

        # C6: Deslizamiento motor
        res_c6 = LatheMotorRundown.calc_06_sincrona_y_deslizamiento(
            params.freq, params.polos, params.n_nom
        )
        s_c6_pct = res_c6["slip_pct"]

        # C7: Velocidad a r = 30 mm
        campo_c7 = LatheKinematics.calc_07_campo_velocidades(omega_nom, [0.030])
        v30_c7 = campo_c7[0.030]

        # C8: Velocidad relativa A respecto a Q (rA = 40 mm, rQ = 20 mm)
        res_c8 = LatheKinematics.calc_08_velocidad_relativa(omega_nom, 0.040, 0.020)
        v_rel_c8 = res_c8["v_rel_m_s"]

        # C9: Rebaje radial de 1 mm
        res_c9 = LatheKinematics.calc_09_rebaje_radial(0.001, params.fr, params.n_nom)
        t_corte_c9 = res_c9["t_corte_s"]

        # C10: Aceleración total en régimen
        res_c10 = LatheKinematics.calc_10_aceleracion_total(at_c2, an_c2)
        atot_c10 = res_c10["a_tot_m_s2"]

        # C11: Fuerza de desbalance
        res_c11 = LatheKinetics.calc_11_fuerza_desbalance(params.mu, params.e_desbalance, omega_nom)
        Fu_c11 = res_c11["F_u_N"]

        # C12: Trabajo para partícula de 1 g (0.001 kg)
        res_c12 = LatheKinetics.calc_12_trabajo_energia_particula(0.001, v_c1)
        U_c12 = res_c12["U_1_2_J"]

        # C13: Potencia total de corte y pérdidas
        res_c13 = LatheKinetics.calc_13_potencias_y_eficiencia(params.Fc, vc_c5, b_viscoso, omega_nom)
        P_tot_c13 = res_c13["P_total_W"]

        # C14: Impulso angular de arranque
        res_c14 = LatheKinetics.calc_14_impulso_angular(I_tot, omega_nom, params.dt_arranque)
        DeltaH_c14 = res_c14["Delta_H_O_Nms"]

        # C15: Reacción inercial por viruta
        res_c15 = LatheKinetics.calc_15_transporte_momento_viruta(
            params.rho_pieza, params.bw, params.tc, vc_c5, params.u_viruta
        )
        Freac_c15 = res_c15["F_reac_N"]

        # C16: Inercia compuesta total
        res_c16 = LatheKinetics.calc_16_inercia_compuesta(
            params.m_pieza, params.R0, params.m_plato, params.R_plato
        )
        Itot_c16 = res_c16["I_tot_kgm2"]

        # C17: Coeficiente de amortiguamiento viscoso
        res_c17 = LatheMotorRundown.calc_17_perdidas_viscosas_arranque(
            params.dt_parada, I_tot, omega_nom, params.dt_arranque
        )
        b_c17 = res_c17["b_viscoso_Nms"]

        # C18: Vueltas remanentes en parada libre
        res_c18 = LatheMotorRundown.calc_18_rundown_remanente(
            omega_nom, params.tau_stop, b_c17
        )
        N_inf_c18 = res_c18["N_inf_rev"]

        # C19: Esfuerzo cortante máximo con chavetero
        res_c19 = LatheMechanics.calc_19_torsion_eje_chaveta(
            params.M_torsion_diseno, params.d_eje, params.L_eje,
            params.b_chaveta, params.h_chaveta, params.l_chaveta,
            params.Kt_chaveta, params.G_acero
        )
        taumax_c19 = res_c19["tau_max_MPa"]

        # C20: Fuerza manual en volante del contrapunto
        res_c20 = LatheMechanics.calc_20_mecanica_contrapunto(
            params.F0_cp, params.k_cp, params.x_cp,
            params.p_cp, params.r_volante
        )
        Fmano_c20 = res_c20["F_mano_N"]

        sim_map = {
            1: v_c1,
            2: an_c2,
            3: theta_c3,
            4: s_c4,
            5: vc_c5,
            6: s_c6_pct,
            7: v30_c7,
            8: v_rel_c8,
            9: t_corte_c9,
            10: atot_c10,
            11: Fu_c11,
            12: U_c12,
            13: P_tot_c13,
            14: DeltaH_c14,
            15: Freac_c15,
            16: Itot_c16,
            17: b_c17,
            18: N_inf_c18,
            19: taumax_c19,
            20: Fmano_c20
        }

        for bm in AVANCE2_BENCHMARK_LIST:
            v_sim = sim_map[bm.num]
            v_ana = bm.valor_analitico
            err_abs = abs(v_sim - v_ana)
            err_rel = (err_abs / abs(v_ana) * 100.0) if v_ana != 0 else 0.0
            aprobado = err_rel <= bm.tolerancia_pct

            rows.append(ValidationRow(
                calc_num=bm.num,
                titulo=bm.titulo,
                unidad_tematica=bm.unidad_tematica,
                variable_simbolo=bm.variable_simbolo,
                variable_nombre=bm.variable_nombre,
                ecuacion_latex=bm.ecuacion_latex,
                valor_analitico=v_ana,
                valor_simulado=v_sim,
                error_absoluto=err_abs,
                error_relativo_pct=err_rel,
                tolerancia_pct=bm.tolerancia_pct,
                unidad_si=bm.unidad_si,
                aprobado=aprobado,
                descripcion=bm.descripcion,
                ecuacion_compilada=getattr(bm, 'ecuacion_compilada', ""),
                variable_html=getattr(bm, 'variable_html', bm.variable_simbolo)
            ))

        return rows
