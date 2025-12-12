# src/graficos_cambios.py - Versión adaptada con subtitle
import matplotlib.pyplot as plt
import numpy as np
import math
import geopandas as gpd

shapefile_path = 'data/geo/peru32.geojson'

def generar_mapa_multimodelo(dict_cambios, dict_pvals, vmin_global, vmax_global, var,
                             agregacion=None, sel_base=None, ssp=None, centro=None):
    """
    Genera mapas alineados en filas de 4 con barra global.
    La significancia se marca con 'x' en el centro de cada celda.
    Los rangos y colormap dependen de la variable.
    
    Parámetros adicionales para subtitle:
    - agregacion: tipo de agregación temporal (ej: "anual", "DJF", "MAM")
    - sel_base: periodo base (ej: "1981-2010")
    - ssp: escenario (ej: "ssp245", "ssp585")
    - centro: año centro (ej: "2030", "2050")
    """
    # configuración de colores y niveles según variable
    if var == "pr":
        cmap = "BrBG"
        levels = np.arange(-100.0, 110.0, 10.0)  # -100 a 100 cada 10
    else:
        cmap = "turbo"
        levels = np.arange(-4.0, 4.5, 0.5)       #

    modelos = list(dict_cambios.keys())
    n = len(modelos)
    cols = 4
    rows = math.ceil(n / cols)

    fig, axes = plt.subplots(
        rows, cols,
        figsize=(cols * 2, rows * 3),
        squeeze=False
    )

    axes_flat = axes.flatten()
    im = None

    for i, mod in enumerate(modelos):
        ax = axes_flat[i]
        da = dict_cambios[mod]

        # mapa de cambios
        im = da.plot(
            ax=ax,
            cmap=cmap,
            vmin=vmin_global,
            vmax=vmax_global,
            levels=levels,
            add_colorbar=False,
            extend='both',
        )

        ax.set_title(mod.upper())
        #
        _agregar_shapefile(ax, fig, shapefile_path)
        # DEJA SIN NOMBRE EJES
        ax.set_ylabel('')
        ax.set_xlabel('')

        # marcadores de significancia
        if dict_pvals is not None and mod in dict_pvals:
            pvals = dict_pvals[mod]

            mask = (pvals < 0.05)

            if np.any(mask):
                lats = da["lat"].values
                lons = da["lon"].values
                Lon, Lat = np.meshgrid(lons, lats)

                x_sig = Lon[mask]
                y_sig = Lat[mask]

                ax.scatter(
                    x_sig,
                    y_sig,
                    marker="x", ## TIPO DE MARKADOR
                    s=12,
                    linewidths=0.3,
                    color='k',
                )

    # ocultar ejes vacíos
    for j in range(n, rows * cols):
        axes_flat[j].axis("off")
    
    # barra
    last_ax = axes_flat[n-1] if n > 0 else None
    # Llamar a la función de barra dinámica
    _agregar_barra_d(fig, im, last_ax, rows, var)
    
    # ===== AGREGAR SUBTITLE =====
    _agregar_subtitle(fig, agregacion, sel_base, ssp, centro, var, n)
    
    # Ajustar espacios (reducir top para dar espacio al subtitle)
    fig.subplots_adjust(
            left=0.05,
            right=0.90,
            top=0.92,  # Cambiado de 0.95 a 0.92
            bottom=0.05,
            wspace=0.25,
            hspace=0.25
            )
    return fig


def _agregar_subtitle(fig, agregacion, sel_base, ssp, centro, var ,n):
    """
    Agrega un subtitle con información de la configuración del análisis.
    """
    if agregacion is None and sel_base is None and ssp is None:
        return  # No agregar subtitle si no hay información
    
    # Diccionario de nombres más descriptivos para agregaciones
    nombres_agregacion = {
        'anual': 'Anual',
        'DJF': 'DEF', #Verano (DJF)
        'MAM': 'MAM', #Otoño (MAM)
        'JJA': 'JJA', #Invierno (JJA)
        'SON': 'SON', #Primavera (SON)
        'mensual': 'Mensual'
    }
    
    # Diccionario para nombres de escenarios
    nombres_ssp = {
        'ssp245': 'SSP2-4.5',
        'ssp585': 'SSP5-8.5',
        'ssp126': 'SSP1-2.6',
        'ssp370': 'SSP3-7.0'
    }
    
    # Diccionario para nombres de variables
    nombres_var = {
        'pr': 'Precipitación',
        'tasmin': 'Temperatura mínima',
        'tasmax': 'Temperatura máxima',
        'tas': 'Temperatura media'
    }
    
    # Construir el texto del subtitle
    partes = []
    
    if var:
        var_nombre = nombres_var.get(var, var)
        partes.append(f"{var_nombre}")
    
    if agregacion:
        agre_nombre = nombres_agregacion.get(agregacion, agregacion)
        partes.append(f"{agre_nombre}")
    
    if sel_base:
        partes.append(f"Base: {sel_base}")
    
    if centro and ssp:
        ssp_nombre = nombres_ssp.get(ssp.lower(), ssp.upper())
        partes.append(f"Futuro: {centro} ({ssp_nombre})")
    elif centro:
        partes.append(f"Año centro: {centro}")
    elif ssp:
        ssp_nombre = nombres_ssp.get(ssp.lower(), ssp.upper())
        partes.append(f"Escenario: {ssp_nombre}")
    
    subtitle_text = " | ".join(partes)
    
    # Agregar el subtitle en la parte superior de la figura
    if n==2: x0=0.3
    elif n==3: x0=0.4
    else: x0=0.4
    fig.suptitle(
        subtitle_text,
        fontsize=12,
        y=0.98,
        x=x0,
        fontweight='normal',
        color='#05457a'
    )


def _agregar_barra_d(fig, im, last_ax, rows ,var='pr'):
    """
    Agrega barra de color al lado del último panel.
    Barra tendrá el mismo tamaño vertical que el panel.
    """
    if im is None or last_ax is None:
        return None

    # Obtener posición del último panel
    pos = last_ax.get_position()

    # Barra al lado derecho del panel (3% de ancho, 1% de separación)
    bar_width = pos.width * 0.08
    cax_left = pos.x1 + 0.01
    cax_bottom = pos.y0
    cax_height = pos.height
    if rows > 0: cax_bottom = cax_bottom - 0.03
    # Crear eje para la barra
    cax = fig.add_axes([cax_left, cax_bottom, bar_width, cax_height])
    # Añadir barra
    cbar = fig.colorbar(im, cax=cax, orientation="vertical", extend='both')
    cbar.ax.set_ylabel('Cambio (%)' if var == "pr" else 'Cambio (°C)', fontsize=10)
    return cbar


def _agregar_shapefile(ax, fig, geojson_path, edgecolor='black', facecolor='none', linewidth=1, alpha=0.5):
    """
    Agrega un shapefile (.geojson) encima del plot.
    """
    try:
        # Cargar el shapefile
        gdf = gpd.read_file(geojson_path)

        # Verificar que tenga sistema de coordenadas
        if gdf.crs is None:
            print(f"Advertencia: Shapefile {geojson_path} no tiene CRS definido")
            # Asumir WGS84 si no tiene CRS
            gdf = gdf.set_crs('EPSG:4326')

        # Plotear el shapefile encima
        gdf.plot(
            ax=ax,
            edgecolor=edgecolor,
            facecolor=facecolor,
            linewidth=linewidth,
            alpha=alpha
        )

        return gdf

    except FileNotFoundError:
        print(f"Error: No se encontró el archivo {geojson_path}")
        return None
    except Exception as e:
        print(f"Error al cargar shapefile: {e}")
        return None