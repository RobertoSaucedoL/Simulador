import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st
import google.generativeai as genai
import json
import os
import numpy as np
from openpyxl import load_workbook
from pathlib import Path
from datetime import datetime

# --- OBTENER RUTA ACTUAL ---
current_dir = Path(__file__).parent

# --- CONFIGURACIÓN INICIAL ---
st.set_page_config(page_title="Simulador Financiero Jerárquico PORTAWARE", layout="wide",
                   initial_sidebar_state="expanded")

# --- OCULTAR ELEMENTOS DE STREAMLIT (VERSIÓN ACTUALIZADA) ---
hide_st_style = """
<style>
/* Oculta elementos de la interfaz de Streamlit */
#MainMenu {visibility: hidden;}
footer {visibility: hidden;}
header {visibility: hidden;}
.stDeployButton {visibility: hidden;}
[data-testid="stToolbar"] {display: none;}
[data-testid="stDecoration"] {display: none;}
[data-testid="stStatusWidget"] {display: none;}
#stStatusWidget {display: none;}
[data-testid="baseButton-header"] {display: none;}
.st-emotion-cache-1wbqy5l {display: none;}
.st-emotion-cache-1y4p8pa {padding: 0; margin: 0;}

/* Custom style for the small info text below inputs */
.small-input-info p {
    font-size: 0.75rem !important;
    margin-bottom: 2px;
    margin-top: 2px;
}
</style>
"""
st.markdown(hide_st_style, unsafe_allow_html=True)

# --- CONFIGURACIÓN EXCEL DINÁMICA ---
EXCEL_PATH = current_dir / "PY FINANCIERO V2.xlsx"
SHEET_NAME = "PY"

# Verificar si el archivo existe
if not EXCEL_PATH.exists():
    st.error(f"⚠️ Archivo Excel no encontrado en: {EXCEL_PATH}")
    st.info("Por favor, coloca el archivo 'PY FINANCIERO V2.xlsx' en la misma carpeta que este script")
    st.stop()
    
def cargar_excel():
    try:
        wb = load_workbook(EXCEL_PATH, data_only=True)
        sheet = wb[SHEET_NAME]
        
        data = sheet.values
        cols = next(data)
        df = pd.DataFrame(data, columns=cols)
        
        st.session_state.excel_data = df
        st.session_state.last_modified = datetime.now()
        return True
    except Exception as e:
        st.error(f"Error al cargar Excel: {str(e)}")
        return False

# En el sidebar
st.sidebar.markdown("---")
st.sidebar.subheader("Actualización de Datos")

if st.sidebar.button("🔄 Recargar Datos desde Excel", use_container_width=True):
    if cargar_excel():
        st.sidebar.success("¡Datos actualizados correctamente!")
        st.cache_data.clear()
        st.rerun()
    else:
        st.sidebar.error("Error al cargar datos")

# Mostrar última actualización
if 'last_modified' in st.session_state:
    st.sidebar.caption(f"Última actualización: {st.session_state.last_modified.strftime('%Y-%m-%d %H:%M:%S')}")
    
    try:
        import pandas as pd  # Importación local para asegurar disponibilidad
        
        wb = load_workbook(EXCEL_PATH, data_only=True)
        sheet = wb[SHEET_NAME]
        
        # Convertir hoja a DataFrame
        data = sheet.values
        cols = next(data)
        df = pd.DataFrame(data, columns=cols)
        
        # Almacenar en session_state
        st.session_state.excel_data = df
        st.session_state.last_modified = os.path.getmtime(EXCEL_PATH)
        return True
    except Exception as e:
        st.error(f"Error al cargar Excel: {str(e)}")
        return False

# --- OCULTAR ELEMENTOS POR DEFECTO DE STREAMLIT (VERSION MÁS AGRESIVA) ---
hide_st_style = """
<style>
/* Oculta el menú principal de hamburguesa */
#MainMenu {visibility: hidden;}

/* Oculta el pie de página "Made with Streamlit" */
footer {visibility: hidden;}

/* Oculta la barra de cabecera predeterminada de Streamlit */
header {visibility: hidden;}

/* Oculta el botón de "Deploy" si aparece */
.stAppDeployButton {display: none !important;}

/* Oculta todos los "viewer badges", incluyendo la corona, el icono de GitHub y el texto de "View app by..." */
/* Estos selectores cubren varias versiones y ubicaciones posibles del badge */
.viewerBadge_container__1QSob,
.styles_viewerBadge__1yB5_,
.viewerBadge_link__1S137,
.viewerBadge_text__1JaDK,
/* Selectores más generales que a menudo Streamlit usa para sus insignias */
[data-testid="stToolbar"] > div:last-child, /* Targets the last child in the toolbar, often where badges are */
[data-testid="stDecoration"], /* Hides the entire decoration layer, might be too broad but effective */
.css-1jc7ptx.e1ewe7hr3 { /* A common combination of classes for the badge */
    display: none !important;
    visibility: hidden !important; /* Adding visibility hidden for stronger hiding */
    width: 0 !important;
    height: 0 !important;
    overflow: hidden !important; /* Ensure no residual space */
    margin: 0 !important;
    padding: 0 !important;
}

/* Opcional: Si aún ves un pequeño espacio o borde en la parte inferior, puedes ajustar esto */
body {
    padding-bottom: 0 !important;
}

/* Make st.caption text slightly smaller - targeting a common Streamlit caption class */
/* Note: The exact class name can change with Streamlit versions. You might need to inspect it. */
.st-emotion-cache-1f8u60b { /* This is a common class for st.caption in recent versions */
    font-size: 0.75rem !important; /* Adjust as needed, e.g., 0.85rem for slightly larger */
}

/* Custom style for the small info text below inputs */
.small-input-info p {
    font-size: 0.75rem !important; /* Smaller font for these paragraphs */
    margin-bottom: 2px; /* Reduce space between lines */
    margin-top: 2px;
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

# Paleta de colores profesional y extendida (Más marcados y estéticos)
PALETA_GRAFICOS = {
    'Actual': '#1F77B4',  # Azul fuerte
    'Simulado': '#FF7F0E',  # Naranja vibrante
    'Meta': '#2CA02C',  # Verde brillante

    'Positivo': '#28A745',  # Verde para ganancias / mejoras
    'Negativo': '#DC3545',  # Rojo para pérdidas / deterioros

    # Colores para ingresos y egresos en gráficos de composición
    'Ingresos': '#6F42C1',  # Morado oscuro
    'Egresos': '#FD7E14',  # Naranja rojizo
    'Neutro': '#6C757D'  # Gris neutro
}

# --- CONFIGURACIÓN EXCEL DINÁMICA ---
EXCEL_PATH = r"C:\Users\ROBERTO LOPEZ\OneDrive - Porta\Documentos\Analisis Financiero\01 Finanzas\PY FINANCIERO V2.xlsx"
SHEET_NAME = "PY"


def cargar_excel():
    """Carga el archivo Excel y lo almacena en session_state"""
    try:
        # Usamos openpyxl para mantener fórmulas actualizadas
        wb = load_workbook(EXCEL_PATH, data_only=True)
        sheet = wb[SHEET_NAME]

        # Convertir hoja a DataFrame
        data = sheet.values
        cols = next(data)
        df = pd.DataFrame(data, columns=cols)  # <-- Ahora pd está definido

        # Almacenar en session_state
        st.session_state.excel_data = df
        st.session_state.last_modified = os.path.getmtime(EXCEL_PATH)
        return True
    except Exception as e:
        st.error(f"Error al cargar Excel: {str(e)}")
        return False


def obtener_valor_celda(cell_ref):
    """Obtiene el valor de una celda usando referencia Excel (ej: 'B2')"""
    if 'excel_data' not in st.session_state:
        if not cargar_excel():
            return 0.0

    # Convertir referencia de celda a coordenadas
    col_letter = cell_ref[0]
    row_num = int(cell_ref[1:]) - 1  # -1 porque las filas empiezan en 0

    # Convertir letra a índice de columna
    col_num = ord(col_letter) - ord('A')

    try:
        # Obtener valor de la celda
        return st.session_state.excel_data.iloc[row_num, col_num]
    except:
        return 0.0


# --- INICIALIZAR DATOS EXCEL ---
if 'excel_data' not in st.session_state:
    cargar_excel()

# --- VALORES META HARDCODEADOS ---
# Consolidados según la solicitud del usuario y las imágenes
META_VALUES = {
    'VENTAS BRUTAS': {
        'VENTAS BRUTAS NACIONAL 16%': {
            'RETAIL': 168934800,
            'CATALOGO': 5232032,
            'MAYOREO': 57000000
        },
        'VENTAS BRUTAS EXTRANJERO': {
            'RETAIL': 0,
            'CATALOGO': 0,
            'MAYOREO': 0
        }
    },
    'DESCUENTOS': 14608084,
    'OTROS INGRESOS': 0,  # Asumiendo 0 si no se especifica una meta en imagen

    'COSTO': {
        'COSTO DIRECTO': {
            'MATERIALES A PROCESO': 101987820,
            'MANO DE OBRA ARMADO': 4859868
        },
        'COSTO INDIRECTO': {
            'COSTOS DE CALIDAD': 159044,
            'COSTOS DE MOLDES': 366000
        },
        'OTROS COSTOS': 0  # Asumiendo 0 si no se especifica una meta
    },

    # Gastos Operativos (Ajustado para que el total sume 46,738,177)
    'GASTOS_OPERATIVOS_INDIVIDUALES': {
        'SUELDOS Y SALARIOS': 22818917,
        'PRESTACIONES': 0,
        'OTRAS COMPENSACIONES': 0,
        'SEGURIDAD E HIGIENE': 172490,
        'GASTOS DE PERSONAL': 425174,
        'COMBUSTIBLE': 388200,
        'ESTACIONAMIENTO': 143808,
        'TRANSPORTE LOCAL': 180000,
        'GASTOS DE VIAJE': 420000,
        'ASESORIAS PM': 21246,
        'SEGURIDAD Y VIGILANCIA': 41371,
        'SERVICIOS INSTALACIONES': 338864,
        'CELULARES': 144720,
        'SUMINISTROS GENERALES': 144840,
        'SUMINISTROS OFICINA': 66600,
        'SUMINISTROS COMPUTO': 49200,
        'ARRENDAMIENTOS': 6448852,
        'MANTENIMIENTOS': 355000,  # Corrected: Changed from string to integer/float
        'INVENTARIO FÍSICO': 50000,
        'OTROS IMPUESTOS Y DERECHOS': 0,
        'NO DEDUCIBLES': 3000,
        'SEGUROS Y FIANZAS': 185033,
        'CAPACITACION Y ENTRENAMIENTO': 131654,
        'MENSAJERIA': 115400,
        'MUESTRAS': 22800,
        'FERIAS Y EXPOSICIONES': 26200,
        'PUBLICIDAD IMPRESA': 67200,
        'IMPRESIONES 3D': 420000,
        'MATERIAL DISEÑO': 18000,
        'PATENTES': 0,
        'LICENCIAS Y SOFTWARE': 470712,
        'ATENCION A CLIENTES': 0,
        'ASESORIAS PF': 725482,
        'PORTALES CLIENTES': 144475,
        'CUOTAS Y SUSCRIPCIONES': 106218,
        'FLETES EXTERNOS': 7594838,
        'FLETES INTERNOS': 0,
        'IMPTOS S/NOMINA': 658364,
        'CONTRIBUCIONES PATRONALES': 3836805,
        'TIMBRES Y FOLIOS FISCALES': 2714,
        'COMISION MERCANTIL': 0,
        'GASTOS ADUANALES': 173000  # Ajustado para que el total de G.O. sea 46,738,177
    },
    'TOTAL DE OTROS GASTOS': 0,  # Asumiendo 0 si no se especifica una meta

    # Conceptos Financieros (META de la imagen proporcionada)
    'FINANCIEROS_INDIVIDUALES': {
        'GASTOS FINANCIEROS': 828874.64,
        'PRODUCTOS FINANCIEROS': 52800.00,  # Positivo según imagen
        'RESULTADO CAMBIARIO': 981730.62  # Positivo según imagen
    }
}


# --- DATOS ESTRUCTURADOS ---
def obtener_estructura_cuentas():
    """Retorna la estructura completa de cuentas con jerarquía para PORTAWARE."""

    # Mapeo de celdas para gastos operativos (used for actual values)
    gastos_operativos_map_cells = {
        'SUELDOS Y SALARIOS': 'I19', 'PRESTACIONES': 'I20', 'OTRAS COMPENSACIONES': 'I21',
        'SEGURIDAD E HIGIENE': 'I22', 'GASTOS DE PERSONAL': 'I23', 'COMBUSTIBLE': 'I24',
        'ESTACIONAMIENTO': 'I25', 'TRANSPORTE LOCAL': 'I26', 'GASTOS DE VIAJE': 'I27',
        'ASESORIAS PM': 'I28', 'SEGURIDAD Y VIGILANCIA': 'I29', 'SERVICIOS INSTALACIONES': 'I30',
        'CELULARES': 'I31', 'SUMINISTROS GENERALES': 'I32', 'SUMINISTROS OFICINA': 'I33',
        'SUMINISTROS COMPUTO': 'I34', 'ARRENDAMIENTOS': 'I35', 'MANTENIMIENTOS': 'I36',
        'INVENTARIO FÍSICO': 'I37', 'OTROS IMPUESTOS Y DERECHOS': 'I38', 'NO DEDUCIBLES': 'I39',
        'SEGUROS Y FIANZAS': 'I40', 'CAPACITACION Y ENTRENAMIENTO': 'I41', 'MENSAJERIA': 'I42',
        'MUESTRAS': 'I43', 'FERIAS Y EXPOSICIONES': 'I44', 'PUBLICIDAD IMPRESA': 'I45',
        'IMPRESIONES 3D': 'I46', 'MATERIAL DISEÑO': 'I47', 'PATENTES': 'I48',
        'LICENCIAS Y SOFTWARE': 'I49', 'ATENCION A CLIENTES': 'I50', 'ASESORIAS PF': 'I51',
        'PORTALES CLIENTES': 'I52', 'CUOTAS Y SUSCRIPCIONES': 'I53', 'FLETES EXTERNOS': 'I54',
        'FLETES INTERNOS': 'I55', 'IMPTOS S/NOMINA': 'I56', 'CONTRIBUCIONES PATRONALES': 'I57',
        'TIMBRES Y FOLIOS FISCALES': 'I58', 'COMISION MERCANTIL': 'I59', 'GASTOS ADUANALES': 'I60'
    }

    gastos_operativos_subcuentas = {}
    for gasto, cell in gastos_operativos_map_cells.items():
        gastos_operativos_subcuentas[gasto] = {
            'actual': obtener_valor_celda(cell),
            'meta': META_VALUES['GASTOS_OPERATIVOS_INDIVIDUALES'].get(gasto, 0),
            'simulable': True
        }

    return {
        # Nivel 4 - VENTAS BRUTAS (INGRESO)
        'VENTAS BRUTAS': {
            'jerarquia': '4', 'tipo': 'suma',
            'componentes': ['VENTAS BRUTAS NACIONAL 16%', 'VENTAS BRUTAS EXTRANJERO'],
            'subcuentas': {
                'VENTAS BRUTAS NACIONAL 16%': {
                    'RETAIL': {'actual': obtener_valor_celda('I2'),
                               'meta': META_VALUES['VENTAS BRUTAS']['VENTAS BRUTAS NACIONAL 16%']['RETAIL'],
                               'simulable': True},
                    'CATALOGO': {'actual': obtener_valor_celda('I3'),
                                 'meta': META_VALUES['VENTAS BRUTAS']['VENTAS BRUTAS NACIONAL 16%']['CATALOGO'],
                                 'simulable': True},
                    'MAYOREO': {'actual': obtener_valor_celda('I4'),
                                'meta': META_VALUES['VENTAS BRUTAS']['VENTAS BRUTAS NACIONAL 16%']['MAYOREO'],
                                'simulable': True}
                },
                'VENTAS BRUTAS EXTRANJERO': {
                    'RETAIL': {'actual': obtener_valor_celda('I5'),
                               'meta': META_VALUES['VENTAS BRUTAS']['VENTAS BRUTAS EXTRANJERO']['RETAIL'],
                               'simulable': True},
                    'CATALOGO': {'actual': obtener_valor_celda('I6'),
                                 'meta': META_VALUES['VENTAS BRUTAS']['VENTAS BRUTAS EXTRANJERO']['CATALOGO'],
                                 'simulable': True},
                    'MAYOREO': {'actual': obtener_valor_celda('I7'),
                                'meta': META_VALUES['VENTAS BRUTAS']['VENTAS BRUTAS EXTRANJERO']['MAYOREO'],
                                'simulable': True}
                }
            }
        },

        # Nivel 5 - DESCUENTOS Y OTROS (DESCUENTOS son una reducción de ingresos, OTROS INGRESOS es un ingreso)
        'DESCUENTOS': {'jerarquia': '5', 'tipo': 'simple', 'actual': obtener_valor_celda('I8'),
                       'meta': META_VALUES['DESCUENTOS'],
                       'simulable': True},
        'OTROS INGRESOS': {'jerarquia': '5.3', 'tipo': 'simple', 'actual': obtener_valor_celda('I9'),
                           'meta': META_VALUES['OTROS INGRESOS'],
                           'simulable': True},

        # Nivel 6 - VENTAS NETAS (INGRESO CLAVE)
        'VENTAS NETAS': {'jerarquia': '6', 'tipo': 'formula', 'formula': 'VENTAS BRUTAS - DESCUENTOS + OTROS INGRESOS'},

        # Nivel 7 - COSTOS (EGRESO)
        'COSTO': {
            'jerarquia': '7', 'tipo': 'suma',
            'componentes': ['COSTO DIRECTO', 'COSTO INDIRECTO', 'OTROS COSTOS'],
            'subcuentas': {
                'COSTO DIRECTO': {
                    'MATERIALES A PROCESO': {'actual': obtener_valor_celda('I12'),
                                             'meta': META_VALUES['COSTO']['COSTO DIRECTO']['MATERIALES A PROCESO'],
                                             'simulable': True},
                    'MANO DE OBRA ARMADO': {'actual': obtener_valor_celda('I13'),
                                            'meta': META_VALUES['COSTO']['COSTO DIRECTO']['MANO DE OBRA ARMADO'],
                                            'simulable': True}
                },
                'COSTO INDIRECTO': {
                    'COSTOS DE CALIDAD': {'actual': obtener_valor_celda('I14'),
                                          'meta': META_VALUES['COSTO']['COSTO INDIRECTO']['COSTOS DE CALIDAD'],
                                          'simulable': True},
                    'COSTOS DE MOLDES': {'actual': obtener_valor_celda('I15'),
                                         'meta': META_VALUES['COSTO']['COSTO INDIRECTO']['COSTOS DE MOLDES'],
                                         'simulable': True}
                },
                'OTROS COSTOS': {
                    'OTROS COSTOS': {'actual': obtener_valor_celda('I16'), 'meta': META_VALUES['COSTO']['OTROS COSTOS'],
                                     'simulable': True}}
            }
        },

        # Nivel 8 - MARGEN BRUTO
        'MARGEN BRUTO': {'jerarquia': '8', 'tipo': 'formula', 'formula': 'VENTAS NETAS - COSTO'},

        # Nivel 9 - GASTOS OPERATIVOS (EGRESO)
        'TOTAL GASTOS OPERATIVOS': {
            'jerarquia': '9', 'tipo': 'suma_gastos',
            'subcuentas': gastos_operativos_subcuentas  # Se asigna el diccionario generado dinámicamente
        },

        # Resto de la estructura
        'EBITDA OPERATIVA': {'jerarquia': '10', 'tipo': 'formula',
                             'formula': 'VENTAS NETAS - COSTO - TOTAL GASTOS OPERATIVOS'},
        'TOTAL DE OTROS GASTOS': {'jerarquia': '11', 'tipo': 'simple', 'actual': obtener_valor_celda('I62'),
                                  'meta': META_VALUES['TOTAL DE OTROS GASTOS'],
                                  'simulable': True},
        'EBITDA': {'jerarquia': '12', 'tipo': 'formula', 'formula': 'EBITDA OPERATIVA - TOTAL DE OTROS GASTOS'},
        'FINANCIEROS': {
            'jerarquia': '13', 'tipo': 'suma',
            'componentes': ['GASTOS FINANCIEROS', 'PRODUCTOS FINANCIEROS', 'RESULTADO CAMBIARIO'],
            'subcuentas': {
                # Valores tomados directamente de la imagen para 'meta' y 'actual'
                'GASTOS FINANCIEROS': {'actual': obtener_valor_celda('I65'),
                                       'meta': META_VALUES['FINANCIEROS_INDIVIDUALES']['GASTOS FINANCIEROS'],
                                       'simulable': True},
                'PRODUCTOS FINANCIEROS': {'actual': obtener_valor_celda('I66'),
                                          'meta': META_VALUES['FINANCIEROS_INDIVIDUALES']['PRODUCTOS FINANCIEROS'],
                                          'simulable': True},
                'RESULTADO CAMBIARIO': {'actual': obtener_valor_celda('I67'),
                                        'meta': META_VALUES['FINANCIEROS_INDIVIDUALES']['RESULTADO CAMBIARIO'],
                                        'simulable': True}
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


# Helper function to get the meta value of a specific simulable account
def get_meta_value(estructura, account_key, sub_account_key=None, sub_item_key=None):
    if sub_account_key and sub_item_key:
        return estructura.get(account_key, {}).get('subcuentas', {}).get(sub_account_key, {}).get(sub_item_key, {}).get(
            'meta', 0)
    elif sub_account_key:
        return estructura.get(account_key, {}).get('subcuentas', {}).get(sub_account_key, {}).get('meta', 0)
    else:
        return estructura.get(account_key, {}).get('meta', 0)


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
    # Remove mobile view checkbox state as it's no longer used
    if 'mobile_view_checkbox' in st.session_state:
        del st.session_state['mobile_view_checkbox']
    # Inicializar el estado de los escenarios guardados
    if 'saved_scenarios' not in st.session_state:
        st.session_state['saved_scenarios'] = {}
        load_scenarios_from_file()  # Load on first run


def calculate_account_value(_estructura, scenario, changes):
    """Calcula los valores de las cuentas para un escenario dado (actual, meta, simulado)."""
    results = {}

    def get_val(cuenta):
        # Si ya calculamos esta cuenta en esta corrida, devolver el valor
        if cuenta in results:
            return results[cuenta]

        datos = _estructura.get(cuenta)
        if not datos:
            return 0  # Devolver 0 si la cuenta no existe o no tiene datos

        valor = 0
        if datos['tipo'] == 'simple':
            base_value = datos['actual'] if scenario == 'actual' else datos.get('meta', 0) if scenario == 'meta' else \
                datos['actual']
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
                else:  # Es una subcuenta simple dentro de una suma (ej. SUELDOS Y SALARIOS)
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
                results[cuenta] = _estructura[cuenta]['actual'] if scenario == 'actual' else _estructura[cuenta].get(
                    'meta', 0)
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
    ventas_netas_simulado = df.loc[df['Cuenta'] == 'VENTAS NETAS', 'Simulado'].iloc[0] if 'VENTAS NETAS' in df[
        'Cuenta'].values else 1
    ventas_netas_meta = df.loc[df['Cuenta'] == 'VENTAS NETAS', 'Meta'].iloc[0] if 'VENTAS NETAS' in df[
        'Cuenta'].values else 1

    df['Simulado (% VN)'] = (df['Simulado'] / ventas_netas_simulado) * 100 if ventas_netas_simulado != 0 else 0
    df['Meta (% VN)'] = (df['Meta'] / ventas_netas_meta) * 100 if ventas_netas_meta != 0 else 0

    return df


def obtener_variables_modificadas(changes):
    """Retorna un DataFrame con las variables que han sido modificadas, mostrando el cambio monetario y el porcentaje."""
    variables_modificadas = []

    estructura = get_cached_structure()

    # Initialize sim_key_info here, outside the loop that populates it
    sim_key_info = {}
    for cuenta, datos in estructura.items():
        # Handle top-level simulable accounts (not nested under 'subcuentas')
        if datos.get('simulable') and 'subcuentas' not in datos:
            sim_key_info[f"sim_{cuenta.replace(' ', '_').replace('/', '_')}"] = {'name': cuenta,
                                                                                 'actual_val': datos['actual']}
        # Handle accounts that have 'subcuentas'
        if 'subcuentas' in datos and isinstance(datos['subcuentas'], dict):
            for subcuenta_name, subdatos_value in datos['subcuentas'].items():
                # Case 1: subdatos_value is a simple simulable account (e.g., 'SUELDOS Y SALARIOS')
                if isinstance(subdatos_value, dict) and 'actual' in subdatos_value and subdatos_value.get('simulable'):
                    full_name = subcuenta_name
                    actual_val = subdatos_value['actual']
                    meta_val = subdatos_value['meta']
                    sim_key_info[f"sim_{subcuenta_name.replace(' ', '_')}"] = {
                        'name': full_name, 'actual_val': subdatos_value['actual']}
                # Case 2: subdatos_value is a nested dictionary of sub-items (e.g., 'COSTO DIRECTO')
                elif isinstance(subdatos_value, dict) and 'actual' not in subdatos_value:
                    for subitem_name, itemdatos in subdatos_value.items():
                        if itemdatos.get('simulable'):
                            full_name = f"{subcuenta_name} - {subitem_name}"
                            actual_val = itemdatos['actual']
                            meta_val = itemdatos['meta']
                            sim_key_info[f"sim_{subcuenta_name.replace(' ', '_')}_{subitem_name.replace(' ', '_')}"] = {
                                'name': full_name, 'actual_val': itemdatos['actual']}
                # Other cases (not simulable or not structured as expected) are ignored

    for key, value in changes.items():
        # Only include if the change is significant or it's not a derived auto-adjusted cost
        if key.startswith('sim_') and value != 0.0 and key != 'sim_COSTO_DIRECTO_MATERIALES_A_PROCESO':
            info = sim_key_info.get(key)
            if info:
                display_name = info['name']
                actual_val = info['actual_val']

                porcentaje_cambio = 0.0
                if actual_val != 0:
                    porcentaje_cambio = (value / actual_val) * 100
                elif value != 0:  # If actual_val is 0 but there's a change, percentage is "infinite"
                    porcentaje_cambio = float('inf') if value > 0 else float('-inf')

                variables_modificadas.append({
                    'Variable': display_name,
                    'Cambio Monetario': value,
                    'Cambio Porcentual': porcentaje_cambio,
                    'ValorNumAbsoluto': abs(value)
                })
    # Add the auto-adjusted "Materiales A Proceso" if adjustment is active and it's changed
    if st.session_state.get('ajuste_activo', False):
        key_materiales_proceso = 'sim_COSTO_DIRECTO_MATERIALES_A_PROCESO'
        ajuste_val = changes.get(key_materiales_proceso, 0.0)
        actual_val_mp = get_actual_value(estructura, 'COSTO', 'COSTO DIRECTO', 'MATERIALES A PROCESO')
        if ajuste_val != 0:  # Only add if there's an actual adjustment
            porcentaje_cambio_mp = 0.0
            if actual_val_mp != 0:
                porcentaje_cambio_mp = (ajuste_val / actual_val_mp) * 100
            elif ajuste_val != 0:
                porcentaje_cambio_mp = float('inf') if ajuste_val > 0 else float('-inf')

            variables_modificadas.append({
                'Variable': 'COSTO DIRECTO - MATERIALES A PROCESO (Ajuste Automático)',
                'Cambio Monetario': ajuste_val,
                'Cambio Porcentual': porcentaje_cambio_mp,
                'ValorNumAbsoluto': abs(ajuste_val)
            })

    df_variables = pd.DataFrame(variables_modificadas)
    if not df_variables.empty:
        df_variables = df_variables.sort_values('ValorNumAbsoluto', ascending=False)
        df_variables['Cambio Monetario'] = df_variables['Cambio Monetario'].apply(lambda x: f"${x:,.0f}")
        df_variables['Cambio Porcentual'] = df_variables['Cambio Porcentual'].apply(
            lambda x: f"{x:+.1f}%" if x != float('inf') and x != float('-inf') else (
                "+Inf%" if x == float('inf') else "-Inf%"))
        df_variables = df_variables.drop(columns=['ValorNumAbsoluto'])
    return df_variables


# Función para aplicar estilos financieros a la tabla de DataFrame
def aplicar_estilo_financiero(df):
    # Cuentas clave para resaltar con negrita y para la lógica de color de brecha
    cuentas_ingresos = ['VENTAS BRUTAS', 'VENTAS NETAS', 'OTROS INGRESOS']
    cuentas_egresos = ['DESCUENTOS', 'COSTO', 'TOTAL GASTOS OPERATIVOS', 'TOTAL DE OTROS GASTOS', 'FINANCIEROS']
    cuentas_resultados = ['MARGEN BRUTO', 'EBITDA OPERATIVA', 'EBITDA', 'BAI']

    def estilo_fila(row):
        # Inicializar una lista de estilos vacíos para cada celda en la fila
        styles = [''] * len(row)

        # Aplicar negrita a la columna 'Cuenta' si está presente y es una cuenta clave
        if 'Cuenta' in row.index and row['Cuenta'] in (cuentas_ingresos + cuentas_egresos + cuentas_resultados):
            try:
                cuenta_idx = list(row.index).index('Cuenta')
                styles[cuenta_idx] = 'font-weight: bold;'
            except ValueError:
                pass

        # Aplicar estilo de color a la columna 'Brecha (% S vs M)'
        if 'Brecha (% S vs M)' in row.index:
            brecha_val = row['Brecha (% S vs M)']
            try:
                brecha_idx = list(row.index).index('Brecha (% S vs M)')
            except ValueError:
                brecha_idx = -1

            if pd.notna(brecha_val) and brecha_idx != -1:
                # Para ingresos y resultados, verde si es positivo, rojo si es negativo
                if row['Cuenta'] in (cuentas_ingresos + cuentas_resultados):
                    if brecha_val > 0.01:
                        styles[brecha_idx] += f'color: {PALETA_GRAFICOS["Positivo"]}; font-weight: bold;'
                    elif brecha_val < -0.01:
                        styles[brecha_idx] += f'color: {PALETA_GRAFICOS["Negativo"]}; font-weight: bold;'
                # Para costos y gastos, verde si es negativo (mejor), rojo si es positivo (peor)
                elif row['Cuenta'] in cuentas_egresos:
                    if brecha_val < -0.01:  # Menor es mejor para gastos (significa que disminuyó el gasto)
                        styles[brecha_idx] += f'color: {PALETA_GRAFICOS["Positivo"]}; font-weight: bold;'
                    elif brecha_val > 0.01:  # Mayor es peor para gastos (significa que aumentó el gasto)
                        styles[brecha_idx] += f'color: {PALETA_GRAFICOS["Negativo"]}; font-weight: bold;'

        return styles

    # Aplica la función de estilo a cada fila del DataFrame
    return df.style.apply(estilo_fila, axis=1)


def generar_recomendacion_variables_ia(df_completo):
    """Genera recomendaciones de variables clave para simular usando IA."""
    if not GEMINI_AVAILABLE:
        return "⚠️ **Error**: La API de Gemini no está configurada."

    estructura_original = get_cached_structure()
    simulable_accounts_details = []

    for cuenta_name, datos in estructura_original.items():
        if datos.get('simulable') and 'subcuentas' not in datos:
            actual_val = df_completo.loc[df_completo['Cuenta'] == cuenta_name, 'Actual'].iloc[0] if cuenta_name in \
                                                                                                    df_completo[
                                                                                                        'Cuenta'].values else \
                datos['actual']
            meta_val = df_completo.loc[df_completo['Cuenta'] == cuenta_name, 'Meta'].iloc[0] if cuenta_name in \
                                                                                                df_completo[
                                                                                                    'Cuenta'].values else \
                datos['meta']
            simulable_accounts_details.append({
                'Variable': cuenta_name, 'Actual': actual_val, 'Meta': meta_val
            })
        elif 'subcuentas' in datos and isinstance(datos['subcuentas'], dict):
            for subcuenta_name, subdatos in datos['subcuentas'].items():
                if isinstance(subdatos, dict) and 'actual' in subdatos and subdatos.get('simulable'):
                    full_name = subcuenta_name
                    actual_val = subdatos['actual']
                    meta_val = subdatos['meta']
                    simulable_accounts_details.append({
                        'Variable': full_name, 'Actual': actual_val, 'Meta': meta_val
                    })
                elif isinstance(subdatos, dict) and 'actual' not in subdatos:  # Nested subaccounts
                    for subitem_name, itemdatos in subdatos.items():
                        if itemdatos.get('simulable'):
                            full_name = f"{subcuenta_name} - {subitem_name}"
                            actual_val = itemdatos['actual']
                            meta_val = itemdatos['meta']
                            simulable_accounts_details.append({
                                'Variable': full_name, 'Actual': actual_val, 'Meta': meta_val
                            })

    df_simulable = pd.DataFrame(simulable_accounts_details)
    df_simulable['Desviacion (Actual vs Meta)'] = df_simulable['Actual'] - df_simulable['Meta']
    df_simulable['Abs_Deviation'] = df_simulable['Desviacion (Actual vs Meta)'].abs()

    df_top_deviations = df_simulable[df_simulable['Abs_Deviation'] > 1000].sort_values(by='Abs_Deviation',
                                                                                       ascending=False).head(7)

    # Initialize top_deviations_table_md here
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

    **Análisis y Recomendación Estratégica (máximo 100 palabras):**
    Basándote únicamente en la tabla de desviaciones anterior y el contexto de PORTAWARE:
    1.  **Diagnóstico Rápido:** ¿Cuál es la tendencia general de estas desviaciones y su implicación para el EBITDA? ¿Estamos por encima o por debajo de la meta en las áreas clave?
    2.  **Variables Clave y Dirección de Ajuste:** Para las 3-5 variables con mayor desviación (no más de 5):
        * Nombra la variable.
        * Indica brevemente el impacto en el BAI y la conexión con el contexto de PORTAWARE (ej., "impacto directo en ventas y la estrategia de expansión", "reduce margen por costos de materia prima").
        * Menciona una **acción estratégica específica y cuantificable** (si es posible) para esa variable, considerando el mercado y ambiente económico actual.
    3.  **Priorización:** ¿Cuáles 2-3 variables (revisa sub cuenta) de esta lista deberían ser la *máxima prioridad* para la simulación inicial, y por qué, en línea con el crecimiento nacional e internacional de PORTAWARE?
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
    ventas_netas_actual = cuentas_para_ia.loc[cuentas_para_ia['Cuenta'] == 'VENTAS NETAS', actual_col].iloc[
        0] if 'VENTAS NETAS' in cuentas_para_ia['Cuenta'].values else 1
    margen_bruto_actual = cuentas_para_ia.loc[cuentas_para_ia['Cuenta'] == 'MARGEN BRUTO', actual_col].iloc[
        0] if 'MARGEN BRUTO' in cuentas_para_ia['Cuenta'].values else 0
    ebitda_actual = cuentas_para_ia.loc[cuentas_para_ia['Cuenta'] == 'EBITDA', actual_col].iloc[0] if 'EBITDA' in \
                                                                                                      cuentas_para_ia[
                                                                                                          'Cuenta'].values else 0
    bai_actual = cuentas_para_ia.loc[cuentas_para_ia['Cuenta'] == 'BAI', actual_col].iloc[0] if 'BAI' in \
                                                                                                cuentas_para_ia[
                                                                                                    'Cuenta'].values else 0

    ventas_netas_meta = cuentas_para_ia.loc[cuentas_para_ia['Cuenta'] == 'VENTAS NETAS', meta_col].iloc[
        0] if 'VENTAS NETAS' in cuentas_para_ia['Cuenta'].values else 1
    margen_bruto_meta = cuentas_para_ia.loc[cuentas_para_ia['Cuenta'] == 'MARGEN BRUTO', meta_col].iloc[
        0] if 'MARGEN BRUTO' in cuentas_para_ia['Cuenta'].values else 0
    ebitda_meta = cuentas_para_ia.loc[cuentas_para_ia['Cuenta'] == 'EBITDA', meta_col].iloc[0] if 'EBITDA' in \
                                                                                                  cuentas_para_ia[
                                                                                                      'Cuenta'].values else 0
    bai_meta = cuentas_para_ia.loc[cuentas_para_ia['Cuenta'] == 'BAI', meta_col].iloc[0] if 'BAI' in cuentas_para_ia[
        'Cuenta'].values else 1

    ventas_netas_simulado = cuentas_para_ia.loc[cuentas_para_ia['Cuenta'] == 'VENTAS NETAS', simulado_col].iloc[
        0] if 'VENTAS NETAS' in cuentas_para_ia['Cuenta'].values else 1
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

    # Retrieve top_deviations_table_md content from session state, or use a placeholder
    # This ensures the prompt can always be constructed, even if the user hasn't clicked
    # the 'Get AI Recommendation' button yet.
    top_deviations_context_for_insight = st.session_state.get('recomendacion_ia_dashboard_content',
                                                              "*(No se ha generado una tabla de desviaciones de variables clave aún. Haz clic en 'Obtener Recomendación IA de Variables Clave' en el Dashboard de Brechas para verla.)*"
                                                              )

    prompt = f"""
    Eres un Director Financiero (CFO) experto, muy conciso y estratégico. Tu tarea es analizar el desempeño financiero de la empresa PORTAWARE comparando el escenario **Actual** con la **Meta** establecida, considerando también el escenario **Simulado** (si hay cambios). Proporciona un diagnóstico ejecutivo y recomendaciones estratégicas concretas, integrando el contexto de la empresa, el mercado, el ambiente económico y las razones financieras clave.

    **Contexto de PORTAWARE:**
    {company_context}

    **Variables Clave con Mayores Desviaciones (si disponibles):**
    {top_deviations_context_for_insight} # Corrected variable name in f-string

    **Datos Financieros Clave (Valores Absolutos):**
    {analysis_table_md}

    **Razones Financieras (Rentabilidad y Eficiencia):**
    {razones_table_md}

    **Análisis Estratégico y Recomendaciones Ejecutivas (Máximo 100 palabras):**

    1.  **Panorama General y Razones Clave (Actual vs. Meta y Simulado):**
        -   Inicia con un resumen de 1-2 frases sobre el cumplimiento de la meta del BAI y las principales tendencias en las **razones financieras **. ¿Cómo se comparan los porcentajes Actuales, Meta y Simulados? ¿Qué implicaciones tiene para la salud financiera y la estrategia de PORTAWARE?
        -   Identifica las 2-3 áreas principales (Ventas, Costos, Gastos) y las razones financieras asociadas que explican la mayor parte de la desviación del BAI y los márgenes.

    2.  **Recomendaciones Estratégicas y Cuantificables:**
        -   Proporciona 2-3 recomendaciones *accionables* para PORTAWARE, enfocadas en mejorar las razones financieras y el BAI, priorizando el cierre de las brechas más grandes o el impulso de la estrategia de expansión. Incluye:
            * **Acción específica** (ej: "Optimizar la compra de polímeros para mejorar el Margen Bruto en X puntos porcentuales").
            * **Razón Financiera impactada** y su potencial de mejora.
            * **Relevancia estratégica** para PORTAWARE, considerando su expansión internacional y el manejo de costos.

    3.  **Conclusión Ejecutiva:**
        -   Una breve declaración sobre la visión general, el potencial de mejora, y los próximos pasos estratégicos para PORTAWARE, con énfasis in the profitability and operational efficiency on its path to growth.

    Sé conciso, directo y enfocado en la toma de decisiones estratégicas de alto nivel. Usa negritas para resaltar conceptos clave, cursivas para énfasis y listas para las recomendaciones.
    """
    try:
        model = genai.GenerativeModel('gemini-1.5-flash')
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        return f"❌ **Error al contactar la API de Gemini**: {e}"


# --- SCENARIO MANAGEMENT FUNCTIONS ---
SCENARIOS_FILE = "saved_scenarios.json"


def load_scenarios_from_file():
    """Loads saved scenarios from a JSON file into st.session_state."""
    if os.path.exists(SCENARIOS_FILE):
        with open(SCENARIOS_FILE, 'r') as f:
            try:
                st.session_state['saved_scenarios'] = json.load(f)
            except json.JSONDecodeError:
                st.session_state['saved_scenarios'] = {}
                st.error("Error al leer el archivo de escenarios guardados. Se reiniciará la lista de escenarios.")
    else:
        st.session_state['saved_scenarios'] = {}


def save_scenarios_to_file():
    """Saves current scenarios from st.session_state to a JSON file."""
    with open(SCENARIOS_FILE, 'w') as f:
        json.dump(st.session_state['saved_scenarios'], f)


def save_current_scenario_callback():
    """Callback to save the current simulation state as a named scenario."""
    scenario_name = st.session_state.new_scenario_name_input
    if scenario_name:
        current_changes = {key: value for key, value in st.session_state.items() if key.startswith('sim_')}
        # Filter out adjustment state variables to only save the manual inputs
        current_changes_filtered = {k: v for k, v in current_changes.items() if
                                    not k.startswith('sim_COSTO_DIRECTO_MATERIALES_A_PROCESO')}

        st.session_state['saved_scenarios'][scenario_name] = current_changes_filtered
        save_scenarios_to_file()
        st.success(f"Escenario '{scenario_name}' guardado exitosamente.")
        st.session_state.new_scenario_name_input = ""  # Clear input after saving
    else:
        st.warning("Por favor, introduce un nombre para el escenario.")


def load_scenario_callback():
    """Callback to load a named scenario into the current simulation state."""
    scenario_name = st.session_state.load_scenario_selectbox
    if scenario_name and scenario_name in st.session_state['saved_scenarios']:
        loaded_changes = st.session_state['saved_scenarios'][scenario_name]
        # Reset all sim_ values to 0 before loading to ensure a clean state
        for key in list(st.session_state.keys()):
            if key.startswith('sim_'):
                st.session_state[key] = 0.0
        # Apply the loaded changes
        for key, value in loaded_changes.items():
            st.session_state[key] = value

        # Also reset adjustment flags if they were part of the saved state, or just reset them
        st.session_state['ajuste_activo'] = False
        st.session_state['porcentaje_ajuste'] = 45  # Default value

        st.success(f"Escenario '{scenario_name}' cargado exitosamente.")
        # No st.rerun() needed here as Streamlit will rerun after the callback finishes.
    elif scenario_name:
        st.error(f"Escenario '{scenario_name}' no encontrado.")


def delete_scenario_callback():
    """Callback to delete a named scenario."""
    scenario_name = st.session_state.delete_scenario_selectbox
    if scenario_name and scenario_name in st.session_state['saved_scenarios']:
        del st.session_state['saved_scenarios'][scenario_name]
        save_scenarios_to_file()
        st.success(f"Escenario '{scenario_name}' eliminado exitosamente.")
        # No st.rerun() needed here as Streamlit will rerun after the callback finishes.
    elif scenario_name:
        st.error(f"Escenario '{scenario_name}' no encontrado.")


def reset_simulator_callback():
    """Callback to reset all simulation values."""
    for key in list(st.session_state.keys()):
        if key.startswith('sim_'):
            st.session_state[key] = 0.0
    st.session_state['ajuste_activo'] = False  # Resetear también el ajuste automático
    st.session_state['porcentaje_ajuste'] = 45  # Resetear su valor por defecto
    # mobile_view_checkbox is removed from UI, no need to reset it.
    # Clear stored AI content too
    if 'recomendacion_ia_dashboard' in st.session_state:
        del st.session_state['recomendacion_ia_dashboard']
    if 'recomendacion_ia_dashboard_content' in st.session_state:
        del st.session_state['recomendacion_ia_dashboard_content']
    if 'informe_ia' in st.session_state:
        del st.session_state['informe_ia']
    # No st.rerun() needed here.


def simulate_plus_10_percent_sales_callback():
    """Callback to simulate +10% in national sales."""
    estructura = get_cached_structure()
    retail_actual = get_actual_value(estructura, 'VENTAS BRUTAS', 'VENTAS BRUTAS NACIONAL 16%', 'RETAIL')
    mayoreo_actual = get_actual_value(estructura, 'VENTAS BRUTAS', 'VENTAS BRUTAS NACIONAL 16%', 'MAYOREO')
    catalogo_actual = get_actual_value(estructura, 'VENTAS BRUTAS', 'VENTAS BRUTAS NACIONAL 16%', 'CATALOGO')

    st.session_state['sim_VENTAS_BRUTAS_NACIONAL_16%_RETAIL'] = retail_actual * 0.10
    st.session_state['sim_VENTAS_BRUTAS_NACIONAL_16%_MAYOREO'] = mayoreo_actual * 0.10
    st.session_state['sim_VENTAS_BRUTAS_NACIONAL_16%_CATALOGO'] = catalogo_actual * 0.10
    # No st.rerun() needed here.


# --- INTERFAZ DE USUARIO ---
st.title('📊 Simulador Financiero Jerárquico')
st.caption(
    "Simulación detallada con estructura de subcuentas. "
    f"Estado de IA: {'✅ Conectada' if GEMINI_AVAILABLE else '❌ No disponible'}"
)

# Botón para recargar Excel
if st.sidebar.button("🔄 Recargar Datos desde Excel", use_container_width=True):
    if cargar_excel():
        st.sidebar.success("¡Datos actualizados desde Excel!")
        # Limpiar caché para forzar recálculo
        st.cache_data.clear()
    else:
        st.sidebar.error("Error al actualizar datos")

# Inicializa el estado de las simulaciones y carga escenarios al inicio
# This should only be called once, at the very beginning of the script execution.
if 'initial_load_done' not in st.session_state:
    inicializar_simulaciones()
    st.session_state['initial_load_done'] = True

# --- SIDEBAR CON CONTROLES JERÁRQUICOS ---
with st.sidebar:
    st.header("⚙️ Controles de Simulación")

    # Sección de Gestión de Escenarios (Nueva)
    st.markdown("---")
    st.subheader("💾 Gestión de Escenarios")
    scenario_names = list(st.session_state['saved_scenarios'].keys())

    # Guardar Escenario
    st.text_input("Nombre del escenario para guardar:", key="new_scenario_name_input")
    st.button("Guardar Escenario Actual", use_container_width=True, on_click=save_current_scenario_callback)

    # Cargar Escenario
    if scenario_names:
        selected_scenario_load = st.selectbox("Seleccionar escenario para cargar:", [""] + scenario_names,
                                              key="load_scenario_selectbox")
        st.button("Cargar Escenario", use_container_width=True, disabled=(selected_scenario_load == ""),
                  on_click=load_scenario_callback)
    else:
        st.info("No hay escenarios guardados.")

    # Eliminar Escenario
    if scenario_names:
        selected_scenario_delete = st.selectbox("Seleccionar escenario para eliminar:", [""] + scenario_names,
                                                key="delete_scenario_selectbox")
        st.button("Eliminar Escenario", use_container_width=True, disabled=(selected_scenario_delete == ""),
                  on_click=delete_scenario_callback)

    st.markdown("---")
    st.subheader("📦 Ajuste Automático de Costos")

    # Checkbox para activar/desactivar el ajuste automático de costos
    st.session_state['ajuste_activo'] = st.checkbox(
        "Activar ajuste automático de costos",
        value=st.session_state.get('ajuste_activo', False),
        key='ajuste_activo_checkbox_widget',  # Clave única para el widget
        help="Vincula el costo de materiales con el incremento en ventas brutas nacionales"
    )

    if st.session_state['ajuste_activo']:
        # Slider para el porcentaje de ajuste, solo visible if el ajuste está activo
        st.session_state['porcentaje_ajuste'] = st.slider(
            "Porcentaje de ajuste sobre aumento de ventas brutas nacionales (%)",
            0, 100, st.session_state.get('porcentaje_ajuste', 45),
            key='porcentaje_ajuste_slider_widget',  # Clave única para el widget
            help="El costo de Materiales A Proceso se ajustará en este porcentaje del cambio en Ventas Brutas Nacionales (Retail, Catálogo y Mayoreo)"
        )

    st.markdown("---")

    estructura = get_cached_structure()
    # Se usan tabs para organizar los controles y mejorar la navegación en móvil
    tab_ventas, tab_costos, tab_gastos, tab_otros = st.tabs(["💰 Ventas", "🏭 Costos", "💸 Gastos", "📊 Otros"])


    # Función auxiliar para mostrar el valor actual, cambio y porcentaje de cambio debajo de cada input
    def display_number_input_info_with_actual_meta_brecha(key, actual_val, meta_val, is_auto_adjusted=False):
        current_change = st.session_state.get(key, 0.0)

        # Calculate percentage change for 'Cambio'
        percentage_change_sim = 0.0
        if actual_val != 0:
            percentage_change_sim = (current_change / actual_val) * 100
        elif current_change != 0:
            percentage_change_sim = float('inf') if current_change > 0 else float('-inf')

        # Calculate brecha vs Meta
        simulated_val_for_brecha = actual_val + current_change  # This is the effective simulated value
        brecha_vs_meta = simulated_val_for_brecha - meta_val
        brecha_vs_meta_percent = 0.0
        if meta_val != 0:
            brecha_vs_meta_percent = (brecha_vs_meta / meta_val) * 100
        elif brecha_vs_meta != 0:
            brecha_vs_meta_percent = float('inf') if brecha_vs_meta > 0 else float('-inf')

        # Display the info using markdown with inline styles for smaller font
        st.markdown(
            f'<div class="small-input-info">'  # Custom class for styling
            f'<p><b>Actual:</b> ${actual_val:,.0f} | '
            f'<b>Meta:</b> ${meta_val:,.0f} | '
            f'<b>Brecha vs Meta:</b> {brecha_vs_meta_percent:+.1f}%</p>'
            f'<p><b>{"Ajuste Automático" if is_auto_adjusted else "Cambio"}:</b> ${current_change:,.0f} ({percentage_change_sim:+.1f}%)</p>'
            f'</div>',
            unsafe_allow_html=True
        )


    # Sección de Ventas en el sidebar
    with tab_ventas:
        st.subheader("Ventas por Canal")
        with st.expander("🏠 Ventas Nacionales", expanded=True):
            for canal, datos in estructura['VENTAS BRUTAS']['subcuentas']['VENTAS BRUTAS NACIONAL 16%'].items():
                key = f"sim_VENTAS_BRUTAS_NACIONAL_16%_{canal}"
                actual_val = get_actual_value(estructura, 'VENTAS BRUTAS', 'VENTAS BRUTAS NACIONAL 16%', canal)
                meta_val = get_meta_value(estructura, 'VENTAS BRUTAS', 'VENTAS BRUTAS NACIONAL 16%', canal)
                min_val = -float(actual_val * 2) if actual_val > 0 else -200000000.0
                max_val = float(actual_val * 2) if actual_val > 0 else 200000000.0
                st.number_input(f"{canal}", min_value=min_val, max_value=max_val, value=st.session_state.get(key, 0.0),
                                step=10000.0, key=key)
                display_number_input_info_with_actual_meta_brecha(key, actual_val, meta_val)

        with st.expander("🌎 Ventas Extranjero"):
            for canal, datos in estructura['VENTAS BRUTAS']['subcuentas']['VENTAS BRUTAS EXTRANJERO'].items():
                key = f"sim_VENTAS_BRUTAS_EXTRANJERO_{canal}"
                actual_val = get_actual_value(estructura, 'VENTAS BRUTAS', 'VENTAS BRUTAS EXTRANJERO', canal)
                meta_val = get_meta_value(estructura, 'VENTAS BRUTAS', 'VENTAS BRUTAS EXTRANJERO', canal)
                min_val = -float(actual_val * 2) if actual_val > 0 else -2000000.0
                max_val = float(actual_val * 2) if actual_val > 0 else 2000000.0
                st.number_input(f"{canal} (Ext)", min_value=min_val, max_value=max_val,
                                value=st.session_state.get(key, 0.0), step=1000.0, key=key)
                display_number_input_info_with_actual_meta_brecha(key, actual_val, meta_val)

        key = 'sim_DESCUENTOS'
        actual_desc = get_actual_value(estructura, 'DESCUENTOS')
        meta_desc = get_meta_value(estructura, 'DESCUENTOS')
        min_desc = -float(actual_desc * 2) if actual_desc > 0 else -10000000.0
        max_desc = float(actual_desc * 2) if actual_desc > 0 else 10000000.0
        st.number_input("Descuentos", min_value=min_desc, max_value=max_desc, value=st.session_state.get(key, 0.0),
                        step=5000.0, key=key)
        display_number_input_info_with_actual_meta_brecha(key, actual_desc, meta_desc)

        key = 'sim_OTROS_INGRESOS'
        actual_otros_ingresos = get_actual_value(estructura, 'OTROS INGRESOS')
        meta_otros_ingresos = get_meta_value(estructura, 'OTROS INGRESOS')
        min_oi = -float(abs(actual_otros_ingresos) * 5) if actual_otros_ingresos != 0 else -5000000.0
        max_oi = float(abs(actual_otros_ingresos) * 5) if actual_otros_ingresos != 0 else 5000000.0
        st.number_input("Otros Ingresos", min_value=min_oi, max_value=max_oi, value=st.session_state.get(key, 0.0),
                        step=100.0, key=key)
        display_number_input_info_with_actual_meta_brecha(key, actual_otros_ingresos, meta_otros_ingresos)

    # Sección de Costos en el sidebar
    with tab_costos:
        st.subheader("Estructura de Costos")
        with st.expander("🎯 Costos Directos", expanded=True):
            for item, datos in estructura['COSTO']['subcuentas']['COSTO DIRECTO'].items():
                key = f"sim_COSTO_DIRECTO_{item.replace(' ', '_')}"
                actual_val = get_actual_value(estructura, 'COSTO', 'COSTO DIRECTO', item)
                meta_val = get_meta_value(estructura, 'COSTO', 'COSTO DIRECTO', item)
                min_val = -float(actual_val * 2) if actual_val > 0 else -50000000.0
                max_val = float(actual_val * 2) if actual_val > 0 else 50000000.0

                # Lógica para el campo "Materiales A Proceso"
                if item == 'MATERIALES A PROCESO':
                    if st.session_state.get('ajuste_activo', False):
                        cambio_ventas_brutas_nacional = 0
                        for canal_vn in ['RETAIL', 'CATALOGO', 'MAYOREO']:
                            key_ventas_nacional = f"sim_VENTAS_BRUTAS_NACIONAL_16%_{canal_vn}"
                            # Only add positive changes to the materials adjustment calculation
                            cambio_ventas_brutas_nacional += max(0, st.session_state.get(key_ventas_nacional, 0.0))

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
                        # Displaying combined info for auto-adjusted field
                        display_number_input_info_with_actual_meta_brecha(key, actual_val, meta_val,
                                                                          is_auto_adjusted=True)
                    else:
                        st.number_input(f"{item.replace('_', ' ').title()}", min_value=min_val, max_value=max_val,
                                        value=st.session_state.get(key, 0.0), step=1000.0, key=key)
                        display_number_input_info_with_actual_meta_brecha(key, actual_val, meta_val)
                else:  # For other direct costs
                    st.number_input(f"{item.replace('_', ' ').title()}", min_value=min_val, max_value=max_val,
                                    value=st.session_state.get(key, 0.0), step=1000.0, key=key)
                    display_number_input_info_with_actual_meta_brecha(key, actual_val, meta_val)

        with st.expander("🔧 Costos Indirectos"):
            for item, datos in estructura['COSTO']['subcuentas']['COSTO INDIRECTO'].items():
                key = f"sim_COSTO_INDIRECTO_{item.replace(' ', '_')}"
                actual_val = get_actual_value(estructura, 'COSTO', 'COSTO INDIRECTO', item)
                meta_val = get_meta_value(estructura, 'COSTO', 'COSTO INDIRECTO', item)
                min_val = -float(actual_val * 2) if actual_val > 0 else -1000000.0
                max_val = float(actual_val * 2) if actual_val > 0 else 1000000.0
                st.number_input(f"{item.replace('_', ' ').title()}", min_value=min_val, max_value=max_val,
                                value=st.session_state.get(key, 0.0), step=100.0, key=key)
                display_number_input_info_with_actual_meta_brecha(key, actual_val, meta_val)

        key = 'sim_OTROS_COSTOS_OTROS_COSTOS'
        actual_otros_costos = get_actual_value(estructura, 'COSTO', 'OTROS COSTOS', 'OTROS COSTOS')
        meta_otros_costos = get_meta_value(estructura, 'COSTO', 'OTROS COSTOS', 'OTROS COSTOS')
        min_oc = -float(actual_otros_costos * 2) if actual_otros_costos > 0 else -500000.0
        max_oc = float(actual_otros_costos * 2) if actual_otros_costos > 0 else 500000.0
        st.number_input("Otros Costos", min_value=min_oc, max_value=max_oc, value=st.session_state.get(key, 0.0),
                        step=100.0, key=key)
        display_number_input_info_with_actual_meta_brecha(key, actual_otros_costos, meta_otros_costos)

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
                        meta_val = get_meta_value(estructura, 'TOTAL GASTOS OPERATIVOS', cuenta)
                        min_val = -float(actual_val * 2) if actual_val > 0 else -1000000.0
                        max_val = float(actual_val * 2) if actual_val > 0 else 1000000.0
                        st.number_input(f"{cuenta.title()}", min_value=min_val, max_value=max_val,
                                        value=st.session_state.get(key, 0.0), step=100.0, key=key)
                        display_number_input_info_with_actual_meta_brecha(key, actual_val, meta_val)

        with st.expander("Otros Gastos Operativos (No agrupados)"):
            for cuenta in all_op_expense_accounts:
                if cuenta not in cuentas_agrupadas:
                    key = f"sim_{cuenta.replace(' ', '_')}"
                    actual_val = get_actual_value(estructura, 'TOTAL GASTOS OPERATIVOS', cuenta)
                    meta_val = get_meta_value(estructura, 'TOTAL GASTOS OPERATIVOS', cuenta)
                    min_val = -float(actual_val * 2) if actual_val > 0 else -500000.0
                    max_val = float(actual_val * 2) if actual_val > 0 else 500000.0
                    st.number_input(f"{cuenta.title()}", min_value=min_val, max_value=max_val,
                                    value=st.session_state.get(key, 0.0), step=10.0, key=key)
                    display_number_input_info_with_actual_meta_brecha(key, actual_val, meta_val)

    # Sección de Otros en el sidebar
    with tab_otros:
        st.subheader("Otros Conceptos")
        key = 'sim_TOTAL_DE_OTROS_GASTOS'
        actual_tot_otros_gastos = get_actual_value(estructura, 'TOTAL DE OTROS GASTOS')
        meta_tot_otros_gastos = get_meta_value(estructura, 'TOTAL DE OTROS GASTOS')
        min_tog = -float(actual_tot_otros_gastos * 2) if actual_tot_otros_gastos > 0 else -1000000.0
        max_tog = float(actual_tot_otros_gastos * 2) if actual_tot_otros_gastos > 0 else 1000000.0
        st.number_input("Total Otros Gastos", min_value=min_tog, max_value=max_tog,
                        value=st.session_state.get(key, 0.0), step=1000.0, key=key)
        display_number_input_info_with_actual_meta_brecha(key, actual_tot_otros_gastos, meta_tot_otros_gastos)

        st.subheader("Conceptos Financieros")
        for concepto in ['GASTOS FINANCIEROS', 'PRODUCTOS FINANCIEROS', 'RESULTADO CAMBIARIO']:
            key = f"sim_{concepto.replace(' ', '_')}"
            actual_val = get_actual_value(estructura, 'FINANCIEROS', concepto)
            meta_val = get_meta_value(estructura, 'FINANCIEROS', concepto)
            # Ajustar min/max basándose en si el actual es 0 o no, para evitar valores absurdos
            if actual_val != 0:
                min_val = -float(abs(actual_val) * 2)
                max_val = float(abs(actual_val) * 2)
            else:
                min_val = -500000.0
                max_val = 500000.0

            st.number_input(f"{concepto.title()}", min_value=min_val, max_value=max_val,
                            value=st.session_state.get(key, 0.0), step=100.0, key=key)
            display_number_input_info_with_actual_meta_brecha(key, actual_val, meta_val)

    # Move "Escenarios Rápidos" to the end of the sidebar
    st.markdown("---")
    st.subheader("🎭 Escenarios Rápidos")
    col1_scenario, col2_scenario = st.columns(2)
    with col1_scenario:
        # Botón para refrescar el simulador y resetear todos los valores
        st.button("🔄 Refrescar Simulador", use_container_width=True,
                  help="Restablece todos los simuladores a cero.", on_click=reset_simulator_callback)

    with col2_scenario:
        # Botón para simular un aumento del 10% en ventas nacionales específicas
        st.button("📈 Simular +10% en Ventas Nacionales", use_container_width=True,
                  help="Aumenta en un 10% del valor actual las ventas nacionales de Retail, Catálogo y Mayoreo",
                  on_click=simulate_plus_10_percent_sales_callback)

# --- CONTENIDO PRINCIPAL ---

# Obtener cambios actuales de todos los simuladores manuales.
# ESTA PARTE FUE MOVIDA AQUÍ ARRIBA para asegurar que 'changes' SIEMPRE esté definido.
changes = {key: value for key, value in st.session_state.items() if key.startswith('sim_')}

# Lógica CLAVE para el ajuste automático de costos: se aplica ANTES de generar el dataframe
key_materiales_proceso = 'sim_COSTO_DIRECTO_MATERIALES_A_PROCESO'
if st.session_state.get('ajuste_activo', False):
    # Si el ajuste automático está activo, calcula y aplica el ajuste
    cambio_ventas_brutas_nacional = 0
    # Sumar solo los cambios POSITIVOS de los inputs de ventas nacionales (Retail, Catalogo, Mayoreo)
    for canal in ['RETAIL', 'CATALOGO', 'MAYOREO']:
        key_ventas_nacional = f"sim_VENTAS_BRUTAS_NACIONAL_16%_{canal}"
        # Use max(0, value) to ensure only positive changes contribute
        cambio_ventas_brutas_nacional += max(0, st.session_state.get(key_ventas_nacional, 0.0))

    porcentaje_ajuste = st.session_state.get('porcentaje_ajuste', 45)
    ajuste_materiales = (porcentaje_ajuste / 100) * cambio_ventas_brutas_nacional
    changes[key_materiales_proceso] = ajuste_materiales
else:
    # If the automatic adjustment is NOT active, ensure the change for "Materiales A Proceso" is 0.0
    # This prevents its value from persisting if the user turns off the adjustment.
    changes[key_materiales_proceso] = 0.0

# Generar dataframe con los cambios actualizados
df_completo = generar_dataframe_completo(changes)
df_variables_mod = obtener_variables_modificadas(changes)

# Pestañas principales para organizar el contenido en el dashboard
# Moved 'IA: Brecha a Meta y Razones' into 'Análisis Visual Intuitivo'
tab1, tab2 = st.tabs(["📊 Dashboard de Brechas", "📈 Análisis Visual e IA"])

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

    # Para Ventas Netas, Margen Bruto, EBITDA, BAI:
    # Un delta positivo es una MEJORA (verde).
    # Un delta negativo es un DETERIORO (rojo).
    # `delta_color="normal"` aplica esto por defecto en Streamlit.
    col1.metric("VENTAS NETAS", f"${ventas_netas:,.0f}", f"{diff_ventas_netas:+,.0f} vs Meta",
                delta_color="normal")
    col2.metric("MARGEN BRUTO", f"${margen_bruto:,.0f}", f"{diff_margen_bruto:+,.0f} vs Meta",
                delta_color="normal")
    col3.metric("EBITDA", f"${ebitda:,.0f}", f"{diff_ebitda:+,.0f} vs Meta",
                delta_color="normal")
    col4.metric("BAI", f"${bai:,.0f}", f"{diff_bai:+,.0f} vs Meta",
                delta_color="normal")

    st.subheader("Análisis Comparativo Detallado")

    # Crear df_display with the desired column order.
    df_display = df_completo[[
        'Cuenta', 'Actual', 'Simulado', 'Simulado (% VN)', 'Meta', 'Meta (% VN)', 'Brecha vs Meta (%)'
    ]].copy()
    df_display.rename(columns={
        'Simulado (% VN)': '% Sim. vs VN',
        'Meta (% VN)': '% Meta vs VN',
        'Brecha vs Meta (%)': 'Brecha (% S vs M)'
    }, inplace=True)

    # Formatos para la tabla (updated to reflect new column order)
    formatos = {
        'Actual': '{:,.0f}',
        'Simulado': '{:,.0f}',
        '% Sim. vs VN': '{:,.2f}%',
        'Meta': '{:,.0f}',
        '% Meta vs VN': '{:,.2f}%',
        'Brecha (% S vs M)': '{:+.2f}%'
    }

    # Calculate height needed for all rows
    row_height = 34
    header_height = 38
    total_rows = len(df_display)
    desired_height = (total_rows * row_height) + header_height + 5  # Added a bit extra padding

    st.dataframe(
        aplicar_estilo_financiero(df_display).format(formatos),
        use_container_width=True,
        height=desired_height
    )

    # Botón para obtener recomendaciones de IA sobre variables clave
    if st.button("🚀 Obtener Recomendación IA de Variables Clave", use_container_width=True, type="secondary"):
        with st.spinner("🧠 El CFO Virtual está analizando las desviaciones para darte recomendaciones..."):
            # Store the generated content in session state for reuse
            recomendacion_ia_content = generar_recomendacion_variables_ia(df_completo)
            st.session_state['recomendacion_ia_dashboard'] = recomendacion_ia_content
            st.session_state['recomendacion_ia_dashboard_content'] = recomendacion_ia_content  # For the other AI prompt

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

# --- TAB 2: ANÁLISIS VISUAL E IA ---
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

    st.markdown("---")
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

    # Removed the "Exportar Informe (Próximamente)" section as requested.
