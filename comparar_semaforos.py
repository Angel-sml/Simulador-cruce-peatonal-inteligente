"""
Script para comparar semáforo fijo vs adaptativo.
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from config import *
from test_semaforo_fijo import simular_semaforo_fijo
from test_semaforo_adaptativo import simular_semaforo_adaptativo


def comparar_controladores(tiempo_sim=3600, lambda_v=0.3, lambda_p=0.1, semilla=42):
    """
    Compara el desempeño de ambos controladores.
    """
    print("\n" + "="*70)
    print("COMPARACIÓN: SEMÁFORO FIJO vs ADAPTATIVO")
    print("="*70)
    
    # Ejecutar semáforo fijo
    print("\n[1/2] Ejecutando FIJO...")
    _, metricas_fijo, _ = simular_semaforo_fijo(
        tiempo_sim=tiempo_sim,
        lambda_v=lambda_v,
        lambda_p=lambda_p,
        g_v=G_V_FIJO,
        g_p=G_P_FIJO,
        s_v=S_V,
        s_p=S_P,
        warmup=T_WARMUP,
        semilla=semilla,
        verbose=False
    )
    
    # Ejecutar semáforo adaptativo
    print("[2/2] Ejecutando ADAPTATIVO...")
    _, metricas_adapt, _ = simular_semaforo_adaptativo(
        tiempo_sim=tiempo_sim,
        lambda_v=lambda_v,
        lambda_p=lambda_p,
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
        semilla=semilla,
        verbose=False
    )
    
    # Imprimir comparación
    print("\n" + "="*70)
    print("COMPARACIÓN DE RESULTADOS")
    print("="*70)
    
    print(f"\n{'Métrica':<30} {'FIJO':>15} {'ADAPTATIVO':>15} {'Mejora':>10}")
    print("-"*70)
    
    # Vehículos
    if metricas_fijo['vehiculos'] and metricas_adapt['vehiculos']:
        v_f = metricas_fijo['vehiculos']
        v_a = metricas_adapt['vehiculos']
        
        mejora_espera_v = (v_f['espera_media'] - v_a['espera_media']) / v_f['espera_media'] * 100
        mejora_p95_v = (v_f['percentil_95'] - v_a['percentil_95']) / v_f['percentil_95'] * 100
        
        print(f"{'Espera media vehículos (s)':<30} {v_f['espera_media']:>15.2f} {v_a['espera_media']:>15.2f} {mejora_espera_v:>9.1f}%")
        print(f"{'Percentil 95 vehículos (s)':<30} {v_f['percentil_95']:>15.2f} {v_a['percentil_95']:>15.2f} {mejora_p95_v:>9.1f}%")
    
    # Peatones
    if metricas_fijo['peatones'] and metricas_adapt['peatones']:
        p_f = metricas_fijo['peatones']
        p_a = metricas_adapt['peatones']
        
        mejora_espera_p = (p_f['espera_media'] - p_a['espera_media']) / p_f['espera_media'] * 100
        mejora_p95_p = (p_f['percentil_95'] - p_a['percentil_95']) / p_f['percentil_95'] * 100
        
        print(f"{'Espera media peatones (s)':<30} {p_f['espera_media']:>15.2f} {p_a['espera_media']:>15.2f} {mejora_espera_p:>9.1f}%")
        print(f"{'Percentil 95 peatones (s)':<30} {p_f['percentil_95']:>15.2f} {p_a['percentil_95']:>15.2f} {mejora_p95_p:>9.1f}%")
    
    print("="*70)
    print("\n✅ Comparación completada.\n")
    
    return metricas_fijo, metricas_adapt


if __name__ == "__main__":
    metricas_fijo, metricas_adapt = comparar_controladores(
        tiempo_sim=T_SIM,
        lambda_v=LAMBDA_V,
        lambda_p=LAMBDA_P,
        semilla=SEMILLA
    )