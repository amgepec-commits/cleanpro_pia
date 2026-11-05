from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

from src.domain.errors import DomainError

app = FastAPI(
    title="API de Gestión de Operaciones - PIA",
    description="API REST desarrollada para el Producto Integrador de Aprendizaje (Gestión de Actores, Catálogos y Operaciones).",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
)

@app.exception_handler(DomainError)
async def manejar_error_de_dominio(request: Request, exc: DomainError):
    """400 validación, 404 no encontrado, 409 conflicto/transición, 422 regla de negocio."""
    return JSONResponse(status_code=exc.status_code, content={"detail": str(exc)})


# Importar y registrar los routers (asegúrate de crear los routers correspondientes)
from src.api.routers import actores, catalogo, operaciones

app.include_router(actores.router, prefix="/api/actores", tags=["Actores"])
app.include_router(catalogo.router, prefix="/api/catalogo", tags=["Catálogo"])
app.include_router(operaciones.router, prefix="/api/operaciones", tags=["Operaciones"])


@app.get("/", tags=["Root"])
def read_root():
    return {
        "mensaje": "Bienvenido a la API del PIA",
        "documentacion_swagger": "/docs",
        "documentacion_redoc": "/redoc",
    }