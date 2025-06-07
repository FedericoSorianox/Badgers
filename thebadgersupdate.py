# thebadgersupdate.py - Script de Prueba Final
import streamlit as st
import os
import psycopg2

st.set_page_config(layout="centered")

st.title("Prueba de Conexión Final")
st.write("Esta es la prueba definitiva para la aplicación principal.")

# --- 1. Verificar la Variable de Entorno ---
st.header("Paso 1: Lectura de la Variable de Entorno")
database_url = os.environ.get('DATABASE_URL')

if database_url:
    st.success("✅ ÉXITO: La variable `DATABASE_URL` fue encontrada por la aplicación.")
    # Mostramos una parte para confirmar que es la correcta
    st.code(f"Valor encontrado (parcial): {database_url[:30]}...") 
else:
    st.error("❌ FALLO: La aplicación NO pudo encontrar la variable `DATABASE_URL`.")
    st.warning("Esto confirma que, a pesar de la configuración, el servidor de Render no está entregando la variable a este script. Con esta prueba, puedes contactar al soporte de Render.")
    st.stop() # Detener la ejecución si no hay URL

# --- 2. Intentar Conexión a la Base de Datos ---
st.header("Paso 2: Intento de Conexión a la Base de Datos")

try:
    # Intentar conectar usando la URL encontrada
    conn = psycopg2.connect(database_url)
    
    # Si la conexión tiene éxito, cierra la conexión y muestra el mensaje
    conn.close()
    
    st.success("✅ ¡ÉXITO TOTAL! La conexión a la base de datos se ha realizado correctamente.")
    st.balloons()
    st.info("Ahora que esto funciona, podemos restaurar el código completo de la aplicación con la certeza de que la conexión está resuelta.")

except Exception as e:
    st.error("❌ FALLO: La conexión a la base de datos ha fallado.")
    st.write("La URL fue encontrada, pero no se pudo conectar. El error fue:")
    st.code(str(e))
    st.warning("Verifica que la URL, usuario y contraseña sean correctos y que la base de datos esté activa.")

