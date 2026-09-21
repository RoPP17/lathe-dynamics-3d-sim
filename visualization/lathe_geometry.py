"""
Geometría 3D Técnica de Alta Precisión del Torno Didáctico para Madera.
Ensamble mecánico completo: bancada con costillas de refuerzo, cabezal motriz con
aletas de refrigeración y botonera, husillo de arrastre, plato de 4 mordazas con ranuras,
pieza de madera de pino con anillos de crecimiento y zona de corte maquinada,
contrapunto con caña graduada milimétricamente y volantes, banquillo y gubia HSS.
"""

import math
from OpenGL.GL import *
from OpenGL.GLU import *
from config.constants import (
    PIEZA_RADIO_NOMINAL_M, PIEZA_LONGITUD_M, PLATO_RADIO_M,
    EJE_DIAMETRO_M, CONTRAPUNTO_RADIO_VOLANTE_M
)


def draw_cylinder_x(radius: float, length: float, slices: int = 32,
                    caps: bool = True, color_body=(0.7, 0.7, 0.7),
                    color_caps=(0.6, 0.6, 0.6)):
    """
    Dibuja un cilindro orientado a lo largo del eje X (eje de rotación del torno).
    Desde x = 0 hasta x = length.
    """
    glColor3fv(color_body)
    glBegin(GL_QUAD_STRIP)
    for i in range(slices + 1):
        angle = 2.0 * math.pi * i / slices
        cy = radius * math.cos(angle)
        cz = radius * math.sin(angle)
        glNormal3f(0.0, math.cos(angle), math.sin(angle))
        glVertex3f(0.0, cy, cz)
        glVertex3f(length, cy, cz)
    glEnd()

    if caps:
        glColor3fv(color_caps)
        # Tapa en x = 0 (normal hacia -X)
        glBegin(GL_TRIANGLE_FAN)
        glNormal3f(-1.0, 0.0, 0.0)
        glVertex3f(0.0, 0.0, 0.0)
        for i in range(slices + 1):
            angle = -2.0 * math.pi * i / slices
            glVertex3f(0.0, radius * math.cos(angle), radius * math.sin(angle))
        glEnd()

        # Tapa en x = length (normal hacia +X)
        glBegin(GL_TRIANGLE_FAN)
        glNormal3f(1.0, 0.0, 0.0)
        glVertex3f(length, 0.0, 0.0)
        for i in range(slices + 1):
            angle = 2.0 * math.pi * i / slices
            glVertex3f(length, radius * math.cos(angle), radius * math.sin(angle))
        glEnd()


def draw_box(x_min, x_max, y_min, y_max, z_min, z_max, color=(0.5, 0.5, 0.5)):
    """Dibuja un prisma rectangular alineado con los ejes coordenados."""
    glColor3fv(color)
    glBegin(GL_QUADS)
    # Frontal (+Z)
    glNormal3f(0.0, 0.0, 1.0)
    glVertex3f(x_min, y_min, z_max); glVertex3f(x_max, y_min, z_max)
    glVertex3f(x_max, y_max, z_max); glVertex3f(x_min, y_max, z_max)
    # Trasera (-Z)
    glNormal3f(0.0, 0.0, -1.0)
    glVertex3f(x_min, y_min, z_min); glVertex3f(x_min, y_max, z_min)
    glVertex3f(x_max, y_max, z_min); glVertex3f(x_max, y_min, z_min)
    # Superior (+Y)
    glNormal3f(0.0, 1.0, 0.0)
    glVertex3f(x_min, y_max, z_min); glVertex3f(x_min, y_max, z_max)
    glVertex3f(x_max, y_max, z_max); glVertex3f(x_max, y_max, z_min)
    # Inferior (-Y)
    glNormal3f(0.0, -1.0, 0.0)
    glVertex3f(x_min, y_min, z_min); glVertex3f(x_max, y_min, z_min)
    glVertex3f(x_max, y_min, z_max); glVertex3f(x_min, y_min, z_max)
    # Izquierda (-X)
    glNormal3f(-1.0, 0.0, 0.0)
    glVertex3f(x_min, y_min, z_min); glVertex3f(x_min, y_min, z_max)
    glVertex3f(x_min, y_max, z_max); glVertex3f(x_min, y_max, z_min)
    # Derecha (+X)
    glNormal3f(1.0, 0.0, 0.0)
    glVertex3f(x_max, y_min, z_min); glVertex3f(x_max, y_max, z_min)
    glVertex3f(x_max, y_max, z_max); glVertex3f(x_max, y_min, z_max)
    glEnd()


class Lathe3DModel:
    """Modelo 3D mecánico y paramétrico de alta fidelidad del torno de madera."""

    def __init__(self):
        # Escala: 1 unidad OpenGL = 1 metro
        # Origen (0,0,0) en la cara de contacto plato-madera sobre el eje del husillo.
        self.L_madera = PIEZA_LONGITUD_M        # 0.25 m (250 mm)
        self.R_madera = PIEZA_RADIO_NOMINAL_M   # 0.040 m (40 mm)
        self.R_plato = PLATO_RADIO_M            # 0.055 m (55 mm)
        self.espesor_plato = 0.018              # 18 mm
        self.d_eje = EJE_DIAMETRO_M             # 0.019 m (19 mm)
        self.r_volante = CONTRAPUNTO_RADIO_VOLANTE_M # 0.060 m (60 mm)

    def render(self, theta_rad: float, R_actual_m: float,
               desbalance_activo: bool = False,
               e_desbalance_m: float = 0.002,
               tool_engaged: bool = False,
               avance_contrapunto_m: float = 0.0015,
               is_rotating: bool = True):
        """
        Dibuja todos los componentes ensamblados del torno.
        theta_rad: ángulo de rotación instantáneo del husillo y la pieza.
        R_actual_m: radio actual de la madera (disminuye durante el desbaste).
        is_rotating: indica si el husillo tiene velocidad angular > 0.
        """
        # 1. Bancada estructural con guías prismáticas, costillas y tacones
        self._render_bed()

        # 2. Cabezal fijo con carcasa de motor, aletas y botonera industrial
        self._render_headstock(is_rotating)

        # 3. Conjunto rotatorio (Husillo + Plato 4 Mordazas + Madera + Desbalance)
        glPushMatrix()
        glRotatef(math.degrees(theta_rad), 1.0, 0.0, 0.0)

        # 3.1 Eje de acero rectificado del husillo (x = -0.060 a x = -0.018 m)
        glPushMatrix()
        glTranslatef(-0.060, 0.0, 0.0)
        draw_cylinder_x(self.d_eje / 2.0, 0.045, slices=24,
                        color_body=(0.78, 0.80, 0.84), color_caps=(0.65, 0.68, 0.72))
        glPopMatrix()

        # 3.2 Plato de 4 mordazas metálico con estrías
        glPushMatrix()
        glTranslatef(-self.espesor_plato, 0.0, 0.0)
        draw_cylinder_x(self.R_plato, self.espesor_plato, slices=36,
                        color_body=(0.38, 0.40, 0.45), color_caps=(0.50, 0.52, 0.56))
        self._render_chuck_details()
        glPopMatrix()

        # 3.3 Pieza cilíndrica de madera con anillos de crecimiento y ranura maquinada
        self._render_wood_workpiece(R_actual_m, tool_engaged)

        # 3.4 Masa de desbalance excéntrica (mu = 20 g)
        if desbalance_activo:
            self._render_unbalance_mass(e_desbalance_m, R_actual_m)

        glPopMatrix()

        # 4. Contrapunto móvil con caña graduada, volante y cono morse
        self._render_tailstock(avance_contrapunto_m)

        # 5. Banquillo portaherramientas y gubia de desbaste HSS
        self._render_tool_rest(R_actual_m, tool_engaged)

        # 6. Eje de referencia de simetría de rotación
        self._render_rotation_axis()

    def _render_bed(self):
        """Dibuja la bancada de fundición gris con costillas de rigidez torsional y guías rectificadas."""
        x_min, x_max = -0.15, 0.45
        y_bed = -0.090
        h_bed = 0.045
        w_bed = 0.140

        # Bloque base principal de fundición (Gris oscuro fundición)
        draw_box(x_min, x_max, y_bed - h_bed, y_bed, -w_bed / 2.0, w_bed / 2.0,
                 color=(0.20, 0.22, 0.25))

        # Costillas transversales de refuerzo de la bancada (Rigidización torsional - Avance 2)
        rib_xs = [ -0.05, 0.05, 0.15, 0.25, 0.35 ]
        for rx in rib_xs:
            draw_box(rx - 0.008, rx + 0.008, y_bed - h_bed + 0.005, y_bed - 0.005,
                     -w_bed / 2.0 + 0.006, w_bed / 2.0 - 0.006,
                     color=(0.16, 0.17, 0.19))

        # Guías prismáticas rectificadas dobles (Gris claro acero rectificado)
        g_w = 0.024
        g_h = 0.009
        z_offset = 0.040
        draw_box(x_min, x_max, y_bed, y_bed + g_h, -z_offset - g_w / 2.0, -z_offset + g_w / 2.0,
                 color=(0.68, 0.70, 0.74))
        draw_box(x_min, x_max, y_bed, y_bed + g_h, z_offset - g_w / 2.0, z_offset + g_w / 2.0,
                 color=(0.68, 0.70, 0.74))

        # Ranura central en T para guiado y fijación de carros
        draw_box(x_min, x_max, y_bed - 0.012, y_bed, -0.014, 0.014,
                 color=(0.14, 0.15, 0.16))

        # Patas de soporte con tacones antivibratorios de elastómero
        for px in [x_min, x_max - 0.045]:
            # Pata metálica
            draw_box(px, px + 0.045, y_bed - h_bed - 0.055, y_bed - h_bed,
                     -w_bed / 2.0, w_bed / 2.0, color=(0.18, 0.19, 0.22))
            # Tacón de goma negra en la base
            draw_box(px - 0.003, px + 0.048, y_bed - h_bed - 0.065, y_bed - h_bed - 0.055,
                     -w_bed / 2.0 - 0.004, w_bed / 2.0 + 0.004, color=(0.08, 0.08, 0.09))

    def _render_headstock(self, is_rotating: bool):
        """Dibuja el cabezal motriz fijo, motor de 1 CV con aletas disipadoras y botonera de mando."""
        # Carcasa principal del cabezal fijo (Azul martillado industrial)
        draw_box(-0.145, -0.040, -0.090, 0.075, -0.068, 0.068,
                 color=(0.17, 0.29, 0.42))

        # Tapa de rodamientos del husillo frontal
        glPushMatrix()
        glTranslatef(-0.040, 0.0, 0.0)
        draw_cylinder_x(0.028, 0.010, slices=24,
                        color_body=(0.45, 0.48, 0.52), color_caps=(0.50, 0.53, 0.58))
        glPopMatrix()

        # Motor de inducción monofásico (P = 735.5 W / 1 CV) en la parte trasera
        glPushMatrix()
        glTranslatef(-0.100, -0.015, -0.115)
        # Cuerpo cilíndrico del motor
        draw_cylinder_x(0.058, 0.115, slices=24,
                        color_body=(0.13, 0.15, 0.18), color_caps=(0.22, 0.24, 0.27))

        # Aletas de refrigeración del motor
        for fx in range(6):
            draw_box(0.015 + fx * 0.016, 0.018 + fx * 0.016, -0.063, 0.063, -0.063, 0.063,
                     color=(0.10, 0.12, 0.14))
        glPopMatrix()

        # Botonera industrial de control (Start / Stop) con luz piloto
        draw_box(-0.135, -0.075, 0.010, 0.060, 0.069, 0.082,
                 color=(0.22, 0.24, 0.26))
        # Botón verde Start
        draw_box(-0.125, -0.105, 0.035, 0.052, 0.082, 0.086,
                 color=(0.0, 0.85, 0.3) if is_rotating else (0.0, 0.45, 0.15))
        # Botón rojo Stop
        draw_box(-0.098, -0.082, 0.035, 0.052, 0.082, 0.086,
                 color=(0.5, 0.1, 0.1) if is_rotating else (0.9, 0.15, 0.15))
        # Testigo luminoso LED de estado
        led_col = (0.0, 1.0, 0.4) if is_rotating else (1.0, 0.2, 0.1)
        draw_box(-0.110, -0.095, 0.016, 0.026, 0.082, 0.086, color=led_col)

    def _render_chuck_details(self):
        """Dibuja detalles realistas del plato de 4 mordazas: guías radiales, mordazas y prongs."""
        # Ranuras en cruz y mordazas escalonadas
        for ang_deg in [0, 90, 180, 270]:
            rad = math.radians(ang_deg)
            cos_a = math.cos(rad)
            sin_a = math.sin(rad)

            # Guía radial en el plato
            glDisable(GL_LIGHTING)
            glColor3f(0.18, 0.20, 0.22)
            glLineWidth(3.0)
            glBegin(GL_LINES)
            glVertex3f(self.espesor_plato + 0.0005, (self.d_eje / 2.0 + 0.002) * cos_a, (self.d_eje / 2.0 + 0.002) * sin_a)
            glVertex3f(self.espesor_plato + 0.0005, (self.R_plato - 0.004) * cos_a, (self.R_plato - 0.004) * sin_a)
            glEnd()
            glEnable(GL_LIGHTING)

            # Bloque de mordaza escalonada de acero templado
            r_mid = (self.d_eje / 2.0 + self.R_plato) / 2.0
            my = r_mid * cos_a
            mz = r_mid * sin_a
            glPushMatrix()
            glTranslatef(self.espesor_plato, my, mz)
            glRotatef(ang_deg, 1.0, 0.0, 0.0)
            draw_box(0.0, 0.008, -0.006, 0.006, -0.006, 0.006, color=(0.72, 0.74, 0.78))
            glPopMatrix()

        # Dientes centrales de arrastre tipo 'Spur Drive Center' que clavan en la madera
        glColor3f(0.85, 0.88, 0.92)
        glBegin(GL_TRIANGLES)
        for ang_deg in [45, 135, 225, 315]:
            rad = math.radians(ang_deg)
            cos_a = math.cos(rad)
            sin_a = math.sin(rad)
            r_p = 0.012
            # Prisma triangular que penetra en la madera
            glVertex3f(self.espesor_plato + 0.006, r_p * cos_a, r_p * sin_a)
            glVertex3f(self.espesor_plato, (r_p - 0.003) * cos_a, (r_p - 0.003) * sin_a)
            glVertex3f(self.espesor_plato, (r_p + 0.003) * cos_a, (r_p + 0.003) * sin_a)
        glEnd()

    def _render_wood_workpiece(self, R_actual_m: float, tool_engaged: bool):
        """Dibuja el cilindro de madera de pino con anillos de crecimiento y zona de corte rebajada."""
        color_wood = (0.83, 0.67, 0.46)       # Pino radiata natural
        color_cut_wood = (0.89, 0.76, 0.55)   # Madera recién torneada pulida
        color_endgrain = (0.76, 0.59, 0.39)   # Testa con anillos anuales

        # Si el radio disminuyó por mecanizado (Cálculo 9: desbaste de 1 mm),
        # modelamos la pieza con la zona rebajada entre x = 0.08 y x = 0.16 m
        x_c1, x_c2 = 0.080, 0.160
        r_nominal = self.R_madera

        if R_actual_m < r_nominal - 1e-4:
            # Sección 1: Sin tornear (x = 0 a 0.08)
            draw_cylinder_x(r_nominal, x_c1, slices=36, caps=False, color_body=color_wood)
            # Escalón de transición
            draw_cylinder_x(r_nominal, 0.002, slices=36, caps=False, color_body=(0.70, 0.55, 0.36))

            # Sección 2: Rebajada por la gubia (x = 0.08 a 0.16)
            glPushMatrix()
            glTranslatef(x_c1, 0.0, 0.0)
            draw_cylinder_x(R_actual_m, x_c2 - x_c1, slices=36, caps=False, color_body=color_cut_wood)
            glPopMatrix()

            # Sección 3: Sin tornear (x = 0.16 a L_madera)
            glPushMatrix()
            glTranslatef(x_c2, 0.0, 0.0)
            draw_cylinder_x(r_nominal, self.L_madera - x_c2, slices=36, caps=False, color_body=color_wood)
            glPopMatrix()
        else:
            # Cilindro completo uniforme
            draw_cylinder_x(r_nominal, self.L_madera, slices=36, caps=False, color_body=color_wood)

        # Tapas de testa con anillos de crecimiento concéntricos (End-grain annual growth rings)
        for x_face, normal_x in [(0.0001, -1.0), (self.L_madera - 0.0001, 1.0)]:
            glPushMatrix()
            glTranslatef(x_face, 0.0, 0.0)
            # Fondo de testa
            glColor3fv(color_endgrain)
            glBegin(GL_TRIANGLE_FAN)
            glNormal3f(normal_x, 0.0, 0.0)
            glVertex3f(0.0, 0.0, 0.0)
            for i in range(37):
                ang = 2.0 * math.pi * i / 36.0
                glVertex3f(0.0, r_nominal * math.cos(ang), r_nominal * math.sin(ang))
            glEnd()

            # Anillos concéntricos de duramen y albura
            glDisable(GL_LIGHTING)
            glLineWidth(1.2)
            for ring_r in [0.008, 0.016, 0.024, 0.032, 0.038]:
                glColor3f(0.60, 0.44, 0.28) # Marrón oscuro de anillos tardíos
                glBegin(GL_LINE_LOOP)
                for i in range(36):
                    ang = 2.0 * math.pi * i / 36.0
                    glVertex3f(0.0, ring_r * math.cos(ang), ring_r * math.sin(ang))
                glEnd()
            glEnable(GL_LIGHTING)
            glPopMatrix()

        # Vetas longitudinales de madera a lo largo del cilindro
        glDisable(GL_LIGHTING)
        glColor3f(0.70, 0.52, 0.32)
        glLineWidth(1.0)
        glBegin(GL_LINES)
        for i in range(12):
            ang = 2.0 * math.pi * i / 12.0
            cy = (r_nominal + 0.0002) * math.cos(ang)
            cz = (r_nominal + 0.0002) * math.sin(ang)
            glVertex3f(0.005, cy, cz)
            glVertex3f(self.L_madera - 0.005, cy, cz)
        glEnd()
        glEnable(GL_LIGHTING)

    def _render_unbalance_mass(self, e_m: float, R_actual_m: float):
        """Dibuja la masa excéntrica de desbalance (mu = 20 g) con indicador radial didáctico."""
        e_vis = max(e_m * 4.0, 0.014)
        x_unb = self.L_madera / 2.0

        glPushMatrix()
        glTranslatef(x_unb, e_vis, 0.0)

        # Esfera técnica roja reflectante para la masa excéntrica (mu = 20 g)
        glColor3f(1.0, 0.15, 0.15)
        quad = gluNewQuadric()
        gluSphere(quad, 0.008, 16, 16)
        gluDeleteQuadric(quad)

        # Anillo de fijación sobre la superficie
        glDisable(GL_LIGHTING)
        glColor3f(1.0, 0.85, 0.0) # Amarillo de seguridad
        glLineWidth(2.5)
        glBegin(GL_LINES)
        glVertex3f(0.0, -e_vis, 0.0)
        glVertex3f(0.0, 0.0, 0.0)
        glEnd()

        # Marcador circular de excentricidad
        glBegin(GL_LINE_LOOP)
        for k in range(24):
            a = 2.0 * math.pi * k / 24.0
            glVertex3f(0.0, 0.010 * math.cos(a), 0.010 * math.sin(a))
        glEnd()
        glEnable(GL_LIGHTING)

        glPopMatrix()

    def _render_tailstock(self, avance_x_m: float):
        """Dibuja el contrapunto móvil con caña telescópica, escala milimétrica grabada y volante."""
        x_base = self.L_madera + 0.015 - avance_x_m

        # Carro principal del contrapunto (Azul martillado)
        draw_box(x_base + 0.020, x_base + 0.145, -0.090, 0.065, -0.055, 0.055,
                 color=(0.19, 0.31, 0.44))

        # Palanca de bloqueo excéntrico a la bancada
        draw_box(x_base + 0.070, x_base + 0.082, 0.065, 0.115, 0.035, 0.047,
                 color=(0.12, 0.12, 0.14))
        # Pomo esférico de la palanca
        glPushMatrix()
        glTranslatef(x_base + 0.076, 0.118, 0.041)
        glColor3f(0.85, 0.2, 0.2)
        q = gluNewQuadric()
        gluSphere(q, 0.009, 12, 12)
        gluDeleteQuadric(q)
        glPopMatrix()

        # Caña telescópica rectificada (Quill de acero cromado)
        r_quill = 0.016
        l_quill = 0.045
        glPushMatrix()
        glTranslatef(x_base - 0.012, 0.0, 0.0)
        draw_cylinder_x(r_quill, l_quill, slices=24,
                        color_body=(0.82, 0.84, 0.88), color_caps=(0.72, 0.74, 0.78))

        # Escala métrica milimétrica grabada por láser sobre la caña
        glDisable(GL_LIGHTING)
        glLineWidth(1.0)
        glColor3f(0.20, 0.22, 0.25)
        glBegin(GL_LINES)
        for mm in range(0, 35, 2):
            gx = mm * 0.001
            gh = 0.004 if (mm % 10 == 0) else 0.002
            # Graduación en la generatriz superior
            glVertex3f(gx, r_quill + 0.0002, 0.0)
            glVertex3f(gx, r_quill + 0.0002, gh)
        glEnd()
        glEnable(GL_LIGHTING)

        # Punto giratorio cónico a 60° (Live center cónico para madera)
        glTranslatef(-0.016, 0.0, 0.0)
        glRotatef(90.0, 0.0, 1.0, 0.0)
        glColor3f(0.92, 0.94, 0.98)
        quad = gluNewQuadric()
        gluCylinder(quad, 0.0, r_quill, 0.016, 24, 4)
        gluDeleteQuadric(quad)
        glPopMatrix()

        # Volante manual circular (r_v = 60 mm) para avance micrométrico
        glPushMatrix()
        glTranslatef(x_base + 0.150, 0.0, 0.0)
        # Llanta circular del volante
        draw_cylinder_x(self.r_volante, 0.014, slices=32,
                        color_body=(0.28, 0.29, 0.32), color_caps=(0.42, 0.44, 0.48))
        # Centro y rayos del volante
        draw_cylinder_x(0.018, 0.016, slices=16,
                        color_body=(0.7, 0.7, 0.75), color_caps=(0.8, 0.8, 0.85))
        # Manija giratoria ergonómica en la periferia
        glTranslatef(0.014, self.r_volante - 0.012, 0.0)
        draw_cylinder_x(0.006, 0.038, slices=12,
                        color_body=(0.15, 0.15, 0.18), color_caps=(0.8, 0.2, 0.2))
        glPopMatrix()

    def _render_tool_rest(self, R_actual_m: float, tool_engaged: bool):
        """Dibuja el banquillo portaherramientas y la gubia de desbaste HSS con bisel de corte a 45°."""
        x_t = 0.120
        z_tool = R_actual_m + 0.001 if tool_engaged else (R_actual_m + 0.022)

        # Base del banquillo (Banjo) fijado a la bancada
        draw_box(x_t - 0.038, x_t + 0.038, -0.090, -0.015, -0.030, 0.075,
                 color=(0.24, 0.26, 0.29))

        # Columna cilíndrica de ajuste de altura
        glPushMatrix()
        glTranslatef(x_t, -0.015, R_actual_m + 0.010)
        glRotatef(-90.0, 1.0, 0.0, 0.0)
        draw_cylinder_x(0.010, 0.020, slices=16,
                        color_body=(0.65, 0.67, 0.70), color_caps=(0.6, 0.6, 0.6))
        glPopMatrix()

        # Barra de apoyo horizontal pulida de acero endurecido
        draw_box(x_t - 0.055, x_t + 0.055, -0.012, -0.002, R_actual_m + 0.004, R_actual_m + 0.016,
                 color=(0.75, 0.77, 0.82))

        # Gubia de desbaste (HSS Roughing Gouge) apoyada sobre la barra
        glPushMatrix()
        glTranslatef(x_t, 0.0, z_tool)

        # Mango ergonómico de madera de fresno torneada
        draw_box(-0.009, 0.009, -0.011, 0.011, 0.065, 0.190,
                 color=(0.60, 0.38, 0.22))
        # Virola de latón pulido que une mango y espiga
        draw_box(-0.007, 0.007, -0.009, 0.009, 0.055, 0.065,
                 color=(0.85, 0.72, 0.25))
        # Hoja de acero rápido HSS pulido con sección cóncava
        draw_box(-0.006, 0.006, -0.004, 0.004, 0.002, 0.055,
                 color=(0.90, 0.92, 0.96))
        # Filo biselado a 45° que penetra la madera
        glColor3f(1.0, 1.0, 1.0)
        glBegin(GL_TRIANGLES)
        glVertex3f(0.0, 0.004, 0.0)
        glVertex3f(-0.006, -0.004, 0.005)
        glVertex3f(0.006, -0.004, 0.005)
        glEnd()

        glPopMatrix()

    def _render_rotation_axis(self):
        """Línea de referencia del eje de revolución (Eje X punteado)."""
        glDisable(GL_LIGHTING)
        glColor4f(0.55, 0.60, 0.65, 0.6)
        glLineWidth(1.2)
        glEnable(GL_LINE_STIPPLE)
        glLineStipple(2, 0xAAAA)
        glBegin(GL_LINES)
        glVertex3f(-0.130, 0.0, 0.0)
        glVertex3f(self.L_madera + 0.120, 0.0, 0.0)
        glEnd()
        glDisable(GL_LINE_STIPPLE)
        glEnable(GL_LIGHTING)
