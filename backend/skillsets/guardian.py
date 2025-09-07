# =================================================================
# GUARDIAN.PY (v2.5 - Con Sello de Tiempo)
# =================================================================
# Se añade una marca de tiempo ("Sellado a las HH:MM") a todos
# los contratos forjados para darles un contexto temporal.

import re
from datetime import datetime, timedelta
import pytz

class Guardian:
    def __init__(self):
        print(f"    - Especialista 'Guardian' v2.5 (Con Sello de Tiempo) listo.")

    # ... (Omito las funciones sin cambios por brevedad: _extraer_duracion_de_tarea, _gestionar_diseno) ...

    # --- FUNCIÓN DE FORJAR CONTRATO (¡MODIFICADA!) ---
    def _forjar_contrato(self, datos_plan):
        """
        Toma los datos recopilados y genera el mensaje final del contrato,
        incluyendo la hora a la que fue sellado.
        """
        # Obtenemos la hora actual en la zona horaria correcta
        zona_horaria_usuario = pytz.timezone("America/Montevideo")
        ahora = datetime.now(zona_horaria_usuario)
        hora_sellado = ahora.strftime("%H:%M") # Formato HH:MM

        mision_base = datos_plan.get('mision', 'N/A')
        especificaciones = datos_plan.get('especificaciones', [])
        mision_completa = f"{mision_base} -> {' -> '.join(especificaciones)}" if especificaciones else mision_base
        
        contrato_texto = (
            f"**CONTRATO FORJADO**\n--------------------\n"
            f"**Misión:** {mision_completa}\n"
            f"**Arranque:** {datos_plan.get('arranque', 'N/A')}\n"
            f"**Duración:** {datos_plan.get('duracion', 'N/A')}\n"
            f"**Sellado a las:** {hora_sellado}\n--------------------\n" # <-- NUEVA LÍNEA
            f"Contrato sellado. ¿Siguiente misión?"
        )
        nuevo_estado = {"modo": "libre"}
        return {"nuevo_estado": nuevo_estado, "mensaje_para_ui": contrato_texto}

    # --- FUNCIÓN DE GESTIÓN DE TRANSICIÓN (¡MODIFICADA!) ---
    def _gestionar_transicion(self, estado_actual, comando):
        # ... (Omito los primeros pasos de la función que no cambian) ...
        paso = estado_actual.get("paso_transicion")
        datos_bache = estado_actual.get("datos_bache", {})

        # ... (PASO 1, 2, 3 son iguales) ...

        # PASO 4: Procesar resultado, forjar contrato y decidir si continuar
        elif paso == "ESPERANDO_RESULTADO_TRANSICION":
            # Obtenemos la hora actual en la zona horaria correcta
            zona_horaria_usuario = pytz.timezone("America/Montevideo")
            ahora = datetime.now(zona_horaria_usuario)
            hora_sellado = ahora.strftime("%H:%M") # Formato HH:MM

            tarea_elegida = comando
            duracion_tarea = self._extraer_duracion_de_tarea(tarea_elegida)

            bache_anterior = datos_bache.get("bache_restante_minutos", 0)
            nuevo_bache = bache_anterior - duracion_tarea
            datos_bache["bache_restante_minutos"] = nuevo_bache

            contrato_texto = (
                f"**CONTRATO DE TRANSICIÓN FORJADO**\n--------------------\n"
                f"**Misión Actual:** **{tarea_elegida}**\n"
                f"**Tiempo Restante en Bache:** {nuevo_bache} minutos\n"
                f"**Actividad Madre:** {datos_bache.get('actividad_madre')} (a las {datos_bache.get('hora_inicio_madre')})\n"
                f"**Sellado a las:** {hora_sellado}\n--------------------" # <-- NUEVA LÍNEA
            )

            # ... (El resto de la lógica de decisión de continuar es igual) ...
            if nuevo_bache < 10:
                mensaje_final = f"{contrato_texto}\n\nBache de tiempo casi agotado. Prepárate para '{datos_bache.get('actividad_madre')}'. Saliendo de modo transición."
                return {"nuevo_estado": {"modo": "libre"}, "mensaje_para_ui": mensaje_final}
            else:
                nuevo_estado = {"modo": "transicion", "paso_transicion": "ESPERANDO_DECISION_CONTINUAR", "datos_bache": datos_bache}
                mensaje_continuacion = f"{contrato_texto}\n\n¿Forjamos otro contrato para los {nuevo_bache} minutos restantes? (sí/no)"
                return {"nuevo_estado": nuevo_estado, "mensaje_para_ui": mensaje_continuacion}

        # ... (El resto de la función es igual) ...
        return {"nuevo_estado": {"modo": "libre"}, "mensaje_para_ui": "Error en el flujo de transición. Reiniciando."}

    # ... (El resto de las funciones de la clase Guardian son iguales) ...
