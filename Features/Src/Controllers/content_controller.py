"""
CONTROLADOR DE CONTENIDO - content_controller.py

Este archivo contiene toda la lógica de:
- Obtener materias disponibles
- Obtener preguntas de una materia
- Guardar respuestas del usuario
- Calcular estadísticas del usuario
"""

from sqlalchemy.orm import Session
from ..Config.models import Usuario, Materia, Pregunta, Opcion, Progreso

# =====================================================
# CONTROLADOR: OBTENER MATERIAS
# =====================================================

def obtener_todas_materias(db: Session):
    """
    Obtiene todas las materias disponibles
    
    Explicación:
    - Consulta todas las filas de la tabla materias
    - Las convierte a un formato que el frontend entiende
    - Retorna una lista de diccionarios
    """
    
    try:
        materias = db.query(Materia).all()
        
        resultado = []
        for materia in materias:
            resultado.append({
                "id_materia": materia.id_materia,
                "nombre": materia.nombre,
                "descripcion": getattr(materia, 'descripcion', 'Aprende con Lynko'),
                "nivel": getattr(materia, 'nivel', 1),
                "icon": getattr(materia, 'icono', '📚'),
                "color": getattr(materia, 'color', '#FF8C42')
            })
        
        print(f"✅ Materias obtenidas: {len(resultado)}")
        return {
            "success": True,
            "materias": resultado
        }
    
    except Exception as e:
        print(f"❌ Error obteniendo materias: {str(e)}")
        return {
            "success": False,
            "error": f"Error: {str(e)}"
        }


# =====================================================
# CONTROLADOR: OBTENER MATERIA ESPECÍFICA
# =====================================================

def obtener_materia_por_id(id_materia: int, db: Session):
    """
    Obtiene los detalles de una materia específica
    """
    
    try:
        materia = db.query(Materia).filter(
            Materia.id_materia == id_materia
        ).first()
        
        if not materia:
            return {
                "success": False,
                "error": "Materia no encontrada"
            }
        
        return {
            "success": True,
            "materia": {
                "id_materia": materia.id_materia,
                "nombre": materia.nombre,
                "descripcion": getattr(materia, 'descripcion', ''),
                "nivel": getattr(materia, 'nivel', 1),
                "icon": getattr(materia, 'icono', '📚'),
                "color": getattr(materia, 'color', '#FF8C42')
            }
        }
    
    except Exception as e:
        print(f"❌ Error obteniendo materia: {str(e)}")
        return {
            "success": False,
            "error": f"Error: {str(e)}"
        }


# =====================================================
# CONTROLADOR: OBTENER PREGUNTAS DE UNA MATERIA
# =====================================================

def obtener_preguntas_por_materia(id_materia: int, db: Session):
    """
    Obtiene todas las preguntas de una materia con sus opciones
    
    Explicación:
    - Busca todas las preguntas de la materia
    - Para cada pregunta, obtiene sus opciones
    - NO incluye la respuesta correcta en el frontend
      (la verificación se hace en el servidor)
    """
    
    try:
        preguntas = db.query(Pregunta).filter(
            Pregunta.id_materia == id_materia
        ).all()
        
        if not preguntas:
            return {
                "success": False,
                "error": "No hay preguntas en esta materia"
            }
        
        resultado = []
        for pregunta in preguntas:
            # Obtener opciones de esta pregunta
            opciones = db.query(Opcion).filter(
                Opcion.id_pregunta == pregunta.id_pregunta
            ).all()
            
            opciones_lista = []
            for opcion in opciones:
                opciones_lista.append({
                    "id_opcion": opcion.id_opcion,
                    "texto": opcion.opcion,
                    # NO enviamos es_correcta al frontend
                    # Se verifica en el servidor por seguridad
                })
            
            resultado.append({
                "id_pregunta": pregunta.id_pregunta,
                "pregunta": pregunta.pregunta,
                "nivel": pregunta.nivel,
                "opciones": opciones_lista
            })
        
        print(f"✅ Preguntas obtenidas: {len(resultado)}")
        return {
            "success": True,
            "preguntas": resultado
        }
    
    except Exception as e:
        print(f"❌ Error obteniendo preguntas: {str(e)}")
        return {
            "success": False,
            "error": f"Error: {str(e)}"
        }


# =====================================================
# CONTROLADOR: GUARDAR RESPUESTA
# =====================================================

def guardar_respuesta(usuario_id: int, id_pregunta: int, id_opcion: int, db: Session):
    """
    Guarda la respuesta de un usuario y otorga XP si es correcta
    
    Paso a paso:
    1. Obtener la opción seleccionada
    2. Verificar si es correcta
    3. Crear registro en la tabla progreso
    4. Si es correcta, sumar XP al usuario
    5. Retornar resultado
    """
    
    try:
        # Obtener la opción seleccionada
        opcion = db.query(Opcion).filter(
            Opcion.id_opcion == id_opcion
        ).first()
        
        if not opcion:
            return {
                "success": False,
                "error": "Opción no encontrada"
            }
        
        # Verificar si la respuesta es correcta
        es_correcta = opcion.es_correcta
        
        # Crear registro de progreso
        progreso = Progreso(
            id_usuario=usuario_id,
            id_pregunta=id_pregunta,
            correcta=es_correcta
        )
        
        db.add(progreso)
        
        # Si es correcta, sumar XP
        xp_ganado = 0
        nuevo_puntaje = 0
        
        if es_correcta:
            usuario = db.query(Usuario).filter(
                Usuario.id_usuario == usuario_id
            ).first()
            
            if usuario:
                xp_ganado = 10  # XP base por respuesta correcta
                usuario.puntaje += xp_ganado
                nuevo_puntaje = usuario.puntaje
                db.commit()
                
                print(f"✅ Respuesta correcta. XP ganado: {xp_ganado}")
                
                return {
                    "success": True,
                    "es_correcta": True,
                    "xp_ganado": xp_ganado,
                    "nuevo_puntaje": nuevo_puntaje,
                    "mensaje": f"¡Correcto! +{xp_ganado} XP"
                }
        
        db.commit()
        
        print(f"❌ Respuesta incorrecta")
        
        return {
            "success": True,
            "es_correcta": False,
            "xp_ganado": 0,
            "mensaje": "Respuesta incorrecta. Intenta de nuevo."
        }
    
    except Exception as e:
        db.rollback()
        print(f"❌ Error guardando respuesta: {str(e)}")
        return {
            "success": False,
            "error": f"Error: {str(e)}"
        }


# =====================================================
# CONTROLADOR: OBTENER ESTADÍSTICAS DEL USUARIO
# =====================================================

def obtener_estadisticas_usuario(usuario_id: int, db: Session):
    """
    Obtiene las estadísticas completas del usuario
    
    Calcula:
    - Puntaje total
    - Nivel (basado en XP)
    - Respuestas correctas
    - Respuestas incorrectas
    - Porcentaje de acierto
    - Racha de días (simplificado)
    """
    
    try:
        usuario = db.query(Usuario).filter(
            Usuario.id_usuario == usuario_id
        ).first()
        
        if not usuario:
            return {
                "success": False,
                "error": "Usuario no encontrado"
            }
        
        # Obtener progreso del usuario
        progresos = db.query(Progreso).filter(
            Progreso.id_usuario == usuario_id
        ).all()
        
        # Calcular estadísticas
        correctas = sum(1 for p in progresos if p.correcta)
        incorrectas = sum(1 for p in progresos if not p.correcta)
        
        total = len(progresos)
        porcentaje = (correctas / total * 100) if total > 0 else 0
        
        # Calcular nivel (cada 100 XP = 1 nivel)
        nivel = (usuario.puntaje // 100) + 1
        
        print(f"✅ Estadísticas obtenidas para usuario: {usuario_id}")
        
        return {
            "success": True,
            "estadisticas": {
                "puntaje_total": usuario.puntaje,
                "nivel": nivel,
                "respuestas_correctas": correctas,
                "respuestas_incorrectas": incorrectas,
                "porcentaje_acierto": round(porcentaje, 2),
                "total_respuestas": total,
                "racha_dias": 0  # Se puede calcular desde fecha_registro
            }
        }
    
    except Exception as e:
        print(f"❌ Error obteniendo estadísticas: {str(e)}")
        return {
            "success": False,
            "error": f"Error: {str(e)}"
        }


# =====================================================
# CONTROLADOR: OBTENER PROGRESO POR MATERIA
# =====================================================

def obtener_progreso_materia(usuario_id: int, id_materia: int, db: Session):
    """
    Obtiene el progreso del usuario en una materia específica
    
    Retorna:
    - Nombre de la materia
    - Preguntas respondidas
    - Preguntas correctas
    - Porcentaje de acierto
    - Nivel actual
    """
    
    try:
        # Obtener preguntas de la materia
        preguntas = db.query(Pregunta).filter(
            Pregunta.id_materia == id_materia
        ).all()
        
        if not preguntas:
            return {
                "success": False,
                "error": "No hay preguntas en esta materia"
            }
        
        # Obtener respuestas del usuario en esa materia
        respuestas = db.query(Progreso).filter(
            Progreso.id_usuario == usuario_id,
            Progreso.id_pregunta.in_([p.id_pregunta for p in preguntas])
        ).all()
        
        correctas = sum(1 for r in respuestas if r.correcta)
        total = len(respuestas)
        porcentaje = (correctas / total * 100) if total > 0 else 0
        
        # Obtener nombre de la materia
        materia = db.query(Materia).filter(
            Materia.id_materia == id_materia
        ).first()
        
        print(f"✅ Progreso obtenido para materia: {id_materia}")
        
        return {
            "success": True,
            "progreso": {
                "materia": materia.nombre if materia else "Desconocida",
                "preguntas_respondidas": total,
                "preguntas_correctas": correctas,
                "porcentaje": round(porcentaje, 2),
                "nivel_actual": 1,
                "proximo_nivel": 2
            }
        }
    
    except Exception as e:
        print(f"❌ Error obteniendo progreso: {str(e)}")
        return {
            "success": False,
            "error": f"Error: {str(e)}"
        }


# =====================================================
# CONTROLADOR: OBTENER OPCIÓN CORRECTA (Para verificar)
# =====================================================

def obtener_respuesta_correcta(id_pregunta: int, db: Session):
    """
    Obtiene la respuesta correcta de una pregunta
    
    NOTA: Esta función NO se expone en la API
    Solo se usa internamente en el servidor
    """
    
    try:
        opcion_correcta = db.query(Opcion).filter(
            Opcion.id_pregunta == id_pregunta,
            Opcion.es_correcta == True
        ).first()
        
        if opcion_correcta:
            return opcion_correcta.id_opcion
        
        return None
    
    except Exception as e:
        print(f"❌ Error obteniendo respuesta correcta: {str(e)}")
        return None
