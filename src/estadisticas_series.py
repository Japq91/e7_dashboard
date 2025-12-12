# src/estadisticas_series.py - Versión adaptada

import pandas as pd
import numpy as np

def calcular_estadisticas_periodos(df_series, variable, periodo_base, year_ssp):
    """
    Calcula estadísticas para periodos base y futuro.
    
    Args:
        df_series: DataFrame con series temporales
        variable: tasmin, tasmax o pr
        periodo_base: "1981-2010" o "1991-2020"
        year_ssp: string con formato "centro_ssp", ej: "2030_ssp245"
    """
    # Separar el year_ssp
    centro, ssp = year_ssp.split('_')
    centro = int(centro)
    
    # Definir periodos base
    periodos = {
        "1981-2010": (pd.Timestamp('1981-01-01'), pd.Timestamp('2010-12-31')),
        "1991-2020": (pd.Timestamp('1991-01-01'), pd.Timestamp('2020-12-31'))
    }
    
    # Definir ventana futura (30 años centrados)
    fut_inicio = centro - 14  # 2030-14 = 2016
    fut_fin = centro + 15     # 2030+15 = 2045
    
    # Ajustar para los años disponibles (1981-2065) - puede variar según datos
    fut_inicio = max(fut_inicio, 1981)
    fut_fin = min(fut_fin, 2065)
    
    fecha_inicio_fut = pd.Timestamp(f'{fut_inicio}-01-01')
    fecha_fin_fut = pd.Timestamp(f'{fut_fin}-12-31')
    
    # Filtrar periodos
    fecha_inicio_base, fecha_fin_base = periodos[periodo_base]
    
    # Asegurarse de que tenemos la columna PROMEDIO
    if 'PROMEDIO' not in df_series.columns:
        # Calcular promedio si no existe
        columnas_modelos = [col for col in df_series.columns if col != 'PROMEDIO']
        df_series['PROMEDIO'] = df_series[columnas_modelos].mean(axis=1)
    
    # Filtrar periodos
    base_data = df_series.loc[fecha_inicio_base:fecha_fin_base]
    fut_data = df_series.loc[fecha_inicio_fut:fecha_fin_fut]
    
    # Calcular estadísticas del PROMEDIO
    base_prom = base_data['PROMEDIO'].mean()
    fut_prom = fut_data['PROMEDIO'].mean()
    
    # Calcular desviaciones estándar del PROMEDIO
    base_std = base_data['PROMEDIO'].std()
    fut_std = fut_data['PROMEDIO'].std()
    
    # Calcular cambio
    if variable in ['tasmin', 'tasmax']:
        cambio_abs = fut_prom - base_prom
        cambio_rel = (cambio_abs / base_prom * 100) if base_prom != 0 else 0
        cambio = f"{cambio_abs:.2f}°C"
        cambio_porcentual = f"{cambio_rel:.1f}%"
    elif variable == 'pr':
        cambio_rel = ((fut_prom - base_prom) / base_prom * 100) if base_prom != 0 else 0
        cambio_abs = fut_prom - base_prom
        cambio = f"{cambio_abs:.2f} mm"
        cambio_porcentual = f"{cambio_rel:.1f}%"
    else:
        cambio = "N/A"
        cambio_porcentual = "N/A"
    
    # Nombres completos de variables
    nombres_var = {
        'tasmin': 'Temperatura mínima promedio',
        'tasmax': 'Temperatura máxima promedio',
        'pr': 'Precipitación'
    }
    
    # Unidades (ajustadas a la nueva agregación: anual/estacional)
    unidades = {
        'tasmin': '°C',
        'tasmax': '°C',
        'pr': 'mm'
    }
    
    return {
        'variable_nombre': nombres_var.get(variable, variable),
        'periodo_base': periodo_base,
        'ano_centro': centro,
        'periodo_futuro': f"{fut_inicio}-{fut_fin}",
        'base_promedio': base_prom,
        'base_std': base_std,
        'fut_promedio': fut_prom,
        'fut_std': fut_std,
        'cambio_absoluto': cambio,
        'cambio_porcentual': cambio_porcentual,
        'unidad': unidades.get(variable, ''),
        'años_base': len(base_data),
        'años_futuro': len(fut_data)
    }
