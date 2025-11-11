"""
Configuración centralizada del proyecto.
"""
import os

# PARÁMETROS DE LLEGADAS (Procesos Poisson)
LAMBDA_V = 0.3  # veh/seg → 1080 veh/hora
LAMBDA_P = 0.1  # peat/seg → 360 peat/hora

# PARÁMETROS DE SERVICIO
S_V = 0.5  # veh/seg → 1800 veh/hora
S_P = 1.0  # peat/seg → 3600 peat/hora

# CONTROL SEMÁFORO FIJO
G_V_FIJO = 30  # segundos
G_P_FIJO = 15  # segundos
AMARILLO = 3   # segundos

# CONTROL SEMÁFORO ADAPTATIVO
G_MIN = 20
G_MAX = 60
T_V = 5        # umbral cola vehicular
T_P = 3        # umbral cola peatonal
B_EXTENSION = 5
W_MAX = 90     # espera máxima peatonal

# SIMULACIÓN
T_SIM = 3600   # 1 hora
T_WARMUP = 300 # 5 minutos
SEMILLA = 42

# RUTAS
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
RESULTADOS_DIR = os.path.join(BASE_DIR, 'resultados')
CSV_DIR = os.path.join(RESULTADOS_DIR, 'csv')
GRAFICOS_DIR = os.path.join(RESULTADOS_DIR, 'graficos')

for directorio in [RESULTADOS_DIR, CSV_DIR, GRAFICOS_DIR]:
    os.makedirs(directorio, exist_ok=True)

def imprimir_config():
    print("="*70)
    print("CONFIGURACIÓN DEL SISTEMA")
    print("="*70)
    print(f"\nLLEGADAS:")
    print(f"  λ_v = {LAMBDA_V} veh/seg ({LAMBDA_V*3600:.0f} veh/hora)")
    print(f"  λ_p = {LAMBDA_P} peat/seg ({LAMBDA_P*3600:.0f} peat/hora)")
    print(f"\nSERVICIO:")
    print(f"  s_v = {S_V} veh/seg | s_p = {S_P} peat/seg")
    print(f"\nCONTROL FIJO:")
    print(f"  Verde veh: {G_V_FIJO}s | Verde peat: {G_P_FIJO}s")
    print(f"\nCONTROL ADAPTATIVO:")
    print(f"  Rango: [{G_MIN}, {G_MAX}]s | T_v={T_V} | T_p={T_P} | b={B_EXTENSION}s")
    print(f"\nSIMULACIÓN: {T_SIM}s (warm-up: {T_WARMUP}s)")
    print("="*70)

if __name__ == "__main__":
    imprimir_config()