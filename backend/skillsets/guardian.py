# =================================================================
# guardian.py (v11.0 - Flujo de Forjado 3.1 + IA)
# =================================================================

import json
from datetime import datetime
import g4f

class Guardian:
    def __init__(self):
        self.estado_global = {}
        print(f"    - Especialista 'Guardian' v11.0 (Flujo 3.1) listo.")

    # --- Lógica de Diseño de Contratos ---
    def _gestionar_diseno(self, estado_actual, comando):
        paso = estado_actual.get("paso_diseno")
        datos_plan = estado_actual.get("datos_plan", {})

        # PASO 1: ESPERANDO LA MISIÓN INICIAL
        if paso == "ESPERANDO_MISION":
            opciones = [opt.strip() for opt in comando.split(',') if opt.strip()]
            if not opciones:
                return {"nuevo_estado": estado_actual, "mensaje_para_ui": "Define la misión con una o más opciones."}
            
            if len(opciones) == 1:
                datos_plan["mision"] = opciones[0]
                nuevo_estado = {"modo": "diseño", "paso_diseno": "ESPERANDO_ARRANQUE", "datos_plan": datos_plan}
                return {"nuevo_estado": nuevo_estado, "mensaje_para_ui": f"Misión aceptada: **{opciones[0]}**.\n\nAhora, define el **momento de arranque** (ej: Ahora, 15:00)."}
            
            else:
                estado_actual["paso_diseno"] = "ESPERANDO_RESULTADO_MISION"
                return {"nuevo_estado": estado_actual, "accion_ui": "MOSTRAR_RULETA", "opciones_ruleta": opciones}

        # PASO 1.5: ESPERANDO RESULTADO DE RULETA DE MISIÓN
        elif paso == "ESPERANDO_RESULTADO_MISION":
            datos_plan["mision"] = comando
            nuevo_estado = {"modo": "diseño", "paso_diseno": "ESPERANDO_ARRANQUE", "datos_plan": datos_plan}
            return {"nuevo_estado": nuevo_estado, "mensaje_para_ui": f"Misión elegida: **{comando}**.\n\nAhora, define el **momento de arranque**."}

        # PASO 2: ESPERANDO EL ARRANQUE (OBLIGATORIO)
        elif paso == "ESPERANDO_ARRANQUE":
            datos_plan["arranque"] = comando.split(',')[0].strip()
            nuevo_estado = {"modo": "diseño", "paso_diseno": "ESPERANDO_DECISION_DURACION", "datos_plan": datos_plan}
            return {"nuevo_estado": nuevo_estado, "mensaje_para_ui": f"Arranque fijado para: **{datos_plan['arranque']}**.\n\n¿Necesitas definir una duración para esta tarea? (sí/no)"}

        # PASO 3: ESPERANDO DECISIÓN SOBRE LA DURACIÓN (OPCIONAL)
        elif paso == "ESPERANDO_DECISION_DURACION":
            if "si" in comando.lower():
                nuevo_estado = {"modo": "diseño", "paso_diseno": "ESPERANDO_DURACION", "datos_plan": datos_plan}
                return {"nuevo_estado": nuevo_estado, "mensaje_para_ui": "Entendido. Dime las opciones para la duración (ej: 25 min, 1 hora)."}
            
            elif "no" in comando.lower():
                datos_plan["duracion"] = "No definida"
                contrato_texto = (
                    f"**CONTRATO FORJADO**\n--------------------\n"
                    f"**Misión:** {datos_plan.get('mision', 'N/A')}\n"
                    f"**Arranque:** {datos_plan.get('arranque', 'N/A')}\n"
                    f"**Duración:** {datos_plan.get('duracion', 'N/A')}\n--------------------\n"
                    f"Contrato sellado. ¿Siguiente misión?"
                )
                nuevo_estado = {"modo": "libre"}
                return {"nuevo_estado": nuevo_estado, "mensaje_para_ui": contrato_texto}
            
            else:
                return {"nuevo_estado": estado_actual, "mensaje_para_ui": "Responde 'sí' o 'no'."}

        # PASO 4: ESPERANDO LA DURACIÓN
        elif paso == "ESPERANDO_DURACION":
            datos_plan["duracion"] = comando.split(',')[0].strip()
            contrato_texto = (
                f"**CONTRATO FORJADO**\n--------------------\n"
                f"**Misión:** {datos_plan.get('mision', 'N/A')}\n"
                f"**Arranque:** {datos_plan.get('arranque', 'N/A')}\n"
                f"**Duración:** {datos_plan.get('duracion', 'N/A')}\n--------------------\n"
                f"Contrato sellado. ¿Siguiente misión?"
            )
            nuevo_estado = {"modo": "libre"}
            return {"nuevo_estado": nuevo_estado, "mensaje_para_ui": contrato_texto}

        # Fallback por si algo sale mal
        return {"nuevo_estado": {"modo": "libre"}, "mensaje_para_ui": "Hubo un error en el flujo de diseño. Reiniciando."}

    # --- Lógica de Conversación con IA ---
    async def _gestionar_charla_ia(self, comando):
        try:
            prompt = f"Eres el Guardián, una IA compañera de Juan. Eres directo, sabio y motivador. Tu objetivo es ayudarlo a mantenerse enfocado y productivo, pero también puedes conversar como un amigo. El usuario dice: '{comando}'"
            respuesta_ia = await g4f.ChatCompletion.create_async(
                model=g4f.models.default,
                messages=[{"role": "user", "content": prompt}]
            )
            if not respuesta_ia:
                raise ValueError("La respuesta de la IA llegó vacía.")
            return respuesta_ia
        except Exception as e:
            print(f"Error crítico al llamar a g4f: {e}")
            return "Mi núcleo cognitivo tuvo una sobrecarga. Por favor, inténtalo de nuevo o prueba a 'diseñar un contrato'."

    # --- Punto de Entrada Principal ---
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

        # Si no es un comando de diseño, llamamos a la IA para una charla normal.
        respuesta_conversacional = await self._gestionar_charla_ia(comando)
        return {"nuevo_estado": {"modo": "libre"}, "mensaje_para_ui": respuesta_conversacional}

