from pydantic import BaseModel

class UsuarioCreate(BaseModel):
    nombre: str
    correo: str
    contraseña: str

class UsuarioOut(BaseModel):
    id_usuario: int
    nombre: str
    correo: str
    puntaje: int

    class Config:
        from_attributes = True
