
"""
Script de demostración del semáforo adaptativo.
"""
import simpy
import random
import numpy as np
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from config import *
from simulacion.llegadas import GeneradorLlegadas
from simulacion.semaforo_adaptativo import (
    SemaforoAdaptativo, 
    calcular_metricas_adaptativas,
    imprimir_metricas_adaptativas
)


def simular_semaforo_adaptativo(tiempo_sim=3600, lambda_v=0.3, lambda_p=0.1,
                                g_min=20, g_max=60, g_p=15, s_v=0.5, s_p=1.0,
                                t_v=5, t_p=3, b=5, w_max=90,
                                warmup=300, semilla=42, verbose=True):
    """
    Ejecuta simulación completa con semáforo adaptativo.
    """
    # Configurar semilla
    random.seed(semilla)
    np.random.seed(semilla)
    
    if verbose:
        print(f"\n{'='*70}")
        print(f"SIMULACIÓN: SEMÁFORO ADAPTATIVO")
        print(f"{'='*70}")
        print(f"Parámetros:")
        print(f"  λ_v = {lambda_v} veh/seg | λ_p = {lambda_p} peat/seg")
        print(f"  s_v = {s_v} veh/seg | s_p = {s_p} peat/seg")
        print(f"  Verde veh: [{g_min}, {g_max}]s | Verde peat = {g_p}s")
        print(f"  Umbrales: T_v={t_v} | T_p={t_p} | W_max={w_max}s | b={b}s")
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
    
    # Crear semáforo adaptativo
    semaforo = SemaforoAdaptativo(
        env=env,
        cola_vehiculos=cola_vehiculos,
        cola_peatones=cola_peatones,
        registros=registros,
        g_min=g_min,
        g_max=g_max,
        g_p_fijo=g_p,
        s_v=s_v,
        s_p=s_p,
        t_v=t_v,
        t_p=t_p,
        b_extension=b,
        w_max=w_max,
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
    metricas = calcular_metricas_adaptativas(registros)
    
    if verbose:
        imprimir_metricas_adaptativas(metricas)
    
    return registros, metricas, semaforo


if __name__ == "__main__":
    # Simulación con parámetros por defecto
    registros, metricas, semaforo = simular_semaforo_adaptativo(
        tiempo_sim=T_SIM,
        lambda_v=LAMBDA_V,
        lambda_p=LAMBDA_P,
        g_min=G_MIN,
        g_max=G_MAX,
        g_p=G_P_FIJO,
        s_v=S_V,
        s_p=S_P,
        t_v=T_V,
        t_p=T_P,
        b=B_EXTENSION,
        w_max=W_MAX,
        warmup=T_WARMUP,
        semilla=SEMILLA,
        verbose=True
    )
    
    print("✅ Simulación con semáforo adaptativo completada exitosamente.\n")