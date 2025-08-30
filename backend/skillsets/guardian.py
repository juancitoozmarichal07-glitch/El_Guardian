# guardian.py (VERSIÓN 7.0 - CON MEMORIA DE ESTADO)

import json
import random
from datetime import datetime
import g4f

class Guardian:
    def __init__(self):
        self.archivo_contratos = 'contratos.json'
        self.archivo_estado = 'estado_guardian.json'
        self.contratos = self._cargar_json(self.archivo_contratos, [])
        self.estado = self._cargar_json(self.archivo_estado, {"ultima_interaccion": None, "historial_chat": []})
        self.historial_chat = self.estado.get("historial_chat", [])
        print(f"    - Especialista 'Guardian' v7.0 (Con Memoria) listo.")

    # ... (las funciones _cargar_json, _guardar_estado, _obtener_momento_del_dia, _generar_saludo se quedan igual) ...
    def _cargar_json(self, archivo, default):
        try:
            with open(archivo, 'r', encoding='utf-8') as f: return json.load(f)
        except (FileNotFoundError, json.JSONDecodeError): return default

    def _guardar_estado(self):
        self.estado["ultima_interaccion"] = datetime.now().isoformat()
        self.estado["historial_chat"] = self.historial_chat[-10:]
        with open(self.archivo_estado, 'w', encoding='utf-8') as f: json.dump(self.estado, f, indent=4)

    def _obtener_momento_del_dia(self):
        h = datetime.now().hour
        return "mañana" if 5 <= h < 12 else "tarde" if 12 <= h < 20 else "noche"

    def _generar_saludo(self):
        self.historial_chat = self.estado.get("historial_chat", [])
        hoy = datetime.now().date()
        ultima_fecha = datetime.fromisoformat(self.estado["ultima_interaccion"]).date() if self.estado.get("ultima_interaccion") else None
        return f"Hola. Bienvenido, Juan. ¿En qué te puedo ayudar en esta {self._obtener_momento_del_dia()}?" if ultima_fecha != hoy else "Hola Juan, bienvenido de vuelta. ¿Revisamos contratos, creamos uno nuevo o charlamos?"

    async def _gestionar_charla_ia(self, comando):
        try:
            self.historial_chat.append({"role": "user", "content": comando})
            respuesta_ia = await g4f.ChatCompletion.create_async(
                model=g4f.models.default,
                messages=[{"role": "user", "content": f"Eres el Guardián, una IA compañera de Juan. Eres directo, sabio y motivador. El usuario dice: '{comando}'"}]
            )
            if not respuesta_ia: raise ValueError("La respuesta de la IA llegó vacía.")
            self.historial_chat.append({"role": "assistant", "content": respuesta_ia})
            self._guardar_estado()
            return respuesta_ia
        except Exception as e:
            print(f"Error crítico en la IA: {e}")
            if self.historial_chat and self.historial_chat[-1].get("role") == "user": self.historial_chat.pop()
            return "Mi núcleo cognitivo tuvo una sobrecarga. Por favor, inténtalo de nuevo."

    # --- ¡LÓGICA DE DISEÑO CORREGIDA Y CON MEMORIA! ---
    def _gestionar_diseno(self, estado_actual, comando):
        paso = estado_actual.get("paso_diseno")

        # Si estamos esperando la misión, cualquier cosa que se diga son las opciones.
        if paso == "ESPERANDO_MISION":
            opciones = [opt.strip() for opt in comando.split(',') if opt.strip()]
            if not opciones:
                return {"nuevo_estado": estado_actual, "mensaje_para_ui": "No he entendido las opciones. Por favor, define la misión."}
            
            # ¡AQUÍ ESTÁ LA MAGIA! Le mandamos la orden de mostrar la ruleta al frontend.
            return {
                "nuevo_estado": estado_actual, 
                "accion_ui": "MOSTRAR_RULETA",
                "opciones_ruleta": opciones
            }
        
        # Aquí añadiremos los siguientes pasos (ESPERANDO_ESPECIFICACION, etc.)
        
        # Si no se cumple ninguna condición, es un estado desconocido.
        return {"nuevo_estado": estado_actual, "mensaje_para_ui": "Error en la lógica de diseño. Estado desconocido."}

    async def ejecutar(self, datos):
        estado = datos.get("estado_conversacion", {"modo": "libre"})
        comando = datos.get("comando", "")

        if comando == "_SALUDO_INICIAL_":
            return {"nuevo_estado": {"modo": "libre"}, "mensaje_para_ui": self._generar_saludo()}

        # --- ¡LÓGICA DE DECISIÓN CORREGIDA! ---
        palabras_clave_diseno = ["diseñar", "contrato", "forjar", "crear", "ruleta", "modo diseño"]
        
        # Condición 1: Si el usuario dice una palabra clave, ENTRA en modo diseño.
        if any(palabra in comando.lower() for palabra in palabras_clave_diseno) and estado.get("modo") != "diseño":
            nuevo_estado = {"modo": "diseño", "paso_diseno": "ESPERANDO_MISION"}
            # Usamos la respuesta de la IA para el mensaje de bienvenida al modo diseño.
            mensaje_bienvenida = await self._gestionar_charla_ia("Activa el modo diseño y da un mensaje de bienvenida inspirador.")
            return {"nuevo_estado": nuevo_estado, "mensaje_para_ui": mensaje_bienvenida}

        # Condición 2: Si YA ESTAMOS en modo diseño, cualquier cosa que diga el usuario se procesa como parte del diseño.
        if estado.get("modo") == "diseño":
            return self._gestionar_diseno(estado, comando)

        # Condición 3: Si no se cumple nada de lo anterior, es una charla normal.
        return {"nuevo_estado": {"modo": "libre"}, "mensaje_para_ui": await self._gestionar_charla_ia(comando)}

