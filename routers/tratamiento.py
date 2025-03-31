from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from database import get_db
from models import Paciente, Paciente_Tratamiento
import random

router = APIRouter(
    prefix="/tratamiento",
    tags=["Tratamiento"]
)

@router.post("/asignar_protocolo/{paciente_id}")
def asignar_tratamiento(paciente_id: int, db: Session = Depends(get_db)):
    paciente = db.query(Paciente).filter(Paciente.ID_Paciente == paciente_id).first()
    if not paciente:
        raise HTTPException(status_code=404, detail="Paciente no encontrado")

    # Asignar un ID de tratamiento aleatorio entre 1 y 3
    tratamiento_id = random.randint(1, 3)

    # Crear una instancia de Paciente_Tratamiento
    nuevo_tratamiento = Paciente_Tratamiento(
        ID_Paciente=paciente_id,
        ID_Tratamiento=tratamiento_id,
        FechaInicio=date.today()  # Asumiendo que tienes esta columna para registrar la fecha de inicio
    )
    db.add(nuevo_tratamiento)
    db.commit()
    return {"message": "Tratamiento asignado correctamente", "ID_Tratamiento": tratamiento_id}

