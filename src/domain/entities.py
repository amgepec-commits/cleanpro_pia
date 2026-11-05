from dataclasses import dataclass
from datetime import datetime

@dataclass #los entidades si cambian, por ello no usamos (frozen=True)
class Cliente:
    ID_Cliente: str
    Nombre_Completo: str
    Correo_Electronico: str
    Telefono: str
    Contrasena: str

    def Registrar_Solicitud(self):
        pass

@dataclass
class Proveedor:
    ID_Provedor: str
    Nombre_Razon_Social: str
    Especialidad_Limpieza: str
    Calificacion_Promedio: float
    Estatus_Disponibilidad: str

    def Aceptar_Servicio(self):
        pass

@dataclass
class Servicio:
    ID_Servicio: str
    Estado_Actual: str
    Fecha_Hora_Ejecucion: datetime

    def Iniciar_Servicio(self):
        pass

    def Finalizar_Servicio(self):
        pass