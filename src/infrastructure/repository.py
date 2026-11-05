import os
from decimal import Decimal
from pathlib import Path

import pandas as pd


def _csv(nombre: str) -> Path:
  """Ruta del CSV; DATA_DIR (variable de entorno) permite separar datos del código."""
  return Path(os.getenv("DATA_DIR", ".")) / nombre


class DataRepository:

  _instance = None

  def __new__(cls):
    if cls._instance is None:
      cls._instance = super(DataRepository, cls).__new__(cls)
      cls._instance.actores = {}
      cls._instance.catalogo = {}
      cls._instance.operaciones = {}
      cls._instance.detalles = {}
      cls._instance.cargar_datos()
    return cls._instance

  def reiniciar(self):
    """Vuelve a cargar los CSV (útil en pruebas para aislar estado)."""
    for coleccion in (self.actores, self.catalogo, self.operaciones, self.detalles):
      coleccion.clear()
    self.cargar_datos()

  def cargar_datos(self):
    # Cargar actores.csv
    df_act = pd.read_csv(_csv("actores.csv"))
    for _, row in df_act.iterrows():
      self.actores[str(row["actor_id"])] = {
          "actor_id": str(row["actor_id"]),
          "nombre": str(row["nombre"]),
          "es_preferente": int(row["es_preferente"]),
          "activo": int(row["activo"]),
          "ciudad": str(row["ciudad"]),
      }

    # Cargar catalogo.csv
    df_cat = pd.read_csv(_csv("catalogo.csv"))
    for _, row in df_cat.iterrows():
      self.catalogo[str(row["recurso_id"])] = {
          "recurso_id": str(row["recurso_id"]),
          "descripcion": str(row["descripcion"]),
          "precio_mxn": float(row["precio_mxn"]),
          "capacidad_o_stock": int(row["capacidad_o_stock"]),
          "habilitado": int(row["habilitado"]),
      }

    # Cargar operaciones.csv y detalle_operaciones.csv
    df_ops = pd.read_csv(_csv("operaciones.csv"))
    for _, row in df_ops.iterrows():
      self.operaciones[str(row["operacion_id"])] = {
          "operacion_id": str(row["operacion_id"]),
          "actor_id": str(row["actor_id"]),
          "estado_inicial": str(row["estado_inicial"]),
          "estado_actual": str(row["estado_inicial"]),
          "fecha_solicitud": str(row["fecha_solicitud"]),
          "promocion_activa": int(row["promocion_activa"]),
          "autorizado": int(row["autorizado"]),
          "referencia": str(row["referencia"]),
      }

    df_det = pd.read_csv(_csv("detalle_operaciones.csv"))
    for _, row in df_det.iterrows():
      op_id = str(row["operacion_id"])
      if op_id not in self.detalles:
        self.detalles[op_id] = []
      self.detalles[op_id].append({
          "operacion_id": op_id,
          "recurso_id": str(row["recurso_id"]),
          "cantidad": int(row["cantidad"]),
      })


db = DataRepository()
