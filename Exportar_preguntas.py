import pandas as pd
from database import engine
import os

def exportar_pretest_completo():
    try:
        print("🟢 Iniciando exportación...")

        engine
        output_dir = os.path.dirname(os.path.abspath(__file__))
        output_path = os.path.join(output_dir, "Pretest_Completo.xlsx")

        # Obtener nombres de formularios
        formularios_df = pd.read_sql("SELECT id_tipoformulario, nombreformulario FROM tipos_formulario", engine)
        formulario_nombre = {
            row.id_tipoformulario: row.nombreformulario.split("(")[-1].replace(")", "").replace(" ", "").upper()
            for _, row in formularios_df.iterrows()
        }

        # preguntas ordenadas
        preguntas_df = pd.read_sql("""
            SELECT id_pregunta, id_tipoformulario, texto
            FROM preguntas
            ORDER BY id_tipoformulario, id_pregunta
        """, engine)

        pacientes_df = pd.read_sql("""
            SELECT DISTINCT pacientes.id_paciente, pacientes.nombre, pacientes.apellidos, pacientes.correo
            FROM pacientes
            JOIN respuestas ON pacientes.id_paciente = respuestas.id_paciente
            ORDER BY pacientes.id_paciente
        """, engine)

        respuestas_df = pd.read_sql("""
            SELECT id_paciente, id_pregunta, respuesta
            FROM respuestas
        """, engine)

        resultados_df = pd.read_sql("""
            SELECT f.id_paciente, f.id_tipoformulario, r.puntuacion
            FROM resultados r
            JOIN formularios f ON f.id_formulario = r.id_formulario
        """, engine)

        preguntas_df_filtradas = preguntas_df[preguntas_df.id_tipoformulario != 11]
        preguntas_por_formulario = preguntas_df_filtradas.groupby("id_tipoformulario")

        export_data = []

        for _, paciente in pacientes_df.iterrows():
            fila = {
                "nombre": paciente["nombre"],
                "apellidos": paciente["apellidos"],
                "correo": paciente["correo"]
            }

            respuestas_paciente = respuestas_df[respuestas_df.id_paciente == paciente.id_paciente]
            
            resultados_paciente = resultados_df[
                (resultados_df.id_paciente == paciente.id_paciente) &
                (resultados_df.id_tipoformulario != 11)
            ]

            for tipo_formulario, grupo_preguntas in preguntas_por_formulario:
                nombre_formulario = formulario_nombre.get(tipo_formulario, f"FORM{tipo_formulario}")

                grupo_preguntas = grupo_preguntas.reset_index(drop=True)
                for i, pregunta in grupo_preguntas.iterrows():
                    num_pregunta = i + 1
                    col_name = f"p{num_pregunta}_{nombre_formulario}"
                    respuesta = respuestas_paciente[respuestas_paciente.id_pregunta == pregunta.id_pregunta]["respuesta"]
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

def exportar_base_completa():
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

if __name__ == "__main__":
    #exportar_pretest_completo()
    #exportar_pretest_individual(paciente_id=1)
    exportar_base_completa()