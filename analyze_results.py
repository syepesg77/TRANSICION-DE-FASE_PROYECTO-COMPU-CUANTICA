import numpy as np
import matplotlib.pyplot as plt
import pickle

def create_publication_quality_plot():
    """Crear una gráfica de calidad para publicaciones"""
    

    with open('mipt_simulation_results.pkl', 'rb') as f:
        results = pickle.load(f)
    
    probabilities = sorted(results.keys())
    final_entropies = []
    errors = []
    
    for p in probabilities:
        avg_entanglement = results[p]['average']
        final_entropy = np.mean(avg_entanglement[-5:])
        final_entropies.append(final_entropy)
        
        # Calcular error estándar
        all_final = [np.mean(realization[-5:]) for realization in results[p]['all_realizations']]
        errors.append(np.std(all_final))
    
    # Crear gráfica profesional
    plt.figure(figsize(12, 8))
    
    # Gráfica principal con barras de error
    plt.errorbar(probabilities, final_entropies, yerr=errors, 
                fmt='o-', color='navy', linewidth=3, markersize=8,
                capsize=5, capthick=2, label='Datos de simulación')
    
    # Resaltar las fases
    plt.axvspan(0, 0.3, alpha=0.15, color='blue', label='Fase Entrelazada\n(Ley de Volumen)')
    plt.axvspan(0.3, 0.7, alpha=0.15, color='purple', label='Regimen Crítico')
    plt.axvspan(0.7, 1.0, alpha=0.15, color='red', label='Fase Desentrelazada\n(Ley de Área)')
    
    # Línea en el punto crítico
    critical_point = 0.5  # Puedes ajustar esto basado en tus datos
    plt.axvline(x=critical_point, color='black', linestyle='--', 
                alpha=0.7, linewidth=2, label=f'Punto crítico p_c ≈ {critical_point}')
    
    # Personalización
    plt.xlabel('Probabilidad de Medida (p)', fontsize=16, fontweight='bold')
    plt.ylabel('Entropía de Entrelazamiento Promedio', fontsize=16, fontweight='bold')
    plt.title('Transición de Fase Inducida por Medida (MIPT)\nSimulación con Circuitos Cuánticos Aleatorios', 
              fontsize=18, fontweight='bold', pad=20)
    
    plt.grid(True, alpha=0.3)
    plt.legend(fontsize=12, loc='upper right', framealpha=0.9)
    
    # Añadir anotaciones explicativas
    plt.annotate('Entrelazamiento extensivo\ncorrelaciones no-locales', 
                 xy=(0.15, 0.7), xytext=(0.05, 0.85),
                 arrowprops=dict(arrowstyle='->', color='blue', lw=2),
                 fontsize=11, ha='center')
    
    plt.annotate('Entrelazamiento localizado\ncorrelaciones locales', 
                 xy=(0.85, 0.25), xytext=(0.7, 0.4),
                 arrowprops=dict(arrowstyle='->', color='red', lw=2),
                 fontsize=11, ha='center')
    
    plt.tight_layout()
    plt.savefig('mipt_publication_quality.png', dpi=300, bbox_inches='tight')
    plt.show()
    
    # Análisis cuantitativo
    print("\n" + "="*60)
    print("ANÁLISIS CUANTITATIVO DE LA TRANSICIÓN DE FASE")
    print("="*60)
    
    # Encontrar el punto crítico aproximado
    max_slope_idx = np.argmax(np.abs(np.diff(final_entropies)))
    p_critical = (probabilities[max_slope_idx] + probabilities[max_slope_idx + 1]) / 2
    
    print(f"• Punto crítico estimado (p_c): {p_critical:.3f}")
    print(f"• Entropía en fase entrelazada (p=0): {final_entropies[0]:.3f}")
    print(f"• Entropía en fase desentrelazada (p=1): {final_entropies[-1]:.3f}")
    print(f"• Caída de entropía en la transición: {final_entropies[0] - final_entropies[-1]:.3f}")
    
    return p_critical

if __name__ == "__main__":
    p_c = create_publication_quality_plot()