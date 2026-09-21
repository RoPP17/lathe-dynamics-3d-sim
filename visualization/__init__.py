"""Módulo de renderizado y visualización técnica 3D."""
from .gl_widget import LatheGLWidget
from .lathe_geometry import Lathe3DModel
from .dynamic_vectors import DynamicVectorRenderer
from .particle_system import ChipParticleSystem

__all__ = [
    "LatheGLWidget",
    "Lathe3DModel",
    "DynamicVectorRenderer",
    "ChipParticleSystem"
]
