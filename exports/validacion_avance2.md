# Reporte de Validación Técnica — Simulador del Torno
**Asignatura:** Dinámica — Universidad Técnica de Ambato (FICM)
**Cálculos Evaluados:** 20 | **Aprobados en Tolerancia:** 20 (100.0%)

| N° | Cálculo | Variable | Analítico | Simulado | Error Rel. (%) | Tolerancia | Estado |
|:---|:---|:---|:---|:---|:---|:---|:---|
| **C01** | Velocidad Tangencial en la Periferia | `v` | 7.1209 m/s | 7.1209 m/s | 0.001% | ±0.05% | ✅ APROBADO |
| **C02** | Aceleración Normal Centrípeta en Arranque | `a_n` | 1267.7 m/s² | 1267.7 m/s² | 0.000% | ±0.05% | ✅ APROBADO |
| **C03** | Desplazamiento Angular en Arranque Amortiguado | `\theta` | 243.14 rad | 243.14 rad | 0.000% | ±0.05% | ✅ APROBADO |
| **C04** | Longitud de Trayectoria Periférica Barrida | `s_{\text{arco}}` | 9.7255 m | 9.7255 m | 0.000% | ±0.05% | ✅ APROBADO |
| **C05** | Velocidad de Corte Estandarizada | `v_c` | 7.1209 m/s | 7.1209 m/s | 0.001% | ±0.05% | ✅ APROBADO |
| **C06** | Deslizamiento del Motor de Inducción | `s` | 5.5556 % | 5.5556 % | 0.001% | ±0.10% | ✅ APROBADO |
| **C07** | Campo Lineal de Velocidades a r = 30 mm | `v(30)` | 5.3407 m/s | 5.3407 m/s | 0.000% | ±0.05% | ✅ APROBADO |
| **C08** | Velocidad Relativa entre Partículas A y Q | `v_{A/Q}` | 3.5605 m/s | 3.5605 m/s | 0.001% | ±0.05% | ✅ APROBADO |
| **C09** | Tiempo de Rebaje Radial de 1 mm | `t_{\text{corte}}` | 14.118 s | 14.118 s | 0.000% | ±0.05% | ✅ APROBADO |
| **C10** | Aceleración Lineal Total en Régimen | `a_{\text{tot}}` | 1267.7 m/s² | 1267.7 m/s² | 0.000% | ±0.05% | ✅ APROBADO |
| **C11** | Fuerza Centrífuga por Desbalance Excéntrico | `F_u` | 1.2677 N | 1.2677 N | 0.000% | ±0.05% | ✅ APROBADO |
| **C12** | Trabajo Aceleratriz para Partícula de 1 g | `U_{1-2}` | 0.02535 J | 0.025354 J | 0.015% | ±0.05% | ✅ APROBADO |
| **C13** | Potencia Total y Eficiencia de Mecanizado | `P_{\text{total}}` | 200.86 W | 200.85 W | 0.005% | ±0.05% | ✅ APROBADO |
| **C14** | Variación de Momento Angular en el Arranque | `\Delta H_O` | 0.2138 N·m·s | 0.2138 N·m·s | 0.001% | ±0.05% | ✅ APROBADO |
| **C15** | Reacción Inercial por Desprendimiento de Viruta | `F_{\text{reac}}` | 0.0534 N | 0.053407 N | 0.013% | ±0.10% | ✅ APROBADO |
| **C16** | Momento de Inercia Total Equivalente | `I_{\text{tot}}` | 0.001201 kg·m² | 0.001201 kg·m² | 0.001% | ±0.05% | ✅ APROBADO |
| **C17** | Coeficiente de Amortiguamiento Viscoso | `b` | 0.0018436 N·m·s | 0.0018436 N·m·s | 0.002% | ±0.05% | ✅ APROBADO |
| **C18** | Vueltas Remanentes en Parada Libre | `N_\infty` | 18.457 rev | 18.458 rev | 0.001% | ±0.10% | ✅ APROBADO |
| **C19** | Esfuerzo Cortante Máximo en Eje con Chavetero | `\tau_{\text{máx}}` | 0.9504 MPa | 0.95043 MPa | 0.003% | ±0.05% | ✅ APROBADO |
| **C20** | Fuerza Manual en Volante del Contrapunto | `F_{\text{mano}}` | 2.8519 N | 2.8515 N | 0.013% | ±0.10% | ✅ APROBADO |
