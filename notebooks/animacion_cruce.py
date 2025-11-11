"""
Animación visual del cruce peatonal con vehículos y peatones.
"""
import matplotlib.pyplot as plt
import matplotlib.animation as animation
from matplotlib.patches import Rectangle, Circle
import numpy as np
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from config import *
from test_semaforo_adaptativo import simular_semaforo_adaptativo
from analisis.metricas import AnalizadorMetricas


class AnimacionCruce:
    """
    Clase para animar el cruce peatonal.
    """
    
    def __init__(self, registros, duracion_animacion=30):
        """
        Parámetros:
        -----------
        registros : dict
            Registros de la simulación
        duracion_animacion : int
            Duración en segundos de la animación (tiempo simulado)
        """
        self.registros = registros
        self.duracion_animacion = duracion_animacion
        
        # Extraer datos relevantes
        self.df_estado = self._preparar_datos()
        self.eventos = registros.get('eventos_semaforo', [])
        
    def _preparar_datos(self):
        """Prepara los datos para la animación."""
        import pandas as pd
        
        if not self.registros.get('estado_colas'):
            return pd.DataFrame()
        
        df = pd.DataFrame(self.registros['estado_colas'])
        df = df[df['tiempo'] <= self.duracion_animacion]
        return df
    
    def crear_animacion(self, intervalo=100, guardar=False, filename='animacion_cruce.mp4'):
        """
        Crea la animación del cruce.
        
        Parámetros:
        -----------
        intervalo : int
            Milisegundos entre frames
        guardar : bool
            Si True, guarda la animación como video
        filename : str
            Nombre del archivo de salida
        """
        if self.df_estado.empty:
            print("⚠️ No hay datos para animar")
            return None
        
        fig, (ax_cruce, ax_graficas) = plt.subplots(1, 2, figsize=(16, 6))
        
        # Configurar eje del cruce
        ax_cruce.set_xlim(-10, 10)
        ax_cruce.set_ylim(-10, 10)
        ax_cruce.set_aspect('equal')
        ax_cruce.axis('off')
        ax_cruce.set_title('Cruce Peatonal en Tiempo Real', fontsize=14, fontweight='bold')
        
        # Dibujar calles
        # Calle horizontal (vehículos)
        ax_cruce.add_patch(Rectangle((-10, -2), 20, 4, facecolor='gray', alpha=0.3))
        # Calle vertical (peatones)
        ax_cruce.add_patch(Rectangle((-2, -10), 4, 20, facecolor='lightblue', alpha=0.3))
        
        # Semáforo vehicular
        semaforo_v = Circle((6, 3), 0.5, color='red')
        ax_cruce.add_patch(semaforo_v)
        ax_cruce.text(6, 4.5, 'SEM V', ha='center', fontsize=9, fontweight='bold')
        
        # Semáforo peatonal
        semaforo_p = Circle((3, 6), 0.5, color='red')
        ax_cruce.add_patch(semaforo_p)
        ax_cruce.text(3, 7.5, 'SEM P', ha='center', fontsize=9, fontweight='bold')
        
        # Textos informativos
        texto_tiempo = ax_cruce.text(-9, 9, '', fontsize=12, fontweight='bold')
        texto_fase = ax_cruce.text(-9, 8, '', fontsize=10)
        texto_colas = ax_cruce.text(-9, 6.5, '', fontsize=10)
        
        # Configurar eje de gráficas
        ax_graficas.set_xlabel('Tiempo (s)', fontweight='bold')
        ax_graficas.set_ylabel('Longitud de cola', fontweight='bold')
        ax_graficas.set_title('Evolución de Colas', fontsize=12, fontweight='bold')
        ax_graficas.grid(True, alpha=0.3)
        
        linea_v, = ax_graficas.plot([], [], 'o-', color='#2E86AB', label='Vehículos', linewidth=2)
        linea_p, = ax_graficas.plot([], [], 's-', color='#A23B72', label='Peatones', linewidth=2)
        ax_graficas.legend()
        
        # Listas para almacenar histórico
        tiempos = []
        colas_v = []
        colas_p = []
        
        # Marcadores para vehículos y peatones en espera
        vehiculos_markers = []
        peatones_markers = []
        
        def init():
            """Inicialización de la animación."""
            linea_v.set_data([], [])
            linea_p.set_data([], [])
            return linea_v, linea_p
        
        def animate(frame):
            """Función de animación para cada frame."""
            if frame >= len(self.df_estado):
                return linea_v, linea_p
            
            # Obtener datos del frame actual
            fila = self.df_estado.iloc[frame]
            tiempo_actual = fila['tiempo']
            cola_v_actual = fila['cola_v']
            cola_p_actual = fila['cola_p']
            fase_actual = fila['fase']
            
            # Actualizar histórico
            tiempos.append(tiempo_actual)
            colas_v.append(cola_v_actual)
            colas_p.append(cola_p_actual)
            
            # Actualizar textos
            texto_tiempo.set_text(f't = {tiempo_actual:.1f}s')
            texto_fase.set_text(f'Fase: {fase_actual}')
            texto_colas.set_text(f'Colas: V={cola_v_actual} | P={cola_p_actual}')
            
            # Actualizar color de semáforos
            if 'VERDE_VEHICULAR' in fase_actual:
                semaforo_v.set_color('green')
                semaforo_p.set_color('red')
            elif fase_actual == 'VERDE_PEATONAL':
                semaforo_v.set_color('red')
                semaforo_p.set_color('green')
            elif 'AMARILLO' in fase_actual:
                if 'VEHICULAR' in fase_actual:
                    semaforo_v.set_color('yellow')
                else:
                    semaforo_p.set_color('yellow')
            
            # Limpiar marcadores anteriores
            for marker in vehiculos_markers:
                marker.remove()
            for marker in peatones_markers:
                marker.remove()
            vehiculos_markers.clear()
            peatones_markers.clear()
            
            # Dibujar vehículos en espera
            for i in range(min(cola_v_actual, 8)):  # Máximo 8 visibles
                x = -8 + i * 0.8
                y = 0
                vehiculo = Rectangle((x, y-0.3), 0.6, 0.6, facecolor='blue', edgecolor='darkblue')
                ax_cruce.add_patch(vehiculo)
                vehiculos_markers.append(vehiculo)
            
            # Dibujar peatones en espera
            for i in range(min(cola_p_actual, 8)):  # Máximo 8 visibles
                x = 0
                y = -8 + i * 0.8
                peaton = Circle((x, y), 0.25, facecolor='orange', edgecolor='darkorange')
                ax_cruce.add_patch(peaton)
                peatones_markers.append(peaton)
            
            # Actualizar gráficas
            linea_v.set_data(tiempos, colas_v)
            linea_p.set_data(tiempos, colas_p)
            ax_graficas.set_xlim(0, max(tiempos[-1], 10))
            ax_graficas.set_ylim(0, max(max(colas_v + colas_p), 5) + 2)
            
            return linea_v, linea_p
        
        # Crear animación
        anim = animation.FuncAnimation(
            fig, animate, init_func=init,
            frames=len(self.df_estado),
            interval=intervalo,
            blit=False,
            repeat=True
        )
        
        if guardar:
            print(f"💾 Guardando animación como {filename}...")
            print("   (Esto puede tardar varios minutos)")
            
            # Intentar guardar como MP4 (requiere ffmpeg)
            try:
                Writer = animation.writers['ffmpeg']
                writer = Writer(fps=10, metadata=dict(artist='SimPy'), bitrate=1800)
                anim.save(filename, writer=writer)
                print(f"✅ Animación guardada: {filename}")
            except:
                # Si falla, guardar como GIF
                print("⚠️  FFmpeg no disponible, guardando como GIF...")
                filename_gif = filename.replace('.mp4', '.gif')
                anim.save(filename_gif, writer='pillow', fps=10)
                print(f"✅ Animación guardada: {filename_gif}")
        
        plt.tight_layout()
        return anim


def demo_animacion():
    """
    Ejecuta una demostración de la animación.
    """
    print("\n" + "="*70)
    print("🎬 DEMO: ANIMACIÓN DEL CRUCE PEATONAL")
    print("="*70 + "\n")
    
    # Ejecutar simulación corta
    print("Ejecutando simulación...")
    registros, _, _ = simular_semaforo_adaptativo(
        tiempo_sim=60,  # Solo 60 segundos
        lambda_v=0.4,
        lambda_p=0.15,
        warmup=0,
        semilla=42,
        verbose=False
    )
    
    # Crear animación
    print("\nCreando animación...")
    animador = AnimacionCruce(registros, duracion_animacion=60)
    anim = animador.crear_animacion(intervalo=100, guardar=False)
    
    if anim:
        print("\n✅ Animación creada. Mostrando ventana...")
        print("   Cierra la ventana para continuar.")
        plt.show()
    else:
        print("❌ Error al crear la animación")


def crear_animacion_completa(guardar=True):
    """
    Crea y guarda una animación completa.
    """
    print("\n" + "="*70)
    print("🎬 CREANDO ANIMACIÓN COMPLETA")
    print("="*70 + "\n")
    
    # Simulación más larga
    print("Ejecutando simulación (120 segundos)...")
    registros, _, _ = simular_semaforo_adaptativo(
        tiempo_sim=120,
        lambda_v=0.3,
        lambda_p=0.1,
        warmup=0,
        semilla=42,
        verbose=False
    )
    
    # Crear y guardar animación
    print("\nCreando y guardando animación...")
    animador = AnimacionCruce(registros, duracion_animacion=120)
    
    output_path = os.path.join(GRAFICOS_DIR, 'animacion_cruce.mp4')
    anim = animador.crear_animacion(
        intervalo=100,
        guardar=guardar,
        filename=output_path
    )
    
    if not guardar:
        print("\n✅ Animación creada. Mostrando ventana...")
        plt.show()
    
    return anim


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description='Animación del cruce peatonal')
    parser.add_argument('--guardar', action='store_true', 
                       help='Guardar animación como archivo')
    parser.add_argument('--demo', action='store_true',
                       help='Ejecutar demo rápida (60s)')
    
    args = parser.parse_args()
    
    if args.demo:
        demo_animacion()
    else:
        crear_animacion_completa(guardar=args.guardar)