# backend/main.py

import sys
import os
import asyncio
from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS

# Esto permite que Python encuentre nuestros módulos en la carpeta 'skillsets'
# Es una buena práctica para mantener el proyecto ordenado.
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# --- PASO 1: IMPORTAR LOS SKILLSETS ---
# Importamos las clases de los archivos .py correspondientes.
from ale_core import ALE_Core
from skillsets.guardian import Guardian
from skillsets.oracle import Oracle

# --- PASO 2: CONFIGURAR LA APLICACIÓN FLASK ---
# Creamos la app. No es necesario tocar más esta parte.
app = Flask(__name__)
CORS(app) # Habilitamos CORS para permitir la comunicación desde tu PWA.

# --- PASO 3: INICIALIZAR Y CARGAR EL MOTOR A.L.E. ---
# Creamos una instancia de nuestro motor lógico.
ale = ALE_Core()

# Cargamos cada skillset con un nombre único.
# Este nombre es el que usarás en el 'main.js' de cada PWA para identificarse.
ale.cargar_skillset("guardian", Guardian())
ale.cargar_skillset("oracle", Oracle())

print("✅ Motor A.L.E. inicializado. Skillsets 'guardian' y 'oracle' cargados.")

# --- PASO 4: DEFINIR LAS RUTAS DEL SERVIDOR ---

# RUTA PRINCIPAL DE EJECUCIÓN
# Esta es la única ruta que tus PWAs necesitarán llamar.
@app.route('/execute', methods=['POST'])
def handle_execution():
    datos_peticion = request.json
    try:
        # Manejo del bucle de eventos asíncronos (necesario para g4f).
        loop = asyncio.get_running_loop()
    except RuntimeError:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
    
    # Le pasamos la petición completa al motor A.L.E. para que él decida qué hacer.
    respuesta_de_ale = loop.run_until_complete(ale.procesar_peticion(datos_peticion))
    return jsonify(respuesta_de_ale)

# --- PASO 5: ARRANQUE DEL SERVIDOR ---
# Este bloque solo se ejecuta cuando corres el archivo directamente.
if __name__ == "__main__":
    print("===================================================")
    print("==    SERVIDOR CENTRAL DE A.L.E. OPERATIVO     ==")
    print("==       Múltiples skillsets están activos       ==")
    print("==      Servidor escuchando en puerto 5000       ==")
    print("===================================================")
    app.run(host='0.0.0.0', port=5000)

