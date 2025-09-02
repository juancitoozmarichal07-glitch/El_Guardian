# =================================================================
# guardian.py (v14.0 - EL PIZARRÓN DIARIO)
# =================================================================

import json
import os
from datetime import datetime
import g4f

class Guardian:
    def __init__(self):
        # La memoria ya no se carga al iniciar, se carga por petición.
        self.ruta_memoria = 'memoria'
        if not os.path.exists(self.ruta_memoria):
            os.makedirs(self.ruta_memoria)
        print(f"    - Especialista 'Guardian' v14.0 (Pizarrón Diario) listo.")

    # --- NUEVAS FUNCIONES DE GESTIÓN DE MEMORIA DIARIA ---
    def _get_ruta_archivo_hoy(self):
        """Devuelve la ruta completa al archivo JSON del día actual."""
        hoy_str = datetime.now().strftime('%Y-%m-%d')
        return os.path.join(self.ruta_memoria, f"{hoy_str}.json")

    def _cargar_estado_hoy(self):
        """Carga el estado del día actual. Si no existe, crea uno nuevo."""
        ruta_archivo = self._get_ruta_archivo_hoy()
        try:
            with open(ruta_archivo, 'r', encoding='utf-8') as f:
                return json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            # Si el archivo no existe o está corrupto, empezamos un día nuevo.
            return {"historial_chat": [], "contratos_forjados": []}

    def _guardar_estado_hoy(self, estado):
        """Guarda el estado proporcionado en el archivo del día actual."""
        ruta_archivo = self._get_ruta_archivo_hoy()
        with open(ruta_archivo, 'w', encoding='utf-8') as f:
            json.dump(estado, f, indent=4)

    # --- Lógica de Diseño de Contratos (sin cambios, pero ahora usa el estado diario) ---
    def _gestionar_diseno(self, estado_actual, comando):
        # (Esta función se queda exactamente igual que en la v13.0)
        # ... (pegar aquí la función _gestionar_diseno completa de la v13.0)
        paso = estado_actual.get("paso_diseno")
        datos_plan = estado_actual.get("datos_plan", {})

        # PASO 1: MISIÓN INICIAL
        if paso == "ESPERANDO_MISION":
            opciones = [opt.strip() for opt in comando.split(',') if opt.strip()]
            if not opciones: return {"nuevo_estado": estado_actual, "mensaje_para_ui": "Define la misión."}
            if len(opciones) == 1:
                datos_plan["mision"] = [opciones[0]]
                nuevo_estado = {"modo": "diseño", "paso_diseno": "ESPERANDO_DECISION_ESPECIFICACION", "datos_plan": datos_plan}
                return {"nuevo_estado": nuevo_estado, "mensaje_para_ui": f"Misión aceptada: **{opciones[0]}**.\n\n¿Necesitas especificar más? (sí/no)"}
            else:
                estado_actual["paso_diseno"] = "ESPERANDO_RESULTADO_MISION"
                return {"nuevo_estado": estado_actual, "accion_ui": "MOSTRAR_RULETA", "opciones_ruleta": opciones}
        elif paso == "ESPERANDO_RESULTADO_MISION":
            datos_plan["mision"] = [comando]
            nuevo_estado = {"modo": "diseño", "paso_diseno": "ESPERANDO_DECISION_ESPECIFICACION", "datos_plan": datos_plan}
            return {"nuevo_estado": nuevo_estado, "mensaje_para_ui": f"Misión elegida: **{comando}**.\n\n¿Necesitas especificar más? (sí/no)"}

        # PASO 2: ESPECIFICACIÓN
        elif paso == "ESPERANDO_DECISION_ESPECIFICACION":
            if "si" in comando.lower():
                nuevo_estado = {"modo": "diseño", "paso_diseno": "ESPERANDO_ESPECIFICACION", "datos_plan": datos_plan}
                mision_actual_str = " -> ".join(datos_plan.get('mision', []))
                return {"nuevo_estado": nuevo_estado, "mensaje_para_ui": f"Misión actual: **{mision_actual_str}**.\n\nDime las opciones para la siguiente capa."}
            elif "no" in comando.lower():
                nuevo_estado = {"modo": "diseño", "paso_diseno": "ESPERANDO_ARRANQUE", "datos_plan": datos_plan}
                mision_final_str = " -> ".join(datos_plan.get('mision', []))
                return {"nuevo_estado": nuevo_estado, "mensaje_para_ui": f"Perfecto. Misión definida: **{mision_final_str}**.\n\nAhora, define el **momento de arranque**."}
            else: return {"nuevo_estado": estado_actual, "mensaje_para_ui": "Responde 'sí' o 'no'."}
        elif paso == "ESPERANDO_ESPECIFICACION":
            opciones = [opt.strip() for opt in comando.split(',') if opt.strip()]
            if not opciones: return {"nuevo_estado": estado_actual, "mensaje_para_ui": "Define la especificación."}
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
            # ... (lógica de arranque igual que v13.0)
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

        # PASO 4: DURACIÓN
        elif paso == "ESPERANDO_DECISION_DURACION":
            # ... (lógica de decisión de duración igual que v13.0)
            if "si" in comando.lower():
                nuevo_estado = {"modo": "diseño", "paso_diseno": "ESPERANDO_DURACION", "datos_plan": datos_plan}
                return {"nuevo_estado": nuevo_estado, "mensaje_para_ui": "Entendido. Dime las opciones para la duración."}
            elif "no" in comando.lower():
                datos_plan["duracion"] = "No definida"
                mision_final_str = " -> ".join(datos_plan.get('mision', ['N/A']))
                contrato_texto = (f"**CONTRATO FORJADO**\n--------------------\n**Misión:** {mision_final_str}\n**Arranque:** {datos_plan.get('arranque', 'N/A')}\n**Duración:** {datos_plan.get('duracion', 'N/A')}\n--------------------\nContrato sellado. ¿Siguiente misión?")
                
                # Guardamos el contrato antes de salir del modo diseño
                estado_actual["contratos_forjados"].append({"mision": mision_final_str, "arranque": datos_plan.get('arranque', 'N/A'), "duracion": datos_plan.get('duracion', 'N/A'), "estado": "agendado"})
                
                return {"nuevo_estado": {"modo": "libre"}, "mensaje_para_ui": contrato_texto}
            else: return {"nuevo_estado": estado_actual, "mensaje_para_ui": "Responde 'sí' o 'no'."}
        elif paso == "ESPERANDO_DURACION":
            # ... (lógica de duración igual que v13.0, con "min")
            opciones = [opt.strip() for opt in comando.split(',') if opt.strip()]
            if not opciones: return {"nuevo_estado": estado_actual, "mensaje_para_ui": "Define la duración."}
            if len(opciones) == 1:
                datos_plan["duracion"] = opciones[0]
                mision_final_str = " -> ".join(datos_plan.get('mision', ['N/A']))
                contrato_texto = (f"**CONTRATO FORJADO**\n--------------------\n**Misión:** {mision_final_str}\n**Arranque:** {datos_plan.get('arranque', 'N/A')}\n**Duración:** {datos_plan.get('duracion', 'N/A')} min\n--------------------\nContrato sellado. ¿Siguiente misión?")
                
                # Guardamos el contrato
                estado_actual["contratos_forjados"].append({"mision": mision_final_str, "arranque": datos_plan.get('arranque', 'N/A'), "duracion": f"{datos_plan.get('duracion', 'N/A')} min", "estado": "agendado"})
                
                return {"nuevo_estado": {"modo": "libre"}, "mensaje_para_ui": contrato_texto}
            else:
                estado_actual["paso_diseno"] = "ESPERANDO_RESULTADO_DURACION"
                return {"nuevo_estado": estado_actual, "accion_ui": "MOSTRAR_RULETA", "opciones_ruleta": opciones}
        elif paso == "ESPERANDO_RESULTADO_DURACION":
            datos_plan["duracion"] = comando
            mision_final_str = " -> ".join(datos_plan.get('mision', ['N/A']))
            contrato_texto = (f"**CONTRATO FORJADO**\n--------------------\n**Misión:** {mision_final_str}\n**Arranque:** {datos_plan.get('arranque', 'N/A')}\n**Duración:** {datos_plan.get('duracion', 'N/A')} min\n--------------------\nContrato sellado. ¿Siguiente misión?")
            
            # Guardamos el contrato
            estado_actual["contratos_forjados"].append({"mision": mision_final_str, "arranque": datos_plan.get('arranque', 'N/A'), "duracion": f"{datos_plan.get('duracion', 'N/A')} min", "estado": "agendado"})
            
            return {"nuevo_estado": {"modo": "libre"}, "mensaje_para_ui": contrato_texto}

        return {"nuevo_estado": {"modo": "libre"}, "mensaje_para_ui": "Hubo un error en el flujo de diseño. Reiniciando."}

    # --- Lógica de Conversación con IA (sin cambios) ---
    async def _gestionar_charla_ia(self, comando):
        # ... (pegar aquí la función _gestionar_charla_ia completa de la v13.0)
        try:
            prompt = f"Eres el Guardián, una IA compañera de Juan. Eres directo, sabio y motivador. El usuario dice: '{comando}'"
            respuesta_ia = await g4f.ChatCompletion.create_async(model=g4f.models.default, messages=[{"role": "user", "content": prompt}])
            if not respuesta_ia: raise ValueError("La respuesta de la IA llegó vacía.")
            return respuesta_ia
        except Exception as e:
            print(f"Error crítico al llamar a g4f: {e}")
            return "Mi núcleo cognitivo tuvo una sobrecarga."

    # --- Punto de Entrada Principal (¡MODIFICADO PARA CARGAR/GUARDAR ESTADO DIARIO!) ---
    async def ejecutar(self, datos):
        # 1. Cargar el estado del día actual al inicio de cada petición.
        estado_hoy = self._cargar_estado_hoy()
        
        # El estado de la conversación viene del cliente, pero lo fusionamos con los datos del día.
        estado_conversacion_cliente = datos.get("estado_conversacion", {"modo": "libre"})
        estado_hoy["modo"] = estado_conversacion_cliente.get("modo")
        estado_hoy["paso_diseno"] = estado_conversacion_cliente.get("paso_diseno")
        estado_hoy["datos_plan"] = estado_conversacion_cliente.get("datos_plan", {})

        comando = datos.get("comando", "")
        respuesta_final = {}

        if comando == "_SALUDO_INICIAL_":
            # Al saludar, le enviamos el historial del día al cliente.
            estado_hoy["modo"] = "libre"
            respuesta_final = {"nuevo_estado": {"modo": "libre"}, "historial_para_ui": estado_hoy["historial_chat"], "mensaje_para_ui": "Guardián online. ¿Forjamos un Contrato o necesitas conversar?"}
        
        else:
            # Añadimos el comando del usuario al historial del día
            estado_hoy["historial_chat"].append({"role": "user", "content": comando})

            palabras_clave_diseno = ["diseñar", "contrato", "forjar", "crear", "ruleta", "modo diseño"]
            
            if any(palabra in comando.lower() for palabra in palabras_clave_diseno) and estado_hoy.get("modo") != "diseño":
                estado_hoy["modo"] = "diseño"
                estado_hoy["paso_diseno"] = "ESPERANDO_MISION"
                estado_hoy["datos_plan"] = {}
                mensaje_bienvenida = "Modo Diseño activado. La claridad precede a la acción. Dime las opciones para la misión."
                respuesta_final = {"nuevo_estado": {"modo": "diseño", "paso_diseno": "ESPERANDO_MISION", "datos_plan": {}}, "mensaje_para_ui": mensaje_bienvenida}

            elif estado_hoy.get("modo") == "diseño":
                respuesta_diseno = self._gestionar_diseno(estado_hoy, comando)
                estado_hoy["modo"] = respuesta_diseno["nuevo_estado"].get("modo")
                estado_hoy["paso_diseno"] = respuesta_diseno["nuevo_estado"].get("paso_diseno")
                estado_hoy["datos_plan"] = respuesta_diseno["nuevo_estado"].get("datos_plan")
                respuesta_final = respuesta_diseno

            else: # Modo conversacional
                respuesta_conversacional = await self._gestionar_charla_ia(comando)
                respuesta_final = {"nuevo_estado": {"modo": "libre"}, "mensaje_para_ui": respuesta_conversacional}

            # Añadimos la respuesta del Guardián al historial del día
            if respuesta_final.get("mensaje_para_ui"):
                estado_hoy["historial_chat"].append({"role": "assistant", "content": respuesta_final.get("mensaje_para_ui")})

        # 2. Guardar el estado actualizado del día antes de devolver la respuesta.
        self._guardar_estado_hoy(estado_hoy)
        
        return respuesta_final

