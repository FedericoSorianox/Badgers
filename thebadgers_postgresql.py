# Sistema de Gestión para Academia "The Badgers"
# Interfaz Web con Streamlit - Versión PostgreSQL
import time
import uuid
import streamlit as st
import pandas as pd
import base64
from PIL import Image
import io
import os
from datetime import datetime
import psycopg2
from psycopg2 import sql

# --- Configuración de la Página de Streamlit ---
st.set_page_config(
    page_title="🥋 The Badgers",
    page_icon="🥋",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- Funciones de Utilidad ---

def get_db_connection():
    """Establishes a connection to the PostgreSQL database."""
    try:
        conn_url = st.secrets["DATABASE_URL"]
        conn = psycopg2.connect(conn_url)
        return conn
    except Exception as e:
        st.error(f"Error de conexión a la base de datos. Verifica la DATABASE_URL en los secretos.")
        log_operacion(f"DB Connection Error: {e}", "error")
        return None

def log_operacion(mensaje, nivel="info"):
    """Imprime un mensaje de log con formato en la consola para depuración."""
    iconos = {"info": "ℹ️", "success": "✅", "warning": "⚠️", "error": "❌"}
    print(f"{iconos.get(nivel, '➡️')} [{nivel.upper()}] {mensaje}")

# --- Funciones de Base de Datos (PostgreSQL) ---

def init_database():
    """Inicializa la base de datos y crea las tablas si no existen."""
    conn = get_db_connection()
    if not conn:
        st.stop()
    
    try:
        with conn.cursor() as cursor:
            # Tabla de socios
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS socios (
                    ci VARCHAR(20) PRIMARY KEY,
                    nombre VARCHAR(255) NOT NULL,
                    celular VARCHAR(50),
                    contacto_emergencia VARCHAR(255),
                    emergencia_movil VARCHAR(50),
                    fecha_nacimiento DATE,
                    tipo_cuota VARCHAR(100),
                    enfermedades TEXT,
                    comentarios TEXT,
                    foto TEXT,
                    fecha_registro TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP
                );
            """)
            # Tabla de pagos
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS pagos (
                    id VARCHAR(255) PRIMARY KEY,
                    ci VARCHAR(20) REFERENCES socios(ci) ON DELETE CASCADE,
                    mes VARCHAR(50),
                    año INTEGER,
                    monto NUMERIC(10, 2),
                    fecha_pago DATE,
                    tipo_cuota VARCHAR(100),
                    fecha_registro TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP
                );
            """)
        conn.commit()
        log_operacion("Base de datos y tablas verificadas/creadas en PostgreSQL.", "success")
    except psycopg2.Error as e:
        st.error(f"Error al inicializar la base de datos: {e}")
    finally:
        if conn:
            conn.close()

def cargar_datos_desde_db():
    """Carga todos los datos desde PostgreSQL a st.session_state."""
    conn = get_db_connection()
    if not conn: return
    try:
        with conn.cursor() as cursor:
            cursor.execute('SELECT * FROM socios ORDER BY nombre ASC')
            st.session_state.socios = {row[0]: {
                'ci': row[0], 'nombre': row[1], 'celular': row[2],
                'contacto_emergencia': row[3], 'emergencia_movil': row[4],
                'fecha_nacimiento': str(row[5]) if row[5] else '', 'tipo_cuota': row[6],
                'enfermedades': row[7], 'comentarios': row[8], 'foto': row[9]
            } for row in cursor.fetchall()}
        log_operacion(f"Datos cargados desde PostgreSQL: {len(st.session_state.socios)} socios.")
    except psycopg2.Error as e:
        log_operacion(f"Error al cargar datos desde PostgreSQL: {e}", "error")
    finally:
        if conn: conn.close()

def guardar_socio_db(ci, socio_data):
    """Guarda o actualiza un socio en la base de datos PostgreSQL."""
    conn = get_db_connection()
    if not conn: return False
    try:
        with conn.cursor() as cursor:
            query = sql.SQL("""
                INSERT INTO socios (ci, nombre, celular, contacto_emergencia, emergencia_movil, fecha_nacimiento, tipo_cuota, enfermedades, comentarios, foto)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                ON CONFLICT (ci) DO UPDATE SET
                    nombre = EXCLUDED.nombre, celular = EXCLUDED.celular,
                    contacto_emergencia = EXCLUDED.contacto_emergencia, emergencia_movil = EXCLUDED.emergencia_movil,
                    fecha_nacimiento = EXCLUDED.fecha_nacimiento, tipo_cuota = EXCLUDED.tipo_cuota,
                    enfermedades = EXCLUDED.enfermedades, comentarios = EXCLUDED.comentarios, foto = EXCLUDED.foto;
            """)
            fecha_nac = socio_data.get('fecha_nacimiento')
            fecha_obj = datetime.strptime(fecha_nac, '%Y-%m-%d').date() if fecha_nac else None
            cursor.execute(query, (
                ci, socio_data.get('nombre'), socio_data.get('celular'),
                socio_data.get('contacto_emergencia'), socio_data.get('emergencia_movil'),
                fecha_obj, socio_data.get('tipo_cuota'),
                socio_data.get('enfermedades'), socio_data.get('comentarios'),
                socio_data.get('foto')
            ))
        conn.commit()
        return True
    except psycopg2.Error as e:
        log_operacion(f"Error al guardar socio {ci}: {e}", "error")
        return False
    finally:
        if conn: conn.close()

def eliminar_socio_db(ci):
    """Elimina un socio y sus pagos asociados de la base de datos."""
    conn = get_db_connection()
    if not conn: return False
    try:
        with conn.cursor() as cursor:
            cursor.execute("DELETE FROM socios WHERE ci = %s", (ci,))
        conn.commit()
        return True
    except psycopg2.Error as e:
        st.error(f"Error eliminando socio: {e}")
        return False
    finally:
        if conn: conn.close()

# --- Funciones de Interfaz de Usuario (UI) ---

def guardar_imagen_base64(imagen_file):
    """Convierte un archivo de imagen subido a una cadena Base64."""
    if imagen_file is None: return None
    try:
        image = Image.open(imagen_file)
        max_size = (400, 400)
        image.thumbnail(max_size, Image.Resampling.LANCZOS)
        if image.mode != 'RGB': image = image.convert('RGB')
        buffer = io.BytesIO()
        image.save(buffer, format='JPEG', quality=80, optimize=True)
        return base64.b64encode(buffer.getvalue()).decode('utf-8')
    except Exception as e:
        st.error(f"❌ Error procesando imagen: {e}")
        return None

def mostrar_imagen_socio(img_base64, width=150):
    """Muestra una imagen desde una cadena Base64 o un placeholder."""
    if img_base64:
        st.image(io.BytesIO(base64.b64decode(img_base64)), width=width)
    else:
        st.markdown(f'<div style="width:{width}px; height:{width}px; background-color:#f0f2f6; border-radius:10px; display:flex; align-items:center; justify-content:center; color:#555; text-align: center;">Sin foto</div>', unsafe_allow_html=True)

def formulario_socio(socio_data=None, es_edicion=False):
    """Formulario unificado para agregar o editar un socio."""
    defaults = socio_data if socio_data else {}
    ci_original = defaults.get('ci') if es_edicion else None
    
    with st.form(key=f"form_socio_{ci_original or 'nuevo'}", clear_on_submit=True):
        if es_edicion and defaults.get('foto'):
            st.subheader("📷 Foto Actual")
            mostrar_imagen_socio(defaults.get('foto'), width=120)
        
        col1, col2 = st.columns(2)
        with col1:
            ci = st.text_input("CI*", value=defaults.get('ci', ''), placeholder="Ej: 12345678", disabled=es_edicion)
            nombre = st.text_input("Nombre Completo*", value=defaults.get('nombre', ''), placeholder="Ej: Juan Pérez")
            celular = st.text_input("Celular", value=defaults.get('celular', ''), placeholder="Ej: 099123456")
        with col2:
            fecha_str = defaults.get('fecha_nacimiento')
            fecha_valor = datetime.strptime(fecha_str, '%Y-%m-%d').date() if fecha_str else None
            fecha_nacimiento = st.date_input("Fecha de Nacimiento", value=fecha_valor)
            tipos_cuota = ["Libre - $2000", "Solo Pesas - $800"]
            indice_cuota = tipos_cuota.index(defaults['tipo_cuota']) if defaults.get('tipo_cuota') in tipos_cuota else 0
            tipo_cuota = st.selectbox("Tipo de Cuota", tipos_cuota, index=indice_cuota)

        comentarios = st.text_area("Comentarios", value=defaults.get('comentarios', ''), placeholder="Preferencias, objetivos, etc.")
        nueva_foto = st.file_uploader("Subir/Cambiar foto", type=['png', 'jpg', 'jpeg'])
        eliminar_foto = st.checkbox("🗑️ Eliminar foto actual") if es_edicion and defaults.get('foto') else False

        submitted = st.form_submit_button(f"💾 {'Actualizar' if es_edicion else 'Guardar'} Socio", type="primary")

        if submitted:
            final_ci = ci_original or ci.strip()
            if not final_ci or not nombre.strip():
                st.error("CI y Nombre son campos obligatorios."); return

            foto_base64 = defaults.get('foto')
            if nueva_foto: foto_base64 = guardar_imagen_base64(nueva_foto)
            elif eliminar_foto: foto_base64 = None
                
            socio_actualizado = {
                'nombre': nombre.strip(), 'ci': final_ci, 'celular': celular.strip(),
                'contacto_emergencia': defaults.get('contacto_emergencia'), # Añadir estos campos al formulario si se desean
                'emergencia_movil': defaults.get('emergencia_movil'),
                'fecha_nacimiento': str(fecha_nacimiento) if fecha_nacimiento else '',
                'tipo_cuota': tipo_cuota, 'enfermedades': defaults.get('enfermedades'),
                'comentarios': comentarios.strip(), 'foto': foto_base64
            }
            if guardar_socio_db(final_ci, socio_actualizado):
                st.success(f"✅ Socio '{nombre}' {'actualizado' if es_edicion else 'guardado'}.")
                st.balloons()
                cargar_datos_desde_db() # Recargar datos en la sesión
                st.session_state.edit_mode = {} # Salir del modo edición
                st.rerun()

def pagina_socios():
    """Página para gestionar (ver, agregar, editar, eliminar) socios."""
    st.header("👥 Gestión de Socios")
    accion = st.radio("Elige una acción:", ["Ver Lista", "Agregar Nuevo"], horizontal=True, label_visibility="collapsed")

    if accion == "Agregar Nuevo":
        st.subheader("➕ Agregar Nuevo Socio")
        formulario_socio(es_edicion=False)

    elif accion == "Ver Lista":
        if not st.session_state.get('socios'):
            st.warning("No hay socios registrados. Agrega uno para comenzar.")
            return

        termino_busqueda = st.text_input("Buscar por nombre o CI...", placeholder="Escribe para buscar...").lower()
        socios_a_mostrar = {ci: data for ci, data in st.session_state.socios.items() if termino_busqueda in data['nombre'].lower() or termino_busqueda in ci}
        
        for ci, socio in socios_a_mostrar.items():
            with st.expander(f"{socio['nombre']} (CI: {ci})"):
                col1, col2 = st.columns([1, 2])
                with col1: mostrar_imagen_socio(socio.get('foto'), width=200)
                with col2:
                    st.write(f"**Celular:** {socio.get('celular') or 'N/A'}")
                    st.write(f"**Tipo de Cuota:** {socio.get('tipo_cuota')}")
                    if st.button("✏️ Editar", key=f"edit_{ci}"):
                        st.session_state.edit_mode = {ci: True}
                        st.rerun()
                    if st.button("🗑️ Eliminar", key=f"delete_{ci}", type="secondary"):
                        if eliminar_socio_db(ci):
                            cargar_datos_desde_db(); st.rerun()
                
                if st.session_state.get('edit_mode', {}).get(ci):
                    st.markdown("---")
                    st.subheader("✍️ Editando Socio")
                    formulario_socio(socio_data=socio, es_edicion=True)
                    if st.button("Cancelar Edición", key=f"cancel_edit_{ci}"):
                        st.session_state.edit_mode = {}; st.rerun()

# --- Bloque Principal de Ejecución ---

def main():
    """Función principal que ejecuta la aplicación Streamlit."""
    st.title("🥋 Sistema de Gestión de The Badgers")

    if 'app_initialized' not in st.session_state:
        init_database()
        cargar_datos_desde_db()
        st.session_state.app_initialized = True
        st.session_state.edit_mode = {}

    st.sidebar.title("Menú de Navegación")
    seleccion = st.sidebar.radio("Secciones", ["Socios", "Pagos", "Finanzas"], label_visibility="collapsed")
    st.sidebar.markdown("---")
    st.sidebar.info("Aplicación de gestión para la academia.")

    if seleccion == "Socios":
        pagina_socios()
    elif seleccion == "Pagos":
        st.header("💸 Gestión de Pagos")
        st.info("Sección en desarrollo.")
    elif seleccion == "Finanzas":
        st.header("💰 Resumen Financiero")
        st.info("Sección en desarrollo.")

if __name__ == "__main__":
    main()
