# =================================================================
# GUARDIAN.PY (v18.0 - El Analista)
# =================================================================
# - NUEVO MODO "TICKET DE ACCIÓN": Un modo inteligente que analiza el texto del usuario.
#   Extrae automáticamente Tarea, Arranque y Duración desde una sola frase.
# - FLUJO CONVERSACIONAL: El modo ticket ahora dialoga con el usuario.
# - ENCADENAMIENTO DE TICKETS: Permite crear múltiples tickets en una sola sesión.
# - FILOSOFÍA REFINADA: Distingue claramente entre Contratos (fricción) y Tickets (enfoque).

import g4f
import re
from datetime import datetime, timedelta
import pytz
import random
import string
import json
import os

class Guardian:
    def __init__(self):
        """
        Inicializa el especialista Guardian y carga la memoria persistente.
        """
        self.memory_file = "guardian_memory.json"
        self.archivador_contratos = {}
        self.datos_usuario = {
            "racha_diaria": 0,
            "fecha_ultima_racha": None,
            "logros": []
        }
        # Listas de sinónimos para comandos flexibles
        self.PALABRAS_CONFIRMACION = ["confirmar", "confirmo", "acepto", "dale", "proceder", "adelante", "si", "sí", "seguro"]
        self.PALABRAS_CORRECCION = ["corregir", "corrijo", "editar", "cambiar", "modificar", "ajustar"]
        self.PALABRAS_SI = ["si", "sí", "claro", "afirmativo", "acepto"]
        self.PALABRAS_NO = ["no", "negativo", "cancelar"]
        self.PALABRAS_DISENO_MULTIPLE = ["múltiple", "multiple", "combo", "ráfaga", "secuencia"]
        self.MISIONES_GENERICAS = ["estudiar", "trabajar", "leer", "programar", "escribir", "dibujar", "practicar", "ordenar", "limpiar"]

        self._cargar_memoria()
        print(f"    - Especialista 'Guardian' v18.0 (El Analista) listo.")

    # --- GESTIÓN DE MEMORIA PERSISTENTE ---
    def _cargar_memoria(self):
        if os.path.exists(self.memory_file):
            try:
                with open(self.memory_file, 'r', encoding='utf-8') as f:
                    memoria = json.load(f)
                    self.archivador_contratos = memoria.get("archivador_contratos", {})
                    self.datos_usuario = memoria.get("datos_usuario", self.datos_usuario)
                    print("      -> Memoria del Guardián cargada exitosamente.")
            except (json.JSONDecodeError, IOError) as e:
                print(f"      -> 🚨 Error al cargar la memoria: {e}. Se usará una memoria nueva.")
        else:
            print("      -> No se encontró archivo de memoria. Se creará uno nuevo.")

    def _guardar_memoria(self):
        try:
            with open(self.memory_file, 'w', encoding='utf-8') as f:
                memoria = {
                    "archivador_contratos": self.archivador_contratos,
                    "datos_usuario": self.datos_usuario
                }
                json.dump(memoria, f, indent=4, ensure_ascii=False)
        except IOError as e:
            print(f"      -> 🚨 Error crítico al guardar la memoria: {e}")

    # --- FUNCIONES AUXILIARES ---
    def _generar_id_aleatorio(self, prefijo="PLAN"):
        caracteres = string.ascii_uppercase + string.digits
        sufijo = ''.join(random.choices(caracteres, k=4))
        return f"{prefijo}-{sufijo}"

    # --- FUNCIONES DEL MODO TICKET DE ACCIÓN ---
    def _analizar_texto_ticket(self, texto):
        """
        Analiza el texto del usuario para extraer Tarea, Arranque y Duración.
        """
        tarea = texto
        arranque = "No definido"
        duracion = "No definida"

        # Buscar hora de arranque (ej: a las 14:30)
        match_arranque = re.search(r'a las\s+(\d{1,2}:\d{2})', texto, re.IGNORECASE)
        if match_arranque:
            arranque = match_arranque.group(1)
            tarea = tarea.replace(match_arranque.group(0), "").strip()

        # Buscar duración (ej: durante 25 min, (25 min))
        match_duracion = re.search(r'(?:durante\s+|por\s+)?\(?(\d+)\s*min(?:utos)?\)?', texto, re.IGNORECASE)
        if match_duracion:
            duracion = f"{match_duracion.group(1)} min"
            tarea = tarea.replace(match_duracion.group(0), "").strip()
        
        # Limpiar frases introductorias comunes
        frases_a_limpiar = [
            "bueno mira tengo ganas de", "tengo ganas de", "quiero", "voy a"
        ]
        for frase in frases_a_limpiar:
            if tarea.lower().startswith(frase):
                tarea = tarea[len(frase):].strip()

        return tarea.capitalize(), arranque, duracion

    def _emitir_ticket(self, detalles_texto):
        if not detalles_texto:
            return {"nuevo_estado": {"modo": "libre"}, "mensaje_para_ui": "La descripción del ticket no puede estar vacía. Operación cancelada."}

        tarea, arranque, duracion = self._analizar_texto_ticket(detalles_texto)
        
        zona_horaria_usuario = pytz.timezone("America/Montevideo")
        ahora = datetime.now(zona_horaria_usuario)
        identificador = self._generar_id_aleatorio("TCKT")

        ticket_obj = {
            "tipo": "Ticket",
            "id": identificador,
            "tarea": tarea,
            "arranque": arranque,
            "duracion": duracion,
            "fecha_emision": ahora.strftime("%d/%m/%y"),
            "hora_emision": ahora.strftime("%H:%M")
        }
        self.archivador_contratos[identificador] = ticket_obj
        self._guardar_memoria()

        ticket_texto = (
            f"**TICKET DE ACCIÓN EMITIDO**\n--------------------\n"
            f"**ID:** {identificador}\n"
            f"**Tarea:** {tarea}\n"
            f"**Arranque:** {arranque}\n"
            f"**Duración:** {duracion}\n"
            f"**Emitido:** {ticket_obj['fecha_emision']} a las {ticket_obj['hora_emision']}\n--------------------\n\n"
            f"¿Deseas gestionar otro ticket?"
        )
        
        nuevo_estado = {"modo": "ticket", "paso_ticket": "ESPERANDO_ENCADENAR"}
        return {"nuevo_estado": nuevo_estado, "mensaje_para_ui": ticket_texto}

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
            f"¿Confirmas este contrato o quieres corregir algo?"
        )
        
        paso_actual = datos_plan.get("paso_origen_borrador", "ESPERANDO_CONFIRMACION_CONTRATO")
        modo_actual = datos_plan.get("modo_origen_borrador", "diseño")

        nuevo_estado = {"modo": modo_actual, "paso_diseno": paso_actual, "datos_plan": datos_plan}
        if modo_actual == "diseno_multiple":
            nuevo_estado["paso_combo"] = "ESPERANDO_CONFIRMACION_CONTRATO_COMBO"

        return {"nuevo_estado": nuevo_estado, "mensaje_para_ui": contrato_borrador_texto}

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
        self._guardar_memoria()

        contrato_texto = (
            f"**CONTRATO FORJADO**\n--------------------\n"
            f"**Misión:** {mision_completa}\n"
            f"**Arranque:** {contrato_obj['arranque']}\n"
            f"**Duración:** {contrato_obj['duracion']}\n"
            f"**Sellado:** {fecha_sellado} a las {hora_sellado}\n"
            f"**Identificador:** {identificador}\n--------------------"
        )
        
        if datos_plan.get("en_combo"):
            return {"nuevo_estado": {"modo": "diseno_multiple"}, "mensaje_para_ui": contrato_texto, "evento": "CONTRATO_COMBO_FORJADO"}
        else:
            contrato_texto += "\nContrato sellado. ¿Deseas forjar otro contrato?"
            nuevo_estado = {"modo": "diseño", "paso_diseno": "ESPERANDO_ENCADENAR", "datos_plan": {}}
            return {"nuevo_estado": nuevo_estado, "mensaje_para_ui": contrato_texto}

    def _gestionar_diseno(self, estado_actual, comando):
        paso = estado_actual.get("paso_diseno")
        datos_plan = estado_actual.get("datos_plan", {})
        comando_lower = comando.lower()
        
        if paso == "ESPERANDO_MISION":
            opciones = [opt.strip() for opt in comando.split(',') if opt.strip()]
            if not opciones: return {"nuevo_estado": estado_actual, "mensaje_para_ui": "Define la misión."}
            if len(opciones) == 1:
                datos_plan["mision"] = opciones[0]
                nuevo_estado = {"modo": "diseño", "paso_diseno": "ESPERANDO_ESPECIFICACION", "datos_plan": datos_plan}
                return {"nuevo_estado": nuevo_estado, "mensaje_para_ui": f"Misión: **{opciones[0]}**. ¿Necesitas especificar más?"}
            else:
                estado_actual["paso_diseno"] = "ESPERANDO_RESULTADO_MISION"
                return {"nuevo_estado": estado_actual, "accion_ui": "MOSTRAR_RULETA", "opciones_ruleta": opciones}
        
        elif paso == "ESPERANDO_RESULTADO_MISION":
            if datos_plan.get("corrigiendo_con_ruleta"):
                datos_plan.pop("corrigiendo_con_ruleta", None)
                campo_en_edicion = datos_plan.pop("campo_en_edicion", None)
                datos_plan["mision"] = comando
                if campo_en_edicion and "especificaciones" in datos_plan:
                    nuevo_estado = {"modo": "diseño", "paso_diseno": "PREGUNTAR_MANTENER_CAPAS", "datos_plan": datos_plan}
                    return {"nuevo_estado": nuevo_estado, "mensaje_para_ui": "Has cambiado la misión. ¿Quieres mantener las especificaciones (capas) actuales?"}
                return self._presentar_borrador_contrato(datos_plan)
            
            datos_plan["mision"] = comando
            nuevo_estado = {"modo": "diseño", "paso_diseno": "ESPERANDO_ESPECIFICACION", "datos_plan": datos_plan}
            return {"nuevo_estado": nuevo_estado, "mensaje_para_ui": f"Misión elegida: **{comando}**. ¿Necesitas especificar más?"}
        
        elif paso == "ESPERANDO_ESPECIFICACION":
            if any(palabra in comando_lower for palabra in self.PALABRAS_SI):
                nuevo_estado = {"modo": "diseño", "paso_diseno": "ESPERANDO_OPCIONES_ESPECIFICACION", "datos_plan": datos_plan}
                return {"nuevo_estado": nuevo_estado, "mensaje_para_ui": "Entendido. Dame las opciones para la siguiente capa."}
            else:
                mision_actual = datos_plan.get("mision", "").lower()
                tiene_especificaciones = "especificaciones" in datos_plan and datos_plan["especificaciones"]
                if mision_actual in self.MISIONES_GENERICAS and not tiene_especificaciones:
                    nuevo_estado = {"modo": "diseño", "paso_diseno": "VALIDANDO_ESPECIFICACION", "datos_plan": datos_plan}
                    mensaje = f"**¡Atención!** La misión '{datos_plan.get('mision')}' es muy amplia. Para que sea más efectiva, te recomiendo añadir una especificación. ¿Estás seguro de que quieres forjarla así de general?"
                    return {"nuevo_estado": nuevo_estado, "mensaje_para_ui": mensaje}
                
                nuevo_estado = {"modo": "diseño", "paso_diseno": "ESPERANDO_ARRANQUE", "datos_plan": datos_plan}
                return {"nuevo_estado": nuevo_estado, "mensaje_para_ui": "Misión definida. Ahora, define el **momento de arranque**."}

        elif paso == "VALIDANDO_ESPECIFICACION":
            if any(palabra in comando_lower for palabra in self.PALABRAS_SI):
                nuevo_estado = {"modo": "diseño", "paso_diseno": "ESPERANDO_ARRANQUE", "datos_plan": datos_plan}
                return {"nuevo_estado": nuevo_estado, "mensaje_para_ui": "Entendido. Misión definida. Ahora, define el **momento de arranque**."}
            else:
                nuevo_estado = {"modo": "diseño", "paso_diseno": "ESPERANDO_OPCIONES_ESPECIFICACION", "datos_plan": datos_plan}
                return {"nuevo_estado": nuevo_estado, "mensaje_para_ui": "Perfecto. Dame las opciones para la siguiente capa."}

        elif paso == "ESPERANDO_OPCIONES_ESPECIFICACION":
            opciones = [opt.strip() for opt in comando.split(',') if opt.strip()]
            if not opciones: return {"nuevo_estado": estado_actual, "mensaje_para_ui": "Define las opciones."}
            if "especificaciones" not in datos_plan: datos_plan["especificaciones"] = []
            if len(opciones) == 1:
                datos_plan["especificaciones"].append(opciones[0])
                mision_completa = f"{datos_plan.get('mision', '')} -> {' -> '.join(datos_plan['especificaciones'])}"
                nuevo_estado = {"modo": "diseño", "paso_diseno": "ESPERANDO_ESPECIFICACION", "datos_plan": datos_plan}
                return {"nuevo_estado": nuevo_estado, "mensaje_para_ui": f"Entendido: **{mision_completa}**. ¿Otra capa más?"}
            else:
                estado_actual["paso_diseno"] = "ESPERANDO_RESULTADO_ESPECIFICACION"
                return {"nuevo_estado": estado_actual, "accion_ui": "MOSTRAR_RULETA", "opciones_ruleta": opciones}
                
        elif paso == "ESPERANDO_RESULTADO_ESPECIFICACION":
            if "especificaciones" not in datos_plan: datos_plan["especificaciones"] = []
            datos_plan["especificaciones"].append(comando)
            mision_completa = f"{datos_plan.get('mision', '')} -> {' -> '.join(datos_plan['especificaciones'])}"
            nuevo_estado = {"modo": "diseño", "paso_diseno": "ESPERANDO_ESPECIFICACION", "datos_plan": datos_plan}
            return {"nuevo_estado": nuevo_estado, "mensaje_para_ui": f"Entendido: **{mision_completa}**. ¿Otra capa más?"}
            
        elif paso == "ESPERANDO_ARRANQUE":
            opciones = [opt.strip() for opt in comando.split(',') if opt.strip()]
            if not opciones: return {"nuevo_estado": estado_actual, "mensaje_para_ui": "Define el momento de arranque."}
            if len(opciones) == 1:
                datos_plan["arranque"] = opciones[0]
                nuevo_estado = {"modo": "diseño", "paso_diseno": "ESPERANDO_DECISION_DURACION", "datos_plan": datos_plan}
                return {"nuevo_estado": nuevo_estado, "mensaje_para_ui": f"Arranque: **{opciones[0]}**. ¿Necesitas definir una duración?"}
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
            return {"nuevo_estado": nuevo_estado, "mensaje_para_ui": f"Arranque: **{comando}**. ¿Necesitas definir una duración?"}
            
        elif paso == "ESPERANDO_DECISION_DURACION":
            if any(palabra in comando_lower for palabra in self.PALABRAS_SI):
                nuevo_estado = {"modo": "diseño", "paso_diseno": "ESPERANDO_DURACION", "datos_plan": datos_plan}
                return {"nuevo_estado": nuevo_estado, "mensaje_para_ui": "Entendido. Dime las opciones para la duración o di 'aleatorio'."}
            else:
                datos_plan["duracion"] = "No definida"
                return self._presentar_borrador_contrato(datos_plan)
                
        elif paso == "ESPERANDO_DURACION":
            if "aleatorio" in comando_lower:
                duracion_aleatoria = random.randint(30, 70)
                duracion_redondeada = 5 * round(duracion_aleatoria / 5)
                datos_plan["duracion"] = f"{duracion_redondeada} min"
                return self._presentar_borrador_contrato(datos_plan)

            opciones = [opt.strip() for opt in comando.split(',') if opt.strip()]
            if not opciones: return {"nuevo_estado": estado_actual, "mensaje_para_ui": "Define la duración o di 'aleatorio'."}
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
            if any(palabra in comando_lower for palabra in self.PALABRAS_CONFIRMACION):
                return self._forjar_contrato(datos_plan)
            elif any(palabra in comando_lower for palabra in self.PALABRAS_CORRECCION):
                nuevo_estado = {"modo": "diseño", "paso_diseno": "ESPERANDO_CAMPO_A_CORREGIR", "datos_plan": datos_plan}
                mensaje = "Entendido. ¿Qué campo quieres corregir? (misión / arranque / duración)"
                return {"nuevo_estado": nuevo_estado, "mensaje_para_ui": mensaje}
            else:
                return {"nuevo_estado": estado_actual, "mensaje_para_ui": "No te he entendido. Por favor, responde con algo como 'confirmar' o 'corregir'."}

        elif paso == "ESPERANDO_CAMPO_A_CORREGIR":
            campo_a_corregir = comando.lower()
            if campo_a_corregir in ["misión", "mision", "arranque", "duración", "duracion"]:
                if campo_a_corregir == "mision": campo_a_corregir = "misión"
                if campo_a_corregir == "duracion": campo_a_corregir = "duración"
                
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
                if campo_en_edicion == "misión":
                    datos_plan["mision"] = comando
                    datos_plan.pop("campo_en_edicion", None)
                    if "especificaciones" in datos_plan:
                        nuevo_estado = {"modo": "diseño", "paso_diseno": "PREGUNTAR_MANTENER_CAPAS", "datos_plan": datos_plan}
                        return {"nuevo_estado": nuevo_estado, "mensaje_para_ui": "Has cambiado la misión. ¿Quieres mantener las especificaciones (capas) actuales?"}
                else:
                    datos_plan[campo_en_edicion] = comando
                    datos_plan.pop("campo_en_edicion", None)
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

        elif paso == "PREGUNTAR_MANTENER_CAPAS":
            if any(palabra in comando_lower for palabra in self.PALABRAS_SI):
                pass
            else:
                datos_plan.pop("especificaciones", None)
            return self._presentar_borrador_contrato(datos_plan)

        elif paso == "ESPERANDO_ENCADENAR":
            if any(palabra in comando_lower for palabra in self.PALABRAS_SI):
                nuevo_estado = {"modo": "diseño", "paso_diseno": "ESPERANDO_MISION", "datos_plan": {}}
                return {"nuevo_estado": nuevo_estado, "mensaje_para_ui": "Perfecto. Define la misión para el nuevo contrato."}
            else:
                return {"nuevo_estado": {"modo": "libre"}, "mensaje_para_ui": "Entendido. Guardián en espera."}
            
        return {"nuevo_estado": {"modo": "libre"}, "mensaje_para_ui": "Error en el flujo de diseño. Reiniciando."}
    # --- MODO DISEÑO MÚLTIPLE (COMBO) ---
    def _gestionar_diseno_multiple(self, estado_actual, comando):
        paso_combo = estado_actual.get("paso_combo", "INICIO_COMBO")
        datos_combo = estado_actual.get("datos_combo", {})
        
        if paso_combo == "INICIO_COMBO":
            datos_combo = {"tareas_pendientes": [], "contratos_forjados": [], "indice_actual": 0}
            nuevo_estado = {"modo": "diseno_multiple", "paso_combo": "ESPERANDO_TAREAS_COMBO", "datos_combo": datos_combo}
            mensaje = "Modo Diseño Múltiple activado. Dame la lista de tareas que quieres encadenar, separadas por comas (máximo 3)."
            return {"nuevo_estado": nuevo_estado, "mensaje_para_ui": mensaje}

        elif paso_combo == "ESPERANDO_TAREAS_COMBO":
            tareas = [t.strip() for t in comando.split(',') if t.strip()]
            if not tareas:
                return {"nuevo_estado": estado_actual, "mensaje_para_ui": "Necesito al menos una tarea. Por favor, dame la lista de tareas."}
            
            random.shuffle(tareas)
            tareas_seleccionadas = tareas[:3]
            datos_combo["tareas_pendientes"] = tareas_seleccionadas
            
            orden_texto = "\n".join([f"{i+1}. {tarea}" for i, tarea in enumerate(tareas_seleccionadas)])
            mensaje = f"Perfecto. He establecido el siguiente orden aleatorio para tus contratos:\n\n{orden_texto}\n\nPresiona Enter o di 'continuar' para empezar a configurar el primer contrato: **{tareas_seleccionadas[0]}**."
            
            nuevo_estado = {"modo": "diseno_multiple", "paso_combo": "ESPERANDO_INICIO_CREACION", "datos_combo": datos_combo}
            return {"nuevo_estado": nuevo_estado, "mensaje_para_ui": mensaje}

        elif paso_combo == "ESPERANDO_INICIO_CREACION" or estado_actual.get("evento") == "CONTRATO_COMBO_FORJADO":
            if estado_actual.get("evento") == "CONTRATO_COMBO_FORJADO":
                datos_combo = estado_actual["datos_combo"]
                datos_combo["indice_actual"] += 1

            indice = datos_combo["indice_actual"]
            tareas = datos_combo["tareas_pendientes"]

            if indice < len(tareas):
                mision_actual = tareas[indice]
                datos_plan = {"mision": mision_actual, "en_combo": True}
                
                nuevo_estado = {
                    "modo": "diseño", 
                    "paso_diseno": "ESPERANDO_ESPECIFICACION",
                    "datos_plan": datos_plan,
                    "estado_combo_padre": {"modo": "diseno_multiple", "paso_combo": paso_combo, "datos_combo": datos_combo}
                }
                mensaje = f"**Configurando Contrato {indice + 1}/{len(tareas)}: {mision_actual}**\n\n¿Necesitas especificar más esta misión?"
                return {"nuevo_estado": nuevo_estado, "mensaje_para_ui": mensaje}
            else:
                mensaje_final = f"¡Combo completado! Se han forjado {len(tareas)} contratos con éxito. Guardián en espera."
                return {"nuevo_estado": {"modo": "libre"}, "mensaje_para_ui": mensaje_final}
        
        return {"nuevo_estado": {"modo": "libre"}, "mensaje_para_ui": "Error en el flujo de Diseño Múltiple. Reiniciando."}

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
        comando = datos.get("comando", "").strip()
        comando_lower = comando.lower()

        # --- GESTIÓN DE COMANDOS UNIVERSALES ---
        if comando_lower == "cancelar":
            return {"nuevo_estado": {"modo": "libre"}, "mensaje_para_ui": "Operación cancelada. Guardián en espera."}

        if comando == "_SALUDO_INICIAL_":
            return {"nuevo_estado": {"modo": "libre"}, "mensaje_para_ui": "Guardián online. Para iniciar, di 'Activar [modo]'."}

        # --- GESTIÓN DE MODOS ACTIVOS ---
        if estado.get("estado_combo_padre"):
            respuesta_diseno = self._gestionar_diseno(estado, comando)
            if respuesta_diseno.get("evento") == "CONTRATO_COMBO_FORJADO":
                estado_combo = estado["estado_combo_padre"]
                estado_combo["evento"] = "CONTRATO_COMBO_FORJADO"
                return self._gestionar_diseno_multiple(estado_combo, comando)
            return respuesta_diseno

        if estado.get("modo") == "diseño":
            return self._gestionar_diseno(estado, comando)
        
        if estado.get("modo") == "diseno_multiple":
            return self._gestionar_diseno_multiple(estado, comando)
        
        if estado.get("modo") == "ticket":
            if estado.get("paso_ticket") == "ESPERANDO_DETALLES":
                return self._emitir_ticket(comando)
            elif estado.get("paso_ticket") == "ESPERANDO_ENCADENAR":
                if any(palabra in comando_lower for palabra in self.PALABRAS_SI):
                    nuevo_estado = {"modo": "ticket", "paso_ticket": "ESPERANDO_DETALLES"}
                    return {"nuevo_estado": nuevo_estado, "mensaje_para_ui": "Genial. Dame los detalles del siguiente ticket."}
                else:
                    return {"nuevo_estado": {"modo": "libre"}, "mensaje_para_ui": "Entendido. Guardián en espera."}
            return {"nuevo_estado": {"modo": "libre"}, "mensaje_para_ui": "Error en el flujo de Ticket. Reiniciando."}

        # --- LÓGICA DE ACTIVACIÓN DE MODOS (SOLO SI NO HAY UN MODO ACTIVO) ---
        if comando_lower.startswith("activar"):
            palabras_clave_diseno = ["diseño", "contrato", "forjar", "crear", "ruleta"]
            comando_sin_activar = comando_lower.replace("activar", "").strip()

            # Prioridad 1: Ticket de Acción
            if comando_sin_activar.startswith("ticket"):
                nuevo_estado = {"modo": "ticket", "paso_ticket": "ESPERANDO_DETALLES"}
                return {"nuevo_estado": nuevo_estado, "mensaje_para_ui": "Genial, creando ticket. Dame los detalles."}

            # Prioridad 2: Diseño Múltiple
            if any(palabra in comando_sin_activar for palabra in self.PALABRAS_DISENO_MULTIPLE):
                return self._gestionar_diseno_multiple({"modo": "diseno_multiple"}, comando)

            # Prioridad 3: Diseño Simple (y recuperación por ID)
            if any(palabra in comando_sin_activar for palabra in palabras_clave_diseno):
                match_id = re.search(r'([A-Z]{4,5}-[A-Z0-9]{4})', comando, re.IGNORECASE)
                if match_id:
                    item_id = match_id.group(1).upper()
                    item = self.archivador_contratos.get(item_id)
                    if item:
                        if item.get("tipo") == "Ticket":
                            item_texto = (
                                f"**TICKET RECUPERADO**\n--------------------\n"
                                f"**ID:** {item['id']}\n"
                                f"**Tarea:** {item['tarea']}\n"
                                f"**Arranque:** {item.get('arranque', 'No definido')}\n"
                                f"**Duración:** {item.get('duracion', 'No definida')}\n"
                                f"**Emitido:** {item['fecha_emision']} a las {item['hora_emision']}\n--------------------"
                            )
                        else: # Es un Contrato
                            item_texto = (
                                f"**CONTRATO RECUPERADO**\n--------------------\n"
                                f"**Misión:** {item['mision']}\n"
                                f"**Arranque:** {item['arranque']}\n"
                                f"**Duración:** {item['duracion']}\n"
                                f"**Sellado:** {item['fecha_sellado']} a las {item['hora_sellado']}\n"
                                f"**Identificador:** {item['id']}\n--------------------"
                            )
                        return {"nuevo_estado": {"modo": "libre"}, "mensaje_para_ui": item_texto}
                    else:
                        return {"nuevo_estado": {"modo": "libre"}, "mensaje_para_ui": f"No se encontró ningún item con el identificador {item_id}."}

                nuevo_estado = {"modo": "diseño", "paso_diseno": "ESPERANDO_MISION", "datos_plan": {}}
                return {"nuevo_estado": nuevo_estado, "mensaje_para_ui": "Modo Diseño activado. Define la misión."}

        # --- MODO CHARLA POR DEFECTO ---
        respuesta_conversacional = await self._gestionar_charla_ia(comando)
        return {"nuevo_estado": {"modo": "libre"}, "mensaje_para_ui": respuesta_conversacional}
