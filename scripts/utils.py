import re
import unicodedata
from pathlib import Path

import pandas as pd

BASE = Path(__file__).resolve().parent.parent
ORIGINALES = BASE / "datos" / "originales"
LIMPIOS = BASE / "datos" / "limpios"

MESES = {"ene": 1, "feb": 2, "mar": 3, "abr": 4, "may": 5, "jun": 6, "jul": 7, "ago": 8, "sep": 9, "sept": 9, "oct": 10, "nov": 11, "dic": 12}
PATRON_FECHA = re.compile(r"^\s*([a-z]+)\.?\s+(\d{1,2}),\s*(\d{4})\s+(\d{1,2}):(\d{2}):(\d{2})\s*([ap])\.?\s*m\.?\s*$")
PATRON_EMPRESA = re.compile(r"^EMP-\d{4}$")
PATRON_PERSONA = re.compile(r"^P-\d{5}$")
TILDES_CIUDAD = {"chia": "Chía", "monteria": "Montería", "jamundi": "Jamundí", "guacari": "Guacarí", "itagui": "Itagüí"}


def sin_tildes(texto):
    texto = unicodedata.normalize("NFD", str(texto))
    return "".join(c for c in texto if unicodedata.category(c) != "Mn")


def fecha_es(valor):
    if pd.isna(valor):
        return pd.NaT
    texto = str(valor).replace("\xa0", " ").lower()
    m = PATRON_FECHA.match(texto)
    if not m:
        return pd.NaT
    mes, dia, anio, hora, minuto, segundo, jornada = m.groups()
    hora = int(hora) % 12 + (12 if jornada == "p" else 0)
    return pd.Timestamp(int(anio), MESES[mes], int(dia), hora, int(minuto), int(segundo))


def ciudad_estandar(valor):
    if pd.isna(valor):
        return pd.NA
    texto = sin_tildes(valor).lower().strip()
    if "," in texto or " y " in texto:
        return "Varias"
    if texto.startswith("bogot"):
        return "Bogotá"
    if texto.startswith(("mede", "medi")) or texto == "medelon":
        return "Medellín"
    if texto in TILDES_CIUDAD:
        return TILDES_CIUDAD[texto]
    return " ".join(p.capitalize() for p in str(valor).strip().split())


def actualizaciones_estandar(valor):
    if pd.isna(valor):
        return pd.NA
    texto = str(valor).strip()
    if texto in ("Sí", "No"):
        return texto
    return "Otro"
