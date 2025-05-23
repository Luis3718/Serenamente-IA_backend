import hashlib
import os
import jwt
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from database import get_db
from models import admin as Admin
from models import paciente as Paciente
from schemas import admin_login as AdminLogin
from schemas import admin_create, paciente_admin_full_update
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
    admin = db.query(Admin).filter(Admin.usuario == data.usuario).first()
    if not admin:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")
    
    hashed = hash_password(data.contrasena)
    if admin.contrasena != hashed:
        raise HTTPException(status_code=401, detail="Contraseña incorrecta")

    # Generar token
    payload = {
        "id": admin.id_admin,
        "usuario": admin.usuario,
        "exp": datetime.utcnow() + timedelta(hours=2)
    }
    token = jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)

    return {"access_token": token, "message": "Login exitoso"}

@router.get("/perfil")
def perfil_admin(admin_actual=Depends(obtener_admin_actual)):
    return {"message": f"Bienvenido, {admin_actual['usuario']}"}

@router.post("/crear")
def crear_admin(data: admin_create, db: Session = Depends(get_db)):
    existente = db.query(Admin).filter(Admin.usuario == data.usuario).first()
    if existente:
        raise HTTPException(status_code=400, detail="El usuario ya existe")

    nuevo_admin = Admin(
        usuario=data.usuario,
        contrasena=hash_password(data.contrasena)
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
    
@router.put("/actualizar_completo/{paciente_id}")
def actualizar_paciente_completo(
    paciente_id: int,
    data: paciente_admin_full_update,
    db: Session = Depends(get_db),
    admin=Depends(obtener_admin_actual)
):
    db_paciente = db.query(Paciente).filter(Paciente.id_paciente == paciente_id).first()
    if not db_paciente:
        raise HTTPException(status_code=404, detail="Paciente no encontrado")

    if data.nombre:
        db_paciente.nombre = data.nombre
    if data.apellidos:
        db_paciente.apellidos = data.apellidos
    if data.correo:
        db_paciente.correo = data.correo
    if data.correoalternativo:
        db_paciente.correoalternativo = data.correoalternativo
    if data.sexo:
        db_paciente.sexo = data.sexo
    if data.fechanacimiento:
        db_paciente.fechanacimiento = data.fechanacimiento
    if data.nuevacontrasena:
        db_paciente.contrasena = hash_password(data.nuevacontrasena)

    db.commit()
    db.refresh(db_paciente)
    return {"message": "Paciente actualizado completamente"}