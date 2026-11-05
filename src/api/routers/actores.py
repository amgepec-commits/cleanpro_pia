from pathlib import Path
from fastapi import APIRouter, HTTPException
import pandas as pd

router = APIRouter()


def cargar_actores():
  # Buscar el archivo actores.csv subiendo niveles o buscando en el directorio actual y carpetas padre
  directorio_actual = Path(__file__).resolve().parent

  # Intentar buscar en varias rutas posibles (desde src/api/routers hasta la raíz)
  posibles_rutas = [
      directorio_actual / "actores.csv",
      directorio_actual.parent / "actores.csv",
      directorio_actual.parent.parent / "actores.csv",
      Path("actores.csv"),  # Directorio de trabajo actual
      Path("/home/bard/actores.csv"),  # Ruta absoluta del entorno actual si aplica
  ]

  df = None
  for ruta in posibles_rutas:
    if ruta.exists():
      try:
        df = pd.read_csv(ruta)
        break
      except Exception:
        continue

  if df is None or df.empty:
    return []
  return df.to_dict(orient="records")


@router.get("/", summary="Obtener todos los actores")
def listar_actores():
  actores = cargar_actores()
  return {"total": len(actores), "data": actores}


@router.get("/{actor_id}", summary="Obtener actor por ID")
def obtener_actor(actor_id: str):
  actores = cargar_actores()
  actor = next((a for a in actores if str(a.get("actor_id")) == actor_id), None)
  if not actor:
    raise HTTPException(status_code=404, detail="Actor no encontrado")
  return actor
