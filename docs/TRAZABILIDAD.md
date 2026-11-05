# Matriz de trazabilidad BRD → regla → componente → prueba (CleanPro)

Estado al 04-nov-2026. "Pendiente" = no hay código todavía; se mantiene visible a propósito
(la rúbrica castiga la falta de trazabilidad, no los huecos reconocidos).

## Reglas de negocio (BRD §4)
| BRD | Regla | Componente | Prueba | Estado |
|-----|-------|-----------|--------|--------|
| RN-01 | 1 persona y 1 h por cada 50 m² + extras | `Solicitud_Sevicio.calcular_cotizacion` (Decimal) | `tests/unit/test_dominio.py::test_calcular_cotizacion`, `::test_cotizacion_sin_error_de_punto_flotante` | Parcial: calcula precio; falta personal/duración (US-02, US-03) y tiempos de extras |
| RN-02a | Máx. 8 h/día por cuadrilla | `Limite_Jornada_Specification` | `tests/unit/test_specifications.py::test_limite_jornada` (límite 8 = cumple, 9 = bloquea) | Implementado |
| RN-02b | Descuento ≤ 10 % sin aprobación gerencial | `Tope_Descuento_Specification` | `::test_tope_descuento` | Parcial: falta la excepción "con aprobación gerencial" |
| RN-02 (combinación) | AND / OR / NOT de Specifications | `And_/Or_/Not_Specification` | `::test_tabla_verdad_and_or`, `::test_not`, `::test_combinacion_de_negocio_and_con_not`, `::test_or_de_reglas_de_negocio` | Implementado |
| RN-03 | Cierre exige geolocalización/hora, checklist 100 % y firma | `Cierre_Conforme_Specification` + `OperacionService.ejecutar_transicion` (422) | `test_specifications.py::test_cierre_conforme_rn03`; `test_operacion_service.py::test_rn03_*`; `test_api.py::test_flujo_completo_con_evidencia_rn03` | Implementado (evidencia por JSON; sin app móvil) |
| RN-04 | Sustitución por guardia; alerta si retraso > 30 min | — | — | Pendiente |
| RN-05 | Cargos extra/visita fallida (15 min) impactan estado de cuenta | — | — | Pendiente |

## Reglas de los fixtures del profesor (PIA)
| Regla | Componente | Prueba | Estado |
|-------|-----------|--------|--------|
| `puede_procesarse`: actor activo AND ≥1 línea AND autorización | `Puede_Procesarse_Specification` | `tests/unit/test_specifications.py::test_puede_procesarse`; `tests/integration/test_fixtures_profesor.py` (60 casos vs oráculo CSV) | Implementado |
| `beneficio_referencia`: preferente AND total ≥ 1500 AND NOT promoción | `Beneficio_Referencia_Specification` | `::test_beneficio_referencia`; 60 casos vs oráculo CSV | Implementado |
| 20 transiciones (aprobar, completar, cancelar, saltar_estado, repetir_aprobacion) | `scripts/run_fixtures.py` → `docs/evidencia/` | `test_runner_genera_evidencia_completa` | Implementado; evento = pendiente (Domain Events) |

## Ciclo de vida (BRD §1–2, PIA)
| Requisito | Componente | Prueba | Estado |
|-----------|-----------|--------|--------|
| SOLICITADO→PROGRAMADO→EN_PROCESO→COMPLETADO; SOLICITADO→CANCELADO | `Validador_Flujo`, `OperacionStateMachine` | `tests/unit/test_state_machine.py` (válidas, 20 inválidas, terminales, flujo feliz, adaptador) y `tests/integration/test_operacion_service.py` | Implementado |
| Transición inválida → 409 | `TransicionInvalidaError` + handler de `DomainError` en `src/api/main.py` | `test_api.py::test_transicion_invalida_409` | Implementado |
| Domain Events (Solicitada, Programada, Iniciada, Completada, Cancelada) | `src/domain/events.py`, `src/application/event_bus.py` | `tests/unit/test_eventos.py`; `test_operacion_service.py::test_flujo_emite_eventos_en_orden`; `GET /{id}/eventos` | Implementado |
| Validar cantidades, capacidad, recurso deshabilitado | `OperacionService.crear_operacion` (400/422) | `test_operacion_service.py::test_cantidad_*`, `test_capacidad_*`, `test_recurso_deshabilitado_422` | Implementado |

## Historias de usuario
| US | Cubierta por | Estado |
|----|--------------|--------|
| US-01 cotizar | `calcular_cotizacion` | Parcial (sin endpoint de cotización) |
| US-02 duración / US-03 personal | — | Pendiente |
| US-04 registrar y programar | state machine + `OperacionService` + `POST /{id}/transicion` | Implementado |
| US-05, US-06 agenda / cuadrilla cercana | `Limite_Jornada_Specification` (solo el tope) | Pendiente |
| US-07 llegada/salida, US-08 checklist, US-09 firma | `Cierre_Conforme_Specification` (evidencia en el cierre) | Parcial (se valida al completar; sin registro independiente por US) |
| US-10, US-11 incidencias | — | Pendiente |
| US-12 cambio de personal | — | Pendiente (RN-04) |
| US-13 adicional, US-14 recálculo | — | Pendiente (RN-05) |
| US-15 reprogramación (20 % si < 24 h) | — | Pendiente |

> El PDF de user stories entregado **no incluye criterios Gherkin**; la rúbrica los exige (≥ 15).

## Diferencias entre el modelo de pruebas del profesor (CSV) y el BRD propio
(Las instrucciones piden documentarlas y no reemplazar los requerimientos propios.)
| Tema | CSV del profesor | BRD del equipo |
|------|------------------|----------------|
| Importe | Σ `precio_mxn × cantidad` por recurso del catálogo | Tarifa por m² (1 persona/1 h por 50 m²) + extras |
| Actores | "contratante" con `es_preferente`/`activo` | Cliente, Coordinador, Supervisor, Cuadrilla, Administración |
| Reglas ilustrativas | `puede_procesarse`, `beneficio_referencia` | RN-01…RN-05 |
| Estados | SOLICITADO…CANCELADO | Mismos 5 estados (coinciden) |
Los fixtures se usan como oráculo de **datos y transiciones**; las reglas de negocio se derivan del BRD.
