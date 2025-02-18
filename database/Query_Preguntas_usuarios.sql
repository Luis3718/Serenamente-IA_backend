SELECT
    q.Texto AS 'Pregunta',
    r.Respuesta AS 'Respuesta'
FROM
    Formularios f
INNER JOIN Pacientes p ON f.ID_Paciente = p.ID_Paciente
INNER JOIN TiposFormulario tf ON f.ID_TipoFormulario = tf.ID_TipoFormulario
INNER JOIN Preguntas q ON tf.ID_TipoFormulario = q.ID_TipoFormulario
INNER JOIN Respuestas r ON q.ID_Pregunta = r.ID_Pregunta AND r.ID_Paciente = p.ID_Paciente
WHERE
    f.ID_Formulario = 1;  -- Asegúrate de reemplazar '1' con el ID de formulario que deseas consultar
