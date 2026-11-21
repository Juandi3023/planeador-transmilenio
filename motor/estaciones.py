"""Requisitos R1, R2 y R3: Consulta de estado, autocompletado y rango alfabetico."""


def consultar_estado(tabla_estaciones, nombre):
    """R1: Devuelve 'ABIERTA', 'CERRADA' o 'NO EXISTE' en O(1) promedio."""
    if not isinstance(nombre, str):
        return "NO EXISTE"
    clave = nombre.strip().upper()
    estado = tabla_estaciones.obtener(clave)
    if estado is None:
        return "NO EXISTE"
    return "ABIERTA" if estado else "CERRADA"


def autocompletar_estaciones(arbol_estaciones, prefijo, k):
    """R2: Devuelve hasta k estaciones abiertas que inician con prefijo en O(log n + k)."""
    if not isinstance(prefijo, str) or k <= 0:
        return []
    pref = prefijo.strip().upper()
    return arbol_estaciones.autocompletar(pref, k)


def listar_rango_estaciones(arbol_estaciones, desde, hasta):
    """R3: Devuelve estaciones abiertas en [desde, hasta] ordenadas en O(log n + m)."""
    if not isinstance(desde, str) or not isinstance(hasta, str):
        return []
    d = desde.strip().upper()
    h = hasta.strip().upper()
    return arbol_estaciones.rango(d, h)