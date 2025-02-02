from pydantic import BaseModel, EmailStr
from datetime import date
from typing import Optional  # Importar Optional para Python 3.9

class PacienteBase(BaseModel):
    Nombre: str
    Apellidos: str
    Correo: EmailStr
    CorreoAlternativo: Optional[EmailStr] = None
    Celular: str
    Sexo: str
    FechaNacimiento: date
    ID_NivelEstudios: int
    ID_Ocupacion: int
    ID_Residencia: int
    ID_EstadoCivil: int
    EnTratamiento: str
    TomaMedicamentos: Optional[str] = None
    NombreMedicacion: Optional[str] = None
    AvisoPrivacidad: bool
    CartaConsentimiento: bool
    EsApto: Optional[bool] = None  # Nuevo campo agregado
    CorreoVerificado: Optional[bool] = None  # Nuevo campo

class PacienteCreate(PacienteBase):
    Contraseña: str
    EsApto: Optional[bool] = None  # Campo opcional pero no necesario en la entrada

class Paciente(PacienteBase):
    ID_Paciente: int

    class Config:
        from_attributes = True  # Esto habilita la conversión desde modelos de SQLAlchemy
