import logging

from fastapi import FastAPI, HTTPException

from datos import cargar_libros, guardar_libros, obtener_siguiente_id
from schemas import LibroEntrada, LibroPatch, LibroSalida

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(name)s - %(message)s",
)
logger = logging.getLogger(__name__)

app = FastAPI()

libros: list[dict] = sorted(cargar_libros(), key=lambda libro: int(libro["id"]))
siguiente_id: int = obtener_siguiente_id(libros)


def _buscar_indice_por_id(libro_id: int) -> int | None:
    """Devuelve el índice del libro con el ID indicado o None si no existe."""
    for indice, libro in enumerate(libros):
        if int(libro["id"]) == libro_id:
            return indice
    return None


@app.get("/", status_code=200, summary="Mensaje de bienvenida")
def raiz():
    """Devuelve un mensaje de bienvenida de la API de la biblioteca."""
    return {"mensaje": "API de la biblioteca"}


@app.get(
    "/libros",
    response_model=list[LibroSalida],
    status_code=200,
    summary="Listar libros",
)
def listar_libros(
    autor: str | None = None,
    disponible: bool | None = None,
    desde: int = 0,
    limite: int = 100,
):
    """Devuelve la lista de libros filtrada, ordenada por ID y paginada."""
    resultado = sorted(libros, key=lambda libro: int(libro["id"]))

    if autor is not None:
        autor_norm = autor.strip().lower()
        resultado = [
            libro for libro in resultado if libro["autor"].strip().lower() == autor_norm
        ]

    if disponible is not None:
        resultado = [libro for libro in resultado if libro["disponible"] == disponible]

    return resultado[desde : desde + limite]


@app.get(
    "/libros/buscar",
    response_model=list[LibroSalida],
    status_code=200,
    summary="Buscar libros por texto",
)
def buscar_libros(texto: str):
    """Busca libros cuyo título o autor contenga el texto indicado."""
    texto_norm = texto.lower()
    resultado = [
        libro
        for libro in sorted(libros, key=lambda item: int(item["id"]))
        if texto_norm in libro["titulo"].lower() or texto_norm in libro["autor"].lower()
    ]
    return resultado


@app.get(
    "/libros/estadisticas",
    status_code=200,
    summary="Obtener estadísticas de libros",
)
def obtener_estadisticas():
    """Devuelve el total de libros, los disponibles y los prestados."""
    total = len(libros)
    disponibles = sum(1 for libro in libros if libro["disponible"])
    prestados = sum(1 for libro in libros if not libro["disponible"])
    return {
        "total": total,
        "disponibles": disponibles,
        "prestados": prestados,
    }


@app.post(
    "/libros",
    response_model=LibroSalida,
    status_code=201,
    summary="Crear un libro",
)
def crear_libro(libro: LibroEntrada):
    """Crea un nuevo libro validando que no exista duplicado por título y autor."""
    global siguiente_id

    titulo_norm = libro.titulo.strip().lower()
    autor_norm = libro.autor.strip().lower()
    for existente in libros:
        if (
            existente["titulo"].strip().lower() == titulo_norm
            and existente["autor"].strip().lower() == autor_norm
        ):
            logger.warning(
                "Intento de crear libro duplicado: '%s' de '%s'",
                libro.titulo,
                libro.autor,
            )
            raise HTTPException(
                status_code=409,
                detail="Ya existe un libro con ese titulo y autor",
            )

    nuevo_id = max(siguiente_id, obtener_siguiente_id(libros))
    siguiente_id = nuevo_id + 1

    nuevo_libro = {"id": nuevo_id, **libro.model_dump()}
    libros.append(nuevo_libro)
    libros.sort(key=lambda item: int(item["id"]))
    guardar_libros(libros)
    logger.info("Libro creado con ID %s: '%s'", nuevo_id, libro.titulo)
    return nuevo_libro


@app.get(
    "/libros/{id}",
    response_model=LibroSalida,
    status_code=200,
    summary="Obtener un libro por ID",
)
def obtener_libro(id: int):
    """Devuelve un libro por su ID o 404 si no existe."""
    indice = _buscar_indice_por_id(id)
    if indice is None:
        logger.warning("Libro no encontrado al consultar ID %s", id)
        raise HTTPException(status_code=404, detail="Libro no encontrado")
    return libros[indice]


@app.put(
    "/libros/{id}",
    response_model=LibroSalida,
    status_code=200,
    summary="Reemplazar un libro por ID",
)
def actualizar_libro(id: int, datos: LibroEntrada):
    """Reemplaza todos los campos de un libro existente conservando su ID."""
    indice = _buscar_indice_por_id(id)
    if indice is None:
        logger.warning("Libro no encontrado al reemplazar ID %s", id)
        raise HTTPException(status_code=404, detail="Libro no encontrado")

    actualizado = {"id": id, **datos.model_dump()}
    libros[indice] = actualizado
    libros.sort(key=lambda item: int(item["id"]))
    guardar_libros(libros)
    logger.info("Libro reemplazado con ID %s", id)
    return actualizado


@app.patch(
    "/libros/{id}",
    response_model=LibroSalida,
    status_code=200,
    summary="Actualizar parcialmente un libro",
)
def modificar_libro(id: int, cambios: LibroPatch):
    """Actualiza parcialmente los campos enviados de un libro existente."""
    indice = _buscar_indice_por_id(id)
    if indice is None:
        logger.warning("Libro no encontrado al modificar ID %s", id)
        raise HTTPException(status_code=404, detail="Libro no encontrado")

    campos_actualizados = {
        clave: valor
        for clave, valor in cambios.model_dump(exclude_unset=True).items()
        if valor is not None
    }
    if campos_actualizados:
        libros[indice] = {**libros[indice], **campos_actualizados}
        guardar_libros(libros)
        logger.info("Libro modificado parcialmente con ID %s", id)

    return libros[indice]


@app.delete(
    "/libros/{id}",
    status_code=204,
    summary="Eliminar un libro por ID",
)
def eliminar_libro(id: int):
    """Elimina un libro por su ID devolviendo 204 sin cuerpo."""
    indice = _buscar_indice_por_id(id)
    if indice is None:
        logger.warning("Libro no encontrado al eliminar ID %s", id)
        raise HTTPException(status_code=404, detail="Libro no encontrado")

    libros.pop(indice)
    guardar_libros(libros)
    logger.info("Libro eliminado con ID %s", id)
