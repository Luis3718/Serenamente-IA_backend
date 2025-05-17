import hashlib
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from database import get_db
from models import Admin
from schemas import AdminLogin, AdminCreate

router = APIRouter(prefix="/admin", tags=["Administrador"])

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
    
    return {"mensaje": "Login exitoso"}

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