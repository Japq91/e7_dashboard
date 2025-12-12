#!/usr/bin/env python
# coding: utf-8
"""
01_preproc_03_ens_cdo.py - Cálculo de ensambles usando CDO (versión simplificada)
Modificado para saltar archivos existentes
"""

import os
import sys
import numpy as np
import xarray as xr

# Añadir src al path
sys.path.append(os.path.join(os.path.dirname(__file__), "src"))

# Importar funciones de CDO
from aux_ens_cdo import calcular_ensemble_cdo, verificar_ensemble_existente
# Importar funciones de cálculos (las mismas que para modelos individuales)
from aux_cambios_significancia import (
    seleccionar_periodo,
    calcular_delta,
    calcular_pvals
)

# ============================================================
# CONFIGURACIÓN
# ============================================================

BASE_DIR = "data"
MOD_DIR = os.path.join(BASE_DIR, "modelos_agre")
OUT_ENS_BRUTO = os.path.join(BASE_DIR, "ensamble", "datos")
OUT_ENS_CAMBIOS = os.path.join(BASE_DIR, "ensamble", "cambios")
OUT_ENS_SIGNIF = os.path.join(BASE_DIR, "ensamble", "significancia")

# Crear directorios
os.makedirs(OUT_ENS_BRUTO, exist_ok=True)
os.makedirs(OUT_ENS_CAMBIOS, exist_ok=True)
os.makedirs(OUT_ENS_SIGNIF, exist_ok=True)

# Periodos base
REF_PERIODS = {"1981-2010": (1981, 2010), "1991-2020": (1991, 2020)}
REF_LABEL = "1991-2020" #"1981-2010"
REF_START, REF_END = REF_PERIODS[REF_LABEL]

# Años centro
CENTER_YEARS = [2030, 2035, 2040, 2045, 2050]
FUT_WINDOW = 30

# ============================================================
# FUNCIONES PRINCIPALES
# ============================================================

def obtener_combinaciones_unicas():
    """Obtiene combinaciones únicas de archivos."""
    combinaciones = set()
    
    for archivo in os.listdir(MOD_DIR):
        if archivo.endswith('.nc'):
            partes = archivo.replace('.nc', '').split('_')
            if len(partes) >= 4:
                combinaciones.add((partes[0], partes[1], partes[3]))
    
    return sorted(combinaciones)


def verificar_cambios_existentes(variable, agregacion, ssp, cy):
    """Verifica si ya existen archivos de cambios y significancia."""
    out_nc = os.path.join(
        OUT_ENS_CAMBIOS,
        f"ensemble_{variable}_{agregacion}_{ssp}_{REF_LABEL}_centro-{cy}.nc"
    )
    
    out_npy = os.path.join(
        OUT_ENS_SIGNIF,
        f"ensemble_{variable}_{agregacion}_{ssp}_{REF_LABEL}_centro-{cy}.npy"
    )
    
    return os.path.exists(out_nc) and os.path.exists(out_npy)


def procesar_cambios_ensemble(ruta_ensemble, variable, agregacion, ssp):
    """Calcula cambios y significancia para el ensemble."""
    
    # Cargar ensemble
    ds = xr.open_dataset(ruta_ensemble)
    da = ds[variable]
    
    # Periodo histórico
    da_hist = seleccionar_periodo(da, REF_START, REF_END)
    
    if da_hist.time.size == 0:
        print(f"  -> Error: No hay datos históricos")
        return
    
    archivos_procesados = 0
    archivos_saltados = 0
    
    # Procesar cada año centro
    for cy in CENTER_YEARS:
        # Verificar si ya existen los archivos
        if verificar_cambios_existentes(variable, agregacion, ssp, cy):
            print(f"  -> Saltando centro-{cy} (archivos ya existen)")
            archivos_saltados += 1
            continue
        
        fut_start = cy - (FUT_WINDOW // 2) + 1
        fut_end = fut_start + FUT_WINDOW - 1
        
        da_fut = seleccionar_periodo(da, fut_start, fut_end)
        
        if da_fut.time.size == 0:
            print(f"  -> Advertencia: No hay datos para centro-{cy}")
            continue
        
        # Calcular cambios
        delta = calcular_delta(da_hist, da_fut, variable)
        pvals = np.asarray(calcular_pvals(da_hist, da_fut))
        
        # Guardar cambios
        delta_ds = xr.Dataset({
            f"delta_{variable}": delta.assign_coords(
                center_year=cy, reference=REF_LABEL,
                agregacion=agregacion, ssp=ssp
            )
        })
        
        out_nc = os.path.join(
            OUT_ENS_CAMBIOS,
            f"ensemble_{variable}_{agregacion}_{ssp}_{REF_LABEL}_centro-{cy}.nc"
        )
        
        print(f"  -> Guardando cambios: centro-{cy}")
        delta_ds.to_netcdf(out_nc)
        
        # Guardar significancia
        out_npy = os.path.join(
            OUT_ENS_SIGNIF,
            f"ensemble_{variable}_{agregacion}_{ssp}_{REF_LABEL}_centro-{cy}.npy"
        )
        
        np.save(out_npy, pvals, allow_pickle=True)
        archivos_procesados += 1
    
    # Resumen
    if archivos_procesados > 0 or archivos_saltados > 0:
        print(f"  -> Resumen: {archivos_procesados} procesados, {archivos_saltados} saltados")


def procesar_combinacion(variable, agregacion, ssp):
    """Procesa una combinación completa."""
    print(f"\n=== ENSEMBLE: {variable} | {agregacion} | {ssp} ===")
    
    # 1. Verificar si ensemble ya existe
    if verificar_ensemble_existente(OUT_ENS_BRUTO, variable, agregacion, ssp):
        print(f"  -> Ensemble bruto ya existe, usando existente...")
        ruta_ensemble = os.path.join(
            OUT_ENS_BRUTO, 
            f"ensemble_{variable}_{agregacion}_{ssp}.nc"
        )
    else:
        # 2. Calcular ensemble con CDO
        print(f"  -> Calculando ensemble con CDO...")
        ruta_ensemble = calcular_ensemble_cdo(
            MOD_DIR, variable, agregacion, ssp, OUT_ENS_BRUTO
        )
    
    if not ruta_ensemble:
        print(f"  -> Error: No se pudo obtener/crear el ensemble")
        return
    
    # 3. Calcular cambios y significancia (solo si no existen)
    procesar_cambios_ensemble(ruta_ensemble, variable, agregacion, ssp)


# ============================================================
# EJECUCIÓN PRINCIPAL
# ============================================================

def main():
    print("=" * 60)
    print("ENSEMBLES CON CDO - VERSIÓN SIMPLIFICADA")
    print("(Saltando archivos existentes)")
    print("=" * 60)
    
    if not os.path.exists(MOD_DIR):
        print(f"Error: No existe {MOD_DIR}")
        return
    
    # Verificar que CDO está instalado
    try:
        import subprocess
        subprocess.run(["cdo", "--version"], capture_output=True, check=True)
        print("✓ CDO encontrado y funcionando")
    except:
        print("✗ ERROR: CDO no está instalado o no está en PATH")
        print("  Instala con: conda install -c conda-forge cdo")
        return
    
    # Obtener combinaciones
    combinaciones = obtener_combinaciones_unicas()
    
    if not combinaciones:
        print("No se encontraron archivos .nc")
        return
    
    print(f"\nSe encontraron {len(combinaciones)} combinaciones")
    
    # Procesar cada combinación
    total_combinaciones = len(combinaciones)
    for idx, (variable, agregacion, ssp) in enumerate(combinaciones, 1):
        print(f"\n[{idx}/{total_combinaciones}]", end=" ")
        procesar_combinacion(variable, agregacion, ssp)
    
    print(f"\n" + "=" * 60)
    print("PROCESAMIENTO COMPLETADO")
    print("=" * 60)


if __name__ == "__main__":
    main()