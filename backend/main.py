# main.py (VERSIÓN MONOLITO - FINAL)
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Le decimos a Flask que la carpeta 'frontend' contiene la web
from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
import asyncio

from ale_core import ALE_Core
from skillsets.guardian import Guardian

# Creamos la app, especificando la ruta a la carpeta 'frontend'
app = Flask(__name__, static_folder='../frontend', static_url_path='/')
CORS(app)

ale = ALE_Core()
ale.cargar_skillset("guardian", Guardian())

# RUTA 1: El cerebro (la que ya teníamos)
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

# RUTA 2: El cuerpo (la nueva ruta para servir la página)
@app.route('/')
def serve_index():
    # Busca y sirve el 'index.html' desde la carpeta 'frontend'
    return send_from_directory(app.static_folder, 'index.html')

if __name__ == "__main__":
    print("===================================================")
    print("==    SERVIDOR MONOLITO DE A.L.E. OPERATIVO    ==")
    print("==         Servidor escuchando en puerto 5000      ==")
    print("===================================================")
    app.run(host='0.0.0.0', port=5000)
