import os
import geopandas as gpd
import xarray as xr
import pandas as pd
import numpy as np
import rioxarray
from shapely.geometry import mapping

# --- CONFIGURACIÓN ACTUALIZADA ---
BASE_DIR = "data"
MOD_DIR = os.path.join(BASE_DIR, "modelos_agre")  # Nueva ruta
OUT_DIR = os.path.join(BASE_DIR, "procesados")
GEO_FILE = os.path.join(BASE_DIR, "geo", "peru32.geojson")
os.makedirs(OUT_DIR, exist_ok=True)
resolucion = 0.5

# Cargar y asegurar CRS
gdf = gpd.read_file(GEO_FILE)
gdf1 = gdf.to_crs("EPSG:4326")

# Variables, agregaciones temporales y escenarios se detectarán automáticamente
# Extraeremos estas dimensiones de los nombres de archivo disponibles

# --- FUNCIONES AUXILIARES ---

def extraer_dimensiones_archivo(nombre_archivo):
    """
    Extrae variable, agregación, modelo y escenario del nombre del archivo.
    Formato: {variable}_{AGREGACION}_{modelo}_{ssp}.nc
    """
    # Remover extensión .nc
    base_name = nombre_archivo.replace('.nc', '')
    
    # Dividir por guiones bajos
    partes = base_name.split('_')
    
    if len(partes) >= 4:
        variable = partes[0]  # tasmin, tasmax, pr
        agregacion = partes[1]  # ANUAL, DEF, MAM, JJA, SON
        modelo = partes[2]  # ecmwf-51, ncep-2, etc.
        ssp = partes[3]  # ssp245, ssp585
        
        return {
            'variable': variable,
            'agregacion': agregacion,
            'modelo': modelo,
            'ssp': ssp,
            'nombre_completo': nombre_archivo
        }
    return None

def procesar_archivo_nc(nc_path, mod_name, var_name, reso=0.1):
    """
    Procesa un archivo netCDF individual.
    """
    if not os.path.exists(nc_path):
        print(f"  -> Advertencia: Archivo no encontrado en {nc_path}")
        return None
    
    print(f"  -> Modelo: {mod_name} | Variable: {var_name}")
    
    try:
        # Cargar netcdf
        ds = xr.open_dataset(nc_path)
        
        # Comprobar si la variable existe (ahora coincide con nombre del archivo)
        if var_name not in ds.data_vars:
            # Intentar con nombres alternativos
            var_names_alt = [var_name, var_name.upper(), 'tas', 'pr']
            var_encontrada = None
            for v in var_names_alt:
                if v in ds.data_vars:
                    var_encontrada = v
                    break
            
            if var_encontrada is None:
                print(f"  -> Error: Variable '{var_name}' no encontrada en dataset")
                return None
            var_name = var_encontrada
        
        # Interpolar
        ds_interp = ds.interp(lon=np.arange(-82, 1+reso, reso), 
                             lat=np.arange(-19, 1+reso, reso))
        
        # Seleccionar la DataArray
        da = ds_interp[var_name]
        
        # Configurar CRS para rioxarray
        da = da.rio.write_crs("EPSG:4326", inplace=False)
        da = da.rio.set_spatial_dims(x_dim="lon", y_dim="lat")
        
        return da
    except Exception as e:
        print(f"  -> Error al procesar {nc_path}: {e}")
        return None

def iter_depa(gdf, da):
    """
    Itera por departamentos y calcula media espacial.
    """
    df_list = []
    
    for _, row in gdf.iterrows():
        geom = mapping(row.geometry)
        recorte = da.rio.clip([geom])
        
        if recorte.size > 0:
            serie = recorte.mean(dim=["lat", "lon"]).to_series()
            serie.name = row["DEPARTAMEN"]
            df_list.append(serie)
        else:
            print(f"  -> Advertencia: Sin datos para {row['DEPARTAMEN']}")
    
    if not df_list:
        return None
    
    return pd.concat(df_list, axis=1)

# --- BUCLE PRINCIPAL ACTUALIZADO ---

print(f"Buscando archivos en: {MOD_DIR}")

# Obtener todos los archivos netCDF
archivos_nc = [f for f in os.listdir(MOD_DIR) if f.endswith('.nc')]

if not archivos_nc:
    print("No se encontraron archivos .nc en la ruta especificada")
    exit()

print(f"Se encontraron {len(archivos_nc)} archivos para procesar")

for archivo_nc in sorted(archivos_nc):
    # Extraer dimensiones del nombre del archivo
    dims = extraer_dimensiones_archivo(archivo_nc)
    
    if dims is None:
        print(f"  -> Saltando archivo con formato no válido: {archivo_nc}")
        continue
    
    # Desempaquetar dimensiones
    var = dims['variable']          # tasmin, tasmax, pr
    agregacion = dims['agregacion']  # ANUAL, DEF, MAM, etc.
    modelo = dims['modelo']         # ecmwf-51, ncep-2, etc.
    ssp = dims['ssp']               # ssp245, ssp585
    
    # Definir ruta de entrada
    nc_path = os.path.join(MOD_DIR, archivo_nc)
    
    # Definir nombre de salida (incluye todas las dimensiones)
    out_name = f"{modelo}_{var}_{agregacion}_{ssp}.csv"
    out_path = os.path.join(OUT_DIR, out_name)
    
    # Verificar si ya existe
    if os.path.exists(out_path):
        #print(f"  -> Saltando: {out_name} ya existe")
        continue
    
    print(f"\nProcesando: {modelo} | {var} | {agregacion} | {ssp}")
    
    try:
        # Procesar archivo
        d1 = procesar_archivo_nc(nc_path, modelo, var, reso=resolucion)
        
        if d1 is None:
            print(f"  -> Saltando {archivo_nc} debido a error en procesamiento")
            continue
        
        # Iterar por departamentos
        df_final = iter_depa(gdf1, d1)
        
        if df_final is not None:
            df_final.to_csv(out_path)
            print(f"  -> Guardado: {out_name}")
        else:
            print(f"  -> Advertencia: No se generaron datos para {out_name}")
            
    except Exception as e:
        print(f"  -> Error procesando {archivo_nc}: {e}")

print("\n¡Procesamiento completado!")
