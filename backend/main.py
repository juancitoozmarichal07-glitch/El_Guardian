# =================================================================
# MAIN.PY (v1.0 - ESTABLE)
# =================================================================
# Este archivo crea el servidor web Flask y actúa como el punto de
# entrada para todas las peticiones de la PWA.

import sys
import os
import asyncio
from flask import Flask, request, jsonify
from flask_cors import CORS

# --- CONFIGURACIÓN DE LA APLICACIÓN Y CORS ---
app = Flask(__name__)
# Configuración de CORS reforzada para permitir llamadas desde cualquier origen.
CORS(app, resources={r"/*": {"origins": "*"}})

@app.after_request
def after_request(response):
    # Añadimos cabeceras de seguridad en cada respuesta.
    response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization')
    response.headers.add('Access-Control-Allow-Methods', 'GET,PUT,POST,DELETE,OPTIONS')
    return response

# --- PREPARAR EL CAMINO A LOS MÓDULOS ---
# Añadimos la carpeta actual al path de Python para que encuentre nuestros módulos.
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# --- IMPORTAR E INICIALIZAR EL CEREBRO Y LOS SKILLSETS ---
from ale_core import ALE_Core
from skillsets.guardian import Guardian

# 1. Creamos la instancia del motor A.L.E.
ale = ALE_Core()

# 2. Cargamos el skillset del Guardián con su nombre oficial.
#    La PWA deberá usar "guardian" para llamarlo.
ale.cargar_skillset("guardian", Guardian())

print("✅ Servidor listo. A.L.E. está online con el skillset 'guardian'.")

# --- DEFINIR LA RUTA DE EJECUCIÓN ---
# Esta es la única "puerta" o "endpoint" de nuestro servidor.
@app.route('/execute', methods=['POST'])
def handle_execution():
    datos_peticion = request.json
    
    # Manejo del bucle de eventos asíncrono, necesario para g4f.
    try:
        loop = asyncio.get_running_loop()
    except RuntimeError:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
    
    # Pasamos la petición al motor A.L.E. y esperamos su respuesta.
    respuesta_de_ale = loop.run_until_complete(ale.procesar_peticion(datos_peticion))
    
    # Devolvemos la respuesta a la PWA.
    return jsonify(respuesta_de_ale)

# --- ARRANQUE DEL SERVIDOR (SOLO PARA PRUEBAS LOCALES) ---
if __name__ == "__main__":
    # Render ignorará esto y usará el "Start Command" (gunicorn main:app).
    app.run(host='0.0.0.0', port=5000, debug=True)

