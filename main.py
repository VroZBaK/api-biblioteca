from fastapi import FastAPI, HTTPException

from datos import cargar_libros, guardar_libros, obtener_siguiente_id
from schemas import LibroEntrada, LibroPatch, LibroSalida

app = FastAPI()

libros: list[dict] = sorted(cargar_libros(), key=lambda libro: int(libro["id"]))
siguiente_id: int = obtener_siguiente_id(libros)


def _buscar_indice_por_id(libro_id: int) -> int | None:
    """Devuelve el índice del libro con el ID indicado o None si no existe."""
    for indice, libro in enumerate(libros):
        if int(libro["id"]) == libro_id:
            return indice
    return None


@app.get("/", status_code=200)
def raiz():
    """Devuelve un mensaje de bienvenida de la API de la biblioteca."""
    return {"mensaje": "API de la biblioteca"}


@app.get("/libros", response_model=list[LibroSalida], status_code=200)
def listar_libros():
    """Devuelve la lista de libros ordenada por ID de menor a mayor."""
    return sorted(libros, key=lambda libro: int(libro["id"]))


@app.post("/libros", response_model=LibroSalida, status_code=201)
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
    return nuevo_libro


@app.get("/libros/{id}", response_model=LibroSalida, status_code=200)
def obtener_libro(id: int):
    """Devuelve un libro por su ID o 404 si no existe."""
    indice = _buscar_indice_por_id(id)
    if indice is None:
        raise HTTPException(status_code=404, detail="Libro no encontrado")
    return libros[indice]


@app.put("/libros/{id}", response_model=LibroSalida, status_code=200)
def actualizar_libro(id: int, datos: LibroEntrada):
    """Reemplaza todos los campos de un libro existente conservando su ID."""
    indice = _buscar_indice_por_id(id)
    if indice is None:
        raise HTTPException(status_code=404, detail="Libro no encontrado")

    actualizado = {"id": id, **datos.model_dump()}
    libros[indice] = actualizado
    libros.sort(key=lambda item: int(item["id"]))
    guardar_libros(libros)
    return actualizado


@app.patch("/libros/{id}", response_model=LibroSalida, status_code=200)
def modificar_libro(id: int, cambios: LibroPatch):
    """Actualiza parcialmente los campos enviados de un libro existente."""
    indice = _buscar_indice_por_id(id)
    if indice is None:
        raise HTTPException(status_code=404, detail="Libro no encontrado")

    campos_actualizados = {
        clave: valor
        for clave, valor in cambios.model_dump(exclude_unset=True).items()
        if valor is not None
    }
    if campos_actualizados:
        libros[indice] = {**libros[indice], **campos_actualizados}
        guardar_libros(libros)

    return libros[indice]


@app.delete("/libros/{id}", status_code=204)
def eliminar_libro(id: int):
    """Elimina un libro por su ID devolviendo 204 sin cuerpo."""
    indice = _buscar_indice_por_id(id)
    if indice is None:
        raise HTTPException(status_code=404, detail="Libro no encontrado")

    libros.pop(indice)
    guardar_libros(libros)
