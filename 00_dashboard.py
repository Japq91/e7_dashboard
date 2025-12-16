#!/usr/bin/env python
# coding: utf-8

"""
00_dashboard.py - 
    Dashboard climático con análisis espacial y temporal
    Incluye: Mapas de cambios, Series temporales y Gráfico PROMEDIO
Para ejecutar:
    streamlit run 00_dashboard.py
"""

import streamlit as st
import os
import sys

# Preparar path
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

# Importar funciones de la carpeta src
from data_loader_cambios import (cargar_cambios,cargar_significancia,obtener_vmin_vmax)
from graficos_cambios import generar_mapa_multimodelo
from data_loader_series import cargar_series_modelos, obtener_serie_departamento
from graficos_series import crear_grafico_series
from estadisticas_series import calcular_estadisticas_periodos
from mapa_interactivo import crear_mapa_departamentos

# Importar funciones para el botón PROMEDIO
from graficos_promedio import generar_mapa_promedio
from data_loader_promedio import cargar_cambios_ensemble

# Importar funciones auxiliares del dashboard
from dashboard_utils import (
    obtener_lista_modelos,
    obtener_lista_var_agre,
    obtener_lista_year_ssp,
    obtener_lista_escenarios,
    separar_var_agre,
    separar_centro_ssp,
    obtener_unidad_variable,
    obtener_nombre_completo_variable,
    obtener_nombre_agregacion
)
# GEOJSON FILE <---------------------------------
geo_file="data/geo/peru32.geojson"
# Configuración inicial
st.set_page_config(
    page_title="Dashboard CC - SMN",
    layout="wide",
    page_icon="⛰️🏔️⛰️",
    initial_sidebar_state="expanded"
)

def main():
    """
    Función principal del dashboard
    """
    ###############################
    # Inyectar CSS global
    ###############################    
    st.markdown("""
        <style>
        h1 {font-size: 36px !important;text-align: center;}
        h2, h3 {font-size: 24px !important;color: #05457a !important;}    
        section[data-testid="stSidebar"] {
            background-color: #D2B48C !important;
            width: 220px;          /* ancho fijo */
            min-width: 200px;
            max-width: 300px;
        }
    
        .medium-label {
            font-size: 18px !important;
            font-weight: bold !important;
            margin-bottom: 0.5rem;
        }        
    
        .stMultiSelect label, 
        .stSelectbox label, 
        .stCheckbox label {
            font-size: 18px !important;
            font-weight: bold !important;
        }        
    
        .stButton button {
            font-size: 18px !important;
            font-weight: bold !important;
        }
    
        .stSelectbox, 
        .stMultiselect {
            border: 1px solid #D2B48C !important;
        }
        /* ===== título compacto ===== */
        .titulo-compacto {
            font-size: 16px !important;
            color: #05457a;
            text-align: left;
            padding: 5px 0;
            margin: 0;
            font-weight: 500;
        }
        </style>
    """, unsafe_allow_html=True)

    vista = st.session_state.get("vista", "inicio")

    ###############################
    # BARRA LATERAL (SIDEBAR)
    ###############################
    with st.sidebar:        
        st.header("⚙️Configuración")
        # ============================
        # NAVEGACIÓN POR "VISTA"
        # ============================
        ejecutar_inicio = st.button("INICIO GENERAL -> 🏠")
        if ejecutar_inicio:
            st.session_state.vista = "inicio"
        
        # BOTÓN PROMEDIO
        ejecutar_promedio = st.button("PROMEDIO -> 🌍", type="primary")
        if ejecutar_promedio:
            st.session_state.vista = "promedio"
        
        st.markdown("---")
        
        # 1. Modelos
        st.markdown('<p class="medium-label">Modelos</p>', unsafe_allow_html=True)
        modelos = obtener_lista_modelos()
        sel_mod = st.multiselect(
            "Modelos",
            modelos,
            default=modelos[:min(3, len(modelos))] if modelos else [],
            label_visibility="collapsed"
        )

        # 2. Variable con agregación
        st.markdown('<p class="medium-label">Variable y Agregación</p>', unsafe_allow_html=True)
        var_agres = obtener_lista_var_agre()
        sel_var_agre = st.selectbox(
            "Variable y Agregación",
            var_agres,
            label_visibility="collapsed"
        )

        # 3. Periodo base
        st.markdown('<p class="medium-label">Periodo base</p>', unsafe_allow_html=True)
        bases = ["1981-2010", "1991-2020"]
        sel_base = st.selectbox(
            "Periodo base",
            bases,
            label_visibility="collapsed"
        )

        # 4. Año centro con escenario (USADO PARA CAMBIOS Y SERIES)
        st.markdown('<p class="medium-label">Año centro y Escenario</p>', unsafe_allow_html=True)
        year_ssp_list = obtener_lista_year_ssp()
        sel_year_ssp = st.selectbox(
            "Año centro y Escenario",
            year_ssp_list,
            label_visibility="collapsed"
        )

        # 5. Checkbox de significancia
        activar_sig = st.checkbox("Significancia: [ p < 0.05 ]")

        # BOTÓN CAMBIOS
        ejecutar_cambios = st.button("CAMBIOS", type="primary")
        if ejecutar_cambios:
            st.session_state.vista = "cambios"
        
        st.markdown("---")
        
        ###############################
        # SECCIÓN DE SERIES TEMPORALES
        ###############################
        st.markdown('<p class="medium-label">SERIES TEMPORALES</p>', unsafe_allow_html=True)
        
        # BOTÓN SERIES
        ejecutar_series = st.button("SERIES", type="primary")
        if ejecutar_series:
            st.session_state.vista = "series"

        # Control de mostrar_series
        st.session_state.mostrar_series = (st.session_state.get("vista", "inicio") == "series")

        # Si se activa series temporales, mostrar lista de departamentos
        if st.session_state.get('mostrar_series', False):
            try:
                import geopandas as gpd
                gdf = gpd.read_file(geo_file)
                departamentos = sorted(gdf['DEPARTAMEN'].tolist())
                
                depto_seleccionado = st.selectbox(
                    "Seleccione departamento:",
                    departamentos,
                    key="selector_depto"
                )
                
                st.session_state.depto_seleccionado = depto_seleccionado
                
            except Exception as e:
                st.error(f"Error cargando departamentos: {e}")
        else:
            if 'depto_seleccionado' in st.session_state:
                del st.session_state.depto_seleccionado
    
    ###############################
    # ÁREA PRINCIPAL DEL DASHBOARD
    ###############################

    vista = st.session_state.get("vista", "inicio")
    if vista == "inicio":
        # Título completo solo en página de inicio
        st.title("🌡️ ⛈️ Dashboard – Cambio Climático 🌍 💾")
        st.title("Subdirección de Modelamiento Numérico – SMN")
        st.markdown("---")
    else:
        # Título compacto para vistas de gráficos
        st.markdown(
            '<p class="titulo-compacto">🌡️ Dashboard CC – SMN</p>', 
            unsafe_allow_html=True
        )
    
    # 0. GRÁFICO DE PROMEDIO
    if vista == "promedio" and sel_var_agre:
        st.header("📊 PROMEDIO (%s MODELOS)"%len(modelos))
        
        try:
            var, agregacion = separar_var_agre(sel_var_agre)
            
            # EXTRAER EL AÑO CENTRO DEL SELECTOR EXISTENTE
            if '_' in sel_year_ssp:
                centro_year = sel_year_ssp.split('_')[0]
            else:
                centro_year = "2050"
                
        except ValueError as e:
            st.error(f"Error en formato: {e}")
            return
        
        with st.spinner("Generando gráfico de promedio..."):
            try:
                fig = generar_mapa_promedio(
                    variable=var,
                    agregacion=agregacion,
                    periodo_base=sel_base,
                    centro_year=centro_year
                )
                
                st.plotly_chart(fig, use_container_width=True)
                
                col1, col2, col3, col4 = st.columns(4)
                with col1:
                    st.info(f"**Variable:** {var}")
                with col2:
                    st.info(f"**Agregación:** {agregacion}")
                with col3:
                    st.info(f"**Período base:** {sel_base}")
                with col4:
                    st.info(f"**Año centro:** {centro_year}")
                
                with st.expander("ℹ️ Información general u_u"):
                    st.markdown(f"""
                    **Mapa 1 (Izquierda):** Cambios promedio SSP245 (centrado en {centro_year})  
                    **Mapa 2 (Centro):** Cambios promedio SSP585 (centrado en {centro_year})  
                    **Mapa 3 (Derecha):** TOE (Time of Emergence)  
                    
                    *Nota:*
                    - Los cambios se calculan como promedio de todos los modelos disponibles.
                    - Modelos: {modelos}
                    - Los puntos negros indican significancia estadística (p < 0.05)
                    - La barra de color es compartida para SSP245 y SSP585
                    """)
                    
            except Exception as e:
                st.error(f"Error generando gráfico de promedio: {e}")
                st.info("""
                Si los datos del ensemble no están disponibles, ejecuta primero:
                ```
                python 01_preproc_03_ens_cdo.py
                ```
                """)

    # 1. MAPA DE CAMBIOS
    elif vista == "cambios" and sel_mod and sel_var_agre and sel_year_ssp:
        st.header("📈 Cambios Proyectados >._.<")
        
        try:
            var, agregacion = separar_var_agre(sel_var_agre)
            centro, ssp = separar_centro_ssp(sel_year_ssp)
        except ValueError as e:
            st.error(f"Error en formato: {e}")
            return
        
        with st.spinner("Generando mapa de cambios..."):
            try:
                dict_cambios = cargar_cambios(sel_mod, var, agregacion, ssp, sel_base, centro)
                dict_pvals = None

                if activar_sig:
                    dict_pvals = cargar_significancia(sel_mod, var, agregacion, ssp, sel_base, centro)

                vmin_global, vmax_global = obtener_vmin_vmax(var)

                fig = generar_mapa_multimodelo(
                    dict_cambios,
                    dict_pvals,
                    vmin_global,
                    vmax_global,
                    var,
                    agregacion=agregacion,
                    sel_base=sel_base,
                    ssp=ssp,
                    centro=centro
                )

                st.pyplot(fig)
                
                col1, col2, col3, col4 = st.columns(4)
                with col1:
                    st.info(f"**Modelos:** {len(sel_mod)}")
                with col2:
                    st.info(f"**Variable:** {var}")
                with col3:
                    st.info(f"**Agregación:** {agregacion}")
                with col4:
                    st.info(f"**Año centro:** {centro}, **Escenario:** {ssp}")
                    
            except Exception as e:
                st.error(f"Error generando mapa de cambios: {e}")
             
    # 2. SERIES TEMPORALES (AHORA USA sel_year_ssp)
    elif vista == "series" and sel_mod and sel_var_agre:
        st.header("📈 Series Temporales  ._. ")
        
        if 'depto_seleccionado' in st.session_state:
            depto_seleccionado = st.session_state.depto_seleccionado

            try:
                var, agregacion = separar_var_agre(sel_var_agre)
                # EXTRAER EL ESCENARIO del selector año_centro_escenario
                centro, ssp = separar_centro_ssp(sel_year_ssp)
            except ValueError as e:
                st.error(f"Error en formato: {e}")
                return
            
            # Cargar series usando el escenario extraído de sel_year_ssp
            cache_key = f"{sel_mod}_{var}_{agregacion}_{ssp}"
            
            if ('series_dict' not in st.session_state or 
                st.session_state.get('cache_key', '') != cache_key):
                
                with st.spinner("Cargando datos de series..."):
                    series_dict = cargar_series_modelos(sel_mod, var, agregacion, ssp)
                    st.session_state.series_dict = series_dict
                    st.session_state.cache_key = cache_key
                    st.session_state.ultima_var = var
                    st.session_state.ultima_agregacion = agregacion
            
            # Generar gráfico de series
            with st.spinner("Generando series temporales..."):
                try:
                    df_series = obtener_serie_departamento(
                        st.session_state.series_dict, 
                        depto_seleccionado
                    )
                    
                    if df_series is not None:
                        fig_series = crear_grafico_series(
                            df_series, 
                            depto_seleccionado, 
                            var
                        )
                        
                        st.plotly_chart(fig_series, use_container_width=True)
                        
                        estadisticas = calcular_estadisticas_periodos(
                            df_series, 
                            var, 
                            sel_base, 
                            sel_year_ssp
                        )
                        
                        st.markdown("### Resumen general u_u 📋")
                        
                        col1, col2, col3, col4 = st.columns(4)
                        
                        with col1:
                            st.metric(
                                label=f"Período Base {estadisticas['periodo_base']}",
                                value=f"{estadisticas['base_promedio']:.2f}{estadisticas['unidad']}",
                                delta=f"±{estadisticas['base_std']:.2f}"
                            )
                            st.caption("Desv. estándar")
                        
                        with col2:
                            st.metric(
                                label=f"Período Futuro {estadisticas['periodo_futuro']}",
                                value=f"{estadisticas['fut_promedio']:.2f}{estadisticas['unidad']}",
                                delta=f"±{estadisticas['fut_std']:.2f}"
                            )
                            st.caption(f"Centrado en {estadisticas['ano_centro']}")
                        
                        with col3:
                            if var in ['tasmin', 'tasmax']:
                                cambio_abs = estadisticas['fut_promedio'] - estadisticas['base_promedio']
                                st.metric(
                                    label="Cambio Absoluto",
                                    value=f"{estadisticas['base_promedio']:.2f} → {estadisticas['fut_promedio']:.2f}",
                                    delta=f"{cambio_abs:.2f}°C"
                                )
                            else:
                                st.metric(
                                    label="Cambio Absoluto",
                                    value=estadisticas['cambio_absoluto'],
                                    delta=None
                                )
                            st.caption("Diferencia directa")
                        
                        with col4:
                            st.metric(
                                label="Cambio Porcentual",
                                value=estadisticas['cambio_porcentual'],
                                delta=None
                            )
                            if var == 'pr':
                                st.caption("Relativo al periodo base")
                            else:
                                st.caption("(Para referencia)")
                        
                    else:
                        st.warning(f"No hay datos disponibles para {depto_seleccionado}")
                        
                except Exception as e:
                    st.error(f"Error generando series: {e}")
            
            # Crear y mostrar mapas
            with st.spinner("Generando mapas..."):
                try:
                    fig_general, fig_zoom, gdf = crear_mapa_departamentos(
                        geo_file, 
                        depto_seleccionado
                    )
                    
                    col_mapa1, col_mapa2, col_info = st.columns([2, 2, 1.5])
                    
                    with col_mapa1:
                        st.plotly_chart(fig_general, use_container_width=True)
                        st.caption("Vista general -> Perú")
                    
                    with col_mapa2:
                        st.plotly_chart(fig_zoom, use_container_width=True)
                        st.caption(f"🔍 Departamento seleccionado")

                    with col_info:
                        st.info(f"**Departamento:**\n### {depto_seleccionado}")
                        
                        nombres_var = {
                            'tasmin': 'Temperatura mínima promedio',
                            'tasmax': 'Temperatura máxima promedio',
                            'pr': 'Precipitación'
                        }
                        
                        st.info(f"**Agregación:** {agregacion}")
                        st.info(f"**Escenario:** {ssp}")
                
                except Exception as e:
                    st.error(f"Error creando mapas: {e}")

        else:
            st.info("Seleccione un departamento de la lista en la barra lateral")

    # 3. PANTALLA DE INICIO (DEFAULT)
    else:
        st.info("👈 Seleccione una opción en la barra lateral para comenzar")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("### 🗺️ Análisis Espacial -> Mapa de Cambios")
            st.markdown("""
            1. Seleccione modelos, variable (con agregación) y periodo base
            2. Seleccione año centro y escenario (ej: 2030_ssp245)
            3. Haga clic en **"CAMBIOS"**
            4. Opcional: active significancia estadística
            """)
            
        with col2:
            st.markdown("### 📊 Gráfico PROMEDIO -> %s Modelos"%len(modelos))
            st.markdown("""
            1. Seleccione variable (con agregación) y periodo base
            2. Haga clic en **"PROMEDIO"**
            3. Vea los 3 mapas: SSP245, SSP585 y TOE
            """)
        
        st.markdown("---")
        
        st.markdown("### 📈 Análisis Temporal -> Departamentos")
        st.markdown("""
        1. Seleccione modelos, variable (con agregación) y periodo base
        2. Seleccione año centro y escenario (se usará el escenario)
        3. Haga clic en **"SERIES"**
        4. Elija un departamento de la lista
        5. Vea las series en el gráfico
        6. Revise estadísticas comparativas
        """)

if __name__ == "__main__":
    # Inicializar estados de sesión
    if 'mostrar_series' not in st.session_state:
        st.session_state.mostrar_series = False
    if 'series_dict' not in st.session_state:
        st.session_state.series_dict = None
    if 'cache_key' not in st.session_state:
        st.session_state.cache_key = ""
    if 'ultima_var' not in st.session_state:
        st.session_state.ultima_var = ""
    if 'ultima_agregacion' not in st.session_state:
        st.session_state.ultima_agregacion = ""

    if 'vista' not in st.session_state:
        st.session_state.vista = "inicio"
    
    # Ejecutar dashboard
    main()