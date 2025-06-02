import hashlib
from datetime import date
from typing import List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from database import get_db
from models import paciente as Paciente
from schemas import (
    paciente_create,
    paciente,
    perfil_update,
    paciente_out,
    paciente_admin_full_update
)
from correo import enviar_correo_verificacion
from routers.admin import obtener_admin_actual

router = APIRouter(
    prefix="/pacientes",
    tags=["Pacientes"]
)

def hash_password(password: str) -> str:
    """Función para hashear la contraseña usando SHA-256."""
    return hashlib.sha256(password.encode("utf-8")).hexdigest()

@router.post("/", response_model=paciente)
def crear_paciente(data: paciente_create, db: Session = Depends(get_db)):
    db_paciente = db.query(Paciente).filter(Paciente.correo == data.correo).first()
    if db_paciente:
        raise HTTPException(status_code=400, detail="El correo ya está registrado.")

    hoy = date.today()
    fecha_nacimiento = data.fechanacimiento
    edad = hoy.year - fecha_nacimiento.year - ((hoy.month, hoy.day) < (fecha_nacimiento.month, fecha_nacimiento.day))

    es_apto = edad >= 18 and data.entratamiento.lower() == "ninguno"

    hashed_password = hash_password(data.contrasena)
    nuevo_paciente = Paciente(
        nombre=data.nombre,
        apellidos=data.apellidos,
        correo=data.correo,
        correoalternativo=data.correoalternativo,
        contrasena=hashed_password,
        celular=data.celular,
        sexo=data.sexo,
        fechanacimiento=data.fechanacimiento,
        id_nivelestudios=data.id_nivelestudios,
        id_ocupacion=data.id_ocupacion,
        id_residencia=data.id_residencia,
        id_estadocivil=data.id_estadocivil,
        entratamiento=data.entratamiento,
        id_tipoent=data.id_tipoent,
        tomamedicamentos=data.tomamedicamentos,
        nombremedicacion=data.nombremedicacion,
        avisoprivacidad=data.avisoprivacidad,
        cartaconsentimiento=data.cartaconsentimiento,
        esapto=es_apto
    )
    db.add(nuevo_paciente)
    db.commit()
    db.refresh(nuevo_paciente)

    if es_apto:
        enviar_correo_verificacion(data.correo, data.nombre, data.apellidos)

    return nuevo_paciente

@router.get("/", response_model=List[paciente_out])
def obtener_todos_los_pacientes(db: Session = Depends(get_db), admin=Depends(obtener_admin_actual)):
    return db.query(Paciente).all()

@router.get("/{paciente_id}", response_model=paciente)
def obtener_paciente(paciente_id: int, db: Session = Depends(get_db)):
    db_paciente = db.query(Paciente).filter(Paciente.id_paciente == paciente_id).first()
    if not db_paciente:
        raise HTTPException(status_code=404, detail="Paciente no encontrado")
    return db_paciente

@router.get("/termina_tratamiento/{paciente_id}")
def salir_tratamiento(paciente_id: int, db: Session = Depends(get_db)):
    db_paciente = db.query(Paciente).filter(Paciente.id_paciente == paciente_id).first()
    if not db_paciente:
        raise HTTPException(status_code=404, detail="Paciente no encontrado")

    db_paciente.esapto = False
    db.commit()

    return {"message": "El paciente ha salido del tratamiento exitosamente"}

@router.get("/perfil/{paciente_id}")
def obtener_perfil_paciente(paciente_id: int, db: Session = Depends(get_db)):
    db_paciente = db.query(Paciente).filter(Paciente.id_paciente == paciente_id).first()
    if not db_paciente:
        raise HTTPException(status_code=404, detail="Paciente no encontrado")

    return {
        "nombre": db_paciente.nombre,
        "apellidos": db_paciente.apellidos,
        "correo": db_paciente.correo,
        "celular": db_paciente.celular
    }

@router.put("/perfil/{paciente_id}")
def actualizar_perfil_paciente(paciente_id: int, perfil_data: perfil_update, db: Session = Depends(get_db)):
    db_paciente = db.query(Paciente).filter(Paciente.id_paciente == paciente_id).first()
    if not db_paciente:
        raise HTTPException(status_code=404, detail="Paciente no encontrado")

    if perfil_data.nombre:
        db_paciente.nombre = perfil_data.nombre
    if perfil_data.apellidos:
        db_paciente.apellidos = perfil_data.apellidos
    if perfil_data.celular:
        db_paciente.celular = perfil_data.celular

    db.commit()
    db.refresh(db_paciente)
    return {"message": "Perfil actualizado exitosamente"}

@router.put("/admin/actualizar_completo/{paciente_id}")
def actualizar_paciente_completo(
    paciente_id: int,
    data: paciente_admin_full_update,
    db: Session = Depends(get_db),
    admin=Depends(obtener_admin_actual)
):
    db_paciente = db.query(Paciente).filter(Paciente.id_paciente == paciente_id).first()
    if not db_paciente:
        raise HTTPException(status_code=404, detail="Paciente no encontrado")

    if data.nombre:
        db_paciente.nombre = data.nombre
    if data.apellidos:
        db_paciente.apellidos = data.apellidos
    if data.correo:
        db_paciente.correo = data.correo
    if data.correoalternativo:
        db_paciente.correoalternativo = data.correoalternativo
    if data.sexo:
        db_paciente.sexo = data.sexo
    if data.fechanacimiento:
        db_paciente.fechanacimiento = data.fechanacimiento
    if data.nuevacontrasena:
        db_paciente.contrasena = hash_password(data.nuevacontrasena)

    db.commit()
    db.refresh(db_paciente)
    return {"message": "Paciente actualizado completamente"}
