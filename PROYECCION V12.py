import streamlit as st
import plotly.graph_objects as go
from datetime import datetime

# --- CONFIGURACIÓN ---
st.set_page_config(page_title="PORTAWARE Financiero", layout="wide")

# --- FUNCIONES ---
def calcular_financieros(ventas_netas, pct_costo, nomina, pct_comisiones, pct_fletes, rentas, otros_gastos, pct_gastos_financieros):
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

# --- INICIALIZAR SESSION STATE ---
if 'ventas_netas' not in st.session_state:
    st.session_state.ventas_netas = 189878959
if 'pct_costo' not in st.session_state:
    st.session_state.pct_costo = 47.0
if 'nomina' not in st.session_state:
    st.session_state.nomina = 25800000
if 'pct_comisiones' not in st.session_state:
    st.session_state.pct_comisiones = 3.0
if 'pct_fletes' not in st.session_state:
    st.session_state.pct_fletes = 6.0
if 'rentas' not in st.session_state:
    st.session_state.rentas = 6711000
if 'otros_gastos' not in st.session_state:
    st.session_state.otros_gastos = 5446936
if 'pct_gastos_financieros' not in st.session_state:
    st.session_state.pct_gastos_financieros = 1.0

# --- CALCULAR ---
calculos = calcular_financieros(
    st.session_state.ventas_netas,
    st.session_state.pct_costo,
    st.session_state.nomina,
    st.session_state.pct_comisiones,
    st.session_state.pct_fletes,
    st.session_state.rentas,
    st.session_state.otros_gastos,
    st.session_state.pct_gastos_financieros
)

# --- INTERFAZ ---
st.title("🏢 PORTAWARE - Análisis Financiero")

# Métricas principales
col1, col2, col3 = st.columns(3)
col1.metric("Ventas Netas", f"${st.session_state.ventas_netas/1_000_000:.1f}M")
col2.metric("Margen Bruto", f"${calculos['margen_bruto']/1_000_000:.1f}M", f"{calculos['margen_bruto_pct']:.1f}%")
col3.metric("EBITDA", f"${calculos['ebitda']/1_000_000:.1f}M", f"{calculos['margen_ebitda_pct']:.1f}%")

st.divider()

# Botones de escenario
st.write("**Escenarios:**")
c1, c2, c3 = st.columns(3)

if c1.button('🚀 Optimista', use_container_width=True):
    st.session_state.ventas_netas = 189878959 * 1.15
    st.session_state.pct_costo = 45.0
    st.session_state.pct_fletes = 5.5
    st.session_state.pct_gastos_financieros = 0.8

if c2.button('🛡️ Conservador', use_container_width=True):
    st.session_state.ventas_netas = 189878959 * 0.95
    st.session_state.pct_costo = 48.0
    st.session_state.pct_fletes = 6.5

if c3.button('⚡ Reset', use_container_width=True):
    st.session_state.ventas_netas = 189878959
    st.session_state.pct_costo = 47.0
    st.session_state.nomina = 25800000
    st.session_state.pct_comisiones = 3.0
    st.session_state.pct_fletes = 6.0
    st.session_state.rentas = 6711000
    st.session_state.otros_gastos = 5446936
    st.session_state.pct_gastos_financieros = 1.0

st.divider()

# Layout principal
col_left, col_right = st.columns([1, 2])

# CONTROLES
with col_left:
    st.subheader("Panel de Control")
    
    st.write("**Ingresos**")
    ventas = st.number_input("Ventas Netas", min_value=0.0, value=st.session_state.ventas_netas, step=1000000.0)
    st.session_state.ventas_netas = ventas
    
    st.write("**Costos**")
    costo = st.slider("Costo de Ventas (%)", 30.0, 70.0, st.session_state.pct_costo, 0.5)
    st.session_state.pct_costo = costo
    
    st.write("**Gastos Operativos**")
    nomina = st.number_input("Nómina", min_value=0.0, value=st.session_state.nomina, step=100000.0)
    st.session_state.nomina = nomina
    
    comisiones = st.slider("Comisiones (%)", 0.0, 10.0, st.session_state.pct_comisiones, 0.25)
    st.session_state.pct_comisiones = comisiones
    
    fletes = st.slider("Fletes (%)", 0.0, 15.0, st.session_state.pct_fletes, 0.25)
    st.session_state.pct_fletes = fletes
    
    rentas = st.number_input("Rentas", min_value=0.0, value=st.session_state.rentas, step=100000.0)
    st.session_state.rentas = rentas
    
    otros = st.number_input("Otros Gastos", min_value=0.0, value=st.session_state.otros_gastos, step=100000.0)
    st.session_state.otros_gastos = otros
    
    st.write("**Financieros**")
    gf = st.slider("Gastos Financieros (%)", 0.0, 5.0, st.session_state.pct_gastos_financieros, 0.1)
    st.session_state.pct_gastos_financieros = gf

# VISUALIZACIÓN
with col_right:
    st.subheader("Gráfico de Cascada")
    
    # Gráfico simplificado
    fig = go.Figure(go.Waterfall(
        name="",
        orientation="v",
        measure=['absolute', 'relative', 'total', 'relative', 'total', 'relative', 'total'],
        x=['Ventas', 'Costo', 'Margen Bruto', 'Gastos Op', 'EBITDA Op', 'G. Financ', 'EBITDA'],
        y=[
            st.session_state.ventas_netas,
            -calculos['costo_ventas'],
            calculos['margen_bruto'],
            -calculos['gasto_total'],
            calculos['ebitda_operativo'],
            -calculos['gastos_financieros'],
            calculos['ebitda']
        ],
        text=[f"${x/1_000_000:.1f}M" for x in [
            st.session_state.ventas_netas,
            -calculos['costo_ventas'],
            calculos['margen_bruto'],
            -calculos['gasto_total'],
            calculos['ebitda_operativo'],
            -calculos['gastos_financieros'],
            calculos['ebitda']
        ]],
        textposition="outside"
    ))
    
    fig.update_layout(height=400, showlegend=False)
    st.plotly_chart(fig, use_container_width=True)
    
    # Tabla simple
    st.subheader("Detalle Financiero")
    
    st.write(f"**Ventas Netas:** ${st.session_state.ventas_netas:,.0f} (100%)")
    st.write(f"**Costo de Ventas:** ${calculos['costo_ventas']:,.0f} ({st.session_state.pct_costo:.1f}%)")
    st.write(f"**Margen Bruto:** ${calculos['margen_bruto']:,.0f} ({calculos['margen_bruto_pct']:.1f}%)")
    st.write("")
    st.write("**Gastos Operativos:**")
    st.write(f"- Nómina: ${st.session_state.nomina:,.0f}")
    st.write(f"- Comisiones: ${calculos['comisiones']:,.0f}")
    st.write(f"- Fletes: ${calculos['fletes']:,.0f}")
    st.write(f"- Rentas: ${st.session_state.rentas:,.0f}")
    st.write(f"- Otros: ${st.session_state.otros_gastos:,.0f}")
    st.write(f"**Total Gastos:** ${calculos['gasto_total']:,.0f}")
    st.write("")
    st.write(f"**EBITDA Operativo:** ${calculos['ebitda_operativo']:,.0f}")
    st.write(f"**Gastos Financieros:** ${calculos['gastos_financieros']:,.0f}")
    st.write(f"**EBITDA Final:** ${calculos['ebitda']:,.0f} ({calculos['margen_ebitda_pct']:.1f}%)")

st.divider()

# Análisis
st.subheader("Análisis de Eficiencia")

ca, cb = st.columns(2)

with ca:
    # Gráfico de pastel simplificado
    fig_pie = go.Figure(go.Pie(
        labels=['Nómina', 'Comisiones', 'Fletes', 'Rentas', 'Otros'],
        values=[
            st.session_state.nomina,
            calculos['comisiones'],
            calculos['fletes'],
            st.session_state.rentas,
            st.session_state.otros_gastos
        ],
        hole=0.4
    ))
    fig_pie.update_layout(height=300, showlegend=True)
    st.plotly_chart(fig_pie, use_container_width=True)

with cb:
    st.write("**Indicadores:**")
    margen_op = (calculos['ebitda_operativo'] / st.session_state.ventas_netas) * 100
    st.metric("Margen Operativo", f"{margen_op:.1f}%")
    
    if calculos['gastos_financieros'] > 0:
        cobertura = calculos['ebitda'] / calculos['gastos_financieros']
        st.metric("Cobertura Intereses", f"{cobertura:.1f}x")
    
    if calculos['margen_ebitda_pct'] > 15:
        st.success("Salud Financiera: Excelente")
    elif calculos['margen_ebitda_pct'] > 10:
        st.warning("Salud Financiera: Bueno")
    else:
        st.error("Salud Financiera: Requiere Atención")

st.caption(f"Actualizado: {datetime.now().strftime('%Y-%m-%d %H:%M')}")


