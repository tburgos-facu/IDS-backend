from flask import Blueprint, jsonify, request

from ..services import canchas as canchas_service
from ..utils import build_hateoas_links
from ..validators.canchas import (
    validate_actualizar_cancha,
    validate_consultar_disponibilidad,
    validate_crear_cancha,
)

canchas_bp = Blueprint("canchas", __name__)


@canchas_bp.route("/canchas", methods=["GET"])
def get_canchas():
    # 1. Parámetros de paginación con valores por defecto
    try:
        limit = min(int(request.args.get("_limit", 10)), 100)
        offset = max(int(request.args.get("_offset", 0)), 0)
    except ValueError:
        return jsonify({"error": "Parámetros de paginación inválidos"}), 400
    # filtros opcionales
    id_deporte = request.args.get("id_deporte", type=int)
    nombre = request.args.get("nombre")
    techada_param = request.args.get("techada")
    techada = (
        techada_param.lower() == "true" if techada_param in ["true", "false"] else None
    )

    activa_param = request.args.get("activa")
    activa = (
        activa_param.lower() == "true" if activa_param in ["true", "false"] else None
    )
    # 3 llamada al servicio
    canchas, total = canchas_service.listar_canchas(
        limit=limit,
        offset=offset,
        id_deporte=id_deporte,
        nombre=nombre,
        techada=techada,
        activa=activa,
    )
    # 4. Armado de respuesta HATEOAS
    extra_params = {
        k: v for k, v in request.args.items() if k not in ["_limit", "_offset"]
    }
    links = build_hateoas_links(total, limit, offset, extra_params)

    return jsonify({"canchas": canchas, "_links": links}), 200


@canchas_bp.route("/canchas/disponibles", methods=["GET"])
def get_canchas_disponibles():
    # 1.Validar parámetros obligatorios de horario
    is_valid, result = validate_consultar_disponibilidad(request.args)
    if not is_valid:
        return jsonify({"error": result}), 400

    fecha_hora_inicio, fecha_hora_fin = result

    # 2. Parámetros de paginación
    try:
        limit = min(int(request.args.get("_limit", 10)), 100)
        offset = max(int(request.args.get("_offset", 0)), 0)
    except ValueError:
        return jsonify({"error": "Parámtros de paginación inválidos"}), 400

    # 3. Filtros opcionales
    id_deporte = request.args.get("id_deporte", type=int)
    techada_param = request.args.get("techada")
    techada = (
        techada_param.lower() == "true" if techada_param in ["true", "false"] else None
    )

    # 4. Consulta al servicio
    canchas, total = canchas_service.obtener_canchas_disponibles(
        fecha_hora_inicio=fecha_hora_inicio,
        fecha_hora_fin=fecha_hora_fin,
        limit=limit,
        offset=offset,
        id_deporte=id_deporte,
        techada=techada,
    )

    # 5. Enlace HATEOAS
    extra_params = {
        k: v for k, v in request.args.items() if k not in ["_limit", "_offset"]
    }
    links = build_hateoas_links(total, limit, offset, extra_params)

    return jsonify({"canchas": canchas, "_links": links}), 200


@canchas_bp.route("/canchas/<int:cancha_id>", methods=["GET"])
def get_cancha_by_id(cancha_id):
    cancha = canchas_service.obtener_cancha_por_id(cancha_id)
    if not cancha:
        return jsonify({"error": "Cancha no encontrada"}), 404

    return jsonify(cancha), 200


@canchas_bp.route("/canchas", methods=["POST"])
def create_cancha():
    # Leer el JSON del cuerpo de la petición
    data = request.get_json(silent=True)

    # Validar campos obligatorios y formato
    is_valid, error_msg = validate_crear_cancha(data)
    if not is_valid:
        return jsonify({"error": error_msg}), 400

    nueva_cancha, error = canchas_service.crear_cancha(data)
    if error:
        return jsonify({"error": error}), 400

    return jsonify(nueva_cancha), 201


@canchas_bp.route("/canchas/<int:cancha_id>", methods=["PATCH"])
def patch_cancha(cancha_id):
    data = request.get_json(silent=True)

    is_valid, error_msg = validate_actualizar_cancha(data)
    if not is_valid:
        return jsonify({"error": error_msg}), 400

    cancha_actualizada, error = canchas_service.actualizar_cancha(cancha_id, data)
    if error:
        return jsonify({"error": error}), 404

    return jsonify(cancha_actualizada), 200


@canchas_bp.route("/canchas/<int:cancha_id>", methods=["DELETE"])
def delete_cancha(cancha_id):
    status_code, error = canchas_service.eliminar_cancha(cancha_id)
    if error:
        return jsonify({"error": error}), status_code

    return "", 204
