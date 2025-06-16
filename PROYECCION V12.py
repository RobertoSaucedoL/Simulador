import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st
import google.generativeai as genai

# --- CONFIGURACIÓN INICIAL ---
st.set_page_config(page_title="Simulador Financiero Jerárquico", layout="wide", initial_sidebar_state="expanded")

# Configuración de Gemini AI
try:
    genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
    GEMINI_AVAILABLE = True
except (FileNotFoundError, KeyError):
    GEMINI_AVAILABLE = False
    st.warning(
        "⚠️ **Advertencia**: La clave de API de Gemini no está configurada en `st.secrets`. Las funcionalidades de IA no estarán disponibles.")

# Paleta de colores profesional
PALETA_GRAFICOS = {
    'Actual': '#0077B6',
    'Simulado': '#F79F1F',
    'Meta': '#00A896',
    'Positivo': '#2ECC71',  # Verde
    'Negativo': '#E74C3C'  # Rojo
}


# --- DATOS ESTRUCTURADOS ---
def obtener_estructura_cuentas():
    """Retorna la estructura completa de cuentas con jerarquía"""
    return {
        # Nivel 4 - VENTAS BRUTAS
        'VENTAS BRUTAS': {
            'jerarquia': '4', 'tipo': 'suma',
            'componentes': ['VENTAS BRUTAS NACIONAL 16%', 'VENTAS BRUTAS EXTRANJERO'],
            'subcuentas': {
                'VENTAS BRUTAS NACIONAL 16%': {
                    'RETAIL': {'actual': 173562776, 'meta': 168934800, 'simulable': True},
                    'CATALOGO': {'actual': 7153580, 'meta': 5232032, 'simulable': True},
                    'MAYOREO': {'actual': 45616798, 'meta': 57000000, 'simulable': True}
                },
                'VENTAS BRUTAS EXTRANJERO': {
                    'RETAIL': {'actual': 4089, 'meta': 0, 'simulable': True},
                    'CATALOGO': {'actual': 339355, 'meta': 0, 'simulable': True},
                    'MAYOREO': {'actual': 0, 'meta': 0, 'simulable': True}
                }
            }
        },

        # Nivel 5 - DESCUENTOS Y OTROS
        'DESCUENTOS': {'jerarquia': '5', 'tipo': 'simple', 'actual': 14370489, 'meta': 14608084, 'simulable': True},
        'OTROS INGRESOS': {'jerarquia': '5.3', 'tipo': 'simple', 'actual': -7071, 'meta': 0, 'simulable': True},

        # Nivel 6 - VENTAS NETAS
        'VENTAS NETAS': {'jerarquia': '6', 'tipo': 'formula', 'formula': 'VENTAS BRUTAS - DESCUENTOS + OTROS INGRESOS'},

        # Nivel 7 - COSTOS
        'COSTO': {
            'jerarquia': '7', 'tipo': 'suma',
            'componentes': ['COSTO DIRECTO', 'COSTO INDIRECTO', 'OTROS COSTOS'],
            'subcuentas': {
                'COSTO DIRECTO': {
                    'MATERIALES A PROCESO': {'actual': 103175886, 'meta': 101987820, 'simulable': True},
                    'MANO DE OBRA ARMADO': {'actual': 3239912, 'meta': 4859868, 'simulable': True}
                },
                'COSTO INDIRECTO': {
                    'COSTOS DE CALIDAD': {'actual': 137498, 'meta': 159044, 'simulable': True},
                    'COSTOS DE MOLDES': {'actual': 244000, 'meta': 366000, 'simulable': True}
                },
                'OTROS COSTOS': {'OTROS COSTOS': {'actual': 75250, 'meta': 0, 'simulable': True}}
            }
        },

        # Nivel 8 - MARGEN BRUTO
        'MARGEN BRUTO': {'jerarquia': '8', 'tipo': 'formula', 'formula': 'VENTAS NETAS - COSTO'},

        # Nivel 9 - GASTOS OPERATIVOS
        'TOTAL GASTOS OPERATIVOS': {
            'jerarquia': '9', 'tipo': 'suma_gastos',
            'subcuentas': {
                'SUELDOS Y SALARIOS': {'actual': 20749436, 'meta': 22818917, 'simulable': True},
                'PRESTACIONES': {'actual': 1085362, 'meta': 0, 'simulable': True},
                'OTRAS COMPENSACIONES': {'actual': 28214, 'meta': 0, 'simulable': True},
                'SEGURIDAD E HIGIENE': {'actual': 120498, 'meta': 172490, 'simulable': True},
                'GASTOS DE PERSONAL': {'actual': 384668, 'meta': 425174, 'simulable': True},
                'COMBUSTIBLE': {'actual': 284529, 'meta': 388200, 'simulable': True},
                'ESTACIONAMIENTO': {'actual': 110217, 'meta': 143808, 'simulable': True},
                'TRANSPORTE LOCAL': {'actual': 122285, 'meta': 180000, 'simulable': True},
                'GASTOS DE VIAJE': {'actual': 402950, 'meta': 420000, 'simulable': True},
                'ASESORIAS PM': {'actual': 519661, 'meta': 21246, 'simulable': True},
                'SEGURIDAD Y VIGILANCIA': {'actual': 36941, 'meta': 41371, 'simulable': True},
                'SERVICIOS INSTALACIONES': {'actual': 246172, 'meta': 338864, 'simulable': True},
                'CELULARES': {'actual': 120840, 'meta': 144720, 'simulable': True},
                'SUMINISTROS GENERALES': {'actual': 126046, 'meta': 144840, 'simulable': True},
                'SUMINISTROS OFICINA': {'actual': 56617, 'meta': 66600, 'simulable': True},
                'SUMINISTROS COMPUTO': {'actual': 67112, 'meta': 49200, 'simulable': True},
                'ARRENDAMIENTOS': {'actual': 6211694, 'meta': 6448852, 'simulable': True},
                'MANTENIMIENTOS': {'actual': 438694, 'meta': 355000, 'simulable': True},
                'INVENTARIO FÍSICO': {'actual': 33333, 'meta': 50000, 'simulable': True},
                'OTROS IMPUESTOS Y DERECHOS': {'actual': 9084, 'meta': 0, 'simulable': True},
                'NO DEDUCIBLES': {'actual': 38472, 'meta': 3000, 'simulable': True},
                'SEGUROS Y FIANZAS': {'actual': 185402, 'meta': 185033, 'simulable': True},
                'CAPACITACION Y ENTRENAMIENTO': {'actual': 126476, 'meta': 131654, 'simulable': True},
                'MENSAJERIA': {'actual': 111428, 'meta': 115400, 'simulable': True},
                'MUESTRAS': {'actual': 15200, 'meta': 22800, 'simulable': True},
                'FERIAS Y EXPOSICIONES': {'actual': 25000, 'meta': 26200, 'simulable': True},
                'PUBLICIDAD IMPRESA': {'actual': 46369, 'meta': 67200, 'simulable': True},
                'IMPRESIONES 3D': {'actual': 334000, 'meta': 420000, 'simulable': True},
                'MATERIAL DISEÑO': {'actual': 12000, 'meta': 18000, 'simulable': True},
                'PATENTES': {'actual': 15225, 'meta': 0, 'simulable': True},
                'LICENCIAS Y SOFTWARE': {'actual': 402602, 'meta': 470712, 'simulable': True},
                'ATENCION A CLIENTES': {'actual': 2099, 'meta': 0, 'simulable': True},
                'ASESORIAS PF': {'actual': 259655, 'meta': 725482, 'simulable': True},
                'PORTALES CLIENTES': {'actual': 98487, 'meta': 144475, 'simulable': True},
                'CUOTAS Y SUSCRIPCIONES': {'actual': 79954, 'meta': 106218, 'simulable': True},
                'FLETES EXTERNOS': {'actual': 8586502, 'meta': 7594838, 'simulable': True},
                'FLETES INTERNOS': {'actual': 24727, 'meta': 0, 'simulable': True},
                'IMPTOS S/NOMINA': {'actual': 445410, 'meta': 658364, 'simulable': True},
                'CONTRIBUCIONES PATRONALES': {'actual': 2604096, 'meta': 3836805, 'simulable': True},
                'TIMBRES Y FOLIOS FISCALES': {'actual': 2304, 'meta': 2714, 'simulable': True},
                'COMISION MERCANTIL': {'actual': 12, 'meta': 0, 'simulable': True},
                'GASTOS ADUANALES': {'actual': 174732, 'meta': 0, 'simulable': True}
            }
        },

        # Resto de la estructura
        'EBITDA OPERATIVA': {'jerarquia': '10', 'tipo': 'formula', 'formula': 'MARGEN BRUTO - TOTAL GASTOS OPERATIVOS'},
        'TOTAL DE OTROS GASTOS': {'jerarquia': '11', 'tipo': 'simple', 'actual': 2362914, 'meta': 0, 'simulable': True},
        'EBITDA': {'jerarquia': '12', 'tipo': 'formula', 'formula': 'EBITDA OPERATIVA - TOTAL DE OTROS GASTOS'},
        'FINANCIEROS': {
            'jerarquia': '13', 'tipo': 'suma',
            'componentes': ['GASTOS FINANCIEROS', 'PRODUCTOS FINANCIEROS', 'RESULTADO CAMBIARIO'],
            'subcuentas': {
                'GASTOS FINANCIEROS': {'actual': 794755, 'meta': 828875, 'simulable': True},
                'PRODUCTOS FINANCIEROS': {'actual': -35200, 'meta': -52800, 'simulable': True},
                'RESULTADO CAMBIARIO': {'actual': -654487, 'meta': -981731, 'simulable': True}
            }
        },
        'BAI': {'jerarquia': '14', 'tipo': 'formula', 'formula': 'EBITDA - FINANCIEROS'}
    }


# --- FUNCIONES DE CÁLCULO ---
@st.cache_data
def get_cached_structure():
    return obtener_estructura_cuentas()


# Helper function to get the actual value of a specific simulable account
def get_actual_value(estructura, account_key, sub_account_key=None, sub_item_key=None):
    if sub_account_key and sub_item_key:
        return estructura.get(account_key, {}).get('subcuentas', {}).get(sub_account_key, {}).get(sub_item_key, {}).get(
            'actual', 0)
    elif sub_account_key:
        return estructura.get(account_key, {}).get('subcuentas', {}).get(sub_account_key, {}).get('actual', 0)
    else:
        return estructura.get(account_key, {}).get('actual', 0)


def inicializar_simulaciones():
    # Asegura que las claves de simulación existan al inicio en st.session_state
    estructura = get_cached_structure()
    for cuenta, datos in estructura.items():
        if datos.get('simulable'):
            key = f"sim_{cuenta.replace(' ', '_').replace('/', '_')}"
            if key not in st.session_state:
                st.session_state[key] = 0.0
        if 'subcuentas' in datos:
            for subcuenta, subdatos in datos['subcuentas'].items():
                if isinstance(subdatos, dict) and 'actual' not in subdatos:
                    for subitem, itemdatos in subdatos.items():
                        if itemdatos.get('simulable'):
                            key = f"sim_{subcuenta.replace(' ', '_')}_{subitem.replace(' ', '_')}"
                            if key not in st.session_state:
                                st.session_state[key] = 0.0
                elif isinstance(subdatos, dict) and subdatos.get('simulable'):
                    key = f"sim_{subcuenta.replace(' ', '_')}"
                    if key not in st.session_state:
                        st.session_state[key] = 0.0
    # Inicializa también los controles del ajuste automático de costos
    if 'ajuste_activo' not in st.session_state:
        st.session_state['ajuste_activo'] = False
    if 'porcentaje_ajuste' not in st.session_state:
        st.session_state['porcentaje_ajuste'] = 45


def calculate_account_value(_estructura, scenario, changes):
    results = {}

    def get_val(cuenta):
        if cuenta in results:
            return results[cuenta]

        datos = _estructura.get(cuenta)
        if not datos:
            return 0

        valor = 0
        if datos['tipo'] == 'simple':
            base_value = datos['actual'] if scenario == 'actual' else datos.get('meta', 0) if scenario == 'meta' else \
            datos['actual']  # Default to actual for 'simulado' base
            if datos.get('simulable') and scenario == 'simulado':
                key = f"sim_{cuenta.replace(' ', '_').replace('/', '_')}"
                cambio_monetario = changes.get(key, 0.0)
                valor = base_value + cambio_monetario
            else:
                valor = base_value
        elif datos['tipo'] in ['suma', 'suma_gastos']:
            for subcuenta_name, subdatos_dict_or_item in datos['subcuentas'].items():
                if isinstance(subdatos_dict_or_item, dict) and 'actual' not in subdatos_dict_or_item:
                    for subitem_name, itemdatos in subdatos_dict_or_item.items():
                        base_value = itemdatos['actual'] if scenario == 'actual' else itemdatos.get('meta',
                                                                                                    0) if scenario == 'meta' else \
                        itemdatos['actual']
                        if itemdatos.get('simulable') and scenario == 'simulado':
                            key = f"sim_{subcuenta_name.replace(' ', '_')}_{subitem_name.replace(' ', '_')}"
                            cambio_monetario = changes.get(key, 0.0)
                            valor += base_value + cambio_monetario
                        else:
                            valor += base_value
                else:
                    itemdatos = subdatos_dict_or_item
                    base_value = itemdatos['actual'] if scenario == 'actual' else itemdatos.get('meta',
                                                                                                0) if scenario == 'meta' else \
                    itemdatos['actual']
                    if itemdatos.get('simulable') and scenario == 'simulado':
                        key = f"sim_{subcuenta_name.replace(' ', '_')}"
                        cambio_monetario = changes.get(key, 0.0)
                        valor += base_value + cambio_monetario
                    else:
                        valor += base_value
        elif datos['tipo'] == 'formula':
            temp_formula = datos['formula'].replace(' - ', '|').replace(' + ', '|')
            operands = temp_formula.split('|')
            operators = [char for char in datos['formula'] if char in ['+', '-']]

            first_operand_val = get_val(operands[0])
            valor = first_operand_val
            for i, operand_name in enumerate(operands[1:]):
                op = operators[i]
                current_operand_val = get_val(operand_name)
                if op == '+':
                    valor += current_operand_val
                elif op == '-':
                    valor -= current_operand_val
        results[cuenta] = valor
        return valor

    cuentas_ordenadas = sorted(_estructura.keys(), key=lambda k: float(_estructura[k]['jerarquia']))

    # Primera pasada: Calcular todos los "simples" y componentes de "sumas"
    for cuenta in cuentas_ordenadas:
        if _estructura[cuenta]['tipo'] in ['simple', 'suma', 'suma_gastos']:
            get_val(cuenta)

    # Segunda pasada: Calcular todas las "fórmulas" que dependen de los anteriores
    for cuenta in cuentas_ordenadas:
        if _estructura[cuenta]['tipo'] == 'formula':
            get_val(cuenta)

    return results


def generar_dataframe_completo(changes):
    estructura = get_cached_structure()
    actual_values = calculate_account_value(estructura, 'actual', changes)
    meta_values = calculate_account_value(estructura, 'meta', changes)
    simulado_values = calculate_account_value(estructura, 'simulado', changes)

    data_list = []
    for c, i in estructura.items():
        data_list.append({
            'Cuenta': c,
            'Jerarquia': i['jerarquia'],
            'Actual': actual_values.get(c, 0),
            'Simulado': simulado_values.get(c, 0),
            'Meta': meta_values.get(c, 0)
        })
    df = pd.DataFrame(data_list)

    df['Jerarquia'] = pd.to_numeric(df['Jerarquia'])
    df = df.sort_values(by='Jerarquia').reset_index(drop=True)

    # Solo la brecha del escenario Simulado contra la Meta (%)
    df['Brecha vs Meta (%)'] = ((df['Simulado'] - df['Meta']) / df['Meta'].replace(0, pd.NA)) * 100
    # Brecha de Simulado vs Actual (%)
    df['Brecha Simulado vs Actual (%)'] = ((df['Simulado'] - df['Actual']) / df['Actual'].replace(0, pd.NA)) * 100

    # Porcentajes respecto a ventas netas
    ventas_netas_simulado = df.loc[df['Cuenta'] == 'VENTAS NETAS', 'Simulado'].iloc[0] if 'VENTAS NETAS' in df[
        'Cuenta'].values else 1
    ventas_netas_meta = df.loc[df['Cuenta'] == 'VENTAS NETAS', 'Meta'].iloc[0] if 'VENTAS NETAS' in df[
        'Cuenta'].values else 1

    df['Simulado (% VN)'] = (df['Simulado'] / ventas_netas_simulado) * 100 if ventas_netas_simulado != 0 else 0
    df['Meta (% VN)'] = (df['Meta'] / ventas_netas_meta) * 100 if ventas_netas_meta != 0 else 0

    return df


def obtener_variables_modificadas(changes):
    """Retorna un DataFrame con las variables que han sido modificadas, mostrando el cambio monetario y el porcentaje"""
    variables_modificadas = []

    estructura = get_cached_structure()

    # Mapeo de claves de simulación a nombres de cuentas legibles y sus valores actuales base
    sim_key_info = {}
    for cuenta, datos in estructura.items():
        # Manejo de cuentas simples simulables (ej. DESCUENTOS)
        if datos.get('simulable') and 'subcuentas' not in datos:
            sim_key_info[f"sim_{cuenta.replace(' ', '_').replace('/', '_')}"] = {'name': cuenta,
                                                                                 'actual_val': datos['actual']}

        # Manejo de subcuentas con sub-ítems simulables (ej. VENTAS BRUTAS NACIONAL 16% - RETAIL)
        if 'subcuentas' in datos:
            for subcuenta, subdatos in datos['subcuentas'].items():
                if isinstance(subdatos, dict) and 'actual' not in subdatos:
                    for subitem, itemdatos in subdatos.items():
                        if itemdatos.get('simulable'):
                            sim_key_info[f"sim_{subcuenta.replace(' ', '_')}_{subitem.replace(' ', '_')}"] = {
                                'name': f"{subcuenta} - {subitem}", 'actual_val': itemdatos['actual']}
                # Manejo de subcuentas directamente simulables (ej. SUELDOS Y SALARIOS)
                elif isinstance(subdatos, dict) and subdatos.get('simulable'):
                    sim_key_info[f"sim_{subcuenta.replace(' ', '_')}"] = {'name': subcuenta,
                                                                          'actual_val': subdatos['actual']}

    for key, value in changes.items():
        # IMPORTANTE: No considerar el cambio de Materiales A Proceso si es resultado del ajuste automático
        # y si el ajuste automático no está activo. Esto se manejará antes de llamar a esta función.
        if key.startswith('sim_') and value != 0.0:
            info = sim_key_info.get(key)
            if info:
                display_name = info['name']
                actual_val = info['actual_val']

                # Calcular porcentaje de cambio
                porcentaje_cambio = 0.0
                if actual_val != 0:
                    porcentaje_cambio = (value / actual_val) * 100
                elif value != 0:
                    porcentaje_cambio = float('inf') if value > 0 else float('-inf')

                variables_modificadas.append({
                    'Variable': display_name,
                    'Cambio Monetario': value,  # Usar valor numérico para ordenar
                    'Cambio Porcentual': porcentaje_cambio,  # Usar valor numérico para ordenar
                    'ValorNumAbsoluto': abs(value)
                })

    df_variables = pd.DataFrame(variables_modificadas)
    if not df_variables.empty:
        # Formatear después de ordenar
        df_variables = df_variables.sort_values('ValorNumAbsoluto', ascending=False)
        df_variables['Cambio Monetario'] = df_variables['Cambio Monetario'].apply(lambda x: f"${x:,.0f}")
        df_variables['Cambio Porcentual'] = df_variables['Cambio Porcentual'].apply(
            lambda x: f"{x:+.1f}%" if x != float('inf') and x != float('-inf') else (
                "+Inf%" if x == float('inf') else "-Inf%"))
        df_variables = df_variables.drop(columns=['ValorNumAbsoluto'])
    return df_variables


# --- FUNCIONES DE UI Y ANÁLISIS ---
def aplicar_estilo_financiero(df):
    def estilo_fila(row):
        styles = []
        # Estilos para cuentas principales y subtotales
        cuentas_clave = [
            'VENTAS BRUTAS', 'DESCUENTOS', 'OTROS INGRESOS', 'VENTAS NETAS', 'COSTO',
            'MARGEN BRUTO', 'TOTAL GASTOS OPERATIVOS', 'EBITDA OPERATIVA',
            'TOTAL DE OTROS GASTOS', 'EBITDA', 'FINANCIEROS', 'BAI'
        ]
        if row['Cuenta'] in cuentas_clave:
            styles.append('font-weight: bold;')
            if row['Cuenta'] in ['VENTAS NETAS', 'MARGEN BRUTO', 'EBITDA', 'BAI']:
                styles.append('background-color: rgba(0, 168, 150, 0.1);')  # Color para subtotales importantes

        # Estilo para celdas de brecha (mejorado para claridad)
        if 'Brecha (% S vs M)' in row.index:
            brecha_val = row['Brecha (% S vs M)']
            if pd.notna(brecha_val):
                # Para ingresos y ganancias, verde si es positivo, rojo si es negativo
                if row['Cuenta'] in ['VENTAS BRUTAS', 'VENTAS NETAS', 'MARGEN BRUTO', 'EBITDA OPERATIVA', 'EBITDA',
                                     'BAI']:
                    if brecha_val > 0.01:  # Pequeño umbral para considerar "positivo"
                        styles.append('color: green; font-weight: bold;')
                    elif brecha_val < -0.01:  # Pequeño umbral para considerar "negativo"
                        styles.append('color: red; font-weight: bold;')
                # Para costos y gastos, verde si es negativo (mejor), rojo si es positivo (peor)
                elif row['Cuenta'] in ['DESCUENTOS', 'COSTO', 'TOTAL GASTOS OPERATIVOS', 'TOTAL DE OTROS GASTOS',
                                       'FINANCIEROS']:
                    if brecha_val < -0.01:  # Reducción de costo/gasto es buena
                        styles.append('color: green; font-weight: bold;')
                    elif brecha_val > 0.01:  # Aumento de costo/gasto es mala
                        styles.append('color: red; font-weight: bold;')

        style_string = '; '.join(styles)
        return [style_string] * len(row)

    return df.style.apply(estilo_fila, axis=1)


def generar_recomendacion_variables_ia(df_completo):
    if not GEMINI_AVAILABLE:
        return "⚠️ **Error**: La API de Gemini no está configurada."

    estructura_original = get_cached_structure()
    simulable_accounts_details = []

    # Recopilar todas las cuentas simulables con sus valores Actual y Meta
    for cuenta_name, datos in estructura_original.items():
        # Primero, las cuentas de nivel superior que son simulables
        if datos.get(
                'simulable') and 'subcuentas' not in datos:
            actual_val = df_completo[df_completo['Cuenta'] == cuenta_name]['Actual'].iloc[0] if cuenta_name in \
                                                                                                df_completo[
                                                                                                    'Cuenta'].values else \
                datos['actual']
            meta_val = df_completo[df_completo['Cuenta'] == cuenta_name]['Meta'].iloc[0] if cuenta_name in df_completo[
                'Cuenta'].values else datos['meta']

            simulable_accounts_details.append({
                'Variable': cuenta_name,
                'Actual': actual_val,
                'Meta': meta_val
            })

        # Luego, iterar sobre subcuentas para obtener los elementos simulables más granulares
        if 'subcuentas' in datos:
            for subcuenta_name, subdatos_dict_or_item in datos['subcuentas'].items():
                if isinstance(subdatos_dict_or_item, dict) and 'actual' not in subdatos_dict_or_item:
                    # Es un nivel intermedio (ej. VENTAS BRUTAS NACIONAL 16%, COSTO DIRECTO)
                    for subitem_name, itemdatos in subdatos_dict_or_item.items():
                        if itemdatos.get('simulable'):
                            full_name = f"{subcuenta_name} - {subitem_name}"
                            actual_val = itemdatos['actual']
                            meta_val = itemdatos['meta']
                            simulable_accounts_details.append({
                                'Variable': full_name,
                                'Actual': actual_val,
                                'Meta': meta_val
                            })
                elif isinstance(subdatos_dict_or_item, dict) and subdatos_dict_or_item.get('simulable'):
                    # Es una subcuenta directamente simulable (ej. SUELDOS Y SALARIOS)
                    full_name = subcuenta_name
                    actual_val = subdatos_dict_or_item['actual']
                    meta_val = subdatos_dict_or_item['meta']
                    simulable_accounts_details.append({
                        'Variable': full_name,
                        'Actual': actual_val,
                        'Meta': meta_val
                    })

    df_simulable = pd.DataFrame(simulable_accounts_details)
    df_simulable['Desviacion (Actual vs Meta)'] = df_simulable['Actual'] - df_simulable['Meta']
    df_simulable['Abs_Deviation'] = df_simulable['Desviacion (Actual vs Meta)'].abs()

    # Filtrar solo desviaciones significativas y tomar el top N
    df_top_deviations = df_simulable[df_simulable['Abs_Deviation'] > 1000].sort_values(by='Abs_Deviation',
                                                                                       ascending=False).head(
        7)  # Top 7 variables recomendadas

    # Formatear la tabla para el prompt
    top_deviations_table_md = "No se identificaron desviaciones significativas entre el Actual y la Meta para recomendar acciones en este momento."
    if not df_top_deviations.empty:
        top_deviations_table_md = "A continuación, se presenta una tabla con las **variables que muestran las mayores desviaciones monetarias entre su valor Actual y la Meta**. Estas son las áreas clave recomendadas para enfocar tus esfuerzos de simulación, ya que representan el mayor potencial de mejora o riesgo:\n\n"
        top_deviations_table_md += "| Variable | Actual | Meta | Desviación (Actual vs Meta) |\n"
        top_deviations_table_md += "|:---------|-------:|-----:|----------------------------:|\n"
        for _, row in df_top_deviations.iterrows():
            top_deviations_table_md += f"| {row['Variable']} | ${row['Actual']:,.0f} | ${row['Meta']:,.0f} | ${row['Desviacion (Actual vs Meta)']:+,.0f} |\n"
        top_deviations_table_md += "\n"

    # Contexto mejorado de la empresa PORTAWARE
    company_context = """
    La empresa es **PORTAWARE**, fabricante de artículos para el hogar, predominantemente de plástico. Tienen fuertes expectativas de crecimiento a nivel nacional y están comenzando a expandirse en mercados internacionales. El ambiente económico actual es volátil, con presiones inflacionarias en materias primas (plástico, derivados del petróleo) y fluctuaciones en las tasas de cambio. La estrategia de la empresa debe enfocarse en la eficiencia operativa, la gestión de costos, y la optimización de ingresos en un entorno de expansión.
    """

    prompt = f"""
    Eres un Director Financiero (CFO) experto, muy conciso y enfocado en la estrategia. Tu tarea es analizar las desviaciones entre el desempeño financiero **Actual** y la **Meta** establecida para PORTAWARE. Luego, identificar las variables más críticas para que un usuario las mueva en un simulador financiero, siendo muy concreto y ejecutivo en tu recomendación.

    **Contexto de PORTAWARE:**
    {company_context}

    {top_deviations_table_md}

    **Análisis y Recomendación Estratégica (máximo 300 palabras):**
    Basándote únicamente en la tabla de desviaciones anterior y el contexto de PORTAWARE:
    1.  **Diagnóstico Rápido:** ¿Cuál es la tendencia general de estas desviaciones y su implicación para el BAI? ¿Estamos por encima o por debajo de la meta en las áreas clave?
    2.  **Variables Clave y Dirección de Ajuste:** Para las 3-5 variables con mayor desviación (no más de 5):
        * Nombra la variable.
        * Indica brevemente el impacto en el BAI y la conexión con el contexto de PORTAWARE (ej., "impacto directo en ventas y la estrategia de expansión", "reduce margen por costos de materia prima").
        * Especifica la **dirección de la acción recomendada** para la simulación (ej., "incrementar", "disminuir", "optimizar").
        * Menciona una **acción estratégica específica y cuantificable** (si es posible) para esa variable, considerando el mercado y ambiente económico actual.
    3.  **Priorización:** ¿Cuáles 2-3 variables de esta lista deberían ser la *máxima prioridad* para la simulación inicial, y por qué, en línea con el crecimiento nacional e internacional de PORTAWARE?
    4.  **Conclusión General:** Una breve frase de cierre sobre el potencial de mejora estratégica.

    Usa un tono profesional y directo. Formatea tu respuesta con Markdown, incluyendo negritas y listas.
    """
    try:
        model = genai.GenerativeModel('gemini-1.5-flash')
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        return f"❌ **Error al contactar la API de Gemini**: {e}"


def generar_insight_financiero(df_completo, actual_col='Actual', meta_col='Meta', simulado_col='Simulado'):
    if not GEMINI_AVAILABLE:
        return "⚠️ **Error**: La API de Gemini no está configurada."

    df_analisis = df_completo.copy()
    df_analisis['Brecha Actual vs Meta'] = df_analisis[actual_col] - df_analisis[meta_col]
    df_analisis['Brecha Simulado vs Actual'] = df_analisis[simulado_col] - df_analisis[actual_col]
    df_analisis['Brecha Simulado vs Meta'] = df_analisis[simulado_col] - df_analisis[meta_col]

    # Asegurar el orden de las cuentas para el análisis, usando la jerarquía
    cuentas_para_ia = df_analisis.sort_values(by='Jerarquia').reset_index(drop=True)

    # --- CÁLCULO DE RAZONES FINANCIERAS ---
    razones_data = []

    # Obtener valores necesarios para los cálculos, manejando casos donde el denominador es cero
    ventas_netas_actual = cuentas_para_ia.loc[cuentas_para_ia['Cuenta'] == 'VENTAS NETAS', actual_col].iloc[
        0] if 'VENTAS NETAS' in cuentas_para_ia['Cuenta'].values else 0
    margen_bruto_actual = cuentas_para_ia.loc[cuentas_para_ia['Cuenta'] == 'MARGEN BRUTO', actual_col].iloc[
        0] if 'MARGEN BRUTO' in cuentas_para_ia['Cuenta'].values else 0
    ebitda_actual = cuentas_para_ia.loc[cuentas_para_ia['Cuenta'] == 'EBITDA', actual_col].iloc[0] if 'EBITDA' in \
                                                                                                      cuentas_para_ia[
                                                                                                          'Cuenta'].values else 0
    bai_actual = cuentas_para_ia.loc[cuentas_para_ia['Cuenta'] == 'BAI', actual_col].iloc[0] if 'BAI' in \
                                                                                                cuentas_para_ia[
                                                                                                    'Cuenta'].values else 0

    ventas_netas_meta = cuentas_para_ia.loc[cuentas_para_ia['Cuenta'] == 'VENTAS NETAS', meta_col].iloc[
        0] if 'VENTAS NETAS' in cuentas_para_ia['Cuenta'].values else 0
    margen_bruto_meta = cuentas_para_ia.loc[cuentas_para_ia['Cuenta'] == 'MARGEN BRUTO', meta_col].iloc[
        0] if 'MARGEN BRUTO' in cuentas_para_ia['Cuenta'].values else 0
    ebitda_meta = cuentas_para_ia.loc[cuentas_para_ia['Cuenta'] == 'EBITDA', meta_col].iloc[0] if 'EBITDA' in \
                                                                                                  cuentas_para_ia[
                                                                                                      'Cuenta'].values else 0
    bai_meta = cuentas_para_ia.loc[cuentas_para_ia['Cuenta'] == 'BAI', meta_col].iloc[0] if 'BAI' in cuentas_para_ia[
        'Cuenta'].values else 0

    ventas_netas_simulado = cuentas_para_ia.loc[cuentas_para_ia['Cuenta'] == 'VENTAS NETAS', simulado_col].iloc[
        0] if 'VENTAS NETAS' in cuentas_para_ia['Cuenta'].values else 0
    margen_bruto_simulado = cuentas_para_ia.loc[cuentas_para_ia['Cuenta'] == 'MARGEN BRUTO', simulado_col].iloc[
        0] if 'MARGEN BRUTO' in cuentas_para_ia['Cuenta'].values else 0
    ebitda_simulado = cuentas_para_ia.loc[cuentas_para_ia['Cuenta'] == 'EBITDA', simulado_col].iloc[0] if 'EBITDA' in \
                                                                                                          cuentas_para_ia[
                                                                                                              'Cuenta'].values else 0
    bai_simulado = cuentas_para_ia.loc[cuentas_para_ia['Cuenta'] == 'BAI', simulado_col].iloc[0] if 'BAI' in \
                                                                                                    cuentas_para_ia[
                                                                                                        'Cuenta'].values else 0

    # Margen Bruto sobre Ventas Netas
    margen_bruto_vn_actual = (margen_bruto_actual / ventas_netas_actual * 100) if ventas_netas_actual != 0 else 0
    margen_bruto_vn_meta = (margen_bruto_meta / ventas_netas_meta * 100) if ventas_netas_meta != 0 else 0
    margen_bruto_vn_simulado = (
                margen_bruto_simulado / ventas_netas_simulado * 100) if ventas_netas_simulado != 0 else 0
    razones_data.append({'Razon Financiera': 'Margen Bruto sobre Ventas Netas (%)', 'Actual': margen_bruto_vn_actual,
                         'Meta': margen_bruto_vn_meta, 'Simulado': margen_bruto_vn_simulado})

    # Margen EBITDA sobre Ventas Netas
    margen_ebitda_vn_actual = (ebitda_actual / ventas_netas_actual * 100) if ventas_netas_actual != 0 else 0
    margen_ebitda_vn_meta = (ebitda_meta / ventas_netas_meta * 100) if ventas_netas_meta != 0 else 0
    margen_ebitda_vn_simulado = (ebitda_simulado / ventas_netas_simulado * 100) if ventas_netas_simulado != 0 else 0
    razones_data.append({'Razon Financiera': 'Margen EBITDA sobre Ventas Netas (%)', 'Actual': margen_ebitda_vn_actual,
                         'Meta': margen_ebitda_vn_meta, 'Simulado': margen_ebitda_vn_simulado})

    # Margen BAI sobre Ventas Netas
    margen_bai_vn_actual = (bai_actual / ventas_netas_actual * 100) if ventas_netas_actual != 0 else 0
    margen_bai_vn_meta = (bai_meta / ventas_netas_meta * 100) if ventas_netas_meta != 0 else 0
    margen_bai_vn_simulado = (bai_simulado / ventas_netas_simulado * 100) if ventas_netas_simulado != 0 else 0
    razones_data.append({'Razon Financiera': 'Margen BAI sobre Ventas Netas (%)', 'Actual': margen_bai_vn_actual,
                         'Meta': margen_bai_vn_meta, 'Simulado': margen_bai_vn_simulado})

    df_razones = pd.DataFrame(razones_data)
    df_razones['Brecha Actual vs Meta (%)'] = df_razones['Actual'] - df_razones['Meta']
    df_razones['Brecha Simulado vs Actual (%)'] = df_razones['Simulado'] - df_razones['Actual']
    df_razones['Brecha Simulado vs Meta (%)'] = df_razones['Simulado'] - df_razones['Meta']

    # Formatear números para el prompt de IA
    cols_for_prompt_df = cuentas_para_ia[['Cuenta', actual_col, meta_col, simulado_col,
                                          'Brecha Actual vs Meta', 'Brecha Simulado vs Actual',
                                          'Brecha Simulado vs Meta']].copy()

    for col in [actual_col, meta_col, simulado_col, 'Brecha Actual vs Meta', 'Brecha Simulado vs Actual',
                'Brecha Simulado vs Meta']:
        if col in cols_for_prompt_df.columns:
            cols_for_prompt_df[col] = pd.to_numeric(cols_for_prompt_df[col], errors='coerce').fillna(0)
            cols_for_prompt_df[col] = cols_for_prompt_df[col].apply(lambda x: f"{x:+.0f}")

    # Convertir a Markdown la tabla de razones financieras
    razones_table_md = df_razones.to_markdown(index=False, floatfmt="+.2f")

    # Convertir a Markdown la tabla de cuentas para el prompt
    analysis_table_md = cols_for_prompt_df.to_markdown(index=False, numalign="left", stralign="left")

    # Contexto mejorado de la empresa PORTAWARE
    company_context = """
    La empresa es **PORTAWARE**, fabricante de artículos para el hogar, predominantemente de plástico. Tienen fuertes expectativas de crecimiento a nivel nacional y están comenzando a expandirse en mercados internacionales. El ambiente económico actual es volátil, con presiones inflacionarias en materias primas (plástico, derivados del petróleo) y fluctuaciones en las tasas de cambio. La estrategia de la empresa debe enfocarse en la eficiencia operativa, la gestión de costos, y la optimización de ingresos en un entorno de expansión.
    """

    prompt = f"""
    Eres un Director Financiero (CFO) experto, muy conciso y estratégico. Tu tarea es analizar el desempeño financiero de la empresa PORTAWARE comparando el escenario **Actual** con la **Meta** establecida, considerando también el escenario **Simulado** (si hay cambios). Proporciona un diagnóstico ejecutivo y recomendaciones estratégicas concretas, integrando el contexto de la empresa, el mercado, el ambiente económico y las razones financieras clave.

    **Contexto de PORTAWARE:**
    {company_context}

    **Datos Financieros Clave (Valores Absolutos):**
    {analysis_table_md}

    **Razones Financieras (Rentabilidad y Eficiencia):**
    {razones_table_md}

    **Análisis Estratégico y Recomendaciones Ejecutivas (Máximo 400 palabras):**

    1.  **Panorama General y Razones Clave (Actual vs. Meta y Simulado):**
        -   Inicia con un resumen de 1-2 frases sobre el cumplimiento de la meta del BAI y las principales tendencias en las **razones financieras de rentabilidad (Margen Bruto, EBITDA y BAI sobre Ventas Netas)**. ¿Cómo se comparan los porcentajes Actuales, Meta y Simulados? ¿Qué implicaciones tiene para la salud financiera y la estrategia de PORTAWARE?
        -   Identifica las 2-3 áreas principales (Ventas, Costos, Gastos) y las razones financieras asociadas que explican la mayor parte de la desviación del BAI y los márgenes.

    2.  **Causa Raíz y Estrategia (por Área y Razón):**
        -   Para cada área clave y razón identificada, menciona las subcuentas específicas que tuvieron la mayor desviación.
        -   Explica la **causa raíz más probable** de cada desviación, vinculándola directamente al contexto de PORTAWARE, las dinámicas del mercado (expansión, competencia) o el ambiente económico (presiones inflacionarias en plásticos, tipo de cambio).
        -   Analiza cómo el escenario Simulado impacta estas razones y si las mejoras son suficientes y sostenibles para la estrategia de crecimiento nacional e internacional de PORTAWARE.

    3.  **Recomendaciones Estratégicas y Cuantificables:**
        -   Proporciona 2-3 recomendaciones *accionables* para PORTAWARE, enfocadas en mejorar las razones financieras y el BAI, priorizando el cierre de las brechas más grandes o el impulso de la estrategia de expansión. Incluye:
            * **Acción específica** (ej: "Optimizar la compra de polímeros para mejorar el Margen Bruto en X puntos porcentuales").
            * **Razón Financiera impactada** y su potencial de mejora.
            * **Relevancia estratégica** para PORTAWARE, considerando su expansión internacional y el manejo de costos.

    4.  **Conclusión Ejecutiva:**
        -   Una breve declaración sobre la visión general, el potencial de mejora, y los próximos pasos estratégicos para PORTAWARE, con énfasis en la rentabilidad y la eficiencia operativa en su camino de crecimiento.

    Sé conciso, directo y enfocado en la toma de decisiones estratégicas de alto nivel. Usa negritas para resaltar conceptos clave, cursivas para énfasis y listas para las recomendaciones.
    """
    try:
        model = genai.GenerativeModel('gemini-1.5-flash')
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        return f"❌ **Error al contactar la API de Gemini**: {e}"


# --- INTERFAZ DE USUARIO ---
st.title('📊 Simulador Financiero Jerárquico')
st.caption(
    f"Simulación detallada con estructura de subcuentas. Estado de IA: {'✅ Conectada' if GEMINI_AVAILABLE else '❌ No disponible'}")

# Inicializa el estado de las simulaciones
inicializar_simulaciones()

# --- SIDEBAR CON CONTROLES JERÁRQUICOS ---
with st.sidebar:
    st.header("⚙️ Controles de Simulación")

    # --- MÓDULO DE AJUSTE AUTOMÁTICO DE COSTOS ---
    st.markdown("---")
    st.subheader("📦 Ajuste Automático de Costos")

    # Interruptor para activar/desactivar el ajuste de costos
    # Se usa 'key' para que el estado persista en session_state
    st.session_state['ajuste_activo'] = st.checkbox(
        "Activar ajuste automático de costos",
        value=st.session_state.get('ajuste_activo', False),  # Usar el valor existente o False por defecto
        key='ajuste_activo_checkbox_widget',  # Clave única para el widget
        help="Vincula el costo de materiales con el incremento en ventas brutas nacionales"
    )

    if st.session_state['ajuste_activo']:
        # Control deslizante para el porcentaje de ajuste
        # Se usa 'key' para que el valor persista en session_state
        st.session_state['porcentaje_ajuste'] = st.slider(
            "Porcentaje de ajuste sobre aumento de ventas brutas nacionales (%)",
            0, 100, st.session_state.get('porcentaje_ajuste', 45),  # Usar el valor existente o 45 por defecto
            key='porcentaje_ajuste_slider_widget',  # Clave única para el widget
            help="El costo de Materiales A Proceso se ajustará en este porcentaje del cambio en Ventas Brutas Nacionales (Retail, Catálogo y Mayoreo)"
        )
    # else: # Esto es clave: si el ajuste está desactivado, el valor en session_state DEBE ser 0.
    #     st.session_state['sim_COSTO_DIRECTO_MATERIALES_A_PROCESO'] = 0.0 # ¡NO HAGAS ESTO AQUÍ! Genera un loop infinito.
    # La lógica de reseteo debe estar ANTES de generar el df_completo.

    st.markdown("---")
    st.subheader("🎭 Escenarios Rápidos")
    col1_scenario, col2_scenario = st.columns(2)
    with col1_scenario:
        # Botón "Refrescar Simulador" para resetear los valores a cero
        if st.button("🔄 Refrescar Simulador", use_container_width=True,
                     help="Restablece todos los simuladores a cero."):
            for key in list(
                    st.session_state.keys()):
                if key.startswith('sim_'):
                    st.session_state[key] = 0.0
            st.session_state['ajuste_activo'] = False  # Resetear también el ajuste automático
            st.session_state['porcentaje_ajuste'] = 45  # Resetear su valor por defecto
            st.rerun()

    with col2_scenario:
        if st.button("📈 Simular +10% en Ventas Nacionales", use_container_width=True,
                     help="Aumenta en un 10% del valor actual las ventas nacionales de Retail y Mayoreo"):
            estructura = get_cached_structure()
            retail_actual = get_actual_value(estructura, 'VENTAS BRUTAS', 'VENTAS BRUTAS NACIONAL 16%', 'RETAIL')
            mayoreo_actual = get_actual_value(estructura, 'VENTAS BRUTAS', 'VENTAS BRUTAS NACIONAL 16%', 'MAYOREO')
            catalogo_actual = get_actual_value(estructura, 'VENTAS BRUTAS', 'VENTAS BRUTAS NACIONAL 16%', 'CATALOGO')

            st.session_state['sim_VENTAS_BRUTAS_NACIONAL_16%_RETAIL'] = retail_actual * 0.10
            st.session_state['sim_VENTAS_BRUTAS_NACIONAL_16%_MAYOREO'] = mayoreo_actual * 0.10
            st.session_state[
                'sim_VENTAS_BRUTAS_NACIONAL_16%_CATALOGO'] = catalogo_actual * 0.10  # Asegurar que Catalogo también se incluya en la simulación rápida
            st.rerun()

    st.markdown("---")

    estructura = get_cached_structure()
    tab_ventas, tab_costos, tab_gastos, tab_otros = st.tabs(["💰 Ventas", "🏭 Costos", "💸 Gastos", "📊 Otros"])


    def display_number_input_info_with_actual(key, actual_val):
        current_change = st.session_state.get(key, 0.0)
        percentage_change = 0.0
        if actual_val != 0:
            percentage_change = (current_change / actual_val) * 100
        elif current_change != 0:
            percentage_change = float('inf') if current_change > 0 else float('-inf')

        st.caption(
            f"**Valor Actual:** ${actual_val:,.0f} | **Cambio Actual:** ${current_change:,.0f} ({percentage_change:+.1f}%)")


    with tab_ventas:
        st.subheader("Ventas por Canal")
        with st.expander("🏠 Ventas Nacionales", expanded=True):
            for canal, datos in estructura['VENTAS BRUTAS']['subcuentas']['VENTAS BRUTAS NACIONAL 16%'].items():
                key = f"sim_VENTAS_BRUTAS_NACIONAL_16%_{canal}"
                actual_val = get_actual_value(estructura, 'VENTAS BRUTAS', 'VENTAS BRUTAS NACIONAL 16%', canal)
                min_val = -float(actual_val * 2) if actual_val > 0 else -200000000.0
                max_val = float(actual_val * 2) if actual_val > 0 else 200000000.0
                st.number_input(f"{canal}", min_value=min_val, max_value=max_val, value=st.session_state.get(key, 0.0),
                                step=10000.0, key=key)
                display_number_input_info_with_actual(key, actual_val)

        with st.expander("🌎 Ventas Extranjero"):
            for canal, datos in estructura['VENTAS BRUTAS']['subcuentas']['VENTAS BRUTAS EXTRANJERO'].items():
                key = f"sim_VENTAS_BRUTAS_EXTRANJERO_{canal}"
                actual_val = get_actual_value(estructura, 'VENTAS BRUTAS', 'VENTAS BRUTAS EXTRANJERO', canal)
                min_val = -float(actual_val * 2) if actual_val > 0 else -2000000.0
                max_val = float(actual_val * 2) if actual_val > 0 else 2000000.0
                st.number_input(f"{canal} (Ext)", min_value=min_val, max_value=max_val,
                                value=st.session_state.get(key, 0.0), step=1000.0, key=key)
                display_number_input_info_with_actual(key, actual_val)

        key = 'sim_DESCUENTOS'
        actual_desc = get_actual_value(estructura, 'DESCUENTOS')
        min_desc = -float(actual_desc * 2) if actual_desc > 0 else -10000000.0
        max_desc = float(actual_desc * 2) if actual_desc > 0 else 10000000.0
        st.number_input("Descuentos", min_value=min_desc, max_value=max_desc, value=st.session_state.get(key, 0.0),
                        step=5000.0, key=key)
        display_number_input_info_with_actual(key, actual_desc)

        key = 'sim_OTROS_INGRESOS'
        actual_otros_ingresos = get_actual_value(estructura, 'OTROS INGRESOS')
        min_oi = -float(abs(actual_otros_ingresos) * 5) if actual_otros_ingresos != 0 else -5000000.0
        max_oi = float(abs(actual_otros_ingresos) * 5) if actual_otros_ingresos != 0 else 5000000.0
        st.number_input("Otros Ingresos", min_value=min_oi, max_value=max_oi, value=st.session_state.get(key, 0.0),
                        step=100.0, key=key)
        display_number_input_info_with_actual(key, actual_otros_ingresos)

    with tab_costos:
        st.subheader("Estructura de Costos")
        with st.expander("🎯 Costos Directos", expanded=True):
            # Iterar sobre las cuentas de costo directo
            for item, datos in estructura['COSTO']['subcuentas']['COSTO DIRECTO'].items():
                key = f"sim_COSTO_DIRECTO_{item.replace(' ', '_')}"
                actual_val = get_actual_value(estructura, 'COSTO', 'COSTO DIRECTO', item)
                min_val = -float(actual_val * 2) if actual_val > 0 else -50000000.0
                max_val = float(actual_val * 2) if actual_val > 0 else 50000000.0

                # Para "Materiales A Proceso", el control manual se desactiva si el ajuste automático está activo
                if item == 'MATERIALES A PROCESO' and st.session_state.get('ajuste_activo', False):
                    # Mostrar el valor del ajuste automático
                    actual_mat_proceso = get_actual_value(estructura, 'COSTO', 'COSTO DIRECTO', 'MATERIALES A PROCESO')

                    # Calcular el cambio en ventas brutas para mostrar el ajuste en Materiales A Proceso
                    cambio_ventas_brutas_nacional = 0
                    for canal in ['RETAIL', 'CATALOGO', 'MAYOREO']:
                        cambio_ventas_brutas_nacional += st.session_state.get(f"sim_VENTAS_BRUTAS_NACIONAL_16%_{canal}",
                                                                              0.0)

                    porcentaje_ajuste_val = st.session_state.get('porcentaje_ajuste', 45)
                    ajuste_automatico_para_display = (porcentaje_ajuste_val / 100) * cambio_ventas_brutas_nacional

                    st.number_input(f"{item.replace('_', ' ').title()}",
                                    min_value=min_val,
                                    max_value=max_val,
                                    value=ajuste_automatico_para_display,
                                    # Mostrar el valor calculado por el ajuste automático
                                    step=1000.0,
                                    key=key,
                                    disabled=True,  # Desactivar el input manual
                                    help="Este valor se ajusta automáticamente según el 'Ajuste Automático de Costos'."
                                    )
                    st.caption(
                        f"**Valor Actual (Base):** ${actual_val:,.0f} | **Ajuste Automático:** ${ajuste_automatico_para_display:,.0f}"
                    )
                else:
                    st.number_input(f"{item.replace('_', ' ').title()}", min_value=min_val, max_value=max_val,
                                    value=st.session_state.get(key, 0.0), step=1000.0, key=key)
                    display_number_input_info_with_actual(key, actual_val)

        with st.expander("🔧 Costos Indirectos"):
            for item, datos in estructura['COSTO']['subcuentas']['COSTO INDIRECTO'].items():
                key = f"sim_COSTO_INDIRECTO_{item.replace(' ', '_')}"
                actual_val = get_actual_value(estructura, 'COSTO', 'COSTO INDIRECTO', item)
                min_val = -float(actual_val * 2) if actual_val > 0 else -1000000.0
                max_val = float(actual_val * 2) if actual_val > 0 else 1000000.0
                st.number_input(f"{item.replace('_', ' ').title()}", min_value=min_val, max_value=max_val,
                                value=st.session_state.get(key, 0.0), step=100.0, key=key)
                display_number_input_info_with_actual(key, actual_val)

        key = 'sim_OTROS_COSTOS_OTROS_COSTOS'
        actual_otros_costos = get_actual_value(estructura, 'COSTO', 'OTROS COSTOS', 'OTROS COSTOS')
        min_oc = -float(actual_otros_costos * 2) if actual_otros_costos > 0 else -500000.0
        max_oc = float(actual_otros_costos * 2) if actual_otros_costos > 0 else 500000.0
        st.number_input("Otros Costos", min_value=min_oc, max_value=max_oc, value=st.session_state.get(key, 0.0),
                        step=100.0, key=key)
        display_number_input_info_with_actual(key, actual_otros_costos)

    with tab_gastos:
        st.subheader("Gastos Operativos")
        grupos_gastos = {
            "👥 Personal": ['SUELDOS Y SALARIOS', 'PRESTACIONES', 'OTRAS COMPENSACIONES', 'IMPTOS S/NOMINA',
                           'CONTRIBUCIONES PATRONALES', 'SEGURIDAD E HIGIENE', 'GASTOS DE PERSONAL'],
            "🏢 Instalaciones": ['ARRENDAMIENTOS', 'SERVICIOS INSTALACIONES', 'SEGURIDAD Y VIGILANCIA',
                                'MANTENIMIENTOS'],
            "🚚 Logística y Aduanas": ['FLETES EXTERNOS', 'FLETES INTERNOS', 'GASTOS ADUANALES'],
            "🚗 Vehículos y Viajes": ['COMBUSTIBLE', 'ESTACIONAMIENTO', 'TRANSPORTE LOCAL', 'GASTOS DE VIAJE'],
            "💼 Asesorías y Servicios Externos": ['ASESORIAS PM', 'ASESORIAS PF', 'PORTALES CLIENTES'],
            "📦 Suministros": ['SUMINISTROS GENERALES', 'SUMINISTROS OFICINA', 'SUMINISTROS COMPUTO'],
            "📊 Marketing y Diseño": ['MUESTRAS', 'FERIAS Y EXPOSICIONES', 'PUBLICIDAD IMPRESA', 'IMPRESIONES 3D',
                                     'MATERIAL DISEÑO'],
            "⚖️ Legales y Administrativos": ['OTROS IMPUESTOS Y DERECHOS', 'NO DEDUCIBLES', 'SEGUROS Y FIANZAS',
                                             'PATENTES', 'LICENCIAS Y SOFTWARE', 'TIMBRES Y FOLIOS FISCALES',
                                             'COMISION MERCANTIL'],
            "📞 Comunicación y Atención": ['CELULARES', 'MENSAJERIA', 'ATENCION A CLIENTES', 'CUOTAS Y SUSCRIPCIONES'],
            "🎓 Capacitación": ['CAPACITACION Y ENTRENAMIENTO', 'INVENTARIO FÍSICO']
        }

        all_op_expense_accounts = list(estructura['TOTAL GASTOS OPERATIVOS']['subcuentas'].keys())
        cuentas_agrupadas = [cuenta for grupo in grupos_gastos.values() for cuenta in grupo]

        for grupo, cuentas in grupos_gastos.items():
            with st.expander(grupo):
                for cuenta in cuentas:
                    if cuenta in estructura['TOTAL GASTOS OPERATIVOS']['subcuentas']:
                        key = f"sim_{cuenta.replace(' ', '_')}"
                        actual_val = get_actual_value(estructura, 'TOTAL GASTOS OPERATIVOS', cuenta)
                        min_val = -float(actual_val * 2) if actual_val > 0 else -1000000.0
                        max_val = float(actual_val * 2) if actual_val > 0 else 1000000.0
                        st.number_input(f"{cuenta.title()}", min_value=min_val, max_value=max_val,
                                        value=st.session_state.get(key, 0.0), step=100.0, key=key)
                        display_number_input_info_with_actual(key, actual_val)

        with st.expander("Otros Gastos Operativos (No agrupados)"):
            for cuenta in all_op_expense_accounts:
                if cuenta not in cuentas_agrupadas:
                    key = f"sim_{cuenta.replace(' ', '_')}"
                    actual_val = get_actual_value(estructura, 'TOTAL GASTOS OPERATIVOS', cuenta)
                    min_val = -float(actual_val * 2) if actual_val > 0 else -500000.0
                    max_val = float(actual_val * 2) if actual_val > 0 else 500000.0
                    st.number_input(f"{cuenta.title()}", min_value=min_val, max_value=max_val,
                                    value=st.session_state.get(key, 0.0), step=10.0, key=key)
                    display_number_input_info_with_actual(key, actual_val)

    with tab_otros:
        st.subheader("Otros Conceptos")
        key = 'sim_TOTAL_DE_OTROS_GASTOS'
        actual_tot_otros_gastos = get_actual_value(estructura, 'TOTAL DE OTROS GASTOS')
        min_tog = -float(actual_tot_otros_gastos * 2) if actual_tot_otros_gastos > 0 else -1000000.0
        max_tog = float(actual_tot_otros_gastos * 2) if actual_tot_otros_gastos > 0 else 1000000.0
        st.number_input("Total Otros Gastos", min_value=min_tog, max_value=max_tog,
                        value=st.session_state.get(key, 0.0), step=1000.0, key=key)
        display_number_input_info_with_actual(key, actual_tot_otros_gastos)

        st.subheader("Conceptos Financieros")
        for concepto in ['GASTOS FINANCIEROS', 'PRODUCTOS FINANCIEROS', 'RESULTADO CAMBIARIO']:
            key = f"sim_{concepto.replace(' ', '_')}"
            actual_val = get_actual_value(estructura, 'FINANCIEROS', concepto)

            if actual_val > 0:
                min_val = -float(actual_val * 2)
                max_val = float(actual_val * 2)
            elif actual_val < 0:
                min_val = float(actual_val * 2)
                max_val = -float(actual_val * 2)
            else:
                min_val = -500000.0
                max_val = 500000.0
            st.number_input(f"{concepto.title()}", min_value=min_val, max_value=max_val,
                            value=st.session_state.get(key, 0.0), step=100.0, key=key)
            display_number_input_info_with_actual(key, actual_val)

# --- CONTENIDO PRINCIPAL ---
# Obtener cambios actuales de todos los simuladores manuales
changes = {key: value for key, value in st.session_state.items() if key.startswith('sim_')}

# Lógica CLAVE para el ajuste automático de costos
key_materiales_proceso = 'sim_COSTO_DIRECTO_MATERIALES_A_PROCESO'
if st.session_state.get('ajuste_activo', False):
    # Si el ajuste automático está activo, calcula y aplica el ajuste
    cambio_ventas_brutas_nacional = 0
    for canal in ['RETAIL', 'CATALOGO', 'MAYOREO']:
        key_ventas_nacional = f"sim_VENTAS_BRUTAS_NACIONAL_16%_{canal}"
        cambio_ventas_brutas_nacional += st.session_state.get(key_ventas_nacional, 0.0)

    porcentaje_ajuste = st.session_state.get('porcentaje_ajuste', 45)
    ajuste_materiales = (porcentaje_ajuste / 100) * cambio_ventas_brutas_nacional
    changes[key_materiales_proceso] = ajuste_materiales
else:
    # Si el ajuste automático NO está activo, asegura que el cambio en Materiales A Proceso sea cero
    changes[key_materiales_proceso] = 0.0
    # Opcional: Si quieres que el usuario pueda ingresar un valor manual cuando el ajuste está apagado,
    # necesitarías que el number_input para Materiales A Proceso NO esté disabled cuando ajuste_activo es False.
    # En ese caso, la línea `changes[key_materiales_proceso] = 0.0` se ejecutaría solo si no hay un input manual para esa variable.
    # Por ahora, con disabled=True, esta línea es necesaria para resetear el efecto al desactivar.

# Generar dataframe con los cambios actualizados
df_completo = generar_dataframe_completo(changes)
df_variables_mod = obtener_variables_modificadas(changes)

tab1, tab2, tab3 = st.tabs(["📊 Dashboard de Brechas", "📈 Análisis Visual", "🤖 IA: Brecha a Meta y Razones"])

with tab1:
    st.header("Dashboard de Brechas vs. Meta")

    # Métricas principales - Comparar Simulado vs Meta
    col1, col2, col3, col4 = st.columns(4)
    metricas = {'VENTAS NETAS': col1, 'MARGEN BRUTO': col2, 'EBITDA': col3, 'BAI': col4}

    # Obtener valores para mostrar
    ventas_netas = df_completo.loc[df_completo['Cuenta'] == 'VENTAS NETAS', 'Simulado'].iloc[0]
    margen_bruto = df_completo.loc[df_completo['Cuenta'] == 'MARGEN BRUTO', 'Simulado'].iloc[0]
    ebitda = df_completo.loc[df_completo['Cuenta'] == 'EBITDA', 'Simulado'].iloc[0]
    bai = df_completo.loc[df_completo['Cuenta'] == 'BAI', 'Simulado'].iloc[0]

    ventas_netas_meta = df_completo.loc[df_completo['Cuenta'] == 'VENTAS NETAS', 'Meta'].iloc[0]
    margen_bruto_meta = df_completo.loc[df_completo['Cuenta'] == 'MARGEN BRUTO', 'Meta'].iloc[0]
    ebitda_meta = df_completo.loc[df_completo['Cuenta'] == 'EBITDA', 'Meta'].iloc[0]
    bai_meta = df_completo.loc[df_completo['Cuenta'] == 'BAI', 'Meta'].iloc[0]

    # Calcular diferencias
    diff_ventas_netas = ventas_netas - ventas_netas_meta
    diff_margen_bruto = margen_bruto - margen_bruto_meta
    diff_ebitda = ebitda - ebitda_meta
    diff_bai = bai - bai_meta

    # Mostrar métricas con colores correctos
    col1.metric("VENTAS NETAS", f"${ventas_netas:,.0f}", f"${diff_ventas_netas:+,.0f} vs Meta",
                delta_color="normal" if diff_ventas_netas >= 0 else "inverse")
    col2.metric("MARGEN BRUTO", f"${margen_bruto:,.0f}", f"${diff_margen_bruto:+,.0f} vs Meta",
                delta_color="normal" if diff_margen_bruto >= 0 else "inverse")
    col3.metric("EBITDA", f"${ebitda:,.0f}", f"${diff_ebitda:+,.0f} vs Meta",
                delta_color="normal" if diff_ebitda >= 0 else "inverse")
    col4.metric("BAI", f"${bai:,.0f}", f"${diff_bai:+,.0f} vs Meta",
                delta_color="normal" if diff_bai >= 0 else "inverse")

    # Nuevo botón para la recomendación de variables por IA
    if st.button("🚀 Obtener Recomendación IA de Variables Clave", use_container_width=True, type="secondary"):
        with st.spinner("🧠 El CFO Virtual está analizando las desviaciones para darte recomendaciones..."):
            recomendacion_ia = generar_recomendacion_variables_ia(df_completo)
            st.session_state['recomendacion_ia_dashboard'] = recomendacion_ia

    if 'recomendacion_ia_dashboard' in st.session_state:
        st.markdown("### 💡 Recomendación de Variables Clave por IA")
        st.markdown(st.session_state['recomendacion_ia_dashboard'])
        st.markdown("---")

    # Panel de variables modificadas
    if not df_variables_mod.empty:
        st.subheader("🎯 Variables Modificadas")
        st.dataframe(
            df_variables_mod,
            use_container_width=True,
            hide_index=True
        )
        st.info(
            f"**{len(df_variables_mod)}** variables modificadas\n\nEstas son las palancas que estás utilizando para optimizar el resultado."
        )
    else:
        st.info(
            "🔍 **No hay variables modificadas.** Usa los controles del panel lateral para simular diferentes escenarios."
        )

    # Checkbox de porcentajes
    col_checkbox_percentage = st.columns(1)[0]
    with col_checkbox_percentage:
        mostrar_porcentajes = st.checkbox("📊 Mostrar % vs Ventas Netas", value=True, key="show_percentage_checkbox")

    # Crear df_display con las columnas necesarias
    df_display = df_completo[
        ['Cuenta', 'Actual', 'Simulado', 'Meta', 'Brecha vs Meta (%)', 'Simulado (% VN)', 'Meta (% VN)']].copy()
    df_display.rename(columns={
        'Brecha vs Meta (%)': 'Brecha (% S vs M)',
        'Simulado (% VN)': '% Sim. vs VN',
        'Meta (% VN)': '% Meta vs VN'
    }, inplace=True)

    # Definir las columnas a mostrar según el checkbox de porcentajes
    if mostrar_porcentajes:
        columnas_a_mostrar = ['Cuenta', 'Actual', 'Simulado', '% Sim. vs VN', 'Meta', '% Meta vs VN',
                              'Brecha (% S vs M)']
    else:
        columnas_a_mostrar = ['Cuenta', 'Actual', 'Simulado', 'Meta', 'Brecha (% S vs M)']

    # Formatos para la tabla
    formatos = {
        'Actual': '${:,.0f}',
        'Simulado': '${:,.0f}',
        'Meta': '${:,.0f}',
        '% Sim. vs VN': '{:,.2f}%',
        '% Meta vs VN': '{:,.2f}%',
        'Brecha (% S vs M)': '{:+.2f}%'
    }

    st.subheader("Análisis Comparativo Detallado")
    st.dataframe(aplicar_estilo_financiero(df_display[columnas_a_mostrar]).format(formatos), use_container_width=True)

with tab2:
    st.header("Análisis Visual Intuitivo")
    st.info("Estos gráficos te ayudan a identificar rápidamente los puntos clave de tu simulación.")
    col1, col2 = st.columns(2)
    with col1:
        st.subheader("Puente de Utilidad (Waterfall)")
        df_sim = df_completo.set_index('Cuenta')['Simulado']
        fig_waterfall = go.Figure(go.Waterfall(
            name="Simulado", orientation="v",
            measure=['absolute', 'relative', 'total', 'relative', 'total', 'relative', 'total', 'relative', 'absolute'],
            x=['Ventas Netas', 'Costo', 'Margen Bruto', 'Gastos Op.', 'EBITDA Op.', 'Otros Gastos', 'EBITDA',
               'Financieros', 'BAI'],
            y=[df_sim.get('VENTAS NETAS', 0), -df_sim.get('COSTO', 0), 0, -df_sim.get('TOTAL GASTOS OPERATIVOS', 0), 0,
               -df_sim.get('TOTAL DE OTROS GASTOS', 0), 0, -df_sim.get('FINANCIEROS', 0), 0],
            totals={'marker': {'color': PALETA_GRAFICOS['Actual']}},
            increasing={'marker': {'color': PALETA_GRAFICOS['Positivo']}},
            decreasing={'marker': {'color': PALETA_GRAFICOS['Negativo']}}))
        st.plotly_chart(fig_waterfall, use_container_width=True, key="waterfall_chart")

    with col2:
        st.subheader("Composición de Costos y Gastos")
        df_costs = df_completo.set_index('Cuenta')
        fig_pie = px.pie(
            values=[
                abs(df_costs.loc['COSTO', 'Simulado']),
                abs(df_costs.loc['TOTAL GASTOS OPERATIVOS', 'Simulado']),
                abs(df_costs.loc['TOTAL DE OTROS GASTOS', 'Simulado']),
                abs(df_costs.loc['FINANCIEROS', 'Simulado'])
            ],
            names=['Costos', 'Gastos Operativos', 'Otros Gastos', 'Financieros'],
            hole=0.4,
            color_discrete_sequence=['#F79F1F', '#FF6B6B', '#4ECDC4', '#FFD166']
        )
        st.plotly_chart(fig_pie, use_container_width=True, key="pie_chart")

with tab3:
    st.header("🤖 IA: Análisis Estratégico (Actual vs. Meta vs. Simulación)")
    st.info(
        "Esta herramienta utiliza IA para analizar tus escenarios, proporcionando un análisis profundo y recomendaciones estratégicas, incluyendo razones financieras clave.")
    if st.button("🚀 Generar Análisis Estratégico", use_container_width=True, type="primary"):
        with st.spinner("🧠 El CFO Virtual está analizando tus escenarios..."):
            informe = generar_insight_financiero(df_completo)
            st.session_state['informe_ia'] = informe

    if 'informe_ia' in st.session_state:
        st.markdown(st.session_state['informe_ia'])