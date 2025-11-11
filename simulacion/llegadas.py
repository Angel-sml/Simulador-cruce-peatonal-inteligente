"""
Módulo de generación de llegadas con procesos Poisson.
"""
import simpy
import random
import numpy as np
from collections import namedtuple

# Estructura para almacenar información de agentes
Vehiculo = namedtuple('Vehiculo', ['id', 'tiempo_llegada'])
Peaton = namedtuple('Peaton', ['id', 'tiempo_llegada'])


class GeneradorLlegadas:
    """
    Gestiona la generación de llegadas de vehículos y peatones
    siguiendo procesos Poisson independientes.
    """
    
    def __init__(self, env, lambda_v, lambda_p, cola_vehiculos, cola_peatones, 
                 registros, warmup_time=0):
        """
        Parámetros:
        -----------
        env : simpy.Environment
            Entorno de simulación
        lambda_v : float
            Tasa de llegada de vehículos (veh/seg)
        lambda_p : float
            Tasa de llegada de peatones (peat/seg)
        cola_vehiculos : simpy.Store
            Cola donde se almacenan vehículos
        cola_peatones : simpy.Store
            Cola donde se almacenan peatones
        registros : dict
            Diccionario para almacenar eventos
        warmup_time : float
            Tiempo de warm-up (no se registran datos)
        """
        self.env = env
        self.lambda_v = lambda_v
        self.lambda_p = lambda_p
        self.cola_vehiculos = cola_vehiculos
        self.cola_peatones = cola_peatones
        self.registros = registros
        self.warmup_time = warmup_time
        
        # Contadores
        self.vehiculo_id = 0
        self.peaton_id = 0
        
        # Inicializar listas de registros
        self.registros['llegadas_vehiculos'] = []
        self.registros['llegadas_peatones'] = []
    
    def generar_vehiculos(self):
        """
        Proceso generador de llegadas de vehículos (Poisson).
        Los tiempos entre llegadas siguen distribución exponencial.
        """
        while True:
            # Tiempo entre llegadas ~ Exponencial(lambda_v)
            tiempo_entre_llegadas = random.expovariate(self.lambda_v)
            yield self.env.timeout(tiempo_entre_llegadas)
            
            # Crear nuevo vehículo
            self.vehiculo_id += 1
            vehiculo = Vehiculo(
                id=self.vehiculo_id,
                tiempo_llegada=self.env.now
            )
            
            # Agregar a la cola
            self.cola_vehiculos.put(vehiculo)
            
            # Registrar llegada (solo después del warm-up)
            if self.env.now >= self.warmup_time:
                self.registros['llegadas_vehiculos'].append({
                    'id': vehiculo.id,
                    'tiempo': self.env.now,
                    'cola_longitud': len(self.cola_vehiculos.items)
                })
    
    def generar_peatones(self):
        """
        Proceso generador de llegadas de peatones (Poisson).
        Los tiempos entre llegadas siguen distribución exponencial.
        """
        while True:
            # Tiempo entre llegadas ~ Exponencial(lambda_p)
            tiempo_entre_llegadas = random.expovariate(self.lambda_p)
            yield self.env.timeout(tiempo_entre_llegadas)
            
            # Crear nuevo peatón
            self.peaton_id += 1
            peaton = Peaton(
                id=self.peaton_id,
                tiempo_llegada=self.env.now
            )
            
            # Agregar a la cola
            self.cola_peatones.put(peaton)
            
            # Registrar llegada (solo después del warm-up)
            if self.env.now >= self.warmup_time:
                self.registros['llegadas_peatones'].append({
                    'id': peaton.id,
                    'tiempo': self.env.now,
                    'cola_longitud': len(self.cola_peatones.items),
                    'tiempo_espera_actual': 0  # Se actualizará cuando sea atendido
                })
    
    def iniciar(self):
        """Inicia ambos procesos generadores."""
        self.env.process(self.generar_vehiculos())
        self.env.process(self.generar_peatones())


def validar_proceso_poisson(tiempos_llegada, lambda_esperada, nombre="Proceso"):
    """
    Valida estadísticamente si un conjunto de llegadas sigue un proceso Poisson.
    
    Parámetros:
    -----------
    tiempos_llegada : list
        Lista de tiempos de llegada
    lambda_esperada : float
        Tasa esperada del proceso
    nombre : str
        Nombre del proceso (para reportes)
    
    Returns:
    --------
    dict : Estadísticas del proceso
    """
    if len(tiempos_llegada) < 2:
        return None
    
    # Calcular tiempos entre llegadas
    tiempos_llegada_sorted = sorted(tiempos_llegada)
    inter_arribos = np.diff(tiempos_llegada_sorted)
    
    # Estadísticas
    media_inter_arribos = np.mean(inter_arribos)
    std_inter_arribos = np.std(inter_arribos)
    
    # Teórico: media = 1/lambda, std = 1/lambda
    media_teorica = 1 / lambda_esperada
    std_teorica = 1 / lambda_esperada
    
    # Tasa observada
    lambda_observada = 1 / media_inter_arribos if media_inter_arribos > 0 else 0
    
    stats = {
        'nombre': nombre,
        'n_llegadas': len(tiempos_llegada),
        'lambda_esperada': lambda_esperada,
        'lambda_observada': lambda_observada,
        'media_inter_arribos': media_inter_arribos,
        'media_teorica': media_teorica,
        'error_media': abs(media_inter_arribos - media_teorica) / media_teorica * 100,
        'std_inter_arribos': std_inter_arribos,
        'std_teorica': std_teorica,
        'coef_variacion': std_inter_arribos / media_inter_arribos if media_inter_arribos > 0 else 0
    }
    
    return stats


def imprimir_validacion(stats):
    """Imprime resultados de validación de forma legible."""
    if stats is None:
        print("No hay suficientes datos para validar")
        return
    
    print(f"\n{'='*70}")
    print(f"VALIDACIÓN: {stats['nombre']}")
    print(f"{'='*70}")
    print(f"  Llegadas registradas:     {stats['n_llegadas']}")
    print(f"  λ esperada:               {stats['lambda_esperada']:.4f}")
    print(f"  λ observada:              {stats['lambda_observada']:.4f}")
    print(f"  Error λ:                  {abs(stats['lambda_observada']-stats['lambda_esperada'])/stats['lambda_esperada']*100:.2f}%")
    print(f"\n  Media inter-arribos:")
    print(f"    Observada:              {stats['media_inter_arribos']:.4f} seg")
    print(f"    Teórica (1/λ):          {stats['media_teorica']:.4f} seg")
    print(f"    Error:                  {stats['error_media']:.2f}%")
    print(f"\n  Coef. de variación:       {stats['coef_variacion']:.4f}")
    print(f"  (Exponencial teórico = 1.0)")
    print(f"{'='*70}\n")