"""Integridad de los fixtures del profesor (40/20/60 + detalle, FKs, Decimal)."""
from decimal import Decimal

import pytest

pytestmark = pytest.mark.integration


def test_volumenes(csv_actores, csv_catalogo, csv_operaciones):
    assert (len(csv_actores), len(csv_catalogo), len(csv_operaciones)) == (40, 20, 60)


def test_claves_foraneas(csv_actores, csv_catalogo, csv_operaciones, csv_detalle):
    actores = {a["actor_id"] for a in csv_actores}
    recursos = {r["recurso_id"] for r in csv_catalogo}
    ops = {o["operacion_id"] for o in csv_operaciones}
    assert {o["actor_id"] for o in csv_operaciones} <= actores
    assert {d["recurso_id"] for d in csv_detalle} <= recursos
    assert {d["operacion_id"] for d in csv_detalle} <= ops


def test_todas_las_operaciones_arrancan_solicitado(csv_operaciones):
    assert {o["estado_inicial"] for o in csv_operaciones} == {"SOLICITADO"}


def test_cantidades_positivas(csv_detalle):
    assert all(int(d["cantidad"]) > 0 for d in csv_detalle)


def test_total_es_decimal_exacto(total_esperado):
    # CLN-O001: CLN-P009 ×3 + CLN-P014 ×4
    t = total_esperado("CLN-O001")
    assert isinstance(t, Decimal)
    assert t == t.quantize(Decimal("0.01"))
