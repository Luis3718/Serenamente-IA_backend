from pydantic import BaseModel, EmailStr
from datetime import date, datetime
from typing import Optional, List

class paciente_base(BaseModel):
    nombre: str
    apellidos: str
    correo: EmailStr
    correoalternativo: Optional[EmailStr] = None
    celular: str
    sexo: str
    fechanacimiento: date
    id_nivelestudios: int
    id_ocupacion: int
    id_residencia: int
    id_estadocivil: int
    entratamiento: str
    id_tipoent: int
    tomamedicamentos: Optional[str] = None
    nombremedicacion: Optional[str] = None
    avisoprivacidad: bool
    cartaconsentimiento: bool
    esapto: Optional[bool] = None
    correoverificado: Optional[bool] = None
    formulario_contestado: Optional[bool] = None
    entrevista_contestada: Optional[bool] = None
    en_pausa: Optional[bool] = None


class paciente_create(paciente_base):
    contrasena: str
    esapto: Optional[bool] = None

class paciente(paciente_base):
    id_paciente: int

    model_config = {
        "from_attributes": True
    }

class perfil_update(BaseModel):
    nombre: Optional[str] = None
    apellidos: Optional[str] = None
    celular: Optional[str] = None

class paciente_out(BaseModel):
    id_paciente: int
    nombre: str
    apellidos: str
    correo: str
    sexo: str
    fechanacimiento: date

    model_config = {
        "from_attributes": True
    }

class paciente_admin_full_update(BaseModel):
    nombre: Optional[str]
    apellidos: Optional[str]
    correo: Optional[str]
    correoalternativo: Optional[str]
    sexo: Optional[str]
    fechanacimiento: Optional[date]
    nuevacontrasena: Optional[str]

    model_config = {
        "from_attributes": True
    }

class login_request(BaseModel):
    correo: str
    contrasena: str

class forgot_password_request(BaseModel):
    correo: str

class reset_password_request(BaseModel):
    token: str
    nuevacontrasena: str

class admin_login(BaseModel):
    usuario: str
    contrasena: str

class admin_create(BaseModel):
    usuario: str
    contrasena: str

class formulario_base(BaseModel):
    id_paciente: int
    id_tipoformulario: int
    fecha_respuesta: Optional[datetime] = None

class formulario_create(formulario_base):
    pass

class formulario(formulario_base):
    id_formulario: int

    model_config = {
        "from_attributes": True
    }

class pregunta_base(BaseModel):
    id_tipoformulario: int
    texto: str

class pregunta_create(pregunta_base):
    pass

class pregunta(pregunta_base):
    id_pregunta: int

    model_config = {
        "from_attributes": True
    }

class respuesta_base(BaseModel):
    id_pregunta: int
    id_paciente: int
    respuesta: str

class respuesta_create(respuesta_base):
    pass

class respuesta(respuesta_base):
    id_respuesta: int

    model_config = {
        "from_attributes": True
    }

class resultado_base(BaseModel):
    id_formulario: int
    puntuacion: int
    categoria: str  # Bajo, Medio, Alto

class resultado_create(resultado_base):
    pass

class resultado(resultado_base):
    id_resultado: int

    model_config = {
        "from_attributes": True
    }

class asignacion_create(BaseModel):
    id_paciente: int
    id_tratamiento: int
    log_sistema: List[str]

class asignacion_out(BaseModel):
    id_asignacion: int
    id_paciente: int
    id_tratamiento: int
    log_sistema: str
    fechaevaluacion: datetime

    model_config = {
        "from_attributes": True
    }

class tratamiento_base(BaseModel):
    nivel: str

class habilidad_base(BaseModel):
    id_habilidad: int
    nombre: str

    model_config = {
        "from_attributes": True
    }

class actividad_base(BaseModel):
    id_habilidad: int
    nombre: str

class actividad_con_id(BaseModel):
    id_actividad: int
    id_habilidad: int
    nombre: str

    model_config = {
        "from_attributes": True
    }

class respuesta_entrada(BaseModel):
    id_pregunta: Optional[int] = None
    id_actividad: int
    id_paciente: int
    respuesta: str

class paciente_tratamiento_base(BaseModel):
    id_paciente: int
    id_tratamiento: int
    fechainicio: date

class paciente_actividad_base(BaseModel):
    id_paciente: int
    id_actividad: int
    fechacompletada: date
    completada: bool

class paciente_habilidad_base(BaseModel):
    id_paciente: int
    id_habilidad: int
    fechacompletada: date
    completada: bool    

class progreso_paciente_base(BaseModel):
    id_paciente: int
    id_tratamiento: int
    id_habilidad: Optional[int]
    id_actividad: Optional[int]
    fechainicio: Optional[date]

class progreso_response(BaseModel):
    id_paciente: int
    id_tratamiento: int
    id_habilidad: int
    id_actividad: int
    fechainicio: date
    nombre_habilidad: str
    nombre_actividad: str

    model_config = {
        "from_attributes": True
    }

class progreso_paciente_create(progreso_paciente_base):
    pass

class progreso_paciente_update(progreso_paciente_base):
    pass

class progreso_paciente_in_db(progreso_paciente_base):
    model_config = {
        "from_attributes": True
    }