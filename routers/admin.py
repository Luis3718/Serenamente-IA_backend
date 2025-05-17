import hashlib
import jwt
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from database import get_db
from models import Admin
from schemas import AdminLogin, AdminCreate
from datetime import datetime, timedelta
from fastapi.security import HTTPBearer
from fastapi import Security

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