#En este codigo se aplica el patron elegido: Specification Pattern
#Usaremos las dos reglas principales del negocio: el tope de 8 horas diarias y el limite del 10% de descuento.
#importamos ABC (Abstract Base Class) para crear plantillas que otras deben de usar
from abc import ABC, abstractmethod

#Creamos la base (plantilla)
class Specification(ABC):
    # Este metodo es obligatorio para todas las reglas.
    # Evaluara si un 'candidato' (ej. un proveedor o una cotizacion) cumple la regla.
    @abstractmethod
    def is_satisfied_by(self, candidato) -> bool:
        pass

    #operador __and__ (esto permite usar el simbolo & en python)
    def __and__(self, otra_regla):
        return And_Specification(self, otra_regla)

    #Operador __or__ (esto permite usar el simbolo | en python)
    def __or__(self, otra_regla):
        return Or_Specification(self, otra_regla)

    #Operador __invert__ (esto permite usar el simbolo ~ en python)
    def __invert__(self):
        return Not_Specification(self)

#Combinadores logicos (and,or,not)
class And_Specification(Specification):
    def __init__(self, spec1, spec2):
        #sepc1= regla_horas y spec2 = regla_descuento
        self.spec1 = spec1
        self.spec2 = spec2

    def is_satisfied_by(self, candidato):
        # Devuelve True solo si AMBAS reglas se cumplen
        return self.spec1.is_satisfied_by(candidato) and self.spec2.is_satisfied_by(candidato)
        
        
class Or_Specification(Specification):
    def __init__(self, spec1, spec2):
        self.spec1 = spec1
        self.spec2 = spec2

    def is_satisfied_by(self, candidato) -> bool:
        # Devuelve True si AL MENOS UNA regla se cumple
        return self.spec1.is_satisfied_by(candidato) or self.spec2.is_satisfied_by(candidato)

class Not_Specification(Specification):
    def __init__(self, spec):
        self.spec = spec

    def is_satisfied_by(self, candidato) -> bool:
        # Devuelve lo contrario de la regla (Si era True, devuelve False)
        return not self.spec.is_satisfied_by(candidato)

#Reglas especificas del negocio

class Limite_Jornada_Specification(Specification):
    "Regla RN-02: Bloquea intentos de asignar mas de 8 horas diarias a una cuadrilla."
    "El 'candidato' en este caso seria un diccionario o un objeto con las horas."
    def is_satisfied_by(self, proveedor_horas) -> bool:
        horas_ya_agendadas = proveedor_horas.get('horas_agendadas', 0)
        horas_nuevo_servicio = proveedor_horas.get('duracion_nuevo_servicio', 0)
        
        # Si la suma es menor o igual a 8, la regla se cumple (True)
        return (horas_ya_agendadas + horas_nuevo_servicio) <= 8

class Tope_Descuento_Specification(Specification):
    "Regla RN-02: Restringe los descuentos comerciales a un tope del 10%."
    def is_satisfied_by(self, cotizacion) -> bool:
        descuento_solicitado = cotizacion.get('porcentaje_descuento', 0)
        
        # Si el descuento es menor o igual a 10%, la regla se cumple (True)
        return descuento_solicitado <= 10

# ---------------------------------------------------------------------------
# Specifications de los fixtures del PIA (puede_procesarse / beneficio_referencia)
# Candidato: dict con actor_activo, actor_preferente, num_lineas, autorizado,
# total (Decimal) y promocion_activa (ver OperacionService.construir_candidato).
# ---------------------------------------------------------------------------
from decimal import Decimal


class Actor_Activo_Specification(Specification):
    def is_satisfied_by(self, candidato) -> bool:
        return bool(candidato.get("actor_activo"))


class Detalle_No_Vacio_Specification(Specification):
    """La operación debe tener al menos una línea de detalle."""
    def is_satisfied_by(self, candidato) -> bool:
        return candidato.get("num_lineas", 0) >= 1


class Autorizacion_Specification(Specification):
    def is_satisfied_by(self, candidato) -> bool:
        return bool(candidato.get("autorizado"))


class Actor_Preferente_Specification(Specification):
    def is_satisfied_by(self, candidato) -> bool:
        return bool(candidato.get("actor_preferente"))


class Total_Minimo_Specification(Specification):
    def __init__(self, minimo=Decimal("1500")):
        self.minimo = Decimal(str(minimo))

    def is_satisfied_by(self, candidato) -> bool:
        return Decimal(str(candidato.get("total", 0))) >= self.minimo


class Promocion_Activa_Specification(Specification):
    def is_satisfied_by(self, candidato) -> bool:
        return bool(candidato.get("promocion_activa"))


class Puede_Procesarse_Specification(Specification):
    """actor activo AND operación con al menos una línea AND autorización."""
    def __init__(self):
        self._regla = (Actor_Activo_Specification()
                       & Detalle_No_Vacio_Specification()
                       & Autorizacion_Specification())

    def is_satisfied_by(self, candidato) -> bool:
        return self._regla.is_satisfied_by(candidato)


class Beneficio_Referencia_Specification(Specification):
    """actor preferente AND total >= 1500 MXN AND NOT promoción activa."""
    def __init__(self):
        self._regla = (Actor_Preferente_Specification()
                       & Total_Minimo_Specification(Decimal("1500"))
                       & ~Promocion_Activa_Specification())

    def is_satisfied_by(self, candidato) -> bool:
        return self._regla.is_satisfied_by(candidato)


# ---------------------------------------------------------------------------
# RN-03 (BRD): cierre de servicio exige hora/geolocalización de inicio,
# checklist al 100 % y firma digital del cliente.
# Candidato: dict con hora_inicio, ubicacion, checklist_porcentaje, firma_cliente.
# ---------------------------------------------------------------------------
class Inicio_Registrado_Specification(Specification):
    def is_satisfied_by(self, candidato) -> bool:
        return bool(candidato.get("hora_inicio")) and bool(candidato.get("ubicacion"))


class Checklist_Completo_Specification(Specification):
    def is_satisfied_by(self, candidato) -> bool:
        return Decimal(str(candidato.get("checklist_porcentaje", 0))) >= Decimal("100")


class Firma_Cliente_Specification(Specification):
    def is_satisfied_by(self, candidato) -> bool:
        return bool(candidato.get("firma_cliente"))


class Cierre_Conforme_Specification(Specification):
    """RN-03: inicio registrado AND checklist 100 % AND firma del cliente."""
    def __init__(self):
        self._regla = (Inicio_Registrado_Specification()
                       & Checklist_Completo_Specification()
                       & Firma_Cliente_Specification())

    def is_satisfied_by(self, candidato) -> bool:
        return self._regla.is_satisfied_by(candidato)
