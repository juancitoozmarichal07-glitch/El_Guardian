# =================================================================
# ALE_CORE.PY (v1.0 - ESTABLE)
# =================================================================
# Este es el motor central. Actúa como un recepcionista que dirige
# las peticiones al especialista (skillset) adecuado.

class ALE_Core:
    def __init__(self):
        """
        Inicializa el motor A.L.E. y prepara el diccionario
        para almacenar los skillsets que se carguen.
        """
        self._skillsets = {}
        print("✅ Motor A.L.E. Core v1.0 (Estable) inicializado.")

    def cargar_skillset(self, nombre, instancia_skillset):
        """
        Carga una instancia de un skillset en el motor.
        El 'nombre' es la clave que usará la PWA para llamar a este skillset.
        """
        self._skillsets[nombre] = instancia_skillset
        print(f"    -> Skillset '{nombre}' cargado en el motor.")

    async def procesar_peticion(self, datos_peticion):
        """
        El punto de entrada principal para todas las llamadas desde el main.py.
        Lee la petición, encuentra el skillset solicitado y le pasa el trabajo.
        """
        # Extrae el nombre del skillset que la PWA quiere usar.
        nombre_skillset = datos_peticion.get("skillset_target")

        if not nombre_skillset:
            return {"error": "Petición inválida: No se especificó un 'skillset_target'."}

        # Busca el skillset en el diccionario.
        skillset_seleccionado = self._skillsets.get(nombre_skillset)

        if not skillset_seleccionado:
            return {"error": f"Skillset '{nombre_skillset}' no encontrado o no cargado."}

        # Si lo encuentra, le pasa la petición completa para que la ejecute.
        # El skillset es quien decide qué hacer con los datos.
        try:
            # La función 'ejecutar' debe ser asíncrona en cada skillset.
            resultado = await skillset_seleccionado.ejecutar(datos_peticion)
            return resultado
        except Exception as e:
            print(f"🚨 ERROR al ejecutar el skillset '{nombre_skillset}': {e}")
            return {"error": f"Hubo un error interno en el skillset '{nombre_skillset}'."}

