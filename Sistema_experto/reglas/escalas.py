def escala_ansiedad(puntaje):
    if puntaje <= 13:
        return 25
    elif 14 <= puntaje <= 20:
        return 50
    elif 21 <= puntaje <= 31:
        return 75
    else:
        return 100

def escala_depresion(puntaje):
    return escala_ansiedad(puntaje)

def escala_estres(puntaje):
    if puntaje <= 18:
        return 22
    elif 19 <= puntaje <= 37:
        return 43
    else:
        return 65

def escala_bienestar(puntaje):
    if puntaje <= 40:
        return 65
    elif 41 <= puntaje <= 60:
        return 43
    else:
        return 22
