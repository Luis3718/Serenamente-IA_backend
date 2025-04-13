import pandas as pd
from sqlalchemy import create_engine

# Establecer conexión con la base de datos MySQL
engine = create_engine('mysql+pymysql://root:root@localhost/SerenaMenteDB')

# Ejecutar consulta SQL para obtener los datos
query = "SELECT * FROM Preguntas"
df = pd.read_sql_query(query, engine)
print(df)

# Exportar a Excel
excel_path = 'C:/Users/Alvar/Proyectos/Serenamente-IA_backend/Preguntas.xlsx'
df.to_excel(excel_path, index=False)

print("Los datos han sido exportados a Excel con éxito.")
