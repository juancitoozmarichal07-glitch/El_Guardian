# =================================================================
# GUARDIAN.PY (v3.2 - El Estratega de Bloques Aleatorios)
# =================================================================
# - Asigna duraciones aleatorias entre 20 y 45 min.
# - Las duraciones son siempre en intervalos de 5.
# - El plan es final, no intenta llenar todo el bache.

import re
from datetime import datetime, timedelta
import pytz
import random

class Guardian:
    def __init__(self):
        print(f"    - Especialista 'Guardian' v3.2 (Estratega de Bloques) listo.")

    # ... (Omito las funciones sin cambios por brevedad) ...

    # --- ¡NUEVO CEREBRO ESTRATÉGICO CON LAS NUEVAS REGLAS! ---
    def _crear_plan_de_transicion(self, tareas, bache_utilizable):
        """
        Asigna duraciones aleatorias (20-45 min, en bloques de 5) a las
        tareas, sin exceder el tiempo del bache.
        """
        plan_final = []
        tiempo_restante = bache_utilizable
        
        # 1. Barajamos las tareas para que el orden sea diferente cada vez
        random.shuffle(tareas)

        # 2. Definimos los posibles bloques de tiempo
        bloques_de_tiempo = [20, 25, 30, 35, 40, 45]

        for tarea in tareas:
            # 3. Si el tiempo que queda es menor que el bloque mínimo, paramos.
            if tiempo_restante < 20:
                break

            # 4. Elegimos un bloque de tiempo aleatorio
            duracion_asignada = random.choice(bloques_de_tiempo)

            # 5. Si el bloque elegido es mayor que el tiempo restante,
            # intentamos con uno más pequeño. Si no hay, paramos.
            while duracion_asignada > tiempo_restante:
                # Filtramos para encontrar bloques que aún quepan
                posibles_bloques = [b for b in bloques_de_tiempo if b <= tiempo_restante]
                if not posibles_bloques:
                    duracion_asignada = 0 # No hay bloques que quepan
                    break
                # Elegimos uno de los bloques más pequeños que sí caben
                duracion_asignada = random.choice(posibles_bloques)
            
            if duracion_asignada == 0:
                continue # Pasamos a la siguiente tarea, quizás para ella sí quepa

            plan_final.append(f"{tarea} ({duracion_asignada} min)")
            tiempo_restante -= duracion_asignada
        
        return plan_final

    # --- FUNCIÓN DE TRANSICIÓN (Usa el nuevo cerebro) ---
    def _gestionar_transicion(self, estado_actual, comando):
        paso = estado_actual.get("paso_transicion")
        datos_bache = estado_actual.get("datos_bache", {})
        zona_horaria_usuario = pytz.timezone("America/Montevideo")

        # PASO 1 y 2 (Cálculo del bache con colchón variable)
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

                colchon_seguridad = random.randint(10, 20)
                bache_utilizable = bache_total_minutos - colchon_seguridad

                if bache_utilizable < 20:
                    return {"nuevo_estado": {"modo": "libre"}, "mensaje_para_ui": "Bache de tiempo insuficiente para planificar. Reiniciando."}

                datos_bache["bache_utilizable_minutos"] = bache_utilizable
                
                horas, minutos = divmod(bache_utilizable, 60)
                mensaje = f"Detectado un bache utilizable de **{horas}h y {minutos}min** (con {colchon_seguridad} min de colchón).\n\nAhora, dime las tareas que quieres hacer, separadas por comas."

                nuevo_estado = {"modo": "transicion", "paso_transicion": "ESPERANDO_TAREAS_OBJETIVO", "datos_bache": datos_bache}
                return {"nuevo_estado": nuevo_estado, "mensaje_para_ui": mensaje}
            except Exception as e:
                print(f"🚨 Error inesperado en _gestionar_transicion: {e}")
                return {"nuevo_estado": {"modo": "libre"}, "mensaje_para_ui": "Ocurrió un error inesperado."}

        # PASO 3: Recibir objetivos y generar el plan completo
        elif paso == "ESPERANDO_TAREAS_OBJETIVO":
            tareas_objetivo = [tarea.strip() for tarea in comando.split(',') if tarea.strip()]
            if not tareas_objetivo:
                return {"nuevo_estado": estado_actual, "mensaje_para_ui": "Necesito al menos una tarea objetivo."}

            bache_utilizable = datos_bache.get("bache_utilizable_minutos", 0)
            
            plan_generado = self._crear_plan_de_transicion(tareas_objetivo, bache_utilizable)

            if not plan_generado:
                return {"nuevo_estado": {"modo": "libre"}, "mensaje_para_ui": "No se pudo generar un plan con el tiempo disponible. Intenta con un bache más grande."}

            plan_texto = "\n".join([f"**{i+1}.** {tarea}" for i, tarea in enumerate(plan_generado)])
            
            tiempo_total_planificado = sum(self._extraer_duracion_de_tarea(t) for t in plan_generado)
            tiempo_libre_restante = bache_utilizable - tiempo_total_planificado
            
            mensaje_final = (
                f"**PLAN DE TRANSICIÓN FORJADO**\n--------------------\n"
                f"He preparado el siguiente plan para tu bache de tiempo:\n\n"
                f"{plan_texto}\n\n"
                f"**Tiempo total planificado:** {tiempo_total_planificado} minutos.\n"
                f"**Tiempo libre no asignado:** {tiempo_libre_restante} minutos.\n--------------------\n"
                f"¡A la carga! El plan está sellado."
            )
            
            return {"nuevo_estado": {"modo": "libre"}, "mensaje_para_ui": mensaje_final}

        return {"nuevo_estado": {"modo": "libre"}, "mensaje_para_ui": "Error en el flujo de transición. Reiniciando."}

    # ... (resto de funciones de la clase)
