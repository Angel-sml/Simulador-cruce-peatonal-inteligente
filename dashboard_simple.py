"""
Dashboard simple sin Jupyter usando matplotlib interactivo.
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from config import *
from test_semaforo_fijo import simular_semaforo_fijo
from test_semaforo_adaptativo import simular_semaforo_adaptativo
from analisis.metricas import AnalizadorMetricas, imprimir_resumen_metricas
import matplotlib.pyplot as plt

def menu_interactivo():
    """Menú interactivo para simulaciones."""
    
    while True:
        print("\n" + "="*70)
        print("🚦 DASHBOARD SIMPLE - SIMULACIÓN CRUCE PEATONAL")
        print("="*70)
        print("\nOpciones:")
        print("  1. Simular semáforo FIJO")
        print("  2. Simular semáforo ADAPTATIVO")
        print("  3. COMPARAR ambos")
        print("  4. Cambiar parámetros")
        print("  5. Salir")
        print("="*70)
        
        opcion = input("\nSelecciona opción (1-5): ").strip()
        
        if opcion == '1':
            ejecutar_fijo()
        elif opcion == '2':
            ejecutar_adaptativo()
        elif opcion == '3':
            comparar_ambos()
        elif opcion == '4':
            cambiar_parametros()
        elif opcion == '5':
            print("\n👋 ¡Hasta luego!\n")
            break
        else:
            print("❌ Opción inválida")

def ejecutar_fijo():
    """Ejecuta simulación fija."""
    print("\n🚀 Ejecutando FIJO...")
    registros, _, _ = simular_semaforo_fijo(
        tiempo_sim=1800,
        lambda_v=LAMBDA_V,
        lambda_p=LAMBDA_P,
        warmup=180,
        semilla=42,
        verbose=False
    )
    
    analizador = AnalizadorMetricas(registros, 1800, 180)
    resumen = analizador.generar_resumen_completo()
    imprimir_resumen_metricas(resumen)
    
    input("\nPresiona ENTER para continuar...")

def ejecutar_adaptativo():
    """Ejecuta simulación adaptativa."""
    print("\n🚀 Ejecutando ADAPTATIVO...")
    registros, _, _ = simular_semaforo_adaptativo(
        tiempo_sim=1800,
        lambda_v=LAMBDA_V,
        lambda_p=LAMBDA_P,
        warmup=180,
        semilla=42,
        verbose=False
    )
    
    analizador = AnalizadorMetricas(registros, 1800, 180)
    resumen = analizador.generar_resumen_completo()
    imprimir_resumen_metricas(resumen)
    
    input("\nPresiona ENTER para continuar...")

def comparar_ambos():
    """Compara ambos controladores."""
    print("\n⚡ COMPARANDO FIJO vs ADAPTATIVO...")
    
    from comparar_semaforos import comparar_controladores
    comparar_controladores(tiempo_sim=1800, lambda_v=LAMBDA_V, lambda_p=LAMBDA_P)
    
    input("\nPresiona ENTER para continuar...")

def cambiar_parametros():
    """Permite cambiar parámetros."""
    global LAMBDA_V, LAMBDA_P
    
    print("\n⚙️ CAMBIAR PARÁMETROS")
    print("="*70)
    print(f"Actuales: λ_v={LAMBDA_V}, λ_p={LAMBDA_P}")
    
    try:
        nuevo_v = input(f"\nNuevo λ_v (Enter para mantener {LAMBDA_V}): ").strip()
        if nuevo_v:
            LAMBDA_V = float(nuevo_v)
        
        nuevo_p = input(f"Nuevo λ_p (Enter para mantener {LAMBDA_P}): ").strip()
        if nuevo_p:
            LAMBDA_P = float(nuevo_p)
        
        print(f"\n✅ Parámetros actualizados: λ_v={LAMBDA_V}, λ_p={LAMBDA_P}")
    except:
        print("❌ Error en los valores ingresados")

if __name__ == "__main__":
    menu_interactivo()