"""
Implementación de semáforo con control de tiempos fijos.
"""
import simpy
import random
import numpy as np
from collections import namedtuple

# Estructura para eventos del semáforo
EventoSemaforo = namedtuple('EventoSemaforo', ['tiempo', 'fase', 'duracion'])


class SemaforoFijo:
    """
    Semáforo con control de tiempos fijos.
    Alterna entre fase vehicular y peatonal con duraciones predefinidas.
    """
    
    def __init__(self, env, cola_vehiculos, cola_peatones, registros,
                 g_v_fijo, g_p_fijo, s_v, s_p, amarillo=3, warmup_time=0):
        """
        Parámetros:
        -----------
        env : simpy.Environment
        cola_vehiculos : simpy.Store
        cola_peatones : simpy.Store
        registros : dict
        g_v_fijo : float
            Duración fase verde vehicular (segundos)
        g_p_fijo : float
            Duración fase verde peatonal (segundos)
        s_v : float
            Tasa de servicio vehicular (veh/seg)
        s_p : float
            Tasa de servicio peatonal (peat/seg)
        amarillo : float
            Duración fase amarilla (segundos)
        warmup_time : float
            Tiempo de warm-up
        """
        self.env = env
        self.cola_vehiculos = cola_vehiculos
        self.cola_peatones = cola_peatones
        self.registros = registros
        self.g_v_fijo = g_v_fijo
        self.g_p_fijo = g_p_fijo
        self.s_v = s_v
        self.s_p = s_p
        self.amarillo = amarillo
        self.warmup_time = warmup_time
        
        # Estado actual
        self.fase_actual = "VERDE_VEHICULAR"  # Inicia con vehículos
        self.ciclo_numero = 0
        
        # Inicializar registros
        self.registros['eventos_semaforo'] = []
        self.registros['servicios_vehiculos'] = []
        self.registros['servicios_peatones'] = []
        self.registros['estado_colas'] = []
    
    def registrar_evento(self, fase, duracion):
        """Registra un cambio de fase del semáforo."""
        if self.env.now >= self.warmup_time:
            self.registros['eventos_semaforo'].append({
                'tiempo': self.env.now,
                'fase': fase,
                'duracion': duracion,
                'ciclo': self.ciclo_numero,
                'cola_v': len(self.cola_vehiculos.items),
                'cola_p': len(self.cola_peatones.items)
            })
    
    def registrar_estado_cola(self):
        """Registra el estado actual de las colas."""
        if self.env.now >= self.warmup_time:
            self.registros['estado_colas'].append({
                'tiempo': self.env.now,
                'cola_v': len(self.cola_vehiculos.items),
                'cola_p': len(self.cola_peatones.items),
                'fase': self.fase_actual
            })
    
    def atender_vehiculos(self, duracion):
        """
        Atiende vehículos durante la fase verde vehicular.
        """
        tiempo_inicio = self.env.now
        tiempo_fin = tiempo_inicio + duracion
        vehiculos_atendidos = 0
        
        while self.env.now < tiempo_fin:
            # Verificar si hay vehículos en cola
            if len(self.cola_vehiculos.items) == 0:
                # No hay vehículos, esperar un poco
                yield self.env.timeout(min(1.0, tiempo_fin - self.env.now))
                continue
            
            # Obtener vehículo
            vehiculo = yield self.cola_vehiculos.get()
            
            # Calcular tiempo de espera
            tiempo_espera = self.env.now - vehiculo.tiempo_llegada
            
            # Tiempo de servicio (exponencial inversa de la tasa)
            tiempo_servicio = random.expovariate(self.s_v)
            
            # Verificar si hay tiempo suficiente en esta fase
            tiempo_restante = tiempo_fin - self.env.now
            if tiempo_servicio > tiempo_restante:
                # No alcanza el tiempo, devolver a la cola
                self.cola_vehiculos.put(vehiculo)
                yield self.env.timeout(tiempo_restante)
                break
            
            # Servir el vehículo
            yield self.env.timeout(tiempo_servicio)
            vehiculos_atendidos += 1
            
            # Registrar servicio
            if self.env.now >= self.warmup_time:
                self.registros['servicios_vehiculos'].append({
                    'id': vehiculo.id,
                    'tiempo_llegada': vehiculo.tiempo_llegada,
                    'tiempo_inicio_servicio': self.env.now - tiempo_servicio,
                    'tiempo_fin_servicio': self.env.now,
                    'tiempo_espera': tiempo_espera,
                    'tiempo_servicio': tiempo_servicio,
                    'ciclo': self.ciclo_numero
                })
        
        return vehiculos_atendidos
    
    def atender_peatones(self, duracion):
        """
        Atiende peatones durante la fase verde peatonal.
        """
        tiempo_inicio = self.env.now
        tiempo_fin = tiempo_inicio + duracion
        peatones_atendidos = 0
        
        while self.env.now < tiempo_fin:
            # Verificar si hay peatones en cola
            if len(self.cola_peatones.items) == 0:
                # No hay peatones, esperar un poco
                yield self.env.timeout(min(1.0, tiempo_fin - self.env.now))
                continue
            
            # Obtener peatón
            peaton = yield self.cola_peatones.get()
            
            # Calcular tiempo de espera
            tiempo_espera = self.env.now - peaton.tiempo_llegada
            
            # Tiempo de servicio (exponencial inversa de la tasa)
            tiempo_servicio = random.expovariate(self.s_p)
            
            # Verificar si hay tiempo suficiente en esta fase
            tiempo_restante = tiempo_fin - self.env.now
            if tiempo_servicio > tiempo_restante:
                # No alcanza el tiempo, devolver a la cola
                self.cola_peatones.put(peaton)
                yield self.env.timeout(tiempo_restante)
                break
            
            # Servir el peatón
            yield self.env.timeout(tiempo_servicio)
            peatones_atendidos += 1
            
            # Registrar servicio
            if self.env.now >= self.warmup_time:
                self.registros['servicios_peatones'].append({
                    'id': peaton.id,
                    'tiempo_llegada': peaton.tiempo_llegada,
                    'tiempo_inicio_servicio': self.env.now - tiempo_servicio,
                    'tiempo_fin_servicio': self.env.now,
                    'tiempo_espera': tiempo_espera,
                    'tiempo_servicio': tiempo_servicio,
                    'ciclo': self.ciclo_numero
                })
        
        return peatones_atendidos
    
    def controlador(self):
        """
        Proceso principal que controla el ciclo del semáforo.
        """
        while True:
            self.ciclo_numero += 1
            
            # ============================================================
            # FASE 1: VERDE VEHICULAR
            # ============================================================
            self.fase_actual = "VERDE_VEHICULAR"
            self.registrar_evento("VERDE_VEHICULAR", self.g_v_fijo)
            self.registrar_estado_cola()
            
            # Atender vehículos
            yield self.env.process(self.atender_vehiculos(self.g_v_fijo))
            
            # ============================================================
            # FASE 2: AMARILLO VEHICULAR
            # ============================================================
            self.fase_actual = "AMARILLO_VEHICULAR"
            self.registrar_evento("AMARILLO_VEHICULAR", self.amarillo)
            yield self.env.timeout(self.amarillo)
            
            # ============================================================
            # FASE 3: VERDE PEATONAL
            # ============================================================
            self.fase_actual = "VERDE_PEATONAL"
            self.registrar_evento("VERDE_PEATONAL", self.g_p_fijo)
            self.registrar_estado_cola()
            
            # Atender peatones
            yield self.env.process(self.atender_peatones(self.g_p_fijo))
            
            # ============================================================
            # FASE 4: AMARILLO PEATONAL
            # ============================================================
            self.fase_actual = "AMARILLO_PEATONAL"
            self.registrar_evento("AMARILLO_PEATONAL", self.amarillo)
            yield self.env.timeout(self.amarillo)
            
            # Registrar estado al final del ciclo
            self.registrar_estado_cola()
    
    def iniciar(self):
        """Inicia el controlador del semáforo."""
        self.env.process(self.controlador())


def calcular_metricas_basicas(registros):
    """
    Calcula métricas básicas de desempeño del sistema.
    """
    metricas = {}
    
    # Métricas de vehículos
    if registros['servicios_vehiculos']:
        esperas_v = [s['tiempo_espera'] for s in registros['servicios_vehiculos']]
        metricas['vehiculos'] = {
            'atendidos': len(esperas_v),
            'espera_media': np.mean(esperas_v),
            'espera_std': np.std(esperas_v),
            'espera_max': np.max(esperas_v),
            'espera_min': np.min(esperas_v),
            'percentil_50': np.percentile(esperas_v, 50),
            'percentil_95': np.percentile(esperas_v, 95)
        }
    else:
        metricas['vehiculos'] = None
    
    # Métricas de peatones
    if registros['servicios_peatones']:
        esperas_p = [s['tiempo_espera'] for s in registros['servicios_peatones']]
        metricas['peatones'] = {
            'atendidos': len(esperas_p),
            'espera_media': np.mean(esperas_p),
            'espera_std': np.std(esperas_p),
            'espera_max': np.max(esperas_p),
            'espera_min': np.min(esperas_p),
            'percentil_50': np.percentile(esperas_p, 50),
            'percentil_95': np.percentile(esperas_p, 95)
        }
    else:
        metricas['peatones'] = None
    
    # Métricas del semáforo
    if registros['eventos_semaforo']:
        eventos = registros['eventos_semaforo']
        ciclos_completos = max([e['ciclo'] for e in eventos])
        
        # Tiempo total en verde por tipo
        tiempo_verde_v = sum([e['duracion'] for e in eventos if e['fase'] == 'VERDE_VEHICULAR'])
        tiempo_verde_p = sum([e['duracion'] for e in eventos if e['fase'] == 'VERDE_PEATONAL'])
        
        metricas['semaforo'] = {
            'ciclos_completos': ciclos_completos,
            'tiempo_verde_vehicular': tiempo_verde_v,
            'tiempo_verde_peatonal': tiempo_verde_p,
            'proporcion_verde_v': tiempo_verde_v / (tiempo_verde_v + tiempo_verde_p) if (tiempo_verde_v + tiempo_verde_p) > 0 else 0
        }
    else:
        metricas['semaforo'] = None
    
    return metricas


def imprimir_metricas(metricas, titulo="MÉTRICAS DEL SISTEMA"):
    """Imprime métricas de forma legible."""
    print(f"\n{'='*70}")
    print(f"{titulo}")
    print(f"{'='*70}")
    
    if metricas['vehiculos']:
        v = metricas['vehiculos']
        print(f"\n🚗 VEHÍCULOS:")
        print(f"   Atendidos:           {v['atendidos']}")
        print(f"   Espera media:        {v['espera_media']:.2f} seg (σ={v['espera_std']:.2f})")
        print(f"   Espera máxima:       {v['espera_max']:.2f} seg")
        print(f"   Percentil 95:        {v['percentil_95']:.2f} seg")
    
    if metricas['peatones']:
        p = metricas['peatones']
        print(f"\n🚶 PEATONES:")
        print(f"   Atendidos:           {p['atendidos']}")
        print(f"   Espera media:        {p['espera_media']:.2f} seg (σ={p['espera_std']:.2f})")
        print(f"   Espera máxima:       {p['espera_max']:.2f} seg")
        print(f"   Percentil 95:        {p['percentil_95']:.2f} seg")
    
    if metricas['semaforo']:
        s = metricas['semaforo']
        print(f"\n🚦 SEMÁFORO:")
        print(f"   Ciclos completos:    {s['ciclos_completos']}")
        print(f"   Tiempo verde veh:    {s['tiempo_verde_vehicular']:.0f} seg")
        print(f"   Tiempo verde peat:   {s['tiempo_verde_peatonal']:.0f} seg")
        print(f"   Proporción verde V:  {s['proporcion_verde_v']*100:.1f}%")
    
    print(f"{'='*70}\n")