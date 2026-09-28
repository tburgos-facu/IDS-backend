import re

from .. import utils

PATRON_EMAIL = r"^[\w\.-]+@[\w\.-]+\.\w+$"


def email_es_valido(email):
    return re.match(PATRON_EMAIL, email) is not None


def validar_crear_socio(datos):
    resultado = {"datos_limpios": {}, "error": None}

    if datos == None:
        resultado["error"] = utils.armar_error(
            400,
            "required.body",
            "Cuerpo vacio",
            "Falta enviar el JSON con los datos del socio",
        )
    else:
        tiene_desconocidos = False
        for llave in datos.keys():
            if llave != "nombre" and llave != "email":
                tiene_desconocidos = True

        if tiene_desconocidos == True:
            resultado["error"] = utils.armar_error(
                400,
                "invalid.campos",
                "Campos desconocidos",
                "Solo se permiten los campos nombre y email",
            )
        elif "nombre" not in datos or "email" not in datos:
            resultado["error"] = utils.armar_error(
                400,
                "required.campos",
                "Nombre y email son obligatorios",
                "Debe enviar nombre y email",
            )
        else:
            nombre = str(datos["nombre"]).strip()
            email = str(datos["email"]).strip().lower()

            if nombre == "":
                resultado["error"] = utils.armar_error(
                    400,
                    "required.nombre",
                    "Nombre inválido",
                    "El nombre no puede quedar vacío",
                )
            elif email_es_valido(email) == False:
                resultado["error"] = utils.armar_error(
                    400,
                    "invalid.email.format",
                    "Formato de email inválido",
                    "El email no tiene un formato válido",
                )
            else:
                resultado["datos_limpios"]["nombre"] = nombre
                resultado["datos_limpios"]["email"] = email

    return resultado


def validar_actualizar_socio(datos):
    resultado = {"datos_limpios": {}, "error": None}

    if datos == None:
        resultado["error"] = utils.armar_error(
            400,
            "required.body",
            "Cuerpo vacío",
            "Falta enviar el JSON con los campos a actualizar",
        )
    else:
        tiene_desconocidos = False
        for llave in datos.keys():
            if llave != "nombre" and llave != "email" and llave != "activo":
                tiene_desconocidos = True

        if tiene_desconocidos == True:
            resultado["error"] = utils.armar_error(
                400,
                "invalid.campos",
                "Campos desconocidos",
                "Solo se permiten nombre, email y activo",
            )
        else:
            if "nombre" in datos:
                nombre = str(datos["nombre"]).strip()
                if nombre == "":
                    resultado["error"] = utils.armar_error(
                        400,
                        "invalid.nombre",
                        "Nombre inválido",
                        "El nombre no puede quedar vacío",
                    )
                else:
                    resultado["datos_limpios"]["nombre"] = nombre

            if "email" in datos and resultado["error"] == None:
                email = str(datos["email"]).strip().lower()
                if email_es_valido(email) == False:
                    resultado["error"] = utils.armar_error(
                        400,
                        "invalid.email.format",
                        "Formato de email inválido",
                        "El email no tiene un formato válido",
                    )
                else:
                    resultado["datos_limpios"]["email"] = email

            if "activo" in datos and resultado["error"] == None:
                activo = datos["activo"]
                if activo in [True, False, 1, 0, "true", "false"]:
                    if activo == True or activo == 1 or activo == "true":
                        resultado["datos_limpios"]["activo"] = 1
                    else:
                        resultado["datos_limpios"]["activo"] = 0
                else:
                    resultado["error"] = utils.armar_error(
                        400,
                        "invalid.activo",
                        "Valor de activo inválido",
                        "Debe ser booleano (true/false)",
                    )

            if len(resultado["datos_limpios"]) == 0 and resultado["error"] == None:
                resultado["error"] = utils.armar_error(
                    400,
                    "required.body",
                    "Cuerpo inválido",
                    "Debe enviar al menos un campo válido",
                )

    return resultado


def validar_get_socios(parametros_url):
    resultado = {"datos_limpios": {}, "error": None}

    tiene_parametros_invalidos = False
    for parametro in parametros_url.keys():
        if (
            parametro != "nombre"
            and parametro != "activo"
            and parametro != "_limit"
            and parametro != "_offset"
        ):
            tiene_parametros_invalidos = True

    if tiene_parametros_invalidos == True:
        resultado["error"] = utils.armar_error(
            400,
            "invalid.parametros",
            "Parámetros desconocidos",
            "Se enviaron parámetros no soportados",
        )
    else:
        nombre = parametros_url.get("nombre")
        activo = parametros_url.get("activo")
        limit = parametros_url.get("_limit", "10")
        offset = parametros_url.get("_offset", "0")

        if activo != None and activo != "true" and activo != "false":
            resultado["error"] = utils.armar_error(
                400,
                "invalid.activo",
                "Filtro activo inválido",
                "El filtro activo admite únicamente true o false",
            )
        elif str(limit).isdigit() == False or str(offset).isdigit() == False:
            resultado["error"] = utils.armar_error(
                400,
                "invalid.paginacion",
                "Paginación inválida",
                "_limit y _offset deben ser números",
            )
        else:
            limit_int = int(limit)
            offset_int = int(offset)

            if limit_int < 1 or limit_int > 100 or offset_int < 0:
                resultado["error"] = utils.armar_error(
                    400,
                    "invalid.paginacion",
                    "Paginación fuera de rango",
                    "_limit debe estar entre 1 y 100, _offset debe ser mayor o igual a 0",
                )
            else:
                resultado["datos_limpios"]["nombre"] = nombre
                resultado["datos_limpios"]["activo"] = activo
                resultado["datos_limpios"]["limit"] = limit_int
                resultado["datos_limpios"]["offset"] = offset_int

    return resultado
