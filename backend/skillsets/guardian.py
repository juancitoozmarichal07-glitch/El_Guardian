# =================================================================
# GUARDIAN.PY (v10.1 - El Planificador Meticuloso)
# =================================================================
# - CORRECCIÓN: Solucionado bug en Modo Diseño que se saltaba los pasos de "Arranque" y "Duración".
# - CORRECCIÓN: Solucionado bug en Modo Transición que impedía confirmar/corregir el plan borrador.
# - MEJORA: Añadida la capacidad de encadenar la creación de múltiples contratos.

import g4f
import re
from datetime import datetime, timedelta
import pytz
import random
import string

class Guardian:
    def __init__(self):
        """
        Inicializa el especialista Guardian.
        """
        self.archivador_contratos = {}
        print(f"    - Especialista 'Guardian' v10.1 (Planificador Meticuloso) listo.")

    # --- FUNCIONES AUXILIARES ---
    def _generar_id_aleatorio(self, prefijo="PLAN"):
        caracteres = string.ascii_uppercase + string.digits
        sufijo = ''.join(random.choices(caracteres, k=4))
        return f"{prefijo}-{sufijo}"

    def _redondear_minutos(self, dt, direccion='siguiente', intervalo=5):
        minutos_descartados = dt.minute % intervalo
        if direccion == 'siguiente':
            if minutos_descartados > 0:
                minutos_a_sumar = intervalo - minutos_descartados
                return dt + timedelta(minutes=minutos_a_sumar)
            return dt
        elif direccion == 'anterior':
            return dt - timedelta(minutes=minutos_descartados)
        return dt

    def _extraer_duracion_de_tarea(self, texto_tarea):
        match = re.search(r'\((\d+)\s*min\s*\)', texto_tarea)
        if match: return int(match.group(1))
        match_num = re.search(r'\((\d+)\)', texto_tarea)
        if match_num: return int(match_num.group(1))
        return 0

    def _calendarizar_plan(self, plan_generado, zona_horaria):
        if not plan_generado: return [], 0
        itinerario_final, minutos_descanso_totales = [], 0
        
        hora_actual_exacta = datetime.now(zona_horaria)
        hora_inicio_redondeada = self._redondear_minutos(hora_actual_exacta, 'siguiente', 5)
        
        respiro_inicial = random.randint(5, 10)
        respiro_inicial_redondeado = 5 * round(respiro_inicial / 5)
        
        proxima_hora_inicio = hora_inicio_redondeada + timedelta(minutes=respiro_inicial_redondeado)
        
        itinerario_final.append(f"**(Respiro inicial de {respiro_inicial_redondeado} minutos)**")

        for i, tarea_texto in enumerate(plan_generado):
            duracion_minutos = self._extraer_duracion_de_tarea(tarea_texto)
            if duracion_minutos == 0: continue
            
            hora_fin = proxima_hora_inicio + timedelta(minutes=duracion_minutos)
            
            texto_itinerario = f"{proxima_hora_inicio.strftime('%H:%M')} - {hora_fin.strftime('%H:%M')}: {tarea_texto}"
            itinerario_final.append(texto_itinerario)
            
            proxima_hora_inicio = hora_fin
            
            if i < len(plan_generado) - 1:
                descanso_minutos = random.randint(5, 10)
                descanso_redondeado = 5 * round(descanso_minutos / 5)
                minutos_descanso_totales += descanso_redondeado
                itinerario_final.append(f"*(Descanso de {descanso_redondeado} minutos)*")
                proxima_hora_inicio += timedelta(minutes=descanso_redondeado)
                
        return itinerario_final, minutos_descanso_totales

    def _crear_plan_de_transicion(self, tareas, bache_utilizable):
        if not tareas: return []
        
        tareas = tareas[:5]

        if bache_utilizable < len(tareas) * 20:
            if not tareas: return []
            tarea_unica = random.choice(tareas)
            duracion = min(bache_utilizable, 45)
            duracion = 5 * round(duracion / 5)
            if duracion < 20: return []
            return [f"{tarea_unica} ({duracion} min)"]

        plan_final, tiempo_restante = [], bache_utilizable
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
            tarea_nombre = re.sub(r'\s*\(\d+\s*min\s*\)', '', parte).strip()
            tarea_nombre = re.sub(r'\s*\(\d+\)', '', tarea_nombre).strip()
            if duracion > 0:
                tareas_con_duracion.append(f"{tarea_nombre} ({duracion} min)")
                tiempo_comprometido += duracion
            else:
                tareas_sin_duracion.append(tarea_nombre)
        
        bache_para_flexibles = bache_utilizable - tiempo_comprometido
        plan_flexible = self._crear_plan_de_transicion(tareas_sin_duracion, bache_para_flexibles)
        
        plan_final = tareas_con_duracion + plan_flexible
        random.shuffle(plan_final)
        return plan_final

    # --- FUNCIONES DEL MODO DISEÑO ---
    def _forjar_contrato(self, datos_plan):
        zona_horaria_usuario = pytz.timezone("America/Montevideo")
        ahora = datetime.now(zona_horaria_usuario)
        fecha_sellado = ahora.strftime("%d/%m/%y")
        hora_sellado = ahora.strftime("%H:%M")
        
        mision_base = datos_plan.get('mision', 'N/A')
        especificaciones = datos_plan.get('especificaciones', [])
        mision_completa = f"{mision_base} -> {' -> '.join(especificaciones)}" if especificaciones else mision_base
        
        identificador = self._generar_id_aleatorio("CONT")
        
        contrato_obj = {
            "tipo": "Contrato",
            "mision": mision_completa,
            "arranque": datos_plan.get('arranque', 'N/A'),
            "duracion": datos_plan.get('duracion', 'N/A'),
            "fecha_sellado": fecha_sellado,
            "hora_sellado": hora_sellado,
            "id": identificador
        }
        self.archivador_contratos[identificador] = contrato_obj

        contrato_texto = (
            f"**CONTRATO FORJADO**\n--------------------\n"
            f"**Misión:** {mision_completa}\n"
            f"**Arranque:** {contrato_obj['arranque']}\n"
            f"**Duración:** {contrato_obj['duracion']}\n"
            f"**Sellado:** {fecha_sellado} a las {hora_sellado}\n"
            f"**Identificador:** {identificador}\n--------------------\n"
            f"Contrato sellado. ¿Deseas forjar otro contrato? (sí/no)"
        )
        
        nuevo_estado = {"modo": "diseño", "paso_diseno": "ESPERANDO_ENCADENAR", "datos_plan": {}}
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
            if datos_plan.get("corrigiendo_con_ruleta"):
                datos_plan.pop("corrigiendo_con_ruleta", None)
                datos_plan.pop("campo_en_edicion", None)
                datos_plan["mision"] = comando
                return self._presentar_borrador_contrato(datos_plan)
            
            datos_plan["mision"] = comando
            nuevo_estado = {"modo": "diseño", "paso_diseno": "ESPERANDO_ESPECIFICACION", "datos_plan": datos_plan}
            return {"nuevo_estado": nuevo_estado, "mensaje_para_ui": f"Misión elegida: **{comando}**. ¿Necesitas especificar más? (sí/no)"}
        
        # --- SECCIÓN CORREGIDA ---
        elif paso == "ESPERANDO_ESPECIFICACION":
            if "si" in comando.lower():
                nuevo_estado = {"modo": "diseño", "paso_diseno": "ESPERANDO_OPCIONES_ESPECIFICACION", "datos_plan": datos_plan}
                return {"nuevo_estado": nuevo_estado, "mensaje_para_ui": "Entendido. Dame las opciones para la siguiente capa."}
            else:
                # CORRECCIÓN: Avanza al siguiente paso en lugar de forjar el contrato prematuramente.
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
            if datos_plan.get("corrigiendo_con_ruleta"):
                datos_plan.pop("corrigiendo_con_ruleta", None)
                datos_plan.pop("campo_en_edicion", None)
                datos_plan["arranque"] = comando
                return self._presentar_borrador_contrato(datos_plan)

            datos_plan["arranque"] = comando
            nuevo_estado = {"modo": "diseño", "paso_diseno": "ESPERANDO_DECISION_DURACION", "datos_plan": datos_plan}
            return {"nuevo_estado": nuevo_estado, "mensaje_para_ui": f"Arranque: **{comando}**. ¿Necesitas definir una duración? (sí/no)"}
            
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
            if datos_plan.get("corrigiendo_con_ruleta"):
                datos_plan.pop("corrigiendo_con_ruleta", None)
                datos_plan.pop("campo_en_edicion", None)
                datos_plan["duracion"] = comando
                return self._presentar_borrador_contrato(datos_plan)

            datos_plan["duracion"] = comando
            return self._forjar_contrato(datos_plan)

        elif paso == "ESPERANDO_ENCADENAR":
            if "si" in comando.lower():
                nuevo_estado = {"modo": "diseño", "paso_diseno": "ESPERANDO_MISION", "datos_plan": {}}
                return {"nuevo_estado": nuevo_estado, "mensaje_para_ui": "Perfecto. Define la misión para el nuevo contrato."}
            else:
                return {"nuevo_estado": {"modo": "libre"}, "mensaje_para_ui": "Entendido. Guardián en espera."}
            
        return {"nuevo_estado": {"modo": "libre"}, "mensaje_para_ui": "Error en el flujo de diseño. Reiniciando."}
    # --- MODO TRANSICIÓN (v4.0 - CON CICLO DE CORRECCIÓN Y BUGFIX) ---
    def _presentar_borrador_transicion(self, datos_bache):
        plan_borrador = datos_bache.get("plan_borrador", [])
        if not plan_borrador:
            return {"nuevo_estado": {"modo": "libre"}, "mensaje_para_ui": "No se pudo generar un plan viable con el tiempo disponible. Reiniciando."}
        
        plan_texto_lista = [f"{i+1}. {tarea}" for i, tarea in enumerate(plan_borrador)]
        plan_texto = "\n".join(plan_texto_lista)

        mensaje = (f"He generado el siguiente plan borrador:\n\n{plan_texto}\n\n"
                   f"**¿Confirmas este plan o quieres corregir algo?** (confirmar/corregir)")
        
        nuevo_estado = {"modo": "transicion", "paso_transicion": "ESPERANDO_CONFIRMACION_PLAN", "datos_bache": datos_bache}
        return {"nuevo_estado": nuevo_estado, "mensaje_para_ui": mensaje}

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
                
                respiro_final = random.randint(5, 10)
                bache_utilizable = bache_total_minutos - respiro_final

                if bache_utilizable < 20:
                    return {"nuevo_estado": {"modo": "libre"}, "mensaje_para_ui": f"El bache de solo {bache_total_minutos} min es demasiado corto (necesario al menos 20 min + respiro final)."}
                
                datos_bache["bache_utilizable_minutos"] = bache_utilizable
                datos_bache["respiro_final_minutos"] = respiro_final
                horas, minutos = divmod(bache_utilizable, 60)
                mensaje = (f"Detectado un bache utilizable de **{horas}h y {minutos}min** (reservando {respiro_final} min de respiro al final).\n\n"
                           f"Ahora, dime las tareas que quieres hacer (máximo 5), separadas por comas.")
                nuevo_estado = {"modo": "transicion", "paso_transicion": "ESPERANDO_TAREAS_OBJETIVO", "datos_bache": datos_bache}
                return {"nuevo_estado": nuevo_estado, "mensaje_para_ui": mensaje}
            except Exception as e:
                print(f"🚨 Error inesperado en _gestionar_transicion (HORA_INICIO_MADRE): {e}")
                return {"nuevo_estado": {"modo": "libre"}, "mensaje_para_ui": "Formato de hora no válido. Usa HH:MM (ej: 23:50). Reiniciando."}

        elif paso == "ESPERANDO_TAREAS_OBJETIVO":
            bache_utilizable = datos_bache.get("bache_utilizable_minutos", 0)
            plan_generado = self._procesar_plan_mixto(comando, bache_utilizable)
            datos_bache["plan_borrador"] = plan_generado
            return self._presentar_borrador_transicion(datos_bache)

        # --- SECCIÓN CORREGIDA ---
        elif paso == "ESPERANDO_CONFIRMACION_PLAN":
            comando_lower = comando.lower()
            if "confirmar" in comando_lower:
                plan_final = datos_bache.get("plan_borrador", [])
                itinerario_agendado, total_descansos = self._calendarizar_plan(plan_final, zona_horaria_usuario)
                
                identificador = self._generar_id_aleatorio("BACHE")
                ahora = datetime.now(zona_horaria_usuario)
                
                plan_texto = "\n".join([f"**-** {linea}" for linea in itinerario_agendado])
                tiempo_total_planificado = sum(self._extraer_duracion_de_tarea(t) for t in plan_final)
                
                mensaje_final = (
                    f"**PLAN DE TRANSICIÓN AGENDADO**\n--------------------\n"
                    f"Itinerario para tu bache:\n\n{plan_texto}\n\n"
                    f"**Actividades planificadas:** {len(plan_final)}\n"
                    f"**Tiempo total planificado:** {tiempo_total_planificado} min\n"
                    f"**Itinerario sellado:** {ahora.strftime('%d/%m/%y a las %H:%M')}\n"
                    f"**Identificador:** {identificador}\n--------------------\n"
                    f"¡Itinerario sellado!"
                )
                self.archivador_contratos[identificador] = {"tipo": "Bache", "id": identificador, "itinerario": itinerario_agendado}
                return {"nuevo_estado": {"modo": "libre"}, "mensaje_para_ui": mensaje_final}

            elif "corregir" in comando_lower:
                nuevo_estado = {"modo": "transicion", "paso_transicion": "ESPERANDO_CATEGORIA_CORRECCION", "datos_bache": datos_bache}
                return {"nuevo_estado": nuevo_estado, "mensaje_para_ui": "Entendido. ¿Qué categoría quieres corregir? **(Tareas / Duraciones)**"}
            
            else:
                return {"nuevo_estado": estado_actual, "mensaje_para_ui": "No te he entendido. Por favor, responde 'confirmar' o 'corregir'."}

        elif paso == "ESPERANDO_CATEGORIA_CORRECCION":
            if "tareas" in comando.lower():
                nuevo_estado = {"modo": "transicion", "paso_transicion": "ESPERANDO_CORRECCION_TAREAS", "datos_bache": datos_bache}
                plan_actual_texto = "\n".join([f"{i+1}. {t}" for i, t in enumerate(datos_bache.get("plan_borrador", []))])
                mensaje = f"De acuerdo. Este es el plan actual:\n\n{plan_actual_texto}\n\nDime el número de la tarea a cambiar y el nuevo nombre.\n*Ej: 1 Jugar, 3 Dibujar*"
                return {"nuevo_estado": nuevo_estado, "mensaje_para_ui": mensaje}
            elif "duraciones" in comando.lower():
                nuevo_estado = {"modo": "transicion", "paso_transicion": "ESPERANDO_CORRECCION_DURACIONES", "datos_bache": datos_bache}
                plan_actual_texto = "\n".join([f"{i+1}. {t}" for i, t in enumerate(datos_bache.get("plan_borrador", []))])
                mensaje = f"De acuerdo. Este es el plan actual:\n\n{plan_actual_texto}\n\nDime el número de la tarea y la nueva duración. Si no pones duración, la elegiré yo.\n*Ej: 1: 25, 3, 4 (35)*"
                return {"nuevo_estado": nuevo_estado, "mensaje_para_ui": mensaje}
            else:
                return {"nuevo_estado": estado_actual, "mensaje_para_ui": "Categoría no válida. Elige 'Tareas' o 'Duraciones'."}

        elif paso == "ESPERANDO_CORRECCION_TAREAS":
            plan_actual = datos_bache.get("plan_borrador", [])
            cambios = [c.strip() for c in comando.split(',') if c.strip()]
            for cambio in cambios:
                match = re.match(r'(\d+)\s*(?::\s*|\s+)(.+)', cambio)
                if match:
                    idx = int(match.group(1)) - 1
                    nuevo_nombre = match.group(2).strip()
                    if 0 <= idx < len(plan_actual):
                        duracion_actual = self._extraer_duracion_de_tarea(plan_actual[idx])
                        plan_actual[idx] = f"{nuevo_nombre} ({duracion_actual} min)"
            datos_bache["plan_borrador"] = plan_actual
            return self._presentar_borrador_transicion(datos_bache)

        elif paso == "ESPERANDO_CORRECCION_DURACIONES":
            plan_actual = list(datos_bache.get("plan_borrador", []))
            bache_utilizable = datos_bache.get("bache_utilizable_minutos", 0)
            
            tareas_modificadas = list(plan_actual)
            indices_para_reasignar = []
            partes_comando = [p.strip() for p in comando.split(',') if p.strip()]

            for parte in partes_comando:
                match_con_valor = re.match(r'(\d+)\s*[:\s(]+(\d+)\)?', parte)
                match_sin_valor = re.match(r'(\d+)\s*$', parte)
                idx = -1
                if match_con_valor:
                    idx = int(match_con_valor.group(1)) - 1
                    nueva_duracion = int(match_con_valor.group(2))
                    if 0 <= idx < len(tareas_modificadas):
                        nombre_tarea = re.sub(r'\s*\(\d+.*\)', '', tareas_modificadas[idx]).strip()
                        tareas_modificadas[idx] = f"{nombre_tarea} ({nueva_duracion} min)"
                elif match_sin_valor:
                    idx = int(match_sin_valor.group(1)) - 1
                    if 0 <= idx < len(tareas_modificadas):
                        indices_para_reasignar.append(idx)

            tareas_fijas = [t for i, t in enumerate(tareas_modificadas) if i not in indices_para_reasignar]
            tareas_flexibles_nombres = [re.sub(r'\s*\(\d+.*\)', '', tareas_modificadas[i]).strip() for i in indices_para_reasignar]
            
            tiempo_comprometido = sum(self._extraer_duracion_de_tarea(t) for t in tareas_fijas)
            bache_restante = bache_utilizable - tiempo_comprometido
            
            plan_flexible_nuevo = self._crear_plan_de_transicion(tareas_flexibles_nombres, bache_restante)
            
            plan_final = tareas_fijas + plan_flexible_nuevo
            datos_bache["plan_borrador"] = plan_final
            return self._presentar_borrador_transicion(datos_bache)

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
        comando_lower = comando.lower()

        if comando == "_SALUDO_INICIAL_":
            return {"nuevo_estado": {"modo": "libre"}, "mensaje_para_ui": "Guardián online. ¿Forjamos un Contrato o negociamos una Transición?"}

        palabras_clave_diseno = ["diseñar", "contrato", "forjar", "crear", "ruleta", "modo diseño"]
        palabras_clave_transicion = ["transicion", "bache", "preparar", "plan", "agendar", "negociar"]
        
        if any(palabra in comando_lower for palabra in palabras_clave_transicion) and estado.get("modo") != "transicion":
            nuevo_estado = {"modo": "transicion", "paso_transicion": "ESPERANDO_ACTIVIDAD_MADRE", "datos_bache": {}}
            return {"nuevo_estado": nuevo_estado, "mensaje_para_ui": "Modo Transición activado. ¿Cuál es la actividad principal que harás después?"}

        if any(palabra in comando_lower for palabra in palabras_clave_diseno) and estado.get("modo") != "diseño":
            match_id = re.search(r'([A-Z]{4,5}-[A-Z0-9]{4})', comando, re.IGNORECASE)
            if match_id:
                contrato_id = match_id.group(1).upper()
                contrato = self.archivador_contratos.get(contrato_id)
                if contrato:
                    contrato_texto = (
                        f"**CONTRATO RECUPERADO**\n--------------------\n"
                        f"**Misión:** {contrato['mision']}\n"
                        f"**Arranque:** {contrato['arranque']}\n"
                        f"**Duración:** {contrato['duracion']}\n"
                        f"**Sellado:** {contrato['fecha_sellado']} a las {contrato['hora_sellado']}\n"
                        f"**Identificador:** {contrato['id']}\n--------------------"
                    )
                    return {"nuevo_estado": {"modo": "libre"}, "mensaje_para_ui": contrato_texto}
                else:
                    return {"nuevo_estado": {"modo": "libre"}, "mensaje_para_ui": f"No se encontró ningún contrato con el identificador {contrato_id}."}

            nuevo_estado = {"modo": "diseño", "paso_diseno": "ESPERANDO_MISION", "datos_plan": {}}
            return {"nuevo_estado": nuevo_estado, "mensaje_para_ui": "Modo Diseño activado. Define la misión."}

        if estado.get("modo") == "diseño":
            return self._gestionar_diseno(estado, comando)
        
        if estado.get("modo") == "transicion":
            return self._gestionar_transicion(estado, comando)

        respuesta_conversacional = await self._gestionar_charla_ia(comando)
        return {"nuevo_estado": {"modo": "libre"}, "mensaje_para_ui": respuesta_conversacional}

