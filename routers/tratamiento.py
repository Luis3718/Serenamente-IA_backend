from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from datetime import date
from typing import List
from database import get_db
from models import (
    paciente, tratamiento, paciente_tratamiento, habilidad,
    tratamiento_habilidad_actividad, paciente_habilidad, paciente_actividad,
    actividad, progreso_paciente, respuesta_actividad
)
from schemas import (
    habilidad_base, actividad_base, progreso_response,
    actividad_con_id, respuesta_entrada
)
import random

router = APIRouter(
    prefix="/tratamiento",
    tags=["Tratamiento"]
)

@router.post("/asignar_protocolo/{paciente_id}")
def asignar_tratamiento(paciente_id: int, db: Session = Depends(get_db)):
    paciente_existente = db.query(paciente).filter(paciente.id_paciente == paciente_id).first()
    if not paciente_existente:
        raise HTTPException(status_code=404, detail="Paciente no encontrado")

    tratamiento_existente = db.query(paciente_tratamiento).filter(paciente_tratamiento.id_paciente == paciente_id).first()
    if tratamiento_existente:
        raise HTTPException(status_code=400, detail="El paciente ya tiene un tratamiento asignado")

    tratamiento_id = 3  # fijo por ahora

    nuevo_tratamiento = paciente_tratamiento(
        id_paciente=paciente_id,
        id_tratamiento=tratamiento_id,
        fechainicio=date.today()
    )
    db.add(nuevo_tratamiento)
    db.commit()
    return {"message": "Tratamiento asignado correctamente", "id_tratamiento": tratamiento_id}

@router.get("/buscar_protocolo/{paciente_id}")
def get_tratamiento_paciente(paciente_id: int, db: Session = Depends(get_db)):
    paciente_trat = db.query(paciente_tratamiento).filter(paciente_tratamiento.id_paciente == paciente_id).first()
    if not paciente_trat:
        raise HTTPException(status_code=404, detail="Tratamiento no encontrado para el paciente")

    trat = db.query(tratamiento).filter(tratamiento.id_tratamiento == paciente_trat.id_tratamiento).first()
    if not trat:
        raise HTTPException(status_code=404, detail="Tratamiento no encontrado")

    return trat

@router.get("/ruta_habilidades/{id_tratamiento}", response_model=List[habilidad_base])
def get_habilidades_tratamiento(id_tratamiento: int, db: Session = Depends(get_db)):
    habilidades = db.query(habilidad).join(
        tratamiento_habilidad_actividad,
        tratamiento_habilidad_actividad.id_habilidad == habilidad.id_habilidad
    ).filter(
        tratamiento_habilidad_actividad.id_tratamiento == id_tratamiento
    ).all()
    if not habilidades:
        raise HTTPException(status_code=404, detail="No se encontraron habilidades para este tratamiento")
    return habilidades

@router.get("/ruta_actividad/{id_tratamiento}/habilidad/{id_habilidad}", response_model=List[actividad_con_id])
def get_actividades_tratamiento_habilidad(id_tratamiento: int, id_habilidad: int, db: Session = Depends(get_db)):
    actividades = db.query(actividad).\
        join(tratamiento_habilidad_actividad, tratamiento_habilidad_actividad.id_actividad == actividad.id_actividad).\
        filter(
            tratamiento_habilidad_actividad.id_tratamiento == id_tratamiento,
            tratamiento_habilidad_actividad.id_habilidad == id_habilidad
        ).all()

    if not actividades:
        raise HTTPException(status_code=404, detail="No se encontraron actividades para esta habilidad en este tratamiento")

    return actividades

@router.get("/progreso/actividad_actual/{paciente_id}")
def obtener_actividad_actual(paciente_id: int, db: Session = Depends(get_db)):
    progreso = db.query(progreso_paciente).filter(progreso_paciente.id_paciente == paciente_id).first()
    if not progreso:
        raise HTTPException(status_code=404, detail="Progreso no encontrado")

    return {"id_actividad_actual": progreso.id_actividad}

@router.post("/asignar_habilidad_actividad/{paciente_id}")
def asignar_habilidad_actividad(paciente_id: int, db: Session = Depends(get_db)):
    paciente_existente = db.query(paciente).filter(paciente.id_paciente == paciente_id).first()
    if not paciente_existente:
        raise HTTPException(status_code=404, detail="Paciente no encontrado")

    tratamiento_asignado = db.query(paciente_tratamiento)\
        .filter(paciente_tratamiento.id_paciente == paciente_id)\
        .first()

    if not tratamiento_asignado:
        raise HTTPException(status_code=404, detail="El paciente no tiene tratamiento asignado")

    tratamiento_id = tratamiento_asignado.id_tratamiento

    th_actividad = db.query(tratamiento_habilidad_actividad)\
        .join(habilidad, tratamiento_habilidad_actividad.id_habilidad == habilidad.id_habilidad)\
        .join(actividad, tratamiento_habilidad_actividad.id_actividad == actividad.id_actividad)\
        .filter(tratamiento_habilidad_actividad.id_tratamiento == tratamiento_id)\
        .first()

    if not th_actividad:
        raise HTTPException(status_code=404, detail="No se encontraron habilidades y actividades para este tratamiento")

    progreso = db.query(progreso_paciente).filter(progreso_paciente.id_paciente == paciente_id).first()
    if not progreso:
        progreso = progreso_paciente(
            id_paciente=paciente_id,
            id_tratamiento=tratamiento_id,
            id_habilidad=th_actividad.id_habilidad,
            id_actividad=th_actividad.id_actividad,
            fechainicio=date.today()
        )
        db.add(progreso)
    else:
        progreso.id_tratamiento = tratamiento_id
        progreso.id_habilidad = th_actividad.id_habilidad
        progreso.id_actividad = th_actividad.id_actividad
        progreso.fechainicio = date.today()

    db.commit()
    return {
        "message": "Habilidad y actividad asignadas correctamente, progreso actualizado",
        "id_habilidad": th_actividad.id_habilidad,
        "id_actividad": th_actividad.id_actividad
    }

@router.get("/progreso/{paciente_id}", response_model=progreso_response)
def get_progreso_paciente(paciente_id: int, db: Session = Depends(get_db)):
    progreso = db.query(
        progreso_paciente.id_paciente,
        progreso_paciente.id_tratamiento,
        progreso_paciente.id_habilidad,
        progreso_paciente.id_actividad,
        progreso_paciente.fechainicio,
        habilidad.nombre.label('nombre_habilidad'),
        actividad.nombre.label('nombre_actividad')
    ).join(
        habilidad, progreso_paciente.id_habilidad == habilidad.id_habilidad
    ).join(
        actividad, progreso_paciente.id_actividad == actividad.id_actividad
    ).filter(
        progreso_paciente.id_paciente == paciente_id
    ).first()

    if not progreso:
        raise HTTPException(status_code=404, detail="Progreso del paciente no encontrado")

    return progreso

@router.post("/progreso/completar_actividad/{paciente_id}")
def completar_actividad(paciente_id: int, db: Session = Depends(get_db)):
    progreso = db.query(progreso_paciente).filter(progreso_paciente.id_paciente == paciente_id).first()
    if not progreso:
        raise HTTPException(status_code=404, detail="No se encontró el progreso del paciente")
    
    # 1. Registrar actividad completada en histórico
    historico = paciente_actividad(
        id_paciente=paciente_id,
        id_actividad=progreso.id_actividad,
        completada=True,
        fechacompletada=date.today()
    )
    db.add(historico)
    
    # 2. Buscar la siguiente actividad
    siguiente_actividad = db.query(tratamiento_habilidad_actividad).filter(
        tratamiento_habilidad_actividad.id_tratamiento == progreso.id_tratamiento,
        tratamiento_habilidad_actividad.id_habilidad == progreso.id_habilidad,
        tratamiento_habilidad_actividad.id_actividad > progreso.id_actividad
    ).order_by(tratamiento_habilidad_actividad.id_actividad).first()

    if siguiente_actividad:
        # 3. Actualizar el progreso con la siguiente actividad
        progreso.id_actividad = siguiente_actividad.id_actividad
        db.commit()
        return {"message": "Actividad completada. Avanzando a la siguiente actividad."}

    # 4. No hay más actividades -> completar habilidad actual
    db.add(paciente_habilidad(
        id_paciente=paciente_id,
        id_habilidad=progreso.id_habilidad,
        completada=True,
        fechacompletada=date.today()
    ))

    # 5. Buscar la siguiente habilidad
    habilidades = db.query(habilidad.id_habilidad).join(
        tratamiento_habilidad_actividad,
        tratamiento_habilidad_actividad.id_habilidad == habilidad.id_habilidad
    ).filter(
        tratamiento_habilidad_actividad.id_tratamiento == progreso.id_tratamiento
    ).distinct().order_by(habilidad.id_habilidad).all()

    # Encuentra la siguiente habilidad con ID mayor a la actual
    ids = [h[0] for h in habilidades]
    try:
        idx_actual = ids.index(progreso.id_habilidad)
        id_siguiente = ids[idx_actual + 1]
    except (ValueError, IndexError):
        id_siguiente = None

    if id_siguiente:
        # Buscar la primera actividad de la siguiente habilidad
        actividad_inicio = db.query(tratamiento_habilidad_actividad).filter(
            tratamiento_habilidad_actividad.id_tratamiento == progreso.id_tratamiento,
            tratamiento_habilidad_actividad.id_habilidad == id_siguiente
        ).order_by(tratamiento_habilidad_actividad.id_actividad).first()

        if not actividad_inicio:
            raise HTTPException(status_code=400, detail="La siguiente habilidad no tiene actividades.")

        progreso.id_habilidad = id_siguiente
        progreso.id_actividad = actividad_inicio.id_actividad
        db.commit()
        return {"message": "Habilidad completada. Iniciando siguiente habilidad."}
    
    else:
        db.commit()
        return {"message": "Tratamiento completado. No hay más habilidades ni actividades por realizar."}

@router.get("/actividad/completada/{paciente_id}/{actividad_id}")
def actividad_completada(paciente_id: int, actividad_id: int, db: Session = Depends(get_db)):
    actividad = db.query(paciente_actividad).filter(
        paciente_actividad.id_paciente == paciente_id,
        paciente_actividad.id_actividad == actividad_id,
        paciente_actividad.completada == True
    ).first()

    return {"completada": bool(actividad)}

@router.get("/progreso/habilidades_estado/{paciente_id}")
def obtener_estado_habilidades(paciente_id: int, db: Session = Depends(get_db)):
    progreso = db.query(progreso_paciente).filter(progreso_paciente.id_paciente == paciente_id).first()
    if not progreso:
        raise HTTPException(status_code=404, detail="No se encontró progreso")

    completadas = db.query(paciente_habilidad.id_habilidad).filter(
        paciente_habilidad.id_paciente == paciente_id,
        paciente_habilidad.completada == True
    ).all()
    completadas_ids = [h[0] for h in completadas]

    habilidades = db.query(habilidad).select_from(tratamiento_habilidad_actividad).join(
        habilidad, tratamiento_habilidad_actividad.id_habilidad == habilidad.id_habilidad
    ).filter(
        tratamiento_habilidad_actividad.id_tratamiento == progreso.id_tratamiento
    ).distinct().order_by(habilidad.id_habilidad).all()

    resultado = []
    for hab in habilidades:
        estado = "pendiente"
        if hab.id_habilidad == progreso.id_habilidad:
            estado = "actual"
        elif hab.id_habilidad in completadas_ids:
            estado = "completada"
        resultado.append({
            "id": hab.id_habilidad,
            "nombre": hab.nombre,
            "estado": estado
        })

    return resultado

@router.post("/respuestas/guardar")
def guardar_respuestas(respuestas: List[respuesta_entrada], db: Session = Depends(get_db)):
    for r in respuestas:
        nueva = respuesta_actividad(
            id_pregunta=r.id_pregunta,
            id_actividad=r.id_actividad,
            id_paciente=r.id_paciente,
            respuesta=r.respuesta
        )
        db.add(nueva)

    db.commit()
    return {"message": "Respuestas guardadas correctamente"}

@router.get("/progreso/porcentaje_habilidad/{paciente_id}/{id_habilidad}")
def obtener_porcentaje_habilidad(paciente_id: int, id_habilidad: int, db: Session = Depends(get_db)):
    tratamiento = db.query(paciente_tratamiento).filter(paciente_tratamiento.id_paciente == paciente_id).first()
    if not tratamiento:
        raise HTTPException(status_code=404, detail="Tratamiento no asignado")

    tratamiento_id = tratamiento.id_tratamiento

    total = db.query(tratamiento_habilidad_actividad).filter(
        tratamiento_habilidad_actividad.id_tratamiento == tratamiento_id,
        tratamiento_habilidad_actividad.id_habilidad == id_habilidad
    ).count()

    completadas = db.query(paciente_actividad).join(
        tratamiento_habilidad_actividad,
        paciente_actividad.id_actividad == tratamiento_habilidad_actividad.id_actividad
    ).filter(
        paciente_actividad.id_paciente == paciente_id,
        tratamiento_habilidad_actividad.id_habilidad == id_habilidad,
        tratamiento_habilidad_actividad.id_tratamiento == tratamiento_id,
        paciente_actividad.completada == True
    ).count()

    porcentaje = int((completadas / total) * 100) if total > 0 else 0
    return {"porcentaje": porcentaje}