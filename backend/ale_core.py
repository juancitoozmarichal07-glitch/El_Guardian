# ale_core.py (VERSIÓN ESTABLE Y DEFINITIVA)

class ALE_Core:
    def __init__(self):
        self.skillsets = {}
        print("⚡ A.L.E. Core v3.0 (Arquitectura de Directorio) inicializado.")

    def cargar_skillset(self, nombre, skillset):
        self.skillsets[nombre] = skillset
        print(f"✅ Skillset '{nombre}' cargado y listo para recibir peticiones.")

    async def procesar_peticion(self, datos_peticion):
        # 1. Lee el identificador para saber a qué skillset llamar.
        skillset_nombre = datos_peticion.get("skillset_target")

        if not skillset_nombre:
            return {"error": "Petición inválida. No se especificó un 'skillset_target'."}

        # 2. Busca el skillset solicitado en la biblioteca.
        skillset_a_usar = self.skillsets.get(skillset_nombre)
            
        if not skillset_a_usar:
            return {"error": f"Skillset '{skillset_nombre}' no encontrado o no cargado."}
            
        # 3. Pasa la petición al skillset correcto.
        print(f"--> Petición recibida para el skillset: '{skillset_nombre}'")
        return await skillset_a_usar.ejecutar(datos_peticion)
