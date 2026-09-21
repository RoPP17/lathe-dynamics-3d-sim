"""
SIMULADOR DINÁMICO 3D DEL TORNO DIDÁCTICO PARA MADERA
Asignatura: Dinámica - FICM - Universidad Técnica de Ambato
Tema: Cálculos Dinámicos de un Torno Didáctico para Madera (Avance 2)
Autor: Roberto Andrés Pepe Sánchez et al.

Punto de entrada principal para ejecución local y compatibilidad con PyCharm.
"""

import sys
import os

# Asegurar que el directorio raíz de Parte_Simulacion esté en sys.path (compatible con PyInstaller)
if getattr(sys, "frozen", False) and hasattr(sys, "_MEIPASS"):
    BASE_DIR = sys._MEIPASS
else:
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))

if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

from PyQt6.QtWidgets import QApplication, QMessageBox
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QIcon
from ui.main_window import MainWindow


def main():
    """Función principal de inicio del simulador dinámico."""
    # Configuración de identificación para la barra de tareas de Windows
    if sys.platform == "win32":
        try:
            import ctypes
            myappid = "uta.mecanica.dinamica.torno.3d.v2"
            ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(myappid)
        except Exception:
            pass

    # Configuración de renderizado y escalado para pantallas High-DPI
    QApplication.setHighDpiScaleFactorRoundingPolicy(
        Qt.HighDpiScaleFactorRoundingPolicy.PassThrough
    )

    app = QApplication(sys.argv)
    app.setApplicationName("Simulador Dinámico del Torno - Dinámica UTA")
    app.setOrganizationName("Universidad Técnica de Ambato")

    # Icono aplicativo
    icon_path = os.path.join(BASE_DIR, "resources", "icon.ico")
    if not os.path.exists(icon_path):
        icon_path = os.path.join(BASE_DIR, "resources", "icon.png")
    if os.path.exists(icon_path):
        app.setWindowIcon(QIcon(icon_path))

    try:
        window = MainWindow()
        window.show()
        # Iniciar reproducción automática del Caso Base sin pop-up de inicio
        window.load_case_avance2(show_msg=False)
        sys.exit(app.exec())
    except Exception as e:
        import traceback
        err_msg = f"Error crítico durante la ejecución de la simulación:\n\n{str(e)}\n\nDetalles técnicos:\n{traceback.format_exc()}"
        print(err_msg, file=sys.stderr)
        QMessageBox.critical(None, "Error del Simulador", err_msg)
        sys.exit(1)


if __name__ == "__main__":
    main()
