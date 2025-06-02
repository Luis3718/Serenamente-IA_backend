import pandas as pd
from database import engine
import os

def exportar_pretest_completo(): 
    engine
    try:
        print("🟢 Iniciando exportación del Pretest...")

        output_dir = os.path.dirname(os.path.abspath(__file__))
        output_path = os.path.join(output_dir, "Pretest_Completo.xlsx")

        # 1. Obtener nombres de formularios
        formularios_df = pd.read_sql("SELECT id_tipoformulario, nombreformulario FROM tipos_formulario", engine)
        formulario_nombre = {
            row.id_tipoformulario: row.nombreformulario.split("(")[-1].replace(")", "").replace(" ", "").upper()
            for _, row in formularios_df.iterrows()
        }

        # 2. Obtener las preguntas (ordenadas)
        preguntas_df = pd.read_sql("""
            SELECT id_pregunta, id_tipoformulario, texto
            FROM preguntas
            WHERE id_tipoformulario BETWEEN 1 AND 11
            ORDER BY id_tipoformulario, id_pregunta
        """, engine)

        preguntas_por_formulario = preguntas_df.groupby("id_tipoformulario")

        # 3. Formularios más antiguos por tipo y paciente
        formularios_df = pd.read_sql("""
            WITH formularios_ordenados AS (
              SELECT *,
                     ROW_NUMBER() OVER (
                       PARTITION BY id_paciente, id_tipoformulario
                       ORDER BY fecha_respuesta ASC
                     ) AS rn
              FROM formularios
              WHERE id_tipoformulario BETWEEN 1 AND 11
            )
            SELECT *
            FROM formularios_ordenados
            WHERE rn = 1
        """, engine)

        # 4. Respuestas asociadas a esos formularios
        respuestas_df = pd.read_sql("""
            SELECT r.id_paciente, r.id_pregunta, r.respuesta
            FROM respuestas r
            JOIN preguntas p ON r.id_pregunta = p.id_pregunta
            WHERE p.id_tipoformulario BETWEEN 1 AND 11
        """, engine)

        # 5. Resultados por formulario más antiguo
        resultados_df = pd.read_sql("""
            SELECT f.id_paciente, f.id_tipoformulario, r.puntuacion
            FROM resultados r
            JOIN formularios f ON f.id_formulario = r.id_formulario
            WHERE f.id_formulario IN (
                SELECT id_formulario
                FROM (
                    SELECT id_formulario,
                           ROW_NUMBER() OVER (
                               PARTITION BY id_paciente, id_tipoformulario
                               ORDER BY fecha_respuesta ASC
                           ) AS rn
                    FROM formularios
                    WHERE id_tipoformulario BETWEEN 1 AND 11
                ) sub
                WHERE rn = 1
            )
        """, engine)

        # 6. Pacientes que han contestado al menos un pretest
        pacientes_df = pd.read_sql("""
            SELECT DISTINCT pacientes.id_paciente, pacientes.nombre, pacientes.apellidos, pacientes.correo
            FROM pacientes
            JOIN formularios f ON pacientes.id_paciente = f.id_paciente
            WHERE f.id_tipoformulario BETWEEN 1 AND 11
        """, engine)

        export_data = []

        for _, paciente in pacientes_df.iterrows():
            fila = {
                "nombre": paciente["nombre"],
                "apellidos": paciente["apellidos"],
                "correo": paciente["correo"]
            }

            formularios_paciente = formularios_df[formularios_df.id_paciente == paciente.id_paciente]
            respuestas_paciente = respuestas_df[respuestas_df.id_paciente == paciente.id_paciente]
            resultados_paciente = resultados_df[resultados_df.id_paciente == paciente.id_paciente]

            for tipo_formulario, grupo_preguntas in preguntas_por_formulario:
                nombre_formulario = formulario_nombre.get(tipo_formulario, f"FORM{tipo_formulario}")

                preguntas_ids = grupo_preguntas.id_pregunta.tolist()

                for i, pregunta_id in enumerate(preguntas_ids):
                    col_name = f"p{i+1}_{nombre_formulario}"
                    respuesta = respuestas_paciente[respuestas_paciente.id_pregunta == pregunta_id]["respuesta"]
                    fila[col_name] = respuesta.values[0] if not respuesta.empty else ""

                col_puntaje = f"puntaje_{nombre_formulario}"
                puntaje = resultados_paciente[resultados_paciente.id_tipoformulario == tipo_formulario]["puntuacion"]
                fila[col_puntaje] = puntaje.values[0] if not puntaje.empty else ""

            export_data.append(fila)

        df_export = pd.DataFrame(export_data)
        df_export.to_excel(output_path, index=False)
        print(f"✅ Exportación completada en: {output_path}")

    except Exception as e:
        print("❌ Error durante la exportación:", str(e))

def exportar_posttest_completo(): 
    engine
    try:
        print("🟢 Iniciando exportación del Post-test...")

        output_dir = os.path.dirname(os.path.abspath(__file__))
        output_path = os.path.join(output_dir, "Posttest_Completo.xlsx")

        # IDs post-test
        post_ids = [1, 2, 5, 4, 9, 7, 8, 6, 10, 12, 13, 14, 15]

        # Obtener nombres de formularios
        formularios_df = pd.read_sql("SELECT id_tipoformulario, nombreformulario FROM tipos_formulario", engine)
        formulario_nombre = {
            row.id_tipoformulario: row.nombreformulario.split("(")[-1].replace(")", "").replace(" ", "").upper()
            for _, row in formularios_df.iterrows()
            if row.id_tipoformulario in post_ids
        }

        # Preguntas ordenadas
        preguntas_df = pd.read_sql(f"""
            SELECT id_pregunta, id_tipoformulario, texto
            FROM preguntas
            WHERE id_tipoformulario IN ({','.join(map(str, post_ids))})
            ORDER BY id_tipoformulario, id_pregunta
        """, engine)
        preguntas_por_formulario = preguntas_df.groupby("id_tipoformulario")

        # Formularios más recientes por tipo y paciente
        formularios_df = pd.read_sql(f"""
            WITH formularios_recientes AS (
                SELECT *,
                       ROW_NUMBER() OVER (
                           PARTITION BY id_paciente, id_tipoformulario
                           ORDER BY fecha_respuesta DESC, id_formulario DESC
                       ) AS rn
                FROM formularios
                WHERE id_tipoformulario IN ({','.join(map(str, post_ids))})
            )
            SELECT *
            FROM formularios_recientes
            WHERE rn = 1
        """, engine)

        # Respuestas asociadas a esos formularios
        respuestas_df = pd.read_sql(f"""
            SELECT r.id_paciente, r.id_pregunta, r.respuesta
            FROM respuestas r
            JOIN preguntas p ON r.id_pregunta = p.id_pregunta
            WHERE p.id_tipoformulario IN ({','.join(map(str, post_ids))})
        """, engine)

        # Eliminar duplicados, conservando solo la respuesta más reciente por paciente y pregunta
        respuestas_df = respuestas_df.drop_duplicates(subset=["id_paciente", "id_pregunta"], keep="last")

        # Resultados únicamente de los formularios más recientes
        resultados_df = pd.read_sql(f"""
            SELECT f.id_paciente, f.id_tipoformulario, r.puntuacion
            FROM resultados r
            JOIN formularios f ON f.id_formulario = r.id_formulario
            WHERE f.id_formulario IN (
                SELECT id_formulario
                FROM (
                    SELECT id_formulario,
                           ROW_NUMBER() OVER (
                               PARTITION BY id_paciente, id_tipoformulario
                               ORDER BY fecha_respuesta DESC, id_formulario DESC
                           ) AS rn
                    FROM formularios
                    WHERE id_tipoformulario IN ({','.join(map(str, post_ids))})
                ) sub
                WHERE rn = 1
            )
        """, engine)

        # IDs
        post_ids_doble = [1, 2, 5, 4, 9, 7, 8, 6, 10]     # Requieren al menos 2 respuestas
        post_ids_unico = [12, 13, 14, 15]                # Requieren al menos 1

        pacientes_df = pd.read_sql(f"""
            WITH conteo_formularios AS (
                SELECT id_paciente, id_tipoformulario, COUNT(*) AS total
                FROM formularios
                WHERE id_tipoformulario IN ({','.join(map(str, post_ids_doble + post_ids_unico))})
                GROUP BY id_paciente, id_tipoformulario
            ),
            pacientes_validos AS (
                SELECT id_paciente
                FROM conteo_formularios
                GROUP BY id_paciente
                HAVING 
                    COUNT(CASE WHEN id_tipoformulario IN ({','.join(map(str, post_ids_doble))}) AND total >= 2 THEN 1 END) = {len(post_ids_doble)}
                    AND
                    COUNT(CASE WHEN id_tipoformulario IN ({','.join(map(str, post_ids_unico))}) AND total >= 1 THEN 1 END) = {len(post_ids_unico)}
            )
            SELECT p.id_paciente, p.nombre, p.apellidos, p.correo
            FROM pacientes p
            JOIN pacientes_validos pv ON p.id_paciente = pv.id_paciente
        """, engine)        
        
        export_data = []

        for _, paciente in pacientes_df.iterrows():
            fila = {
                "nombre": paciente["nombre"],
                "apellidos": paciente["apellidos"],
                "correo": paciente["correo"]
            }

            formularios_paciente = formularios_df[formularios_df.id_paciente == paciente.id_paciente]
            respuestas_paciente = respuestas_df[respuestas_df.id_paciente == paciente.id_paciente]
            resultados_paciente = resultados_df[resultados_df.id_paciente == paciente.id_paciente]

            for tipo_formulario, grupo_preguntas in preguntas_por_formulario:
                nombre_formulario = formulario_nombre.get(tipo_formulario, f"FORM{tipo_formulario}")
                grupo_preguntas = grupo_preguntas.reset_index(drop=True)

                for i, pregunta in grupo_preguntas.iterrows():
                    col_name = f"p{i+1}_{nombre_formulario}"
                    respuesta = respuestas_paciente[respuestas_paciente.id_pregunta == pregunta.id_pregunta]["respuesta"]
                    fila[col_name] = respuesta.values[0] if not respuesta.empty else ""

                col_puntaje = f"puntaje_{nombre_formulario}"
                puntaje = resultados_paciente[resultados_paciente.id_tipoformulario == tipo_formulario]["puntuacion"]
                fila[col_puntaje] = puntaje.values[0] if not puntaje.empty else ""

            export_data.append(fila)

        df_export = pd.DataFrame(export_data)
        df_export.to_excel(output_path, index=False)
        print(f"✅ Post-test exportado correctamente en: {output_path}")

    except Exception as e:
        print("❌ Error durante la exportación del post-test:", str(e))

def exportar_pretest_individual(paciente_id: int):
    try:
        print(f"🟢 Exportando pretest del paciente ID {paciente_id}...")

        engine
        output_dir = os.path.dirname(os.path.abspath(__file__))

        # Obtener el nombre del paciente
        paciente_info = pd.read_sql(f"""
            SELECT id_paciente, nombre, apellidos, correo
            FROM pacientes
            WHERE id_paciente = {paciente_id}
        """, engine)

        if paciente_info.empty:
            print("❌ Paciente no encontrado.")
            return

        nombre_archivo = f"Pretest_{paciente_info.iloc[0]['nombre']}_{paciente_info.iloc[0]['apellidos']}.xlsx"
        output_path = os.path.join(output_dir, nombre_archivo)

        print("📂 Archivo de salida:", output_path)

        # Obtener los nombres de formularios
        formularios_df = pd.read_sql("SELECT id_tipoformulario, nombreformulario FROM tipos_formulario", engine)
        formulario_nombre = {
            row.id_tipoformulario: row.nombreformulario.split("(")[-1].replace(")", "").replace(" ", "").upper()
            for _, row in formularios_df.iterrows()
        }

        # preguntas (excluyendo entrevista chatbot)
        preguntas_df = pd.read_sql("""
            SELECT id_pregunta, id_tipoformulario, texto
            FROM preguntas
            WHERE id_tipoformulario != 11
            ORDER BY id_tipoformulario, id_pregunta
        """, engine)
        preguntas_por_formulario = preguntas_df.groupby("id_tipoformulario")

        # respuestas de ese paciente
        respuestas_df = pd.read_sql(f"""
            SELECT id_pregunta, respuesta
            FROM respuestas
            WHERE id_paciente = {paciente_id}
        """, engine)

        # resultados de ese paciente
        resultados_df = pd.read_sql(f"""
            SELECT f.id_tipoformulario, r.puntuacion
            FROM resultados r
            JOIN formularios f ON f.id_formulario = r.id_formulario
            WHERE f.id_paciente = {paciente_id} AND f.id_tipoformulario != 11
        """, engine)

        fila = {
            "nombre": paciente_info.iloc[0]['nombre'],
            "apellidos": paciente_info.iloc[0]['apellidos'],
            "correo": paciente_info.iloc[0]['correo']
        }

        for tipo_formulario, grupo_preguntas in preguntas_por_formulario:
            nombre_formulario = formulario_nombre.get(tipo_formulario, f"FORM{tipo_formulario}")
            grupo_preguntas = grupo_preguntas.reset_index(drop=True)

            for i, pregunta in grupo_preguntas.iterrows():
                num_pregunta = i + 1
                col_name = f"p{num_pregunta}_{nombre_formulario}"
                respuesta = respuestas_df[respuestas_df.id_pregunta == pregunta.id_pregunta]["respuesta"]
                fila[col_name] = respuesta.values[0] if not respuesta.empty else ""

            col_puntaje = f"puntaje_{nombre_formulario}"
            puntaje = resultados_df[resultados_df.id_tipoformulario == tipo_formulario]["puntuacion"]
            fila[col_puntaje] = puntaje.values[0] if not puntaje.empty else ""

        # Exportar
        df_export = pd.DataFrame([fila])
        df_export.to_excel(output_path, index=False)
        print(f"✅ Pretest individual exportado correctamente: {output_path}")
        return nombre_archivo

    except Exception as e:
        print("❌ Error durante la exportación individual:", str(e))

def exportar_posttest_individual(paciente_id: int):
    try:
        print(f"🟢 Exportando post-test del paciente ID {paciente_id}...")

        output_dir = os.path.dirname(os.path.abspath(__file__))

        post_ids = [1, 2, 5, 4, 9, 7, 8, 6, 10, 12, 13, 14, 15]
        post_ids_doble = [1, 2, 5, 4, 9, 7, 8, 6, 10]
        post_ids_unico = [12, 13, 14, 15]

        # Validar si el paciente cumple con los criterios
        validacion_df = pd.read_sql(f"""
            WITH conteo_formularios AS (
                SELECT id_paciente, id_tipoformulario, COUNT(*) AS total
                FROM formularios
                WHERE id_paciente = {paciente_id}
                AND id_tipoformulario IN ({','.join(map(str, post_ids))})
                GROUP BY id_paciente, id_tipoformulario
            )
            SELECT
                SUM(CASE WHEN id_tipoformulario IN ({','.join(map(str, post_ids_doble))}) AND total >= 2 THEN 1 ELSE 0 END) AS cumple_doble,
                SUM(CASE WHEN id_tipoformulario IN ({','.join(map(str, post_ids_unico))}) AND total >= 1 THEN 1 ELSE 0 END) AS cumple_unico
            FROM conteo_formularios
        """, engine)

        if validacion_df.empty or \
            validacion_df.iloc[0]['cumple_doble'] < len(post_ids_doble) or \
            validacion_df.iloc[0]['cumple_unico'] < len(post_ids_unico):
            print("⚠️ Este paciente no ha completado los formularios requeridos del post-test. No se exportará.")
            return

        # Obtener nombres de formularios
        formularios_df = pd.read_sql("SELECT id_tipoformulario, nombreformulario FROM tipos_formulario", engine)
        formulario_nombre = {
            row.id_tipoformulario: row.nombreformulario.split("(")[-1].replace(")", "").replace(" ", "").upper()
            for _, row in formularios_df.iterrows()
            if row.id_tipoformulario in post_ids
        }

        # Preguntas ordenadas
        preguntas_df = pd.read_sql(f"""
            SELECT id_pregunta, id_tipoformulario, texto
            FROM preguntas
            WHERE id_tipoformulario IN ({','.join(map(str, post_ids))})
            ORDER BY id_tipoformulario, id_pregunta
        """, engine)
        preguntas_por_formulario = preguntas_df.groupby("id_tipoformulario")

        # Formularios más recientes por tipo
        formularios_df = pd.read_sql(f"""
            WITH formularios_recientes AS (
                SELECT *,
                        ROW_NUMBER() OVER (
                            PARTITION BY id_tipoformulario
                            ORDER BY fecha_respuesta DESC, id_formulario DESC
                        ) AS rn
                FROM formularios
                WHERE id_tipoformulario IN ({','.join(map(str, post_ids))})
                AND id_paciente = {paciente_id}
            )
            SELECT *
            FROM formularios_recientes
            WHERE rn = 1
        """, engine)

        # Respuestas del paciente
        respuestas_df = pd.read_sql(f"""
            SELECT r.id_paciente, r.id_pregunta, r.respuesta
            FROM respuestas r
            JOIN preguntas p ON r.id_pregunta = p.id_pregunta
            WHERE p.id_tipoformulario IN ({','.join(map(str, post_ids))})
            AND r.id_paciente = {paciente_id}
        """, engine)
        respuestas_df = respuestas_df.drop_duplicates(subset=["id_pregunta"], keep="last")

        # Resultados del paciente
        resultados_df = pd.read_sql(f"""
            SELECT f.id_tipoformulario, r.puntuacion
            FROM resultados r
            JOIN formularios f ON f.id_formulario = r.id_formulario
            WHERE f.id_paciente = {paciente_id}
            AND f.id_formulario IN (
                SELECT id_formulario
                FROM (
                    SELECT id_formulario,
                            ROW_NUMBER() OVER (
                                PARTITION BY id_tipoformulario
                                ORDER BY fecha_respuesta DESC, id_formulario DESC
                            ) AS rn
                    FROM formularios
                    WHERE id_tipoformulario IN ({','.join(map(str, post_ids))})
                    AND id_paciente = {paciente_id}
                ) sub
                WHERE rn = 1
            )
        """, engine)

        # Datos del paciente
        paciente_info = pd.read_sql(f"""
            SELECT id_paciente, nombre, apellidos, correo
            FROM pacientes
            WHERE id_paciente = {paciente_id}
        """, engine)

        if paciente_info.empty:
            print("❌ Paciente no encontrado.")
            return

        fila = {
            "nombre": paciente_info.iloc[0]['nombre'],
            "apellidos": paciente_info.iloc[0]['apellidos'],
            "correo": paciente_info.iloc[0]['correo']
        }

        for tipo_formulario, grupo_preguntas in preguntas_por_formulario:
            nombre_formulario = formulario_nombre.get(tipo_formulario, f"FORM{tipo_formulario}")
            grupo_preguntas = grupo_preguntas.reset_index(drop=True)

            for i, pregunta in grupo_preguntas.iterrows():
                col_name = f"p{i+1}_{nombre_formulario}"
                respuesta = respuestas_df[respuestas_df.id_pregunta == pregunta.id_pregunta]["respuesta"]
                fila[col_name] = respuesta.values[0] if not respuesta.empty else ""

            col_puntaje = f"puntaje_{nombre_formulario}"
            puntaje = resultados_df[resultados_df.id_tipoformulario == tipo_formulario]["puntuacion"]
            fila[col_puntaje] = puntaje.values[0] if not puntaje.empty else ""

        df_export = pd.DataFrame([fila])
        nombre_archivo = f"Posttest_{paciente_info.iloc[0]['nombre']}_{paciente_info.iloc[0]['apellidos']}.xlsx"
        output_path = os.path.join(output_dir, nombre_archivo)
        df_export.to_excel(output_path, index=False)

        print(f"✅ Post-test individual exportado correctamente: {output_path}")
        return nombre_archivo
    except Exception as e:
        print("❌ Error durante la exportación individual del post-test:", str(e))

def exportar_base_completa_sirve():
    try:
        print("🟢 Iniciando exportación...")

        engine
        output_dir = os.path.dirname(os.path.abspath(__file__))
        output_path = os.path.join(output_dir, "Base_de_datos_Serenamente.xlsx")

        # Nombres de formularios
        formularios_df = pd.read_sql("SELECT id_tipoformulario, nombreformulario FROM tipos_formulario", engine)
        formulario_nombre = {
            row.id_tipoformulario: row.nombreformulario.split("(")[-1].replace(")", "").replace(" ", "").upper()
            for _, row in formularios_df.iterrows()
        }

        # preguntas
        preguntas_df = pd.read_sql("""
            SELECT id_pregunta, id_tipoformulario, texto
            FROM preguntas
            ORDER BY id_tipoformulario, id_pregunta
        """, engine)

        # pacientes y respuestas
        pacientes_df = pd.read_sql("SELECT * FROM pacientes", engine)
        respuestas_df = pd.read_sql("SELECT id_paciente, id_pregunta, respuesta FROM respuestas", engine)

        # Puntajes por formulario
        resultados_df = pd.read_sql("""
            SELECT f.id_paciente, f.id_tipoformulario, r.puntuacion
            FROM resultados r
            JOIN formularios f ON f.id_formulario = r.id_formulario
        """, engine)

        preguntas_por_formulario = preguntas_df.groupby("id_tipoformulario")

        # Consultas adicionales con manejo de errores
        try:
            tratamientos_df = pd.read_sql("""
                SELECT pt.id_paciente, t.nivel AS NivelTratamiento
                FROM paciente_tratamiento pt
                JOIN tratamientos t ON pt.id_tratamiento = t.id_tratamiento
            """, engine)
        except:
            tratamientos_df = pd.DataFrame()

        try:
            habilidades_df = pd.read_sql("""
                SELECT id_paciente, h.nombre AS Habilidad
                FROM paciente_habilidad ph
                JOIN habilidades h ON ph.id_habilidad = h.id_habilidad
                WHERE ph.completada = TRUE
            """, engine)
        except:
            habilidades_df = pd.DataFrame()

        try:
            actividades_df = pd.read_sql("""
                SELECT id_paciente, a.nombre AS Actividad
                FROM paciente_actividad pa
                JOIN actividades a ON pa.id_actividad = a.id_actividad
                WHERE pa.completada = TRUE
            """, engine)
        except:
            actividades_df = pd.DataFrame()

        try:
            respuestas_actividad_df = pd.read_sql("""
                SELECT ra.id_paciente, a.nombre AS Actividad, ra.respuesta
                FROM respuestas_actividad ra
                JOIN actividades a ON a.id_actividad = ra.id_actividad
            """, engine)
        except:
            respuestas_actividad_df = pd.DataFrame()

        export_data = []

        for _, paciente in pacientes_df.iterrows():
            fila = paciente.to_dict()

            respuestas_paciente = respuestas_df[respuestas_df.id_paciente == paciente.id_paciente]
            resultados_paciente = resultados_df[resultados_df.id_paciente == paciente.id_paciente]

            # respuestas por formulario
            for tipo_formulario, grupo_preguntas in preguntas_por_formulario:
                nombre_formulario = formulario_nombre.get(tipo_formulario, f"FORM{tipo_formulario}")
                grupo_preguntas = grupo_preguntas.reset_index(drop=True)

                for i, pregunta in grupo_preguntas.iterrows():
                    num_pregunta = i + 1
                    col_name = f"p{num_pregunta}_{nombre_formulario}"
                    respuesta = respuestas_paciente[respuestas_paciente.id_pregunta == pregunta.id_pregunta]["respuesta"]
                    fila[col_name] = respuesta.values[0] if not respuesta.empty else ""

                if tipo_formulario != 11:
                    col_puntaje = f"puntaje_{nombre_formulario}"
                    puntaje = resultados_paciente[resultados_paciente.id_tipoformulario == tipo_formulario]["puntuacion"]
                    fila[col_puntaje] = puntaje.values[0] if not puntaje.empty else ""

            # Tratamiento
            if not tratamientos_df.empty:
                tratamiento = tratamientos_df[tratamientos_df.id_paciente == paciente.id_paciente]["NivelTratamiento"]
                fila["Tratamiento"] = tratamiento.values[0] if not tratamiento.empty else ""

            # habilidades completadas
            if not habilidades_df.empty:
                habilidades = habilidades_df[habilidades_df.id_paciente == paciente.id_paciente]["Habilidad"].tolist()
                fila["Habilidades_Completadas"] = ", ".join(habilidades)

            # actividades completadas
            if not actividades_df.empty:
                actividades = actividades_df[actividades_df.id_paciente == paciente.id_paciente]["Actividad"].tolist()
                fila["Actividades_Completadas"] = ", ".join(actividades)

            # respuestas a actividades (todas)
            if not respuestas_actividad_df.empty:
                respuestas_actividades_paciente = respuestas_actividad_df[respuestas_actividad_df.id_paciente == paciente.id_paciente]
                contador_columnas = {}

                for _, row in respuestas_actividades_paciente.iterrows():
                    base_name = f"respuesta_{row.Actividad.replace(' ', '_')}"
                    if base_name not in contador_columnas:
                        contador_columnas[base_name] = 1
                        col_actividad = base_name
                    else:
                        contador_columnas[base_name] += 1
                        col_actividad = f"{base_name}_{contador_columnas[base_name]}"

                    fila[col_actividad] = row.respuesta

            export_data.append(fila)

        df_export = pd.DataFrame(export_data)
        df_export.to_excel(output_path, index=False)
        print(f"✅ Exportación completada en: {output_path}")

    except Exception as e:
        print("❌ Error durante la exportación:", str(e))

def exportar_base_completa():
    try:
        print("🟢 Iniciando exportación completa...")

        output_dir = os.path.dirname(os.path.abspath(__file__))
        output_path = os.path.join(output_dir, "Base_de_datos_Serenamente.xlsx")

        # IDs post-test
        post_ids = [1, 2, 5, 4, 9, 7, 8, 6, 10, 12, 13, 14, 15]
        post_ids_doble = [1, 2, 5, 4, 9, 7, 8, 6, 10]
        post_ids_unico = [12, 13, 14, 15]

        # Formularios y nombres
        formularios_df = pd.read_sql("SELECT id_tipoformulario, nombreformulario FROM tipos_formulario", engine)
        formulario_nombre = {
            row.id_tipoformulario: row.nombreformulario.split("(")[-1].replace(")", "").replace(" ", "").upper()
            for _, row in formularios_df.iterrows()
        }

        # Preguntas y respuestas
        preguntas_df = pd.read_sql("SELECT id_pregunta, id_tipoformulario, texto FROM preguntas ORDER BY id_tipoformulario, id_pregunta", engine)
        preguntas_por_formulario = preguntas_df.groupby("id_tipoformulario")

        respuestas_df = pd.read_sql("SELECT id_paciente, id_pregunta, respuesta FROM respuestas", engine)
        respuestas_df = respuestas_df.drop_duplicates(subset=["id_paciente", "id_pregunta"], keep="last")

        resultados_df = pd.read_sql("""
            SELECT f.id_paciente, f.id_formulario, f.id_tipoformulario, r.puntuacion
            FROM resultados r
            JOIN formularios f ON f.id_formulario = r.id_formulario
        """, engine)

        pacientes_df = pd.read_sql("SELECT * FROM pacientes", engine)

        # Tratamientos, habilidades, actividades
        try:
            tratamientos_df = pd.read_sql("""
                SELECT pt.id_paciente, t.nivel AS NivelTratamiento
                FROM paciente_tratamiento pt
                JOIN tratamientos t ON pt.id_tratamiento = t.id_tratamiento
            """, engine)
        except:
            tratamientos_df = pd.DataFrame()

        try:
            habilidades_df = pd.read_sql("""
                SELECT id_paciente, h.nombre AS Habilidad
                FROM paciente_habilidad ph
                JOIN habilidades h ON ph.id_habilidad = h.id_habilidad
                WHERE ph.completada = TRUE
            """, engine)
        except:
            habilidades_df = pd.DataFrame()

        try:
            actividades_df = pd.read_sql("""
                SELECT id_paciente, a.nombre AS Actividad
                FROM paciente_actividad pa
                JOIN actividades a ON pa.id_actividad = a.id_actividad
                WHERE pa.completada = TRUE
            """, engine)
        except:
            actividades_df = pd.DataFrame()

        try:
            respuestas_actividad_df = pd.read_sql("""
                SELECT ra.id_paciente, a.nombre AS Actividad, ra.respuesta
                FROM respuestas_actividad ra
                JOIN actividades a ON a.id_actividad = ra.id_actividad
            """, engine)
        except:
            respuestas_actividad_df = pd.DataFrame()

        # Validación post-test por paciente
        conteo_formularios = pd.read_sql(f"""
            SELECT id_paciente, id_tipoformulario, COUNT(*) AS total
            FROM formularios
            WHERE id_tipoformulario IN ({','.join(map(str, post_ids))})
            GROUP BY id_paciente, id_tipoformulario
        """, engine)

        export_data = []

        for _, paciente in pacientes_df.iterrows():
            fila = paciente.to_dict()
            id_paciente = paciente["id_paciente"]

            respuestas_paciente = respuestas_df[respuestas_df.id_paciente == id_paciente]
            resultados_paciente = resultados_df[resultados_df.id_paciente == id_paciente]

            # 1. Pretest (formulario 1–11)
            for tipo_formulario, grupo_preguntas in preguntas_por_formulario:
                if tipo_formulario > 11: continue
                nombre_formulario = formulario_nombre.get(tipo_formulario, f"FORM{tipo_formulario}")
                grupo_preguntas = grupo_preguntas.reset_index(drop=True)

                for i, pregunta in grupo_preguntas.iterrows():
                    col_name = f"p{i+1}_{nombre_formulario}"
                    respuesta = respuestas_paciente[respuestas_paciente.id_pregunta == pregunta.id_pregunta]["respuesta"]
                    fila[col_name] = respuesta.values[0] if not respuesta.empty else ""

                col_puntaje = f"puntaje_{nombre_formulario}"
                puntaje = resultados_paciente[resultados_paciente.id_tipoformulario == tipo_formulario]["puntuacion"]
                fila[col_puntaje] = puntaje.values[0] if not puntaje.empty else ""

            # 2. Tratamiento
            if not tratamientos_df.empty:
                t = tratamientos_df[tratamientos_df.id_paciente == id_paciente]["NivelTratamiento"]
                fila["Tratamiento"] = t.values[0] if not t.empty else ""

            # 3. Habilidades completadas
            if not habilidades_df.empty:
                habilidades = habilidades_df[habilidades_df.id_paciente == id_paciente]["Habilidad"].tolist()
                fila["Habilidades_Completadas"] = ", ".join(habilidades)

            # 4. Actividades completadas
            if not actividades_df.empty:
                acts = actividades_df[actividades_df.id_paciente == id_paciente]["Actividad"].tolist()
                fila["Actividades_Completadas"] = ", ".join(acts)

            # 5. Respuestas a actividades
            if not respuestas_actividad_df.empty:
                respuestas_acts = respuestas_actividad_df[respuestas_actividad_df.id_paciente == id_paciente]
                contador_columnas = {}
                for _, row in respuestas_acts.iterrows():
                    base = f"respuesta_{row.Actividad.replace(' ', '_')}"
                    contador_columnas[base] = contador_columnas.get(base, 0) + 1
                    col_name = base if contador_columnas[base] == 1 else f"{base}_{contador_columnas[base]}"
                    fila[col_name] = row.respuesta

            # 6. Validar si tiene post-test completo
            conteo = conteo_formularios[conteo_formularios.id_paciente == id_paciente]
            cumple_doble = conteo[(conteo.id_tipoformulario.isin(post_ids_doble)) & (conteo.total >= 2)].shape[0]
            cumple_unico = conteo[(conteo.id_tipoformulario.isin(post_ids_unico)) & (conteo.total >= 1)].shape[0]

            if cumple_doble == len(post_ids_doble) and cumple_unico == len(post_ids_unico):
                for tipo_formulario in post_ids:
                    nombre_formulario = formulario_nombre.get(tipo_formulario, f"FORM{tipo_formulario}_post")
                    grupo_preguntas = preguntas_por_formulario.get_group(tipo_formulario).reset_index(drop=True)
                    for i, pregunta in grupo_preguntas.iterrows():
                        col_name = f"p{i+1}_{nombre_formulario}_post"
                        respuesta = respuestas_paciente[respuestas_paciente.id_pregunta == pregunta.id_pregunta]["respuesta"]
                        fila[col_name] = respuesta.values[0] if not respuesta.empty else ""

                    col_puntaje = f"puntaje_{nombre_formulario}"
                    puntaje = resultados_paciente[resultados_paciente.id_tipoformulario == tipo_formulario]["puntuacion"]
                    fila[col_puntaje] = puntaje.values[0] if not puntaje.empty else ""

            export_data.append(fila)

        df_export = pd.DataFrame(export_data)
        df_export.to_excel(output_path, index=False)
        print(f"✅ Base de datos exportada correctamente: {output_path}")

    except Exception as e:
        print("❌ Error durante la exportación:", str(e))


if __name__ == "__main__":
    # exportar_pretest_completo(engine)
    # exportar_pretest_individual(paciente_id=1)
    # exportar_posttest_completo(engine)
    # exportar_posttest_individual(paciente_id=2)
    exportar_base_completa()
    