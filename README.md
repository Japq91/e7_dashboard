# 🌍 Dashboard de Análisis Climático Multimodelo - SMN

## 📋 Descripción General

Este repositorio aloja el **Dashboard de Análisis Climático Multimodelo**, una herramienta integral desarrollada para la **Subdirección de Modelamiento Numérico (SMN)** del SENAMHI. El sistema permite visualizar, analizar y comparar proyecciones climáticas (CMIP6) para Perú, combinando un procesamiento científico robusto (backend batch) con visualizaciones interactivas en tiempo real (frontend Streamlit).

---

## 🚀 Parte 1: Para el Usuario Final

### 🎯 Objetivos del Sistema
Proporcionar una interfaz intuitiva para explorar:
- **Proyecciones de Cambio Climático:** Visualización espacial de anomalías (Futuro - Histórico) en temperatura y precipitación bajo escenarios SSP245 y SSP585.
- **Consenso Científico:** Generación de ensambles multimodelo para reducir la incertidumbre individual de los modelos globales.
- **Análisis Estadístico:** Evaluación de la robustez de las señales mediante pruebas de significancia (T-Student).
- **Time of Emergence (TOE):** Identificación del año exacto en que la señal de cambio climático emerge permanentemente sobre la variabilidad natural del clima.
- **Escala Subnacional:** Desglose de información (series temporales y estadísticas) a nivel departamental para la toma de decisiones locales.

### 🖥️ Navegación en el Dashboard

#### 📊 Vistas Disponibles:

1. **INICIO GENERAL (🏠)**
   - Punto de entrada con instrucciones detalladas
   - Descripción de funcionalidades disponibles
   - No requiere configuración previa

2. **PROMEDIO (🌍)**
   - **Objetivo**: Visualizar consenso multimodelo
   - **Salidas**: 
     - Mapa 1: Cambios SSP245 (escenario moderado)
     - Mapa 2: Cambios SSP585 (escenario severo)
     - Mapa 3: TOE (año de emergencia de la señal climática)
   - **Beneficio**: Identificación rápida de zonas críticas con acuerdo multimodelo

3. **CAMBIOS**
   - **Objetivo**: Comparar proyecciones individuales de modelos
   - **Configuración requerida**:
     - Modelos (selección múltiple)
     - Variable + Agregación temporal
     - Periodo de referencia
     - Año centro + Escenario
   - **Beneficio**: Análisis detallado de incertidumbre intermodelo

4. **SERIES**
   - **Objetivo**: Analizar evolución temporal por departamento
   - **Componentes**:
     - Gráfico de series temporales (modelos + promedio)
     - Estadísticas comparativas periodos base/futuro
     - Mapas de ubicación departamental
   - **Beneficio**: Evaluación de impactos a escala subnacional

### 🎮 Controles Principales

| Control | Función | Valores Típicos |
|---------|---------|-----------------|
| **Modelos** | Selección de modelos climáticos | ecmwf-51, ncep-2, etc. |
| **Variable y Agregación** | Variable climática + escala temporal | tasmin_ANUAL, pr_DEF, tasmax_MAM |
| **Periodo base** | Línea de referencia climática | 1981-2010, 1991-2020 |
| **Año centro y Escenario** | Periodo futuro + trayectoria socioeconómica | 2050_ssp585, 2030_ssp245 |
| **Significancia** | Filtro estadístico (p < 0.05) | Activado/Desactivado |
| **Departamento** | Unidad subnacional para series | Lima, Cusco, Loreto, etc. |

---

## 🔧 Parte 2: Para el Desarrollador/Analista

### 🏗️ Arquitectura del Sistema

#### **ESTRUCTURA GENERAL DEL SISTEMA**

```
SISTEMA DASHBOARD CLIMÁTICO
├── 📊 INTERFAZ PRINCIPAL (00_dashboard.py)
├── 🔄 PROCESAMIENTO DE DATOS (Scripts 01_*)
├── 🧩 MÓDULOS AUXILIARES (carpeta src/)
└── 📁 ESTRUCTURA DE DATOS (carpeta data/)
```

---

### **📊 INTERFAZ PRINCIPAL**

#### **00_dashboard.py** ⭐
**Función**: Aplicación web completa con Streamlit

```
Flujo de la interfaz:
1. USUARIO → Selecciona parámetros en Sidebar
2. SISTEMA → Detecta vista activa (Inicio/Cambios/Series/Promedio)
3. CARGA → Llama módulos correspondientes según vista
4. VISUALIZA → Muestra gráficos en área principal
5. ACTUALIZA → Maneja estado con st.session_state
```

**Componentes clave**:
- **Sidebar**: Controles de selección (modelos, variables, periodos)
- **Área principal**: Visualizaciones según vista seleccionada
- **Gestión de estado**: Cache para series temporales
- **Estilos CSS**: Personalización visual para SMN

---

### **🔄 PROCESAMIENTO**

#### **4 Scripts Principales** (ejecución secuencial)

```
📁 DATOS BRUTOS (modelos_agre/*.nc)
    │
    ▼
┌─────────────────────────────────────┐
│   01_preproc_01_dep.py              │ ← 📊 Procesa por departamento
│   • Entrada: NetCDF modelos         │
│   • Salida: CSV por depto          │
└─────────────────┬───────────────────┘
                  │
                  ▼
┌─────────────────────────────────────┐
│   01_preproc_02_cambio.py           │ ← 🔄 Calcula cambios + significancia
│   • Cambios: futuro vs referencia   │
│   • Significancia: test estadístico │
└─────────────────┬───────────────────┘
                  │
                  ▼
┌─────────────────────────────────────┐
│   01_preproc_03_ens_cdo.py          │ ← 🧮 Genera ensambles (requiere CDO)
│   • Agrupa modelos por variable     │
│   • Promedio multimodelo con CDO    │
└─────────────────┬───────────────────┘
                  │
                  ▼
┌─────────────────────────────────────┐
│   01_preproc_04_toe.py              │ ← ⏰ Calcula Time of Emergence
│   • Algoritmo de 5 partes          │
│   • Detección señal/ruido          │
└─────────────────────────────────────┘
```

---

### **🧩 MÓDULOS AUXILIARES (src/)**

#### **1. ALGORITMOS CIENTÍFICOS 🧪**
```
aux_cambios_significancia.py
├── seleccionar_periodo() → Filtra años
├── calcular_delta() → Cambios (absoluto/porcentual)
└── calcular_pvals() → Significancia estadística

aux_ens_cdo.py (interfaz CDO)
├── calcular_ensemble_cdo() → Ejecuta "cdo ensmean"
└── verificar_ensemble_existente() → Evita reproceso

aux_calcular_toe.py (algoritmo TOE en 5 partes)
├── Parte 1: Ajuste polinomial + residuos
├── Parte 2: Agregación temporal
├── Parte 3: Variabilidad interna
├── Parte 4: Preparación series
└── Parte 5: Detección con umbrales
```

#### **2. CARGA DE DATOS 💾**
```
data_loader_cambios.py → Cambios por modelo individual
data_loader_promedio.py → Datos de ensamble y TOE
series_temporales.py → Series por departamento
estadisticas_series.py → Cálculo métricas comparativas
```

#### **3. GENERACIÓN DE GRÁFICOS 🎨**
```
graficos_cambios.py → Mapas con Matplotlib (por modelo)
graficos_promedio.py → 3 mapas con Plotly (ensamble)
graficos_series.py → Series temporales con Plotly
mapa_interactivo.py → Mapas departamentales interactivos
```

#### **4. UTILITARIOS 🛠️**
```
dashboard_utils.py → Funciones auxiliares
├── obtener_lista_modelos() → Detecta modelos disponibles
├── separar_var_agre() → Procesa cadenas
└── verificar_datos_disponibles() → Diagnóstico sistema
```

---

### **📁 ESTRUCTURA DE DATOS**

#### **Jerarquía de carpetas:**
```
data/
├── 📂 geo/                   # Archivos geoespaciales
│   └── peru32.geojson       # Límites departamentales
│
├── 📂 modelos_agre/         # ENTRADA PRINCIPAL
│   └── {var}_{agg}_{modelo}_{ssp}.nc
│
├── 📂 procesados/           # Series por departamento
│   └── {modelo}_{var}_{agg}_{ssp}.csv
│
├── 📂 mod_cambios/          # Cambios por modelo
│   └── {modelo}_{var}_{agg}_{ssp}_{base}_centro-{cy}.nc
│
├── 📂 mod_significancia/    # p-valores por modelo
│   └── {modelo}_{var}_{agg}_{ssp}_{base}_centro-{cy}.npy
│
├── 📂 ensamble/             # Resultados multimodelo
│   ├── 📂 datos/            # Ensambles brutos
│   ├── 📂 cambios/          # Cambios de ensamble
│   └── 📂 significancia/    # Significancia de ensamble
│
└── 📂 mod_toe/              # Time of Emergence
    └── ensemble_{var}_{agg}_toe.nc
```

---

### **🔄 FLUJOS DE DATOS PRINCIPALES**

#### **FLUJO 1: Datos crudos → Series departamentales**
```
1. NetCDF modelos → Interpolación a resolución 0.5°
2. Recorte por geometría departamental
3. Cálculo promedio espacial por departamento
4. Guardado como CSV (fecha × departamento)
```

#### **FLUJO 2: Datos crudos → Cambios climáticos**
```
1. Selección periodo histórico (1981-2010 / 1991-2020)
2. Selección periodo futuro (ventana 30 años centrada)
3. Cálculo diferencia futuro-histórico
4. Test estadístico (Mann-Whitney U) por punto de grilla
5. Guardado: NetCDF (cambios) + numpy (p-valores)
```

#### **FLUJO 3: Múltiples modelos → Ensamble**
```
1. Agrupación por variable/agregación/escenario
2. Ejecución: cdo ensmean modelo1.nc modelo2.nc ... ensemble.nc
3. Cálculo cambios y significancia sobre ensamble
4. Guardado estructura similar a modelos individuales
```

#### **FLUJO 4: Modelos → Time of Emergence**
```
PASO 1: Ajuste polinomial (grado 4) por modelo
PASO 2: Separación tendencia/residuos
PASO 3: Cálculo variabilidad interna (ventanas móviles)
PASO 4: Relación señal/ruido = tendencia / √(variabilidad)
PASO 5: Detección cuando S/N > umbral (1°C o ±1%)
```

---

### **🔗 CONEXIONES ENTRE MÓDULOS**

#### **Preprocesamiento → Dashboard**
```
01_preproc_01_dep.py → series_temporales.py
    (CSV por depto)     (Carga para gráficos)

01_preproc_02_cambio.py → data_loader_cambios.py
    (Cambios por modelo)  (Carga para mapas)

01_preproc_03_ens_cdo.py → data_loader_promedio.py
    (Ensamble)            (Carga para gráficos promedio)

01_preproc_04_toe.py → data_loader_promedio.py
    (TOE)                 (Carga para mapa TOE)
```

#### **Data Loaders → Generadores Gráficos**
```
data_loader_cambios.py → graficos_cambios.py
    (cargar_cambios)       (generar_mapa_multimodelo)

data_loader_promedio.py → graficos_promedio.py
    (cargar_cambios_ensemble) (generar_mapa_promedio)

series_temporales.py → graficos_series.py
    (cargar_series_modelos)   (crear_grafico_series)
```


### 🗃️ Estructura de NetCDF

#### **Entradas (`data/modelos_agre/`)**
```
{tasmin,tasmax,pr}_{ANUAL,DEF,MAM,JJA,SON}_{modelo}_{ssp245,ssp585}.nc
```

**Ejemplo**: `tasmin_ANUAL_ecmwf-51_ssp245.nc`

**Estructura interna NetCDF**:
```python
Dimensions:  (time: 85, lat: 40, lon: 83)  # 1981-2065, resolución ~0.5°
Variables:
    tasmin (time, lat, lon)  # Temperatura mínima en °C
    pr (time, lat, lon)      # Precipitación en mm/día
Coordinates:
    time: datetime64[ns]     # 1981-01-01 a 2065-12-31
    lat: float64            # -19.0 a -0.5
    lon: float64            # -82.0 a -0.5
```

#### **Salidas Generadas**

##### `data/procesados/` (Series departamentales)
```csv
# tasmin_ANUAL_ecmwf-51_ssp245.csv
Fecha,AMAZONAS,ANCASH,APURIMAC,AR...
1981-01-01,15.2,12.4,10.8,...
1982-01-01,15.3,12.5,10.9,...
...
```

##### `data/mod_cambios/` (Cambios por modelo)
```python
# ecmwf-51_tasmin_ANUAL_ssp245_1981-2010_centro-2050.nc
Dimensions:  (lat: 40, lon: 83)
Variables:
    delta_tasmin (lat, lon)  # Cambio en °C
Attributes:
    center_year: 2050
    reference: 1981-2010
    agregacion: ANUAL
    ssp: ssp245
```

##### `data/mod_significancia/` (Significancia estadística)
```python
# ecmwf-51_tasmin_ANUAL_ssp245_1981-2010_centro-2050.npy
Shape: (40, 83)  # lat × lon
Dtype: float64
Valores: p-values (0.0 a 1.0)
```

##### `data/ensamble/` (Resultados multimodelo)
```
ensamble/
├── datos/                          # Ensambles brutos
│   └── ensemble_{var}_{agg}_{ssp}.nc
├── cambios/                        # Cambios del ensamble
│   └── ensemble_{var}_{agg}_{ssp}_{base}_centro-{cy}.nc
└── significancia/                  # Significancia del ensamble
    └── ensemble_{var}_{agg}_{ssp}_{base}_centro-{cy}.npy
```

##### `data/mod_toe/` (Time of Emergence)
```python
# ensemble_tasmin_ANUAL_toe.nc
Dimensions:  (lat: 40, lon: 83)
Variables:
    TOE_1 (lat, lon)  # Emergencia con umbral 1°C (temperatura) o -1% (precipitación)
    TOE_2 (lat, lon)  # Emergencia con umbral 2°C (temperatura) o +1% (precipitación)
```

### ⚙️ Configuración Técnica Avanzada

#### **Parámetros Clave por Módulo**

| Módulo | Parámetro | Valor | Descripción |
|--------|-----------|-------|-------------|
| `01_preproc_01_dep.py` | `reso` | 0.5 | Resolución de interpolación (°) |
| `01_preproc_02_cambio.py` | `FUT_WINDOW` | 30 | Ventana temporal para futuro (años) |
| `01_preproc_02_cambio.py` | `CENTER_YEARS` | [2030, 2035, 2040, 2045, 2050] | Años centro para análisis |
| `graficos_cambios.py` | `levels` (pr) | np.arange(-100, 110, 10) | Contornos para precipitación |
| `graficos_cambios.py` | `levels` (temp) | np.arange(-4, 4.5, 0.5) | Contornos para temperatura |
| `aux_calcular_toe.py` | `deg` (polyfit) | 4 | Grado del polinomio de ajuste |
| `aux_calcular_toe.py` | `window` (rolling) | 10 | Ventana móvil para suavizado (años) |

#### **Algoritmos Estadísticos Implementados**

1. **Test de Significancia** (`aux_cambios_significancia.py`):
   ```python
   # Prueba t de Student para muestras independientes
   t_stat, p_val = stats.ttest_ind(hist_series, fut_series, 
                                    equal_var=False, nan_policy='omit')
   ```

2. **Cálculo de Cambios**:
   - **Temperatura**: ΔT = T_futuro - T_histórico (en °C)
   - **Precipitación**: ΔP% = ((P_futuro - P_histórico) / P_histórico) × 100

3. **Time of Emergence** (5-part algorithm):
   ```
   Input: Series temporales multimodelo
   Step 1: Ajuste polinomial (grado 4) → Tendencia + Residuos
   Step 2: Variabilidad interna = f(residuos, ventana móvil)
   Step 3: Relación señal/ruido = Tendencia / √(Variabilidad)
   Step 4: Detección: S/N > umbral durante N años consecutivos
   Step 5: TOE = Primer año de detección sostenida
   ```

#### **Gestión de Memoria y Rendimiento**

| Técnica | Módulo | Beneficio |
|---------|--------|-----------|
| **Carga** | xarray.open_dataset() | Reduce uso de memoria inicial |
| **Verificación de existencia** | Todos los preprocesadores | Evita reprocesamiento |
| **Cache en sesión** | 00_dashboard.py (series_dict) | Acelera navegación |
| **Procesamiento por chunks** | Implícito en xarray | Manejo de grandes datasets |
| **Formato CSV para series** | 01_preproc_01_dep.py | Acceso rápido a datos frecuentes |

### 📊 Validación y Control de Calidad

#### **Verificaciones Implementadas**

1. **Consistencia dimensional**:
   ```python
   # En aux_cambios_significancia.py
   if hist_mean.shape != fut_mean.shape:
       fut_mean = fut_mean.reindex_like(hist_mean)
   ```

2. **Validación de datos faltantes**:
   ```python
   # Remoción segura de NaN antes de cálculos
   hist_series = hist_series[~np.isnan(hist_series)]
   fut_series = fut_series[~np.isnan(fut_series)]
   ```

3. **Umbrales de calidad**:
   - Mínimo 2 años de datos para tests estadísticos
   - Valores infinitos convertidos a NaN
   - Coordenadas fuera de Perú filtradas implícitamente

#### **Mensajes de Error Informativos**

| Error | Módulo | Mensaje | Acción recomendada |
|-------|--------|---------|-------------------|
| Archivo no encontrado | data_loader_cambios.py | "no existe {ruta}" | Verificar preprocesamiento |
| Dimensión temporal faltante | aux_cambios_significancia.py | "No se encontró dimensión temporal" | Revisar formato NetCDF |
| CDO no disponible | 01_preproc_03_ens_cdo.py | "✗ ERROR: CDO no está instalado" | `conda install -c conda-forge cdo` |
| Shapefile faltante | graficos_cambios.py | "Error cargando shapefile" | Verificar `data/geo/peru32.geojson` |

### 🔄 Flujos de Trabajo Recomendados

#### **Para Nuevos Datos de Modelos**
```bash
# 1. Colocar nuevos NetCDF en data/modelos_agre/
# 2. Ejecutar preprocesamiento secuencial
python 01_preproc_01_dep.py      # ~10 min para 10 modelos
python 01_preproc_02_cambio.py   # ~15 min para 100 combinaciones
python 01_preproc_03_ens_cdo.py  # ~5 min (si CDO disponible)
python 01_preproc_04_toe.py      # ~8 min por variable

# 3. Verificar salidas
ls -lh data/procesados/*.csv | wc -l
ls -lh data/mod_cambios/*.nc | wc -l
ls -lh data/ensamble/cambios/*.nc
```

#### **Para Desarrollo de Nuevas Funcionalidades**
```python
# Patrón recomendado para nuevos módulos:
# 1. Ubicar en src/ según categoría
# 2. Importar en 00_dashboard.py si es necesario
# 3. Usar dashboard_utils.py para funciones comunes
# 4. Seguir convenciones de nombres existentes

# Ejemplo: Nuevo tipo de gráfico
# src/graficos_nuevos.py → importado en 00_dashboard.py
# Usar st.session_state para manejo de estado # IMPORTANTE!
```

### 🚨 Consideraciones Críticas

Se recomienda crear el ambiente desde cero para evitar conflictos de binarios geoespaciales:

```bash
# 1. Crear entorno limpio
conda env create -f environment.yml
conda activate e7-cc
# 2. Ejecutar dashboard
streamlit run 00_dashboard.py
```

#### **Requisitos Específicos**
1. **CDO**: Obligatorio para ensambles (`01_preproc_03_ens_cdo.py`)
   ```bash
   conda install -c conda-forge cdo
   ```

2. **Memoria RAM**: 
   - Mínimo: 8 GB para procesamiento
   - Recomendado: 16+ GB para múltiples modelos simultáneos


#### **Limitaciones Conocidas**
1. **Periodo histórico**: Fijo a 1981-2010 o 1991-2020 (no configurable desde dashboard)
2. **Modelos soportados**: Requieren formato específico de nombres
3. **Escenarios**: Solo SSP245 y SSP585 implementados completamente

#### **Extensiones Futuras**
1. **Más escenarios**: SSP126, SSP370, SSP434, SSP460
2. **Indicadores derivados**: Índices de extremos, días secos/consecutivos
3. **Análisis de incertidumbre**: Intervalos de confianza, percentiles
4. **Exportación avanzada**: PDF, PNG de alta resolución, datos tabulares

---

## Soporte y Mantenimiento

### **Equipo Responsable**
- **Locación SMN** - JAPQ
- **Contacto**: [japaredesq@gmail.com]
- **Repositorio**: [https://github.com/Japq91/e7_dashboard]

### **Actualización**
1. **Semestral**: Revisión de algoritmos estadísticos
2. **Anual**: Incorporación de nuevos modelos CMIP6

### **Registro de Cambios**
| Versión | Fecha | Cambios Principales |
|---------|-------|---------------------|
| 1.0 | Dic 2025 | Versión inicial con procesamiento básico |
| _._ | Mon 202# | Modificación 1, 2, 3, 4, 5, 6, etc. |


---
### 📚 Referencias
#### R. Bibliografía

1.  **Time of Emergence:** Hawkins, E., & Sutton, R. (2012). *Time of emergence of climate signals*. Geophysical Research Letters.
2.  **CMIP6:** Eyring, V., et al. (2016). *Overview of the Coupled Model Intercomparison Project Phase 6 (CMIP6)*.
3.  **CDO:** Schulzweida, U. (2019). *CDO User Guide*. Max Planck Institute for Meteorology. [CDO (Climate Data Operators)](https://code.mpimet.mpg.de/projects/cdo) 

#### R. Técnicas

1. **CDO (Climate Data Operators)**: https://code.mpimet.mpg.de/projects/cdo
2. **xarray**: https://xarray.pydata.org/ - Manejo de datos multidimensionales
3. **CMIP6 (Coupled Model Intercomparison Project Phase 6)**: https://www.wcrp-climate.org/wgcm-cmip/wgcm-cmip6
4. **Plotly**: https://plotly.com/python/ - Visualizaciones interactivas
5. **Streamlit**: https://streamlit.io/ - Framework para aplicaciones de datos
---

*Documentación actualizada: Diciembre 2025*  
*Sistema desarrollado por la Subdirección de Modelamiento Numérico (SMN) - SENAMHI*  
*© Servicio Nacional de Meteorología e Hidrología del Perú*