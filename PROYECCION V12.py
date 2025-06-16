import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st
import google.generativeai as genai

# --- CONFIGURACIÓN INICIAL ---
# Configuración inicial de la página para un layout amplio y sidebar expandido
st.set_page_config(page_title="Simulador Financiero Jerárquico PORTAWARE", layout="wide", initial_sidebar_state="expanded")

# --- OCULTAR ELEMENTOS POR DEFECTO DE STREAMLIT (para una interfaz más limpia y profesional) ---
# Este bloque de CSS se inyecta en la aplicación para ocultar el menú principal,
# el pie de página "Made with Streamlit" y cualquier botón de despliegue o icono de GitHub.
hide_st_style = """
<style>
#MainMenu {visibility: hidden;}
footer {visibility: hidden;}
header {visibility: hidden;}
/* Oculta el botón de "Deploy" si aparece en la esquina superior derecha */
.stAppDeployButton {display:none;} 
/* Oculta el icono de GitHub/Source Code o cualquier "viewer badge" */
.css-1jc7ptx, .e1ewe7hr3, .viewerBadge_container__1QSob, 
.styles_viewerBadge__1yB5_, .viewerBadge_link__1S137, 
.viewerBadge_text__1JaDK {
    display: none !important;
}
</style>
"""
st.markdown(hide_st_style, unsafe_allow_html=True)

# --- FIN DE OCULTAR ELEMENTOS POR DEFECTO DE STREAMLIT ---

# Configuración de Gemini AI
try:
    genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
    GEMINI_AVAILABLE = True
except (FileNotFoundError, KeyError):
    GEMINI_AVAILABLE = False
    st.warning(
        "⚠️ **Advertencia**: La clave de API de Gemini no está configurada en `st.secrets`. Las funcionalidades de IA no estarán disponibles."
    )

# Paleta de colores profesional y extendida
PALETA_GRAFICOS = {
    'Actual': '#0077B6',   # Azul profesional
    'Simulado': '#F79F1F', # Naranja vibrante
    'Meta': '#00A896',     # Verde azulado
    'Positivo': '#2ECC71', # Verde claro (para mejoras)
    'Negativo': '#E74C3C',  # Rojo tomate (para deterioros)

    # NUEVOS COLORES PARA INGRESOS Y EGRESOS
    'Ingresos': '#8A2BE2', # Morado para ingresos (un poco más claro para estética)
    'Egresos': '#FF6347',  # Rojo claro/coral para egresos (agradable a la vista)
    'Neutro': '#CCCCCC'    # Gris para elementos neutros o que no se destaquen
}


# --- DATOS ESTRUCTURADOS ---
def obtener_estructura_cuentas():
    """Retorna la estructura completa de cuentas con jerarquía para PORTAWARE."""
    return {
        # Nivel 4 - VENTAS BRUTAS (INGRESO)
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

        # Nivel 5 - DESCUENTOS Y OTROS (DESCUENTOS son una reducción de ingresos, OTROS INGRESOS es un ingreso)
        'DESCUENTOS': {'jerarquia': '5', 'tipo': 'simple', 'actual': 14370489, 'meta': 14608084, 'simulable': True},
        'OTROS INGRESOS': {'jerarquia': '5.3', 'tipo': 'simple', 'actual': -7071, 'meta': 0, 'simulable': True},

        # Nivel 6 - VENTAS NETAS (INGRESO CLAVE)
        'VENTAS NETAS': {'jerarquia': '6', 'tipo': 'formula', 'formula': 'VENTAS BRUTAS - DESCUENTOS + OTROS INGRESOS'},

        # Nivel 7 - COSTOS (EGRESO)
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

        # Nivel 9 - GASTOS OPERATIVOS (EGRESO)
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
        # CORRECCIÓN: La fórmula de EBITDA Operativa debe ser (Ventas Netas - Costo - TOTAL GASTOS OPERATIVOS)
        'EBITDA OPERATIVA': {'jerarquia': '10', 'tipo': 'formula', 'formula': 'VENTAS NETAS - COSTO - TOTAL GASTOS OPERATIVOS'},
        'TOTAL DE OTROS GASTOS': {'jerarquia': '11', 'tipo': 'simple', 'actual': 2362914, 'meta': 0, 'simulable': True}, # EGRESO
        'EBITDA': {'jerarquia': '12', 'tipo': 'formula', 'formula': 'EBITDA OPERATIVA - TOTAL DE OTROS GASTOS'},
        'FINANCIEROS': { # EGRESO FINANCIERO (suma de sus componentes)
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


# Función auxiliar para obtener el valor actual de una cuenta
def get_actual_value(estructura, account_key, sub_account_key=None, sub_item_key=None):
    if sub_account_key and sub_item_key:
        return estructura.get(account_key, {}).get('subcuentas', {}).get(sub_account_key, {}).get(sub_item_key, {}).get(
            'actual', 0)
    elif sub_account_key:
        return estructura.get(account_key, {}).get('subcuentas', {}).get(sub_account_key, {}).get('actual', 0)
    else:
        return estructura.get(account_key, {}).get('actual', 0)


def inicializar_simulaciones():
    """Inicializa el estado de las simulaciones y controles en st.session_state."""
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
    # Inicializa el estado para la vista móvil simplificada de la tabla
    if 'mobile_view_checkbox' not in st.session_state:
        st.session_state['mobile_view_checkbox'] = False


def calculate_account_value(_estructura, scenario, changes):
    """Calcula los valores de las cuentas para un escenario dado (actual, meta, simulado)."""
    results = {}

    def get_val(cuenta):
        # Si ya calculamos esta cuenta en esta corrida, devolver el valor
        if cuenta in results:
            return results[cuenta]

        datos = _estructura.get(cuenta)
        if not datos:
            return 0 # Devolver 0 si la cuenta no existe o no tiene datos

        valor = 0
        if datos['tipo'] == 'simple':
            base_value = datos['actual'] if scenario == 'actual' else datos.get('meta', 0) if scenario == 'meta' else datos['actual']
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
                        base_value = itemdatos['actual'] if scenario == 'actual' else itemdatos.get('meta', 0) if scenario == 'meta' else itemdatos['actual']
                        if itemdatos.get('simulable') and scenario == 'simulado':
                            key = f"sim_{subcuenta_name.replace(' ', '_')}_{subitem_name.replace(' ', '_')}"
                            cambio_monetario = changes.get(key, 0.0)
                            valor += base_value + cambio_monetario
                        else:
                            valor += base_value
                else: # Es una subcuenta simple dentro de una suma (ej. SUELDOS Y SALARIOS)
                    itemdatos = subdatos_dict_or_item
                    base_value = itemdatos['actual'] if scenario == 'actual' else itemdatos.get('meta', 0) if scenario == 'meta' else itemdatos['actual']
                    if itemdatos.get('simulable') and scenario == 'simulado':
                        key = f"sim_{subcuenta_name.replace(' ', '_')}"
                        cambio_monetario = changes.get(key, 0.0)
                        valor += base_value + cambio_monetario
                    else:
                        valor += base_value
        elif datos['tipo'] == 'formula':
            # La lógica para resolver fórmulas necesita obtener los valores de sus componentes
            temp_formula = datos['formula'].replace(' - ', '|').replace(' + ', '|')
            operands = temp_formula.split('|')
            operators = [char for char in datos['formula'] if char in ['+', '-']]

            first_operand_name = operands[0].strip()
            first_operand_val = results.get(first_operand_name)
            if first_operand_val is None:
                first_operand_val = get_val(first_operand_name)

            valor = first_operand_val
            for i, operand_name_raw in enumerate(operands[1:]):
                op = operators[i]
                current_operand_name = operand_name_raw.strip()
                current_operand_val = results.get(current_operand_name)
                if current_operand_val is None:
                    current_operand_val = get_val(current_operand_name)

                if op == '+':
                    valor += current_operand_val
                elif op == '-':
                    valor -= current_operand_val
        
        # Guardar el resultado antes de devolverlo para evitar recálculos
        results[cuenta] = valor
        return valor

    cuentas_ordenadas = sorted(_estructura.keys(), key=lambda k: float(_estructura[k]['jerarquia']))

    # Realizar múltiples pasadas para asegurar que todas las fórmulas que dependen de otras
    # fórmulas o sumas se calculen correctamente.
    for _ in range(5):
        for cuenta in cuentas_ordenadas:
            if cuenta not in results or _estructura[cuenta]['tipo'] == 'formula':
                get_val(cuenta)

    # Asegurarse de que TODAS las cuentas estén en results al final, incluso las que no son simulables o fórmulas,
    # para que el DataFrame final sea completo.
    for cuenta in cuentas_ordenadas:
        if cuenta not in results:
            if _estructura[cuenta]['tipo'] == 'simple':
                results[cuenta] = _estructura[cuenta]['actual'] if scenario == 'actual' else _estructura[cuenta].get('meta', 0)
            elif _estructura[cuenta]['tipo'] in ['suma', 'suma_gastos']:
                sum_val = 0
                for subcuenta_name, subdatos_dict_or_item in _estructura[cuenta]['subcuentas'].items():
                    if isinstance(subdatos_dict_or_item, dict) and 'actual' not in subdatos_dict_or_item:
                        for subitem_name, itemdatos in subdatos_dict_or_item.items():
                             sum_val += itemdatos['actual'] if scenario == 'actual' else itemdatos.get('meta', 0)
                    else:
                        itemdatos = subdatos_dict_or_item
                        sum_val += itemdatos['actual'] if scenario == 'actual' else itemdatos.get('meta', 0)
                results[cuenta] = sum_val
    return results


def generar_dataframe_completo(changes):
    """Genera el DataFrame completo con valores Actual, Simulado, Meta y brechas/porcentajes."""
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

    df['Brecha vs Meta (%)'] = ((df['Simulado'] - df['Meta']) / df['Meta'].replace(0, pd.NA)) * 100
    df['Brecha Simulado vs Actual (%)'] = ((df['Simulado'] - df['Actual']) / df['Actual'].replace(0, pd.NA)) * 100

    # Asegurarse de que Ventas Netas no sea 0 para evitar ZeroDivisionError en los porcentajes
    ventas_netas_simulado = df.loc[df['Cuenta'] == 'VENTAS NETAS', 'Simulado'].iloc[0] if 'VENTAS NETAS' in df['Cuenta'].values else 1
    ventas_netas_meta = df.loc[df['Cuenta'] == 'VENTAS NETAS', 'Meta'].iloc[0] if 'VENTAS NETAS' in df['Cuenta'].values else 1

    df['Simulado (% VN)'] = (df['Simulado'] / ventas_netas_simulado) * 100 if ventas_netas_simulado != 0 else 0
    df['Meta (% VN)'] = (df['Meta'] / ventas_netas_meta) * 100 if ventas_netas_meta != 0 else 0

    return df


def obtener_variables_modificadas(changes):
    """Retorna un DataFrame con las variables que han sido modificadas, mostrando el cambio monetario y el porcentaje."""
    variables_modificadas = []

    estructura = get_cached_structure()

    sim_key_info = {}
    for cuenta, datos in estructura.items():
        if datos.get('simulable') and 'subcuentas' not in datos:
            sim_key_info[f"sim_{cuenta.replace(' ', '_').replace('/', '_')}"] = {'name': cuenta, 'actual_val': datos['actual']}
        
        if 'subcuentas' in datos:
            for subcuenta, subdatos in datos['subcuentas'].items():
                if isinstance(subdatos, dict) and 'actual' not in subdatos:
                    for subitem, itemdatos in subdatos.items():
                        if itemdatos.get('simulable'):
                            sim_key_info[f"sim_{subcuenta.replace(' ', '_')}_{subitem.replace(' ', '_')}"] = {
                                'name': f"{subcuenta} - {subitem}", 'actual_val': itemdatos['actual']}
                elif isinstance(subdatos, dict) and subdatos.get('simulable'):
                    sim_key_info[f"sim_{subcuenta.replace(' ', '_')}"] = {'name': subcuenta, 'actual_val': subdatos['actual']}

    for key, value in changes.items():
        if key.startswith('sim_') and value != 0.0:
            info = sim_key_info.get(key)
            if info:
                display_name = info['name']
                actual_val = info['actual_val']

                porcentaje_cambio = 0.0
                if actual_val != 0:
                    porcentaje_cambio = (value / actual_val) * 100
                elif value != 0:
                    porcentaje_cambio = float('inf') if value > 0 else float('-inf')

                variables_modificadas.append({
                    'Variable': display_name,
                    'Cambio Monetario': value,
                    'Cambio Porcentual': porcentaje_cambio,
                    'ValorNumAbsoluto': abs(value)
                })

    df_variables = pd.DataFrame(variables_modificadas)
    if not df_variables.empty:
        df_variables = df_variables.sort_values('ValorNumAbsoluto', ascending=False)
        df_variables['Cambio Monetario'] = df_variables['Cambio Monetario'].apply(lambda x: f"${x:,.0f}")
        df_variables['Cambio Porcentual'] = df_variables['Cambio Porcentual'].apply(lambda x: f"{x:+.1f}%" if x != float('inf') and x != float('-inf') else ("+Inf%" if x == float('inf') else "-Inf%"))
        df_variables = df_variables.drop(columns=['ValorNumAbsoluto'])
    return df_variables


# Función para aplicar estilos financieros a la tabla de DataFrame
def aplicar_estilo_financiero(df):
    def estilo_fila(row):
        styles = []
        # Cuentas clave para resaltar
        cuentas_ingresos = ['VENTAS BRUTAS', 'VENTAS NETAS', 'OTROS INGRESOS']
        cuentas_egresos = ['DESCUENTOS', 'COSTO', 'TOTAL GASTOS OPERATIVOS', 'TOTAL DE OTROS GASTOS', 'FINANCIEROS']
        cuentas_resultados = ['MARGEN BRUTO', 'EBITDA OPERATIVA', 'EBITDA', 'BAI']

        # Estilo para ingresos (morado claro)
        if row['Cuenta'] in cuentas_ingresos:
            styles.append(f'background-color: {PALETA_GRAFICOS["Ingresos"]}15;') # Usamos un alpha para que sea sutil
            styles.append('font-weight: bold;')
        # Estilo para egresos (rojo claro/coral)
        elif row['Cuenta'] in cuentas_egresos:
            styles.append(f'background-color: {PALETA_GRAFICOS["Egresos"]}15;') # Usamos un alpha para que sea sutil
            styles.append('font-weight: bold;')
        # Estilo para resultados intermedios/finales (verde azulado claro)
        elif row['Cuenta'] in cuentas_resultados:
            styles.append('background-color: rgba(0, 168, 150, 0.1);') # Ya tiene alpha, se mantiene
            styles.append('font-weight: bold;')

        # Estilo para celdas de brecha (mejorado para claridad)
        if 'Brecha (% S vs M)' in row.index:
            brecha_val = row['Brecha (% S vs M)']
            if pd.notna(brecha_val):
                # Para ingresos y ganancias, verde si es positivo, rojo si es negativo
                if row['Cuenta'] in (cuentas_ingresos + cuentas_resultados):
                    if brecha_val > 0.01:
                        styles.append('color: green; font-weight: bold;')
                    elif brecha_val < -0.01:
                        styles.append('color: red; font-weight: bold;')
                # Para costos y gastos, verde si es negativo (mejor), rojo si es positivo (peor)
                elif row['Cuenta'] in cuentas_egresos:
                    if brecha_val < -0.01:
                        styles.append('color: green; font-weight: bold;')
                    elif brecha_val > 0.01:
                        styles.append('color: red; font-weight: bold;')

        style_string = '; '.join(styles)
        return [style_string] * len(row)

    return df.style.apply(estilo_fila, axis=1)


def generar_recomendacion_variables_ia(df_completo):
    """Genera recomendaciones de variables clave para simular usando IA."""
    if not GEMINI_AVAILABLE:
        return "⚠️ **Error**: La API de Gemini no está configurada."

    estructura_original = get_cached_structure()
    simulable_accounts_details = []

    for cuenta_name, datos in estructura_original.items():
        if datos.get('simulable') and 'subcuentas' not in datos:
            actual_val = df_completo[df_completo['Cuenta'] == cuenta_name]['Actual'].iloc[0] if cuenta_name in df_completo['Cuenta'].values else datos['actual']
            meta_val = df_completo[df_completo['Cuenta'] == cuenta_name]['Meta'].iloc[0] if cuenta_name in df_completo['Cuenta'].values else datos['meta']
            simulable_accounts_details.append({
                'Variable': cuenta_name, 'Actual': actual_val, 'Meta': meta_val
            })

        if 'subcuentas' in datos:
            for subcuenta_name, subdatos_dict_or_item in datos['subcuentas'].items():
                if isinstance(subdatos_dict_or_item, dict) and 'actual' not in subdatos_dict_or_item:
                    for subitem_name, itemdatos in subdatos_dict_or_item.items():
                        if itemdatos.get('simulable'):
                            full_name = f"{subcuenta_name} - {subitem_name}"
                            actual_val = itemdatos['actual']
                            meta_val = itemdatos['meta']
                            simulable_accounts_details.append({
                                'Variable': full_name, 'Actual': actual_val, 'Meta': meta_val
                            })
                elif isinstance(subdatos_dict_or_item, dict) and subdatos_dict_or_item.get('simulable'):
                    full_name = subcuenta_name
                    actual_val = subdatos_dict_or_item['actual']
                    meta_val = subdatos_dict_or_item['meta']
                    simulable_accounts_details.append({
                        'Variable': full_name, 'Actual': actual_val, 'Meta': meta_val
                    })

    df_simulable = pd.DataFrame(simulable_accounts_details)
    df_simulable['Desviacion (Actual vs Meta)'] = df_simulable['Actual'] - df_simulable['Meta']
    df_simulable['Abs_Deviation'] = df_simulable['Desviacion (Actual vs Meta)'].abs()

    df_top_deviations = df_simulable[df_simulable['Abs_Deviation'] > 1000].sort_values(by='Abs_Deviation', ascending=False).head(7)

    top_deviations_table_md = "No se identificaron desviaciones significativas entre el Actual y la Meta para recomendar acciones en este momento."
    if not df_top_deviations.empty:
        top_deviations_table_md = "A continuación, se presenta una tabla con las **variables que muestran las mayores desviaciones monetarias entre su valor Actual y la Meta**. Estas son las áreas clave recomendadas para enfocar tus esfuerzos de simulación, ya que representan el mayor potencial de mejora o riesgo:\n\n"
        top_deviations_table_md += "| Variable | Actual | Meta | Desviación (Actual vs Meta) |\n"
        top_deviations_table_md += "|:---------|-------:|-----:|----------------------------:|\n"
        for _, row in df_top_deviations.iterrows():
            top_deviations_table_md += f"| {row['Variable']} | ${row['Actual']:,.0f} | ${row['Meta']:,.0f} | ${row['Desviacion (Actual vs Meta)']:+,.0f} |\n"
        top_deviations_table_md += "\n"

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
    """Genera un análisis estratégico detallado con IA, incluyendo razones financieras."""
    if not GEMINI_AVAILABLE:
        return "⚠️ **Error**: La API de Gemini no está configurada."

    df_analisis = df_completo.copy()
    df_analisis['Brecha Actual vs Meta'] = df_analisis[actual_col] - df_analisis[meta_col]
    df_analisis['Brecha Simulado vs Actual'] = df_analisis[simulado_col] - df_analisis[actual_col]
    df_analisis['Brecha Simulado vs Meta'] = df_analisis[simulado_col] - df_analisis[meta_col]

    cuentas_para_ia = df_analisis.sort_values(by='Jerarquia').reset_index(drop=True)

    # --- CÁLCULO DE RAZONES FINANCIERAS ---
    razones_data = []

    # Obtener valores necesarios para los cálculos, manejando casos donde el denominador es cero
    ventas_netas_actual = cuentas_para_ia.loc[cuentas_para_ia['Cuenta'] == 'VENTAS NETAS', actual_col].iloc[0] if 'VENTAS NETAS' in cuentas_para_ia['Cuenta'].values else 1
    margen_bruto_actual = cuentas_para_ia.loc[cuentas_para_ia['Cuenta'] == 'MARGEN BRUTO', actual_col].iloc[0] if 'MARGEN BRUTO' in cuentas_para_ia['Cuenta'].values else 0
    ebitda_actual = cuentas_para_ia.loc[cuentas_para_ia['Cuenta'] == 'EBITDA', actual_col].iloc[0] if 'EBITDA' in cuentas_para_ia['Cuenta'].values else 0
    bai_actual = cuentas_para_ia.loc[cuentas_para_ia['Cuenta'] == 'BAI', actual_col].iloc[0] if 'BAI' in cuentas_para_ia['Cuenta'].values else 0

    ventas_netas_meta = cuentas_para_ia.loc[cuentas_para_ia['Cuenta'] == 'VENTAS NETAS', meta_col].iloc[0] if 'VENTAS NETAS' in cuentas_para_ia['Cuenta'].values else 1
    margen_bruto_meta = cuentas_para_ia.loc[cuentas_para_ia['Cuenta'] == 'MARGEN BRUTO', meta_col].iloc[0] if 'MARGEN BRUTO' in cuentas_para_ia['Cuenta'].values else 0
    ebitda_meta = cuentas_para_ia.loc[cuentas_para_ia['Cuenta'] == 'EBITDA', meta_col].iloc[0] if 'EBITDA' in cuentas_para_ia['Cuenta'].values else 0
    bai_meta = cuentas_para_ia.loc[cuentas_para_ia['Cuenta'] == 'BAI', meta_col].iloc[0] if 'BAI' in cuentas_para_ia['Cuenta'].values else 0

    ventas_netas_simulado = cuentas_para_ia.loc[cuentas_para_ia['Cuenta'] == 'VENTAS NETAS', simulado_col].iloc[0] if 'VENTAS NETAS' in cuentas_para_ia['Cuenta'].values else 1
    margen_bruto_simulado = cuentas_para_ia.loc[cuentas_para_ia['Cuenta'] == 'MARGEN BRUTO', simulado_col].iloc[0] if 'MARGEN BRUTO' in cuentas_para_ia['Cuenta'].values else 0
    ebitda_simulado = cuentas_para_ia.loc[cuentas_para_ia['Cuenta'] == 'EBITDA', simulado_col].iloc[0] if 'EBITDA' in cuentas_para_ia['Cuenta'].values else 0
    bai_simulado = cuentas_para_ia.loc[cuentas_para_ia['Cuenta'] == 'BAI', simulado_col].iloc[0] if 'BAI' in cuentas_para_ia['Cuenta'].values else 0

    # Margen Bruto sobre Ventas Netas
    margen_bruto_vn_actual = (margen_bruto_actual / ventas_netas_actual * 100) if ventas_netas_actual != 0 else 0
    margen_bruto_vn_meta = (margen_bruto_meta / ventas_netas_meta * 100) if ventas_netas_meta != 0 else 0
    margen_bruto_vn_simulado = (margen_bruto_simulado / ventas_netas_simulado * 100) if ventas_netas_simulado != 0 else 0
    razones_data.append({'Razon Financiera': 'Margen Bruto sobre Ventas Netas (%)', 'Actual': margen_bruto_vn_actual, 'Meta': margen_bruto_vn_meta, 'Simulado': margen_bruto_vn_simulado})

    # Margen EBITDA sobre Ventas Netas
    margen_ebitda_vn_actual = (ebitda_actual / ventas_netas_actual * 100) if ventas_netas_actual != 0 else 0
    margen_ebitda_vn_meta = (ebitda_meta / ventas_netas_meta * 100) if ventas_netas_meta != 0 else 0
    margen_ebitda_vn_simulado = (ebitda_simulado / ventas_netas_simulado * 100) if ventas_netas_simulado != 0 else 0
    razones_data.append({'Razon Financiera': 'Margen EBITDA sobre Ventas Netas (%)', 'Actual': margen_ebitda_vn_actual, 'Meta': margen_ebitda_vn_meta, 'Simulado': margen_ebitda_vn_simulado})

    # Margen BAI sobre Ventas Netas
    margen_bai_vn_actual = (bai_actual / ventas_netas_actual * 100) if ventas_netas_actual != 0 else 0
    margen_bai_vn_meta = (bai_meta / ventas_netas_meta * 100) if ventas_netas_meta != 0 else 0
    margen_bai_vn_simulado = (bai_simulado / ventas_netas_simulado * 100) if ventas_netas_simulado != 0 else 0
    razones_data.append({'Razon Financiera': 'Margen BAI sobre Ventas Netas (%)', 'Actual': margen_bai_vn_actual, 'Meta': margen_bai_vn_meta, 'Simulado': margen_bai_vn_simulado})

    df_razones = pd.DataFrame(razones_data)
    df_razones['Brecha Actual vs Meta (%)'] = df_razones['Actual'] - df_razones['Meta']
    df_razones['Brecha Simulado vs Actual (%)'] = df_razones['Simulado'] - df_razones['Actual']
    df_razones['Brecha Simulado vs Meta (%)'] = df_razones['Simulado'] - df_razones['Meta']

    # Formatear números para el prompt de IA (sin comas para evitar problemas de interpretación, pero con signo)
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
    "Simulación detallada con estructura de subcuentas. "
    f"Estado de IA: {'✅ Conectada' if GEMINI_AVAILABLE else '❌ No disponible'}"
)

# Inicializa el estado de las simulaciones
inicializar_simulaciones()

# --- SIDEBAR CON CONTROLES JERÁRQUICOS ---
with st.sidebar:
    st.header("⚙️ Controles de Simulación")

    st.markdown("---")
    st.subheader("📦 Ajuste Automático de Costos")

    # Checkbox para activar/desactivar el ajuste automático de costos
    st.session_state['ajuste_activo'] = st.checkbox(
        "Activar ajuste automático de costos",
        value=st.session_state.get('ajuste_activo', False),
        key='ajuste_activo_checkbox_widget', # Clave única para el widget
        help="Vincula el costo de materiales con el incremento en ventas brutas nacionales"
    )

    if st.session_state['ajuste_activo']:
        # Slider para el porcentaje de ajuste, solo visible si el ajuste está activo
        st.session_state['porcentaje_ajuste'] = st.slider(
            "Porcentaje de ajuste sobre aumento de ventas brutas nacionales (%)",
            0, 100, st.session_state.get('porcentaje_ajuste', 45),
            key='porcentaje_ajuste_slider_widget', # Clave única para el widget
            help="El costo de Materiales A Proceso se ajustará en este porcentaje del cambio en Ventas Brutas Nacionales (Retail, Catálogo y Mayoreo)"
        )
    
    st.markdown("---")
    st.subheader("🎭 Escenarios Rápidos")
    col1_scenario, col2_scenario = st.columns(2)
    with col1_scenario:
        # Botón para refrescar el simulador y resetear todos los valores
        if st.button("🔄 Refrescar Simulador", use_container_width=True,
                     help="Restablece todos los simuladores a cero."):
            for key in list(st.session_state.keys()):
                if key.startswith('sim_'):
                    st.session_state[key] = 0.0
            st.session_state['ajuste_activo'] = False # Resetear también el ajuste automático
            st.session_state['porcentaje_ajuste'] = 45 # Resetear su valor por defecto
            st.session_state['mobile_view_checkbox'] = False # Resetear la vista móvil
            st.rerun()

    with col2_scenario:
        # Botón para simular un aumento del 10% en ventas nacionales específicas
        if st.button("📈 Simular +10% en Ventas Nacionales", use_container_width=True,
                     help="Aumenta en un 10% del valor actual las ventas nacionales de Retail, Catálogo y Mayoreo"):
            estructura = get_cached_structure()
            # Se obtienen los valores actuales para calcular el 10% de aumento
            retail_actual = get_actual_value(estructura, 'VENTAS BRUTAS', 'VENTAS BRUTAS NACIONAL 16%', 'RETAIL')
            mayoreo_actual = get_actual_value(estructura, 'VENTAS BRUTAS', 'VENTAS BRUTAS NACIONAL 16%', 'MAYOREO')
            catalogo_actual = get_actual_value(estructura, 'VENTAS BRUTAS', 'VENTAS BRUTAS NACIONAL 16%', 'CATALOGO')

            # Se aplican los cambios a st.session_state
            st.session_state['sim_VENTAS_BRUTAS_NACIONAL_16%_RETAIL'] = retail_actual * 0.10
            st.session_state['sim_VENTAS_BRUTAS_NACIONAL_16%_MAYOREO'] = mayoreo_actual * 0.10
            st.session_state['sim_VENTAS_BRUTAS_NACIONAL_16%_CATALOGO'] = catalogo_actual * 0.10
            st.rerun()

    st.markdown("---")

    estructura = get_cached_structure()
    # Se usan tabs para organizar los controles y mejorar la navegación en móvil
    tab_ventas, tab_costos, tab_gastos, tab_otros = st.tabs(["💰 Ventas", "🏭 Costos", "💸 Gastos", "📊 Otros"])


    # Función auxiliar para mostrar el valor actual, cambio y porcentaje de cambio debajo de cada input
    def display_number_input_info_with_actual(key, actual_val):
        current_change = st.session_state.get(key, 0.0)
        percentage_change = 0.0
        if actual_val != 0:
            percentage_change = (current_change / actual_val) * 100
        elif current_change != 0: # Si actual_val es 0 pero hay un cambio, el porcentaje es "infinito"
            percentage_change = float('inf') if current_change > 0 else float('-inf')

        st.caption(
            f"**Valor Actual:** ${actual_val:,.0f} | **Cambio:** ${current_change:,.0f} ({percentage_change:+.1f}%)"
        )


    # Sección de Ventas en el sidebar
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

    # Sección de Costos en el sidebar
    with tab_costos:
        st.subheader("Estructura de Costos")
        with st.expander("🎯 Costos Directos", expanded=True):
            for item, datos in estructura['COSTO']['subcuentas']['COSTO DIRECTO'].items():
                key = f"sim_COSTO_DIRECTO_{item.replace(' ', '_')}"
                actual_val = get_actual_value(estructura, 'COSTO', 'COSTO DIRECTO', item)
                min_val = -float(actual_val * 2) if actual_val > 0 else -50000000.0
                max_val = float(actual_val * 2) if actual_val > 0 else 50000000.0

                # Lógica para el campo "Materiales A Proceso"
                if item == 'MATERIALES A PROCESO':
                    if st.session_state.get('ajuste_activo', False):
                        cambio_ventas_brutas_nacional = 0
                        for canal_vn in ['RETAIL', 'CATALOGO', 'MAYOREO']:
                            cambio_ventas_brutas_nacional += st.session_state.get(f"sim_VENTAS_BRUTAS_NACIONAL_16%_{canal_vn}", 0.0)
                        
                        porcentaje_ajuste_val = st.session_state.get('porcentaje_ajuste', 45)
                        ajuste_automatico_para_display = (porcentaje_ajuste_val / 100) * cambio_ventas_brutas_nacional

                        st.number_input(f"{item.replace('_', ' ').title()}", 
                                        min_value=min_val, 
                                        max_value=max_val, 
                                        value=ajuste_automatico_para_display,
                                        step=1000.0, 
                                        key=key, 
                                        disabled=True,
                                        help="Este valor se ajusta automáticamente según el 'Ajuste Automático de Costos'."
                                        )
                        st.caption(
                            f"**Valor Actual (Base):** ${actual_val:,.0f} | **Ajuste Automático:** ${ajuste_automatico_para_display:,.0f}"
                        )
                    else:
                        st.number_input(f"{item.replace('_', ' ').title()}", min_value=min_val, max_value=max_val,
                                        value=st.session_state.get(key, 0.0), step=1000.0, key=key)
                        display_number_input_info_with_actual(key, actual_val)
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

    # Sección de Gastos en el sidebar
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

    # Sección de Otros en el sidebar
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

# Lógica CLAVE para el ajuste automático de costos: se aplica ANTES de generar el dataframe
key_materiales_proceso = 'sim_COSTO_DIRECTO_MATERIALES_A_PROCESO'
if st.session_state.get('ajuste_activo', False):
    # Si el ajuste automático está activo, calcula y aplica el ajuste
    cambio_ventas_brutas_nacional = 0
    # Sumar los cambios de los inputs de ventas nacionales (Retail, Catalogo, Mayoreo)
    for canal in ['RETAIL', 'CATALOGO', 'MAYOREO']:
        key_ventas_nacional = f"sim_VENTAS_BRUTAS_NACIONAL_16%_{canal}"
        cambio_ventas_brutas_nacional += st.session_state.get(key_ventas_nacional, 0.0)

    porcentaje_ajuste = st.session_state.get('porcentaje_ajuste', 45)
    ajuste_materiales = (porcentaje_ajuste / 100) * cambio_ventas_brutas_nacional
    changes[key_materiales_proceso] = ajuste_materiales
else:
    # Si el ajuste automático NO está activo, asegura que el cambio en Materiales A Proceso sea cero
    changes[key_materiales_proceso] = 0.0

# Generar dataframe con los cambios actualizados
df_completo = generar_dataframe_completo(changes)
df_variables_mod = obtener_variables_modificadas(changes)

# Pestañas principales para organizar el contenido en el dashboard
tab1, tab2, tab3 = st.tabs(["📊 Dashboard de Brechas", "📈 Análisis Visual", "🤖 IA: Brecha a Meta y Razones"])

# --- TAB 1: DASHBOARD DE BRECHAS ---
with tab1:
    st.header("Dashboard de Brechas vs. Meta")
    # Mensaje para usuarios móviles indicando dónde están los controles
    st.info("💡 **Consejo móvil:** En dispositivos pequeños, los controles de simulación están en el menú lateral (☰).")

    # Métricas principales (VENTAS NETAS, MARGEN BRUTO, EBITDA, BAI)
    col1, col2, col3, col4 = st.columns(4)
    
    ventas_netas = df_completo.loc[df_completo['Cuenta'] == 'VENTAS NETAS', 'Simulado'].iloc[0]
    margen_bruto = df_completo.loc[df_completo['Cuenta'] == 'MARGEN BRUTO', 'Simulado'].iloc[0]
    ebitda = df_completo.loc[df_completo['Cuenta'] == 'EBITDA', 'Simulado'].iloc[0]
    bai = df_completo.loc[df_completo['Cuenta'] == 'BAI', 'Simulado'].iloc[0]

    ventas_netas_meta = df_completo.loc[df_completo['Cuenta'] == 'VENTAS NETAS', 'Meta'].iloc[0]
    margen_bruto_meta = df_completo.loc[df_completo['Cuenta'] == 'MARGEN BRUTO', 'Meta'].iloc[0]
    ebitda_meta = df_completo.loc[df_completo['Cuenta'] == 'EBITDA', 'Meta'].iloc[0]
    bai_meta = df_completo.loc[df_completo['Cuenta'] == 'BAI', 'Meta'].iloc[0]

    diff_ventas_netas = ventas_netas - ventas_netas_meta
    diff_margen_bruto = margen_bruto - margen_bruto_meta
    diff_ebitda = ebitda - ebitda_meta
    diff_bai = bai - bai_meta

    col1.metric("VENTAS NETAS", f"${ventas_netas:,.0f}", f"${diff_ventas_netas:+,.0f} vs Meta",
                delta_color="normal" if diff_ventas_netas >= 0 else "inverse")
    col2.metric("MARGEN BRUTO", f"${margen_bruto:,.0f}", f"${diff_margen_bruto:+,.0f} vs Meta",
                delta_color="normal" if diff_margen_bruto >= 0 else "inverse")
    col3.metric("EBITDA", f"${ebitda:,.0f}", f"${diff_ebitda:+,.0f} vs Meta",
                delta_color="normal" if diff_ebitda >= 0 else "inverse")
    col4.metric("BAI", f"${bai:,.0f}", f"${diff_bai:+,.0f} vs Meta",
                delta_color="normal" if diff_bai >= 0 else "inverse")

    # Botón para obtener recomendaciones de IA sobre variables clave
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

    # Checkbox para mostrar/ocultar porcentajes y vista simplificada para móvil
    col_checkbox_percentage = st.columns(1)[0]
    with col_checkbox_percentage:
        mostrar_porcentajes = st.checkbox("📊 Mostrar % vs Ventas Netas", value=True, key="show_percentage_checkbox")
        st.session_state['mobile_view_checkbox'] = st.checkbox(
            "📱 Vista simplificada para móvil (menos columnas)",
            value=st.session_state.get('mobile_view_checkbox', False),
            key="mobile_view_checkbox_widget"
        )

    # Crear df_display con las columnas necesarias
    df_display = df_completo[
        ['Cuenta', 'Actual', 'Simulado', 'Meta', 'Brecha vs Meta (%)', 'Simulado (% VN)', 'Meta (% VN)']].copy()
    df_display.rename(columns={
        'Brecha vs Meta (%)': 'Brecha (% S vs M)',
        'Simulado (% VN)': '% Sim. vs VN',
        'Meta (% VN)': '% Meta vs VN'
    }, inplace=True)

    # Definir las columnas a mostrar según los checkboxes de usuario
    columnas_base = ['Cuenta', 'Actual', 'Simulado', 'Meta']
    columnas_porcentajes = ['% Sim. vs VN', '% Meta vs VN']
    columna_brecha = 'Brecha (% S vs M)'

    columnas_final_a_mostrar = []
    
    # Lógica para la vista simplificada en móvil
    if st.session_state.get('mobile_view_checkbox', False):
        columnas_final_a_mostrar.append('Cuenta')
        columnas_final_a_mostrar.append('Simulado')
        columnas_final_a_mostrar.append('Meta')
        if mostrar_porcentajes:
            columnas_final_a_mostrar.extend(col for col in columnas_porcentajes if col in df_display.columns)
        columnas_final_a_mostrar.append(columna_brecha)
    else:
        columnas_final_a_mostrar.extend(col for col in columnas_base if col in df_display.columns)
        if mostrar_porcentajes:
            columnas_final_a_mostrar.extend(col for col in columnas_porcentajes if col in df_display.columns)
        columnas_final_a_mostrar.append(columna_brecha)

    columnas_final_a_mostrar = [col for col in columnas_final_a_mostrar if col in df_display.columns]

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
    st.dataframe(
        aplicar_estilo_financiero(df_display[columnas_final_a_mostrar]).format(formatos),
        use_container_width=True
    )

# --- TAB 2: ANÁLISIS VISUAL ---
with tab2:
    st.header("Análisis Visual Intuitivo")
    st.info("Estos gráficos te ayudan a identificar rápidamente los puntos clave de tu simulación.")
    col1_chart, col2_chart = st.columns(2)
    with col1_chart:
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
        
        fig_waterfall.update_layout(
            margin=dict(l=20, r=20, t=30, b=20),
            height=400,
            xaxis_tickangle=-45
        )
        st.plotly_chart(fig_waterfall, use_container_width=True, key="waterfall_chart")

    with col2_chart:
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
            color_discrete_map={
                'Costos': PALETA_GRAFICOS['Egresos'],
                'Gastos Operativos': PALETA_GRAFICOS['Egresos'],
                'Otros Gastos': PALETA_GRAFICOS['Egresos'],
                'Financieros': PALETA_GRAFICOS['Egresos']
            }
        )
        fig_pie.update_layout(
            margin=dict(l=20, r=20, t=30, b=20),
            height=400,
            legend_orientation="h",
            legend_yanchor="bottom",
            legend_y=-0.2
        )
        st.plotly_chart(fig_pie, use_container_width=True, key="pie_chart")

# --- TAB 3: ANÁLISIS ESTRATÉGICO CON IA ---
with tab3:
    st.header("🤖 IA: Análisis Estratégico (Actual vs. Meta vs. Simulación)")
    st.info(
        "Esta herramienta utiliza IA para analizar tus escenarios, proporcionando un análisis profundo y recomendaciones estratégicas, incluyendo razones financieras clave."
    )
    if st.button("🚀 Generar Análisis Estratégico", use_container_width=True, type="primary"):
        with st.spinner("🧠 El CFO Virtual está analizando tus escenarios..."):
            informe = generar_insight_financiero(df_completo)
            st.session_state['informe_ia'] = informe

    if 'informe_ia' in st.session_state:
        st.markdown(st.session_state['informe_ia'])
