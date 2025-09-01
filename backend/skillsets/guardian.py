# =================================================================
# guardian.py (v13.0 - LA VISIÓN COMPLETA)
# =================================================================

import json
from datetime import datetime
import g4f

class Guardian:
    def __init__(self):
        self.estado_global = {}
        print(f"    - Especialista 'Guardian' v13.0 (Visión Completa) listo.")

    # --- Lógica de Diseño de Contratos (Flujo Maestro Restaurado) ---
    def _gestionar_diseno(self, estado_actual, comando):
        paso = estado_actual.get("paso_diseno")
        datos_plan = estado_actual.get("datos_plan", {})

        # PASO 1: MISIÓN INICIAL
        if paso == "ESPERANDO_MISION":
            opciones = [opt.strip() for opt in comando.split(',') if opt.strip()]
            if not opciones:
                return {"nuevo_estado": estado_actual, "mensaje_para_ui": "Define la misión con una o más opciones."}
            
            if len(opciones) == 1:
                datos_plan["mision"] = [opciones[0]] # Guardamos como lista
                nuevo_estado = {"modo": "diseño", "paso_diseno": "ESPERANDO_DECISION_ESPECIFICACION", "datos_plan": datos_plan}
                return {"nuevo_estado": nuevo_estado, "mensaje_para_ui": f"Misión aceptada: **{opciones[0]}**.\n\n¿Necesitas especificar más esta tarea? (sí/no)"}
            else:
                estado_actual["paso_diseno"] = "ESPERANDO_RESULTADO_MISION"
                return {"nuevo_estado": estado_actual, "accion_ui": "MOSTRAR_RULETA", "opciones_ruleta": opciones}

        elif paso == "ESPERANDO_RESULTADO_MISION":
            datos_plan["mision"] = [comando] # Guardamos como lista
            nuevo_estado = {"modo": "diseño", "paso_diseno": "ESPERANDO_DECISION_ESPECIFICACION", "datos_plan": datos_plan}
            return {"nuevo_estado": nuevo_estado, "mensaje_para_ui": f"Misión elegida: **{comando}**.\n\n¿Necesitas especificar más? (sí/no)"}

        # PASO 2: DECISIÓN DE ESPECIFICACIÓN (¡RESTAURADO!)
        elif paso == "ESPERANDO_DECISION_ESPECIFICACION":
            if "si" in comando.lower():
                nuevo_estado = {"modo": "diseño", "paso_diseno": "ESPERANDO_ESPECIFICACION", "datos_plan": datos_plan}
                mision_actual_str = " -> ".join(datos_plan.get('mision', []))
                return {"nuevo_estado": nuevo_estado, "mensaje_para_ui": f"Misión actual: **{mision_actual_str}**.\n\nDime las opciones para la siguiente capa de especificación."}
            elif "no" in comando.lower():
                nuevo_estado = {"modo": "diseño", "paso_diseno": "ESPERANDO_ARRANQUE", "datos_plan": datos_plan}
                mision_final_str = " -> ".join(datos_plan.get('mision', []))
                return {"nuevo_estado": nuevo_estado, "mensaje_para_ui": f"Perfecto. Misión definida: **{mision_final_str}**.\n\nAhora, define el **momento de arranque**."}
            else:
                return {"nuevo_estado": estado_actual, "mensaje_para_ui": "Responde 'sí' o 'no'."}

        # PASO 2.5: GESTIÓN DE ESPECIFICACIONES (¡RESTAURADO!)
        elif paso == "ESPERANDO_ESPECIFICACION":
            opciones = [opt.strip() for opt in comando.split(',') if opt.strip()]
            if not opciones:
                return {"nuevo_estado": estado_actual, "mensaje_para_ui": "Define la especificación."}
            
            if len(opciones) == 1:
                datos_plan["mision"].append(opciones[0])
                nuevo_estado = {"modo": "diseño", "paso_diseno": "ESPERANDO_DECISION_ESPECIFICACION", "datos_plan": datos_plan}
                mision_actual_str = " -> ".join(datos_plan.get('mision', []))
                return {"nuevo_estado": nuevo_estado, "mensaje_para_ui": f"Misión actualizada: **{mision_actual_str}**.\n\n¿Necesitas especificar más? (sí/no)"}
            else:
                estado_actual["paso_diseno"] = "ESPERANDO_RESULTADO_ESPECIFICACION"
                return {"nuevo_estado": estado_actual, "accion_ui": "MOSTRAR_RULETA", "opciones_ruleta": opciones}

        elif paso == "ESPERANDO_RESULTADO_ESPECIFICACION":
            datos_plan["mision"].append(comando)
            nuevo_estado = {"modo": "diseño", "paso_diseno": "ESPERANDO_DECISION_ESPECIFICACION", "datos_plan": datos_plan}
            mision_actual_str = " -> ".join(datos_plan.get('mision', []))
            return {"nuevo_estado": nuevo_estado, "mensaje_para_ui": f"Misión actualizada: **{mision_actual_str}**.\n\n¿Necesitas especificar más? (sí/no)"}

        # PASO 3: ARRANQUE
        elif paso == "ESPERANDO_ARRANQUE":
            opciones = [opt.strip() for opt in comando.split(',') if opt.strip()]
            if not opciones: return {"nuevo_estado": estado_actual, "mensaje_para_ui": "Define el momento de arranque."}
            if len(opciones) == 1:
                datos_plan["arranque"] = opciones[0]
                nuevo_estado = {"modo": "diseño", "paso_diseno": "ESPERANDO_DECISION_DURACION", "datos_plan": datos_plan}
                return {"nuevo_estado": nuevo_estado, "mensaje_para_ui": f"Arranque fijado para: **{opciones[0]}**.\n\n¿Necesitas definir una duración? (sí/no)"}
            else:
                estado_actual["paso_diseno"] = "ESPERANDO_RESULTADO_ARRANQUE"
                return {"nuevo_estado": estado_actual, "accion_ui": "MOSTRAR_RULETA", "opciones_ruleta": opciones}

        elif paso == "ESPERANDO_RESULTADO_ARRANQUE":
            datos_plan["arranque"] = comando
            nuevo_estado = {"modo": "diseño", "paso_diseno": "ESPERANDO_DECISION_DURACION", "datos_plan": datos_plan}
            return {"nuevo_estado": nuevo_estado, "mensaje_para_ui": f"Arranque fijado para: **{comando}**.\n\n¿Necesitas definir una duración? (sí/no)"}

        # PASO 4: DECISIÓN DE DURACIÓN
        elif paso == "ESPERANDO_DECISION_DURACION":
            if "si" in comando.lower():
                nuevo_estado = {"modo": "diseño", "paso_diseno": "ESPERANDO_DURACION", "datos_plan": datos_plan}
                return {"nuevo_estado": nuevo_estado, "mensaje_para_ui": "Entendido. Dime las opciones para la duración."}
            elif "no" in comando.lower():
                datos_plan["duracion"] = "No definida"
                mision_final_str = " -> ".join(datos_plan.get('mision', ['N/A']))
                contrato_texto = (f"**CONTRATO FORJADO**\n--------------------\n**Misión:** {mision_final_str}\n**Arranque:** {datos_plan.get('arranque', 'N/A')}\n**Duración:** {datos_plan.get('duracion', 'N/A')}\n--------------------\nContrato sellado. ¿Siguiente misión?")
                return {"nuevo_estado": {"modo": "libre"}, "mensaje_para_ui": contrato_texto}
            else:
                return {"nuevo_estado": estado_actual, "mensaje_para_ui": "Responde 'sí' o 'no'."}

        # PASO 5: DURACIÓN (¡CON UNIDADES CORREGIDAS!)
        elif paso == "ESPERANDO_DURACION":
            opciones = [opt.strip() for opt in comando.split(',') if opt.strip()]
            if not opciones: return {"nuevo_estado": estado_actual, "mensaje_para_ui": "Define la duración."}
            if len(opciones) == 1:
                datos_plan["duracion"] = opciones[0]
                mision_final_str = " -> ".join(datos_plan.get('mision', ['N/A']))
                contrato_texto = (f"**CONTRATO FORJADO**\n--------------------\n**Misión:** {mision_final_str}\n**Arranque:** {datos_plan.get('arranque', 'N/A')}\n**Duración:** {datos_plan.get('duracion', 'N/A')} min\n--------------------\nContrato sellado. ¿Siguiente misión?")
                return {"nuevo_estado": {"modo": "libre"}, "mensaje_para_ui": contrato_texto}
            else:
                estado_actual["paso_diseno"] = "ESPERANDO_RESULTADO_DURACION"
                return {"nuevo_estado": estado_actual, "accion_ui": "MOSTRAR_RULETA", "opciones_ruleta": opciones}

        elif paso == "ESPERANDO_RESULTADO_DURACION":
            datos_plan["duracion"] = comando
            mision_final_str = " -> ".join(datos_plan.get('mision', ['N/A']))
            contrato_texto = (f"**CONTRATO FORJADO**\n--------------------\n**Misión:** {mision_final_str}\n**Arranque:** {datos_plan.get('arranque', 'N/A')}\n**Duración:** {datos_plan.get('duracion', 'N/A')} min\n--------------------\nContrato sellado. ¿Siguiente misión?")
            return {"nuevo_estado": {"modo": "libre"}, "mensaje_para_ui": contrato_texto}

        return {"nuevo_estado": {"modo": "libre"}, "mensaje_para_ui": "Hubo un error en el flujo de diseño. Reiniciando."}

    # --- Lógica de Conversación con IA ---
    async def _gestionar_charla_ia(self, comando):
        try:
            prompt = f"Eres el Guardián, una IA compañera de Juan. Eres directo, sabio y motivador. Tu objetivo es ayudarlo a mantenerse enfocado y productivo, pero también puedes conversar como un amigo. El usuario dice: '{comando}'"
            respuesta_ia = await g4f.ChatCompletion.create_async(model=g4f.models.default, messages=[{"role": "user", "content": prompt}])
            if not respuesta_ia: raise ValueError("La respuesta de la IA llegó vacía.")
            return respuesta_ia
        except Exception as e:
            print(f"Error crítico al llamar a g4f: {e}")
            return "Mi núcleo cognitivo tuvo una sobrecarga. Por favor, inténtalo de nuevo."

    # --- Punto de Entrada Principal ---
    async def ejecutar(self, datos):
        estado = datos.get("estado_conversacion", {"modo": "libre"})
        comando = datos.get("comando", "")

        if comando == "_SALUDO_INICIAL_":
            return {"nuevo_estado": {"modo": "libre"}, "mensaje_para_ui": "Guardián online. ¿Forjamos un Contrato o necesitas conversar?"}

        palabras_clave_diseno = ["diseñar", "contrato", "forjar", "crear", "ruleta", "modo diseño"]
        
        if any(palabra in comando.lower() for palabra in palabras_clave_diseno) and estado.get("modo") != "diseño":
            nuevo_estado = {"modo": "diseño", "paso_diseno": "ESPERANDO_MISION", "datos_plan": {}}
            return {"nuevo_estado": nuevo_estado, "mensaje_para_ui": "Modo Diseño activado. La claridad precede a la acción. Dime las opciones para la misión."}

        if estado.get("modo") == "diseño":
            return self._gestionar_diseno(estado, comando)

        respuesta_conversacional = await self._gestionar_charla_ia(comando)
        return {"nuevo_estado": {"modo": "libre"}, "mensaje_para_ui": respuesta_conversacional}
