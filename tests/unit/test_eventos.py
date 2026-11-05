"""Domain Events y EventBus."""
import pytest

from src.application.event_bus import EventBus
from src.domain.events import (OperacionCancelada, OperacionCompletada, OperacionIniciada,
                               OperacionProgramada, OperacionSolicitada, evento_de_transicion)
from src.domain.state_machine import Estado_Servicio as E

pytestmark = pytest.mark.unit


@pytest.mark.parametrize("nuevo,clase", [
    (E.PROGRAMADO, OperacionProgramada), (E.EN_PROCESO, OperacionIniciada),
    (E.COMPLETADO, OperacionCompletada), (E.CANCELADO, OperacionCancelada)])
def test_evento_por_estado(nuevo, clase):
    ev = evento_de_transicion("O-1", E.SOLICITADO, nuevo)
    assert isinstance(ev, clase) and ev.estado_nuevo == nuevo.name and ev.nombre == clase.__name__


def test_eventos_inmutables_y_con_fecha():
    from dataclasses import FrozenInstanceError
    ev = OperacionSolicitada(operacion_id="O-1", actor_id="A")
    assert ev.ocurrido_en.tzinfo is not None
    with pytest.raises(FrozenInstanceError):
        ev.actor_id = "B"


def test_bus_historial_filtrado_y_suscriptores():
    bus, visto = EventBus(), []
    bus.suscribir(OperacionSolicitada, visto.append)
    bus.publicar(OperacionSolicitada(operacion_id="O-1"))
    bus.publicar(OperacionSolicitada(operacion_id="O-2"))
    assert len(visto) == 2 and [e.operacion_id for e in bus.eventos_de("O-2")] == ["O-2"]
    bus.reiniciar()
    assert bus.historial == []
