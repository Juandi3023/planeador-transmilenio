# Planeador de Viajes TransMilenio · Estructuras de Datos y Algoritmos

Aplicación de escritorio y motor algorítmico implementado desde cero en Python puro (`motor/`) sin uso de `dict`, `set`, `sorted`, `.sort()`, búsquedas nativas con `in` sobre listas ni librerías externas.

---

## Decisiones de Diseño, Estructuras y Complejidad Big-O (R12)

### R1 · Buscar una estación (`red.estado(nombre)`)
* **Estructura y algoritmo:** `TablaHash` propia con encadenamiento (*chaining*) y redimensionamiento dinámico cuando el factor de carga supera $0.75$.
* **Alternativa descartada:** Búsqueda lineal sobre lista ($O(n)$) o búsqueda binaria sobre arreglo ordenado ($O(\log n)$). Se descartaron porque R1 es la consulta más frecuente de la aplicación y la tabla hash permite acceso directo en tiempo constante.
* **Complejidad:** **$O(1)$** promedio ($O(n)$ en el peor caso teórico de colisiones), donde **$n$** es el número total de estaciones de la red.

### R2 · Autocompletar (`red.autocompletar(prefijo, k)`)
* **Estructura y algoritmo:** `ArbolAVL` (Árbol Binario de Búsqueda autobalanceado mediante rotaciones simples y dobles) con recorrido *in-order* podado que se detiene al recolectar $k$ estaciones abiertas.
* **Alternativa descartada:** `TablaHash` (pierde el orden alfabético y obligaría a recorrer y ordenar todas las estaciones en $O(n \log n)$) y un BST simple sin balanceo (al cargar `estaciones.csv` ordenado alfabéticamente, un BST normal degeneraría en una lista enlazada de altura $O(n)$).
* **Complejidad:** **$O(\log n + k)$**, donde **$n$** es el número total de estaciones y **$k$** es el límite máximo de sugerencias solicitadas.

### R3 · Listar un rango (`red.rango(desde, hasta)`)
* **Estructura y algoritmo:** Recorrido *in-order* acotado sobre el `ArbolAVL`, podando subárboles izquierdos menores a `desde` y subárboles derechos mayores a `hasta`.
* **Alternativa descartada:** Filtrado lineal sobre un arreglo ($O(n)$), que inspecciona toda la red aunque el rango solicitado tenga pocas estaciones.
* **Complejidad:** **$O(\log n + m)$**, donde **$n$** es el número total de estaciones y **$m$** es la cantidad de estaciones abiertas dentro del intervalo `[desde, hasta]`.