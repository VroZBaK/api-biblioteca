import json
from pathlib import Path

RUTA_ARCHIVO = Path(__file__).resolve().parent / "datos" / "libros.json"


def cargar_libros() -> list[dict]:
    """Lee los libros del JSON o devuelve [] si falta o está roto."""
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
    """Guarda los libros en el JSON (crea la carpeta si hace falta)."""
    RUTA_ARCHIVO.parent.mkdir(parents=True, exist_ok=True)
    with RUTA_ARCHIVO.open("w", encoding="utf-8") as archivo:
        json.dump(libros, archivo, indent=2, ensure_ascii=False)


def obtener_siguiente_id(libros: list[dict]) -> int:
    """Calcula el próximo ID sin repetir los ya borrados."""
    if not libros:
        return 1
    return max(int(libro["id"]) for libro in libros) + 1
