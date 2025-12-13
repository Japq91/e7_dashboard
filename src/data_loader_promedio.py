#!/usr/bin/env python
# coding: utf-8

"""
data_loader_promedio.py - Funciones para cargar datos de promedio/ensemble
"""

import os
import xarray as xr
import numpy as np

def cargar_cambios_ensemble(variable, agregacion, ssp, periodo_base, centro_year="2050"):
    """
    Carga los cambios del ensemble para un escenario específico.
    
    Args:
        variable: Variable climática (tasmin, tasmax, pr)
        agregacion: Agregación temporal (ANUAL, DEF, MAM, etc.)
        ssp: Escenario (ssp245, ssp585)
        periodo_base: Periodo base (1981-2010 o 1991-2020)
        centro_year: Año centro (2030, 2035, ..., 2050)
    
    Returns:
        DataArray con los cambios del ensemble
    """
    ruta_base = "data/ensamble/cambios"
    
    # Construir nombre del archivo
    nombre_archivo = f"ensemble_{variable}_{agregacion}_{ssp}_{periodo_base}_centro-{centro_year}.nc"
    ruta_completa = os.path.join(ruta_base, nombre_archivo)
    
    if not os.path.exists(ruta_completa):
        # Intentar con diferentes formatos de periodo_base
        if "-" in periodo_base:
            periodo_base_alt = periodo_base.replace("-", "_")
            nombre_archivo_alt = f"ensemble_{variable}_{agregacion}_{ssp}_{periodo_base_alt}_centro-{centro_year}.nc"
            ruta_completa = os.path.join(ruta_base, nombre_archivo_alt)
    
    if not os.path.exists(ruta_completa):
        print(f"  -> Archivo no encontrado: {ruta_completa}")
        return None
    
    try:
        ds = xr.open_dataset(ruta_completa)
        # La variable se llama delta_{variable}
        var_name = f"delta_{variable}"
        if var_name in ds:
            return ds[var_name]
        else:
            # Buscar cualquier variable que comience con 'delta'
            for var in ds.data_vars:
                if var.startswith('delta'):
                    return ds[var]
            return None
    except Exception as e:
        print(f"  -> Error cargando ensemble: {e}")
        return None


def cargar_toe(variable, agregacion):
    """
    Carga el TOE (Time of Emergence) para una variable y agregación.
    
    Args:
        variable: Variable -> pr, tasmax, tasmin
        agregacion: Agregación temporal -> SON, JJA, Anual, etc.
    
    Returns:
        DataArray con el TOE 1
        TOE1 para temperatura es el TOE 1
        TOE1 para precipitacion es el TOE -1, osea valores negativos
    """
    ruta_base = "data/mod_toe"
    
    # Construir nombre del archivo (asumiendo formato ensemble)
    nombre_archivo = f"ensemble_{variable}_{agregacion}_toe.nc"
    ruta_completa = os.path.join(ruta_base, nombre_archivo)
    
    if not os.path.exists(ruta_completa):
        print(f"  -> Archivo TOE no encontrado: {ruta_completa}")
        return None
    
    try:
        ds = xr.open_dataset(ruta_completa)
        # # Buscar variable TOE
        # for var in ds.data_vars:
        #     if 'toe' in var.lower() or 'emergence' in var.lower():
        #         return ds[var]
        # Si no encuentra, retorna la primera variable        
        if 'pr' in variable: ds_toe_var=ds[list(ds.data_vars)[-1]]
        else: ds_toe_var=ds[list(ds.data_vars)[0]]
        return ds_toe_var #ds[list(ds.data_vars)[0]]
    except Exception as e:
        print(f"  -> Error cargando TOE: {e}")
        return None


def obtener_info_ensemble(variable):
    """
    Obtiene información de colores y unidades para el ensemble.
    """
    config = {
        'tasmin': {
            'cmap': 'RdBu_r',
            'units': '°C',
            'label': 'Cambio en temperatura mínima'
        },
        'tasmax': {
            'cmap': 'RdBu_r',
            'units': '°C',
            'label': 'Cambio en temperatura máxima'
        },
        'pr': {
            'cmap': 'BrBG',
            'units': '%',
            'label': 'Cambio en precipitación'
        }
    }
    return config.get(variable, {'cmap': 'viridis', 'units': '', 'label': ''})

def cargar_significancia_ensemble(variable, agregacion, ssp, periodo_base, centro_year="2050"):
    """
    Carga los p-values del ensemble para un escenario específico.
    
    Args:
        variable: Variable climática (tasmin, tasmax, pr)
        agregacion: Agregación temporal (ANUAL, DEF, MAM, etc.)
        ssp: Escenario (ssp245, ssp585)
        periodo_base: Periodo base (1981-2010 o 1991-2020)
        centro_year: Año centro (2030, 2035, ..., 2050)
    
    Returns:
        DataArray con los p-values del ensemble
    """
    ruta_base = "data/ensamble/significancia"
    
    # Construir nombre del archivo
    nombre_archivo = f"ensemble_{variable}_{agregacion}_{ssp}_{periodo_base}_centro-{centro_year}.npy"
    ruta_completa = os.path.join(ruta_base, nombre_archivo)
    
    if not os.path.exists(ruta_completa):
        # Intentar con formato alternativo
        if "-" in periodo_base:
            periodo_base_alt = periodo_base.replace("-", "_")
            nombre_archivo_alt = f"ensemble_{variable}_{agregacion}_{ssp}_{periodo_base_alt}_centro-{centro_year}.npy"
            ruta_completa = os.path.join(ruta_base, nombre_archivo_alt)
    
    if not os.path.exists(ruta_completa):
        print(f"  -> Archivo de significancia no encontrado: {nombre_archivo}")
        return None
    
    try:
        # Cargar array numpy
        pvals_array = np.load(ruta_completa, allow_pickle=True)
        
        # Necesitamos las coordenadas para crear un DataArray
        # Cargamos un archivo de cambios para obtener las coordenadas
        cambios_ref = cargar_cambios_ensemble(variable, agregacion, ssp, periodo_base, centro_year)
        
        if cambios_ref is not None:
            # Crear DataArray con las mismas coordenadas
            pvals_da = xr.DataArray(
                pvals_array,
                coords={
                    'lat': cambios_ref.lat,
                    'lon': cambios_ref.lon
                },
                dims=['lat', 'lon']
            )
            return pvals_da
        else:
            print(f"  -> No se pudieron obtener coordenadas para la significancia")
            return None
            
    except Exception as e:
        print(f"  -> Error cargando significancia: {e}")
        return None
