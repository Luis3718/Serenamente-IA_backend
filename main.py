import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from routers import pacientes, auth # Importa los endpoints desde la carpeta routers
from fastapi.staticfiles import StaticFiles

app = FastAPI()

# Configuración de CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Permite todas las URLs de origen
    allow_credentials=True,
    allow_methods=["*"],  # Permite todos los métodos HTTP (GET, POST, etc.)
    allow_headers=["*"],  # Permite todos los encabezados
)

app.mount("/static", StaticFiles(directory="static"), name="static")

# Incluye los routers
app.include_router(pacientes.router)
app.include_router(auth.router)  # Registra el router de autenticación

if __name__ == "__main__":
    # Configuración del puerto
    uvicorn.run("main:app", host="127.0.0.1", port=8002, reload=True)
