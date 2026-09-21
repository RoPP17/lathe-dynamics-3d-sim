"""
Núcleo Físico y Matemático del Torno Didáctico.
Fuente única de verdad matemática para simulación, gráficos y validación.
"""

from .models import LatheParameters, DynamicState
from .kinematics import LatheKinematics
from .kinetics import LatheKinetics
from .motor_rundown import LatheMotorRundown
from .mechanics import LatheMechanics
from .benchmark import CalculationBenchmark, AVANCE2_BENCHMARK_LIST, get_benchmark_dict

__all__ = [
    "LatheParameters",
    "DynamicState",
    "LatheKinematics",
    "LatheKinetics",
    "LatheMotorRundown",
    "LatheMechanics",
    "CalculationBenchmark",
    "AVANCE2_BENCHMARK_LIST",
    "get_benchmark_dict"
]
