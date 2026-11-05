"""Domain Events del ciclo de vida de una operación/servicio."""
from dataclasses import dataclass, field
from datetime import datetime, timezone

from src.domain.state_machine import Estado_Servicio


@dataclass(frozen=True)
class DomainEvent:
    operacion_id: str
    ocurrido_en: datetime = field(default_factory=lambda: datetime.now(timezone.utc))

    @property
    def nombre(self) -> str:
        return type(self).__name__


@dataclass(frozen=True)
class OperacionSolicitada(DomainEvent):
    actor_id: str = ""


@dataclass(frozen=True)
class CambioDeEstado(DomainEvent):
    estado_anterior: str = ""
    estado_nuevo: str = ""


@dataclass(frozen=True)
class OperacionProgramada(CambioDeEstado):
    pass


@dataclass(frozen=True)
class OperacionIniciada(CambioDeEstado):
    pass


@dataclass(frozen=True)
class OperacionCompletada(CambioDeEstado):
    pass


@dataclass(frozen=True)
class OperacionCancelada(CambioDeEstado):
    pass


EVENTO_POR_ESTADO = {
    Estado_Servicio.PROGRAMADO: OperacionProgramada,
    Estado_Servicio.EN_PROCESO: OperacionIniciada,
    Estado_Servicio.COMPLETADO: OperacionCompletada,
    Estado_Servicio.CANCELADO: OperacionCancelada,
}


def evento_de_transicion(operacion_id: str, anterior: Estado_Servicio, nuevo: Estado_Servicio) -> CambioDeEstado:
    return EVENTO_POR_ESTADO[nuevo](operacion_id=operacion_id,
                                    estado_anterior=anterior.name, estado_nuevo=nuevo.name)
