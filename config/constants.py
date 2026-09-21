"""
Constantes físicas, parámetros del Caso Avance 2 y tolerancias numéricas.
Asignatura: Dinámica - FICM - UTA
Tema: Cálculos Dinámicos de un Torno Didáctico para Madera
"""

# ==============================================================================
# PARÁMETROS OFICIALES: CASO BASE AVANCE 2
# ==============================================================================

# Motor Eléctrico Monofásico de Inducción
MOTOR_POTENCIA_NOM_CV = 1.0          # CV
MOTOR_POTENCIA_NOM_W = 735.5         # W (0.7355 kW)
MOTOR_VOLTAJE_V = 127.0              # V
MOTOR_FRECUENCIA_HZ = 60.0           # Hz
MOTOR_CORRIENTE_A = 5.0              # A
MOTOR_COS_PHI = 0.80                 # Factor de potencia
MOTOR_POLOS = 4                      # Número de polos magnéticos
MOTOR_RPM_NOMINAL = 1700.0           # rpm

# Pieza de Madera Cilíndrica (Pino radiata)
PIEZA_RADIO_NOMINAL_M = 0.040        # m (40 mm)
PIEZA_DIAMETRO_NOMINAL_M = 0.080     # m (80 mm)
PIEZA_LONGITUD_M = 0.250             # m (250 mm)
PIEZA_DENSIDAD_KG_M3 = 500.0         # kg/m^3

# Plato de Arrastre Metálico (Acero AISI 1018)
PLATO_MASA_KG = 0.46170              # kg
PLATO_RADIO_M = 0.055                # m (55 mm)

# Eje del Husillo y Chaveta
EJE_DIAMETRO_M = 0.019               # m (19 mm)
EJE_LONGITUD_M = 0.040               # m (40 mm)
ACERO_MODULO_G_PA = 79.0e9           # Pa (79 GPa)
CHAVETA_ANCHO_M = 0.006              # m (6 mm)
CHAVETA_ALTURA_M = 0.006             # m (6 mm)
CHAVETA_LONGITUD_M = 0.025           # m (25 mm)
FACTOR_ENTALLADURA_KT = 1.6          # Adimensional

# Proceso de Torneado / Mecanizado
CORTE_FUERZA_FC_N = 20.0             # N
CORTE_AVANCE_RADIAL_M_REV = 2.5e-6   # m/rev (2.5 um/rev)
CORTE_ESPESOR_TC_M = 0.0005          # m (0.5 mm)
CORTE_ANCHO_BW_M = 0.005             # m (5.0 mm)
VIRUTA_VEL_EYECCION_U_M_S = 6.0      # m/s

# Tiempos Transitorios de Operación
TIEMPO_ARRANQUE_S = 2.0              # s
TIEMPO_PARADA_LIBRE_S = 3.0          # s (run-down al 1% de omega)

# Contrapunto de Sujeción Axial
CONTRAPUNTO_F0_N = 500.0             # N (precarga de centrado)
CONTRAPUNTO_RIGIDEZ_K_N_M = 5.0e4    # N/m
CONTRAPUNTO_AVANCE_X_M = 0.0015      # m (1.5 mm)
CONTRAPUNTO_PASO_P_M_REV = 0.002     # m/rev (2.0 mm/rev)
CONTRAPUNTO_RADIO_VOLANTE_M = 0.060  # m (60 mm)

# Desbalance Dinámico Residual
DESBALANCE_MASA_MU_KG = 0.020        # kg (20 g)
DESBALANCE_EXCENTRICIDAD_E_M = 0.002 # m (2 mm)

# Aliases y constantes calculadas
import math
MOTOR_POTENCIA_NOMINAL_W = MOTOR_POTENCIA_NOM_W
MOTOR_VELOCIDAD_NOMINAL_RPM = MOTOR_RPM_NOMINAL
MOTOR_VELOCIDAD_NOMINAL_RAD_S = MOTOR_RPM_NOMINAL * 2.0 * math.pi / 60.0
CORTE_FUERZA_TANGENCIAL_N = CORTE_FUERZA_FC_N
DESBALANCE_FUERZA_NOMINAL_N = DESBALANCE_MASA_MU_KG * DESBALANCE_EXCENTRICIDAD_E_M * (MOTOR_VELOCIDAD_NOMINAL_RAD_S ** 2)


# ==============================================================================
# COLORES Y VISUALIZACIÓN DE VECTORES TÉCNICOS
# ==============================================================================
COLOR_VELOCIDAD = (0.85, 0.33, 0.10, 1.0)       # Naranja técnico
COLOR_ACEL_TANG = (0.00, 0.60, 0.20, 1.0)       # Verde esmeralda
COLOR_ACEL_NORM = (0.85, 0.20, 0.20, 1.0)       # Rojo bermellón
COLOR_ACEL_TOTAL = (0.55, 0.20, 0.65, 1.0)      # Púrpura inercial
COLOR_DESBALANCE = (0.90, 0.15, 0.15, 1.0)      # Rojo vibración
COLOR_CORTE = (0.10, 0.50, 0.85, 1.0)           # Azul cobalto
COLOR_VIRUTA = (0.95, 0.75, 0.30, 0.9)          # Dorado madera
COLOR_EJE_ROTACION = (0.40, 0.40, 0.40, 0.7)    # Gris eje

# ==============================================================================
# TOLERANCIAS PARA VALIDACIÓN
# ==============================================================================
TOLERANCIA_ERROR_RELATIVO_PCT = 0.10  # 0.10% para tolerar redondeos del informe
