from sqlalchemy import Column, Integer, String, Date, Text, Boolean, TIMESTAMP, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from database import Base

class paciente(Base):
    __tablename__ = "pacientes"

    id_paciente = Column(Integer, primary_key=True, index=True)
    nombre = Column(String(100), nullable=False)
    apellidos = Column(String(100), nullable=False)
    correo = Column(String(100), unique=True, nullable=False)
    correoalternativo = Column(String(100))
    contrasena = Column(String(255), nullable=False)
    celular = Column(String(10), nullable=False)
    sexo = Column(String(20), nullable=False)
    fechanacimiento = Column(Date, nullable=False)
    id_nivelestudios = Column(Integer, nullable=False)
    id_ocupacion = Column(Integer, nullable=False)
    id_residencia = Column(Integer, nullable=False)
    id_estadocivil = Column(Integer, nullable=False)
    id_tipoent = Column(Integer, nullable=False)
    entratamiento = Column(String(20), nullable=False)
    tomamedicamentos = Column(String(255))
    nombremedicacion = Column(String(255))
    avisoprivacidad = Column(Boolean, nullable=False)
    cartaconsentimiento = Column(Boolean, nullable=False)
    fecharegistro = Column(TIMESTAMP, server_default=func.current_timestamp())
    esapto = Column(Boolean, default=False, nullable=False)
    correoverificado = Column(Boolean, default=False, nullable=False)
    formulario_contestado = Column(Boolean, default=False, nullable=False)
    entrevista_contestada = Column(Boolean, default=False, nullable=False)
    en_pausa = Column(Boolean, default=False, nullable=False)

class admin(Base):
    __tablename__ = "admins"

    id_admin = Column(Integer, primary_key=True, index=True, autoincrement=True)
    usuario = Column(String(100), unique=True, nullable=False)
    contrasena = Column(String(64), nullable=False)

class tipos_formulario(Base):
    __tablename__ = "tipos_formulario"

    id_tipoformulario = Column(Integer, primary_key=True, autoincrement=True)
    nombreformulario = Column(String(255), nullable=False)

class formulario(Base):
    __tablename__ = "formularios"

    id_formulario = Column(Integer, primary_key=True, autoincrement=True)
    id_paciente = Column(Integer, ForeignKey("pacientes.id_paciente"), nullable=False)
    id_tipoformulario = Column(Integer, ForeignKey("tipos_formulario.id_tipoformulario"), nullable=False)
    fecha_respuesta = Column(TIMESTAMP, server_default=func.current_timestamp())

class pregunta(Base):
    __tablename__ = "preguntas"

    id_pregunta = Column(Integer, primary_key=True)
    id_tipoformulario = Column(Integer, ForeignKey("tipos_formulario.id_tipoformulario"), nullable=False)
    texto = Column(String(512), nullable=False)

class respuesta(Base):
    __tablename__ = "respuestas"

    id_respuesta = Column(Integer, primary_key=True, autoincrement=True)
    id_pregunta = Column(Integer, ForeignKey("preguntas.id_pregunta"), nullable=False)
    id_paciente = Column(Integer, ForeignKey("pacientes.id_paciente"), nullable=False)
    respuesta = Column(String(200), nullable=False)

class resultado(Base):
    __tablename__ = "resultados"

    id_resultado = Column(Integer, primary_key=True, autoincrement=True)
    id_formulario = Column(Integer, ForeignKey("formularios.id_formulario"), nullable=False)
    puntuacion = Column(Integer, nullable=False)
    categoria = Column(String(50), nullable=False)

class asignacion_sistema_experto(Base):
    __tablename__ = "asignacionessistemaexperto"

    id_asignacion = Column(Integer, primary_key=True, autoincrement=True, index=True)
    id_paciente = Column(Integer, ForeignKey("pacientes.id_paciente"), nullable=False)
    id_tratamiento = Column(Integer, ForeignKey("tratamientos.id_tratamiento"), nullable=False)
    log_sistema = Column(Text, nullable=False)
    fechaevaluacion = Column(TIMESTAMP, server_default=func.current_timestamp())

class tratamiento(Base):
    __tablename__ = "tratamientos"

    id_tratamiento = Column(Integer, primary_key=True, autoincrement=True)
    nivel = Column(String(20), nullable=False)

class habilidad(Base):
    __tablename__ = "habilidades"

    id_habilidad = Column(Integer, primary_key=True, autoincrement=True)
    nombre = Column(String(100), nullable=False)

class AdminHabilidad(Base):
    __tablename__ = "habilidades"
    __table_args__ = {'extend_existing': True}

    id_habilidad = Column(Integer, primary_key=True, autoincrement=True)
    nombre = Column(String(100), nullable=False)

class actividad(Base):
    __tablename__ = "actividades"

    id_actividad = Column(Integer, primary_key=True, autoincrement=True)
    id_habilidad = Column(Integer, ForeignKey("habilidades.id_habilidad"), nullable=False)
    nombre = Column(String(100), nullable=False)

class AdminActividad(Base):
    __tablename__ = "actividades"
    __table_args__ = {'extend_existing': True}

    id_actividad = Column(Integer, primary_key=True, autoincrement=True)
    id_habilidad = Column(Integer, ForeignKey("habilidades.id_habilidad"))
    nombre = Column(String(100), nullable=False)

    habilidad = relationship("AdminHabilidad", backref="actividades")

class respuesta_actividad(Base):
    __tablename__ = "respuestas_actividad"

    id_respuesta = Column(Integer, primary_key=True, autoincrement=True, index=True)
    id_pregunta = Column(Integer, nullable=True)
    id_paciente = Column(Integer, ForeignKey("pacientes.id_paciente"), nullable=False)
    id_actividad = Column(Integer, ForeignKey("actividades.id_actividad"), nullable=False)
    respuesta = Column(Text, nullable=False)
    fecha_registro = Column(DateTime, server_default=func.current_timestamp())

class tratamiento_habilidad_actividad(Base):
    __tablename__ = "tratamiento_habilidad_actividad"

    id_tratamiento = Column(Integer, ForeignKey("tratamientos.id_tratamiento"), primary_key=True)
    id_habilidad = Column(Integer, ForeignKey("habilidades.id_habilidad"), primary_key=True)
    id_actividad = Column(Integer, ForeignKey("actividades.id_actividad"), primary_key=True)

class paciente_tratamiento(Base):
    __tablename__ = "paciente_tratamiento"

    id_paciente = Column(Integer, ForeignKey("pacientes.id_paciente"), primary_key=True)
    id_tratamiento = Column(Integer, ForeignKey("tratamientos.id_tratamiento"), primary_key=True)
    fechainicio = Column(Date, nullable=False)

class paciente_actividad(Base):
    __tablename__ = "paciente_actividad"

    id_paciente = Column(Integer, ForeignKey("pacientes.id_paciente"), primary_key=True)
    id_actividad = Column(Integer, ForeignKey("actividades.id_actividad"), primary_key=True)
    fechacompletada = Column(Date)
    completada = Column(Boolean, default=False)

class paciente_habilidad(Base):
    __tablename__ = "paciente_habilidad"

    id_paciente = Column(Integer, ForeignKey("pacientes.id_paciente"), primary_key=True)
    id_habilidad = Column(Integer, ForeignKey("habilidades.id_habilidad"), primary_key=True)
    fechacompletada = Column(Date)
    completada = Column(Boolean, default=False)

class progreso_paciente(Base):
    __tablename__ = "progreso_paciente"

    id_paciente = Column(Integer, ForeignKey("pacientes.id_paciente"), primary_key=True)
    id_tratamiento = Column(Integer, ForeignKey("tratamientos.id_tratamiento"))
    id_habilidad = Column(Integer, ForeignKey("habilidades.id_habilidad"))
    id_actividad = Column(Integer, ForeignKey("actividades.id_actividad"))
    fechainicio = Column(Date)