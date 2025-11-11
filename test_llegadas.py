"""
Script de demostración del módulo de llegadas.
Ejecuta una simulación simple para verificar el funcionamiento.
"""
import simpy
import random
import numpy as np
import sys
import os

# Agregar directorio padre al path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from config import *
from simulacion.llegadas import GeneradorLlegadas, validar_proceso_poisson, imprimir_validacion


def demo_llegadas(tiempo_sim=600, lambda_v=0.3, lambda_p=0.1, verbose=True):
    """
    Demuestra el funcionamiento del generador de llegadas.
    
    Parámetros:
    -----------
    tiempo_sim : float
        Tiempo de simulación en segundos
    lambda_v : float
        Tasa de llegada de vehículos
    lambda_p : float
        Tasa de llegada de peatones
    verbose : bool
        Si True, imprime eventos en tiempo real
    """
    # Configurar semilla
    random.seed(SEMILLA)
    np.random.seed(SEMILLA)
    
    # Crear entorno SimPy
    env = simpy.Environment()
    
    # Crear colas (Store permite almacenar objetos)
    cola_vehiculos = simpy.Store(env)
    cola_peatones = simpy.Store(env)
    
    # Diccionario para registros
    registros = {}
    
    # Crear generador de llegadas
    generador = GeneradorLlegadas(
        env=env,
        lambda_v=lambda_v,
        lambda_p=lambda_p,
        cola_vehiculos=cola_vehiculos,
        cola_peatones=cola_peatones,
        registros=registros,
        warmup_time=0  # Sin warm-up para esta demo
    )
    
    # Iniciar generadores
    generador.iniciar()
    
    # Proceso monitor (opcional) para mostrar estado cada 60 segundos
    def monitor():
        while True:
            yield env.timeout(60)
            if verbose:
                print(f"⏱️  t={env.now:.0f}s | Veh en cola: {len(cola_vehiculos.items)} | "
                      f"Peat en cola: {len(cola_peatones.items)}")
    
    if verbose:
        env.process(monitor())
    
    # Ejecutar simulación
    print(f"\n🚀 Iniciando simulación de llegadas...")
    print(f"   Tiempo: {tiempo_sim}s | λ_v={lambda_v} | λ_p={lambda_p}")
    print(f"   Llegadas esperadas: Veh≈{lambda_v*tiempo_sim:.0f} | Peat≈{lambda_p*tiempo_sim:.0f}\n")
    
    env.run(until=tiempo_sim)
    
    # Resultados
    print(f"\n✅ Simulación completada\n")
    print(f"{'='*70}")
    print(f"RESULTADOS")
    print(f"{'='*70}")
    print(f"  Vehículos generados:      {len(registros['llegadas_vehiculos'])}")
    print(f"  Peatones generados:       {len(registros['llegadas_peatones'])}")
    print(f"  Vehículos en cola final:  {len(cola_vehiculos.items)}")
    print(f"  Peatones en cola final:   {len(cola_peatones.items)}")
    print(f"{'='*70}\n")
    
    # Validación estadística
    if registros['llegadas_vehiculos']:
        tiempos_v = [r['tiempo'] for r in registros['llegadas_vehiculos']]
        stats_v = validar_proceso_poisson(tiempos_v, lambda_v, "Vehículos")
        imprimir_validacion(stats_v)
    
    if registros['llegadas_peatones']:
        tiempos_p = [r['tiempo'] for r in registros['llegadas_peatones']]
        stats_p = validar_proceso_poisson(tiempos_p, lambda_p, "Peatones")
        imprimir_validacion(stats_p)
    
    return registros, generador


if __name__ == "__main__":
    # Demo corta: 10 minutos
    print("\n" + "="*70)
    print("DEMOSTRACIÓN: GENERADOR DE LLEGADAS POISSON")
    print("="*70)
    
    registros, generador = demo_llegadas(
        tiempo_sim=600,  # 10 minutos
        lambda_v=LAMBDA_V,
        lambda_p=LAMBDA_P,
        verbose=False  # Cambiar a True para ver monitor
    )
    
    print("\n✅ Demo completada. Los generadores funcionan correctamente.\n")