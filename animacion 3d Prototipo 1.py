import numpy as np
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
from matplotlib.colors import LinearSegmentedColormap
import pickle

class Quantum3DAnimationFixed:
    def __init__(self, results, num_qubits=6):
        self.results = results
        self.num_qubits = num_qubits
        
        # Usar los puntos originales sin interpolación compleja
        self.probabilities = sorted(results.keys())
        print(f" Probabilidades a animar: {self.probabilities}")
        
        # Configurar figura
        self.fig = plt.figure(figsize=(16, 10))
        
        # Crear más frames interpolando manualmente
        self.fine_probabilities = self.create_smooth_transition()
        
        # Colormaps
        self.qubit_cmap = LinearSegmentedColormap.from_list('quantum_3d', 
                                                           ['#000000', '#0011ff', '#00ffff', '#ff00ff', '#ff0000'])
        self.entanglement_cmap = LinearSegmentedColormap.from_list('entanglement_glow', 
                                                                  ['#000000', '#00ff00', '#ffff00', '#ff0000'])
        
        # Datos para animación
        self.particles = []
        self.connections = []
        
    def create_smooth_transition(self):
        """Crear transición suave interpolando entre puntos"""
        fine_probs = []
        
        for i in range(len(self.probabilities) - 1):
            p_start = self.probabilities[i]
            p_end = self.probabilities[i + 1]
            
            # Añadir puntos intermedios
            fine_probs.append(p_start)
            for j in range(1, 4):  # 3 puntos intermedios
                interp_p = p_start + (p_end - p_start) * j / 4
                fine_probs.append(interp_p)
        
        fine_probs.append(self.probabilities[-1])
        print(f" Frames totales después de interpolación: {len(fine_probs)}")
        return fine_probs
    
    def calculate_3d_positions(self, p):
        """Calcular posiciones 3D de los qubits"""
        radius = 1.5
        positions = []
        
        # Distribuir qubits en un círculo (2D por simplicidad pero con efecto 3D)
        for i in range(self.num_qubits):
            angle = 2 * np.pi * i / self.num_qubits
            x = radius * np.cos(angle)
            y = radius * np.sin(angle)
            z = 0.5 * np.sin(p * np.pi * 2)  # Pequeña variación en Z para efecto 3D
            
            positions.append((x, y, z))
        
        return positions
    
    def get_current_entropy(self, p):
        """Obtener entropía actual para una probabilidad p"""
        # Encontrar el punto más cercano en los resultados originales
        closest_p = min(self.results.keys(), key=lambda x: abs(x - p))
        avg_entanglement = self.results[closest_p]['average']
        return np.mean(avg_entanglement[-5:])
    
    def draw_quantum_scene(self, p):
        """Dibujar escena cuántica completa"""
        self.fig.clear()
        
        # Crear subplots
        ax_3d = self.fig.add_subplot(221, projection='3d')
        ax_graph = self.fig.add_subplot(222)
        ax_time = self.fig.add_subplot(223)
        ax_info = self.fig.add_subplot(224)
        
        # Configurar 3D
        ax_3d.set_xlim(-2, 2)
        ax_3d.set_ylim(-2, 2)
        ax_3d.set_zlim(-2, 2)
        ax_3d.set_facecolor('black')
        ax_3d.grid(True, alpha=0.3)
        
        # Obtener datos
        current_entropy = self.get_current_entropy(p)
        positions = self.calculate_3d_positions(p)
        
        # Dibujar qubits en 3D
        self.draw_3d_qubits(ax_3d, positions, p, current_entropy)
        
        # Dibujar partículas y conexiones
        self.draw_particles_and_connections(ax_3d, positions, current_entropy)
        
        # Dibujar gráficas
        self.draw_transition_graph(ax_graph, p)
        self.draw_time_evolution(ax_time, p)
        self.draw_info_panel(ax_info, p, current_entropy)
        
        # Título principal
        self.fig.suptitle(f'TRANSICIÓN DE FASE CUÁNTICA 3D\np = {p:.3f}, Entropía = {current_entropy:.3f}', 
                         fontsize=14, fontweight='bold', color='white')
        
        plt.tight_layout()
    
    def draw_3d_qubits(self, ax, positions, p, current_entropy):
        """Dibujar qubits en 3D"""
        for i, (x, y, z) in enumerate(positions):
            # Tamaño y color basado en la fase
            if p < 0.3:
                size = 100 + 50 * np.sin(i + p * 10)
                color_val = 0.8
                glow_alpha = 0.6
            elif p > 0.7:
                size = 80
                color_val = 0.3
                glow_alpha = 0.2
            else:
                size = 90 + 30 * np.sin(i * 2 + p * 8)
                color_val = 0.5 + 0.3 * (0.5 - abs(p - 0.5))
                glow_alpha = 0.4
            
            color = self.qubit_cmap(color_val)
            
            # Glow effect
            ax.scatter([x], [y], [z], s=size*3, alpha=glow_alpha, 
                      color=color, marker='o')
            
            # Qubit principal
            ax.scatter([x], [y], [z], s=size, alpha=0.9,
                      color=color, marker='o', edgecolors='white', linewidth=2)
            
            # Etiqueta
            ax.text(x, y, z, f'q{i}', fontsize=8, color='white', 
                   ha='center', va='center')
    
    def draw_particles_and_connections(self, ax, positions, current_entropy):
        """Dibujar partículas y conexiones de entrelazamiento"""
        # Solo dibujar si hay suficiente entrelazamiento
        if current_entropy < 0.2:
            return
        
        num_particles = int(15 * current_entropy)
        
        for i in range(num_particles):
            # Seleccionar dos qubits aleatorios para conectar
            idx1, idx2 = np.random.choice(len(positions), 2, replace=False)
            pos1 = np.array(positions[idx1])
            pos2 = np.array(positions[idx2])
            
            # Crear partículas a lo largo de la línea
            num_segments = 3
            for seg in range(num_segments):
                t = seg / num_segments
                particle_pos = pos1 + t * (pos2 - pos1)
                
                # Añadir algo de ruido para efecto 3D
                particle_pos += 0.1 * np.random.randn(3)
                
                color_val = 0.3 + 0.7 * current_entropy
                color = self.entanglement_cmap(color_val)
                
                ax.scatter([particle_pos[0]], [particle_pos[1]], [particle_pos[2]],
                          s=30 + 50 * current_entropy, alpha=0.7,
                          color=color, marker='o')
            
            # Dibujar línea de conexión
            if current_entropy > 0.4:
                line_width = 1 + 3 * current_entropy
                ax.plot([pos1[0], pos2[0]], [pos1[1], pos2[1]], [pos1[2], pos2[2]],
                       color='cyan', alpha=0.3 + 0.4 * current_entropy,
                       linewidth=line_width)
    
    def draw_transition_graph(self, ax, p):
        """Dibujar gráfica de transición"""
        probabilities = sorted(self.results.keys())
        final_entropies = []
        
        for prob in probabilities:
            avg_entanglement = self.results[prob]['average']
            final_entropy = np.mean(avg_entanglement[-5:])
            final_entropies.append(final_entropy)
        
        ax.plot(probabilities, final_entropies, 'o-', color='cyan', 
                linewidth=3, markersize=6)
        
        # Marcar punto actual
        closest_idx = min(range(len(probabilities)), 
                         key=lambda i: abs(probabilities[i] - p))
        ax.plot(probabilities[closest_idx], final_entropies[closest_idx], 'ro', 
                markersize=10, markerfacecolor='red')
        
        ax.set_xlabel('Probabilidad de Medida (p)')
        ax.set_ylabel('Entropía de Entrelazamiento')
        ax.set_title('Curva de Transición')
        ax.grid(True, alpha=0.3)
        ax.set_facecolor('black')
    
    def draw_time_evolution(self, ax, p):
        """Dibujar evolución temporal"""
        closest_p = min(self.results.keys(), key=lambda x: abs(x - p))
        time_data = self.results[closest_p]['average']
        
        ax.plot(range(len(time_data)), time_data, color='magenta', linewidth=2)
        ax.set_xlabel('Tiempo (pasos)')
        ax.set_ylabel('Entropía')
        ax.set_title('Evolución Temporal')
        ax.grid(True, alpha=0.3)
        ax.set_facecolor('black')
    
    def draw_info_panel(self, ax, p, current_entropy):
        """Dibujar panel de información"""
        ax.axis('off')
        
        # Determinar fase
        if p < 0.3:
            phase = "FASE ENTRELAZADA"
            color = 'cyan'
        elif p > 0.7:
            phase = "FASE DESENTRELAZADA"
            color = 'red'
        else:
            phase = "REGIMEN CRÍTICO"
            color = 'magenta'
        
        info_text = f"""🌌 {phase}

 Probabilidad: {p:.3f}
 Entropía: {current_entropy:.3f}

 Partículas: {int(15 * current_entropy)}
 Conexiones: { 'Muchas' if current_entropy > 0.4 else 'Pocas' }

{' Sistema muy entrelazado' if p < 0.3 else 
  ' Transición crítica' if p < 0.7 else 
  ' Sistema desentrelazado'}"""
        
        ax.text(0.5, 0.5, info_text, transform=ax.transAxes,
               ha='center', va='center', fontsize=11, color='white',
               bbox=dict(boxstyle="round,pad=1", facecolor='navy', alpha=0.8))
    
    def animate(self, frame):
        """Función de animación"""
        p = self.fine_probabilities[frame % len(self.fine_probabilities)]
        self.draw_quantum_scene(p)
        return []
    
    def create_animation(self, filename='quantum_3d_fixed.gif'):
        """Crear y guardar la animación"""
        print("🎬 Creando animación 3D corregida...")
        
        # Crear animación
        anim = FuncAnimation(self.fig, self.animate, 
                           frames=len(self.fine_probabilities),
                           interval=200, blit=False, repeat=True)
        
        # Guardar como GIF
        try:
            print("💾 Guardando animación...")
            anim.save(filename, writer='pillow', fps=5, dpi=100)
            print(f"✅ Animación guardada como: {filename}")
        except Exception as e:
            print(f"❌ Error al guardar: {e}")
            print("💡 Mostrando animación en pantalla...")
            plt.show()
        
        return anim

def main():
    """Función principal"""
    print("🌌 INICIANDO SIMULACIÓN CUÁNTICA 3D CORREGIDA")
    print("=" * 50)
    
    try:
        # Cargar resultados
        with open('mipt_simulation_results.pkl', 'rb') as f:
            results = pickle.load(f)
        
        print("✅ Datos cargados correctamente")
        print(f"📊 Número de puntos de probabilidad: {len(results)}")
        
        # Crear animación
        animator = Quantum3DAnimationFixed(results, num_qubits=6)
        animation = animator.create_animation('quantum_3d_fixed.gif')
        
        print("\n🎉 ¡ANIMACIÓN COMPLETADA!")
        print("✨ Características:")
        print("   - Visualización 3D simplificada pero efectiva")
        print("   - Partículas que muestran el entrelazamiento")
        print("   - Conexiones entre qubits")
        print("   - 4 paneles de información")
        print("   - Animación suave con interpolación")
        
    
        plt.show()
        
    except FileNotFoundError:
        print("❌ Error: Archivo 'mipt_simulation_results.pkl' no encontrado")
        print("💡 Ejecuta primero: python mipt_simulation.py")
    except Exception as e:
        print(f"❌ Error inesperado: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()