"""Ejecuta transiciones_prueba.csv (20) y casos_prueba.csv (120) del profesor.

Uso (desde cualquier carpeta):  python scripts/run_fixtures.py
Lee los CSV de la raíz del repo y escribe evidencia en docs/evidencia/:
  - transiciones_resultado.csv  (columnas del profe + resultado_alumno + estado_final, excepcion, evento)
  - casos_resultado.csv         (columnas del profe + resultado_alumno + candidato)
  - RESUMEN.md
Supuestos (confirmar con el profesor): ver ACCIONES abajo.
"""
import csv
import os
import sys
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
os.chdir(ROOT)  # el repositorio de datos usa rutas relativas
sys.path.insert(0, str(ROOT))

from src.application.operacion_service import OperacionService  # noqa: E402
from src.domain.specifications import (Beneficio_Referencia_Specification,  # noqa: E402
                                       Puede_Procesarse_Specification)

EVID = ROOT / "docs" / "evidencia"
# accion_sugerida del profesor -> acciones de la máquina de estados (supuesto)
ACCIONES = {
    "aprobar": ["programar"],                   # SOLICITADO -> PROGRAMADO
    "repetir_aprobacion": ["programar", "programar"],  # la 2a debe fallar
    "completar": ["completar"],                 # SOLICITADO -> COMPLETADO (salto)
    "saltar_estado": ["iniciar"],               # SOLICITADO -> EN_PROCESO (salto)
    "cancelar": ["cancelar"],                   # SOLICITADO -> CANCELADO
}
REGLAS = {
    "validar_operacion": Puede_Procesarse_Specification(),
    "evaluar_beneficio": Beneficio_Referencia_Specification(),
}


def leer(nombre):
    with open(ROOT / nombre, encoding="utf-8-sig", newline="") as f:
        return list(csv.DictReader(f))


def escribir(ruta, filas):
    EVID.mkdir(parents=True, exist_ok=True)
    with open(ruta, "w", encoding="utf-8-sig", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(filas[0]))
        w.writeheader()
        w.writerows(filas)


def correr_transiciones():
    salida = []
    for fila in leer("transiciones_prueba.csv"):
        op_id, accion = fila["operacion_id"], fila["accion_sugerida"]
        pasos = ACCIONES.get(accion)
        estado, excepcion, resultado = fila["estado_inicial"], "", "OK"
        if pasos is None:
            resultado, excepcion = "EXCEPCION", f"AccionNoMapeada: {accion}"
        else:
            try:
                for paso in pasos:
                    estado = OperacionService.ejecutar_transicion(op_id, paso)["estado_actual"]
            except Exception as exc:  # se registra la excepción tal cual
                resultado, excepcion = "EXCEPCION", f"{type(exc).__name__}: {exc}"
                from src.infrastructure.repository import db
                estado = db.operaciones[op_id]["estado_actual"]
        fila.update(resultado_alumno=resultado, estado_final=estado, excepcion=excepcion,
                    evento="NO_IMPLEMENTADO (Domain Events pendientes)")
        salida.append(fila)
    escribir(EVID / "transiciones_resultado.csv", salida)
    return salida


def correr_casos():
    salida = []
    for fila in leer("casos_prueba.csv"):
        candidato = OperacionService.construir_candidato(fila["operacion_id"])
        cumple = REGLAS[fila["tipo_prueba"]].is_satisfied_by(candidato)
        fila.update(resultado_alumno="CUMPLE" if cumple else "NO_CUMPLE",
                    candidato="; ".join(f"{k}={v}" for k, v in candidato.items()))
        salida.append(fila)
    escribir(EVID / "casos_resultado.csv", salida)
    return salida


if __name__ == "__main__":
    t, c = correr_transiciones(), correr_casos()
    resumen = ["# Resumen de ejecución de fixtures", "",
               f"Transiciones: {len(t)} -> {dict(Counter((x['accion_sugerida'], x['estado_final']) for x in t))}", "",
               f"Casos: {len(c)} -> {dict(Counter((x['tipo_prueba'], x['resultado_alumno']) for x in c))}", ""]
    (EVID / "RESUMEN.md").write_text("\n".join(resumen), encoding="utf-8")
    print("\n".join(resumen))
