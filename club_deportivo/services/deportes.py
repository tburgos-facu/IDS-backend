from .. import db


def construir_deporte_dto(deporte: dict) -> dict:
    return {
        "id": deporte["id"],
        "nombre": deporte["nombre"],
    }


def listar_deportes() -> list[dict]:
    sql = "SELECT id, nombre FROM deportes ORDER BY id"
    filas = db.ejecutar_consulta(sql)

    return [construir_deporte_dto(fila) for fila in filas]
