from pydantic import BaseModel, EmailStr
from datetime import date, datetime
from typing import Optional

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
    formulario_contestado: Optional[bool] = None  # Nuevo campo


class PacienteCreate(PacienteBase):
    Contraseña: str
    EsApto: Optional[bool] = None  # Campo opcional pero no necesario en la entrada

class Paciente(PacienteBase):
    ID_Paciente: int

    class Config:
        from_attributes = True  # Esto habilita la conversión desde modelos de SQLAlchemy

class FormularioBase(BaseModel):
    ID_Paciente: int
    ID_TipoFormulario: int
    Fecha_Respuesta: datetime = None

class FormularioCreate(FormularioBase):
    pass

class Formulario(FormularioBase):
    ID_Formulario: int

    class Config:
        from_attributes = True

class PreguntaBase(BaseModel):
    ID_TipoFormulario: int
    Texto: str

class PreguntaCreate(PreguntaBase):
    pass

class Pregunta(PreguntaBase):
    ID_Pregunta: int

    class Config:
        from_attributes = True

class RespuestaBase(BaseModel):
    ID_Pregunta: int
    ID_Paciente: int
    Respuesta: str

class RespuestaCreate(RespuestaBase):
    pass

class Respuesta(RespuestaBase):
    ID_Respuesta: int

    class Config:
        from_attributes = True

class ResultadoBase(BaseModel):
    ID_Formulario: int
    Puntuacion: int
    Categoria: str  # Bajo, Medio, Alto

class ResultadoCreate(ResultadoBase):
    pass

class Resultado(ResultadoBase):
    ID_Resultado: int

    class Config:
        from_attributes = True
