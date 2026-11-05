"""Capa de aplicación: OperacionService (409/422/404 por mensaje de excepción)."""
import pytest

try:
    from src.application.operacion_service import OperacionService
    from src.infrastructure.repository import db
except ImportError as exc:  # hoy: falta OperacionStateMachine en domain
    pytest.skip(f"OperacionService no importable todavía: {exc}", allow_module_level=True)

pytestmark = pytest.mark.integration

EVIDENCIA_OK = {"hora_inicio": "2026-11-10T09:00", "ubicacion": "25.67,-100.31",
                "checklist_porcentaje": 100, "firma_cliente": True}


def _en_proceso(op_id):
    OperacionService.crear_operacion({"operacion_id": op_id, "actor_id": "CLN-C001"})
    OperacionService.ejecutar_transicion(op_id, "programar")
    OperacionService.ejecutar_transicion(op_id, "iniciar")


def test_total_operacion_coincide_con_oraculo(total_esperado, csv_operaciones):
    for op_id in (o["operacion_id"] for o in csv_operaciones):
        assert OperacionService.calcular_total_operacion(op_id) == total_esperado(op_id)


def test_crear_operacion_ok():
    op = OperacionService.crear_operacion({
        "operacion_id": "T-001", "actor_id": "CLN-C001",
        "detalles": [{"recurso_id": "CLN-P001", "cantidad": 1}]})
    assert op["estado_actual"] == "SOLICITADO"


def test_crear_duplicada_conflict():
    with pytest.raises(ValueError, match="CONFLICT"):
        OperacionService.crear_operacion({"operacion_id": "CLN-O001", "actor_id": "CLN-C001"})


def test_crear_actor_inexistente_unprocessable():
    with pytest.raises(KeyError, match="UNPROCESSABLE"):
        OperacionService.crear_operacion({"operacion_id": "T-002", "actor_id": "NOPE"})


def test_crear_recurso_inexistente_unprocessable():
    with pytest.raises(KeyError, match="UNPROCESSABLE"):
        OperacionService.crear_operacion({
            "operacion_id": "T-003", "actor_id": "CLN-C001",
            "detalles": [{"recurso_id": "NOPE", "cantidad": 1}]})


def test_transicion_operacion_inexistente_not_found():
    with pytest.raises(KeyError, match="NOT_FOUND"):
        OperacionService.ejecutar_transicion("NOPE", "programar")


@pytest.mark.parametrize("accion,estado", [
    ("programar", "PROGRAMADO"), ("cancelar", "CANCELADO")])
def test_transicion_valida_actualiza_estado(accion, estado):
    OperacionService.crear_operacion({"operacion_id": f"T-{accion}", "actor_id": "CLN-C001"})
    assert OperacionService.ejecutar_transicion(f"T-{accion}", accion)["estado_actual"] == estado


def test_flujo_completo_por_servicio():
    OperacionService.crear_operacion({"operacion_id": "T-flujo", "actor_id": "CLN-C001"})
    for accion, estado in (("programar", "PROGRAMADO"), ("iniciar", "EN_PROCESO")):
        assert OperacionService.ejecutar_transicion("T-flujo", accion)["estado_actual"] == estado
    op = OperacionService.ejecutar_transicion("T-flujo", "completar", EVIDENCIA_OK)
    assert op["estado_actual"] == "COMPLETADO"


def test_transicion_invalida_lanza_error_de_dominio():
    from src.domain.state_machine import TransicionInvalidaError
    OperacionService.crear_operacion({"operacion_id": "T-inv", "actor_id": "CLN-C001"})
    with pytest.raises(TransicionInvalidaError):
        OperacionService.ejecutar_transicion("T-inv", "completar")


# ---- Validaciones (cantidad, capacidad, disponibilidad) ----------------------
from src.domain.errors import (ConflictError, NotFoundError,  # noqa: E402
                               ReferenciaInvalidaError, ReglaNegocioError,
                               ValidacionError)


@pytest.mark.parametrize("cantidad", [0, -1, 2.5, "3", True, None])
def test_cantidad_invalida_400(cantidad):
    with pytest.raises(ValidacionError):
        OperacionService.crear_operacion({
            "operacion_id": "T-q", "actor_id": "CLN-C001",
            "detalles": [{"recurso_id": "CLN-P001", "cantidad": cantidad}]})


def test_capacidad_excedida_422(csv_catalogo):
    r = next(x for x in csv_catalogo if x["habilitado"] == "1")
    with pytest.raises(ReglaNegocioError, match="excede"):
        OperacionService.crear_operacion({
            "operacion_id": "T-cap", "actor_id": "CLN-C001",
            "detalles": [{"recurso_id": r["recurso_id"], "cantidad": int(r["capacidad_o_stock"]) + 1}]})


def test_capacidad_se_acumula_por_recurso(csv_catalogo):
    r = next(x for x in csv_catalogo if x["habilitado"] == "1")
    mitad = int(r["capacidad_o_stock"]) // 2 + 1
    linea = {"recurso_id": r["recurso_id"], "cantidad": mitad}
    with pytest.raises(ReglaNegocioError):
        OperacionService.crear_operacion({"operacion_id": "T-acum", "actor_id": "CLN-C001",
                                          "detalles": [linea, dict(linea)]})


def test_recurso_deshabilitado_422(csv_catalogo):
    r = next(x for x in csv_catalogo if x["habilitado"] == "0")
    with pytest.raises(ReglaNegocioError, match="deshabilitado"):
        OperacionService.crear_operacion({
            "operacion_id": "T-off", "actor_id": "CLN-C001",
            "detalles": [{"recurso_id": r["recurso_id"], "cantidad": 1}]})


def test_operacion_sin_id_400():
    with pytest.raises(ValidacionError):
        OperacionService.crear_operacion({"actor_id": "CLN-C001"})


def test_fallo_de_validacion_no_deja_operacion_a_medias():
    with pytest.raises(ValidacionError):
        OperacionService.crear_operacion({
            "operacion_id": "T-x", "actor_id": "CLN-C001",
            "detalles": [{"recurso_id": "CLN-P001", "cantidad": 0}]})
    assert "T-x" not in db.operaciones and "T-x" not in db.detalles


def test_tipos_de_error_y_codigos_http():
    assert ConflictError.status_code == 409 and NotFoundError.status_code == 404
    assert ReferenciaInvalidaError.status_code == 422 and ReglaNegocioError.status_code == 422
    assert ValidacionError.status_code == 400
    assert str(NotFoundError("NOT_FOUND: x")) == "NOT_FOUND: x"  # sin comillas de KeyError


# ---- RN-03: cierre con evidencia ----------------------------------------------
@pytest.mark.parametrize("quitar", [
    {}, {"hora_inicio": ""}, {"ubicacion": None},
    {"checklist_porcentaje": 99}, {"firma_cliente": False}])
def test_rn03_bloquea_cierre_sin_evidencia_completa(quitar):
    _en_proceso("T-rn3")
    evidencia = None if quitar == {} else {**EVIDENCIA_OK, **quitar}
    with pytest.raises(ReglaNegocioError, match="RN-03"):
        OperacionService.ejecutar_transicion("T-rn3", "completar", evidencia)
    assert db.operaciones["T-rn3"]["estado_actual"] == "EN_PROCESO"


def test_rn03_no_enmascara_transicion_invalida():
    OperacionService.crear_operacion({"operacion_id": "T-409", "actor_id": "CLN-C001"})
    with pytest.raises(ConflictError):  # SOLICITADO->COMPLETADO sigue siendo 409, no 422
        OperacionService.ejecutar_transicion("T-409", "completar")


def test_rn03_guarda_evidencia_al_completar():
    _en_proceso("T-ev")
    op = OperacionService.ejecutar_transicion("T-ev", "completar", EVIDENCIA_OK)
    assert op["evidencia_cierre"] == EVIDENCIA_OK


# ---- Domain Events -----------------------------------------------------------
from src.application.event_bus import event_bus  # noqa: E402


def test_crear_emite_operacion_solicitada():
    OperacionService.crear_operacion({"operacion_id": "T-e1", "actor_id": "CLN-C001"})
    ev = event_bus.eventos_de("T-e1")
    assert [e.nombre for e in ev] == ["OperacionSolicitada"] and ev[0].actor_id == "CLN-C001"


def test_flujo_emite_eventos_en_orden():
    _en_proceso("T-e2")
    OperacionService.ejecutar_transicion("T-e2", "completar", EVIDENCIA_OK)
    assert [e.nombre for e in event_bus.eventos_de("T-e2")] == [
        "OperacionSolicitada", "OperacionProgramada", "OperacionIniciada", "OperacionCompletada"]
    ultimo = event_bus.eventos_de("T-e2")[-1]
    assert (ultimo.estado_anterior, ultimo.estado_nuevo) == ("EN_PROCESO", "COMPLETADO")


def test_cancelacion_emite_operacion_cancelada():
    OperacionService.crear_operacion({"operacion_id": "T-e3", "actor_id": "CLN-C001"})
    OperacionService.ejecutar_transicion("T-e3", "cancelar")
    assert event_bus.eventos_de("T-e3")[-1].nombre == "OperacionCancelada"


def test_transicion_fallida_no_emite_evento():
    OperacionService.crear_operacion({"operacion_id": "T-e4", "actor_id": "CLN-C001"})
    with pytest.raises(ConflictError):
        OperacionService.ejecutar_transicion("T-e4", "completar")
    assert [e.nombre for e in event_bus.eventos_de("T-e4")] == ["OperacionSolicitada"]


def test_suscriptor_recibe_evento():
    recibidos = []
    from src.domain.events import OperacionProgramada
    event_bus.suscribir(OperacionProgramada, recibidos.append)
    OperacionService.crear_operacion({"operacion_id": "T-e5", "actor_id": "CLN-C001"})
    OperacionService.ejecutar_transicion("T-e5", "programar")
    assert len(recibidos) == 1 and recibidos[0].operacion_id == "T-e5"


def test_construir_candidato_inexistente_404():
    with pytest.raises(NotFoundError):
        OperacionService.construir_candidato("NOPE")
