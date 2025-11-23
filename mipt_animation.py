import numpy as np
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
import matplotlib.patches as patches
from matplotlib.colors import LinearSegmentedColormap
import pickle
import os

class MIPTAnimator:
    def __init__(self, results, num_qubits=6):
        self.results = results
        self.num_qubits = num_qubits
        self.probabilities = sorted(results.keys())
        
        # Configurar figura
        plt.rcParams['font.size'] = 12
        self.fig = plt.figure(figsize=(15, 8))
        
        # Crear subplots
        self.ax1 = plt.subplot2grid((2, 3), (0, 0), colspan=2)  # Curva principal
        self.ax2 = plt.subplot2grid((2, 3), (1, 0), colspan=2)  # Evolución temporal
        self.ax3 = plt.subplot2grid((2, 3), (0, 2), rowspan=2)  # Cadena de qubits
        
        # Colormap
        self.cmap = LinearSegmentedColormap.from_list('entanglement', 
                                                     ['white', 'lightblue', 'blue', 'darkblue', 'purple', 'red'])
        
        self.current_frame = 0
        self.setup_plots()
    
    def setup_plots(self):
        """Configurar los plots iniciales"""
        for ax in [self.ax1, self.ax2, self.ax3]:
            ax.clear()
        
        self.ax1.set_xlabel('Probabilidad de Medida (p)')
        self.ax1.set_ylabel('Entropía de Entrelazamiento')
        self.ax1.set_title('TRANSICIÓN DE FASE INDUCIDA POR MEDIDA', fontweight='bold')
        self.ax1.grid(True, alpha=0.3)
        self.ax1.set_xlim(-0.1, 1.1)
        self.ax1.set_ylim(0, 1)
        
        self.ax2.set_xlabel('Tiempo (pasos del circuito)')
        self.ax2.set_ylabel('Entropía de Entrelazamiento')
        self.ax2.set_title('Evolución Temporal', fontweight='bold')
        self.ax2.grid(True, alpha=0.3)
        
        self.ax3.set_xlim(-1, self.num_qubits)
        self.ax3.set_ylim(-2, 2)
        self.ax3.set_aspect('equal')
        self.ax3.set_title('Estado de los Qubits', fontweight='bold')
        self.ax3.axis('off')
        
        plt.tight_layout()
    
    def calculate_transition_curve(self):
        """Calcular curva de transición"""
        probabilities = []
        final_entropies = []
        
        for p in self.probabilities:
            avg_entanglement = self.results[p]['average']
            final_entropy = np.mean(avg_entanglement[-5:])
            probabilities.append(p)
            final_entropies.append(final_entropy)
        
        return probabilities, final_entropies
    
    def animate_frame(self, frame):
        """Actualizar animación para cada frame"""
        self.current_frame = frame
        p_idx = frame % len(self.probabilities)
        p = self.probabilities[p_idx]
        
        self.setup_plots()
        
        # Plot 1: Curva de transición
        probs, entropies = self.calculate_transition_curve()
        self.ax1.plot(probs, entropies, 'b-', alpha=0.7, linewidth=3, label='Curva de transición')
        self.ax1.plot(p, entropies[p_idx], 'ro', markersize=12, 
                     label=f'p actual = {p:.2f}')
        self.ax1.legend()
        
        # Añadir regiones de fase
        self.ax1.axvspan(0, 0.3, alpha=0.1, color='blue')
        self.ax1.axvspan(0.3, 0.7, alpha=0.1, color='purple')
        self.ax1.axvspan(0.7, 1.0, alpha=0.1, color='red')
        
        # Plot 2: Evolución temporal
        time_steps = range(len(self.results[p]['average']))
        avg_entropy = self.results[p]['average']
        self.ax2.plot(time_steps, avg_entropy, 'b-', linewidth=2, label='Promedio')
        self.ax2.set_xlim(0, len(time_steps))
        self.ax2.set_ylim(0, 1)
        self.ax2.legend()
        
        # Plot 3: Cadena de qubits
        self.draw_qubit_chain(p)
        
        # Texto informativo
        phase_info = self.get_phase_info(p)
        self.ax3.text(self.num_qubits/2 - 0.5, -1.5, phase_info, 
                     ha='center', va='center', fontsize=14, 
                     fontweight='bold', bbox=dict(boxstyle="round,pad=0.5", 
                     facecolor='lightyellow', alpha=0.8))
        
        self.fig.suptitle(f'Frame {frame + 1}: Probabilidad de Medida p = {p:.2f}', 
                         fontsize=16, fontweight='bold')
    
    def get_phase_info(self, p):
        """Obtener información de la fase actual"""
        if p < 0.3:
            return "FASE ENTRELAZADA\n• Alta entropía\n• Ley de Volumen\n• Correlaciones no locales"
        elif p > 0.7:
            return "FASE DESENTRELAZADA\n• Baja entropía\n• Ley de Área\n• Correlaciones locales"
        else:
            return "REGIMEN CRÍTICO\n• Comportamiento universal\n• Fluctuaciones grandes\n• Punto de transición"
    
    def draw_qubit_chain(self, p):
        """Dibujar la cadena de qubits"""
        # Obtener entropía actual
        avg_entanglement = self.results[p]['average']
        current_entropy = np.mean(avg_entanglement[-5:])
        
        for i in range(self.num_qubits):
            # Calcular nivel de entrelazamiento individual
            if p < 0.3:
                # Fase entrelazada: todos altos
                entanglement = 0.7 + 0.2 * np.random.random()
            elif p > 0.7:
                # Fase desentrelazada: todos bajos
                entanglement = 0.1 + 0.2 * np.random.random()
            else:
                # Crítico: mezcla
                base = current_entropy
                entanglement = base + 0.3 * (np.random.random() - 0.5)
            
            entanglement = max(0.05, min(0.95, entanglement))
            color = self.cmap(entanglement)
            
            # Dibujar qubit
            circle = patches.Circle((i, 0), 0.3, facecolor=color, 
                                  edgecolor='black', linewidth=2)
            self.ax3.add_patch(circle)
            
            # Etiqueta
            self.ax3.text(i, 0, f'q{i}', ha='center', va='center', 
                         fontweight='bold', fontsize=10)
            
            # Conexiones
            if i < self.num_qubits - 1:
                strength = min(entanglement, current_entropy)
                linewidth = 1 + 4 * strength
                alpha = 0.3 + 0.7 * strength
                
                self.ax3.plot([i + 0.3, i + 1 - 0.3], [0, 0], 'k-', 
                            linewidth=linewidth, alpha=alpha,
                            solid_capstyle='round')
    
    def create_animation(self, filename='mipt_animation.gif', fps=2):
        """Crear animación GIF"""
        print("🎬 Creando animación...")
        
        # Crear animación
        anim = FuncAnimation(self.fig, self.animate_frame, 
                           frames=len(self.probabilities), 
                           interval=1000/fps, repeat=True)
        
        # Guardar como GIF
        anim.save(filename, writer='pillow', fps=fps, dpi=100)
        print(f"💾 Animación guardada como {filename}")
        
        return anim

def main():
    """Función principal de animación"""
    print("🎨 Iniciando creación de animación MIPT...")
    
    try:
        # Cargar resultados
        with open('mipt_simulation_results.pkl', 'rb') as f:
            results = pickle.load(f)
        
        # Crear animación
        animator = MIPTAnimator(results, num_qubits=6)
        animation = animator.create_animation('mipt_animation.gif', fps=1)
        
        print("✅ Animación completada!")
        
        # Mostrar última frame
        plt.show()
        
    except FileNotFoundError:
        print("❌ Error: Primero ejecuta mipt_simulation.py")
        print("💡 Ejecuta: python mipt_simulation.py")

if __name__ == "__main__":
    main()


