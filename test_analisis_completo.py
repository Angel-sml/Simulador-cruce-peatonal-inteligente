"""
Script para ejecutar simulación completa y análisis de métricas.
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from config import *
from test_semaforo_fijo import simular_semaforo_fijo
from test_semaforo_adaptativo import simular_semaforo_adaptativo
from analisis.metricas import AnalizadorMetricas, imprimir_resumen_metricas


def analisis_completo_fijo():
    """Ejecuta simulación fija y análisis completo."""
    print("\n" + "="*70)
    print("ANÁLISIS COMPLETO - SEMÁFORO FIJO")
    print("="*70 + "\n")
    
    # Ejecutar simulación
    registros, _, _ = simular_semaforo_fijo(
        tiempo_sim=T_SIM,
        lambda_v=LAMBDA_V,
        lambda_p=LAMBDA_P,
        warmup=T_WARMUP,
        semilla=SEMILLA,
        verbose=False
    )
    
    # Crear analizador
    analizador = AnalizadorMetricas(registros, T_SIM, T_WARMUP)
    
    # Generar resumen
    resumen = analizador.generar_resumen_completo()
    imprimir_resumen_metricas(resumen)
    
    # Exportar a CSV
    print("📁 Exportando datos a CSV...")
    archivos = analizador.exportar_a_csv(os.path.join(CSV_DIR, 'fijo'))
    print(f"   ✅ {len(archivos)} archivos creados en {CSV_DIR}/fijo/\n")
    
    return analizador, resumen


def analisis_completo_adaptativo():
    """Ejecuta simulación adaptativa y análisis completo."""
    print("\n" + "="*70)
    print("ANÁLISIS COMPLETO - SEMÁFORO ADAPTATIVO")
    print("="*70 + "\n")
    
    # Ejecutar simulación
    registros, _, _ = simular_semaforo_adaptativo(
        tiempo_sim=T_SIM,
        lambda_v=LAMBDA_V,
        lambda_p=LAMBDA_P,
        warmup=T_WARMUP,
        semilla=SEMILLA,
        verbose=False
    )
    
    # Crear analizador
    analizador = AnalizadorMetricas(registros, T_SIM, T_WARMUP)
    
    # Generar resumen
    resumen = analizador.generar_resumen_completo()
    imprimir_resumen_metricas(resumen)
    
    # Exportar a CSV
    print("📁 Exportando datos a CSV...")
    archivos = analizador.exportar_a_csv(os.path.join(CSV_DIR, 'adaptativo'))
    print(f"   ✅ {len(archivos)} archivos creados en {CSV_DIR}/adaptativo/\n")
    
    return analizador, resumen


def comparar_resumenes(resumen_fijo, resumen_adaptativo):
    """Compara los resúmenes de ambos controladores."""
    print("\n" + "="*70)
    print("COMPARACIÓN DETALLADA - FIJO vs ADAPTATIVO")
    print("="*70)
    
    print(f"\n{'Métrica':<40} {'FIJO':>12} {'ADAPT':>12} {'Mejora':>10}")
    print("-"*70)
    
    # Vehículos - Espera media
    if resumen_fijo.get('metricas_espera_vehiculos') and resumen_adaptativo.get('metricas_espera_vehiculos'):
        v_f = resumen_fijo['metricas_espera_vehiculos']['espera_media']
        v_a = resumen_adaptativo['metricas_espera_vehiculos']['espera_media']
        mejora = (v_f - v_a) / v_f * 100
        print(f"{'Espera media vehículos (s)':<40} {v_f:>12.2f} {v_a:>12.2f} {mejora:>9.1f}%")
        
        # Percentil 95
        v_f_p95 = resumen_fijo['metricas_espera_vehiculos']['percentil_95']
        v_a_p95 = resumen_adaptativo['metricas_espera_vehiculos']['percentil_95']
        mejora_p95 = (v_f_p95 - v_a_p95) / v_f_p95 * 100
        print(f"{'Percentil 95 vehículos (s)':<40} {v_f_p95:>12.2f} {v_a_p95:>12.2f} {mejora_p95:>9.1f}%")
        
        # Espera excesiva
        v_f_exc = resumen_fijo['metricas_espera_vehiculos']['prop_espera_excesiva'] * 100
        v_a_exc = resumen_adaptativo['metricas_espera_vehiculos']['prop_espera_excesiva'] * 100
        print(f"{'Espera excesiva vehículos (%)':<40} {v_f_exc:>12.1f} {v_a_exc:>12.1f}")
    
    print()
    
    # Peatones - Espera media
    if resumen_fijo.get('metricas_espera_peatones') and resumen_adaptativo.get('metricas_espera_peatones'):
        p_f = resumen_fijo['metricas_espera_peatones']['espera_media']
        p_a = resumen_adaptativo['metricas_espera_peatones']['espera_media']
        mejora = (p_f - p_a) / p_f * 100
        print(f"{'Espera media peatones (s)':<40} {p_f:>12.2f} {p_a:>12.2f} {mejora:>9.1f}%")
        
        # Percentil 95
        p_f_p95 = resumen_fijo['metricas_espera_peatones']['percentil_95']
        p_a_p95 = resumen_adaptativo['metricas_espera_peatones']['percentil_95']
        mejora_p95 = (p_f_p95 - p_a_p95) / p_f_p95 * 100
        print(f"{'Percentil 95 peatones (s)':<40} {p_f_p95:>12.2f} {p_a_p95:>12.2f} {mejora_p95:>9.1f}%")
        
        # Espera excesiva
        p_f_exc = resumen_fijo['metricas_espera_peatones']['prop_espera_excesiva'] * 100
        p_a_exc = resumen_adaptativo['metricas_espera_peatones']['prop_espera_excesiva'] * 100
        print(f"{'Espera excesiva peatones (%)':<40} {p_f_exc:>12.1f} {p_a_exc:>12.1f}")
    
    print()
    
    # Throughput
    if resumen_fijo.get('throughput_vehiculos') and resumen_adaptativo.get('throughput_vehiculos'):
        th_v_f = resumen_fijo['throughput_vehiculos']['throughput_hora']
        th_v_a = resumen_adaptativo['throughput_vehiculos']['throughput_hora']
        mejora_th = (th_v_a - th_v_f) / th_v_f * 100
        print(f"{'Throughput vehicular (veh/h)':<40} {th_v_f:>12.1f} {th_v_a:>12.1f} {mejora_th:>9.1f}%")
    
    if resumen_fijo.get('throughput_peatones') and resumen_adaptativo.get('throughput_peatones'):
        th_p_f = resumen_fijo['throughput_peatones']['throughput_hora']
        th_p_a = resumen_adaptativo['throughput_peatones']['throughput_hora']
        mejora_th = (th_p_a - th_p_f) / th_p_f * 100
        print(f"{'Throughput peatonal (peat/h)':<40} {th_p_f:>12.1f} {th_p_a:>12.1f} {mejora_th:>9.1f}%")
    
    print()
    
    # Equidad
    if resumen_fijo.get('equidad') and resumen_adaptativo.get('equidad'):
        eq_f = resumen_fijo['equidad']['ratio_equidad']
        eq_a = resumen_adaptativo['equidad']['ratio_equidad']
        mejora_eq = (eq_f - eq_a) / eq_f * 100
        print(f"{'Ratio de equidad (menor=mejor)':<40} {eq_f:>12.3f} {eq_a:>12.3f} {mejora_eq:>9.1f}%")
    
    print("="*70 + "\n")


if __name__ == "__main__":
    # Análisis semáforo fijo
    analizador_fijo, resumen_fijo = analisis_completo_fijo()
    
    # Análisis semáforo adaptativo

    analizador_adaptativo, resumen_adaptativo = analisis_completo_adaptativo()
    
    # Comparación
    comparar_resumenes(resumen_fijo, resumen_adaptativo)
    
    print("✅ Análisis completo finalizado.\n")