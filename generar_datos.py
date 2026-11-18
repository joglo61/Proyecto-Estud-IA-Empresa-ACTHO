import random
from datetime import date, timedelta
from pathlib import Path

import pandas as pd
from faker import Faker

SEMILLA = 42
N_AFILIADOS = 500
N_ACTIVIDADES = 60
HOY = date.today()
SALIDA = Path("data")

PERFILES = {
    "sano": 0.60,
    "en_riesgo": 0.20,
    "solo_inactivo": 0.10,
    "solo_insatisfecho": 0.10,
}
SEMAFORO_REAL = {
    "sano": "verde",
    "en_riesgo": "rojo",
    "solo_inactivo": "amarillo",
    "solo_insatisfecho": "amarillo",
}
PLAN = {
    "sano": {"reciente": (3, 8), "antigua": (0, 6)},
    "en_riesgo": {"reciente": (0, 0), "antigua": (1, 4)},
    "solo_inactivo": {"reciente": (0, 0), "antigua": (0, 4)},
    "solo_insatisfecho": {"reciente": (2, 6), "antigua": (0, 4)},
}
PERFILES_BAJOS = ("en_riesgo", "solo_insatisfecho")
TIPOS_ACTIVIDAD = ["taller", "webinar", "evento", "comunidad"]
COMENTARIOS_NEGATIVOS = [
    "El contenido fue muy general",
    "El horario no me permitió asistir completo",
    "El precio no se justifica",
    "Hubo problemas de logística y conexión",
    "Faltó profundidad en los temas",
]
COMENTARIOS_POSITIVOS = [
    "Muy buen contenido",
    "Excelente organización",
    "Los ponentes fueron muy buenos",
    "Buen espacio para conectar con otros",
    "Aprendí herramientas útiles",
]

random.seed(SEMILLA)
Faker.seed(SEMILLA)
fake = Faker("es_CO")
SALIDA.mkdir(exist_ok=True)


def elegir(lista, minimo, maximo):
    k = random.randint(minimo, maximo)
    return random.sample(lista, min(k, len(lista)))


def asignar_perfiles():
    perfiles = []
    for perfil, proporcion in PERFILES.items():
        perfiles += [perfil] * round(N_AFILIADOS * proporcion)
    while len(perfiles) < N_AFILIADOS:
        perfiles.append("sano")
    perfiles = perfiles[:N_AFILIADOS]
    random.shuffle(perfiles)
    return perfiles


def crear_actividades():
    actividades = [
        {
            "id_actividad": f"ACT-{i:03d}",
            "tipo_actividad": random.choice(TIPOS_ACTIVIDAD),
            "fecha": HOY - timedelta(days=random.randint(1, 365)),
        }
        for i in range(1, N_ACTIVIDADES + 1)
    ]
    recientes = [a for a in actividades if (HOY - a["fecha"]).days <= 90]
    antiguas = [a for a in actividades if (HOY - a["fecha"]).days > 90]
    return actividades, recientes, antiguas


def crear_afiliado(numero, perfil):
    afiliacion = HOY - timedelta(days=random.randint(30, 1100))
    anios = -(-(HOY - afiliacion).days // 365)
    vencimiento = afiliacion + timedelta(days=365 * anios)
    if random.random() < 0.05:
        vencimiento -= timedelta(days=365)
    tipo = random.choices(["empresa", "profesional"], weights=[0.6, 0.4])[0]
    return {
        "id_afiliado": f"A-{numero:04d}",
        "nombre": fake.company() if tipo == "empresa" else fake.name(),
        "correo": fake.company_email() if tipo == "empresa" else fake.email(),
        "tipo": tipo,
        "fecha_afiliacion": afiliacion,
        "fecha_vencimiento": vencimiento,
        "estado": "activo" if vencimiento >= HOY else "vencido",
    }


def crear_encuesta(id_afiliado, actividad, perfil, numero):
    if perfil in PERFILES_BAJOS:
        nps = random.randint(0, 6)
        calidad = random.randint(1, 3)
        textos = COMENTARIOS_NEGATIVOS
    else:
        nps = random.choice([7, 8, 9, 9, 10, 10])
        calidad = random.randint(4, 5)
        textos = COMENTARIOS_POSITIVOS
    comentario = random.choice(textos) if random.random() < 0.7 else ""
    return {
        "id_encuesta": f"E-{numero:06d}",
        "id_afiliado": id_afiliado,
        "id_actividad": actividad["id_actividad"],
        "fecha": actividad["fecha"],
        "nps": nps,
        "calidad": calidad,
        "comentario": comentario,
    }


def generar_tablas():
    actividades, recientes, antiguas = crear_actividades()
    afiliados, participacion, encuestas, verdad = [], [], [], []
    for numero, perfil in enumerate(asignar_perfiles(), start=1):
        afiliado = crear_afiliado(numero, perfil)
        id_afiliado = afiliado["id_afiliado"]
        afiliados.append(afiliado)
        verdad.append(
            {
                "id_afiliado": id_afiliado,
                "perfil": perfil,
                "semaforo_real": SEMAFORO_REAL[perfil],
            }
        )
        plan = PLAN[perfil]
        asistidas = elegir(recientes, *plan["reciente"]) + elegir(
            antiguas, *plan["antigua"]
        )
        for actividad in asistidas:
            participacion.append(
                {
                    "id_participacion": f"P-{len(participacion) + 1:06d}",
                    "id_afiliado": id_afiliado,
                    "id_actividad": actividad["id_actividad"],
                    "tipo_actividad": actividad["tipo_actividad"],
                    "fecha": actividad["fecha"],
                    "asistio": "si",
                }
            )
        for actividad in elegir(
            [a for a in actividades if a not in asistidas], 0, 2
        ):
            participacion.append(
                {
                    "id_participacion": f"P-{len(participacion) + 1:06d}",
                    "id_afiliado": id_afiliado,
                    "id_actividad": actividad["id_actividad"],
                    "tipo_actividad": actividad["tipo_actividad"],
                    "fecha": actividad["fecha"],
                    "asistio": "no",
                }
            )
        responde = [random.random() < 0.6 for _ in asistidas]
        if perfil in PERFILES_BAJOS and asistidas and not any(responde):
            responde[0] = True
        for actividad, respondio in zip(asistidas, responde):
            if respondio:
                encuestas.append(
                    crear_encuesta(id_afiliado, actividad, perfil, len(encuestas) + 1)
                )
    return (
        pd.DataFrame(afiliados),
        pd.DataFrame(participacion),
        pd.DataFrame(encuestas),
        pd.DataFrame(verdad),
    )


def ensuciar(afiliados, participacion, encuestas, verdad):
    errores = []

    def registrar(tabla, tipo, cantidad):
        errores.append({"tabla": tabla, "tipo_error": tipo, "cantidad": cantidad})

    afiliados = afiliados.copy()
    afiliados["fecha_afiliacion"] = afiliados["fecha_afiliacion"].astype(str)
    afiliados["fecha_vencimiento"] = afiliados["fecha_vencimiento"].astype(str)
    # Solo formatos sin ambigüedad: día antes del mes, o año primero.
    formatos_fecha = ["%d/%m/%Y", "%Y/%m/%d"]

    def fecha_desordenada(s):
        return date.fromisoformat(s).strftime(random.choice(formatos_fecha))

    afiliados = pd.concat(
        [afiliados, afiliados.sample(70, random_state=SEMILLA)], ignore_index=True
    )
    registrar("afiliados", "filas duplicadas", 70)

    indices = afiliados.sample(60, random_state=SEMILLA + 1).index
    afiliados.loc[indices, "correo"] = ""
    registrar("afiliados", "correo vacío", 60)

    indices = afiliados.sample(50, random_state=SEMILLA + 6).index
    afiliados.loc[indices, "correo"] = afiliados.loc[indices, "correo"].map(
        lambda s: random.choice([s.upper(), " " + s, s + " "])
    )
    registrar("afiliados", "correo en mayúsculas o con espacios", 50)

    indices = afiliados.sample(60, random_state=SEMILLA + 10).index
    afiliados.loc[indices, "estado"] = afiliados.loc[indices, "estado"].map(
        lambda s: random.choice([s.upper(), s.capitalize(), s + " "])
    )
    registrar("afiliados", "estado con mayúsculas o espacios", 60)

    indices = afiliados.sample(80, random_state=SEMILLA + 2).index
    afiliados.loc[indices, "fecha_afiliacion"] = afiliados.loc[
        indices, "fecha_afiliacion"
    ].map(fecha_desordenada)
    registrar("afiliados", "fecha_afiliacion en dd/mm/aaaa o aaaa/mm/dd", 80)

    indices = afiliados.sample(100, random_state=SEMILLA + 3).index
    afiliados.loc[indices, "tipo"] = afiliados.loc[indices, "tipo"].map(
        lambda s: random.choice([s.upper(), s.capitalize(), s + " ", " " + s])
    )
    registrar("afiliados", "tipo con mayúsculas o espacios", 100)

    indices = afiliados.sample(70, random_state=SEMILLA + 7).index
    afiliados.loc[indices, "nombre"] = afiliados.loc[indices, "nombre"].map(
        lambda s: random.choice([s.upper(), s.lower(), "  " + s, s + "  "])
    )
    registrar("afiliados", "nombre con mayúsculas o espacios", 70)

    participacion = participacion.copy()
    participacion["fecha"] = participacion["fecha"].astype(str)
    participacion = pd.concat(
        [participacion, participacion.sample(300, random_state=SEMILLA)],
        ignore_index=True,
    )
    registrar("participacion", "filas duplicadas", 300)

    candidatos = participacion[participacion["asistio"] == "si"]
    indices = candidatos.sample(400, random_state=SEMILLA + 4).index
    participacion.loc[indices, "asistio"] = [
        random.choice(["Sí", "SI", "Si", "s", "1"]) for _ in indices
    ]
    registrar("participacion", "asistio con variantes de 'si'", 400)

    candidatos = participacion[participacion["asistio"] == "no"]
    indices = candidatos.sample(min(200, len(candidatos)), random_state=SEMILLA + 8).index
    participacion.loc[indices, "asistio"] = [
        random.choice(["No", "NO", "n", "0"]) for _ in indices
    ]
    registrar("participacion", "asistio con variantes de 'no'", len(indices))

    indices = participacion.sample(300, random_state=SEMILLA + 9).index
    participacion.loc[indices, "fecha"] = participacion.loc[indices, "fecha"].map(
        fecha_desordenada
    )
    registrar("participacion", "fecha en dd/mm/aaaa o aaaa/mm/dd", 300)

    indices = participacion.sample(250, random_state=SEMILLA + 11).index
    participacion.loc[indices, "tipo_actividad"] = participacion.loc[
        indices, "tipo_actividad"
    ].map(lambda s: random.choice([s.upper(), s.capitalize(), s + " ", s + "s"]))
    registrar("participacion", "tipo_actividad con mayúsculas, espacios o plural", 250)

    indices = participacion.sample(150, random_state=SEMILLA + 12).index
    participacion.loc[indices, "id_afiliado"] = participacion.loc[
        indices, "id_afiliado"
    ].map(lambda s: random.choice([s.lower(), " " + s, s + " ", s.replace("-", "")]))
    registrar("participacion", "id_afiliado en minúscula, con espacios o sin guion", 150)

    encuestas = encuestas.copy()
    encuestas["fecha"] = encuestas["fecha"].astype(str)
    sanos = verdad.loc[verdad["perfil"] == "sano", "id_afiliado"]
    candidatos = encuestas[encuestas["id_afiliado"].isin(sanos)]
    indices = candidatos.sample(160, random_state=SEMILLA + 5).index
    encuestas["nps"] = encuestas["nps"].astype("object")
    encuestas.loc[indices[:70], "nps"] = None
    encuestas.loc[indices[70:110], "nps"] = [
        random.choice([11, 15, -1]) for _ in indices[70:110]
    ]
    encuestas.loc[indices[110:], "nps"] = [
        random.choice([f"{n}.0", f" {n}", f"{n}/10"])
        for n in encuestas.loc[indices[110:], "nps"]
    ]
    registrar("encuestas", "nps vacío", 70)
    registrar("encuestas", "nps fuera de rango (11, 15, -1)", 40)
    registrar("encuestas", "nps como texto ('9.0', ' 9', '9/10')", 50)

    indices = candidatos.sample(60, random_state=SEMILLA + 13).index
    encuestas["calidad"] = encuestas["calidad"].astype("object")
    encuestas.loc[indices[:30], "calidad"] = None
    encuestas.loc[indices[30:], "calidad"] = [
        random.choice([0, 6, 10]) for _ in indices[30:]
    ]
    registrar("encuestas", "calidad vacía", 30)
    registrar("encuestas", "calidad fuera de rango (0, 6, 10)", 30)

    indices = encuestas.sample(200, random_state=SEMILLA + 14).index
    encuestas.loc[indices, "comentario"] = encuestas.loc[indices, "comentario"].map(
        lambda s: random.choice([s.upper(), "  " + s + "  ", s + "!!!", "N/A", "-"])
    )
    registrar("encuestas", "comentario en mayúsculas, con espacios, 'N/A' o '-'", 200)

    indices = encuestas.sample(120, random_state=SEMILLA + 15).index
    encuestas.loc[indices, "fecha"] = encuestas.loc[indices, "fecha"].map(
        fecha_desordenada
    )
    registrar("encuestas", "fecha en dd/mm/aaaa o aaaa/mm/dd", 120)

    encuestas = pd.concat(
        [encuestas, encuestas.sample(150, random_state=SEMILLA)], ignore_index=True
    )
    registrar("encuestas", "filas duplicadas", 150)

    return afiliados, participacion, encuestas, pd.DataFrame(errores)


def guardar(tablas):
    nombres = [
        "afiliados",
        "participacion",
        "encuestas",
        "verdad_conocida",
        "errores_insertados",
    ]
    for nombre, tabla in zip(nombres, tablas):
        tabla.to_csv(SALIDA / f"{nombre}.csv", index=False, encoding="utf-8-sig")
        print(f"{nombre}.csv: {len(tabla)} filas")


def main():
    afiliados, participacion, encuestas, verdad = generar_tablas()
    afiliados, participacion, encuestas, errores = ensuciar(
        afiliados, participacion, encuestas, verdad
    )
    guardar([afiliados, participacion, encuestas, verdad, errores])


if __name__ == "__main__":
    main()