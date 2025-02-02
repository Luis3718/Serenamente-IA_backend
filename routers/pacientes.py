import hashlib  # Importar hashlib para el hash de contraseñas
import schemas
import models
from correo import enviar_correo_verificacion
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from database import get_db
from models import Paciente
from schemas import PacienteCreate, Paciente

router = APIRouter(
    prefix="/pacientes",
    tags=["Pacientes"]
)

def hash_password(password: str) -> str:
    """Función para hashear la contraseña usando SHA-256."""
    return hashlib.sha256(password.encode("utf-8")).hexdigest()

from datetime import date

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
        TomaMedicamentos=paciente.TomaMedicamentos,
        NombreMedicacion=paciente.NombreMedicacion,
        AvisoPrivacidad=paciente.AvisoPrivacidad,
        CartaConsentimiento=paciente.CartaConsentimiento,
        EsApto=es_apto,  # Almacenar si es apto o no
    )
    db.add(nuevo_paciente)
    db.commit()
    db.refresh(nuevo_paciente)

    # Enviar correo solo si es apto
    if es_apto:
        print("Hola")
        enviar_correo_verificacion(paciente.Correo)

    return nuevo_paciente

@router.get("/{paciente_id}", response_model=Paciente)
def obtener_paciente(paciente_id: int, db: Session = Depends(get_db)):
    paciente = db.query(Paciente).filter(Paciente.ID_Paciente == paciente_id).first()
    if not paciente:
        raise HTTPException(status_code=404, detail="Paciente no encontrado")
    return paciente
