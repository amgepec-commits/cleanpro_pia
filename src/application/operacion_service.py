from decimal import Decimal
from typing import Any, Dict, Optional

from src.application.event_bus import event_bus
from src.domain.errors import (ConflictError, NotFoundError, ReferenciaInvalidaError,
                               ReglaNegocioError, ValidacionError)
from src.domain.events import OperacionSolicitada, evento_de_transicion
from src.domain.specifications import Cierre_Conforme_Specification
from src.domain.state_machine import Estado_Servicio, OperacionStateMachine
from src.infrastructure.repository import db


class OperacionService:

  @staticmethod
  def crear_operacion(data: Dict[str, Any]) -> Dict[str, Any]:
    op_id = data.get("operacion_id")
    actor_id = data.get("actor_id")
    detalles = data.get("detalles") or []

    if not op_id:
      raise ValidacionError("VALIDATION: operacion_id es obligatorio.")  # 400
    if op_id in db.operaciones:
      raise ConflictError(f"CONFLICT: La operación '{op_id}' ya existe.")  # 409
    if actor_id not in db.actores:
      raise ReferenciaInvalidaError(  # 422
          f"UNPROCESSABLE: El actor '{actor_id}' no existe en el catálogo.")

    acumulado: Dict[str, int] = {}
    for d in detalles:
      rec_id, cant = d.get("recurso_id"), d.get("cantidad")
      if isinstance(cant, bool) or not isinstance(cant, int) or cant < 1:
        raise ValidacionError(  # 400
            f"VALIDATION: cantidad inválida ({cant!r}) para '{rec_id}'; debe ser un entero >= 1.")
      recurso = db.catalogo.get(rec_id)
      if recurso is None:
        raise ReferenciaInvalidaError(  # 422
            f"UNPROCESSABLE: El recurso '{rec_id}' no existe en el catálogo.")
      if not recurso["habilitado"]:
        raise ReglaNegocioError(  # 422
            f"UNPROCESSABLE: El recurso '{rec_id}' está deshabilitado.")
      acumulado[rec_id] = acumulado.get(rec_id, 0) + cant
      if acumulado[rec_id] > recurso["capacidad_o_stock"]:
        raise ReglaNegocioError(  # 422
            f"UNPROCESSABLE: '{rec_id}' excede la capacidad disponible "
            f"({acumulado[rec_id]} > {recurso['capacidad_o_stock']}).")

    nueva_op = {
        "operacion_id": op_id,
        "actor_id": actor_id,
        "estado_inicial": "SOLICITADO",
        "estado_actual": "SOLICITADO",
        "fecha_solicitud": data.get("fecha_solicitud", "2026-11-04"),
        "promocion_activa": data.get("promocion_activa", 0),
        "autorizado": data.get("autorizado", 1),
        "referencia": data.get("referencia", f"REF_{op_id}"),
    }
    db.operaciones[op_id] = nueva_op
    db.detalles[op_id] = [dict(d, operacion_id=op_id) for d in detalles]
    event_bus.publicar(OperacionSolicitada(operacion_id=op_id, actor_id=actor_id))
    return nueva_op

  @staticmethod
  def calcular_total_operacion(op_id: str) -> Decimal:
    detalles = db.detalles.get(op_id, [])
    total = Decimal("0.00")
    for item in detalles:
      recurso = db.catalogo.get(item.get("recurso_id"), {})
      precio = Decimal(str(recurso.get("precio_mxn", 0.0)))
      cant = Decimal(str(item.get("cantidad", 0)))
      total += precio * cant
    return total

  @staticmethod
  def ejecutar_transicion(op_id: str, accion: str,
                          evidencia: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    if op_id not in db.operaciones:
      raise NotFoundError(f"NOT_FOUND: La operación {op_id} no existe.")  # 404

    op = db.operaciones[op_id]
    sm = OperacionStateMachine(op["estado_actual"])
    anterior = sm.estado_actual

    # RN-03: para cerrar un servicio en proceso se exige evidencia de campo.
    if (str(accion).strip().lower() == "completar" and anterior is Estado_Servicio.EN_PROCESO
        and not Cierre_Conforme_Specification().is_satisfied_by(evidencia or {})):
      raise ReglaNegocioError(  # 422
          "UNPROCESSABLE: RN-03 exige hora/ubicación de inicio, checklist al 100% "
          "y firma del cliente para completar el servicio.")

    sm.transicionar(accion)  # 400 acción desconocida / 409 transición inválida
    op["estado_actual"] = sm.estado_actual.name  # mismo formato que los CSV
    if evidencia and sm.estado_actual is Estado_Servicio.COMPLETADO:
      op["evidencia_cierre"] = evidencia
    event_bus.publicar(evento_de_transicion(op_id, anterior, sm.estado_actual))
    return op

  @staticmethod
  def construir_candidato(op_id: str) -> Dict[str, Any]:
    """Datos de una operación listos para evaluar Specifications."""
    if op_id not in db.operaciones:
      raise NotFoundError(f"NOT_FOUND: La operación {op_id} no existe.")
    op = db.operaciones[op_id]
    actor = db.actores.get(op["actor_id"], {})
    return {
        "actor_activo": bool(actor.get("activo", 0)),
        "actor_preferente": bool(actor.get("es_preferente", 0)),
        "num_lineas": len(db.detalles.get(op_id, [])),
        "autorizado": bool(op.get("autorizado", 0)),
        "promocion_activa": bool(op.get("promocion_activa", 0)),
        "total": OperacionService.calcular_total_operacion(op_id),
    }
