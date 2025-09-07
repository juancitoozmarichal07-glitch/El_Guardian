# =================================================================
# GUARDIAN.PY (v2.2 - Con Importación Retrasada para Despliegue)
# =================================================================
# Se mueve la importación de g4f dentro de la función que la usa
# para evitar errores de carga de proveedores durante el arranque del servidor.

# NO importamos g4f aquí
import re
from datetime import datetime, timedelta

class Guardian:
    def __init__(self):
        """
        Inicializa el especialista Guardian.
        """
        print(f"    - Especialista 'Guardian' v2.2 (Con Importación Retrasada) listo.")

    def _extraer_duracion_de_tarea(self, texto_tarea):
        # ... (código sin cambios)
        match = re.search(r'\((\d+)\s*min\)', texto_tarea)
        if match:
            return int(match.group(1))
        match_num = re.search(r'\((\d+)\)', texto_tarea)
        if match_num:
            return int(match_num.group(1))
        return 0

    def _gestionar_diseno(self, estado_actual, comando):
        # ... (Pega aquí tu función _gestionar_diseno completa, sin cambios)
        paso = estado_actual.get("paso_diseno")
        datos_plan = estado_actual.get("datos_plan", {})

        # PASO 1: MISIÓN
        if paso == "ESPERANDO_MISION":
            opciones = [opt.strip() for opt in comando.split(',') if opt.strip()]
            if not opciones:
                return {"nuevo_estado": estado_actual, "mensaje_para_ui": "Define la misión."}
            if len(opciones) == 1:
                datos_plan["mision"] = opciones[0]
                nuevo_estado = {"modo": "diseño", "paso_diseno": "ESPERANDO_ESPECIFICACION", "datos_plan": datos_plan}
                return {"nuevo_estado": nuevo_estado, "mensaje_para_ui": f"Misión: **{opciones[0]}**. ¿Necesitas especificar más? (sí/no)"}
            else:
                estado_actual["paso_diseno"] = "ESPERANDO_RESULTADO_MISION"
                return {"nuevo_estado": estado_actual, "accion_ui": "MOSTRAR_RULETA", "opciones_ruleta": opciones}

        elif paso == "ESPERANDO_RESULTADO_MISION":
            datos_plan["mision"] = comando
            nuevo_estado = {"modo": "diseño", "paso_diseno": "ESPERANDO_ESPECIFICACION", "datos_plan": datos_plan}
            return {"nuevo_estado": nuevo_estado, "mensaje_para_ui": f"Misión elegida: **{comando}**. ¿Necesitas especificar más? (sí/no)"}

        # PASO 2: ESPECIFICACIÓN (EN CASCADA)
        elif paso == "ESPERANDO_ESPECIFICACION":
            if "si" in comando.lower():
                nuevo_estado = {"modo": "diseño", "paso_diseno": "ESPERANDO_OPCIONES_ESPECIFICACION", "datos_plan": datos_plan}
                return {"nuevo_estado": nuevo_estado, "mensaje_para_ui": "Entendido. Dame las opciones para la siguiente capa."}
            else:
                nuevo_estado = {"modo": "diseño", "paso_diseno": "ESPERANDO_ARRANQUE", "datos_plan": datos_plan}
                return {"nuevo_estado": nuevo_estado, "mensaje_para_ui": "Misión definida. Ahora, define el **momento de arranque**."}

        elif paso == "ESPERANDO_OPCIONES_ESPECIFICACION":
            opciones = [opt.strip() for opt in comando.split(',') if opt.strip()]
            if not opciones:
                return {"nuevo_estado": estado_actual, "mensaje_para_ui": "Define las opciones."}
            
            if "especificaciones" not in datos_plan: datos_plan["especificaciones"] = []
            
            if len(opciones) == 1:
                datos_plan["especificaciones"].append(opciones[0])
                mision_completa = f"{datos_plan.get('mision', '')} -> {' -> '.join(datos_plan['especificaciones'])}"
                nuevo_estado = {"modo": "diseño", "paso_diseno": "ESPERANDO_ESPECIFICACION", "datos_plan": datos_plan}
                return {"nuevo_estado": nuevo_estado, "mensaje_para_ui": f"Entendido: **{mision_completa}**. ¿Otra capa más? (sí/no)"}
            else:
                estado_actual["paso_diseno"] = "ESPERANDO_RESULTADO_ESPECIFICACION"
                return {"nuevo_estado": estado_actual, "accion_ui": "MOSTRAR_RULETA", "opciones_ruleta": opciones}

        elif paso == "ESPERANDO_RESULTADO_ESPECIFICACION":
            if "especificaciones" not in datos_plan: datos_plan["especificaciones"] = []
            datos_plan["especificaciones"].append(comando)
            mision_completa = f"{datos_plan.get('mision', '')} -> {' -> '.join(datos_plan['especificaciones'])}"
            nuevo_estado = {"modo": "diseño", "paso_diseno": "ESPERANDO_ESPECIFICACION", "datos_plan": datos_plan}
            return {"nuevo_estado": nuevo_estado, "mensaje_para_ui": f"Entendido: **{mision_completa}**. ¿Otra capa más? (sí/no)"}

        # PASO 3: ARRANQUE
        elif paso == "ESPERANDO_ARRANQUE":
            opciones = [opt.strip() for opt in comando.split(',') if opt.strip()]
            if not opciones: return {"nuevo_estado": estado_actual, "mensaje_para_ui": "Define el momento de arranque."}
            if len(opciones) == 1:
                datos_plan["arranque"] = opciones[0]
                nuevo_estado = {"modo": "diseño", "paso_diseno": "ESPERANDO_DECISION_DURACION", "datos_plan": datos_plan}
                return {"nuevo_estado": nuevo_estado, "mensaje_para_ui": f"Arranque: **{opciones[0]}**. ¿Necesitas definir una duración? (sí/no)"}
            else:
                estado_actual["paso_diseno"] = "ESPERANDO_RESULTADO_ARRANQUE"
                return {"nuevo_estado": estado_actual, "accion_ui": "MOSTRAR_RULETA", "opciones_ruleta": opciones}

        elif paso == "ESPERANDO_RESULTADO_ARRANQUE":
            datos_plan["arranque"] = comando
            nuevo_estado = {"modo": "diseño", "paso_diseno": "ESPERANDO_DECISION_DURACION", "datos_plan": datos_plan}
            return {"nuevo_estado": nuevo_estado, "mensaje_para_ui": f"Arranque: **{comando}**. ¿Necesitas definir una duración? (sí/no)"}

        # PASO 4: DURACIÓN
        elif paso == "ESPERANDO_DECISION_DURACION":
            if "si" in comando.lower():
                nuevo_estado = {"modo": "diseño", "paso_diseno": "ESPERANDO_DURACION", "datos_plan": datos_plan}
                return {"nuevo_estado": nuevo_estado, "mensaje_para_ui": "Entendido. Dime las opciones para la duración."}
            else:
                datos_plan["duracion"] = "No definida"
                return self._forjar_contrato(datos_plan)

        elif paso == "ESPERANDO_DURACION":
            opciones = [opt.strip() for opt in comando.split(',') if opt.strip()]
            if not opciones: return {"nuevo_estado": estado_actual, "mensaje_para_ui": "Define la duración."}
            if len(opciones) == 1:
                datos_plan["duracion"] = opciones[0]
                return self._forjar_contrato(datos_plan)
            else:
                estado_actual["paso_diseno"] = "ESPERANDO_RESULTADO_DURACION"
                return {"nuevo_estado": estado_actual, "accion_ui": "MOSTRAR_RULETA", "opciones_ruleta": opciones}

        elif paso == "ESPERANDO_RESULTADO_DURACION":
            datos_plan["duracion"] = comando
            return self._forjar_contrato(datos_plan)

        return {"nuevo_estado": {"modo": "libre"}, "mensaje_para_ui": "Error en el flujo de diseño. Reiniciando."}

    def _forjar_contrato(self, datos_plan):
        # ... (Pega aquí tu función _forjar_contrato completa, sin cambios)
        mision_base = datos_plan.get('mision', 'N/A')
        especificaciones = datos_plan.get('especificaciones', [])
        mision_completa = f"{mision_base} -> {' -> '.join(especificaciones)}" if especificaciones else mision_base
        
        contrato_texto = (
            f"**CONTRATO FORJADO**\n--------------------\n"
            f"**Misión:** {mision_completa}\n"
            f"**Arranque:** {datos_plan.get('arranque', 'N/A')}\n"
            f"**Duración:** {datos_plan.get('duracion', 'N/A')}\n--------------------\n"
            f"Contrato sellado. ¿Siguiente misión?"
        )
        nuevo_estado = {"modo": "libre"}
        return {"nuevo_estado": nuevo_estado, "mensaje_para_ui": contrato_texto}

    def _gestionar_transicion(self, estado_actual, comando):
        # ... (Pega aquí tu función _gestionar_transicion completa, sin cambios)
        paso = estado_actual.get("paso_transicion")
        datos_bache = estado_actual.get("datos_bache", {})

        # PASO 1: Esperando la actividad madre
        if paso == "ESPERANDO_ACTIVIDAD_MADRE":
            datos_bache["actividad_madre"] = comando
            nuevo_estado = {"modo": "transicion", "paso_transicion": "ESPERANDO_HORA_INICIO_MADRE", "datos_bache": datos_bache}
            return {"nuevo_estado": nuevo_estado, "mensaje_para_ui": f"Entendido: **{comando}**. ¿A qué hora comienza?"}

        # PASO 2: Esperando la hora de inicio y calculando el bache inicial
        elif paso == "ESPERANDO_HORA_INICIO_MADRE":
            try:
                hora_inicio_madre = datetime.strptime(comando, "%H:%M").time()
                ahora = datetime.now()
                fecha_inicio_madre = datetime.combine(ahora.date(), hora_inicio_madre)
                
                if fecha_inicio_madre < ahora:
                    fecha_inicio_madre += timedelta(days=1)

                bache_total_minutos = int((fecha_inicio_madre - ahora).total_seconds() / 60)

                if bache_total_minutos <= 5:
                    return {"nuevo_estado": {"modo": "libre"}, "mensaje_para_ui": "El bache de tiempo es muy corto. Reiniciando."}

                datos_bache["hora_inicio_madre"] = comando
                datos_bache["bache_restante_minutos"] = bache_total_minutos
                
                horas, minutos = divmod(bache_total_minutos, 60)
                mensaje_bache = f"Detectado un bache de **{horas}h y {minutos}min** hasta '{datos_bache['actividad_madre']}'.\n\nDefine las tareas de transición (ej: Tarea 1 (20 min))."

                nuevo_estado = {"modo": "transicion", "paso_transicion": "ESPERANDO_OPCIONES_TRANSICION", "datos_bache": datos_bache}
                return {"nuevo_estado": nuevo_estado, "mensaje_para_ui": mensaje_bache}

            except ValueError:
                return {"nuevo_estado": estado_actual, "mensaje_para_ui": "Formato de hora no válido. Usa HH:MM (ej: 23:50)."}

        # PASO 3: Esperando las opciones para la ruleta
        elif paso == "ESPERANDO_OPCIONES_TRANSICION":
            opciones = [opt.strip() for opt in comando.split(',') if opt.strip()]
            if not opciones:
                return {"nuevo_estado": estado_actual, "mensaje_para_ui": "Necesito al menos una opción de tarea."}
            
            estado_actual["paso_transicion"] = "ESPERANDO_RESULTADO_TRANSICION"
            return {"nuevo_estado": estado_actual, "accion_ui": "MOSTRAR_RULETA", "opciones_ruleta": opciones}

        # PASO 4: Procesar resultado, forjar contrato y decidir si continuar
        elif paso == "ESPERANDO_RESULTADO_TRANSICION":
            tarea_elegida = comando
            duracion_tarea = self._extraer_duracion_de_tarea(tarea_elegida)

            bache_anterior = datos_bache.get("bache_restante_minutos", 0)
            nuevo_bache = bache_anterior - duracion_tarea
            datos_bache["bache_restante_minutos"] = nuevo_bache

            contrato_texto = (
                f"**CONTRATO DE TRANSICIÓN FORJADO**\n--------------------\n"
                f"**Misión Actual:** **{tarea_elegida}**\n"
                f"**Tiempo Restante en Bache:** {nuevo_bache} minutos\n"
                f"**Actividad Madre:** {datos_bache.get('actividad_madre')} (a las {datos_bache.get('hora_inicio_madre')})\n--------------------"
            )

            if nuevo_bache < 10: # Umbral mínimo para continuar
                mensaje_final = f"{contrato_texto}\n\nBache de tiempo casi agotado. Prepárate para '{datos_bache.get('actividad_madre')}'. Saliendo de modo transición."
                return {"nuevo_estado": {"modo": "libre"}, "mensaje_para_ui": mensaje_final}
            else:
                nuevo_estado = {"modo": "transicion", "paso_transicion": "ESPERANDO_DECISION_CONTINUAR", "datos_bache": datos_bache}
                mensaje_continuacion = f"{contrato_texto}\n\n¿Forjamos otro contrato para los {nuevo_bache} minutos restantes? (sí/no)"
                return {"nuevo_estado": nuevo_estado, "mensaje_para_ui": mensaje_continuacion}

        # PASO 5: Esperar decisión de continuar el ciclo
        elif paso == "ESPERANDO_DECISION_CONTINUAR":
            if "si" in comando.lower():
                bache_restante = datos_bache.get("bache_restante_minutos", 0)
                horas, minutos = divmod(bache_restante, 60)
                mensaje_peticion = f"Entendido. Quedan **{horas}h y {minutos}min**. Define las nuevas tareas de transición."
                nuevo_estado = {"modo": "transicion", "paso_transicion": "ESPERANDO_OPCIONES_TRANSICION", "datos_bache": datos_bache}
                return {"nuevo_estado": nuevo_estado, "mensaje_para_ui": mensaje_peticion}
            else:
                return {"nuevo_estado": {"modo": "libre"}, "mensaje_para_ui": "De acuerdo. Saliendo de modo transición."}

        return {"nuevo_estado": {"modo": "libre"}, "mensaje_para_ui": "Error en el flujo de transición. Reiniciando."}

    # --- FUNCIÓN DE CHARLA (¡MODIFICADA!) ---
    async def _gestionar_charla_ia(self, comando):
        """
        Maneja la conversación libre, importando g4f solo cuando es necesario.
        """
        # --- ¡LA CLAVE ESTÁ AQUÍ! ---
        import g4f
        
        try:
            prompt = f"Eres el Guardián, una IA compañera de Juan. Eres directo, sabio y motivador. El usuario dice: '{comando}'"
            
            # Llamada limpia, sin especificar proveedor, como pediste.
            respuesta_ia = await g4f.ChatCompletion.create_async(
                model=g4f.models.default,
                messages=[{"role": "user", "content": prompt}]
            )
            return respuesta_ia or "No he podido procesar eso. Intenta de nuevo."
        except Exception as e:
            print(f"🚨 Error en la llamada a g4f: {e}")
            return "Mi núcleo cognitivo tuvo una sobrecarga. Inténtalo de nuevo."

    async def ejecutar(self, datos):
        # ... (Pega aquí tu función ejecutar completa, sin cambios)
        estado = datos.get("estado_conversacion", {"modo": "libre"})
        comando = datos.get("comando", "")

        if comando == "_SALUDO_INICIAL_":
            return {"nuevo_estado": {"modo": "libre"}, "mensaje_para_ui": "Guardián online. ¿Forjamos un Contrato o preparamos una Transición?"}

        palabras_clave_diseno = ["diseñar", "contrato", "forjar", "crear", "ruleta", "modo diseño"]
        palabras_clave_transicion = ["transicion", "bache", "preparar"] # <-- NUEVO

        # Activar Modo Transición
        if any(palabra in comando.lower() for palabra in palabras_clave_transicion) and estado.get("modo") != "transicion":
            nuevo_estado = {"modo": "transicion", "paso_transicion": "ESPERANDO_ACTIVIDAD_MADRE", "datos_bache": {}}
            return {"nuevo_estado": nuevo_estado, "mensaje_para_ui": "Modo Transición activado. ¿Cuál es la actividad principal para la que nos preparamos?"}
        
        # Activar Modo Diseño
        if any(palabra in comando.lower() for palabra in palabras_clave_diseno) and estado.get("modo") != "diseño":
            nuevo_estado = {"modo": "diseño", "paso_diseno": "ESPERANDO_MISION", "datos_plan": {}}
            return {"nuevo_estado": nuevo_estado, "mensaje_para_ui": "Modo Diseño activado. Define la misión."}

        # Gestionar los flujos si ya estamos en un modo
        if estado.get("modo") == "diseño":
            return self._gestionar_diseno(estado, comando)
        
        if estado.get("modo") == "transicion":
            return self._gestionar_transicion(estado, comando)

        # Si no, es una conversación normal.
        respuesta_conversacional = await self._gestionar_charla_ia(comando)
        return {"nuevo_estado": {"modo": "libre"}, "mensaje_para_ui": respuesta_conversacional}
