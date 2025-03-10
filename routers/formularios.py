from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from database import get_db
from schemas import RespuestaCreate, ResultadoCreate
from models import Formulario, Respuesta, Resultado, Paciente

router = APIRouter(
    prefix="/formularios",
    tags=["Formularios"]
)

@router.post("/respuestas")
def almacenar_respuestas_y_Resultado(data: dict, db: Session = Depends(get_db)):
    # Extraer la información del formulario del JSON
    form_type = data['formType']
    total_score = data['totalScore']
    category = data['category']
    responses = data['responses']
    
    # Crear una nueva entrada en la tabla Formularios
    nuevo_formulario = Formulario(ID_Paciente=data['ID_Paciente'], ID_TipoFormulario=form_type)
    db.add(nuevo_formulario)
    db.commit()
    db.refresh(nuevo_formulario)

    # Almacenar cada respuesta
    for response in responses:
        nueva_respuesta = Respuesta(
            ID_Paciente=data['ID_Paciente'],
            ID_Pregunta=response['question'],
            Respuesta=response['answer']
        )
        db.add(nueva_respuesta)
    
    # Almacenar la resultado
    nueva_Resultado = Resultado(
        ID_Formulario=nuevo_formulario.ID_Formulario,
        Puntuacion=total_score,
        Categoria=category
    )
    db.add(nueva_Resultado)
    db.commit()

    return {"message": "Formulario y respuestas almacenadas correctamente"}

@router.get("/categorias/{id_paciente}")
def obtener_categorias(id_paciente: int, db: Session = Depends(get_db)):
    # Definir los IDs de los formularios que quieres consultar
    ids_formulario = [1, 2, 4, 5]
    
    # Realizar la consulta para obtener las categorías basadas en los IDs de formulario y el ID del paciente
    resultados = db.query(Resultado)\
        .join(Formulario, Formulario.ID_Formulario == Resultado.ID_Formulario)\
        .filter(Resultado.ID_Formulario.in_(ids_formulario), Formulario.ID_Paciente == id_paciente)\
        .all()
    
    # Extraer y devolver las categorías
    categorias = [{"ID_Formulario": resultado.ID_Formulario, "Categoria": resultado.Categoria} for resultado in resultados]
    if not categorias:
        raise HTTPException(status_code=404, detail="Resultados no encontrados para el paciente especificado")

    return categorias

@router.post("/contestar_pretest/{id_paciente}")
def entrevista_contestada(id_paciente: int, db: Session = Depends(get_db)):
    paciente = db.query(Paciente).filter_by(ID_Paciente=id_paciente).first()
    if not paciente:
        raise HTTPException(status_code=404, detail="Paciente no encontrado")
    
    paciente.formulario_contestado = True
    db.commit()
    return {"message": "Pre-test marcado como contestado"}

@router.post("/contestar_entrevista/{id_paciente}")
def entrevista_contestada(id_paciente: int, db: Session = Depends(get_db)):
    paciente = db.query(Paciente).filter_by(ID_Paciente=id_paciente).first()
    if not paciente:
        raise HTTPException(status_code=404, detail="Paciente no encontrado")
    
    paciente.entrevista_contestada = True
    db.commit()
    return {"message": "Entrevista marcada como contestada"}

@router.get("/evaluar_paciente/{id_paciente}")
def evaluar_paciente(id_paciente: int, db: Session = Depends(get_db)):
    # Definir los IDs de las preguntas que quieres consultar
    ids_preguntas = [30]  # Aquí pones el ID de la pregunta que quieres evaluar

    # Realizar la consulta para obtener las respuestas del paciente a las preguntas específicas
    respuestas = db.query(Respuesta)\
        .filter(Respuesta.ID_Paciente == id_paciente, Respuesta.ID_Pregunta.in_(ids_preguntas))\
        .all()

    # Evaluar las respuestas
    for respuesta in respuestas:
        if respuesta.Respuesta in ['2', '3']:  # Asume que las respuestas están guardadas como enteros
            return {"status": "No apto", "message": "El paciente tiene respuestas que indican no aptitud."}

    # Consultar los resultados del formulario con ID 1 (Ansiedad) para este paciente
    resultado = db.query(Resultado)\
        .join(Formulario, Formulario.ID_Formulario == Resultado.ID_Formulario)\
        .filter(Formulario.ID_Formulario == 1, Formulario.ID_Paciente == id_paciente)\
        .first()

    # Verificar la categoría del resultado
    if resultado and resultado.Categoria == "Severa":
        return {"status": "No apto", "message": "El paciente tiene un resultado severo en un formulario de ansiedad."}

    # Consultar los resultados del formulario con ID 2 (Depresion) para este paciente
    resultado = db.query(Resultado)\
        .join(Formulario, Formulario.ID_Formulario == Resultado.ID_Formulario)\
        .filter(Formulario.ID_Formulario == 2, Formulario.ID_Paciente == id_paciente)\
        .first()

    # Verificar la categoría del resultado
    if resultado and resultado.Categoria == "Severa":
        return {"status": "No apto", "message": "El paciente tiene un resultado severo en un formulario de depresion."}

    # Consultar los resultados del formulario con ID 3 (Riesgo Suicida) para este paciente
    resultado_form3 = db.query(Resultado)\
        .join(Formulario, Formulario.ID_Formulario == Resultado.ID_Formulario)\
        .filter(Formulario.ID_Formulario == 3, Formulario.ID_Paciente == id_paciente)\
        .first()

    if resultado_form3 and resultado_form3.Categoria in ["Moderado", "Severa"]:
        return {"status": "No apto", "message": "El paciente tiene un resultado moderado o severo en el formulario de riesgo suicida, lo cual excluye su aptitud."}

    if not respuestas and not resultado:
        raise HTTPException(status_code=404, detail="No se encontraron respuestas o resultados para el paciente especificado")

    paciente = db.query(Paciente).filter_by(ID_Paciente=id_paciente).first()
    if paciente:
        return {"status": "Apto", "message": "El paciente es apto y el formulario ha sido marcado como contestado."}
    else:
        raise HTTPException(status_code=404, detail="Paciente no encontrado")
