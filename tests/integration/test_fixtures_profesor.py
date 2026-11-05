"""Fixtures del profesor: 120 casos (puede_procesarse / beneficio_referencia) y 20 transiciones.
El oráculo se calcula aparte, solo con los CSV y Decimal, sin usar las Specifications."""
from decimal import Decimal

import pytest

from src.application.operacion_service import OperacionService
from src.domain.specifications import (Beneficio_Referencia_Specification,
                                       Puede_Procesarse_Specification)

pytestmark = pytest.mark.integration


def _casos():
    from tests.conftest import leer_csv
    return leer_csv("casos_prueba.csv")


@pytest.fixture(scope="module")
def mundo(csv_actores, csv_operaciones, csv_detalle, total_esperado):
    actores = {a["actor_id"]: a for a in csv_actores}
    ops = {o["operacion_id"]: o for o in csv_operaciones}
    lineas = {}
    for d in csv_detalle:
        lineas[d["operacion_id"]] = lineas.get(d["operacion_id"], 0) + 1
    return actores, ops, lineas, total_esperado


def test_120_casos_cargados():
    casos = _casos()
    assert len(casos) == 120
    assert {c["tipo_prueba"] for c in casos} == {"validar_operacion", "evaluar_beneficio"}


def test_puede_procesarse_contra_oraculo_csv(mundo):
    actores, ops, lineas, _ = mundo
    for c in (c for c in _casos() if c["tipo_prueba"] == "validar_operacion"):
        op = ops[c["operacion_id"]]
        esperado = (actores[op["actor_id"]]["activo"] == "1"
                    and lineas.get(op["operacion_id"], 0) >= 1
                    and op["autorizado"] == "1")
        obtenido = Puede_Procesarse_Specification().is_satisfied_by(
            OperacionService.construir_candidato(op["operacion_id"]))
        assert obtenido is esperado, c["caso_id"]


def test_beneficio_referencia_contra_oraculo_csv(mundo):
    actores, ops, _, total = mundo
    for c in (c for c in _casos() if c["tipo_prueba"] == "evaluar_beneficio"):
        op = ops[c["operacion_id"]]
        esperado = (actores[op["actor_id"]]["es_preferente"] == "1"
                    and total(op["operacion_id"]) >= Decimal("1500")
                    and op["promocion_activa"] == "0")
        obtenido = Beneficio_Referencia_Specification().is_satisfied_by(
            OperacionService.construir_candidato(op["operacion_id"]))
        assert obtenido is esperado, c["caso_id"]


def test_runner_genera_evidencia_completa(tmp_path, monkeypatch):
    import scripts.run_fixtures as rf
    monkeypatch.setattr(rf, "EVID", tmp_path)
    t, c = rf.correr_transiciones(), rf.correr_casos()
    assert (len(t), len(c)) == (20, 120)
    assert (tmp_path / "transiciones_resultado.csv").exists()
    assert all(x["resultado_alumno"] != "PENDIENTE" for x in t + c)
    finales = {(x["accion_sugerida"], x["estado_final"], x["resultado_alumno"]) for x in t}
    assert finales == {
        ("aprobar", "PROGRAMADO", "OK"), ("cancelar", "CANCELADO", "OK"),
        ("completar", "SOLICITADO", "EXCEPCION"), ("saltar_estado", "SOLICITADO", "EXCEPCION"),
        ("repetir_aprobacion", "PROGRAMADO", "EXCEPCION")}
