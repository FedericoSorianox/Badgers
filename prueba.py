# Sistema de Gestión - Academia de Artes Marciales
# Interfaz Web con Streamlit - VERSIÓN CON GASTOS UNIFICADOS
# Ejecutar con: streamlit run badgers_unified.py

import time
import uuid
import streamlit as st
import pandas as pd
import base64
from PIL import Image
import io
import json
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, date

# Configuración de la página
st.set_page_config(
    page_title="🥋 Academia de Artes Marciales",
    page_icon="🥋",
    layout="wide",
    initial_sidebar_state="expanded"
)

def inicializar_datos():
    """Inicializar datos de ejemplo si no existen"""
    if 'socios' not in st.session_state:
        st.session_state.socios = {
            '12345678': {
                'nombre': 'Juan Pérez',
                'ci': '12345678',
                'celular': '099123456',
                'contacto_emergencia': 'María Pérez',
                'emergencia_movil': '098765432',
                'fecha_nacimiento': '1990-05-15',
                'tipo_cuota': 'Libre - $2000',
                'enfermedades': 'Ninguna',
                'comentarios': 'Socio muy activo, prefiere entrenar por las mañanas',
                'foto': None
            },
            '87654321': {
                'nombre': 'Ana García',
                'ci': '87654321',
                'celular': '095456789',
                'contacto_emergencia': 'Pedro García',
                'emergencia_movil': '097123456',
                'fecha_nacimiento': '1985-12-03',
                'tipo_cuota': 'Solo Pesas - $800',
                'enfermedades': 'Alergia al polen',
                'comentarios': 'Interesada en clases grupales',
                'foto': None
            }
        }

    if 'pagos' not in st.session_state:
        st.session_state.pagos = {
            '12345678_Enero_2025': {
                'ci': '12345678',
                'mes': 'Enero',
                'año': 2025,
                'monto': 2000,
                'fecha_pago': '2025-01-15',
                'tipo_cuota': 'Libre - $2000'
            },
            '87654321_Enero_2025': {
                'ci': '87654321',
                'mes': 'Enero',
                'año': 2025,
                'monto': 800,
                'fecha_pago': '2025-01-20',
                'tipo_cuota': 'Solo Pesas - $800'
            }
        }

    # INVENTARIO
    if 'inventario' not in st.session_state:
        st.session_state.inventario = {
            'Guantes de boxeo': {
                'precio_unitario': 1200,
                'valor_unitario': 800,
                'stock_semanal': 10
            },
            'Protector bucal': {
                'precio_unitario': 350,
                'valor_unitario': 200,
                'stock_semanal': 25
            },
            'Vendas elásticas': {
                'precio_unitario': 150,
                'valor_unitario': 80,
                'stock_semanal': 50
            },
            'Pesas 5kg': {
                'precio_unitario': 2500,
                'valor_unitario': 1800,
                'stock_semanal': 8
            },
            'Colchonetas': {
                'precio_unitario': 3500,
                'valor_unitario': 2200,
                'stock_semanal': 12
            }
        }

    # GASTOS UNIFICADOS
    if 'gastos' not in st.session_state:
        st.session_state.gastos = {
            f"gasto_{int(time.time())}_1": {
                'concepto': 'Alquiler local',
                'monto': 15000,
                'fecha': '2025-01-01',
                'descripcion': 'Alquiler mensual del gimnasio',
                'categoria': 'Alquiler',
                'es_recurrente': True,
                'frecuencia': 'Mensual'
            },
            f"gasto_{int(time.time())}_2": {
                'concepto': 'Servicios (luz/agua)',
                'monto': 3500,
                'fecha': '2025-01-05',
                'descripcion': 'Servicios básicos',
                'categoria': 'Servicios',
                'es_recurrente': True,
                'frecuencia': 'Mensual'
            },
            f"gasto_{int(time.time())}_3": {
                'concepto': 'Internet y teléfono',
                'monto': 1200,
                'fecha': '2025-01-05',
                'descripcion': 'Conectividad y comunicaciones',
                'categoria': 'Servicios',
                'es_recurrente': True,
                'frecuencia': 'Mensual'
            },
            f"gasto_{int(time.time())}_4": {
                'concepto': 'Reparación equipo',
                'monto': 2500,
                'fecha': '2025-01-15',
                'descripcion': 'Reparación de máquina de pesas',
                'categoria': 'Mantenimiento',
                'es_recurrente': False,
                'frecuencia': 'Única vez'
            },
            f"gasto_{int(time.time())}_5": {
                'concepto': 'Compra productos limpieza',
                'monto': 800,
                'fecha': '2025-01-20',
                'descripcion': 'Productos de higiene y limpieza',
                'categoria': 'Limpieza',
                'es_recurrente': False,
                'frecuencia': 'Única vez'
            }
        }

def guardar_imagen_base64(imagen_file):
    """Convertir imagen a base64 para almacenamiento"""
    if imagen_file is not None:
        try:
            imagen_file.seek(0)
            file_bytes = imagen_file.read()
            if len(file_bytes) == 0:
                st.error("❌ El archivo está vacío")
                return None
            
            image = Image.open(io.BytesIO(file_bytes))
            max_size = (300, 300)
            image.thumbnail(max_size, Image.Resampling.LANCZOS)
            
            if image.mode != 'RGB':
                image = image.convert('RGB')
            
            buffer = io.BytesIO()
            image.save(buffer, format='JPEG', quality=85, optimize=True)
            
            img_bytes = buffer.getvalue()
            img_str = base64.b64encode(img_bytes).decode('utf-8')
            
            return img_str
                
        except Exception as e:
            st.error(f"❌ Error procesando imagen: {str(e)}")
            return None
    
    return None

def mostrar_imagen_socio(img_base64, width=150):
    """Mostrar imagen del socio desde base64"""
    if img_base64:
        try:
            img_html = f"""
            <div style="display: flex; justify-content: center; margin: 10px 0;">
                <img src="data:image/jpeg;base64,{img_base64}" 
                     style="width: {width}px; height: {width}px; 
                            object-fit: cover; border-radius: 10px; 
                            border: 2px solid #ddd; box-shadow: 0 2px 4px rgba(0,0,0,0.1);">
            </div>
            """
            st.markdown(img_html, unsafe_allow_html=True)
        except Exception as e:
            st.error(f"Error mostrando imagen: {str(e)}")
    else:
        placeholder_html = f"""
        <div style="display: flex; justify-content: center; margin: 10px 0;">
            <div style="width: {width}px; height: {width}px; 
                        background-color: #f0f0f0; border-radius: 10px; 
                        border: 2px solid #ddd; display: flex; 
                        align-items: center; justify-content: center; 
                        color: #999; font-size: 14px;">
                Sin foto
            </div>
        </div>
        """
        st.markdown(placeholder_html, unsafe_allow_html=True)

def formulario_socio(socio_data=None, es_edicion=False, ci_original=None):
    """Formulario unificado para agregar/editar socio"""
    form_id = str(uuid.uuid4())[:8]
    
    if socio_data:
        defaults = {
            'ci': socio_data.get('ci', ''),
            'nombre': socio_data.get('nombre', ''),
            'celular': socio_data.get('celular', ''),
            'contacto_emergencia': socio_data.get('contacto_emergencia', ''),
            'emergencia_movil': socio_data.get('emergencia_movil', ''),
            'fecha_nacimiento': socio_data.get('fecha_nacimiento', ''),
            'tipo_cuota': socio_data.get('tipo_cuota', 'Libre - $2000'),
            'enfermedades': socio_data.get('enfermedades', ''),
            'comentarios': socio_data.get('comentarios', ''),
            'foto': socio_data.get('foto', None)
        }
    else:
        defaults = {
            'ci': '', 'nombre': '', 'celular': '', 'contacto_emergencia': '',
            'emergencia_movil': '', 'fecha_nacimiento': '', 
            'tipo_cuota': 'Libre - $2000', 'enfermedades': '', 
            'comentarios': '', 'foto': None
        }
    
    with st.form(f"form_socio_{form_id}"):
        
        if es_edicion and defaults['foto']:
            st.subheader("📷 Foto Actual")
            mostrar_imagen_socio(defaults['foto'], width=120)
        
        if es_edicion:
            st.warning("⚠️ **Cambiar la CI actualizará todos los registros relacionados (pagos, etc.)**")
        
        col1, col2, col3 = st.columns([2, 2, 1])
        
        with col1:
            ci = st.text_input(
                "CI*", 
                value=defaults['ci'],
                placeholder="Ej: 12345678",
                key=f"ci_{form_id}"
            )
            
            if es_edicion and ci_original:
                st.caption(f"CI original: {ci_original}")
            
            nombre = st.text_input(
                "Nombre Completo*", 
                value=defaults['nombre'],
                placeholder="Ej: Juan Pérez",
                key=f"nombre_{form_id}"
            )
            
            celular = st.text_input(
                "Celular", 
                value=defaults['celular'],
                placeholder="Ej: 099123456",
                key=f"celular_{form_id}"
            )
            
            contacto_emergencia = st.text_input(
                "Contacto de Emergencia", 
                value=defaults['contacto_emergencia'],
                placeholder="Ej: María Pérez",
                key=f"contacto_{form_id}"
            )
        
        with col2:
            emergencia_movil = st.text_input(
                "Teléfono de Emergencia", 
                value=defaults['emergencia_movil'],
                placeholder="Ej: 098765432",
                key=f"emergencia_{form_id}"
            )
            
            fecha_valor = None
            if defaults['fecha_nacimiento']:
                try:
                    fecha_valor = datetime.strptime(defaults['fecha_nacimiento'], '%Y-%m-%d').date()
                except:
                    fecha_valor = None
            
            fecha_nacimiento = st.date_input(
                "Fecha de Nacimiento", 
                value=fecha_valor,
                key=f"fecha_{form_id}"
            )
            
            tipos_cuota = ["Libre - $2000", "Solo Pesas - $800"]
            indice_cuota = 0
            if defaults['tipo_cuota'] in tipos_cuota:
                indice_cuota = tipos_cuota.index(defaults['tipo_cuota'])
            
            tipo_cuota = st.selectbox(
                "Tipo de Cuota", 
                tipos_cuota,
                index=indice_cuota,
                key=f"tipo_cuota_{form_id}"
            )
            
            enfermedades = st.text_area(
                "Enfermedades/Alergias", 
                value=defaults['enfermedades'],
                placeholder="Opcional",
                height=80,
                key=f"enfermedades_{form_id}"
            )
        
        with col3:
            st.subheader("📷 Foto")
            
            nueva_foto = st.file_uploader(
                "Subir foto",
                type=['png', 'jpg', 'jpeg'],
                help="Formatos: PNG, JPG, JPEG",
                key=f"foto_{form_id}"
            )
            
            if nueva_foto is not None:
                st.write("👀 **Vista previa:**")
                try:
                    image = Image.open(nueva_foto)
                    st.image(image, width=150)
                except Exception as e:
                    st.error(f"Error cargando imagen: {str(e)}")
            
            if es_edicion and defaults['foto']:
                eliminar_foto = st.checkbox("🗑️ Eliminar foto actual", key=f"eliminar_foto_{form_id}")
            else:
                eliminar_foto = False
        
        st.markdown("---")
        st.subheader("💭 Comentarios")
        comentarios = st.text_area(
            "Comentarios adicionales sobre el socio:",
            value=defaults['comentarios'],
            placeholder="Ej: Preferencias de horarios, notas especiales, objetivos personales, etc.",
            height=100,
            key=f"comentarios_{form_id}"
        )
        
        st.markdown("---")
        col1, col2, col3 = st.columns([1, 1, 1])
        
        with col2:
            submitted = st.form_submit_button(
                f"💾 {'Actualizar' if es_edicion else 'Guardar'} Socio",
                type="primary",
                use_container_width=True
            )
        
        if submitted:
            if not ci.strip() or not nombre.strip():
                st.error("CI y nombre son obligatorios")
                return None
            
            if not ci.isdigit() or len(ci) < 7:
                st.error("CI debe tener al menos 7 dígitos numéricos")
                return None
            
            if es_edicion:
                ci_cambio = ci != ci_original
                if ci_cambio and ci in st.session_state.socios:
                    st.error(f"Ya existe otro socio con la CI: {ci}")
                    return None
            else:
                if ci in st.session_state.socios:
                    st.error("Ya existe un socio con ese CI")
                    return None
            
            foto_base64 = defaults.get('foto', None)
            
            if nueva_foto is not None:
                foto_base64 = guardar_imagen_base64(nueva_foto)
                if foto_base64 is None:
                    st.error("❌ Error procesando la imagen. Inténtelo nuevamente.")
                    return None
            
            elif eliminar_foto:
                foto_base64 = None
            
            socio_data_final = {
                'nombre': nombre.strip(),
                'ci': ci.strip(),
                'celular': celular.strip(),
                'contacto_emergencia': contacto_emergencia.strip(),
                'emergencia_movil': emergencia_movil.strip(),
                'fecha_nacimiento': str(fecha_nacimiento) if fecha_nacimiento else '',
                'tipo_cuota': tipo_cuota,
                'enfermedades': enfermedades.strip(),
                'comentarios': comentarios.strip(),
                'foto': foto_base64
            }
            
            return {
                'socio_data': socio_data_final,
                'ci_cambio': es_edicion and ci != ci_original,
                'ci_original': ci_original if es_edicion else None,
                'ci_nueva': ci.strip()
            }
    
    return None

def mostrar_agregar_socio():
    """Mostrar formulario para agregar socio"""
    st.subheader("➕ Agregar Nuevo Socio")
    
    st.info(f"📊 Socios actuales en el sistema: {len(st.session_state.socios)}")
    
    resultado = formulario_socio(es_edicion=False)
    
    if resultado:
        socio_data = resultado['socio_data']
        ci = socio_data['ci']
        
        try:
            if ci in st.session_state.socios:
                st.error(f"❌ Ya existe un socio con CI: {ci}")
                return
            
            st.session_state.socios[ci] = socio_data
            
            if ci in st.session_state.socios:
                socio_guardado = st.session_state.socios[ci]
                
                st.success(f"✅ Socio {socio_data['nombre']} guardado correctamente")
                
                if socio_guardado.get('foto'):
                    st.success(f"📸 CON FOTO guardada ({len(socio_guardado['foto'])} caracteres)")
                    st.write("👀 **Preview de la foto guardada:**")
                    mostrar_imagen_socio(socio_guardado['foto'], width=100)
                else:
                    st.info("📸 SIN FOTO")
                
                st.balloons()
                
                if st.button("👁️ Ver en Lista de Socios", key="ver_lista_nuevo"):
                    st.rerun()
            else:
                st.error("❌ Error: No se pudo guardar el socio en session_state")
                
        except Exception as e:
            st.error(f"❌ Error guardando socio: {str(e)}")

def show_dashboard():
    """Mostrar dashboard principal"""
    st.header("📊 Dashboard Principal")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric(
            label="👥 Socios Activos",
            value=len(st.session_state.socios),
            delta=None
        )
    
    with col2:
        total_pagos = len(st.session_state.pagos)
        st.metric(
            label="💳 Pagos Registrados",
            value=total_pagos,
            delta=None
        )
    
    with col3:
        ingresos = sum(p['monto'] for p in st.session_state.pagos.values())
        st.metric(
            label="💰 Ingresos Totales",
            value=f"${ingresos:,.0f}",
            delta=None
        )
    
    with col4:
        # Calcular todos los gastos
        gastos_totales = sum(g['monto'] for g in st.session_state.gastos.values())
        balance = ingresos - gastos_totales
        
        st.metric(
            label="📈 Balance",
            value=f"${balance:,.0f}",
            delta=f"${balance:,.0f}" if balance >= 0 else f"-${abs(balance):,.0f}",
            delta_color="normal" if balance >= 0 else "inverse"
        )
    
    st.markdown("---")
    
    # Análisis Financiero Mensual
    st.subheader("📊 Análisis Financiero Mensual")
    
    año_actual = datetime.now().year
    meses = ['Enero', 'Febrero', 'Marzo', 'Abril', 'Mayo', 'Junio',
             'Julio', 'Agosto', 'Septiembre', 'Octubre', 'Noviembre', 'Diciembre']
    
    # Ingresos mensuales
    ingresos_mensuales = {}
    for pago in st.session_state.pagos.values():
        if pago.get('año') == año_actual:
            mes = pago.get('mes', 'Sin especificar')
            monto = pago.get('monto', 0)
            ingresos_mensuales[mes] = ingresos_mensuales.get(mes, 0) + monto
    
    # Gastos por mes
    gastos_mensuales = {}
    for gasto in st.session_state.gastos.values():
        try:
            fecha_gasto = datetime.strptime(gasto.get('fecha', ''), '%Y-%m-%d')
            if fecha_gasto.year == año_actual:
                mes_nombre = meses[fecha_gasto.month - 1]
                monto = gasto.get('monto', 0)
                gastos_mensuales[mes_nombre] = gastos_mensuales.get(mes_nombre, 0) + monto
        except:
            continue
    
    # Preparar datos para la gráfica
    mes_actual_num = datetime.now().month
    meses_activos = meses[:mes_actual_num]
    
    ingresos_data = [ingresos_mensuales.get(mes, 0) for mes in meses_activos]
    gastos_data = [gastos_mensuales.get(mes, 0) for mes in meses_activos]
    diferencia_data = [ing - gasto for ing, gasto in zip(ingresos_data, gastos_data)]
    
    if meses_activos:
        fig = go.Figure()
        
        fig.add_trace(go.Bar(
            name='Ingresos',
            x=meses_activos,
            y=ingresos_data,
            marker_color='#28a745'
        ))
        
        fig.add_trace(go.Bar(
            name='Gastos',
            x=meses_activos,
            y=gastos_data,
            marker_color='#dc3545'
        ))
        
        fig.add_trace(go.Scatter(
            name='Diferencia',
            x=meses_activos,
            y=diferencia_data,
            mode='lines+markers',
            line=dict(color='#007bff', width=3),
            marker=dict(size=8)
        ))
        
        fig.update_layout(
            title=f'Ingresos vs Gastos Mensuales - {año_actual}',
            xaxis_title='Mes',
            yaxis_title='Monto ($)',
            barmode='group',
            hovermode='x unified'
        )
        
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("No hay datos financieros para mostrar este año")

def show_inventario():
    """Mostrar gestión de inventario"""
    st.header("📦 Gestión de Inventario")
    
    tab1, tab2 = st.tabs(["📋 Lista de Productos", "➕ Agregar Producto"])
    
    with tab1:
        st.subheader("Inventario de Productos")
        
        if st.session_state.inventario:
            productos_display = []
            total_valor_costo = 0
            total_valor_venta = 0
            total_ganancia_potencial = 0
            
            for nombre, producto in st.session_state.inventario.items():
                precio_unitario = producto.get('precio_unitario', 0)
                valor_unitario = producto.get('valor_unitario', 0)
                stock_semanal = producto.get('stock_semanal', 0)
                
                ganancia_unitaria = precio_unitario - valor_unitario
                valor_total_costo = stock_semanal * valor_unitario
                valor_total_venta = stock_semanal * precio_unitario
                ganancia_total = stock_semanal * ganancia_unitaria
                
                total_valor_costo += valor_total_costo
                total_valor_venta += valor_total_venta
                total_ganancia_potencial += ganancia_total
                
                if stock_semanal == 0:
                    estado = "🔴 Sin stock"
                elif stock_semanal <= 5:
                    estado = "🟡 Bajo"
                else:
                    estado = "🟢 OK"
                
                productos_display.append({
                    'Producto': nombre,
                    'Precio Unit.': f"${precio_unitario:,.0f}",
                    'Valor Unit.': f"${valor_unitario:,.0f}",
                    'Ganancia Unit.': f"${ganancia_unitaria:,.0f}",
                    'Stock Semanal': stock_semanal,
                    'Valor Total Costo': f"${valor_total_costo:,.0f}",
                    'Valor Total Venta': f"${valor_total_venta:,.0f}",
                    'Estado': estado
                })
            
            df_inventario = pd.DataFrame(productos_display)
            st.dataframe(df_inventario, use_container_width=True, hide_index=True)
            
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("💰 Valor Total (Costo)", f"${total_valor_costo:,.0f}")
            with col2:
                st.metric("💵 Valor Total (Venta)", f"${total_valor_venta:,.0f}")
            with col3:
                st.metric("📈 Ganancia Potencial", f"${total_ganancia_potencial:,.0f}")
            
            col1, col2 = st.columns([3, 1])
            with col2:
                producto_actualizar = st.selectbox(
                    "Actualizar stock:",
                    ["Seleccionar..."] + list(st.session_state.inventario.keys()),
                    key="select_producto"
                )
                
                if producto_actualizar != "Seleccionar...":
                    producto_data = st.session_state.inventario.get(producto_actualizar, {})
                    stock_actual = producto_data.get('stock_semanal', 0)
                    
                    nuevo_stock = st.number_input(
                        f"Nuevo stock semanal para {producto_actualizar}:",
                        min_value=0,
                        value=stock_actual,
                        key="nuevo_stock"
                    )
                    
                    if st.button("🔄 Actualizar Stock", key="actualizar_stock"):
                        st.session_state.inventario[producto_actualizar]['stock_semanal'] = nuevo_stock
                        st.success("Stock actualizado correctamente")
                        st.rerun()
        else:
            st.info("No hay productos en inventario")
    
    with tab2:
        st.subheader("Agregar Producto")
        
        with st.form("form_producto"):
            nombre_producto = st.text_input("Nombre del Producto*", placeholder="Ej: Guantes de boxeo")
            
            col1, col2 = st.columns(2)
            with col1:
                precio_unitario = st.number_input("Precio Unitario (Venta)*", min_value=0.0, value=0.0, step=0.01)
                valor_unitario = st.number_input("Valor Unitario (Costo)*", min_value=0.0, value=0.0, step=0.01)
            with col2:
                stock_semanal = st.number_input("Stock Semanal*", min_value=0, value=0)
                
                if precio_unitario > 0 and valor_unitario > 0:
                    ganancia = precio_unitario - valor_unitario
                    margen = (ganancia / precio_unitario) * 100 if precio_unitario > 0 else 0
                    st.metric("📈 Ganancia Unitaria", f"${ganancia:,.2f}")
                    st.metric("📊 Margen de Ganancia", f"{margen:.1f}%")
            
            submitted = st.form_submit_button("💾 Agregar Producto")
            
            if submitted:
                if not nombre_producto.strip():
                    st.error("El nombre del producto es obligatorio")
                elif nombre_producto in st.session_state.inventario:
                    st.error("Ya existe un producto con ese nombre")
                elif precio_unitario <= 0 or valor_unitario <= 0:
                    st.error("Precio unitario y valor unitario deben ser mayor a 0")
                elif valor_unitario >= precio_unitario:
                    st.error("El valor unitario (costo) debe ser menor al precio unitario (venta)")
                elif stock_semanal < 0:
                    st.error("Stock semanal no puede ser negativo")
                else:
                    st.session_state.inventario[nombre_producto] = {
                        'precio_unitario': precio_unitario,
                        'valor_unitario': valor_unitario,
                        'stock_semanal': stock_semanal
                    }
                    ganancia = precio_unitario - valor_unitario
                    st.success(f"Producto {nombre_producto} agregado correctamente")
                    st.info(f"Ganancia unitaria: ${ganancia:,.2f}")
                    st.rerun()

def show_gastos():
    """Mostrar gestión de gastos unificados"""
    st.header("💸 Gestión de Gastos")
    
    # Verificar si hay un gasto en modo edición
    if 'editando_gasto' in st.session_state:
        mostrar_modal_edicion_gasto(st.session_state.editando_gasto)
    else:
        tab1, tab2 = st.tabs([
            "📋 Lista de Gastos", 
            "➕ Agregar Gasto"
        ])
        
        with tab1:
            mostrar_lista_gastos()
        
        with tab2:
            mostrar_agregar_gasto()

def mostrar_lista_gastos():
    """Mostrar lista de gastos unificados"""
    st.subheader("💸 Todos los Gastos")
    
    if st.session_state.gastos:
        # Filtros
        col1, col2, col3 = st.columns(3)
        
        with col1:
            categorias_unicas = ["Todas"] + list(set(g.get('categoria', 'Sin categoría') for g in st.session_state.gastos.values()))
            categoria_filtro = st.selectbox("Filtrar por categoría:", categorias_unicas)
        
        with col2:
            tipos_gasto = ["Todos", "Recurrentes", "Únicos"]
            tipo_filtro = st.selectbox("Filtrar por tipo:", tipos_gasto)
        
        with col3:
            orden = st.selectbox("Ordenar por:", ["Fecha (más reciente)", "Fecha (más antigua)", "Monto (mayor)", "Monto (menor)"])
        
        # Filtrar gastos
        gastos_filtrados = {}
        for gasto_id, gasto in st.session_state.gastos.items():
            incluir = True
            
            # Filtro por categoría
            if categoria_filtro != "Todas" and gasto.get('categoria', 'Sin categoría') != categoria_filtro:
                incluir = False
            
            # Filtro por tipo
            if tipo_filtro == "Recurrentes" and not gasto.get('es_recurrente', False):
                incluir = False
            elif tipo_filtro == "Únicos" and gasto.get('es_recurrente', False):
                incluir = False
            
            if incluir:
                gastos_filtrados[gasto_id] = gasto
        
        # Ordenar gastos
        if orden == "Fecha (más reciente)":
            gastos_ordenados = sorted(gastos_filtrados.items(), key=lambda x: x[1].get('fecha', ''), reverse=True)
        elif orden == "Fecha (más antigua)":
            gastos_ordenados = sorted(gastos_filtrados.items(), key=lambda x: x[1].get('fecha', ''))
        elif orden == "Monto (mayor)":
            gastos_ordenados = sorted(gastos_filtrados.items(), key=lambda x: x[1].get('monto', 0), reverse=True)
        else:  # Monto (menor)
            gastos_ordenados = sorted(gastos_filtrados.items(), key=lambda x: x[1].get('monto', 0))
        
        # Mostrar gastos
        total_gastos = 0
        total_recurrentes = 0
        total_unicos = 0
        
        for gasto_id, gasto in gastos_ordenados:
            monto = gasto.get('monto', 0)
            total_gastos += monto
            
            if gasto.get('es_recurrente', False):
                total_recurrentes += monto
            else:
                total_unicos += monto
            
            with st.container():
                # Color de fondo según si es recurrente o no
                color_fondo = "#e8f4f8" if gasto.get('es_recurrente', False) else "#fff3cd"
                
                st.markdown(f"""
                <div style="border: 1px solid #ddd; border-radius: 10px; 
                           padding: 15px; margin: 10px 0; background-color: {color_fondo};
                           box-shadow: 0 2px 4px rgba(0,0,0,0.1);">
                """, unsafe_allow_html=True)
                
                col1, col2, col3 = st.columns([3, 2, 1])
                
                with col1:
                    tipo_badge = "🔄 Recurrente" if gasto.get('es_recurrente', False) else "📌 Único"
                    st.markdown(f"**{tipo_badge} - {gasto.get('concepto', 'Sin concepto')}**")
                    st.markdown(f"💰 Monto: **${monto:,.0f}**")
                    st.markdown(f"📅 Fecha: **{gasto.get('fecha', 'Sin fecha')}**")
                    st.markdown(f"🏷️ Categoría: **{gasto.get('categoria', 'Sin categoría')}**")
                    
                    if gasto.get('es_recurrente', False):
                        st.markdown(f"📆 Frecuencia: **{gasto.get('frecuencia', 'No especificada')}**")
                    
                    descripcion = gasto.get('descripcion', '').strip()
                    if descripcion:
                        st.markdown(f"📝 {descripcion}")
                
                with col2:
                    # Calcular impacto anual si es recurrente
                    if gasto.get('es_recurrente', False):
                        frecuencia = gasto.get('frecuencia', 'Mensual')
                        if frecuencia == 'Mensual':
                            impacto_anual = monto * 12
                        elif frecuencia == 'Trimestral':
                            impacto_anual = monto * 4
                        elif frecuencia == 'Semestral':
                            impacto_anual = monto * 2
                        elif frecuencia == 'Anual':
                            impacto_anual = monto
                        else:
                            impacto_anual = monto
                        
                        st.markdown(f"📊 **Impacto anual:** ${impacto_anual:,.0f}")
                    
                    # Días desde el gasto
                    try:
                        fecha_gasto = datetime.strptime(gasto.get('fecha', ''), '%Y-%m-%d').date()
                        dias_transcurridos = (date.today() - fecha_gasto).days
                        st.markdown(f"📆 Hace **{dias_transcurridos}** días")
                    except:
                        st.markdown("📆 Fecha inválida")
                
                with col3:
                    col_edit, col_del = st.columns(2)
                    
                    with col_edit:
                        if st.button("✏️", key=f"edit_gasto_{gasto_id}", help="Editar gasto"):
                            st.session_state.editando_gasto = gasto_id
                            st.rerun()
                    
                    with col_del:
                        if st.button("🗑️", key=f"del_gasto_{gasto_id}", help="Eliminar gasto"):
                            st.session_state.confirmar_eliminar_gasto = gasto_id
                            st.rerun()
                
                st.markdown("</div>", unsafe_allow_html=True)
        
        # Mostrar totales
        st.markdown("---")
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("💰 Total Gastos", f"${total_gastos:,.0f}")
        with col2:
            st.metric("🔄 Gastos Recurrentes", f"${total_recurrentes:,.0f}")
        with col3:
            st.metric("📌 Gastos Únicos", f"${total_unicos:,.0f}")
        with col4:
            st.metric("📊 Cantidad de Gastos", len(gastos_filtrados))
        
        # Modal de confirmación de eliminación
        if 'confirmar_eliminar_gasto' in st.session_state:
            mostrar_confirmacion_eliminar_gasto()
    
    else:
        st.info("No hay gastos registrados")

def mostrar_agregar_gasto():
    """Mostrar formulario para agregar gasto"""
    st.subheader("➕ Agregar Nuevo Gasto")
    
    with st.form("form_gasto_nuevo"):
        col1, col2 = st.columns(2)
        
        with col1:
            concepto = st.text_input("Concepto del Gasto*", placeholder="Ej: Alquiler local")
            monto = st.number_input("Monto*", min_value=0.0, value=0.0, step=0.01)
            fecha = st.date_input("Fecha del Gasto*", value=date.today())
        
        with col2:
            categorias = [
                "Alquiler", "Servicios", "Mantenimiento", "Limpieza", 
                "Equipamiento", "Marketing", "Capacitación", "Otros"
            ]
            categoria = st.selectbox("Categoría*", categorias)
            
            es_recurrente = st.checkbox("¿Es un gasto recurrente?", value=False)
            
            if es_recurrente:
                frecuencias = ["Mensual", "Trimestral", "Semestral", "Anual"]
                frecuencia = st.selectbox("Frecuencia*", frecuencias)
            else:
                frecuencia = "Única vez"
        
        descripcion = st.text_area(
            "Descripción (opcional)", 
            placeholder="Detalles adicionales sobre este gasto...",
            height=80
        )
        
        # Mostrar información adicional si es recurrente
        if es_recurrente:
            st.info(f"💡 Este gasto se repetirá de forma **{frecuencia.lower()}**")
            if frecuencia == "Mensual":
                impacto_anual = monto * 12
            elif frecuencia == "Trimestral":
                impacto_anual = monto * 4
            elif frecuencia == "Semestral":
                impacto_anual = monto * 2
            else:  # Anual
                impacto_anual = monto
            
            if monto > 0:
                st.warning(f"⚠️ Impacto anual estimado: **${impacto_anual:,.0f}**")
        
        submitted = st.form_submit_button("💾 Agregar Gasto")
        
        if submitted:
            if not concepto.strip():
                st.error("El concepto es obligatorio")
            elif monto <= 0:
                st.error("El monto debe ser mayor a 0")
            else:
                # Generar ID único para el gasto
                gasto_id = f"gasto_{int(time.time())}_{uuid.uuid4().hex[:8]}"
                
                st.session_state.gastos[gasto_id] = {
                    'concepto': concepto.strip(),
                    'monto': monto,
                    'fecha': str(fecha),
                    'categoria': categoria,
                    'descripcion': descripcion.strip(),
                    'es_recurrente': es_recurrente,
                    'frecuencia': frecuencia
                }
                
                tipo_texto = "recurrente" if es_recurrente else "único"
                st.success(f"✅ Gasto {tipo_texto} '{concepto}' agregado correctamente")
                st.balloons()
                st.rerun()

def mostrar_modal_edicion_gasto(gasto_id):
    """Mostrar modal de edición de gasto"""
    gasto_actual = st.session_state.gastos.get(gasto_id)
    
    if not gasto_actual:
        st.error("❌ Gasto no encontrado")
        if st.button("🔙 Volver a la Lista", key=f"volver_error_gasto_{gasto_id}"):
            del st.session_state.editando_gasto
            st.rerun()
        return
    
    col1, col2 = st.columns([4, 1])
    
    with col1:
        st.subheader(f"✏️ Editando Gasto: {gasto_actual.get('concepto', 'Sin concepto')}")
        st.caption(f"Monto actual: ${gasto_actual.get('monto', 0):,.0f}")
    
    with col2:
        if st.button("❌ Cancelar", type="secondary", key=f"cancelar_edicion_gasto_{gasto_id}"):
            del st.session_state.editando_gasto
            st.rerun()
    
    st.markdown("---")
    
    with st.form(f"form_editar_gasto_{gasto_id}"):
        col1, col2 = st.columns(2)
        
        with col1:
            nuevo_concepto = st.text_input(
                "Concepto del Gasto*", 
                value=gasto_actual.get('concepto', ''),
                placeholder="Ej: Alquiler local"
            )
            
            nuevo_monto = st.number_input(
                "Monto*", 
                min_value=0.0, 
                value=float(gasto_actual.get('monto', 0)),
                step=0.01
            )
            
            try:
                fecha_actual = datetime.strptime(gasto_actual.get('fecha', ''), '%Y-%m-%d').date()
            except:
                fecha_actual = date.today()
            
            nueva_fecha = st.date_input(
                "Fecha del Gasto*", 
                value=fecha_actual
            )
        
        with col2:
            categorias = [
                "Alquiler", "Servicios", "Mantenimiento", "Limpieza", 
                "Equipamiento", "Marketing", "Capacitación", "Otros"
            ]
            categoria_actual = gasto_actual.get('categoria', 'Otros')
            indice_categoria = categorias.index(categoria_actual) if categoria_actual in categorias else 0
            
            nueva_categoria = st.selectbox(
                "Categoría*", 
                categorias,
                index=indice_categoria
            )
            
            es_recurrente_actual = gasto_actual.get('es_recurrente', False)
            nuevo_es_recurrente = st.checkbox(
                "¿Es un gasto recurrente?", 
                value=es_recurrente_actual
            )
            
            if nuevo_es_recurrente:
                frecuencias = ["Mensual", "Trimestral", "Semestral", "Anual"]
                frecuencia_actual = gasto_actual.get('frecuencia', 'Mensual')
                indice_frecuencia = frecuencias.index(frecuencia_actual) if frecuencia_actual in frecuencias else 0
                
                nueva_frecuencia = st.selectbox(
                    "Frecuencia*", 
                    frecuencias,
                    index=indice_frecuencia
                )
            else:
                nueva_frecuencia = "Única vez"
        
        nueva_descripcion = st.text_area(
            "Descripción (opcional)", 
            value=gasto_actual.get('descripcion', ''),
            placeholder="Detalles adicionales sobre este gasto...",
            height=80
        )
        
        col1, col2, col3 = st.columns([1, 1, 1])
        
        with col2:
            submitted = st.form_submit_button(
                "💾 Actualizar Gasto",
                type="primary",
                use_container_width=True
            )
        
        if submitted:
            if not nuevo_concepto.strip():
                st.error("El concepto es obligatorio")
            elif nuevo_monto <= 0:
                st.error("El monto debe ser mayor a 0")
            else:
                # Actualizar gasto
                st.session_state.gastos[gasto_id] = {
                    'concepto': nuevo_concepto.strip(),
                    'monto': nuevo_monto,
                    'fecha': str(nueva_fecha),
                    'categoria': nueva_categoria,
                    'descripcion': nueva_descripcion.strip(),
                    'es_recurrente': nuevo_es_recurrente,
                    'frecuencia': nueva_frecuencia
                }
                
                del st.session_state.editando_gasto
                st.success("✅ Gasto actualizado correctamente")
                st.rerun()

def mostrar_confirmacion_eliminar_gasto():
    """Mostrar modal de confirmación para eliminar gasto"""
    gasto_id = st.session_state.confirmar_eliminar_gasto
    gasto_eliminar = st.session_state.gastos.get(gasto_id, {})
    
    st.markdown("---")
    st.error(f"⚠️ ¿Está seguro de eliminar el gasto **{gasto_eliminar.get('concepto', 'Sin concepto')}**?")
    
    col_info1, col_info2 = st.columns(2)
    with col_info1:
        st.write(f"**Concepto:** {gasto_eliminar.get('concepto', 'Sin concepto')}")
        st.write(f"**Monto:** ${gasto_eliminar.get('monto', 0):,.0f}")
        st.write(f"**Fecha:** {gasto_eliminar.get('fecha', 'Sin fecha')}")
    with col_info2:
        st.write(f"**Categoría:** {gasto_eliminar.get('categoria', 'Sin categoría')}")
        tipo = "Recurrente" if gasto_eliminar.get('es_recurrente', False) else "Único"
        st.write(f"**Tipo:** {tipo}")
        if gasto_eliminar.get('es_recurrente', False):
            st.write(f"**Frecuencia:** {gasto_eliminar.get('frecuencia', 'No especificada')}")
    
    descripcion = gasto_eliminar.get('descripcion', '').strip()
    if descripcion:
        st.write(f"**Descripción:** {descripcion}")
    
    st.warning("⚠️ Esta acción no se puede deshacer.")
    
    col1, col2, col3 = st.columns([1, 1, 1])
    
    with col1:
        if st.button("✅ Sí, eliminar", type="primary", key=f"confirmar_del_gasto_{gasto_id}"):
            del st.session_state.gastos[gasto_id]
            del st.session_state.confirmar_eliminar_gasto
            st.success(f"✅ Gasto eliminado correctamente")
            st.rerun()
    
    with col3:
        if st.button("❌ Cancelar", key=f"cancelar_del_gasto_{gasto_id}"):
            del st.session_state.confirmar_eliminar_gasto
            st.rerun()

def show_socios():
    """Mostrar gestión de socios"""
    st.header("👥 Gestión de Socios")
    
    # Verificar si hay un socio en modo edición
    if 'editando_socio' in st.session_state:
        mostrar_modal_edicion(st.session_state.editando_socio)
    else:
        tab1, tab2, tab3, tab4 = st.tabs([
            "📋 Lista de Socios", 
            "➕ Agregar Socio",
            "🔍 Buscar Socio",
            "📊 Importar CSV"
        ])
        
        with tab1:
            mostrar_lista_socios()
        
        with tab2:
            mostrar_agregar_socio()
        
        with tab3:
            mostrar_buscar_socio()
        
        with tab4:
            mostrar_importar_csv()
            # Calcular total_pendiente para mostrar el metric
            total_pendiente = 0
            meses = ['Enero', 'Febrero', 'Marzo', 'Abril', 'Mayo', 'Junio',
                     'Julio', 'Agosto', 'Septiembre', 'Octubre', 'Noviembre', 'Diciembre']
            año_verificar = datetime.now().year
            mes_actual = datetime.now().month
            for ci, socio in st.session_state.socios.items():
                tipo_cuota = socio.get('tipo_cuota', 'Libre - $2000')
                monto_cuota = 2000 if '2000' in tipo_cuota else 800
                for i in range(mes_actual):
                    mes = meses[i]
                    pago_key = f"{ci}_{mes}_{año_verificar}"
                    if pago_key not in st.session_state.pagos:
                        total_pendiente += monto_cuota
            st.metric("💰 Total Pendiente", f"${total_pendiente:,.0f}")
        # else removed because it was not needed and caused a syntax error

def show_estadisticas():
    
    """Mostrar estadísticas detalladas"""
    st.header("📈 Estadísticas Financieras")
    
    año_actual = datetime.now().year
    mes_actual = datetime.now().month
    
    ingresos_año = sum(p.get('monto', 0) for p in st.session_state.pagos.values() 
                      if p.get('año') == año_actual)
    
    # Calcular gastos del año
    gastos_año = 0
    for gasto in st.session_state.gastos.values():
        try:
            fecha_gasto = datetime.strptime(gasto.get('fecha', ''), '%Y-%m-%d')
            if fecha_gasto.year == año_actual:
                monto = gasto.get('monto', 0)
                
                # Si es recurrente, calcular el impacto hasta el mes actual
                if gasto.get('es_recurrente', False):
                    frecuencia = gasto.get('frecuencia', 'Mensual')
                    mes_gasto = fecha_gasto.month
                    
                    if frecuencia == 'Mensual':
                        # Contar desde el mes del gasto hasta el mes actual
                        meses_transcurridos = mes_actual - mes_gasto + 1
                        gastos_año += monto * meses_transcurridos
                    elif frecuencia == 'Trimestral':
                        trimestres = ((mes_actual - mes_gasto) // 3) + 1
                        gastos_año += monto * trimestres
                    elif frecuencia == 'Semestral':
                        semestres = ((mes_actual - mes_gasto) // 6) + 1
                        gastos_año += monto * semestres
                    elif frecuencia == 'Anual':
                        gastos_año += monto
                else:
                    # Gasto único
                    gastos_año += monto
        except:
            continue
    
    balance_año = ingresos_año - gastos_año
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("👥 Socios Activos", len(st.session_state.socios))
    
    with col2:
        st.metric("💰 Ingresos del Año", f"${ingresos_año:,.0f}")
    
    with col3:
        st.metric("💸 Gastos del Año", f"${gastos_año:,.0f}")
    
    with col4:
        st.metric(
            "📈 Balance del Año", 
            f"${balance_año:,.0f}",
            delta=f"${balance_año:,.0f}" if balance_año >= 0 else f"-${abs(balance_año):,.0f}",
            delta_color="normal" if balance_año >= 0 else "inverse"
        )
    
    st.markdown("---")
    
    # Desglose de gastos
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("💸 Desglose de Gastos por Tipo")
        
        gastos_recurrentes = 0
        gastos_unicos = 0
        
        for gasto in st.session_state.gastos.values():
            try:
                fecha_gasto = datetime.strptime(gasto.get('fecha', ''), '%Y-%m-%d')
                if fecha_gasto.year == año_actual:
                    monto = gasto.get('monto', 0)
                    
                    if gasto.get('es_recurrente', False):
                        frecuencia = gasto.get('frecuencia', 'Mensual')
                        mes_gasto = fecha_gasto.month
                        
                        if frecuencia == 'Mensual':
                            meses_transcurridos = mes_actual - mes_gasto + 1
                            gastos_recurrentes += monto * meses_transcurridos
                        elif frecuencia == 'Trimestral':
                            trimestres = ((mes_actual - mes_gasto) // 3) + 1
                            gastos_recurrentes += monto * trimestres
                        elif frecuencia == 'Semestral':
                            semestres = ((mes_actual - mes_gasto) // 6) + 1
                            gastos_recurrentes += monto * semestres
                        elif frecuencia == 'Anual':
                            gastos_recurrentes += monto
                    else:
                        gastos_unicos += monto
            except:
                continue
        
        col_rec, col_uni = st.columns(2)
        with col_rec:
            st.metric("🔄 Gastos Recurrentes", f"${gastos_recurrentes:,.0f}")
        with col_uni:
            st.metric("📌 Gastos Únicos", f"${gastos_unicos:,.0f}")
        
        # Gráfico de torta
        if gastos_recurrentes > 0 or gastos_unicos > 0:
            fig_pie = px.pie(
                values=[gastos_recurrentes, gastos_unicos],
                names=['Recurrentes', 'Únicos'],
                title="Distribución de Gastos por Tipo"
            )
            st.plotly_chart(fig_pie, use_container_width=True)
    
    with col2:
        st.subheader("📊 Evolución de Ingresos")
        ingresos_mes = {}
        for pago in st.session_state.pagos.values():
            if pago.get('año') == año_actual:
                mes = pago.get('mes', 'Sin especificar')
                monto = pago.get('monto', 0)
                ingresos_mes[mes] = ingresos_mes.get(mes, 0) + monto
        
        if ingresos_mes:
            fig_line = px.line(
                x=list(ingresos_mes.keys()),
                y=list(ingresos_mes.values()),
                title=f"Ingresos por Mes - {año_actual}",
                markers=True
            )
            fig_line.update_layout(showlegend=False)
            st.plotly_chart(fig_line, use_container_width=True)
        else:
            st.info("No hay datos de ingresos para mostrar")
    
    st.subheader("🔮 Proyecciones Anuales")
    if mes_actual > 0:
        # Proyección de ingresos
        proyeccion_ingresos = (ingresos_año / mes_actual) * 12
        
        # Proyección de gastos recurrentes
        gastos_recurrentes_mensuales = 0
        for gasto in st.session_state.gastos.values():
            if gasto.get('es_recurrente', False):
                monto = gasto.get('monto', 0)
                frecuencia = gasto.get('frecuencia', 'Mensual')
                
                if frecuencia == 'Mensual':
                    gastos_recurrentes_mensuales += monto
                elif frecuencia == 'Trimestral':
                    gastos_recurrentes_mensuales += monto / 3
                elif frecuencia == 'Semestral':
                    gastos_recurrentes_mensuales += monto / 6
                elif frecuencia == 'Anual':
                    gastos_recurrentes_mensuales += monto / 12
        
        proyeccion_gastos_recurrentes = gastos_recurrentes_mensuales * 12
        proyeccion_gastos_totales = proyeccion_gastos_recurrentes + gastos_unicos
        proyeccion_neta = proyeccion_ingresos - proyeccion_gastos_totales
        
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("💰 Proyección Ingresos", f"${proyeccion_ingresos:,.0f}")
        with col2:
            st.metric("🔄 Proyección Gastos Recurrentes", f"${proyeccion_gastos_recurrentes:,.0f}")
        with col3:
            st.metric("📌 Gastos Únicos Actuales", f"${gastos_unicos:,.0f}")
        with col4:
            st.metric(
                "📈 Proyección Neta", 
                f"${proyeccion_neta:,.0f}",
                delta_color="normal" if proyeccion_neta >= 0 else "inverse"
            )
def mostrar_modal_edicion(ci_socio):
    """Mostrar modal de edición de socio"""
    socio_actual = st.session_state.socios.get(ci_socio)
    
    if not socio_actual:
        st.error("❌ Socio no encontrado")
        if st.button("🔙 Volver a la Lista", key=f"volver_error_{ci_socio}"):
            del st.session_state.editando_socio
            st.rerun()
        return
    
    col1, col2 = st.columns([4, 1])
    
    with col1:
        st.subheader(f"✏️ Editando: {socio_actual.get('nombre', 'N/A')}")
        st.caption(f"CI: {ci_socio}")
    
    with col2:
        if st.button("❌ Cancelar", type="secondary", key=f"cancelar_edicion_{ci_socio}"):
            del st.session_state.editando_socio
            st.rerun()
    
    st.markdown("---")
    
    resultado = formulario_socio(
        socio_data=socio_actual, 
        es_edicion=True, 
        ci_original=ci_socio
    )
    
    if resultado:
        actualizar_socio_con_ci(resultado, ci_socio)
        del st.session_state.editando_socio
        st.success("✅ Socio actualizado correctamente")
        st.rerun()

def actualizar_socio_con_ci(resultado, ci_original):
    """Actualiza los datos del socio con manejo de cambio de CI"""
    socio_data = resultado['socio_data']
    ci_cambio = resultado.get('ci_cambio', False)
    ci_nueva = resultado.get('ci_nueva', ci_original)
    
    if ci_cambio:
        if ci_original in st.session_state.socios:
            del st.session_state.socios[ci_original]
        
        # Actualizar pagos relacionados
        pagos_actualizados = {}
        for pago_key, pago in st.session_state.pagos.items():
            if pago.get('ci') == ci_original:
                nueva_clave = pago_key.replace(ci_original, ci_nueva)
                pago['ci'] = ci_nueva
                pagos_actualizados[nueva_clave] = pago
            else:
                pagos_actualizados[pago_key] = pago
        
        st.session_state.pagos = pagos_actualizados
        st.info(f"✅ CI actualizada de {ci_original} a {ci_nueva}")
    
    st.session_state.socios[ci_nueva] = socio_data

def mostrar_lista_socios():
    """Mostrar lista de socios"""
    st.subheader("Lista de Socios")
    
    col1, col2, col3 = st.columns([2, 1, 1])
    
    with col2:
        if st.button("🔄 Refrescar", help="Actualizar lista", key="refrescar_lista"):
            st.rerun()
    
    if st.session_state.socios:
        with col3:
            if st.button("📥 Exportar CSV", help="Descargar CSV", key="exportar_csv"):
                exportar_socios_csv()
        
        st.info(f"📊 **Total de socios registrados: {len(st.session_state.socios)}**")
        
        # Mostrar detalles si está seleccionado
        if 'ver_detalle_socio' in st.session_state:
            mostrar_detalle_socio()
        else:
            # Lista de socios en tarjetas
            socios_list = list(st.session_state.socios.items())
            
            for i in range(0, len(socios_list), 2):
                cols = st.columns(2)
                
                for j, (ci, socio) in enumerate(socios_list[i:i+2]):
                    with cols[j]:
                        with st.container():
                            st.markdown("""
                            <div style="border: 1px solid #ddd; border-radius: 10px; 
                                       padding: 20px; margin: 10px 0; background-color: white;
                                       box-shadow: 0 2px 4px rgba(0,0,0,0.1);">
                            """, unsafe_allow_html=True)
                            
                            mostrar_imagen_socio(socio.get('foto'), width=100)
                            
                            st.markdown(f"**{socio.get('nombre', 'N/A')}**")
                            st.markdown(f"📋 CI: {ci}")
                            st.markdown(f"📱 {socio.get('celular', 'Sin celular')}")
                            st.markdown(f"💳 {socio.get('tipo_cuota', 'N/A')}")
                            
                            comentarios = socio.get('comentarios', '').strip()
                            if comentarios:
                                comentarios_cortos = comentarios[:80] + "..." if len(comentarios) > 80 else comentarios
                                st.markdown(f"💭 *{comentarios_cortos}*")
                            
                            st.markdown("---")
                            
                            col_btn1, col_btn2, col_btn3 = st.columns(3)
                            
                            with col_btn1:
                                if st.button("👁️", key=f"view_{ci}", help="Ver detalles"):
                                    st.session_state.ver_detalle_socio = ci
                                    st.rerun()
                            
                            with col_btn2:
                                if st.button("✏️", key=f"edit_{ci}", help="Editar"):
                                    st.session_state.editando_socio = ci
                                    st.rerun()
                            
                            with col_btn3:
                                if st.button("🗑️", key=f"del_{ci}", help="Eliminar"):
                                    st.session_state.confirmar_eliminar = ci
                                    st.rerun()
                            
                            st.markdown("</div>", unsafe_allow_html=True)
        
        # Modal de confirmación de eliminación
        if 'confirmar_eliminar' in st.session_state:
            mostrar_confirmacion_eliminar()
    else:
        st.info("No hay socios registrados")

def mostrar_detalle_socio():
    """Mostrar detalles completos del socio"""
    ci_detalle = st.session_state.ver_detalle_socio
    socio = st.session_state.socios.get(ci_detalle)
    
    if not socio:
        del st.session_state.ver_detalle_socio
        st.rerun()
        return
    
    st.markdown("---")
    st.subheader(f"👤 Detalles de {socio.get('nombre', 'N/A')}")
    
    col1, col2 = st.columns([1, 2])
    
    with col1:
        mostrar_imagen_socio(socio.get('foto'), width=200)
    
    with col2:
        st.markdown(f"**📋 CI:** {ci_detalle}")
        st.markdown(f"**👤 Nombre:** {socio.get('nombre', 'N/A')}")
        st.markdown(f"**📱 Celular:** {socio.get('celular', 'No especificado')}")
        st.markdown(f"**👨‍👩‍👧‍👦 Contacto Emergencia:** {socio.get('contacto_emergencia', 'No especificado')}")
        st.markdown(f"**📞 Tel. Emergencia:** {socio.get('emergencia_movil', 'No especificado')}")
        st.markdown(f"**🎂 Fecha Nacimiento:** {socio.get('fecha_nacimiento', 'No especificado')}")
        st.markdown(f"**💳 Tipo de Cuota:** {socio.get('tipo_cuota', 'No especificado')}")
        st.markdown(f"**🏥 Enfermedades/Alergias:** {socio.get('enfermedades', 'Ninguna')}")
    
    comentarios = socio.get('comentarios', '').strip()
    if comentarios:
        st.markdown("---")
        st.subheader("💭 Comentarios")
        st.markdown(f"*{comentarios}*")
    
    st.markdown("---")
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        if st.button("✏️ Editar", use_container_width=True, key=f"editar_detalle_{ci_detalle}"):
            st.session_state.editando_socio = ci_detalle
            del st.session_state.ver_detalle_socio
            st.rerun()
    
    with col2:
        if st.button("💳 Ver Pagos", use_container_width=True, key=f"pagos_detalle_{ci_detalle}"):
            st.info("Funcionalidad próximamente...")
    
    with col3:
        if st.button("📥 Exportar", use_container_width=True, key=f"exportar_detalle_{ci_detalle}"):
            exportar_socio_individual(ci_detalle, socio)
    
    with col4:
        if st.button("❌ Cerrar", use_container_width=True, key=f"cerrar_detalle_{ci_detalle}"):
            del st.session_state.ver_detalle_socio
            st.rerun()

def mostrar_confirmacion_eliminar():
    """Mostrar modal de confirmación para eliminar socio"""
    ci_eliminar = st.session_state.confirmar_eliminar
    socio_eliminar = st.session_state.socios.get(ci_eliminar, {})
    
    st.markdown("---")
    st.error(f"⚠️ ¿Está seguro de eliminar a **{socio_eliminar.get('nombre', 'N/A')}**?")
    
    col_info1, col_info2 = st.columns(2)
    with col_info1:
        st.write(f"**CI:** {ci_eliminar}")
        st.write(f"**Celular:** {socio_eliminar.get('celular', 'N/A')}")
    with col_info2:
        st.write(f"**Tipo Cuota:** {socio_eliminar.get('tipo_cuota', 'N/A')}")
        pagos_relacionados = sum(1 for pago in st.session_state.pagos.values() 
                               if pago.get('ci') == ci_eliminar)
        st.write(f"**Pagos registrados:** {pagos_relacionados}")
    
    if pagos_relacionados > 0:
        st.warning(f"⚠️ Este socio tiene {pagos_relacionados} pagos registrados que también se eliminarán.")
    
    col1, col2, col3 = st.columns([1, 1, 1])
    
    with col1:
        if st.button("✅ Sí, eliminar", type="primary", key=f"confirmar_del_{ci_eliminar}"):
            eliminar_socio_completo(ci_eliminar)
    
    with col3:
        if st.button("❌ Cancelar", key=f"cancelar_del_{ci_eliminar}"):
            del st.session_state.confirmar_eliminar
            st.rerun()

def eliminar_socio_completo(ci_eliminar):
    """Eliminar socio y todos sus pagos relacionados"""
    socio_eliminar = st.session_state.socios.get(ci_eliminar, {})
    nombre_eliminado = socio_eliminar.get('nombre', 'N/A')
    
    # Eliminar pagos relacionados
    pagos_a_eliminar = [key for key, pago in st.session_state.pagos.items() 
                        if pago.get('ci') == ci_eliminar]
    
    pagos_eliminados = len(pagos_a_eliminar)
    
    for pago_key in pagos_a_eliminar:
        del st.session_state.pagos[pago_key]
    
    # Eliminar socio
    del st.session_state.socios[ci_eliminar]
    del st.session_state.confirmar_eliminar
    
    # Mostrar resultado
    st.success(f"✅ Socio {nombre_eliminado} eliminado correctamente")
    if pagos_eliminados > 0:
        st.info(f"📋 También se eliminaron {pagos_eliminados} pagos relacionados")
    
    st.rerun()

def mostrar_buscar_socio():
    """Mostrar búsqueda de socios"""
    st.subheader("🔍 Buscar Socio")
    
    busqueda = st.text_input("Buscar por nombre o CI:", placeholder="Ingrese término de búsqueda", key="buscar_socio")
    
    if busqueda:
        resultados = {}
        for ci, socio in st.session_state.socios.items():
            nombre = socio.get('nombre', '')
            if (busqueda.lower() in nombre.lower() or busqueda in ci):
                resultados[ci] = socio
        
        if resultados:
            st.success(f"✅ Se encontraron {len(resultados)} resultados:")
            
            for ci, socio in resultados.items():
                with st.container():
                    col1, col2, col3 = st.columns([1, 3, 1])
                    
                    with col1:
                        mostrar_imagen_socio(socio.get('foto'), width=80)
                    
                    with col2:
                        st.markdown(f"**{socio.get('nombre', 'N/A')}**")
                        st.markdown(f"📋 CI: {ci}")
                        st.markdown(f"📱 {socio.get('celular', 'Sin celular')}")
                        st.markdown(f"💳 {socio.get('tipo_cuota', 'N/A')}")
                    
                    with col3:
                        if st.button("✏️ Editar", key=f"edit_buscar_{ci}"):
                            st.session_state.editando_socio = ci
                            st.rerun()
                    
                    st.markdown("---")
        else:
            st.info("No se encontraron resultados")

def mostrar_importar_csv():
    """Mostrar importación CSV"""
    st.subheader("📊 Importar Socios desde CSV")
    
    st.info(f"📊 **Socios actuales en el sistema: {len(st.session_state.socios)}**")
    st.warning("⚠️ **Nota:** La importación CSV no incluye fotos. Las fotos deben agregarse individualmente después de la importación.")
    
    st.markdown("""
    📋 **Formato del archivo CSV:**
    
    El archivo debe contener las siguientes columnas (mínimo requerido):
    - **ci**: Cédula de identidad (obligatorio)
    - **nombre**: Nombre completo (obligatorio)
    
    Columnas opcionales:
    - celular, contacto_emergencia, emergencia_movil, fecha_nacimiento, tipo_cuota, enfermedades, comentarios
    """)
    
    with st.expander("👀 Ver ejemplo de CSV"):
        ejemplo_csv = """ci,nombre,celular,contacto_emergencia,tipo_cuota,enfermedades,comentarios
12345678,Juan Pérez,099123456,María Pérez,Libre - $2000,Ninguna,Socio muy activo
87654321,Ana García,095456789,Pedro García,Solo Pesas - $800,Alergia al polen,Interesada en clases grupales
11111111,Carlos López,094555666,Laura López,Libre - $2000,Asma,Necesita seguimiento especial"""
        
        st.code(ejemplo_csv, language="csv")
        
        st.download_button(
            label="📥 Descargar Plantilla CSV",
            data=ejemplo_csv,
            file_name="plantilla_socios.csv",
            mime="text/csv",
            key="download_plantilla"
        )
    
    st.markdown("---")
    
    uploaded_file = st.file_uploader(
        "📁 Seleccionar archivo CSV",
        type=['csv'],
        help="Archivo CSV con datos de socios",
        key="upload_csv"
    )
    
    if uploaded_file is not None:
        importar_csv_socios(uploaded_file)

def importar_csv_socios(uploaded_file):
    """Importar socios desde archivo CSV"""
    try:
        df = pd.read_csv(uploaded_file)
        
        columnas_requeridas = ['ci', 'nombre']
        columnas_faltantes = [col for col in columnas_requeridas if col not in df.columns.str.lower()]
        
        if columnas_faltantes:
            st.error(f"❌ Columnas faltantes en el CSV: {', '.join(columnas_faltantes)}")
            st.info("💡 El CSV debe tener al menos las columnas: ci, nombre")
            return False
        
        df.columns = df.columns.str.lower().str.strip()
        
        if 'comentarios' in df.columns:
            st.success("✅ Campo 'comentarios' detectado en el CSV")
        else:
            st.info("ℹ️ No se detectó campo 'comentarios'. Se importará con comentarios vacíos.")
        
        st.subheader("👀 Vista Previa del CSV")
        st.dataframe(df.head(10), use_container_width=True)
        
        if len(df) > 10:
            st.info(f"📊 Mostrando las primeras 10 filas de {len(df)} total")
        
        col1, col2, col3 = st.columns([1, 1, 1])
        
        with col2:
            if st.button("✅ Confirmar Importación", type="primary", use_container_width=True, key="confirmar_import"):
                importados = 0
                actualizados = 0
                errores = 0
                
                for index, row in df.iterrows():
                    try:
                        ci = str(row.get('ci', '')).strip()
                        nombre = str(row.get('nombre', '')).strip()
                        
                        if not ci or not nombre or ci.lower() == 'nan' or nombre.lower() == 'nan':
                            errores += 1
                            continue
                        
                        existia = ci in st.session_state.socios
                        
                        socio_data = {
                            'nombre': nombre,
                            'ci': ci,
                            'celular': str(row.get('celular', '')).strip(),
                            'contacto_emergencia': str(row.get('contacto_emergencia', '')).strip(),
                            'emergencia_movil': str(row.get('emergencia_movil', '')).strip(),
                            'fecha_nacimiento': str(row.get('fecha_nacimiento', '')).strip(),
                            'tipo_cuota': str(row.get('tipo_cuota', 'Libre - $2000')).strip(),
                            'enfermedades': str(row.get('enfermedades', '')).strip(),
                            'comentarios': str(row.get('comentarios', '')).strip(),
                            'foto': None
                        }
                        
                        for key, value in socio_data.items():
                            if isinstance(value, str) and value.lower() == 'nan':
                                socio_data[key] = ''
                        
                        st.session_state.socios[ci] = socio_data
                        
                        if existia:
                            actualizados += 1
                        else:
                            importados += 1
                            
                    except Exception as e:
                        errores += 1
                        st.warning(f"⚠️ Error procesando fila {index + 1}: {str(e)}")
                
                st.success("✅ ¡Importación exitosa!")
                
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.metric("📊 Nuevos Socios", importados)
                with col2:
                    st.metric("🔄 Actualizados", actualizados)
                with col3:
                    st.metric("❌ Errores", errores)
                
                if errores > 0:
                    st.warning(f"⚠️ Se encontraron {errores} errores durante la importación")
                
                st.balloons()
                
                if st.button("👁️ Ver Socios Importados", type="secondary", key="ver_importados"):
                    st.rerun()
        
        return True
        
    except Exception as e:
        st.error(f"❌ Error leyendo el archivo CSV: {str(e)}")
        st.info("💡 Asegúrese de que el archivo esté en formato CSV válido")
        return False

def exportar_socios_csv():
    """Función auxiliar para exportar CSV"""
    try:
        socios_data = []
        for ci, socio in st.session_state.socios.items():
            socio_sin_foto = {k: v for k, v in socio.items() if k != 'foto'}
            socios_data.append(socio_sin_foto)
        
        df_export = pd.DataFrame(socios_data)
        csv = df_export.to_csv(index=False)
        
        st.download_button(
            label="💾 Descargar CSV",
            data=csv,
            file_name=f"socios_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
            mime="text/csv",
            use_container_width=True,
            key="download_csv"
        )
    except Exception as e:
        st.error(f"Error exportando: {str(e)}")

def exportar_socio_individual(ci, socio):
    """Exportar datos de un socio específico"""
    socio_data = {k: v for k, v in socio.items() if k != 'foto'}
    df_socio = pd.DataFrame([socio_data])
    csv_socio = df_socio.to_csv(index=False)
    
    st.download_button(
        label=f"💾 Descargar datos de {socio.get('nombre', 'socio')}",
        data=csv_socio,
        file_name=f"socio_{ci}_{datetime.now().strftime('%Y%m%d')}.csv",
        mime="text/csv",
        use_container_width=True,
        key=f"download_individual_{ci}"
    )

def show_pagos():
    """Mostrar control de pagos"""
    st.header("💳 Control de Pagos")
    
    if not st.session_state.socios:
        st.warning("⚠️ Primero debe agregar socios antes de registrar pagos")
        return
    
    tab1, tab2, tab3 = st.tabs(["📋 Historial", "➕ Registrar Pago", "🔔 Pendientes"])
    
    with tab1:
        st.subheader("Historial de Pagos")
        
        if st.session_state.pagos:
            pagos_display = []
            for key, pago in st.session_state.pagos.items():
                ci = pago.get('ci', 'N/A')
                socio = st.session_state.socios.get(ci, {})
                
                pagos_display.append({
                    'Socio': socio.get('nombre', 'N/A'),
                    'CI': ci,
                    'Mes': pago.get('mes', 'N/A'),
                    'Año': pago.get('año', 'N/A'),
                    'Monto': f"${pago.get('monto', 0):,.0f}",
                    'Fecha Pago': pago.get('fecha_pago', 'N/A'),
                    'Tipo Cuota': pago.get('tipo_cuota', 'N/A')
                })
            
            df_pagos = pd.DataFrame(pagos_display)
            st.dataframe(df_pagos, use_container_width=True, hide_index=True)
            
            total_ingresos = sum(p.get('monto', 0) for p in st.session_state.pagos.values())
            st.metric("💰 Total Ingresos", f"${total_ingresos:,.0f}")
        else:
            st.info("No hay pagos registrados")
    
    with tab2:
        st.subheader("Registrar Nuevo Pago")
        
        with st.form("form_pago"):
            col1, col2 = st.columns(2)
            
            with col1:
                socios_options = {f"{socio.get('nombre', 'Sin nombre')} ({ci})": ci 
                                for ci, socio in st.session_state.socios.items()}
                socio_selected = st.selectbox("Socio*", list(socios_options.keys()))
                
                meses = ['Enero', 'Febrero', 'Marzo', 'Abril', 'Mayo', 'Junio',
                        'Julio', 'Agosto', 'Septiembre', 'Octubre', 'Noviembre', 'Diciembre']
                mes = st.selectbox("Mes*", meses, index=datetime.now().month - 1)
                
            with col2:
                año = st.number_input("Año*", min_value=2020, max_value=2030, value=datetime.now().year)
                fecha_pago = st.date_input("Fecha de Pago", value=date.today())
                
                if socio_selected:
                    ci_selected = socios_options[socio_selected]
                    socio_data = st.session_state.socios.get(ci_selected, {})
                    tipo_cuota = socio_data.get('tipo_cuota', 'Libre - $2000')
                    monto_default = 2000 if '2000' in tipo_cuota else 800
                    monto = st.number_input("Monto", value=monto_default, min_value=0)
            
            submitted = st.form_submit_button("💾 Registrar Pago")
            
            if submitted:
                ci_selected = socios_options[socio_selected]
                pago_key = f"{ci_selected}_{mes}_{año}"
                
                if pago_key in st.session_state.pagos:
                    st.warning("Ya existe un pago para este socio en este mes/año")
                else:
                    socio_data = st.session_state.socios.get(ci_selected, {})
                    st.session_state.pagos[pago_key] = {
                        'ci': ci_selected,
                        'mes': mes,
                        'año': año,
                        'monto': monto,
                        'fecha_pago': str(fecha_pago),
                        'tipo_cuota': socio_data.get('tipo_cuota', 'N/A')
                    }
                    st.success(f"Pago de ${monto:,.0f} registrado para {socio_selected}")
                    st.rerun()
    
    with tab3:
        st.subheader("Pagos Pendientes")
        
        año_verificar = st.selectbox("Año a verificar", [2024, 2025, 2026], index=1)
        
        meses = ['Enero', 'Febrero', 'Marzo', 'Abril', 'Mayo', 'Junio',
                'Julio', 'Agosto', 'Septiembre', 'Octubre', 'Noviembre', 'Diciembre']
        mes_actual = datetime.now().month if año_verificar == datetime.now().year else 12
        
        pendientes = []
        for ci, socio in st.session_state.socios.items():
            meses_pendientes = []
            monto_total = 0
            tipo_cuota = socio.get('tipo_cuota', 'Libre - $2000')
            monto_cuota = 2000 if '2000' in tipo_cuota else 800
            
            for i in range(mes_actual):
                mes = meses[i]
                pago_key = f"{ci}_{mes}_{año_verificar}"
                if pago_key not in st.session_state.pagos:
                    meses_pendientes.append(mes)
                    monto_total += monto_cuota
            
            if meses_pendientes:
                pendientes.append({
                    'Socio': socio.get('nombre', 'N/A'),
                    'CI': ci,
                    'Meses Pendientes': ', '.join(meses_pendientes),
                    'Cantidad': len(meses_pendientes),
                    'Monto Total': f"${monto_total:,.0f}"
                })
        
        if pendientes:
            df_pendientes = pd.DataFrame(pendientes)
            st.dataframe(df_pendientes, use_container_width=True, hide_index=True)
            
            total_pendiente = sum(
                int(p['Monto Total'].replace(',', '').replace('$', ''))
                for p in pendientes
            )
            st.metric("💰 Total Pendiente", f"${total_pendiente:,.0f}")
        else:
            st.success("✅ No hay pagos pendientes")

def main():
    """Función principal"""
    inicializar_datos()
    
    st.title("🥋 Sistema de Gestión - Academia de Artes Marciales")
    st.markdown("---")

    st.sidebar.title("📋 Menú Principal")
    
    menu_options = [
        "📊 Dashboard",
        "👥 Gestión de Socios",
        "💳 Control de Pagos",
        "📦 Inventario",
        "💸 Gastos",
        "📈 Estadísticas"
    ]
    
    selected_page = st.sidebar.radio(
        "Selecciona una sección:",
        menu_options,
        index=0
    )
    
    # Mostrar información de debug en el sidebar
    with st.sidebar.expander("🔧 Debug Info"):
        st.write(f"**Socios:** {len(st.session_state.socios)}")
        st.write(f"**Pagos:** {len(st.session_state.pagos)}")
        st.write(f"**Gastos:** {len(st.session_state.gastos)}")
        
        if st.button("🔄 Reinicializar Datos"):
            # Limpiar session state
            for key in list(st.session_state.keys()):
                del st.session_state[key]
            st.rerun()
    
    # Mapeo a funciones
    if selected_page == "📊 Dashboard":
        show_dashboard()
    elif selected_page == "👥 Gestión de Socios":
        show_socios()
    elif selected_page == "💳 Control de Pagos":
        show_pagos()
    elif selected_page == "📦 Inventario":
        show_inventario()
    elif selected_page == "💸 Gastos":
        show_gastos()
    elif selected_page == "📈 Estadísticas":
        show_estadisticas()

if __name__ == "__main__":
    main()#!/usr/bin/env python3
# -*- coding: utf-8 -*-
