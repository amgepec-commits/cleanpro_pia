# Máquina de estados del ciclo de vida del servicio:
# SOLICITADO -> PROGRAMADO -> EN_PROCESO -> COMPLETADO   (cancelación: SOLICITADO/PROGRAMADO -> CANCELADO)
from enum import Enum

from src.domain.errors import ConflictError, ValidacionError


class Estado_Servicio(Enum):
    """Los 5 estados exigidos en el diseño del sistema."""
    SOLICITADO = "Solicitado"
    PROGRAMADO = "Programado"
    EN_PROCESO = "En Proceso"
    COMPLETADO = "Completado"
    CANCELADO = "Cancelado"


class TransicionInvalidaError(ConflictError):
    """Transición no permitida -> 409 (sigue siendo ValueError)."""


class AccionDesconocidaError(ValidacionError):
    """Acción no reconocida -> 400."""


class Validador_Flujo:
    TRANSICIONES = {
        Estado_Servicio.SOLICITADO: [Estado_Servicio.PROGRAMADO, Estado_Servicio.CANCELADO],
        Estado_Servicio.PROGRAMADO: [Estado_Servicio.EN_PROCESO, Estado_Servicio.CANCELADO],
        Estado_Servicio.EN_PROCESO: [Estado_Servicio.COMPLETADO],
        Estado_Servicio.COMPLETADO: [],  # terminal
        Estado_Servicio.CANCELADO: [],   # terminal
    }

    @staticmethod
    def Cambiar_Estado(estado_actual: Estado_Servicio, nuevo_estado: Estado_Servicio) -> Estado_Servicio:
        if nuevo_estado not in Validador_Flujo.TRANSICIONES[estado_actual]:
            raise TransicionInvalidaError(
                f"Error de dominio: No se puede pasar de {estado_actual.name} a {nuevo_estado.name}")
        return nuevo_estado


def _a_estado(valor) -> Estado_Servicio:
    """Acepta Estado_Servicio, nombre ('EN_PROCESO') o valor ('En Proceso')."""
    if isinstance(valor, Estado_Servicio):
        return valor
    texto = str(valor).strip()
    if texto.upper().replace(" ", "_") in Estado_Servicio.__members__:
        return Estado_Servicio[texto.upper().replace(" ", "_")]
    raise ValidacionError(f"Estado desconocido: {valor!r}")


class OperacionStateMachine:
    """Adaptador orientado a acciones, usado por la capa de aplicación."""
    ACCIONES = {
        "programar": Estado_Servicio.PROGRAMADO,
        "iniciar": Estado_Servicio.EN_PROCESO,
        "completar": Estado_Servicio.COMPLETADO,
        "cancelar": Estado_Servicio.CANCELADO,
    }

    def __init__(self, estado_actual="SOLICITADO"):
        self.estado_actual = _a_estado(estado_actual)

    def transicionar(self, accion: str) -> Estado_Servicio:
        destino = self.ACCIONES.get(str(accion).strip().lower())
        if destino is None:
            raise AccionDesconocidaError(
                f"Acción desconocida: {accion!r}. Válidas: {sorted(self.ACCIONES)}")
        self.estado_actual = Validador_Flujo.Cambiar_Estado(self.estado_actual, destino)
        return self.estado_actual
