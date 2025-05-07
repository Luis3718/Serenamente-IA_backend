def filtro_1_canalizacion(bai, bdi, suicida, log):
    if bai == 100:
        log.append("Canalización inmediata: BAI severo (Regla 1)")
        return {"Canalizado": True, "razon": "BAI severo (Regla 1)", "log": log}
    if bdi == 100:
        log.append("Canalización inmediata: BDI severo (Regla 2)")
        return {"Canalizado": True, "razon": "BDI severo (Regla 2)", "log": log}
    if suicida[2] == "si" or suicida[3] == "si" or suicida[4] == "si":
        log.append("Canalización inmediata: Riesgo suicida (MINI 3/4/5)")
        return {"Canalizado": True, "razon": "Riesgo suicida relevante (MINI 3/4/5)", "log": log}
    return None

def b_alerta(bai, bdi):
    return bai == 75 or bdi == 75

def si_ents(ent):
    return ent == "si"

def filtro_3_perfil_afectacion(bai, bdi, pss, bi):
    return bai + bdi + pss + bi

def filtro_4_subcategoria(total):
    if total <= 139:
        return "Bajo"
    elif total <= 186:
        return "Medio"
    elif total <= 233:
        return "Alto"
    else:
        return "Muy Alto"

def filtro_5_suicida(suicida):
    if suicida[0] == "si" or suicida[1] == "si" or suicida[5] == "si":
        return "leve"
    return "sin riesgo"

def filtro_6_maas(maas):
    return "buena" if maas >= 8.0 else "no buena"

def reglas_sub(subcat, mini, maas, alerta):
    if subcat == "Muy Alto":
        return "Intenso"
    if subcat == "Alto":
        if mini == "leve":
            return "Intenso"
        elif mini == "sin riesgo":
            if maas == "no buena":
                return "Intenso"
            else:
                return "Moderado"
    if subcat == "Medio":
        if mini == "leve":
            if maas == "buena":
                return "Moderado"
            else:
                return "Intenso"
        elif mini == "sin riesgo":
            if maas == "buena":
                return "Leve"
            else:
                return "Moderado"
    if subcat == "Bajo":
        if mini == "leve":
            return "Moderado"
        elif mini == "sin riesgo":
            if maas == "no buena":
                return "Moderado"
            else:
                return "Leve"
    return "Indefinido"
