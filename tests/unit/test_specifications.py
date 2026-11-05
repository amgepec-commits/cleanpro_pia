"""Patrón Specification: reglas RN-02 y combinadores AND/OR/NOT."""
import itertools

import pytest
from src.domain.specifications import (And_Specification, Limite_Jornada_Specification,
                            Not_Specification, Or_Specification, Specification,
                            Tope_Descuento_Specification)

pytestmark = pytest.mark.unit


class Siempre(Specification):
    def __init__(self, valor):
        self.valor = valor

    def is_satisfied_by(self, candidato):
        return self.valor


@pytest.mark.parametrize("ya,nuevo,esperado", [
    (0, 8, True), (6, 2, True), (5, 3, True),   # límite exacto = 8 → cumple
    (6, 3, False), (8, 1, False), (0, 9, False),
])
def test_limite_jornada(ya, nuevo, esperado):
    c = {"horas_agendadas": ya, "duracion_nuevo_servicio": nuevo}
    assert Limite_Jornada_Specification().is_satisfied_by(c) is esperado


@pytest.mark.parametrize("pct,esperado", [
    (0, True), (5, True), (10, True), (10.01, False), (11, False), (50, False)])
def test_tope_descuento(pct, esperado):
    assert Tope_Descuento_Specification().is_satisfied_by(
        {"porcentaje_descuento": pct}) is esperado


def test_valores_por_defecto_si_faltan_llaves():
    assert Limite_Jornada_Specification().is_satisfied_by({}) is True
    assert Tope_Descuento_Specification().is_satisfied_by({}) is True


@pytest.mark.parametrize("a,b", list(itertools.product([True, False], repeat=2)))
def test_tabla_verdad_and_or(a, b):
    sa, sb = Siempre(a), Siempre(b)
    assert (sa & sb).is_satisfied_by(None) is (a and b)
    assert (sa | sb).is_satisfied_by(None) is (a or b)


@pytest.mark.parametrize("a", [True, False])
def test_not(a):
    assert (~Siempre(a)).is_satisfied_by(None) is (not a)


def test_operadores_devuelven_combinadores():
    s = Siempre(True)
    assert isinstance(s & s, And_Specification)
    assert isinstance(s | s, Or_Specification)
    assert isinstance(~s, Not_Specification)


def test_combinacion_de_negocio_and_con_not():
    # Jornada válida Y NO (descuento > 10%)  ==  jornada OK y descuento OK
    regla = Limite_Jornada_Specification() & ~(~Tope_Descuento_Specification())
    ok = {"horas_agendadas": 5, "duracion_nuevo_servicio": 2,
          "porcentaje_descuento": 5}
    mal = {**ok, "porcentaje_descuento": 15}
    assert regla.is_satisfied_by(ok) is True
    assert regla.is_satisfied_by(mal) is False


def test_or_de_reglas_de_negocio():
    regla = Limite_Jornada_Specification() | Tope_Descuento_Specification()
    solo_descuento_ok = {"horas_agendadas": 8, "duracion_nuevo_servicio": 5,
                         "porcentaje_descuento": 3}
    ninguna = {"horas_agendadas": 8, "duracion_nuevo_servicio": 5,
               "porcentaje_descuento": 30}
    assert regla.is_satisfied_by(solo_descuento_ok) is True
    assert regla.is_satisfied_by(ninguna) is False


def test_specification_abstracta_no_se_instancia():
    with pytest.raises(TypeError):
        Specification()


# ---- Specifications de los fixtures del PIA ---------------------------------
from decimal import Decimal  # noqa: E402

from src.domain.specifications import (Beneficio_Referencia_Specification,  # noqa: E402
                                       Puede_Procesarse_Specification,
                                       Total_Minimo_Specification)

BASE = {"actor_activo": True, "actor_preferente": True, "num_lineas": 2,
        "autorizado": True, "promocion_activa": False, "total": Decimal("1500")}


@pytest.mark.parametrize("cambio,esperado", [
    ({}, True), ({"actor_activo": False}, False),
    ({"num_lineas": 0}, False), ({"autorizado": False}, False)])
def test_puede_procesarse(cambio, esperado):
    assert Puede_Procesarse_Specification().is_satisfied_by({**BASE, **cambio}) is esperado


@pytest.mark.parametrize("cambio,esperado", [
    ({}, True),                                   # total == 1500 cumple
    ({"total": Decimal("1499.99")}, False),
    ({"actor_preferente": False}, False),
    ({"promocion_activa": True}, False)])
def test_beneficio_referencia(cambio, esperado):
    assert Beneficio_Referencia_Specification().is_satisfied_by({**BASE, **cambio}) is esperado


def test_total_minimo_configurable_y_sin_total():
    assert Total_Minimo_Specification(100).is_satisfied_by({"total": 100}) is True
    assert Total_Minimo_Specification().is_satisfied_by({}) is False


# ---- RN-03 ------------------------------------------------------------------
from src.domain.specifications import Cierre_Conforme_Specification  # noqa: E402

CIERRE = {"hora_inicio": "09:00", "ubicacion": "25.6,-100.3",
          "checklist_porcentaje": 100, "firma_cliente": True}


@pytest.mark.parametrize("cambio,esperado", [
    ({}, True), ({"hora_inicio": None}, False), ({"ubicacion": ""}, False),
    ({"checklist_porcentaje": 99.9}, False), ({"firma_cliente": False}, False)])
def test_cierre_conforme_rn03(cambio, esperado):
    assert Cierre_Conforme_Specification().is_satisfied_by({**CIERRE, **cambio}) is esperado


def test_cierre_conforme_sin_datos():
    assert Cierre_Conforme_Specification().is_satisfied_by({}) is False
