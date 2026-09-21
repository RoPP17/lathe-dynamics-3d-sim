"""
Modelos de datos y estado físico del torno.
Fuente única de verdad matemática - Asignatura Dinámica.
"""

from dataclasses import dataclass, field
import math
from config.constants import (
    MOTOR_POTENCIA_NOM_W, MOTOR_RPM_NOMINAL, MOTOR_FRECUENCIA_HZ, MOTOR_POLOS,
    PIEZA_RADIO_NOMINAL_M, PIEZA_LONGITUD_M, PIEZA_DENSIDAD_KG_M3,
    PLATO_MASA_KG, PLATO_RADIO_M,
    EJE_DIAMETRO_M, EJE_LONGITUD_M, ACERO_MODULO_G_PA,
    CHAVETA_ANCHO_M, CHAVETA_ALTURA_M, CHAVETA_LONGITUD_M, FACTOR_ENTALLADURA_KT,
    CORTE_FUERZA_FC_N, CORTE_AVANCE_RADIAL_M_REV, CORTE_ESPESOR_TC_M, CORTE_ANCHO_BW_M,
    VIRUTA_VEL_EYECCION_U_M_S, TIEMPO_ARRANQUE_S, TIEMPO_PARADA_LIBRE_S,
    CONTRAPUNTO_F0_N, CONTRAPUNTO_RIGIDEZ_K_N_M, CONTRAPUNTO_AVANCE_X_M,
    CONTRAPUNTO_PASO_P_M_REV, CONTRAPUNTO_RADIO_VOLANTE_M,
    DESBALANCE_MASA_MU_KG, DESBALANCE_EXCENTRICIDAD_E_M
)


@dataclass
class LatheParameters:
    """Parámetros físicos y operativos del torno."""
    # Motor
    P_nom: float = MOTOR_POTENCIA_NOM_W
    n_nom: float = MOTOR_RPM_NOMINAL
    freq: float = MOTOR_FRECUENCIA_HZ
    polos: int = MOTOR_POLOS

    # Pieza
    R0: float = PIEZA_RADIO_NOMINAL_M
    L_pieza: float = PIEZA_LONGITUD_M
    rho_pieza: float = PIEZA_DENSIDAD_KG_M3

    # Plato
    m_plato: float = PLATO_MASA_KG
    R_plato: float = PLATO_RADIO_M

    # Eje y chaveta
    d_eje: float = EJE_DIAMETRO_M
    L_eje: float = EJE_LONGITUD_M
    G_acero: float = ACERO_MODULO_G_PA
    b_chaveta: float = CHAVETA_ANCHO_M
    h_chaveta: float = CHAVETA_ALTURA_M
    l_chaveta: float = CHAVETA_LONGITUD_M
    Kt_chaveta: float = FACTOR_ENTALLADURA_KT
    M_torsion_diseno: float = 0.800  # N*m

    # Corte y viruta
    Fc: float = CORTE_FUERZA_FC_N
    fr: float = CORTE_AVANCE_RADIAL_M_REV
    tc: float = CORTE_ESPESOR_TC_M
    bw: float = CORTE_ANCHO_BW_M
    u_viruta: float = VIRUTA_VEL_EYECCION_U_M_S

    # Transitorios
    dt_arranque: float = TIEMPO_ARRANQUE_S
    dt_parada: float = TIEMPO_PARADA_LIBRE_S

    # Contrapunto
    F0_cp: float = CONTRAPUNTO_F0_N
    k_cp: float = CONTRAPUNTO_RIGIDEZ_K_N_M
    x_cp: float = CONTRAPUNTO_AVANCE_X_M
    p_cp: float = CONTRAPUNTO_PASO_P_M_REV
    r_volante: float = CONTRAPUNTO_RADIO_VOLANTE_M

    # Desbalance
    mu: float = DESBALANCE_MASA_MU_KG
    e_desbalance: float = DESBALANCE_EXCENTRICIDAD_E_M

    # --------------------------------------------------------------------------
    # Magnitudes Derivadas Base (Ecuaciones 1 a 6 de la sección Parámetros del Informe)
    # --------------------------------------------------------------------------
    @property
    def omega_nom(self) -> float:
        """Velocidad angular nominal: omega = 2*pi*n / 60 [rad/s]"""
        return 2.0 * math.pi * self.n_nom / 60.0

    @property
    def V_cil(self) -> float:
        """Volumen inicial de la pieza cilíndrica: pi*R^2*L [m^3]"""
        return math.pi * (self.R0 ** 2) * self.L_pieza

    @property
    def m_pieza(self) -> float:
        """Masa inicial de la pieza: rho * V_cil [kg]"""
        return self.rho_pieza * self.V_cil

    @property
    def I_pieza(self) -> float:
        """Momento de inercia de la pieza: 0.5 * m * R^2 [kg*m^2]"""
        return 0.5 * self.m_pieza * (self.R0 ** 2)

    @property
    def I_plato(self) -> float:
        """Momento de inercia del plato: 0.5 * m_p * R_p^2 [kg*m^2]"""
        return 0.5 * self.m_plato * (self.R_plato ** 2)

    @property
    def I_tot(self) -> float:
        """Momento de inercia total equivalente: I_pieza + I_plato [kg*m^2]"""
        return self.I_pieza + self.I_plato

    @property
    def tau_arranque(self) -> float:
        """Constante de tiempo de arranque al 95%: dt / ln(20) [s]"""
        return self.dt_arranque / math.log(20.0)

    @property
    def tau_stop(self) -> float:
        """Constante de tiempo de parada al 1%: dt_stop / ln(100) [s]"""
        return self.dt_parada / math.log(100.0)

    @property
    def b_viscoso(self) -> float:
        """Coeficiente de amortiguamiento viscoso torsional: I_tot / tau_stop [N*m*s]"""
        return self.I_tot / self.tau_stop

    def copy(self) -> 'LatheParameters':
        """Crea una copia independiente de los parámetros."""
        import copy
        return copy.deepcopy(self)


@dataclass
class DynamicState:
    """Estado dinámico instantáneo del torno a un tiempo t."""
    t: float = 0.0                     # s
    fase: str = "ARRANQUE"             # 'ARRANQUE', 'REGIMEN', 'TORNEADO', 'DESBALANCE', 'PARADA'

    # Cinemática angular
    omega: float = 0.0                 # rad/s
    rpm: float = 0.0                   # rev/min
    alpha: float = 0.0                 # rad/s^2
    theta: float = 0.0                 # rad
    rev: float = 0.0                   # rev

    # Geometría actual
    R_actual: float = 0.040            # m
    D_actual: float = 0.080            # m

    # Cinemática puntual y periférica
    v_perif: float = 0.0               # m/s
    v_corte: float = 0.0               # m/s
    a_t: float = 0.0                   # m/s^2
    a_n: float = 0.0                   # m/s^2
    a_total: float = 0.0               # m/s^2
    beta_deg: float = 0.0              # grados
    s_arco: float = 0.0                # m

    # Cinética y fuerzas
    F_desbalance: float = 0.0          # N (magnitud)
    F_desbalance_x: float = 0.0        # N
    F_desbalance_y: float = 0.0        # N
    F_corte_actual: float = 0.0        # N
    m_dot_viruta: float = 0.0          # kg/s
    F_reac_viruta: float = 0.0         # N

    # Potencias y energía
    P_corte: float = 0.0               # W
    P_loss: float = 0.0                # W
    P_total: float = 0.0               # W
    eficiencia_pct: float = 0.0        # %
    H_O: float = 0.0                   # N*m*s (momento angular)
    E_cinetica_rot: float = 0.0        # J
