# API de la Biblioteca

API REST desarrollada con Python y FastAPI para gestionar el catálogo de libros de una biblioteca con persistencia en archivo JSON (`datos/libros.json`).

## Funcionalidades

- Operaciones CRUD completas sobre `/libros` (`GET`, `POST`, `PUT`, `PATCH`, `DELETE`).
- Validación de datos con Pydantic (`LibroEntrada`, `LibroSalida`, `LibroPatch`).
- Filtrado por `autor` y `disponible`, y paginación con `desde` y `limite`.
- Búsqueda de libros por texto en título o autor (`/libros/buscar?texto=...`).
- Estadísticas del catálogo en `/libros/estadisticas`.

## Instalación

1. Crear y activar el entorno virtual:

```bash
python -m venv venv
```

En Windows (PowerShell):

```powershell
.\venv\Scripts\Activate.ps1
```

2. Instalar las dependencias:

```bash
pip install -r requirements.txt
```

## Ejecución

Para levantar el servidor en modo desarrollo:

```bash
fastapi dev main.py
```

O alternativamente con Uvicorn:

```bash
uvicorn main:app --reload
```

La documentación interactiva estará disponible en `http://127.0.0.1:8000/docs`.
