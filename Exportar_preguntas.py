import pandas as pd
from sqlalchemy import create_engine
import os

def exportar_pretest_completo():
    try:
        print("🟢 Iniciando exportación...")

        engine = create_engine('mysql+pymysql://root:Gomuroot2527@localhost/SerenaMenteDB')
        output_dir = os.path.dirname(os.path.abspath(__file__))
        output_path = os.path.join(output_dir, "Pretest_Completo.xlsx")

        # Obtener nombres de formularios
        formularios_df = pd.read_sql("SELECT ID_TipoFormulario, NombreFormulario FROM TiposFormulario", engine)
        formulario_nombre = {
            row.ID_TipoFormulario: row.NombreFormulario.split("(")[-1].replace(")", "").replace(" ", "").upper()
            for _, row in formularios_df.iterrows()
        }

        # Preguntas ordenadas
        preguntas_df = pd.read_sql("""
            SELECT ID_Pregunta, ID_TipoFormulario, Texto
            FROM Preguntas
            ORDER BY ID_TipoFormulario, ID_Pregunta
        """, engine)

        pacientes_df = pd.read_sql("""
            SELECT DISTINCT Pacientes.ID_Paciente, Pacientes.Nombre, Pacientes.Apellidos, Pacientes.Correo
            FROM Pacientes
            JOIN Respuestas ON Pacientes.ID_Paciente = Respuestas.ID_Paciente
            ORDER BY Pacientes.ID_Paciente
        """, engine)

        respuestas_df = pd.read_sql("""
            SELECT ID_Paciente, ID_Pregunta, Respuesta
            FROM Respuestas
        """, engine)

        resultados_df = pd.read_sql("""
            SELECT f.ID_Paciente, f.ID_TipoFormulario, r.Puntuacion
            FROM Resultados r
            JOIN Formularios f ON f.ID_Formulario = r.ID_Formulario
        """, engine)

        preguntas_df_filtradas = preguntas_df[preguntas_df.ID_TipoFormulario != 11]
        preguntas_por_formulario = preguntas_df_filtradas.groupby("ID_TipoFormulario")

        export_data = []

        for _, paciente in pacientes_df.iterrows():
            fila = {
                "nombre": paciente["Nombre"],
                "apellidos": paciente["Apellidos"],
                "correo": paciente["Correo"]
            }

            respuestas_paciente = respuestas_df[respuestas_df.ID_Paciente == paciente.ID_Paciente]
            
            resultados_paciente = resultados_df[
                (resultados_df.ID_Paciente == paciente.ID_Paciente) &
                (resultados_df.ID_TipoFormulario != 11)
            ]

            for tipo_formulario, grupo_preguntas in preguntas_por_formulario:
                nombre_formulario = formulario_nombre.get(tipo_formulario, f"FORM{tipo_formulario}")

                grupo_preguntas = grupo_preguntas.reset_index(drop=True)
                for i, pregunta in grupo_preguntas.iterrows():
                    num_pregunta = i + 1
                    col_name = f"p{num_pregunta}_{nombre_formulario}"
                    respuesta = respuestas_paciente[respuestas_paciente.ID_Pregunta == pregunta.ID_Pregunta]["Respuesta"]
                    fila[col_name] = respuesta.values[0] if not respuesta.empty else ""

                col_puntaje = f"puntaje_{nombre_formulario}"
                puntaje = resultados_paciente[resultados_paciente.ID_TipoFormulario == tipo_formulario]["Puntuacion"]
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

        engine = create_engine('mysql+pymysql://root:Gomuroot2527@localhost/SerenaMenteDB')
        output_dir = os.path.dirname(os.path.abspath(__file__))

        # Obtener el nombre del paciente
        paciente_info = pd.read_sql(f"""
            SELECT ID_Paciente, Nombre, Apellidos, Correo
            FROM Pacientes
            WHERE ID_Paciente = {paciente_id}
        """, engine)

        if paciente_info.empty:
            print("❌ Paciente no encontrado.")
            return

        nombre_archivo = f"Pretest_{paciente_info.iloc[0]['Nombre']}_{paciente_info.iloc[0]['Apellidos']}.xlsx"
        output_path = os.path.join(output_dir, nombre_archivo)

        print("📂 Archivo de salida:", output_path)

        # Obtener los nombres de formularios
        formularios_df = pd.read_sql("SELECT ID_TipoFormulario, NombreFormulario FROM TiposFormulario", engine)
        formulario_nombre = {
            row.ID_TipoFormulario: row.NombreFormulario.split("(")[-1].replace(")", "").replace(" ", "").upper()
            for _, row in formularios_df.iterrows()
        }

        # Preguntas (excluyendo entrevista chatbot)
        preguntas_df = pd.read_sql("""
            SELECT ID_Pregunta, ID_TipoFormulario, Texto
            FROM Preguntas
            WHERE ID_TipoFormulario != 11
            ORDER BY ID_TipoFormulario, ID_Pregunta
        """, engine)
        preguntas_por_formulario = preguntas_df.groupby("ID_TipoFormulario")

        # Respuestas de ese paciente
        respuestas_df = pd.read_sql(f"""
            SELECT ID_Pregunta, Respuesta
            FROM Respuestas
            WHERE ID_Paciente = {paciente_id}
        """, engine)

        # Resultados de ese paciente
        resultados_df = pd.read_sql(f"""
            SELECT f.ID_TipoFormulario, r.Puntuacion
            FROM Resultados r
            JOIN Formularios f ON f.ID_Formulario = r.ID_Formulario
            WHERE f.ID_Paciente = {paciente_id} AND f.ID_TipoFormulario != 11
        """, engine)

        fila = {
            "nombre": paciente_info.iloc[0]['Nombre'],
            "apellidos": paciente_info.iloc[0]['Apellidos'],
            "correo": paciente_info.iloc[0]['Correo']
        }

        for tipo_formulario, grupo_preguntas in preguntas_por_formulario:
            nombre_formulario = formulario_nombre.get(tipo_formulario, f"FORM{tipo_formulario}")
            grupo_preguntas = grupo_preguntas.reset_index(drop=True)

            for i, pregunta in grupo_preguntas.iterrows():
                num_pregunta = i + 1
                col_name = f"p{num_pregunta}_{nombre_formulario}"
                respuesta = respuestas_df[respuestas_df.ID_Pregunta == pregunta.ID_Pregunta]["Respuesta"]
                fila[col_name] = respuesta.values[0] if not respuesta.empty else ""

            col_puntaje = f"puntaje_{nombre_formulario}"
            puntaje = resultados_df[resultados_df.ID_TipoFormulario == tipo_formulario]["Puntuacion"]
            fila[col_puntaje] = puntaje.values[0] if not puntaje.empty else ""

        # Exportar
        df_export = pd.DataFrame([fila])
        df_export.to_excel(output_path, index=False)
        print(f"✅ Pretest individual exportado correctamente: {output_path}")

    except Exception as e:
        print("❌ Error durante la exportación individual:", str(e))

if __name__ == "__main__":
    exportar_pretest_completo()
    exportar_pretest_individual(paciente_id=1)