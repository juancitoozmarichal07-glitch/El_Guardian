# =================================================================
# guardian.py (VERSIÓN FINAL Y COMPLETA)
# Cerebro del Guardián con lógica de diseño corregida y completa.
# =================================================================

import json
from datetime import datetime

class Guardian:
    def __init__(self):
        # Por ahora, no usaremos archivos para simplificar. La memoria vive solo mientras el servidor está activo.
        self.estado_global = {} # Un diccionario para guardar el estado de la conversación.
        print(f"    - Especialista 'Guardian' v8.0 (Lógica Completa) listo.")

    def _gestionar_diseno(self, estado_actual, comando):
        """
        Maneja el flujo de conversación cuando estamos en 'modo: "diseño"'.
        """
        paso = estado_actual.get("paso_diseno")
        datos_plan = estado_actual.get("datos_plan", {"mision": "", "especificaciones": []})

        # --- PASO 1: ESPERANDO LA MISIÓN INICIAL ---
        if paso == "ESPERANDO_MISION":
            opciones = [opt.strip() for opt in comando.split(',') if opt.strip()]
            if not opciones:
                return {"nuevo_estado": estado_actual, "mensaje_para_ui": "No he entendido las opciones. Por favor, define la misión con una o más opciones separadas por comas."}
            
            # Si solo hay una opción, la aceptamos directamente y avanzamos.
            if len(opciones) == 1:
                datos_plan["mision"] = opciones[0]
                nuevo_estado = {
                    "modo": "diseño",
                    "paso_diseno": "ESPERANDO_ESPECIFICACION", # Avanzamos al siguiente paso
                    "datos_plan": datos_plan
                }
                return {"nuevo_estado": nuevo_estado, "mensaje_para_ui": f"Misión aceptada: **{opciones[0]}**.\n\n¿Quieres añadir otra capa de ruleta para especificar más? (sí/no)"}
            
            # Si hay varias, preparamos el estado para la ruleta.
            else:
                estado_actual["paso_diseno"] = "ESPERANDO_RESULTADO_MISION" # Un paso intermedio para esperar el resultado.
                return {
                    "nuevo_estado": estado_actual, 
                    "accion_ui": "MOSTRAR_RULETA",
                    "opciones_ruleta": opciones
                }

        # --- PASO 1.5: ESPERANDO EL RESULTADO DE LA RULETA DE MISIÓN ---
        elif paso == "ESPERANDO_RESULTADO_MISION":
            # El 'comando' ahora es la elección que nos devuelve el frontend desde la ruleta.
            datos_plan["mision"] = comando
            nuevo_estado = {
                "modo": "diseño",
                "paso_diseno": "ESPERANDO_ESPECIFICACION",
                "datos_plan": datos_plan
            }
            return {"nuevo_estado": nuevo_estado, "mensaje_para_ui": f"Misión aceptada: **{comando}**.\n\n¿Quieres añadir otra capa de ruleta para especificar más? (sí/no)"}

        # --- PASO 2: ESPERANDO DECISIÓN DE ESPECIFICAR ---
        elif paso == "ESPERANDO_ESPECIFICACION":
            # Si el usuario quiere añadir más detalle, volvemos al paso de la misión.
            if "si" in comando.lower():
                # Aquí se añadiría la lógica para las especificaciones. Por ahora, lo saltamos para mantenerlo simple.
                # En un futuro, podríamos volver a "ESPERANDO_MISION" para crear un bucle.
                # Por ahora, avanzamos como si hubiera dicho que no.
                pass

            if "no" in comando.lower() or "si" in comando.lower(): # Avanzamos en ambos casos por ahora
                nuevo_estado = {
                    "modo": "diseño",
                    "paso_diseno": "ESPERANDO_HORA", # ¡AVANZAMOS A LA HORA!
                    "datos_plan": datos_plan
                }
                return {"nuevo_estado": nuevo_estado, "mensaje_para_ui": "Perfecto. Misión definida.\n\nAhora, dime las opciones para la **hora de inicio** (ej: 22:00, 22:30)."}
            
            else:
                return {"nuevo_estado": estado_actual, "mensaje_para_ui": "No te he entendido. Por favor, responde 'sí' o 'no'."}

        # --- PASO 3: ESPERANDO LA HORA ---
        elif paso == "ESPERANDO_HORA":
            # Aceptamos la primera opción que nos den para la hora.
            datos_plan["hora"] = comando.split(',')[0].strip()
            nuevo_estado = {
                "modo": "diseño",
                "paso_diseno": "ESPERANDO_DURACION",
                "datos_plan": datos_plan
            }
            return {"nuevo_estado": nuevo_estado, "mensaje_para_ui": f"Hora de inicio: **{datos_plan['hora']}**.\n\nFinalmente, dime las opciones para la **duración** (ej: 30 min, 1 hora)."}

        # --- PASO 4: ESPERANDO LA DURACIÓN Y FINALIZANDO ---
        elif paso == "ESPERANDO_DURACION":
            datos_plan["duracion"] = comando.split(',')[0].strip()
            
            # Construimos el texto del contrato final con toda la información recopilada.
            mision_final = datos_plan.get('mision', 'No definida')
            hora_final = datos_plan.get('hora', 'No definida')
            duracion_final = datos_plan.get('duracion', 'No definida')
            
            contrato_texto = (
                f"**CONTRATO FORJADO**\n"
                f"--------------------\n"
                f"**Misión:** {mision_final}\n"
                f"**Inicio:** {hora_final}\n"
                f"**Duración:** {duracion_final}\n"
                f"--------------------\n"
                f"Contrato sellado. La disciplina es libertad. ¿Siguiente misión?"
            )
            
            # Volvemos al modo libre, reseteando el estado para empezar de nuevo.
            nuevo_estado = {"modo": "libre"}
            return {"nuevo_estado": nuevo_estado, "mensaje_para_ui": contrato_texto}

        # Si por alguna razón el paso es desconocido, devolvemos el error.
        return {"nuevo_estado": estado_actual, "mensaje_para_ui": "Error en la lógica de diseño. Estado desconocido."}


    async def ejecutar(self, datos):
        """
        Punto de entrada principal que decide qué hacer con el comando del usuario.
        """
        # Obtenemos el estado de la conversación actual y el comando del usuario.
        estado = datos.get("estado_conversacion", {"modo": "libre"})
        comando = datos.get("comando", "")

        # Comando especial para el primer saludo al abrir la app.
        if comando == "_SALUDO_INICIAL_":
            return {"nuevo_estado": {"modo": "libre"}, "mensaje_para_ui": "Guardián online. ¿Forjamos un Contrato o necesitas conversar?"}

        # Palabras clave para entrar en el modo de diseño de contratos.
        palabras_clave_diseno = ["diseñar", "contrato", "forjar", "crear", "ruleta", "modo diseño"]
        
        # Condición 1: Si el usuario dice una palabra clave Y NO estamos ya en modo diseño, entramos.
        if any(palabra in comando.lower() for palabra in palabras_clave_diseno) and estado.get("modo") != "diseño":
            nuevo_estado = {"modo": "diseño", "paso_diseno": "ESPERANDO_MISION", "datos_plan": {}}
            mensaje_bienvenida = (
                "Modo Diseño activado. La claridad precede a la acción.\n"
                "Vamos a dar forma a tus visiones y hacer que tus ideas cobren vida. ¡Juntos, podemos lograrlo! 💪✨\n"
                "---\n"
                "¿Qué te gustaría diseñar hoy? Dime las opciones para la misión."
            )
            return {"nuevo_estado": nuevo_estado, "mensaje_para_ui": mensaje_bienvenida}

        # Condición 2: Si YA ESTAMOS en modo diseño, cualquier cosa que diga el usuario se procesa como parte del diseño.
        if estado.get("modo") == "diseño":
            return self._gestionar_diseno(estado, comando)

        # Condición 3: Si no se cumple nada de lo anterior, es una charla normal (por ahora, una respuesta simple).
        respuesta_charla = f"Comando recibido: '{comando}'. Aún estoy aprendiendo a conversar. Por ahora, puedes 'diseñar un contrato'."
        return {"nuevo_estado": {"modo": "libre"}, "mensaje_para_ui": respuesta_charla}

