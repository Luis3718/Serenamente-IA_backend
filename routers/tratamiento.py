from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from datetime import date
from typing import List
from database import get_db
from models import (
    Paciente, Tratamiento, Paciente_Tratamiento, Habilidad, 
    Tratamiento_Habilidad_Actividad, Paciente_Habilidad, Actividad, ProgresoPaciente
)
from schemas import HabilidadBase, ActividadBase, ProgresoResponse
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

@router.get("/ruta_actividad/{id_tratamiento}/habilidad/{id_habilidad}", response_model=List[ActividadBase])
def get_actividades_tratamiento_habilidad(id_tratamiento: int, id_habilidad: int, db: Session = Depends(get_db)):
    actividades = db.query(Actividad).\
    join(Tratamiento_Habilidad_Actividad, Tratamiento_Habilidad_Actividad.ID_Actividad == Actividad.ID_Actividad).\
    filter(Tratamiento_Habilidad_Actividad.ID_Tratamiento == id_tratamiento,
            Tratamiento_Habilidad_Actividad.ID_Habilidad == id_habilidad).all()

    if not actividades:
        raise HTTPException(status_code=404, detail="No se encontraron actividades para esta habilidad en este tratamiento")

    return actividades

@router.post("/asignar_habilidad_actividad/{paciente_id}/{tratamiento_id}")
def asignar_habilidad_actividad(paciente_id: int, tratamiento_id: int, db: Session = Depends(get_db)):
    # Verificar si el paciente existe
    paciente = db.query(Paciente).filter(Paciente.ID_Paciente == paciente_id).first()
    if not paciente:
        raise HTTPException(status_code=404, detail="Paciente no encontrado")

    # Buscar la primera habilidad y actividad para el tratamiento especificado
    th_actividad = db.query(Tratamiento_Habilidad_Actividad).\
        join(Habilidad, Tratamiento_Habilidad_Actividad.ID_Habilidad == Habilidad.ID_Habilidad).\
        join(Actividad, Tratamiento_Habilidad_Actividad.ID_Actividad == Actividad.ID_Actividad).\
        filter(Tratamiento_Habilidad_Actividad.ID_Tratamiento == tratamiento_id).\
        first()

    if not th_actividad:
        raise HTTPException(status_code=404, detail="No se encontraron habilidades y actividades para este tratamiento")

    # Actualizar o crear un registro en ProgresoPaciente
    progreso = db.query(ProgresoPaciente).filter(ProgresoPaciente.ID_Paciente == paciente_id).first()
    if not progreso:
        progreso = ProgresoPaciente(
            ID_Paciente=paciente_id,
            ID_Tratamiento=tratamiento_id,
            ID_Habilidad=th_actividad.ID_Habilidad,
            ID_Actividad=th_actividad.ID_Actividad,
            FechaInicio=date.today()
        )
        db.add(progreso)
    else:
        progreso.ID_Tratamiento = tratamiento_id
        progreso.ID_Habilidad = th_actividad.ID_Habilidad
        progreso.ID_Actividad = th_actividad.ID_Actividad
        progreso.FechaInicio = date.today()

    db.commit()
    return {"message": "Habilidad y actividad asignadas correctamente, progreso actualizado"}

@router.get("/progreso/{paciente_id}", response_model=ProgresoResponse)
def get_progreso_paciente(paciente_id: int, db: Session = Depends(get_db)):
    # Realizar la consulta uniendo las tablas necesarias para obtener toda la información
    progreso = db.query(
        ProgresoPaciente.ID_Paciente,
        ProgresoPaciente.ID_Tratamiento,
        ProgresoPaciente.ID_Habilidad,
        ProgresoPaciente.ID_Actividad,
        ProgresoPaciente.FechaInicio,
        Habilidad.Nombre.label('Nombre_Habilidad'),
        Actividad.Nombre.label('Nombre_Actividad')
    ).join(
        Habilidad, ProgresoPaciente.ID_Habilidad == Habilidad.ID_Habilidad
    ).join(
        Actividad, ProgresoPaciente.ID_Actividad == Actividad.ID_Actividad
    ).filter(
        ProgresoPaciente.ID_Paciente == paciente_id
    ).first()

    if not progreso:
        raise HTTPException(status_code=404, detail="Progreso del paciente no encontrado")

    return progreso