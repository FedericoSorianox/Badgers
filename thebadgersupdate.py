# Sistema de Gestión para Academia "The Badgers"
# Interfaz Web con Streamlit - Versión Final
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
    page_icon="🥋",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- Funciones de Utilidad ---

def get_db_connection():
    """Establishes a connection to the PostgreSQL database."""
    # --- CAMBIO CRÍTICO: Usamos os.environ.get() en lugar de st.secrets ---
    # Este es el método directo que funcionó en nuestra prueba de diagnóstico.
    conn_url = os.environ.get('DATABASE_URL')
    
    if not conn_url:
        st.error("Error Crítico: La variable de entorno DATABASE_URL no fue encontrada.")
        log_operacion("DATABASE_URL not found in os.environ", "error")
        return None
        
    try:
        return psycopg2.connect(conn_url)
    except Exception as e:
        st.error(f"Error de conexión a la base de datos: {e}")
        log_operacion(f"DB Connection Error: {e}", "error")
        return None

def log_operacion(mensaje, nivel="info"):
    """Imprime un mensaje de log con formato en la consola para depuración."""
    print(f"[{nivel.upper()}] {mensaje}")

@st.cache_data
def convert_df_to_csv(df):
    """Convierte un DataFrame a CSV para que pueda ser descargado."""
    return df.to_csv(index=False).encode('utf-8')

# --- Funciones de Base de Datos (PostgreSQL) ---

def db_execute(query, params=None, fetch=None):
    """Función genérica para ejecutar consultas en la BD."""
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
    """Inicializa la base de datos y crea todas las tablas si no existen."""
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
    """Carga todos los datos de todas las tablas."""
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

# --- El resto de las funciones (UI, páginas, etc.) se mantienen igual ---
# ... (Código completo y funcional aquí) ...
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
    """Formulario unificado para agregar o editar un socio."""
    defaults = socio_data if socio_data else {}
    ci_original = defaults.get('ci') if es_edicion else None
    
    with st.form(key=f"form_socio_{ci_original or 'nuevo'}", clear_on_submit=True):
        if es_edicion and defaults.get('foto'):
            st.subheader("📷 Foto Actual"); mostrar_imagen_socio(defaults.get('foto'), width=120)
        
        col1, col2 = st.columns(2)
        with col1:
            ci = st.text_input("CI*", value=defaults.get('ci', ''), placeholder="Ej: 12345678", disabled=es_edicion)
            nombre = st.text_input("Nombre Completo*", value=defaults.get('nombre', ''), placeholder="Ej: Juan Pérez")
            celular = st.text_input("Celular", value=defaults.get('celular', ''), placeholder="Ej: 099123456")
            contacto_emergencia = st.text_input("Contacto de Emergencia", value=defaults.get('contacto_emergencia', ''), placeholder="Ej: María Pérez")
        with col2:
            emergencia_movil = st.text_input("Teléfono de Emergencia", value=defaults.get('emergencia_movil', ''), placeholder="Ej: 098765432")
            fecha_str = str(defaults.get('fecha_nacimiento', ''))
            fecha_valor = datetime.strptime(fecha_str, '%Y-%m-%d').date() if fecha_str else None
            fecha_nacimiento = st.date_input("Fecha de Nacimiento", value=fecha_valor)
            tipos_cuota = ["Libre - $2000", "Solo Pesas - $800"]
            indice_cuota = tipos_cuota.index(defaults['tipo_cuota']) if defaults.get('tipo_cuota') in tipos_cuota else 0
            tipo_cuota = st.selectbox("Tipo de Cuota", tipos_cuota, index=indice_cuota)

        enfermedades = st.text_area("Enfermedades/Alergias", value=defaults.get('enfermedades', ''), placeholder="Opcional")
        comentarios = st.text_area("Comentarios", value=defaults.get('comentarios', ''), placeholder="Preferencias, objetivos, etc.")
        nueva_foto = st.file_uploader("Subir/Cambiar foto", type=['png', 'jpg', 'jpeg'])
        eliminar_foto = st.checkbox("🗑️ Eliminar foto actual") if es_edicion and defaults.get('foto') else False

        if st.form_submit_button(f"💾 {'Actualizar' if es_edicion else 'Guardar'} Socio", type="primary"):
            final_ci = ci_original or ci.strip()
            if not final_ci or not nombre.strip(): st.error("CI y Nombre son campos obligatorios."); return
            foto_base64 = defaults.get('foto')
            if nueva_foto: foto_base64 = guardar_imagen_base64(nueva_foto)
            elif eliminar_foto: foto_base64 = None
            socio_actualizado = {'nombre': nombre.strip(), 'ci': final_ci, 'celular': (celular or '').strip(), 'contacto_emergencia': (contacto_emergencia or '').strip(), 'emergencia_movil': (emergencia_movil or '').strip(), 'fecha_nacimiento': str(fecha_nacimiento) if fecha_nacimiento else '', 'tipo_cuota': tipo_cuota, 'enfermedades': (enfermedades or '').strip(), 'comentarios': (comentarios or '').strip(), 'foto': foto_base64}
            query = """INSERT INTO socios (ci, nombre, celular, contacto_emergencia, emergencia_movil, fecha_nacimiento, tipo_cuota, enfermedades, comentarios, foto) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s) ON CONFLICT (ci) DO UPDATE SET nombre = EXCLUDED.nombre, celular = EXCLUDED.celular, contacto_emergencia = EXCLUDED.contacto_emergencia, emergencia_movil = EXCLUDED.emergencia_movil, fecha_nacimiento = EXCLUDED.fecha_nacimiento, tipo_cuota = EXCLUDED.tipo_cuota, enfermedades = EXCLUDED.enfermedades, comentarios = EXCLUDED.comentarios, foto = EXCLUDED.foto;"""
            params = (final_ci, socio_actualizado['nombre'], socio_actualizado['celular'], socio_actualizado['contacto_emergencia'], socio_actualizado['emergencia_movil'], socio_actualizado['fecha_nacimiento'] or None, socio_actualizado['tipo_cuota'], socio_actualizado['enfermedades'], socio_actualizado['comentarios'], socio_actualizado['foto'])
            if db_execute(query, params):
                st.success(f"✅ Socio '{nombre}' guardado."); st.balloons(); cargar_todos_los_datos.clear(); st.session_state.edit_mode = {}; st.rerun()
# --- PÁGINAS ---
def pagina_dashboard(app_data):
    st.header("📊 Dashboard Principal")
    col1, col2, col3 = st.columns(3)
    col1.metric("Socios Activos", f"{len(app_data.get('socios', {}))} 👥")
    col2.metric("Productos en Inventario", f"{len(app_data.get('inventario', []))} 📦")
    total_gastos = sum(g['monto'] for g in app_data.get('gastos', []))
    col3.metric("Gastos Totales", f"${total_gastos:,.2f} �")
    st.markdown("---")
    st.subheader("Evolución de Socios Registrados")
    if app_data.get('socios'):
        df_socios = pd.DataFrame(app_data['socios'].values())
        if not df_socios.empty and 'fecha_registro' in df_socios.columns:
            df_socios['fecha_registro'] = pd.to_datetime(df_socios['fecha_registro'])
            df_socios_resampled = df_socios.set_index('fecha_registro').resample('M').size().reset_index(name='nuevos_socios')
            df_socios_resampled['total_acumulado'] = df_socios_resampled['nuevos_socios'].cumsum()
            fig = px.line(df_socios_resampled, x='fecha_registro', y='total_acumulado', title="Crecimiento de Socios a lo Largo del Tiempo", markers=True)
            st.plotly_chart(fig, use_container_width=True)
    st.subheader("Stock de Productos")
    if app_data.get('inventario'):
        df_inventario = pd.DataFrame(app_data['inventario'])
        if not df_inventario.empty:
            fig_stock = px.bar(df_inventario, x='nombre', y='stock', title="Niveles de Stock por Producto", color='nombre')
            st.plotly_chart(fig_stock, use_container_width=True)

def pagina_socios(app_data):
    st.header("👥 Gestión de Socios")
    accion = st.radio("Elige una acción:", ["Ver Lista", "Agregar Nuevo", "Importar/Exportar"], horizontal=True, label_visibility="collapsed")
    if accion == "Agregar Nuevo":
        st.subheader("➕ Agregar Nuevo Socio"); formulario_socio(es_edicion=False)
    elif accion == "Ver Lista":
        if not app_data.get('socios'): st.warning("No hay socios registrados."); return
        termino_busqueda = st.text_input("Buscar por nombre o CI...", "").lower()
        socios_a_mostrar = {ci: data for ci, data in app_data['socios'].items() if termino_busqueda in data['nombre'].lower() or termino_busqueda in ci}
        for ci, socio in socios_a_mostrar.items():
            with st.expander(f"{socio['nombre']} (CI: {ci})"):
                col1, col2 = st.columns([1, 2])
                with col1: mostrar_imagen_socio(socio.get('foto'), width=200)
                with col2:
                    if socio.get('tipo_cuota'): st.write(f"**Tipo de Cuota:** {socio['tipo_cuota']}")
                    if st.button("✏️ Editar", key=f"edit_{ci}"):
                        st.session_state.edit_mode = {ci: True}; st.rerun()
                    if st.session_state.get('confirm_delete_ci') == ci:
                        st.warning(f"**¿Estás seguro de que quieres eliminar a {socio['nombre']}?**")
                        if st.button("🔴 Sí, eliminar", key=f"confirm_delete_{ci}"):
                            if db_execute("DELETE FROM socios WHERE ci = %s", (ci,)):
                                st.success(f"Socio {socio['nombre']} eliminado.")
                                st.session_state.confirm_delete_ci = None; cargar_todos_los_datos.clear(); st.rerun()
                    else:
                        if st.button("🗑️ Eliminar", key=f"delete_{ci}", type="secondary"):
                            st.session_state.confirm_delete_ci = ci; st.rerun()
                if st.session_state.get('edit_mode', {}).get(ci):
                    st.markdown("---"); st.subheader("✍️ Editando Socio"); formulario_socio(socio_data=socio, es_edicion=True)
                    if st.button("Cancelar Edición", key=f"cancel_edit_{ci}"):
                        st.session_state.edit_mode = {}; st.rerun()
    elif accion == "Importar/Exportar":
        st.subheader("⬆️⬇️ Importar y Exportar Socios")
        st.markdown("#### Exportar a CSV")
        if app_data.get('socios'):
            df_socios = pd.DataFrame(app_data['socios'].values())
            if 'foto' in df_socios.columns: df_socios_export = df_socios.drop(columns=['foto'])
            else: df_socios_export = df_socios
            csv = convert_df_to_csv(df_socios_export); st.download_button(label="📥 Descargar lista de socios como CSV", data=csv, file_name=f"socios_{datetime.now().strftime('%Y%m%d')}.csv", mime='text/csv')
        st.markdown("---")
        st.markdown("#### Importar desde CSV")
        uploaded_file = st.file_uploader("Sube un archivo CSV.", type="csv")
        if uploaded_file:
            try:
                df_import = pd.read_csv(uploaded_file, dtype=str).fillna('')
                st.dataframe(df_import)
                if st.button("Confirmar Importación", type="primary"):
                    all_db_columns = ['ci', 'nombre', 'celular', 'contacto_emergencia', 'emergencia_movil', 'fecha_nacimiento', 'tipo_cuota', 'enfermedades', 'comentarios', 'foto']
                    df_import.columns = [col.lower().strip() for col in df_import.columns]
                    for _, row in df_import.iterrows():
                        if not row.get('ci') or not row.get('nombre'): continue
                        params_tuple = tuple(row.get(col, '') for col in all_db_columns)
                        query = "INSERT INTO socios (ci, nombre, celular, contacto_emergencia, emergencia_movil, fecha_nacimiento, tipo_cuota, enfermedades, comentarios, foto) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s) ON CONFLICT (ci) DO UPDATE SET nombre = EXCLUDED.nombre, celular = EXCLUDED.celular, contacto_emergencia = EXCLUDED.contacto_emergencia, emergencia_movil = EXCLUDED.emergencia_movil, fecha_nacimiento = EXCLUDED.fecha_nacimiento, tipo_cuota = EXCLUDED.tipo_cuota, enfermedades = EXCLUDED.enfermedades, comentarios = EXCLUDED.comentarios;"
                        db_execute(query, params_tuple)
                    st.success("Importación completada."); cargar_todos_los_datos.clear(); st.rerun()
            except Exception as e: st.error(f"Error al importar: {e}")

def pagina_pagos(app_data):
    st.header("💸 Gestión de Pagos")
    socios = app_data.get('socios', {});
    if not socios: st.warning("No hay socios registrados."); return
    hoy = datetime.now(); meses = ["Ene", "Feb", "Mar", "Abr", "May", "Jun", "Jul", "Ago", "Sep", "Oct", "Nov", "Dic"]
    año_actual = st.selectbox("Selecciona el año:", options=range(hoy.year + 1, hoy.year - 5, -1), index=0)
    data = [{'CI': ci, 'Socio': socio['nombre'], **{mes_nombre: "✅" if any(p['mes'] == i + 1 for p in app_data.get('pagos', []) if p['ci'] == ci and p['año'] == año_actual) else "❌" for i, mes_nombre in enumerate(meses)}} for ci, socio in socios.items()]
    st.dataframe(pd.DataFrame(data), use_container_width=True)
    st.subheader("Registrar Nuevo Pago")
    with st.form("form_pago", clear_on_submit=True):
        col1, col2, col3, col4 = st.columns(4)
        socio_ci = col1.selectbox("Socio*", options=list(socios.keys()), format_func=lambda ci: socios[ci]['nombre'])
        mes_pago = col2.selectbox("Mes*", options=list(range(1, 13)), format_func=lambda m: meses[m-1])
        año_pago = col3.number_input("Año*", min_value=2020, value=hoy.year)
        monto_pago = col4.number_input("Monto*", min_value=0.0)
        if st.form_submit_button("💾 Guardar Pago", type="primary"):
            id_pago = f"{socio_ci}_{mes_pago}_{año_pago}"
            query = "INSERT INTO pagos (id, ci, mes, año, monto, fecha_pago) VALUES (%s, %s, %s, %s, %s, %s) ON CONFLICT (ci, mes, año) DO UPDATE SET monto = EXCLUDED.monto, fecha_pago = EXCLUDED.fecha_pago"
            if db_execute(query, (id_pago, socio_ci, mes_pago, año_pago, monto_pago, datetime.now().date())):
                st.success("Pago registrado."); cargar_todos_los_datos.clear(); st.rerun()

def pagina_finanzas(app_data):
    st.header("💰 Gestión de Finanzas")
    with st.form("form_gastos", clear_on_submit=True):
        col1, col2, col3 = st.columns(3)
        concepto = col1.text_input("Concepto*"); fecha = col1.date_input("Fecha*", datetime.now())
        monto = col2.number_input("Monto*", min_value=0.0); categoria = col2.selectbox("Categoría", ["Alquiler", "Servicios", "Material", "Marketing", "Sueldos", "Otros"])
        descripcion = col3.text_area("Descripción")
        if st.form_submit_button("💸 Registrar Gasto", type="primary") and concepto and monto:
            query = "INSERT INTO gastos (concepto, monto, fecha, categoria, descripcion) VALUES (%s, %s, %s, %s, %s)"
            if db_execute(query, (concepto, monto, fecha, categoria, descripcion)):
                st.success("Gasto registrado."); cargar_todos_los_datos.clear(); st.rerun()
    st.subheader("Historial de Gastos")
    if app_data.get('gastos'): st.dataframe(pd.DataFrame(app_data['gastos']), use_container_width=True)

def pagina_inventario(app_data):
    st.header("📦 Gestión de Inventario")
    with st.form("form_inventario", clear_on_submit=True):
        col1, col2, col3 = st.columns(3)
        nombre_prod = col1.text_input("Nombre del Producto*")
        precio_prod = col2.number_input("Precio de Venta*", min_value=0.0)
        stock_prod = col3.number_input("Stock Inicial/Añadir*", min_value=0)
        if st.form_submit_button("📦 Guardar Producto", type="primary") and nombre_prod:
            query = "INSERT INTO inventario (nombre, precio_venta, stock) VALUES (%s, %s, %s) ON CONFLICT (nombre) DO UPDATE SET precio_venta = EXCLUDED.precio_venta, stock = inventario.stock + EXCLUDED.stock;"
            if db_execute(query, (nombre_prod, precio_prod, stock_prod)):
                st.success("Producto guardado."); cargar_todos_los_datos.clear(); st.rerun()
    st.subheader("Listado de Productos")
    if app_data.get('inventario'): st.dataframe(pd.DataFrame(app_data['inventario']), use_container_width=True, hide_index=True)

def pagina_administracion():
    st.header("⚙️ Administración del Sistema")
    st.warning("⚠️ **Atención:** Las acciones en esta sección son destructivas y no se pueden deshacer.")
    with st.expander("Reiniciar Base de Datos"):
        st.write("Esto borrará **TODAS** las tablas y las volverá a crear con la estructura más reciente.")
        if st.checkbox("Entiendo que esto borrará todos los datos existentes."):
            if st.button("🔴 REINICIAR BASE DE DATOS AHORA", type="primary"):
                with st.spinner("Reiniciando..."):
                    tables_to_drop = ["pagos", "gastos", "inventario", "socios"]
                    for table in tables_to_drop:
                        db_execute(f"DROP TABLE IF EXISTS {table} CASCADE;")
                    init_database()
                    cargar_todos_los_datos.clear()
                st.success("¡Base de datos reiniciada!"); st.balloons(); st.rerun()

# --- Bloque Principal de Ejecución ---
def main():
    st.title("🥋 Sistema de Gestión de The Badgers")
    
    conn = get_db_connection()
    if not conn:
        st.error("Error de conexión a la base de datos. Verifica la `DATABASE_URL` en los secretos de tu entorno en Render."); st.stop()
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
    
    page_map = {
        "Dashboard": pagina_dashboard, "Socios": pagina_socios, "Pagos": pagina_pagos,
        "Finanzas": pagina_finanzas, "Inventario": pagina_inventario, "Administración": pagina_administracion
    }
    page_to_run = page_map.get(seleccion, pagina_dashboard)
    if seleccion == "Administración":
        page_to_run()
    else:
        page_to_run(app_data)

if __name__ == "__main__":
    main()
