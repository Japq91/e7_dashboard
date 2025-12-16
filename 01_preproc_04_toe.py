#!/usr/bin/env python
# coding: utf-8

"""
01_preproc_04_toe.py - Cálculo de Time of Emergence (TOE)
Versión simplificada.
"""
import os
import sys
from glob import glob

sys.path.append(os.path.join(os.path.dirname(__file__), "src"))
from aux_calcular_toe import calcular_toe_completo, guardar_toe

# ============================================================
# CONFIGURACIÓN
# ============================================================
BASE_DIR = "data"
MOD_DIR = os.path.join(BASE_DIR, "modelos_agre")
OUT_TOE = os.path.join(BASE_DIR, "mod_toe")
os.makedirs(OUT_TOE, exist_ok=True)
# ============================================================
# FUNCIONES PRINCIPALES
# ============================================================
def obtener_combinaciones():
    """Obtiene combinaciones únicas de (variable, agregacion)."""
    archivos = glob(os.path.join(MOD_DIR, "*.nc"))
    combinaciones = set()    
    for archivo in archivos:
        nombre = os.path.basename(archivo).replace('.nc', '')
        partes = nombre.split('_')
        if len(partes) >= 4:
            combinaciones.add((partes[0], partes[1]))    
    return sorted(list(combinaciones))

def procesar_variable(var, agg):
    """Procesa una variable para calcular TOE."""
    archivo_toe = os.path.join(OUT_TOE, f"ensemble_{var}_{agg}_toe.nc")
    
    if os.path.exists(archivo_toe):
        print(f"  Ya existe, saltando...")
        return True
    
    try:
        resultados = calcular_toe_completo(var, agg, MOD_DIR)        
        if resultados:
            ruta = guardar_toe(resultados, OUT_TOE, var, agg)
            print(f"  Guardado: {os.path.basename(ruta)}")
            return True
        else:
            print(f"  Error en cálculo")
            return False
            
    except Exception as e:
        print(f"  Error: {e}")
        return False

# ============================================================
# EJECUCIÓN
# ============================================================
if __name__ == "__main__":
    print("Calculando TOE para todas las variables...")
    
    combinaciones = obtener_combinaciones()
    print(f"Encontradas {len(combinaciones)} combinaciones")
    
    exitos = 0
    for i, (var, agg) in enumerate(combinaciones, 1):
        
        #if i>1: continue
        print(f"\n[{i}/{len(combinaciones)}] {var}_{agg}:")
        if procesar_variable(var, agg):
            exitos += 1
    
    print(f"\n✓ Proceso completado. Éxitos: {exitos}/{len(combinaciones)}")