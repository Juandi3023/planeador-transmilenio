"""Script de conversion desde GTFS crudo de TransMilenio a estaciones.csv, rutas.csv y horarios.csv."""
import csv
import os
import sys
import unicodedata
import zipfile

def normalizar_texto(texto):
   """Convierte a mayusculas, elimina tildes y limpia espacios sobrantes."""
   s = texto.strip().upper()
   s = unicodedata.normalize("NFD", s)
   s = "".join(c for c in s if unicodedata.category(c) != "Mn")
   return " ".join(s.split())

def normalizar_hora(hora_gtfs):
   """Convierte horas GTFS (incluyendo >= 24:00 como 25:10) al formato HH:MM valido (00:00-23:59)."""
   partes = hora_gtfs.strip().split(":")
   hh = int(partes[0]) % 24
   mm = int(partes[1])
   return f"{hh:02d}:{mm:02d}"

def _abrir_gtfs(origen_gtfs, nombre_archivo):
   if zipfile.is_zipfile(origen_gtfs):
       zf = zipfile.ZipFile(origen_gtfs, "r")
       for member in zf.namelist():
           if member.endswith(nombre_archivo):
               raw = zf.read(member).decode("utf-8-sig").splitlines()
               return csv.DictReader(raw)
       raise FileNotFoundError(f"No se encontro {nombre_archivo} dentro de {origen_gtfs}")
   ruta = os.path.join(origen_gtfs, nombre_archivo)
   f = open(ruta, mode="r", encoding="utf-8-sig", newline="")
   return csv.DictReader(f)

def convertir_gtfs(origen_gtfs, carpeta_salida):
   os.makedirs(carpeta_salida, exist_ok=True)
   # 1. Leer stops.txt
   stops_map = {}
   estaciones_set = set()
   for row in _abrir_gtfs(origen_gtfs, "stops.txt"):
       stop_id = row["stop_id"].strip()
       nombre = normalizar_texto(row["stop_name"])
       if nombre:
           stops_map[stop_id] = nombre
           estaciones_set.add(nombre)
   # 2. Leer routes.txt
   routes_map = {}
   for row in _abrir_gtfs(origen_gtfs, "routes.txt"):
       route_id = row["route_id"].strip()
       short_name = normalizar_texto(row.get("route_short_name") or row.get("route_long_name") or route_id)
       routes_map[route_id] = short_name
   # 3. Leer trips.txt (separar por sentido usando direction_id)
   trip_to_ruta = {}
   for row in _abrir_gtfs(origen_gtfs, "trips.txt"):
       trip_id = row["trip_id"].strip()
       route_id = row["route_id"].strip()
       direction = row.get("direction_id", "0").strip() or "0"
       base_name = routes_map.get(route_id, route_id)
       ruta_sentido = f"{base_name}-{int(direction) + 1}"
       trip_to_ruta[trip_id] = ruta_sentido
   # 4. Leer stop_times.txt
   viajes_paradas = {}
   horarios_filas = []
   for row in _abrir_gtfs(origen_gtfs, "stop_times.txt"):
       trip_id = row["trip_id"].strip()
       if trip_id not in trip_to_ruta:
           continue
       stop_id = row["stop_id"].strip()
       if stop_id not in stops_map:
           continue
       ruta = trip_to_ruta[trip_id]
       estacion = stops_map[stop_id]
       seq = int(row["stop_sequence"])
       hora = normalizar_hora(row["departure_time"])
       viajes_paradas.setdefault(trip_id, []).append((seq, estacion))
       horarios_filas.append((ruta, estacion, hora))
   # Seleccionar el recorrido patron (el viaje con mas paradas) por cada ruta
   patron_por_ruta = {}
   for trip_id, paradas in viajes_paradas.items():
       ruta = trip_to_ruta[trip_id]
       paradas_ord = sorted(paradas, key=lambda x: x[0])
       secuencia_limpia = []
       vistos = set()
       for _, est in paradas_ord:
           if est not in vistos:
               vistos.add(est)
               secuencia_limpia.append(est)
       if len(secuencia_limpia) > len(patron_por_ruta.get(ruta, [])):
           patron_por_ruta[ruta] = secuencia_limpia
   # 5. Escribir estaciones.csv
   with open(os.path.join(carpeta_salida, "estaciones.csv"), "w", encoding="utf-8", newline="") as f:
       w = csv.writer(f)
       w.writerow(["nombre"])
       for est in sorted(estaciones_set):
           w.writerow([est])
   # 6. Escribir rutas.csv
   with open(os.path.join(carpeta_salida, "rutas.csv"), "w", encoding="utf-8", newline="") as f:
       w = csv.writer(f)
       w.writerow(["ruta", "orden", "estacion"])
       for ruta in sorted(patron_por_ruta.keys()):
           for idx, est in enumerate(patron_por_ruta[ruta], start=1):
               w.writerow([ruta, idx, est])
   # 7. Escribir horarios.csv
   with open(os.path.join(carpeta_salida, "horarios.csv"), "w", encoding="utf-8", newline="") as f:
       w = csv.writer(f)
       w.writerow(["ruta", "estacion", "hora"])
       for fila in horarios_filas:
           w.writerow(fila)
   print(f"Conversion exitosa en '{carpeta_salida}': {len(estaciones_set)} estaciones, {len(patron_por_ruta)} rutas, {len(horarios_filas)} horarios.")

if __name__ == "__main__":
   if len(sys.argv) < 2:
       print("Uso: python conversion/convertir_gtfs.py <ruta_gtfs.zip_o_carpeta> [carpeta_salida]")
       sys.exit(1)
   origen = sys.argv[1]
   destino = sys.argv[2] if len(sys.argv) >= 3 else "datos"
   convertir_gtfs(origen, destino)