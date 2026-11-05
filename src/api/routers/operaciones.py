from typing import List, Optional

from fastapi import APIRouter
from pydantic import BaseModel

from src.application.event_bus import event_bus
from src.application.operacion_service import OperacionService
from src.domain.errors import NotFoundError
from src.domain.specifications import (Beneficio_Referencia_Specification,
                                       Puede_Procesarse_Specification)
from src.infrastructure.repository import db

router = APIRouter()


class DetalleIn(BaseModel):
  recurso_id: str
  cantidad: int


class OperacionIn(BaseModel):
  operacion_id: str
  actor_id: str
  detalles: List[DetalleIn] = []
  fecha_solicitud: Optional[str] = None
  promocion_activa: int = 0
  autorizado: int = 1
  referencia: Optional[str] = None


class EvidenciaCierre(BaseModel):
  """Evidencia de campo exigida por RN-03 para completar un servicio."""
  hora_inicio: Optional[str] = None
  ubicacion: Optional[str] = None
  checklist_porcentaje: float = 0
  firma_cliente: bool = False


class TransicionIn(BaseModel):
  accion: str  # programar | iniciar | completar | cancelar
  evidencia: Optional[EvidenciaCierre] = None


def _detalle(op_id: str) -> dict:
  if op_id not in db.operaciones:
    raise NotFoundError(f"NOT_FOUND: La operación {op_id} no existe.")
  lineas = []
  for d in db.detalles.get(op_id, []):
    recurso = db.catalogo.get(d["recurso_id"], {})
    lineas.append({**d, **{k: v for k, v in recurso.items() if k != "recurso_id"}})
  return {
      **db.operaciones[op_id],
      "detalles": lineas,
      "importe_total_mxn": float(OperacionService.calcular_total_operacion(op_id)),
  }


@router.get("/", summary="Listar todas las operaciones")
def listar_operaciones():
  data = list(db.operaciones.values())
  return {"total": len(data), "data": data}


@router.post("/", status_code=201, summary="Crear una operación (201 / 400 / 409 / 422)")
def crear_operacion(body: OperacionIn):
  op = OperacionService.crear_operacion(body.model_dump(exclude_none=True))
  return _detalle(op["operacion_id"])


@router.get("/{operacion_id}", summary="Obtener detalle completo de una operación")
def obtener_detalle_operacion(operacion_id: str):
  return _detalle(operacion_id)


@router.post("/{operacion_id}/transicion",
             summary="Cambiar de estado (200 / 400 / 404 / 409 / 422)")
def transicionar(operacion_id: str, body: TransicionIn):
  evidencia = body.evidencia.model_dump() if body.evidencia else None
  OperacionService.ejecutar_transicion(operacion_id, body.accion, evidencia)
  return _detalle(operacion_id)


@router.get("/{operacion_id}/evaluacion",
            summary="Evalúa las Specifications puede_procesarse y beneficio_referencia")
def evaluar(operacion_id: str):
  candidato = OperacionService.construir_candidato(operacion_id)
  return {
      "operacion_id": operacion_id,
      "puede_procesarse": Puede_Procesarse_Specification().is_satisfied_by(candidato),
      "beneficio_referencia": Beneficio_Referencia_Specification().is_satisfied_by(candidato),
      "total_mxn": float(candidato["total"]),
  }


@router.get("/{operacion_id}/eventos", summary="Domain Events emitidos por la operación")
def eventos(operacion_id: str):
  if operacion_id not in db.operaciones:
    raise NotFoundError(f"NOT_FOUND: La operación {operacion_id} no existe.")
  data = [{"evento": e.nombre, "ocurrido_en": e.ocurrido_en.isoformat(),
           "estado_anterior": getattr(e, "estado_anterior", None),
           "estado_nuevo": getattr(e, "estado_nuevo", None)}
          for e in event_bus.eventos_de(operacion_id)]
  return {"total": len(data), "data": data}
