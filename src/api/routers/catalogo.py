from fastapi import APIRouter, HTTPException
import pandas as pd

router = APIRouter()


def cargar_catalogo():
  try:
    df = pd.read_csv("catalogo.csv")
    return df.to_dict(orient="records")
  except Exception as e:
    return []


@router.get("/", summary="Obtener el catálogo completo")
def listar_catalogo():
  catalogo = cargar_catalogo()
  return {"total": len(catalogo), "data": catalogo}


@router.get("/{recurso_id}", summary="Obtener recurso del catálogo por ID")
def obtener_recurso(recurso_id: str):
  catalogo = cargar_catalogo()
  recurso = next((r for r in catalogo if r["recurso_id"] == recurso_id), None)
  if not recurso:
    raise HTTPException(status_code=404, detail="Recurso no encontrado")
  return recurso