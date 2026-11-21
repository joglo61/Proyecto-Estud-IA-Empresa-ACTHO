# Proyecto EstudIA - ACTHO (PENTA DATA)

Tablero integral de afiliados con actividad, satisfacción y NPS.

## Carpetas
- `datos/originales/`: Excel entregados por ACTHO. No se modifican.
- `datos/contexto/`: instrumento NPS de 90 días e informe de membresías.
- `datos/limpios/`: tablas generadas por los scripts. No se suben a Git.
- `scripts/`: scripts de Python numerados en orden de ejecución.
- `tablero/`: exportes para Looker Studio.
- `docs/`: documentos de entendimiento y diccionario de datos.

## Uso
```
pip install -r requirements.txt
python scripts/01_limpieza.py
```
