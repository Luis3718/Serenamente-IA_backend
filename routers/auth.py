import hashlib
import jwt
from fastapi import APIRouter, Depends, HTTPException, Security
from fastapi.responses import HTMLResponse
from fastapi.security import HTTPBearer
from sqlalchemy.orm import Session
from datetime import datetime, timedelta
from models import paciente as Paciente
from database import get_db
from correo import verificar_token_verificacion, enviar_correo_recuperacion
from schemas import login_request, forgot_password_request, reset_password_request

router = APIRouter(
    prefix="/auth",
    tags=["Autenticación"]
)

SECRET_KEY = "HBAFIQBbhb2u3412bHB"  # Usa una clave secreta segura y guárdala en un lugar seguro
ALGORITHM = "HS256"

security = HTTPBearer()

def obtener_usuario_actual(token: str = Security(security)):
    try:
        payload = jwt.decode(token.credentials, SECRET_KEY, algorithms=[ALGORITHM])
        return {"id": payload["id"], "nombre": payload["nombre"]}
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token expirado")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail="Token inválido")

@router.post("/login")
def login(request: login_request, db: Session = Depends(get_db)):
    usuario = db.query(Paciente).filter(Paciente.correo == request.correo).first()

    if not usuario:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")

    hashed_password = hashlib.sha256(request.contrasena.encode("utf-8")).hexdigest()
    if usuario.contrasena != hashed_password:
        raise HTTPException(status_code=401, detail="Contraseña incorrecta")

    if not usuario.esapto:
        raise HTTPException(status_code=403, detail="No estás autorizado para usar el sistema")

    if not usuario.correoverificado:
        raise HTTPException(status_code=403, detail="Debes verificar tu correo para usar el sistema")

    payload = {
        "id": usuario.id_paciente,
        "nombre": usuario.nombre,
        "formulario_contestado": usuario.formulario_contestado,
        "entrevista_contestada": usuario.entrevista_contestada,
        "exp": datetime.utcnow() + timedelta(hours=2)
    }
    token = jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)

    return {
        "access_token": token,
        "message": "Login exitoso",
        "formulario_contestado": usuario.formulario_contestado,
        "entrevista_contestada": usuario.entrevista_contestada
    }

@router.get("/verify")
def verificar_correo(token: str, db: Session = Depends(get_db)):
    correo = verificar_token_verificacion(token)
    if not correo:
        raise HTTPException(status_code=400, detail="Token inválido o expirado")

    usuario = db.query(Paciente).filter(Paciente.correo == correo).first()
    if not usuario:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")

    usuario.correoverificado = True
    db.commit()
    content = open("verify_success.html", encoding="utf-8").read()
    return HTMLResponse(content=content, status_code=200)

@router.get("/verify-token")
def verificar_token_autenticado(usuario: dict = Depends(obtener_usuario_actual)):
    return {"message": "Token válido", "usuario": usuario}

@router.post("/update-form-status")
def actualizar_estado_formulario(usuario: dict = Depends(obtener_usuario_actual), db: Session = Depends(get_db)):
    db_usuario = db.query(Paciente).filter(Paciente.id_paciente == usuario["id"]).first()
    if not db_usuario:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")

    db_usuario.formulario_contestado = True
    db.commit()
    db.refresh(db_usuario)

    return {"message": "Formulario contestado con éxito"}

@router.post("/forgot-password")
def forgot_password(request: forgot_password_request, db: Session = Depends(get_db)):
    usuario = db.query(Paciente).filter(Paciente.correo == request.correo).first()

    if not usuario:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")

    if not usuario.correoverificado:
        raise HTTPException(status_code=403, detail="Debes verificar tu correo antes de recuperar tu contraseña")

    enviar_correo_recuperacion(usuario.correo)
    return {"message": "Instrucciones para recuperar tu contraseña fueron enviadas a tu correo"}

@router.get("/reset-password")
def reset_password_page(token: str):
    # Verificar si el token es válido antes de mostrar la página
    correo = verificar_token_verificacion(token)
    if not correo:
        raise HTTPException(status_code=400, detail="Token inválido o expirado")
    
    # Cargar una página HTML con el formulario para restablecer la contraseña
    content = open("reset_password_form.html", encoding="utf-8").read()
    return HTMLResponse(content=content, status_code=200)

@router.post("/reset-password")
def reset_password(request: reset_password_request, db: Session = Depends(get_db)):
    try:
        correo = verificar_token_verificacion(request.token)
        if not correo:
            raise HTTPException(status_code=400, detail="Token inválido o expirado")
    except Exception:
        raise HTTPException(status_code=400, detail="Token inválido o expirado")

    usuario = db.query(Paciente).filter(Paciente.correo == correo).first()
    if not usuario:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")

    nueva_contrasena_hashed = hashlib.sha256(request.nuevacontrasena.encode("utf-8")).hexdigest()
    usuario.contrasena = nueva_contrasena_hashed
    db.commit()

    return {"message": "Contraseña actualizada exitosamente"}
