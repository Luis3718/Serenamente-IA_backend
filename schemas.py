from pydantic import BaseModel, EmailStr
from datetime import date, datetime
from typing import Optional, List

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
    ID_TipoENT: int
    TomaMedicamentos: Optional[str] = None
    NombreMedicacion: Optional[str] = None
    AvisoPrivacidad: bool
    CartaConsentimiento: bool
    EsApto: Optional[bool] = None  
    CorreoVerificado: Optional[bool] = None  
    formulario_contestado: Optional[bool] = None  
    entrevista_contestada: Optional[bool] = None  
    en_pausa: Optional[bool] = None  


class PacienteCreate(PacienteBase):
    Contraseña: str
    EsApto: Optional[bool] = None  

class Paciente(PacienteBase):
    ID_Paciente: int

    class Config:
        from_attributes = True  

class PerfilUpdate(BaseModel):
    Nombre: str = None
    Apellidos: str = None
    Celular: str = None

class PacienteOut(BaseModel):
    ID_Paciente: int
    Nombre: str
    Apellidos: str
    Correo: str
    Sexo: str
    FechaNacimiento: date

    class Config:
        orm_mode = True

class PacienteAdminFullUpdate(BaseModel):
    Nombre: Optional[str]
    Apellidos: Optional[str]
    Correo: Optional[str]
    SegundoCorreo: Optional[str]
    Sexo: Optional[str]
    FechaNacimiento: Optional[date]
    NuevaContrasena: Optional[str]  # En texto plano (la hashearemos)

    class Config:
        orm_mode = True

class AdminLogin(BaseModel):
    usuario: str
    contrasena: str

class AdminCreate(BaseModel):
    usuario: str
    contrasena: str

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

class AsignacionCreate(BaseModel):
    ID_Paciente: int
    ID_Tratamiento: int
    Log_sistema: List[str]  # lista de pasos aplicados

class AsignacionOut(BaseModel):
    ID_Asignacion: int
    ID_Paciente: int
    ID_Tratamiento: int
    Log_sistema: str
    FechaEvaluacion: datetime

    class Config:
        orm_mode = True

class TratamientoBase(BaseModel):
    Nivel: str

class HabilidadBase(BaseModel):
    ID_Habilidad: int
    Nombre: str

    class Config:
        orm_mode = True  # Usar from_attributes en Pydantic v2

class ActividadBase(BaseModel):
    ID_Habilidad: int
    Nombre: str

class ActividadConID(BaseModel):
    ID_Actividad: int
    ID_Habilidad: int
    Nombre: str

    class Config:
        orm_mode = True

class RespuestaEntrada(BaseModel):
    ID_Pregunta: Optional[int] = None
    ID_Actividad: int
    ID_Paciente: int
    Respuesta: str

class PacienteTratamientoBase(BaseModel):
    ID_Paciente: int
    ID_Tratamiento: int
    FechaInicio: date

class PacienteActividadBase(BaseModel):
    ID_Paciente: int
    ID_Actividad: int
    FechaCompletada: date
    Completada: bool

class PacienteHabilidadBase(BaseModel):
    ID_Paciente: int
    ID_Habilidad: int
    FechaCompletada: date
    Completada: bool

class ProgresoPacienteBase(BaseModel):
    ID_Paciente: int
    ID_Tratamiento: int
    ID_Habilidad: Optional[int]
    ID_Actividad: Optional[int]
    FechaInicio: Optional[date]

class ProgresoResponse(BaseModel):
    ID_Paciente: int
    ID_Tratamiento: int
    ID_Habilidad: int
    ID_Actividad: int
    FechaInicio: date
    Nombre_Habilidad: str
    Nombre_Actividad: str

    class Config:
        orm_mode = True

class ProgresoPacienteCreate(ProgresoPacienteBase):
    pass

class ProgresoPacienteUpdate(ProgresoPacienteBase):
    pass

class ProgresoPacienteInDB(ProgresoPacienteBase):
    class Config:
        orm_mode = True