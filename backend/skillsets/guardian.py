# =================================================================
# GUARDIAN.PY (v4.1 - Corrección de Bugs)
# =================================================================
# Esta versión corrige los 3 bugs principales identificados:
# 1. Las especificaciones de la misión se concatenan correctamente.
# 2. El regex para corregir duraciones es más flexible.
# 3. El cálculo del bache de tiempo es preciso y sin "colchón".

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
        print(f"    - Especialista 'Guardian' v4.1 (Bugs Corregidos) listo.")

    # --- FUNCIONES AUXILIARES ---
    def _extraer_duracion_de_tarea(self, texto_tarea):
        match = re.search(r'\((\d+)\s*min\s*\)', texto_tarea)
        if match: return int(match.group(1))
        match_num = re.search(r'\((\d+)\)', texto_tarea)
        if match_num: return int(match_num.group(1))
        return 0

    def _redondear_hora_a_5_min(self, dt):
        """Función para redondear una hora al siguiente múltiplo de 5 minutos."""
        minutos_para_sumar = (5 - dt.minute % 5) % 5
        return dt + timedelta(minutes=minutos_para_sumar)

    def _calendarizar_plan(self, plan_generado, zona_horaria):
        """
        MODIFICADO:
        - Añade un "respiro" inicial antes de la primera tarea.
        - Redondea todas las horas de inicio al siguiente múltiplo de 5 minutos.
        """
        if not plan_generado: return [], 0
        
        itinerario_final, minutos_descanso_totales = [], 0
        hora_actual = datetime.now(zona_horaria)

        # 1. Añadir respiro inicial y redondear la primera hora de inicio
        respiro_inicial = random.randint(5, 10)
        minutos_descanso_totales += respiro_inicial
        proxima_hora_inicio_bruta = hora_actual + timedelta(minutes=respiro_inicial)
        proxima_hora_inicio = self._redondear_hora_a_5_min(proxima_hora_inicio_bruta)
        
        itinerario_final.append(f"*(Respiro inicial de {respiro_inicial} minutos)*")

        for i, tarea_texto in enumerate(plan_generado):
            duracion_minutos = self._extraer_duracion_de_tarea(tarea_texto)
            if duracion_minutos == 0: continue

            # Asegurarse de que la duración también sea un múltiplo de 5
            duracion_minutos = 5 * round(duracion_minutos / 5)
            
            hora_fin = proxima_hora_inicio + timedelta(minutes=duracion_minutos)
            texto_itinerario = f"{proxima_hora_inicio.strftime('%H:%M')} - {hora_fin.strftime('%H:%M')}: {tarea_texto}"
            itinerario_final.append(texto_itinerario)
            
            # Si no es la última tarea, añadir descanso y calcular la siguiente hora de inicio
            if i < len(plan_generado) - 1:
                descanso_minutos = random.choice([5, 10]) # Descansos fijos de 5 o 10
                minutos_descanso_totales += descanso_minutos
                itinerario_final.append(f"*(Descanso de {descanso_minutos} minutos)*")
                
                # La siguiente tarea empieza después del descanso
                proxima_hora_inicio = hora_fin + timedelta(minutes=descanso_minutos)
            else:
                # Es la última tarea, no hay más descansos
                proxima_hora_inicio = hora_fin

        return itinerario_final, minutos_descanso_totales

    def _crear_plan_de_transicion(self, tareas, bache_utilizable):
        if not tareas: return []
        if bache_utilizable < len(tareas) * 20:
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
                return {"nuevo_estado": nuevo_estado, "mensaje_para_ui": f"Misión: **{opciones[0]}**. Añade detalles o escribe 'listo' para continuar."}
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
            return {"nuevo_estado": nuevo_estado, "mensaje_para_ui": f"Misión elegida: **{comando}**. Añade detalles o escribe 'listo' para continuar."}
        
        # === LÓGICA CORREGIDA PARA EL BUG #1 ===
        elif paso == "ESPERANDO_ESPECIFICACION":
            if "listo" in comando.lower():
                nuevo_estado = {"modo": "diseño", "paso_diseno": "ESPERANDO_ARRANQUE", "datos_plan": datos_plan}
                return {"nuevo_estado": nuevo_estado, "mensaje_para_ui": "Misión definida. Ahora, define el **momento de arranque**."}
            else:
                if "especificaciones" not in datos_plan:
                    datos_plan["especificaciones"] = []
                datos_plan["especificaciones"].append(comando)
                mision_completa = f"{datos_plan.get('mision', '')} -> {' -> '.join(datos_plan['especificaciones'])}"
                nuevo_estado = {"modo": "diseño", "paso_diseno": "ESPERANDO_ESPECIFICACION", "datos_plan": datos_plan}
                return {"nuevo_estado": nuevo_estado, "mensaje_para_ui": f"Entendido: **{mision_completa}**. Añade más detalles o escribe 'listo'."}
                
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
            if datos_plan.get("corrigiendo_con_ruleta"):
                datos_plan.pop("corrigiendo_con_ruleta", None)
                datos_plan.pop("campo_en_edicion", None)
                datos_plan["duracion"] = comando
                return self._presentar_borrador_contrato(datos_plan)

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
            campo_en_edicion = datos_plan.get("campo_en_edicion")
            opciones = [opt.strip() for opt in comando.split(',') if opt.strip()]
            
            if len(opciones) == 1:
                datos_plan.pop("campo_en_edicion", None)
                if campo_en_edicion == "misión":
                    datos_plan["mision"] = comando
                    datos_plan.pop("especificaciones", None)
                else:
                    datos_plan[campo_en_edicion] = comando
                return self._presentar_borrador_contrato(datos_plan)
            
            else:
                mapa_pasos = {
                    "misión": "ESPERANDO_RESULTADO_MISION",
                    "arranque": "ESPERANDO_RESULTADO_ARRANQUE",
                    "duración": "ESPERANDO_RESULTADO_DURACION"
                }
                paso_siguiente = mapa_pasos.get(campo_en_edicion)
                if paso_siguiente:
                    datos_plan["corrigiendo_con_ruleta"] = True
                    estado_actual["paso_diseno"] = paso_siguiente
                    return {"nuevo_estado": estado_actual, "accion_ui": "MOSTRAR_RULETA", "opciones_ruleta": opciones}
                else:
                    return {"nuevo_estado": {"modo": "libre"}, "mensaje_para_ui": "Error en la corrección con ruleta. Reiniciando."}
            
        return {"nuevo_estado": {"modo": "libre"}, "mensaje_para_ui": "Error en el flujo de diseño. Reiniciando."}
    # --- MODO TRANSICIÓN (v4.1 - CON BUGS CORREGIDOS) ---
    def _presentar_borrador_transicion(self, datos_bache):
        plan_borrador = datos_bache.get("plan_borrador", [])
        if not plan_borrador:
            return {"nuevo_estado": {"modo": "libre"}, "mensaje_para_ui": "Error: No hay plan que mostrar."}
        
        plan_texto_lista = []
        for i, tarea in enumerate(plan_borrador):
            plan_texto_lista.append(f"{i+1}. {tarea}")
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
                
                # === LÓGICA CORREGIDA PARA EL BUG #3 ===
                bache_total_minutos = int((fecha_inicio_madre - ahora).total_seconds() / 60)
                
                if bache_total_minutos <= 15:
                    return {"nuevo_estado": {"modo": "libre"}, "mensaje_para_ui": f"El bache de solo {bache_total_minutos} minutos es demasiado corto. Reiniciando."}
                
                datos_bache["bache_total_minutos"] = bache_total_minutos
                horas, minutos = divmod(bache_total_minutos, 60)
                mensaje = f"Detectado un bache de **{horas}h y {minutos}min**.\n\nAhora, dime las tareas que quieres hacer, separadas por comas."
                nuevo_estado = {"modo": "transicion", "paso_transicion": "ESPERANDO_TAREAS_OBJETIVO", "datos_bache": datos_bache}
                return {"nuevo_estado": nuevo_estado, "mensaje_para_ui": mensaje}
            except Exception as e:
                print(f"🚨 Error inesperado en _gestionar_transicion: {e}")
                return {"nuevo_estado": {"modo": "libre"}, "mensaje_para_ui": "Ocurrió un error inesperado."}

        elif paso == "ESPERANDO_TAREAS_OBJETIVO":
            bache_utilizable = datos_bache.get("bache_total_minutos", 0)
            plan_generado = self._procesar_plan_mixto(comando, bache_utilizable)
            if not plan_generado:
                return {"nuevo_estado": {"modo": "libre"}, "mensaje_para_ui": "No se pudo generar un plan viable con el tiempo disponible."}
            datos_bache["plan_borrador"] = plan_generado
            return self._presentar_borrador_transicion(datos_bache)

        elif paso == "ESPERANDO_CONFIRMACION_PLAN":
            if "confirmar" in comando.lower():
                plan_final = datos_bache.get("plan_borrador", [])
                itinerario_agendado, total_descansos = self._calendarizar_plan(plan_final, zona_horaria_usuario)
                plan_texto = "\n".join([f"**-** {linea}" for linea in itinerario_agendado])
                tiempo_total_planificado = sum(self._extraer_duracion_de_tarea(t) for t in plan_final)
                tiempo_total_usado = tiempo_total_planificado + total_descansos
                
                # === LÓGICA CORREGIDA PARA EL BUG #3 ===
                tiempo_libre_restante = datos_bache.get("bache_total_minutos", 0) - tiempo_total_usado
                
                mensaje_final = (f"**PLAN DE TRANSICIÓN AGENDADO**\n--------------------\n"
                                 f"Itinerario para tu bache:\n\n{plan_texto}\n\n"
                                 f"**Tiempo planificado:** {tiempo_total_planificado} min.\n"
                                 f"**Tiempo libre no asignado:** {tiempo_libre_restante} min.\n--------------------\n"
                                 f"¡Itinerario sellado!")
                return {"nuevo_estado": {"modo": "libre"}, "mensaje_para_ui": mensaje_final}
            elif "corregir" in comando.lower():
                nuevo_estado = {"modo": "transicion", "paso_transicion": "ESPERANDO_CATEGORIA_CORRECCION", "datos_bache": datos_bache}
                return {"nuevo_estado": nuevo_estado, "mensaje_para_ui": "Entendido. ¿Qué categoría quieres corregir? **(Tareas / Duraciones)**"}
            else:
                return {"nuevo_estado": estado_actual, "mensaje_para_ui": "No te he entendido. Responde 'confirmar' o 'corregir'."}

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
            bache_utilizable = datos_bache.get("bache_total_minutos", 0)
            
            tareas_modificadas = list(plan_actual)
            indices_para_reasignar = []

            partes_comando = [p.strip() for p in comando.split(',') if p.strip()]

            for parte in partes_comando:
                # === LÓGICA CORREGIDA PARA EL BUG #2 ===
                match_con_valor = re.match(r'(\d+)\s*[\.:\s(]+(\d+)\)?', parte)
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

            tareas_fijas = []
            tareas_flexibles_nombres = []
            for i, tarea in enumerate(tareas_modificadas):
                if i in indices_para_reasignar:
                    nombre_tarea = re.sub(r'\s*\(\d+.*\)', '', tarea).strip()
                    tareas_flexibles_nombres.append(nombre_tarea)
                else:
                    tareas_fijas.append(tarea)
            
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
        """
        El punto de entrada que es llamado por A.L.E. Core.
        Decide a qué modo de operación entrar (Diseño, Transición o Charla).
        """
        estado = datos.get("estado_conversacion", {"modo": "libre"})
        comando = datos.get("comando", "")
        comando_lower = comando.lower()

        if comando == "_SALUDO_INICIAL_":
            return {"nuevo_estado": {"modo": "libre"}, "mensaje_para_ui": "Guardián online. ¿Forjamos un Contrato o negociamos una Transición?"}

        palabras_clave_diseno = ["diseñar", "contrato", "forjar", "crear", "ruleta", "modo diseño"]
        palabras_clave_transicion = ["transicion", "bache", "preparar", "plan", "agendar", "negociar", "hueco", "espacio"]
        
        if any(palabra in comando_lower for palabra in palabras_clave_transicion) and estado.get("modo") != "transicion":
            nuevo_estado = {"modo": "transicion", "paso_transicion": "ESPERANDO_ACTIVIDAD_MADRE", "datos_bache": {}}
            return {"nuevo_estado": nuevo_estado, "mensaje_para_ui": "Modo Transición activado. ¿Cuál es la actividad principal para la que nos preparamos?"}

        if any(palabra in comando_lower for palabra in palabras_clave_diseno) and estado.get("modo") != "diseño":
            nuevo_estado = {"modo": "diseño", "paso_diseno": "ESPERANDO_MISION", "datos_plan": {}}
            return {"nuevo_estado": nuevo_estado, "mensaje_para_ui": "Modo Diseño activado. Define la misión."}

        if estado.get("modo") == "diseño":
            return self._gestionar_diseno(estado, comando)
        
        if estado.get("modo") == "transicion":
            return self._gestionar_transicion(estado, comando)

        respuesta_conversacional = await self._gestionar_charla_ia(comando)
        return {"nuevo_estado": {"modo": "libre"}, "mensaje_para_ui": respuesta_conversacional}
