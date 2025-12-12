# Dashboard de Análisis Climático Multimodelo - SMN

## Descripción General

Sistema integral desarrollado para la Subdirección de Modelamiento Numérico (SMN) del SENAMHI que permite visualizar, analizar y comparar proyecciones climáticas (CMIP6) para Perú. Combina procesamiento científico batch con visualizaciones interactivas en tiempo real mediante Streamlit.

## Parte 1: Guía para Usuario Final

### Objetivos del Sistema

Proporcionar una interfaz intuitiva para explorar:
- **Escala Subnacional:** Desglose de información (series temporales y estadísticas) a nivel departamental.
- **Proyecciones de Cambio Climático:** Visualización espacial de anomalías (Futuro - Histórico) en temperatura y precipitación bajo escenarios SSP245 y SSP585.
- **Multimodel:** Generación de ensambles multimodelo para reducir la incertidumbre individual de los modelos globales.
- **Análisis Estadístico:** Análisis de cambios mediante pruebas estadisticas (T-Student) de significancia (p < 0.05)
- **Time of Emergence (TOE):** Identificación del año exacto en que la señal de cambio climático emerge permanentemente sobre la variabilidad natural del clima.

### Navegación y Vistas

#### Vista 1: Inicio General
Pantalla de bienvenida con instrucciones básicas y descripción de funcionalidades.

#### Vista 2: Promedio (Ensemble Multimodelo)
Visualización de consenso científico con tres componentes:
- Mapa de cambios SSP245 (escenario moderado)
- Mapa de cambios SSP585 (escenario severo)  
- Mapa de Time of Emergence (TOE)

#### Vista 3: Cambios por Modelo Individual
Comparación de proyecciones entre modelos específicos, con análisis de significancia de cambios por modelo.

#### Vista 4: Series Temporales por Departamento
Análisis temporal a escala subnacional que incluye:
- Gráfico de series (modelos individuales + promedio)
- Estadísticas comparativas entre períodos
- Mapas de ubicación departamental

### Controles de Interfaz

| Control | Función | Valores |
|---------|---------|---------|
| Modelos | Selección de modelos climáticos | ecmwf-51, ncep-2, etc. |
| Variable + Agregación | Variable climática y escala temporal | tasmin_ANUAL, pr_DEF, tasmax_MAM |
| Periodo base | Referencia climática | 1981-2010, 1991-2020 |
| Año centro + Escenario | Período futuro y trayectoria | 2050_ssp585, 2030_ssp245 |
| Significancia | Filtro estadístico | Activado/Desactivado |
| Departamento | Unidad subnacional | Lima, Cusco, Loreto, etc. |

---

## Parte 2: Documentación Técnica

### Arquitectura del Sistema

```
SISTEMA DASHBOARD CLIMÁTICO
├── Interfaz Principal (00_dashboard.py)
├── Procesamiento Batch (Scripts 01_*)
├── Módulos Auxiliares (src/)
└── Estructura de Datos (data/)
```

### 1. Interfaz Principal (00_dashboard.py)

Aplicación web Streamlit que orquesta:
- Gestión de estado mediante `st.session_state`
- Sidebar con controles de configuración
- Sistema de vistas (Inicio, Cambios, Series, Promedio)
- Integración de módulos de visualización
- Cache para optimización de rendimiento

**Flujo principal:**
```
Usuario → Selección parámetros → Detección vista → Carga datos → Generación visualización
```

### 2. Scripts de Procesamiento Batch

#### 01_preproc_01_dep.py
Procesamiento geoespacial por departamento:
- **Entrada**: NetCDF en `data/modelos_agre/`
- **Proceso**: Interpolación (0.1°), recorte departamental, cálculo de promedio espacial
- **Salida**: CSV en `data/procesados/` (formato: fecha × departamento)

#### 01_preproc_02_cambio.py
Cálculo de cambios climáticos y significancia:
- **Periodos**: Histórico (1981-2010/1991-2020) vs Futuro (ventana 30 años)
- **Algoritmo**: Δ = Futuro - Histórico, con test estadístico por punto de grilla
- **Salidas**: NetCDF (`mod_cambios/`) + numpy arrays (`mod_significancia/`)

#### 01_preproc_03_ens_cdo.py
Generación de ensambles multimodelo:
- **Requisito**: CDO (Climate Data Operators) instalado
- **Comando**: `cdo ensmean modelo1.nc modelo2.nc ... ensemble.nc`
- **Salidas**: Ensambles brutos, cambios y significancia en `data/ensamble/`

#### 01_preproc_04_toe.py
Cálculo de Time of Emergence:
- **Algoritmo**: 5-part algorithm implementado en `aux_calcular_toe.py`
- **Salida**: NetCDF con TOE_1 y TOE_2 en `data/mod_toe/`

### 3. Módulos Auxiliares (src/)

#### Categoría: Algoritmos Científicos
- `aux_cambios_significancia.py`: Funciones base para cambios y tests estadísticos
- `aux_ens_cdo.py`: Interfaz con CDO para cálculo de ensambles
- `aux_calcular_toe.py`: Implementación completa del algoritmo TOE (5 partes)

#### Categoría: Carga de Datos
- `data_loader_cambios.py`: Carga cambios por modelo individual
- `data_loader_promedio.py`: Carga datos de ensamble y TOE
- `series_temporales.py`: Carga series por departamento
- `estadisticas_series.py`: Cálculo de métricas comparativas

#### Categoría: Generación de Visualizaciones
- `graficos_cambios.py`: Mapas de cambios (Matplotlib + Geopandas)
- `graficos_promedio.py`: 3-map layout para ensambles (Plotly)
- `graficos_series.py`: Series temporales (Plotly)
- `mapa_interactivo.py`: Mapas departamentales interactivos

#### Categoría: Utilidades
- `dashboard_utils.py`: Funciones auxiliares (detectores, parsers, verificadores)

### 4. Estructura de Datos

```
data/
├── geo/peru32.geojson                   # Límites departamentales
├── modelos_agre/                        # ENTRADA PRINCIPAL
│   └── {variable}_{agregacion}_{modelo}_{ssp}.nc
├── procesados/                          # Series por departamento
│   └── {modelo}_{variable}_{agregacion}_{ssp}.csv
├── mod_cambios/                         # Cambios por modelo
│   └── {modelo}_{var}_{agg}_{ssp}_{base}_centro-{año}.nc
├── mod_significancia/                   # p-valores por modelo
│   └── {modelo}_{var}_{agg}_{ssp}_{base}_centro-{año}.npy
├── ensamble/                            # Resultados multimodelo
│   ├── datos/                          # Ensambles brutos
│   ├── cambios/                        # Cambios del ensamble
│   └── significancia/                  # Significancia del ensamble
└── mod_toe/                            # Time of Emergence
    └── ensemble_{variable}_{agregacion}_toe.nc
```

### Formatos de Archivo

#### Entrada NetCDF:
```python
Dimensions:  (time: 85, lat: 40, lon: 83)  # 1981-2065, resolución ~0.5°
Variables:
    tasmin (time, lat, lon)  # Temperatura mínima (°C)
    pr (time, lat, lon)      # Precipitación (mm/día)
Coordinates:
    time: datetime64[ns]     # 1981-01-01 a 2065-12-31
    lat: float64            # -19.0 a -0.5
    lon: float64            # -82.0 a -0.5
```

#### Salida CSV (series):
```csv
Fecha,AMAZONAS,ANCASH,APURIMAC,...
1981-01-01,15.2,12.4,10.8,...
1982-01-01,15.3,12.5,10.9,...
```

### Parámetros de Configuración

| Parámetro | Módulo | Valor | Descripción |
|-----------|--------|-------|-------------|
| `reso` | 01_preproc_01_dep.py | 0.5 | Resolución de interpolación (°) |
| `FUT_WINDOW` | 01_preproc_02_cambio.py | 30 | Ventana temporal futura (años) |
| `CENTER_YEARS` | 01_preproc_02_cambio.py | [2030, 2035, 2040, 2045, 2050] | Años centro |
| `levels` (pr) | graficos_cambios.py | np.arange(-100, 110, 10) | Contornos para precipitación |
| `levels` (temp) | graficos_cambios.py | np.arange(-4, 4.5, 0.5) | Contornos para temperatura |
| `deg` (polyfit) | aux_calcular_toe.py | 4 | Grado del polinomio de ajuste |
| `window` (rolling) | aux_calcular_toe.py | 10 | Ventana móvil para suavizado |

### Algoritmos Implementados

#### Cálculo de Cambios:
- **Temperatura**: ΔT = T_futuro - T_histórico (°C)
- **Precipitación**: ΔP% = ((P_futuro - P_histórico) / P_histórico) × 100

#### Test de Significancia:
```python
# Prueba t de Student para muestras independientes
t_stat, p_val = stats.ttest_ind(hist_series, fut_series, 
                                 equal_var=False, nan_policy='omit')
```

#### Time of Emergence (5-part algorithm):
1. Ajuste polinomial (grado 4) → Tendencia + Residuos
2. Separación señal/ruido
3. Cálculo variabilidad interna (ventanas móviles)
4. Relación señal/ruido = Tendencia / √(Variabilidad)
5. Detección cuando S/N > umbral (1°C o ±1%)

### Flujos de Trabajo

#### Para Nuevos Datos:
```bash
# 1. Colocar NetCDF en data/modelos_agre/
# 2. Ejecutar procesamiento secuencial
python 01_preproc_01_dep.py      # ~10 min para 10 modelos
python 01_preproc_02_cambio.py   # ~15 min para 100 combinaciones
python 01_preproc_03_ens_cdo.py  # ~5 min (requiere CDO)
python 01_preproc_04_toe.py      # ~8 min por variable

# 3. Verificar salidas
ls -lh data/procesados/*.csv | wc -l
ls -lh data/mod_cambios/*.nc | wc -l
ls -lh data/ensamble/cambios/*.nc
```

#### Para Desarrollo:
```python
# Patrón recomendado para nuevos módulos:
# 1. Ubicar en src/ según categoría
# 2. Importar en 00_dashboard.py si es necesario
# 3. Usar dashboard_utils.py para funciones comunes
# 4. Seguir convenciones de nombres existentes
```
#### Mensajes de Error Informativos

| Error | Módulo | Mensaje | Acción recomendada |
|-------|--------|---------|-------------------|
| Archivo no encontrado | data_loader_cambios.py | "no existe {ruta}" | Verificar preprocesamiento |
| Dimensión temporal faltante | aux_cambios_significancia.py | "No se encontró dimensión temporal" | Revisar formato NetCDF |
| CDO no disponible | 01_preproc_03_ens_cdo.py | "✗ ERROR: CDO no está instalado" | `conda install -c conda-forge cdo` |
| Shapefile faltante | graficos_cambios.py | "Error cargando shapefile" | Verificar `data/geo/peru32.geojson` |

### Consideraciones Técnicas
Se recomienda crear el ambiente desde cero para evitar conflictos de binarios geoespaciales:

```bash
# 1. Crear entorno limpio
conda env create -f environment.yml
conda activate e7-cc
# 2. Ejecutar dashboard
streamlit run 00_dashboard.py
```

#### Requisitos:
- **CDO**: Obligatorio para ensambles (`conda install -c conda-forge cdo`)
- **Memoria RAM**: Mínimo 8 GB (recomendado 16+ GB)
- **Espacio disco**: ~10 GB para datos completos

#### Validaciones:
1. Verificación de existencia de archivos antes de procesar
2. Consistencia dimensional entre datos históricos y futuros
3. Manejo robusto de NaN y valores extremos
4. Umbrales de calidad (mínimo 2 años para tests estadísticos)

#### Limitaciones Conocidas:
- Periodos base fijos (1981-2010, 1991-2020)
- Solo escenarios SSP245 y SSP585 completamente implementados
- Resolución espacial fija a 0.5°
- Formato específico de nombres de archivos requerido

#### Extensiones Futuras:
- Más escenarios (SSP126, SSP370, etc.)
- Indicadores derivados (índices de extremos)
- Análisis de incertidumbre (intervalos de confianza)
- Exportación avanzada (PDF, PNG, datos tabulares)

---

## Soporte y Mantenimiento

### Equipo Responsable
- **Locación SMN** - JAPQ
- **Contacto**: japaredesq@gmail.com
- **Repositorio**: https://github.com/Japq91/e7_dashboard

### Ciclo de Actualización
- **Semestral**: Revisión de algoritmos estadísticos
- **Anual**: Incorporación de nuevos modelos CMIP6

### Registro de Cambios
| Versión | Fecha | Cambios Principales |
|---------|-------|---------------------|
| 1.0 | Dic 2025 | Versión inicial con procesamiento básico |

## Referencias

### Bibliografía
1. Hawkins, E., & Sutton, R. (2012). *Time of emergence of climate signals*. Geophysical Research Letters.
2. Eyring, V., et al. (2016). *Overview of the Coupled Model Intercomparison Project Phase 6 (CMIP6)*.
3. Schulzweida, U. (2019). *CDO User Guide*. Max Planck Institute for Meteorology.

### Referencias Técnicas
1. **CDO**: https://code.mpimet.mpg.de/projects/cdo
2. **xarray**: https://xarray.pydata.org/
3. **CMIP6**: https://www.wcrp-climate.org/wgcm-cmip/wgcm-cmip6
4. **Plotly**: https://plotly.com/python/
5. **Streamlit**: https://streamlit.io/

---

*Documentación actualizada: Diciembre 2025*  
*Sistema desarrollado por la Subdirección de Modelamiento Numérico (SMN) - SENAMHI*  
*© Servicio Nacional de Meteorología e Hidrología del Perú*