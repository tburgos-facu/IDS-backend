from flask import Blueprint, jsonify, request

from .. import utils
from ..services import socios as socios_service
from ..validators import socios as socios_validator

socios_bp = Blueprint("socios", __name__)


@socios_bp.route("/socios", methods=["GET"])
def get_socios():
    validacion = socios_validator.validar_get_socios(request.args)

    if validacion["error"] != None:
        return jsonify(validacion["error"]["body"]), validacion["error"]["status"]

    datos = validacion["datos_limpios"]
    nombre = datos["nombre"]
    activo = datos["activo"]
    limit = datos["limit"]
    offset = datos["offset"]

    socios_lista = socios_service.listar_socios(nombre, activo, limit, offset)
    total_socios = socios_service.contar_socios(nombre, activo)

    # los filtros se mandan para que los links los conserven
    extra_params = {
        k: v for k, v in request.args.items() if k not in ["_limit", "_offset"]
    }
    links = utils.build_hateoas_links(total_socios, limit, offset, extra_params)

    respuesta = {
        "socios": socios_lista,
        "_links": links,
    }
    return jsonify(respuesta), 200


@socios_bp.route("/socios", methods=["POST"])
def create_socio():
    datos_recibidos = request.get_json(
        silent=True
    )  # si no es JSON lo guardo como vacio
    validacion = socios_validator.validar_crear_socio(datos_recibidos)

    if validacion["error"] != None:
        return jsonify(validacion["error"]["body"]), validacion["error"]["status"]

    resultado = socios_service.crear_socio(validacion["datos_limpios"])

    if "error" in resultado:
        return jsonify(resultado["error"]["body"]), resultado["error"]["status"]

    return jsonify({"id": resultado["id"]}), 201


@socios_bp.route("/socios/<int:id>", methods=["GET"])
def get_socio(id):
    socio = socios_service.obtener_socio_por_id(id)

    if len(socio) == 0:
        error = utils.armar_error(
            404,
            "not_found.socio",
            "Socio no encontrado",
            f"No existe un socio con id {id}",
        )  # no hay validacion de formato
        return jsonify(error["body"]), error["status"]

    return jsonify(socio), 200


@socios_bp.route("/socios/<int:id>", methods=["PATCH"])
def update_socio(id):
    datos_recibidos = request.get_json(silent=True)
    validacion = socios_validator.validar_actualizar_socio(datos_recibidos)

    if validacion["error"] != None:
        return jsonify(validacion["error"]["body"]), validacion["error"]["status"]

    resultado = socios_service.actualizar_socio_parcial(id, validacion["datos_limpios"])

    if "error" in resultado:
        return jsonify(resultado["error"]["body"]), resultado["error"]["status"]

    return (
        "",
        204,
    )  # cambio se hace sin tener que mostrarlo, por eso devuelvo un string vacio
