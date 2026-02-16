import streamlit as st
import plotly.graph_objects as go
import plotly.express as px
from datetime import datetime

# --- CONFIGURACIÓN INICIAL ---
st.set_page_config(
    page_title="PORTAWARE Financiero", 
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Paleta de colores premium
COLORES = {
    'primary': '#1F3A5F',
    'secondary': '#4FD1C5',
    'accent': '#2D5B8F',
    'success': '#48BB78',
    'warning': '#ED8936',
    'error': '#F56565',
    'dark': '#2D3748',
    'light': '#F7FAFC',
    'highlight': '#FFD700'
}

# Estilos CSS personalizados
st.markdown(f"""
<style>
    .main .block-container {{
        padding-top: 2rem;
    }}
    .metric-card {{
        background: linear-gradient(135deg, {COLORES['primary']}, {COLORES['accent']});
        padding: 1.5rem;
        border-radius: 15px;
        color: white;
        box-shadow: 0 4px 20px rgba(0,0,0,0.1);
    }}
    .control-panel {{
        background-color: {COLORES['light']};
        padding: 1.5rem;
        border-radius: 15px;
        border-left: 4px solid {COLORES['secondary']};
    }}
    .section-title {{
        color: {COLORES['primary']};
        font-weight: 600;
        margin-bottom: 1rem;
    }}
    .highlight-row {{
        background-color: #E8F5E8 !important;
        font-weight: bold !important;
    }}
</style>
""", unsafe_allow_html=True)

# --- FUNCIONES DE CÁLCULO ---
def calcular_financieros(ventas_netas, pct_costo, nomina, pct_comisiones, pct_fletes, rentas, otros_gastos, pct_gastos_financieros):
    """Calcula todos los valores financieros"""
    # CORRECCIÓN: Calcular costo correctamente y restarlo de ventas netas
    costo_ventas = ventas_netas * (pct_costo / 100)
    margen_bruto = ventas_netas - costo_ventas  # ¡Aquí está la resta!
    
    comisiones = ventas_netas * (pct_comisiones / 100)
    fletes = ventas_netas * (pct_fletes / 100)
    gasto_total = nomina + comisiones + fletes + rentas + otros_gastos
    ebitda_operativo = margen_bruto - gasto_total
    gastos_financieros = ventas_netas * (pct_gastos_financieros / 100)
    ebitda = ebitda_operativo - gastos_financieros
    
    margen_bruto_pct = (margen_bruto / ventas_netas) * 100 if ventas_netas != 0 else 0
    margen_ebitda_pct = (ebitda / ventas_netas) * 100 if ventas_netas != 0 else 0
    
    return {
        'costo_ventas': costo_ventas,  # Nombre más descriptivo
        'margen_bruto': margen_bruto,
        'comisiones': comisiones,
        'fletes': fletes,
        'gasto_total': gasto_total,
        'ebitda_operativo': ebitda_operativo,
        'gastos_financieros': gastos_financieros,
        'ebitda': ebitda,
        'margen_bruto_pct': margen_bruto_pct,
        'margen_ebitda_pct': margen_ebitda_pct
    }

def aplicar_escenario(tipo):
    """Aplica escenarios predefinidos"""
    if tipo == 'optimista':
        st.session_state.ventas_netas = 189878959 * 1.15
        st.session_state.pct_costo = 45.0
        st.session_state.pct_fletes = 5.5
        st.session_state.pct_gastos_financieros = 0.8
    elif tipo == 'conservador':
        st.session_state.ventas_netas = 189878959 * 0.95
        st.session_state.pct_costo = 48.0
        st.session_state.pct_fletes = 6.5
    elif tipo == 'reset':
        st.session_state.ventas_netas = 189878959
        st.session_state.pct_costo = 47.0
        st.session_state.nomina = 25800000
        st.session_state.pct_comisiones = 3.0
        st.session_state.pct_fletes = 6.0
        st.session_state.rentas = 6711000
        st.session_state.otros_gastos = 5446936
        st.session_state.pct_gastos_financieros = 1.0

# --- INICIALIZAR SESSION STATE ---
valores_por_defecto = {
    'ventas_netas': 189878959,
    'pct_costo': 47.0,
    'nomina': 25800000,
    'pct_comisiones': 3.0,
    'pct_fletes': 6.0,
    'rentas': 6711000,
    'otros_gastos': 5446936,
    'pct_gastos_financieros': 1.0
}

for key, value in valores_por_defecto.items():
    if key not in st.session_state:
        st.session_state[key] = value

# --- CALCULAR VALORES ACTUALES ---
calculos = calcular_financieros(
    float(st.session_state.ventas_netas),
    float(st.session_state.pct_costo),
    float(st.session_state.nomina),
    float(st.session_state.pct_comisiones),
    float(st.session_state.pct_fletes),
    float(st.session_state.rentas),
    float(st.session_state.otros_gastos),
    float(st.session_state.pct_gastos_financieros)
)

# --- INTERFAZ DE USUARIO ---
# Header Premium
col_logo, col_title, col_actions = st.columns([1, 2, 1])
with col_logo:
    st.markdown("### 🏢 PORTAWARE")
with col_title:
    st.markdown("<h1 style='text-align: center; color: #1F3A5F;'>Análisis Financiero</h1>", unsafe_allow_html=True)
with col_actions:
    st.markdown("**💎 Professional Edition**")

st.markdown("---")

# Métricas principales con diseño premium
st.markdown("<div class='section-title'>PRINCIPALES INDICADORES</div>", unsafe_allow_html=True)

col1, col2, col3 = st.columns(3)

with col1:
    st.markdown(f"""
    <div class='metric-card'>
        <div style='font-size: 0.9rem; opacity: 0.9;'>VENTAS NETAS</div>
        <div style='font-size: 2rem; font-weight: bold;'>${float(st.session_state.ventas_netas)/1_000_000:.1f}M</div>
        <div style='font-size: 0.8rem; opacity: 0.8;'>Ingresos totales</div>
    </div>
    """, unsafe_allow_html=True)

with col2:
    st.markdown(f"""
    <div class='metric-card'>
        <div style='font-size: 0.9rem; opacity: 0.9;'>MARGEN BRUTO</div>
        <div style='font-size: 2rem; font-weight: bold;'>${calculos['margen_bruto']/1_000_000:.1f}M</div>
        <div style='font-size: 1rem; opacity: 0.9;'>{calculos['margen_bruto_pct']:.1f}% del total</div>
    </div>
    """, unsafe_allow_html=True)

with col3:
    st.markdown(f"""
    <div class='metric-card'>
        <div style='font-size: 0.9rem; opacity: 0.9;'>EBITDA</div>
        <div style='font-size: 2rem; font-weight: bold;'>${calculos['ebitda']/1_000_000:.1f}M</div>
        <div style='font-size: 1rem; opacity: 0.9;'>{calculos['margen_ebitda_pct']:.1f}% del total</div>
    </div>
    """, unsafe_allow_html=True)

st.markdown("---")

# Controles de escenario
st.markdown("<div class='section-title'>ESCENARIOS ESTRATÉGICOS</div>", unsafe_allow_html=True)

sc1, sc2, sc3, sc4 = st.columns(4)
with sc1:
    if st.button('🚀 **Optimista**', use_container_width=True, type="primary"):
        aplicar_escenario('optimista')
        st.rerun()
with sc2:
    if st.button('🛡️ **Conservador**', use_container_width=True):
        aplicar_escenario('conservador')
        st.rerun()
with sc3:
    if st.button('⚡ **Valores Base**', use_container_width=True):
        aplicar_escenario('reset')
        st.rerun()
with sc4:
    st.info("💡 Ajusta los controles para simular")

# Layout principal
col_controles, col_visuales = st.columns([1, 2])

with col_controles:
    st.markdown("<div class='section-title'>PANEL DE CONTROL</div>", unsafe_allow_html=True)
    
    with st.container():
        st.markdown("<div class='control-panel'>", unsafe_allow_html=True)
        
        st.markdown("##### 💰 Ingresos")
        st.session_state.ventas_netas = st.number_input(
            "Ventas Netas",
            min_value=0.0,
            value=float(st.session_state.ventas_netas),
            step=1000000.0,
            format="%f",
            help="Ingresos totales de la empresa"
        )
        st.caption(f"**${float(st.session_state.ventas_netas):,.0f}**")
        
        st.markdown("---")
        
        st.markdown("##### 🏭 Estructura de Costos")
        st.session_state.pct_costo = st.slider(
            "Costo de Ventas (%)",
            min_value=30.0,
            max_value=70.0,
            value=float(st.session_state.pct_costo),
            step=0.5,
            help="Porcentaje del costo sobre ventas netas"
        )
        
        # Mostrar desglose del cálculo del margen bruto
        st.markdown(f"""
        <div style='background-color: #f8f9fa; padding: 1rem; border-radius: 8px; margin: 1rem 0;'>
            <p style='margin: 0.2rem 0; font-size: 0.9rem;'><strong>Desglose del Margen Bruto:</strong></p>
            <p style='margin: 0.2rem 0; font-size: 0.85rem;'>Ventas Netas: <strong>${float(st.session_state.ventas_netas):,.0f}</strong></p>
            <p style='margin: 0.2rem 0; font-size: 0.85rem;'>Menos Costo de Ventas: <strong>${calculos['costo_ventas']:,.0f}</strong></p>
            <p style='margin: 0.2rem 0; font-size: 0.85rem;'><strong>Margen Bruto: ${calculos['margen_bruto']:,.0f}</strong></p>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown("---")
        
        st.markdown("##### 💸 Gastos Operativos")
        
        st.session_state.nomina = st.number_input(
            "Nómina",
            min_value=0.0,
            value=float(st.session_state.nomina),
            step=100000.0,
            format="%f"
        )
        
        st.session_state.pct_comisiones = st.slider(
            "Comisiones (%)",
            min_value=0.0,
            max_value=10.0,
            value=float(st.session_state.pct_comisiones),
            step=0.25
        )
        
        st.session_state.pct_fletes = st.slider(
            "Fletes (%)",
            min_value=0.0,
            max_value=15.0,
            value=float(st.session_state.pct_fletes),
            step=0.25
        )
        
        st.session_state.rentas = st.number_input(
            "Rentas",
            min_value=0.0,
            value=float(st.session_state.rentas),
            step=100000.0,
            format="%f"
        )
        
        st.session_state.otros_gastos = st.number_input(
            "Otros Gastos",
            min_value=0.0,
            value=float(st.session_state.otros_gastos),
            step=100000.0,
            format="%f"
        )
        
        st.markdown(f"**Total Gastos Operativos: ${calculos['gasto_total']:,.0f}**")
        
        st.markdown("---")
        
        st.markdown("##### 🏦 Gastos Financieros")
        st.session_state.pct_gastos_financieros = st.slider(
            "Gastos Financieros (%)",
            min_value=0.0,
            max_value=5.0,
            value=float(st.session_state.pct_gastos_financieros),
            step=0.1
        )
        
        st.markdown("</div>", unsafe_allow_html=True)

with col_visuales:
    # Gráfico de Cascada Corregido
    st.markdown("<div class='section-title'>ANÁLISIS DE RENTABILIDAD</div>", unsafe_allow_html=True)
    
    # Datos para el gráfico de cascada
    categories = ['Ventas Netas', 'Costo de Ventas', 'Margen Bruto', 'Gastos Operativos', 'EBITDA Operativo', 'Gastos Financieros', 'EBITDA Final']
    values = [
        float(st.session_state.ventas_netas),
        -calculos['costo_ventas'],  # Usar el nombre correcto
        calculos['margen_bruto'],
        -calculos['gasto_total'],
        calculos['ebitda_operativo'],
        -calculos['gastos_financieros'],
        calculos['ebitda']
    ]
    
    measures = ['absolute', 'relative', 'total', 'relative', 'total', 'relative', 'total']
    
    fig_waterfall = go.Figure(go.Waterfall(
        name="",
        orientation="v",
        measure=measures,
        x=categories,
        y=values,
        text=[f"${x/1_000_000:.1f}M" for x in values],
        textposition="outside",
        connector={"line":{"color":"rgb(63, 63, 63)"}},
        increasing={"marker":{"color":COLORES['success']}},
        decreasing={"marker":{"color":COLORES['error']}},
        totals={"marker":{"color":COLORES['secondary']}}
    ))
    
    fig_waterfall.update_layout(
        showlegend=False,
        height=400,
        margin=dict(l=50, r=50, t=50, b=100),
        xaxis_tickangle=-45,
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        font=dict(color=COLORES['dark'])
    )
    
    st.plotly_chart(fig_waterfall, use_container_width=True)
    
    # Tabla de resultados mejorada
    st.markdown("<div class='section-title'>DETALLE FINANCIERO</div>", unsafe_allow_html=True)
    
    # Crear tabla de resultados con filas destacadas
    datos_tabla = [
        ["Ventas Netas", f"${float(st.session_state.ventas_netas):,.0f}", "100.0%"],
        ["Costo de Ventas", f"${calculos['costo_ventas']:,.0f}", f"{float(st.session_state.pct_costo):.1f}%"],
        ["MARGEN BRUTO", f"${calculos['margen_bruto']:,.0f}", f"<b>{calculos['margen_bruto_pct']:.1f}%</b>"],
        ["", "", ""],
        ["GASTOS OPERATIVOS", "", ""],
        ["Nómina", f"${float(st.session_state.nomina):,.0f}", f"{(float(st.session_state.nomina)/float(st.session_state.ventas_netas))*100:.1f}%"],
        ["Comisiones", f"${calculos['comisiones']:,.0f}", f"{float(st.session_state.pct_comisiones):.1f}%"],
        ["Fletes", f"${calculos['fletes']:,.0f}", f"{float(st.session_state.pct_fletes):.1f}%"],
        ["Rentas", f"${float(st.session_state.rentas):,.0f}", f"{(float(st.session_state.rentas)/float(st.session_state.ventas_netas))*100:.1f}%"],
        ["Otros Gastos", f"${float(st.session_state.otros_gastos):,.0f}", f"{(float(st.session_state.otros_gastos)/float(st.session_state.ventas_netas))*100:.1f}%"],
        ["TOTAL GASTOS OPERATIVOS", f"${calculos['gasto_total']:,.0f}", f"<b>{(calculos['gasto_total']/float(st.session_state.ventas_netas))*100:.1f}%</b>"],
        ["", "", ""],
        ["EBITDA OPERATIVO", f"${calculos['ebitda_operativo']:,.0f}", f"<b>{(calculos['ebitda_operativo']/float(st.session_state.ventas_netas))*100:.1f}%</b>"],
        ["Gastos Financieros", f"${calculos['gastos_financieros']:,.0f}", f"{float(st.session_state.pct_gastos_financieros):.1f}%"],
        ["EBITDA FINAL", f"${calculos['ebitda']:,.0f}", f"<b>{calculos['margen_ebitda_pct']:.1f}%</b>"]
    ]
    
    # Definir colores de fondo para filas destacadas
    fill_colors = []
    for i, fila in enumerate(datos_tabla):
        if any(keyword in fila[0] for keyword in ['MARGEN BRUTO', 'TOTAL GASTOS OPERATIVOS', 'EBITDA OPERATIVO', 'EBITDA FINAL']):
            fill_colors.append(['#E8F5E8', '#E8F5E8', '#E8F5E8'])  # Verde claro para destacar
        else:
            fill_colors.append(['white', '#F8FAFC', '#F8FAFC'])
    
    # Crear tabla con diseño premium y filas destacadas
    fig_tabla = go.Figure(data=[go.Table(
        columnwidth=[2, 1.5, 1],
        header=dict(
            values=['<b>CONCEPTO</b>', '<b>MONTO</b>', '<b>%</b>'],
            fill_color=COLORES['primary'],
            align=['left', 'right', 'right'],
            font=dict(color='white', size=13, family="Arial", weight="bold")
        ),
        cells=dict(
            values=[[fila[0] for fila in datos_tabla], 
                   [fila[1] for fila in datos_tabla], 
                   [fila[2] for fila in datos_tabla]],
            align=['left', 'right', 'right'],
            fill_color=[[fila[i] for fila in fill_colors] for i in range(3)],
            font=dict(size=12, family="Arial"),
            height=30
        )
    )])
    
    fig_tabla.update_layout(
        height=500,
        margin=dict(l=0, r=0, t=0, b=0)
    )
    
    st.plotly_chart(fig_tabla, use_container_width=True)

# Nueva sección combinada: Composición de Gastos + Indicadores Clave
st.markdown("<div class='section-title'>ANÁLISIS DE EFICIENCIA OPERATIVA</div>", unsafe_allow_html=True)

col_analisis1, col_analisis2 = st.columns([2, 1])

with col_analisis1:
    # Gráfico de composición de gastos operativos
    st.markdown("##### 🥧 Composición de Gastos Operativos")
    
    datos_gastos = [
        dict(name='Nómina', value=float(st.session_state.nomina)),
        dict(name='Comisiones', value=calculos['comisiones']),
        dict(name='Fletes', value=calculos['fletes']),
        dict(name='Rentas', value=float(st.session_state.rentas)),
        dict(name='Otros', value=float(st.session_state.otros_gastos))
    ]
    
    fig_pie = go.Figure(data=[go.Pie(
        labels=[d['name'] for d in datos_gastos],
        values=[d['value'] for d in datos_gastos],
        hole=0.5,
        marker_colors=[COLORES['primary'], COLORES['secondary'], COLORES['accent'], 
                      COLORES['success'], COLORES['warning']],
        textinfo='percent+label',
        textposition='inside',
        insidetextorientation='radial',
        hovertemplate='<b>%{label}</b><br>Monto: $%{value:,.0f}<br>Porcentaje: %{percent}<extra></extra>'
    )])
    
    fig_pie.update_layout(
        height=350,
        margin=dict(l=20, r=20, t=40, b=20),
        showlegend=False,
        font=dict(size=11, family="Arial")
    )
    
    st.plotly_chart(fig_pie, use_container_width=True)

with col_analisis2:
    # Cálculo de indicadores financieros reales
    margen_operativo = (calculos['ebitda_operativo'] / float(st.session_state.ventas_netas)) * 100
    cobertura_intereses = calculos['ebitda'] / calculos['gastos_financieros'] if calculos['gastos_financieros'] > 0 else 0
    eficiencia_operativa = (calculos['ebitda_operativo'] / calculos['margen_bruto']) * 100 if calculos['margen_bruto'] > 0 else 0
    
    
# Footer premium
st.markdown("---")
st.markdown(f"""
<div style='text-align: center; color: #718096; font-size: 0.9rem;'>
    PORTAWARE Financiero • Última actualización: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} • 
    <span style='color: #4FD1C5;'>Professional Edition</span>
</div>
""", unsafe_allow_html=True)








