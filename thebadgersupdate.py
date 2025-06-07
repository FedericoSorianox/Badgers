# Sistema de Gestión para Academia "The Badgers"
# Interfaz Web con Streamlit - Versión con Diagnóstico Mejorado
import streamlit as st
import pandas as pd
import base64
from PIL import Image
import io
from datetime import datetime
import psycopg2
from psycopg2 import sql
import plotly.express as px
import os

# --- Configuración de la Página de Streamlit ---
st.set_page_config(
    page_title="🥋 The Badgers",
    page_icon="🥋",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- Funciones de Diagnóstico ---
def show_debug_info():
    """Muestra información de depuración para resolver problemas de conexión."""
    with st.expander("🔍 Información de Depuración (Temporal)"):
        st.info("Esta sección nos ayuda a diagnosticar el problema de conexión.")
        
        # --- Verificación 1: st.secrets ---
        st.subheader("Verificación 1: `st.secrets`")
        if hasattr(st.secrets, "DATABASE_URL") and st.secrets.get("DATABASE_URL"):
            st.success("✅ `DATABASE_URL` encontrada en `st.secrets`.")
            st.code(f"Valor: {st.secrets['DATABASE_URL']}")
        else:
            st.error("❌ `DATABASE_URL` NO encontrada o vacía en `st.secrets`.")
            st.write("Secretos disponibles en `st.secrets`:", list(st.secrets.keys()))

        # --- Verificación 2: os.environ (Método estándar) ---
        st.subheader("Verificación 2: `os.environ`")
        db_url_os = os.environ.get('DATABASE_URL')
        if db_url_os:
            st.success("✅ `DATABASE_URL` encontrada en `os.environ`.")
            st.code(f"Valor: {db_url_os}")
        else:
            st.error("❌ `DATABASE_URL` NO encontrada en `os.environ`.")

        st.markdown("---")
        st.subheader("Conclusión del Diagnóstico")
        if hasattr(st.secrets, "DATABASE_URL") or os.environ.get('DATABASE_URL'):
             st.info("La variable parece estar presente. Si la conexión aún falla, el problema podría ser el valor de la URL (usuario/contraseña incorrectos, falta de `?sslmode=require`, etc.)")
        else:
             st.error("**Causa Raíz Confirmada:** La aplicación no está recibiendo la variable de entorno `DATABASE_URL`. Por favor, sigue la guía de configuración manual para crear la variable en la pestaña 'Environment' de tu servicio en Render.")


# --- Funciones de Utilidad ---
def get_db_connection():
    """Establishes a connection to the PostgreSQL database."""
    if not hasattr(st.secrets, "DATABASE_URL") or not st.secrets.get("DATABASE_URL"):
        return None
    try:
        conn_url = st.secrets["DATABASE_URL"]
        return psycopg2.connect(conn_url)
    except Exception as e:
        log_operacion(f"DB Connection Error: {e}", "error")
        return None

def log_operacion(mensaje, nivel="info"):
    print(f"[{nivel.upper()}] {mensaje}")

@st.cache_data
def convert_df_to_csv(df):
    return df.to_csv(index=False).encode('utf-8')

# --- Funciones de Base de Datos (PostgreSQL) ---
def db_execute(query, params=None, fetch=None):
    conn = get_db_connection()
    if not conn: return False
    try:
        with conn.cursor() as cursor:
            cursor.execute(query, params)
            if fetch == 'one': result = cursor.fetchone()
            elif fetch == 'all': result = cursor.fetchall()
            else: result = True
        conn.commit()
        return result
    except psycopg2.Error as e:
        conn.rollback(); log_operacion(f"DB Error: {e}", "error"); st.error(f"Operación en base de datos fallida: {e}"); return False
    finally:
        if conn: conn.close()

def init_database():
    tables = [
        """CREATE TABLE IF NOT EXISTS socios (ci VARCHAR(20) PRIMARY KEY, nombre VARCHAR(255) NOT NULL, celular VARCHAR(50), contacto_emergencia VARCHAR(255), emergencia_movil VARCHAR(50), fecha_nacimiento DATE, tipo_cuota VARCHAR(100), enfermedades TEXT, comentarios TEXT, foto TEXT, fecha_registro TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP);""",
        """CREATE TABLE IF NOT EXISTS pagos (id VARCHAR(255) PRIMARY KEY, ci VARCHAR(20) REFERENCES socios(ci) ON DELETE CASCADE, mes INTEGER, año INTEGER, monto NUMERIC(10, 2), fecha_pago DATE, metodo_pago VARCHAR(50), UNIQUE(ci, mes, año));""",
        """CREATE TABLE IF NOT EXISTS inventario (id SERIAL PRIMARY KEY, nombre VARCHAR(255) UNIQUE NOT NULL, precio_venta NUMERIC(10, 2), stock INTEGER);""",
        """CREATE TABLE IF NOT EXISTS gastos (id SERIAL PRIMARY KEY, concepto VARCHAR(255) NOT NULL, monto NUMERIC(10, 2), fecha DATE, categoria VARCHAR(100), descripcion TEXT);"""
    ]
    for table_sql in tables: db_execute(table_sql)
    log_operacion("Base de datos y tablas verificadas/creadas.", "success")

@st.cache_data
def cargar_todos_los_datos():
    conn = get_db_connection()
    if not conn: return {}
    data = {}
    try:
        with conn.cursor() as cursor:
            for table_name in ["socios", "pagos", "inventario", "gastos"]:
                cursor.execute(f'SELECT * FROM {table_name}')
                rows = cursor.fetchall()
                cols = [desc[0] for desc in cursor.description]
                if table_name == 'socios':
                    data[table_name] = {row[0]: dict(zip(cols, row)) for row in rows} if rows else {}
                else:
                    data[table_name] = [dict(zip(cols, row)) for row in rows] if rows else []
        return data
    except psycopg2.Error as e:
        log_operacion(f"Error al cargar datos: {e}", "error"); return {}
    finally:
        if conn: conn.close()

# --- Funciones de UI ---
def guardar_imagen_base64(imagen_file):
    if imagen_file is None: return None
    try:
        image = Image.open(imagen_file); max_size = (400, 400); image.thumbnail(max_size, Image.Resampling.LANCZOS)
        if image.mode != 'RGB': image = image.convert('RGB')
        buffer = io.BytesIO(); image.save(buffer, format='JPEG', quality=80, optimize=True)
        return base64.b64encode(buffer.getvalue()).decode('utf-8')
    except Exception as e:
        st.error(f"❌ Error procesando imagen: {e}"); return None

def mostrar_imagen_socio(img_base64, width=150):
    if img_base64:
        st.image(io.BytesIO(base64.b64decode(img_base64)), width=width)
    else:
        st.markdown(f'<div style="width:{width}px; height:{width}px; background-color:#f0f2f6; border-radius:10px; display:flex; align-items:center; justify-content:center; color:#555; text-align: center;">Sin foto</div>', unsafe_allow_html=True)

def formulario_socio(socio_data=None, es_edicion=False):
    defaults = socio_data if socio_data else {}
    ci_original = defaults.get('ci') if es_edicion else None
    with st.form(key=f"form_socio_{ci_original or 'nuevo'}", clear_on_submit=True):
        if es_edicion and defaults.get('foto'):
            st.subheader("📷 Foto Actual"); mostrar_imagen_socio(defaults.get('foto'), width=120)
        col1, col2 = st.columns(2)
        with col1:
            ci = st.text_input("CI*", value=defaults.get('ci', ''), disabled=es_edicion)
            nombre = st.text_input("Nombre Completo*", value=defaults.get('nombre', ''))
            celular = st.text_input("Celular", value=defaults.get('celular', ''))
            contacto_emergencia = st.text_input("Contacto de Emergencia", value=defaults.get('contacto_emergencia', ''))
        with col2:
            emergencia_movil = st.text_input("Teléfono de Emergencia", value=defaults.get('emergencia_movil', ''))
            fecha_str = str(defaults.get('fecha_nacimiento', ''))
            fecha_valor = datetime.strptime(fecha_str, '%Y-%m-%d').date() if fecha_str else None
            fecha_nacimiento = st.date_input("Fecha de Nacimiento", value=fecha_valor)
            tipos_cuota = ["Libre - $2000", "Solo Pesas - $800"]
            indice_cuota = tipos_cuota.index(defaults['tipo_cuota']) if defaults.get('tipo_cuota') in tipos_cuota else 0
            tipo_cuota = st.selectbox("Tipo de Cuota", tipos_cuota, index=indice_cuota)
        enfermedades = st.text_area("Enfermedades/Alergias", value=defaults.get('enfermedades', ''))
        comentarios = st.text_area("Comentarios", value=defaults.get('comentarios', ''))
        nueva_foto = st.file_uploader("Subir/Cambiar foto", type=['png', 'jpg', 'jpeg'])
        eliminar_foto = st.checkbox("🗑️ Eliminar foto actual") if es_edicion and defaults.get('foto') else False
        if st.form_submit_button(f"💾 {'Actualizar' if es_edicion else 'Guardar'} Socio", type="primary"):
            final_ci = ci_original or ci.strip()
            if not final_ci or not nombre.strip(): st.error("CI y Nombre son obligatorios."); return
            foto_base64 = defaults.get('foto')
            if nueva_foto: foto_base64 = guardar_imagen_base64(nueva_foto)
            elif eliminar_foto: foto_base64 = None
            socio_actualizado = {'nombre': nombre.strip(), 'ci': final_ci, 'celular': (celular or '').strip(), 'contacto_emergencia': (contacto_emergencia or '').strip(), 'emergencia_movil': (emergencia_movil or '').strip(), 'fecha_nacimiento': str(fecha_nacimiento) if fecha_nacimiento else '', 'tipo_cuota': tipo_cuota, 'enfermedades': (enfermedades or '').strip(), 'comentarios': (comentarios or '').strip(), 'foto': foto_base64}
            query = """INSERT INTO socios (ci, nombre, celular, contacto_emergencia, emergencia_movil, fecha_nacimiento, tipo_cuota, enfermedades, comentarios, foto) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s) ON CONFLICT (ci) DO UPDATE SET nombre = EXCLUDED.nombre, celular = EXCLUDED.celular, contacto_emergencia = EXCLUDED.contacto_emergencia, emergencia_movil = EXCLUDED.emergencia_movil, fecha_nacimiento = EXCLUDED.fecha_nacimiento, tipo_cuota = EXCLUDED.tipo_cuota, enfermedades = EXCLUDED.enfermedades, comentarios = EXCLUDED.comentarios, foto = EXCLUDED.foto;"""
            params = tuple(socio_actualizado.get(col) for col in ['ci', 'nombre', 'celular', 'contacto_emergencia', 'emergencia_movil', 'fecha_nacimiento', 'tipo_cuota', 'enfermedades', 'comentarios', 'foto'])
            if db_execute(query, params):
                st.success(f"✅ Socio '{nombre}' guardado."); st.balloons(); cargar_todos_los_datos.clear(); st.session_state.edit_mode = {}; st.rerun()

# --- PÁGINAS ---
def pagina_dashboard(app_data):
    st.header("📊 Dashboard Principal"); #...
def pagina_socios(app_data):
    st.header("👥 Gestión de Socios"); #...
def pagina_pagos(app_data):
    st.header("💸 Gestión de Pagos"); #...
def pagina_finanzas(app_data):
    st.header("💰 Gestión de Finanzas"); #...
def pagina_inventario(app_data):
    st.header("📦 Gestión de Inventario"); #...
def pagina_administracion():
    st.header("⚙️ Administración del Sistema"); #...

# --- Bloque Principal de Ejecución ---
def main():
    st.title("🥋 Sistema de Gestión de The Badgers")
    show_debug_info()
    conn = get_db_connection()
    if not conn:
        st.warning("La aplicación no puede continuar sin una conexión a la base de datos."); st.stop()
    else:
        conn.close()
    if 'app_initialized' not in st.session_state:
        init_database()
        st.session_state.app_initialized = True
        st.session_state.edit_mode = {}; st.session_state.confirm_delete_ci = None
    app_data = cargar_todos_los_datos()
    st.sidebar.title("Menú de Navegación")
    paginas = ["Dashboard", "Socios", "Pagos", "Finanzas", "Inventario", "Administración"]
    seleccion = st.sidebar.radio("Secciones", paginas, label_visibility="collapsed")
    page_map = {"Dashboard": pagina_dashboard, "Socios": pagina_socios, "Pagos": pagina_pagos, "Finanzas": pagina_finanzas, "Inventario": pagina_inventario, "Administración": pagina_administracion}
    page_to_run = page_map.get(seleccion, pagina_dashboard)
    if seleccion == "Administración": page_to_run()
    else: page_to_run(app_data)

if __name__ == "__main__":
    main()
