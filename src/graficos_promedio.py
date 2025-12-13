#!/usr/bin/env python
# coding: utf-8

"""
graficos_promedio.py - Genera gráficos de promedio (3 mapas) con barras de color horizontales
y significancia como puntos scatter.
"""

import plotly.graph_objects as go
from plotly.subplots import make_subplots
import numpy as np
import geopandas as gpd
import xarray as xr

from data_loader_promedio import (
    cargar_cambios_ensemble,
    cargar_significancia_ensemble,
    cargar_toe,
    obtener_info_ensemble
)

def agregar_contorno_peru(fig, row, col):
    """
    Agrega el contorno de Perú desde un archivo GeoJSON.
    """
    try:
        peru_gdf = gpd.read_file("data/geo/peru32.geojson")
        
        for geometry in peru_gdf.geometry:
            if geometry.geom_type == 'Polygon':
                x, y = geometry.exterior.xy
                fig.add_trace(
                    go.Scatter(
                        x=list(x),
                        y=list(y),
                        mode='lines',
                        line=dict(color='black', width=1.5),
                        showlegend=False,
                        hoverinfo='skip'
                    ),
                    row=row, col=col
                )
            elif geometry.geom_type == 'MultiPolygon':
                for polygon in geometry:
                    x, y = polygon.exterior.xy
                    fig.add_trace(
                        go.Scatter(
                            x=list(x),
                            y=list(y),
                            mode='lines',
                            line=dict(color='black', width=1.5),
                            showlegend=False,
                            hoverinfo='skip'
                        ),
                        row=row, col=col
                    )
    except Exception as e:
        print(f"  -> Error cargando GeoJSON: {e}")

def agregar_puntos_significancia(fig, pvals_data, cambios_data, row, col, umbral=0.05):
    """
    Agrega puntos de significancia (p < umbral) como scatter.
    
    Args:
        fig: Figura de Plotly
        pvals_data: DataArray con valores p
        cambios_data: DataArray con cambios (para coordenadas)
        row: Fila del subplot
        col: Columna del subplot
        umbral: Umbral de significancia (default: 0.05)
    """
    if pvals_data is None or cambios_data is None:
        return
    
    try:
        # Obtener coordenadas
        lon = cambios_data.lon.values
        lat = cambios_data.lat.values
        
        # Crear máscara para p < umbral
        mask_significativo = pvals_data < umbral
        
        # Obtener índices de puntos significativos
        idx_significativos = np.where(mask_significativo)
        
        if len(idx_significativos[0]) > 0:
            # Obtener coordenadas de puntos significativos
            lon_significativos = lon[idx_significativos[1]]
            lat_significativos = lat[idx_significativos[0]]
            
            # Agregar scatter plot con puntos negros pequeños
            scatter = go.Scatter(
                x=lon_significativos,
                y=lat_significativos,
                mode='markers',
                marker=dict(
                    color='black',
                    size=5,
                    symbol='circle',
                    opacity=0.7
                ),
                name='Significancia: [ p < 0.05 ]',
                showlegend=(row == 1 and col == 1),  # Mostrar leyenda solo en el primer mapa
                hoverinfo='skip'
            )
            
            fig.add_trace(scatter, row=row, col=col)
            
    except Exception as e:
        print(f"  -> Error agregando puntos de significancia: {e}")

def generar_mapa_promedio(variable, agregacion, periodo_base, centro_year="2050"):
    """
    Genera un gráfico con 3 mapas: SSP245, SSP585 y TOE.
    
    Args:
        variable: Variable climática
        agregacion: Agregación temporal
        periodo_base: Periodo base
        centro_year: Año centro para cambios
    
    Returns:
        Plotly Figure con 3 subplots
    """
    # Cargar datos
    cambios_245 = cargar_cambios_ensemble(variable, agregacion, "ssp245", periodo_base, centro_year)
    cambios_585 = cargar_cambios_ensemble(variable, agregacion, "ssp585", periodo_base, centro_year)
    toe_data = cargar_toe(variable, agregacion)
    
    # Cargar significancia
    pvals_245 = cargar_significancia_ensemble(variable, agregacion, "ssp245", periodo_base, centro_year)
    pvals_585 = cargar_significancia_ensemble(variable, agregacion, "ssp585", periodo_base, centro_year)
    
    # Configuración de colores
    config = obtener_info_ensemble(variable)
    
    # Determinar rangos para las barras de color
    # Para los mapas de cambios (SSP245 y SSP585) - misma escala
    cambios_values = []
    if cambios_245 is not None:
        cambios_values.append(cambios_245.values.flatten())
    if cambios_585 is not None:
        cambios_values.append(cambios_585.values.flatten())
    
    if cambios_values:
        all_cambios = np.concatenate(cambios_values)
        all_cambios = all_cambios[~np.isnan(all_cambios)]
        if len(all_cambios) > 0:
            # Usar percentiles 2.5 y 97.5 para evitar outliers
            zmin_cambios = np.percentile(all_cambios, 2.5)
            zmax_cambios = np.percentile(all_cambios, 97.5)
            
            # Asegurar que 0 esté centrado para variables de temperatura
            if variable in ['tasmin', 'tasmax', 'tas']:
                max_abs = max(abs(zmin_cambios), abs(zmax_cambios))
                zmin_cambios = -max_abs
                zmax_cambios = max_abs
        else:
            zmin_cambios, zmax_cambios = -1, 1
    else:
        zmin_cambios, zmax_cambios = -1, 1
     
    # Para el TOE - escala independiente    
    zmin_toe, zmax_toe = 2020, 2065
   
    # Crear figura con 3 columnas - SOLO 1 FILA
    fig = make_subplots(
        rows=1,  # SOLO 1 FILA
        cols=3,
        subplot_titles=[
            f"SSP245 ({centro_year})",
            f"SSP585 ({centro_year})", 
            "TOE (Time of Emergence)"
        ],
        horizontal_spacing=0.03,
        vertical_spacing=0.05,
        column_widths=[0.33, 0.33, 0.34],
        specs=[[{'type': 'heatmap'}, {'type': 'heatmap'}, {'type': 'heatmap'}]]
    )
    
    # 1. MAPA SSP245
    if cambios_245 is not None:
        lon = cambios_245.lon.values
        lat = cambios_245.lat.values
        valores = cambios_245.values
        
        # Crear heatmap
        heatmap_245 = go.Heatmap(
            x=lon,
            y=lat,
            z=valores,
            colorscale=config['cmap'],
            zmin=zmin_cambios,
            zmax=zmax_cambios,
            colorbar=dict(
                title=f"Cambio ({config['units']})",
                len=0.4,  # Más corta
                y=-0.22,     # Más abajo, dentro del mismo subplot
                yanchor="bottom",
                x=0.2,    # Posicionada debajo del primer mapa
                xanchor="center",
                orientation="h",
                thickness=10,
                title_font=dict(size=14)
            ),
            hovertemplate=(
                f"Lon: %{{x:.2f}}°<br>"
                f"Lat: %{{y:.2f}}°<br>"
                f"Cambio: %{{z:.2f}}{config['units']}<br>"
                "<extra>SSP245</extra>"
            ),
            showscale=True
        )
        
        fig.add_trace(heatmap_245, row=1, col=1)
        
        # Agregar puntos de significancia
        agregar_puntos_significancia(fig, pvals_245, cambios_245, 1, 1)
        
        # Agregar contorno de Perú
        agregar_contorno_peru(fig, 1, 1)
    
    else:
        fig.add_annotation(
            row=1, col=1,
            text="Datos no disponibles",
            showarrow=False,
            font=dict(size=18, color="red")
        )
    
    # 2. MAPA SSP585
    if cambios_585 is not None:
        lon = cambios_585.lon.values
        lat = cambios_585.lat.values
        valores = cambios_585.values
        
        # Crear heatmap con barra de color compartida
        heatmap_585 = go.Heatmap(
            x=lon,
            y=lat,
            z=valores,
            colorscale=config['cmap'],
            zmin=zmin_cambios,
            zmax=zmax_cambios,
            showscale=False,  # No mostrar barra, usar la compartida
            hovertemplate=(
                f"Lon: %{{x:.2f}}°<br>"
                f"Lat: %{{y:.2f}}°<br>"
                f"Cambio: %{{z:.2f}}{config['units']}<br>"
                "<extra>SSP585</extra>"
            )
        )
        
        fig.add_trace(heatmap_585, row=1, col=2)
        
        # Agregar puntos de significancia
        agregar_puntos_significancia(fig, pvals_585, cambios_585, 1, 2)
        
        # Agregar contorno de Perú
        agregar_contorno_peru(fig, 1, 2)
    
    else:
        fig.add_annotation(
            row=1, col=2,
            text="Datos no disponibles",
            showarrow=False,
            font=dict(size=18, color="red")
        )
    
    # 3. MAPA TOE
    if toe_data is not None:
        lon = toe_data.lon.values
        lat = toe_data.lat.values
        valores = toe_data.values
        
        # Crear heatmap con barra de color independiente
        heatmap_toe = go.Heatmap(
            x=lon,
            y=lat,
            z=valores,
            colorscale="Viridis",
            zmin=zmin_toe,
            zmax=zmax_toe,
            colorbar=dict(
                title="Año",
                len=0.4,  # Mismo tamaño que la otra
                y=-0.22,     # Misma posición vertical
                yanchor="bottom",
                x=0.8,    # Posicionada debajo del tercer mapa
                xanchor="center",
                orientation="h",
                thickness=10,
                title_font=dict(size=14)
            ),
            hovertemplate=(
                f"Lon: %{{x:.2f}}°<br>"
                f"Lat: %{{y:.2f}}°<br>"
                f"TOE: %{{z:.0f}}<br>"
                "<extra>Time of Emergence</extra>"
            ),
            showscale=True
        )
        
        fig.add_trace(heatmap_toe, row=1, col=3)
        
        # Agregar contorno de Perú
        agregar_contorno_peru(fig, 1, 3)
    
    else:
        fig.add_annotation(
            row=1, col=3,
            text="TOE no disponible",
            showarrow=False,
            font=dict(size=16, color="gray")
        )
    
    # Configurar layout
    fig.update_layout(
        height=550,  # Altura adecuada para 1 fila
        showlegend=True,
        legend=dict(
            yanchor="top",
            y=-0.23,
            xanchor="left",
            x=-0.05,
            bgcolor="white",
            bordercolor="black",
            borderwidth=.8,
            font=dict(size=12)
        ),
        title_text=f"{config['label']} - {agregacion} (Base: {periodo_base}, Año centro: {centro_year})",
        title_font_size=19,
        title_x=0.2,
        margin=dict(l=50, r=50, t=80, b=50)  # Menos margen inferior
    )
    
    # Configurar ejes para todos los subplots
    for i in range(1, 4):
        fig.update_xaxes(
            title_text="Longitud" if i == 2 else "",
            row=1, col=i,
            scaleanchor="y",
            scaleratio=1,
            gridcolor='lightgray',
            griddash='dash',
            tickangle=0
        )
        fig.update_yaxes(
            title_text="Latitud" if i == 1 else "",
            row=1, col=i,
            gridcolor='lightgray',
            griddash='dash'
        )
    
    return fig