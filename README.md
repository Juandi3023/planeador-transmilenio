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