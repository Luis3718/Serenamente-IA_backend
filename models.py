from sqlalchemy import Column, Integer, String, Date, Boolean, TIMESTAMP, ForeignKey
from sqlalchemy.sql import func
from database import Base

class Paciente(Base):
    __tablename__ = "Pacientes"

    ID_Paciente = Column(Integer, primary_key=True, index=True)
    Nombre = Column(String(100), nullable=False)
    Apellidos = Column(String(100), nullable=False)
    Correo = Column(String(100), unique=True, nullable=False)
    CorreoAlternativo = Column(String(100))
    Contraseña = Column(String(255), nullable=False)
    Celular = Column(String(10), nullable=False)
    Sexo = Column(String(20), nullable=False)
    FechaNacimiento = Column(Date, nullable=False)
    ID_NivelEstudios = Column(Integer, nullable=False)
    ID_Ocupacion = Column(Integer, nullable=False)
    ID_Residencia = Column(Integer, nullable=False)
    ID_EstadoCivil = Column(Integer, nullable=False)
    EnTratamiento = Column(String(20), nullable=False)
    TomaMedicamentos = Column(String(255))
    NombreMedicacion = Column(String(255))
    AvisoPrivacidad = Column(Boolean, nullable=False)
    CartaConsentimiento = Column(Boolean, nullable=False)
    EsApto = Column(Boolean, default=False, nullable=False) 
    CorreoVerificado = Column(Boolean, default=False, nullable=False)
    formulario_contestado = Column(Boolean, default=False, nullable=False) 
    entrevista_contestada = Column(Boolean, default=False, nullable=False)  
    en_pausa = Column(Boolean, default=False, nullable=False)  

class TiposFormulario(Base):
    __tablename__ = 'TiposFormulario'
    ID_TipoFormulario = Column(Integer, primary_key=True)
    NombreFormulario = Column(String(255), nullable=False)

class Formulario(Base):
    __tablename__ = 'Formularios'
    ID_Formulario = Column(Integer, primary_key=True, autoincrement=True)
    ID_Paciente = Column(Integer, ForeignKey('Pacientes.ID_Paciente'), nullable=False)
    ID_TipoFormulario = Column(Integer, ForeignKey('TiposFormulario.ID_TipoFormulario'), nullable=False)
    Fecha_Respuesta = Column(TIMESTAMP, default=func.current_timestamp())

class Pregunta(Base):
    __tablename__ = 'Preguntas'
    ID_Pregunta = Column(Integer, primary_key=True)
    ID_TipoFormulario = Column(Integer, ForeignKey('TiposFormulario.ID_TipoFormulario'), nullable=False)
    Texto = Column(String(255), nullable=False)

class Respuesta(Base):
    __tablename__ = 'Respuestas'
    ID_Respuesta = Column(Integer, primary_key=True, autoincrement=True)
    ID_Pregunta = Column(Integer, ForeignKey('Preguntas.ID_Pregunta'), nullable=False)
    ID_Paciente = Column(Integer, ForeignKey('Pacientes.ID_Paciente'), nullable=False)
    Respuesta = Column(String, nullable=False)

class Resultado(Base):
    __tablename__ = 'Resultados'
    ID_Resultado = Column(Integer, primary_key=True, autoincrement=True)
    ID_Formulario = Column(Integer, ForeignKey('Formularios.ID_Formulario'), nullable=False)
    Puntuacion = Column(Integer, nullable=False)
    Categoria = Column(String(50), nullable=False)  # Bajo, Medio, Alto

class Tratamiento(Base):
    __tablename__ = 'Tratamientos'
    ID_Tratamiento = Column(Integer, primary_key=True, autoincrement=True)
    Nivel = Column(String(20), nullable=False)

class Habilidad(Base):
    __tablename__ = 'Habilidades'
    ID_Habilidad = Column(Integer, primary_key=True, autoincrement=True)
    Nombre = Column(String(100), nullable=False)

class Actividad(Base):
    __tablename__ = 'Actividades'
    ID_Actividad = Column(Integer, primary_key=True, autoincrement=True)
    ID_Habilidad = Column(Integer, ForeignKey('Habilidades.ID_Habilidad'), nullable=False)
    Nombre = Column(String(100), nullable=False)

class Tratamiento_Habilidad_Actividad(Base):
    __tablename__ = 'tratamiento_habilidad_actividad'
    ID_Tratamiento = Column(Integer, ForeignKey('tratamientos.ID_Tratamiento'), primary_key=True)
    ID_Habilidad = Column(Integer, ForeignKey('habilidades.ID_Habilidad'), primary_key=True)
    ID_Actividad = Column(Integer, ForeignKey('actividades.ID_Actividad'), primary_key=True)

class Paciente_Tratamiento(Base):
    __tablename__ = 'Paciente_Tratamiento'
    ID_Paciente = Column(Integer, ForeignKey('Pacientes.ID_Paciente'), primary_key=True)
    ID_Tratamiento = Column(Integer, ForeignKey('Tratamientos.ID_Tratamiento'), primary_key=True)
    FechaInicio = Column(Date, nullable=False)

class Paciente_Actividad(Base):
    __tablename__ = 'Paciente_Actividad'
    ID_Paciente = Column(Integer, ForeignKey('Pacientes.ID_Paciente'), primary_key=True)
    ID_Actividad = Column(Integer, ForeignKey('Actividades.ID_Actividad'), primary_key=True)
    FechaCompletada = Column(Date)
    Completada = Column(Boolean, default=False)

class Paciente_Habilidad(Base):
    __tablename__ = 'Paciente_Habilidad'
    ID_Paciente = Column(Integer, ForeignKey('Pacientes.ID_Paciente'), primary_key=True)
    ID_Habilidad = Column(Integer, ForeignKey('Habilidades.ID_Habilidad'), primary_key=True)
    FechaCompletada = Column(Date)
    Completada = Column(Boolean, default=False)

class ProgresoPaciente(Base):
    __tablename__ = 'progreso_paciente'
    ID_Paciente = Column(Integer, ForeignKey('pacientes.ID_Paciente'), primary_key=True)
    ID_Tratamiento = Column(Integer, ForeignKey('tratamientos.ID_Tratamiento'), nullable=False)
    ID_Habilidad = Column(Integer, ForeignKey('habilidades.ID_Habilidad'))
    ID_Actividad = Column(Integer, ForeignKey('actividades.ID_Actividad'))
    FechaInicio = Column(Date)