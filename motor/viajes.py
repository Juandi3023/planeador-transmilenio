"""Requisitos R4, R5 y R6: Proximo bus, planeacion de viaje y ranking diario."""

from motor.estructuras import TablaHash, merge_sort, busqueda_binaria_siguiente


def hora_a_minutos(hora_str):
    """Convierte 'HH:MM' a minutos desde 00:00."""
    partes = hora_str.strip().split(":")
    if len(partes) != 2:
        return -1
    hh = int(partes[0])
    mm = int(partes[1])
    return hh * 60 + mm


def consultar_proximo_bus(tabla_estaciones, tabla_rutas, tabla_horarios, estacion, ruta, hora):
    """R4: Busca el siguiente bus >= hora en O(log h) usando busqueda binaria."""
    if not isinstance(estacion, str) or not isinstance(ruta, str) or not isinstance(hora, str):
        return None
    est = estacion.strip().upper()
    rt = ruta.strip().upper()

    abierta = tabla_estaciones.obtener(est)
    if abierta is not True:
        return None

    lista_ruta = tabla_rutas.obtener(rt)
    if lista_ruta is None or not lista_ruta.contiene(est):
        return None

    clave_hor = rt + "|" + est
    horarios = tabla_horarios.obtener(clave_hor)
    if horarios is None or len(horarios) == 0:
        return None

    mins = hora_a_minutos(hora)
    if mins < 0:
        return None

    encontrado = busqueda_binaria_siguiente(horarios, (mins, ""))
    if encontrado is None:
        return None
    return encontrado[1]