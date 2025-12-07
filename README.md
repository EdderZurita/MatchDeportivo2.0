# MatchDeportivo 🏃‍♂️⚽

Plataforma web para conectar personas que desean realizar actividades deportivas, con sistema de geolocalización, notificaciones y gestión de participantes.

---

## 🚀 Instalación y Configuración

### Requisitos Previos

- Python 3.8+
- MySQL (XAMPP para desarrollo local)
- pip (gestor de paquetes de Python)

### 1. Clonar el Repositorio

```bash
git clone https://github.com/Maxcsay/MatchDeportivo.git
cd MatchDeportivo
```

### 2. Crear Entorno Virtual

```bash
# Crear entorno virtual
python -m venv venv

# Activar entorno virtual
# En Windows:
venv\Scripts\activate
# En Linux/Mac:
source venv/bin/activate
```

### 3. Instalar Dependencias

```bash
pip install -r requirements.txt
```

### 4. Configurar Variables de Entorno

#### Para Desarrollo Local (XAMPP)

1. Copia el archivo de ejemplo:
   ```bash
   copy .env.example .env
   ```

2. El archivo `.env` ya viene preconfigurado para desarrollo local con XAMPP:
   ```env
   ENVIRONMENT=development
   SECRET_KEY=django-insecure-local-dev-key-change-in-production-12345678
   DEBUG=True
   DB_NAME=match_deportivo2_pruebas_locales
   DB_USER=root
   DB_PASSWORD=
   DB_HOST=localhost
   ALLOWED_HOSTS=localhost,127.0.0.1
   ```

3. **Importante**: Asegúrate de tener XAMPP corriendo y la base de datos `match_deportivo2_pruebas_locales` creada.

#### Para Producción (PythonAnywhere)

Modifica el archivo `.env` con las credenciales de producción:

```env
ENVIRONMENT=production
SECRET_KEY=tu-secret-key-de-produccion-super-segura
DEBUG=False
DB_NAME=SAYOzzz$default
DB_USER=SAYOzzz
DB_PASSWORD=tu-password-de-produccion
DB_HOST=SAYOzzz.mysql.pythonanywhere-services.com
ALLOWED_HOSTS=SAYOzzz.pythonanywhere.com
```

### 5. Configurar Base de Datos

#### Crear Base de Datos en XAMPP

1. Abre XAMPP y arranca MySQL
2. Abre phpMyAdmin (http://localhost/phpmyadmin)
3. Crea una nueva base de datos llamada `match_deportivo2_pruebas_locales`
4. Charset: `utf8mb4_general_ci`

#### Ejecutar Migraciones

```bash
python manage.py migrate
```

### 6. Crear Superusuario

```bash
python manage.py createsuperuser
```

### 7. Ejecutar Servidor de Desarrollo

```bash
python manage.py runserver
```

Abre tu navegador en: http://localhost:8000

---

## 📁 Estructura del Proyecto

```
MatchDeportivo/
├── MatchDeportivo/          # Configuración del proyecto
│   ├── settings.py          # Configuración principal
│   ├── urls.py              # URLs principales
│   └── wsgi.py
├── MatchDeportivoAPP/       # Aplicación principal
│   ├── models.py            # Modelos (Perfil, Actividad, Notificacion, Log)
│   ├── views.py             # Vistas y lógica de negocio
│   ├── forms.py             # Formularios
│   ├── admin.py             # Configuración del admin
│   ├── templates/           # Plantillas HTML
│   │   ├── actividades/
│   │   ├── sesion/
│   │   ├── usuarios/
│   │   └── administracion/
│   └── static/              # Archivos estáticos
│       └── img/
├── .env                     # Variables de entorno (NO SUBIR A GIT)
├── .env.example             # Plantilla de variables de entorno
├── requirements.txt         # Dependencias del proyecto
└── manage.py
```

---

## 🔑 Funcionalidades Principales

### Autenticación
- ✅ Registro de usuarios
- ✅ Login con email
- ✅ Recuperación de contraseña
- ✅ Perfiles de usuario personalizables

### Actividades Deportivas
- ✅ Crear actividades con geolocalización
- ✅ Buscar actividades por deporte y distancia
- ✅ Unirse/Salir de actividades
- ✅ Sistema de cupos
- ✅ Gestión de participantes (organizador)
- ✅ Editar/Eliminar actividades propias

### Geolocalización
- ✅ Cálculo de distancia con fórmula de Haversine
- ✅ Filtrado por radio de búsqueda
- ✅ Ordenamiento por proximidad

### Notificaciones
- ✅ Notificaciones automáticas de actividades cercanas
- ✅ Confirmación al unirse a actividad
- ✅ Sistema de notificaciones leídas/no leídas

### Administración
- ✅ Panel de administración de Django
- ✅ Sistema de logs de auditoría
- ✅ Gestión de usuarios

---

## 🛠️ Comandos Útiles

### Migraciones

```bash
# Crear migraciones
python manage.py makemigrations

# Aplicar migraciones
python manage.py migrate

# Ver estado de migraciones
python manage.py showmigrations
```

### Archivos Estáticos

```bash
# Recolectar archivos estáticos para producción
python manage.py collectstatic
```

### Base de Datos

```bash
# Crear respaldo de la base de datos
python manage.py dumpdata > backup.json

# Restaurar desde respaldo
python manage.py loaddata backup.json
```

### Shell de Django

```bash
# Abrir shell interactivo
python manage.py shell
```

---

## 🔒 Seguridad

### Variables de Entorno

**NUNCA** subas el archivo `.env` a Git. Este archivo contiene información sensible como:
- SECRET_KEY
- Credenciales de base de datos
- Configuraciones de producción

El archivo `.env` ya está incluido en `.gitignore`.

### Generar Nueva SECRET_KEY

```bash
python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
```

---

## 🌿 Flujo de Trabajo con Git

### Ramas

- `main` - Rama de producción (protegida)
- `develop` - Rama de desarrollo
- `feature/*` - Ramas de funcionalidades

### Crear Nueva Funcionalidad

```bash
# Actualizar develop
git checkout develop
git pull origin develop

# Crear rama de feature
git checkout -b feature/nombre-funcionalidad

# Hacer cambios y commits
git add .
git commit -m "feat: descripción del cambio"

# Subir cambios
git push origin feature/nombre-funcionalidad
```

---

## 📝 Tecnologías Utilizadas

- **Backend**: Django 5.1
- **Base de Datos**: MySQL
- **Frontend**: HTML, Bootstrap 5, JavaScript
- **Geolocalización**: Fórmula de Haversine
- **Despliegue**: PythonAnywhere

---

## 👥 Contribuidores

- Maxcsay
- EdderZurita

---

## 📄 Licencia

Este proyecto es privado y está en desarrollo.

---

## 🐛 Reportar Problemas

Si encuentras algún bug o tienes sugerencias, por favor crea un issue en GitHub.

---

## 📞 Contacto

Para más información, contacta al equipo de desarrollo.
