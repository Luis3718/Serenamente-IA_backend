from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from database import get_db
from schemas import RespuestaCreate, ResultadoCreate
from models import Formulario, Respuesta, Resultado

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
        if respuesta.Respuesta in [2, 3]:  # Asume que las respuestas están guardadas como enteros
            return {"status": "No apto", "message": "El paciente tiene respuestas que indican no aptitud."}

    if not respuestas:
        raise HTTPException(status_code=404, detail="No se encontraron respuestas para el paciente especificado")

    return {"status": "Apto", "message": "El paciente no tiene respuestas críticas."}
