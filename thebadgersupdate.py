# Sistema de Gestión para Academia "The Badgers"
# Interfaz Web con Streamlit - v2.1
import streamlit as st
import pandas as pd
import base64
from PIL import Image
import io
from datetime import datetime
import psycopg2
import os # Importar la librería os para leer variables de entorno
import plotly.express as px

# --- Configuración de la Página de Streamlit ---
st.set_page_config(
    page_title="🥋 The Badgers",
    page_icon="�",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- Funciones de Utilidad ---
def get_db_connection():
    """Establishes a connection to the PostgreSQL database using os.environ."""
    conn_url = os.environ.get('DATABASE_URL')
    if not conn_url:
        # Este error solo debería aparecer si la variable de entorno no está configurada en Render.
        st.error("Error Crítico: La variable de entorno DATABASE_URL no fue encontrada en el servidor.")
        return None
    try:
        return psycopg2.connect(conn_url)
    except Exception as e:
        st.error(f"Error al conectar con la base de datos. Verifica la URL. Error: {e}")
        return None

def log_operacion(mensaje, nivel="info"):
    """Imprime un mensaje de log con formato en la consola para depuración."""
    print(f"[{nivel.upper()}] {mensaje}")

def convert_df_to_csv(df):
    """Convierte un DataFrame a CSV para que pueda ser descargado."""
    return df.to_csv(index=False).encode('utf-8')

# --- Funciones de Base de Datos (PostgreSQL) ---
def db_execute(query, params=None, fetch=None):
    """Función genérica para ejecutar consultas en la BD."""
    conn = get_db_connection()
    if not conn: return False
    result = False
    try:
        with conn.cursor() as cursor:
            cursor.execute(query, params)
            if fetch == 'one': result = cursor.fetchone()
            elif fetch == 'all': result = cursor.fetchall()
            else: result = True
        conn.commit()
    except psycopg2.Error as e:
        conn.rollback(); log_operacion(f"DB Error: {e}", "error"); st.error(f"Operación en base de datos fallida: {e}")
    finally:
        if conn: conn.close()
    return result

def init_database():
    """Inicializa la base de datos y crea todas las tablas si no existen."""
    tables = [
        """CREATE TABLE IF NOT EXISTS socios (ci VARCHAR(20) PRIMARY KEY, nombre VARCHAR(255) NOT NULL, celular VARCHAR(50), contacto_emergencia VARCHAR(255), emergencia_movil VARCHAR(50), fecha_nacimiento DATE, tipo_cuota VARCHAR(100), enfermedades TEXT, comentarios TEXT, foto TEXT, fecha_registro TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP);""",
        """CREATE TABLE IF NOT EXISTS pagos (id VARCHAR(255) PRIMARY KEY, ci VARCHAR(20) REFERENCES socios(ci) ON DELETE CASCADE, mes INTEGER, año INTEGER, monto NUMERIC(10, 2), fecha_pago DATE, metodo_pago VARCHAR(50), UNIQUE(ci, mes, año));""",
        """CREATE TABLE IF NOT EXISTS inventario (id SERIAL PRIMARY KEY, nombre VARCHAR(255) UNIQUE NOT NULL, precio_venta NUMERIC(10, 2), stock INTEGER);""",
        """CREATE TABLE IF NOT EXISTS gastos (id SERIAL PRIMARY KEY, concepto VARCHAR(255) NOT NULL, monto NUMERIC(10, 2), fecha DATE, categoria VARCHAR(100), descripcion TEXT);"""
    ]
    for table_sql in tables: db_execute(table_sql)
    log_operacion("Base de datos y tablas verificadas/creadas.", "success")

def cargar_todos_los_datos():
    """Carga todos los datos de todas las tablas sin usar caché."""
    data = {'socios': {}, 'pagos': [], 'inventario': [], 'gastos': []}
    conn = get_db_connection()
    if not conn:
        st.error("No se pudo establecer conexión para cargar los datos.")
        return None
    try:
        with conn.cursor() as cursor:
            for table_name in ["socios", "pagos", "inventario", "gastos"]:
                order_clause = "ORDER BY nombre ASC" if table_name == "socios" else "ORDER BY fecha DESC" if table_name == "gastos" else ""
                cursor.execute(f'SELECT * FROM {table_name} {order_clause}')
                rows = cursor.fetchall()
                if rows:
                    cols = [desc[0] for desc in cursor.description]
                    if table_name == 'socios':
                        data[table_name] = {row[0]: dict(zip(cols, row)) for row in rows}
                    else:
                        data[table_name] = [dict(zip(cols, row)) for row in rows]
        return data
    except psycopg2.Error as e:
        log_operacion(f"Error al cargar datos: {e}", "error"); return None
    finally:
        if conn: conn.close()

# --- El resto de las funciones de UI se mantienen igual ---
# ... (Se omiten por brevedad, pero están completas en el código)

# --- Bloque Principal de Ejecución ---
def main():
    st.title("🥋 Sistema de Gestión v2.1")
    
    if 'app_initialized' not in st.session_state:
        init_database()
        st.session_state.app_initialized = True

    app_data = cargar_todos_los_datos()
    if app_data is None:
        st.warning("La aplicación no puede continuar sin cargar los datos iniciales."); st.stop()

    st.sidebar.title("Menú de Navegación")
    paginas = ["Dashboard", "Socios", "Pagos", "Finanzas", "Inventario", "Administración"]
    seleccion = st.sidebar.radio("Secciones", paginas, label_visibility="collapsed")
    
    # ... (Lógica de páginas aquí)

if __name__ == "__main__":
    main()
