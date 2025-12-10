# Pasos para Deploy en PythonAnywhere

## 1. Pull del Código

```bash
cd ~/MatchDeportivo
workon matchdeportivo
git fetch origin
git reset --hard origin/develop
```

## 2. Crear archivo .env

```bash
nano .env
```

Copiar contenido de `.env.pythonanywhere` y:
- Generar nueva SECRET_KEY
- Verificar credenciales de base de datos

## 3. Instalar Dependencias

```bash
pip install -r requirements.txt
```

## 4. Aplicar Migraciones

```bash
python manage.py migrate
```

## 5. Crear Superusuario

```bash
python manage.py createsuperuser
```

## 6. Recolectar Estáticos

```bash
python manage.py collectstatic --noinput
```

## 7. Reload Web App

Dashboard → Web → Reload (botón verde)

## 8. Probar

Ir a: https://SAYOzzz.pythonanywhere.com

---

## Comando Todo-en-Uno

```bash
cd ~/MatchDeportivo && \
workon matchdeportivo && \
git fetch origin && \
git reset --hard origin/develop && \
pip install -r requirements.txt && \
python manage.py migrate && \
python manage.py collectstatic --noinput && \
echo "✅ Listo! Ahora reload web app desde dashboard"
```

**Nota:** Asegúrate de crear el archivo .env ANTES de ejecutar los comandos.
