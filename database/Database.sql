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

CREATE TABLE TipoENTs (
	ID_TipoENT INTEGER PRIMARY KEY auto_increment,
    NombreENT VARCHAR(255) NOT NULL
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
    ID_TipoENT INTEGER NOT NULL,
    TomaMedicamentos VARCHAR(255),
    NombreMedicacion VARCHAR(255),
    AvisoPrivacidad BOOLEAN NOT NULL,
    CartaConsentimiento BOOLEAN NOT NULL,
    FechaRegistro TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    EsApto BOOLEAN DEFAULT FALSE,
    CorreoVerificado BOOLEAN DEFAULT FALSE,
    formulario_contestado BOOLEAN DEFAULT FALSE,
    entrevista_contestada BOOLEAN DEFAULT FALSE,
    en_pausa BOOLEAN DEFAULT FALSE,
    FOREIGN KEY (ID_NivelEstudios) REFERENCES NivelesEstudios(ID_NivelEstudios),
    FOREIGN KEY (ID_Ocupacion) REFERENCES Ocupaciones(ID_Ocupacion),
    FOREIGN KEY (ID_Residencia) REFERENCES Residencias(ID_Residencia),
    FOREIGN KEY (ID_EstadoCivil) REFERENCES EstadosCiviles(ID_EstadoCivil),
    FOREIGN KEY (Sexo) REFERENCES SexoCatalogo(Descripcion),
    FOREIGN KEY (EnTratamiento) REFERENCES TratamientoCatalogo(Descripcion),
    FOREIGN KEY (ID_TipoENT) REFERENCES TipoENTs(ID_TipoENT)
);

-- Tabla de usuarios administrador
CREATE TABLE Admins (
  ID_Admin INT PRIMARY KEY AUTO_INCREMENT,
  Usuario VARCHAR(100) UNIQUE NOT NULL,
  Contrasena VARCHAR(64) NOT NULL  
);

-- Tabla de formularios
CREATE TABLE Formularios (
    ID_Formulario INTEGER PRIMARY KEY auto_increment,
    ID_Paciente INTEGER NOT NULL,
    ID_TipoFormulario INTEGER NOT NULL,
    Fecha_Respuesta TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (ID_Paciente) REFERENCES Pacientes(ID_Paciente),
    FOREIGN KEY (ID_TipoFormulario) REFERENCES TiposFormulario(ID_TipoFormulario)
);

-- Tabla de preguntas del formulario
CREATE TABLE Preguntas (
    ID_Pregunta INTEGER PRIMARY KEY,
    ID_TipoFormulario INTEGER NOT NULL,
    Texto VARCHAR(512) NOT NULL,
    FOREIGN KEY (ID_TipoFormulario) REFERENCES Tiposformulario(ID_TipoFormulario)
);

-- Tabla de respuestas a las preguntas del formulario
CREATE TABLE Respuestas (
    ID_Respuesta INTEGER PRIMARY KEY auto_increment,
    ID_Pregunta INTEGER NOT NULL,
    ID_Paciente INTEGER NOT NULL,
    Respuesta VARCHAR(200) NOT NULL,
    FOREIGN KEY (ID_Pregunta) REFERENCES Preguntas(ID_Pregunta),
    FOREIGN KEY (ID_Paciente) REFERENCES Pacientes(ID_Paciente)
);

-- Tabla de Resultados para los formularios
CREATE TABLE Resultados (
    ID_Resultado INTEGER PRIMARY KEY auto_increment,
    ID_Formulario INTEGER NOT NULL,
    Puntuacion INTEGER NOT NULL,
    Categoria VARCHAR(50) NOT NULL, 
    FOREIGN KEY (ID_Formulario) REFERENCES Formularios(ID_Formulario)
);

CREATE TABLE Tratamientos (
    ID_Tratamiento INTEGER PRIMARY KEY auto_increment,
    Nivel VARCHAR(20) NOT NULL
);

CREATE TABLE AsignacionesSistemaExperto (
    ID_Asignacion INTEGER PRIMARY KEY auto_increment,
    ID_Paciente INTEGER NOT NULL,
    ID_Tratamiento INTEGER NOT NULL,
    Log_sistema TEXT NOT NULL,
    FechaEvaluacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (ID_Paciente) REFERENCES Pacientes(ID_Paciente),
    FOREIGN KEY (ID_Tratamiento) REFERENCES Tratamientos(ID_Tratamiento)
);

CREATE TABLE Habilidades (
    ID_Habilidad INTEGER PRIMARY KEY auto_increment,
    Nombre VARCHAR(100) NOT NULL
);

CREATE TABLE Actividades (
    ID_Actividad INTEGER PRIMARY KEY auto_increment,
    ID_Habilidad INTEGER NOT NULL,
    Nombre VARCHAR(100) NOT NULL,
    FOREIGN KEY (ID_Habilidad) REFERENCES Habilidades (ID_Habilidad)
);

CREATE TABLE Respuestas_Actividad (
    ID_Respuesta INT PRIMARY KEY auto_increment,
    ID_Pregunta INT,
    ID_Paciente INT NOT NULL,
    ID_Actividad INT NOT NULL,
    Respuesta TEXT NOT NULL,
    Fecha_Registro DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (ID_Paciente) REFERENCES Pacientes(ID_Paciente),
    FOREIGN KEY (ID_Actividad) REFERENCES Actividades(ID_Actividad)
);

CREATE TABLE Tratamiento_Habilidad_Actividad (
    ID_Tratamiento INTEGER NOT NULL,
    ID_Habilidad INTEGER NOT NULL,
    ID_Actividad INTEGER NOT NULL,
    FOREIGN KEY (ID_Tratamiento) REFERENCES Tratamientos (ID_Tratamiento),
    FOREIGN KEY (ID_Habilidad) REFERENCES Habilidades (ID_Habilidad),
    FOREIGN KEY (ID_Actividad) REFERENCES Actividades (ID_Actividad)
);

CREATE TABLE Paciente_Tratamiento (
    ID_Paciente INTEGER NOT NULL,
    ID_Tratamiento INTEGER NOT NULL,
    FechaInicio DATE NOT NULL,
    PRIMARY KEY (ID_Paciente, ID_Tratamiento),
    FOREIGN KEY (ID_Paciente) REFERENCES Pacientes (ID_Paciente),
    FOREIGN KEY (ID_Tratamiento) REFERENCES Tratamientos (ID_Tratamiento)
);

CREATE TABLE Paciente_Actividad (
    ID_Paciente INTEGER NOT NULL,
    ID_Actividad INTEGER NOT NULL,
    FechaCompletada DATE,
    Completada BOOLEAN DEFAULT FALSE,
    PRIMARY KEY (ID_Paciente, ID_Actividad),
    FOREIGN KEY (ID_Paciente) REFERENCES Pacientes (ID_Paciente),
    FOREIGN KEY (ID_Actividad) REFERENCES Actividades (ID_Actividad)
);

CREATE TABLE Paciente_Habilidad (
    ID_Paciente INTEGER NOT NULL,
    ID_Habilidad INTEGER NOT NULL,
    FechaCompletada DATE,
    Completada BOOLEAN DEFAULT FALSE,
    PRIMARY KEY (ID_Paciente, ID_Habilidad),
    FOREIGN KEY (ID_Paciente) REFERENCES Pacientes (ID_Paciente),
    FOREIGN KEY (ID_Habilidad) REFERENCES Habilidades (ID_Habilidad)
);

CREATE TABLE ProgresoPaciente (
    ID_Paciente INTEGER NOT NULL,
    ID_Tratamiento INTEGER NOT NULL,
    ID_Habilidad INTEGER,
    ID_Actividad INTEGER,
    FechaInicio DATE,
    PRIMARY KEY (ID_Paciente),
    FOREIGN KEY (ID_Paciente) REFERENCES Pacientes (ID_Paciente),
    FOREIGN KEY (ID_Tratamiento) REFERENCES Tratamientos (ID_Tratamiento),
    FOREIGN KEY (ID_Habilidad) REFERENCES Habilidades (ID_Habilidad),
    FOREIGN KEY (ID_Actividad) REFERENCES Actividades (ID_Actividad)
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

INSERT INTO TipoENTs (NombreENT) VALUES
('Enfermedades cardiovasculares'),
('Diabetes'),
('Cáncer'),
('Enfermedades renales'),
('Enfermedad respiratorias crónicas'),
('Ninguno');

-- Insertar los formularios iniciales en el catálogo
INSERT INTO TiposFormulario (NombreFormulario) VALUES
('Inventario de Ansiedad de Beck (BAI)'),
('Inventario de Depresión de Beck (BDI-II)'),
('MINI - Apartado riesgo suicida'),
('(WBI5) Índice de Bienestar General-5 de la Organización Mundial de la Salud'),
('Escala de Estrés Percibido -14 (PSS-14)'),
('Escala de Atención Plena MAAS'),
('APOI Desfavorable'),
('APOI Favorable'),
('Índice de Calidad de Sueño de Pittsburgh'),
('Escala de Autocompasión (SCS)'),
('Entrevista Chatbot');

-- Insertar las preguntas del BAI
INSERT INTO Preguntas(ID_Pregunta, ID_TipoFormulario, Texto) VALUES
(1, 1, 'Hormigueo o entumecimiento'),
(2, 1, 'Sensación de calor'),
(3, 1, 'Temblor en las piernas'),
(4, 1, 'Incapacidad de relajarse'),
(5, 1, 'Miedo a que suceda lo peor'),
(6, 1, 'Mareo o aturdimiento'),
(7, 1, 'Palpitaciones o taquicardia'),
(8, 1, 'Sensación de inestabilidad e inseguridad física'),
(9, 1, 'Terrores'),
(10, 1, 'Nerviosismo'),
(11, 1, 'Sensación de ahogo'),
(12, 1, 'Temblores de manos'),
(13, 1, 'Temblor generalizado o estremecimiento'),
(14, 1, 'Miedo a perder el control'),
(15, 1, 'Dificultad para respirar'),
(16, 1, 'Miedo a morirse'),
(17, 1, 'Sobresaltos'),
(18, 1, 'Molestias digestivas o abdominales'),
(19, 1, 'Palidez'),
(20, 1, 'Rubor facial'),
(21, 1, 'Sudoración (no debida al calor)');

-- Insertar las preguntas del beck
INSERT INTO Preguntas(ID_Pregunta, ID_TipoFormulario, Texto) VALUES
(22, 2, 'Tristeza'),
(23, 2, 'Pesimismo'),
(24, 2, 'Fracasos del pasado'),
(25, 2, 'Pérdida del placer'),
(26, 2, 'Sentimientos de culpa'),
(27, 2, 'Sentimientos de castigo'),
(28, 2, 'Desagrado con uno mismo'),
(29, 2, 'Auto-crítica'),
(30, 2, 'Ideación o deseos suicidas'),
(31, 2, 'Llanto'),
(32, 2, 'Inquietud'),
(33, 2, 'Pérdida del interés'),
(34, 2, 'Indecisión'),
(35, 2, 'Inutilidad'),
(36, 2, 'Pérdida de energía'),
(37, 2, 'Cambios en los patrones de sueño'),
(38, 2, 'Irritabilidad'),
(39, 2, 'Cambios en los hábitos alimenticios'),
(40, 2, 'Dificultad para concentrarse'),
(41, 2, 'Cansancio o fatiga'),
(42, 2, 'Pérdida de interés en el sexo');

-- Insertar las preguntas para el MINI apartado de riesgo suicida 
INSERT INTO Preguntas(ID_Pregunta, ID_TipoFormulario, Texto) VALUES
(43, 3, '¿Ha pensado que sería mejor morirse o ha deseado estar muerto(a)?'),
(44, 3, '¿Ha querido hacerse daño?'),
(45, 3, '¿Ha pensado en el suicidio?'),
(46, 3, '¿Ha planeado suicidarse?'),
(47, 3, '¿Ha intentado suicidarse?'),
(48, 3, '¿Alguna vez ha intentado suicidarse?');

-- Insertar las preguntas para el indice de bienestar
INSERT INTO Preguntas(ID_Pregunta, ID_TipoFormulario, Texto) VALUES
(49, 4, '¿Me he sentido alegre y de buen ánimo?'),
(50, 4, '¿Me he sentido tranquilo/a y relajado/a?'),
(51, 4, '¿Me he sentido activo/a y con energía?'),
(52, 4, '¿Me he levantado sintiéndome bien y descansado/a?'),
(53, 4, '¿Mi vida diaria ha tenido cosas interesantes para mí?');

-- Insertar las preguntas para el de escala de estres
INSERT INTO Preguntas(ID_Pregunta, ID_TipoFormulario, Texto) VALUES
(54, 5, '¿Con qué frecuencia has estado afectado/a por algo que ha ocurrido inesperadamente?'),
(55, 5, '¿Con qué frecuencia te has sentido incapaz de controlar las cosas importantes de tu vida?'),
(56, 5, '¿Con qué frecuencia te has sentido nervioso/a o estresado/a?'),
(57, 5, '¿Con qué frecuencia has manejado con éxito los pequeños problemas irritantes de la vida?'),
(58, 5, '¿Con qué frecuencia has sentido que has afrontado efectivamente los cambios importantes que han estado ocurriendo en tu vida?'),
(59, 5, '¿Con qué frecuencia has estado seguro/a sobre tu capacidad de manejar tus problemas personales?'),
(60, 5, '¿Con qué frecuencia has sentido que las cosas te van bien?'),
(61, 5, '¿Con qué frecuencia has sentido que no podías afrontar todas las cosas que tenías que hacer?'),
(62, 5, '¿Con qué frecuencia has podido controlar las dificultades de tu vida?'),
(63, 5, '¿Con qué frecuencia has sentido que tienes el control de todo?'),
(64, 5, '¿Con qué frecuencia has estado enfadado/a porque las cosas que te han ocurrido estaban fuera de tu control?'),
(65, 5, '¿Con qué frecuencia has pensado sobre las cosas que no has terminado?'),
(66, 5, '¿Con qué frecuencia has podido controlar la forma de pasar el tiempo?'),
(67, 5, '¿Con qué frecuencia has sentido que las dificultades se acumulan tanto que no puedes superarlas?');

-- Insertar las preguntas para el de escala de atencion plena
INSERT INTO Preguntas(ID_Pregunta, ID_TipoFormulario, Texto) VALUES
(68, 6, 'Puedo sentir una emoción y no estar consciente de ella hasta tiempo después.'),
(69, 6, 'Rompo o derramo cosas por descuido, al no poner atención, o porque estoy pensando en otra cosa.'),
(70, 6, 'Se me hace difícil permanecer concentrado en lo que está sucediendo en un momento dado.'),
(71, 6, 'Tiendo a caminar rápidamente para llegar a donde tengo que ir, sin poner mucha atención a lo que ocurre alrededor.'),
(72, 6, 'Tiendo a no percibir la tensión física o el nivel de incomodidad a que estoy sometido, hasta que realmente son evidentes.'),
(73, 6, 'Se me olvidan los nombres de las personas, inmediatamente después de que me presentan a alguien.'),
(74, 6, 'Parece como si estuviera funcionando de manera «automática» sin darme cuenta de lo que estoy haciendo.'),
(75, 6, 'Me apresuro a hacer mis tareas sin realmente prestarles mucha atención a lo que hago.'),
(76, 6, 'Me concentro tanto en la meta que quiero alcanzar que pierdo contacto con lo que estoy haciendo para conseguirla.'),
(77, 6, 'Realizo trabajos automáticamente, sin ponerle mucha atención a lo que hago.'),
(78, 6, 'Escucho a mi interlocutor con un oído, mientras hago otra cosa simultáneamente.'),
(79, 6, 'Llego a un lugar en «piloto automático» y luego me pregunto qué iba a hacer en ese lugar.'),
(80, 6, 'Me preocupo por cosas que pueden ocurrir en el futuro o por asuntos del pasado.'),
(81, 6, 'Hago cosas sin ponerles mucha atención.'),
(82, 6, 'Como entre comidas sin estar consciente de que estoy comiendo.');

-- Insertar las preguntas para la evaluacion APOI desfavorable
INSERT INTO Preguntas(ID_Pregunta, ID_TipoFormulario, Texto) VALUES
(83, 7, 'Si quiero aprender habilidades para gestionar mejor mi vida, prefiero un terapeuta antes que una intervención psicológica online.'),
(84, 7, 'Es más probable que me mantenga motivada/o con un terapeuta que con una intervención psicológica online.'),
(85, 7, 'En situaciones de crisis, un terapeuta puede ayudarme mejor que una intervención psicológica online.');

-- Insertar las preguntas para la evaluacion APOI favorable
INSERT INTO Preguntas(ID_Pregunta, ID_TipoFormulario, Texto) VALUES
(86, 8, 'Una intervención psicológica online puede ayudarme a reconocer los problemas que tengo que enfrentar.'),
(87, 8, 'Una intervención psicológica online puede inspirarme para abordar mejor mis problemas.'),
(88, 8, 'Creo que el concepto de intervenciones psicológicas online tiene sentido.'),
(89, 8, 'Tengo la sensación de que una intervención psicológica online puede ayudarme.');

-- Insertar las preguntas para el indice de calidad de sueño de pitsburg
INSERT INTO Preguntas(ID_Pregunta, ID_TipoFormulario, Texto) VALUES
(90, 9,  "Durante el último mes, ¿cuál ha sido, usualmente, su hora de acostarse?"),
(91, 9, "Durante el último mes, ¿cuánto tiempo ha tardado en dormirse en las noches del último mes?"),
(92, 9, "Durante el último mes, ¿a que hora se ha estado levantando por la mañana?"),
(93, 9, "¿Cuántas horas calcula que habrá dormido verdaderamente cada noche durante el último mes?"),
(94, 9, "Respuesta personalizada"),
(95, 9 , "Durante el último mes, ¿cuántas veces ha tenido problemas para dormir a causa de (Respuesta personalizada): "),
(96, 9, "Durante el último mes, ¿cuántas veces ha tenido problemas para dormir a causa de no poder conciliar el sueño en la primera media hora?"),
(97, 9, "Durante el último mes, ¿cuántas veces ha tenido problemas para dormir a causa de despertarse durante la noche o de madrugada?"),
(98, 9, "Durante el último mes, ¿cuántas veces ha tenido problemas para dormir a causa de tener que levantarse para ir al sanitario?"),
(99, 9, "Durante el último mes, ¿cuántas veces ha tenido problemas para dormir a causa de no poder respirar bien?"),
(100, 9, "Durante el último mes, ¿cuántas veces ha tenido problemas para dormir a causa de toser o roncar ruidosamente?"),
(101, 9, "Durante el último mes, ¿cuántas veces ha tenido problemas para dormir a causa de sentir frío?"),
(102, 9, "Durante el último mes, ¿cuántas veces ha tenido problemas para dormir a causa de sentir demasiado calor?"),
(103, 9, "Durante el último mes, ¿cuántas veces ha tenido problemas para dormir a causa de tener pesadillas o “malos sueños”?"),
(104, 9, "Durante el último mes, ¿cuántas veces ha tenido problemas para dormir a causa de sufrir dolores?"),
(105, 9, "Durante el último mes, ¿cuántas veces ha tenido problemas para dormir a causa de otras razones?"),
(106, 9, "Durante el último mes ¿cómo valoraría, en conjunto, la calidad de su dormir?"),
(107, 9, "Durante el último mes, ¿cuántas veces habrá tomado medicinas (por su cuenta o recetadas por el médico) para dormir?"),
(108, 9, "Durante el último mes, ¿cuántas veces ha sentido somnolencia mientras conducía, comía o desarrollaba alguna otra actividad?"),
(109, 9, "Durante el último mes, ¿ha representado para usted mucho problema el “tener ánimos” para realizar alguna de las actividades detalladas en la pregunta anterior?");

-- Insertar las preguntas para el de autocompasion
INSERT INTO Preguntas(ID_Pregunta, ID_TipoFormulario, Texto) VALUES
(110, 10, 'Me desapruebo y me juzgo por mis defectos y limitaciones.'),
(111, 10, 'Cuando me siento desanimado tiendo a obsesionarme y fijarme en todo lo que está mal.'),
(112, 10, 'Cuando las cosas van mal para mí, veo las dificultades como una parte de la vida por la que todos pasan.'),
(113, 10, 'Cuando pienso en mis limitaciones tiendo a sentirme más separado y aislado del resto del mundo.'),
(114, 10, 'Intento ser cariñoso/a conmigo mismo/a cuando siento dolor emocional.'),
(115, 10, 'Cuando fallo en algo importante para mí, me consumen los sentimientos de insuficiencia.'),
(116, 10, 'Cuando me siento desanimado y triste, me recuerdo a mí mismo que hay muchas otras personas en el mundo que se sienten como yo.'),
(117, 10, 'Cuando atravieso épocas muy difíciles, tiendo a ser duro/a conmigo mismo/a.'),
(118, 10, 'Cuando algo me molesta, trato de mantener mis emociones en equilibrio.'),
(119, 10, 'Cuando me siento incapaz de alguna manera, trato de recordarme que esos sentimientos de incapacidad son compartidos por la mayoría de las personas.'),
(120, 10, 'Soy intolerante e impaciente con aquellos aspectos de mi personalidad que no me gustan.'),
(121, 10, 'Cuando atravieso una situación muy difícil, yo mismo/a me proporciono el cuidado y cariño que necesito.'),
(122, 10, 'Cuando me siento desanimado/a, tiendo a sentir que probablemente la mayoría de las personas son más felices que yo.'),
(123, 10, 'Cuando sucede algo doloroso, trato de tener una visión equilibrada de la situación.'),
(124, 10, 'Intento ver mis fallas como parte de la condición humana.'),
(125, 10, 'Cuando veo aspectos de mí mismo/a que no me gustan, me deprimo.'),
(126, 10, 'Cuando me equivoco en algo importante para mí, trato de ver las cosas con perspectiva.'),
(127, 10, 'Cuando realmente estoy en problemas, tiendo a sentir que a otras personas les debe resultar más fácil.'),
(128, 10, 'Soy amable conmigo mismo/a cuando estoy experimentando sufrimiento.'),
(129, 10, 'Cuando algo me molesta me dejo llevar por mis sentimientos.'),
(130, 10, 'Puedo ser un poco insensible hacia mí mismo/a cuando experimento sufrimiento.'),
(131, 10, 'Cuando me siento deprimido/a trato de observar mis sentimientos con curiosidad y mente abierta.'),
(132, 10, 'Soy intolerante con mis propios defectos y limitaciones.'),
(133, 10, 'Cuando sucede algo doloroso tiendo a exagerar la gravedad del incidente.'),
(134, 10, 'Cuando fallo en algo que es importante para mí, tiendo a sentirme solo en mi fracaso.'),
(135, 10, 'Intento ser comprensivo y paciente con aquellos aspectos de mi personalidad que no me gustan.');

-- Insertar las preguntas para la entrevista con el Chatbot
INSERT INTO Preguntas(ID_Pregunta, ID_TipoFormulario, Texto) VALUES
(136, 11, '¿Me gustaría saber si has estado en terapia psicológica antes?'),
(137, 11, '¿Hace cuánto fue esa terapia, en meses?'),
(138, 11, '¿Cuánto tiempo consideras que dedicas a la semana  a tu salud emocional (talleres, podcast, asesorías, etc)?'),
(139, 11, '¿Cuánto tiempo dedicas a la semana a realizar actividades físicas (deportes como correr, nadar, pesas, o a través de caminar, correr o baile, etc?)'),
(140, 11, '¿Cuánto tiempo dedicas a la semana a tu la convivencia con tu red social (encontrarte con vecinos, amistades, familiares, o en clubes de pasatiempos, grupos deportivos o culturales, etc?)'),
(141, 11, '¿Sabes en qué consiste el concepto mindfulness?'),
(142, 11, '¿Has practicado mindfulness?'),
(143, 11, '¿Cuántas horas a la semana?'),
(144, 11, '¿En qué nivel de practicante te identificas?'),
(145, 11, 'Un elemento fundamental para que las actividades de mindfulness tengan un impacto positivo en la vida es la constancia diaria de las prácticas, nos gustaría enviarte recordatorios para realizar tus prácticas. ¿En qué horario quieres que te envíe un recordatorio para hacer tus prácticas de SerenaMente IA?'),
(146, 11, '¿Qué dificultades crees que puede haber en tu práctica de mindfulness?'),
(147, 11, '¿Qué te gustaría lograr o mejorar con la práctica de mindfulness?');

-- Crear los valores de los diferentes tratamientos
INSERT INTO Tratamientos(ID_Tratamiento, Nivel) VALUES
(1, "Leve"),
(2, "Moderado"),
(3, "Alto");

-- Insertar datos de todas las habilidades
INSERT INTO Habilidades (ID_Habilidad, Nombre) VALUES
(1,"Comenzar a trabajar en mi"),
(2,"Ser y estar"),
(3,"De la Distracción a la Conciencia"),
(4,"El poder de estar presente"),
(5,"Re-Conocer el Estrés"),
(6,"Comunicación que Conecta"),
(7,"Cuidarte es volver a ti"),
(8,"Final del Tratamiento");


-- Insertar los valores de las habilidades
INSERT INTO Actividades (ID_Actividad, ID_Habilidad, Nombre) VALUES
(1,1,"Qué es mindfulness y cómo puede ayudarme"),
(2,1,"Ya sé que es mindfulness, ¿qué sigue?"),
(3,1,"Respiración Consciente"),
(4,2,"Práctica: Consciencia en mi respiración"),
(5,2,"Práctica: Meditación de la montaña"),
(6,2,"Práctica: Escaneo corporal"),
(7,2,"Práctica: Yoga consciente"),
(8,3,"Meditación para Ver"),
(9,3,"Práctica de Aceptación y No Juicio"),
(10,3,"Práctica Breve de Yoga"),
(11,3,"Escaneo Corporal"),
(12,4,"Meditación sentada"),
(13,4,"Meditación caminando"),
(14,4,"Práctica Breve de Yoga"),
(15,4,"Introducción al escaneo"),
(16,5,"Entendiendo la Rueda de la Consciencia"),
(17,5,"Practicando la Rueda de la Consciencia"),
(18,5,"Práctica Breve de Yoga"),
(19,5,"Atender el conflicto interno"),
(20,6,"Tejiendo Conexiones Conscientes"),
(21,6,"Pausa y Elige tu Respuesta"),
(22,6,"La Montaña Interior en tus Vínculos"),
(23,6,"Presencia Consciente en tus Conversaciones"),
(24,7,"Actividades que Nutren"),
(25,7,"Presencia Sostenida en la Vida Real"),
(26,7,"Respiración Consciente"),
(27,7,"Meditación de la Montaña"),
(28,8,"Final del Tratamiento");

-- Hacer las insercion de valores para el tratamiento 1 hasta la habilidad 7
INSERT INTO Tratamiento_Habilidad_Actividad (ID_Tratamiento, ID_Habilidad, ID_Actividad) VALUES
-- Actividades que se mostraran de las habilidades 0 para cada tratamiento
(1,1,1),
(1,1,2),
(1,1,3),
(1,2,4),
(1,2,5),
(1,3,8),
(1,3,9),
(1,4,12),
(1,4,13),
(1,5,16),
(1,5,17),
(1,6,20),
(1,6,21),
(1,7,24),
(1,7,25),
(1,8,28);


-- Hacer las insercion de valores para el tratamiento 2 hasta la habilidad 7
INSERT INTO Tratamiento_Habilidad_Actividad (ID_Tratamiento, ID_Habilidad, ID_Actividad) VALUES
-- Actividades que se mostraran de las habilidades 0 para cada tratamiento
(2,1,1),
(2,1,2),
(2,1,3),
(2,2,4),
(2,2,5),
(2,2,6),
(2,3,8),
(2,3,9),
(2,3,10),
(2,4,12),
(2,4,13),
(2,4,14),
(2,5,16),
(2,5,17),
(2,5,18),
(2,6,20),
(2,6,21),
(2,6,22),
(2,7,24),
(2,7,25),
(2,7,26),
(2,8,28);

-- Hacer las insercion de valores para el tratamiento 3 hasta la habilidad 7
INSERT INTO Tratamiento_Habilidad_Actividad (ID_Tratamiento, ID_Habilidad, ID_Actividad) VALUES
-- Actividades que se mostraran de las habilidades 0 para cada tratamiento
(3,1,1),
(3,1,2),
(3,1,3),
(3,2,4),
(3,2,5),
(3,2,6),
(3,2,7),
(3,3,8),
(3,3,9),
(3,3,10),
(3,3,11),
(3,4,12),
(3,4,13),
(3,4,14),
(3,4,15),
(3,5,16),
(3,5,17),
(3,5,18),
(3,5,19),
(3,6,20),
(3,6,21),
(3,6,22),
(3,6,23),
(3,7,24),
(3,7,25),
(3,7,26),
(3,7,27),
(3,8,28);

-- Agregamos el usuario 1 de administrador 
INSERT INTO Admins (Usuario, Contrasena)
VALUES ('admin', '4813494d137e1631bba301d5acab6e7bb7aa74ce1185d456565ef51d737677b2');