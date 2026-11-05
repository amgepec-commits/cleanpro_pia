# Integrante 3 — QA, DevOps y Despliegue (CleanPro)

Entrega de documentos y repo: **6 nov 2026**. Defensa: 9–20 nov.

## 1. Bloqueos encontrados en el código de los Integrantes 1 y 2
(Avísales hoy; tus pruebas y el CI dependen de esto.)

| # | Problema | Dueño | Efecto |
|---|----------|-------|--------|
| 1 | `src/application/operacion_service.py` importa `OperacionStateMachine` (con `.transicionar(accion)` y `.estado_actual.value`), pero `state_machine.py` solo define `Validador_Flujo.Cambiar_Estado(actual, nuevo)`. | 1 | La capa de aplicación y la API de escritura no importan. |
| 2 | `src/domain/*` usa imports sueltos (`from entities import ...`) en vez de `from src.domain.entities import ...`; `domain/__init__.py` contiene `x=1`. | 1 | No se puede importar como paquete; mis tests usan un shim temporal en `tests/conftest.py`. |
| 3 | ~~Faltaban Specifications y Domain Events~~ **Resuelto en el parche** (puede_procesarse, beneficio_referencia, RN-03, eventos). Siguen pendientes RN-04, RN-05 y US-02/03/05/06/10–15. | 1 | Declarar en el reporte. |
| 4 | Typo `Solicitud_Sevicio`; el agregado guarda `Estado` como `str` y no usa la máquina de estados. | 1 | Se arrastra a UML, docs y defensa. |
| 5 | ~~API sin POST/transición~~ **Resuelto en el parche** (la API ya usa el servicio). **Sigue pendiente la DB real**: el estado vive en memoria y se reinicia con la app. | 2 | Sin 201/409/422 ni transiciones por API. Mis tests de escritura están `xfail`. |
| 6 | El servicio distingue 409/422/404 por **texto** de la excepción (`"CONFLICT:"`...) y usa `ValueError` tanto para conflicto como para transición inválida. | 1/2 | La API no puede mapear bien a 400/409. Conviene crear excepciones propias. |
| 7 | Rutas de CSV relativas al cwd (e incluso `/home/bard/actores.csv`). | 2 | Usar `DATA_DIR` (ya está en `.env.example`). |

## 2. Qué trae este kit (copiar a la raíz del repo, respetando carpetas)
- `tests/unit/` y `tests/integration/`: 68 pruebas pasan hoy; 2 módulos se saltan hasta que se corrijan #1 y la falta de FastAPI local.
- `pytest.ini`: cobertura sobre `src`, **falla si < 80 %**.
- `scripts/run_fixtures.py`: evidencia de `transiciones_prueba.csv` (y esqueleto para `casos_prueba.csv`) en `docs/evidencia/`.
- `Dockerfile`, `docker-compose.yml` (db + app + tests), `.env.example`, `.dockerignore`, `.gitignore`.
- `.github/workflows/ci.yml`: tests+cobertura → Docker Compose → deploy hook.
- `render.yaml`: blueprint de Render (web + Postgres).

## 3. Orden de trabajo sugerido (hoy → 6 nov)
1. Mandar la tabla de bloqueos al grupo; pedir que suban a GitHub (para tener historial de commits tuyo).
2. Copiar el kit, `pip install -r requirements-dev.txt`, correr `pytest` y **mirar el % de cobertura real** (no lo pude medir aquí: sin `pytest-cov`).
3. `python scripts/run_fixtures.py` ya procesa `casos_prueba.csv` (120) y `transiciones_prueba.csv` (20) y deja la evidencia en `docs/evidencia/`. Supuesto a confirmar con el profe: `aprobar` = SOLICITADO→PROGRAMADO.
4. Si cobertura < 80 %: probar `domain/main.py` (conviene moverlo a `scripts/`) y agregar tests de repositorio/servicio.
5. `cp .env.example .env` → `docker compose up --build` y `docker compose --profile test run --rm tests`.
6. Subir a GitHub, confirmar CI en verde (captura para el reporte).
7. Desplegar en Render: *New → Blueprint* con `render.yaml` (o Web Service con Docker). Verificar `https://<app>.onrender.com/docs`. Poner la URL en el README. Opcional: guardar el deploy hook como secreto `RENDER_DEPLOY_HOOK_URL`.
8. Evidencias para el PDF: salida de pytest/cobertura, captura del CI, `docker compose` corriendo, Swagger en producción, `evidencia_transiciones.csv`.

## 4. Cosas por definir con el equipo
- **Contrato de API** de escritura: yo supuse `POST /api/operaciones/` (201/409/422) y `POST /api/operaciones/{id}/transicion` con `{"accion": "programar|iniciar|completar|cancelar"}`. Si difiere, ajustar `tests/integration/test_api.py`.
- Plan gratuito de Render: la app se duerme tras inactividad (primer request lento) y el Postgres gratuito expira; abrir la URL antes de la demo.
- La rúbrica pide trazabilidad BRD → regla → componente → prueba: arma la matriz con tus pruebas (cada test cita su regla RN-xx).
