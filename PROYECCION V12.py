import streamlit as st
import plotly.graph_objects as go
from datetime import datetime

st.set_page_config(page_title="PORTAWARE Financiero", layout="wide")

# ---------- FUNCION ----------
def calcular(ventas, costo_pct, nom, com_pct, fle_pct, rent, otros, gf_pct):
    if ventas <= 0:
        return dict.fromkeys(
            ['costo','margen','comisiones','fletes','gasto_total',
             'ebitda_op','gf','ebitda','margen_pct','ebitda_pct'], 0
        )

    costo = ventas * costo_pct / 100
    margen = ventas - costo
    comisiones = ventas * com_pct / 100
    fletes = ventas * fle_pct / 100
    gasto_total = nom + comisiones + fletes + rent + otros
    ebitda_op = margen - gasto_total
    gf = ventas * gf_pct / 100
    ebitda = ebitda_op - gf

    return {
        "costo": costo,
        "margen": margen,
        "comisiones": comisiones,
        "fletes": fletes,
        "gasto_total": gasto_total,
        "ebitda_op": ebitda_op,
        "gf": gf,
        "ebitda": ebitda,
        "margen_pct": (margen/ventas)*100,
        "ebitda_pct": (ebitda/ventas)*100
    }

# ---------- SIDEBAR ----------
st.sidebar.header("⚙️ Parámetros")

ventas = st.sidebar.number_input("Ventas Netas", 0.0, 999999999.0, 189878959.0)
costo_pct = st.sidebar.slider("Costo %", 30.0, 70.0, 47.0)
nomina = st.sidebar.number_input("Nómina", 0.0, 999999999.0, 25800000.0)
com_pct = st.sidebar.slider("Comisiones %", 0.0, 10.0, 3.0)
fle_pct = st.sidebar.slider("Fletes %", 0.0, 15.0, 6.0)
rentas = st.sidebar.number_input("Rentas", 0.0, 999999999.0, 6711000.0)
otros = st.sidebar.number_input("Otros Gastos", 0.0, 999999999.0, 5446936.0)
gf_pct = st.sidebar.slider("Gastos Financieros %", 0.0, 5.0, 1.0)

# ---------- CALCULO ----------
r = calcular(ventas, costo_pct, nomina, com_pct, fle_pct, rentas, otros, gf_pct)

# ---------- MAIN ----------
st.title("🏢 PORTAWARE - Análisis Financiero")

col1, col2, col3 = st.columns(3)
col1.metric("Ventas", f"${ventas/1e6:.1f}M")
col2.metric("Margen Bruto", f"${r['margen']/1e6:.1f}M", f"{r['margen_pct']:.1f}%")
col3.metric("EBITDA", f"${r['ebitda']/1e6:.1f}M", f"{r['ebitda_pct']:.1f}%")

st.subheader("📊 Composición de Gastos")

fig = go.Figure(go.Bar(
    x=["Nómina","Comisiones","Fletes","Rentas","Otros"],
    y=[nomina, r["comisiones"], r["fletes"], rentas, otros]
))

fig.update_layout(height=400)
st.plotly_chart(fig, use_container_width=True)

st.subheader("📄 Resumen")

st.write(f"""
**Ventas:** ${ventas:,.0f}  
**Costo:** ${r['costo']:,.0f}  
**Margen Bruto:** ${r['margen']:,.0f}  

**Gasto Total:** ${r['gasto_total']:,.0f}  
**EBITDA Operativo:** ${r['ebitda_op']:,.0f}  
**EBITDA Final:** ${r['ebitda']:,.0f}  
""")

st.caption(f"Actualizado: {datetime.now().strftime('%Y-%m-%d %H:%M')}")



