# 🔗 Guía de Integración: Auth → Dashboard

## Vista general del flujo

```
[login.html] → POST /api/auth/login → Recibe token + user data
      ↓
Guarda en localStorage
      ↓
[Redirige a inicio_lynko.html]
      ↓
dashboard-auth-helper.js verifica token
      ↓
Carga dashboard con datos del usuario
```

## Paso 1: Agregar script de autenticación al dashboard

En `inicio_lynko.html`, antes de cerrar `</head>`:

```html
<script src="dashboard-auth-helper.js"></script>
```

## Paso 2: Mostrar datos del usuario en el navbar

Reemplaza tu navbar con:

```html
<nav class="navbar">
    <div class="navbar-left">
        <h2>🎯 Lynko</h2>
    </div>
    
    <div class="navbar-stats">
        <div class="stat">
            <span class="label">Nombre:</span>
            <span id="userName">Cargando...</span>
        </div>
        <div class="stat">
            <span class="label">Nivel:</span>
            <span id="userLevel">-</span>
        </div>
        <div class="stat">
            <span class="label">XP:</span>
            <span id="userXP">-</span>
        </div>
    </div>
    
    <div class="navbar-right">
        <button id="logoutBtn" class="btn-logout">Cerrar sesión</button>
    </div>
</nav>
```

## Paso 3: Agregar CSS para el navbar

```css
.navbar {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 15px 30px;
    background: linear-gradient(135deg, #FF7A00, #E66E00);
    color: white;
    box-shadow: 0 4px 12px rgba(0,0,0,0.15);
}

.navbar-stats {
    display: flex;
    gap: 30px;
    flex: 1;
    justify-content: center;
}

.stat {
    display: flex;
    flex-direction: column;
    align-items: center;
    gap: 5px;
}

.stat .label {
    font-size: 12px;
    opacity: 0.8;
    font-weight: 600;
}

.stat span:not(.label) {
    font-size: 18px;
    font-weight: 800;
}

.btn-logout {
    background: rgba(255,255,255,0.2);
    color: white;
    border: 2px solid white;
    padding: 8px 16px;
    border-radius: 20px;
    cursor: pointer;
    font-weight: 700;
    transition: all 0.2s;
}

.btn-logout:hover {
    background: rgba(255,255,255,0.3);
    transform: translateY(-2px);
}
```

## Paso 4: Actualizar evento del botón de logout

Agrega al final de `dashboard.js`:

```javascript
// Logout
document.getElementById("logoutBtn").addEventListener("click", () => {
    LynkoAuth.logout();
});
```

## Paso 5: Proteger acceso al dashboard

Al inicio de `dashboard.js`, agrega:

```javascript
// Verificar autenticación
document.addEventListener("DOMContentLoaded", () => {
    LynkoAuth.checkAuth();      // Redirige a login si no está autenticado
    LynkoAuth.updateDashboard(); // Carga datos del usuario
});
```

## Paso 6: Obtener datos del usuario para los quizzes

Cuando el usuario responda un quiz y gane XP, actualizar datos:

```javascript
async function submitQuiz(answers) {
    // Validar respuestas...
    const xpEarned = 100; // O lo que sea
    
    // Obtener usuario actual
    const user = LynkoAuth.getUser();
    console.log("Usuario actual:", user);
    
    // Actualizar en localStorage (temporal)
    user.xp = (user.xp || 0) + xpEarned;
    user.level = Math.floor(user.xp / 500) + 1;
    localStorage.setItem("user", JSON.stringify(user));
    
    // Actualizar dashboard
    LynkoAuth.updateDashboard();
    
    // TODO: Enviar a API para guardar en BD
    // await LynkoAuth.authenticatedFetch("http://localhost:8000/api/users/xp", {
    //     method: "POST",
    //     body: JSON.stringify({ xp_amount: xpEarned })
    // });
}
```

## Archivo HTML completo 

```html
<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Lynko Dashboard</title>
    <link rel="stylesheet" href="css/dashboard.css">
    <script src="dashboard-auth-helper.js"></script>
</head>
<body>
    <nav class="navbar">
        <div class="navbar-left">
            <h2>🎯 Lynko</h2>
        </div>
        
        <div class="navbar-stats">
            <div class="stat">
                <span class="label">Hola,</span>
                <span id="userName">Cargando...</span>
            </div>
            <div class="stat">
                <span class="label">Nivel</span>
                <span id="userLevel">1</span>
            </div>
            <div class="stat">
                <span class="label">XP</span>
                <span id="userXP">0</span>
            </div>
        </div>
        
        <div class="navbar-right">
            <button id="logoutBtn" class="btn-logout">Cerrar sesión</button>
        </div>
    </nav>

    <div class="dashboard">
        <!-- Contenido existente del dashboard -->
    </div>

    <script src="js/dashboard.js"></script>
    <script>
        // Proteger acceso
        document.addEventListener("DOMContentLoaded", () => {
            LynkoAuth.checkAuth();
            LynkoAuth.updateDashboard();
        });
    </script>
</body>
</html>
```

## Prueba de integración

1. ✅ Abre `login.html`
2. ✅ Registra o inicia sesión
3. ✅ Deberías ser redirigido a `inicio_lynko.html`
4. ✅ Deberías ver tu nombre, nivel y XP en el navbar
5. ✅ Haz click en "Cerrar sesión" - deberías volver a login.html

## Variables disponibles en localStorage

Después de login/registro:

```javascript
// Token JWT
const token = localStorage.getItem("token");
// "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."

// Datos del usuario
const user = JSON.parse(localStorage.getItem("user"));
// {
//   "id": 1,
//   "name": "Juan Pérez",
//   "email": "juan@example.com",
//   "is_active": true,
//   "xp": 0,
//   "level": 1,
//   "created_at": "2026-06-09T..."
// }
```

## Próximos pasos

1. Crear endpoint `POST /api/users/xp` para actualizar XP en BD
2. Crear endpoint `PUT /api/users/profile` para actualizar perfil
3. Conectar quizzes con el sistema de XP
4. Agregar historial de actividades del usuario

---

**¿Necesitas ayuda?** Revisa `dashboard-auth-helper.js` para ver todas las funciones disponibles.
