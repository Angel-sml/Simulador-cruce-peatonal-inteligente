"""
Implementación de semáforo con control adaptativo (inteligente).
"""
import simpy
import random
import numpy as np


class SemaforoAdaptativo:
    """
    Semáforo con control adaptativo que ajusta tiempos según demanda.
    """
    
    def __init__(self, env, cola_vehiculos, cola_peatones, registros,
                 g_min, g_max, g_p_fijo, s_v, s_p, t_v, t_p, b_extension,
                 w_max, amarillo=3, warmup_time=0):
        """
        Parámetros:
        -----------
        env : simpy.Environment
        cola_vehiculos : simpy.Store
        cola_peatones : simpy.Store
        registros : dict
        g_min : float
            Duración mínima fase verde vehicular (segundos)
        g_max : float
            Duración máxima fase verde vehicular (segundos)
        g_p_fijo : float
            Duración fase verde peatonal (segundos)
        s_v : float
            Tasa de servicio vehicular (veh/seg)
        s_p : float
            Tasa de servicio peatonal (peat/seg)
        t_v : int
            Umbral de cola vehicular para extender verde
        t_p : int
            Umbral de cola peatonal para activar fase
        b_extension : float
            Bloques de extensión de tiempo (segundos)
        w_max : float
            Espera máxima peatonal para prioridad forzada (segundos)
        amarillo : float
            Duración fase amarilla (segundos)
        warmup_time : float
            Tiempo de warm-up
        """
        self.env = env
        self.cola_vehiculos = cola_vehiculos
        self.cola_peatones = cola_peatones
        self.registros = registros
        self.g_min = g_min
        self.g_max = g_max
        self.g_p_fijo = g_p_fijo
        self.s_v = s_v
        self.s_p = s_p
        self.t_v = t_v
        self.t_p = t_p
        self.b_extension = b_extension
        self.w_max = w_max
        self.amarillo = amarillo
        self.warmup_time = warmup_time
        
        # Estado actual
        self.fase_actual = "VERDE_VEHICULAR"
        self.ciclo_numero = 0
        
        # Inicializar registros
        self.registros['eventos_semaforo'] = []
        self.registros['servicios_vehiculos'] = []
        self.registros['servicios_peatones'] = []
        self.registros['estado_colas'] = []
        self.registros['decisiones_adaptativas'] = []
    
    def registrar_evento(self, fase, duracion, info_adicional=None):
        """Registra un cambio de fase del semáforo."""
        if self.env.now >= self.warmup_time:
            evento = {
                'tiempo': self.env.now,
                'fase': fase,
                'duracion': duracion,
                'ciclo': self.ciclo_numero,
                'cola_v': len(self.cola_vehiculos.items),
                'cola_p': len(self.cola_peatones.items)
            }
            if info_adicional:
                evento.update(info_adicional)
            self.registros['eventos_semaforo'].append(evento)
    
    def registrar_estado_cola(self):
        """Registra el estado actual de las colas."""
        if self.env.now >= self.warmup_time:
            self.registros['estado_colas'].append({
                'tiempo': self.env.now,
                'cola_v': len(self.cola_vehiculos.items),
                'cola_p': len(self.cola_peatones.items),
                'fase': self.fase_actual
            })
    
    def registrar_decision(self, tipo, motivo, valor):
        """Registra decisiones del control adaptativo."""
        if self.env.now >= self.warmup_time:
            self.registros['decisiones_adaptativas'].append({
                'tiempo': self.env.now,
                'ciclo': self.ciclo_numero,
                'tipo': tipo,
                'motivo': motivo,
                'valor': valor,
                'cola_v': len(self.cola_vehiculos.items),
                'cola_p': len(self.cola_peatones.items)
            })
    
    def obtener_espera_maxima_peatonal(self):
        """
        Calcula la espera máxima actual de los peatones en cola.
        """
        if len(self.cola_peatones.items) == 0:
            return 0
        
        esperas = [self.env.now - p.tiempo_llegada for p in self.cola_peatones.items]
        return max(esperas)
    
    def atender_vehiculos(self, duracion):
        """
        Atiende vehículos durante la fase verde vehicular.
        """
        tiempo_inicio = self.env.now
        tiempo_fin = tiempo_inicio + duracion
        vehiculos_atendidos = 0
        
        while self.env.now < tiempo_fin:
            if len(self.cola_vehiculos.items) == 0:
                yield self.env.timeout(min(1.0, tiempo_fin - self.env.now))
                continue
            
            vehiculo = yield self.cola_vehiculos.get()
            tiempo_espera = self.env.now - vehiculo.tiempo_llegada
            tiempo_servicio = random.expovariate(self.s_v)
            
            tiempo_restante = tiempo_fin - self.env.now
            if tiempo_servicio > tiempo_restante:
                self.cola_vehiculos.put(vehiculo)
                yield self.env.timeout(tiempo_restante)
                break
            
            yield self.env.timeout(tiempo_servicio)
            vehiculos_atendidos += 1
            
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
            if len(self.cola_peatones.items) == 0:
                yield self.env.timeout(min(1.0, tiempo_fin - self.env.now))
                continue
            
            peaton = yield self.cola_peatones.get()
            tiempo_espera = self.env.now - peaton.tiempo_llegada
            tiempo_servicio = random.expovariate(self.s_p)
            
            tiempo_restante = tiempo_fin - self.env.now
            if tiempo_servicio > tiempo_restante:
                self.cola_peatones.put(peaton)
                yield self.env.timeout(tiempo_restante)
                break
            
            yield self.env.timeout(tiempo_servicio)
            peatones_atendidos += 1
            
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
    
    def fase_verde_vehicular_adaptativa(self):
        """
        Gestiona la fase verde vehicular con lógica adaptativa.
        Inicia con G_min y extiende según demanda.
        """
        tiempo_verde_total = self.g_min
        
        # Fase inicial (mínimo)
        self.registrar_evento("VERDE_VEHICULAR_INICIAL", self.g_min, 
                             {'extension': 0, 'tiempo_total': self.g_min})
        yield self.env.process(self.atender_vehiculos(self.g_min))
        
        # Lógica de extensión
        extensiones = 0
        while tiempo_verde_total < self.g_max:
            # Verificar condiciones para extensión
            cola_actual_v = len(self.cola_vehiculos.items)
            espera_max_p = self.obtener_espera_maxima_peatonal()
            
            # Condición 1: Prioridad peatonal por espera excesiva
            if espera_max_p > self.w_max:
                self.registrar_decision(
                    'FIN_EXTENSION',
                    'PRIORIDAD_PEATONAL',
                    {'espera_max_p': espera_max_p, 'w_max': self.w_max}
                )
                break
            
            # Condición 2: Cola vehicular insuficiente
            if cola_actual_v < self.t_v:
                self.registrar_decision(
                    'FIN_EXTENSION',
                    'COLA_VEHICULAR_BAJA',
                    {'cola_v': cola_actual_v, 't_v': self.t_v}
                )
                break
            
            # Condición 3: Se alcanzó el máximo
            if tiempo_verde_total + self.b_extension > self.g_max:
                self.registrar_decision(
                    'FIN_EXTENSION',
                    'MAXIMO_ALCANZADO',
                    {'tiempo_total': tiempo_verde_total, 'g_max': self.g_max}
                )
                break
            
            # EXTENDER la fase verde
            extensiones += 1
            tiempo_verde_total += self.b_extension
            
            self.registrar_decision(
                'EXTENSION',
                'ALTA_DEMANDA_VEHICULAR',
                {'extension': extensiones, 'tiempo_total': tiempo_verde_total, 'cola_v': cola_actual_v}
            )
            
            self.registrar_evento("VERDE_VEHICULAR_EXTENSION", self.b_extension,
                                 {'extension': extensiones, 'tiempo_total': tiempo_verde_total})
            
            yield self.env.process(self.atender_vehiculos(self.b_extension))
        
        return tiempo_verde_total
    
    def debe_activar_fase_peatonal(self):
        """
        Decide si se debe activar la fase peatonal.
        """
        cola_p = len(self.cola_peatones.items)
        espera_max_p = self.obtener_espera_maxima_peatonal()
        
        # Criterio 1: Hay suficientes peatones esperando
        if cola_p >= self.t_p:
            return True, "COLA_PEATONAL_ALTA"
        
        # Criterio 2: Hay peatones con espera excesiva
        if espera_max_p > self.w_max:
            return True, "ESPERA_EXCESIVA"
        
        # Criterio 3: Hay peatones esperando (activación por defecto)
        if cola_p > 0:
            return True, "HAY_PEATONES"
        
        return False, "SIN_PEATONES"
    
    def controlador(self):
        """
        Proceso principal que controla el ciclo del semáforo adaptativo.
        """
        while True:
            self.ciclo_numero += 1
            
            # ============================================================
            # FASE 1: VERDE VEHICULAR (ADAPTATIVO)
            # ============================================================
            self.fase_actual = "VERDE_VEHICULAR"
            self.registrar_estado_cola()
            
            tiempo_verde_vehicular = yield self.env.process(
                self.fase_verde_vehicular_adaptativa()
            )
            
            # ============================================================
            # FASE 2: AMARILLO VEHICULAR
            # ============================================================
            self.fase_actual = "AMARILLO_VEHICULAR"
            self.registrar_evento("AMARILLO_VEHICULAR", self.amarillo)
            yield self.env.timeout(self.amarillo)
            
            # ============================================================
            # DECIDIR SI ACTIVAR FASE PEATONAL
            # ============================================================
            activar_peatonal, motivo = self.debe_activar_fase_peatonal()
            
            if activar_peatonal:
                # ============================================================
                # FASE 3: VERDE PEATONAL
                # ============================================================
                self.fase_actual = "VERDE_PEATONAL"
                self.registrar_evento("VERDE_PEATONAL", self.g_p_fijo, {'motivo': motivo})
                self.registrar_estado_cola()
                
                yield self.env.process(self.atender_peatones(self.g_p_fijo))
                
                # ============================================================
                # FASE 4: AMARILLO PEATONAL
                # ============================================================
                self.fase_actual = "AMARILLO_PEATONAL"
                self.registrar_evento("AMARILLO_PEATONAL", self.amarillo)
                yield self.env.timeout(self.amarillo)
            else:
                # Saltar fase peatonal si no hay demanda
                self.registrar_decision(
                    'SALTAR_FASE_PEATONAL',
                    motivo,
                    {'cola_p': len(self.cola_peatones.items)}
                )
            
            # Registrar estado al final del ciclo
            self.registrar_estado_cola()
    
    def iniciar(self):
        """Inicia el controlador del semáforo."""
        self.env.process(self.controlador())


def calcular_metricas_adaptativas(registros):
    """
    Calcula métricas específicas del control adaptativo.
    """
    from simulacion.semaforo_fijo import calcular_metricas_basicas
    
    # Métricas básicas
    metricas = calcular_metricas_basicas(registros)
    
    # Métricas adaptativas adicionales
    if registros['decisiones_adaptativas']:
        decisiones = registros['decisiones_adaptativas']
        
        extensiones = [d for d in decisiones if d['tipo'] == 'EXTENSION']
        fin_extensiones = [d for d in decisiones if d['tipo'] == 'FIN_EXTENSION']
        
        metricas['adaptativo'] = {
            'total_extensiones': len(extensiones),
            'extensiones_por_ciclo': len(extensiones) / max(1, metricas['semaforo']['ciclos_completos']),
            'motivos_fin': {}
        }
        
        # Contar motivos de finalización
        for decision in fin_extensiones:
            motivo = decision['motivo']
            metricas['adaptativo']['motivos_fin'][motivo] = \
                metricas['adaptativo']['motivos_fin'].get(motivo, 0) + 1
    else:
        metricas['adaptativo'] = None
    
    # Duración promedio de fase verde vehicular
    if registros['eventos_semaforo']:
        eventos_v = [e for e in registros['eventos_semaforo'] 
                     if 'VEHICULAR' in e['fase'] and e['fase'] != 'AMARILLO_VEHICULAR']
        
        if eventos_v:
            # Agrupar por ciclo
            duraciones_por_ciclo = {}
            for evento in eventos_v:
                ciclo = evento['ciclo']
                if ciclo not in duraciones_por_ciclo:
                    duraciones_por_ciclo[ciclo] = 0
                duraciones_por_ciclo[ciclo] += evento['duracion']
            
            duraciones = list(duraciones_por_ciclo.values())
            
            if not metricas['adaptativo']:
                metricas['adaptativo'] = {}
            
            metricas['adaptativo']['duracion_verde_vehicular'] = {
                'media': np.mean(duraciones),
                'std': np.std(duraciones),
                'min': np.min(duraciones),
                'max': np.max(duraciones)
            }
    
    return metricas


def imprimir_metricas_adaptativas(metricas, titulo="MÉTRICAS - SEMÁFORO ADAPTATIVO"):
    """Imprime métricas del sistema adaptativo."""
    from simulacion.semaforo_fijo import imprimir_metricas
    
    # Imprimir métricas básicas
    imprimir_metricas(metricas, titulo)
    
    # Imprimir métricas adaptativas
    if metricas.get('adaptativo'):
        print(f"{'='*70}")
        print(f"MÉTRICAS ADAPTATIVAS")
        print(f"{'='*70}")
        
        a = metricas['adaptativo']
        
        if 'total_extensiones' in a:
            print(f"\n🎛️  EXTENSIONES:")
            print(f"   Total:               {a['total_extensiones']}")
            print(f"   Por ciclo (media):   {a['extensiones_por_ciclo']:.2f}")
        
        if 'motivos_fin' in a:
            print(f"\n📊 MOTIVOS DE FIN DE EXTENSIÓN:")
            for motivo, count in a['motivos_fin'].items():
                print(f"   {motivo:25s}: {count} veces")
        
        if 'duracion_verde_vehicular' in a:
            d = a['duracion_verde_vehicular']
            print(f"\n⏱️  DURACIÓN VERDE VEHICULAR:")
            print(f"   Media:               {d['media']:.2f} seg")
            print(f"   Desv. estándar:      {d['std']:.2f} seg")
            print(f"   Rango:               [{d['min']:.0f}, {d['max']:.0f}] seg")
        
        print(f"{'='*70}\n")