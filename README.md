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

### R4 · Próximo bus (red.proximo_bus(estacion, ruta, hora))
* *Estructura y algoritmo:* Arreglo ordenado de tuplas (minutos, "HH:MM") indexado por (ruta, estación) en TablaHash, consultado mediante *Búsqueda Binaria* (busqueda_binaria_siguiente) para encontrar el primer bus con salida $\ge \text{hora}$.
* *Alternativa descartada:* Búsqueda lineal sobre los horarios ($O(n)$) o búsqueda por interpolación (en horas pico hay alta frecuencia de buses y en madrugada baja frecuencia; al no ser una distribución uniforme, la interpolación puede degradarse a $O(n)$).
* *Complejidad:* *$O(\log n)$, donde *$n$** es la cantidad de horarios diarios de esa ruta en esa estación.

### R5 · Planear un viaje (red.viaje(origen, destino))
* *Estructura y algoritmo:* Recorrido de rutas almacenadas en ListaDobleRuta apoyado en una TablaHash (alcanzables_origen) que guarda el mínimo de paradas desde origen hacia cada estación intermedia abierta, evaluando viajes directos (0 transbordos) y con 1 transbordo en una sola pasada.
* *Alternativa descartada:* Algoritmo de Dijkstra general con cola de prioridad ($O((V + E) \log V)$), innecesario dado que el problema acota el itinerario a máximo 1 transbordo y minimiza el conteo de paradas sin pesos variables.
* *Complejidad:* *$O(n \cdot L)$, donde *$n$* es el número de rutas activas y *$L$** es el promedio de paradas por ruta.

### R6 · Ranking de estaciones (red.ranking(k))
* *Estructura y algoritmo:* *Caché con invalidación perezosa (*lazy invalidation)* ordenada con **Merge Sort* propio. Cuando se edita una ruta (R7) o se cierra/reabre una estación (R8), se marca una bandera _ranking_sucio = True; solo en la siguiente consulta se recalcula y ordena, mientras que las consultas repetidas leen directamente la caché.
* *Alternativa descartada:* Recalcular y ordenar toda la red en cada llamada a ranking(k), lo cual repetiría trabajo $O(n \log n)$ innecesariamente cuando la red no ha sufrido cambios.
* *Complejidad:* *$O(k)$* en consultas con caché vigente y *$O(M + n \log n)$* tras una modificación de la red, donde *$n$* es el número de estaciones y *$M$* es el total de paradas en las rutas.

### R7 · Editar rutas y ver recorrido (agregar_parada, quitar_parada, recorrido)
* *Estructura y algoritmo:* ListaDobleRuta (lista doblemente enlazada con punteros prev y next) combinada con una TablaHash interna (indice_nodos) que apunta directamente al NodoDoble de cada estación dentro de la ruta.
* *Alternativa descartada:* list de Python estándar, donde insertar o eliminar paradas intermedias obliga a desplazar elementos en memoria ($O(n)$), y lista simplemente enlazada, donde recorrer en sentido inverso (al_reves=True) requeriría invertir la lista o usar recursión.
* *Complejidad:* *$O(1)$* promedio para agregar_parada y quitar_parada, y *$O(n)$* para recorrido, donde *$n$* es el número de paradas de la ruta.

### R8 · Cerrar y reabrir estaciones (cerrar, reabrir)
* *Estructura y algoritmo:* Actualización directa de bandera booleana tanto en TablaHash ($O(1)$) como en el NodoAVL correspondiente dentro del ArbolAVL ($O(\log n)$), conservando intacta la estación y sus horarios históricos para futuras reaperturas.
* *Alternativa descartada:* Eliminar físicamente el nodo del ArbolAVL al cerrar y volver a insertarlo al reabrir, lo que complicaría restaurar su información asociada.
* *Complejidad:* *$O(\log n)$* para cerrar y reabrir, donde *$n$* es el número total de estaciones de la red.

### R9 · Deshacer y rehacer (deshacer, rehacer)
* *Estructura y algoritmo:* Dos *Pilas (LIFO)* independientes (pila_deshacer y pila_rehacer) que almacenan tuplas de comando con la información mínima para aplicar la acción inversa. Cualquier cambio nuevo limpia pila_rehacer.
* *Alternativa descartada:* Guardar copias completas (snapshots) de toda la red antes de cada edición, lo que consumiría $O(n + M)$ de memoria y tiempo por operación.
* *Complejidad:* *$O(1)$* al deshacer/rehacer ediciones de ruta (R7) y *$O(\log n)$* al deshacer/rehacer cierres o reaperturas (R8), donde *$n$* es el número total de estaciones.

### R10 · Fila de abordaje en hora pico (simular_fila)
* *Estructura y algoritmo:* Cola *FIFO enlazada* con punteros explícitos _frente y _final para encolar llegadas de pasajeros y desencolar abordajes según la frecuencia y capacidad de cada bus.
* *Alternativa descartada:* Implementar la fila con list.pop(0) de Python, ya que cada desencolado desplaza todos los elementos restantes en memoria y degrada la simulación a $O(n^2)$ con cientos de miles de pasajeros.
* *Complejidad:* *$O(n)$* cuando las llegadas vienen ordenadas cronológicamente ($O(n \log n)$ si requieren ordenamiento previo con Merge Sort), donde *$n$* es el número total de pasajeros simulados.
*

---

## Comando Único de Arranque

Desde la raíz del repositorio (`planeador-transmilenio/`), ejecutar:

```bash
python front/app.py
```

*(No requiere dependencias externas: utiliza únicamente la biblioteca estándar de Python).*

Para regenerar los tres archivos CSV a partir de un paquete GTFS crudo:

```bash
python conversion/convertir_gtfs.py ruta/al/gtfs.zip datos
```

---

## Tratamiento de Datos GTFS y Horas Nocturnas (`25:10`)

El estándar GTFS representa viajes nocturnos posteriores a la medianoche con horas mayores o iguales a `24:00` (por ejemplo, `25:10` equivale a la `01:10` a.m. de la operación del día).
* En `conversion/convertir_gtfs.py`, todas las horas se normalizan módulo 24 (`hh % 24`) al formato estricto `HH:MM` (`00:00` a `23:59`), y los nombres de estaciones se limpian en mayúsculas sin tildes ni duplicados.
* Al cargar `horarios.csv` en `Red.__init__`, los horarios de cada `(ruta, estación)` se convierten a minutos desde `00:00` y se ordenan con **Merge Sort** propio ($O(n \log n)$) para garantizar que la búsqueda binaria de R4 funcione correctamente incluso con rutas de madrugada.

---

## Panel de Rendimiento Empírico (R11)

La pestaña **4. Panel Rendimiento (R11)** de la interfaz gráfica genera redes sintéticas de tamaño creciente ($n = 500, 1000, 2000, 4000$), mide los tiempos de ejecución al duplicar $n \to 2n$ y grafica las curvas junto a la relación de crecimiento empírica:
* **R1 (`estado`):** tiempo constante (~$1.0\times$ al duplicar $n$), confirmando $O(1)$.
* **R2 (`autocompletar`) y R4 (`proximo_bus`):** crecimiento logarítmico (~$1.0\times - 1.2\times$ al duplicar $n$), confirmando $O(\log n)$.
* **R10 (`simular_fila`):** duplica el tiempo de ejecución (~$2.0\times$ al duplicar $n$), confirmando $O(n)$.