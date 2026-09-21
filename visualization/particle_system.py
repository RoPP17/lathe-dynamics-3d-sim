"""
Sistema de partículas 3D para viruta desprendida en el torneado.
Modela la eyección continua a u = 6.0 m/s (Cálculo 15).
"""

import random
from typing import List
from OpenGL.GL import *


class ChipParticle:
    """Partícula individual de viruta de madera."""
    def __init__(self, x: float, y: float, z: float, vx: float, vy: float, vz: float, life: float):
        self.x = x
        self.y = y
        self.z = z
        self.vx = vx
        self.vy = vy
        self.vz = vz
        self.life = life
        self.max_life = life


class ChipParticleSystem:
    """Emisor y gestor de partículas de viruta."""

    def __init__(self, max_particles: int = 150):
        self.max_particles = max_particles
        self.particles: List[ChipParticle] = []

    def update(self, dt: float, is_cutting: bool, R_actual_m: float, u_m_s: float = 6.0):
        """Actualiza la física y vida de las partículas."""
        # Envejecer y mover partículas existentes
        alive = []
        for p in self.particles:
            p.life -= dt
            if p.life > 0:
                p.x += p.vx * dt
                p.y += p.vy * dt
                p.z += p.vz * dt
                # Gravedad sutil
                p.vy -= 9.81 * dt * 0.2
                alive.append(p)
        self.particles = alive

        # Emitir nuevas partículas si la gubia está en corte
        if is_cutting and len(self.particles) < self.max_particles:
            num_to_emit = random.randint(3, 7)
            # Punto de origen: filo de la gubia en (x=0.120, y=0, z=R_actual)
            orig_x = 0.120 + random.uniform(-0.003, 0.003)
            orig_y = random.uniform(-0.002, 0.002)
            orig_z = R_actual_m + 0.001

            for _ in range(num_to_emit):
                # Velocidad de eyección tangencial + componente aleatoria de dispersión
                speed_scale = 0.035 # Factor para recorrido visual en la escena
                vx = random.uniform(-0.3, 0.3) * speed_scale
                vy = (-u_m_s * 0.7 + random.uniform(-1.0, 1.0)) * speed_scale
                vz = (u_m_s * 0.7 + random.uniform(-1.0, 1.0)) * speed_scale
                life = random.uniform(0.15, 0.35)
                self.particles.append(ChipParticle(orig_x, orig_y, orig_z, vx, vy, vz, life))

    def render(self):
        """Dibuja las virutas en la escena OpenGL."""
        if not self.particles:
            return

        glDisable(GL_LIGHTING)
        glPointSize(4.0)
        glBegin(GL_POINTS)
        for p in self.particles:
            alpha = max(0.0, min(1.0, p.life / p.max_life))
            glColor4f(0.92, 0.78, 0.45, alpha) # Dorado madera
            glVertex3f(p.x, p.y, p.z)
        glEnd()
        glEnable(GL_LIGHTING)
