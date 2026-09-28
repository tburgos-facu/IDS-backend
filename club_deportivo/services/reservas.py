from datetime import datetime, timedelta, timezone

from .. import db
from ..utils import construir_error_api

# VOY CONSTRUYENDO LA QUERY A PARTIR DE QUE PARAEMTROS ME LLEGAN. EVALUO SI EL PARAMETRO VIENE EN NONE
# EN CASO DE QUE NO VENGA EN NONE ES PORQUE EXISTE EL PARAMETRO Y ES UN FILTRO ASIQUE DEBE ESTAR EN LA QUERY.


def listar_reservas(
    id_cancha, id_socio, estado, fecha_hasta, fecha_desde, limit, offset
):
    parametros = {}
    condiciones = []
    sql = "SELECT * FROM reservas"
    sql_total = "SELECT COUNT(*) AS total FROM reservas"
    if id_cancha is not None:
        condiciones.append("id_cancha = :id_cancha")
        parametros["id_cancha"] = id_cancha

    if id_socio is not None:
        condiciones.append("id_socio = :id_socio")
        parametros["id_socio"] = id_socio

    if estado is not None:
        condiciones.append("estado = :estado")
        parametros["estado"] = estado
    if fecha_hasta is not None:
        condiciones.append("DATE(fecha_hora_inicio) <= :fecha_hasta")
        parametros["fecha_hasta"] = fecha_hasta

    if fecha_desde is not None:
        condiciones.append("DATE(fecha_hora_inicio) >= :fecha_desde")
        parametros["fecha_desde"] = fecha_desde

    if condiciones:
        sql += " WHERE " + " AND ".join(condiciones)
        sql_total += " WHERE " + " AND ".join(condiciones)

    # el total se cuenta con los mismos filtros pero sin paginar, para armar los links
    total = db.ejecutar_consulta(sql_total, parametros)[0]["total"]

    sql += " ORDER BY  id ASC LIMIT :limit OFFSET :offset"
    parametros["limit"] = limit
    parametros["offset"] = offset
    print(repr(sql))
    print(parametros)
    reservas = db.ejecutar_consulta(sql, parametros)

    return [construir_reserva_dto(reserva) for reserva in reservas], total


def crear_reserva(datos_reserva):

    inicio = datos_reserva["fecha_hora_inicio"]
    fin = datos_reserva["fecha_hora_fin"]
    # reviso los datos con las reglas que me pusieron, que no haya superposicion de horarios, que exista la cancha y socio.
    socio = db.ejecutar_consulta(
        "SELECT * FROM socios WHERE id = :id_socio",
        {"id_socio": datos_reserva["id_socio"]},
    )
    # pruebo que el socio este cargado en DB
    if not socio:
        raise ValueError(
            construir_error_api(
                code="error id socio",
                message="el id del socio no esta en la base de datos",
                description=f"el id {datos_reserva['id_socio']} no existe",
            ),
            404,
        )

    cancha = db.ejecutar_consulta(
        "SELECT * FROM canchas WHERE id = :id_cancha",
        {"id_cancha": datos_reserva["id_cancha"]},
    )
    # Pruebo que la cancha este en la DB
    if not cancha:
        raise ValueError(
            construir_error_api(
                code="error id cancha",
                message="la cancha no existe",
                description=f"el id de cancha {datos_reserva['id_cancha']} no existe",
            ),
            404,
        )

    # me fijo si la reserva se superpone con otra, osea que compartan en algun momento el mismo horario, excepto los bordes

    superponen = db.ejecutar_consulta(
        "SELECT * FROM reservas WHERE id_cancha = :id_cancha AND estado = 'confirmada' AND fecha_hora_inicio < :fecha_hasta AND fecha_hora_fin > :fecha_desde",
        {
            "id_cancha": datos_reserva["id_cancha"],
            "fecha_hasta": fin,
            "fecha_desde": inicio,
        },
    )

    if superponen:
        raise ValueError(
            construir_error_api(
                code="error en reserva",
                message="la reserva se superpone con otra",
                description=f"alguno de los horarios {inicio, fin} se superpone con otra reserva",
            ),
            409,
        )
    # veo si la cancha y el socio estan activos
    if not socio[0]["activo"]:
        raise ValueError(
            construir_error_api(
                code="error en reserva",
                message="socio no esta activo",
                description=f"el socio {datos_reserva['id_socio']} no esta disponible",
            ),
            409,
        )

    if not cancha[0]["activa"]:
        raise ValueError(
            construir_error_api(
                code="error en reserva",
                message="cancha no esta activo",
                description=f"la cancha {datos_reserva['id_cancha']} no esta disponible",
            ),
            409,
        )

    reservas_socio = db.ejecutar_consulta(
        "SELECT * FROM reservas WHERE id_socio = :id_socio AND estado = 'confirmada' AND fecha_hora_inicio < :fecha_hasta AND fecha_hora_fin > :fecha_desde",
        {
            "id_socio": datos_reserva["id_socio"],
            "fecha_hasta": fin,
            "fecha_desde": inicio,
        },
    )
    # veo que el socio no tenga otra reserva creada que se superponga con la nueva
    if reservas_socio:
        raise ValueError(
            construir_error_api(
                code="error en reserva",
                message="el socio tiene una reserva que se superpone",
                description=f"el socio {datos_reserva['id_socio']} ya tiene una reserva en ese lapso de tiempo",
            ),
            409,
        )

    if fin <= inicio:
        raise ValueError(
            construir_error_api(
                code="invalid_time_range",
                message="El intervalo de la reserva es invalido",
                description="La fecha y hora de fin debe ser posterior a la de inicio",
            ),
            400,
        )

    zona_horaria = timezone(timedelta(hours=-3))
    ahora = datetime.now(zona_horaria)

    if inicio <= ahora:
        raise ValueError(
            construir_error_api(
                code="reservation_not_future",
                message="La reserva debe comenzar en el futuro",
                description="La fecha y hora de inicio debe ser posterior al momento actual",
            ),
            400,
        )

    if (
        inicio.minute != 0
        or inicio.second != 0
        or inicio.microsecond != 0
        or fin.minute != 0
        or fin.second != 0
        or fin.microsecond != 0
    ):
        raise ValueError(
            construir_error_api(
                code="invalid_reservation_time",
                message="El horario de la reserva es invalido",
                description="Las reservas deben comenzar y terminar en horas en punto",
            ),
            400,
        )

    if inicio.date() != fin.date():
        raise ValueError(
            construir_error_api(
                code="reservation_crosses_midnight",
                message="La reserva no puede atravesar la medianoche",
                description="El inicio y el fin de la reserva deben pertenecer al mismo dia",
            ),
            400,
        )

    if inicio.hour < 8 or fin.hour > 23:
        raise ValueError(
            construir_error_api(
                code="outside_club_hours",
                message="La reserva esta fuera del horario del club",
                description="El horario permitido para reservas es de 08:00 a 23:00",
            ),
            400,
        )

    duracion_segundos = (fin - inicio).total_seconds()

    if duracion_segundos not in (3600, 7200, 10800):
        raise ValueError(
            construir_error_api(
                code="invalid_reservation_duration",
                message="La duracion de la reserva es invalida",
                description="La reserva debe durar entre 1 y 3 horas completas",
            ),
            400,
        )

        # BUSCO EL PRECIO POR HORA Y CALCULO EL TOTAL DE HORAS DE LA RESERVA PARA CALCULAR EL TOTAL DE LA CANCHA
    precio_x_hora = cancha[0]["precio_hora"]
    duracion = fin - inicio
    horas = int(duracion.total_seconds() / 3600)
    total = horas * precio_x_hora

    sql = """INSERT INTO reservas (
        id_socio,
        id_cancha,
        fecha_hora_inicio,
        fecha_hora_fin,
        estado,
        precio_hora,
        precio_total

             )

        VALUES(
        :id_socio,
        :id_cancha,
        :fecha_desde,
        :fecha_hasta,
        :estado,
        :precio_hora,
        :total

        )"""

    parametros = {
        "id_socio": datos_reserva["id_socio"],
        "id_cancha": datos_reserva["id_cancha"],
        "fecha_desde": inicio,
        "fecha_hasta": fin,
        "estado": "confirmada",
        "precio_hora": precio_x_hora,
        "total": total,
    }

    id_reserva = db.ejecutar_mutacion(sql, parametros)

    return id_reserva


def construir_reserva_dto(reserva: dict) -> dict:
    formato = "%Y-%m-%dT%H:%M:%S.%f-03:00"
    return {
        "id": reserva["id"],
        "id_socio": reserva["id_socio"],
        "id_cancha": reserva["id_cancha"],
        "fecha_hora_inicio": reserva["fecha_hora_inicio"].strftime(formato),
        "fecha_hora_fin": reserva["fecha_hora_fin"].strftime(formato),
        "estado": reserva["estado"],
        "precio_hora": reserva["precio_hora"],
        "precio_total": reserva["precio_total"],
    }


def buscar_reserva(id_reserva):
    reserva = db.ejecutar_consulta(
        "SELECT * FROM reservas WHERE id = :id", {"id": id_reserva}
    )
    if not reserva:
        return None
    return reserva[0]


def obtener_reserva_por_id(id_reserva):
    reserva = buscar_reserva(id_reserva)
    if reserva is None:
        return None
    return construir_reserva_dto(reserva)


def cambiar_estado_reserva(id_reserva, nuevo_estado):
    reserva = buscar_reserva(id_reserva)
    if reserva is None:
        return None

    estado_actual = reserva["estado"]

    # si piden el mismo estado que ya tiene no se cambia nada
    if nuevo_estado == estado_actual:
        return construir_reserva_dto(reserva)

    # las canceladas y finalizadas ya no pueden cambiar
    if estado_actual != "confirmada":
        raise ValueError(
            construir_error_api(
                code="error en reserva",
                message="la reserva no puede cambiar de estado",
                description=f"la reserva {id_reserva} esta {estado_actual} y no se puede modificar",
            )
        )

    # la base guarda las fechas sin zona horaria, asique ahora tambien va sin zona
    zona_horaria = timezone(timedelta(hours=-3))
    ahora = datetime.now(zona_horaria).replace(tzinfo=None)

    if nuevo_estado == "cancelada" and ahora >= reserva["fecha_hora_inicio"]:
        raise ValueError(
            construir_error_api(
                code="error en reserva",
                message="la reserva no se puede cancelar",
                description=f"la reserva {id_reserva} ya empezo",
            )
        )

    if nuevo_estado == "finalizada" and ahora < reserva["fecha_hora_fin"]:
        raise ValueError(
            construir_error_api(
                code="error en reserva",
                message="la reserva no se puede finalizar",
                description=f"la reserva {id_reserva} todavia no termino",
            )
        )

    db.ejecutar_mutacion(
        "UPDATE reservas SET estado = :estado WHERE id = :id",
        {"estado": nuevo_estado, "id": id_reserva},
    )

    return obtener_reserva_por_id(id_reserva)
