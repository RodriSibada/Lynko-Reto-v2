from sqlalchemy import Column, Integer, String, Text, Boolean, ForeignKey, Date, TIMESTAMP
from sqlalchemy.orm import relationship
from database import Base

class Usuario(Base):
    __tablename__ = "usuarios"

    id_usuario = Column(Integer, primary_key=True, index=True)
    nombre = Column(String, nullable=False)
    correo = Column(String, unique=True, nullable=False)
    contraseña = Column(String, nullable=False)
    puntaje = Column(Integer, default=0)
    fecha_registro = Column(TIMESTAMP)

    progresos = relationship("Progreso", back_populates="usuario")
    examenes = relationship("Examen", back_populates="usuario")


class Materia(Base):
    __tablename__ = "materias"

    id_materia = Column(Integer, primary_key=True, index=True)
    nombre = Column(String, nullable=False)

    preguntas = relationship("Pregunta", back_populates="materia")


class Pregunta(Base):
    __tablename__ = "preguntas"

    id_pregunta = Column(Integer, primary_key=True, index=True)
    pregunta = Column(Text, nullable=False)
    nivel = Column(Integer, default=1)

    id_materia = Column(Integer, ForeignKey("materias.id_materia"))

    # relaciones
    materia = relationship("Materia", back_populates="preguntas")
    opciones = relationship("Opcion", back_populates="pregunta")
    progresos = relationship("Progreso", back_populates="pregunta")


class Opcion(Base):
    __tablename__ = "opciones"

    id_opcion = Column(Integer, primary_key=True, index=True)
    opcion = Column(Text, nullable=False)
    es_correcta = Column(Boolean, default=False)

    id_pregunta = Column(Integer, ForeignKey("preguntas.id_pregunta"))

    pregunta = relationship("Pregunta", back_populates="opciones")


class Progreso(Base):
    __tablename__ = "progreso"

    id_progreso = Column(Integer, primary_key=True, index=True)
    correcta = Column(Boolean)

    id_usuario = Column(Integer, ForeignKey("usuarios.id_usuario"))
    id_pregunta = Column(Integer, ForeignKey("preguntas.id_pregunta"))

    usuario = relationship("Usuario", back_populates="progresos")
    pregunta = relationship("Pregunta", back_populates="progresos")


class Examen(Base):
    __tablename__ = "examenes"

    id_examen = Column(Integer, primary_key=True, index=True)
    fecha = Column(Date)

    id_usuario = Column(Integer, ForeignKey("usuarios.id_usuario"))
    materia = Column(Integer)

    usuario = relationship("Usuario", back_populates="examenes")
