import streamlit as st
import plotly.graph_objects as go
from datetime import datetime

# CONFIGURACIÓN
st.set_page_config(page_title="PORTAWARE Financiero", layout="wide")

# FUNCIONES
def calcular(ventas, costo_pct, nom, com_pct, fle_pct, rent, otros, gf_pct):
    costo = ventas * (costo_pct / 100)
    margen = ventas - costo
    comisiones = ventas * (com_pct / 100)
    fletes = ventas * (fle_pct / 100)
    gasto_total = nom + comisiones + fletes + rent + otros
    ebitda_op = margen - gasto_total
    gf = ventas * (gf_pct / 100)
    ebitda = ebitda_op - gf
    margen_pct = (margen / ventas) * 100 if ventas > 0 else 0
    ebitda_pct = (ebitda / ventas) * 100 if ventas > 0 else 0
    
    return {
        'costo': costo, 'margen': margen, 'comisiones': comisiones,
        'fletes': fletes, 'gasto_total': gasto_total, 'ebitda_op': ebitda_op,
        'gf': gf, 'ebitda': ebitda, 'margen_pct': margen_pct, 'ebitda_pct': ebitda_pct
    }

# TITULO
st.title("🏢 PORTAWARE - Análisis Financiero")
st.write("Simulador financiero interactivo")
st.divider()

# ESCENARIOS
st.write("**Selecciona un Escenario:**")
col_e1, col_e2, col_e3, col_e4 = st.columns(4)

escenario = "manual"
if col_e1.button("🚀 Optimista"):
    escenario = "optimista"
elif col_e2.button("🛡️ Conservador"):
    escenario = "conservador"
elif col_e3.button("⚡ Base"):
    escenario = "base"

# VALORES SEGÚN ESCENARIO
if escenario == "optimista":
    v_default = 189878959 * 1.15
    c_default = 45.0
    n_default = 25800000
    com_default = 3.0
    f_default = 5.5
    r_default = 6711000
    o_default = 5446936
    gf_default = 0.8
elif escenario == "conservador":
    v_default = 189878959 * 0.95
    c_default = 48.0
    n_default = 25800000
    com_default = 3.0
    f_default = 6.5
    r_default = 6711000
    o_default = 5446936
    gf_default = 1.0
else:  # base o manual
    v_default = 189878959
    c_default = 47.0
    n_default = 25800000
    com_default = 3.0
    f_default = 6.0
    r_default = 6711000
    o_default = 5446936
    gf_default = 1.0

col_e4.info("💡 O ajusta manualmente")

st.divider()

# LAYOUT
izq, der = st.columns([1, 2])

# PANEL IZQUIERDO - CONTROLES
with izq:
    st.subheader("⚙️ Controles")
    
    st.write("**💰 Ingresos**")
    ventas = st.number_input("Ventas Netas ($)", 0.0, 999999999.0, v_default, 1000000.0)
    
    st.write("**🏭 Costos**")
    costo_pct = st.slider("Costo de Ventas (%)", 30.0, 70.0, c_default, 0.5)
    
    st.write("**💸 Gastos Operativos**")
    nomina = st.number_input("Nómina ($)", 0.0, 999999999.0, n_default, 100000.0)
    comisiones_pct = st.slider("Comisiones (%)", 0.0, 10.0, com_default, 0.25)
    fletes_pct = st.slider("Fletes (%)", 0.0, 15.0, f_default, 0.25)
    rentas = st.number_input("Rentas ($)", 0.0, 999999999.0, r_default, 100000.0)
    otros = st.number_input("Otros Gastos ($)", 0.0, 999999999.0, o_default, 100000.0)
    
    st.write("**🏦 Financieros**")
    gf_pct = st.slider("Gastos Financieros (%)", 0.0, 5.0, gf_default, 0.1)

# CALCULAR
r = calcular(ventas, costo_pct, nomina, comisiones_pct, fletes_pct, rentas, otros, gf_pct)

# PANEL DERECHO - VISUALIZACIÓN
with der:
    st.subheader("📊 Resultados")
    
    # Métricas
    m1, m2, m3 = st.columns(3)
    m1.metric("Ventas", f"${ventas/1e6:.1f}M")
    m2.metric("Margen Bruto", f"${r['margen']/1e6:.1f}M", f"{r['margen_pct']:.1f}%")
    m3.metric("EBITDA", f"${r['ebitda']/1e6:.1f}M", f"{r['ebitda_pct']:.1f}%")
    
    # Gráfico Cascada
    st.write("**Análisis de Cascada**")
    
    fig_w = go.Figure(go.Waterfall(
        orientation="v",
        measure=['absolute', 'relative', 'total', 'relative', 'total', 'relative', 'total'],
        x=['Ventas', 'Costo', 'Margen', 'Gastos', 'EBITDA Op', 'G.Fin', 'EBITDA'],
        y=[ventas, -r['costo'], r['margen'], -r['gasto_total'], r['ebitda_op'], -r['gf'], r['ebitda']],
        text=[f"${x/1e6:.1f}M" for x in [ventas, -r['costo'], r['margen'], -r['gasto_total'], r['ebitda_op'], -r['gf'], r['ebitda']]],
        textposition="outside"
    ))
    fig_w.update_layout(height=350, showlegend=False)
    st.plotly_chart(fig_w, use_container_width=True)
    
    # Detalle
    st.write("**Detalle Financiero**")
    detalle = f"""
Ventas Netas: ${ventas:,.0f} (100%)
Costo de Ventas: ${r['costo']:,.0f} ({costo_pct:.1f}%)
MARGEN BRUTO: ${r['margen']:,.0f} ({r['margen_pct']:.1f}%)

Gastos Operativos:
  • Nómina: ${nomina:,.0f}
  • Comisiones: ${r['comisiones']:,.0f}
  • Fletes: ${r['fletes']:,.0f}
  • Rentas: ${rentas:,.0f}
  • Otros: ${otros:,.0f}
  Total: ${r['gasto_total']:,.0f}

EBITDA Operativo: ${r['ebitda_op']:,.0f}
Gastos Financieros: ${r['gf']:,.0f}
EBITDA FINAL: ${r['ebitda']:,.0f} ({r['ebitda_pct']:.1f}%)
    """
    st.text(detalle)

st.divider()

# ANÁLISIS
st.subheader("💡 Análisis Adicional")

an1, an2 = st.columns(2)

with an1:
    st.write("**Composición de Gastos**")
    
    fig_p = go.Figure(go.Pie(
        labels=['Nómina', 'Comisiones', 'Fletes', 'Rentas', 'Otros'],
        values=[nomina, r['comisiones'], r['fletes'], rentas, otros],
        hole=0.4
    ))
    fig_p.update_layout(height=300)
    st.plotly_chart(fig_p, use_container_width=True)

with an2:
    st.write("**Indicadores**")
    
    marg_op = (r['ebitda_op'] / ventas) * 100 if ventas > 0 else 0
    st.metric("Margen Operativo", f"{marg_op:.1f}%")
    
    if r['gf'] > 0:
        cob = r['ebitda'] / r['gf']
        st.metric("Cobertura", f"{cob:.1f}x")
    
    if r['ebitda_pct'] > 15:
        st.success("🟢 Excelente")
    elif r['ebitda_pct'] > 10:
        st.warning("🟡 Bueno")
    else:
        st.error("🔴 Atención")

st.caption(f"Actualizado: {datetime.now().strftime('%Y-%m-%d %H:%M')}")

