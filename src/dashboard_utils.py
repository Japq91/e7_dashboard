#!/usr/bin/env python
# coding: utf-8

"""
dashboard_utils.py - Funciones auxiliares para el dashboard
"""

import os
import glob
from typing import List, Dict, Tuple, Set


def obtener_lista_modelos(ruta_base: str = "data/modelos_agre") -> List[str]:
    """
    Obtiene la lista de modelos únicos de la carpeta de modelos.
    
    Args:
        ruta_base: Ruta base donde están los archivos .nc
    
    Returns:
        Lista de nombres de modelos únicos y ordenados
    """
    if not os.path.exists(ruta_base):
        return []
    
    archivos = [f for f in os.listdir(ruta_base) if f.endswith('.nc')]
    modelos = set()
    
    for archivo in archivos:
        partes = archivo.split('_')
        if len(partes) >= 4:
            modelos.add(partes[2])  # El modelo es la tercera parte
    
    return sorted(list(modelos))


def obtener_lista_var_agre(ruta_base: str = "data/modelos_agre") -> List[str]:
    """
    Obtiene la lista de combinaciones variable_agregacion únicas.
    
    Args:
        ruta_base: Ruta base donde están los archivos .nc
    
    Returns:
        Lista de combinaciones variable_agregacion
    """
    if not os.path.exists(ruta_base):
        return []
    
    archivos = [f for f in os.listdir(ruta_base) if f.endswith('.nc')]
    var_agre_set = set()
    
    for archivo in archivos:
        partes = archivo.split('_')
        if len(partes) >= 4:
            var_agre_set.add(f"{partes[0]}_{partes[1]}")
    
    return sorted(list(var_agre_set))


def obtener_lista_year_ssp(
    ruta_cambios: str = "data/mod_cambios",
    ruta_ensemble: str = "data/ensamble/cambios"
) -> List[str]:
    """
    Obtiene la lista de combinaciones año_centro-ssp disponibles.
    Busca tanto en modelos individuales como en ensemble.
    
    Args:
        ruta_cambios: Ruta de cambios de modelos individuales
        ruta_ensemble: Ruta de cambios del ensemble
    
    Returns:
        Lista de combinaciones centro_ssp
    """
    year_ssp_set = set()
    
    # Buscar en modelos individuales
    if os.path.exists(ruta_cambios):
        archivos = glob.glob(os.path.join(ruta_cambios, "*.nc"))
        
        for archivo in archivos:
            nombre = os.path.basename(archivo)
            if 'centro-' in nombre:
                partes = nombre.replace('.nc', '').split('_')
                if len(partes) >= 6:
                    try:
                        ssp = partes[3]
                        for parte in partes:
                            if 'centro-' in parte:
                                centro = parte.replace('centro-', '')
                                year_ssp_set.add(f"{centro}_{ssp}")
                                break
                    except (IndexError, ValueError):
                        continue
    
    # Buscar en ensemble (si existe)
    if os.path.exists(ruta_ensemble):
        archivos = glob.glob(os.path.join(ruta_ensemble, "*.nc"))
        
        for archivo in archivos:
            nombre = os.path.basename(archivo)
            if 'centro-' in nombre and nombre.startswith('ensemble'):
                partes = nombre.replace('.nc', '').split('_')
                if len(partes) >= 6:
                    try:
                        ssp = partes[3]
                        for parte in partes:
                            if 'centro-' in parte:
                                centro = parte.replace('centro-', '')
                                year_ssp_set.add(f"{centro}_{ssp}")
                                break
                    except (IndexError, ValueError):
                        continue
    
    return sorted(list(year_ssp_set))


def obtener_lista_escenarios(ruta_base: str = "data/modelos_agre") -> List[str]:
    """
    Obtiene la lista de escenarios únicos.
    
    Args:
        ruta_base: Ruta base donde están los archivos .nc
    
    Returns:
        Lista de escenarios únicos
    """
    if not os.path.exists(ruta_base):
        return []
    
    archivos = [f for f in os.listdir(ruta_base) if f.endswith('.nc')]
    escenarios = set()
    
    for archivo in archivos:
        partes = archivo.split('_')
        if len(partes) >= 4:
            escenarios.add(partes[3].replace('.nc', ''))
    
    return sorted(list(escenarios))


def obtener_centro_years_disponibles() -> List[str]:
    """
    Obtiene la lista de años centro disponibles.
    
    Returns:
        Lista de años centro únicos
    """
    year_ssp_list = obtener_lista_year_ssp()
    centro_years = set()
    
    for item in year_ssp_list:
        if '_' in item:
            centro = item.split('_')[0]
            centro_years.add(centro)
    
    return sorted(list(centro_years))


def obtener_escenarios_disponibles() -> List[str]:
    """
    Obtiene la lista de escenarios disponibles.
    
    Returns:
        Lista de escenarios únicos
    """
    year_ssp_list = obtener_lista_year_ssp()
    escenarios = set()
    
    for item in year_ssp_list:
        if '_' in item:
            ssp = item.split('_')[1]
            escenarios.add(ssp)
    
    return sorted(list(escenarios))


def separar_var_agre(var_agre: str) -> Tuple[str, str]:
    """
    Separa una cadena variable_agregacion en sus componentes.
    
    Args:
        var_agre: Cadena en formato "variable_agregacion"
    
    Returns:
        Tupla (variable, agregacion)
    
    Raises:
        ValueError: Si el formato no es válido
    """
    partes = var_agre.split('_')
    if len(partes) < 2:
        raise ValueError(f"Formato inválido: {var_agre}")
    
    variable = partes[0]
    agregacion = '_'.join(partes[1:])  # Por si la agregación tiene _
    
    return variable, agregacion


def separar_centro_ssp(centro_ssp: str) -> Tuple[str, str]:
    """
    Separa una cadena centro_ssp en sus componentes.
    
    Args:
        centro_ssp: Cadena en formato "centro_ssp"
    
    Returns:
        Tupla (centro, ssp)
    
    Raises:
        ValueError: Si el formato no es válido
    """
    if '_' not in centro_ssp:
        raise ValueError(f"Formato inválido: {centro_ssp}")
    
    centro, ssp = centro_ssp.split('_', 1)
    return centro, ssp


def obtener_unidad_variable(variable: str) -> str:
    """
    Obtiene la unidad de una variable climática.
    
    Args:
        variable: Nombre de la variable
    
    Returns:
        Unidad de la variable
    """
    unidades = {
        'tasmin': '°C',
        'tasmax': '°C',
        'pr': 'mm',
        'tas': '°C',
        'tmin': '°C',
        'tmax': '°C'
    }
    return unidades.get(variable, '')


def obtener_nombre_completo_variable(variable: str) -> str:
    """
    Obtiene el nombre completo/descriptivo de una variable.
    
    Args:
        variable: Nombre corto de la variable
    
    Returns:
        Nombre descriptivo
    """
    nombres = {
        'tasmin': 'Temperatura mínima',
        'tasmax': 'Temperatura máxima',
        'pr': 'Precipitación',
        'tas': 'Temperatura promedio'
    }
    return nombres.get(variable, variable)


def obtener_nombre_agregacion(agregacion: str) -> str:
    """
    Obtiene el nombre descriptivo de una agregación temporal.
    
    Args:
        agregacion: Código de agregación
    
    Returns:
        Nombre descriptivo
    """
    nombres = {
        'ANUAL': 'Anual',
        'DEF': 'Verano (DJF)',
        'MAM': 'Otoño (MAM)',
        'JJA': 'Invierno (JJA)',
        'SON': 'Primavera (SON)',
        'DJF': 'Verano (DJF)',
        'MAM': 'Otoño (MAM)',
        'JJA': 'Invierno (JJA)',
        'SON': 'Primavera (SON)'
    }
    return nombres.get(agregacion, agregacion)


def verificar_datos_disponibles() -> Dict[str, bool]:
    """
    Verifica qué tipos de datos están disponibles.
    
    Returns:
        Diccionario con disponibilidad de datos
    """
    disponibilidad = {
        'modelos_individuales': os.path.exists("data/modelos_agre") and 
                                len(os.listdir("data/modelos_agre")) > 0,
        'cambios_individuales': os.path.exists("data/mod_cambios") and 
                                len(os.listdir("data/mod_cambios")) > 0,
        'ensamble_bruto': os.path.exists("data/ensamble/datos") and 
                          len(os.listdir("data/ensamble/datos")) > 0,
        'ensamble_cambios': os.path.exists("data/ensamble/cambios") and 
                            len(os.listdir("data/ensamble/cambios")) > 0,
        'toe': os.path.exists("data/mod_toe") and 
               len(os.listdir("data/mod_toe")) > 0
    }
    
    return disponibilidad

def obtener_opciones_var_agre_formateadas():
    """
    Devuelve una tupla con:
    1. Lista de nombres amigables
    2. Lista de valores reales
    3. Diccionario de mapeo
    """
    var_agres = obtener_lista_var_agre()
    nombres_vars = []
    mapeo = {}
    
    for var_agre in var_agres:
        try:
            var, agre = var_agre.split('_')
            
            # Nombres en español
            var_espanol = {
                'tasmin': 'T. Mínima',
                'tasmax': 'T. Máxima',
                'pr': 'Prec.',
                'tas': 'Temperatura'
            }.get(var, var)
            
            agre_espanol = {
                'annual': 'Anual',
                'seasonal': 'Estacional',
                'monthly': 'Mensual',
                'djf': 'Verano (DJF)',
                'mam': 'Otoño (MAM)',
                'jja': 'Invierno (JJA)',
                'son': 'Primavera (SON)'
            }.get(agre, agre)
            
            nombre_amigable = f"{var_espanol} →› {agre_espanol}"
            nombres_vars.append(nombre_amigable)
            mapeo[nombre_amigable] = var_agre
            
        except ValueError:
            nombres_vars.append(var_agre)
            mapeo[var_agre] = var_agre
    
    return nombres_vars, var_agres, mapeo

def obtener_opciones_year_ssp_formateadas():
    """
    Versión más simple - solo formatea para visualización
    """
    year_ssp_list = obtener_lista_year_ssp()
    opciones_formateadas = []
    
    for year_ssp in year_ssp_list:
        if '_' in year_ssp:
            year, ssp = year_ssp.split('_')
            # Asignar emoji según escenario
            emoji = {
                'ssp126': '🟢',
                'ssp245': '🟡',
                'ssp370': '🟠',
                'ssp585': '🔴'
            }.get(ssp.lower(), '📊')
            
            opciones_formateadas.append(f"{emoji} {ssp.upper()} → {year}")
        else:
            opciones_formateadas.append(year_ssp)
    
    return opciones_formateadas, year_ssp_list
