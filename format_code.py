#!/usr/bin/env python3
"""
Script para formatear y verificar el código del proyecto.

Uso:
    python format_code.py --format    # Formatear código con Black
    python format_code.py --lint      # Verificar código con flake8
    python format_code.py --all       # Formatear y verificar
"""

import argparse
import subprocess
import sys


def run_black():
    """Ejecuta Black para formatear el código."""
    print("🔧 Formateando código con Black...")
    result = subprocess.run(["black", "."], capture_output=True, text=True)

    if result.returncode == 0:
        print("✅ Formateo completado exitosamente")
        if result.stdout:
            print(result.stdout)
    else:
        print("❌ Error en el formateo:")
        print(result.stderr)
        return False
    return True


def run_flake8():
    """Ejecuta flake8 para verificar el código."""
    print("🔍 Verificando código con flake8...")
    result = subprocess.run(["flake8", "."], capture_output=True, text=True)

    if result.returncode == 0:
        print("✅ No se encontraron problemas de linting")
    else:
        print("⚠️  Se encontraron problemas de linting:")
        print(result.stdout)
        return False
    return True


def main():
    parser = argparse.ArgumentParser(description="Formatear y verificar código")
    parser.add_argument(
        "--format", action="store_true", help="Formatear código con Black"
    )
    parser.add_argument(
        "--lint", action="store_true", help="Verificar código con flake8"
    )
    parser.add_argument(
        "--all", action="store_true", help="Formatear y verificar código"
    )

    args = parser.parse_args()

    if not any([args.format, args.lint, args.all]):
        parser.print_help()
        return

    success = True

    if args.format or args.all:
        success &= run_black()

    if args.lint or args.all:
        success &= run_flake8()

    if success:
        print("\n🎉 Todas las verificaciones pasaron exitosamente")
        sys.exit(0)
    else:
        print("\n💥 Algunas verificaciones fallaron")
        sys.exit(1)


if __name__ == "__main__":
    main()
