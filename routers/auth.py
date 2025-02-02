from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import HTMLResponse
from itsdangerous import URLSafeTimedSerializer
from correo import verificar_token_verificacion
from correo import enviar_correo_recuperacion
from sqlalchemy.orm import Session
from database import get_db
from models import Paciente
from pydantic import BaseModel
import hashlib
import jwt
from datetime import datetime, timedelta
from fastapi.security import HTTPBearer
from fastapi import Security

router = APIRouter(
    prefix="/auth",
    tags=["Autenticación"]
)

SECRET_KEY = "HBAFIQBbhb2u3412bHB"  # Usa una clave secreta segura y guárdala en un lugar seguro
ALGORITHM = "HS256"

class LoginRequest(BaseModel):
    Correo: str
    Contraseña: str

class ForgotPasswordRequest(BaseModel):
    Correo: str

class ResetPasswordRequest(BaseModel):
    Token: str
    NuevaContraseña: str

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
def login(request: LoginRequest, db: Session = Depends(get_db)):
    usuario = db.query(Paciente).filter(Paciente.Correo == request.Correo).first()

    if not usuario:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")

    hashed_password = hashlib.sha256(request.Contraseña.encode("utf-8")).hexdigest()
    if usuario.Contraseña != hashed_password:
        raise HTTPException(status_code=401, detail="Contraseña incorrecta")

    if not usuario.EsApto:
        raise HTTPException(status_code=403, detail="No estás autorizado para usar el sistema")

    if not usuario.CorreoVerificado:
        raise HTTPException(status_code=403, detail="Debes verificar tu correo para usar el sistema")
 
    # Crear el token JWT
    payload = {
        "id": usuario.ID_Paciente,
        "nombre": usuario.Nombre,
        "exp": datetime.utcnow() + timedelta(hours=2)  # Expira en 2 horas
    }
    token = jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)

    return {"access_token": token, "message": "Login exitoso"}  
    
@router.get("/verify")
def verificar_correo(token: str, db: Session = Depends(get_db)):
    correo = verificar_token_verificacion(token)
    if not correo:
        raise HTTPException(status_code=400, detail="Token inválido o expirado")

    usuario = db.query(Paciente).filter(Paciente.Correo == correo).first()
    if not usuario:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")

    usuario.CorreoVerificado = True
    db.commit()
    content = open("verify_success.html", encoding="utf-8").read()
    return HTMLResponse(content=content, status_code=200)

@router.post("/forgot-password")
def forgot_password(request: ForgotPasswordRequest, db: Session = Depends(get_db)):
    usuario = db.query(Paciente).filter(Paciente.Correo == request.Correo).first()

    if not usuario:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")

    if not usuario.CorreoVerificado:
        raise HTTPException(status_code=403, detail="Debes verificar tu correo antes de recuperar tu contraseña")

    # Enviar correo de recuperación
    enviar_correo_recuperacion(usuario.Correo)
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
def reset_password(request: ResetPasswordRequest, db: Session = Depends(get_db)):
    try:
        # Validar el token
        correo = verificar_token_verificacion(request.Token)
        if not correo:
            raise HTTPException(status_code=400, detail="Token inválido o expirado")
    except Exception:
        raise HTTPException(status_code=400, detail="Token inválido o expirado")

    # Buscar al usuario por correo
    usuario = db.query(Paciente).filter(Paciente.Correo == correo).first()
    if not usuario:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")

    # Actualizar la contraseña
    nueva_contraseña_hashed = hashlib.sha256(request.NuevaContraseña.encode("utf-8")).hexdigest()
    usuario.Contraseña = nueva_contraseña_hashed
    db.commit()

    return {"message": "Contraseña actualizada exitosamente"}
