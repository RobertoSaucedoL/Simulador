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

# Estilos CSS mínimos y seguros
st.markdown(f"""
<style>
    .main .block-container {{
        padding-top: 2rem;
    }}
    .stMetric {{
        background: linear-gradient(135deg, {COLORES['primary']}, {COLORES['accent']});
        padding: 1rem;
        border-radius: 10px;
        color: white;
    }}
    .stMetric label {{
        color: white !important;
    }}
    .stMetric [data-testid="stMetricValue"] {{
        color: white !important;
    }}
</style>
""", unsafe_allow_html=True)

# --- FUNCIONES DE CÁLCULO ---
def calcular_financieros(ventas_netas, pct_costo, nomina, pct_comisiones, pct_fletes, rentas, otros_gastos, pct_gastos_financieros):
    """Calcula todos los valores financieros"""
    costo_ventas = ventas_netas * (pct_costo / 100)
    margen_bruto = ventas_netas - costo_ventas
    
    comisiones = ventas_netas * (pct_comisiones / 100)
    fletes = ventas_netas * (pct_fletes / 100)
    gasto_total = nomina + comisiones + fletes + rentas + otros_gastos
    ebitda_operativo = margen_bruto - gasto_total
    gastos_financieros = ventas_netas * (pct_gastos_financieros / 100)
    ebitda = ebitda_operativo - gastos_financieros
    
    margen_bruto_pct = (margen_bruto / ventas_netas) * 100 if ventas_netas != 0 else 0
    margen_ebitda_pct = (ebitda / ventas_netas) * 100 if ventas_netas != 0 else 0
    
    return {
        'costo_ventas': costo_ventas,
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
# Header
st.title("🏢 PORTAWARE - Análisis Financiero")
st.markdown("---")

# Métricas principales
st.subheader("📊 PRINCIPALES INDICADORES")

col1, col2, col3 = st.columns(3)

with col1:
    st.metric(
        label="VENTAS NETAS",
        value=f"${float(st.session_state.ventas_netas)/1_000_000:.1f}M",
        delta="Ingresos totales"
    )

with col2:
    st.metric(
        label="MARGEN BRUTO",
        value=f"${calculos['margen_bruto']/1_000_000:.1f}M",
        delta=f"{calculos['margen_bruto_pct']:.1f}%"
    )

with col3:
    st.metric(
        label="EBITDA",
        value=f"${calculos['ebitda']/1_000_000:.1f}M",
        delta=f"{calculos['margen_ebitda_pct']:.1f}%"
    )

st.markdown("---")

# Controles de escenario
st.subheader("🎯 ESCENARIOS ESTRATÉGICOS")

sc1, sc2, sc3, sc4 = st.columns(4)
with sc1:
    if st.button('🚀 Optimista', use_container_width=True, type="primary"):
        aplicar_escenario('optimista')
        st.rerun()
with sc2:
    if st.button('🛡️ Conservador', use_container_width=True):
        aplicar_escenario('conservador')
        st.rerun()
with sc3:
    if st.button('⚡ Valores Base', use_container_width=True):
        aplicar_escenario('reset')
        st.rerun()
with sc4:
    st.info("💡 Ajusta los controles")

st.markdown("---")

# Layout principal
col_controles, col_visuales = st.columns([1, 2])

with col_controles:
    st.subheader("⚙️ PANEL DE CONTROL")
    
    st.markdown("#### 💰 Ingresos")
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
    
    st.markdown("#### 🏭 Estructura de Costos")
    st.session_state.pct_costo = st.slider(
        "Costo de Ventas (%)",
        min_value=30.0,
        max_value=70.0,
        value=float(st.session_state.pct_costo),
        step=0.5,
        help="Porcentaje del costo sobre ventas netas"
    )
    
    # Desglose simple
    st.info(f"""
    **Desglose del Margen Bruto:**
    - Ventas Netas: ${float(st.session_state.ventas_netas):,.0f}
    - Costo de Ventas: ${calculos['costo_ventas']:,.0f}
    - **Margen Bruto: ${calculos['margen_bruto']:,.0f}**
    """)
    
    st.markdown("---")
    
    st.markdown("#### 💸 Gastos Operativos")
    
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
    
    st.success(f"**Total Gastos: ${calculos['gasto_total']:,.0f}**")
    
    st.markdown("---")
    
    st.markdown("#### 🏦 Gastos Financieros")
    st.session_state.pct_gastos_financieros = st.slider(
        "Gastos Financieros (%)",
        min_value=0.0,
        max_value=5.0,
        value=float(st.session_state.pct_gastos_financieros),
        step=0.1
    )

with col_visuales:
    # Gráfico de Cascada
    st.subheader("📈 ANÁLISIS DE RENTABILIDAD")
    
    categories = ['Ventas Netas', 'Costo de Ventas', 'Margen Bruto', 'Gastos Operativos', 'EBITDA Operativo', 'Gastos Financieros', 'EBITDA Final']
    values = [
        float(st.session_state.ventas_netas),
        -calculos['costo_ventas'],
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
    
    # Tabla de resultados
    st.subheader("📋 DETALLE FINANCIERO")
    
    datos_tabla = [
        ["Ventas Netas", f"${float(st.session_state.ventas_netas):,.0f}", "100.0%"],
        ["Costo de Ventas", f"${calculos['costo_ventas']:,.0f}", f"{float(st.session_state.pct_costo):.1f}%"],
        ["MARGEN BRUTO", f"${calculos['margen_bruto']:,.0f}", f"{calculos['margen_bruto_pct']:.1f}%"],
        ["", "", ""],
        ["GASTOS OPERATIVOS", "", ""],
        ["Nómina", f"${float(st.session_state.nomina):,.0f}", f"{(float(st.session_state.nomina)/float(st.session_state.ventas_netas))*100:.1f}%"],
        ["Comisiones", f"${calculos['comisiones']:,.0f}", f"{float(st.session_state.pct_comisiones):.1f}%"],
        ["Fletes", f"${calculos['fletes']:,.0f}", f"{float(st.session_state.pct_fletes):.1f}%"],
        ["Rentas", f"${float(st.session_state.rentas):,.0f}", f"{(float(st.session_state.rentas)/float(st.session_state.ventas_netas))*100:.1f}%"],
        ["Otros Gastos", f"${float(st.session_state.otros_gastos):,.0f}", f"{(float(st.session_state.otros_gastos)/float(st.session_state.ventas_netas))*100:.1f}%"],
        ["TOTAL GASTOS", f"${calculos['gasto_total']:,.0f}", f"{(calculos['gasto_total']/float(st.session_state.ventas_netas))*100:.1f}%"],
        ["", "", ""],
        ["EBITDA OPERATIVO", f"${calculos['ebitda_operativo']:,.0f}", f"{(calculos['ebitda_operativo']/float(st.session_state.ventas_netas))*100:.1f}%"],
        ["Gastos Financieros", f"${calculos['gastos_financieros']:,.0f}", f"{float(st.session_state.pct_gastos_financieros):.1f}%"],
        ["EBITDA FINAL", f"${calculos['ebitda']:,.0f}", f"{calculos['margen_ebitda_pct']:.1f}%"]
    ]
    
    fill_colors = []
    for fila in datos_tabla:
        if any(keyword in fila[0] for keyword in ['MARGEN BRUTO', 'TOTAL GASTOS', 'EBITDA OPERATIVO', 'EBITDA FINAL']):
            fill_colors.append(['#E8F5E8', '#E8F5E8', '#E8F5E8'])
        else:
            fill_colors.append(['white', '#F8FAFC', '#F8FAFC'])
    
    fig_tabla = go.Figure(data=[go.Table(
        columnwidth=[2, 1.5, 1],
        header=dict(
            values=['<b>CONCEPTO</b>', '<b>MONTO</b>', '<b>%</b>'],
            fill_color=COLORES['primary'],
            align=['left', 'right', 'right'],
            font=dict(color='white', size=13)
        ),
        cells=dict(
            values=[[fila[0] for fila in datos_tabla], 
                   [fila[1] for fila in datos_tabla], 
                   [fila[2] for fila in datos_tabla]],
            align=['left', 'right', 'right'],
            fill_color=[[fila[i] for fila in fill_colors] for i in range(3)],
            font=dict(size=12),
            height=30
        )
    )])
    
    fig_tabla.update_layout(
        height=500,
        margin=dict(l=0, r=0, t=0, b=0)
    )
    
    st.plotly_chart(fig_tabla, use_container_width=True)

# Análisis de Eficiencia
st.markdown("---")
st.subheader("💡 ANÁLISIS DE EFICIENCIA OPERATIVA")

col_analisis1, col_analisis2 = st.columns([2, 1])

with col_analisis1:
    st.markdown("#### 🥧 Composición de Gastos")
    
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
        textposition='inside'
    )])
    
    fig_pie.update_layout(
        height=350,
        margin=dict(l=20, r=20, t=40, b=20),
        showlegend=False
    )
    
    st.plotly_chart(fig_pie, use_container_width=True)

with col_analisis2:
    st.markdown("#### 📊 Indicadores Clave")
    
    margen_operativo = (calculos['ebitda_operativo'] / float(st.session_state.ventas_netas)) * 100
    cobertura = calculos['ebitda'] / calculos['gastos_financieros'] if calculos['gastos_financieros'] > 0 else 0
    eficiencia = (calculos['ebitda_operativo'] / calculos['margen_bruto']) * 100 if calculos['margen_bruto'] > 0 else 0
    
    st.metric("Margen Operativo", f"{margen_operativo:.1f}%")
    st.metric("Cobertura Intereses", f"{cobertura:.1f}x")
    st.metric("Eficiencia Operativa", f"{eficiencia:.1f}%")
    
    if calculos['margen_ebitda_pct'] > 15:
        st.success("🟢 Salud Financiera: Excelente")
    elif calculos['margen_ebitda_pct'] > 10:
        st.warning("🟡 Salud Financiera: Bueno")
    else:
        st.error("🔴 Salud Financiera: Atención")

# Footer
st.markdown("---")
st.caption(f"PORTAWARE Financiero • {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")



