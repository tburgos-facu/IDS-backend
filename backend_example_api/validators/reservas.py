from datetime import datetime

from ..utils import construir_error_api


def validar_id(id):
    if id is None:
        return None

    try:
        id_a_int = int(id)
    except ValueError:
        raise ValueError(
            construir_error_api(
                code="invalid_id_format",
                message="El id es invalido",
                description=f"El valor '{id}' no tiene un formato valido",
            )
        )

    if id_a_int <= 0:
        raise ValueError(
            construir_error_api(
                code="invalid id format",
                message="El id es invalido",
                description=f"el valor de {id} no tiene un formato valido",
            )
        )

    return id_a_int


def validar_estado(estado):
    if estado is None:
        return None

    if not estado in ["confirmada", "cancelada", "finalizada"]:
        raise ValueError(
            construir_error_api(
                code="invalid format",
                message="el estado es invalido",
                description=f"el estado {estado} no es valido",
            )
        )
    return estado


def validar_fechas(fecha_desde, fecha_hasta):
    formato = "%Y-%m-%d"
    fecha_desde_convertida = None
    fecha_hasta_convertida = None

    if fecha_desde is None and fecha_hasta is None:
        return None, None

    if fecha_desde is not None:
        try:
            fecha_desde_convertida = datetime.strptime(fecha_desde, formato)
        except ValueError:
            raise ValueError(
                construir_error_api(
                    code="invalid format",
                    message="el estado es valido",
                    description=f"la fecha {fecha_desde} no es valida",
                )
            )
    if fecha_hasta is not None:
        try:
            fecha_hasta_convertida = datetime.strptime(fecha_hasta, formato)
        except ValueError:
            raise ValueError(
                construir_error_api(
                    code="formato invalido",
                    message="el estado no es valido",
                    description=f"la fecha {fecha_hasta} no es valida",
                )
            )
    if fecha_desde is not None and fecha_hasta is not None:
        if fecha_hasta_convertida < fecha_desde_convertida:
            raise ValueError(
                construir_error_api(
                    code="invalid format",
                    message="las fechas se superponen",
                    description=f"la fecha desde {fecha_desde_convertida} es mayor a la fecha hasta {fecha_hasta_convertida}",
                )
            )
    return fecha_desde_convertida, fecha_hasta_convertida


def validar_reserva(body):
    id_socio = body.get("id_socio")
    id_cancha = body.get("id_cancha")
    fecha_hora_inicio = body.get("fecha_hora_inicio")
    fecha_hora_fin = body.get("fecha_hora_fin")

    formato = "%Y-%m-%dT%H:%M:%S.%f%z"

    if id_socio is None:
        raise ValueError(
            construir_error_api(
                code="invalid format",
                message="el id de socio es invalido",
                description=f"el id del socio {id_socio} no es valido",
            )
        )

    if type(id_socio) is not int:
        raise ValueError(
            construir_error_api(
                code="invalid format",
                message="el id del socio no es un enter",
                description=f"el id del socio {id_socio} no es un entero",
            )
        )

    if id_cancha is None:
        raise ValueError(
            construir_error_api(
                code="invalid format",
                message="el id de la cancha en None",
                description=f"el id de la cancha {id_cancha} no es valido",
            )
        )

    if type(id_cancha) is not int:
        raise ValueError(
            construir_error_api(
                code="invalid format",
                message="el id de la cancha no es un entero",
                description=f"el id {id_cancha} no es un entero",
            )
        )

    try:
        inicio_convertido = datetime.strptime(fecha_hora_inicio, formato)
    except (ValueError, TypeError):
        raise ValueError(
            construir_error_api(
                code="formato no valido",
                message=" el formato de la hora no es valido",
                description=f"el formato de hora inicio {fecha_hora_inicio} no es valido",
            )
        )

    try:
        fin_convertido = datetime.strptime(fecha_hora_fin, formato)
    except (ValueError, TypeError):
        raise ValueError(
            construir_error_api(
                code="formato no valido",
                message="el formato de la hora no es valido",
                description=f"el formato de hora fin {fecha_hora_fin} no es valido",
            )
        )

    return {
        "id_socio": id_socio,
        "id_cancha": id_cancha,
        "fecha_hora_inicio": inicio_convertido,
        "fecha_hora_fin": fin_convertido,
    }


def validar_cambio_estado(body):
    if not isinstance(body, dict):
        raise ValueError(
            construir_error_api(
                code="invalid format",
                message="el cuerpo es invalido",
                description="no se mando un json con el estado de la reserva",
            )
        )

    for campo in body.keys():
        if campo != "estado":
            raise ValueError(
                construir_error_api(
                    code="invalid format",
                    message="hay campos no permitidos",
                    description=f"el campo {campo} no esta permitido, solo se puede mandar estado",
                )
            )

    estado = body.get("estado")

    if estado not in ["confirmada", "cancelada", "finalizada"]:
        raise ValueError(
            construir_error_api(
                code="invalid format",
                message="el estado es invalido",
                description=f"el estado {estado} no es valido",
            )
        )

    return estado


def validar_paginacion(limit, offset):
    if not str(limit).isdigit() or not str(offset).isdigit():
        raise ValueError(
            construir_error_api(
                code="invalid format",
                message="la paginacion es invalida",
                description="_limit y _offset tienen que ser numeros enteros",
            )
        )

    limit = int(limit)
    offset = int(offset)

    if limit < 1 or limit > 100:
        raise ValueError(
            construir_error_api(
                code="invalid format",
                message="la paginacion es invalida",
                description=f"_limit tiene que estar entre 1 y 100, se mando {limit}",
            )
        )

    return limit, offset
