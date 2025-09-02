# backend/main.py

import sys
import os
import asyncio
from flask import Flask, request, jsonify
from flask_cors import CORS

# --- PASO 1: CONFIGURAR LA APLICACIÓN Y CORS ---
# Primero, creamos la aplicación Flask. Esta es la base de todo.
app = Flask(__name__)

# Ahora, aplicamos la configuración de CORS reforzada a nuestra 'app'.
# Esto le dice al servidor que acepte peticiones desde cualquier origen.
CORS(app, resources={r"/*": {"origins": "*"}})

# Esta función añade cabeceras de permiso a CADA respuesta del servidor.
@app.after_request
def after_request(response):
    response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization')
    response.headers.add('Access-Control-Allow-Methods', 'GET,PUT,POST,DELETE,OPTIONS')
    return response

# --- PASO 2: IMPORTAR LOS SKILLSETS ---
# (El resto del código ya estaba perfecto)
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from ale_core import ALE_Core
from skillsets.guardian import Guardian
# from skillsets.oracle import Oracle # Lo dejamos comentado por ahora

# --- PASO 3: INICIALIZAR Y CARGAR EL MOTOR A.L.E. ---
ale = ALE_Core()
ale.cargar_skillset("guardian", Guardian())
# ale.cargar_skillset("oracle", Oracle()) # Comentado

print("✅ Motor A.L.E. inicializado. Skillset 'guardian' cargado.")

# --- PASO 4: DEFINIR LA RUTA DE EJECUCIÓN ---
@app.route('/execute', methods=['POST'])
def handle_execution():
    datos_peticion = request.json
    try:
        loop = asyncio.get_running_loop()
    except RuntimeError:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
    
    respuesta_de_ale = loop.run_until_complete(ale.procesar_peticion(datos_peticion))
    return jsonify(respuesta_de_ale)

# --- PASO 5: ARRANQUE DEL SERVIDOR ---
if __name__ == "__main__":
    print("===================================================")
    print("==    SERVIDOR CENTRAL DE A.L.E. OPERATIVO     ==")
    print("==      Servidor escuchando en puerto 5000       ==")
    print("===================================================")
    app.run(host='0.0.0.0', port=5000)
