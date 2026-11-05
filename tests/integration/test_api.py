"""Pruebas de integración de la API REST (FastAPI TestClient).

Contrato de errores: 400 dato mal formado, 404 no existe, 409 duplicado o
transición inválida, 422 referencia/regla de negocio (capacidad, RN-03).
Cada prueba parte de los CSV originales (fixture autouse en conftest).
"""
import pytest

pytest.importorskip("fastapi")
pytest.importorskip("httpx")
from fastapi.testclient import TestClient  # noqa: E402

pytestmark = pytest.mark.integration


@pytest.fixture(scope="module")
def client():
    from src.api.main import app
    return TestClient(app)


def test_root_ok(client):
    r = client.get("/")
    assert r.status_code == 200
    assert r.json()["documentacion_swagger"] == "/docs"


def test_swagger_y_openapi_activos(client):
    assert client.get("/docs").status_code == 200
    spec = client.get("/openapi.json")
    assert spec.status_code == 200
    assert "/api/operaciones/" in spec.json()["paths"]


def test_listar_actores(client):
    r = client.get("/api/actores/")
    assert r.status_code == 200 and r.json()["total"] == 40


def test_actor_existente_y_404(client):
    assert client.get("/api/actores/CLN-C001").status_code == 200
    assert client.get("/api/actores/NO-EXISTE").status_code == 404


def test_catalogo_y_404(client):
    assert client.get("/api/catalogo/").json()["total"] == 20
    assert client.get("/api/catalogo/CLN-P001").status_code == 200
    assert client.get("/api/catalogo/NO-EXISTE").status_code == 404


def test_listar_operaciones(client):
    assert client.get("/api/operaciones/").json()["total"] == 60


def test_detalle_operacion_total_decimal_correcto(client, total_esperado):
    for op_id in ("CLN-O001", "CLN-O002", "CLN-O030", "CLN-O060"):
        r = client.get(f"/api/operaciones/{op_id}")
        assert r.status_code == 200
        assert r.json()["importe_total_mxn"] == pytest.approx(float(total_esperado(op_id)))
        assert len(r.json()["detalles"]) >= 1


def test_operacion_404(client):
    assert client.get("/api/operaciones/NO-EXISTE").status_code == 404


# ---- Escritura y transiciones ---------------------------------------------
EVIDENCIA = {"hora_inicio": "2026-11-10T09:00", "ubicacion": "25.67,-100.31",
             "checklist_porcentaje": 100, "firma_cliente": True}


def _nueva(client, op_id="CLN-O900", cantidad=2):
    return client.post("/api/operaciones/", json={
        "operacion_id": op_id, "actor_id": "CLN-C001",
        "detalles": [{"recurso_id": "CLN-P001", "cantidad": cantidad}]})


def test_crear_operacion_201_y_consultable(client):
    r = _nueva(client)
    assert r.status_code == 201
    assert r.json()["estado_actual"] == "SOLICITADO" and r.json()["importe_total_mxn"] > 0
    assert client.get("/api/operaciones/CLN-O900").status_code == 200
    assert client.get("/api/operaciones/").json()["total"] == 61


def test_crear_operacion_duplicada_409(client):
    body = {"operacion_id": "CLN-O001", "actor_id": "CLN-C001", "detalles": []}
    assert client.post("/api/operaciones/", json=body).status_code == 409


def test_crear_operacion_actor_inexistente_422(client):
    body = {"operacion_id": "CLN-O901", "actor_id": "NOPE", "detalles": []}
    assert client.post("/api/operaciones/", json=body).status_code == 422


def test_cantidad_invalida_400(client):
    assert _nueva(client, "CLN-O902", cantidad=0).status_code == 400
    assert client.get("/api/operaciones/CLN-O902").status_code == 404  # no quedó a medias


def test_capacidad_excedida_422(client):
    assert _nueva(client, "CLN-O903", cantidad=10_000).status_code == 422


def test_recurso_deshabilitado_422(client, csv_catalogo):
    off = next(r["recurso_id"] for r in csv_catalogo if r["habilitado"] == "0")
    r = client.post("/api/operaciones/", json={
        "operacion_id": "CLN-O904", "actor_id": "CLN-C001",
        "detalles": [{"recurso_id": off, "cantidad": 1}]})
    assert r.status_code == 422


def test_cuerpo_incompleto_lo_rechaza_fastapi_422(client):
    assert client.post("/api/operaciones/", json={"actor_id": "CLN-C001"}).status_code == 422


def test_transicion_valida_200(client):
    r = client.post("/api/operaciones/CLN-O003/transicion", json={"accion": "programar"})
    assert r.status_code == 200 and r.json()["estado_actual"] == "PROGRAMADO"


def test_transicion_invalida_409(client):
    r = client.post("/api/operaciones/CLN-O004/transicion", json={"accion": "completar"})
    assert r.status_code == 409 and "No se puede pasar" in r.json()["detail"]


def test_transicion_repetida_409(client):
    url = "/api/operaciones/CLN-O005/transicion"
    assert client.post(url, json={"accion": "programar"}).status_code == 200
    assert client.post(url, json={"accion": "programar"}).status_code == 409


def test_accion_desconocida_400(client):
    r = client.post("/api/operaciones/CLN-O006/transicion", json={"accion": "volar"})
    assert r.status_code == 400


def test_transicion_operacion_inexistente_404(client):
    r = client.post("/api/operaciones/NOPE/transicion", json={"accion": "programar"})
    assert r.status_code == 404


def test_flujo_completo_con_evidencia_rn03(client):
    url = "/api/operaciones/CLN-O007/transicion"
    for accion in ("programar", "iniciar"):
        assert client.post(url, json={"accion": accion}).status_code == 200
    sin = client.post(url, json={"accion": "completar"})
    assert sin.status_code == 422 and "RN-03" in sin.json()["detail"]
    ok = client.post(url, json={"accion": "completar", "evidencia": EVIDENCIA})
    assert ok.status_code == 200 and ok.json()["estado_actual"] == "COMPLETADO"


def test_cancelar_desde_solicitado_200(client):
    r = client.post("/api/operaciones/CLN-O008/transicion", json={"accion": "cancelar"})
    assert r.status_code == 200 and r.json()["estado_actual"] == "CANCELADO"


def test_eventos_de_la_operacion(client):
    client.post("/api/operaciones/CLN-O009/transicion", json={"accion": "programar"})
    r = client.get("/api/operaciones/CLN-O009/eventos")
    assert r.status_code == 200
    assert [e["evento"] for e in r.json()["data"]] == ["OperacionProgramada"]
    assert client.get("/api/operaciones/NOPE/eventos").status_code == 404


def test_evaluacion_specifications(client, total_esperado):
    r = client.get("/api/operaciones/CLN-O001/evaluacion")
    assert r.status_code == 200
    assert r.json()["total_mxn"] == pytest.approx(float(total_esperado("CLN-O001")))
    assert isinstance(r.json()["puede_procesarse"], bool)
    assert client.get("/api/operaciones/NOPE/evaluacion").status_code == 404
