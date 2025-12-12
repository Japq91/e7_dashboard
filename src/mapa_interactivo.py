# src/mapa_interactivo.py - Versión adaptada (sin cambios en parámetros)

import geopandas as gpd
import plotly.express as px

def crear_mapa_departamentos(geojson_path, departamento_seleccionado=None):
    """
    Crea dos mapas:
    1. Mapa fijo de Sudamérica (Perú completo) - MÁS ZOOM OUT
    2. Mapa con zoom al departamento seleccionado (±1.5 grado) - DEPARTAMENTO EN NEGRO
    """
    # Cargar y preparar datos
    gdf = gpd.read_file(geojson_path)
    gdf = gdf.to_crs(epsg=4326)

    # Crear columna para color: 0=gris, 1=negro (para departamento seleccionado)
    gdf['color_value'] = 0  # Todos grises por defecto

    # Si hay departamento seleccionado, marcarlo con 1 (negro)
    if departamento_seleccionado:
        idx_seleccionado = gdf[gdf['DEPARTAMEN'] == departamento_seleccionado].index
        if len(idx_seleccionado) > 0:
            gdf.loc[idx_seleccionado, 'color_value'] = 1

    # Crear escala de colores personalizada: 0=gris, 1=negro
    escala_colores = [[0, '#054579'], [1, '#f8cf3a']]

    # 1. MAPA GENERAL - Perú en Sudamérica (MÁS ZOOM OUT)
    fig_general = px.choropleth_mapbox(
        gdf,
        geojson=gdf.geometry.__geo_interface__,
        locations=gdf.index,
        color='color_value',
        color_continuous_scale=escala_colores,
        range_color=[0, 1],  # Fijar el rango para que solo use nuestros dos colores
        mapbox_style="carto-positron",
        zoom=2.3,  # MÁS ZOOM OUT para ver más de Sudamérica
        center={"lat": -10.0, "lon": -70.0},  # Centrado más al sur para ver mejor Sudamérica
        opacity=0.9,
        hover_name='DEPARTAMEN',
        hover_data={'DEPARTAMEN': True, 'color_value': False},
        labels={'DEPARTAMEN': 'Departamento'}
    )

    fig_general.update_coloraxes(showscale=False)  # Ocultar barra de color
    fig_general.update_traces(
        marker_line_width=0.5,
        marker_line_color='white'
    )

    fig_general.update_layout(
        margin={"r":0,"t":30,"l":0,"b":0},
        height=250,
        title_text="📍 Perú - Sudamerica".upper(),
        title_font_size=17,
        title_x=0.2,  # Centrar título
        title_y=0.95
    )

    # 2. MAPA CON ZOOM - Departamento seleccionado en NEGRO
    fig_zoom = px.choropleth_mapbox(
        gdf,
        geojson=gdf.geometry.__geo_interface__,
        locations=gdf.index,
        color='color_value',
        color_continuous_scale=escala_colores,
        range_color=[0, 1],
        mapbox_style="carto-positron",
        opacity=0.5,
        hover_name='DEPARTAMEN',
        hover_data={'DEPARTAMEN': True, 'color_value': False},
        labels={'DEPARTAMEN': 'Departamento'}
    )

    fig_zoom.update_coloraxes(showscale=False)
    fig_zoom.update_traces(
        marker_line_width=1.0,
        marker_line_color='white'
    )

    # Configurar zoom si hay departamento seleccionado
    if departamento_seleccionado:
        # Encontrar el departamento
        depto_filtrado = gdf[gdf['DEPARTAMEN'] == departamento_seleccionado]
        if not depto_filtrado.empty:
            bounds = depto_filtrado.iloc[0].geometry.bounds

            # Expandir bbox ±1.5 grado (MENOS ZOOM que antes)
            minx, miny, maxx, maxy = bounds
            minx -= 1.9
            maxx += 1.9
            miny -= 1.9
            maxy += 1.9

            # Calcular centro y zoom apropiado
            centro_lat = (miny + maxy) / 2
            centro_lon = (minx + maxx) / 2

            # Calcular el tamaño del bbox para ajustar el zoom
            lat_span = maxy - miny
            lon_span = maxx - minx
            max_span = max(lat_span, lon_span)

            # Ajustar zoom basado en el tamaño del área (menos zoom = número más pequeño)
            if max_span < 2:                zoom_level = 7.5
            elif max_span < 3:                zoom_level = 7.0
            elif max_span < 4:                zoom_level = 6.5
            elif max_span < 5:                zoom_level = 6.0
            else:                zoom_level = 5.5

            fig_zoom.update_layout(
                mapbox=dict(
                    center={"lat": centro_lat, "lon": centro_lon},
                    zoom=zoom_level  # MENOS ZOOM que antes
                ),
                margin={"r":0,"t":30,"l":0,"b":0},
                height=250,
                title_text=f"🔍 {departamento_seleccionado}",
                title_font_size=16,
                title_x=0.2,
                title_y=0.95
            )
        else:
            # Si no encuentra el departamento, vista por defecto
            fig_zoom.update_layout(
                mapbox_center={"lat": -9.19, "lon": -75.0},
                mapbox_zoom=5.0,  # Menos zoom por defecto también
                margin={"r":0,"t":30,"l":0,"b":0},
                height=250,
                title_text="🔍 Zoom a Departamento",
                title_font_size=16,
                title_x=0.5,
                title_y=0.95
            )
    else:
        # Sin departamento seleccionado
        fig_zoom.update_layout(
            mapbox_center={"lat": -10, "lon": -75.0},
            mapbox_zoom=4.5,  # Menos zoom
            margin={"r":0,"t":30,"l":0,"b":0},
            height=250,
            title_text="🔍 Seleccione un departamento para ver zoom",
            title_font_size=16,
            title_x=0.5,
            title_y=0.95
        )

    return fig_general, fig_zoom, gdf
