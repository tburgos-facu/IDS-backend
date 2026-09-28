import logging
from re import sub
from urllib.parse import urlencode

from flask import request

from .constants import ERROR_CODE_INVALID_MIN_VALUE

logger = logging.getLogger(__name__)


def construir_error_api(
    code: str, message: str, description: str, level: str = "error"
) -> dict:
    """Construye un payload de error compatible con el resto de la API."""
    return {
        "errors": [
            {
                "code": code,
                "message": message,
                "level": level,
                "description": description,
            }
        ]
    }


def validar_entero(numero, nombre: str = "numero") -> int:
    valor = str(numero)
    valor_sin_letras = sub("[a-zA-Z]+", "", valor)

    try:
        return int(valor_sin_letras)
    except ValueError:
        logger.warning(
            f"Valor numerico invalido: '{numero}' no puede convertirse a entero"
        )

        raise ValueError(
            construir_error_api(
                code=f"invalid.{nombre}.format",
                message=f"Formato de '{nombre}' invalido",
                description=f"El valor '{numero}' no puede convertirse a un numero entero",
            )
        )


def validar_minimo(valor: int, minimo: int, nombre: str) -> int:
    if valor < minimo:
        logger.warning(
            f"Valor por debajo del minimo: '{nombre}' es {valor}, minimo esperado {minimo}"
        )

        raise ValueError(
            construir_error_api(
                code=ERROR_CODE_INVALID_MIN_VALUE,
                message="Valor por debajo del minimo permitido",
                description=f"El parametro '{nombre}' debe ser mayor o igual a {minimo}. Se recibio: {valor}",
            )
        )

    return valor


def validar_string_no_vacio(valor, nombre: str) -> str:
    if valor is None or not str(valor).strip():
        raise ValueError(
            construir_error_api(
                code=f"required.{nombre}",
                message=f"Campo requerido: '{nombre}'",
                description=f"El campo '{nombre}' es obligatorio y no puede estar vacio",
            )
        )

    return str(valor).strip()


def armar_error(status, code, message, description):
    return {
        "status": status,
        "body": {
            "errors": [
                {
                    "code": code,
                    "message": message,
                    "level": "error",
                    "description": description,
                }
            ]
        },
    }


def build_hateoas_links(
    total: int, limit: int, offset: int, extra_params: dict = None
) -> dict:
    """
    Genera el objetivo _links con los enlaces HATEOAS (_first, _prev, _next, _last)
    Conserva los filtros adicionales de la URL.
    """
    if extra_params is None:
        extra_params = {}

    base_url = request.base_url

    def make_url(new_offset: int) -> dict:
        params = dict(extra_params)
        params["_limit"] = limit
        params["_offset"] = new_offset
        return {"href": f"{base_url}?{urlencode(params)}"}

    first_url = make_url(0)

    if offset > 0:
        prev_offset = max(0, offset - limit)
        prev_url = make_url(prev_offset)
    else:
        prev_url = None

    if offset + limit < total:
        next_offset = offset + limit
        next_url = make_url(next_offset)
    else:
        next_url = None

    if total > 0:
        last_offset = ((total - 1) // limit) * limit
    else:
        last_offset = 0

    last_url = make_url(last_offset)

    return {
        "_first": first_url,
        "_prev": prev_url,
        "_next": next_url,
        "_last": last_url,
    }
