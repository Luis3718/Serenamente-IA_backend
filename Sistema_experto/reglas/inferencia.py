from reglas.escalas import (
    escala_ansiedad,
    escala_depresion,
    escala_estres,
    escala_bienestar
)
from reglas.filtros import *

def evaluar_paciente(datos):
    log = []

    esc_bai = escala_ansiedad(datos["ansiedad"])
    esc_bdi = escala_depresion(datos["depresion"])
    esc_pss = escala_estres(datos["estres"])
    esc_bi = escala_bienestar(datos["bienestar"])

    log.append(f"Escala Ansiedad: {esc_bai}")
    log.append(f"Escala Depresión: {esc_bdi}")
    log.append(f"Escala Estrés: {esc_pss}")
    log.append(f"Escala Bienestar: {esc_bi}")

    canal = filtro_1_canalizacion(esc_bai, esc_bdi, datos["suicida"], log)
    if canal:
        return canal

    if si_ents(datos["ent"]):
        log.append("ENT detectada: intervención intensa aplicada directamente")
        return {
            "Canalizado": False,
            "nivel_intervencion": "Intenso",
            "subcategoria": "No aplica por ENTs",
            "log": log
        }

    alerta = b_alerta(esc_bai, esc_bdi)
    if alerta:
        log.append("Alerta por BAI o BDI en 75")

    total = filtro_3_perfil_afectacion(esc_bai, esc_bdi, esc_pss, esc_bi)
    log.append(f"Puntaje total combinado: {total}")

    subcat = filtro_4_subcategoria(total)
    log.append(f"Subcategoría de afectación: {subcat}")

    mini = filtro_5_suicida(datos["suicida"])
    log.append(f"Riesgo suicida detectado: {mini}")

    maas = filtro_6_maas(datos["mindfulness"])
    log.append(f"Actitud mindfulness: {maas}")

    nivel = reglas_sub(subcat, mini, maas, alerta)
    log.append(f"Nivel de intervención sugerido: {nivel}")

    return {
        "Canalizado": False,
        "ansiedad_escala": esc_bai,
        "depresion_escala": esc_bdi,
        "estres_escala": esc_pss,
        "bienestar_escala": esc_bi,
        "subcategoria": subcat,
        "riesgo_suicida": mini,
        "actitud_mindfulness": maas,
        "nivel_intervencion": nivel,
        "alerta": alerta,
        "log": log
    }
