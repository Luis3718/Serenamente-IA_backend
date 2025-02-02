from sqlalchemy import Column, Integer, String, Date, Boolean
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
