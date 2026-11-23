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


def planear_viaje(tabla_estaciones, tabla_rutas, origen, destino):
    """R5: Encuentra el viaje directo o con 1 transbordo con menor numero de paradas."""
    if not isinstance(origen, str) or not isinstance(destino, str):
        return None
    orig = origen.strip().upper()
    dest = destino.strip().upper()

    if tabla_estaciones.obtener(orig) is not True or tabla_estaciones.obtener(dest) is not True:
        return None
    if orig == dest:
        return []

    mejor_directo = None
    mejor_directo_paradas = 10 ** 9

    alcanzables_origen = TablaHash(64)
    tramos_hacia_destino = []

    nombres_rutas = tabla_rutas.claves()
    for rt in nombres_rutas:
        lista_ruta = tabla_rutas.obtener(rt)
        paradas = lista_ruta.a_lista(False)
        n = len(paradas)
        idx_orig = -1
        idx_dest = -1
        for i in range(n):
            if paradas[i] == orig and idx_orig == -1:
                idx_orig = i
            if paradas[i] == dest and idx_dest == -1:
                idx_dest = i

        if idx_orig != -1 and idx_dest != -1 and idx_dest > idx_orig:
            costo = idx_dest - idx_orig
            if costo < mejor_directo_paradas:
                mejor_directo_paradas = costo
                mejor_directo = [(rt, orig, dest, costo)]

        if idx_orig != -1:
            for j in range(idx_orig + 1, n):
                inter = paradas[j]
                if inter != dest and tabla_estaciones.obtener(inter) is True:
                    costo1 = j - idx_orig
                    previo = alcanzables_origen.obtener(inter)
                    if previo is None or costo1 < previo[0]:
                        alcanzables_origen.insertar(inter, [costo1, rt])

        if idx_dest != -1:
            for i in range(0, idx_dest):
                inter = paradas[i]
                if inter != orig and tabla_estaciones.obtener(inter) is True:
                    costo2 = idx_dest - i
                    tramos_hacia_destino.append((rt, inter, costo2))

    mejor_transbordo = None
    mejor_transbordo_paradas = 10 ** 9

    for tramo in tramos_hacia_destino:
        rt2 = tramo[0]
        inter = tramo[1]
        costo2 = tramo[2]
        info1 = alcanzables_origen.obtener(inter)
        if info1 is not None:
            total = info1[0] + costo2
            if total < mejor_transbordo_paradas:
                mejor_transbordo_paradas = total
                mejor_transbordo = [
                    (info1[1], orig, inter, info1[0]),
                    (rt2, inter, dest, costo2),
                ]

    if mejor_directo is None and mejor_transbordo is None:
        return None
    if mejor_directo_paradas <= mejor_transbordo_paradas:
        return mejor_directo
    return mejor_transbordo


def calcular_ranking_completo(tabla_estaciones, tabla_rutas, conteo_buses, viajes_por_ruta):
    """R6: Construye el ranking ordenado de estaciones abiertas por buses al dia."""
    acumulado = TablaHash(128)
    for rt in tabla_rutas.claves():
        lista_ruta = tabla_rutas.obtener(rt)
        buses_defecto = viajes_por_ruta.obtener(rt, 0)
        actual = lista_ruta.head
        while actual is not None:
            est = actual.estacion
            if tabla_estaciones.obtener(est) is True:
                clave_he = rt + "|" + est
                c = conteo_buses.obtener(clave_he)
                if c is None:
                    c = buses_defecto
                prev = acumulado.obtener(est, 0)
                acumulado.insertar(est, prev + c)
            actual = actual.next

    pares = []
    for est in tabla_estaciones.claves():
        if tabla_estaciones.obtener(est) is True:
            total = acumulado.obtener(est, 0)
            pares.append((est, total))

    ordenado = merge_sort(pares, clave_fn=lambda item: (-item[1], item[0]))
    return ordenado