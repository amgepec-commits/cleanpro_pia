"""Configuración común de pruebas.

1) Los CSV se leen con rutas relativas (db = DataRepository() se instancia al
   importar), así que fijamos el cwd a la raíz del repo ANTES de importar src.
"""
import csv
import os
import sys
from datetime import date, time
from decimal import Decimal
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
os.chdir(ROOT)
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

import pytest  # noqa: E402


def leer_csv(nombre: str):
    """CSV UTF-8 con BOM (utf-8-sig), como los entrega el profesor."""
    with open(ROOT / nombre, encoding="utf-8-sig", newline="") as f:
        return list(csv.DictReader(f))


@pytest.fixture(scope="session")
def csv_actores():
    return leer_csv("actores.csv")


@pytest.fixture(scope="session")
def csv_catalogo():
    return leer_csv("catalogo.csv")


@pytest.fixture(scope="session")
def csv_operaciones():
    return leer_csv("operaciones.csv")


@pytest.fixture(scope="session")
def csv_detalle():
    return leer_csv("detalle_operaciones.csv")


@pytest.fixture(scope="session")
def total_esperado(csv_catalogo, csv_detalle):
    """Oráculo independiente: total = Σ precio_mxn × cantidad con Decimal."""
    precios = {r["recurso_id"]: Decimal(r["precio_mxn"]) for r in csv_catalogo}

    def _total(op_id: str) -> Decimal:
        return sum(
            (precios[d["recurso_id"]] * Decimal(d["cantidad"])
             for d in csv_detalle if d["operacion_id"] == op_id),
            Decimal("0.00"),
        )

    return _total


@pytest.fixture
def solicitud():
    from src.domain.aggregates import Solicitud_Sevicio
    from src.domain.entities import Cliente
    from src.domain.value_objects import Direccion, HorarioServicio

    return Solicitud_Sevicio(
        ID_Solicitud="SOL-1",
        Estado="SOLICITADO",
        cliente=Cliente("C-1", "Ana Pérez", "ana@mail.com", "8100000000", "x"),
        direccion=Direccion("Av. Universidad", "101", "Centro", "Monterrey",
                            "64000", "Frente a FIME"),
        horario=HorarioServicio(date(2026, 11, 10), time(9, 0), 2.0),
        cotizacion_asociada=Decimal("0.00"),
    )


@pytest.fixture(autouse=True)
def estado_limpio():
    """Cada prueba parte de los CSV originales y sin eventos previos."""
    from src.application.event_bus import event_bus
    from src.infrastructure.repository import db
    db.reiniciar()
    event_bus.reiniciar()
    yield
