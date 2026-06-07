from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from datetime import datetime, timedelta
from jose import JWTError, jwt
import bcrypt
import os
from dotenv import load_dotenv


from ..Config.models import Usuario
from ..Config.schemas import UsuarioCreate, UsuarioOut


load_dotenv()

# Configuración de seguridad
SECRET_KEY = os.getenv("SECRET_KEY", "tu-clave-secreta-muy-fuerte-cambiar-en-produccion")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30



def hash_password(password: str) -> str:
    """
    Encripta una contraseña usando bcrypt
    
    Explicación:
    - bcrypt es un algoritmo de hash especial para contraseñas
    - Muy lento a propósito (tarda ~0.3 segundos)
    - Hace que sea imposible hacer "fuerza bruta"
    """
    salt = bcrypt.gensalt(rounds=12)
    hashed = bcrypt.hashpw(password.encode('utf-8'), salt)
    return hashed.decode('utf-8')


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Verifica si una contraseña coincide con su versión hasheada

    """
    return bcrypt.checkpw(plain_password.encode('utf-8'), hashed_password.encode('utf-8'))


def create_access_token(data: dict, expires_delta: timedelta = None) -> str:
    """
    Crea un JWT token de sesión
    
    Explicación:
    - JWT (JSON Web Token) es un estándar para tokens seguros
    - Contiene datos del usuario codificados
    - Expira después de cierto tiempo (30 minutos por defecto)
    - El frontend lo envía en cada solicitud para probar su identidad
    """
    to_encode = data.copy()
    
    # Establecer tiempo de expiración
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    
    to_encode.update({"exp": expire})
    
    # Codificar el token con la clave secreta
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt



def registrar_usuario(usuario_data: UsuarioCreate, db: Session):
    """
    Registra un nuevo usuario en la plataforma
    
    Paso a paso:
    1. Validar que el email no exista ya
    2. Encriptar la contraseña
    3. Crear el usuario en la BD
    4. Retornar los datos del usuario creado
    """
    
    try:
        # Verificar si el email ya existe
        usuario_existente = db.query(Usuario).filter(
            Usuario.correo == usuario_data.correo
        ).first()
        
        if usuario_existente:
            # El email ya está registrado
            return {
                "success": False,
                "error": "El correo electrónico ya está registrado"
            }
        
        # Encriptar la contraseña
        contraseña_hasheada = hash_password(usuario_data.contraseña)
        
        # Crear nuevo usuario
        nuevo_usuario = Usuario(
            nombre=usuario_data.nombre,
            correo=usuario_data.correo,
            contraseña=contraseña_hasheada,
            puntaje=0,
            fecha_registro=datetime.utcnow()
        )
        
        # Guardar en la BD
        db.add(nuevo_usuario)
        db.commit()
        db.refresh(nuevo_usuario)
        
        print(f"✅ Usuario registrado: {nuevo_usuario.nombre} ({nuevo_usuario.correo})")
        
        return {
            "success": True,
            "mensaje": "Usuario registrado exitosamente",
            "id_usuario": nuevo_usuario.id_usuario,
            "usuario": {
                "id_usuario": nuevo_usuario.id_usuario,
                "nombre": nuevo_usuario.nombre,
                "correo": nuevo_usuario.correo,
                "puntaje": nuevo_usuario.puntaje
            }
        }
    
    except IntegrityError:
        db.rollback()
        return {
            "success": False,
            "error": "Error al registrar el usuario. Intenta de nuevo."
        }
    except Exception as e:
        db.rollback()
        print(f"❌ Error en registro: {str(e)}")
        return {
            "success": False,
            "error": f"Error en el servidor: {str(e)}"
        }




def login_usuario(correo: str, contraseña: str, db: Session):
    """
    Autentica a un usuario y genera un token de sesión
    
    Paso a paso:
    1. Buscar el usuario por correo
    2. Verificar que la contraseña sea correcta
    3. Generar un JWT token
    4. Retornar el token y datos del usuario
    """
    
    try:
        # Buscar usuario por correo
        usuario = db.query(Usuario).filter(
            Usuario.correo == correo
        ).first()
        
        # Si no existe el usuario
        if not usuario:
            print(f"❌ Login fallido: Usuario no encontrado ({correo})")
            return {
                "success": False,
                "error": "Correo o contraseña incorrectos"
            }
        
        # Verificar la contraseña
        if not verify_password(contraseña, usuario.contraseña):
            print(f"❌ Login fallido: Contraseña incorrecta ({correo})")
            return {
                "success": False,
                "error": "Correo o contraseña incorrectos"
            }
        
        # Generar token JWT
        access_token = create_access_token(
            data={"sub": str(usuario.id_usuario), "correo": usuario.correo}
        )
        
        print(f"✅ Login exitoso: {usuario.nombre} ({usuario.correo})")
        
        return {
            "success": True,
            "access_token": access_token,
            "token_type": "bearer",
            "usuario": {
                "id_usuario": usuario.id_usuario,
                "nombre": usuario.nombre,
                "correo": usuario.correo,
                "puntaje": usuario.puntaje
            }
        }
    
    except Exception as e:
        print(f"❌ Error en login: {str(e)}")
        return {
            "success": False,
            "error": f"Error en el servidor: {str(e)}"
        }



def verificar_token(token: str):
    """
    Verifica si un JWT token es válido
    
    Explicación:
    - Decodifica el token usando la clave secreta
    - Si la firma es válida, retorna el usuario_id
    - Si expiró o es inválido, retorna None
    """
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        usuario_id: str = payload.get("sub")
        
        if usuario_id is None:
            return None
        
        return int(usuario_id)
    
    except JWTError:
        return None


def obtener_usuario_por_id(usuario_id: int, db: Session):
    """
    Obtiene los datos de un usuario por su ID
    
    Útil para obtener el perfil del usuario después del login
    """
    usuario = db.query(Usuario).filter(
        Usuario.id_usuario == usuario_id
    ).first()
    
    if not usuario:
        return None
    
    return {
        "id_usuario": usuario.id_usuario,
        "nombre": usuario.nombre,
        "correo": usuario.correo,
        "puntaje": usuario.puntaje,
        "fecha_registro": usuario.fecha_registro
    }
