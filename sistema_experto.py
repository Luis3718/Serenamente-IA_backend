def escala_ansiedad(puntaje): 
    if puntaje <= 13: return 25 
    elif 14 <= puntaje <= 20: return 50 
    elif 21 <= puntaje <= 31: return 75 
    else: return 100

def escala_depresion(puntaje): return escala_ansiedad(puntaje)

def escala_estres(puntaje): 
    if puntaje <= 18: return 22 
    elif 19 <= puntaje <= 37: return 43 
    else: return 65

def escala_bienestar(puntaje): 
    if puntaje <= 40: return 22 
    elif 41 <= puntaje <= 60: return 43 
    else: return 65

def evaluar_paciente(datos): 
    esc_bai = escala_ansiedad(datos["ansiedad"]) 
    esc_bdi = escala_depresion(datos["depresion"]) 
    esc_pss = escala_estres(datos["estres"]) 
    esc_bi = escala_bienestar(datos["bienestar"]) 
    maas = datos["mindfulness"] 
    suicida = datos["suicida"] 
    ent = datos["ent"]

    # Reglas 1-2: Canalización por severidad
    if esc_bai == 100:
        return {"Canalizado": True, "razon": "Ansiedad severa (Regla 1)"}
    if esc_bdi == 100:
        return {"Canalizado": True, "razon": "Depresión severa (Regla 2)"}

    # Regla 3-5: Nivel intenso inmediato
    if esc_bai == 75 or esc_bdi == 75 or ent == "si":
        return {
            "Canalizado": False,
            "ansiedad_escala": esc_bai,
            "depresion_escala": esc_bdi,
            "estres_escala": esc_pss,
            "bienestar_escala": esc_bi,
            "subcategoria": "Filtro 1",
            "nivel_intervencion": "Intenso"
        }
        

    # Regla 6: Continuar a suma de escalas
    total = esc_bai + esc_bdi + esc_pss + esc_bi

    if total <= 139:
        subcat = "Baja"
    elif total <= 186:
        subcat = "Media"
    elif total <= 233:
        subcat = "Alta"
    else:
        subcat = "Muy Alta"

    # Regla 11: Si es Muy Alta → Intenso directo
    if subcat == "Muy Alta":
        return {"Canalizado": False, "nivel_intervencion": "Intenso", "subcategoria": subcat}

    # Evaluación de riesgo suicida
    riesgo_suicida = "sin riesgo"
    if suicida[0] == "si" or suicida[1] == "si" or suicida[5] == "si":
        riesgo_suicida = "riesgo leve"

    # Reglas suicida predominan
    if subcat == "Alta":
        if riesgo_suicida == "riesgo leve":
            nivel = "Intenso"
        else:
            nivel = "Moderado"
    elif subcat == "Media":
        if riesgo_suicida == "riesgo leve":
            nivel = "Intenso"
        else:
            # Filtro con Mindfulness
            if maas >= 8.0:
                nivel = "Leve"
            else:
                nivel = "Moderado"
    elif subcat == "Baja":
        if riesgo_suicida == "riesgo leve":
            nivel = "Moderado"
        else:
            if maas >= 8.0:
                nivel = "Leve"
            else:
                nivel = "Moderado"

    return {
        "Canalizado": False,
        "ansiedad_escala": esc_bai,
        "depresion_escala": esc_bdi,
        "estres_escala": esc_pss,
        "bienestar_escala": esc_bi,
        "subcategoria": subcat,
        "nivel_intervencion": nivel
    }

def solicitar_datos(): 
    ansiedad = int(input("Puntaje de ANSIEDAD (0-63): "))
    depresion = int(input("Puntaje de DEPRESIÓN (0-63): ")) 
    estres = int(input("Puntaje de ESTRÉS (0-56): ")) 
    bienestar = int(input("Puntaje de BIENESTAR (0-100): ")) 
    mindfulness = float(input("Puntaje de MINDFULNESS (0.0-10.0): "))

    print("\nContesta las preguntas de Riesgo Suicida (si/no):")
    suicida = []
    for i in range(1,7):
        respuesta = input(f"Respuesta a Pregunta {i}: ").strip().lower()
        suicida.append(respuesta)

    ent = input("\n¿Tiene alguna Enfermedad No Transmisible? (si/no): ").strip().lower()

    return {
        "ansiedad": ansiedad,
        "depresion": depresion,
        "estres": estres,
        "bienestar": bienestar,
        "mindfulness": mindfulness,
        "suicida": suicida,
        "ent": ent
    }
       
    if resultado.get("Canalizado"):
        print("\n--- RESULTADO ---")
        print("Paciente CANALIZADO fuera del sistema.")
        print(f"Motivo: {resultado.get('razon', 'Canalización inmediata')}")
    else:
        print("\n--- RESULTADO ---")
        print(f"Escala Ansiedad: {resultado['ansiedad_escala']}")
        print(f"Escala Depresión: {resultado['depresion_escala']}")
        print(f"Escala Estrés: {resultado['estres_escala']}")
        print(f"Escala Bienestar: {resultado['bienestar_escala']}")
        print(f"Subcategoría de afectación: {resultado['subcategoria']}")
        print(f"Nivel de intervención recomendado: {resultado['nivel_intervencion']}")

if __name__ == "__main__":
    datos = solicitar_datos() 
    resultado = evaluar_paciente(datos)
