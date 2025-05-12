use SerenaMenteDB;
describe Pacientes;
select * from Pacientes;	
select * from TiposFormulario;
Select * From Preguntas;
select * from Respuestas;
select * from Resultados;
select * from Formularios;
select * from tratamientos;
select * from Paciente_Tratamiento;
select * from ProgresoPaciente;

SELECT 
    ID_Paciente,
    ID_Pregunta,
    Respuesta
FROM 
    Respuestas_Actividad
WHERE 
    ID_Actividad = 26; -- Cambia el número por el ID de la actividad que quieras consultar

SELECT *
FROM Paciente_Actividad
WHERE ID_Paciente = 1
AND Completada = 1
ORDER BY FechaCompletada ASC;

-- drop database  serenamentedb;	