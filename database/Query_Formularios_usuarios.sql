SELECT DISTINCT
    p.Nombre AS 'Nombre',
    tf.NombreFormulario AS 'Tipo de Formulario',
    f.ID_TipoFormulario AS 'Nombre de Formulario Contestado',
    f.Fecha_Respuesta AS 'Fecha Contestado'
FROM
    Pacientes p
INNER JOIN Formularios f ON p.ID_Paciente = f.ID_Paciente
INNER JOIN TiposFormulario tf ON f.ID_TipoFormulario = tf.ID_TipoFormulario
WHERE
    p.ID_Paciente = 1;  -- Cambia esto por el ID del paciente que estás consultando
