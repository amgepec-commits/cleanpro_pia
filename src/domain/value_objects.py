from dataclasses import dataclass #Libreria para usar dataclass
from datetime import date, time #libreria para tiempo
from decimal import Decimal #Libreria para numeros

@dataclass(frozen=True) #(frozen =True) Hace que los value objects sean inmutables
#Cada uno de los value objects junto con sus atributos
class Direccion:
    Calle: str
    Numero: str
    Colonia: str
    Ciudad: str
    Codigo_Postal: str
    Referencias: str

@dataclass(frozen=True)
class DetallePago:
    Monto_Total: Decimal
    Metodo_Tarjeta_Efectivo: str
    Estatus_Transaccion: str

@dataclass (frozen=True)
class HorarioServicio:
    Fecha_Programada: date
    Hora_Inicio: time
    Duracion: float