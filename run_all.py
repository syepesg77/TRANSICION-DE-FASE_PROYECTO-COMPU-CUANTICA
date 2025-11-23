"""
Script principal para ejecutar todo el proyecto MIPT
"""
import subprocess
import sys
import os

def run_script(script_name):
    """Ejecutar un script y capturar su salida"""
    print(f"\n{'='*50}")
    print(f"Ejecutando: {script_name}")
    print(f"{'='*50}")
    
    try:
        result = subprocess.run([sys.executable, script_name], 
                              capture_output=True, text=True)
        print(result.stdout)
        if result.stderr:
            print("Errores:", result.stderr)
        return result.returncode == 0
    except Exception as e:
        print(f"Error ejecutando {script_name}: {e}")
        return False

def main():
    """Ejecutar todos los scripts en orden"""
    print("🚀 INICIANDO PROYECTO MIPT - EJECUCIÓN COMPLETA")
    
    scripts = [
        "mipt_simulation.py",
        "mipt_animation.py"
    ]
    
    for script in scripts:
        if not run_script(script):
            print(f"❌ Falló la ejecución de {script}")
            break
        print(f"✅ {script} completado exitosamente")
    
    print("\n" + "="*50)
    print("PROYECTO MIPT COMPLETADO")
    print("="*50)
    print("📊 Resultados generados:")
    print("   - mipt_simulation_results.pkl (datos de simulación)")
    print("   - mipt_quick_plot.png (gráfica estática)")
    print("   - mipt_animation.gif (animación)")
    print("\n🎯 ¡Listo para el siguiente paso!")

if __name__ == "__main__":
    main()