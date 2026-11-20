from fastapi import FastAPI

app = FastAPI()


@app.get("/", status_code=200)
def raiz():
    """Devuelve un mensaje de bienvenida de la API de la biblioteca."""
    return {"mensaje": "API de la biblioteca"}
