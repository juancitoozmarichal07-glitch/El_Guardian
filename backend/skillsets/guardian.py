# guardian.py (VERSIÓN FINAL, REVISADA Y SIN ERRORES DE SINTAXIS)

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
        print(f"    - Especialista 'Guardian' v6.0 (Sintaxis Corregida) listo.")

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
        # ESTA ES LA FUNCIÓN QUE ESTABA MAL ESCRITA. AHORA ESTÁ CORRECTA.
        try:
            self.historial_chat.append({"role": "user", "content": comando})
            
            # Usamos la llamada simple y robusta que sabemos que funciona
            respuesta_ia = await g4f.ChatCompletion.create_async(
                model=g4f.models.default,
                messages=[{"role": "user", "content": f"Eres el Guardián, una IA compañera de Juan. Eres directo, sabio y motivador. El usuario dice: '{comando}'"}]
            )

            if not respuesta_ia:
                raise ValueError("La respuesta de la IA llegó vacía.")

            self.historial_chat.append({"role": "assistant", "content": respuesta_ia})
            self._guardar_estado()
            return respuesta_ia
        
        # ESTE ES EL BLOQUE 'except' QUE FALTABA
        except Exception as e:
            print(f"Error crítico en la IA: {e}")
            # Si algo falla, eliminamos la última pregunta del usuario para no contaminar el historial
            if self.historial_chat and self.historial_chat[-1].get("role") == "user":
                self.historial_chat.pop()
            return "Mi núcleo cognitivo tuvo una sobrecarga. Por favor, inténtalo de nuevo."

    def _gestionar_diseno(self, estado, comando):
        # Aquí irá la lógica de la ruleta, por ahora está simple
        palabras_clave = ["diseñar", "contrato", "forjar", "crear", "ruleta"]
        if any(palabra in comando.lower() for palabra in palabras_clave) and estado.get("modo") != "diseño":
            return {"nuevo_estado": {"modo": "diseño", "paso_diseno": "ESPERANDO_MISION"}, "mensaje_para_ui": "Modo Diseño activado. Define la misión (puedes dar una o varias opciones separadas por coma)."}
        
        # Lógica de la ruleta (simplificada por ahora)
        if estado.get("paso_diseno") == "ESPERANDO_MISION":
            opciones = [opt.strip() for opt in comando.split(',') if opt.strip()]
            if not opciones:
                return {"nuevo_estado": estado, "mensaje_para_ui": "No he entendido las opciones. Por favor, define la misión."}
            
            eleccion = random.choice(opciones)
            return {"nuevo_estado": {"modo": "libre"}, "mensaje_para_ui": f"La Ruleta ha girado. Misión aceptada: **{eleccion}**. (Lógica de los siguientes pasos pendiente)."}

        return {"nuevo_estado": estado, "mensaje_para_ui": f"Recibido en modo diseño: '{comando}'. Lógica pendiente."}

    async def ejecutar(self, datos):
        estado = datos.get("estado_conversacion", {"modo": "libre"})
        comando = datos.get("comando", "")

        if comando == "_SALUDO_INICIAL_":
            return {"nuevo_estado": {"modo": "libre"}, "mensaje_para_ui": self._generar_saludo()}

        palabras_clave_diseno = ["diseñar", "contrato", "forjar", "crear", "ruleta"]
        if any(palabra in comando.lower() for palabra in palabras_clave_diseno) or estado.get("modo") == "diseño":
            return self._gestionar_diseno(estado, comando)

        return {"nuevo_estado": {"modo": "libre"}, "mensaje_para_ui": await self._gestionar_charla_ia(comando)}

