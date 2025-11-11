"""
Módulo de análisis y cálculo de métricas del sistema.
"""
import pandas as pd
import numpy as np
from scipy import stats


class AnalizadorMetricas:
    """
    Clase para analizar y calcular métricas completas del sistema.
    """
    
    def __init__(self, registros, tiempo_sim, tiempo_warmup):
        """
        Parámetros:
        -----------
        registros : dict
            Diccionario con todos los registros de la simulación
        tiempo_sim : float
            Tiempo total de simulación
        tiempo_warmup : float
            Tiempo de warm-up
        """
        self.registros = registros
        self.tiempo_sim = tiempo_sim
        self.tiempo_warmup = tiempo_warmup
        self.tiempo_efectivo = tiempo_sim - tiempo_warmup
    
    def crear_df_servicios_vehiculos(self):
        """Crea DataFrame con servicios de vehículos."""
        if not self.registros.get('servicios_vehiculos'):
            return pd.DataFrame()
        
        df = pd.DataFrame(self.registros['servicios_vehiculos'])
        return df
    
    def crear_df_servicios_peatones(self):
        """Crea DataFrame con servicios de peatones."""
        if not self.registros.get('servicios_peatones'):
            return pd.DataFrame()
        
        df = pd.DataFrame(self.registros['servicios_peatones'])
        return df
    
    def crear_df_eventos_semaforo(self):
        """Crea DataFrame con eventos del semáforo."""
        if not self.registros.get('eventos_semaforo'):
            return pd.DataFrame()
        
        df = pd.DataFrame(self.registros['eventos_semaforo'])
        return df
    
    def crear_df_estado_colas(self):
        """Crea DataFrame con estado de colas en el tiempo."""
        if not self.registros.get('estado_colas'):
            return pd.DataFrame()
        
        df = pd.DataFrame(self.registros['estado_colas'])
        return df
    
    def calcular_metricas_espera(self, df_servicios, tipo="vehiculos"):
        """
        Calcula métricas de tiempo de espera.
        """
        if df_servicios.empty:
            return None
        
        esperas = df_servicios['tiempo_espera'].values
        
        metricas = {
            'tipo': tipo,
            'n_atendidos': len(esperas),
            'espera_media': np.mean(esperas),
            'espera_mediana': np.median(esperas),
            'espera_std': np.std(esperas),
            'espera_min': np.min(esperas),
            'espera_max': np.max(esperas),
            'percentil_25': np.percentile(esperas, 25),
            'percentil_50': np.percentile(esperas, 50),
            'percentil_75': np.percentile(esperas, 75),
            'percentil_90': np.percentile(esperas, 90),
            'percentil_95': np.percentile(esperas, 95),
            'percentil_99': np.percentile(esperas, 99),
            'coef_variacion': np.std(esperas) / np.mean(esperas) if np.mean(esperas) > 0 else 0
        }
        
        # Proporción con espera excesiva (>60s para vehículos, >90s para peatones)
        umbral_excesivo = 60 if tipo == "vehiculos" else 90
        metricas['prop_espera_excesiva'] = np.sum(esperas > umbral_excesivo) / len(esperas)
        metricas['umbral_excesivo'] = umbral_excesivo
        
        return metricas
    
    def calcular_throughput(self, df_servicios, tipo="vehiculos"):
        """
        Calcula throughput (entidades/hora).
        """
        if df_servicios.empty:
            return None
        
        n_atendidos = len(df_servicios)
        tiempo_horas = self.tiempo_efectivo / 3600
        
        return {
            'tipo': tipo,
            'throughput_hora': n_atendidos / tiempo_horas if tiempo_horas > 0 else 0,
            'throughput_minuto': n_atendidos / (self.tiempo_efectivo / 60) if self.tiempo_efectivo > 0 else 0,
            'n_atendidos': n_atendidos
        }
    
    def calcular_metricas_por_ciclo(self, df_servicios, tipo="vehiculos"):
        """
        Calcula métricas agregadas por ciclo del semáforo.
        """
        if df_servicios.empty or 'ciclo' not in df_servicios.columns:
            return pd.DataFrame()
        
        metricas_ciclo = df_servicios.groupby('ciclo').agg({
            'tiempo_espera': ['count', 'mean', 'std', 'max'],
            'tiempo_servicio': ['mean', 'sum']
        }).reset_index()
        
        metricas_ciclo.columns = ['ciclo', 'n_atendidos', 'espera_media', 'espera_std', 
                                   'espera_max', 'servicio_medio', 'tiempo_servicio_total']
        
        return metricas_ciclo
    
    def calcular_uso_tiempo_verde(self, df_eventos):
        """
        Calcula el uso del tiempo verde por tipo.
        """
        if df_eventos.empty:
            return None
        
        # Filtrar eventos de verde
        verde_v = df_eventos[df_eventos['fase'].str.contains('VERDE_VEHICULAR', na=False)]
        verde_p = df_eventos[df_eventos['fase'] == 'VERDE_PEATONAL']
        
        tiempo_verde_v = verde_v['duracion'].sum()
        tiempo_verde_p = verde_p['duracion'].sum()
        tiempo_total_verde = tiempo_verde_v + tiempo_verde_p
        
        return {
            'tiempo_verde_vehicular': tiempo_verde_v,
            'tiempo_verde_peatonal': tiempo_verde_p,
            'tiempo_total_verde': tiempo_total_verde,
            'proporcion_verde_v': tiempo_verde_v / tiempo_total_verde if tiempo_total_verde > 0 else 0,
            'proporcion_verde_p': tiempo_verde_p / tiempo_total_verde if tiempo_total_verde > 0 else 0,
            'ciclos_totales': df_eventos['ciclo'].max() if 'ciclo' in df_eventos.columns else 0
        }
    
    def calcular_longitud_cola_promedio(self, df_estado):
        """
        Calcula longitud de cola promedio en el tiempo.
        """
        if df_estado.empty:
            return None
        
        return {
            'cola_v_media': df_estado['cola_v'].mean(),
            'cola_v_max': df_estado['cola_v'].max(),
            'cola_p_media': df_estado['cola_p'].mean(),
            'cola_p_max': df_estado['cola_p'].max()
        }
    
    def calcular_indice_equidad(self, metricas_v, metricas_p):
        """
        Calcula un índice de equidad entre vehículos y peatones.
        Basado en la relación de tiempos de espera normalizados.
        """
        if not metricas_v or not metricas_p:
            return None
        
        # Normalizar por umbral de espera aceptable
        umbral_v = 60  # segundos
        umbral_p = 90  # segundos
        
        espera_norm_v = metricas_v['espera_media'] / umbral_v
        espera_norm_p = metricas_p['espera_media'] / umbral_p
        
        # Índice de equidad (1 = perfecta equidad, >1 = sesgo)
        ratio_equidad = max(espera_norm_v, espera_norm_p) / min(espera_norm_v, espera_norm_p) \
                        if min(espera_norm_v, espera_norm_p) > 0 else float('inf')
        
        return {
            'espera_normalizada_v': espera_norm_v,
            'espera_normalizada_p': espera_norm_p,
            'ratio_equidad': ratio_equidad,
            'sesgo': 'vehiculos' if espera_norm_v > espera_norm_p else 'peatones'
        }
    
    def generar_resumen_completo(self):
        """
        Genera resumen completo con todas las métricas.
        """
        # Crear DataFrames
        df_v = self.crear_df_servicios_vehiculos()
        df_p = self.crear_df_servicios_peatones()
        df_eventos = self.crear_df_eventos_semaforo()
        df_estado = self.crear_df_estado_colas()
        
        # Calcular métricas
        resumen = {
            'configuracion': {
                'tiempo_simulacion': self.tiempo_sim,
                'tiempo_warmup': self.tiempo_warmup,
                'tiempo_efectivo': self.tiempo_efectivo
            },
            'metricas_espera_vehiculos': self.calcular_metricas_espera(df_v, "vehiculos"),
            'metricas_espera_peatones': self.calcular_metricas_espera(df_p, "peatones"),
            'throughput_vehiculos': self.calcular_throughput(df_v, "vehiculos"),
            'throughput_peatones': self.calcular_throughput(df_p, "peatones"),
            'uso_tiempo_verde': self.calcular_uso_tiempo_verde(df_eventos),
            'longitud_colas': self.calcular_longitud_cola_promedio(df_estado),
            'equidad': self.calcular_indice_equidad(
                self.calcular_metricas_espera(df_v, "vehiculos"),
                self.calcular_metricas_espera(df_p, "peatones")
            )
        }
        
        return resumen
    
    def exportar_a_csv(self, directorio_salida):
        """
        Exporta todos los DataFrames a archivos CSV.
        """
        import os
        os.makedirs(directorio_salida, exist_ok=True)
        
        archivos_creados = []
        
        # Servicios de vehículos
        df_v = self.crear_df_servicios_vehiculos()
        if not df_v.empty:
            path = os.path.join(directorio_salida, 'servicios_vehiculos.csv')
            df_v.to_csv(path, index=False)
            archivos_creados.append(path)
        
        # Servicios de peatones
        df_p = self.crear_df_servicios_peatones()
        if not df_p.empty:
            path = os.path.join(directorio_salida, 'servicios_peatones.csv')
            df_p.to_csv(path, index=False)
            archivos_creados.append(path)
        
        # Eventos del semáforo
        df_eventos = self.crear_df_eventos_semaforo()
        if not df_eventos.empty:
            path = os.path.join(directorio_salida, 'eventos_semaforo.csv')
            df_eventos.to_csv(path, index=False)
            archivos_creados.append(path)
        
        # Estado de colas
        df_estado = self.crear_df_estado_colas()
        if not df_estado.empty:
            path = os.path.join(directorio_salida, 'estado_colas.csv')
            df_estado.to_csv(path, index=False)
            archivos_creados.append(path)
        
        # Métricas por ciclo
        if not df_v.empty:
            df_ciclos_v = self.calcular_metricas_por_ciclo(df_v, "vehiculos")
            if not df_ciclos_v.empty:
                path = os.path.join(directorio_salida, 'metricas_por_ciclo_vehiculos.csv')
                df_ciclos_v.to_csv(path, index=False)
                archivos_creados.append(path)
        
        if not df_p.empty:
            df_ciclos_p = self.calcular_metricas_por_ciclo(df_p, "peatones")
            if not df_ciclos_p.empty:
                path = os.path.join(directorio_salida, 'metricas_por_ciclo_peatones.csv')
                df_ciclos_p.to_csv(path, index=False)
                archivos_creados.append(path)
        
        # Resumen de métricas
        resumen = self.generar_resumen_completo()
        df_resumen = self._convertir_resumen_a_df(resumen)
        path = os.path.join(directorio_salida, 'resumen_metricas.csv')
        df_resumen.to_csv(path, index=False)
        archivos_creados.append(path)
        
        return archivos_creados
    
    def _convertir_resumen_a_df(self, resumen):
        """Convierte el resumen a un DataFrame plano."""
        filas = []
        
        for seccion, datos in resumen.items():
            if datos is None:
                continue
            if isinstance(datos, dict):
                for clave, valor in datos.items():
                    filas.append({
                        'seccion': seccion,
                        'metrica': clave,
                        'valor': valor
                    })
        
        return pd.DataFrame(filas)


def imprimir_resumen_metricas(resumen):
    """
    Imprime el resumen de métricas de forma legible.
    """
    print("\n" + "="*70)
    print("RESUMEN COMPLETO DE MÉTRICAS")
    print("="*70)
    
    # Configuración
    if resumen.get('configuracion'):
        cfg = resumen['configuracion']
        print(f"\n⚙️  CONFIGURACIÓN:")
        print(f"   Tiempo total simulación:  {cfg['tiempo_simulacion']:.0f} seg")
        print(f"   Tiempo warm-up:           {cfg['tiempo_warmup']:.0f} seg")
        print(f"   Tiempo efectivo:          {cfg['tiempo_efectivo']:.0f} seg")
    
    # Vehículos
    if resumen.get('metricas_espera_vehiculos'):
        v = resumen['metricas_espera_vehiculos']
        print(f"\n🚗 VEHÍCULOS:")
        print(f"   Atendidos:                {v['n_atendidos']}")
        print(f"   Espera media:             {v['espera_media']:.2f} seg (σ={v['espera_std']:.2f})")
        print(f"   Espera mediana:           {v['espera_mediana']:.2f} seg")
        print(f"   Rango:                    [{v['espera_min']:.2f}, {v['espera_max']:.2f}] seg")
        print(f"   Percentil 95:             {v['percentil_95']:.2f} seg")
        print(f"   Espera excesiva (>{v['umbral_excesivo']}s): {v['prop_espera_excesiva']*100:.1f}%")
    
    # Peatones
    if resumen.get('metricas_espera_peatones'):
        p = resumen['metricas_espera_peatones']
        print(f"\n🚶 PEATONES:")
        print(f"   Atendidos:                {p['n_atendidos']}")
        print(f"   Espera media:             {p['espera_media']:.2f} seg (σ={p['espera_std']:.2f})")
        print(f"   Espera mediana:           {p['espera_mediana']:.2f} seg")
        print(f"   Rango:                    [{p['espera_min']:.2f}, {p['espera_max']:.2f}] seg")
        print(f"   Percentil 95:             {p['percentil_95']:.2f} seg")
        print(f"   Espera excesiva (>{p['umbral_excesivo']}s): {p['prop_espera_excesiva']*100:.1f}%")
    
    # Throughput
    if resumen.get('throughput_vehiculos'):
        tv = resumen['throughput_vehiculos']
        print(f"\n📊 THROUGHPUT VEHICULAR:")
        print(f"   {tv['throughput_hora']:.1f} veh/hora")
    
    if resumen.get('throughput_peatones'):
        tp = resumen['throughput_peatones']
        print(f"\n📊 THROUGHPUT PEATONAL:")
        print(f"   {tp['throughput_hora']:.1f} peat/hora")
    
    # Uso de tiempo verde
    if resumen.get('uso_tiempo_verde'):
        u = resumen['uso_tiempo_verde']
        print(f"\n🚦 USO DE TIEMPO VERDE:")
        print(f"   Ciclos totales:           {u['ciclos_totales']}")
        print(f"   Tiempo verde vehicular:   {u['tiempo_verde_vehicular']:.0f} seg ({u['proporcion_verde_v']*100:.1f}%)")
        print(f"   Tiempo verde peatonal:    {u['tiempo_verde_peatonal']:.0f} seg ({u['proporcion_verde_p']*100:.1f}%)")
    
    # Longitud de colas
    if resumen.get('longitud_colas'):
        lc = resumen['longitud_colas']
        print(f"\n📈 LONGITUD DE COLAS:")
        print(f"   Cola vehicular media:     {lc['cola_v_media']:.2f} veh (máx: {lc['cola_v_max']})")
        print(f"   Cola peatonal media:      {lc['cola_p_media']:.2f} peat (máx: {lc['cola_p_max']})")
    
    # Equidad
    if resumen.get('equidad'):
        eq = resumen['equidad']
        print(f"\n⚖️  ÍNDICE DE EQUIDAD:")
        print(f"   Espera normalizada veh:   {eq['espera_normalizada_v']:.3f}")
        print(f"   Espera normalizada peat:  {eq['espera_normalizada_p']:.3f}")
        print(f"   Ratio de equidad:         {eq['ratio_equidad']:.3f}")
        print(f"   Sesgo hacia:              {eq['sesgo']}")
    
    print("="*70 + "\n")