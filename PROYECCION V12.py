import streamlit as st
import plotly.graph_objects as go
from datetime import datetime

# ---------------- CONFIGURACIÓN ----------------
st.set_page_config(page_title="PORTAWARE Financiero", layout="wide")

# Inicializar estado
if "escenario" not in st.session_state:
    st.session_state.escenario = "manual"

# ---------------- FUNCIONES ----------------
def calcular(ventas, costo_pct, nom, com_pct, fle_pct, rent, otros, gf_pct):
    if ventas <= 0:
        return {
            'costo': 0, 'margen': 0, 'comisiones': 0,
            'fletes': 0, 'gasto_total': 0, 'ebitda_op': 0,
            'gf': 0, 'ebitda': 0, 'margen_pct': 0, 'ebitda_pct': 0
        }

    costo = ventas * (costo_pct / 100)
    margen = ventas - costo
    comisiones = ventas * (com_pct / 100)
    fletes = ventas * (fle_pct / 100)
    gasto_total = nom + comisiones + fletes + rent + otros
    ebitda_op = margen - gasto_total
    gf = ventas * (gf_pct / 100)
    ebitda = ebitda_op - gf
    margen_pct = (margen / ventas) * 100
    ebitda_pct = (ebitda / ventas) * 100

    return {
        'costo': costo, 'margen': margen, 'comisiones': comisiones,
        'fletes': fletes, 'gasto_total': gasto_total, 'ebitda_op': ebitda_op,
        'gf': gf, 'ebitda': ebitda, 'margen_pct': margen_pct, 'ebitda_pct': ebitda_pct
    }

# ---------------- TITULO ----------------
st.title("🏢 PORTAWARE - Análisis Financiero")
st.write("Simulador financiero interactivo")
st.divider()

# ---------------- ESCENARIOS ----------------
st.write("**Selecciona un Escenario:**")
col_e1, col_e2, col_e3, col_e4 = st.columns(4)

if col_e1.button("🚀 Optimista"):
    st.session_state.escenario = "optimista"
if col_e2.button("🛡️ Conservador"):
    st.session_state.escenario = "conservador"
if col_e3.button("⚡ Base"):
    st.session_state.escenario = "base"

escenario = st.session_state.escenario

# ---------------- VALORES POR ESCENARIO ----------------
if escenario == "optimista":
    v_default = 189_878_959 * 1.15
    c_default = 45.0
    n_default = 25_800_000
    com_default = 3.0
    f_default = 5.5
    r_default = 6_711_000
    o_default = 5_446_936
    gf_default = 0.8

elif escenario == "conservador":
    v_default = 189_878_959 * 0.95
    c_default = 48.0
    n_default = 25_800_000
    com_default = 3.0
    f_default = 6.5
    r_default = 6_711_000
    o_default = 5_446_936
    gf_default = 1.0

else:
    v_default = 189_878_959
    c_default = 47.0
    n_default = 25_800_000
    com_default = 3.0
    f_default = 6.0
    r_default = 6_711_000
    o_default = 5_446_936
    gf_default = 1.0

col_e4.info("💡 O ajusta manualmente")
st.divider()

# ---------------- LAYOUT ----------------
izq, der = st.columns([1, 2])

# -------- PANEL IZQUIERDO --------
with izq:
    st.subheader("⚙️ Controles")

    ventas = st.number_input("Ventas Netas ($)", 0.0, 999_999_999.0, float(v_default), 1_000_000.0)
    costo_pct = st.slider("Costo de Ventas (%)", 30.0, 70.0, c_default, 0.5)

    nomina = st.number_input("Nómina ($)", 0.0, 999_999_999.0, float(n_default), 100_000.0)
    comisiones_pct = st.slider("Comisiones (%)", 0.0, 10.0, com_default, 0.25)
    fletes_pct = st.slider("Fletes (%)", 0.0, 15.0, f_default, 0.25)
    rentas = st.number_input("Rentas ($)", 0.0, 999_999_999.0, float(r_default), 100_000.0)
    otros = st.number_input("Otros Gastos ($)", 0.0, 999_999_999.0, float(o_default), 100_000.0)

    gf_pct = st.slider("Gastos Financieros (%)", 0.0, 5.0, gf_default, 0.1)

# -------- CALCULAR --------
r = calcular(ventas, costo_pct, nomina, comisiones_pct, fletes_pct, rentas, otros, gf_pct)

# -------- PANEL DERECHO --------
with der:
    st.subheader("📊 Resultados")

    m1, m2, m3 = st.columns(3)
    m1.metric("Ventas", f"${ventas/1e6:.1f}M")
    m2.metric("Margen Bruto", f"${r['margen']/1e6:.1f}M", f"{r['margen_pct']:.1f}%")
    m3.metric("EBITDA", f"${r['ebitda']/1e6:.1f}M", f"{r['ebitda_pct']:.1f}%")

    st.write("**Análisis de Cascada**")

    fig_w = go.Figure(go.Waterfall(
        orientation="v",
        measure=["absolute", "relative", "relative", "relative", "relative", "relative", "total"],
        x=["Ventas", "Costo", "Nómina+OpEx", "G.Fin", "EBITDA Op", "Ajuste", "EBITDA Final"],
        y=[
            ventas,
            -r['costo'],
            -r['gasto_total'],
            -r['gf'],
            0,
            0,
            r['ebitda']
        ],
        connector={"line": {"color": "gray"}}
    ))

    fig_w.update_layout(height=400, showlegend=False)
    st.plotly_chart(fig_w, use_container_width=True, key="waterfall_chart")

    st.write("**Detalle Financiero**")
    st.text(f"""
Ventas Netas: ${ventas:,.0f}
Costo de Ventas: ${r['costo']:,.0f}
Margen Bruto: ${r['margen']:,.0f}

Gasto Total: ${r['gasto_total']:,.0f}
EBITDA Operativo: ${r['ebitda_op']:,.0f}
Gastos Financieros: ${r['gf']:,.0f}
EBITDA Final: ${r['ebitda']:,.0f} ({r['ebitda_pct']:.1f}%)
""")

st.divider()

# -------- ANÁLISIS --------
st.subheader("💡 Análisis Adicional")

an1, an2 = st.columns(2)

with an1:
    fig_p = go.Figure(go.Pie(
        labels=["Nómina", "Comisiones", "Fletes", "Rentas", "Otros"],
        values=[nomina, r['comisiones'], r['fletes'], rentas, otros],
        hole=0.4
    ))
    fig_p.update_layout(height=300)
    st.plotly_chart(fig_p, use_container_width=True, key="pie_chart")

with an2:
    if ventas > 0:
        marg_op = (r['ebitda_op'] / ventas) * 100
        st.metric("Margen Operativo", f"{marg_op:.1f}%")

    if r['gf'] > 0:
        cobertura = r['ebitda'] / r['gf']
        st.metric("Cobertura Financiera", f"{cobertura:.1f}x")

    if r['ebitda_pct'] > 15:
        st.success("🟢 Excelente rentabilidad")
    elif r['ebitda_pct'] > 10:
        st.warning("🟡 Buena rentabilidad")
    else:
        st.error("🔴 Margen bajo")

st.caption(f"Actualizado: {datetime.now().strftime('%Y-%m-%d %H:%M')}")


