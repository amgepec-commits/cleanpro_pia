from dataclasses import dataclass
from decimal import Decimal
from src.domain.entities import Cliente
from src.domain.value_objects import Direccion, HorarioServicio

@dataclass
class Solicitud_Sevicio:
    ID_Solicitud: str
    Estado: str
    cliente: Cliente # Vinculacion obligatoria para que no existan solicitudes huerfanas
    direccion: Direccion
    horario: HorarioServicio
    cotizacion_asociada: Decimal

    def calcular_cotizacion(self, superficie_m2: Decimal, precio_base: Decimal, precio_extras: Decimal = Decimal('0.00')):
        "Implementa la regla de negocio: 1 persona y 1 hora base por cada 50 m2."
        # Se calcula el multiplo de 50 m2
        factor_superficie = superficie_m2 / Decimal('50')
        
        # El costo base es el factor multiplicado por el precio base, mas extras
        costo_total = (factor_superficie * precio_base) + precio_extras
        
        self.cotizacion_asociada = costo_total
        return self.cotizacion_asociada