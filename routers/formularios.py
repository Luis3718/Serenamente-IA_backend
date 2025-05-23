from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from datetime import datetime, date
from database import get_db
from schemas import respuesta_create, resultado_create
from Sistema_experto.reglas.inferencia import evaluar_paciente
from models import (
    formulario as Formulario,
    respuesta as Respuesta,
    resultado as Resultado,
    paciente as Paciente,
    asignacion_sistema_experto,
    paciente_tratamiento as Paciente_Tratamiento
)

router = APIRouter(
    prefix="/formularios",
    tags=["Formularios"]
)

@router.post("/respuestas")
def almacenar_respuestas_y_resultado(data: dict, db: Session = Depends(get_db)):
    form_type = data['formType']
    total_score = data['totalScore']
    category = data['category']
    responses = data['responses']

    nuevo_formulario = Formulario(
        id_paciente=data['ID_Paciente'],
        id_tipoformulario=form_type
    )
    db.add(nuevo_formulario)
    db.commit()
    db.refresh(nuevo_formulario)

    # Almacenar cada respuesta
    for response in responses:
        nueva_respuesta = Respuesta(
            id_paciente=data['ID_Paciente'],
            id_pregunta=response['question'],
            respuesta=response['answer']
        )
        db.add(nueva_respuesta)

    nueva_resultado = Resultado(
        id_formulario=nuevo_formulario.id_formulario,
        puntuacion=total_score,
        categoria=category
    )
    db.add(nueva_resultado)
    db.commit()

    return {"message": "Formulario y respuestas almacenadas correctamente"}

@router.get("/categorias/{id_paciente}")
def obtener_categorias(id_paciente: int, db: Session = Depends(get_db)):
    ids_tipo_formulario = [1, 2, 4, 5]

    resultados = db.query(Resultado, Formulario)\
        .join(Formulario, Formulario.id_formulario == Resultado.id_formulario)\
        .filter(Formulario.id_paciente == id_paciente)\
        .filter(Formulario.id_tipoformulario.in_(ids_tipo_formulario))\
        .all()

    categorias = [
        {
            "ID_Formulario": formulario.id_formulario,
            "ID_TipoFormulario": formulario.id_tipoformulario,
            "Categoria": resultado.categoria
        }
        for resultado, formulario in resultados
    ]

    if not categorias:
        raise HTTPException(status_code=404, detail="Resultados no encontrados para el paciente especificado")

    return categorias

@router.post("/contestar_pretest/{id_paciente}")
def entrevista_contestada(id_paciente: int, db: Session = Depends(get_db)):
    paciente = db.query(Paciente).filter_by(id_paciente=id_paciente).first()
    if not paciente:
        raise HTTPException(status_code=404, detail="Paciente no encontrado")
    
    paciente.formulario_contestado = True
    db.commit()
    return {"message": "Pre-test marcado como contestado"}

@router.post("/contestar_entrevista/{id_paciente}")
def entrevista_contestada(id_paciente: int, db: Session = Depends(get_db)):
    paciente = db.query(Paciente).filter_by(id_paciente=id_paciente).first()
    if not paciente:
        raise HTTPException(status_code=404, detail="Paciente no encontrado")
    
    paciente.entrevista_contestada = True
    db.commit()
    return {"message": "Entrevista marcada como contestada"}

@router.get("/evaluar_paciente/{id_paciente}")
def evaluar_paciente(id_paciente: int, db: Session = Depends(get_db)):
    ids_preguntas = [30]

    # Realizar la consulta para obtener las respuestas del paciente a las preguntas específicas
    respuestas = db.query(Respuesta)\
        .filter(Respuesta.id_paciente == id_paciente, Respuesta.id_pregunta.in_(ids_preguntas))\
        .all()
    
    # Evaluar las respuestas
    for respuesta in respuestas:
        if respuesta.respuesta in ['2', '3']:
            return {"status": "No apto", "message": "El paciente tiene respuestas que indican no aptitud."}

    # Consultar los resultados del formulario con ID 1 (Ansiedad) para este paciente
    resultado = db.query(Resultado)\
        .join(Formulario, Formulario.id_formulario == Resultado.id_formulario)\
        .filter(Formulario.id_formulario == 1, Formulario.id_paciente == id_paciente)\
        .first()

    # Verificar la categoría del resultado
    if resultado and resultado.categoria == "Severa":
        return {"status": "No apto", "message": "El paciente tiene un resultado severo en un formulario de ansiedad."}
    
    # Consultar los resultados del formulario con ID 2 (Depresion) para este paciente
    resultado = db.query(Resultado)\
        .join(Formulario, Formulario.id_formulario == Resultado.id_formulario)\
        .filter(Formulario.id_formulario == 2, Formulario.id_paciente == id_paciente)\
        .first()
    
    # Verificar la categoría del resultado
    if resultado and resultado.categoria == "Severa":
        return {"status": "No apto", "message": "El paciente tiene un resultado severo en un formulario de depresion."}
    
    # Consultar los resultados del formulario con ID 3 (Riesgo Suicida) para este paciente
    resultado_form3 = db.query(Resultado)\
        .join(Formulario, Formulario.id_formulario == Resultado.id_formulario)\
        .filter(Formulario.id_formulario == 3, Formulario.id_paciente == id_paciente)\
        .first()

    # Consultar los resultados del formulario con ID 3 (Riesgo Suicida) para este paciente
    if resultado_form3 and resultado_form3.categoria in ["Moderado", "Severa"]:
        return {"status": "No apto", "message": "El paciente tiene un resultado moderado o severo en el formulario de riesgo suicida, lo cual excluye su aptitud."}

    if not respuestas and not resultado:
        raise HTTPException(status_code=404, detail="No se encontraron respuestas o resultados para el paciente especificado")

    paciente = db.query(Paciente).filter_by(id_paciente=id_paciente).first()
    if paciente:
        return {"status": "Apto", "message": "El paciente es apto y el formulario ha sido marcado como contestado."}
    else:
        raise HTTPException(status_code=404, detail="Paciente no encontrado")

@router.get("/datos_expertos/{id_paciente}")
def obtener_datos_expertos(id_paciente: int, db: Session = Depends(get_db)):
    TIPOS_FORM = {"ansiedad": 1, "depresion": 2, "estres": 5, "bienestar": 4, "mindfulness": 6}
    preguntas_suicidas = [43, 44, 45, 46, 47, 48]

    def obtener_puntaje(tipo):
        form = db.query(Formulario).filter(
            Formulario.id_paciente == id_paciente,
            Formulario.id_tipoformulario == tipo
        ).order_by(Formulario.id_formulario.desc()).first()
        if not form:
            return None
        resultado = db.query(Resultado).filter(Resultado.id_formulario == form.id_formulario).first()
        return resultado.puntuacion if resultado else None

    datos = {
        "ansiedad": obtener_puntaje(TIPOS_FORM["ansiedad"]),
        "depresion": obtener_puntaje(TIPOS_FORM["depresion"]),
        "estres": obtener_puntaje(TIPOS_FORM["estres"]),
        "bienestar": obtener_puntaje(TIPOS_FORM["bienestar"]),
        "mindfulness": float(obtener_puntaje(TIPOS_FORM["mindfulness"]) or 0.0),
        "suicida": [],
        "ent": "no"
    }

    for pid in preguntas_suicidas:
        r = db.query(Respuesta).filter(
            Respuesta.id_paciente == id_paciente,
            Respuesta.id_pregunta == pid
        ).order_by(Respuesta.id_respuesta.desc()).first()
        datos["suicida"].append(r.respuesta.lower() if r else "no")

    paciente = db.query(Paciente).filter(Paciente.id_paciente == id_paciente).first()
    if not paciente:
        raise HTTPException(status_code=404, detail="Paciente no encontrado")
    datos["ent"] = "no" if paciente.id_tipoent == 6 else "si"

    return {"id_paciente": id_paciente, **datos}

@router.post("/asignar_tratamiento")
def asignar_tratamiento(data: dict, db: Session = Depends(get_db)):
    from Sistema_experto.reglas.inferencia import evaluar_paciente

    resultado = evaluar_paciente(data)

    if resultado.get("Canalizado"):
        raise HTTPException(status_code=403, detail="Paciente requiere canalización clínica")

    nivel = resultado["nivel_intervencion"]
    log = resultado["log"]
    paciente_id = data.get("id_paciente")

    nivel_map = {"Leve": 1, "Moderado": 2, "Intenso": 3}
    id_tratamiento = nivel_map.get(nivel)

    if not id_tratamiento:
        raise HTTPException(status_code=400, detail="Nivel inválido")

    asignacion = asignacion_sistema_experto(
        id_paciente=paciente_id,
        id_tratamiento=id_tratamiento,
        log_sistema="\n".join(log)
    )

    db.add(asignacion)
    db.commit()
    db.refresh(asignacion)

    ya_asignado = db.query(Paciente_Tratamiento).filter(Paciente_Tratamiento.id_paciente == paciente_id).first()
    if ya_asignado:
        raise HTTPException(status_code=400, detail="El paciente ya tiene un tratamiento asignado")

    nuevo_tratamiento = Paciente_Tratamiento(
        id_paciente=paciente_id,
        id_tratamiento=id_tratamiento,
        fechainicio=date.today()
    )
    db.add(nuevo_tratamiento)
    db.commit()


    return {
        "mensaje": "Tratamiento asignado",
        "nivel": nivel,
        "id_tratamiento": id_tratamiento,
        "log": log
    }
