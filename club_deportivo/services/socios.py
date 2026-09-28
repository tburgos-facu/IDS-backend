from .. import db, utils


def construir_socio_dto(socio: dict) -> dict:
    return {
        "id": socio["id"],
        "nombre": socio["nombre"],
        "email": socio["email"],
        "activo": bool(socio["activo"]),
    }


def obtener_socio_por_id(id_socio):
    socio_limpio = {}
    sql = "SELECT id, nombre, email, activo FROM socios WHERE id = :id"
    filas = db.ejecutar_consulta(sql, {"id": id_socio})

    if len(filas) > 0:
        socio_limpio = construir_socio_dto(filas[0])

    return socio_limpio


def listar_socios(nombre, activo, limit, offset):
    sql = "SELECT id, nombre, email, activo FROM socios WHERE 1=1"
    parametros = {"limit": limit, "offset": offset}

    if nombre != None:
        sql = sql + " AND nombre LIKE :nombre"
        parametros["nombre"] = "%" + nombre + "%"

    if activo != None:
        sql = sql + " AND activo = :activo"
        if activo == "true" or activo == True or activo == "1":
            parametros["activo"] = 1
        else:
            parametros["activo"] = 0

    sql = sql + " ORDER BY id ASC LIMIT :limit OFFSET :offset"
    filas = db.ejecutar_consulta(sql, parametros)

    resultado = []
    for fila in filas:
        resultado.append(construir_socio_dto(fila))

    return resultado


def crear_socio(datos_limpios):
    resultado = {}

    # no duplicar mail
    sql_buscar = "SELECT id FROM socios WHERE email = :email"
    ya_existe = db.ejecutar_consulta(sql_buscar, {"email": datos_limpios["email"]})

    if len(ya_existe) > 0:
        resultado = {
            "error": utils.armar_error(
                409,
                "conflict.email",
                "Correo ya registrado",
                "El correo ya está registrado por otro socio",
            )
        }
    else:
        # guardo
        sql_insertar = (
            "INSERT INTO socios (nombre, email, activo) VALUES (:nombre, :email, 1)"
        )
        id_nuevo = db.ejecutar_mutacion(sql_insertar, datos_limpios)
        resultado = {"id": id_nuevo, "status": 201}

    return resultado


def contar_socios(nombre, activo):
    sql = "SELECT COUNT(*) as total FROM socios WHERE 1=1"
    parametros = {}
    total = 0
    if nombre != None:
        sql = sql + " AND nombre LIKE :nombre"
        parametros["nombre"] = "%" + nombre + "%"

    if activo != None:
        sql = sql + " AND activo = :activo"
        if activo == "true":
            parametros["activo"] = 1
        else:
            parametros["activo"] = 0

    filas = db.ejecutar_consulta(sql, parametros)

    if len(filas) > 0:
        total = filas[0]["total"]

    return total


def actualizar_socio_parcial(id_socio, datos_limpios):
    resultado = {}

    sql_existe = "SELECT id FROM socios WHERE id = :id"
    existe = db.ejecutar_consulta(sql_existe, {"id": id_socio})

    if len(existe) == 0:
        resultado = {
            "error": utils.armar_error(
                404,
                "not_found.socio",
                "Socio no encontrado",
                f"No existe un socio con id {id_socio}",
            )
        }
    else:
        if "email" in datos_limpios:
            sql_mail = "SELECT id FROM socios WHERE email = :email AND id != :id"
            usados = db.ejecutar_consulta(
                sql_mail, {"email": datos_limpios["email"], "id": id_socio}
            )  # chequea que no este usado por otro socio
            if len(usados) > 0:
                resultado = {
                    "error": utils.armar_error(
                        409,
                        "conflict.email",
                        "Correo ya registrado",
                        "El correo ya está registrado por otro socio",
                    )
                }

        if len(resultado) == 0:
            if "nombre" in datos_limpios:
                sql_nombre = "UPDATE socios SET nombre = :nombre WHERE id = :id"
                db.ejecutar_mutacion(
                    sql_nombre, {"nombre": datos_limpios["nombre"], "id": id_socio}
                )

            if "email" in datos_limpios:
                sql_update_mail = "UPDATE socios SET email = :email WHERE id = :id"
                db.ejecutar_mutacion(
                    sql_update_mail, {"email": datos_limpios["email"], "id": id_socio}
                )

            if "activo" in datos_limpios:
                sql_activo = "UPDATE socios SET activo = :activo WHERE id = :id"
                db.ejecutar_mutacion(
                    sql_activo, {"activo": datos_limpios["activo"], "id": id_socio}
                )

            socio_terminado = obtener_socio_por_id(id_socio)
            resultado = {"socio": socio_terminado, "status": 200}

    return resultado
