
:- use_module(library(csv)).

% 📌 Leer datos desde un archivo CSV y almacenarlos en hechos
leer_datos_excel(Archivo) :-
    writeln('📥 Cargando archivo CSV...'),
    csv_read_file(Archivo, Filas, [functor(datos), arity(5)]),
    length(Filas, N),
    format('✔ Archivo leído correctamente. Número de filas: ~w~n', [N]),
    maplist(assertz, Filas).

% 📌 Tabla de tratamientos según nivel
tratamiento('ALTO', 'Terapia Intensiva').
tratamiento('MODERADO', 'Seguimiento Psicológico').
tratamiento('LEVE', 'Ejercicios de Autoayuda').

% 📌 Definición de rangos para cada nivel
rango(depresion, leve, 0, 13).
rango(depresion, moderado, 14, 20).
rango(depresion, alto, 21, 29).

rango(ansiedad, leve, 0, 13).
rango(ansiedad, moderado, 14, 20).
rango(ansiedad, alto, 21, 31).

rango(estres, leve, 0, 18).
rango(estres, moderado, 19, 37).
rango(estres, alto, 38, 56).

rango(compasion, leve, 1, 2.5).
rango(compasion, moderado, 2.6, 3.4).
rango(compasion, alto, 3.5, 5).

% 📌 Determinar nivel según los rangos
nivel(Tipo, Categoria, Puntaje) :-
    rango(Tipo, Categoria, Min, Max),
    Puntaje >= Min,
    Puntaje =< Max.

% 📌 Reglas de inferencia corregidas para evaluar a todos los pacientes
nivel_intervencion(ID, 'ALTO') :-
    datos(ID, Depresion, Ansiedad, Estres, Compasion),
    (nivel(depresion, alto, Depresion);
     nivel(ansiedad, alto, Ansiedad);
     nivel(estres, alto, Estres);
     nivel(compasion, alto, Compasion)), !.

nivel_intervencion(ID, 'MODERADO') :-
    datos(ID, Depresion, Ansiedad, Estres, _),
    (nivel(depresion, moderado, Depresion);
     nivel(ansiedad, moderado, Ansiedad);
     nivel(estres, moderado, Estres)), !.

   nivel_intervencion(ID, 'LEVE') :-
    datos(ID, Depresion, Ansiedad, Estres, Compasion),
    nivel(depresion, leve, Depresion),
    nivel(ansiedad, leve, Ansiedad),
    nivel(estres, leve, Estres),
    nivel(compasion, moderado, Compasion),
    !.


nivel_intervencion(ID, 'LEVE') :-
    datos(ID, _, _, _, Compasion),
    nivel(compasion, alto, Compasion), !.

nivel_intervencion(ID, 'SIN DATOS').

% 📌 Procesar todos los pacientes sin repetir
procesar_datos :-
    writeln('🔍 Procesando datos de pacientes...'),
    findall(ID, datos(ID, _, _, _, _), ListaIDs),
    sort(ListaIDs, PacientesUnicos), % Asegura que no haya duplicados
    forall(member(ID, PacientesUnicos), procesar_paciente(ID)).

procesar_paciente(ID) :-
    nivel_intervencion(ID, Nivel),
    (   tratamiento(Nivel, Tratamiento)
    ->  format('📌 Paciente ~w: Nivel ~w - Recomendación: ~w~n', [ID, Nivel, Tratamiento])
    ;   format('⚠ Paciente ~w: Nivel desconocido~n', [ID])).

% 📌 Cargar y procesar datos al inicio
:- leer_datos_excel('datos.csv'), procesar_datos.

