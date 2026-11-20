import json
from pathlib import Path

RUTA_ARCHIVO = Path(__file__).resolve().parent / "datos" / "libros.json"


def cargar_libros() -> list[dict]:
    """Carga la lista de libros desde el archivo JSON.

    Si el archivo no existe, está vacío, está dañado o no contiene una lista,
    devuelve una lista vacía.
    """
    try:
        contenido = RUTA_ARCHIVO.read_text(encoding="utf-8")
        if not contenido.strip():
            return []
        datos = json.loads(contenido)
    except (FileNotFoundError, json.JSONDecodeError, OSError, ValueError):
        return []

    if not isinstance(datos, list):
        return []
    return datos


def guardar_libros(libros: list[dict]) -> None:
    """Guarda la lista de libros en el archivo JSON creando la carpeta si no existe."""
    RUTA_ARCHIVO.parent.mkdir(parents=True, exist_ok=True)
    with RUTA_ARCHIVO.open("w", encoding="utf-8") as archivo:
        json.dump(libros, archivo, indent=2, ensure_ascii=False)


def obtener_siguiente_id(libros: list[dict]) -> int:
    """Devuelve el próximo ID entero disponible sin reutilizar IDs eliminados."""
    if not libros:
        return 1
    return max(int(libro["id"]) for libro in libros) + 1
