import pandas as pd
import matplotlib.pyplot as plt
import matplotlib
matplotlib.use('Agg')
from fpdf import FPDF
from database import engine
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
    engine
    pdf = PDF()
    pdf.add_page()

    # 1. Datos del paciente
    pdf.section_title("Datos del paciente")
    paciente = pd.read_sql(f"""
        SELECT nombre, apellidos, correo, celular, sexo, fechanacimiento
        FROM pacientes WHERE id_paciente = {paciente_id}
    """, engine)
    paciente_info = paciente.iloc[0]
    info_text = "\n".join([f"{col}: {paciente_info[col]}" for col in paciente.columns])
    pdf.section_body(info_text)

    # 2. Puntajes de test
    pdf.section_title("Puntajes de test")
    resultados = pd.read_sql(f"""
        SELECT tf.nombreformulario, r.puntuacion
        FROM resultados r
        JOIN formularios f ON f.id_formulario = r.id_formulario
        JOIN tipos_formulario tf ON f.id_tipoformulario = tf.id_tipoformulario
        WHERE f.id_paciente = {paciente_id} AND f.id_tipoformulario != 11
    """, engine)

    for _, row in resultados.iterrows():
        pdf.section_body(f"{row.nombreformulario}: {row.puntuacion}")

    # 3. Gráfica de progreso (basada solo en su tratamiento)
    # 1. Obtener ID del tratamiento asignado al paciente
    tratamiento_id_df = pd.read_sql("""
        SELECT id_tratamiento FROM paciente_tratamiento
        WHERE id_paciente = %s
    """, engine, params=(paciente_id,))

    if tratamiento_id_df.empty:
        pdf.section_title("Progreso de habilidades")
        pdf.section_body("El paciente no tiene un tratamiento asignado.")
    else:
        tratamiento_id = tratamiento_id_df.iloc[0]["id_tratamiento"]

        # 2. Obtener actividades esperadas y completadas por habilidad para ese tratamiento
        query = """
            SELECT h.nombre AS Habilidad,
                tha.id_actividad,
                pa.completada
            FROM tratamiento_habilidad_actividad tha
            JOIN actividades a ON tha.id_actividad = a.id_actividad
            JOIN habilidades h ON tha.id_habilidad = h.id_habilidad
            LEFT JOIN paciente_actividad pa ON pa.id_actividad = tha.id_actividad AND pa.id_paciente = %s
            WHERE tha.id_tratamiento = %s AND h.nombre NOT LIKE '%%Final del Tratamiento%%'
        """
        progreso = pd.read_sql(query, engine, params=(paciente_id, tratamiento_id))

        # 3. Calcular progreso real por habilidad
        progreso["completada"] = progreso["completada"].fillna(False).infer_objects(copy=False)

        conteo = progreso.groupby("Habilidad").agg(
            total_actividades=("id_actividad", "count"),
            completadas=("completada", lambda x: x.astype(bool).sum())
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
        SELECT log_sistema, fechaevaluacion
        FROM asignacionessistemaexperto
        WHERE id_paciente = {paciente_id}
        ORDER BY fechaevaluacion DESC
        LIMIT 1
    """, engine)

    if not logs.empty:
        log_text = f"{logs.iloc[0]['fechaevaluacion']}:\n{logs.iloc[0]['log_sistema']}"
        pdf.section_body(log_text)
    else:
        pdf.section_body("Sin registros de asignación del sistema experto.")

    # 5. Puntajes más recientes de post-test (solo si tiene post-test válidos)
    pdf.section_title("Puntajes del post-test")

    post_ids = [1, 2, 5, 4, 9, 7, 8, 6, 10, 12, 13, 14, 15]

    resultados_recientes = pd.read_sql(f"""
        WITH ultimos_formularios AS (
            SELECT f.id_formulario, f.id_tipoformulario, tf.nombreformulario,
                   ROW_NUMBER() OVER (PARTITION BY f.id_tipoformulario ORDER BY f.fecha_respuesta DESC, f.id_formulario DESC) AS rn
            FROM formularios f
            JOIN tipos_formulario tf ON tf.id_tipoformulario = f.id_tipoformulario
            WHERE f.id_paciente = {paciente_id}
            AND f.id_tipoformulario IN ({','.join(map(str, post_ids))})
        )
        SELECT u.nombreformulario, r.puntuacion
        FROM ultimos_formularios u
        JOIN resultados r ON r.id_formulario = u.id_formulario
        WHERE u.rn = 1
    """, engine)

    if resultados_recientes.empty:
        pdf.section_body("No se encontraron puntajes de post-test.")
    else:
        for _, row in resultados_recientes.iterrows():
            pdf.section_body(f"{row.nombreformulario}: {row.puntuacion}")

    # Guardar PDF
    output_path = f"Reporte_Paciente_{paciente_id}.pdf"
    pdf.output(output_path)
    print(f"✅ PDF generado: {output_path}")

if __name__ == "__main__":
    generar_pdf_reporte(paciente_id=1)
