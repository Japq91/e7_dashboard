# src/data_loader_cambios.py - Versión adaptada para nueva estructura

import os
import numpy as np
import xarray as xr

def cargar_cambios(lista_modelos, var, agregacion, ssp, base, cy):
    """
    Carga los campos delta del directorio mod_cambios/
    Nueva estructura: modelo_variable_agregacion_ssp_referencia_centro-XXX.nc
    """
    out = {}
    for mod in lista_modelos:
        ruta = f"data/mod_cambios/{mod}_{var}_{agregacion}_{ssp}_{base}_centro-{cy}.nc"
        if not os.path.exists(ruta):
            print(f"no existe {ruta}")
            continue
        try:
            ds = xr.open_dataset(ruta)
            # Buscar la variable delta (puede tener nombres diferentes)
            var_key = f"delta_{var}"
            if var_key in ds:
                out[mod] = ds[var_key]
            else:
                # Si no está, tomar la primera variable del dataset
                out[mod] = list(ds.data_vars.values())[0]
        except Exception as e:
            print(f"Error cargando {ruta}: {e}")
    return out

def cargar_significancia(lista_modelos, var, agregacion, ssp, base, cy):
    """
    Carga los archivos npy con p-values del directorio mod_significancia/
    Nueva estructura: modelo_variable_agregacion_ssp_referencia_centro-XXX.npy
    """
    out = {}
    for mod in lista_modelos:
        ruta = f"data/mod_significancia/{mod}_{var}_{agregacion}_{ssp}_{base}_centro-{cy}.npy"
        if not os.path.exists(ruta):
            print(f"no existe {ruta}")
            continue
        try:
            pvals = np.load(ruta, allow_pickle=True)
            out[mod] = pvals
        except Exception as e:
            print(f"Error cargando {ruta}: {e}")
    return out

def obtener_vmin_vmax(var):
    """
    Devuelve límites fijos según la variable.
    - temperatura: -4 a 6 (°C)
    - precipitación: -100 a 100 (%)
    """
    if var == "pr":
        return -100.0, 100.0
    else:  # tasmin, tasmax, tmin, tmax
        return -4.0, 6.0
