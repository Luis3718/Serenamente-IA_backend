from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from datetime import date
from typing import List
from database import get_db
from models import Paciente, Tratamiento, Habilidad, Actividad, Paciente_Habilidad, Paciente_Actividad, Paciente_Tratamiento, Tratamiento_Habilidad_Actividad
from schemas import HabilidadBase
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
        FechaInicio=date.today()  
    )
    db.add(nuevo_tratamiento)
    db.commit()
    return {"message": "Tratamiento asignado correctamente", "ID_Tratamiento": tratamiento_id}

@router.get("/buscar_protocolo/{paciente_id}")
def get_tratamiento_paciente(paciente_id: int, db: Session = Depends(get_db)):
    # Obtener el registro de tratamiento del paciente
    paciente_tratamiento = db.query(Paciente_Tratamiento).filter(Paciente_Tratamiento.ID_Paciente == paciente_id).first()
    if not paciente_tratamiento:
        raise HTTPException(status_code=404, detail="Tratamiento no encontrado para el paciente")
    # Obtener el tratamiento asociado
    tratamiento = db.query(Tratamiento).filter(Tratamiento.ID_Tratamiento == paciente_tratamiento.ID_Tratamiento).first()
    if not tratamiento:
        raise HTTPException(status_code=404, detail="Tratamiento no encontrado")

    return tratamiento

@router.get("/ruta_habilidades/{id_tratamiento}", response_model=List[HabilidadBase])
def get_habilidades_tratamiento(id_tratamiento: int, db: Session = Depends(get_db)):
    habilidades = db.query(Habilidad).join(
        Tratamiento_Habilidad_Actividad,
        Tratamiento_Habilidad_Actividad.ID_Habilidad == Habilidad.ID_Habilidad
    ).filter(
        Tratamiento_Habilidad_Actividad.ID_Tratamiento == id_tratamiento
    ).all()
    if not habilidades:
        raise HTTPException(status_code=404, detail="No se encontraron habilidades para este tratamiento")
    return habilidades