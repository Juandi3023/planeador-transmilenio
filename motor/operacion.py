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