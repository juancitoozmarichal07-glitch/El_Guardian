# =================================================================
# GUARDIAN.PY (v3.6 - El Maestro de Contratos)
# =================================================================
# Esta es la versión definitiva que unifica todas las mejoras:
# - Modo Diseño con ciclo de corrección de campos.
# - Modo Transición con negociación de planes.
# - Calendarización automática de itinerarios.

import g4f
import re
from datetime import datetime, timedelta
import pytz
import random

class Guardian:
    def __init__(self):
        """
        Inicializa el especialista Guardian.
        """
        print(f"    - Especialista 'Guardian' v3.6 (Maestro de Contratos) listo.")

    # --- FUNCIONES AUXILIARES ---
    def _extraer_duracion_de_tarea(self, texto_tarea):
        match = re.search(r'\((\d+)\s*min\s*\)', texto_tarea)
        if match: return int(match.group(1))
        match_num = re.search(r'\((\d+)\)', texto_tarea)
        if match_num: return int(match_num.group(1))
        return 0

    def _calendarizar_plan(self, plan_generado, zona_horaria):
        if not plan_generado: return [], 0
        itinerario_final = []
        minutos_descanso_totales = 0
        hora_actual = datetime.now(zona_horaria)
        proxima_hora_inicio = hora_actual
        for i, tarea_texto in enumerate(plan_generado):
            duracion_minutos = self._extraer_duracion_de_tarea(tarea_texto)
            if duracion_minutos == 0: continue
            hora_fin = proxima_hora_inicio + timedelta(minutes=duracion_minutos)
            texto_itinerario = f"{proxima_hora_inicio.strftime('%H:%M')} - {hora_fin.strftime('%H:%M')}: {tarea_texto}"
            itinerario_final.append(texto_itinerario)
            if i < len(plan_generado) - 1:
                descanso_minutos = random.randint(5, 10)
                minutos_descanso_totales += descanso_minutos
                itinerario_final.append(f"*(Descanso de {descanso_minutos} minutos)*")
                proxima_hora_inicio = hora_fin + timedelta(minutes=descanso_minutos)
        return itinerario_final, minutos_descanso_totales

    def _crear_plan_de_transicion(self, tareas, bache_utilizable):
        if not tareas: return []
        if bache_utilizable < len(tareas) * 20:
            tarea_unica = random.choice(tareas)
            duracion = min(bache_utilizable, 45)
            duracion = 5 * round(duracion / 5)
            if duracion < 20: return []
            return [f"{tarea_unica} ({duracion} min)"]
        plan_final = []
        tiempo_restante = bache_utilizable
        random.shuffle(tareas)
        bloques_de_tiempo = [20, 25, 30, 35, 40, 45]
        for tarea in tareas:
            if tiempo_restante < 20: break
            bloques_posibles = [b for b in bloques_de_tiempo if b <= tiempo_restante]
            if not bloques_posibles: continue
            duracion_asignada = random.choice(bloques_posibles)
            plan_final.append(f"{tarea} ({duracion_asignada} min)")
            tiempo_restante -= duracion_asignada
        return plan_final

    def _procesar_plan_mixto(self, comando_usuario, bache_utilizable):
        tareas_con_duracion, tareas_sin_duracion, tiempo_comprometido = [], [], 0
        partes = [p.strip() for p in comando_usuario.split(',') if p.strip()]
        for parte in partes:
            duracion = self._extraer_duracion_de_tarea(parte)
            if duracion > 0:
                tarea_nombre = re.sub(r'\s*\(\d+\s*min\s*\)', '', parte).strip()
                tareas_con_duracion.append(f"{tarea_nombre} ({duracion} min)")
                tiempo_comprometido += duracion
            else:
                tareas_sin_duracion.append(parte)
        bache_para_flexibles = bache_utilizable - tiempo_comprometido
        plan_flexible = self._crear_plan_de_transicion(tareas_sin_duracion, bache_para_flexibles)
        plan_final = tareas_con_duracion + plan_flexible
        random.shuffle(plan_final)
        return plan_final

    # --- FUNCIONES DEL MODO DISEÑO ---
    def _presentar_borrador_contrato(self, datos_plan):
        mision_base = datos_plan.get('mision', 'N/A')
        especificaciones = datos_plan.get('especificaciones', [])
        mision_completa = f"{mision_base} -> {' -> '.join(especificaciones)}" if especificaciones else mision_base
        contrato_borrador_texto = (
            f"**CONTRATO BORRADOR**\n--------------------\n"
            f"**Misión:** {mision_completa}\n"
            f"**Arranque:** {datos_plan.get('arranque', 'N/A')}\n"
            f"**Duración:** {datos_plan.get('duracion', 'N/A')}\n--------------------\n"
            f"¿Confirmas este contrato o quieres corregir algo? (confirmar/corregir)"
        )
        nuevo_estado = {"modo": "diseño", "paso_diseno": "ESPERANDO_CONFIRMACION_CONTRATO", "datos_plan": datos_plan}
        return {"nuevo_estado": nuevo_estado, "mensaje_para_ui": contrato_borrador_texto}

    def _forjar_contrato(self, datos_plan):
        zona_horaria_usuario = pytz.timezone("America/Montevideo")
        ahora = datetime.now(zona_horaria_usuario)
        hora_sellado = ahora.strftime("%H:%M")
        mision_base = datos_plan.get('mision', 'N/A')
        especificaciones = datos_plan.get('especificaciones', [])
        mision_completa = f"{mision_base} -> {' -> '.join(especificaciones)}" if especificaciones else mision_base
        contrato_texto = (
            f"**CONTRATO FORJADO**\n--------------------\n"
            f"**Misión:** {mision_completa}\n"
            f"**Arranque:** {datos_plan.get('arranque', 'N/A')}\n"
            f"**Duración:** {datos_plan.get('duracion', 'N/A')}\n"
            f"**Sellado a las:** {hora_sellado}\n--------------------\n"
            f"Contrato sellado. ¿Siguiente misión?"
        )
        nuevo_estado = {"modo": "libre"}
        return {"nuevo_estado": nuevo_estado, "mensaje_para_ui": contrato_texto}

    def _gestionar_diseno(self, estado_actual, comando):
        paso = estado_actual.get("paso_diseno")
        datos_plan = estado_actual.get("datos_plan", {})
        
        if paso == "ESPERANDO_MISION":
            opciones = [opt.strip() for opt in comando.split(',') if opt.strip()]
            if not opciones: return {"nuevo_estado": estado_actual, "mensaje_para_ui": "Define la misión."}
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
        
        elif paso == "ESPERANDO_ESPECIFICACION":
            if "si" in comando.lower():
                nuevo_estado = {"modo": "diseño", "paso_diseno": "ESPERANDO_OPCIONES_ESPECIFICACION", "datos_plan": datos_plan}
                return {"nuevo_estado": nuevo_estado, "mensaje_para_ui": "Entendido. Dame las opciones para la siguiente capa."}
            else:
                nuevo_estado = {"modo": "diseño", "paso_diseno": "ESPERANDO_ARRANQUE", "datos_plan": datos_plan}
                return {"nuevo_estado": nuevo_estado, "mensaje_para_ui": "Misión definida. Ahora, define el **momento de arranque**."}
                
        elif paso == "ESPERANDO_OPCIONES_ESPECIFICACION":
            opciones = [opt.strip() for opt in comando.split(',') if opt.strip()]
            if not opciones: return {"nuevo_estado": estado_actual, "mensaje_para_ui": "Define las opciones."}
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
            
        elif paso == "ESPERANDO_DECISION_DURACION":
            if "si" in comando.lower():
                nuevo_estado = {"modo": "diseño", "paso_diseno": "ESPERANDO_DURACION", "datos_plan": datos_plan}
                return {"nuevo_estado": nuevo_estado, "mensaje_para_ui": "Entendido. Dime las opciones para la duración."}
            else:
                datos_plan["duracion"] = "No definida"
                return self._presentar_borrador_contrato(datos_plan)
                
        elif paso == "ESPERANDO_DURACION":
            opciones = [opt.strip() for opt in comando.split(',') if opt.strip()]
            if not opciones: return {"nuevo_estado": estado_actual, "mensaje_para_ui": "Define la duración."}
            if len(opciones) == 1:
                datos_plan["duracion"] = opciones[0]
                return self._presentar_borrador_contrato(datos_plan)
            else:
                estado_actual["paso_diseno"] = "ESPERANDO_RESULTADO_DURACION"
                return {"nuevo_estado": estado_actual, "accion_ui": "MOSTRAR_RULETA", "opciones_ruleta": opciones}
                
        elif paso == "ESPERANDO_RESULTADO_DURACION":
            datos_plan["duracion"] = comando
            return self._presentar_borrador_contrato(datos_plan)

        elif paso == "ESPERANDO_CONFIRMACION_CONTRATO":
            if "confirmar" in comando.lower():
                return self._forjar_contrato(datos_plan)
            elif "corregir" in comando.lower():
                nuevo_estado = {"modo": "diseño", "paso_diseno": "ESPERANDO_CAMPO_A_CORREGIR", "datos_plan": datos_plan}
                mensaje = "Entendido. ¿Qué campo quieres corregir? (misión / arranque / duración)"
                return {"nuevo_estado": nuevo_estado, "mensaje_para_ui": mensaje}
            else:
                return {"nuevo_estado": estado_actual, "mensaje_para_ui": "No te he entendido. Por favor, responde 'confirmar' o 'corregir'."}

        elif paso == "ESPERANDO_CAMPO_A_CORREGIR":
            campo_a_corregir = comando.lower()
            if campo_a_corregir in ["misión", "arranque", "duración"]:
                datos_plan["campo_en_edicion"] = campo_a_corregir
                nuevo_estado = {"modo": "diseño", "paso_diseno": "ESPERANDO_NUEVO_VALOR", "datos_plan": datos_plan}
                mensaje = f"De acuerdo. ¿Cuál es el nuevo valor para '{campo_a_corregir}'?"
                return {"nuevo_estado": nuevo_estado, "mensaje_para_ui": mensaje}
            else:
                return {"nuevo_estado": estado_actual, "mensaje_para_ui": "Campo no válido. Por favor, elige entre 'misión', 'arranque' o 'duración'."}

        elif paso == "ESPERANDO_NUEVO_VALOR":
            campo_en_edicion = datos_plan.pop("campo_en_edicion", None)
            if campo_en_edicion:
                if campo_en_edicion == "misión":
                    datos_plan["mision"] = comando
                    datos_plan.pop("especificaciones", None)
                else:
                    datos_plan[campo_en_edicion] = comando
                return self._presentar_borrador_contrato(datos_plan)
            else:
                return {"nuevo_estado": {"modo": "libre"}, "mensaje_para_ui": "Hubo un error en la corrección. Reiniciando."}
            
        return {"nuevo_estado": {"modo": "libre"}, "mensaje_para_ui": "Error en el flujo de diseño. Reiniciando."}

    # --- MODO TRANSICIÓN ---
    def _gestionar_transicion(self, estado_actual, comando):
        paso = estado_actual.get("paso_transicion")
        datos_bache = estado_actual.get("datos_bache", {})
        zona_horaria_usuario = pytz.timezone("America/Montevideo")

        if paso == "ESPERANDO_ACTIVIDAD_MADRE":
            datos_bache["actividad_madre"] = comando
            nuevo_estado = {"modo": "transicion", "paso_transicion": "ESPERANDO_HORA_INICIO_MADRE", "datos_bache": datos_bache}
            return {"nuevo_estado": nuevo_estado, "mensaje_para_ui": f"Entendido: **{comando}**. ¿A qué hora comienza?"}

        elif paso == "ESPERANDO_HORA_INICIO_MADRE":
            try:
                ahora = datetime.now(zona_horaria_usuario)
                hora_inicio_madre = datetime.strptime(comando, "%H:%M").time()
                fecha_inicio_madre = ahora.replace(hour=hora_inicio_madre.hour, minute=hora_inicio_madre.minute, second=0, microsecond=0)
                if fecha_inicio_madre < ahora:
                    fecha_inicio_madre += timedelta(days=1)
                bache_total_minutos = int((fecha_inicio_madre - ahora).total_seconds() / 60)
                if bache_total_minutos <= 20:
                    return {"nuevo_estado": {"modo": "libre"}, "mensaje_para_ui": f"El bache de solo {bache_total_minutos} minutos es demasiado corto para activar el Modo Transición."}
                colchon_seguridad = random.randint(10, 20)
                bache_utilizable = bache_total_minutos - colchon_seguridad
                if bache_utilizable < 20:
                    return {"nuevo_estado": {"modo": "libre"}, "mensaje_para_ui": f"Tras restar el colchón de seguridad de {colchon_seguridad} min, el tiempo restante es insuficiente. Reiniciando."}
                datos_bache["bache_utilizable_minutos"] = bache_utilizable
                horas, minutos = divmod(bache_utilizable, 60)
                mensaje = f"Detectado un bache utilizable de **{horas}h y {minutos}min** (con {colchon_seguridad} min de colchón).\n\nAhora, dime las tareas que quieres hacer, separadas por comas."
                nuevo_estado = {"modo": "transicion", "paso_transicion": "ESPERANDO_TAREAS_OBJETIVO", "datos_bache": datos_bache}
                return {"nuevo_estado": nuevo_estado, "mensaje_para_ui": mensaje}
            except Exception as e:
                print(f"🚨 Error inesperado en _gestionar_transicion: {e}")
                return {"nuevo_estado": {"modo": "libre"}, "mensaje_para_ui": "Ocurrió un error inesperado."}

        elif paso == "ESPERANDO_TAREAS_OBJETIVO":
            tareas_objetivo = [tarea.strip() for tarea in comando.split(',') if tarea.strip()]
            if not tareas_objetivo:
                return {"nuevo_estado": estado_actual, "mensaje_para_ui": "Necesito al menos una tarea objetivo."}
            bache_utilizable = datos_bache.get("bache_utilizable_minutos", 0)
            plan_generado = self._crear_plan_de_transicion(tareas_objetivo, bache_utilizable)
            if not plan_generado:
                return {"nuevo_estado": {"modo": "libre"}, "mensaje_para_ui": "No se pudo generar un plan viable con el tiempo disponible. Intenta con menos tareas o un bache más grande."}
            datos_bache["plan_borrador"] = plan_generado
            plan_texto = "\n".join([f"- {tarea}" for tarea in plan_generado])
            mensaje = (f"He generado el siguiente plan borrador:\n\n{plan_texto}\n\n"
                       f"**¿Aceptas este plan o quieres modificarlo?** (aceptar/modificar)")
            nuevo_estado = {"modo": "transicion", "paso_transicion": "ESPERANDO_CONFIRMACION_PLAN", "datos_bache": datos_bache}
            return {"nuevo_estado": nuevo_estado, "mensaje_para_ui": mensaje}

        elif paso == "ESPERANDO_CONFIRMACION_PLAN":
            plan_final = []
            if "aceptar" in comando.lower():
                plan_final = datos_bache.get("plan_borrador", [])
            elif "modificar" in comando.lower():
                nuevo_estado = {"modo": "transicion", "paso_transicion": "ESPERANDO_PLAN_MODIFICADO", "datos_bache": datos_bache}
                mensaje = ("Entendido. Por favor, define tú mismo las tareas. Si quieres una duración específica, ponla entre paréntesis.\n\n"
                           "*Ejemplo: Leer la Biblia (15 min), Jugar, Agradecer (5 min)*")
                return {"nuevo_estado": nuevo_estado, "mensaje_para_ui": mensaje}
            else:
                return {"nuevo_estado": estado_actual, "mensaje_para_ui": "No te he entendido. Por favor, responde 'aceptar' o 'modificar'."}
            
            itinerario_agendado, total_descansos = self._calendarizar_plan(plan_final, zona_horaria_usuario)
            plan_texto = "\n".join([f"**-** {linea}" for linea in itinerario_agendado])
            tiempo_total_planificado = sum(self._extraer_duracion_de_tarea(t) for t in plan_final)
            tiempo_total_usado = tiempo_total_planificado + total_descansos
            tiempo_libre_restante = datos_bache.get("bache_utilizable_minutos", 0) - tiempo_total_usado
            mensaje_final = (f"**PLAN DE TRANSICIÓN AGENDADO**\n--------------------\n"
                             f"He preparado el siguiente itinerario para tu bache de tiempo:\n\n{plan_texto}\n\n"
                             f"**Tiempo total planificado:** {tiempo_total_planificado} minutos de trabajo.\n"
                             f"**Tiempo libre no asignado:** {tiempo_libre_restante} minutos.\n--------------------\n"
                             f"¡Itinerario sellado! Puedes registrar estas tareas en tu app.")
            return {"nuevo_estado": {"modo": "libre"}, "mensaje_para_ui": mensaje_final}

        elif paso == "ESPERANDO_PLAN_MODIFICADO":
            bache_utilizable = datos_bache.get("bache_utilizable_minutos", 0)
            plan_final = self._procesar_plan_mixto(comando, bache_utilizable)
            if not plan_final:
                 return {"nuevo_estado": {"modo": "libre"}, "mensaje_para_ui": "No se pudo generar un plan viable con las tareas y el tiempo disponible. Reiniciando."}
            itinerario_agendado, total_descansos = self._calendarizar_plan(plan_final, zona_horaria_usuario)
            plan_texto = "\n".join([f"**-** {linea}" for linea in itinerario_agendado])
            tiempo_total_planificado = sum(self._extraer_duracion_de_tarea(t) for t in plan_final)
            tiempo_total_usado = tiempo_total_planificado + total_descansos
            tiempo_libre_restante = bache_utilizable - tiempo_total_usado
            mensaje_final = (f"**PLAN DE TRANSICIÓN AGENDADO**\n--------------------\n"
                             f"He preparado el siguiente itinerario basado en tu plan manual:\n\n{plan_texto}\n\n"
                             f"**Tiempo total planificado:** {tiempo_total_planificado} minutos de trabajo.\n"
                             f"**Tiempo libre no asignado:** {tiempo_libre_restante} minutos.\n--------------------\n"
                             f"¡Itinerario sellado! Puedes registrar estas tareas en tu app.")
            return {"nuevo_estado": {"modo": "libre"}, "mensaje_para_ui": mensaje_final}

        return {"nuevo_estado": {"modo": "libre"}, "mensaje_para_ui": "Error en el flujo de transición. Reiniciando."}

    # --- CHARLA Y EJECUCIÓN ---
    async def _gestionar_charla_ia(self, comando):
        try:
            prompt = f"Eres el Guardián, una IA compañera de Juan. Eres directo, sabio y motivador. El usuario dice: '{comando}'"
            respuesta_ia = await g4f.ChatCompletion.create_async(model=g4f.models.default, messages=[{"role": "user", "content": prompt}])
            return respuesta_ia or "No he podido procesar eso. Intenta de nuevo."
        except Exception as e:
            print(f"🚨 Error en la llamada a g4f: {e}")
            return "Mi núcleo cognitivo tuvo una sobrecarga. Inténtalo de nuevo."

    async def ejecutar(self, datos):
        estado = datos.get("estado_conversacion", {"modo": "libre"})
        comando = datos.get("comando", "")

        if comando == "_SALUDO_INICIAL_":
            return {"nuevo_estado": {"modo": "libre"}, "mensaje_para_ui": "Guardián online. ¿Forjamos un Contrato o negociamos una Transición?"}

        palabras_clave_diseno = ["diseñar", "contrato", "forjar", "crear", "ruleta", "modo diseño", "corregir contrato"]
        palabras_clave_transicion = ["transicion", "bache", "preparar", "plan", "agendar", "negociar"]
        
        if any(palabra in comando.lower() for palabra in palabras_clave_transicion) and estado.get("modo") != "transicion":
            nuevo_estado = {"modo": "transicion", "paso_transicion": "ESPERANDO_ACTIVIDAD_MADRE", "datos_bache": {}}
            return {"nuevo_estado": nuevo_estado, "mensaje_para_ui": "Modo Transición activado. ¿Cuál es la actividad principal para la que nos preparamos?"}
        
        if any(palabra in comando.lower() for palabra in palabras_clave_diseno) and estado.get("modo") != "diseño":
            nuevo_estado = {"modo": "diseño", "paso_diseno": "ESPERANDO_MISION", "datos_plan": {}}
            return {"nuevo_estado": nuevo_estado, "mensaje_para_ui": "Modo Diseño activado. Define la misión."}

        if estado.get("modo") == "diseño":
            return self._gestionar_diseno(estado, comando)
        
        if estado.get("modo") == "transicion":
            return self._gestionar_transicion(estado, comando)

        respuesta_conversacional = await self._gestionar_charla_ia(comando)
        return {"nuevo_estado": {"modo": "libre"}, "mensaje_para_ui": respuesta_conversacional}
