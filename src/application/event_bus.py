"""Publicador de eventos en memoria (patrón Observer) para los Domain Events."""
from collections import defaultdict
from typing import Callable, Dict, List, Type

from src.domain.events import DomainEvent


class EventBus:
    def __init__(self):
        self._handlers: Dict[Type[DomainEvent], List[Callable]] = defaultdict(list)
        self.historial: List[DomainEvent] = []

    def suscribir(self, tipo: Type[DomainEvent], handler: Callable) -> None:
        self._handlers[tipo].append(handler)

    def publicar(self, evento: DomainEvent) -> None:
        self.historial.append(evento)
        for tipo, handlers in self._handlers.items():
            if isinstance(evento, tipo):
                for h in handlers:
                    h(evento)

    def eventos_de(self, operacion_id: str) -> List[DomainEvent]:
        return [e for e in self.historial if e.operacion_id == operacion_id]

    def reiniciar(self) -> None:
        self._handlers.clear()
        self.historial.clear()


event_bus = EventBus()
