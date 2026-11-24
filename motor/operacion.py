"""Requisitos R7, R8, R9 y R10: Edicion de rutas, cierre/reapertura, deshacer/rehacer y fila."""

from motor.estructuras import Cola, merge_sort


def agregar_parada_ruta(tabla_estaciones, tabla_rutas, ruta, nueva, despues_de, registrar=True, pila_deshacer=None, pila_rehacer=None):
    """R7: Inserta una parada despues de otra en O(1) promedio."""
    if not isinstance(ruta, str) or not isinstance(nueva, str):
        return False
    rt = ruta.strip().upper()
    nv = nueva.strip().upper()
    dp = despues_de.strip().upper() if isinstance(despues_de, str) else None

    if tabla_estaciones.obtener(nv) is None:
        return False
    lista_ruta = tabla_rutas.obtener(rt)
    if lista_ruta is None:
        return False

    exito = lista_ruta.agregar_despues_de(nv, dp)
    if exito and registrar and pila_deshacer is not None:
        pila_deshacer.push(("AGREGAR", rt, nv, dp))
        if pila_rehacer is not None:
            pila_rehacer.limpiar()
    return exito


def quitar_parada_ruta(tabla_rutas, ruta, estacion, registrar=True, pila_deshacer=None, pila_rehacer=None):
    """R7: Elimina una parada de una ruta en O(1) promedio."""
    if not isinstance(ruta, str) or not isinstance(estacion, str):
        return False
    rt = ruta.strip().upper()
    est = estacion.strip().upper()

    lista_ruta = tabla_rutas.obtener(rt)
    if lista_ruta is None:
        return False

    exito, anterior = lista_ruta.quitar(est)
    if exito and registrar and pila_deshacer is not None:
        pila_deshacer.push(("QUITAR", rt, est, anterior))
        if pila_rehacer is not None:
            pila_rehacer.limpiar()
    return exito


def obtener_recorrido_ruta(tabla_rutas, ruta, al_reves=False):
    """R7: Devuelve la lista de paradas de una ruta en sentido normal o inverso en O(L)."""
    if not isinstance(ruta, str):
        return []
    rt = ruta.strip().upper()
    lista_ruta = tabla_rutas.obtener(rt)
    if lista_ruta is None:
        return []
    return lista_ruta.a_lista(al_reves)


def cambiar_estado_estacion(tabla_estaciones, arbol_estaciones, nombre, abrir, registrar=True, pila_deshacer=None, pila_rehacer=None):
    """R8: Cierra o reabre una estacion en O(log n)."""
    if not isinstance(nombre, str):
        return False
    est = nombre.strip().upper()
    estado_actual = tabla_estaciones.obtener(est)
    if estado_actual is None:
        return False
    if estado_actual == abrir:
        return False

    tabla_estaciones.insertar(est, abrir)
    nodo = arbol_estaciones.buscar_nodo(est)
    if nodo is not None:
        nodo.abierto = abrir

    if registrar and pila_deshacer is not None:
        accion = "REABRIR" if abrir else "CERRAR"
        pila_deshacer.push((accion, est, None, None))
        if pila_rehacer is not None:
            pila_rehacer.limpiar()
    return True


def ejecutar_deshacer(tabla_estaciones, arbol_estaciones, tabla_rutas, pila_deshacer, pila_rehacer):
    """R9: Deshace la ultima operacion administrativa en O(1) / O(log n)."""
    op = pila_deshacer.pop()
    if op is None:
        return False
    tipo = op[0]
    if tipo == "AGREGAR":
        quitar_parada_ruta(tabla_rutas, op[1], op[2], registrar=False)
    elif tipo == "QUITAR":
        agregar_parada_ruta(tabla_estaciones, tabla_rutas, op[1], op[2], op[3], registrar=False)
    elif tipo == "CERRAR":
        cambiar_estado_estacion(tabla_estaciones, arbol_estaciones, op[1], True, registrar=False)
    elif tipo == "REABRIR":
        cambiar_estado_estacion(tabla_estaciones, arbol_estaciones, op[1], False, registrar=False)
    pila_rehacer.push(op)
    return True


def ejecutar_rehacer(tabla_estaciones, arbol_estaciones, tabla_rutas, pila_deshacer, pila_rehacer):
    """R9: Rehace la ultima operacion deshecha en O(1) / O(log n)."""
    op = pila_rehacer.pop()
    if op is None:
        return False
    tipo = op[0]
    if tipo == "AGREGAR":
        agregar_parada_ruta(tabla_estaciones, tabla_rutas, op[1], op[2], op[3], registrar=False)
    elif tipo == "QUITAR":
        quitar_parada_ruta(tabla_rutas, op[1], op[2], registrar=False)
    elif tipo == "CERRAR":
        cambiar_estado_estacion(tabla_estaciones, arbol_estaciones, op[1], False, registrar=False)
    elif tipo == "REABRIR":
        cambiar_estado_estacion(tabla_estaciones, arbol_estaciones, op[1], True, registrar=False)
    pila_deshacer.push(op)
    return True


def _parsear_llegada(valor):
    if isinstance(valor, str):
        partes = valor.strip().split(":")
        return int(partes[0]) * 60 + int(partes[1])
    return int(valor)


def simular_fila(llegadas, frecuencia, capacidad):
    """R10: Simula abordaje en hora pico con Cola FIFO en O(P).
    Devuelve (atendidos, buses_usados, espera_promedio, espera_maxima).
    """
    n = len(llegadas)
    if n == 0 or frecuencia <= 0 or capacidad <= 0:
        return (0, 0, 0.0, 0)

    tiempos = []
    ordenado = True
    prev = -10 ** 12
    for x in llegadas:
        t = _parsear_llegada(x)
        if t < prev:
            ordenado = False
        prev = t
        tiempos.append(t)

    if not ordenado:
        tiempos = merge_sort(tiempos)

    cola = Cola()
    idx = 0
    primer_t = tiempos[0]
    tiempo_bus = ((primer_t // frecuencia) + 1) * frecuencia if primer_t % frecuencia != 0 else primer_t

    atendidos = 0
    buses_usados = 0
    suma_espera = 0
    espera_maxima = 0

    while idx < n or not cola.esta_vacia():
        while idx < n and tiempos[idx] <= tiempo_bus:
            cola.enqueue(tiempos[idx])
            idx += 1

        if not cola.esta_vacia():
            buses_usados += 1
            cupo = capacidad
            while cupo > 0 and not cola.esta_vacia():
                t_llegada = cola.dequeue()
                espera = tiempo_bus - t_llegada
                suma_espera += espera
                if espera > espera_maxima:
                    espera_maxima = espera
                atendidos += 1
                cupo -= 1
            tiempo_bus += frecuencia
        else:
            if idx < n:
                sig = tiempos[idx]
                tiempo_bus = ((sig // frecuencia) + 1) * frecuencia if sig % frecuencia != 0 else sig

    espera_promedio = suma_espera / atendidos if atendidos > 0 else 0.0
    return (atendidos, buses_usados, espera_promedio, espera_maxima)