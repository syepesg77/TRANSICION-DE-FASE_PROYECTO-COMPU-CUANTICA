import numpy as np
import matplotlib.pyplot as plt
import pickle

def create_time_evolution_plot():
    """Crear gráfica de evolución temporal con manejo robusto de errores"""
    
    try:
        # Cargar resultados
        with open('mipt_simulation_results.pkl', 'rb') as f:
            results = pickle.load(f)
        
        print("Datos cargados exitosamente")
        print(f"Probabilidades disponibles: {list(results.keys())}")
        
        # Configurar la figura
        plt.figure(figsize=(12, 8))
        
        # Seleccionar algunas probabilidades representativas
        all_probs = sorted(results.keys())
        # Escoger 4 puntos: bajo, medio-bajo, medio-alto, alto
        selected_probs = []
        if len(all_probs) >= 4:
            selected_probs = [all_probs[0], all_probs[len(all_probs)//3], 
                            all_probs[2*len(all_probs)//3], all_probs[-1]]
        else:
            selected_probs = all_probs
        
        print(f"Graficando probabilidades: {selected_probs}")
        
        # Colores distintivos
        colors = ['blue', 'green', 'orange', 'red', 'purple', 'brown']
        
        # Graficar cada probabilidad seleccionada
        for i, p in enumerate(selected_probs):
            if i < len(colors):  # Asegurar que no nos salimos de la lista de colores
                avg_entanglement = results[p]['average']
                time_steps = range(len(avg_entanglement))
                
                plt.plot(time_steps, avg_entanglement, 
                        color=colors[i], 
                        linewidth=3,
                        marker='o',
                        markersize=4,
                        label=f'p = {p:.2f}')
        
        # Personalizar la gráfica
        plt.xlabel('Tiempo (Pasos del Circuito)', fontsize=14, fontweight='bold')
        plt.ylabel('Entropía de Entrelazamiento', fontsize=14, fontweight='bold')
        plt.title('Evolución Temporal de la Entropía para Diferentes Probabilidades de Medida', 
                 fontsize=16, fontweight='bold', pad=20)
        
        plt.legend(fontsize=12)
        plt.grid(True, alpha=0.3)
        plt.xlim(0, None)
        plt.ylim(0, 1)
        
        # Añadir anotaciones explicativas
        plt.text(0.02, 0.98, 'Comportamiento esperado:\n• p baja: Entropía alta y estable\n• p alta: Entropía baja y estable\n• p crítica: Fluctuaciones', 
                transform=plt.gca().transAxes, fontsize=11,
                verticalalignment='top',
                bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.8))
        
        plt.tight_layout()
        
        # Guardar la gráfica
        plt.savefig('time_evolution.png', dpi=300, bbox_inches='tight')
        print("Gráfica guardada como 'time_evolution.png'")
        
        # Mostrar la gráfica
        plt.show()
        
        return True
        
    except FileNotFoundError:
        print("ERROR: No se encuentra 'mipt_simulation_results.pkl'")
        print("Asegúrate de que el archivo esté en la misma carpeta")
        return False
        
    except Exception as e:
        print(f"ERROR: {e}")
        return False

# Versión alternativa si la primera no funciona
def create_simple_time_plot():
    """Versión simplificada para debugging"""
    
    try:
        with open('mipt_simulation_results.pkl', 'rb') as f:
            results = pickle.load(f)
        
        plt.figure(figsize=(10, 6))
        
        # Graficar todas las probabilidades
        for p in sorted(results.keys()):
            data = results[p]['average']
            plt.plot(range(len(data)), data, label=f'p={p:.2f}')
        
        plt.xlabel('Tiempo')
        plt.ylabel('Entropía')
        plt.legend()
        plt.grid(True)
        plt.savefig('time_evolution_simple.png', dpi=300, bbox_inches='tight')
        plt.show()
        print("Gráfica simple guardada como 'time_evolution_simple.png'")
        
    except Exception as e:
        print(f"Error en versión simple: {e}")

if __name__ == "__main__":
    print("Generando gráfica de evolución temporal...")
    
    if not create_time_evolution_plot():
        print("Intentando con método alternativo...")
        create_simple_time_plot()