#!/usr/bin/env python
# coding: utf-8
"""
01_preproc_02.py - Cálculo de cambios y significancia (versión actualizada)
Nueva estructura:
- Detecta automáticamente modelos, variables, agregaciones y escenarios
- Procesa cada combinación: (modelo, variable, agregación, escenario)
- Calcula cambios futuros vs. periodo de referencia
- Calcula significancia estadística
- Guarda salidas por cada combinación y año centro
"""
import os
import sys
import numpy as np
import xarray as xr

# Añadir carpeta src al path
sys.path.append(os.path.join(os.path.dirname(__file__), "src"))

# Años centro para ventanas futuras
CENTER_YEARS = [2030, 2035, 2040, 2045, 2050]
REF_LABEL   = "1981-2010" #"1991-2020"  # "1981-2010"

# Importamos las funciones necesarias del módulo actualizado
from aux_cambios_significancia import (seleccionar_periodo,calcular_delta,calcular_pvals)
# ============================================================
# CONFIGURACIÓN (ahora dinámica)
# ============================================================
BASE_DIR      = "data"
MOD_DIR       = os.path.join(BASE_DIR, "modelos_agre")  # Nueva ruta
OUT_CAMBIOS   = os.path.join(BASE_DIR, "mod_cambios")
OUT_SIGNIF    = os.path.join(BASE_DIR, "mod_significancia")
os.makedirs(OUT_CAMBIOS, exist_ok=True)
os.makedirs(OUT_SIGNIF, exist_ok=True)
# Periodos base fijos
REF_PERIODS = {"1981-2010": (1981, 2010),"1991-2020": (1991, 2020)}
# Selección actual de referencia
REF_START, REF_END = REF_PERIODS[REF_LABEL]
# Longitud de ventana futura: 30 años
FUT_WINDOW = 30  # años

# ============================================================
# FUNCIONES AUXILIARES PARA NUEVA ESTRUCTURA
# ============================================================

def extraer_dimensiones_archivo(nombre_archivo):
    """
    Extrae dimensiones del nombre del archivo.
    Formato: {variable}_{AGREGACION}_{modelo}_{ssp}.nc
    """
    base_name = nombre_archivo.replace('.nc', '')
    partes = base_name.split('_')
    
    if len(partes) >= 4:
        return {
            'variable': partes[0],      # tasmin, tasmax, pr
            'agregacion': partes[1],    # ANUAL, DEF, MAM, etc.
            'modelo': partes[2],        # ecmwf-51, ncep-2, etc.
            'ssp': partes[3]            # ssp245, ssp585
        }
    return None


def cargar_combinacion(ruta_base, modelo, variable, agregacion, ssp):
    """
    Carga un archivo específico según la combinación de dimensiones.
    Reemplaza a la función antigua cargar_var.
    """
    # Construir nombre del archivo
    nombre_archivo = f"{variable}_{agregacion}_{modelo}_{ssp}.nc"
    ruta_completa = os.path.join(ruta_base, nombre_archivo)
    
    # Intentar diferentes combinaciones de mayúsculas/minúsculas
    posibles_nombres = [
        nombre_archivo,
        nombre_archivo.lower(),
        nombre_archivo.upper(),
        f"{variable.lower()}_{agregacion.lower()}_{modelo}_{ssp}.nc",
        f"{variable.upper()}_{agregacion.upper()}_{modelo}_{ssp}.nc"
    ]
    
    ruta_encontrada = None
    for nombre in posibles_nombres:
        ruta_test = os.path.join(ruta_base, nombre)
        if os.path.exists(ruta_test):
            ruta_encontrada = ruta_test
            break
    
    if ruta_encontrada is None:
        print(f"  -> Archivo no encontrado para {modelo}_{variable}_{agregacion}_{ssp}")
        return None
    
    try:
        
        # Cargar dataset
        ds = xr.open_dataset(ruta_encontrada)
        #ds = ds0.interp(lon=np.arange(-82, 1+reso, reso), 
        #                lat=np.arange(-19, 1+reso, reso))
        # Buscar la variable (puede tener diferentes nombres)
        # Primero intentar con el nombre exacto de la variable
        if variable in ds.data_vars:
            return ds[variable]
        
        # Buscar nombres alternativos
        posibles_vars = [
            variable.lower(),
            variable.upper(),
            variable.replace('tas', 't'),  # tasmin -> tmin, tasmax -> tmax
            'tas' if 'tas' in variable else variable,  # Para temperaturas
            'pr' if variable == 'pr' else None
        ]
        
        for var_name in posibles_vars:
            if var_name and var_name in ds.data_vars:
                #print(f"  -> Usando variable '{var_name}' en lugar de '{variable}'")
                return ds[var_name]
        
        # Si no encontramos, ver qué variables hay disponibles
        #print(f"  -> Variables disponibles en {nombre_archivo}: {list(ds.data_vars)}")
        return None
        
    except Exception as e:
        print(f"  -> Error cargando {ruta_encontrada}: {e}")
        return None


# ============================================================
# FUNCIÓN PRINCIPAL ACTUALIZADA
# ============================================================

def procesar_combinacion(modelo, variable, agregacion, ssp):
    """
    Procesa una combinación específica de dimensiones.
    """

    # VERIFICAR SI TODOS LOS ARCHIVOS PARA ESTA COMBINACIÓN YA EXISTEN
    archivos_existen = True
    for cy in CENTER_YEARS:
        out_nc = os.path.join(
            OUT_CAMBIOS,
            f"{modelo}_{variable}_{agregacion}_{ssp}_{REF_LABEL}_centro-{cy}.nc")
        out_npy = os.path.join(
            OUT_SIGNIF,
            f"{modelo}_{variable}_{agregacion}_{ssp}_{REF_LABEL}_centro-{cy}.npy")
        if not (os.path.exists(out_nc) and os.path.exists(out_npy)):
            archivos_existen = False
            break

    if archivos_existen:
        print(f"  -> Saltando: Todos los archivos para esta combinación ya existen")
        return
    print(f"\n=== Procesando: {modelo} | {variable} | {agregacion} | {ssp} ===")
    # Cargar datos
    da = cargar_combinacion(MOD_DIR, modelo, variable, agregacion, ssp)
    if da is None:
        return
    #
    # DIAGNÓSTICO: Imprimir información del dataset
    #print(f"  -> Dimensiones: {da.dims}")
    #print(f"  -> Forma: {da.shape}")
    #print(f"  -> Coordenadas: {list(da.coords)}")
    
    # Periodo histórico fijo
    da_hist = seleccionar_periodo(da, REF_START, REF_END)
    
    # Verificar que tenemos datos históricos
    if da_hist.time.size == 0:
        print(f"  -> Error: No hay datos históricos para el periodo {REF_START}-{REF_END}")
        return
    
    # Procesar cada año centro
    for cy in CENTER_YEARS:
        fut_start = cy - (FUT_WINDOW // 2) + 1
        fut_end   = fut_start + FUT_WINDOW - 1
        
        da_fut = seleccionar_periodo(da, fut_start, fut_end)
        
        # Verificar que tenemos datos futuros
        if da_fut.time.size == 0:
            print(f"  -> Advertencia: No hay datos futuros para {fut_start}-{fut_end}")
            continue
        
        # Delta (campo espacial)
        delta = calcular_delta(da_hist, da_fut, variable)
        
        # p-values (campo 2D)
        pvals = calcular_pvals(da_hist, da_fut)
        pvals = np.asarray(pvals)
        
        # ----------------------------------------------
        # Guardado del NetCDF
        # ----------------------------------------------
        delta_ds = xr.Dataset({
            f"delta_{variable}": delta.assign_coords(
                center_year = cy,
                reference   = REF_LABEL,
                agregacion  = agregacion,
                ssp         = ssp
            )
        })
        
        # Nombre incluye todas las dimensiones
        out_nc = os.path.join(
            OUT_CAMBIOS,
            f"{modelo}_{variable}_{agregacion}_{ssp}_{REF_LABEL}_centro-{cy}.nc"
        )
        
        if not os.path.exists(out_nc):
            print(f"  -> Guardando cambios: {os.path.basename(out_nc)}")
            try:
                delta_ds.to_netcdf(out_nc)
            except Exception as e:
                print(f"  -> Error guardando NetCDF: {e}")
        
        # ----------------------------------------------
        # Guardado de significancia
        # ----------------------------------------------
        out_npy = os.path.join(
            OUT_SIGNIF,
            f"{modelo}_{variable}_{agregacion}_{ssp}_{REF_LABEL}_centro-{cy}.npy"
        )
        
        if not os.path.exists(out_npy):
            print(f"  -> Guardando significancia: {os.path.basename(out_npy)}")
            try:
                np.save(out_npy, pvals, allow_pickle=True)
            except Exception as e:
                print(f"  -> Error guardando NPY: {e}")


def main():
    """
    Función principal que detecta y procesa todas las combinaciones.
    """
    # Verificar que existe la ruta de modelos
    if not os.path.exists(MOD_DIR):
        print(f"Error: No se encuentra la ruta {MOD_DIR}")
        print("Asegúrate de que la carpeta 'modelos_agre' existe en 'data/'")
        return
    
    # Obtener todos los archivos netCDF
    archivos_nc = [f for f in os.listdir(MOD_DIR) if f.endswith('.nc')]
    
    if not archivos_nc:
        print(f"Error: No se encontraron archivos .nc en {MOD_DIR}")
        return
    
    #print(f"Se encontraron {len(archivos_nc)} archivos en {MOD_DIR}")
    
    # Procesar cada archivo
    procesadas = set()  # Evitar duplicados
    
    for archivo in sorted(archivos_nc):
        dims = extraer_dimensiones_archivo(archivo)
        
        if dims is None:
            print(f"  -> Saltando archivo con formato no válido: {archivo}")
            continue
        
        # Crear clave única para evitar duplicados
        clave = (dims['modelo'], dims['variable'], dims['agregacion'], dims['ssp'])
        
        if clave not in procesadas:
            procesar_combinacion(*clave)
            procesadas.add(clave)
        else:
            print(f"  -> Combinación ya procesada: {clave}")
    
    print(f"\n¡Procesamiento completado! Total de combinaciones: {len(procesadas)}")


if __name__ == "__main__":
    main()
