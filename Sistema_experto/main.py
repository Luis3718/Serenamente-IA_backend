from reglas.inferencia import evaluar_paciente

def solicitar_datos():
    ansiedad = int(input("Ansiedad (0-63): "))
    depresion = int(input("Depresión (0-63): "))
    estres = int(input("Estrés (0-56): "))
    bienestar = int(input("Bienestar (0-100): "))
    mindfulness = float(input("Mindfulness (0.0-10.0): "))
    suicida = [input(f"Pregunta {i+1} (si/no): ").lower() for i in range(6)]
    ent = input("¿Tiene ENTs? (si/no): ").lower()

    return {
        "ansiedad": ansiedad,
        "depresion": depresion,
        "estres": estres,
        "bienestar": bienestar,
        "mindfulness": mindfulness,
        "suicida": suicida,
        "ent": ent
    }

if __name__ == "__main__":
    datos = solicitar_datos()
    resultado = evaluar_paciente(datos)

    print("\n--- RESULTADO ---")
    if resultado.get("Canalizado"):
        print("PACIENTE CANALIZADO:")
        print(f"Motivo: {resultado['razon']}")
    else:
        print(f"Nivel de intervención: {resultado['nivel_intervencion']}")
        print(f"Subcategoría: {resultado['subcategoria']}")
        print(f"Ansiedad: {resultado['ansiedad_escala']}, Depresión: {resultado['depresion_escala']}")
        print(f"Estrés: {resultado['estres_escala']}, Bienestar: {resultado['bienestar_escala']}")

    print("\n--- LOG DE DECISIONES ---")
    for linea in resultado["log"]:
        print(" -", linea)