"""Value Objects, entidades y agregado SolicitudServicio (cotización con Decimal)."""
from dataclasses import FrozenInstanceError
from datetime import date, time
from decimal import Decimal

import pytest
from src.domain.entities import Cliente, Proveedor, Servicio
from src.domain.value_objects import DetallePago, Direccion, HorarioServicio

pytestmark = pytest.mark.unit


def test_value_objects_son_inmutables():
    d = Direccion("A", "1", "C", "MTY", "64000", "")
    with pytest.raises(FrozenInstanceError):
        d.Calle = "otra"
    h = HorarioServicio(date(2026, 11, 10), time(9, 0), 2.0)
    with pytest.raises(FrozenInstanceError):
        h.Duracion = 3.0


def test_value_objects_igualdad_por_valor():
    a = Direccion("A", "1", "C", "MTY", "64000", "")
    b = Direccion("A", "1", "C", "MTY", "64000", "")
    assert a == b and hash(a) == hash(b)
    assert DetallePago(Decimal("10"), "Efectivo", "OK") == DetallePago(
        Decimal("10"), "Efectivo", "OK")


def test_entidades_son_mutables():
    c = Cliente("C-1", "Ana", "a@m.com", "1", "x")
    c.Telefono = "2"
    assert c.Telefono == "2"
    p = Proveedor("P-1", "Limpio SA", "Profunda", 4.5, "DISPONIBLE")
    p.Estatus_Disponibilidad = "OCUPADO"
    assert p.Estatus_Disponibilidad == "OCUPADO"
    assert Servicio("S-1", "PROGRAMADO", None).Estado_Actual == "PROGRAMADO"


@pytest.mark.parametrize("m2,base,extras,esperado", [
    ("100", "500", "0.00", "1000"),
    ("50", "500", "0.00", "500"),
    ("25", "500", "0.00", "250"),       # superficie fraccionaria de bloque
    ("100", "500", "150.50", "1150.50"),
    ("0", "500", "0.00", "0"),
])
def test_calcular_cotizacion(solicitud, m2, base, extras, esperado):
    total = solicitud.calcular_cotizacion(
        Decimal(m2), Decimal(base), Decimal(extras))
    assert isinstance(total, Decimal)
    assert total == Decimal(esperado)
    assert solicitud.cotizacion_asociada == total


def test_cotizacion_sin_error_de_punto_flotante(solicitud):
    # 0.1 + 0.2 != 0.3 en float; con Decimal sí.
    assert solicitud.calcular_cotizacion(
        Decimal("50"), Decimal("0.1"), Decimal("0.2")) == Decimal("0.3")


def test_solicitud_requiere_cliente_direccion_y_horario(solicitud):
    assert solicitud.cliente is not None
    assert solicitud.direccion.Ciudad == "Monterrey"
    assert solicitud.horario.Hora_Inicio == time(9, 0)
    assert solicitud.Estado == "SOLICITADO"
