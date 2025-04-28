use SerenaMenteDB;
-- 1. Borrar las respuestas asociadas a la actividad 27
DELETE FROM Respuestas_Actividad
WHERE ID_Actividad = 27
AND ID_Paciente = 1;

-- 2. Borrar el histórico de la actividad 27 como completada
DELETE FROM Paciente_Actividad
WHERE ID_Actividad = 27
AND ID_Paciente = 1;

-- 3. Actualizar el progreso para que vuelva a estar en actividad 26
UPDATE ProgresoPaciente
SET ID_Actividad = 27
WHERE ID_Paciente = 1;

DELETE FROM Paciente_Habilidad
WHERE ID_Paciente = 1
AND ID_Habilidad = 7;

INSERT INTO Habilidades (ID_Habilidad, Nombre)
VALUES (8, 'Final del Tratamiento');

select * from Habilidades;

INSERT INTO Actividades (ID_Actividad, ID_Habilidad, Nombre)
VALUES (28, 8, 'Final del Tratamiento');

select * from actividades;

INSERT INTO Tratamiento_Habilidad_Actividad (ID_Tratamiento, ID_Habilidad, ID_Actividad)
VALUES (3, 8, 28);

select * from tratamiento_habilidad_actividad;
