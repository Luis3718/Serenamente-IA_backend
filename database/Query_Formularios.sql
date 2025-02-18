use SerenaMenteDB;
SELECT
    p.Nombre AS 'Nombre',
    f.ID_TipoFormulario AS 'Tipo de Formulario',
	tf.NombreFormulario AS 'Nombre de Formulario Contestado',
    q.Texto AS 'Pregunta',
    r.Respuesta AS 'Respuesta',
    f.Fecha_Respuesta AS 'Fecha Contestado'
FROM
    Pacientes p
INNER JOIN Formularios f ON p.ID_Paciente = f.ID_Paciente
INNER JOIN TiposFormulario tf ON f.ID_TipoFormulario = tf.ID_TipoFormulario
INNER JOIN Respuestas r ON p.ID_Paciente = r.ID_Paciente
INNER JOIN Preguntas q ON r.ID_Pregunta = q.ID_Pregunta AND q.ID_TipoFormulario = tf.ID_TipoFormulario
WHERE
    p.ID_Paciente = 1;  -- Asumiendo que quieres buscar por un ID específico
