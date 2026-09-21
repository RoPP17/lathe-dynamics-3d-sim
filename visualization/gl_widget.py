"""
Widget OpenGL Interactivo 3D para PyQt6 (LatheGLWidget).
Soporta cámara orbital técnica, presets de vistas y renderizado de vectores dinámicos.
"""

import math
from PyQt6.QtCore import Qt, QPoint, pyqtSignal
from PyQt6.QtOpenGLWidgets import QOpenGLWidget
from OpenGL.GL import *
from OpenGL.GLU import *

from .lathe_geometry import Lathe3DModel
from .dynamic_vectors import DynamicVectorRenderer
from .particle_system import ChipParticleSystem
from physics.models import DynamicState


class LatheGLWidget(QOpenGLWidget):
    """Visualizador tridimensional acelerado por hardware para el torno dinámico."""

    camera_changed = pyqtSignal(str)
    resized_event = pyqtSignal(int, int)

    def __init__(self, parent=None):
        super().__init__(parent)

        # Control de cámara orbital
        self.cam_azimuth: float = 40.0     # grados
        self.cam_elevation: float = 25.0   # grados
        self.cam_distance: float = 0.65    # metros
        self.cam_target = [0.125, -0.010, 0.0] # Centro del área de trabajo

        # Estado del ratón
        self.last_mouse_pos = QPoint()

        # Modelos y subsistemas de visualización
        self.model_3d = Lathe3DModel()
        self.vector_renderer = DynamicVectorRenderer()
        self.particle_system = ChipParticleSystem()

        # Estado dinámico actual a graficar
        self.current_state: DynamicState = DynamicState()

        # Banderas de visibilidad de familias de vectores
        self.vis_flags = {
            "velocidad": True,
            "acel_tang": True,
            "acel_norm": True,
            "acel_total": False,
            "desbalance": True,
            "corte": True,
            "viruta": True,
            "ejes": True
        }

        # Configuración de foco para teclado
        self.setFocusPolicy(Qt.FocusPolicy.StrongFocus)

    def initializeGL(self):
        """Inicializa las capacidades y el sombreado OpenGL."""
        glClearColor(0.08, 0.08, 0.09, 1.0) # Fondo oscuro técnico (#141417)
        glEnable(GL_DEPTH_TEST)
        glDepthFunc(GL_LEQUAL)
        glEnable(GL_CULL_FACE)
        glCullFace(GL_BACK)

        # Suavizado de líneas y puntos
        glEnable(GL_BLEND)
        glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
        glEnable(GL_LINE_SMOOTH)
        glHint(GL_LINE_SMOOTH_HINT, GL_NICEST)

        # Iluminación técnica difusa y especular
        glEnable(GL_LIGHTING)
        glEnable(GL_LIGHT0)
        glEnable(GL_COLOR_MATERIAL)
        glColorMaterial(GL_FRONT_AND_BACK, GL_AMBIENT_AND_DIFFUSE)

        # Luz principal cenital inclinada
        light0_pos = [0.5, 1.0, 1.2, 1.0]
        light0_diff = [0.95, 0.95, 0.95, 1.0]
        light0_amb = [0.35, 0.35, 0.38, 1.0]
        light0_spec = [0.40, 0.40, 0.45, 1.0]
        glLightfv(GL_LIGHT0, GL_POSITION, light0_pos)
        glLightfv(GL_LIGHT0, GL_DIFFUSE, light0_diff)
        glLightfv(GL_LIGHT0, GL_AMBIENT, light0_amb)
        glLightfv(GL_LIGHT0, GL_SPECULAR, light0_spec)

        # Luz de relleno secundaria
        glEnable(GL_LIGHT1)
        light1_pos = [-0.6, -0.4, -0.8, 1.0]
        light1_diff = [0.25, 0.25, 0.30, 1.0]
        light1_amb = [0.10, 0.10, 0.12, 1.0]
        glLightfv(GL_LIGHT1, GL_POSITION, light1_pos)
        glLightfv(GL_LIGHT1, GL_DIFFUSE, light1_diff)
        glLightfv(GL_LIGHT1, GL_AMBIENT, light1_amb)

    def resizeGL(self, width: int, height: int):
        """Ajusta el viewport cuando cambia el tamaño de la ventana."""
        if height == 0:
            height = 1
        glViewport(0, 0, width, height)
        glMatrixMode(GL_PROJECTION)
        glLoadIdentity()
        gluPerspective(42.0, width / float(height), 0.05, 10.0)
        glMatrixMode(GL_MODELVIEW)
        self.resized_event.emit(width, height)

    def paintGL(self):
        """Renderiza la escena completa del simulador."""
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
        glLoadIdentity()

        # Cálculo de la posición de la cámara esférica
        az_rad = math.radians(self.cam_azimuth)
        el_rad = math.radians(self.cam_elevation)

        cam_x = self.cam_target[0] + self.cam_distance * math.cos(el_rad) * math.sin(az_rad)
        cam_y = self.cam_target[1] + self.cam_distance * math.sin(el_rad)
        cam_z = self.cam_target[2] + self.cam_distance * math.cos(el_rad) * math.cos(az_rad)

        # Posicionamiento de la cámara
        gluLookAt(
            cam_x, cam_y, cam_z,
            self.cam_target[0], self.cam_target[1], self.cam_target[2],
            0.0, 1.0, 0.0
        )

        # Ejes coordenados de referencia (RGB = XYZ)
        if self.vis_flags.get("ejes", True):
            self._render_coordinate_axes()

        # Estado dinámico para visualización
        st = self.current_state
        is_desbalance = (st.fase == "DESBALANCE")
        is_cutting = (st.fase == "TORNEADO")

        # 1. Torno mecánico 3D
        self.model_3d.render(
            theta_rad=st.theta,
            R_actual_m=st.R_actual,
            desbalance_activo=is_desbalance,
            tool_engaged=is_cutting,
            avance_contrapunto_m=0.0015,
            is_rotating=(st.omega > 0.5)
        )

        # 2. Vectores dinámicos orientados
        self.vector_renderer.render_vectors(st, self.vis_flags)

        # 3. Partículas de viruta durante mecanizado
        self.particle_system.render()

    def _render_coordinate_axes(self):
        """Dibuja un trípode de ejes cartesianos en la esquina inferior del espacio."""
        glDisable(GL_LIGHTING)
        glLineWidth(2.0)
        glPushMatrix()
        glTranslatef(-0.160, -0.090, 0.120)
        len_axis = 0.040

        glBegin(GL_LINES)
        # Eje X: Rojo (Longitudinal de rotación)
        glColor3f(0.9, 0.2, 0.2)
        glVertex3f(0.0, 0.0, 0.0); glVertex3f(len_axis, 0.0, 0.0)
        # Eje Y: Verde (Vertical)
        glColor3f(0.2, 0.9, 0.2)
        glVertex3f(0.0, 0.0, 0.0); glVertex3f(0.0, len_axis, 0.0)
        # Eje Z: Azul (Radial transversal)
        glColor3f(0.2, 0.5, 0.9)
        glVertex3f(0.0, 0.0, 0.0); glVertex3f(0.0, 0.0, len_axis)
        glEnd()

        glPopMatrix()
        glEnable(GL_LIGHTING)

    def update_simulation_state(self, state: DynamicState):
        """Actualiza el estado dinámico y refresca el renderizado 3D."""
        self.current_state = state
        # Actualizar física de partículas
        is_cutting = (state.fase == "TORNEADO" and state.v_corte > 0.1)
        self.particle_system.update(0.016, is_cutting, state.R_actual)
        self.update()

    def set_vector_visibility(self, vector_name: str, visible: bool):
        """Activa o desactiva la visualización de un vector específico."""
        self.vis_flags[vector_name] = visible
        self.update()

    # --------------------------------------------------------------------------
    # PRESETS DE CÁMARA
    # --------------------------------------------------------------------------
    def set_view_isometric(self):
        """Vista isométrica estándar de ingeniería (45°, 28°)."""
        self.cam_azimuth = 45.0
        self.cam_elevation = 28.0
        self.cam_distance = 0.65
        self.cam_target = [0.125, -0.010, 0.0]
        self.update()
        self.camera_changed.emit("ISOMÉTRICA")

    def set_view_front(self):
        """Vista frontal longitudinal (elevación a lo largo de la bancada)."""
        self.cam_azimuth = 0.0
        self.cam_elevation = 8.0
        self.cam_distance = 0.60
        self.cam_target = [0.125, -0.010, 0.0]
        self.update()
        self.camera_changed.emit("FRONTAL")

    def set_view_side(self):
        """Vista lateral de la sección circular transversal (ideal para vectores radiales an, at, Fu)."""
        self.cam_azimuth = 90.0
        self.cam_elevation = 0.0
        self.cam_distance = 0.50
        self.cam_target = [0.125, 0.0, 0.0]
        self.update()
        self.camera_changed.emit("LATERAL (SECCIÓN)")

    def set_view_top(self):
        """Vista superior en planta (90° cenital)."""
        self.cam_azimuth = 0.0
        self.cam_elevation = 88.0
        self.cam_distance = 0.65
        self.cam_target = [0.125, 0.0, 0.0]
        self.update()
        self.camera_changed.emit("SUPERIOR (PLANTA)")

    def reset_camera(self):
        """Restaura la orientación isométrica inicial."""
        self.set_view_isometric()

    # --------------------------------------------------------------------------
    # INTERACCIÓN CON EL RATÓN (ORBIT, PAN, ZOOM)
    # --------------------------------------------------------------------------
    def mousePressEvent(self, event):
        self.last_mouse_pos = event.position().toPoint()

    def mouseMoveEvent(self, event):
        pos = event.position().toPoint()
        dx = pos.x() - self.last_mouse_pos.x()
        dy = pos.y() - self.last_mouse_pos.y()

        if event.buttons() & Qt.MouseButton.LeftButton:
            # Rotación orbital
            self.cam_azimuth += dx * 0.45
            self.cam_elevation = max(-89.0, min(89.0, self.cam_elevation - dy * 0.45))
            self.update()
        elif event.buttons() & Qt.MouseButton.RightButton or event.buttons() & Qt.MouseButton.MiddleButton:
            # Paneo (desplazamiento del punto focal)
            pan_scale = self.cam_distance * 0.0012
            az_rad = math.radians(self.cam_azimuth)
            # Vectores locales de pantalla
            self.cam_target[0] -= dx * pan_scale * math.cos(az_rad)
            self.cam_target[2] += dx * pan_scale * math.sin(az_rad)
            self.cam_target[1] += dy * pan_scale
            self.update()

        self.last_mouse_pos = pos

    def wheelEvent(self, event):
        # Zoom con la rueda del ratón
        delta = event.angleDelta().y()
        factor = 0.90 if delta > 0 else 1.10
        self.cam_distance = max(0.15, min(2.50, self.cam_distance * factor))
        self.update()
