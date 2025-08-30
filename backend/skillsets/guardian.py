# =================================================================
# Archivo: guardian.py
# Contiene la lógica completa y autocontenida para el Skillset del Guardián.
# Versión 5.1 - Jerarquía Estricta
# =================================================================

import json
import random
from datetime import datetime
import g4f
import asyncio

# --- Clase Principal del Skillset ---
class Guardian:
    def __init__(self):
        """
        El constructor se encarga de cargar los datos necesarios para que el Guardián opere.
        """
        self.archivo_contratos = 'contratos.json'
        self.archivo_estado = 'estado_guardian.json'
        self.contratos = self._cargar_json(self.archivo_contratos, [])
        self.estado = self._cargar_json(self.archivo_estado, {"ultima_interaccion": None, "historial_chat": []})
        self.historial_chat = self.estado.get("historial_chat", [])
        print(f"    - Especialista 'Guardian' v5.1 (Jerarquía Estricta) listo.")

    # --- Funciones de Utilidad Interna ---
    def _cargar_json(self, archivo, default):
        """Carga un archivo JSON de forma segura."""
        try:
            with open(archivo, 'r', encoding='utf-8') as f:
                return json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            return default

    def _guardar_estado(self):
        """Guarda el estado actual de la conversación y la última interacción."""
        self.estado["ultima_interaccion"] = datetime.now().isoformat()
        self.estado["historial_chat"] = self.historial_chat[-10:]
        with open(self.archivo_estado, 'w', encoding='utf-8') as f:
            json.dump(self.estado, f, indent=4, ensure_ascii=False)

    def _obtener_momento_del_dia(self):
        """Determina si es mañana, tarde o noche."""
        h = datetime.now().hour
        return "mañana" if 5 <= h < 12 else "tarde" if 12 <= h < 20 else "noche"

    # --- Módulo 1: Lógica de Saludo ---
    def _generar_saludo(self):
        """Crea el saludo inicial dependiendo de si es la primera visita del día."""
        self.historial_chat = self.estado.get("historial_chat", [])
        hoy = datetime.now().date()
        ultima_fecha = datetime.fromisoformat(self.estado["ultima_interaccion"]).date() if self.estado.get("ultima_interaccion") else None
        
        if ultima_fecha != hoy:
            return f"Hola. Bienvenido, Juan. ¿En qué te puedo ayudar en esta {self._obtener_momento_del_dia()}?"
        else:
            return "Hola Juan, bienvenido de vuelta. ¿Revisamos contratos, creamos uno nuevo o charlamos?"

    # --- Módulo 2: Lógica de IA Conversacional ---
    async def _gestionar_charla_ia(self, comando):
        """Maneja la conversación general usando un modelo de IA externo."""
        try:
            self.historial_chat.append({"role": "user", "content": comando})
            # LA NUEVA VERSIÓN A PRUEBA de ERRORES
respuesta_ia = await g4f.ChatCompletion.create_async(
    model=g4f.models.default,
    messages=[{"role": "user", "content": f"Eres el Guardián, una IA compañera de Juan. Eres directo, sabio y motivador. El usuario dice: '{comando}'"}]
)
            if not respuesta_ia: raise ValueError("Respuesta de IA vacía.")
            
            self.historial_chat.append({"role": "assistant", "content": respuesta_ia})
            self._guardar_estado()
            return respuesta_ia
        except Exception as e:
            print(f"Error en IA: {e}")
            self.historial_chat.pop()
            return "Mi núcleo cognitivo tuvo una sobrecarga. Inténtalo de nuevo."

    # --- Módulo 3: Lógica de Diseño de Contratos ---
        # --- Módulo 3: Lógica de Diseño de Contratos (v3.0 - Flexible y Completo) ---
    def _gestionar_diseno(self, estado, comando):
        """Maneja el flujo completo, permitiendo órdenes directas o ruletas con opciones."""
        paso_actual = estado.get("paso_diseno")
        datos_contrato = estado.get("datos_contrato", {})

        # --- 1. Inicio del Modo Diseño ---
        if estado.get("modo") != "diseño":
            nuevo_estado = {"modo": "diseño", "paso_diseno": "ESPERANDO_MISION", "datos_contrato": {"especificaciones": []}}
            mensaje = "Modo Diseño activado.\n\n**Paso 1: La Misión.**\nDefine la misión (una orden directa o varias opciones)."
            return {"nuevo_estado": nuevo_estado, "mensaje_para_ui": mensaje}

        # --- 2. Recibe Misión (Directa u Opciones) y ordena la ruleta ---
        if paso_actual == "ESPERANDO_MISION":
            opciones = [opt.strip() for opt in comando.split(',') if opt.strip()]
            if not opciones: return {"nuevo_estado": estado, "mensaje_para_ui": "No he detectado una orden válida."}
            
            nuevo_estado = estado.copy()
            nuevo_estado["paso_diseno"] = "ESPERANDO_ELECCION_MISION"
            return {"nuevo_estado": nuevo_estado, "accion_ui": "MOSTRAR_RULETA", "opciones_ruleta": opciones}

        # --- 3. Recibe la elección de la Misión y pide Especificación ---
        if paso_actual == "ESPERANDO_ELECCION_MISION":
            datos_contrato["mision"] = comando
            nuevo_estado = estado.copy()
            nuevo_estado["paso_diseno"] = "ESPERANDO_ESPECIFICACION"
            nuevo_estado["datos_contrato"] = datos_contrato
            mensaje = f"Misión aceptada: **{comando}**.\n\n**Siguiente Paso: Especificación.**\n¿Detalles? (orden directa, opciones o 'listo')."
            return {"nuevo_estado": nuevo_estado, "mensaje_para_ui": mensaje}

        # --- 4. Recibe Especificación (Directa, Opciones o 'listo') ---
        if paso_actual == "ESPERANDO_ESPECIFICACION":
            if comando.lower() == 'listo':
                nuevo_estado = estado.copy()
                nuevo_estado["paso_diseno"] = "ESPERANDO_HORARIO"
                mensaje = "Misión definida.\n\n**Siguiente Paso: Horario.**\nIndica la hora de inicio (directa u opciones)."
                return {"nuevo_estado": nuevo_estado, "mensaje_para_ui": mensaje}
            
            opciones = [opt.strip() for opt in comando.split(',') if opt.strip()]
            if not opciones: return {"nuevo_estado": estado, "mensaje_para_ui": "No he detectado una orden válida."}

            nuevo_estado = estado.copy()
            nuevo_estado["paso_diseno"] = "ESPERANDO_ELECCION_ESPECIFICACION"
            return {"nuevo_estado": nuevo_estado, "accion_ui": "MOSTRAR_RULETA", "opciones_ruleta": opciones}

        # --- 5. Recibe la elección de la Especificación y pide más ---
        if paso_actual == "ESPERANDO_ELECCION_ESPECIFICACION":
            datos_contrato.setdefault("especificaciones", []).append(comando)
            mision_completa = " -> ".join([datos_contrato["mision"]] + datos_contrato["especificaciones"])
            
            nuevo_estado = estado.copy()
            nuevo_estado["paso_diseno"] = "ESPERANDO_ESPECIFICACION"
            nuevo_estado["datos_contrato"] = datos_contrato
            
            mensaje = f"Detalle añadido: **{mision_completa}**.\n\n¿Otra capa de detalle? (orden, opciones o 'listo')."
            return {"nuevo_estado": nuevo_estado, "mensaje_para_ui": mensaje}

        # --- 6. Recibe Horario (Directo u Opciones) ---
        if paso_actual == "ESPERANDO_HORARIO":
            opciones = [opt.strip() for opt in comando.split(',') if opt.strip()]
            if not opciones: return {"nuevo_estado": estado, "mensaje_para_ui": "No he detectado una hora válida."}

            nuevo_estado = estado.copy()
            nuevo_estado["paso_diseno"] = "ESPERANDO_ELECCION_HORARIO"
            return {"nuevo_estado": nuevo_estado, "accion_ui": "MOSTRAR_RULETA", "opciones_ruleta": opciones}

        # --- 7. Recibe la elección del Horario y pide Duración ---
        if paso_actual == "ESPERANDO_ELECCION_HORARIO":
            datos_contrato["horario"] = comando
            nuevo_estado = estado.copy()
            nuevo_estado["paso_diseno"] = "ESPERANDO_DURACION"
            nuevo_estado["datos_contrato"] = datos_contrato
            mensaje = f"Hora de inicio: **{comando}**.\n\n**Paso Final: Duración.**\nDefine la duración (ej: 45 min)."
            return {"nuevo_estado": nuevo_estado, "mensaje_para_ui": mensaje}

        # --- 8. Recibe Duración (Directa u Opciones) y Sella el Contrato ---
        if paso_actual == "ESPERANDO_DURACION":
            opciones = [opt.strip() for opt in comando.split(',') if opt.strip()]
            if not opciones: return {"nuevo_estado": estado, "mensaje_para_ui": "No he detectado una duración válida."}

            nuevo_estado = estado.copy()
            nuevo_estado["paso_diseno"] = "ESPERANDO_ELECCION_DURACION"
            return {"nuevo_estado": nuevo_estado, "accion_ui": "MOSTRAR_RULETA", "opciones_ruleta": opciones}

        # --- 9. Sello Final del Contrato ---
        if paso_actual == "ESPERANDO_ELECCION_DURACION":
            datos_contrato["duracion"] = comando
            
            # Construimos el contrato final
            mision_final = " -> ".join([datos_contrato.get("mision", "N/A")] + datos_contrato.get("especificaciones", []))
            
            nuevo_contrato = {
                "id": int(datetime.now().timestamp() * 1000),
                "mision": mision_final,
                "horario": datos_contrato.get("horario", "N/A"),
                "duracion": datos_contrato.get("duracion", "N/A"),
                "estado": "agendado"
            }
            self.contratos.append(nuevo_contrato)
            # Aquí iría la función para guardar en contratos.json
            
            texto_contrato = (
                f"**CONTRATO FORJADO**\n"
                f"--------------------\n"
                f"**Misión:** {nuevo_contrato['mision']}\n"
                f"**Inicio:** {nuevo_contrato['horario']}\n"
                f"**Duración:** {nuevo_contrato['duracion']}\n"
                f"--------------------\n"
                f"El contrato ha sido sellado. Yo te avisaré."
            )
            
            # Reseteamos al modo libre
            return {"nuevo_estado": {"modo": "libre"}, "mensaje_para_ui": texto_contrato}

        # Fallback de seguridad
        return {"nuevo_estado": {"modo": "libre"}, "mensaje_para_ui": "Hubo un error en el flujo de diseño. Volviendo a modo charla."}
