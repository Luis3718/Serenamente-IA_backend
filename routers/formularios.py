from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from database import get_db
from schemas import RespuestaCreate, CalificacionCreate
from models import Formulario, Respuesta, Calificacion

router = APIRouter(
    prefix="/formularios",
    tags=["Formularios"]
)

@router.post("/respuestas")
def almacenar_respuestas_y_calificacion(data: dict, db: Session = Depends(get_db)):
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
    
    # Almacenar la calificación
    nueva_calificacion = Calificacion(
        ID_Formulario=nuevo_formulario.ID_Formulario,
        Puntuacion=total_score,
        Categoria=category
    )
    db.add(nueva_calificacion)
    db.commit()

    return {"message": "Formulario y respuestas almacenadas correctamente"}
