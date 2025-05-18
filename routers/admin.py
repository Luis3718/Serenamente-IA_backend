import hashlib
import os
import jwt
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from database import get_db
from models import Admin
from schemas import AdminLogin, AdminCreate
from datetime import datetime, timedelta
from fastapi.security import HTTPBearer
from fastapi import Security
from Reportes import generar_pdf_reporte
from Exportar_preguntas import exportar_pretest_individual, exportar_pretest_completo, exportar_base_completa
from fastapi.responses import FileResponse
from starlette.background import BackgroundTask

SECRET_KEY = "HBAFIQBbhb2u3412bHB"
ALGORITHM = "HS256"
security = HTTPBearer()

router = APIRouter(prefix="/admin", tags=["Administrador"])

def obtener_admin_actual(token: str = Security(security)):
    try:
        payload = jwt.decode(token.credentials, SECRET_KEY, algorithms=[ALGORITHM])
        return {"id": payload["id"], "usuario": payload["usuario"]}
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token expirado")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail="Token inválido")

def hash_password(password: str) -> str:
    """Devuelve el hash SHA-256 de la contraseña."""
    return hashlib.sha256(password.encode("utf-8")).hexdigest()

@router.post("/login")
def login_admin(data: AdminLogin, db: Session = Depends(get_db)):
    admin = db.query(Admin).filter(Admin.Usuario == data.usuario).first()
    if not admin:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")
    
    hashed = hash_password(data.contrasena)
    if admin.Contrasena != hashed:
        raise HTTPException(status_code=401, detail="Contraseña incorrecta")

    # Generar token
    payload = {
        "id": admin.ID_Admin,
        "usuario": admin.Usuario,
        "exp": datetime.utcnow() + timedelta(hours=2)
    }
    token = jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)

    return {"access_token": token, "message": "Login exitoso"}

@router.get("/perfil")
def perfil_admin(admin=Depends(obtener_admin_actual)):
    return {"message": f"Bienvenido, {admin['usuario']}"}

@router.post("/crear")
def crear_admin(data: AdminCreate, db: Session = Depends(get_db)):
    existente = db.query(Admin).filter(Admin.Usuario == data.usuario).first()
    if existente:
        raise HTTPException(status_code=400, detail="El usuario ya existe")

    nuevo_admin = Admin(
        Usuario=data.usuario,
        Contrasena=hash_password(data.contrasena)
    )
    db.add(nuevo_admin)
    db.commit()
    db.refresh(nuevo_admin)
    return {"mensaje": "Administrador creado exitosamente"}

@router.get("/descargar_reporte/{paciente_id}")
def descargar_reporte_paciente(paciente_id: int, admin=Depends(obtener_admin_actual)):
    try:
        generar_pdf_reporte(paciente_id)
        filename = f"Reporte_Paciente_{paciente_id}.pdf"
        if not os.path.exists(filename):
            raise HTTPException(status_code=404, detail="Reporte no encontrado")
        return FileResponse(
            path=filename,
            filename=filename,
            media_type="application/pdf",
            background=BackgroundTask(lambda: os.remove(filename))
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al generar el reporte: {str(e)}")

@router.get("/descargar_pretest/{paciente_id}")
def descargar_pretest_paciente(paciente_id: int, admin=Depends(obtener_admin_actual)):
    try:
        # Genera el archivo con nombre interno automático
        filename = exportar_pretest_individual(paciente_id)

        if not os.path.exists(filename):
            raise HTTPException(status_code=404, detail="Archivo no generado")

        return FileResponse(
            path=filename,
            filename=filename,
            media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            background=BackgroundTask(lambda: os.remove(filename))
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al generar el pretest: {str(e)}")

@router.get("/exportar_pretests_completo")
def descargar_pretests_completos(admin=Depends(obtener_admin_actual)):
    try:
        exportar_pretest_completo()
        filename = "Pretest_Completo.xlsx"

        if not os.path.exists(filename):
            raise HTTPException(status_code=404, detail="Archivo no generado")

        return FileResponse(
            path=filename,
            filename="Pretest_Completo.xlsx",
            media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            background=BackgroundTask(lambda: os.remove(filename))
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error exportando pretests: {str(e)}")

@router.get("/exportar_base_completa")
def descargar_base_completa(admin=Depends(obtener_admin_actual)):
    try:
        exportar_base_completa()
        filename = "Base_de_datos_Serenamente.xlsx"

        if not os.path.exists(filename):
            raise HTTPException(status_code=404, detail="Archivo no generado")

        return FileResponse(
            path=filename,
            filename="Base_de_datos_completa.xlsx",
            media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            background=BackgroundTask(lambda: os.remove(filename))
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error exportando base completa: {str(e)}")