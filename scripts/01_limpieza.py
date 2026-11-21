"""Limpieza de las bases de datos de ACTHO (datos/originales -> datos/limpios)."""
from pathlib import Path

import pandas as pd

BASE = Path(__file__).resolve().parent.parent
ORIGINALES = BASE / "datos" / "originales"
LIMPIOS = BASE / "datos" / "limpios"


# --- Etapa 1: Base de datos afiliados ACTHO ---


# --- Etapa 2: Reportes de Zoho (Afiliaciones, Renovaciones, Elite/Premium, Oportunidades) ---


# --- Etapa 3: Encuestas (hoja "Responses") ---


# --- Etapa 4: Asistencia EAFIT, Consolidado KAM, Nuevos afiliados ---


# --- Etapa 5: Guardar resultados en datos/limpios ---


if __name__ == "__main__":
    print("ORIGINALES:", ORIGINALES)
    print("Archivos:", len(list(ORIGINALES.glob("*.xlsx"))))
