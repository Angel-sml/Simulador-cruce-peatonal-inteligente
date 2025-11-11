"""
Script para asegurar que se generen TODOS los gráficos.
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from config import *
from test_semaforo_fijo import simular_semaforo_fijo
from test_semaforo_adaptativo import simular_semaforo_adaptativo
from analisis.metricas import AnalizadorMetricas
from analisis.visualizaciones import VisualizadorSimulacion, comparar_visualizaciones

print("\n" + "="*70)
print("GENERACIÓN COMPLETA DE GRÁFICOS")
print("="*70 + "\n")

# 1. SEMÁFORO FIJO
print("[1/3] Simulando y graficando FIJO...")
registros_fijo, _, _ = simular_semaforo_fijo(
    tiempo_sim=T_SIM,
    lambda_v=LAMBDA_V,
    lambda_p=LAMBDA_P,
    warmup=T_WARMUP,
    semilla=SEMILLA,
    verbose=False
)

dir_fijo = os.path.join(GRAFICOS_DIR, 'fijo')
os.makedirs(dir_fijo, exist_ok=True)
analizador_fijo = AnalizadorMetricas(registros_fijo, T_SIM, T_WARMUP)
visualizador_fijo = VisualizadorSimulacion(analizador_fijo, dir_fijo)
visualizador_fijo.generar_todas_visualizaciones()

# 2. SEMÁFORO ADAPTATIVO
print("\n[2/3] Simulando y graficando ADAPTATIVO...")
registros_adaptativo, _, _ = simular_semaforo_adaptativo(
    tiempo_sim=T_SIM,
    lambda_v=LAMBDA_V,
    lambda_p=LAMBDA_P,
    warmup=T_WARMUP,
    semilla=SEMILLA,
    verbose=False
)

dir_adaptativo = os.path.join(GRAFICOS_DIR, 'adaptativo')
os.makedirs(dir_adaptativo, exist_ok=True)
analizador_adaptativo = AnalizadorMetricas(registros_adaptativo, T_SIM, T_WARMUP)
visualizador_adaptativo = VisualizadorSimulacion(analizador_adaptativo, dir_adaptativo)
visualizador_adaptativo.generar_todas_visualizaciones()

# 3. COMPARACIÓN
print("\n[3/3] Generando gráfico COMPARATIVO...")
dir_comparacion = os.path.join(GRAFICOS_DIR, 'comparacion')
os.makedirs(dir_comparacion, exist_ok=True)
comparar_visualizaciones(analizador_fijo, analizador_adaptativo, dir_comparacion)

# RESUMEN
print("\n" + "="*70)
print("✅ GENERACIÓN COMPLETADA")
print("="*70)
print(f"\n📂 Verifica estas carpetas:")
print(f"   1. {dir_fijo}")
print(f"   2. {dir_adaptativo}")
print(f"   3. {dir_comparacion}")
print("\n" + "="*70 + "\n")

# Contar archivos
import glob
fijo_archivos = len(glob.glob(os.path.join(dir_fijo, "*.png")))
adapt_archivos = len(glob.glob(os.path.join(dir_adaptativo, "*.png")))
comp_archivos = len(glob.glob(os.path.join(dir_comparacion, "*.png")))

print(f"📊 Archivos generados:")
print(f"   Fijo:        {fijo_archivos} gráficos")
print(f"   Adaptativo:  {adapt_archivos} gráficos")
print(f"   Comparación: {comp_archivos} gráfico(s)")
print(f"   TOTAL:       {fijo_archivos + adapt_archivos + comp_archivos} gráficos\n")