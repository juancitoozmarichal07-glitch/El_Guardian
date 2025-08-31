# =================================================================
# guardian.py (v9.0 - CON IA CONVERSACIONAL RESTAURADA)
# =================================================================

import json
from datetime import datetime
import g4f # ¡Importamos la librería!

class Guardian:
    def __init__(self):
        self.estado_global = {}
        print(f"    - Especialista 'Guardian' v9.0 (IA Restaurada) listo.")

    # La función _gestionar_diseno se queda exactamente igual que antes.
    def _gestionar_diseno(self, estado_actual, comando):
        # ... (Aquí va la función _gestionar_diseno completa que ya tienes y funciona)
        # ... (No es necesario que la copies de nuevo, solo asegúrate de que está ahí)
        paso = estado_actual.get("paso_diseno")
        datos_plan = estado_actual.get("datos_plan", {"mision": "", "especificaciones": []})

        if paso == "ESPERANDO_MISION":
            opciones = [opt.strip() for opt in comando.split(',') if opt.strip()]
            if not opciones:
                return {"nuevo_estado": estado_actual, "mensaje_para_ui": "No he entendido las opciones. Por favor, define la misión con una o más opciones separadas por comas."}
            
            if len(opciones) == 1:
                datos_plan["mision"] = opciones[0]
                nuevo_estado = {"modo": "diseño", "paso_diseno": "ESPERANDO_ESPECIFICACION", "datos_plan": datos_plan}
                return {"nuevo_estado": nuevo_estado, "mensaje_para_ui": f"Misión aceptada: **{opciones[0]}**.\n\n¿Quieres añadir otra capa de ruleta para especificar más? (sí/no)"}
            
            else:
                estado_actual["paso_diseno"] = "ESPERANDO_RESULTADO_MISION"
                return {"nuevo_estado": estado_actual, "accion_ui": "MOSTRAR_RULETA", "opciones_ruleta": opciones}

        elif paso == "ESPERANDO_RESULTADO_MISION":
            datos_plan["mision"] = comando
            nuevo_estado = {"modo": "diseño", "paso_diseno": "ESPERANDO_ESPECIFICACION", "datos_plan": datos_plan}
            return {"nuevo_estado": nuevo_estado, "mensaje_para_ui": f"Misión aceptada: **{comando}**.\n\n¿Quieres añadir otra capa de ruleta para especificar más? (sí/no)"}

        elif paso == "ESPERANDO_ESPECIFICACION":
            if "no" in comando.lower() or "si" in comando.lower():
                nuevo_estado = {"modo": "diseño", "paso_diseno": "ESPERANDO_HORA", "datos_plan": datos_plan}
                return {"nuevo_estado": nuevo_estado, "mensaje_para_ui": "Perfecto. Misión definida.\n\nAhora, dime las opciones para la **hora de inicio** (ej: 22:00, 22:30)."}
            
            else:
                return {"nuevo_estado": estado_actual, "mensaje_para_ui": "No te he entendido. Por favor, responde 'sí' o 'no'."}

        elif paso == "ESPERANDO_HORA":
            datos_plan["hora"] = comando.split(',')[0].strip()
            nuevo_estado = {"modo": "diseño", "paso_diseno": "ESPERANDO_DURACION", "datos_plan": datos_plan}
            return {"nuevo_estado": nuevo_estado, "mensaje_para_ui": f"Hora de inicio: **{datos_plan['hora']}**.\n\nFinalmente, dime las opciones para la **duración** (ej: 30 min, 1 hora)."}

        elif paso == "ESPERANDO_DURACION":
            datos_plan["duracion"] = comando.split(',')[0].strip()
            mision_final = datos_plan.get('mision', 'No definida')
            hora_final = datos_plan.get('hora', 'No definida')
            duracion_final = datos_plan.get('duracion', 'No definida')
            
            contrato_texto = (f"**CONTRATO FORJADO**\n--------------------\n**Misión:** {mision_final}\n**Inicio:** {hora_final}\n**Duración:** {duracion_final}\n--------------------\nContrato sellado. La disciplina es libertad. ¿Siguiente misión?")
            
            nuevo_estado = {"modo": "libre"}
            return {"nuevo_estado": nuevo_estado, "mensaje_para_ui": contrato_texto}

        return {"nuevo_estado": estado_actual, "mensaje_para_ui": "Error en la lógica de diseño. Estado desconocido."}


    # --- ¡NUEVA FUNCIÓN ASÍNCRONA PARA LA IA! ---
    async def _gestionar_charla_ia(self, comando):
        try:
            # Creamos el prompt para darle contexto a la IA
            prompt = f"Eres el Guardián, una IA compañera de Juan. Eres directo, sabio y motivador. Tu objetivo es ayudarlo a mantenerse enfocado y productivo, pero también puedes conversar como un amigo. El usuario dice: '{comando}'"
            
            # Hacemos la llamada a la API de g4f
            respuesta_ia = await g4f.ChatCompletion.create_async(
                model=g4f.models.default,
                messages=[{"role": "user", "content": prompt}]
            )
            
            if not respuesta_ia:
                raise ValueError("La respuesta de la IA llegó vacía.")
            
            return respuesta_ia
        except Exception as e:
            print(f"Error crítico al llamar a g4f: {e}")
            # Mensaje de fallback si la IA falla
            return "Mi núcleo cognitivo tuvo una sobrecarga. Por favor, inténtalo de nuevo o prueba a 'diseñar un contrato'."


    # --- FUNCIÓN EJECUTAR ACTUALIZADA ---
    async def ejecutar(self, datos):
        estado = datos.get("estado_conversacion", {"modo": "libre"})
        comando = datos.get("comando", "")

        if comando == "_SALUDO_INICIAL_":
            return {"nuevo_estado": {"modo": "libre"}, "mensaje_para_ui": "Guardián online. ¿Forjamos un Contrato o necesitas conversar?"}

        palabras_clave_diseno = ["diseñar", "contrato", "forjar", "crear", "ruleta", "modo diseño"]
        
        if any(palabra in comando.lower() for palabra in palabras_clave_diseno) and estado.get("modo") != "diseño":
            nuevo_estado = {"modo": "diseño", "paso_diseno": "ESPERANDO_MISION", "datos_plan": {}}
            mensaje_bienvenida = "Modo Diseño activado. La claridad precede a la acción. Dime las opciones para la misión."
            return {"nuevo_estado": nuevo_estado, "mensaje_para_ui": mensaje_bienvenida}

        if estado.get("modo") == "diseño":
            return self._gestionar_diseno(estado, comando)

        # --- ¡AQUÍ ESTÁ LA MAGIA! ---
        # Si no es un comando de diseño, llamamos a la IA para una charla normal.
        respuesta_conversacional = await self._gestionar_charla_ia(comando)
        return {"nuevo_estado": {"modo": "libre"}, "mensaje_para_ui": respuesta_conversacional}

