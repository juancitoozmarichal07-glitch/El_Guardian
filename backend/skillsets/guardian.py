# =================================================================
# GUARDIAN.PY (v3.4 - El Negociador)
# =================================================================
# Esta versión introduce la capacidad de negociar el plan de transición.
# El usuario puede aceptar el plan del Guardián o modificarlo,
# definiendo tareas y duraciones personalizadas.

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
        print(f"    - Especialista 'Guardian' v3.4 (El Negociador) listo.")

    def _extraer_duracion_de_tarea(self, texto_tarea):
        """
        Extrae la duración en minutos de un string como "(20 min)" o "(20)".
        """
        match = re.search(r'\((\d+)\s*min\)', texto_tarea)
        if match:
            return int(match.group(1))
        match_num = re.search(r'\((\d+)\)', texto_tarea)
        if match_num:
            return int(match_num.group(1))
        return 0

    def _calendarizar_plan(self, plan_generado, zona_horaria):
        """
        Toma una lista de tareas con duraciones y la convierte en un itinerario
        con horarios de inicio, fin y descansos.
        """
        if not plan_generado:
            return [], 0

        itinerario_final = []
        minutos_descanso_totales = 0
        
        hora_actual = datetime.now(zona_horaria)
        proxima_hora_inicio = hora_actual

        for i, tarea_texto in enumerate(plan_generado):
            duracion_minutos = self._extraer_duracion_de_tarea(tarea_texto)
            if duracion_minutos == 0:
                continue

            hora_fin = proxima_hora_inicio + timedelta(minutes=duracion_minutos)

            texto_itinerario = (
                f"{proxima_hora_inicio.strftime('%H:%M')} - "
                f"{hora_fin.strftime('%H:%M')}: {tarea_texto}"
            )
            itinerario_final.append(texto_itinerario)

            if i < len(plan_generado) - 1:
                descanso_minutos = random.randint(5, 10)
                minutos_descanso_totales += descanso_minutos
                
                itinerario_final.append(f"*(Descanso de {descanso_minutos} minutos)*")
                
                proxima_hora_inicio = hora_fin + timedelta(minutes=descanso_minutos)

        return itinerario_final, minutos_descanso_totales

    def _crear_plan_de_transicion(self, tareas, bache_utilizable):
        """
        Asigna duraciones a las tareas. Modificado para aceptar duraciones personalizadas.
        """
        num_tareas = len(tareas)
        if num_tareas == 0:
            return []

        # Lógica de "Tarea Única Inteligente" para baches pequeños
        if bache_utilizable < num_tareas * 20:
            tarea_unica = random.choice(tareas)
            duracion = min(bache_utilizable, 45)
            duracion = 5 * round(duracion / 5)
            if duracion < 20: return []
            return [f"{tarea_unica} ({duracion} min)"]

        # Lógica Normal (distribución aleatoria)
        plan_final = []
        tiempo_restante = bache_utilizable
        random.shuffle(tareas)
        
        # Regla del usuario: el tiempo puede ser menor a 20 si él lo define.
        # La lógica aleatoria del guardián sigue respetando el mínimo de 20.
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
        """
        Procesa una entrada de usuario que puede tener tareas con y sin duración.
        """
        tareas_con_duracion = []
        tareas_sin_duracion = []
        tiempo_comprometido = 0

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

    def _gestionar_diseno(self, estado_actual, comando):
        # El código de _gestionar_diseno no cambia, lo omito por brevedad
        # pero debe estar aquí en tu archivo final.
        paso = estado_actual.get("paso_diseno")
        datos_plan = estado_actual.get("datos_plan", {})
        # ... (pega aquí todo el código de la función _gestionar_diseno de la v3.3)
        # ... es largo y no ha cambiado, para no hacer esta respuesta enorme.
        # Si no lo tienes a mano, dímelo y te lo pongo.
        return {"nuevo_estado": {"modo": "libre"}, "mensaje_para_ui": "Flujo de diseño no implementado en este snippet."}


    def _forjar_contrato(self, datos_plan):
        # El código de _forjar_contrato no cambia.
        # ... (pega aquí el código de la función _forjar_contrato de la v3.3)
        return {"nuevo_estado": {"modo": "libre"}, "mensaje_para_ui": "Contrato forjado."}


    def _gestionar_transicion(self, estado_actual, comando):
        """
        Maneja el flujo del "Guardián Negociador" con la lógica de aceptar/modificar.
        """
        paso = estado_actual.get("paso_transicion")
        datos_bache = estado_actual.get("datos_bache", {})
        zona_horaria_usuario = pytz.timezone("America/Montevideo")

        if paso == "ESPERANDO_ACTIVIDAD_MADRE":
            # ... (código sin cambios)
            datos_bache["actividad_madre"] = comando
            nuevo_estado = {"modo": "transicion", "paso_transicion": "ESPERANDO_HORA_INICIO_MADRE", "datos_bache": datos_bache}
            return {"nuevo_estado": nuevo_estado, "mensaje_para_ui": f"Entendido: **{comando}**. ¿A qué hora comienza?"}

        elif paso == "ESPERANDO_HORA_INICIO_MADRE":
            # ... (código sin cambios)
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

            # Guardamos el plan y pasamos a la confirmación
            datos_bache["plan_borrador"] = plan_generado
            plan_texto = "\n".join([f"- {tarea}" for tarea in plan_generado])
            mensaje = (
                f"He generado el siguiente plan borrador:\n\n{plan_texto}\n\n"
                f"**¿Aceptas este plan o quieres modificarlo?** (aceptar/modificar)"
            )
            nuevo_estado = {"modo": "transicion", "paso_transicion": "ESPERANDO_CONFIRMACION_PLAN", "datos_bache": datos_bache}
            return {"nuevo_estado": nuevo_estado, "mensaje_para_ui": mensaje}

        elif paso == "ESPERANDO_CONFIRMACION_PLAN":
            if "aceptar" in comando.lower():
                plan_final = datos_bache.get("plan_borrador", [])
            elif "modificar" in comando.lower():
                nuevo_estado = {"modo": "transicion", "paso_transicion": "ESPERANDO_PLAN_MODIFICADO", "datos_bache": datos_bache}
                mensaje = (
                    "Entendido. Por favor, define tú mismo las tareas. Si quieres una duración específica, ponla entre paréntesis.\n\n"
                    "*Ejemplo: Leer la Biblia (15 min), Jugar, Agradecer (5 min)*"
                )
                return {"nuevo_estado": nuevo_estado, "mensaje_para_ui": mensaje}
            else:
                return {"nuevo_estado": estado_actual, "mensaje_para_ui": "No te he entendido. Por favor, responde 'aceptar' o 'modificar'."}
            
            # Si el plan fue aceptado, se ejecuta el resto del código
            itinerario_agendado, total_descansos = self._calendarizar_plan(plan_final, zona_horaria_usuario)
            plan_texto = "\n".join([f"**-** {linea}" for linea in itinerario_agendado])
            tiempo_total_planificado = sum(self._extraer_duracion_de_tarea(t) for t in plan_final)
            tiempo_total_usado = tiempo_total_planificado + total_descansos
            tiempo_libre_restante = datos_bache.get("bache_utilizable_minutos", 0) - tiempo_total_usado
            mensaje_final = (
                f"**PLAN DE TRANSICIÓN AGENDADO**\n--------------------\n"
                f"He preparado el siguiente itinerario para tu bache de tiempo:\n\n"
                f"{plan_texto}\n\n"
                f"**Tiempo total planificado:** {tiempo_total_planificado} minutos de trabajo.\n"
                f"**Tiempo libre no asignado:** {tiempo_libre_restante} minutos.\n--------------------\n"
                f"¡Itinerario sellado! Puedes registrar estas tareas en tu app."
            )
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
            mensaje_final = (
                f"**PLAN DE TRANSICIÓN AGENDADO**\n--------------------\n"
                f"He preparado el siguiente itinerario basado en tu plan manual:\n\n"
                f"{plan_texto}\n\n"
                f"**Tiempo total planificado:** {tiempo_total_planificado} minutos de trabajo.\n"
                f"**Tiempo libre no asignado:** {tiempo_libre_restante} minutos.\n--------------------\n"
                f"¡Itinerario sellado! Puedes registrar estas tareas en tu app."
            )
            return {"nuevo_estado": {"modo": "libre"}, "mensaje_para_ui": mensaje_final}

        return {"nuevo_estado": {"modo": "libre"}, "mensaje_para_ui": "Error en el flujo de transición. Reiniciando."}

    async def _gestionar_charla_ia(self, comando):
        """
        Maneja la conversación libre usando g4f.
        """
        try:
            prompt = f"Eres el Guardián, una IA compañera de Juan. Eres directo, sabio y motivador. El usuario dice: '{comando}'"
            respuesta_ia = await g4f.ChatCompletion.create_async(
                model=g4f.models.default,
                messages=[{"role": "user", "content": prompt}]
            )
            return respuesta_ia or "No he podido procesar eso. Intenta de nuevo."
        except Exception as e:
            print(f"🚨 Error en la llamada a g4f: {e}")
            return "Mi núcleo cognitivo tuvo una sobrecarga. Inténtalo de nuevo."

    async def ejecutar(self, datos):
        """
        El punto de entrada que es llamado por A.L.E. Core.
        """
        estado = datos.get("estado_conversacion", {"modo": "libre"})
        comando = datos.get("comando", "")

        if comando == "_SALUDO_INICIAL_":
            return {"nuevo_estado": {"modo": "libre"}, "mensaje_para_ui": "Guardián online. ¿Forjamos un Contrato o negociamos una Transición?"}

        palabras_clave_diseno = ["diseñar", "contrato", "forjar", "crear", "ruleta", "modo diseño"]
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
