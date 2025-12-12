#!/usr/bin/env python
# coding: utf-8
"""
aux_ens_cdo.py - Funciones para cálculo de ensambles usando CDO
"""

import os
import subprocess
import glob

def calcular_ensemble_cdo(base_dir, variable, agregacion, ssp, output_dir):
    """
    Calcula ensemble usando CDO ensmean.
    
    Args:
        base_dir: Directorio con archivos de modelos
        variable: Variable climática
        agregacion: Agregación temporal
        ssp: Escenario
        output_dir: Directorio de salida
    
    Returns:
        Ruta al archivo de ensemble creado
    """
    # Crear patrón de búsqueda
    patron = f"{variable}_{agregacion}_*_{ssp}.nc"
    ruta_patron = os.path.join(base_dir, patron)
    
    # Buscar archivos
    archivos = sorted(glob.glob(ruta_patron))
    
    if not archivos:
        print(f"  -> No se encontraron archivos para: {variable}_{agregacion}_{ssp}")
        return None
    
    print(f"  -> Encontrados {len(archivos)} modelos:")
    for archivo in archivos:
        nombre = os.path.basename(archivo)
        modelo = nombre.split('_')[2]
        print(f"     ✓ {modelo}")
    
    # Crear directorio de salida
    os.makedirs(output_dir, exist_ok=True)
    
    # Nombre de archivo de salida
    nombre_salida = f"ensemble_{variable}_{agregacion}_{ssp}.nc"
    ruta_salida = os.path.join(output_dir, nombre_salida)
    
    # Construir comando CDO
    archivos_str = " ".join(archivos)
    comando = f"cdo ensmean {archivos_str} {ruta_salida}"
    
    print(f"  -> Ejecutando: cdo ensmean sobre {len(archivos)} modelos")
    print(f"  -> Salida: {nombre_salida}")
    
    try:
        # Ejecutar CDO
        resultado = subprocess.run(
            comando, 
            shell=True, 
            capture_output=True, 
            text=True,
            check=True
        )
        
        if resultado.returncode == 0:
            print(f"  ✓ Ensemble creado exitosamente")
            # Verificar que el archivo se creó
            if os.path.exists(ruta_salida):
                tamaño = os.path.getsize(ruta_salida) / (1024*1024)  # MB
                print(f"  ✓ Tamaño: {tamaño:.1f} MB")
                return ruta_salida
            else:
                print(f"  ✗ Error: Archivo no creado")
                return None
        else:
            print(f"  ✗ Error CDO: {resultado.stderr}")
            return None
            
    except subprocess.CalledProcessError as e:
        print(f"  ✗ Error ejecutando CDO: {e}")
        return None
    except Exception as e:
        print(f"  ✗ Error inesperado: {e}")
        return None


def verificar_ensemble_existente(output_dir, variable, agregacion, ssp):
    """
    Verifica si ya existe un ensemble.
    """
    nombre_archivo = f"ensemble_{variable}_{agregacion}_{ssp}.nc"
    ruta_completa = os.path.join(output_dir, nombre_archivo)
    
    return os.path.exists(ruta_completa)
