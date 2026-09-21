"""
Valores Analíticos Oficiales de Referencia (Avance 2).
Fuente: Documento oficial LaTeX avance2.tex.
Incluye símbolos en Unicode, variables en HTML con subíndices matemáticos y ecuaciones compiladas.
"""

from dataclasses import dataclass
from typing import Dict, Any, List


@dataclass
class CalculationBenchmark:
    num: int
    titulo: str
    unidad_tematica: str
    variable_simbolo: str
    variable_nombre: str
    ecuacion_latex: str
    valor_analitico: float
    unidad_si: str
    tolerancia_pct: float
    descripcion: str
    ecuacion_compilada: str = ""
    variable_html: str = ""


AVANCE2_BENCHMARK_LIST: List[CalculationBenchmark] = [
    CalculationBenchmark(
        num=1,
        titulo="Velocidad Tangencial en la Periferia",
        unidad_tematica="Unidad 1 - Cinemática de Partícula",
        variable_simbolo="v",
        variable_html="<i>v</i>",
        variable_nombre="Rapidez tangencial superficial",
        ecuacion_latex=r"v = \omega R = \frac{2\pi n}{60} R",
        ecuacion_compilada="<i>v</i> = &omega; &middot; <i>R</i> = (2&pi; &middot; <i>n</i> / 60) &middot; <i>R</i>",
        valor_analitico=7.1209,
        unidad_si="m/s",
        tolerancia_pct=0.05,
        descripcion="Velocidad lineal superficial para el punto periférico a R = 40 mm y n = 1700 rpm."
    ),
    CalculationBenchmark(
        num=2,
        titulo="Aceleración Normal Centrípeta en Arranque",
        unidad_tematica="Unidad 1 - Cinemática de Partícula",
        variable_simbolo="aₙ",
        variable_html="<i>a</i><sub>n</sub>",
        variable_nombre="Aceleración normal en régimen",
        ecuacion_latex=r"a_n = \omega^2 R",
        ecuacion_compilada="<i>a</i><sub>n</sub> = &omega;&sup2; &middot; <i>R</i>",
        valor_analitico=1267.6963,
        unidad_si="m/s²",
        tolerancia_pct=0.05,
        descripcion="Aceleración normal centrípeta debida al giro a velocidad nominal de 178.02 rad/s."
    ),
    CalculationBenchmark(
        num=3,
        titulo="Desplazamiento Angular en Arranque Amortiguado",
        unidad_tematica="Unidad 1 - Cinemática de Partícula",
        variable_simbolo="θ",
        variable_html="&theta;",
        variable_nombre="Ángulo acumulado en arranque",
        ecuacion_latex=r"\theta(t) = \omega_{\text{reg}}[t - \tau(1 - e^{-t/\tau})]",
        ecuacion_compilada="&theta;(<i>t</i>) = &omega;<sub>reg</sub> &middot; [<i>t</i> &minus; &tau; &middot; (1 &minus; <i>e</i><sup>&minus;<i>t</i>/&tau;</sup>)]",
        valor_analitico=243.1383,
        unidad_si="rad",
        tolerancia_pct=0.05,
        descripcion="Giro acumulado durante los 2.0 s del transitorio de aceleración exponencial."
    ),
    CalculationBenchmark(
        num=4,
        titulo="Longitud de Trayectoria Periférica Barrida",
        unidad_tematica="Unidad 1 - Cinemática de Partícula",
        variable_simbolo="s(arco)",
        variable_html="<i>s</i><sub>arco</sub>",
        variable_nombre="Longitud de arco recorrida",
        ecuacion_latex=r"s_{\text{arco}} = R \theta",
        ecuacion_compilada="<i>s</i><sub>arco</sub> = <i>R</i> &middot; &theta;",
        valor_analitico=9.7255,
        unidad_si="m",
        tolerancia_pct=0.05,
        descripcion="Distancia espacial recorrida por un punto exterior durante el encendido."
    ),
    CalculationBenchmark(
        num=5,
        titulo="Velocidad de Corte Estandarizada",
        unidad_tematica="Unidad 1 - Cinemática de Partícula",
        variable_simbolo="v꜀",
        variable_html="<i>v</i><sub>c</sub>",
        variable_nombre="Velocidad estándar de corte",
        ecuacion_latex=r"v_c = \frac{\pi D n}{60}",
        ecuacion_compilada="<i>v</i><sub>c</sub> = (&pi; &middot; <i>D</i> &middot; <i>n</i>) / 60",
        valor_analitico=7.1209,
        unidad_si="m/s",
        tolerancia_pct=0.05,
        descripcion="Velocidad lineal de corte a diámetro exterior inicial D = 80 mm."
    ),
    CalculationBenchmark(
        num=6,
        titulo="Deslizamiento del Motor de Inducción",
        unidad_tematica="Unidad 2 - Cinemática de Cuerpos Rígidos",
        variable_simbolo="s",
        variable_html="<i>s</i>",
        variable_nombre="Deslizamiento porcentual",
        ecuacion_latex=r"s = \frac{n_s - n}{n_s} \times 100\%",
        ecuacion_compilada="<i>s</i> = [(<i>n</i><sub>s</sub> &minus; <i>n</i>) / <i>n</i><sub>s</sub>] &times; 100%",
        valor_analitico=5.5556,
        unidad_si="%",
        tolerancia_pct=0.10,
        descripcion="Deslizamiento electromecánico relativo del motor NEMA de 4 polos a 60 Hz."
    ),
    CalculationBenchmark(
        num=7,
        titulo="Campo Lineal de Velocidades a r = 30 mm",
        unidad_tematica="Unidad 2 - Cinemática de Cuerpos Rígidos",
        variable_simbolo="v(30)",
        variable_html="<i>v</i>(30)",
        variable_nombre="Velocidad tangencial a r = 30 mm",
        ecuacion_latex=r"v(r) = \omega r",
        ecuacion_compilada="<i>v</i>(<i>r</i>) = &omega; &middot; <i>r</i>",
        valor_analitico=5.3407,
        unidad_si="m/s",
        tolerancia_pct=0.05,
        descripcion="Distribución lineal de velocidades respecto al Centro Instantáneo en el eje."
    ),
    CalculationBenchmark(
        num=8,
        titulo="Velocidad Relativa entre Partículas A y Q",
        unidad_tematica="Unidad 2 - Cinemática de Cuerpos Rígidos",
        variable_simbolo="v(A/Q)",
        variable_html="<i>v</i><sub>A/Q</sub>",
        variable_nombre="Rapidez relativa A respecto a Q",
        ecuacion_latex=r"v_{A/Q} = \omega (r_A - r_Q)",
        ecuacion_compilada="<i>v</i><sub>A/Q</sub> = &omega; &middot; (<i>r</i><sub>A</sub> &minus; <i>r</i><sub>Q</sub>)",
        valor_analitico=3.5605,
        unidad_si="m/s",
        tolerancia_pct=0.05,
        descripcion="Velocidad relativa en sólido rígido para rA = 40 mm y rQ = 20 mm."
    ),
    CalculationBenchmark(
        num=9,
        titulo="Tiempo de Rebaje Radial de 1 mm",
        unidad_tematica="Unidad 2 - Cinemática de Cuerpos Rígidos",
        variable_simbolo="t(corte)",
        variable_html="<i>t</i><sub>corte</sub>",
        variable_nombre="Tiempo de desbaste continuo",
        ecuacion_latex=r"t_{\text{corte}} = \frac{\Delta R}{f_r (n/60)}",
        ecuacion_compilada="<i>t</i><sub>corte</sub> = &Delta;<i>R</i> / [<i>f</i><sub>r</sub> &middot; (<i>n</i> / 60)]",
        valor_analitico=14.1176,
        unidad_si="s",
        tolerancia_pct=0.05,
        descripcion="Tiempo para remover 1 mm radial a fr = 2.5 um/rev y 1700 rpm (400 vueltas)."
    ),
    CalculationBenchmark(
        num=10,
        titulo="Aceleración Lineal Total en Régimen",
        unidad_tematica="Unidad 2 - Cinemática de Cuerpos Rígidos",
        variable_simbolo="a(tot)",
        variable_html="<i>a</i><sub>tot</sub>",
        variable_nombre="Magnitud aceleración resultante",
        ecuacion_latex=r"a_{\text{tot}} = \sqrt{a_t^2 + a_n^2}",
        ecuacion_compilada="<i>a</i><sub>tot</sub> = &radic;(<i>a</i><sub>t</sub>&sup2; + <i>a</i><sub>n</sub>&sup2;)",
        valor_analitico=1267.7013,
        unidad_si="m/s²",
        tolerancia_pct=0.05,
        descripcion="Composición vectorial intrínseca tangencial y normal en la periferia."
    ),
    CalculationBenchmark(
        num=11,
        titulo="Fuerza Centrífuga por Desbalance Excéntrico",
        unidad_tematica="Unidad 3 - Cinética de Partícula",
        variable_simbolo="Fᵤ",
        variable_html="<i>F</i><sub>u</sub>",
        variable_nombre="Fuerza centrífuga de desbalance",
        ecuacion_latex=r"F_u = m_u e \omega^2",
        ecuacion_compilada="<i>F</i><sub>u</sub> = <i>m</i><sub>u</sub> &middot; <i>e</i> &middot; &omega;&sup2;",
        valor_analitico=1.2677,
        unidad_si="N",
        tolerancia_pct=0.05,
        descripcion="Fuerza inercial giratoria producida por 20 g a 2 mm de excentricidad."
    ),
    CalculationBenchmark(
        num=12,
        titulo="Trabajo Aceleratriz para Partícula de 1 g",
        unidad_tematica="Unidad 3 - Cinética de Partícula",
        variable_simbolo="U₁₋₂",
        variable_html="<i>U</i><sub>1-2</sub>",
        variable_nombre="Trabajo mecánico neto",
        ecuacion_latex=r"U_{1-2} = \frac{1}{2} m v^2",
        ecuacion_compilada="<i>U</i><sub>1-2</sub> = &frac12; &middot; <i>m</i> &middot; <i>v</i>&sup2;",
        valor_analitico=0.02535,
        unidad_si="J",
        tolerancia_pct=0.05,
        descripcion="Principio del trabajo y la energía para acelerar 1 g hasta la velocidad de régimen."
    ),
    CalculationBenchmark(
        num=13,
        titulo="Potencia Total y Eficiencia de Mecanizado",
        unidad_tematica="Unidad 3 - Cinética de Partícula",
        variable_simbolo="P(total)",
        variable_html="<i>P</i><sub>total</sub>",
        variable_nombre="Potencia mecánica demandada",
        ecuacion_latex=r"P_{\text{total}} = F_c v_c + b \omega^2",
        ecuacion_compilada="<i>P</i><sub>total</sub> = <i>F</i><sub>c</sub> &middot; <i>v</i><sub>c</sub> + <i>b</i> &middot; &omega;&sup2;",
        valor_analitico=200.8561,
        unidad_si="W",
        tolerancia_pct=0.05,
        descripcion="Suma de potencia útil de desbaste (142.42 W) y pérdidas viscosas (58.44 W)."
    ),
    CalculationBenchmark(
        num=14,
        titulo="Variación de Momento Angular en el Arranque",
        unidad_tematica="Unidad 4 - Cinética de Cuerpos Rígidos",
        variable_simbolo="ΔH(O)",
        variable_html="&Delta;<i>H</i><sub>O</sub>",
        variable_nombre="Impulso angular del conjunto",
        ecuacion_latex=r"\Delta H_O = I_{\text{tot}} \omega",
        ecuacion_compilada="&Delta;<i>H</i><sub>O</sub> = <i>I</i><sub>tot</sub> &middot; &omega;",
        valor_analitico=0.21380,
        unidad_si="N·m·s",
        tolerancia_pct=0.05,
        descripcion="Cantidad de movimiento angular ganada por el rotor al pasar del reposo a régimen."
    ),
    CalculationBenchmark(
        num=15,
        titulo="Reacción Inercial por Desprendimiento de Viruta",
        unidad_tematica="Unidad 4 - Cinética de Cuerpos Rígidos",
        variable_simbolo="F(reac)",
        variable_html="<i>F</i><sub>reac</sub>",
        variable_nombre="Fuerza inercial convectiva",
        ecuacion_latex=r"F_{\text{reac}} = \dot{m} u = (\rho b_w t_c v_c) u",
        ecuacion_compilada="<i>F</i><sub>reac</sub> = &#7745; &middot; <i>u</i> = (&rho; &middot; <i>b</i><sub>w</sub> &middot; <i>t</i><sub>c</sub> &middot; <i>v</i><sub>c</sub>) &middot; <i>u</i>",
        valor_analitico=0.0534,
        unidad_si="N",
        tolerancia_pct=0.10,
        descripcion="Transporte convectivo de momento en el flujo continuo de virutas de madera."
    ),
    CalculationBenchmark(
        num=16,
        titulo="Momento de Inercia Total Equivalente",
        unidad_tematica="Unidad 4 - Cinética de Cuerpos Rígidos",
        variable_simbolo="I(tot)",
        variable_html="<i>I</i><sub>tot</sub>",
        variable_nombre="Inercia compuesta masa-rotor",
        ecuacion_latex=r"I_{\text{tot}} = \frac{1}{2} m_{\text{pieza}} R^2 + \frac{1}{2} m_p R_p^2",
        ecuacion_compilada="<i>I</i><sub>tot</sub> = &frac12; &middot; <i>m</i><sub>pieza</sub> &middot; <i>R</i>&sup2; + &frac12; &middot; <i>m</i><sub>p</sub> &middot; <i>R</i><sub>p</sub>&sup2;",
        valor_analitico=1.20097e-3,
        unidad_si="kg·m²",
        tolerancia_pct=0.05,
        descripcion="Suma de las inercias axiales de la pieza de pino (5.03e-4) y el plato de arrastre (6.98e-4)."
    ),
    CalculationBenchmark(
        num=17,
        titulo="Coeficiente de Amortiguamiento Viscoso",
        unidad_tematica="Unidad 4 - Cinética de Cuerpos Rígidos",
        variable_simbolo="b",
        variable_html="<i>b</i>",
        variable_nombre="Coeficiente amortiguamiento",
        ecuacion_latex=r"b = \frac{I_{\text{tot}}}{\tau_{\text{stop}}} = \frac{I_{\text{tot}}}{\Delta t_{\text{stop}} / \ln(100)}",
        ecuacion_compilada="<i>b</i> = <i>I</i><sub>tot</sub> / &tau;<sub>stop</sub> = <i>I</i><sub>tot</sub> / [&Delta;<i>t</i><sub>stop</sub> / ln(100)]",
        valor_analitico=1.8436e-3,
        unidad_si="N·m·s",
        tolerancia_pct=0.05,
        descripcion="Pérdidas mecánicas viscosas equivalentes deducidas del ensayo pasivo de run-down."
    ),
    CalculationBenchmark(
        num=18,
        titulo="Vueltas Remanentes en Parada Libre",
        unidad_tematica="Unidad 4 - Cinética de Cuerpos Rígidos",
        variable_simbolo="N(∞)",
        variable_html="<i>N</i><sub>&infin;</sub>",
        variable_nombre="Revoluciones de giro remanente",
        ecuacion_latex=r"N_\infty = \frac{\omega_0 \tau_{\text{stop}}}{2\pi}",
        ecuacion_compilada="<i>N</i><sub>&infin;</sub> = (&omega;&sub0; &middot; &tau;<sub>stop</sub>) / (2&pi;)",
        valor_analitico=18.4574,
        unidad_si="rev",
        tolerancia_pct=0.10,
        descripcion="Revoluciones acumuladas por inercia tras interrumpir el suministro eléctrico."
    ),
    CalculationBenchmark(
        num=19,
        titulo="Esfuerzo Cortante Máximo en Eje con Chavetero",
        unidad_tematica="Unidad 4 - Cinética de Cuerpos Rígidos",
        variable_simbolo="τ(máx)",
        variable_html="&tau;<sub>m&aacute;x</sub>",
        variable_nombre="Esfuerzo cortante torsional",
        ecuacion_latex=r"\tau_{\text{máx}} = K_t \frac{16 M_t}{\pi d^3}",
        ecuacion_compilada="&tau;<sub>m&aacute;x</sub> = <i>K</i><sub>t</sub> &middot; [16 &middot; <i>M</i><sub>t</sub> / (&pi; &middot; <i>d</i>&sup3;)]",
        valor_analitico=0.9504,
        unidad_si="MPa",
        tolerancia_pct=0.05,
        descripcion="Esfuerzo cortante en el husillo considerando factor de concentración Kt = 1.6."
    ),
    CalculationBenchmark(
        num=20,
        titulo="Fuerza Manual en Volante del Contrapunto",
        unidad_tematica="Unidad 4 - Cinética de Cuerpos Rígidos",
        variable_simbolo="F(mano)",
        variable_html="<i>F</i><sub>mano</sub>",
        variable_nombre="Fuerza tangencial manual requerida",
        ecuacion_latex=r"F_{\text{mano}} = \frac{U_{\text{axial}}}{2\pi (x/p) r_v}",
        ecuacion_compilada="<i>F</i><sub>mano</sub> = <i>U</i><sub>axial</sub> / [2&pi; &middot; (<i>x</i> / <i>p</i>) &middot; <i>r</i><sub>v</sub>]",
        valor_analitico=2.8519,
        unidad_si="N",
        tolerancia_pct=0.10,
        descripcion="Fuerza muscular que aplica el operario para inducir 575 N de apriete axial."
    )
]


def get_benchmark_dict() -> Dict[int, CalculationBenchmark]:
    """Retorna los 20 benchmarks indexados por número de cálculo."""
    return {bm.num: bm for bm in AVANCE2_BENCHMARK_LIST}
