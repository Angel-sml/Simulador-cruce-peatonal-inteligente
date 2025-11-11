"""
Módulo de visualizaciones para análisis del sistema.
"""
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
import pandas as pd
from matplotlib.patches import Rectangle
import os

# Configurar estilo
sns.set_style("whitegrid")
plt.rcParams['figure.figsize'] = (12, 6)
plt.rcParams['font.size'] = 10


class VisualizadorSimulacion:
    """
    Clase para crear visualizaciones del sistema de simulación.
    """
    
    def __init__(self, analizador, directorio_salida):
        """
        Parámetros:
        -----------
        analizador : AnalizadorMetricas
            Analizador con los datos de la simulación
        directorio_salida : str
            Directorio donde guardar los gráficos
        """
        self.analizador = analizador
        self.directorio_salida = directorio_salida
        os.makedirs(directorio_salida, exist_ok=True)
        
        # Obtener DataFrames
        self.df_v = analizador.crear_df_servicios_vehiculos()
        self.df_p = analizador.crear_df_servicios_peatones()
        self.df_eventos = analizador.crear_df_eventos_semaforo()
        self.df_estado = analizador.crear_df_estado_colas()
    
    def graficar_series_temporales_colas(self, guardar=True):
        """
        Gráfico de series temporales de longitud de colas con cambios de fase.
        """
        if self.df_estado.empty:
            print("⚠️  No hay datos de estado de colas")
            return None
        
        fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(14, 8), sharex=True)
        
        # Serie temporal de cola vehicular
        ax1.plot(self.df_estado['tiempo'], self.df_estado['cola_v'], 
                 color='#2E86AB', linewidth=1.5, label='Cola vehicular')
        ax1.fill_between(self.df_estado['tiempo'], self.df_estado['cola_v'], 
                         alpha=0.3, color='#2E86AB')
        ax1.set_ylabel('Vehículos en cola', fontsize=12, fontweight='bold')
        ax1.set_title('Evolución de Colas en el Tiempo', fontsize=14, fontweight='bold')
        ax1.legend(loc='upper right')
        ax1.grid(True, alpha=0.3)
        
        # Serie temporal de cola peatonal
        ax2.plot(self.df_estado['tiempo'], self.df_estado['cola_p'], 
                 color='#A23B72', linewidth=1.5, label='Cola peatonal')
        ax2.fill_between(self.df_estado['tiempo'], self.df_estado['cola_p'], 
                         alpha=0.3, color='#A23B72')
        ax2.set_xlabel('Tiempo (segundos)', fontsize=12, fontweight='bold')
        ax2.set_ylabel('Peatones en cola', fontsize=12, fontweight='bold')
        ax2.legend(loc='upper right')
        ax2.grid(True, alpha=0.3)
        
        # Marcar cambios de fase (fondo de color)
        if not self.df_eventos.empty:
            for _, evento in self.df_eventos.iterrows():
                color = None
                alpha = 0.1
                
                if 'VERDE_VEHICULAR' in evento['fase']:
                    color = '#90EE90'  # Verde claro
                elif evento['fase'] == 'VERDE_PEATONAL':
                    color = '#FFB6C1'  # Rosa claro
                
                if color:
                    for ax in [ax1, ax2]:
                        ax.axvspan(evento['tiempo'], 
                                  evento['tiempo'] + evento['duracion'],
                                  color=color, alpha=alpha)
        
        plt.tight_layout()
        
        if guardar:
            path = os.path.join(self.directorio_salida, 'series_temporales_colas.png')
            plt.savefig(path, dpi=300, bbox_inches='tight')
            print(f"✅ Gráfico guardado: {path}")
        
        return fig
    
    def graficar_histogramas_espera(self, guardar=True):
        """
        Histogramas de distribución de tiempos de espera.
        """
        fig, axes = plt.subplots(1, 2, figsize=(14, 5))
        
        # Histograma vehículos
        if not self.df_v.empty:
            ax1 = axes[0]
            esperas_v = self.df_v['tiempo_espera'].values
            
            ax1.hist(esperas_v, bins=30, color='#2E86AB', alpha=0.7, edgecolor='black')
            ax1.axvline(np.mean(esperas_v), color='red', linestyle='--', 
                       linewidth=2, label=f'Media: {np.mean(esperas_v):.1f}s')
            ax1.axvline(np.percentile(esperas_v, 95), color='orange', linestyle='--',
                       linewidth=2, label=f'P95: {np.percentile(esperas_v, 95):.1f}s')
            
            ax1.set_xlabel('Tiempo de espera (segundos)', fontsize=11, fontweight='bold')
            ax1.set_ylabel('Frecuencia', fontsize=11, fontweight='bold')
            ax1.set_title('Distribución de Espera - Vehículos', fontsize=12, fontweight='bold')
            ax1.legend()
            ax1.grid(True, alpha=0.3)
        
        # Histograma peatones
        if not self.df_p.empty:
            ax2 = axes[1]
            esperas_p = self.df_p['tiempo_espera'].values
            
            ax2.hist(esperas_p, bins=30, color='#A23B72', alpha=0.7, edgecolor='black')
            ax2.axvline(np.mean(esperas_p), color='red', linestyle='--',
                       linewidth=2, label=f'Media: {np.mean(esperas_p):.1f}s')
            ax2.axvline(np.percentile(esperas_p, 95), color='orange', linestyle='--',
                       linewidth=2, label=f'P95: {np.percentile(esperas_p, 95):.1f}s')
            
            ax2.set_xlabel('Tiempo de espera (segundos)', fontsize=11, fontweight='bold')
            ax2.set_ylabel('Frecuencia', fontsize=11, fontweight='bold')
            ax2.set_title('Distribución de Espera - Peatones', fontsize=12, fontweight='bold')
            ax2.legend()
            ax2.grid(True, alpha=0.3)
        
        plt.tight_layout()
        
        if guardar:
            path = os.path.join(self.directorio_salida, 'histogramas_espera.png')
            plt.savefig(path, dpi=300, bbox_inches='tight')
            print(f"✅ Gráfico guardado: {path}")
        
        return fig
    
    def graficar_cdf_espera(self, guardar=True):
        """
        Funciones de distribución acumulada (CDF) de tiempos de espera.
        """
        fig, ax = plt.subplots(figsize=(10, 6))
        
        # CDF vehículos
        if not self.df_v.empty:
            esperas_v = np.sort(self.df_v['tiempo_espera'].values)
            cdf_v = np.arange(1, len(esperas_v) + 1) / len(esperas_v)
            ax.plot(esperas_v, cdf_v, linewidth=2.5, label='Vehículos', color='#2E86AB')
        
        # CDF peatones
        if not self.df_p.empty:
            esperas_p = np.sort(self.df_p['tiempo_espera'].values)
            cdf_p = np.arange(1, len(esperas_p) + 1) / len(esperas_p)
            ax.plot(esperas_p, cdf_p, linewidth=2.5, label='Peatones', color='#A23B72')
        
        # Líneas de referencia
        ax.axhline(0.5, color='gray', linestyle=':', alpha=0.6, label='Mediana (50%)')
        ax.axhline(0.95, color='orange', linestyle=':', alpha=0.6, label='Percentil 95')
        
        ax.set_xlabel('Tiempo de espera (segundos)', fontsize=12, fontweight='bold')
        ax.set_ylabel('Probabilidad acumulada', fontsize=12, fontweight='bold')
        ax.set_title('Función de Distribución Acumulada (CDF) - Tiempos de Espera', 
                    fontsize=13, fontweight='bold')
        ax.legend(loc='lower right', fontsize=11)
        ax.grid(True, alpha=0.3)
        ax.set_ylim([0, 1])
        
        plt.tight_layout()
        
        if guardar:
            path = os.path.join(self.directorio_salida, 'cdf_espera.png')
            plt.savefig(path, dpi=300, bbox_inches='tight')
            print(f"✅ Gráfico guardado: {path}")
        
        return fig
    
    def graficar_gantt_ciclos(self, n_ciclos=10, guardar=True):
        """
        Diagrama de Gantt mostrando fases del semáforo por ciclo.
        """
        if self.df_eventos.empty:
            print("⚠️  No hay datos de eventos del semáforo")
            return None
        
        # Tomar solo los primeros n_ciclos
        df_eventos_subset = self.df_eventos[self.df_eventos['ciclo'] <= n_ciclos].copy()
        
        if df_eventos_subset.empty:
            print("⚠️  No hay suficientes ciclos para graficar")
            return None
        
        fig, ax = plt.subplots(figsize=(14, max(6, n_ciclos * 0.5)))
        
        # Colores por fase
        colores = {
            'VERDE_VEHICULAR': '#4CAF50',
            'VERDE_VEHICULAR_INICIAL': '#4CAF50',
            'VERDE_VEHICULAR_EXTENSION': '#66BB6A',
            'AMARILLO_VEHICULAR': '#FFC107',
            'VERDE_PEATONAL': '#E91E63',
            'AMARILLO_PEATONAL': '#FF9800'
        }
        
        y_pos = 0
        ciclo_anterior = None
        
        for _, evento in df_eventos_subset.iterrows():
            ciclo = evento['ciclo']
            
            # Nueva fila para cada ciclo
            if ciclo != ciclo_anterior:
                y_pos = ciclo - 1
                ciclo_anterior = ciclo
            
            # Determinar color
            fase = evento['fase']
            color = colores.get(fase, '#CCCCCC')
            
            # Dibujar rectángulo
            rect = Rectangle((evento['tiempo'], y_pos - 0.4), 
                           evento['duracion'], 0.8,
                           facecolor=color, edgecolor='black', linewidth=0.5)
            ax.add_patch(rect)
            
            # Etiqueta (solo si la fase es suficientemente larga)
            if evento['duracion'] > 5:
                fase_corta = fase.replace('VERDE_', 'V_').replace('AMARILLO_', 'A_')
                ax.text(evento['tiempo'] + evento['duracion']/2, y_pos,
                       f"{fase_corta}\n{evento['duracion']:.0f}s",
                       ha='center', va='center', fontsize=7, fontweight='bold')
        
        ax.set_xlabel('Tiempo (segundos)', fontsize=12, fontweight='bold')
        ax.set_ylabel('Ciclo del semáforo', fontsize=12, fontweight='bold')
        ax.set_title(f'Diagrama de Gantt - Primeros {n_ciclos} Ciclos', 
                    fontsize=13, fontweight='bold')
        ax.set_yticks(range(n_ciclos))
        ax.set_yticklabels([f'Ciclo {i+1}' for i in range(n_ciclos)])
        ax.grid(True, axis='x', alpha=0.3)
        
        # Leyenda
        from matplotlib.patches import Patch
        legend_elements = [
            Patch(facecolor='#4CAF50', label='Verde Vehicular'),
            Patch(facecolor='#FFC107', label='Amarillo Vehicular'),
            Patch(facecolor='#E91E63', label='Verde Peatonal'),
            Patch(facecolor='#FF9800', label='Amarillo Peatonal')
        ]
        ax.legend(handles=legend_elements, loc='upper right', fontsize=9)
        
        plt.tight_layout()
        
        if guardar:
            path = os.path.join(self.directorio_salida, 'gantt_ciclos.png')
            plt.savefig(path, dpi=300, bbox_inches='tight')
            print(f"✅ Gráfico guardado: {path}")
        
        return fig
    
    def graficar_boxplot_espera(self, guardar=True):
        """
        Boxplots comparativos de tiempos de espera.
        """
        fig, ax = plt.subplots(figsize=(10, 6))
        
        datos = []
        etiquetas = []
        
        if not self.df_v.empty:
            datos.append(self.df_v['tiempo_espera'].values)
            etiquetas.append('Vehículos')
        
        if not self.df_p.empty:
            datos.append(self.df_p['tiempo_espera'].values)
            etiquetas.append('Peatones')
        
        if datos:
            bp = ax.boxplot(datos, labels=etiquetas, patch_artist=True,
                           showmeans=True, meanline=True)
            
            # Colores
            colores = ['#2E86AB', '#A23B72']
            for patch, color in zip(bp['boxes'], colores):
                patch.set_facecolor(color)
                patch.set_alpha(0.6)
            
            ax.set_ylabel('Tiempo de espera (segundos)', fontsize=12, fontweight='bold')
            ax.set_title('Comparación de Tiempos de Espera', fontsize=13, fontweight='bold')
            ax.grid(True, axis='y', alpha=0.3)
        
        plt.tight_layout()
        
        if guardar:
            path = os.path.join(self.directorio_salida, 'boxplot_espera.png')
            plt.savefig(path, dpi=300, bbox_inches='tight')
            print(f"✅ Gráfico guardado: {path}")
        
        return fig
    
    def graficar_metricas_por_ciclo(self, guardar=True):
        """
        Gráfico de métricas agregadas por ciclo.
        """
        if self.df_v.empty or 'ciclo' not in self.df_v.columns:
            print("⚠️  No hay datos de ciclos")
            return None
        
        # Calcular métricas por ciclo
        metricas_v = self.analizador.calcular_metricas_por_ciclo(self.df_v, "vehiculos")
        metricas_p = self.analizador.calcular_metricas_por_ciclo(self.df_p, "peatones")
        
        fig, axes = plt.subplots(2, 1, figsize=(14, 8), sharex=True)
        
        # Vehículos atendidos por ciclo
        if not metricas_v.empty:
            ax1 = axes[0]
            ax1.bar(metricas_v['ciclo'], metricas_v['n_atendidos'], 
                   color='#2E86AB', alpha=0.7, label='Vehículos')
            ax1.set_ylabel('Vehículos atendidos', fontsize=11, fontweight='bold')
            ax1.set_title('Vehículos y Peatones Atendidos por Ciclo', 
                         fontsize=13, fontweight='bold')
            ax1.legend()
            ax1.grid(True, axis='y', alpha=0.3)
        
        # Peatones atendidos por ciclo
        if not metricas_p.empty:
            ax2 = axes[1]
            ax2.bar(metricas_p['ciclo'], metricas_p['n_atendidos'], 
                   color='#A23B72', alpha=0.7, label='Peatones')
            ax2.set_xlabel('Ciclo', fontsize=11, fontweight='bold')
            ax2.set_ylabel('Peatones atendidos', fontsize=11, fontweight='bold')
            ax2.legend()
            ax2.grid(True, axis='y', alpha=0.3)
        
        plt.tight_layout()
        
        if guardar:
            path = os.path.join(self.directorio_salida, 'metricas_por_ciclo.png')
            plt.savefig(path, dpi=300, bbox_inches='tight')
            print(f"✅ Gráfico guardado: {path}")
        
        return fig
    
    def generar_todas_visualizaciones(self):
        """
        Genera todas las visualizaciones y las guarda.
        """
        print(f"\n{'='*70}")
        print(f"GENERANDO VISUALIZACIONES")
        print(f"{'='*70}\n")
        
        graficos_generados = []
        
        # Series temporales
        print("📊 Generando series temporales de colas...")
        fig = self.graficar_series_temporales_colas()
        if fig: 
            graficos_generados.append('series_temporales_colas.png')
            plt.close(fig)
        
        # Histogramas
        print("📊 Generando histogramas de espera...")
        fig = self.graficar_histogramas_espera()
        if fig:
            graficos_generados.append('histogramas_espera.png')
            plt.close(fig)
        
        # CDF
        print("📊 Generando CDF de espera...")
        fig = self.graficar_cdf_espera()
        if fig:
            graficos_generados.append('cdf_espera.png')
            plt.close(fig)
        
        # Gantt
        print("📊 Generando diagrama de Gantt...")
        fig = self.graficar_gantt_ciclos(n_ciclos=10)
        if fig:
            graficos_generados.append('gantt_ciclos.png')
            plt.close(fig)
        
        # Boxplot
        print("📊 Generando boxplot comparativo...")
        fig = self.graficar_boxplot_espera()
        if fig:
            graficos_generados.append('boxplot_espera.png')
            plt.close(fig)
        
        # Métricas por ciclo
        print("📊 Generando métricas por ciclo...")
        fig = self.graficar_metricas_por_ciclo()
        if fig:
            graficos_generados.append('metricas_por_ciclo.png')
            plt.close(fig)
        
        print(f"\n{'='*70}")
        print(f"✅ {len(graficos_generados)} gráficos generados en:")
        print(f"   {self.directorio_salida}")
        print(f"{'='*70}\n")
        
        return graficos_generados


def comparar_visualizaciones(analizador_fijo, analizador_adaptativo, directorio_salida):
    """
    Crea visualizaciones comparativas entre fijo y adaptativo.
    """
    os.makedirs(directorio_salida, exist_ok=True)
    
    df_v_fijo = analizador_fijo.crear_df_servicios_vehiculos()
    df_p_fijo = analizador_fijo.crear_df_servicios_peatones()
    df_v_adapt = analizador_adaptativo.crear_df_servicios_vehiculos()
    df_p_adapt = analizador_adaptativo.crear_df_servicios_peatones()
    
    # Comparación de histogramas
    fig, axes = plt.subplots(2, 2, figsize=(14, 10))
    
    # Vehículos - Fijo
    if not df_v_fijo.empty:
        axes[0, 0].hist(df_v_fijo['tiempo_espera'], bins=30, color='#2E86AB', 
                       alpha=0.6, label='Fijo', edgecolor='black')
        axes[0, 0].axvline(df_v_fijo['tiempo_espera'].mean(), color='red', 
                          linestyle='--', linewidth=2)
        axes[0, 0].set_title('Vehículos - FIJO', fontweight='bold')
        axes[0, 0].set_ylabel('Frecuencia', fontweight='bold')
        axes[0, 0].grid(True, alpha=0.3)
    
    # Vehículos - Adaptativo
    if not df_v_adapt.empty:
        axes[0, 1].hist(df_v_adapt['tiempo_espera'], bins=30, color='#28A745', 
                       alpha=0.6, label='Adaptativo', edgecolor='black')
        axes[0, 1].axvline(df_v_adapt['tiempo_espera'].mean(), color='red',
                          linestyle='--', linewidth=2)
        axes[0, 1].set_title('Vehículos - ADAPTATIVO', fontweight='bold')
        axes[0, 1].grid(True, alpha=0.3)
    
    # Peatones - Fijo
    if not df_p_fijo.empty:
        axes[1, 0].hist(df_p_fijo['tiempo_espera'], bins=30, color='#A23B72',
                       alpha=0.6, label='Fijo', edgecolor='black')
        axes[1, 0].axvline(df_p_fijo['tiempo_espera'].mean(), color='red',
                          linestyle='--', linewidth=2)
        axes[1, 0].set_title('Peatones - FIJO', fontweight='bold')
        axes[1, 0].set_xlabel('Tiempo de espera (s)', fontweight='bold')
        axes[1, 0].set_ylabel('Frecuencia', fontweight='bold')
        axes[1, 0].grid(True, alpha=0.3)
    
    # Peatones - Adaptativo
    if not df_p_adapt.empty:
        axes[1, 1].hist(df_p_adapt['tiempo_espera'], bins=30, color='#FF6B9D',
                       alpha=0.6, label='Adaptativo', edgecolor='black')
        axes[1, 1].axvline(df_p_adapt['tiempo_espera'].mean(), color='red',
                          linestyle='--', linewidth=2)
        axes[1, 1].set_title('Peatones - ADAPTATIVO', fontweight='bold')
        axes[1, 1].set_xlabel('Tiempo de espera (s)', fontweight='bold')
        axes[1, 1].grid(True, alpha=0.3)
    
    plt.suptitle('Comparación: Semáforo Fijo vs Adaptativo', 
                fontsize=15, fontweight='bold', y=1.00)
    plt.tight_layout()
    
    path = os.path.join(directorio_salida, 'comparacion_fijo_vs_adaptativo.png')
    plt.savefig(path, dpi=300, bbox_inches='tight')
    print(f"✅ Gráfico comparativo guardado: {path}")
    plt.close()
    
    return path