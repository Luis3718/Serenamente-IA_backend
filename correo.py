import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from itsdangerous import URLSafeTimedSerializer

def cargar_credenciales(archivo):
    credenciales = {}
    try:
        with open(archivo, "r") as f:
            for linea in f:
                if "=" in linea:
                    clave, valor = linea.strip().split("=", 1)
                    credenciales[clave] = valor
    except FileNotFoundError:
        raise FileNotFoundError(f"El archivo {archivo} no fue encontrado.")
    return credenciales

# Generar un token de verificación
def generar_token_verificacion(correo):
    serializer = URLSafeTimedSerializer("clave-secreta")
    return serializer.dumps(correo, salt="verificacion-correo")

# Verificar un token de verificación
def verificar_token_verificacion(token):
    serializer = URLSafeTimedSerializer("clave-secreta")
    try:
        correo = serializer.loads(token, salt="verificacion-correo", max_age=3600)
        return correo
    except Exception:
        return None

def enviar_correo_verificacion(correo):
    try:
        credenciales = cargar_credenciales("smtp_config.txt")
        remitente = credenciales.get("SMTP_USER")
        contraseña = credenciales.get("SMTP_PASSWORD")
    except FileNotFoundError as e:
        print(e)
        return False

    token = generar_token_verificacion(correo)
    enlace = f"http://127.0.0.1:8002/auth/verify?token={token}"
    
    mensaje = MIMEMultipart()
    mensaje["From"] = remitente
    mensaje["To"] = correo
    mensaje["Subject"] = "Confirmación de Registro en la Plataforma de SerenaMente IA"
    mensaje.attach(MIMEText(
        f"""Estimado/a ¡Bienvenido/a a la plataforma de SerenaMente IA! 
        Nos complace informarle que su registro ha sido exitoso. A continuación, encontrará los detalles para acceder a la plataforma: 

        Verifica tu correo: {enlace}

        Si tiene alguna pregunta o necesita asistencia adicional, no dude en 
        ponerse en contacto con nuestro equipo de soporte a través de [correo 
        de contacto].

        Reciba un cordial saludo.
        Atentamente
        Equipo SerenaMente
        FESI-UNAM IA""", "plain"))

    try:
        with smtplib.SMTP("smtp.gmail.com", 587) as servidor:
            servidor.starttls()
            servidor.login(remitente, contraseña)
            servidor.sendmail(remitente, correo, mensaje.as_string())
            print("Correo enviado exitosamente.")
            return True
    except smtplib.SMTPAuthenticationError as e:
        print("Error de autenticación:", e)
    except smtplib.SMTPException as e:
        print("Error al enviar el correo:", e)
    return False

def enviar_correo_recuperacion(correo):
    try:
        credenciales = cargar_credenciales("smtp_config.txt")
        remitente = credenciales.get("SMTP_USER")
        contraseña = credenciales.get("SMTP_PASSWORD")
    except FileNotFoundError as e:
        print(e)
        return False

    token = generar_token_verificacion(correo)
    enlace = f"http://127.0.0.1:8002/auth/reset-password?token={token}"

    mensaje = MIMEMultipart()
    mensaje["From"] = remitente
    mensaje["To"] = correo
    mensaje["Subject"] = "Recuperación de Contraseña - SerenaMente IA"
    mensaje.attach(MIMEText(
        f"""
        Hola,

        Hemos recibido una solicitud para restablecer tu contraseña. Haz clic en el siguiente enlace para continuar:

        {enlace}

        Si no realizaste esta solicitud, ignora este correo.

        Saludos,
        El equipo de SerenaMente IA
        """, "plain"))

    try:
        with smtplib.SMTP("smtp.gmail.com", 587) as servidor:
            servidor.starttls()
            servidor.login(remitente, contraseña)
            servidor.sendmail(remitente, correo, mensaje.as_string())
            print("Correo enviado exitosamente.")
            return True
    except smtplib.SMTPAuthenticationError as e:
        print("Error de autenticación:", e)
    except smtplib.SMTPException as e:
        print("Error al enviar el correo:", e)
    return False
