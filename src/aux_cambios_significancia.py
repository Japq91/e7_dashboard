"""
Módulo auxiliar para cálculo de cambios y significancia.
Contiene funciones básicas para procesamiento.
"""

import xarray as xr
import numpy as np
from scipy import stats

def seleccionar_periodo(da, start_year, end_year):
    """
    Selecciona datos dentro de un rango de años.
    """
    # Encontrar la dimensión temporal
    time_dims = ['time', 't', 'year', 'years']
    time_dim = None
    
    for dim in time_dims:
        if dim in da.dims:
            time_dim = dim
            break
    
    if time_dim is None:
        print("  -> Advertencia: No se encontró dimensión temporal")
        return da
    
    # Filtrar por años
    try:
        # Asumir que las fechas están en formato datetime
        return da.sel({time_dim: slice(f'{start_year}-01-01', f'{end_year}-12-31')})
    except:
        # Si no funciona con fechas, intentar con años directamente
        try:
            years = da[time_dim].values
            if hasattr(years[0], 'year'):
                # Si son objetos datetime, extraer el año
                mask = np.array([y.year >= start_year and y.year <= end_year for y in years])
                return da.isel({time_dim: mask})
            else:
                # Si son números enteros (años)
                mask = (years >= start_year) & (years <= end_year)
                return da.isel({time_dim: mask})
        except Exception as e:
            print(f"  -> Error seleccionando periodo: {e}")
            return da


def calcular_delta(da_hist, da_fut, variable):
    """
    Calcula diferencia entre futuro e histórico.
    Versión robusta con manejo de errores.
    """
    try:
        # Encontrar dimensión temporal
        time_dims = ['time', 't', 'year', 'years']
        time_dim = None
        
        for dim in time_dims:
            if dim in da_hist.dims:
                time_dim = dim
                break
        
        if time_dim is None:
            print("  -> Error: No se encontró dimensión temporal en datos históricos")
            return None
        
        # Promedio sobre dimensión temporal
        hist_mean = da_hist.mean(dim=time_dim, skipna=True)
        fut_mean = da_fut.mean(dim=time_dim, skipna=True)
        
        # Verificar que las dimensiones coinciden
        if hist_mean.shape != fut_mean.shape:
            print(f"  -> Advertencia: Formas no coinciden. "
                  f"Hist: {hist_mean.shape}, Fut: {fut_mean.shape}")
            # Intentar reindexar si es posible
            try:
                fut_mean = fut_mean.reindex_like(hist_mean)
            except:
                pass
        
        # Calcular cambio según variable
        variable_lower = variable.lower()
        
        if 'pr' in variable_lower or 'precip' in variable_lower:
            # Cambio porcentual para precipitación
            # Evitar división por cero usando where
            hist_mean_pos = hist_mean.where(hist_mean > 0, np.nan)
            delta = ((fut_mean - hist_mean) / hist_mean_pos) * 100
            delta = delta.where(~np.isinf(delta), np.nan)  # Remover infinitos
            delta.attrs['units'] = '%'
            delta.attrs['description'] = 'Cambio porcentual en precipitación'
        else:
            # Cambio absoluto para temperatura
            delta = fut_mean - hist_mean
            delta.attrs['units'] = '°C'
            delta.attrs['description'] = 'Cambio absoluto en temperatura'
        
        # Copiar coordenadas si existen
        if hasattr(hist_mean, 'coords'):
            for coord in ['lat', 'lon', 'latitude', 'longitude']:
                if coord in hist_mean.coords:
                    delta.coords[coord] = hist_mean.coords[coord]
        
        return delta
        
    except Exception as e:
        print(f"  -> Error calculando delta para {variable}: {e}")
        import traceback
        traceback.print_exc()
        return None

def calcular_pvals(da_hist, da_fut):
    """
    Calcula valores p usando prueba t de Student para cada punto de la grilla.
    Devuelve array 2D con dimensiones espaciales (lat, lon).
    """
    import numpy as np
    from scipy import stats

    try:
        # Obtener dimensiones espaciales
        if 'lat' in da_hist.dims and 'lon' in da_hist.dims:
            n_lat = da_hist.sizes['lat']
            n_lon = da_hist.sizes['lon']
        else:
            # Si no tiene lat/lon, usar las primeras dos dimensiones
            n_lat, n_lon = da_hist.shape[0], da_hist.shape[1]

        print(f"  -> Dimensiones espaciales: lat={n_lat}, lon={n_lon}")
        print(f"  -> Datos históricos shape: {da_hist.shape}")
        print(f"  -> Datos futuros shape: {da_fut.shape}")

        # Inicializar array de p-values con dimensiones espaciales correctas
        pvals = np.full((n_lat, n_lon), np.nan)

        # Para cada punto de la grilla
        for i in range(n_lat):
            for j in range(n_lon):
                try:
                    # Extraer series temporales para este punto
                    hist_series = da_hist.isel(lat=i, lon=j).values
                    fut_series = da_fut.isel(lat=i, lon=j).values

                    # Remover NaN
                    hist_series = hist_series[~np.isnan(hist_series)]
                    fut_series = fut_series[~np.isnan(fut_series)]

                    # Verificar que tenemos suficientes datos
                    if len(hist_series) > 1 and len(fut_series) > 1:
                        # Prueba t de Student para dos muestras independientes
                        t_stat, p_val = stats.ttest_ind(
                            hist_series,
                            fut_series,
                            equal_var=False,
                            nan_policy='omit'
                        )
                        pvals[i, j] = p_val
                    else:
                        pvals[i, j] = np.nan

                except Exception as e:
                    pvals[i, j] = np.nan
                    continue

        print(f"  -> p-values shape final: {pvals.shape}")
        print(f"  -> p-values min/max: {np.nanmin(pvals):.4f}/{np.nanmax(pvals):.4f}")
        print(f"  -> Puntos significativos (p<0.05): {np.sum(pvals < 0.05)}")

        return pvals

    except Exception as e:
        print(f"  -> Error calculando p-values: {e}")
        import traceback
        traceback.print_exc()
        # Devolver array con dimensiones por defecto
        return np.full((15, 21), np.nan)
