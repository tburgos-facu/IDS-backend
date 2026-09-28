from flask import Blueprint, jsonify, request

from ..services import reservas as reservas_services
from ..utils import build_hateoas_links, construir_error_api
from ..validators import reservas as reservas_validators

reservas_bp = Blueprint("reservas", __name__)


@reservas_bp.route("/reservas", methods=["GET"])
def get_reservas():
    id_socio = request.args.get("id_socio")
    id_cancha = request.args.get("id_cancha")
    estado = request.args.get("estado")
    fecha_desde = request.args.get("fecha_desde")
    fecha_hasta = request.args.get("fecha_hasta")
    limit = request.args.get("_limit", "10")
    offset = request.args.get("_offset", "0")

    try:
        id_socio = reservas_validators.validar_id(id_socio)
        id_cancha = reservas_validators.validar_id(id_cancha)
        estado = reservas_validators.validar_estado(estado)
        fecha_desde, fecha_hasta = reservas_validators.validar_fechas(
            fecha_desde, fecha_hasta
        )
        limit, offset = reservas_validators.validar_paginacion(limit, offset)
    except ValueError as e:
        return jsonify(e.args[0]), 400

    reservas, total = reservas_services.listar_reservas(
        id_cancha=id_cancha,
        id_socio=id_socio,
        estado=estado,
        fecha_desde=fecha_desde,
        fecha_hasta=fecha_hasta,
        limit=limit,
        offset=offset,
    )

    extra_params = {
        k: v for k, v in request.args.items() if k not in ["_limit", "_offset"]
    }
    links = build_hateoas_links(total, limit, offset, extra_params)

    return jsonify({"reservas": reservas, "_links": links}), 200


@reservas_bp.route("/reservas", methods=["POST"])
def post_reserva():
    body = request.get_json(silent=True)

    if not isinstance(body, dict):
        return jsonify(
            construir_error_api(
                code="invalid format",
                message="el cuerpo de la reserva es invalido",
                description="no se mando un json con los datos de la reserva",
            )
        ), 400

    try:
        datos_reserva = reservas_validators.validar_reserva(body)
    except ValueError as e:
        return jsonify(e.args[0]), 400

    # el service manda el error junto con el status (404, 409 o 400)
    try:
        id_reserva = reservas_services.crear_reserva(datos_reserva)
    except ValueError as e:
        return jsonify(e.args[0]), e.args[1]

    return jsonify({"id": id_reserva}), 201


@reservas_bp.route("/reservas/<int:id>", methods=["GET"])
def get_reserva(id):
    reserva = reservas_services.obtener_reserva_por_id(id)

    if reserva is None:
        return jsonify(
            construir_error_api(
                code="error id reserva",
                message="la reserva no existe",
                description=f"el id de reserva {id} no existe",
            )
        ), 404

    return jsonify(reserva), 200


@reservas_bp.route("/reservas/<int:id>/estado", methods=["PUT"])
def put_estado_reserva(id):
    body = request.get_json(silent=True)

    try:
        nuevo_estado = reservas_validators.validar_cambio_estado(body)
    except ValueError as e:
        return jsonify(e.args[0]), 400

    try:
        reserva = reservas_services.cambiar_estado_reserva(id, nuevo_estado)
    except ValueError as e:
        return jsonify(e.args[0]), 409

    if reserva is None:
        return jsonify(
            construir_error_api(
                code="error id reserva",
                message="la reserva no existe",
                description=f"el id de reserva {id} no existe",
            )
        ), 404

    return jsonify(reserva), 200
