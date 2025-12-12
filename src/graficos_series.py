# src/graficos_series.py - Versión adaptada

import plotly.graph_objects as go

def crear_grafico_series(df, departamento, variable):
    """Crea gráfico con series de modelos y promedio"""
    fig = go.Figure()

    # Nombres completos para variables (actualizado para nuevas variables)
    nombres_var = {
        'tasmin': 'Temperatura mínima promedio',
        'tasmax': 'Temperatura máxima promedio',
        'pr': 'Precipitación'
    }

    # Colores para modelos
    colores = ['#1f77b4', '#ff7f0e', '#2ca02c', '#d62728', '#9467bd']

    # Trazar cada modelo (excluyendo PROMEDIO si existe)
    modelos = [col for col in df.columns if col != 'PROMEDIO']

    for i, modelo in enumerate(modelos):
        fig.add_trace(go.Scatter(
            x=df.index,
            y=df[modelo],
            mode='lines',
            name=modelo,
            line=dict(color=colores[i % len(colores)], width=1.2),
            opacity=0.6,
            hoverinfo='x+y'
        ))

    # Trazar promedio (línea más gruesa) si existe
    if 'PROMEDIO' in df.columns:
        fig.add_trace(go.Scatter(
            x=df.index,
            y=df['PROMEDIO'],
            mode='lines',
            name=f'PROMEDIO ({len(modelos)} modelos)',
            line=dict(color='black', width=2.5),
            opacity=1.0,
            hoverinfo='x+y'
        ))

    # Configurar
    unidades = {'pr': 'mm', 'tasmin': '°C', 'tasmax': '°C'}
    unidad = unidades.get(variable, '')

    fig.update_layout(
        title=f"{departamento} - {nombres_var.get(variable, variable)}",
        xaxis_title="Fecha",
        yaxis_title=f"[ {unidad} ]",
        hovermode='x unified',
        height=400,
        showlegend=True,
        legend=dict(
            yanchor="top",
            xanchor="left",
        )
    )

    return fig
