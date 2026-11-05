"""Máquina de estados: SOLICITADO→PROGRAMADO→EN_PROCESO→COMPLETADO y
SOLICITADO→CANCELADO (el diseño actual también permite PROGRAMADO→CANCELADO)."""
import itertools

import pytest
from src.domain.state_machine import Estado_Servicio as E
from src.domain.state_machine import Validador_Flujo as V

pytestmark = pytest.mark.unit

VALIDAS = [
    (E.SOLICITADO, E.PROGRAMADO),
    (E.PROGRAMADO, E.EN_PROCESO),
    (E.EN_PROCESO, E.COMPLETADO),
    (E.SOLICITADO, E.CANCELADO),
    (E.PROGRAMADO, E.CANCELADO),
]
INVALIDAS = [p for p in itertools.product(E, E) if p not in VALIDAS]


@pytest.mark.parametrize("origen,destino", VALIDAS)
def test_transicion_valida(origen, destino):
    assert V.Cambiar_Estado(origen, destino) is destino


@pytest.mark.parametrize("origen,destino", INVALIDAS)
def test_transicion_invalida_lanza_error(origen, destino):
    with pytest.raises(ValueError, match="No se puede pasar"):
        V.Cambiar_Estado(origen, destino)


@pytest.mark.parametrize("terminal", [E.COMPLETADO, E.CANCELADO])
def test_estados_terminales_no_salen(terminal):
    for destino in E:
        with pytest.raises(ValueError):
            V.Cambiar_Estado(terminal, destino)


def test_flujo_completo_feliz():
    estado = E.SOLICITADO
    for destino in (E.PROGRAMADO, E.EN_PROCESO, E.COMPLETADO):
        estado = V.Cambiar_Estado(estado, destino)
    assert estado is E.COMPLETADO


def test_salto_ilegal_programado_a_completado():
    with pytest.raises(ValueError):
        V.Cambiar_Estado(E.PROGRAMADO, E.COMPLETADO)


def test_hay_exactamente_cinco_estados():
    assert {e.name for e in E} == {
        "SOLICITADO", "PROGRAMADO", "EN_PROCESO", "COMPLETADO", "CANCELADO"}


# ---- Adaptador por acciones (usado por OperacionService) -------------------
from src.domain.state_machine import (AccionDesconocidaError,  # noqa: E402
                                      OperacionStateMachine,
                                      TransicionInvalidaError)


@pytest.mark.parametrize("inicio", ["SOLICITADO", "Solicitado", E.SOLICITADO])
def test_adaptador_acepta_nombre_valor_o_enum(inicio):
    assert OperacionStateMachine(inicio).estado_actual is E.SOLICITADO


def test_adaptador_flujo_por_acciones():
    sm = OperacionStateMachine("SOLICITADO")
    for accion, esperado in (("programar", E.PROGRAMADO), ("iniciar", E.EN_PROCESO),
                             ("completar", E.COMPLETADO)):
        assert sm.transicionar(accion) is esperado


def test_adaptador_cancelacion():
    assert OperacionStateMachine("SOLICITADO").transicionar("CANCELAR") is E.CANCELADO


def test_adaptador_accion_desconocida():
    with pytest.raises(AccionDesconocidaError):
        OperacionStateMachine("SOLICITADO").transicionar("volar")


def test_adaptador_transicion_invalida_es_error_de_dominio():
    with pytest.raises(TransicionInvalidaError):
        OperacionStateMachine("SOLICITADO").transicionar("completar")


def test_adaptador_estado_desconocido():
    with pytest.raises(ValueError):
        OperacionStateMachine("NOPE")
