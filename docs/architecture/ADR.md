Reporte
```
Objetivo:
```
Documentar y justificar las decisiones arquitectónicas propuestas para
CleanPro, considerando el contexto, las alternativas disponibles y las
consecuencias de cada decisión.
```
Nombre: Diego Armando Valenciaro Garcia/ Angela
```
Jaquelyn Pecina Loera/ Eduardo Castro Treviño
Matrícula: 2154143 /
2150932 / 2149985
Nombre del curso: Componentes de
Lógica de Negocio
Nombre del profesor: Miguel Ángel
Gómez Marroquín
```
Modulo Netacad: 24 Actividad: ADR (Architecture Decision
```
```
Record)
```
```
Fecha: 06/05/2022
```
```
Bibliografia (Formato APA)
```
Reporte
```
Procedimiento:
```
ADR-001
Arquitectura modular del sistema
Estado Propuesto
Área Arquitectura de lógica de negocio
Trazabilidad BRD: cotización, programación, ejecución y
administración. Historias US-01 a US-15.
1. Contexto
CleanPro gestiona cotizaciones, agenda y asignación de cuadrillas, ejecución del
servicio, incidencias, cargos y pre-factura. Mantener toda la lógica mezclada dificultaría
el mantenimiento y las pruebas.
2. Problema / fuerzas que influyen
¿Cómo separar responsabilidades sin añadir complejidad técnica innecesaria?
3. Decisión
```
Organizar la lógica en módulos de dominio: Cotizaciones; Programación y Cuadrillas;
```
```
Ejecución del Servicio; Incidencias y Cargos; Administración y Pre-factura. Los módulos
```
```
pueden permanecer dentro de una misma aplicación; esta decisión no obliga a usar
```
microservicios.
4. Alternativas consideradas
• Aplicación con toda la lógica en un solo módulo: sencilla al inicio, pero con mayor
acoplamiento.
• Arquitectura modular dentro de una aplicación: separa responsabilidades sin multiplicar
despliegues.
• Microservicios independientes: permiten despliegues separados, pero añaden complejidad
que el caso no exige.
5. Consecuencias
• Ventaja: responsabilidades y pruebas más claras.
• Ventaja: facilita localizar la lógica responsable de un comportamiento.
• Costo: se deben definir límites e interfaces entre módulos.
• Limitación: no determina por sí sola la base de datos ni la infraestructura.
Reporte
6. Consideraciones de implementación
Definir las operaciones públicas de cada módulo y evitar que las pantallas implementen
reglas de negocio. Documentar dependencias entre módulos.
7. Criterios de validación
• La decisión se puede relacionar con requisitos del caso y verificarse mediante pruebas.
• Las reglas no se duplican innecesariamente en pantallas o módulos.
• Las excepciones y errores relevantes quedan registrados.
Reporte
ADR-002
Trazabilidad y sincronización de cargos
Estado Propuesto
Área Arquitectura de lógica de negocio
Trazabilidad BRD: sincronización en tiempo real de cargos
adicionales, recálculos y visitas fallidas. US-13, US-
14 y US-15.
1. Contexto
Los servicios pueden generar cargos por extras aprobados, recálculos de tarifa,
reprogramaciones tardías o visitas fallidas. El caso indica que los cargos deben
sincronizarse con Administración.
2. Problema / fuerzas que influyen
¿Cómo conservar el origen de cada cargo y evitar duplicados si una sincronización se
reintenta?
3. Decisión
Registrar cada cargo con identificador, servicio relacionado, motivo, importe, fecha y
estado de sincronización. La integración debe detectar reintentos para evitar
duplicados mediante un identificador único o mecanismo equivalente. El protocolo
técnico queda pendiente.
4. Alternativas consideradas
• Registro manual en Administración: fácil de iniciar, pero aumenta omisiones y diferencias.
• Enviar cargos sin controlar repeticiones: sencillo, pero vulnerable a duplicados.
• Cargos trazables y sincronización idempotente: permite auditar el origen y controlar
reintentos.
5. Consecuencias
• Ventaja: cada cargo se rastrea hasta el servicio y su motivo.
• Ventaja: se reduce el riesgo de duplicación.
• Costo: requiere gestionar estados de sincronización y errores.
• Pendiente: el caso no especifica protocolo ni infraestructura de integración.
6. Consideraciones de implementación
```
Definir estados mínimos como pendiente, sincronizado y error; guardar fecha y
```
resultado de intentos. Acordar qué sistema asigna el identificador definitivo.
7. Criterios de validación
• La decisión se puede relacionar con requisitos del caso y verificarse mediante pruebas.
• Las reglas no se duplican innecesariamente en pantallas o módulos.
Reporte
• Las excepciones y errores relevantes quedan registrados.
Reporte
ADR-003
Centralización de reglas y estados del negocio
Estado Propuesto
Área Arquitectura de lógica de negocio
Trazabilidad BRD: tope de descuento, límite diario,
reprogramación y cierre. Historias US-01 a US-15.
1. Contexto
CleanPro debe aplicar reglas en distintos flujos. Si cada pantalla calcula descuentos,
penalizaciones y estados por separado, pueden producirse resultados inconsistentes.
2. Problema / fuerzas que influyen
¿Cómo garantizar que las reglas y transiciones sean iguales en todo el sistema?
3. Decisión
Mantener las reglas en componentes de lógica de negocio compartidos y definir
transiciones válidas para cotizaciones y servicios. Por ejemplo, descuentos superiores al
10 % requieren aprobación gerencial y las reprogramaciones con menos de 24 horas
generan una penalización del 20 %.
4. Alternativas consideradas
• Duplicar validaciones en cada pantalla: rápido al inicio, difícil de mantener.
• Centralizar reglas y validar transiciones: reduce inconsistencias y facilita las pruebas.
• Usar un motor externo de reglas: posible, pero el caso no demuestra que sea necesario.
5. Consecuencias
• Ventaja: las reglas se modifican en un lugar y se prueban consistentemente.
• Ventaja: los estados son más previsibles.
• Costo: se deben definir estados y transiciones permitidos.
• Pendiente: no se especifican el redondeo para personal ni todas las fórmulas de cargos.
6. Consideraciones de implementación
```
Probar límites exactos: descuento de 10 % y superior; reprogramación con 24 horas y
```
```
con menos; jornada de 8 horas y asignaciones que la excedan.
```
7. Criterios de validación
• La decisión se puede relacionar con requisitos del caso y verificarse mediante pruebas.
• Las reglas no se duplican innecesariamente en pantallas o módulos.
• Las excepciones y errores relevantes quedan registrados.
Reporte
ADR-004
Asignación y disponibilidad de cuadrillas
Estado Propuesto
Área Arquitectura de lógica de negocio
Trazabilidad BRD: máximo de 8 horas y sustitución por
ausencias. US-04, US-05 y US-06.
1. Contexto
CleanPro debe programar servicios y sugerir cuadrillas cercanas disponibles. La
asignación debe respetar el máximo de ocho horas programadas por cuadrilla al día y
contemplar ausencias y cuadrillas de guardia.
2. Problema / fuerzas que influyen
¿Cómo evitar asignaciones incompatibles con la agenda y priorizar una cuadrilla
adecuada?
3. Decisión
Validar disponibilidad antes de confirmar una asignación. La sugerencia puede priorizar
la cuadrilla disponible más cercana siempre que cumpla los límites operativos. Ante una
```
ausencia, evaluar una cuadrilla de guardia; si el retraso supera 30 minutos, notificar al
```
cliente según el BRD.
4. Alternativas consideradas
• Asignación manual sin validaciones: flexible, pero propensa a conflictos.
• Elegir solo por cercanía: puede recomendar una cuadrilla ocupada.
• Validar disponibilidad y límite diario antes de priorizar cercanía: respeta restricciones y
después optimiza la elección.
5. Consecuencias
• Ventaja: reduce dobles asignaciones y sobrecarga programada.
• Ventaja: las sugerencias respetan las restricciones.
• Costo: necesita una agenda actualizada y duraciones estimadas.
• Pendiente: no se define cómo calcular distancia ni resolver empates.
6. Consideraciones de implementación
Revalidar disponibilidad al confirmar para reducir conflictos entre solicitudes
simultáneas. Acordar cómo se calcula la cercanía y cómo se administra la cuadrilla de
guardia.
7. Criterios de validación
• La decisión se puede relacionar con requisitos del caso y verificarse mediante pruebas.
Reporte
• Las reglas no se duplican innecesariamente en pantallas o módulos.
• Las excepciones y errores relevantes quedan registrados.
Reporte
ADR-005
Evidencias y cierre del servicio
Estado Propuesto
Área Arquitectura de lógica de negocio
Trazabilidad BRD: hora/ubicación de llegada, checklist y firma.
US-07, US-08, US-09, US-10 y US-11.
1. Contexto
El cierre requiere datos de ejecución. El BRD especifica hora y ubicación de llegada,
```
checklist al 100 % y firma digital del cliente; las incidencias pueden incluir fotografías y
```
deben llegar al coordinador.
2. Problema / fuerzas que influyen
¿Cómo asegurar que un servicio no se marque como completado sin los requisitos
obligatorios?
3. Decisión
Validar hora y ubicación de llegada, checklist completo al 100 % y firma digital antes de
permitir el estado completado. Asociar incidencias y fotografías al servicio. La política
para excepciones de firma o fallos técnicos debe definirse antes de implementar.
4. Alternativas consideradas
• Permitir cerrar sin validar: reduce fricción, pero contradice el BRD.
• Validar requisitos al finalizar: establece criterios de cierre verificables.
• Guardar evidencias sin relacionarlas con un servicio: debilita la trazabilidad.
5. Consecuencias
• Ventaja: el cierre tiene criterios verificables.
• Ventaja: incidencias y evidencias quedan asociadas al servicio.
• Costo: el cierre depende de registrar los datos obligatorios.
• Pendiente: no se define proveedor de firma, retención de fotos ni procedimiento de excepción.
6. Consideraciones de implementación
Probar el cierre con cada requisito faltante. Definir acceso y protección de evidencias,
errores de carga y excepciones autorizadas sin inventar reglas ausentes del BRD.
7. Criterios de validación
• La decisión se puede relacionar con requisitos del caso y verificarse mediante pruebas.
• Las reglas no se duplican innecesariamente en pantallas o módulos.
• Las excepciones y errores relevantes quedan registrados.
Reporte
Matriz de trazabilidad
La matriz relaciona las decisiones propuestas con los requisitos conocidos del caso. Los
identificadores de historias corresponden al documento de historias de usuario de
CleanPro.
ADR Tema Referencias relacionadas
ADR-001 Arquitectura modular Procesos de cotización,
programación, ejecución,
```
incidencias y Administración; US-
```
01 a US-15
ADR-002 Trazabilidad de cargos Cargos y recálculos
```
sincronizados; US-13, US-14 y US-
```
15
ADR-003 Reglas y estados Descuentos, límite diario,
```
reprogramación y cierre; US-01 a
```
US-15
ADR-004 Asignación de cuadrillas Agenda, disponibilidad,
```
sugerencias y ausencias; US-04,
```
US-05 y US-06
ADR-005 Evidencias y cierre Llegada/salida, checklist, firma e
```
incidencias; US-07 a US-11
```