"""
Renderizador de Vectores Dinámicos 3D en OpenGL.
Flechas compuestas por vástago cilíndrico y cabeza cónica con orientación espacial 3D.
"""

import math
from OpenGL.GL import *
from OpenGL.GLU import *
from typing import Tuple


def draw_3d_arrow(origin: Tuple[float, float, float],
                  direction: Tuple[float, float, float],
                  magnitude_visual: float,
                  color: Tuple[float, float, float, float],
                  shaft_radius: float = 0.002,
                  head_radius: float = 0.005,
                  head_ratio: float = 0.25):
    """
    Dibuja una flecha 3D orientada desde 'origin' en la dirección 'direction'
    con longitud visual 'magnitude_visual'.
    """
    if magnitude_visual < 1e-6:
        return

    dx, dy, dz = direction
    norm = math.sqrt(dx * dx + dy * dy + dz * dz)
    if norm < 1e-6:
        return
    dx /= norm
    dy /= norm
    dz /= norm

    head_len = min(magnitude_visual * head_ratio, 0.025)
    shaft_len = magnitude_visual - head_len

    glPushMatrix()
    glTranslatef(origin[0], origin[1], origin[2])

    # Rotación desde el eje +Z predeterminado de gluCylinder hacia (dx, dy, dz)
    # Vector z_axis = (0, 0, 1)
    # Eje de rotación = cross(z_axis, dir) = (-dy, dx, 0)
    dot = dz  # dot product with (0,0,1)
    dot = max(-1.0, min(1.0, dot))
    ang_deg = math.degrees(math.acos(dot))

    rot_x = -dy
    rot_y = dx
    rot_z = 0.0
    rot_norm = math.sqrt(rot_x * rot_x + rot_y * rot_y)

    if rot_norm > 1e-6:
        rot_x /= rot_norm
        rot_y /= rot_norm
        glRotatef(ang_deg, rot_x, rot_y, rot_z)
    elif dz < 0.0:
        glRotatef(180.0, 1.0, 0.0, 0.0)

    # Color del vector con material difuso y especular
    glColor4fv(color)
    glMaterialfv(GL_FRONT_AND_BACK, GL_AMBIENT_AND_DIFFUSE, color)

    quad = gluNewQuadric()
    # 1. Vástago cilíndrico
    if shaft_len > 0:
        gluCylinder(quad, shaft_radius, shaft_radius, shaft_len, 16, 2)

    # 2. Cabeza cónica
    glTranslatef(0.0, 0.0, shaft_len)
    gluCylinder(quad, head_radius, 0.0, head_len, 16, 2)

    # Tapa de la base del cono
    gluDisk(quad, 0.0, head_radius, 16, 2)

    gluDeleteQuadric(quad)
    glPopMatrix()


class DynamicVectorRenderer:
    """Gestiona el cálculo de escala, posición y renderizado de los vectores físicos del torno."""

    def __init__(self):
        # Factores de escala visual para mantener proporciones estéticas y legibles
        self.scale_vel = 0.008          # 7.12 m/s -> ~0.057 m (57 mm)
        self.scale_at = 0.010           # 3.56 m/s^2 -> ~0.035 m (35 mm)
        self.scale_an = 0.000045        # 1267.7 m/s^2 -> ~0.057 m (57 mm)
        self.scale_atot = 0.000045      # ~0.057 m
        self.scale_Fu = 0.035           # 1.27 N -> ~0.044 m (44 mm)
        self.scale_Fc = 0.0025          # 20 N -> ~0.050 m (50 mm)
        self.scale_Freac = 0.40         # 0.053 N -> ~0.021 m (21 mm)

    def render_vectors(self, state, vis_flags: dict):
        """
        Dibuja los vectores habilitados en el instante actual.
        vis_flags: diccionario de booleanos {'velocidad': True, 'acel_norm': True, ...}
        """
        theta = state.theta
        R = state.R_actual
        x_pos = 0.125  # Punto de evaluación periférico en la mitad de la pieza

        # Punto periférico P sobre la superficie de la madera que rota con theta
        py = R * math.cos(theta)
        pz = R * math.sin(theta)
        punto_P = (x_pos, py, pz)

        # ----------------------------------------------------------------------
        # 1. Vector Velocidad Tangencial v (Cálculo 1)
        # Dirección tangencial u_theta = (-sin(theta), cos(theta)) en el plano Y-Z
        # ----------------------------------------------------------------------
        if vis_flags.get("velocidad", True) and state.v_perif > 0.01:
            dir_v = (0.0, -math.sin(theta), math.cos(theta))
            len_v = min(state.v_perif * self.scale_vel, 0.080)
            color_v = (0.95, 0.45, 0.10, 1.0) # Naranja
            draw_3d_arrow(punto_P, dir_v, len_v, color_v, shaft_radius=0.0022, head_radius=0.0055)

        # ----------------------------------------------------------------------
        # 2. Vector Aceleración Tangencial a_t (Cálculo 2)
        # Dirección tangencial u_t (paralela a v cuando acelera, opuesta al frenar)
        # ----------------------------------------------------------------------
        if vis_flags.get("acel_tang", True) and abs(state.a_t) > 0.01:
            sign_at = 1.0 if state.a_t >= 0 else -1.0
            dir_at = (0.0, -sign_at * math.sin(theta), sign_at * math.cos(theta))
            len_at = min(abs(state.a_t) * self.scale_at, 0.065)
            color_at = (0.10, 0.75, 0.25, 1.0) # Verde esmeralda
            draw_3d_arrow(punto_P, dir_at, len_at, color_at, shaft_radius=0.0020, head_radius=0.0050)

        # ----------------------------------------------------------------------
        # 3. Vector Aceleración Normal Centrípeta a_n (Cálculo 2)
        # Dirección centrípeta radial hacia el eje central (0, 0, 0)
        # ----------------------------------------------------------------------
        if vis_flags.get("acel_norm", True) and state.a_n > 0.5:
            dir_an = (0.0, -math.cos(theta), -math.sin(theta))
            len_an = min(state.a_n * self.scale_an, 0.075)
            color_an = (0.90, 0.15, 0.15, 1.0) # Rojo bermellón
            draw_3d_arrow(punto_P, dir_an, len_an, color_an, shaft_radius=0.0022, head_radius=0.0055)

        # ----------------------------------------------------------------------
        # 4. Vector Aceleración Total Resultante a_tot (Cálculo 10)
        # Suma vectorial a_t * u_t + a_n * u_n
        # ----------------------------------------------------------------------
        if vis_flags.get("acel_total", False) and state.a_total > 0.5:
            # Componentes en Y y Z
            sign_at = 1.0 if state.a_t >= 0 else -1.0
            ay = -state.a_n * math.cos(theta) - state.a_t * math.sin(theta)
            az = -state.a_n * math.sin(theta) + state.a_t * math.cos(theta)
            len_tot = min(state.a_total * self.scale_atot, 0.080)
            color_tot = (0.65, 0.20, 0.85, 1.0) # Púrpura
            draw_3d_arrow(punto_P, (0.0, ay, az), len_tot, color_tot, shaft_radius=0.0024, head_radius=0.0060)

        # ----------------------------------------------------------------------
        # 5. Vector Fuerza Centrífuga por Desbalance F_u (Cálculo 11)
        # Rota solidario con el rotor desde el centro de masa excéntrico
        # ----------------------------------------------------------------------
        if vis_flags.get("desbalance", True) and state.F_desbalance > 0.01:
            e_vis = max(state.R_actual * 0.35, 0.012)
            pos_ecc = (x_pos, e_vis * math.cos(theta), e_vis * math.sin(theta))
            dir_Fu = (0.0, math.cos(theta), math.sin(theta)) # Radialmente hacia afuera
            len_Fu = min(state.F_desbalance * self.scale_Fu, 0.070)
            color_Fu = (1.0, 0.05, 0.05, 1.0) # Rojo intenso
            draw_3d_arrow(pos_ecc, dir_Fu, len_Fu, color_Fu, shaft_radius=0.0026, head_radius=0.0065)

        # ----------------------------------------------------------------------
        # 6. Vector Fuerza de Corte F_c (Cálculo 13)
        # Tangencial en el punto de contacto herramienta-pieza (y=0, z=R)
        # ----------------------------------------------------------------------
        if vis_flags.get("corte", True) and state.F_corte_actual > 0.1:
            pto_corte = (0.120, 0.0, R)
            # La fuerza de corte se opone a la rotación de la pieza (hacia abajo en -Y)
            dir_Fc = (0.0, -1.0, 0.0)
            len_Fc = min(state.F_corte_actual * self.scale_Fc, 0.060)
            color_Fc = (0.05, 0.55, 0.95, 1.0) # Azul cobalto
            draw_3d_arrow(pto_corte, dir_Fc, len_Fc, color_Fc, shaft_radius=0.0024, head_radius=0.0060)

        # ----------------------------------------------------------------------
        # 7. Vector Reacción Inercial de Viruta F_reac (Cálculo 15)
        # ----------------------------------------------------------------------
        if vis_flags.get("viruta", True) and state.F_reac_viruta > 0.001:
            pto_corte = (0.120, 0.0, R)
            # Reacción inercial sobre la gubia (hacia afuera y abajo)
            dir_Freac = (0.0, -0.7, 0.7)
            len_Freac = min(state.F_reac_viruta * self.scale_Freac, 0.045)
            color_Freac = (0.95, 0.80, 0.20, 1.0) # Dorado viruta
            draw_3d_arrow(pto_corte, dir_Freac, len_Freac, color_Freac, shaft_radius=0.0018, head_radius=0.0045)
