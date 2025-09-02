# main.py (VERSIÓN ESTABLE Y SEGURA)

import sys
import os
import asyncio
from flask import Flask, request, jsonify
from flask_cors import CORS

# --- CONFIGURACIÓN DE LA APLICACIÓN ---
app = Flask(__name__)
CORS(app) # Configuración de CORS simple y efectiva

# --- IMPORTAR Y CARGAR EL NÚCLEO Y SKILLSETS ---
# Añadimos la ruta para que Python encuentre los módulos
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from ale_core import ALE_Core
from skillsets.guardian import Guardian

# Inicializamos el motor A.L.E.
ale = ALE_Core()
# Cargamos el skillset del Guardián
ale.cargar_skillset("guardian", Guardian())

print("✅ Motor A.L.E. inicializado con skillset 'guardian'.")

# --- RUTA PRINCIPAL DE LA API ---
@app.route('/execute', methods=['POST'])
def handle_execution():
    datos_peticion = request.json
    
    # Lógica para manejar el bucle de eventos asíncronos de forma segura
    try:
        loop = asyncio.get_running_loop()
    except RuntimeError:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
    
    # Procesamos la petición y devolvemos la respuesta
    respuesta_de_ale = loop.run_until_complete(ale.procesar_peticion(datos_peticion))
    return jsonify(respuesta_de_ale)

# --- BLOQUE DE ARRANQUE (SOLO PARA PRUEBAS LOCALES) ---
# Gunicorn ignorará este bloque en Render, lo cual es perfecto.
if __name__ == "__main__":
    print("===================================================")
    print("==    SERVIDOR A.L.E. EN MODO DE PRUEBA LOCAL    ==")
    print("==      Servidor escuchando en puerto 5000       ==")
    print("===================================================")
    app.run(host='0.0.0.0', port=5000)

