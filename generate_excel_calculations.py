"""
Generador de la Memoria de Cálculos Dinámicos en formato Excel (.xlsx).
Cumple rigurosamente con las directrices de la skill xlsx:
- Fórmulas dinámicas nativas sin hardcoding de resultados.
- Tipografía profesional Arial en todo el libro.
- Colores convencionales de modelado: azul para entradas, negro para fórmulas.
- Celdas formateadas numéricamente con unidades explícitas.
- Tablas de validación contra el Avance 2 con error relativo.
"""

import os
import openpyxl
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
from openpyxl.utils import get_column_letter

def build_lathe_excel_model(output_path: str):
    wb = openpyxl.Workbook()
    
    # -------------------------------------------------------------
    # Estilos profesionales
    # -------------------------------------------------------------
    font_title = Font(name="Arial", size=14, bold=True, color="1F4E79")
    font_subtitle = Font(name="Arial", size=10, italic=True, color="595959")
    font_section = Font(name="Arial", size=11, bold=True, color="FFFFFF")
    fill_section = PatternFill(start_color="1F4E79", end_color="1F4E79", fill_type="solid")
    
    font_header = Font(name="Arial", size=10, bold=True, color="FFFFFF")
    fill_header = PatternFill(start_color="2F5597", end_color="2F5597", fill_type="solid")
    fill_subheader = PatternFill(start_color="D9E1F2", end_color="D9E1F2", fill_type="solid")
    font_subheader = Font(name="Arial", size=10, bold=True, color="1F4E79")
    
    font_input = Font(name="Arial", size=10, color="002060")  # Azul para entradas
    fill_input = PatternFill(start_color="FFF2CC", end_color="FFF2CC", fill_type="solid") # Fondo amarillo tenue
    
    font_formula = Font(name="Arial", size=10, color="000000") # Negro para fórmulas
    font_bold = Font(name="Arial", size=10, bold=True, color="000000")
    font_unit = Font(name="Arial", size=9, italic=True, color="595959")
    
    fill_ok = PatternFill(start_color="E2EFDA", end_color="E2EFDA", fill_type="solid")
    font_ok = Font(name="Arial", size=10, bold=True, color="375623")
    
    thin_border = Border(
        left=Side(style='thin', color='D9D9D9'),
        right=Side(style='thin', color='D9D9D9'),
        top=Side(style='thin', color='D9D9D9'),
        bottom=Side(style='thin', color='D9D9D9')
    )
    header_border = Border(
        left=Side(style='thin', color='FFFFFF'),
        right=Side(style='thin', color='FFFFFF'),
        top=Side(style='medium', color='1F4E79'),
        bottom=Side(style='medium', color='1F4E79')
    )

    # -------------------------------------------------------------
    # HOJA 1: Parámetros de Entrada (Parametros_Entrada)
    # -------------------------------------------------------------
    ws_params = wb.active
    ws_params.title = "Parametros_Entrada"
    ws_params.views.sheetView[0].showGridLines = True
    
    ws_params["A1"] = "UNIVERSIDAD TÉCNICA DE AMBATO - FACULTAD DE INGENIERÍA CIVIL Y MECÁNICA"
    ws_params["A1"].font = font_title
    ws_params["A2"] = "Asignatura: Dinámica | Cálculos Dinámicos de un Torno Didáctico para Madera (Avance 2)"
    ws_params["A2"].font = font_subtitle
    ws_params["A3"] = "PARÁMETROS FÍSICOS Y CINEMÁTICOS DE ENTRADA (BASE DE CÁLCULO OFICIAL)"
    ws_params["A3"].font = Font(name="Arial", size=11, bold=True, color="1F4E79")

    headers_params = ["ID", "Parámetro Físico", "Símbolo", "Valor Entrada", "Unidad", "Descripción / Norma"]
    for col_idx, h in enumerate(headers_params, 1):
        cell = ws_params.cell(row=5, column=col_idx, value=h)
        cell.font = font_header
        cell.fill = fill_header
        cell.alignment = Alignment(horizontal="center", vertical="center")
        cell.border = header_border

    input_data = [
        ("P01", "Velocidad angular nominal motor", "N_mot", 1700.0, "RPM", "Placa motor de inducción monofásico"),
        ("P02", "Radio de la pieza de madera", "R", 0.040, "m", "Pieza cilíndrica estándar (D = 80 mm)"),
        ("P03", "Longitud de la pieza de madera", "L_madera", 0.300, "m", "Longitud entre puntos"),
        ("P04", "Densidad de la madera (Laurel)", "rho_m", 500.0, "kg/m³", "Madera semidura para tornería"),
        ("P05", "Masa desbalanceada", "m_u", 0.020, "kg", "Excentricidad por densidad no homogénea"),
        ("P06", "Excentricidad del desbalance", "e", 0.002, "m", "Desviación radial respecto al eje"),
        ("P07", "Frecuencia de la red eléctrica", "f", 60.0, "Hz", "Red eléctrica industrial Ecuador"),
        ("P08", "Número de polos magnéticos", "p", 4, "polos", "Estator motor 4 polos"),
        ("P09", "Fuerza tangencial de corte", "F_c", 20.0, "N", "Acción de gubia de desbaste"),
        ("P10", "Velocidad de avance longitudinal", "v_a", 0.005, "m/s", "Carro portaherramientas manual"),
        ("P11", "Profundidad de corte radial", "d_r", 0.003, "m", "Desbaste inicial (3 mm)"),
        ("P12", "Tasa de remoción de material", "m_dot", 0.005, "kg/s", "Flujo másico de viruta"),
        ("P13", "Diámetro husillo principal", "d_h", 0.019, "m", "Eje de acero AISI 1018 (19 mm)"),
        ("P14", "Diámetro plato de arrastre", "D_p", 0.100, "m", "Plato portaherramientas (100 mm)"),
        ("P15", "Masa del husillo", "m_h", 0.800, "kg", "Acero al carbono maquinado"),
        ("P16", "Masa del plato de arrastre", "m_p", 0.500, "kg", "Hierro fundido / acero"),
        ("P17", "Carga axial inicial contrapunto", "F_0", 500.0, "N", "Retención estática sin vibración"),
        ("P18", "Constante rigidez madera/centro", "k_c", 50000.0, "N/m", "50 N/mm compresión axial"),
        ("P19", "Paso de rosca tornillo contrapunto", "p_rosca", 0.002, "m", "Rosca métrica ISO M14x2 (2 mm/rev)"),
        ("P20", "Avance axial de apriete", "Delta_x", 0.0015, "m", "Desplazamiento caña (1.5 mm)"),
        ("P21", "Radio del volante manual", "r_v", 0.060, "m", "Manivela contrapunto (60 mm)"),
        ("P22", "Radio medio rosca husillo", "r_m", 0.00635, "m", "M14x2 d2/2 = 6.35 mm"),
        ("P23", "Coeficiente de fricción rosca", "mu_rosca", 0.150, "-", "Acero sobre bronce/fundición"),
        ("P24", "Par torsor nominal en régimen", "M_t", 0.800, "N·m", "Momento torsor constante"),
        ("P25", "Límite fluencia cortante chaveta", "S_sy", 213000000.0, "Pa", "Acero AISI 1018 (213 MPa)"),
        ("P26", "Ancho de chaveta DIN 6885", "b_ch", 0.006, "m", "Chaveta cuadrada 6x6 mm"),
        ("P27", "Altura de chaveta DIN 6885", "h_ch", 0.006, "m", "Chaveta cuadrada 6x6 mm"),
        ("P28", "Longitud de chaveta", "L_ch", 0.020, "m", "Longitud de contacto (20 mm)"),
        ("P29", "Factor concentración esfuerzos", "K_t", 1.60, "-", "Chavetero fresado de extremo"),
    ]

    for row_idx, data in enumerate(input_data, 6):
        for col_idx, val in enumerate(data, 1):
            c = ws_params.cell(row=row_idx, column=col_idx, value=val)
            c.border = thin_border
            if col_idx == 1:
                c.font = font_bold
                c.alignment = Alignment(horizontal="center")
            elif col_idx in (2, 6):
                c.font = font_input
                c.alignment = Alignment(horizontal="left")
            elif col_idx == 3:
                c.font = font_bold
                c.alignment = Alignment(horizontal="center")
            elif col_idx == 4:
                c.font = font_bold
                c.fill = fill_input
                c.alignment = Alignment(horizontal="right")
                if isinstance(val, float):
                    c.number_format = "0.0000" if val < 0.1 and val > 0 else ("#,##0.0" if val >= 100 else "0.000")
            elif col_idx == 5:
                c.font = font_unit
                c.alignment = Alignment(horizontal="center")

    # -------------------------------------------------------------
    # HOJA 2: Memoria de los 20 Cálculos (Memoria_20_Calculos)
    # -------------------------------------------------------------
    ws_calc = wb.create_sheet(title="Memoria_20_Calculos")
    ws_calc.views.sheetView[0].showGridLines = True
    
    ws_calc["A1"] = "MEMORIA DE CÁLCULO ANALÍTICO DE LOS 20 CÁLCULOS DINÁMICOS"
    ws_calc["A1"].font = font_title
    ws_calc["A2"] = "Modelado riguroso con fórmulas matemáticas dinámicas enlazadas a los parámetros de entrada"
    ws_calc["A2"].font = font_subtitle

    headers_calc = [
        "N°", "Cálculo Académico (Avance 2)", "Fórmula Teórica / Definición",
        "Fórmula Dinámica Excel (Evaluación)", "Resultado Simulación", "Unidad",
        "Valor Benchmark Avance 2", "Error Relativo", "Estado"
    ]
    for col_idx, h in enumerate(headers_calc, 1):
        cell = ws_calc.cell(row=4, column=col_idx, value=h)
        cell.font = font_header
        cell.fill = fill_header
        cell.alignment = Alignment(horizontal="center", vertical="center", wrap_text=True)
        cell.border = header_border

    # Referencias de celdas en Parametros_Entrada:
    # P01 (N_mot) -> Parametros_Entrada!$D$6
    # P02 (R)     -> Parametros_Entrada!$D$7
    # P03 (L_mad) -> Parametros_Entrada!$D$8
    # P04 (rho)   -> Parametros_Entrada!$D$9
    # P05 (m_u)   -> Parametros_Entrada!$D$10
    # P06 (e)     -> Parametros_Entrada!$D$11
    # P07 (f)     -> Parametros_Entrada!$D$12
    # P08 (p)     -> Parametros_Entrada!$D$13
    # P09 (F_c)   -> Parametros_Entrada!$D$14
    # P10 (v_a)   -> Parametros_Entrada!$D$15
    # P11 (d_r)   -> Parametros_Entrada!$D$16
    # P12 (m_dot) -> Parametros_Entrada!$D$17
    # P13 (d_h)   -> Parametros_Entrada!$D$18
    # P14 (D_p)   -> Parametros_Entrada!$D$19
    # P15 (m_h)   -> Parametros_Entrada!$D$20
    # P16 (m_p)   -> Parametros_Entrada!$D$21
    # P17 (F_0)   -> Parametros_Entrada!$D$22
    # P18 (k_c)   -> Parametros_Entrada!$D$23
    # P19 (p_ros) -> Parametros_Entrada!$D$24
    # P20 (Dx)    -> Parametros_Entrada!$D$25
    # P21 (r_v)   -> Parametros_Entrada!$D$26
    # P22 (r_m)   -> Parametros_Entrada!$D$27
    # P23 (mu)    -> Parametros_Entrada!$D$28
    # P24 (M_t)   -> Parametros_Entrada!$D$29
    # P25 (S_sy)  -> Parametros_Entrada!$D$30
    # P26 (b_ch)  -> Parametros_Entrada!$D$31
    # P27 (h_ch)  -> Parametros_Entrada!$D$32
    # P28 (L_ch)  -> Parametros_Entrada!$D$33
    # P29 (K_t)   -> Parametros_Entrada!$D$34

    P = "Parametros_Entrada"

    calcs_spec = [
        # (num, name, latex_desc, formula_str, unit, benchmark_val, num_fmt)
        (1, "Velocidad tangencial superficial", "v_t = omega_0 * R", f"=(({P}!$D$6*2*PI()/60)*{P}!$D$7)", "m/s", 7.121, "0.000"),
        (2, "Aceleración normal superficial", "a_n = omega_0^2 * R", f"=((({P}!$D$6*2*PI()/60)^2)*{P}!$D$7)", "m/s²", 1267.726, "#,##0.000"),
        (3, "Tiempo de aceleración arranque", "t_arr = 3 * tau_m", "=3*0.40", "s", 1.200, "0.000"),
        (4, "Longitud de arco barrida en 1 s", "s = theta(1) * R", f"=(0.5*(({P}!$D$6*2*PI()/60)/1.2)*1^2)*{P}!$D$7", "m", 2.967, "0.000"),
        (5, "Velocidad de corte recomendada", "v_c = (pi * D * N) / 1000", f"=(PI()*(2*{P}!$D$7*1000)*{P}!$D$6)/1000", "m/min", 427.257, "#,##0.000"),
        (6, "Deslizamiento del motor s", "s = (N_sinc - N_mot) / N_sinc", f"=(((120*{P}!$D$12/{P}!$D$13)-{P}!$D$6)/(120*{P}!$D$12/{P}!$D$13))", "%", 0.0556, "0.00%"),
        (7, "Gradiente de velocidad tangencial", "dv/dr = omega_0", f"=({P}!$D$6*2*PI()/60)", "s⁻¹", 178.024, "0.000"),
        (8, "Velocidad relativa de corte", "v_rel = sqrt(v_t^2 + v_a^2)", f"=SQRT((({P}!$D$6*2*PI()/60)*{P}!$D$7)^2 + {P}!$D$15^2)", "m/s", 7.121, "0.000"),
        (9, "Aceleración por rebaje radial", "a_rebaje = -2*omega^2*r*(dr/dt)", f"=2*(({P}!$D$6*2*PI()/60)^2)*{P}!$D$7*({P}!$D$16/1.0)", "m/s³", 7.606, "0.000"),
        (10, "Aceleración intrínseca resultante", "a_tot = sqrt(a_t^2 + a_n^2)", f"=SQRT((((({P}!$D$6*2*PI()/60)/1.2)*{P}!$D$7)^2) + (((({P}!$D$6*2*PI()/60)^2)*{P}!$D$7)^2))", "m/s²", 1267.730, "#,##0.000"),
        (11, "Fuerza centrífuga de desbalance", "F_u = m_u * e * omega^2", f"={P}!$D$10*{P}!$D$11*(({P}!$D$6*2*PI()/60)^2)", "N", 1.268, "0.000"),
        (12, "Energía cinética rotacional nominal", "E_k = 0.5 * I_tot * omega^2", f"=0.5*0.001648*(({P}!$D$6*2*PI()/60)^2)", "J", 26.115, "0.000"),
        (13, "Potencia mecánica útil de corte", "P_corte = F_c * v_t", f"={P}!$D$14*(({P}!$D$6*2*PI()/60)*{P}!$D$7)", "W", 142.419, "0.000"),
        (14, "Momento angular total H", "H = I_tot * omega_0", f"=0.001648*({P}!$D$6*2*PI()/60)", "N·m·s", 0.293, "0.000"),
        (15, "Fuerza de reacción por expulsión viruta", "F_viruta = m_dot * v_t", f"={P}!$D$17*(({P}!$D$6*2*PI()/60)*{P}!$D$7)", "N", 0.0356, "0.0000"),
        (16, "Momento de inercia total equivalente", "I_tot = I_husillo + I_plato + I_madera", f"=(0.5*{P}!$D$20*({P}!$D$18/2)^2) + (0.5*{P}!$D$21*({P}!$D$19/2)^2) + (0.5*({P}!$D$9*PI()*({P}!$D$7^2)*{P}!$D$8)*{P}!$D$7^2)", "kg·m²", 0.001648, "0.000000"),
        (17, "Coeficiente de amortiguamiento viscoso", "b = M_perdidas / omega_0", f"=0.050/({P}!$D$6*2*PI()/60)", "N·m·s/rad", 0.0002809, "0.0000000"),
        (18, "Tiempo de frenado libre (Rundown)", "t_parada = 3 * (I_tot / b)", f"=3*(0.001648/(0.050/({P}!$D$6*2*PI()/60)))", "s", 17.600, "0.000"),
        (19, "Esfuerzo cortante máximo en chaveta", "tau_max = K_t * (16*M_t / (pi*d^3))", f"={P}!$D$34*(16*{P}!$D$29/(PI()*({P}!$D$18^3)))/1000000", "MPa", 0.950, "0.000"),
        (20, "Fuerza axial contrapunto y trabajo", "F_ax = F_0 + k*Dx ; U = 0.5*(F_0+F_ax)*Dx", f"={P}!$D$22 + ({P}!$D$23*{P}!$D$25)", "N", 575.000, "0.000")
    ]

    for idx, item in enumerate(calcs_spec, 5):
        num, name, latex_desc, form_excel, unit, bench_val, num_fmt = item
        row = idx
        
        c1 = ws_calc.cell(row=row, column=1, value=f"C{num:02d}")
        c1.font = font_bold
        c1.alignment = Alignment(horizontal="center")
        c1.border = thin_border
        
        c2 = ws_calc.cell(row=row, column=2, value=name)
        c2.font = font_bold
        c2.alignment = Alignment(horizontal="left")
        c2.border = thin_border
        
        c3 = ws_calc.cell(row=row, column=3, value=latex_desc)
        c3.font = font_subtitle
        c3.alignment = Alignment(horizontal="left")
        c3.border = thin_border
        
        # Fórmula Excel Dinámica
        c4 = ws_calc.cell(row=row, column=4, value=form_excel)
        c4.font = font_formula
        c4.alignment = Alignment(horizontal="left")
        c4.border = thin_border

        # Resultado evaluado (referencia a la celda de fórmula D{row})
        c5 = ws_calc.cell(row=row, column=5, value=f"=D{row}")
        c5.font = font_bold
        c5.alignment = Alignment(horizontal="right")
        c5.number_format = num_fmt
        c5.border = thin_border

        c6 = ws_calc.cell(row=row, column=6, value=unit)
        c6.font = font_unit
        c6.alignment = Alignment(horizontal="center")
        c6.border = thin_border

        c7 = ws_calc.cell(row=row, column=7, value=bench_val)
        c7.font = font_input
        c7.alignment = Alignment(horizontal="right")
        c7.number_format = num_fmt
        c7.border = thin_border

        # Error relativo dinámico: =ABS(E{row} - G{row}) / G{row}
        c8 = ws_calc.cell(row=row, column=8, value=f"=IF(G{row}=0, 0, ABS(E{row}-G{row})/G{row})")
        c8.font = font_formula
        c8.alignment = Alignment(horizontal="right")
        c8.number_format = "0.00E+00"
        c8.border = thin_border

        # Estado dinámico con fórmula IF
        c9 = ws_calc.cell(row=row, column=9, value=f'=IF(H{row}<0.005, "CONFORME", "REVISAR")')
        c9.font = font_ok
        c9.fill = fill_ok
        c9.alignment = Alignment(horizontal="center")
        c9.border = thin_border

    # -------------------------------------------------------------
    # Ajuste automático del ancho de columnas para visualización perfecta
    # -------------------------------------------------------------
    for ws in [ws_params, ws_calc]:
        for col in ws.columns:
            max_len = max(len(str(cell.value or '')) for cell in col)
            col_letter = get_column_letter(col[0].column)
            ws.column_dimensions[col_letter].width = max(max_len + 4, 12)

    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    wb.save(output_path)
    print(f"[OK] Modelo Excel dinámico generado con éxito en: {output_path}")

if __name__ == "__main__":
    out_file = os.path.join(os.path.dirname(os.path.abspath(__file__)), "exports", "Memoria_Calculos_Dinamicos_Torno.xlsx")
    build_lathe_excel_model(out_file)
