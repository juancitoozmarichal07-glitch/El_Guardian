# =================================================================
# MAIN.PY - SERVIDOR CENTRAL DE A.L.E. (v1.0 - Estable)
# =================================================================
# Este archivo actúa como el "gerente" del edificio. Su única
# responsabilidad es recibir las llamadas y dirigirlas al
# skillset correcto.

# --- PASO 1: IMPORTACIONES NECESARIAS ---
import sys
import os
import asyncio
from flask import Flask, request, jsonify
from flask_cors import CORS

# --- PASO 2: CONFIGURACIÓN DE LA APLICACIÓN Y CORS ---
# Primero, creamos la aplicación Flask. Esta es la base de todo.
app = Flask(__name__)

# Ahora, aplicamos la configuración de CORS reforzada.
# Esto es crucial para permitir la comunicación desde tu PWA en Vercel/GitHub.
CORS(app, resources={r"/*": {"origins": "*"}})

# Esta función añade cabeceras de permiso a CADA respuesta del servidor.
# Es un seguro extra para que los navegadores no bloqueen la conexión.
@app.after_request
def after_request(response):
    response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization')
    response.headers.add('Access-Control-Allow-Methods', 'GET,PUT,POST,DELETE,OPTIONS')
    return response

# --- PASO 3: PREPARAR EL CAMINO A LOS SKILLSETS ---
# Esto le dice a Python que también debe buscar módulos dentro de la
# carpeta actual, lo que nos permite importar 'ale_core'.
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Importamos las "clases" de nuestros cerebros.
from ale_core import ALE_Core
from skillsets.guardian import Guardian
# from skillsets.oracle import Oracle # Lo dejamos comentado para evitar errores.

# --- PASO 4: INICIALIZAR Y CARGAR EL MOTOR A.L.E. ---
# Creamos una instancia de nuestro motor lógico.
ale = ALE_Core()

# Cargamos el skillset del Guardián con su nombre oficial.
# El 'main.js' de la PWA debe usar este mismo nombre: "guardian".
ale.cargar_skillset("guardian", Guardian())

# ale.cargar_skillset("oracle", Oracle()) # Dejamos esto comentado por ahora.

print("✅ Motor A.L.E. inicializado. Skillset 'guardian' cargado y listo.")

# --- PASO 5: DEFINIR LA RUTA DE EJECUCIÓN ---
# Esta es la única "línea telefónica" que nuestro servidor necesita.
# Todas las PWAs llamarán a esta misma ruta.
@app.route('/execute', methods=['POST'])
def handle_execution():
    # Recibimos los datos de la PWA (el comando, el nombre del skillset, etc.)
    datos_peticion = request.json
    
    try:
        # Manejo del bucle de eventos asíncronos (necesario para g4f).
        loop = asyncio.get_running_loop()
    except RuntimeError:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
    
    # Le pasamos la petición completa al motor A.L.E. para que él decida qué hacer.
    respuesta_de_ale = loop.run_until_complete(ale.procesar_peticion(datos_peticion))
    
    # Devolvemos la respuesta del skillset a la PWA.
    return jsonify(respuesta_de_ale)

# --- PASO 6: ARRANQUE DEL SERVIDOR ---
# Este bloque solo se ejecuta cuando corres el archivo directamente.
if __name__ == "__main__":
    print("===================================================")
    print("==    SERVIDOR CENTRAL DE A.L.E. OPERATIVO     ==")
    print("==      Servidor escuchando en puerto 5000       ==")
    print("===================================================")
    # Esta línea es para pruebas locales. Render usará el "Start Command".
    app.run(host='0.0.0.0', port=5000)

