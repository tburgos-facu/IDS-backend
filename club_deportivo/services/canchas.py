from datetime import datetime

from .. import db


def construir_cancha_dto(cancha: dict) -> dict:
    "Transforma el registro SQL al formato que exige la API (DTO)."
    return {
        "id": cancha["id"],
        "nombre": cancha["nombre"],
        "id_deporte": cancha["id_deporte"],
        "precio_hora": cancha["precio_hora"],
        "techada": bool(cancha["techada"]),
        "activa": bool(cancha["activa"]),
    }


def obtener_cancha_por_id(cancha_id: int) -> dict | None:
    sql = "SELECT id, nombre, id_deporte, precio_hora, techada, activa FROM canchas WHERE id = :id"
    resultado = db.ejecutar_consulta(sql, {"id": cancha_id})
    if not resultado:
        return None
    return construir_cancha_dto(resultado[0])


def obtener_las_canchas(
    limit: int,
    offset: int,
    id_deporte: int = None,
    nombre: str = None,
    techada: bool = None,
    activa: bool = None,
) -> tuple[list[dict], int]:

    where_clauses = []
    params = {}
    if id_deporte is not None:
        where_clauses.append("id_deporte = :id_deporte")
        params["id_deporte"] = id_deporte

    if nombre:
        where_clauses.append("LOWER(nombre) LIKE :nombre")
        params["nombre"] = f"%{nombre.lower()}%"  # Busqueda parcial case-insensitive

    if techada is not None:
        where_clauses.append("techada = :techada")
        params["techada"] = techada

    if activa is not None:
        where_clauses.append("activa = :activa")
        params["activa"] = activa

    where_sql = (" WHERE " + " AND ".join(where_clauses)) if where_clauses else ""

    # 2. CONTAR EL TOTAL PARA HATEOAS
    sql_count = f"SELECT COUNT(*) as total FROM canchas{where_sql}"
    res_count = db.ejecutar_consulta(sql_count, params)
    total = res_count[0]["total"] if res_count else 0

    # 3. Consulta con todos los campos necesarios y paginación
    sql = f"""
        SELECT id, nombre, id_deporte, precio_hora, techada, activa
        FROM canchas{where_sql}
        ORDER BY id ASC
        LIMIT :limit OFFSET :offset
    """
    canchas_db = db.ejecutar_consulta(sql, {**params, "limit": limit, "offset": offset})
    return canchas_db, total


def listar_canchas(
    limit: int,
    offset: int,
    id_deporte: int = None,
    nombre: str = None,
    techada: bool = None,
    activa: bool = None,
) -> tuple[list[dict], int]:
    canchas_raw, total = obtener_las_canchas(
        limit=limit,
        offset=offset,
        id_deporte=id_deporte,
        nombre=nombre,
        techada=techada,
        activa=activa,
    )
    canchas_dtos = [construir_cancha_dto(c) for c in canchas_raw]
    return canchas_dtos, total


def obtener_canchas_disponibles(
    fecha_hora_inicio: datetime,
    fecha_hora_fin: datetime,
    limit: int,
    offset: int,
    id_deporte: int = None,
    techada: bool = None,
) -> tuple[list[dict], int]:
    """Busca canchas activas libres durante todo el intervalo solicitado."""
    where_clauses = ["c.activa = TRUE"]
    params = {}

    # Validar que no existan reservas confirmadas superpuestas
    where_clauses.append("""
        NOT EXISTS (
            SELECT 1 FROM reservas r
            WHERE r.id_cancha = c.id
              AND r.estado = 'confirmada'
              AND r.fecha_hora_inicio < :fecha_hora_fin
              AND r.fecha_hora_fin > :fecha_hora_inicio
        )
    """)
    params["fecha_hora_inicio"] = fecha_hora_inicio
    params["fecha_hora_fin"] = fecha_hora_fin

    if id_deporte is not None:
        where_clauses.append("c.id_deporte = :id_deporte")
        params["id_deporte"] = id_deporte

    if techada is not None:
        where_clauses.append("c.techada = :techada")
        params["techada"] = techada

    where_sql = " WHERE " + " AND ".join(where_clauses)

    sql_count = f"SELECT COUNT(*) as total FROM canchas c{where_sql}"
    res_count = db.ejecutar_consulta(sql_count, params)
    total = res_count[0]["total"] if res_count else 0

    sql = f"""
        SELECT c.id, c.nombre, c.id_deporte, c.precio_hora, c.techada, c.activa
        FROM canchas c{where_sql}
        ORDER BY c.id ASC
        LIMIT :limit OFFSET :offset
    """
    canchas_raw = db.ejecutar_consulta(sql, {**params, "limit": limit, "offset": offset})
    canchas_dtos = [construir_cancha_dto(c) for c in canchas_raw]

    return canchas_dtos, total


def crear_cancha(data: dict) -> tuple[dict | None, str | None]:
    # Verificar existencia del deporte asociado
    sql_dep = "SELECT id FROM deportes WHERE id = :id_deporte"
    dep = db.ejecutar_consulta(sql_dep, {"id_deporte": data["id_deporte"]})
    if not dep:
        return None, "El deporte especificado no existe"

    sql = """
        INSERT INTO canchas (nombre, id_deporte, precio_hora, techada, activa)
        VALUES (:nombre, :id_deporte, :precio_hora, :techada, :activa)
    """
    params = {
        "nombre": data["nombre"].strip(),
        "id_deporte": data["id_deporte"],
        "precio_hora": data["precio_hora"],  # Guardado explícito en centavos
        "techada": data.get("techada", False),
        "activa": data.get("activa", True),
    }

    id_cancha = db.ejecutar_mutacion(sql, params)
    return obtener_cancha_por_id(id_cancha), None


def actualizar_cancha(cancha_id: int, data: dict) -> tuple[dict | None, str | None]:
    cancha_actual = obtener_cancha_por_id(cancha_id)
    if not cancha_actual:
        return None, "Cancha no encontrada"

    campos = []
    params = {}

    if "nombre" in data:
        campos.append("nombre = :nombre")
        params["nombre"] = data["nombre"].strip()

    if "precio_hora" in data:
        campos.append("precio_hora = :precio_hora")
        params["precio_hora"] = data["precio_hora"]

    if "techada" in data:
        campos.append("techada = :techada")
        params["techada"] = data["techada"]

    if "activa" in data:
        campos.append("activa = :activa")
        params["activa"] = data["activa"]

    if not campos:
        return cancha_actual, None

    params["id"] = cancha_id
    sql = f"UPDATE canchas SET {', '.join(campos)} WHERE id = :id"
    db.ejecutar_mutacion(sql, params)

    return obtener_cancha_por_id(cancha_id), None


def eliminar_cancha(cancha_id: int) -> tuple[int, str | None]:
    cancha = obtener_cancha_por_id(cancha_id)
    if not cancha:
        return 404, "Cancha no encontrada"

    # Verificar presencia de reservas existentes
    sql_check = "SELECT id FROM reservas WHERE id_cancha = :id_cancha LIMIT 1"
    reservas = db.ejecutar_consulta(sql_check, {"id_cancha": cancha_id})
    if reservas:
        return 409, "No se puede eliminar la cancha porque tiene reservas asociadas"

    sql_delete = "DELETE FROM canchas WHERE id = :id"
    db.ejecutar_mutacion(sql_delete, {"id": cancha_id})

    return 204, None
