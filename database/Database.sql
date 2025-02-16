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
    Texto VARCHAR(255) NOT NULL,
    FOREIGN KEY (ID_TipoFormulario) REFERENCES Tiposformulario(ID_TipoFormulario)
);

-- Tabla de respuestas a las preguntas del formulario
CREATE TABLE Respuestas (
    ID_Respuesta INTEGER PRIMARY KEY auto_increment,
    ID_Pregunta INTEGER NOT NULL,
    ID_Paciente INTEGER NOT NULL,
    Respuesta TEXT NOT NULL,
    FOREIGN KEY (ID_Pregunta) REFERENCES Preguntas(ID_Pregunta),
    FOREIGN KEY (ID_Paciente) REFERENCES Pacientes(ID_Paciente)
);

-- Tabla de calificaciones para los formularios
CREATE TABLE Calificaciones (
    ID_Calificacion INTEGER PRIMARY KEY auto_increment,
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

-- Insertar las preguntas para la evaluacion APOI
INSERT INTO Preguntas(ID_Pregunta, ID_TipoFormulario, Texto) VALUES
(83, 7, 'Si quiero aprender habilidades para gestionar mejor mi vida, prefiero un terapeuta antes que una intervención psicológica online.'),
(84, 7, 'Una intervención psicológica online puede ayudarme a reconocer los problemas que tengo que enfrentar.'),
(85, 7, 'Una intervención psicológica online puede inspirarme para abordar mejor mis problemas.'),
(86, 7, 'Creo que el concepto de intervenciones psicológicas online tiene sentido.'),
(87, 7, 'Tengo la sensación de que una intervención psicológica online puede ayudarme.'),
(88, 7, 'Es más probable que me mantenga motivada/o con un terapeuta que con una intervención psicológica online.'),
(89, 7, 'En situaciones de crisis, un terapeuta puede ayudarme mejor que una intervención psicológica online.');

-- Insertar las preguntas para el de autocompasion
INSERT INTO Preguntas(ID_Pregunta, ID_TipoFormulario, Texto) VALUES
(90, 8, 'Me desapruebo y me juzgo por mis defectos y limitaciones.'),
(91, 8, 'Cuando me siento desanimado tiendo a obsesionarme y fijarme en todo lo que está mal.'),
(92, 8, 'Cuando las cosas van mal para mí, veo las dificultades como una parte de la vida por la que todos pasan.'),
(93, 8, 'Cuando pienso en mis limitaciones tiendo a sentirme más separado y aislado del resto del mundo.'),
(94, 8, 'Intento ser cariñoso/a conmigo mismo/a cuando siento dolor emocional.'),
(95, 8, 'Cuando fallo en algo importante para mí, me consumen los sentimientos de insuficiencia.'),
(96, 8, 'Cuando me siento desanimado y triste, me recuerdo a mí mismo que hay muchas otras personas en el mundo que se sienten como yo.'),
(97, 8, 'Cuando atravieso épocas muy difíciles, tiendo a ser duro/a conmigo mismo/a.'),
(98, 8, 'Cuando algo me molesta, trato de mantener mis emociones en equilibrio.'),
(99, 8, 'Cuando me siento incapaz de alguna manera, trato de recordarme que esos sentimientos de incapacidad son compartidos por la mayoría de las personas.'),
(100, 8, 'Soy intolerante e impaciente con aquellos aspectos de mi personalidad que no me gustan.'),
(101, 8, 'Cuando atravieso una situación muy difícil, yo mismo/a me proporciono el cuidado y cariño que necesito.'),
(102, 8, 'Cuando me siento desanimado/a, tiendo a sentir que probablemente la mayoría de las personas son más felices que yo.'),
(103, 8, 'Cuando sucede algo doloroso, trato de tener una visión equilibrada de la situación.'),
(104, 8, 'Intento ver mis fallas como parte de la condición humana.'),
(105, 8, 'Cuando veo aspectos de mí mismo/a que no me gustan, me deprimo.'),
(106, 8, 'Cuando me equivoco en algo importante para mí, trato de ver las cosas con perspectiva.'),
(107, 8, 'Cuando realmente estoy en problemas, tiendo a sentir que a otras personas les debe resultar más fácil.'),
(108, 8, 'Soy amable conmigo mismo/a cuando estoy experimentando sufrimiento.'),
(109, 8, 'Cuando algo me molesta me dejo llevar por mis sentimientos.'),
(110, 8, 'Puedo ser un poco insensible hacia mí mismo/a cuando experimento sufrimiento.'),
(111, 8, 'Cuando me siento deprimido/a trato de observar mis sentimientos con curiosidad y mente abierta.'),
(112, 8, 'Soy intolerante con mis propios defectos y limitaciones.'),
(113, 8, 'Cuando sucede algo doloroso tiendo a exagerar la gravedad del incidente.'),
(114, 8, 'Cuando fallo en algo que es importante para mí, tiendo a sentirme solo en mi fracaso.'),
(115, 8, 'Intento ser comprensivo y paciente con aquellos aspectos de mi personalidad que no me gustan.');
