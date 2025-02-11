CREATE DATABASE SerenaMenteDB;

USE SerenaMenteDB;

-- Tablas de catálogo
CREATE TABLE NivelesEstudios (
    ID_NivelEstudios INTEGER PRIMARY KEY,
    Descripcion VARCHAR(50) NOT NULL
);

CREATE TABLE Ocupaciones (
    ID_Ocupacion INTEGER PRIMARY KEY,
    Descripcion VARCHAR(50) NOT NULL
);

CREATE TABLE Residencias (
    ID_Residencia INTEGER PRIMARY KEY,
    Descripcion VARCHAR(100) NOT NULL
);

CREATE TABLE EstadosCiviles (
    ID_EstadoCivil INTEGER PRIMARY KEY,
    Descripcion VARCHAR(50) NOT NULL
);

CREATE TABLE SexoCatalogo (
    Descripcion VARCHAR(20) PRIMARY KEY
);

CREATE TABLE TratamientoCatalogo (
    Descripcion VARCHAR(20) PRIMARY KEY
);

CREATE TABLE TiposFormulario (
    ID_TipoFormulario INTEGER PRIMARY KEY auto_increment,
    NombreFormulario VARCHAR(255) NOT NULL
);

-- Tabla para registrar usuarios/pacientes
CREATE TABLE Pacientes (
    ID_Paciente INTEGER PRIMARY KEY auto_increment,
    Nombre VARCHAR(100) NOT NULL,
    Apellidos VARCHAR(100) NOT NULL,
    Correo VARCHAR(100) NOT NULL UNIQUE,
    CorreoAlternativo VARCHAR(100),
    Contraseña VARCHAR(255) NOT NULL,
    Celular CHAR(10) NOT NULL,
    Sexo VARCHAR(20) NOT NULL,
    FechaNacimiento DATE NOT NULL,
    ID_NivelEstudios INTEGER NOT NULL,
    ID_Ocupacion INTEGER NOT NULL,
    ID_Residencia INTEGER NOT NULL,
    ID_EstadoCivil INTEGER NOT NULL,
    EnTratamiento VARCHAR(20) NOT NULL,
    TomaMedicamentos VARCHAR(255), -- Campo libre para escribir el medicamento
    NombreMedicacion VARCHAR(255),
    AvisoPrivacidad BOOLEAN NOT NULL,
    CartaConsentimiento BOOLEAN NOT NULL,
    FechaRegistro TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    EsApto BOOLEAN DEFAULT FALSE,
    CorreoVerificado BOOLEAN DEFAULT FALSE,
    formulario_contestado BOOLEAN DEFAULT FALSE,
    FOREIGN KEY (ID_NivelEstudios) REFERENCES NivelesEstudios(ID_NivelEstudios),
    FOREIGN KEY (ID_Ocupacion) REFERENCES Ocupaciones(ID_Ocupacion),
    FOREIGN KEY (ID_Residencia) REFERENCES Residencias(ID_Residencia),
    FOREIGN KEY (ID_EstadoCivil) REFERENCES EstadosCiviles(ID_EstadoCivil),
    FOREIGN KEY (Sexo) REFERENCES SexoCatalogo(Descripcion),
    FOREIGN KEY (EnTratamiento) REFERENCES TratamientoCatalogo(Descripcion)
);

-- Tabla de formularios
CREATE TABLE Formularios (
    ID_Formulario INTEGER PRIMARY KEY,
    ID_Paciente INTEGER NOT NULL,
    ID_TipoFormulario INTEGER NOT NULL,
    Fecha_Respuesta TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (ID_Paciente) REFERENCES Pacientes(ID_Paciente),
    FOREIGN KEY (ID_TipoFormulario) REFERENCES TiposFormulario(ID_TipoFormulario)
);

-- Tabla de preguntas del formulario
CREATE TABLE Preguntas (
    ID_Pregunta INTEGER PRIMARY KEY,
    ID_Formulario INTEGER NOT NULL,
    Texto VARCHAR(255) NOT NULL,
    FOREIGN KEY (ID_Formulario) REFERENCES Formularios(ID_Formulario)
);

-- Tabla de respuestas a las preguntas del formulario
CREATE TABLE Respuestas (
    ID_Respuesta INTEGER PRIMARY KEY,
    ID_Pregunta INTEGER NOT NULL,
    ID_Paciente INTEGER NOT NULL,
    Respuesta TEXT NOT NULL,
    FOREIGN KEY (ID_Pregunta) REFERENCES Preguntas(ID_Pregunta),
    FOREIGN KEY (ID_Paciente) REFERENCES Pacientes(ID_Paciente)
);

-- Tabla de calificaciones para los formularios
CREATE TABLE Calificaciones (
    ID_Calificacion INTEGER PRIMARY KEY,
    ID_Formulario INTEGER NOT NULL,
    Puntuacion INTEGER NOT NULL,
    Categoria VARCHAR(50) NOT NULL, -- Bajo, Medio, Alto
    FOREIGN KEY (ID_Formulario) REFERENCES Formularios(ID_Formulario)
);

-- Insertar datos en las tablas de catálogo
INSERT INTO NivelesEstudios (ID_NivelEstudios, Descripcion) VALUES
(1, 'No estudié'),
(2, 'Primaria'),
(3, 'Secundaria'),
(4, 'Preparatoria'),
(5, 'Licenciatura'),
(6, 'Maestría'),
(7, 'Doctorado'),
(8, 'Otro');

INSERT INTO Ocupaciones (ID_Ocupacion, Descripcion) VALUES
(1, 'Encargado(a) del hogar'),
(2, 'Estudiante'),
(3, 'Empleado(a)'),
(4, 'Desempleado(a)'),
(5, 'Autoempleo'),
(6, 'Profesionista'),
(7, 'Jubilado(a)'),
(8, 'Otro');

INSERT INTO Residencias (ID_Residencia, Descripcion) VALUES
(1, 'Aguascalientes'),
(2, 'Baja California'),
(3, 'Baja California Sur'),
(4, 'Campeche'),
(5, 'Chiapas'),
(6, 'Chihuahua'),
(7, 'Ciudad de México'),
(8, 'Coahuila'),
(9, 'Colima'),
(10, 'Durango'),
(11, 'Estado de México'),
(12, 'Guanajuato'),
(13, 'Guerrero'),
(14, 'Hidalgo'),
(15, 'Jalisco'),
(16, 'Michoacán'),
(17, 'Morelos'),
(18, 'Nayarit'),
(19, 'Nuevo León'),
(20, 'Oaxaca'),
(21, 'Puebla'),
(22, 'Querétaro'),
(23, 'Quintana Roo'),
(24, 'San Luis Potosí'),
(25, 'Sinaloa'),
(26, 'Sonora'),
(27, 'Tabasco'),
(28, 'Tamaulipas'),
(29, 'Tlaxcala'),
(30, 'Veracruz'),
(31, 'Yucatán'),
(32, 'Zacatecas'),
(33, 'Extranjero');

INSERT INTO EstadosCiviles (ID_EstadoCivil, Descripcion) VALUES
(1, 'Soltero(a)'),
(2, 'Unión libre'),
(3, 'Casado(a)'),
(4, 'Divorciado(a)'),
(5, 'Separado(a)'),
(6, 'Viudo(a)'),
(7, 'Otro');

INSERT INTO SexoCatalogo (Descripcion) VALUES
('Mujer'),
('Hombre'),
('Prefiero no decirlo');

INSERT INTO TratamientoCatalogo (Descripcion) VALUES
('ninguno'),
('psicológico'),
('psiquiátrico'),
('ambos');

-- Insertar los formularios iniciales en el catálogo
INSERT INTO TiposFormulario (NombreFormulario) VALUES
('Inventario de Ansiedad de Beck (BAI)'),
('Inventario de Depresión de Beck (BDI-II)'),
('MINI - Apartado riesgo suicida'),
('(WBI5) Índice de Bienestar General-5 de la Organización Mundial de la Salud'),
('Escala de Estrés Percibido -14 (PSS-14)'),
('Escala de Atención Plena MAAS'),
('APOI'),
('Escala de Autocompasión (SCS)');