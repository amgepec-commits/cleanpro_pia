"""Errores de dominio. Cada uno lleva el código HTTP al que la API debe mapearlo."""


class DomainError(Exception):
    status_code = 400

    def __str__(self):  # evita las comillas que KeyError agrega al mensaje
        return str(self.args[0]) if self.args else self.__class__.__name__


class ValidacionError(DomainError, ValueError):
    """Dato mal formado (cantidad inválida, acción desconocida...). -> 400"""
    status_code = 400


class NotFoundError(DomainError, KeyError):
    """El recurso solicitado no existe. -> 404"""
    status_code = 404


class ConflictError(DomainError, ValueError):
    """Duplicado o transición no permitida. -> 409"""
    status_code = 409


class ReferenciaInvalidaError(DomainError, KeyError):
    """Clave foránea inexistente (actor o recurso). -> 422"""
    status_code = 422


class ReglaNegocioError(DomainError, ValueError):
    """Regla de negocio no satisfecha (capacidad, RN-03...). -> 422"""
    status_code = 422
