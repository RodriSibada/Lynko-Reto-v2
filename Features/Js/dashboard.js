/* =====================================================
   DASHBOARD.JS - Lógica principal del dashboard
   
   Funcionalidades:
   - Cargar materias desde API
   - Mostrar ruta de aprendizaje
   - Cargar y presentar preguntas
   - Guardar respuestas
   - Mostrar resultados
   ===================================================== */

const API_BASE_URL = 'http://localhost:8000/api';

// Variables globales
let usuarioActual = null;
let materiasDisponibles = [];
let preguntasActuales = [];
let materiaSeleccionada = null;
let indicePreguntaActual = 0;
let respuestasCorrectas = 0;
let xpGanado = 0;

// =====================================================
// INICIALIZACIÓN
// =====================================================

document.addEventListener('DOMContentLoaded', function() {
    console.log('🎮 Dashboard cargado');
    
    // Verificar que el usuario esté logueado
    verificarAutenticacion();
    
    // Cargar datos del usuario
    cargarDatosUsuario();
    
    // Cargar materias disponibles
    cargarMaterias();
    
    // Configurar event listeners
    configurarEventListeners();
});

// =====================================================
// VERIFICAR AUTENTICACIÓN
// =====================================================

function verificarAutenticacion() {
    const token = localStorage.getItem('token');
    
    if (!token) {
        console.log('❌ No hay token. Redirigiendo a login...');
        window.location.href = 'login.html';
        return;
    }
    
    console.log('✅ Usuario autenticado');
}

// =====================================================
// CARGAR DATOS DEL USUARIO
// =====================================================

function cargarDatosUsuario() {
    const usuarioJSON = localStorage.getItem('usuario');
    
    if (usuarioJSON) {
        usuarioActual = JSON.parse(usuarioJSON);
        console.log('👤 Usuario:', usuarioActual.nombre);
        
        // Actualizar UI con nombre del usuario
        document.getElementById('nombre-usuario').textContent = usuarioActual.nombre;
        document.getElementById('puntaje-total').textContent = usuarioActual.puntaje || '0';
        
        // Obtener estadísticas del usuario
        obtenerEstadisticas();
    }
}

// =====================================================
// OBTENER ESTADÍSTICAS DEL USUARIO
// =====================================================

async function obtenerEstadisticas() {
    if (!usuarioActual) return;
    
    try {
        const response = await fetch(
            `${API_BASE_URL}/content/usuario/${usuarioActual.id_usuario}/estadisticas`
        );
        
        if (!response.ok) throw new Error('Error al obtener estadísticas');
        
        const stats = await response.json();
        console.log('📊 Estadísticas:', stats);
        
        // Actualizar UI
        document.getElementById('puntaje-total').textContent = stats.puntaje_total;
        document.getElementById('racha').textContent = stats.racha_dias || '0';
    } catch (error) {
        console.error('❌ Error obteniendo estadísticas:', error);
    }
}

// =====================================================
// CARGAR MATERIAS
// =====================================================

async function cargarMaterias() {
    try {
        console.log('📚 Cargando materias...');
        
        const response = await fetch(`${API_BASE_URL}/content/materias`);
        
        if (!response.ok) {
            throw new Error(`Error HTTP: ${response.status}`);
        }
        
        materiasDisponibles = await response.json();
        console.log('✅ Materias cargadas:', materiasDisponibles.length);
        
        // Mostrar materias en la UI
        mostrarMaterias(materiasDisponibles);
    } catch (error) {
        console.error('❌ Error cargando materias:', error);
        mostrarError('No se pudieron cargar las materias. Intenta de nuevo.');
    }
}

// =====================================================
// MOSTRAR MATERIAS EN LA UI
// =====================================================

function mostrarMaterias(materias) {
    const grid = document.getElementById('materias-grid');
    grid.innerHTML = ''; // Limpiar skeleton loaders
    
    materias.forEach(materia => {
        const card = document.createElement('div');
        card.className = 'materia-card';
        card.innerHTML = `
            <span class="materia-icon">${materia.icon || '📚'}</span>
            <div class="materia-nombre">${materia.nombre}</div>
            <div class="materia-descripcion">${materia.descripcion || ''}</div>
            <div class="materia-progreso">
                <div class="materia-progreso-fill" style="width: 45%"></div>
            </div>
        `;
        
        card.addEventListener('click', () => seleccionarMateria(materia));
        grid.appendChild(card);
    });
}

// =====================================================
// SELECCIONAR MATERIA
// =====================================================

async function seleccionarMateria(materia) {
    console.log('📖 Materia seleccionada:', materia.nombre);
    
    materiaSeleccionada = materia;
    
    // Cambiar a vista de ruta
    document.getElementById('materias-section').style.display = 'none';
    document.getElementById('ruta-section').style.display = 'block';
    document.getElementById('ejercicio-section').style.display = 'none';
    
    // Actualizar título
    document.getElementById('materia-titulo').textContent = materia.nombre;
    
    // Cargar preguntas de la materia
    await cargarPreguntasMateria(materia.id_materia);
    
    // Crear ruta visual
    crearRutaVisual();
}

// =====================================================
// CARGAR PREGUNTAS DE UNA MATERIA
// =====================================================

async function cargarPreguntasMateria(idMateria) {
    try {
        console.log('❓ Cargando preguntas de materia:', idMateria);
        
        const response = await fetch(
            `${API_BASE_URL}/content/materias/${idMateria}/preguntas`
        );
        
        if (!response.ok) {
            throw new Error(`Error HTTP: ${response.status}`);
        }
        
        preguntasActuales = await response.json();
        console.log('✅ Preguntas cargadas:', preguntasActuales.length);
    } catch (error) {
        console.error('❌ Error cargando preguntas:', error);
        mostrarError('No se pudieron cargar las preguntas.');
    }
}

// =====================================================
// CREAR RUTA VISUAL (ESTILO DUOLINGO)
// =====================================================

function crearRutaVisual() {
    const rutaContainer = document.getElementById('ruta-container');
    rutaContainer.innerHTML = '';
    
    // Crear hasta 10 niveles (o la cantidad de preguntas disponibles)
    const cantidadNiveles = Math.min(preguntasActuales.length, 10);
    
    for (let i = 0; i < cantidadNiveles; i++) {
        // Nivel
        const nivelItem = document.createElement('div');
        nivelItem.className = 'nivel-item';
        
        const nivelNumero = document.createElement('div');
        nivelNumero.className = 'nivel-numero';
        nivelNumero.textContent = i + 1;
        nivelNumero.onclick = () => iniciarEjercicio(i);
        nivelNumero.style.cursor = 'pointer';
        
        const nivelNombre = document.createElement('div');
        nivelNombre.className = 'nivel-nombre';
        nivelNombre.textContent = `Nivel ${i + 1}`;
        
        nivelItem.appendChild(nivelNumero);
        nivelItem.appendChild(nivelNombre);
        
        rutaContainer.appendChild(nivelItem);
        
        // Conector (si no es el último)
        if (i < cantidadNiveles - 1) {
            const conector = document.createElement('div');
            conector.className = 'nivel-conector';
            rutaContainer.appendChild(conector);
        }
    }
}

// =====================================================
// INICIAR EJERCICIO
// =====================================================

function iniciarEjercicio(indice) {
    console.log('🎮 Iniciando ejercicio:', indice + 1);
    
    indicePreguntaActual = indice;
    respuestasCorrectas = 0;
    xpGanado = 0;
    
    // Cambiar a vista de ejercicio
    document.getElementById('materias-section').style.display = 'none';
    document.getElementById('ruta-section').style.display = 'none';
    document.getElementById('ejercicio-section').style.display = 'block';
    
    // Mostrar primera pregunta
    mostrarPregunta();
}

// =====================================================
// MOSTRAR PREGUNTA
// =====================================================

function mostrarPregunta() {
    if (indicePreguntaActual >= preguntasActuales.length) {
        finalizarEjercicio();
        return;
    }
    
    const pregunta = preguntasActuales[indicePreguntaActual];
    console.log('❓ Mostrando pregunta:', pregunta.pregunta);
    
    // Actualizar progreso
    const progreso = indicePreguntaActual + 1;
    document.getElementById('progreso-fill').style.width = 
        `${(progreso / preguntasActuales.length) * 100}%`;
    document.getElementById('progreso-texto').textContent = 
        `${progreso}/${preguntasActuales.length}`;
    
    // Actualizar pregunta
    document.getElementById('pregunta-texto').textContent = pregunta.pregunta;
    
    // Mostrar opciones
    const opcionesContainer = document.getElementById('opciones-container');
    opcionesContainer.innerHTML = '';
    
    pregunta.opciones.forEach((opcion, index) => {
        const opcionDiv = document.createElement('div');
        opcionDiv.className = 'opcion';
        opcionDiv.textContent = opcion.texto;
        opcionDiv.dataset.opcionId = opcion.id_opcion;
        opcionDiv.dataset.correcta = opcion.es_correcta;
        
        opcionDiv.addEventListener('click', () => seleccionarOpcion(opcionDiv, opcion));
        
        opcionesContainer.appendChild(opcionDiv);
    });
    
    // Deshabilitar botón siguiente
    document.getElementById('btn-siguiente').disabled = true;
}

// =====================================================
// SELECCIONAR OPCIÓN
// =====================================================

function seleccionarOpcion(opcionDiv, opcion) {
    console.log('✓ Opción seleccionada:', opcion.texto);
    
    // Deshabilitar otras opciones
    document.querySelectorAll('.opcion').forEach(o => {
        o.style.pointerEvents = 'none';
        o.style.opacity = '0.6';
    });
    
    // Marcar como seleccionada
    opcionDiv.classList.add('seleccionada');
    
    // Verificar respuesta
    if (opcion.es_correcta) {
        opcionDiv.classList.add('correcta');
        respuestasCorrectas++;
        xpGanado += 10;
        mostrarResultado(true, 'Correcto!');
    } else {
        opcionDiv.classList.add('incorrecta');
        
        // Mostrar la respuesta correcta
        document.querySelectorAll('.opcion').forEach(o => {
            if (o.dataset.correcta === 'true') {
                o.classList.add('correcta');
            }
        });
        
        mostrarResultado(false, 'Intenta de nuevo');
    }
    
    // Habilitar botón siguiente después de 1.5 segundos
    setTimeout(() => {
        document.getElementById('btn-siguiente').disabled = false;
    }, 1500);
}

// =====================================================
// MOSTRAR RESULTADO EN MODAL
// =====================================================

function mostrarResultado(esCorrect, titulo) {
    const modal = document.getElementById('modal-resultado');
    const icon = document.getElementById('resultado-icon');
    const tituloElement = document.getElementById('resultado-titulo');
    const mensaje = document.getElementById('resultado-mensaje');
    const xpElement = document.getElementById('resultado-xp');
    
    if (esCorrect) {
        icon.textContent = '✓';
        icon.style.color = '#4CAF50';
        tituloElement.textContent = '¡Correcto!';
        mensaje.textContent = 'Excelente trabajo';
        xpElement.textContent = '+10 XP';
        xpElement.style.color = '#FF8C42';
    } else {
        icon.textContent = '✗';
        icon.style.color = '#E74C3C';
        tituloElement.textContent = 'Incorrecto';
        mensaje.textContent = 'No te preocupes, intenta de nuevo';
        xpElement.textContent = '0 XP';
        xpElement.style.color = '#ccc';
    }
    
    // Mostrar modal
    modal.classList.add('active');
    
    // Cerrar modal automáticamente después de 2 segundos
    setTimeout(() => {
        modal.classList.remove('active');
    }, 2000);
}

// =====================================================
// FINALIZAR EJERCICIO
// =====================================================

function finalizarEjercicio() {
    console.log('🎉 Ejercicio finalizado');
    console.log('Respuestas correctas:', respuestasCorrectas, 'de', preguntasActuales.length);
    console.log('XP ganado:', xpGanado);
    
    // Mostrar resumen
    const porcentaje = (respuestasCorrectas / preguntasActuales.length) * 100;
    
    let mensaje = `¡Excelente! Obtuviste ${respuestasCorrectas}/${preguntasActuales.length} respuestas correctas (${Math.round(porcentaje)}%)`;
    
    if (porcentaje < 50) {
        mensaje = `Obtuviste ${respuestasCorrectas}/${preguntasActuales.length} respuestas correctas. ¡Sigue practicando!`;
    }
    
    alert(mensaje + `\n\n+${xpGanado} XP`);
    
    // Volver a materias
    volverAMaterias();
}

// =====================================================
// EVENT LISTENERS
// =====================================================

function configurarEventListeners() {
    // Botón siguiente
    document.getElementById('btn-siguiente').addEventListener('click', () => {
        indicePreguntaActual++;
        mostrarPregunta();
    });
    
    // Botón volver (en ruta)
    document.getElementById('back-btn').addEventListener('click', volverAMaterias);
    
    // Botón volver (en ejercicio)
    document.getElementById('back-btn-ejercicio').addEventListener('click', volverARuta);
    
    // Menú usuario
    document.getElementById('user-menu-btn').addEventListener('click', () => {
        const menu = document.getElementById('dropdown-menu');
        menu.classList.toggle('active');
    });
    
    // Logout
    document.getElementById('logout-btn').addEventListener('click', () => {
        if (confirm('¿Estás seguro de que quieres cerrar sesión?')) {
            logout();
        }
    });
    
    // Cerrar dropdown al hacer clic en otro lado
    document.addEventListener('click', (e) => {
        const menu = document.getElementById('dropdown-menu');
        const btn = document.getElementById('user-menu-btn');
        
        if (!menu.contains(e.target) && !btn.contains(e.target)) {
            menu.classList.remove('active');
        }
    });
}

// =====================================================
// FUNCIONES DE NAVEGACIÓN
// =====================================================

function volverAMaterias() {
    console.log('← Volviendo a materias');
    document.getElementById('materias-section').style.display = 'block';
    document.getElementById('ruta-section').style.display = 'none';
    document.getElementById('ejercicio-section').style.display = 'none';
}

function volverARuta() {
    console.log('← Volviendo a ruta');
    document.getElementById('ejercicio-section').style.display = 'none';
    document.getElementById('ruta-section').style.display = 'block';
}

// =====================================================
// LOGOUT
// =====================================================

function logout() {
    localStorage.removeItem('token');
    localStorage.removeItem('usuario');
    window.location.href = 'login.html';
}

// =====================================================
// MOSTRAR ERROR
// =====================================================

function mostrarError(mensaje) {
    alert('❌ ' + mensaje);
}

console.log('🎮 Dashboard.js cargado correctamente');
