from decimal import Decimal
from datetime import date, time

# Importamos todas las piezas que programaste en los otros archivos
from src.domain.value_objects import Direccion, HorarioServicio
from src.domain.entities import Cliente
from src.domain.aggregates import Solicitud_Sevicio
from src.domain.state_machine import Estado_Servicio, Validador_Flujo
from src.domain.specifications import Limite_Jornada_Specification, Tope_Descuento_Specification

def probar_sistema():
    print("=== INICIANDO PRUEBAS DEL SISTEMA CLEANPRO ===\n")

    # 1. Crear los Objetos de Valor
    direccion = Direccion(
        Calle="Av. Universidad", Numero="101", Colonia="Centro", 
        Ciudad="Monterrey", Codigo_Postal="64000", Referencias="Frente a FIME"
    )
    horario = HorarioServicio(
        Fecha_Programada=date(2026, 11, 10), 
        Hora_Inicio=time(9, 0), 
        Duracion=2.0
    )

    # 2. Crear la Entidad Cliente
    cliente = Cliente(
        ID_Cliente="C-001", Nombre_Completo="Diego Valenciano", 
        Correo_Electronico="diego@email.com", Telefono="8123456789", Contrasena="password123"
    )

    # 3. Ensamblar el Agregado Raíz (La Solicitud)
    solicitud = Solicitud_Sevicio(
        ID_Solicitud="SOL-100", 
        Estado=Estado_Servicio.SOLICITADO.name, 
        cliente=cliente, 
        direccion=direccion, 
        horario=horario, 
        cotizacion_asociada=Decimal('0.00')
    )
    print(f"[*] Solicitud {solicitud.ID_Solicitud} creada con estado: {solicitud.Estado}")

    # 4. Probar la regla de cotización (100 m2 a $500 la base de 50 m2 = Debe dar $1000)
    superficie = Decimal('100.00')
    precio_base = Decimal('500.00')
    total = solicitud.calcular_cotizacion(superficie, precio_base)
    print(f"[*] Cotización calculada para 100m2: ${total}")

    # 5. Probar la Máquina de Estados
    print("\n--- Probando Transiciones de Estado ---")
    try:
        # Transición válida: Solicitado -> Programado
        nuevo_estado = Validador_Flujo.Cambiar_Estado(Estado_Servicio.SOLICITADO, Estado_Servicio.PROGRAMADO)
        solicitud.Estado = nuevo_estado.name
        print(f"[*] Éxito: El estado cambió a {solicitud.Estado}")

        # Transición inválida: Programado -> Completado (se salta el "En Proceso")
        print("[*] Intentando forzar un salto ilegal (PROGRAMADO a COMPLETADO)...")
        Validador_Flujo.Cambiar_Estado(Estado_Servicio.PROGRAMADO, Estado_Servicio.COMPLETADO)
    except ValueError as error:
        print(f"[*] Máquina de estados funcionó bloqueando el error: {error}")

    # 6. Probar las Specifications (Reglas de Negocio combinadas)
    print("\n--- Probando Reglas de Negocio (AND) ---")
    regla_horas = Limite_Jornada_Specification()
    regla_descuento = Tope_Descuento_Specification()
    
    # Combinamos ambas reglas con el operador mágico '&'
    reglas_estrictas = regla_horas & regla_descuento

    # Simulamos un servicio que sumará 7 horas en total y tiene 5% de descuento
    candidato_prueba = {
        'horas_agendadas': 5,
        'duracion_nuevo_servicio': 2,
        'porcentaje_descuento': 5
    }

    resultado = reglas_estrictas.is_satisfied_by(candidato_prueba)
    print(f"[*] ¿El servicio cumple con límite de horas y tope de descuento?: {'Sí, pasa.' if resultado else 'No, se bloquea.'}")
    print("\n=== PRUEBAS FINALIZADAS CON ÉXITO ===")

# Ejecutar la prueba
if __name__ == "__main__":
    probar_sistema()