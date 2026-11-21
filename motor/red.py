"""Clase principal Red que integra todas las operaciones del sistema."""

import csv
from motor.estructuras import TablaHash, ArbolAVL, ListaDobleRuta, Pila, merge_sort
from motor.estaciones import consultar_estado, autocompletar_estaciones, listar_rango_estaciones
from motor.viajes import (
    hora_a_minutos,
    consultar_proximo_bus,
    planear_viaje,
    calcular_ranking_completo,
)
from motor.operacion import (
    agregar_parada_ruta,
    quitar_parada_ruta,
    obtener_recorrido_ruta,
    cambiar_estado_estacion,
    ejecutar_deshacer,
    ejecutar_rehacer,
)


class Red:
    """Motor principal de consultas y operaciones de TransMilenio."""

    def __init__(self, carpeta):
        base = carpeta.rstrip("/\\")
        self.tabla_estaciones = TablaHash(256)
        self.arbol_estaciones = ArbolAVL()
        self.tabla_rutas = TablaHash(256)
        self.tabla_horarios = TablaHash(4096)
        self.conteo_buses = TablaHash(4096)
        self.viajes_por_ruta = TablaHash(256)

        self.pila_deshacer = Pila()
        self.pila_rehacer = Pila()
        self._ranking_sucio = True
        self._cache_ranking = []

        self._cargar_estaciones(base + "/estaciones.csv")
        self._cargar_rutas(base + "/rutas.csv")
        self._cargar_horarios(base + "/horarios.csv")

    def _cargar_estaciones(self, ruta_archivo):
        with open(ruta_archivo, mode="r", encoding="utf-8", newline="") as f:
            lector = csv.DictReader(f)
            for fila in lector:
                nombre = fila["nombre"].strip().upper()
                if nombre != "" and not self.tabla_estaciones.contiene(nombre):
                    self.tabla_estaciones.insertar(nombre, True)
                    self.arbol_estaciones.insertar(nombre, True)

    def _cargar_rutas(self, ruta_archivo):
        filas_por_ruta = TablaHash(256)
        with open(ruta_archivo, mode="r", encoding="utf-8", newline="") as f:
            lector = csv.DictReader(f)
            for fila in lector:
                rt = fila["ruta"].strip().upper()
                orden = int(fila["orden"])
                est = fila["estacion"].strip().upper()
                if not self.tabla_estaciones.contiene(est):
                    self.tabla_estaciones.insertar(est, True)
                    self.arbol_estaciones.insertar(est, True)
                lista_filas = filas_por_ruta.obtener(rt)
                if lista_filas is None:
                    lista_filas = []
                    filas_por_ruta.insertar(rt, lista_filas)
                lista_filas.append((orden, est))

        for rt in filas_por_ruta.claves():
            filas = filas_por_ruta.obtener(rt)
            ordenadas = merge_sort(filas, clave_fn=lambda x: x[0])
            lista_doble = ListaDobleRuta()
            for par in ordenadas:
                lista_doble.agregar_al_final(par[1])
            self.tabla_rutas.insertar(rt, lista_doble)

    def _cargar_horarios(self, ruta_archivo):
        crudos = TablaHash(4096)
        with open(ruta_archivo, mode="r", encoding="utf-8", newline="") as f:
            lector = csv.DictReader(f)
            for fila in lector:
                rt = fila["ruta"].strip().upper()
                est = fila["estacion"].strip().upper()
                hora_str = fila["hora"].strip()
                mins = hora_a_minutos(hora_str)
                if mins < 0:
                    continue
                clave = rt + "|" + est
                lista = crudos.obtener(clave)
                if lista is None:
                    lista = []
                    crudos.insertar(clave, lista)
                lista.append((mins, hora_str))

        for clave in crudos.claves():
            lista = crudos.obtener(clave)
            ordenada = merge_sort(lista, clave_fn=lambda x: x[0])
            self.tabla_horarios.insertar(clave, ordenada)
            cantidad = len(ordenada)
            self.conteo_buses.insertar(clave, cantidad)
            rt = clave.split("|")[0]
            actual_max = self.viajes_por_ruta.obtener(rt, 0)
            if cantidad > actual_max:
                self.viajes_por_ruta.insertar(rt, cantidad)

    def estado(self, nombre):
        """R1: Consulta si la estacion existe y si esta abierta."""
        return consultar_estado(self.tabla_estaciones, nombre)

    def autocompletar(self, prefijo, k):
        """R2: Devuelve hasta k estaciones abiertas que empiezan por prefijo."""
        return autocompletar_estaciones(self.arbol_estaciones, prefijo, k)

    def rango(self, desde, hasta):
        """R3: Devuelve todas las estaciones abiertas entre desde y hasta."""
        return listar_rango_estaciones(self.arbol_estaciones, desde, hasta)

    def proximo_bus(self, estacion, ruta, hora):
        """R4: Devuelve la hora del siguiente bus de ruta en estacion >= hora."""
        return consultar_proximo_bus(
            self.tabla_estaciones, self.tabla_rutas, self.tabla_horarios, estacion, ruta, hora
        )

    def viaje(self, origen, destino):
        """R5: Encuentra el viaje directo o con 1 transbordo de menos paradas."""
        return planear_viaje(self.tabla_estaciones, self.tabla_rutas, origen, destino)

    def ranking(self, k):
        """R6: Devuelve las k estaciones abiertas con mas buses diarios."""
        if k <= 0:
            return []
        if self._ranking_sucio:
            self._cache_ranking = calcular_ranking_completo(
                self.tabla_estaciones, self.tabla_rutas, self.conteo_buses, self.viajes_por_ruta
            )
            self._ranking_sucio = False
        return self._cache_ranking[:k]

    def agregar_parada(self, ruta, nueva, despues_de):
        """R7: Agrega nueva parada en ruta despues de despues_de."""
        ok = agregar_parada_ruta(
            self.tabla_estaciones,
            self.tabla_rutas,
            ruta,
            nueva,
            despues_de,
            registrar=True,
            pila_deshacer=self.pila_deshacer,
            pila_rehacer=self.pila_rehacer,
        )
        if ok:
            self._ranking_sucio = True
        return ok

    def quitar_parada(self, ruta, estacion):
        """R7: Quita estacion de ruta."""
        ok = quitar_parada_ruta(
            self.tabla_rutas,
            ruta,
            estacion,
            registrar=True,
            pila_deshacer=self.pila_deshacer,
            pila_rehacer=self.pila_rehacer,
        )
        if ok:
            self._ranking_sucio = True
        return ok

    def recorrido(self, ruta, al_reves=False):
        """R7: Devuelve el recorrido de ruta en sentido normal o inverso."""
        return obtener_recorrido_ruta(self.tabla_rutas, ruta, al_reves=al_reves)

    def cerrar(self, nombre):
        """R8: Cierra una estacion."""
        ok = cambiar_estado_estacion(
            self.tabla_estaciones,
            self.arbol_estaciones,
            nombre,
            False,
            registrar=True,
            pila_deshacer=self.pila_deshacer,
            pila_rehacer=self.pila_rehacer,
        )
        if ok:
            self._ranking_sucio = True
        return ok

    def reabrir(self, nombre):
        """R8: Reabre una estacion."""
        ok = cambiar_estado_estacion(
            self.tabla_estaciones,
            self.arbol_estaciones,
            nombre,
            True,
            registrar=True,
            pila_deshacer=self.pila_deshacer,
            pila_rehacer=self.pila_rehacer,
        )
        if ok:
            self._ranking_sucio = True
        return ok

    def deshacer(self):
        """R9: Deshace la ultima edicion o cierre/reapertura."""
        ok = ejecutar_deshacer(
            self.tabla_estaciones,
            self.arbol_estaciones,
            self.tabla_rutas,
            self.pila_deshacer,
            self.pila_rehacer,
        )
        if ok:
            self._ranking_sucio = True
        return ok

    def rehacer(self):
        """R9: Rehace la ultima operacion deshecha."""
        ok = ejecutar_rehacer(
            self.tabla_estaciones,
            self.arbol_estaciones,
            self.tabla_rutas,
            self.pila_deshacer,
            self.pila_rehacer,
        )
        if ok:
            self._ranking_sucio = True
        return ok