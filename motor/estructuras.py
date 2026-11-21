"""Estructuras de datos fundamentales implementadas desde cero sin librerias prohibidas."""


class TablaHash:
    """Tabla hash con encadenamiento (chaining) y redimensionamiento dinamico."""

    def __init__(self, capacidad_inicial=16):
        self._capacidad = capacidad_inicial if capacidad_inicial >= 8 else 8
        self._cubetas = [[] for _ in range(self._capacidad)]
        self._tamano = 0

    def _hash(self, clave):
        texto = str(clave)
        h = 0
        for ch in texto:
            h = (h * 31 + ord(ch)) % self._capacidad
        return h

    def _redimensionar(self):
        viejas = self._cubetas
        self._capacidad = self._capacidad * 2
        self._cubetas = [[] for _ in range(self._capacidad)]
        self._tamano = 0
        for cubeta in viejas:
            for par in cubeta:
                self.insertar(par[0], par[1])

    def insertar(self, clave, valor):
        if (self._tamano + 1) * 4 > self._capacidad * 3:
            self._redimensionar()
        idx = self._hash(clave)
        cubeta = self._cubetas[idx]
        for par in cubeta:
            if par[0] == clave:
                par[1] = valor
                return
        cubeta.append([clave, valor])
        self._tamano += 1

    def obtener(self, clave, defecto=None):
        idx = self._hash(clave)
        cubeta = self._cubetas[idx]
        for par in cubeta:
            if par[0] == clave:
                return par[1]
        return defecto

    def contiene(self, clave):
        idx = self._hash(clave)
        cubeta = self._cubetas[idx]
        for par in cubeta:
            if par[0] == clave:
                return True
        return False

    def eliminar(self, clave):
        idx = self._hash(clave)
        cubeta = self._cubetas[idx]
        n = len(cubeta)
        for i in range(n):
            if cubeta[i][0] == clave:
                cubeta[i] = cubeta[n - 1]
                cubeta.pop()
                self._tamano -= 1
                return True
        return False

    def valores(self):
        salida = []
        for cubeta in self._cubetas:
            for par in cubeta:
                salida.append(par[1])
        return salida

    def claves(self):
        salida = []
        for cubeta in self._cubetas:
            for par in cubeta:
                salida.append(par[0])
        return salida

    def __len__(self):
        return self._tamano


class NodoAVL:
    """Nodo para Arbol Binario de Busqueda Balanceado (AVL)."""

    def __init__(self, clave, abierto=True):
        self.clave = clave
        self.abierto = abierto
        self.izq = None
        self.der = None
        self.altura = 1


class ArbolAVL:
    """AVL para almacenar estaciones ordenadas alfabeticamente con altura O(log n)."""

    def __init__(self):
        self.raiz = None

    def _altura(self, nodo):
        return nodo.altura if nodo is not None else 0

    def _actualizar_altura(self, nodo):
        hi = self._altura(nodo.izq)
        hd = self._altura(nodo.der)
        nodo.altura = (hi if hi > hd else hd) + 1

    def _factor_balance(self, nodo):
        return self._altura(nodo.izq) - self._altura(nodo.der) if nodo is not None else 0

    def _rotar_derecha(self, y):
        x = y.izq
        t2 = x.der
        x.der = y
        y.izq = t2
        self._actualizar_altura(y)
        self._actualizar_altura(x)
        return x

    def _rotar_izquierda(self, x):
        y = x.der
        t2 = y.izq
        y.izq = x
        x.der = t2
        self._actualizar_altura(x)
        self._actualizar_altura(y)
        return y

    def insertar(self, clave, abierto=True):
        self.raiz = self._insertar(self.raiz, clave, abierto)

    def _insertar(self, nodo, clave, abierto):
        if nodo is None:
            return NodoAVL(clave, abierto)
        if clave < nodo.clave:
            nodo.izq = self._insertar(nodo.izq, clave, abierto)
        elif clave > nodo.clave:
            nodo.der = self._insertar(nodo.der, clave, abierto)
        else:
            nodo.abierto = abierto
            return nodo

        self._actualizar_altura(nodo)
        fb = self._factor_balance(nodo)

        if fb > 1 and clave < nodo.izq.clave:
            return self._rotar_derecha(nodo)
        if fb < -1 and clave > nodo.der.clave:
            return self._rotar_izquierda(nodo)
        if fb > 1 and clave > nodo.izq.clave:
            nodo.izq = self._rotar_izquierda(nodo.izq)
            return self._rotar_derecha(nodo)
        if fb < -1 and clave < nodo.der.clave:
            nodo.der = self._rotar_derecha(nodo.der)
            return self._rotar_izquierda(nodo)
        return nodo

    def buscar_nodo(self, clave):
        actual = self.raiz
        while actual is not None:
            if clave == actual.clave:
                return actual
            elif clave < actual.clave:
                actual = actual.izq
            else:
                actual = actual.der
        return None

    def autocompletar(self, prefijo, k):
        resultado = []
        if k <= 0:
            return resultado
        self._autocompletar(self.raiz, prefijo, k, resultado)
        return resultado

    def _autocompletar(self, nodo, prefijo, k, resultado):
        if nodo is None or len(resultado) >= k:
            return
        if nodo.clave >= prefijo:
            self._autocompletar(nodo.izq, prefijo, k, resultado)
        if len(resultado) >= k:
            return
        if nodo.abierto and nodo.clave.startswith(prefijo):
            resultado.append(nodo.clave)
        if len(resultado) >= k:
            return
        if nodo.clave <= prefijo or nodo.clave.startswith(prefijo):
            self._autocompletar(nodo.der, prefijo, k, resultado)

    def rango(self, desde, hasta):
        resultado = []
        if desde > hasta:
            return resultado
        self._rango(self.raiz, desde, hasta, resultado)
        return resultado

    def _rango(self, nodo, desde, hasta, resultado):
        if nodo is None:
            return
        if desde < nodo.clave:
            self._rango(nodo.izq, desde, hasta, resultado)
        if desde <= nodo.clave <= hasta and nodo.abierto:
            resultado.append(nodo.clave)
        if hasta > nodo.clave:
            self._rango(nodo.der, desde, hasta, resultado)


class NodoDoble:
    """Nodo para Lista Doblemente Enlazada de paradas de una ruta."""

    def __init__(self, estacion):
        self.estacion = estacion
        self.prev = None
        self.next = None


class ListaDobleRuta:
    """Lista doblemente enlazada con indice hash para insercion/eliminacion en O(1)."""

    def __init__(self):
        self.head = None
        self.tail = None
        self.tamano = 0
        self.indice_nodos = TablaHash(16)

    def agregar_al_final(self, estacion):
        if self.indice_nodos.contiene(estacion):
            return False
        nuevo = NodoDoble(estacion)
        if self.head is None:
            self.head = nuevo
            self.tail = nuevo
        else:
            nuevo.prev = self.tail
            self.tail.next = nuevo
            self.tail = nuevo
        self.indice_nodos.insertar(estacion, nuevo)
        self.tamano += 1
        return True

    def agregar_despues_de(self, nueva, despues_de):
        if self.indice_nodos.contiene(nueva):
            return False
        if despues_de is None:
            nuevo = NodoDoble(nueva)
            if self.head is None:
                self.head = nuevo
                self.tail = nuevo
            else:
                nuevo.next = self.head
                self.head.prev = nuevo
                self.head = nuevo
            self.indice_nodos.insertar(nueva, nuevo)
            self.tamano += 1
            return True

        nodo_ref = self.indice_nodos.obtener(despues_de)
        if nodo_ref is None:
            return False
        nuevo = NodoDoble(nueva)
        nuevo.prev = nodo_ref
        nuevo.next = nodo_ref.next
        if nodo_ref.next is not None:
            nodo_ref.next.prev = nuevo
        else:
            self.tail = nuevo
        nodo_ref.next = nuevo
        self.indice_nodos.insertar(nueva, nuevo)
        self.tamano += 1
        return True

    def quitar(self, estacion):
        nodo = self.indice_nodos.obtener(estacion)
        if nodo is None:
            return False, None
        anterior = nodo.prev.estacion if nodo.prev is not None else None
        if nodo.prev is not None:
            nodo.prev.next = nodo.next
        else:
            self.head = nodo.next
        if nodo.next is not None:
            nodo.next.prev = nodo.prev
        else:
            self.tail = nodo.prev
        self.indice_nodos.eliminar(estacion)
        self.tamano -= 1
        return True, anterior

    def contiene(self, estacion):
        return self.indice_nodos.contiene(estacion)

    def a_lista(self, al_reves=False):
        salida = []
        if not al_reves:
            actual = self.head
            while actual is not None:
                salida.append(actual.estacion)
                actual = actual.next
        else:
            actual = self.tail
            while actual is not None:
                salida.append(actual.estacion)
                actual = actual.prev
        return salida


class Pila:
    """Pila LIFO respaldada por arreglo dinamico: push y pop en O(1)."""

    def __init__(self):
        self._datos = []

    def push(self, item):
        self._datos.append(item)

    def pop(self):
        if len(self._datos) == 0:
            return None
        return self._datos.pop()

    def esta_vacia(self):
        return len(self._datos) == 0

    def limpiar(self):
        self._datos = []


class _NodoCola:
    def __init__(self, valor):
        self.valor = valor
        self.next = None


class Cola:
    """Cola FIFO enlazada con punteros frente y final: enqueue y dequeue en O(1)."""

    def __init__(self):
        self._frente = None
        self._final = None
        self._tamano = 0

    def enqueue(self, valor):
        nuevo = _NodoCola(valor)
        if self._final is None:
            self._frente = nuevo
            self._final = nuevo
        else:
            self._final.next = nuevo
            self._final = nuevo
        self._tamano += 1

    def dequeue(self):
        if self._frente is None:
            return None
        val = self._frente.valor
        self._frente = self._frente.next
        if self._frente is None:
            self._final = None
        self._tamano -= 1
        return val

    def frente(self):
        return self._frente.valor if self._frente is not None else None

    def esta_vacia(self):
        return self._tamano == 0

    def __len__(self):
        return self._tamano


def merge_sort(lista, clave_fn=None):
    """Ordenamiento Merge Sort estable en O(n log n) garantizado."""
    n = len(lista)
    if n <= 1:
        return lista[:]
    medio = n // 2
    izq = merge_sort(lista[:medio], clave_fn)
    der = merge_sort(lista[medio:], clave_fn)
    return _mezclar(izq, der, clave_fn)


def _mezclar(izq, der, clave_fn):
    resultado = []
    i = 0
    j = 0
    ni = len(izq)
    nj = len(der)
    while i < ni and j < nj:
        vi = clave_fn(izq[i]) if clave_fn is not None else izq[i]
        vj = clave_fn(der[j]) if clave_fn is not None else der[j]
        if vi <= vj:
            resultado.append(izq[i])
            i += 1
        else:
            resultado.append(der[j])
            j += 1
    while i < ni:
        resultado.append(izq[i])
        i += 1
    while j < nj:
        resultado.append(der[j])
        j += 1
    return resultado


def busqueda_binaria_siguiente(lista_ordenada, objetivo):
    """Devuelve el primer elemento >= objetivo en lista_ordenada en O(log n), o None."""
    izq = 0
    der = len(lista_ordenada) - 1
    ans = None
    while izq <= der:
        medio = (izq + der) // 2
        if lista_ordenada[medio] >= objetivo:
            ans = lista_ordenada[medio]
            der = medio - 1
        else:
            izq = medio + 1
    return ans