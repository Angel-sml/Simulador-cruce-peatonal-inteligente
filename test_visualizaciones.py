"""
Script para generar todas las visualizaciones.
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from config import *
from test_semaforo_fijo import simular_semaforo_fijo
from test_semaforo_adaptativo import simular_semaforo_adaptativo
from analisis.metricas import AnalizadorMetricas
from analisis.visualizaciones import VisualizadorSimulacion, comparar_visualizaciones


def generar_visualizaciones_completas():
    """
    Genera todas las visualizaciones para ambos controladores.
    """
    print("\n" + "="*70)
    print("GENERACIÓN DE VISUALIZACIONES COMPLETAS")
    print("="*70)
    
    # Simular semáforo fijo
    print("\n[1/2] Simulando semáforo FIJO...")
    registros_fijo, _, _ = simular_semaforo_fijo(
        tiempo_sim=T_SIM,
        lambda_v=LAMBDA_V,
        lambda_p=LAMBDA_P,
        warmup=T_WARMUP,
        semilla=SEMILLA,
        verbose=False
    )
    
    # Simular semáforo adaptativo
    print("[2/2] Simulando semáforo ADAPTATIVO...")
    registros_adaptativo, _, _ = simular_semaforo_adaptativo(
        tiempo_sim=T_SIM,
        lambda_v=LAMBDA_V,
        lambda_p=LAMBDA_P,
        warmup=T_WARMUP,
        semilla=SEMILLA,
        verbose=False
    )
    
    # Crear analizadores
    analizador_fijo = AnalizadorMetricas(registros_fijo, T_SIM, T_WARMUP)
    analizador_adaptativo = AnalizadorMetricas(registros_adaptativo, T_SIM, T_WARMUP)
    
    # Visualizaciones semáforo fijo
    print("\n" + "="*70)
    print("SEMÁFORO FIJO")
    print("="*70)
    dir_fijo = os.path.join(GRAFICOS_DIR, 'fijo')
    visualizador_fijo = VisualizadorSimulacion(analizador_fijo, dir_fijo)
    visualizador_fijo.generar_todas_visualizaciones()
    
    # Visualizaciones semáforo adaptativo
    print("\n" + "="*70)
    print("SEMÁFORO ADAPTATIVO")
    print("="*70)
    dir_adaptativo = os.path.join(GRAFICOS_DIR, 'adaptativo')
    visualizador_adaptativo = VisualizadorSimulacion(analizador_adaptativo, dir_adaptativo)
    visualizador_adaptativo.generar_todas_visualizaciones()
    
    # Comparación
    print("\n" + "="*70)
    print("COMPARACIÓN FIJO vs ADAPTATIVO")
    print("="*70 + "\n")
    dir_comparacion = os.path.join(GRAFICOS_DIR, 'comparacion')
    comparar_visualizaciones(analizador_fijo, analizador_adaptativo, dir_comparacion)
    
    print("\n" + "="*70)
    print("✅ TODAS LAS VISUALIZACIONES GENERADAS")
    print("="*70)
    print(f"\n📂 Ubicación de gráficos:")
    print(f"   Fijo:        {dir_fijo}")
    print(f"   Adaptativo:  {dir_adaptativo}")
    print(f"   Comparación: {dir_comparacion}")
    print("="*70 + "\n")


if __name__ == "__main__":
    generar_visualizaciones_completas()