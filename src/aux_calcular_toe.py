#!/usr/bin/env python
# coding: utf-8

"""
aux_calcular_toe.py - Versión exacta de tu script original en funciones
"""

import xarray as xr
import numpy as np
import pandas as pd
from glob import glob
import os
import warnings

warnings.filterwarnings('ignore', message='Degrees of freedom <= 0 for slice')

def polinom(d, var):
    """Función polinom original exacta."""
    coef = d.polyfit(dim='time', deg=4, full=True)
    s_poli = xr.polyval(coord=d.time, coeffs=coef[f'{var}_polyfit_coefficients'])
    
    residuo0 = ((d[var] / s_poli) * 100) - 100
    prom_PR = s_poli.sel(time=slice('1981', '2010')).mean(dim='time')
    
    if 't' in var:
        delta0 = s_poli - ((s_poli / s_poli) * prom_PR)
    else:
        delta0 = ((s_poli / prom_PR) * 100) - 100
    
    return delta0, residuo0

def parte_1(var, agg, data_dir):
    """PARTE 1 exacta de tu script - CORREGIDO para usar datetime64."""
    experimentos = ['245', '585']
    j = 0
    k = 0
    
    for exp in experimentos:
        files = glob(os.path.join(data_dir, f"{var}_{agg}_*_ssp{exp}*.nc"))
        i = 0
        
        for file in files:
            ds = xr.open_dataset(file)
            delta, residuo = polinom(ds, var)
            
            if i == 0:
                delta2 = delta
            else:
                delta2 = xr.concat([delta, delta2], dim='time')
                
            if j == 0:
                delta3 = delta
                residuo4 = residuo
            else:
                delta3 = xr.concat([delta, delta3], dim='time')
                residuo4 = xr.concat([residuo, residuo4], dim='time')
            
            j += 1
            k += 1
            i += 1
        
        delta21 = delta2.sortby('time', ascending=True)
        
        # CORRECCIÓN: Convertir años a datetime64 después del groupby
        var_delta21 = delta21.groupby('time.year').var()
        prom_delta21 = delta21.groupby('time.year').mean()
        
        # Convertir coordenada 'year' (entero) a 'time' (datetime64)
        var_delta21 = var_delta21.rename({'year': 'time'})
        var_delta21['time'] = pd.to_datetime(var_delta21['time'].values, format='%Y')
        
        prom_delta21 = prom_delta21.rename({'year': 'time'})
        prom_delta21['time'] = pd.to_datetime(prom_delta21['time'].values, format='%Y')
        
        if '245' in exp:
            lst_var_mdl = var_delta21
            lst_prom_mdl = prom_delta21
        else:
            lst_var_mdl = xr.concat([lst_var_mdl, var_delta21], dim='time')
            lst_prom_mdl = xr.concat([lst_prom_mdl, prom_delta21], dim='time')
    #print('PARTE 1')
    return lst_var_mdl, lst_prom_mdl, delta3, residuo4, k


def parte_2(lst_var_mdl, lst_prom_mdl, delta3, residuo4):
    """PARTE 2 exacta de tu script - CORREGIDO para usar datetime64."""
    var_mdl_2 = lst_var_mdl.sortby('time', ascending=True)
    prom_mdl_2 = lst_prom_mdl.sortby('time', ascending=True)
    delta31 = delta3.sortby('time', ascending=True)
    residuo41 = residuo4.sortby('time', ascending=True)
    
    # CORRECCIÓN: Convertir años a datetime64 después del groupby
    G0 = delta31.groupby('time.year').mean().rename({'year': 'time'})
    G0['time'] = pd.date_range('1981-01-01', periods=len(G0.time), freq='YS')
    
    SU0 = prom_mdl_2.groupby('time.year').var().rename({'year': 'time'})
    SU0['time'] = pd.date_range('1981-01-01', periods=len(SU0.time), freq='YS')
    
    MU0 = var_mdl_2.groupby('time.year').mean().rename({'year': 'time'})
    MU0['time'] = pd.date_range('1981-01-01', periods=len(MU0.time), freq='YS')
    print('  Parte 2: Gaea')
    return G0, SU0, MU0, residuo41

def parte_3(residuo41, k):
    """PARTE 3 exacta de tu script - YA CORREGIDO."""
    # Extraer años correctamente
    if hasattr(residuo41.time, 'dt'):
        years = residuo41.time.dt.year.values
    else:
        time_values = residuo41['time'].values
        years = np.array([pd.to_datetime(str(t)).year for t in time_values])
    
    year_c = 2010
    l = 0
    
    for ktime in range(len(years) // k - 30):
        y_i = years[ktime * k]
        yi = str(y_i)
        y_f = y_i + 29
        yf = str(y_f)
        
        residuo42 = residuo41.sel(time=slice(yi, yf))
        
        residuo43_std = residuo42.std(dim='time')
        
        year_c += 1
        
        time_d = pd.date_range(f'{year_c}-01-01', periods=1, freq='YS')
        time_ds = xr.DataArray(time_d, [('time', time_d)])
        
        residuo44_std = residuo43_std.expand_dims(time=time_ds)
        
        if l == 0:
            residuo_45_std = residuo44_std
        else:
            residuo_45_std = xr.concat([residuo44_std, residuo_45_std], dim='time')
        
        l += 1
    #print('PARTE 3')
    return residuo_45_std, None  # Solo necesitamos std, no var

def parte_4(residuo_45_std, G0, SU0, MU0):
    """PARTE 4 exacta de tu script."""
    VI0 = residuo_45_std.sortby('time', ascending=True)
    VI0['time'] = pd.date_range('2011', freq='12M', periods=len(VI0.time))    
    VI1 = VI0.rolling(time=10, center=False).mean()
    
    VI = VI1.sel(time=slice('2020', '2065'))
    #print(VI)
    G = G0.sel(time=slice('2020', '2065'))
    #print(G)
    SU = SU0.sel(time=slice('2020', '2065'))
    #print(SU)
    MU = MU0.sel(time=slice('2020', '2065'))    
    #print(MU)
    return VI, G, SU, MU

def parte_5(VI, G, SU, MU, var, agg):
    """PARTE 5 exacta de tu script con umbrales."""
    # Calcular TOE crudo
    TU = VI + MU.values + SU.values
    
    STN = G / (TU.values ** 0.5)
    TOE = G / (VI.values ** 0.5)
    #print(TOE)
    # Calcular t_TOE - EXACTO como tu script
    t_TOE = TOE * np.nan
    tpr = 2020
    
    # CORRECCIÓN: Extraer años de TOE correctamente
    if hasattr(TOE.time, 'dt'):
        toe_years = TOE.time.dt.year.values
    else:
        toe_years = np.array([pd.to_datetime(str(t)).year for t in TOE['time'].values])
    
    for tpru in range(len(TOE.time)):
        # Crear DataArray de años para comparación
        years_array = xr.DataArray(toe_years, dims=['time'], coords={'time': TOE.time})
        
        # EXACTA lógica de tu script
        t_TOE = t_TOE.where(~((TOE < tpr) & (years_array == tpr)), tpr)
        tpr += 1
    
    # Aplicar umbrales según variable - EXACTO como tu código adicional
    if var == 'pr':
        for umbr in [-1, 1]:
            TOE_umbr = TOE[0] * 0
            for t in range(len(TOE.time)):
                if umbr == -1:
                    TOE_umbr = TOE_umbr.where(~((TOE[t] < umbr) & (TOE_umbr <= 0)), t_TOE[t])
                    TOE_umbralnegativo_pr = TOE_umbr
                else:
                    TOE_umbr = TOE_umbr.where(~((TOE[t] > umbr) & (TOE_umbr <= 0)), t_TOE[t])
                    TOE_umbralpositivo_pr = TOE_umbr
        
        TOE_1 = TOE_umbralnegativo_pr.where(~(TOE_umbralnegativo_pr == 0), np.nan)
        TOE_2 = TOE_umbralpositivo_pr.where(~(TOE_umbralpositivo_pr == 0), np.nan)
        
    else:
        for umbr in [1, 2]:
            TOE_umbr = TOE[0] * 0
            for t in range(len(TOE.time)):
                TOE_umbr = TOE_umbr.where(~((TOE[t] > umbr) & (TOE_umbr <= 0)), t_TOE[t])
                if umbr == 1:
                    TOE_u1_tas = TOE_umbr
                else:
                    TOE_u2_tas = TOE_umbr
        
        TOE_1 = TOE_u1_tas.where(~(TOE_u1_tas == 0), np.nan)
        TOE_2 = TOE_u2_tas.where(~(TOE_u2_tas == 0), np.nan)
    #print('PARTE 5')
    return {
        'TOE_1': TOE_1,
        'TOE_2': TOE_2,
        'VI': VI.mean(dim='time'),
        'SU': SU.mean(dim='time'),
        'MU': MU.mean(dim='time'),
        'G': G.mean(dim='time'),
        'STN': STN.mean(dim='time'),
        'TOE_raw': TOE
    }

def calcular_toe_completo(var, agg, data_dir="data/modelos_agre"):
    """Calcula TOE completo llamando a cada parte."""
    print(f"Calculando TOE para {var}_{agg}")
    
    try:
        # Parte 1
        lst_var_mdl, lst_prom_mdl, delta3, residuo4, k = parte_1(var, agg, data_dir)
        print(f"  Parte 1: k={k}")
        
        # Parte 2
        G0, SU0, MU0, residuo41 = parte_2(lst_var_mdl, lst_prom_mdl, delta3, residuo4)
        
        # Parte 3
        residuo_45_std, _ = parte_3(residuo41, k)
        print(f"  Parte 3: ventanas calculadas")
        
        # Parte 4
        VI, G, SU, MU = parte_4(residuo_45_std, G0, SU0, MU0)
        print(f"  Parte 4: datos preparados")
        
        # Parte 5
        resultados = parte_5(VI, G, SU, MU, var, agg)
        print(f"  Parte 5: TOE calculado")
        
        return resultados
        
    except Exception as e:
        print(f"Error: {e}")
        return None

def guardar_toe(resultados, output_dir, var, agg):
    """Guarda resultados TOE."""
    os.makedirs(output_dir, exist_ok=True)
    
    # Guardar TOE principal
    ruta_toe = os.path.join(output_dir, f"ensemble_{var}_{agg}_toe.nc")
    ds_toe = xr.Dataset({
        'TOE_1': resultados['TOE_1'],
        'TOE_2': resultados['TOE_2']
    })
    ds_toe.attrs['variable'] = var
    ds_toe.attrs['aggregation'] = agg
    ds_toe.to_netcdf(ruta_toe)
    
    # Guardar componentes
    ruta_comp = os.path.join(output_dir, f"ensemble_{var}_{agg}_components.nc")
    ds_comp = xr.Dataset({
        'VI': resultados['VI'],
        'SU': resultados['SU'],
        'MU': resultados['MU'],
        'G': resultados['G'],
        'STN': resultados['STN']
    })
    ds_comp.attrs['variable'] = var
    ds_comp.attrs['aggregation'] = agg
    ds_comp.to_netcdf(ruta_comp)
    
    return ruta_toe