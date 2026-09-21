"""
Generador del icono ultraminimalista para el Simulador Dinámico del Torno.
Genera resoluciones múltiples para Windows .ico (16, 24, 32, 48, 64, 128, 256)
y versión .png de alta fidelidad.
"""

from PIL import Image, ImageDraw, ImageFilter
import math
import os

def generate_lathe_icon():
    # Renderizamos a 1024x1024 con supersampling 4x para nitidez absoluta
    size = 1024
    img = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)

    # 1. Fondo Squircle redondeado (Dark slate midnight)
    pad = 48
    corner_r = 210
    bg_box = [pad, pad, size - pad, size - pad]
    # Sombra difusa exterior
    shadow = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    sdraw = ImageDraw.Draw(shadow)
    sdraw.rounded_rectangle(bg_box, radius=corner_r, fill=(0, 0, 0, 160))
    shadow = shadow.filter(ImageFilter.GaussianBlur(radius=28))
    img = Image.alpha_composite(shadow, img)
    draw = ImageDraw.Draw(img)

    # Cuerpo del squircle
    draw.rounded_rectangle(bg_box, radius=corner_r, fill=(16, 18, 26, 255), outline=(42, 48, 68, 255), width=10)

    # 2. Eje central de simetría (línea discontinua de alta precisión)
    cy = 512
    for x in range(120, 904, 28):
        draw.line([(x, cy), (min(x + 16, 904), cy)], fill=(55, 65, 88, 255), width=4)

    # 3. Plato / Husillo (Headstock / Chuck) a la izquierda
    chuck_x1, chuck_x2 = 180, 290
    chuck_y1, chuck_y2 = 270, 754
    draw.rounded_rectangle([chuck_x1, chuck_y1, chuck_x2, chuck_y2], radius=24, fill=(28, 34, 48, 255), outline=(0, 229, 255, 255), width=8)
    
    # Mordazas del plato (Jaws)
    draw.rectangle([chuck_x2 - 20, 310, chuck_x2 + 14, 370], fill=(0, 229, 255, 255))
    draw.rectangle([chuck_x2 - 20, 654, chuck_x2 + 14, 714], fill=(0, 229, 255, 255))

    # 4. Pieza de madera torneada (Workpiece) en el centro
    # Sección 1: Cilindro mayor torneado
    w1_x1, w1_x2 = 290, 520
    w1_y1, w1_y2 = 362, 662
    draw.rounded_rectangle([w1_x1, w1_y1, w1_x2, w1_y2], radius=16, fill=(234, 138, 34, 255), outline=(255, 183, 77, 255), width=6)
    
    # Resalte de brillo en la madera
    draw.line([(w1_x1 + 10, 420), (w1_x2 - 10, 420)], fill=(255, 213, 140, 180), width=8)

    # Sección 2: Cilindro rebajado (diámetro menor maquinado)
    w2_x1, w2_x2 = 520, 710
    w2_y1, w2_y2 = 412, 612
    draw.rounded_rectangle([w2_x1, w2_y1, w2_x2, w2_y2], radius=14, fill=(217, 119, 6, 255), outline=(251, 191, 36, 255), width=6)
    draw.line([(w2_x1 + 10, 452), (w2_x2 - 10, 452)], fill=(254, 240, 138, 160), width=6)

    # 5. Punto giratorio del contrapunto (Live Center) a la derecha
    tip_x, base_x = 710, 800
    cone_points = [(tip_x, cy), (base_x, cy - 90), (base_x, cy + 90)]
    draw.polygon(cone_points, fill=(148, 163, 184, 255), outline=(241, 245, 249, 255))

    # Caña del contrapunto
    draw.rounded_rectangle([base_x, cy - 70, 880, cy + 70], radius=12, fill=(51, 65, 85, 255), outline=(100, 116, 139, 255), width=6)

    # 6. Arco de Dinámica Rotacional (Vector velocidad angular ω)
    arc_box = [330, 250, 670, 774]
    draw.arc(arc_box, start=35, end=195, fill=(0, 229, 255, 255), width=16)

    # Flecha del vector de giro en la punta del arco
    rad = math.radians(35)
    cx_arc, cy_arc = 500, 512
    rx_arc, ry_arc = 170, 262
    ax = cx_arc + rx_arc * math.cos(rad)
    ay = cy_arc + ry_arc * math.sin(rad)
    
    arrow_pts = [
        (ax, ay),
        (ax - 28, ay + 38),
        (ax + 12, ay + 32)
    ]
    draw.polygon(arrow_pts, fill=(0, 229, 255, 255))

    # Guardar versiones en alta resolución y multi-tamaño para Windows
    out_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "resources")
    os.makedirs(out_dir, exist_ok=True)

    png_path = os.path.join(out_dir, "icon.png")
    ico_path = os.path.join(out_dir, "icon.ico")

    # Guardar PNG a 256x256 (downsampling suave con Lanczos)
    img_256 = img.resize((256, 256), Image.Resampling.LANCZOS)
    img_256.save(png_path, "PNG")
    print(f"[OK] Icono PNG generado en: {png_path}")

    # Guardar ICO multi-resolución
    sizes = [(16, 16), (24, 24), (32, 32), (48, 48), (64, 64), (128, 128), (256, 256)]
    img_256.save(ico_path, format="ICO", sizes=sizes)
    print(f"[OK] Icono ICO multi-resolución generado en: {ico_path}")

if __name__ == "__main__":
    generate_lathe_icon()
