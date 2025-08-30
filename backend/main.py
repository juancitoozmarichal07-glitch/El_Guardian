# main.py (VERSIÓN FINAL Y DEFINITIVA)

# --- INICIO DEL MAPA PARA PYDROID 3 ---
# Este bloque es crucial para que Pydroid encuentre los otros archivos.
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
# --- FIN DEL MAPA ---


# 1. Importamos las herramientas necesarias
from flask import Flask, request, jsonify
from flask_cors import CORS
import asyncio

# 2. Importamos a nuestros especialistas y al cerebro
# Esta es la forma correcta y absoluta de importar
from ale_core import ALE_Core
from skillsets.guardian import Guardian


# 3. Creamos la aplicación servidor
app = Flask(__name__)
CORS(app)


# 4. Inicializamos el cerebro A.L.E. y cargamos al especialista
ale = ALE_Core()
ale.cargar_skillset("guardian", Guardian())


# 5. Creamos la "ventanilla" de la API (con el adaptador asíncrono)
@app.route('/execute', methods=['POST'])
def handle_execution():
    datos_peticion = request.json
    
    # Este bloque maneja la naturaleza asíncrona de la IA de forma segura
    try:
        loop = asyncio.get_running_loop()
    except RuntimeError:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)

    # El cerebro procesa la petición
    respuesta_de_ale = loop.run_until_complete(ale.procesar_peticion(datos_peticion))
    
    return jsonify(respuesta_de_ale)


# 6. El botón de "ENCENDIDO" del servidor
if __name__ == "__main__":
    print("===================================================")
    print("==      COCINA DE A.L.E. ABIERTA Y OPERATIVA     ==")
    print("==         Servidor escuchando en puerto 5000      ==")
    print("== No cierres esta ventana. Déjala en 2do plano. ==")
    print("===================================================")
    app.run(host='0.0.0.0', port=5000)

