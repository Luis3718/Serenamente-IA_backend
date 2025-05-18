import hashlib  # Importar hashlib para el hash de contraseñas
import schemas
import models
from datetime import date
from typing import List
from correo import enviar_correo_verificacion
from routers.admin import obtener_admin_actual
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from database import get_db
from models import Paciente
from schemas import PacienteCreate, Paciente, PerfilUpdate, PacienteOut, PacienteAdminFullUpdate

router = APIRouter(
    prefix="/pacientes",
    tags=["Pacientes"]
)

def hash_password(password: str) -> str:
    """Función para hashear la contraseña usando SHA-256."""
    return hashlib.sha256(password.encode("utf-8")).hexdigest()

@router.post("/", response_model=schemas.Paciente)
def crear_paciente(paciente: schemas.PacienteCreate, db: Session = Depends(get_db)):
    # Verificar si el correo ya existe
    db_paciente = db.query(models.Paciente).filter(models.Paciente.Correo == paciente.Correo).first()
    if db_paciente:
        raise HTTPException(status_code=400, detail="El correo ya está registrado.")
    # Calcular la edad
    hoy = date.today()
    fecha_nacimiento = paciente.FechaNacimiento
    edad = hoy.year - fecha_nacimiento.year - ((hoy.month, hoy.day) < (fecha_nacimiento.month, fecha_nacimiento.day))

    # Determinar si el usuario es apto
    es_apto = edad >= 18 and paciente.EnTratamiento == "ninguno"

    # Registrar al usuario
    hashed_password = hash_password(paciente.Contraseña)
    nuevo_paciente = models.Paciente(
        Nombre=paciente.Nombre,
        Apellidos=paciente.Apellidos,
        Correo=paciente.Correo,
        CorreoAlternativo=paciente.CorreoAlternativo,
        Contraseña=hashed_password,
        Celular=paciente.Celular,
        Sexo=paciente.Sexo,
        FechaNacimiento=paciente.FechaNacimiento,
        ID_NivelEstudios=paciente.ID_NivelEstudios,
        ID_Ocupacion=paciente.ID_Ocupacion,
        ID_Residencia=paciente.ID_Residencia,
        ID_EstadoCivil=paciente.ID_EstadoCivil,
        EnTratamiento=paciente.EnTratamiento,
        ID_TipoENT=paciente.ID_TipoENT,
        TomaMedicamentos=paciente.TomaMedicamentos,
        NombreMedicacion=paciente.NombreMedicacion,
        AvisoPrivacidad=paciente.AvisoPrivacidad,
        CartaConsentimiento=paciente.CartaConsentimiento,
        EsApto=es_apto,  
    )
    db.add(nuevo_paciente)
    db.commit()
    db.refresh(nuevo_paciente)

    # Enviar correo solo si es apto
    if es_apto:
        enviar_correo_verificacion(paciente.Correo)

    return nuevo_paciente

@router.get("/", response_model=List[PacienteOut])
def obtener_todos_los_pacientes(db: Session = Depends(get_db), admin=Depends(obtener_admin_actual)):
    return db.query(models.Paciente).all()

@router.get("/{paciente_id}", response_model=Paciente)
def obtener_paciente(paciente_id: int, db: Session = Depends(get_db)):
    paciente = db.query(Paciente).filter(Paciente.ID_Paciente == paciente_id).first()
    if not paciente:
        raise HTTPException(status_code=404, detail="Paciente no encontrado")
    return paciente

@router.get("termina_tratamiento/{paciente_id}", response_model=schemas.Paciente)
def salir_tratamiento(paciente_id: int, db: Session = Depends(get_db)):
    paciente = db.query(models.Paciente).filter(models.Paciente.ID_Paciente == paciente_id).first()
    if not paciente:
        raise HTTPException(status_code=404, detail="Paciente no encontrado")

    paciente.EsApto = False
    db.commit()
    return {"message": "El paciente ha salido del tratamiento exitosamente"}

@router.get("/perfil/{paciente_id}")
def obtener_perfil_paciente(paciente_id: int, db: Session = Depends(get_db)):
    paciente = db.query(models.Paciente).filter(models.Paciente.ID_Paciente == paciente_id).first()
    if not paciente:
        raise HTTPException(status_code=404, detail="Paciente no encontrado")

    return {
        "Nombre": paciente.Nombre,
        "Apellidos": paciente.Apellidos,
        "Correo": paciente.Correo,
        "Celular": paciente.Celular
    }

@router.put("/perfil/{paciente_id}")
def actualizar_perfil_paciente(paciente_id: int, perfil_data: PerfilUpdate, db: Session = Depends(get_db)):
    paciente = db.query(models.Paciente).filter(models.Paciente.ID_Paciente == paciente_id).first()
    if not paciente:
        raise HTTPException(status_code=404, detail="Paciente no encontrado")

    if perfil_data.Nombre:
        paciente.Nombre = perfil_data.Nombre
    if perfil_data.Apellidos:
        paciente.Apellidos = perfil_data.Apellidos
    if perfil_data.Celular:
        paciente.Celular = perfil_data.Celular

    db.commit()
    db.refresh(paciente)
    return {"message": "Perfil actualizado exitosamente"}

@router.put("/admin/actualizar_completo/{paciente_id}")
def actualizar_paciente_completo(
    paciente_id: int,
    data: PacienteAdminFullUpdate,
    db: Session = Depends(get_db),
    admin=Depends(obtener_admin_actual)
):
    paciente = db.query(models.Paciente).filter(models.Paciente.ID_Paciente == paciente_id).first()
    if not paciente:
        raise HTTPException(status_code=404, detail="Paciente no encontrado")

    if data.Nombre:
        paciente.Nombre = data.Nombre
    if data.Apellidos:
        paciente.Apellidos = data.Apellidos
    if data.Correo:
        paciente.Correo = data.Correo
    if data.SegundoCorreo:
        paciente.CorreoAlternativo = data.SegundoCorreo
    if data.Sexo:
        paciente.Sexo = data.Sexo
    if data.FechaNacimiento:
        paciente.FechaNacimiento = data.FechaNacimiento
    if data.NuevaContrasena:
        paciente.Contraseña = hash_password(data.NuevaContrasena)

    db.commit()
    db.refresh(paciente)
    return {"message": "Paciente actualizado completamente"}
