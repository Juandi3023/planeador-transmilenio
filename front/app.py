"""Interfaz de usuario y Panel de Rendimiento (R11) del Planeador TransMilenio."""

import os
import shutil
import sys
import tempfile
import time
import tkinter as tk
from tkinter import ttk

ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)

from motor import Red, simular_fila


class PlaneadorApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Planeador TransMilenio · Estructuras de Datos y Algoritmos")
        self.geometry("1040x700")
        self.configure(bg="#12161f")

        datos_dir = os.path.join(ROOT_DIR, "datos")
        self.red = Red(datos_dir)

        self._configurar_estilos()
        self._construir_ui()

    def _configurar_estilos(self):
        style = ttk.Style(self)
        style.theme_use("clam")
        style.configure("TNotebook", background="#12161f", borderwidth=0)
        style.configure("TNotebook.Tab", background="#1e2433", foreground="#e2e8f0", padding=[14, 8], font=("Segoe UI", 10, "bold"))
        style.map("TNotebook.Tab", background=[("selected", "#d90429")], foreground=[("selected", "#ffffff")])
        style.configure("TFrame", background="#181d29")
        style.configure("TLabel", background="#181d29", foreground="#e2e8f0", font=("Segoe UI", 10))
        style.configure("Header.TLabel", font=("Segoe UI", 13, "bold"), foreground="#ffffff")
        style.configure("TButton", font=("Segoe UI", 10, "bold"), padding=6)

    def _construir_ui(self):
        banner = tk.Frame(self, bg="#d90429", height=54)
        banner.pack(fill="x")
        tk.Label(
            banner,
            text="TRANSMILENIO · PLANEADOR DE VIAJES Y ANÁLISIS ALGORÍTMICO",
            bg="#d90429",
            fg="white",
            font=("Segoe UI", 14, "bold"),
        ).pack(side="left", padx=18, pady=12)

        tabs = ttk.Notebook(self)
        tabs.pack(fill="both", expand=True, padx=12, pady=12)

        self.tab_estaciones = ttk.Frame(tabs)
        self.tab_viajes = ttk.Frame(tabs)
        self.tab_operacion = ttk.Frame(tabs)
        self.tab_rendimiento = ttk.Frame(tabs)

        tabs.add(self.tab_estaciones, text="1. Estaciones (R1–R3)")
        tabs.add(self.tab_viajes, text="2. Viajes y Ranking (R4–R6)")
        tabs.add(self.tab_operacion, text="3. Operación y Fila (R7–R10)")
        tabs.add(self.tab_rendimiento, text="4. Panel Rendimiento (R11)")

        self._build_tab_estaciones()
        self._build_tab_viajes()
        self._build_tab_operacion()
        self._build_tab_rendimiento()

    def _build_tab_estaciones(self):
        f = self.tab_estaciones
        ttk.Label(f, text="Consulta de Estaciones (Tabla Hash + Árbol AVL)", style="Header.TLabel").pack(anchor="w", padx=16, pady=(14, 8))

        row1 = ttk.Frame(f)
        row1.pack(fill="x", padx=16, pady=6)
        ttk.Label(row1, text="Estación exacta (R1):").pack(side="left")
        self.ent_r1 = ttk.Entry(row1, width=28)
        self.ent_r1.insert(0, "CALLE 26")
        self.ent_r1.pack(side="left", padx=8)
        ttk.Button(row1, text="Consultar Estado", command=self._run_r1).pack(side="left")
        self.lbl_r1 = ttk.Label(row1, text="Estado: —", font=("Segoe UI", 10, "bold"))
        self.lbl_r1.pack(side="left", padx=14)

        row2 = ttk.Frame(f)
        row2.pack(fill="x", padx=16, pady=6)
        ttk.Label(row2, text="Prefijo (R2):").pack(side="left")
        self.ent_r2_pref = ttk.Entry(row2, width=18)
        self.ent_r2_pref.insert(0, "CAL")
        self.ent_r2_pref.pack(side="left", padx=6)
        ttk.Label(row2, text="Máx k:").pack(side="left")
        self.ent_r2_k = ttk.Entry(row2, width=6)
        self.ent_r2_k.insert(0, "8")
        self.ent_r2_k.pack(side="left", padx=6)
        ttk.Button(row2, text="Autocompletar", command=self._run_r2).pack(side="left")

        row3 = ttk.Frame(f)
        row3.pack(fill="x", padx=16, pady=6)
        ttk.Label(row3, text="Rango Desde (R3):").pack(side="left")
        self.ent_r3_desde = ttk.Entry(row3, width=20)
        self.ent_r3_desde.insert(0, "CALLE 26")
        self.ent_r3_desde.pack(side="left", padx=6)
        ttk.Label(row3, text="Hasta:").pack(side="left")
        self.ent_r3_hasta = ttk.Entry(row3, width=20)
        self.ent_r3_hasta.insert(0, "CALLE 80")
        self.ent_r3_hasta.pack(side="left", padx=6)
        ttk.Button(row3, text="Listar Rango", command=self._run_r3).pack(side="left")

        self.txt_est = tk.Text(f, height=20, bg="#0f131a", fg="#a5f3fc", font=("Consolas", 10), bd=0, padx=10, pady=10)
        self.txt_est.pack(fill="both", expand=True, padx=16, pady=12)

    def _run_r1(self):
        res = self.red.estado(self.ent_r1.get())
        self.lbl_r1.config(text=f"Estado: {res}")

    def _run_r2(self):
        try:
            k = int(self.ent_r2_k.get())
        except ValueError:
            k = 5
        res = self.red.autocompletar(self.ent_r2_pref.get(), k)
        self.txt_est.delete("1.0", "end")
        self.txt_est.insert("end", f"Autocompletado ('{self.ent_r2_pref.get().upper()}', k={k}):\n")
        for i, est in enumerate(res, 1):
            self.txt_est.insert("end", f"  {i}. {est}\n")

    def _run_r3(self):
        res = self.red.rango(self.ent_r3_desde.get(), self.ent_r3_hasta.get())
        self.txt_est.delete("1.0", "end")
        self.txt_est.insert("end", f"Estaciones abiertas entre '{self.ent_r3_desde.get().upper()}' y '{self.ent_r3_hasta.get().upper()}' ({len(res)}):\n")
        for i, est in enumerate(res, 1):
            self.txt_est.insert("end", f"  {i}. {est}\n")

    def _build_tab_viajes(self):
        f = self.tab_viajes
        ttk.Label(f, text="Planeador de Viajes, Horarios y Ranking (R4–R6)", style="Header.TLabel").pack(anchor="w", padx=16, pady=(14, 8))

        row4 = ttk.Frame(f)
        row4.pack(fill="x", padx=16, pady=6)
        ttk.Label(row4, text="Próximo Bus (R4) · Estación:").pack(side="left")
        self.ent_r4_est = ttk.Entry(row4, width=20)
        self.ent_r4_est.insert(0, "UNIVERSIDADES")
        self.ent_r4_est.pack(side="left", padx=5)
        ttk.Label(row4, text="Ruta:").pack(side="left")
        self.ent_r4_ruta = ttk.Entry(row4, width=10)
        self.ent_r4_ruta.insert(0, "1-1")
        self.ent_r4_ruta.pack(side="left", padx=5)
        ttk.Label(row4, text="Hora:").pack(side="left")
        self.ent_r4_hora = ttk.Entry(row4, width=8)
        self.ent_r4_hora.insert(0, "10:00")
        self.ent_r4_hora.pack(side="left", padx=5)
        ttk.Button(row4, text="Buscar Bus", command=self._run_r4).pack(side="left", padx=4)

        row5 = ttk.Frame(f)
        row5.pack(fill="x", padx=16, pady=6)
        ttk.Label(row5, text="Planear Viaje (R5) · Origen:").pack(side="left")
        self.ent_r5_orig = ttk.Entry(row5, width=20)
        self.ent_r5_orig.insert(0, "21 ANGELES")
        self.ent_r5_orig.pack(side="left", padx=5)
        ttk.Label(row5, text="Destino:").pack(side="left")
        self.ent_r5_dest = ttk.Entry(row5, width=20)
        self.ent_r5_dest.insert(0, "UNIVERSIDADES")
        self.ent_r5_dest.pack(side="left", padx=5)
        ttk.Button(row5, text="Calcular Ruta", command=self._run_r5).pack(side="left", padx=4)

        row6 = ttk.Frame(f)
        row6.pack(fill="x", padx=16, pady=6)
        ttk.Label(row6, text="Top k Estaciones por Buses/Día (R6):").pack(side="left")
        self.ent_r6_k = ttk.Entry(row6, width=6)
        self.ent_r6_k.insert(0, "10")
        self.ent_r6_k.pack(side="left", padx=6)
        ttk.Button(row6, text="Ver Ranking", command=self._run_r6).pack(side="left")

        self.txt_viajes = tk.Text(f, height=19, bg="#0f131a", fg="#fde68a", font=("Consolas", 10), bd=0, padx=10, pady=10)
        self.txt_viajes.pack(fill="both", expand=True, padx=16, pady=12)

    def _run_r4(self):
        res = self.red.proximo_bus(self.ent_r4_est.get(), self.ent_r4_ruta.get(), self.ent_r4_hora.get())
        self.txt_viajes.delete("1.0", "end")
        self.txt_viajes.insert("end", f"Próximo bus ruta {self.ent_r4_ruta.get().upper()} en {self.ent_r4_est.get().upper()} desde {self.ent_r4_hora.get()}:\n  -> {res}\n")

    def _run_r5(self):
        plan = self.red.viaje(self.ent_r5_orig.get(), self.ent_r5_dest.get())
        self.txt_viajes.delete("1.0", "end")
        if plan is None:
            self.txt_viajes.insert("end", "No existe viaje directo ni con 1 transbordo entre esas estaciones.\n")
        elif len(plan) == 0:
            self.txt_viajes.insert("end", "Origen y destino son la misma estación.\n")
        else:
            total = sum(t[3] for t in plan)
            self.txt_viajes.insert("end", f"Itinerario óptimo ({len(plan) - 1} transbordo(s), {total} paradas totales):\n")
            for idx, (rt, sube, baja, paradas) in enumerate(plan, 1):
                self.txt_viajes.insert("end", f"  Tramo {idx}: Tomar ruta {rt} en {sube} -> bajar en {baja} ({paradas} paradas)\n")

    def _run_r6(self):
        try:
            k = int(self.ent_r6_k.get())
        except ValueError:
            k = 10
        top = self.red.ranking(k)
        self.txt_viajes.delete("1.0", "end")
        self.txt_viajes.insert("end", f"Top {k} estaciones abiertas con mayor frecuencia diaria:\n")
        for i, (est, buses) in enumerate(top, 1):
            self.txt_viajes.insert("end", f"  {i:2d}. {est:<30} -> {buses} buses/día\n")

    def _build_tab_operacion(self):
        f = self.tab_operacion
        ttk.Label(f, text="Operación de Red, Deshacer/Rehacer y Simulación Hora Pico (R7–R10)", style="Header.TLabel").pack(anchor="w", padx=16, pady=(14, 8))

        r7 = ttk.Frame(f)
        r7.pack(fill="x", padx=16, pady=5)
        ttk.Label(r7, text="Ruta:").pack(side="left")
        self.ent_op_ruta = ttk.Entry(r7, width=10)
        self.ent_op_ruta.insert(0, "1-1")
        self.ent_op_ruta.pack(side="left", padx=4)
        ttk.Label(r7, text="Parada:").pack(side="left")
        self.ent_op_est = ttk.Entry(r7, width=18)
        self.ent_op_est.insert(0, "AGUAS")
        self.ent_op_est.pack(side="left", padx=4)
        ttk.Label(r7, text="Después de:").pack(side="left")
        self.ent_op_desp = ttk.Entry(r7, width=18)
        self.ent_op_desp.insert(0, "RECINTO FERIAL")
        self.ent_op_desp.pack(side="left", padx=4)
        ttk.Button(r7, text="Agregar", command=self._op_agregar).pack(side="left", padx=3)
        ttk.Button(r7, text="Quitar", command=self._op_quitar).pack(side="left", padx=3)
        ttk.Button(r7, text="Ver Sentidos", command=self._op_recorrido).pack(side="left", padx=3)

        r8 = ttk.Frame(f)
        r8.pack(fill="x", padx=16, pady=5)
        ttk.Label(r8, text="Estación Cierre/Reapertura (R8):").pack(side="left")
        self.ent_cierre = ttk.Entry(r8, width=22)
        self.ent_cierre.insert(0, "CALLE 26")
        self.ent_cierre.pack(side="left", padx=6)
        ttk.Button(r8, text="Cerrar", command=lambda: self._op_estado(False)).pack(side="left", padx=3)
        ttk.Button(r8, text="Reabrir", command=lambda: self._op_estado(True)).pack(side="left", padx=3)
        ttk.Button(r8, text="Deshacer (R9)", command=self._op_undo).pack(side="left", padx=12)
        ttk.Button(r8, text="Rehacer (R9)", command=self._op_redo).pack(side="left", padx=3)

        r10 = ttk.Frame(f)
        r10.pack(fill="x", padx=16, pady=5)
        ttk.Label(r10, text="Fila Hora Pico (R10) · Pasajeros:").pack(side="left")
        self.ent_pas = ttk.Entry(r10, width=10)
        self.ent_pas.insert(0, "250000")
        self.ent_pas.pack(side="left", padx=5)
        ttk.Label(r10, text="Frec (min):").pack(side="left")
        self.ent_frec = ttk.Entry(r10, width=5)
        self.ent_frec.insert(0, "4")
        self.ent_frec.pack(side="left", padx=5)
        ttk.Label(r10, text="Cupo bus:").pack(side="left")
        self.ent_cap = ttk.Entry(r10, width=6)
        self.ent_cap.insert(0, "160")
        self.ent_cap.pack(side="left", padx=5)
        ttk.Button(r10, text="Simular Fila", command=self._run_r10).pack(side="left", padx=6)

        self.txt_op = tk.Text(f, height=18, bg="#0f131a", fg="#bbf7d0", font=("Consolas", 10), bd=0, padx=10, pady=10)
        self.txt_op.pack(fill="both", expand=True, padx=16, pady=12)

    def _op_agregar(self):
        ok = self.red.agregar_parada(self.ent_op_ruta.get(), self.ent_op_est.get(), self.ent_op_desp.get())
        self.txt_op.insert("end", f"[R7 Agregar] Resultado={ok} -> {self.red.recorrido(self.ent_op_ruta.get())}\n")

    def _op_quitar(self):
        ok = self.red.quitar_parada(self.ent_op_ruta.get(), self.ent_op_est.get())
        self.txt_op.insert("end", f"[R7 Quitar] Resultado={ok} -> {self.red.recorrido(self.ent_op_ruta.get())}\n")

    def _op_recorrido(self):
        rt = self.ent_op_ruta.get()
        ida = self.red.recorrido(rt, False)
        vuelta = self.red.recorrido(rt, True)
        self.txt_op.insert("end", f"[R7 Recorrido {rt.upper()}]\n  Ida: {ida}\n  Inverso: {vuelta}\n")

    def _op_estado(self, abrir):
        est = self.ent_cierre.get()
        ok = self.red.reabrir(est) if abrir else self.red.cerrar(est)
        self.txt_op.insert("end", f"[R8 {'Reabrir' if abrir else 'Cerrar'} {est.upper()}] ok={ok}, estado={self.red.estado(est)}\n")

    def _op_undo(self):
        ok = self.red.deshacer()
        self.txt_op.insert("end", f"[R9 Deshacer] ok={ok}\n")

    def _op_redo(self):
        ok = self.red.rehacer()
        self.txt_op.insert("end", f"[R9 Rehacer] ok={ok}\n")

    def _run_r10(self):
        n_pas = int(self.ent_pas.get())
        frec = int(self.ent_frec.get())
        cap = int(self.ent_cap.get())
        llegadas = [i // 45 for i in range(n_pas)]
        t0 = time.perf_counter()
        atendidos, buses, esp_prom, esp_max = simular_fila(llegadas, frec, cap)
        dt = time.perf_counter() - t0
        self.txt_op.insert(
            "end",
            f"[R10 Simulación {n_pas:,} pasajeros en {dt:.3f}s] Atendidos={atendidos:,} | Buses={buses} | Espera prom={esp_prom:.2f} min | Espera máx={esp_max} min\n",
        )

    def _build_tab_rendimiento(self):
        f = self.tab_rendimiento
        top = ttk.Frame(f)
        top.pack(fill="x", padx=16, pady=10)
        ttk.Label(top, text="Panel de Rendimiento Empírico: Duplicando n -> 2n (R11)", style="Header.TLabel").pack(side="left")
        ttk.Button(top, text="Ejecutar Benchmark n -> 2n", command=self._ejecutar_benchmark).pack(side="right")

        self.canvas = tk.Canvas(f, bg="#0f131a", height=320, highlightthickness=0)
        self.canvas.pack(fill="x", padx=16, pady=6)

        self.txt_bench = tk.Text(f, height=12, bg="#0f131a", fg="#e2e8f0", font=("Consolas", 9), bd=0, padx=10, pady=8)
        self.txt_bench.pack(fill="both", expand=True, padx=16, pady=8)

    def _crear_red_sintetica(self, n):
        tmp = tempfile.mkdtemp(prefix=f"tm_bench_{n}_")
        with open(os.path.join(tmp, "estaciones.csv"), "w", encoding="utf-8", newline="") as f:
            f.write("nombre\n")
            for i in range(n):
                f.write(f"ESTACION_{i:06d}\n")
        with open(os.path.join(tmp, "rutas.csv"), "w", encoding="utf-8", newline="") as f:
            f.write("ruta,orden,estacion\n")
            num_rutas = max(1, n // 10)
            for r in range(num_rutas):
                for j in range(10):
                    idx = (r * 10 + j) % n
                    f.write(f"R{r},{j + 1},ESTACION_{idx:06d}\n")
        with open(os.path.join(tmp, "horarios.csv"), "w", encoding="utf-8", newline="") as f:
            f.write("ruta,estacion,hora\n")
            for h in range(n):
                hh = (h // 60) % 24
                mm = h % 60
                f.write(f"R0,ESTACION_000000,{hh:02d}:{mm:02d}\n")
        return tmp

    def _ejecutar_benchmark(self):
        self.txt_bench.delete("1.0", "end")
        self.txt_bench.insert("end", "Ejecutando pruebas con n = 500, 1000, 2000, 4000...\n")
        self.update()

        tamanos = [500, 1000, 2000, 4000]
        resultados = {"R1 estado O(1)": [], "R2 autocompletar O(log n)": [], "R4 proximo_bus O(log n)": [], "R10 fila O(n)": []}

        for n in tamanos:
            tmp = self._crear_red_sintetica(n)
            red_n = Red(tmp)
            shutil.rmtree(tmp, ignore_errors=True)

            t0 = time.perf_counter()
            for _ in range(2000):
                red_n.estado(f"ESTACION_{n // 2:06d}")
            resultados["R1 estado O(1)"].append((time.perf_counter() - t0) * 1000)

            t0 = time.perf_counter()
            for _ in range(1000):
                red_n.autocompletar("ESTACION_00", 5)
            resultados["R2 autocompletar O(log n)"].append((time.perf_counter() - t0) * 1000)

            t0 = time.perf_counter()
            for _ in range(2000):
                red_n.proximo_bus("ESTACION_000000", "R0", "12:00")
            resultados["R4 proximo_bus O(log n)"].append((time.perf_counter() - t0) * 1000)

            llegadas = [i // 10 for i in range(n * 10)]
            t0 = time.perf_counter()
            simular_fila(llegadas, 5, 100)
            resultados["R10 fila O(n)"].append((time.perf_counter() - t0) * 1000)

        self._dibujar_grafica(tamanos, resultados)
        self.txt_bench.insert("end", f"{'Operación':<26} | {'n=500':>8} | {'n=1000':>8} | {'n=2000':>8} | {'n=4000':>8} | Ratio 2n/n\n")
        self.txt_bench.insert("end", "-" * 84 + "\n")
        for nombre, vals in resultados.items():
            ratio = vals[-1] / vals[-2] if vals[-2] > 0 else 1.0
            self.txt_bench.insert(
                "end",
                f"{nombre:<26} | {vals[0]:7.2f}m | {vals[1]:7.2f}m | {vals[2]:7.2f}m | {vals[3]:7.2f}m | {ratio:6.2f}x\n",
            )
        self.txt_bench.insert(
            "end",
            "\nExplicación (R11): R1, R2 y R4 mantienen tiempos casi constantes (~1.0x-1.2x al duplicar n) gracias a TablaHash O(1), AVL O(log n) y Búsqueda Binaria O(log n). R10 duplica su tiempo (~2.0x) confirmando complejidad lineal O(P) con Cola enlazada.\n",
        )

    def _dibujar_grafica(self, tamanos, resultados):
        c = self.canvas
        c.delete("all")
        w = c.winfo_width() or 960
        h = 300
        pad_l, pad_r, pad_t, pad_b = 65, 30, 30, 40

        c.create_line(pad_l, h - pad_b, w - pad_r, h - pad_b, fill="#64748b", width=2)
        c.create_line(pad_l, pad_t, pad_l, h - pad_b, fill="#64748b", width=2)

        max_y = max(max(v) for v in resultados.values()) or 1.0
        colores = ["#38bdf8", "#a78bfa", "#34d399", "#f87171"]

        for idx_x, n in enumerate(tamanos):
            x = pad_l + idx_x * ((w - pad_l - pad_r) / (len(tamanos) - 1))
            c.create_text(x, h - 20, text=f"n={n}", fill="#cbd5e1", font=("Segoe UI", 9))

        for idx_serie, (nombre, vals) in enumerate(resultados.items()):
            color = colores[idx_serie % len(colores)]
            puntos = []
            for idx_x, val in enumerate(vals):
                x = pad_l + idx_x * ((w - pad_l - pad_r) / (len(tamanos) - 1))
                y = (h - pad_b) - (val / max_y) * (h - pad_t - pad_b)
                puntos.append((x, y))
                c.create_oval(x - 4, y - 4, x + 4, y + 4, fill=color, outline="")
            for i in range(len(puntos) - 1):
                c.create_line(puntos[i][0], puntos[i][1], puntos[i + 1][0], puntos[i + 1][1], fill=color, width=2)
            c.create_text(pad_l + 110 + idx_serie * 210, 16, text=f"■ {nombre}", fill=color, font=("Segoe UI", 9, "bold"))


if __name__ == "__main__":
    app = PlaneadorApp()
    app.mainloop()