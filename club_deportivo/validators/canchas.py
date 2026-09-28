from datetime import datetime, timedelta, timezone


def validate_crear_cancha(data):
    """Valida los campos recibidos para la creación de una cancha."""
    if not isinstance(data, dict) or not data:
        return False, "El cuerpo de la solicitud no puede estar vacío"

    # Rechazar campos desconocidos
    allowed_fields = {"nombre", "id_deporte", "precio_hora", "techada", "activa"}
    unknown_fields = set(data.keys()) - allowed_fields
    if unknown_fields:
        return False, f"Campos no permitidos: {', '.join(unknown_fields)}"

    # Campos obligatorios
    if "nombre" not in data or "id_deporte" not in data or "precio_hora" not in data:
        return (
            False,
            "Los campos 'nombre', 'id_deporte' y 'precio_hora' son obligatorios",
        )

    # Validar nombre
    nombre = str(data["nombre"]).strip()
    if not nombre:
        return False, "El nombre no puede estar vacío"

    # Validar id_deporte
    if not isinstance(data["id_deporte"], int) or data["id_deporte"] <= 0:
        return False, "El 'id_deporte' debe ser un entero positivo"

    # Validar precio_hora (entero en centavos mayor a 0)
    if not isinstance(data["precio_hora"], int) or data["precio_hora"] <= 0:
        return False, "El 'precio_hora' debe ser un entero positivo (centavos)"

    # Validar opcionales si se envían
    if "techada" in data and not isinstance(data["techada"], bool):
        return False, "El campo 'techada' debe ser booleano (true/false)"

    if "activa" in data and not isinstance(data["activa"], bool):
        return False, "El campo 'activa' debe ser booleano (true/false)"

    return True, None


def validate_actualizar_cancha(data):
    if not isinstance(data, dict) or not data:
        return False, "El cuerpo de la solicitud no puede estar vacío"

    if "id_deporte" in data:
        return (
            False,
            "El deporte asociado no se puede modificar una vez creada la cancha",
        )

    allowed_fields = {"nombre", "precio_hora", "techada", "activa"}
    unknown_fields = set(data.keys()) - allowed_fields
    if unknown_fields:
        return False, f"Campos no permitidos: {', '.join(unknown_fields)}"

    if "nombre" in data:
        nombre = str(data["nombre"]).strip()
        if not nombre:
            return False, "El nombre no puede quedar vacío"

    if "precio_hora" in data:
        if not isinstance(data["precio_hora"], int) or data["precio_hora"] <= 0:
            return False, "El 'precio_hora' debe ser un entero positivo (centavos)"

    if "techada" in data and not isinstance(data["techada"], bool):
        return False, "El campo 'techada' debe ser booleano"

    if "activa" in data and not isinstance(data["activa"], bool):
        return False, "El campo 'activa' debe ser booleano"

    return True, None


def validate_consultar_disponibilidad(args):
    "Valida los parámetros requeridos para consultar la disponibilidad de las canchas"
    fecha = args.get("fecha")
    hora_inicio = args.get("hora_inicio")
    hora_fin = args.get("hora_fin")
    if not fecha or not hora_inicio or not hora_fin:
        return (
            False,
            "Los parámetros 'fecha', 'hora_inicio' y 'hora_fin' son obligatorios",
        )

    try:
        # Armar strings ISO completos en GMT -3
        iso_inicio = f"{fecha}T{hora_inicio}"
        iso_fin = f"{fecha}T{hora_fin}"
        dt_inicio = datetime.fromisoformat(iso_inicio)
        dt_fin = datetime.fromisoformat(iso_fin)

        gmt3 = timezone(timedelta(hours=-3))
        if dt_inicio.tzinfo is None:
            dt_inicio = dt_inicio.replace(tzinfo=gmt3)
        if dt_fin.tzinfo is None:
            dt_fin = dt_fin.replace(tzinfo=gmt3)

        # Validar horas en punto (00 minutos, 00 segundos, 0 microsegundos)
        if (
            dt_inicio.minute != 0
            or dt_inicio.second != 0
            or dt_fin.minute != 0
            or dt_fin.second != 0
        ):
            return False, "Las reservas deben comenzar y terminar en horas en punto"

        # Validar inicio < fin
        if dt_inicio >= dt_fin:
            return False, "La hora de inicio debe ser anterior a la hora de fin"

        # Validar duración
        duracion_horas = (dt_fin - dt_inicio).total_seconds() / 3600
        if duracion_horas < 1 or duracion_horas > 3 or not duracion_horas.is_integer():
            return (
                False,
                "La duración de la reserva debe ser de 1, 2 o 3 horas completas",
            )

        # Validar horario del club
        if dt_inicio.hour < 8 or dt_fin.hour > 23:
            return (
                False,
                "El horario solicitado debe estar dentro del rango de horario en el que el club abre sus puertas",
            )

        # Vaalidar que sea en el futuro
        ahora = datetime.now(gmt3)
        if dt_inicio <= ahora:
            return (
                False,
                "La fecha y hora de inicio deben ser posteriores al momento actual",
            )

        inicio_gmt3 = dt_inicio.astimezone(gmt3).replace(tzinfo=None)
        fin_gmt3 = dt_fin.astimezone(gmt3).replace(tzinfo=None)
        return True, (inicio_gmt3, fin_gmt3)
    except ValueError:
        return (
            False,
            "Formato de fecha u hora inválido. Formato esperado: YYYY-MM-DD para fecha y HH:MM:SS para hora",
        )
