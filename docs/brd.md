## Reporte

| Nombre: Diego Armando Valenciano García / Angela Jaquelyn Pecina Loera / Eduardo Castro Treviño |   | Matrícula: 2154143 / 2150932 / 2149985 |
| --- | --- | --- |
| Nombre del curso: Componentes de Lógica de Negocio | Marroquín | Nombre del profesor: Miguel Ángel Gómez |
| Modulo Netacad: 24 | Actividad: BRD CleanPro |   |
| Fecha: 04/09/2026 |   |   |

## Bibliografia (Formato APA)

Castro Treviño, E. Pecina Loera, A. J. Valenciano García, D. A. (2026). Business Requirements Document (BRD) CleanPro [Documento de Word no publicado]. Universidad Autónoma de Nuevo León.

## Objetivo:

Definir y estructurar formalmente las necesidades de negocio, alcance, stakeholders, restricciones y requerimientos funcionales para la digitalización de CleanPro. Este documento busca alinear a los equipos de negocio y tecnología, estableciendo las bases para automatizar la cotización de servicios, restringir los límites operativos (máximo 8 horas de trabajo por cuadrilla y 10% de descuento autorizado) y garantizar la sincronización en tiempo real de cargos e incidencias en campo hacia administración.


Reporte

## Procedimiento:

## 1. OBJETIVOS DE NEGOCIO Y VISIÓN DEL PROYECTO

## 1.1 Objetivo General

Desarrollar e implementar una plataforma digital integral que automatice el flujo operativo de CleanPro (cotización, asignación de cuadrillas, control en campo y facturación), eliminando los cuellos de botella del modelo manual actual y garantizando la trazabilidad financiera y operativa.

## 1.2 Objetivos Específicos

- Automatizar el 100% del cálculo de cotizaciones iniciales y tiempos estimados de servicio mediante la regla base de 1 persona y 1 hora por cada 50 metros cuadrados.

- Eliminar la pérdida de ingresos por reportes traspapelados en campo mediante la sincronización en tiempo real de servicios adicionales e incidencias con el módulo de administración.

- Optimizar el proceso de asignación de cuadrillas reduciendo el tiempo de calendarización manual en Excel a un algoritmo de selección por cercanía y disponibilidad en menos de 2 minutos.

- Garantizar el cumplimiento estricto del tope laboral de 8 horas diarias por cuadrilla y el límite del 10% en descuentos comerciales.

## 2. ALCANCE Y LÍMITES DEL PROYECTO

## 2.1 Dentro del Alcance (In-Scope)

- Módulo de Cotización Automática: Cálculo dinámico según metros cuadrados, tipo de inmueble, frecuencia y servicios adicionales.

- Motor de Asignación y Control de Capacidad: Sugerencia algorítmica de cuadrillas respetando el límite de 8 horas diarias y proximidad geográfica.

- Aplicación Móvil para Supervisores: Registro de llegada y salida, listas de verificación (checklists), documentación fotográfica de incidencias y captura de firma digital de conformidad.

- Gestión de Ausentismo y Alertas: Reasignación de personal de guardia y notificación automática a clientes ante retrasos superiores a 30 minutos.

- Integración Financiera: Transmisión en tiempo real de cargos extra, recálculos por tamaño y penalizaciones al sistema de facturación.

- Portal web interactivo para clientes para seguimiento y reprogramaciones.


Reporte

## 2.2 Fuera del Alcance (Out-of-Scope)

- Contabilidad general, nómina profunda y cálculo de impuestos fiscales avanzados (el sistema solo genera las pre-facturas y reportes de insumos/horas para nómina).

- Venta directa de productos de limpieza al detalle sin la contratación de un servicio de limpieza.

## 3. STAKEHOLDERS Y EXPECTATIVAS DE LOS INTERESADOS

| Cliente Final | Requiere cotizaciones transparentes e inmediatas, puntualidad en la atención, alertas claras en caso de retrasos y facilidades para reprogramar o autorizar servicios extras sin complicaciones. |
| --- | --- |
| Coordinador Operativo | Busca sustituir las hojas de cálculo manuales por un tablero centralizado donde pueda visualizar agendas, asignar personal de guardia en segundos y validar límites de descuento. |
| Supervisor de Cuadrilla | Necesita una herramienta ágil en campo para auditar la calidad del servicio, capturar evidencias de daños previos o incidentes y obtener la firma del cliente sin usar papel. |
| Personal de Cuadrilla y Guardia | Esperan agendas de trabajo balanceadas que no superen las 8 horas diarias y claridad en sus asignaciones diarias. |
| Departamento de Administración | Exige que todos los cobros extraordinarios, materiales especiales y penalizaciones acordadas en campo se reflejen automáticamente en la facturación final sin extravíos de información. |


Reporte

## 4. NECESIDADES Y REQUISITOS DE NEGOCIO (BUSINESS REQUIREMENTS)

| RN-01 (Motor de Cotizaciones): | El sistema debe permitir cotizar en tiempo real aplicando automáticamente la equivalencia estándar de 1 persona y 1 hora por cada 50 metros cuadrados de superficie, añadiendo los tiempos y tarifas estandarizadas para servicios extras. |
| --- | --- |
| RN-02 (Reglas de Control Operativo y Comercial): | El sistema debe bloquear automáticamente cualquier intento de asignar más de 8 horas de trabajo acumulado en un solo día a una cuadrilla. Asimismo, restringirá los descuentos comerciales otorgados por coordinadores a un tope máximo del 10% sin aprobación gerencial. |
| RN-03 (Trazabilidad y Conformidad en Campo): | El sistema debe exigir al supervisor el registro de geolocalización/hora de inicio, el marcado al 100% de la lista de verificación de áreas y la firma digital del cliente como condición obligatoria para dar por concluido un servicio. |
| RN-04 (Gestión de Contingencias y Ausentismo): | Ante una falta de personal, el sistema debe facilitar la sustitución por elementos de la plantilla de guardia. Si la reorganización deriva en un desfase mayor a 30 minutos en la llegada, el sistema debe emitir una alerta prioritaria para notificar al cliente. |
| RN-05 (Sincronización Financiera en Tiempo Real): | Cualquier concepto adicional generado en sitio (horas extra por espacio subestimado, servicios adicionales o cargos por visita fallida tras 15 minutos de espera) debe impactar de inmediato el estado de cuenta del cliente en el módulo administrativo. |


Reporte

## 5. RESTRICCIONES Y SUPUESTOS

## Restricciones

- Tope operativo inamovible de 8 horas diarias de trabajo programado por cuadrilla.

- Política rígida de reprogramación: cambios sin costo solo con 24 horas de antelación; después de este plazo se aplica un 20% de penalización por gastos operativos.

- Tiempo máximo de espera en domicilio de 15 minutos antes de declarar una visita fallida y aplicar el cobro correspondiente.

## Supuestos

- El personal de supervisión en campo contará con dispositivos móviles inteligentes con conexión a datos para operar la app en tiempo real.

- Los clientes disponen de medios digitales para revisar presupuestos y otorgar su firma de conformidad al finalizar el trabajo.

## 6. ENTREGABLES CLAVE Y CRITERIOS DE ÉXITO

## Entregables Clave

- 1. Especificación detallada de Historias de Usuario y Criterios de Aceptación (Gherkin).

- 2. Prototipo funcional del Módulo Web de Coordinación y Administración.

- 3. Aplicación móvil para Supervisores de Cuadrilla.

- 4. Portal web para Clientes.

- 5. Matriz de trazabilidad y plan de pruebas de aceptación del usuario (UAT).

## Criterios de Éxito (KPIs)

- Cero pérdida de facturación: Reducción del 100% en las discrepancias financieras causadas por notas en papel extraviadas.

- Agilidad de respuesta: Reducción del tiempo de elaboración de cotizaciones y asignación de cuadrillas de más de 30 minutos a menos de 2 minutos.

- Cumplimiento de servicio: Disminución de quejas por impuntualidad gracias al sistema de alertas por ausencias e incidencias operativas.


Reporte

## 7. GUÍA DE LEVANTAMIENTO (ENTREVISTA CON STAKEHOLDERS)

Como parte de la fase de descubrimiento para construir este BRD, se recopilaron las siguientes respuestas del responsable de operaciones:

## 1. ¿Qué criterio se usa para calcular el personal por inmueble?

Respuesta: Se asigna 1 persona por cada 50 metros cuadrados.

- 2. ¿Cómo estiman la duración de la limpieza?

Respuesta: 1 hora base por cada 50 metros cuadrados, más 30 a 60 minutos adicionales según los extras solicitados.

3. ¿Qué datos debe registrar el supervisor al iniciar y finalizar? Respuesta: Hora de llegada, hora de salida, checklist de áreas concluidas y firma

digital del cliente.

- 4. ¿Cómo se gestionan los daños o reclamos en el lugar?

Respuesta: El supervisor toma fotografías, describe el evento en la app y notifica al coordinador para activar el seguro o garantía.

- 5. ¿Qué sucede si un trabajador falta a su turno?

Respuesta: Se asigna a alguien del personal de guardia. Si esto retrasa la llegada más de 30 minutos, se llama de inmediato al cliente.

## 6. ¿Cuáles son los límites de tiempo de trabajo y de descuento?

Respuesta: Máximo 8 horas de trabajo al día por cuadrilla y máximo 10% de descuento permitido al coordinador.

- 7. ¿Qué ocurre si el servicio toma más tiempo del previsto?

Respuesta: Si fue por ineficiencia nuestra, la empresa asume el costo; si el espacio era más grande de lo declarado, se ajusta la tarifa con el cliente.

- 8. ¿Cómo se tramitan los servicios extra pedidos durante la visita?

Respuesta: El supervisor lo valora con el coordinador, el cliente lo aprueba en el momento y se suma a la cuenta digital.

- 9. ¿Qué se hace si las dimensiones del inmueble son mayores a las registradas?

Respuesta: Se pausa el trabajo y se hace un recálculo. Si el cliente no lo acepta, se cancela y se cobra la cuota de visita.


Reporte

## 10. ¿Por qué razón se perdían ingresos en el esquema anterior?

Respuesta: Porque las notas de extras o fallas anotadas en papel tardaban días en llegar a administración o simplemente se extraviaban.

## 11. ¿Cómo debe enterarse administración de un cambio de personal?

Respuesta: Mediante una actualización en tiempo real en la plataforma para ajustar el control de nómina.

## 12. ¿Cuál es la política para reprogramar una cita?

Respuesta: Es gratuita si se avisa con más de 24 horas de anticipación; si falta menos tiempo, se cobra una penalización del 20%.

## 13. ¿Qué protocolo se aplica si nadie abre la puerta al llegar?

Respuesta: Se otorgan 15 minutos de tolerancia, el coordinador intenta contactar al cliente y, si no hay respuesta, la cuadrilla se retira y se cobra la visita fallida.

## 14. ¿Cómo se debe mejorar la asignación de personal respecto al uso de Excel?

Respuesta: El sistema debe sugerir automáticamente la cuadrilla libre más cercana en lugar de revisarlo manualmente en un pizarrón.

## 15. ¿Cómo se gestionan los materiales o químicos de uso especial?

Respuesta: El coordinador solicita autorización previa a Administración en la cotización inicial y el costo se desglosa como un adicional.


Reporte

## Conclusiones

El BRD establece un marco claro para eliminar las ineficiencias del modelo operativo manual de CleanPro. Al digitalizar las reglas de negocio y los puntos de contacto en campo, la organización asegura la prevención de fugas de capital por notas traspapeladas, estandariza los criterios de atención al cliente y proporciona una guía precisa para el diseño e implementación del nuevo sistema tecnológico.
