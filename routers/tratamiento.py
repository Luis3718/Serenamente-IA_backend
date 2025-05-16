from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from datetime import date
from typing import List
from database import get_db
from models import (
    Paciente, Tratamiento, Paciente_Tratamiento, Habilidad, 
    Tratamiento_Habilidad_Actividad, Paciente_Habilidad, Paciente_Actividad, Actividad, ProgresoPaciente, 
    RespuestaActividad
)
from schemas import HabilidadBase, ActividadBase, ProgresoResponse, ActividadConID, RespuestaEntrada
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

    # Verificar si ya tiene un tratamiento asignado
    tratamiento_existente = db.query(Paciente_Tratamiento).filter(Paciente_Tratamiento.ID_Paciente == paciente_id).first()
    print(tratamiento_existente)
    if tratamiento_existente:
        raise HTTPException(status_code=400, detail="El paciente ya tiene un tratamiento asignado")

    # Asignar un ID de tratamiento aleatorio entre 1 y 3
    #tratamiento_id = random.randint(3, 3)
    tratamiento_id = 3

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

@router.get("/ruta_actividad/{id_tratamiento}/habilidad/{id_habilidad}", response_model=List[ActividadConID])
def get_actividades_tratamiento_habilidad(id_tratamiento: int, id_habilidad: int, db: Session = Depends(get_db)):
    actividades = db.query(Actividad).\
        join(Tratamiento_Habilidad_Actividad, Tratamiento_Habilidad_Actividad.ID_Actividad == Actividad.ID_Actividad).\
        filter(Tratamiento_Habilidad_Actividad.ID_Tratamiento == id_tratamiento,
               Tratamiento_Habilidad_Actividad.ID_Habilidad == id_habilidad).all()

    if not actividades:
        raise HTTPException(status_code=404, detail="No se encontraron actividades para esta habilidad en este tratamiento")

    return actividades

@router.get("/progreso/actividad_actual/{paciente_id}")
def obtener_actividad_actual(paciente_id: int, db: Session = Depends(get_db)):
    progreso = db.query(ProgresoPaciente).filter(ProgresoPaciente.ID_Paciente == paciente_id).first()
    if not progreso:
        raise HTTPException(status_code=404, detail="Progreso no encontrado")

    return {"id_actividad_actual": progreso.ID_Actividad}

@router.post("/asignar_habilidad_actividad/{paciente_id}")
def asignar_habilidad_actividad(paciente_id: int, db: Session = Depends(get_db)):
    # Verificar si el paciente existe
    paciente = db.query(Paciente).filter(Paciente.ID_Paciente == paciente_id).first()
    if not paciente:
        raise HTTPException(status_code=404, detail="Paciente no encontrado")

    # Obtener tratamiento asignado del paciente
    tratamiento_asignado = db.query(Paciente_Tratamiento)\
        .filter(Paciente_Tratamiento.ID_Paciente == paciente_id)\
        .first()

    if not tratamiento_asignado:
        raise HTTPException(status_code=404, detail="El paciente no tiene tratamiento asignado")

    tratamiento_id = tratamiento_asignado.ID_Tratamiento

    # Buscar la primera habilidad y actividad para el tratamiento especificado
    th_actividad = db.query(Tratamiento_Habilidad_Actividad)\
        .join(Habilidad, Tratamiento_Habilidad_Actividad.ID_Habilidad == Habilidad.ID_Habilidad)\
        .join(Actividad, Tratamiento_Habilidad_Actividad.ID_Actividad == Actividad.ID_Actividad)\
        .filter(Tratamiento_Habilidad_Actividad.ID_Tratamiento == tratamiento_id)\
        .first()

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
    return {
        "message": "Habilidad y actividad asignadas correctamente, progreso actualizado",
        "ID_Habilidad": th_actividad.ID_Habilidad,
        "ID_Actividad": th_actividad.ID_Actividad
    }

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

@router.post("/progreso/completar_actividad/{paciente_id}")
def completar_actividad(paciente_id: int, db: Session = Depends(get_db)):
    progreso = db.query(ProgresoPaciente).filter(ProgresoPaciente.ID_Paciente == paciente_id).first()
    if not progreso:
        raise HTTPException(status_code=404, detail="No se encontró el progreso del paciente")

    # 1. Registrar actividad completada en histórico
    historico = Paciente_Actividad(
        ID_Paciente=paciente_id,
        ID_Actividad=progreso.ID_Actividad,
        Completada=True,
        FechaCompletada=date.today()
    )
    db.add(historico)

    # 2. Buscar la siguiente actividad
    siguiente_actividad = db.query(Tratamiento_Habilidad_Actividad).filter(
        Tratamiento_Habilidad_Actividad.ID_Tratamiento == progreso.ID_Tratamiento,
        Tratamiento_Habilidad_Actividad.ID_Habilidad == progreso.ID_Habilidad,
        Tratamiento_Habilidad_Actividad.ID_Actividad > progreso.ID_Actividad
    ).order_by(Tratamiento_Habilidad_Actividad.ID_Actividad).first()

    if siguiente_actividad:
        # 3. Actualizar el progreso con la siguiente actividad
        progreso.ID_Actividad = siguiente_actividad.ID_Actividad
        db.commit()
        return {"message": "Actividad completada. Avanzando a la siguiente actividad."}

    # 4. No hay más actividades -> completar habilidad actual
    db.add(Paciente_Habilidad(
        ID_Paciente=paciente_id,
        ID_Habilidad=progreso.ID_Habilidad,
        Completada=True,
        FechaCompletada=date.today()
    ))

    # 5. Buscar la siguiente habilidad
    habilidades = db.query(Habilidad.ID_Habilidad).join(
        Tratamiento_Habilidad_Actividad,
        Tratamiento_Habilidad_Actividad.ID_Habilidad == Habilidad.ID_Habilidad
    ).filter(
        Tratamiento_Habilidad_Actividad.ID_Tratamiento == progreso.ID_Tratamiento
    ).distinct().order_by(Habilidad.ID_Habilidad).all()

    # Encuentra la siguiente habilidad con ID mayor a la actual
    ids = [h[0] for h in habilidades]
    try:
        idx_actual = ids.index(progreso.ID_Habilidad)
        id_siguiente = ids[idx_actual + 1]
    except (ValueError, IndexError):
        id_siguiente = None

    if id_siguiente:
        # Buscar la primera actividad de la siguiente habilidad
        actividad_inicio = db.query(Tratamiento_Habilidad_Actividad).filter(
            Tratamiento_Habilidad_Actividad.ID_Tratamiento == progreso.ID_Tratamiento,
            Tratamiento_Habilidad_Actividad.ID_Habilidad == id_siguiente
        ).order_by(Tratamiento_Habilidad_Actividad.ID_Actividad).first()

        if not actividad_inicio:
            raise HTTPException(status_code=400, detail="La siguiente habilidad no tiene actividades.")

        progreso.ID_Habilidad = id_siguiente
        progreso.ID_Actividad = actividad_inicio.ID_Actividad
        db.commit()
        return {"message": "Habilidad completada. Iniciando siguiente habilidad."}
    
    else:
        db.commit()
        return {"message": "Tratamiento completado. No hay más habilidades ni actividades por realizar."}

@router.get("/actividad/completada/{paciente_id}/{actividad_id}")
def actividad_completada(paciente_id: int, actividad_id: int, db: Session = Depends(get_db)):
    actividad = db.query(Paciente_Actividad).filter(
        Paciente_Actividad.ID_Paciente == paciente_id,
        Paciente_Actividad.ID_Actividad == actividad_id,
        Paciente_Actividad.Completada == True
    ).first()

    return {"completada": bool(actividad)}

@router.get("/progreso/habilidades_estado/{paciente_id}")
def obtener_estado_habilidades(paciente_id: int, db: Session = Depends(get_db)):
    progreso = db.query(ProgresoPaciente).filter(ProgresoPaciente.ID_Paciente == paciente_id).first()
    if not progreso:
        raise HTTPException(status_code=404, detail="No se encontró progreso")

    completadas = db.query(Paciente_Habilidad.ID_Habilidad).filter(
        Paciente_Habilidad.ID_Paciente == paciente_id,
        Paciente_Habilidad.Completada == True
    ).all()
    completadas_ids = [h[0] for h in completadas]

    habilidades = db.query(Habilidad).select_from(Tratamiento_Habilidad_Actividad).join(
        Habilidad, Tratamiento_Habilidad_Actividad.ID_Habilidad == Habilidad.ID_Habilidad
    ).filter(
        Tratamiento_Habilidad_Actividad.ID_Tratamiento == progreso.ID_Tratamiento
    ).distinct().order_by(Habilidad.ID_Habilidad).all()

    resultado = []
    for hab in habilidades:
        estado = "pendiente"
        if hab.ID_Habilidad == progreso.ID_Habilidad:
            estado = "actual"
        elif hab.ID_Habilidad in completadas_ids:
            estado = "completada"
        resultado.append({
            "id": hab.ID_Habilidad,
            "nombre": hab.Nombre,
            "estado": estado
        })

    return resultado

@router.post("/respuestas/guardar")
def guardar_respuestas(respuestas: List[RespuestaEntrada], db: Session = Depends(get_db)):
    for r in respuestas:
        nueva = RespuestaActividad(
            ID_Pregunta=r.ID_Pregunta,
            ID_Actividad=r.ID_Actividad,
            ID_Paciente=r.ID_Paciente,
            Respuesta=r.Respuesta
        )
        db.add(nueva)

    db.commit()
    return {"message": "Respuestas guardadas correctamente"}

@router.get("/progreso/porcentaje_habilidad/{paciente_id}/{id_habilidad}")
def obtener_porcentaje_habilidad(paciente_id: int, id_habilidad: int, db: Session = Depends(get_db)):
    # Obtener tratamiento asignado al paciente
    tratamiento = db.query(Paciente_Tratamiento).filter(Paciente_Tratamiento.ID_Paciente == paciente_id).first()
    if not tratamiento:
        raise HTTPException(status_code=404, detail="Tratamiento no asignado")

    tratamiento_id = tratamiento.ID_Tratamiento

    # Total de actividades para esa habilidad
    total = db.query(Tratamiento_Habilidad_Actividad).filter(
        Tratamiento_Habilidad_Actividad.ID_Tratamiento == tratamiento_id,
        Tratamiento_Habilidad_Actividad.ID_Habilidad == id_habilidad
    ).count()

    # Actividades completadas por el paciente en esa habilidad
    completadas = db.query(Paciente_Actividad).join(
        Tratamiento_Habilidad_Actividad,
        Paciente_Actividad.ID_Actividad == Tratamiento_Habilidad_Actividad.ID_Actividad
    ).filter(
        Paciente_Actividad.ID_Paciente == paciente_id,
        Tratamiento_Habilidad_Actividad.ID_Habilidad == id_habilidad,
        Tratamiento_Habilidad_Actividad.ID_Tratamiento == tratamiento_id,
        Paciente_Actividad.Completada == True
    ).count()

    porcentaje = int((completadas / total) * 100) if total > 0 else 0
    return {"porcentaje": porcentaje}