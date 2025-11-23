import numpy as np
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
import matplotlib.patches as patches
from matplotlib.colors import LinearSegmentedColormap
import pickle

class QuantumAnimation:
    def __init__(self, results, num_qubits=6):
        self.results = results
        self.num_qubits = num_qubits
        self.probabilities = sorted(results.keys())
        
        # Configurar figura con fondo oscuro para mejor contraste
        plt.style.use('dark_background')
        self.fig = plt.figure(figsize=(16, 10))
        
        # Crear subplots con disposición más visual
        self.ax_main = plt.subplot2grid((3, 4), (0, 0), colspan=4, rowspan=2)  # Visualización principal
        self.ax_graph = plt.subplot2grid((3, 4), (2, 0), colspan=2)  # Gráfica de transición
        self.ax_time = plt.subplot2grid((3, 4), (2, 2), colspan=2)   # Evolución temporal
        
        # Colormap más vibrante
        self.cmap = LinearSegmentedColormap.from_list('quantum_glow', 
                                                     ['#000000', '#0011ff', '#00ffff', '#ff00ff', '#ff0000'])
        
        # Estados de los qubits para la visualización
        self.qubit_positions = self.calculate_qubit_positions()
        
        # Configuración inicial
        self.setup_visualization()
    
    def calculate_qubit_positions(self):
        """Calcular posiciones en forma de arco para los qubits"""
        angles = np.linspace(0, np.pi, self.num_qubits)
        radius = 3
        x = radius * np.cos(angles)
        y = radius * np.sin(angles) + 2
        return list(zip(x, y))
    
    def setup_visualization(self):
        """Configurar la visualización inicial"""
        self.ax_main.set_xlim(-4, 4)
        self.ax_main.set_ylim(-1, 5)
        self.ax_main.set_aspect('equal')
        self.ax_main.axis('off')
        self.ax_main.set_title('EVOLUCIÓN CUÁNTICA - TRANSICIÓN DE FASE', 
                              fontsize=16, fontweight='bold', pad=20, color='white')
    
    def draw_quantum_system(self, p, current_entropy):
        """Dibujar el sistema cuántico completo"""
        self.ax_main.clear()
        self.ax_main.set_xlim(-4, 4)
        self.ax_main.set_ylim(-1, 5)
        self.ax_main.axis('off')
        
        # Determinar fase actual
        if p < 0.3:
            phase = "FASE ENTRELAZADA"
            phase_color = '#00ffff'
            bg_color = 'navy'
        elif p > 0.7:
            phase = "FASE DESENTRELAZADA" 
            phase_color = '#ff4444'
            bg_color = 'darkred'
        else:
            phase = "REGIMEN CRÍTICO"
            phase_color = '#ff00ff'
            bg_color = 'purple'
        
        # Fondo de fase
        self.ax_main.add_patch(patches.Rectangle((-4, -1), 8, 6, 
                                               color=bg_color, alpha=0.2))
        
        # Título con información de fase
        self.ax_main.text(0, 4.5, phase, 
                         ha='center', va='center', fontsize=18, 
                         fontweight='bold', color=phase_color,
                         bbox=dict(boxstyle="round,pad=1", facecolor='black', alpha=0.8))
        
        # Información numérica
        info_text = f'p = {p:.2f}\nEntropía = {current_entropy:.2f}'
        self.ax_main.text(-3.5, 4, info_text, 
                         ha='left', va='top', fontsize=12, 
                         bbox=dict(boxstyle="round,pad=0.5", facecolor='black'))
        
        # Dibujar qubits con efectos visuales
        self.draw_qubits_with_effects(p, current_entropy)
        
        # Dibujar campo cuántico
        self.draw_quantum_field(current_entropy)
    
    def draw_qubits_with_effects(self, p, current_entropy):
        """Dibujar qubits con efectos visuales avanzados"""
        
        for i, (x, y) in enumerate(self.qubit_positions):
            # Calcular propiedades del qubit
            if p < 0.3:
                # Fase entrelazada: qubits muy activos
                size = 0.4 + 0.3 * np.sin(i + p * 10)
                glow_size = size + 0.2
                color_intensity = 0.7 + 0.3 * np.sin(i * 2 + p * 8)
            elif p > 0.7:
                # Fase desentrelazada: qubits quietos
                size = 0.3
                glow_size = size + 0.1
                color_intensity = 0.3
            else:
                # Régimen crítico: comportamiento intermedio
                size = 0.35 + 0.1 * np.sin(i * 3 + p * 12)
                glow_size = size + 0.15
                color_intensity = 0.5 + 0.2 * np.sin(i + p * 6)
            
            color = self.cmap(color_intensity)
            
            # Efecto de glow
            glow = patches.Circle((x, y), glow_size, 
                                facecolor=color, alpha=0.3)
            self.ax_main.add_patch(glow)
            
            # Qubit principal
            qubit = patches.Circle((x, y), size, 
                                 facecolor=color, edgecolor='white', 
                                 linewidth=2, alpha=0.9)
            self.ax_main.add_patch(qubit)
            
            # Etiqueta del qubit
            self.ax_main.text(x, y, f'q{i}', 
                            ha='center', va='center', 
                            fontweight='bold', fontsize=9, color='white')
            
            # Efectos de partículas para fase entrelazada
            if p < 0.4 and current_entropy > 0.5:
                self.draw_quantum_particles(x, y, p, i)
    
    def draw_quantum_particles(self, x, y, p, qubit_index):
        """Dibujar partículas cuánticas alrededor de los qubits"""
        num_particles = int(8 * (1 - p))
        
        for i in range(num_particles):
            angle = 2 * np.pi * i / num_particles + p * 10
            radius = 0.8 + 0.4 * np.sin(qubit_index + p * 5)
            
            px = x + radius * np.cos(angle)
            py = y + radius * np.sin(angle)
            
            # Tamaño y color de partícula variable
            particle_size = 0.05 + 0.03 * np.sin(qubit_index * 3 + p * 8)
            particle_alpha = 0.6 + 0.3 * np.sin(qubit_index * 2 + p * 6)
            
            particle = patches.Circle((px, py), particle_size, 
                                   facecolor='cyan', alpha=particle_alpha)
            self.ax_main.add_patch(particle)
    
    def draw_quantum_field(self, current_entropy):
        """Dibujar campo cuántico de fondo"""
        # Líneas de campo cuántico
        if current_entropy > 0.4:
            num_lines = int(15 * current_entropy)
            
            for i in range(num_lines):
                x_start = -3 + 6 * np.random.random()
                y_start = -0.5
                x_end = -3 + 6 * np.random.random()
                y_end = 4.5
                
                # Color y estilo variable
                line_alpha = 0.1 + 0.1 * current_entropy
                line_color = np.random.choice(['cyan', 'magenta', 'white'])
                
                self.ax_main.plot([x_start, x_end], [y_start, y_end], 
                                color=line_color, alpha=line_alpha, 
                                linewidth=1, linestyle='--')
    
    def draw_transition_graph(self, p):
        """Dibujar gráfica de transición mejorada"""
        self.ax_graph.clear()
        
        # Calcular curva de transición
        probabilities = []
        final_entropies = []
        
        for prob in self.probabilities:
            avg_entanglement = self.results[prob]['average']
            final_entropy = np.mean(avg_entanglement[-5:])
            probabilities.append(prob)
            final_entropies.append(final_entropy)
        
        # Gráfica principal con estilo mejorado
        self.ax_graph.plot(probabilities, final_entropies, 
                          color='cyan', linewidth=4, alpha=0.8,
                          marker='o', markersize=6, markerfacecolor='yellow')
        
        # Resaltar punto actual
        current_idx = self.probabilities.index(p)
        self.ax_graph.plot(p, final_entropies[current_idx], 'ro', 
                          markersize=12, markerfacecolor='red')
        
        # Region shading
        self.ax_graph.axvspan(0, 0.3, alpha=0.2, color='blue', label='Entrelazada')
        self.ax_graph.axvspan(0.3, 0.7, alpha=0.2, color='purple', label='Crítica')
        self.ax_graph.axvspan(0.7, 1.0, alpha=0.2, color='red', label='Desentrelazada')
        
        self.ax_graph.set_xlabel('Probabilidad de Medida (p)', fontweight='bold')
        self.ax_graph.set_ylabel('Entropía de Entrelazamiento', fontweight='bold')
        self.ax_graph.set_title('CURVA DE TRANSICIÓN', fontweight='bold')
        self.ax_graph.grid(True, alpha=0.3)
        self.ax_graph.legend()
        self.ax_graph.set_facecolor('black')
    
    def draw_time_evolution(self, p):
        """Dibujar evolución temporal"""
        self.ax_time.clear()
        
        time_steps = range(len(self.results[p]['average']))
        avg_entropy = self.results[p]['average']
        
        # Gráfica con efecto glow
        self.ax_time.plot(time_steps, avg_entropy, 
                         color='#ff00ff', linewidth=3, alpha=0.9,
                         label=f'p = {p:.2f}')
        
        # Sombras para efecto 3D
        self.ax_time.fill_between(time_steps, avg_entropy, alpha=0.3, color='magenta')
        
        self.ax_time.set_xlabel('Tiempo (pasos)', fontweight='bold')
        self.ax_time.set_ylabel('Entropía', fontweight='bold')
        self.ax_time.set_title('EVOLUCIÓN TEMPORAL', fontweight='bold')
        self.ax_time.grid(True, alpha=0.3)
        self.ax_time.legend()
        self.ax_time.set_facecolor('black')
    
    def animate_frame(self, frame):
        """Actualizar frame de animación"""
        p_idx = frame % len(self.probabilities)
        p = self.probabilities[p_idx]
        
        # Obtener entropía actual
        avg_entanglement = self.results[p]['average']
        current_entropy = np.mean(avg_entanglement[-5:])
        
        # Dibujar todos los componentes
        self.draw_quantum_system(p, current_entropy)
        self.draw_transition_graph(p)
        self.draw_time_evolution(p)
        
        # Progress bar
        progress = (frame % len(self.probabilities)) / len(self.probabilities)
        self.fig.suptitle(f'TRANSICIÓN DE FASE CUÁNTICA - Progreso: {progress*100:.1f}%', 
                         fontsize=14, fontweight='bold', color='white')
    
    def create_spectacular_animation(self, filename='quantum_phase_transition.mp4', fps=2):
        """Crear animación espectacular"""
        print("🎇 Creando visualización cuántica espectacular...")
        
        # Configurar animación
        anim = FuncAnimation(self.fig, self.animate_frame, 
                           frames=len(self.probabilities) * 2,  # 2 ciclos
                           interval=1000//fps, repeat=True)
        
        # Guardar como MP4 (mejor calidad)
        try:
            anim.save(filename, writer='ffmpeg', fps=fps, dpi=120, 
                     bitrate=2000, extra_args=['-vcodec', 'libx264'])
            print(f"💫 Animación guardada como {filename}")
        except:
            # Fallback a GIF si no hay ffmpeg
            gif_filename = filename.replace('.mp4', '.gif')
            anim.save(gif_filename, writer='pillow', fps=fps, dpi=100)
            print(f"💫 Animación guardada como {gif_filename} (formato GIF)")
        
        return anim

def main():
    """Función principal"""
    print("🌌 INICIANDO SIMULACIÓN CUÁNTICA VISUAL")
    print("=" * 50)
    
    try:
        # Cargar resultados
        with open('mipt_simulation_results.pkl', 'rb') as f:
            results = pickle.load(f)
        
        print("✅ Datos de simulación cargados")
        print(f"📊 Número de puntos de probabilidad: {len(results)}")
        
        # Crear animación espectacular
        quantum_anim = QuantumAnimation(results, num_qubits=6)
        animation = quantum_anim.create_spectacular_animation(
            'quantum_phase_transition_spectacular.gif', fps=1.5
        )
        
        print("\n🎊 ANIMACIÓN COMPLETADA!")
        print("✨ Características incluidas:")
        print("   - Visualización 3D de qubits en arco")
        print("   - Efectos de partículas cuánticas")
        print("   - Campos de fuerza visuales")
        print("   - Transiciones de color por fase")
        print("   - Gráficas profesionales integradas")
        
        # Mostrar resultado final
        plt.show()
        
    except FileNotFoundError:
        print("❌ Error: No se encontraron los datos de simulación")
        print("💡 Ejecuta primero: python mipt_simulation.py")
    except Exception as e:
        print(f"❌ Error inesperado: {e}")

if __name__ == "__main__":
    main()