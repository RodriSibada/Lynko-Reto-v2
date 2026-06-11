# 🚀 INICIO RÁPIDO - Lynko Auth + BD

## 1️⃣ Crear tabla en PostgreSQL (5 min)

En **pgAdmin**:
- Click derecho en base de datos `LynkoReto` → `Query Tool`
- Pega contenido de `create_users_table.sql`
- Ejecuta (Ctrl+Enter)

## 2️⃣ Instalar dependencias Python (2 min)

```bash
python -m venv venv
venv\Scripts\activate  # Windows
# source venv/bin/activate  # Linux/Mac
pip install -r requirements.txt
```

## 3️⃣ Verificar conexión a BD en database.py

Confirma que `DATABASE_URL` coincide con tu PostgreSQL:
```python
DATABASE_URL = "postgresql://postgres:password@localhost:5432/LynkoReto"
```

-- En la base de datos NUEVA (lynko_nueva), ejecuta:

CREATE SCHEMA IF NOT EXISTS public;

CREATE TABLE IF NOT EXISTS public.users (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    email VARCHAR(255) NOT NULL UNIQUE,
    password VARCHAR(255) NOT NULL,
    is_active BOOLEAN DEFAULT TRUE,
    xp INTEGER DEFAULT 0,
    level INTEGER DEFAULT 1,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_users_email ON public.users(email);

CREATE OR REPLACE FUNCTION update_updated_at()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

DROP TRIGGER IF EXISTS trigger_update_users_updated_at ON public.users;
CREATE TRIGGER trigger_update_users_updated_at
BEFORE UPDATE ON public.users
FOR EACH ROW
EXECUTE FUNCTION update_updated_at();

## 4️⃣ Ejecutar servidor FastAPI (1 min)

```bash
python main.py
```

Verifica en navegador: http://localhost:8000/health → `{"status":"ok"}`

## 5️⃣ Probar login/registro

**Registro:** http://localhost:8000/static/registro.html
**Login:** http://localhost:8000/static/login.html

## 📊 Ver datos en pgAdmin

- `LynkoReto` → `Schemas` → `public` → `Tables` → `users`
- Click derecho → `View/Edit Data` → `All Rows`

## 🧪 API Testing (Swagger)

http://localhost:8000/docs

Prueba endpoints:
- `POST /api/auth/register` - Registrar
- `POST /api/auth/login` - Iniciar sesión

## ⚠️ Problemas comunes

| Error | Solución |
|-------|----------|
| `ModuleNotFoundError` | Activa venv: `venv\Scripts\activate` |
| `Connection refused` | PostgreSQL no está corriendo |
| `CORS error` | Normal, el servidor tiene CORS habilitado |
| `Email ya registrado` | Usa otro email o borra en pgAdmin |

## 📁 Archivos importantes

- `database.py` - Conexión BD
- `models.py` - Modelo User
- `auth_controller.py` - Lógica auth
- `main.py` - Servidor FastAPI
- `login.html` / `registro.html` - Frontend

## ✅ Checklist

- [ ] PostgreSQL corriendo
- [ ] Base de datos `LynkoReto` existe
- [ ] Tabla `users` creada
- [ ] Python venv activado
- [ ] Dependencias instaladas (`pip install -r requirements.txt`)
- [ ] Servidor corriendo (`python main.py`)
- [ ] Health check funciona (http://localhost:8000/health)
- [ ] Puedo registrar usuario en registro.html
- [ ] Puedo iniciar sesión en login.html
- [ ] Usuario aparece en pgAdmin

---

