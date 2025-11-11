"""
Script de demostración del semáforo con control fijo.
"""
import simpy
import random
import numpy as np
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from config import *
from simulacion.llegadas import GeneradorLlegadas
from simulacion.semaforo_fijo import SemaforoFijo, calcular_metricas_basicas, imprimir_metricas


def simular_semaforo_fijo(tiempo_sim=3600, lambda_v=0.3, lambda_p=0.1,
                          g_v=30, g_p=15, s_v=0.5, s_p=1.0,
                          warmup=300, semilla=42, verbose=True):
    """
    Ejecuta simulación completa con semáforo fijo.
    """
    # Configurar semilla
    random.seed(semilla)
    np.random.seed(semilla)
    
    if verbose:
        print(f"\n{'='*70}")
        print(f"SIMULACIÓN: SEMÁFORO FIJO")
        print(f"{'='*70}")
        print(f"Parámetros:")
        print(f"  λ_v = {lambda_v} veh/seg | λ_p = {lambda_p} peat/seg")
        print(f"  s_v = {s_v} veh/seg | s_p = {s_p} peat/seg")
        print(f"  Verde veh = {g_v}s | Verde peat = {g_p}s")
        print(f"  Tiempo simulación = {tiempo_sim}s | Warm-up = {warmup}s")
        print(f"{'='*70}\n")
    
    # Crear entorno
    env = simpy.Environment()
    
    # Crear colas
    cola_vehiculos = simpy.Store(env)
    cola_peatones = simpy.Store(env)
    
    # Diccionario de registros
    registros = {}
    
    # Crear generador de llegadas
    generador = GeneradorLlegadas(
        env=env,
        lambda_v=lambda_v,
        lambda_p=lambda_p,
        cola_vehiculos=cola_vehiculos,
        cola_peatones=cola_peatones,
        registros=registros,
        warmup_time=warmup
    )
    generador.iniciar()
    
    # Crear semáforo fijo
    semaforo = SemaforoFijo(
        env=env,
        cola_vehiculos=cola_vehiculos,
        cola_peatones=cola_peatones,
        registros=registros,
        g_v_fijo=g_v,
        g_p_fijo=g_p,
        s_v=s_v,
        s_p=s_p,
        amarillo=AMARILLO,
        warmup_time=warmup
    )
    semaforo.iniciar()
    
    # Monitor (opcional)
    def monitor():
        while True:
            yield env.timeout(300)  # Cada 5 minutos
            if verbose:
                print(f"⏱️  t={env.now:.0f}s | Cola V: {len(cola_vehiculos.items)} | "
                      f"Cola P: {len(cola_peatones.items)} | Ciclo: {semaforo.ciclo_numero}")
    
    if verbose:
        env.process(monitor())
    
    # Ejecutar simulación
    if verbose:
        print("🚀 Iniciando simulación...\n")
    
    env.run(until=tiempo_sim)
    
    if verbose:
        print(f"\n✅ Simulación completada\n")
    
    # Calcular métricas
    metricas = calcular_metricas_basicas(registros)
    
    if verbose:
        imprimir_metricas(metricas, "RESULTADOS - SEMÁFORO FIJO")
    
    return registros, metricas, semaforo


if __name__ == "__main__":
    # Simulación con parámetros por defecto
    registros, metricas, semaforo = simular_semaforo_fijo(
        tiempo_sim=T_SIM,
        lambda_v=LAMBDA_V,
        lambda_p=LAMBDA_P,
        g_v=G_V_FIJO,
        g_p=G_P_FIJO,
        s_v=S_V,
        s_p=S_P,
        warmup=T_WARMUP,
        semilla=SEMILLA,
        verbose=True
    )
    
    print("✅ Simulación con semáforo fijo completada exitosamente.\n")