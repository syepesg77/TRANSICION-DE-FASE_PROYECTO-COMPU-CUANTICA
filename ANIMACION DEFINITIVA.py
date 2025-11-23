import numpy as np
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation, PillowWriter
from mpl_toolkits.mplot3d import Axes3D
import matplotlib.colors as mcolors
from matplotlib.colors import LinearSegmentedColormap
import pickle
import time

class MIPT3DVisualizerFinal:
    def __init__(self, results, num_qubits=6):
        self.results = results
        self.num_qubits = num_qubits
        self.probabilities = sorted(results.keys())
        
        first_key = list(results.keys())[0]
        self.depth = len(results[first_key]['average'])
        
        print("Configurando animacion MIPT sin diagrama de fases")
        print(f"Probabilidades: {len(self.probabilities)}")
        print(f"Profundidad: {self.depth} pasos")
        
        # Figura con 5 paneles en lugar de 6
        self.fig = plt.figure(figsize=(18, 12))
        
        # Distribucion de paneles sin el diagrama de fases
        self.ax3d = self.fig.add_subplot(231, projection='3d')
        self.ax_curve = self.fig.add_subplot(232)
        self.ax_time = self.fig.add_subplot(233)
        self.ax_entropy = self.fig.add_subplot(234)
        self.ax_info = self.fig.add_subplot(235)
        
        # Hacer el panel de informacion mas grande
        self.ax_info.axis('off')
        
        self.entanglement_cmap = LinearSegmentedColormap.from_list(
            'quantum_entanglement', 
            ['#FF0000', '#FF8000', '#FFFF00', '#00FF00', '#0080FF', '#0000FF']
        )
        
        self.qubit_positions = self.generate_qubit_positions()
        
    def generate_qubit_positions(self):
        positions = []
        radius = 3
        for i in range(self.num_qubits):
            angle = 2 * np.pi * i / self.num_qubits
            x = radius * np.cos(angle)
            y = radius * np.sin(angle)
            z = 0.5 * np.sin(3 * angle)
            positions.append((x, y, z))
        return np.array(positions)
    
    def get_phase_info(self, p):
        if p < 0.2:
            return "FASE ENTRELAZADA", "blue", 0.7, 0.9
        elif p < 0.4:
            return "REGIMEN CRITICO TEMPRANO", "purple", 0.5, 0.7
        elif p < 0.6:
            return "PUNTO CRITICO", "darkviolet", 0.3, 0.5
        elif p < 0.8:
            return "REGIMEN CRITICO TARDIO", "orange", 0.1, 0.3
        else:
            return "FASE DESENTRELAZADA", "red", 0.0, 0.2

    def calculate_entanglement_with_inverted_colors(self, p, current_step):
        avg_entanglement = self.results[p]['average']
        current_entropy = avg_entanglement[current_step]
        
        print(f"p={p:.2f}, entropia_real={current_entropy:.3f}")
        
        qubit_entanglements = []
        for i in range(self.num_qubits):
            base = current_entropy
            
            if p < 0.3:
                variation = 0.1 * np.sin(current_step * 0.3 + i * 0.5)
            elif p > 0.7:
                variation = 0.05 * np.sin(current_step * 0.2 + i * 0.3)
            else:
                variation = 0.15 * np.sin(current_step * 0.5 + i * 0.8)
            
            entanglement = np.clip(base + variation, 0.05, 0.95)
            qubit_entanglements.append(entanglement)
        
        return current_entropy, qubit_entanglements

    def draw_quantum_system_3d(self, p, current_step):
        self.ax3d.clear()
        
        current_entropy, qubit_entanglements = self.calculate_entanglement_with_inverted_colors(p, current_step)
        phase_name, phase_color, _, _ = self.get_phase_info(p)
        
        for i in range(self.num_qubits):
            for j in range(i + 1, self.num_qubits):
                avg_entanglement_val = (qubit_entanglements[i] + qubit_entanglements[j]) / 2
                
                if avg_entanglement_val > 0.15:
                    pos1 = self.qubit_positions[i]
                    pos2 = self.qubit_positions[j]
                    
                    t = np.linspace(0, 1, 15)
                    x = (1 - t) * pos1[0] + t * pos2[0]
                    y = (1 - t) * pos1[1] + t * pos2[1]
                    z = (1 - t) * pos1[2] + t * pos2[2]
                    
                    oscillation = 0.1 * np.sin(8 * t) * avg_entanglement_val
                    z += oscillation
                    
                    color = self.entanglement_cmap(avg_entanglement_val)
                    linewidth = 1 + 3 * avg_entanglement_val
                    
                    self.ax3d.plot(x, y, z, color=color, linewidth=linewidth, alpha=0.7)
        
        for i, entanglement in enumerate(qubit_entanglements):
            pos = self.qubit_positions[i]
            radius = 0.2 + 0.3 * entanglement
            
            u = np.linspace(0, 2 * np.pi, 10)
            v = np.linspace(0, np.pi, 10)
            x = radius * np.outer(np.cos(u), np.sin(v)) + pos[0]
            y = radius * np.outer(np.sin(u), np.sin(v)) + pos[1]
            z = radius * np.outer(np.ones(np.size(u)), np.cos(v)) + pos[2]
            
            color = self.entanglement_cmap(entanglement)
            
            self.ax3d.plot_surface(x, y, z, color=color, alpha=0.9, shade=True)
            
            self.ax3d.text(pos[0], pos[1], pos[2] + radius + 0.1, 
                          f'q{i}', ha='center', va='bottom', 
                          fontsize=8, fontweight='bold', color='white')
        
        self.ax3d.set_xlim(-4, 4)
        self.ax3d.set_ylim(-4, 4)
        self.ax3d.set_zlim(-2, 2)
        self.ax3d.set_xlabel('X')
        self.ax3d.set_ylabel('Y')
        self.ax3d.set_zlabel('Z')
        
        color_status = "ROJO/NARANJA" if p < 0.3 else "AZUL/VERDE" if p > 0.7 else "MIXTO"
        self.ax3d.set_title(f'SISTEMA 3D - p={p:.2f}\n{phase_name} (Colores: {color_status})', 
                           fontsize=12, fontweight='bold')
        
        angle = current_step * 2
        self.ax3d.view_init(elev=20, azim=angle)

    def draw_transition_curve(self, current_p):
        self.ax_curve.clear()
        
        probabilities = []
        final_entropies = []
        
        for p in self.probabilities:
            avg_entanglement = self.results[p]['average']
            final_entropy = np.mean(avg_entanglement[-5:])
            probabilities.append(p)
            final_entropies.append(final_entropy)
        
        self.ax_curve.plot(probabilities, final_entropies, 'o-', 
                          color='black', linewidth=3, markersize=6,
                          label='Curva de Transicion')
        
        if current_p in probabilities:
            current_idx = probabilities.index(current_p)
            self.ax_curve.plot(current_p, final_entropies[current_idx], 's', 
                              markersize=12, markerfacecolor='gold',
                              markeredgecolor='red', markeredgewidth=3,
                              label=f'Actual: p={current_p:.2f}')
        
        self.ax_curve.axvspan(0, 0.2, alpha=0.2, color='blue', label='Entrelazada')
        self.ax_curve.axvspan(0.2, 0.4, alpha=0.2, color='purple', label='Critico Temprano')
        self.ax_curve.axvspan(0.4, 0.6, alpha=0.2, color='violet', label='Punto Critico')
        self.ax_curve.axvspan(0.6, 0.8, alpha=0.2, color='orange', label='Critico Tardio')
        self.ax_curve.axvspan(0.8, 1.0, alpha=0.2, color='red', label='Desentrelazada')
        
        self.ax_curve.set_xlabel('Probabilidad de Medida (p)')
        self.ax_curve.set_ylabel('Entropia de Entrelazamiento')
        self.ax_curve.set_title('CURVA DE TRANSICION MIPT')
        self.ax_curve.legend(fontsize=9)
        self.ax_curve.grid(True, alpha=0.3)
        self.ax_curve.set_xlim(0, 1)
        self.ax_curve.set_ylim(0, 1)

    def draw_time_evolution(self, current_p, current_step):
        self.ax_time.clear()
        
        if current_p in self.results:
            avg_entropy = self.results[current_p]['average']
            time_steps = range(len(avg_entropy))
            
            phase_name, phase_color, _, _ = self.get_phase_info(current_p)
            
            self.ax_time.plot(time_steps, avg_entropy, color=phase_color, 
                             linewidth=2, label=f'p={current_p:.2f}')
            
            if current_step < len(avg_entropy):
                self.ax_time.plot(current_step, avg_entropy[current_step], 'o',
                                 markersize=8, markerfacecolor='yellow',
                                 markeredgecolor='black', markeredgewidth=2)
            
            if current_step < len(avg_entropy):
                self.ax_time.fill_between(time_steps[:current_step+1], 
                                         avg_entropy[:current_step+1],
                                         alpha=0.3, color=phase_color)
            
            self.ax_time.set_xlabel('Tiempo (Pasos)')
            self.ax_time.set_ylabel('Entropia')
            self.ax_time.set_title(f'EVOLUCION TEMPORAL: {phase_name}')
            self.ax_time.legend()
            self.ax_time.grid(True, alpha=0.3)
            self.ax_time.set_xlim(0, len(time_steps))
            self.ax_time.set_ylim(0, 1)

    def draw_entropy_distribution(self, current_p, current_step):
        self.ax_entropy.clear()
        
        if current_p in self.results:
            avg_entanglement = self.results[current_p]['average']
            if current_step < len(avg_entanglement):
                current_entropy = avg_entanglement[current_step]
                phase_name, phase_color, _, _ = self.get_phase_info(current_p)
                
                if current_p < 0.3:
                    entropies = np.random.normal(current_entropy, 0.1, 500)
                elif current_p > 0.7:
                    entropies = np.random.normal(current_entropy, 0.05, 500)
                else:
                    entropies = np.random.normal(current_entropy, 0.15, 500)
                
                entropies = np.clip(entropies, 0, 1)
                
                n, bins, patches = self.ax_entropy.hist(entropies, bins=15, 
                                                       density=True, alpha=0.7,
                                                       color=phase_color, edgecolor='black')
                
                self.ax_entropy.set_xlabel('Entropia')
                self.ax_entropy.set_ylabel('Densidad')
                self.ax_entropy.set_title(f'DISTRIBUCION - {phase_name}')
                self.ax_entropy.grid(True, alpha=0.3)
                self.ax_entropy.set_xlim(0, 1)

    def draw_info_panel(self, current_p, current_step):
        self.ax_info.clear()
        self.ax_info.axis('off')
        
        current_entropy = 0.5
        if current_p in self.results:
            avg_entanglement = self.results[current_p]['average']
            if current_step < len(avg_entanglement):
                current_entropy = avg_entanglement[current_step]
        
        phase_name, phase_color, min_ent, max_ent = self.get_phase_info(current_p)
        
        info_text = [
            "INFORMACION DEL SISTEMA MIPT:",
            "",
            f"Probabilidad actual: p = {current_p:.3f}",
            f"Paso temporal: {current_step + 1}/{self.depth}",
            f"Entropia actual: {current_entropy:.3f}",
            "",
            f"FASE: {phase_name}",
            f"Rango esperado: {min_ent:.1f} - {max_ent:.1f}",
            "",
            "ESQUEMA DE COLORES:",
            "Azul = Alto  entrelazamiento"
            "Rojo/Naranja = Bajo entrelazamiento",
            "Amarillo/Verde = Entrelazamiento medio", 
            "",
            "",
            "EXPLICACION FISICA:",
            "p baja -> Pocas mediciones ->",
            "  Entrelazamiento alto",
            "p alta -> Muchas mediciones ->", 
            "  Entrelazamiento bajo",
            "",
            f"Procesando: p={current_p:.2f}"
        ]
        
        for i, line in enumerate(info_text):
            color = 'black'
            weight = 'normal'
            size = 9
            
            if "FASE:" in line:
                color = phase_color
                weight = 'bold'
                size = 11
            elif "INFORMACION" in line or "ESQUEMA" in line or "EXPLICACION" in line:
                color = 'darkred'
                weight = 'bold'
                size = 10
            
            self.ax_info.text(0.05, 0.98 - i*0.04, line, 
                             transform=self.ax_info.transAxes,
                             fontsize=size, fontweight=weight,
                             color=color, verticalalignment='top')

    def animate_frame(self, frame):
        try:
            p_index = frame // self.depth
            step_index = frame % self.depth
            
            if p_index < len(self.probabilities):
                current_p = self.probabilities[p_index]
                
                self.draw_quantum_system_3d(current_p, step_index)
                self.draw_transition_curve(current_p)
                self.draw_time_evolution(current_p, step_index)
                self.draw_entropy_distribution(current_p, step_index)
                self.draw_info_panel(current_p, step_index)
                
                total_frames = len(self.probabilities) * self.depth
                progress = (frame + 1) / total_frames * 100
                
                self.fig.suptitle(f'TRANSICION DE FASE MIPT - PROGRESO: {progress:.1f}%',
                                 fontsize=14, fontweight='bold', y=0.98)
                
                plt.tight_layout()
            
        except Exception as e:
            print(f"Error en frame {frame}: {e}")

    def create_animation(self, filename='mipt_sin_fases.gif', fps=5):
        total_frames = len(self.probabilities) * self.depth
        
        print("INICIANDO ANIMACION SIN DIAGRAMA DE FASES")
        print("ESQUEMA DE COLORES:")
        print(" - p < 0.3: DEBE verse AZUL alto entrelazamiento")
        print(" - p > 0.7: DEBE verse ROJO BAJO ENRELAZAMIENTO")
        print(f"Frames totales: {total_frames}")
        print(f"Duracion estimada: {total_frames/fps:.1f} segundos")
        
        writer = PillowWriter(fps=fps)
        start_time = time.time()
        
        try:
            with writer.saving(self.fig, filename, dpi=120):
                for frame in range(total_frames):
                    self.animate_frame(frame)
                    writer.grab_frame()
                    
                    if frame % 20 == 0:
                        elapsed = time.time() - start_time
                        progress = (frame + 1) / total_frames
                        estimated_total = elapsed / progress if progress > 0 else 0
                        remaining = estimated_total - elapsed
                        
                        p_index = frame // self.depth
                        step_index = frame % self.depth
                        current_p = self.probabilities[p_index] if p_index < len(self.probabilities) else self.probabilities[-1]
                        
                        print(f"Frame {frame+1}/{total_frames} "
                              f"({progress*100:.1f}%) - "
                              f"p={current_p:.2f} paso={step_index}")
            
            total_time = time.time() - start_time
            print(f"ANIMACION COMPLETADA")
            print(f"Tiempo total: {total_time/60:.1f} minutos")
            print(f"Archivo: {filename}")
            
        except Exception as e:
            print(f"Error: {e}")

def main():
    print("CARGANDO DATOS PARA ANIMACION SIN DIAGRAMA DE FASES")
    
    try:
        with open('mipt_simulation_results.pkl', 'rb') as f:
            results = pickle.load(f)
        
        print("Datos cargados. Iniciando animacion...")
        
        visualizer = MIPT3DVisualizerFinal(results)
        visualizer.create_animation('animaciIO_3D_1.gif', fps=5)
        
    except FileNotFoundError:
        print("Error: No se encuentra mipt_simulation_results.pkl")
        print("Ejecuta primero: python mipt_simulation.py")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    main()