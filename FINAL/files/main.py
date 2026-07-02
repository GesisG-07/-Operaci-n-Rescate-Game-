"""
main.py — Punto de entrada de "Operación Rescate: Cumbres Salvajes"

Este archivo unifica:
  - Algoritmo_1.py   -> motor de backtracking con poda (Solange / Genesis)
  - interfaz_1.py    -> interfaz gráfica en Pygame, menú, misiones, drag&drop
                         y Harmony Meter (Jordy)

Responsabilidad de main.py:
  1. Verificar que el motor de backtracking esté disponible antes de arrancar
     el juego (si falta, avisar con un mensaje claro en vez de un traceback feo).
  2. Verificar que existan los assets necesarios (fondos y retratos).
  3. Levantar la ventana del juego (Game) y arrancar el bucle principal.

Ejecutar:
    python main.py

Estructura de carpetas esperada:
    proyecto/
        main.py
        Algoritmo_1.py
        interfaz_1.py
        assets/
            bg_bosque.png
            bg_nieve.png
            bg_montana.png
            bg_avalancha.png
            Ana.png, Luis.png, Marta.png, Carlos.png, Sofía.png, Tomás.png
"""

import sys
from pathlib import Path

BASE_DIR = Path(__file__).parent
ASSETS_DIR = BASE_DIR / "assets"

# Assets mínimos que la interfaz necesita para no crashear al cargar imágenes.
FONDOS_REQUERIDOS = [
    "bg_bosque.png",
    "bg_nieve.png",
    "bg_montana.png",
    "bg_avalancha.png",
]
RETRATOS_REQUERIDOS = [
    "Ana.png", "Luis.png", "Marta.png",
    "Carlos.png", "Sofia.png", "Tomas.png",
]


def verificar_motor_backtracking() -> bool:
    """Confirma que Algoritmo_1.py exista y exponga resolver_distribucion."""
    try:
        from Algoritmo_1 import resolver_distribucion  # noqa: F401
        return True
    except ModuleNotFoundError:
        print("❌ No se encontró 'Algoritmo_1.py'. Debe estar en la misma carpeta que main.py.")
        return False
    except ImportError:
        print("❌ 'Algoritmo_1.py' existe pero no tiene la función 'resolver_distribucion'.")
        return False


def verificar_assets() -> bool:
    """Confirma que existan los fondos y retratos que la interfaz va a cargar."""
    faltantes = [
        nombre for nombre in FONDOS_REQUERIDOS + RETRATOS_REQUERIDOS
        if not (ASSETS_DIR / nombre).exists()
    ]

    if faltantes:
        print("❌ Faltan los siguientes archivos en la carpeta 'assets/':")
        for nombre in faltantes:
            print(f"   - {nombre}")
        return False

    return True


def main() -> None:
    print("=" * 50)
    print("OPERACIÓN RESCATE: CUMBRES SALVAJES")
    print("Organización óptima de equipos (Backtracking + Poda)")
    print("=" * 50)

    motor_ok = verificar_motor_backtracking()
    assets_ok = verificar_assets()

    if not assets_ok:
        print("\nNo se puede iniciar el juego sin los assets. Agrega las imágenes faltantes y vuelve a intentar.")
        sys.exit(1)

    if not motor_ok:
        print("\n⚠️ El juego va a abrir, pero el botón 'ANALIZAR IA' no va a funcionar")
        print("   hasta que 'Algoritmo_1.py' esté presente y correcto.\n")
    else:
        print("\n✅ Motor de backtracking conectado correctamente.")
        print("✅ Assets encontrados.")
        print("\nIniciando interfaz...\n")

    # Import diferido: así los mensajes de verificación de arriba se muestran
    # ANTES de que Pygame abra la ventana.
    from interfaz_1 import Game

    Game().run()


if __name__ == "__main__":
    main()
