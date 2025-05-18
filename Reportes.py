import pandas as pd
import matplotlib.pyplot as plt
import matplotlib
matplotlib.use('Agg')
from fpdf import FPDF
from sqlalchemy import create_engine
import os
from io import BytesIO


class PDF(FPDF):
    def header(self):
        self.set_font("Arial", "B", 14)
        self.cell(0, 10, "Reporte de Progreso SerenaMente", ln=True, align="C")

    def section_title(self, title):
        self.set_font("Arial", "B", 12)
        self.set_text_color(33, 37, 41)
        self.ln(10)
        self.cell(0, 10, f"- {title}", ln=True)

    def section_body(self, text):
        self.set_font("Arial", "", 11)
        self.multi_cell(0, 10, text)

def generar_pdf_reporte(paciente_id):
    engine = create_engine('mysql+pymysql://root:Gomuroot2527@localhost/SerenaMenteDB')
    pdf = PDF()
    pdf.add_page()

    # 1. Datos del paciente
    pdf.section_title("Datos del paciente")
    paciente = pd.read_sql(f"""
        SELECT Nombre, Apellidos, Correo, Celular, Sexo, FechaNacimiento
        FROM Pacientes WHERE ID_Paciente = {paciente_id}
    """, engine)
    paciente_info = paciente.iloc[0]
    info_text = "\n".join([f"{col}: {paciente_info[col]}" for col in paciente.columns])
    pdf.section_body(info_text)

    # 2. Puntajes de test
    pdf.section_title("Puntajes de test")
    resultados = pd.read_sql(f"""
        SELECT tf.NombreFormulario, r.Puntuacion
        FROM Resultados r
        JOIN Formularios f ON f.ID_Formulario = r.ID_Formulario
        JOIN TiposFormulario tf ON f.ID_TipoFormulario = tf.ID_TipoFormulario
        WHERE f.ID_Paciente = {paciente_id} AND f.ID_TipoFormulario != 11
    """, engine)

    for _, row in resultados.iterrows():
        pdf.section_body(f"{row.NombreFormulario}: {row.Puntuacion}")

    # 3. Gráfica de progreso (basada solo en su tratamiento)
    # 1. Obtener ID del tratamiento asignado al paciente
    tratamiento_id_df = pd.read_sql("""
        SELECT ID_Tratamiento FROM Paciente_Tratamiento
        WHERE ID_Paciente = %s
    """, engine, params=(paciente_id,))

    if tratamiento_id_df.empty:
        pdf.section_title("Progreso de habilidades")
        pdf.section_body("El paciente no tiene un tratamiento asignado.")
    else:
        tratamiento_id = tratamiento_id_df.iloc[0]["ID_Tratamiento"]

        # 2. Obtener actividades esperadas y completadas por habilidad para ese tratamiento
        query = """
            SELECT h.Nombre AS Habilidad,
                tha.ID_Actividad,
                pa.Completada
            FROM Tratamiento_Habilidad_Actividad tha
            JOIN Actividades a ON tha.ID_Actividad = a.ID_Actividad
            JOIN Habilidades h ON tha.ID_Habilidad = h.ID_Habilidad
            LEFT JOIN Paciente_Actividad pa ON pa.ID_Actividad = tha.ID_Actividad AND pa.ID_Paciente = %s
            WHERE tha.ID_Tratamiento = %s AND h.Nombre NOT LIKE '%%Final del Tratamiento%%'
        """
        progreso = pd.read_sql(query, engine, params=(paciente_id, tratamiento_id))

        # 3. Calcular progreso real por habilidad
        progreso["Completada"] = progreso["Completada"].fillna(False).infer_objects(copy=False)

        conteo = progreso.groupby("Habilidad").agg(
            total_actividades=("ID_Actividad", "count"),
            completadas=("Completada", lambda x: x.astype(bool).sum())
        ).reset_index()

        conteo["Porcentaje"] = round(conteo["completadas"] / conteo["total_actividades"] * 100, 0)

        # Orden personalizado de las habilidades
        orden_habilidades = [
            "Comenzar a trabajar en mi",
            "Ser y estar",
            "De la Distracción a la Conciencia",
            "El poder de estar presente",
            "Re-Conocer el Estrés",
            "Comunicación que Conecta",
            "Cuidarte es volver a ti"
        ]

        # Reordenar el DataFrame según el orden definido
        conteo["Habilidad"] = pd.Categorical(conteo["Habilidad"], categories=orden_habilidades, ordered=True)
        conteo = conteo.sort_values("Habilidad")

        # Paleta de colores pastel
        colores_pastel = [
            "#A8DADC",  # menta
            "#FDCBCA",  # rosa claro
            "#FFE8A1",  # amarillo pálido
            "#CDB4DB",  # lila
            "#BDE0FE",  # azul cielo
            "#D0F4DE",  # verde agua
            "#FFDAC1"   # durazno
        ]

        # Gráfico de barras horizontales
        fig, ax = plt.subplots(figsize=(10, 6))
        habilidades = conteo["Habilidad"].tolist()[::-1]
        porcentajes = conteo["Porcentaje"].tolist()[::-1]
        colores_ordenados = colores_pastel[:len(habilidades)][::-1]

        bars = ax.barh(habilidades, porcentajes, color=colores_ordenados)

        bars = ax.barh(habilidades, porcentajes, color=colores_pastel[:len(habilidades)])
        ax.set_xlabel("Porcentaje completado (%)")
        ax.set_title("Progreso de habilidades por paciente")
        ax.set_xlim(0, 100)

        for bar in bars:
            width = bar.get_width()
            ax.text(width + 2, bar.get_y() + bar.get_height() / 2,
                    f"{width:.0f}%", va='center')

        plt.tight_layout()
        img_path = "grafica_progreso.png"
        plt.savefig(img_path)
        plt.close()

        pdf.image(img_path, w=180)

    # 4. Logs del sistema experto
    pdf.section_title("Diagnóstico sistema experto")
    logs = pd.read_sql(f"""
        SELECT Log_sistema, FechaEvaluacion
        FROM AsignacionesSistemaExperto
        WHERE ID_Paciente = {paciente_id}
        ORDER BY FechaEvaluacion DESC
        LIMIT 1
    """, engine)

    if not logs.empty:
        log_text = f"{logs.iloc[0]['FechaEvaluacion']}:\n{logs.iloc[0]['Log_sistema']}"
        pdf.section_body(log_text)
    else:
        pdf.section_body("Sin registros de asignación del sistema experto.")

    # Guardar PDF
    output_path = f"Reporte_Paciente_{paciente_id}.pdf"
    pdf.output(output_path)
    print(f"✅ PDF generado: {output_path}")

if __name__ == "__main__":
    generar_pdf_reporte(paciente_id=1)
