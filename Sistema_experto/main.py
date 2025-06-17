import requests
from reglas.inferencia import evaluar_paciente

def obtener_datos_desde_api(id_paciente):
    try:
        url = f"http://localhost:8002te/{id_paciente}/datos_expertos"
        response = requests.get(url)
        response.raise_for_status()
        return response.json()
    except requests.RequestException as e:
        print("❌ Error al obtener datos del paciente:", e)
        return None

if __name__ == "__main__":
    id_paciente = int(input("🔍 Ingrese el ID del paciente: "))
    datos = obtener_datos_desde_api(id_paciente)

    if not datos:
        print("No se pudo recuperar la información del paciente.")
    else:
        resultado = evaluar_paciente(datos)

        print("\n--- RESULTADO ---")
        if resultado.get("Canalizado"):
            print("🚨 PACIENTE CANALIZADO:")
            print(f"Motivo: {resultado['razon']}")
        else:
            print("✅ Evaluación completada:")
            print(f"Nivel de intervención: {resultado['nivel_intervencion']}")
            print(f"Subcategoría: {resultado['subcategoria']}")
            print(f"Ansiedad: {resultado['ansiedad_escala']}, Depresión: {resultado['depresion_escala']}")
            print(f"Estrés: {resultado['estres_escala']}, Bienestar: {resultado['bienestar_escala']}")

        print("\n--- LOG DE DECISIONES ---")
        for linea in resultado["log"]:
            print(" -", linea)
