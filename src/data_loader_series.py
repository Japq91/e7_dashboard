# src/data_loader_series.py - Para cargar series por departamento

import os
import pandas as pd
import numpy as np

def cargar_series_modelos(modelos, var, agregacion, ssp):
    """
    Carga series temporales para múltiples modelos.
    Nueva estructura: modelo_variable_agregacion_ssp.csv en data/procesados/
    """
    series_dict = {}
    base_dir = "data/procesados"

    for mod in modelos:
        archivo = f"{mod}_{var}_{agregacion}_{ssp}.csv"
        ruta = os.path.join(base_dir, archivo)

        if os.path.exists(ruta):
            try:
                df = pd.read_csv(ruta, index_col=0, parse_dates=True)
                series_dict[mod] = df
            except Exception as e:
                print(f"Error cargando {archivo}: {e}")
                continue
        else:
            print(f"Archivo no encontrado: {archivo}")

    return series_dict

def obtener_serie_departamento(series_dict, departamento):
    """
    Extrae serie temporal de un departamento específico.
    """
    if not series_dict:
        return None

    # Lista para almacenar series de cada modelo
    series_list = []

    for mod, df in series_dict.items():
        if departamento in df.columns:
            serie = df[departamento].rename(mod)
            series_list.append(serie)
        else:
            # Si el departamento no está en este modelo, continuar
            continue

    if not series_list:
        return None

    # Combinar todas las series en un DataFrame
    df_combinado = pd.concat(series_list, axis=1)

    # Calcular promedio si hay más de un modelo
    if len(series_list) > 1:
        df_combinado['PROMEDIO'] = df_combinado.mean(axis=1)

    return df_combinado
