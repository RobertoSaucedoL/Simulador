import streamlit as st
import plotly.graph_objects as go
import plotly.express as px
import google.generativeai as genai
from datetime import datetime

# --- CONFIGURACIÓN INICIAL ---
st.set_page_config(
    page_title="Simulador Financiero PORTAWARE", 
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Configuración de Gemini AI
try:
    genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
    # Verificar modelos disponibles
    models = genai.list_models()
    available_models = [model.name for model in models]
    st.session_state.available_models = available_models
    GEMINI_AVAILABLE = True
except (FileNotFoundError, KeyError, Exception) as e:
    GEMINI_AVAILABLE = False
    st.session_state.available_models = []

# Paleta de colores
COLORES = {
    'positivo': '#28A745',
    'negativo': '#DC3545',
    'principal': '#1F77B4',
    'secundario': '#FF7F0E',
    'terciario': '#2CA02C',
    'cuaternario': '#D62728',
    'quinario': '#9467BD'
}

# --- FUNCIONES DE CÁLCULO ---
def calcular_financieros(ventas_netas, pct_costo, nomina, pct_comisiones, pct_fletes, rentas, otros_gastos, pct_gastos_financieros):
    """Calcula todos los valores financieros"""
    costo = ventas_netas * (pct_costo / 100)
    margen_bruto = ventas_netas - costo
    comisiones = ventas_netas * (pct_comisiones / 100)
    fletes = ventas_netas * (pct_fletes / 100)
    gasto_total = nomina + comisiones + fletes + rentas + otros_gastos
    ebitda_operativo = margen_bruto - gasto_total
    gastos_financieros = ventas_netas * (pct_gastos_financieros / 100)
    ebitda = ebitda_operativo - gastos_financieros
    
    margen_bruto_pct = (margen_bruto / ventas_netas) * 100 if ventas_netas != 0 else 0
    margen_ebitda_pct = (ebitda / ventas_netas) * 100 if ventas_netas != 0 else 0
    
    return {
        'costo': costo,
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

def generar_analisis_ia(datos, calculos):
    """Genera análisis con IA de Gemini"""
    if not GEMINI_AVAILABLE:
        return "⚠️ La API de Gemini no está configurada. Configura GEMINI_API_KEY en los secrets de Streamlit."
    
    prompt = f"""Analiza esta situación financiera de PORTAWARE (fabricante de artículos de plástico para el hogar) y proporciona un análisis ejecutivo conciso (máximo 150 palabras):

Ventas Netas: ${datos['ventas_netas']:,.0f}
Costo ({datos['pct_costo']}%): ${calculos['costo']:,.0f}
Margen Bruto: ${calculos['margen_bruto']:,.0f} ({calculos['margen_bruto_pct']:.1f}%)
Gastos Totales: ${calculos['gasto_total']:,.0f}
- Nómina: ${datos['nomina']:,.0f}
- Comisiones ({datos['pct_comisiones']}%): ${calculos['comisiones']:,.0f}
- Fletes ({datos['pct_fletes']}%): ${calculos['fletes']:,.0f}
- Rentas: ${datos['rentas']:,.0f}
- Otros: ${datos['otros_gastos']:,.0f}
EBITDA Operativo: ${calculos['ebitda_operativo']:,.0f}
Gastos Financieros ({datos['pct_gastos_financieros']}%): ${calculos['gastos_financieros']:,.0f}
EBITDA Final: ${calculos['ebitda']:,.0f} ({calculos['margen_ebitda_pct']:.1f}%)

Proporciona: 1) Diagnóstico de salud financiera, 2) 2-3 recomendaciones específicas para mejorar rentabilidad."""
    
    try:
        # Probar con modelos disponibles
        modelos_disponibles = st.session_state.available_models
        modelo_usar = None
        
        # Priorizar modelos conocidos
        for modelo in modelos_disponibles:
            if 'gemini-1.5' in modelo and 'flash' in modelo:
                modelo_usar = modelo
                break
            elif 'gemini-1.0' in modelo and 'pro' in modelo:
                modelo_usar = modelo
                break
            elif 'gemini-pro' in modelo:
                modelo_usar = modelo
                break
        
        if modelo_usar:
            model = genai.GenerativeModel(modelo_usar.split('/')[-1])
            response = model.generate_content(prompt)
            return response.text
        else:
            return "ℹ️ No se encontraron modelos de Gemini disponibles. Verifica tu configuración de API."
            
    except Exception as e:
        return f"❌ Error al generar análisis: {str(e)}"

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
st.title('📊 Simulador Financiero PORTAWARE')
st.caption('Análisis simplificado con IA integrada')

# Header con botones de escenarios
col_h1, col_h2, col_h3, col_h4 = st.columns(4)
with col_h1:
    if st.button('📈 Escenario Optimista', use_container_width=True):
        aplicar_escenario('optimista')
        st.rerun()
with col_h2:
    if st.button('📉 Escenario Conservador', use_container_width=True):
        aplicar_escenario('conservador')
        st.rerun()
with col_h3:
    if st.button('🔄 Valores Originales', use_container_width=True):
        aplicar_escenario('reset')
        st.rerun()
with col_h4:
    estado_ia = '✅ IA Activa' if GEMINI_AVAILABLE else '❌ IA Inactiva'
    st.markdown(f"**{estado_ia}**")

st.markdown("---")

# Métricas principales
col1, col2, col3 = st.columns(3)

with col1:
    st.metric(
        "💰 Ventas Netas",
        f"${float(st.session_state.ventas_netas)/1_000_000:.1f}M",
        help="Ingresos totales de la empresa"
    )

with col2:
    st.metric(
        "📊 Margen Bruto",
        f"{calculos['margen_bruto_pct']:.1f}%",
        f"${calculos['margen_bruto']/1_000_000:.1f}M",
        delta_color="normal"
    )

with col3:
    st.metric(
        "🎯 EBITDA",
        f"{calculos['margen_ebitda_pct']:.1f}%",
        f"${calculos['ebitda']/1_000_000:.1f}M",
        delta_color="normal"
    )

st.markdown("---")

# Layout principal: Controles + Visualizaciones
col_controles, col_visuales = st.columns([1, 2])

with col_controles:
    st.subheader("🎛️ Controles de Simulación")
    
    with st.container():
        st.markdown("##### 💰 Ingresos")
        st.session_state.ventas_netas = st.number_input(
            "Ventas Netas ($)",
            min_value=0.0,
            value=float(st.session_state.ventas_netas),
            step=1000000.0,
            format="%f",
            help="Ingresos totales"
        )
        st.caption(f"${float(st.session_state.ventas_netas):,.0f}")
    
    st.markdown("---")
    
    with st.container():
        st.markdown("##### 🏭 Costos")
        st.session_state.pct_costo = st.slider(
            "% Costo de Ventas",
            min_value=30.0,
            max_value=70.0,
            value=float(st.session_state.pct_costo),
            step=0.5,
            help="Porcentaje del costo sobre ventas netas"
        )
        st.caption(f"Costo: ${calculos['costo']:,.0f}")
        st.caption(f"Margen Bruto: ${calculos['margen_bruto']:,.0f}")
    
    st.markdown("---")
    
    with st.container():
        st.markdown("##### 💸 Gastos Operativos")
        
        st.session_state.nomina = st.number_input(
            "Nómina ($)",
            min_value=0.0,
            value=float(st.session_state.nomina),
            step=100000.0,
            format="%f"
        )
        st.caption(f"${float(st.session_state.nomina):,.0f}")
        
        st.session_state.pct_comisiones = st.slider(
            "% Comisiones",
            min_value=0.0,
            max_value=10.0,
            value=float(st.session_state.pct_comisiones),
            step=0.25
        )
        st.caption(f"Comisiones: ${calculos['comisiones']:,.0f}")
        
        st.session_state.pct_fletes = st.slider(
            "% Fletes",
            min_value=0.0,
            max_value=15.0,
            value=float(st.session_state.pct_fletes),
            step=0.25
        )
        st.caption(f"Fletes: ${calculos['fletes']:,.0f}")
        
        st.session_state.rentas = st.number_input(
            "Rentas ($)",
            min_value=0.0,
            value=float(st.session_state.rentas),
            step=100000.0,
            format="%f"
        )
        st.caption(f"${float(st.session_state.rentas):,.0f}")
        
        st.session_state.otros_gastos = st.number_input(
            "Otros Gastos ($)",
            min_value=0.0,
            value=float(st.session_state.otros_gastos),
            step=100000.0,
            format="%f"
        )
        st.caption(f"${float(st.session_state.otros_gastos):,.0f}")
        
        st.markdown(f"**Gasto Total: ${calculos['gasto_total']:,.0f}**")
    
    st.markdown("---")
    
    with st.container():
        st.markdown("##### 🏦 Gastos Financieros")
        st.session_state.pct_gastos_financieros = st.slider(
            "% Gastos Financieros",
            min_value=0.0,
            max_value=5.0,
            value=float(st.session_state.pct_gastos_financieros),
            step=0.1
        )
        st.caption(f"Gastos Financieros: ${calculos['gastos_financieros']:,.0f}")

with col_visuales:
    # Tabla de resultados financieros
    st.subheader("📋 Resumen Financiero")
    
    # Crear tabla de resultados
    datos_tabla = [
        ["Ventas Netas", f"${float(st.session_state.ventas_netas):,.0f}", "100.0%"],
        ["Costo de Ventas", f"${calculos['costo']:,.0f}", f"{float(st.session_state.pct_costo):.1f}%"],
        ["**Margen Bruto**", f"**${calculos['margen_bruto']:,.0f}**", f"**{calculos['margen_bruto_pct']:.1f}%**"],
        ["", "", ""],
        ["**Gastos Operativos:**", "", ""],
        [" - Nómina", f"${float(st.session_state.nomina):,.0f}", f"{(float(st.session_state.nomina)/float(st.session_state.ventas_netas))*100:.1f}%"],
        [" - Comisiones", f"${calculos['comisiones']:,.0f}", f"{float(st.session_state.pct_comisiones):.1f}%"],
        [" - Fletes", f"${calculos['fletes']:,.0f}", f"{float(st.session_state.pct_fletes):.1f}%"],
        [" - Rentas", f"${float(st.session_state.rentas):,.0f}", f"{(float(st.session_state.rentas)/float(st.session_state.ventas_netas))*100:.1f}%"],
        [" - Otros Gastos", f"${float(st.session_state.otros_gastos):,.0f}", f"{(float(st.session_state.otros_gastos)/float(st.session_state.ventas_netas))*100:.1f}%"],
        ["**Total Gastos Operativos**", f"**${calculos['gasto_total']:,.0f}**", f"**{(calculos['gasto_total']/float(st.session_state.ventas_netas))*100:.1f}%**"],
        ["", "", ""],
        ["EBITDA Operativo", f"${calculos['ebitda_operativo']:,.0f}", f"{(calculos['ebitda_operativo']/float(st.session_state.ventas_netas))*100:.1f}%"],
        ["Gastos Financieros", f"${calculos['gastos_financieros']:,.0f}", f"{float(st.session_state.pct_gastos_financieros):.1f}%"],
        ["**EBITDA Final**", f"**${calculos['ebitda']:,.0f}**", f"**{calculos['margen_ebitda_pct']:.1f}%**"]
    ]
    
    # Crear tabla con Plotly
    fig_tabla = go.Figure(data=[go.Table(
        columnwidth=[2, 1.5, 1],
        header=dict(
            values=['<b>Concepto</b>', '<b>Monto</b>', '<b>%</b>'],
            fill_color=COLORES['principal'],
            align=['left', 'right', 'right'],
            font=dict(color='white', size=12)
        ),
        cells=dict(
            values=[[fila[0] for fila in datos_tabla], 
                   [fila[1] for fila in datos_tabla], 
                   [fila[2] for fila in datos_tabla]],
            align=['left', 'right', 'right'],
            fill_color=['white', 'white', 'white'],
            font=dict(size=11),
            height=25
        )
    )])
    
    fig_tabla.update_layout(
        height=500,
        margin=dict(l=0, r=0, t=0, b=0)
    )
    
    st.plotly_chart(fig_tabla, use_container_width=True)
    
    # Gráfico de Composición de Gastos
    st.subheader("🥧 Composición de Gastos Operativos")
    
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
        hole=0.4,
        marker_colors=[COLORES['principal'], COLORES['secundario'], COLORES['terciario'], 
                      COLORES['cuaternario'], COLORES['quinario']]
    )])
    
    fig_pie.update_layout(
        height=400,
        margin=dict(l=20, r=20, t=20, b=20)
    )
    
    st.plotly_chart(fig_pie, use_container_width=True)

st.markdown("---")

# Sección de Análisis IA
st.subheader("🤖 Análisis Estratégico con IA")

col_ia1, col_ia2 = st.columns([3, 1])

with col_ia2:
    if st.button("🚀 Generar Análisis Estratégico", use_container_width=True, type="primary"):
        with st.spinner("🧠 Analizando con IA..."):
            datos_para_ia = {
                'ventas_netas': float(st.session_state.ventas_netas),
                'pct_costo': float(st.session_state.pct_costo),
                'nomina': float(st.session_state.nomina),
                'pct_comisiones': float(st.session_state.pct_comisiones),
                'pct_fletes': float(st.session_state.pct_fletes),
                'rentas': float(st.session_state.rentas),
                'otros_gastos': float(st.session_state.otros_gastos),
                'pct_gastos_financieros': float(st.session_state.pct_gastos_financieros)
            }
            st.session_state.analisis_ia = generar_analisis_ia(datos_para_ia, calculos)

with col_ia1:
    if 'analisis_ia' in st.session_state:
        st.info(st.session_state.analisis_ia)
    else:
        st.info("👆 Haz clic en 'Generar Análisis Estratégico' para obtener recomendaciones con IA")

# Información de modelos disponibles (para debugging)
if GEMINI_AVAILABLE and st.session_state.available_models:
    with st.expander("🔧 Información de Modelos Disponibles"):
        st.write("Modelos encontrados:")
        for modelo in st.session_state.available_models:
            st.write(f"- {modelo}")

# Footer
st.markdown("---")
st.caption(f"Última actualización: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")


