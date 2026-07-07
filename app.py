

import datetime
import json
import os
import threading
import time
import tkinter as tk
from tkinter import ttk, messagebox

# ========== CONFIGURACION GENERAL ==========
ARCHIVO_DATOS = "pedidos.txt"

ZONAS_CONFIG = {
    "Centro": {"costo": 800, "tiempo": 15},
    "Norte": {"costo": 1200, "tiempo": 25},
    "Sur": {"costo": 1200, "tiempo": 25},
    "Este": {"costo": 1500, "tiempo": 30},
    "Oeste": {"costo": 1500, "tiempo": 30},
}

MOTIVOS_CANCELACION = [
    "Sin stock", "Cliente no responde", "Pedido duplicado",
    "Cliente cancelo", "Direccion incorrecta", "Otro",
]

REPARTIDORES = [
    {"nombre": "Carlos Gomez", "telefono": "3624-123456", "calificacion": 4.8},
    {"nombre": "Maria Lopez", "telefono": "3624-234567", "calificacion": 4.9},
    {"nombre": "Jose Ramirez", "telefono": "3624-345678", "calificacion": 4.7},
    {"nombre": "Ana Martinez", "telefono": "3624-456789", "calificacion": 4.6},
    {"nombre": "Pedro Fernandez", "telefono": "3624-567890", "calificacion": 4.5},
]

METODOS_PAGO = ["Efectivo", "Tarjeta de Debito", "Tarjeta de Credito", "Transferencia", "Mercado Pago"]
PRIORIDADES = ["Alta", "Normal", "Baja"]
ESTADOS = ["Pendiente", "En Camino", "Entregado", "Cancelado"]

COLOR_ESTADO = {
    "Pendiente": "#B8860B",
    "En Camino": "#1565C0",
    "Entregado": "#2E7D32",
    "Cancelado": "#C62828",
}

COLOR_FONDO = "#F4F5F7"
COLOR_SIDEBAR = "#1F2733"
COLOR_SIDEBAR_TXT = "#ECEFF4"
COLOR_ACENTO = "#3F8CFF"


# ========== MODELO (misma lógica que la version de consola) ==========
class Pedido:
    def __init__(self, id_pedido, cliente, direccion, telefono, zona,
                 total_productos, metodo_pago="Efectivo", prioridad="Normal",
                 observaciones="", repartidor="No asignado"):
        self.id_pedido = id_pedido
        self.cliente = cliente
        self.direccion = direccion
        self.telefono = telefono
        self.zona = zona
        self.total_productos = total_productos
        self.metodo_pago = metodo_pago
        self.prioridad = prioridad
        self.observaciones = observaciones
        self.repartidor = repartidor
        self.costo_envio = self.calcular_envio()
        self.descuento = self.calcular_descuento()
        self.total_pagar = self.total_productos + self.costo_envio - self.descuento
        self.estado = "Pendiente"
        self.fecha_hora = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")
        self.historial = [{"fecha": self.fecha_hora, "estado": "Pendiente", "detalle": "Pedido creado"}]

    def calcular_envio(self):
        return ZONAS_CONFIG.get(self.zona, {"costo": 1000})["costo"]

    def calcular_descuento(self):
        if self.total_productos >= 10000:
            return round(self.total_productos * 0.10, 2)
        elif self.total_productos >= 5000:
            return round(self.total_productos * 0.05, 2)
        return 0

    def tiempo_estimado(self):
        info = ZONAS_CONFIG.get(self.zona, {"tiempo": 20})
        base = info["tiempo"]
        if self.prioridad == "Alta":
            base = max(10, base - 5)
        elif self.prioridad == "Baja":
            base += 5
        return base

    def cambiar_estado(self, nuevo_estado, motivo=""):
        if nuevo_estado not in ESTADOS:
            return False, "Estado no valido"
        if nuevo_estado == "Cancelado" and not motivo:
            return False, "Debe proporcionar un motivo para cancelar"
        self.estado = nuevo_estado
        detalle = f"Estado cambiado a {nuevo_estado}"
        if motivo:
            detalle += f" - Motivo: {motivo}"
        self.historial.append({
            "fecha": datetime.datetime.now().strftime("%Y-%m-%d %H:%M"),
            "estado": nuevo_estado,
            "detalle": detalle
        })
        return True, ""

    def editar(self, **kwargs):
        cambios = []
        for campo, valor in kwargs.items():
            if hasattr(self, campo) and valor is not None:
                setattr(self, campo, valor)
                cambios.append(campo)
        if "zona" in cambios or "total_productos" in cambios:
            self.costo_envio = self.calcular_envio()
            self.descuento = self.calcular_descuento()
            self.total_pagar = self.total_productos + self.costo_envio - self.descuento
        self.historial.append({
            "fecha": datetime.datetime.now().strftime("%Y-%m-%d %H:%M"),
            "estado": self.estado,
            "detalle": f"Editado: {', '.join(cambios)}"
        })
        return cambios

    def mostrar_completo_texto(self):
        t_est = self.tiempo_estimado()
        return (
            f"PEDIDO COMPLETO #{self.id_pedido}\n"
            f"{'=' * 45}\n"
            f"Cliente:        {self.cliente}\n"
            f"Direccion:      {self.direccion}\n"
            f"Telefono:       {self.telefono}\n"
            f"Zona:           {self.zona}\n"
            f"Prioridad:      {self.prioridad}\n"
            f"Estado:         [{self.estado}]\n"
            f"Metodo de Pago: {self.metodo_pago}\n"
            f"Repartidor:     {self.repartidor}\n"
            f"Subtotal:       ${self.total_productos:.2f}\n"
            f"Envio:          ${self.costo_envio:.2f}\n"
            f"Descuento:      -${self.descuento:.2f}\n"
            f"Total:          ${self.total_pagar:.2f}\n"
            f"Tiempo Estimado:{t_est} min\n"
            f"Fecha/Hora:     {self.fecha_hora}\n"
            f"Observaciones:  {self.observaciones or '(sin observaciones)'}\n"
        )

    def ticket_texto(self):
        t_est = self.tiempo_estimado()
        return (
            f"{'=' * 40}\n"
            f" RAPI DELIVERY - TICKET #{self.id_pedido}\n"
            f"{'=' * 40}\n"
            f" Cliente:    {self.cliente}\n"
            f" Direccion:  {self.direccion}\n"
            f" Telefono:   {self.telefono}\n"
            f" Zona:       {self.zona}\n"
            f" Prioridad:  {self.prioridad}\n"
            f" Pago:       {self.metodo_pago}\n"
            f" Repartidor: {self.repartidor}\n"
            f"{'-' * 40}\n"
            f" Productos:  ${self.total_productos:.2f}\n"
            f" Envio:      ${self.costo_envio:.2f}\n"
            f" Descuento: -${self.descuento:.2f}\n"
            f" TOTAL:      ${self.total_pagar:.2f}\n"
            f"{'-' * 40}\n"
            f" Estado:     {self.estado}\n"
            f" Fecha:      {self.fecha_hora}\n"
            f" T. Estimado:{t_est} min\n"
            f"{'=' * 40}\n"
            f" Gracias por elegirnos!\n"
            f"{'=' * 40}\n"
        )

    def to_dict(self):
        return {
            "id_pedido": self.id_pedido, "cliente": self.cliente, "direccion": self.direccion,
            "telefono": self.telefono, "zona": self.zona, "total_productos": self.total_productos,
            "metodo_pago": self.metodo_pago, "prioridad": self.prioridad,
            "observaciones": self.observaciones, "repartidor": self.repartidor,
            "costo_envio": self.costo_envio, "descuento": self.descuento,
            "total_pagar": self.total_pagar, "estado": self.estado,
            "fecha_hora": self.fecha_hora, "historial": self.historial,
        }

    @staticmethod
    def from_dict(data):
        p = Pedido(
            data["id_pedido"], data["cliente"], data["direccion"], data["telefono"],
            data["zona"], data["total_productos"], data.get("metodo_pago", "Efectivo"),
            data.get("prioridad", "Normal"), data.get("observaciones", ""),
            data.get("repartidor", "No asignado"),
        )
        p.costo_envio = data["costo_envio"]
        p.descuento = data.get("descuento", 0)
        p.total_pagar = data["total_pagar"]
        p.estado = data["estado"]
        p.fecha_hora = data["fecha_hora"]
        p.historial = data.get("historial", [])
        return p


class GestionDelivery:
    def __init__(self):
        self.pedidos = {}
        self.contador_id = 1
        self.mensaje_carga = ""
        self.cargar_datos()

    def guardar_datos(self):
        try:
            data = {
                "contador_id": self.contador_id,
                "pedidos": {str(k): v.to_dict() for k, v in self.pedidos.items()}
            }
            with open(ARCHIVO_DATOS, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            return True, ""
        except Exception as e:
            return False, str(e)

    def cargar_datos(self):
        try:
            if os.path.exists(ARCHIVO_DATOS):
                with open(ARCHIVO_DATOS, "r", encoding="utf-8") as f:
                    data = json.load(f)
                self.contador_id = data.get("contador_id", 1)
                self.pedidos = {}
                for k, v in data.get("pedidos", {}).items():
                    self.pedidos[int(k)] = Pedido.from_dict(v)
                self.mensaje_carga = f"Datos cargados: {len(self.pedidos)} pedido(s)."
        except Exception as e:
            self.pedidos = {}
            self.contador_id = 1
            self.mensaje_carga = f"No se pudieron cargar datos previos: {e}"

    def registrar_pedido(self, cliente, direccion, telefono, zona, total_productos,
                          metodo_pago="Efectivo", prioridad="Normal", observaciones="",
                          repartidor="No asignado"):
        nuevo = Pedido(self.contador_id, cliente, direccion, telefono, zona,
                        total_productos, metodo_pago, prioridad, observaciones, repartidor)
        self.pedidos[self.contador_id] = nuevo
        id_creado = self.contador_id
        self.contador_id += 1
        self.guardar_datos()
        return nuevo, id_creado

    def actualizar_estado(self, id_pedido, nuevo_estado, motivo=""):
        if id_pedido not in self.pedidos:
            return False, "Pedido no encontrado"
        ok, msg = self.pedidos[id_pedido].cambiar_estado(nuevo_estado, motivo)
        if ok:
            self.guardar_datos()
        return ok, msg

    def buscar_pedido(self, id_pedido):
        return self.pedidos.get(id_pedido)

    def buscar_por_nombre(self, texto):
        return [p for p in self.pedidos.values() if texto.lower() in p.cliente.lower()]

    def editar_pedido(self, id_pedido, **kwargs):
        if id_pedido not in self.pedidos:
            return None, "Pedido no encontrado"
        cambios = self.pedidos[id_pedido].editar(**kwargs)
        self.guardar_datos()
        return cambios, ""

    def calcular_estadisticas(self):
        stats = {
            "total_ventas": 0, "entregados": 0, "cancelados": 0, "pendientes": 0,
            "en_camino": 0, "pedidos_por_zona": {}, "ingresos_por_zona": {},
            "montos": [], "metodos_pago": {},
        }
        for p in self.pedidos.values():
            stats["total_ventas"] += p.total_pagar
            stats["montos"].append(p.total_pagar)
            stats["pedidos_por_zona"][p.zona] = stats["pedidos_por_zona"].get(p.zona, 0) + 1
            stats["ingresos_por_zona"][p.zona] = stats["ingresos_por_zona"].get(p.zona, 0) + p.total_pagar
            stats["metodos_pago"][p.metodo_pago] = stats["metodos_pago"].get(p.metodo_pago, 0) + 1
            if p.estado == "Entregado":
                stats["entregados"] += 1
            elif p.estado == "Cancelado":
                stats["cancelados"] += 1
            elif p.estado == "En Camino":
                stats["en_camino"] += 1
            elif p.estado == "Pendiente":
                stats["pendientes"] += 1
        return stats

    def ranking_zonas(self):
        ingresos, conteo = {}, {}
        for p in self.pedidos.values():
            if p.estado == "Entregado":
                ingresos[p.zona] = ingresos.get(p.zona, 0) + p.total_pagar
            conteo[p.zona] = conteo.get(p.zona, 0) + 1
        return ingresos, conteo

    def ordenar_pedidos(self, criterio):
        lista = list(self.pedidos.values())
        if criterio == "Mayor a menor total":
            lista.sort(key=lambda p: p.total_pagar, reverse=True)
        elif criterio == "Menor a mayor total":
            lista.sort(key=lambda p: p.total_pagar)
        elif criterio == "Por cliente (A-Z)":
            lista.sort(key=lambda p: p.cliente.lower())
        elif criterio == "Por zona":
            lista.sort(key=lambda p: p.zona)
        elif criterio == "Mas recientes primero":
            lista.sort(key=lambda p: p.fecha_hora, reverse=True)
        return lista


# ========== INTERFAZ GRAFICA ==========
class App(tk.Tk):
    OPCIONES_MENU = [
        ("Registrar Nuevo Pedido", "pantalla_registrar"),
        ("Buscar Pedido", "pantalla_buscar"),
        ("Editar Pedido", "pantalla_editar"),
        ("Cambiar Estado", "pantalla_cambiar_estado"),
        ("Cancelar Pedido", "pantalla_cancelar"),
        ("Listar Todos los Pedidos", "pantalla_listar"),
        ("Mostrar Pedido Completo", "pantalla_mostrar_completo"),
        ("Generar Ticket", "pantalla_ticket"),
        ("Ordenar Pedidos", "pantalla_ordenar"),
        ("Ranking de Zonas", "pantalla_ranking"),
        ("Ver Estadisticas", "pantalla_estadisticas"),
        ("Simulacro de Recorrido", "pantalla_simulacro"),
        ("Historial de Cambios", "pantalla_historial"),
    ]

    def __init__(self):
        super().__init__()
        self.title("RAPI DELIVERY")
        self.geometry("1050x650")
        self.minsize(900, 560)
        self.configure(bg=COLOR_FONDO)

        self.sistema = GestionDelivery()

        self._construir_layout()
        self.pantalla_listar()

        if self.sistema.mensaje_carga:
            self.after(300, lambda: messagebox.showinfo("Datos", self.sistema.mensaje_carga))

        self.protocol("WM_DELETE_WINDOW", self.al_cerrar)

    # ---------- layout general ----------
    def _construir_layout(self):
        sidebar = tk.Frame(self, bg=COLOR_SIDEBAR, width=230)
        sidebar.pack(side="left", fill="y")
        sidebar.pack_propagate(False)

        tk.Label(sidebar, text="RAPI DELIVERY", bg=COLOR_SIDEBAR, fg=COLOR_SIDEBAR_TXT,
                  font=("Segoe UI", 15, "bold"), pady=18).pack(fill="x")

        self.lbl_contador = tk.Label(sidebar, text="", bg=COLOR_SIDEBAR, fg="#9AA5B1",
                                       font=("Segoe UI", 9))
        self.lbl_contador.pack(fill="x", pady=(0, 10))

        canvas_menu = tk.Canvas(sidebar, bg=COLOR_SIDEBAR, highlightthickness=0)
        canvas_menu.pack(side="left", fill="both", expand=True)
        scrollbar = tk.Scrollbar(sidebar, orient="vertical", command=canvas_menu.yview)
        frame_botones = tk.Frame(canvas_menu, bg=COLOR_SIDEBAR)
        frame_botones.bind("<Configure>", lambda e: canvas_menu.configure(scrollregion=canvas_menu.bbox("all")))
        canvas_menu.create_window((0, 0), window=frame_botones, anchor="nw", width=230)
        canvas_menu.configure(yscrollcommand=scrollbar.set)

        for texto, metodo in self.OPCIONES_MENU:
            b = tk.Button(frame_botones, text=texto, anchor="w", bg=COLOR_SIDEBAR, fg=COLOR_SIDEBAR_TXT,
                          activebackground=COLOR_ACENTO, activeforeground="white",
                          relief="flat", font=("Segoe UI", 10), bd=0, padx=16, pady=9,
                          command=getattr(self, metodo))
            b.pack(fill="x")
            b.bind("<Enter>", lambda e, w=b: w.configure(bg=COLOR_ACENTO))
            b.bind("<Leave>", lambda e, w=b: w.configure(bg=COLOR_SIDEBAR))

        b_salir = tk.Button(sidebar, text="Salir", anchor="w", bg="#C62828", fg="white",
                             relief="flat", font=("Segoe UI", 10, "bold"), bd=0, padx=16, pady=10,
                             command=self.al_cerrar)
        b_salir.pack(fill="x", side="bottom")

        # area de contenido
        contenedor = tk.Frame(self, bg=COLOR_FONDO)
        contenedor.pack(side="right", fill="both", expand=True)

        self.lbl_titulo = tk.Label(contenedor, text="", bg=COLOR_FONDO, font=("Segoe UI", 16, "bold"),
                                     anchor="w", padx=20, pady=14)
        self.lbl_titulo.pack(fill="x")

        self.content = tk.Frame(contenedor, bg=COLOR_FONDO, padx=20, pady=6)
        self.content.pack(fill="both", expand=True)

    def _limpiar_content(self, titulo):
        for w in self.content.winfo_children():
            w.destroy()
        self.lbl_titulo.config(text=titulo)
        self.lbl_contador.config(text=f"Pedidos activos: {len(self.sistema.pedidos)}")

    def _combo(self, parent, valores, valor_defecto=None, width=25):
        var = tk.StringVar(value=valor_defecto if valor_defecto else (valores[0] if valores else ""))
        cb = ttk.Combobox(parent, textvariable=var, values=valores, state="readonly", width=width)
        return cb, var

    def _fila(self, parent, etiqueta):
        f = tk.Frame(parent, bg=COLOR_FONDO)
        f.pack(fill="x", pady=5)
        tk.Label(f, text=etiqueta, bg=COLOR_FONDO, width=18, anchor="w",
                  font=("Segoe UI", 10)).pack(side="left")
        return f

    def _crear_treeview(self, parent, columnas, alto=15):
        cols_ids = [c[0] for c in columnas]
        tree = ttk.Treeview(parent, columns=cols_ids, show="headings", height=alto)
        for cid, texto, ancho in columnas:
            tree.heading(cid, text=texto)
            tree.column(cid, width=ancho, anchor="center")
        for estado, color in COLOR_ESTADO.items():
            tree.tag_configure(estado, foreground=color)
        return tree

    def _poblar_tree(self, tree, pedidos):
        for row in tree.get_children():
            tree.delete(row)
        for p in pedidos:
            tree.insert("", "end", iid=str(p.id_pedido), values=(
                p.id_pedido, p.cliente, p.zona, f"${p.total_pagar:.2f}", p.estado
            ), tags=(p.estado,))

    def _mostrar_texto_popup(self, titulo, texto):
        top = tk.Toplevel(self)
        top.title(titulo)
        top.geometry("480x520")
        txt = tk.Text(top, wrap="word", font=("Consolas", 10))
        txt.insert("1.0", texto)
        txt.config(state="disabled")
        txt.pack(fill="both", expand=True, padx=10, pady=10)

    # ---------- 1. Registrar Nuevo Pedido ----------
    def pantalla_registrar(self):
        self._limpiar_content("Registrar Nuevo Pedido")
        form = tk.Frame(self.content, bg=COLOR_FONDO)
        form.pack(anchor="nw")

        f1 = self._fila(form, "Cliente:")
        e_cliente = tk.Entry(f1, width=35)
        e_cliente.pack(side="left")

        f2 = self._fila(form, "Direccion:")
        e_direccion = tk.Entry(f2, width=35)
        e_direccion.pack(side="left")

        f3 = self._fila(form, "Telefono:")
        e_telefono = tk.Entry(f3, width=35)
        e_telefono.pack(side="left")

        f4 = self._fila(form, "Zona:")
        cb_zona, var_zona = self._combo(f4, list(ZONAS_CONFIG.keys()))
        cb_zona.pack(side="left")

        f5 = self._fila(form, "Monto productos:")
        e_monto = tk.Entry(f5, width=35)
        e_monto.pack(side="left")

        f6 = self._fila(form, "Metodo de pago:")
        cb_pago, var_pago = self._combo(f6, METODOS_PAGO)
        cb_pago.pack(side="left")

        f7 = self._fila(form, "Prioridad:")
        cb_prio, var_prio = self._combo(f7, PRIORIDADES, "Normal")
        cb_prio.pack(side="left")

        f8 = self._fila(form, "Repartidor:")
        nombres_rep = [r["nombre"] for r in REPARTIDORES]
        cb_rep, var_rep = self._combo(f8, nombres_rep, width=30)
        cb_rep.pack(side="left")

        f9 = self._fila(form, "Observaciones:")
        e_obs = tk.Entry(f9, width=35)
        e_obs.pack(side="left")

        def registrar():
            cliente = e_cliente.get().strip()
            direccion = e_direccion.get().strip()
            telefono = e_telefono.get().strip()
            if not cliente or not direccion:
                messagebox.showerror("Error", "Cliente y direccion son obligatorios.")
                return
            if not telefono or not any(c.isdigit() for c in telefono):
                messagebox.showerror("Error", "Ingrese un telefono valido.")
                return
            try:
                monto = float(e_monto.get())
                if monto < 0:
                    raise ValueError
            except ValueError:
                messagebox.showerror("Error", "Ingrese un monto valido.")
                return

            nuevo, id_creado = self.sistema.registrar_pedido(
                cliente, direccion, telefono, var_zona.get(), monto,
                var_pago.get(), var_prio.get(), e_obs.get().strip(), var_rep.get()
            )
            self._mostrar_texto_popup(f"Pedido #{id_creado} registrado", nuevo.ticket_texto())
            self.pantalla_registrar()

        tk.Button(form, text="Registrar Pedido", bg=COLOR_ACENTO, fg="white",
                  font=("Segoe UI", 10, "bold"), padx=14, pady=6, relief="flat",
                  command=registrar).pack(anchor="w", pady=14)

    # ---------- 2. Buscar Pedido ----------
    def pantalla_buscar(self):
        self._limpiar_content("Buscar Pedido")
        top = tk.Frame(self.content, bg=COLOR_FONDO)
        top.pack(fill="x")
        tk.Label(top, text="ID o nombre de cliente:", bg=COLOR_FONDO).pack(side="left")
        e_busqueda = tk.Entry(top, width=30)
        e_busqueda.pack(side="left", padx=8)

        tree = self._crear_treeview(self.content, [
            ("id", "ID", 50), ("cliente", "Cliente", 150), ("zona", "Zona", 90),
            ("total", "Total", 90), ("estado", "Estado", 100)
        ])

        def buscar():
            texto = e_busqueda.get().strip()
            if not texto:
                self._poblar_tree(tree, list(self.sistema.pedidos.values()))
                return
            if texto.isdigit():
                p = self.sistema.buscar_pedido(int(texto))
                self._poblar_tree(tree, [p] if p else [])
            else:
                self._poblar_tree(tree, self.sistema.buscar_por_nombre(texto))

        tk.Button(top, text="Buscar", command=buscar, bg=COLOR_ACENTO, fg="white",
                  relief="flat", padx=10).pack(side="left")

        def ver_detalle(event):
            sel = tree.selection()
            if sel:
                p = self.sistema.buscar_pedido(int(sel[0]))
                if p:
                    self._mostrar_texto_popup(f"Pedido #{p.id_pedido}", p.mostrar_completo_texto())

        tree.bind("<Double-1>", ver_detalle)
        tree.pack(fill="both", expand=True, pady=12)
        self._poblar_tree(tree, list(self.sistema.pedidos.values()))
        tk.Label(self.content, text="Doble click sobre un pedido para ver el detalle completo.",
                  bg=COLOR_FONDO, fg="#666").pack(anchor="w")

    # ---------- 3. Editar Pedido ----------
    def pantalla_editar(self):
        self._limpiar_content("Editar Pedido")
        tree = self._crear_treeview(self.content, [
            ("id", "ID", 50), ("cliente", "Cliente", 150), ("zona", "Zona", 90),
            ("total", "Total", 90), ("estado", "Estado", 100)
        ], alto=8)
        tree.pack(fill="x", pady=8)
        self._poblar_tree(tree, list(self.sistema.pedidos.values()))

        form_frame = tk.Frame(self.content, bg=COLOR_FONDO)
        form_frame.pack(fill="x", pady=10)

        def cargar_formulario(event=None):
            for w in form_frame.winfo_children():
                w.destroy()
            sel = tree.selection()
            if not sel:
                return
            p = self.sistema.buscar_pedido(int(sel[0]))
            if not p:
                return

            f1 = self._fila(form_frame, "Cliente:")
            e_cliente = tk.Entry(f1, width=35)
            e_cliente.insert(0, p.cliente)
            e_cliente.pack(side="left")

            f2 = self._fila(form_frame, "Direccion:")
            e_direccion = tk.Entry(f2, width=35)
            e_direccion.insert(0, p.direccion)
            e_direccion.pack(side="left")

            f3 = self._fila(form_frame, "Telefono:")
            e_telefono = tk.Entry(f3, width=35)
            e_telefono.insert(0, p.telefono)
            e_telefono.pack(side="left")

            f4 = self._fila(form_frame, "Zona:")
            cb_zona, var_zona = self._combo(f4, list(ZONAS_CONFIG.keys()), p.zona)
            cb_zona.pack(side="left")

            f5 = self._fila(form_frame, "Monto productos:")
            e_monto = tk.Entry(f5, width=35)
            e_monto.insert(0, str(p.total_productos))
            e_monto.pack(side="left")

            def guardar():
                kwargs = {}
                if e_cliente.get().strip() and e_cliente.get().strip() != p.cliente:
                    kwargs["cliente"] = e_cliente.get().strip()
                if e_direccion.get().strip() and e_direccion.get().strip() != p.direccion:
                    kwargs["direccion"] = e_direccion.get().strip()
                if e_telefono.get().strip() and e_telefono.get().strip() != p.telefono:
                    kwargs["telefono"] = e_telefono.get().strip()
                if var_zona.get() != p.zona:
                    kwargs["zona"] = var_zona.get()
                try:
                    nuevo_monto = float(e_monto.get())
                    if nuevo_monto != p.total_productos:
                        kwargs["total_productos"] = nuevo_monto
                except ValueError:
                    messagebox.showerror("Error", "Monto invalido.")
                    return

                if kwargs:
                    cambios, _ = self.sistema.editar_pedido(p.id_pedido, **kwargs)
                    messagebox.showinfo("Actualizado", f"Campos actualizados: {', '.join(cambios)}")
                else:
                    messagebox.showinfo("Sin cambios", "No se modifico ningun campo.")
                self.pantalla_editar()

            tk.Button(form_frame, text="Guardar Cambios", bg=COLOR_ACENTO, fg="white",
                      relief="flat", padx=12, pady=6, command=guardar).pack(anchor="w", pady=10)

        tree.bind("<<TreeviewSelect>>", cargar_formulario)

    # ---------- 4. Cambiar Estado ----------
    def pantalla_cambiar_estado(self):
        self._limpiar_content("Cambiar Estado de un Pedido")
        tree = self._crear_treeview(self.content, [
            ("id", "ID", 50), ("cliente", "Cliente", 150), ("zona", "Zona", 90),
            ("total", "Total", 90), ("estado", "Estado", 100)
        ], alto=8)
        tree.pack(fill="x", pady=8)
        self._poblar_tree(tree, list(self.sistema.pedidos.values()))

        panel = tk.Frame(self.content, bg=COLOR_FONDO)
        panel.pack(fill="x", pady=10)

        def actualizar_panel(event=None):
            for w in panel.winfo_children():
                w.destroy()
            sel = tree.selection()
            if not sel:
                return
            p = self.sistema.buscar_pedido(int(sel[0]))

            f1 = self._fila(panel, "Nuevo estado:")
            cb_estado, var_estado = self._combo(f1, ESTADOS, p.estado)
            cb_estado.pack(side="left")

            f2 = self._fila(panel, "Motivo (si cancela):")
            cb_motivo, var_motivo = self._combo(f2, MOTIVOS_CANCELACION, MOTIVOS_CANCELACION[0])
            cb_motivo.pack(side="left")

            def aplicar():
                motivo = var_motivo.get() if var_estado.get() == "Cancelado" else ""
                ok, msg = self.sistema.actualizar_estado(p.id_pedido, var_estado.get(), motivo)
                if ok:
                    messagebox.showinfo("OK", f"Estado actualizado a {var_estado.get()}")
                    self.pantalla_cambiar_estado()
                else:
                    messagebox.showerror("Error", msg)

            tk.Button(panel, text="Aplicar Cambio", bg=COLOR_ACENTO, fg="white",
                      relief="flat", padx=12, pady=6, command=aplicar).pack(anchor="w", pady=10)

        tree.bind("<<TreeviewSelect>>", actualizar_panel)

    # ---------- 5. Cancelar Pedido con Motivo ----------
    def pantalla_cancelar(self):
        self._limpiar_content("Cancelar Pedido con Motivo")
        tree = self._crear_treeview(self.content, [
            ("id", "ID", 50), ("cliente", "Cliente", 150), ("zona", "Zona", 90),
            ("total", "Total", 90), ("estado", "Estado", 100)
        ], alto=8)
        tree.pack(fill="x", pady=8)
        self._poblar_tree(tree, [p for p in self.sistema.pedidos.values() if p.estado != "Cancelado"])

        panel = tk.Frame(self.content, bg=COLOR_FONDO)
        panel.pack(fill="x", pady=10)
        f1 = self._fila(panel, "Motivo:")
        cb_motivo, var_motivo = self._combo(f1, MOTIVOS_CANCELACION, MOTIVOS_CANCELACION[0])
        cb_motivo.pack(side="left")
        e_otro = tk.Entry(panel, width=30)

        def on_motivo_change(event=None):
            if var_motivo.get() == "Otro":
                e_otro.pack(side="left", padx=6)
            else:
                e_otro.pack_forget()
        cb_motivo.bind("<<ComboboxSelected>>", on_motivo_change)

        def cancelar():
            sel = tree.selection()
            if not sel:
                messagebox.showwarning("Atencion", "Seleccione un pedido.")
                return
            motivo = e_otro.get().strip() if var_motivo.get() == "Otro" else var_motivo.get()
            if not motivo:
                messagebox.showerror("Error", "Especifique el motivo.")
                return
            ok, msg = self.sistema.actualizar_estado(int(sel[0]), "Cancelado", motivo)
            if ok:
                messagebox.showinfo("Cancelado", f"Pedido #{sel[0]} cancelado. Motivo: {motivo}")
                self.pantalla_cancelar()
            else:
                messagebox.showerror("Error", msg)

        tk.Button(self.content, text="Cancelar Pedido Seleccionado", bg="#C62828", fg="white",
                  relief="flat", padx=12, pady=6, command=cancelar).pack(anchor="w", pady=6)

    # ---------- 6. Listar Todos los Pedidos ----------
    def pantalla_listar(self):
        self._limpiar_content("Listado de Pedidos")
        tree = self._crear_treeview(self.content, [
            ("id", "ID", 50), ("cliente", "Cliente", 160), ("zona", "Zona", 90),
            ("total", "Total", 100), ("estado", "Estado", 110)
        ], alto=20)
        tree.pack(fill="both", expand=True, pady=8)
        self._poblar_tree(tree, list(self.sistema.pedidos.values()))
        if not self.sistema.pedidos:
            tk.Label(self.content, text="No hay pedidos registrados todavia.",
                      bg=COLOR_FONDO, fg="#666").pack(pady=10)

    # ---------- 7. Mostrar Pedido Completo ----------
    def pantalla_mostrar_completo(self):
        self._limpiar_content("Mostrar Pedido Completo")
        tree = self._crear_treeview(self.content, [
            ("id", "ID", 50), ("cliente", "Cliente", 160), ("zona", "Zona", 90),
            ("total", "Total", 100), ("estado", "Estado", 110)
        ], alto=15)
        tree.pack(fill="both", expand=True, pady=8)
        self._poblar_tree(tree, list(self.sistema.pedidos.values()))

        def mostrar(event=None):
            sel = tree.selection()
            if sel:
                p = self.sistema.buscar_pedido(int(sel[0]))
                self._mostrar_texto_popup(f"Pedido #{p.id_pedido}", p.mostrar_completo_texto())

        tree.bind("<Double-1>", mostrar)
        tk.Label(self.content, text="Doble click para ver el detalle completo.",
                  bg=COLOR_FONDO, fg="#666").pack(anchor="w")

    # ---------- 8. Generar Ticket ----------
    def pantalla_ticket(self):
        self._limpiar_content("Generar Ticket")
        tree = self._crear_treeview(self.content, [
            ("id", "ID", 50), ("cliente", "Cliente", 160), ("zona", "Zona", 90),
            ("total", "Total", 100), ("estado", "Estado", 110)
        ], alto=15)
        tree.pack(fill="both", expand=True, pady=8)
        self._poblar_tree(tree, list(self.sistema.pedidos.values()))

        def generar():
            sel = tree.selection()
            if not sel:
                messagebox.showwarning("Atencion", "Seleccione un pedido.")
                return
            p = self.sistema.buscar_pedido(int(sel[0]))
            self._mostrar_texto_popup(f"Ticket #{p.id_pedido}", p.ticket_texto())

        tk.Button(self.content, text="Generar Ticket del Pedido Seleccionado", bg=COLOR_ACENTO,
                  fg="white", relief="flat", padx=12, pady=6, command=generar).pack(anchor="w", pady=6)

    # ---------- 9. Ordenar Pedidos ----------
    def pantalla_ordenar(self):
        self._limpiar_content("Ordenar Pedidos")
        criterios = ["Mayor a menor total", "Menor a mayor total", "Por cliente (A-Z)",
                     "Por zona", "Mas recientes primero"]
        top = tk.Frame(self.content, bg=COLOR_FONDO)
        top.pack(fill="x")
        tk.Label(top, text="Criterio:", bg=COLOR_FONDO).pack(side="left")
        cb, var = self._combo(top, criterios, criterios[0], width=25)
        cb.pack(side="left", padx=8)

        tree = self._crear_treeview(self.content, [
            ("id", "ID", 50), ("cliente", "Cliente", 160), ("zona", "Zona", 90),
            ("total", "Total", 100), ("estado", "Estado", 110)
        ], alto=18)
        tree.pack(fill="both", expand=True, pady=10)

        def aplicar():
            lista = self.sistema.ordenar_pedidos(var.get())
            self._poblar_tree(tree, lista)

        tk.Button(top, text="Ordenar", command=aplicar, bg=COLOR_ACENTO, fg="white",
                  relief="flat", padx=10).pack(side="left")
        aplicar()

    # ---------- 10. Ranking de Zonas ----------
    def pantalla_ranking(self):
        self._limpiar_content("Ranking de Zonas")
        ingresos, conteo = self.sistema.ranking_zonas()

        if not self.sistema.pedidos:
            tk.Label(self.content, text="No hay datos para ranking.", bg=COLOR_FONDO).pack()
            return

        col1 = tk.Frame(self.content, bg=COLOR_FONDO)
        col1.pack(side="left", fill="both", expand=True, padx=10)
        col2 = tk.Frame(self.content, bg=COLOR_FONDO)
        col2.pack(side="left", fill="both", expand=True, padx=10)

        tk.Label(col1, text="Por facturacion (entregados)", bg=COLOR_FONDO,
                  font=("Segoe UI", 11, "bold")).pack(anchor="w", pady=6)
        for i, (zona, monto) in enumerate(sorted(ingresos.items(), key=lambda x: x[1], reverse=True)):
            medalla = f"#{i+1}"
            tk.Label(col1, text=f"{medalla}  {zona}: ${monto:.2f} ({conteo.get(zona,0)} pedidos)",
                      bg=COLOR_FONDO, font=("Segoe UI", 10)).pack(anchor="w", pady=2)

        tk.Label(col2, text="Por cantidad de pedidos", bg=COLOR_FONDO,
                  font=("Segoe UI", 11, "bold")).pack(anchor="w", pady=6)
        for i, (zona, cant) in enumerate(sorted(conteo.items(), key=lambda x: x[1], reverse=True)):
            medalla = f"#{i+1}"
            tk.Label(col2, text=f"{medalla}  {zona}: {cant} pedido(s)",
                      bg=COLOR_FONDO, font=("Segoe UI", 10)).pack(anchor="w", pady=2)

    # ---------- 11. Ver Estadisticas Completas ----------
    def pantalla_estadisticas(self):
        self._limpiar_content("Estadisticas Completas")
        if not self.sistema.pedidos:
            tk.Label(self.content, text="No hay datos para generar estadisticas.", bg=COLOR_FONDO).pack()
            return

        s = self.sistema.calcular_estadisticas()
        montos = s["montos"]
        promedio = round(sum(montos) / len(montos), 2) if montos else 0
        mayor = max(montos) if montos else 0
        menor = min(montos) if montos else 0

        marco = tk.Frame(self.content, bg="white", padx=16, pady=16, relief="solid", bd=1)
        marco.pack(fill="both", expand=True)

        def sub(txt):
            tk.Label(marco, text=txt, bg="white", font=("Segoe UI", 11, "bold"), fg=COLOR_ACENTO).pack(anchor="w", pady=(10, 4))

        def linea(txt):
            tk.Label(marco, text=txt, bg="white", font=("Segoe UI", 10)).pack(anchor="w")

        sub("Vision General")
        linea(f"Entregados: {s['entregados']}   Pendientes: {s['pendientes']}   "
              f"En Camino: {s['en_camino']}   Cancelados: {s['cancelados']}   "
              f"Total: {len(self.sistema.pedidos)}")

        sub("Facturacion")
        linea(f"Facturacion Total: ${s['total_ventas']:.2f}   Pedido Promedio: ${promedio}")
        linea(f"Mayor Venta: ${mayor:.2f}   Menor Venta: ${menor:.2f}")

        sub("Pedidos por Zona")
        for zona, cant in sorted(s["pedidos_por_zona"].items(), key=lambda x: x[1], reverse=True):
            ingreso = s["ingresos_por_zona"].get(zona, 0)
            linea(f"- {zona}: {cant} pedido(s) | ${ingreso:.2f}")

        sub("Metodos de Pago")
        for metodo, cant in s["metodos_pago"].items():
            linea(f"- {metodo}: {cant} pedido(s)")

    # ---------- 12. Simulacro de Recorrido ----------
    def pantalla_simulacro(self):
        self._limpiar_content("Simulacro de Recorrido")
        disponibles = [p for p in self.sistema.pedidos.values() if p.estado in ("En Camino", "Pendiente")]
        tree = self._crear_treeview(self.content, [
            ("id", "ID", 50), ("cliente", "Cliente", 160), ("zona", "Zona", 90), ("estado", "Estado", 110)
        ], alto=8)
        tree.heading("id", text="ID")
        tree.pack(fill="x", pady=8)
        for p in disponibles:
            tree.insert("", "end", iid=str(p.id_pedido),
                        values=(p.id_pedido, p.cliente, p.zona, p.estado), tags=(p.estado,))

        info = tk.Label(self.content, text="", bg=COLOR_FONDO, font=("Segoe UI", 10))
        info.pack(anchor="w", pady=6)
        barra = ttk.Progressbar(self.content, length=500, mode="determinate")
        barra.pack(anchor="w", pady=6)
        etiqueta_paso = tk.Label(self.content, text="", bg=COLOR_FONDO, font=("Segoe UI", 10, "italic"))
        etiqueta_paso.pack(anchor="w")

        def iniciar():
            sel = tree.selection()
            if not sel:
                messagebox.showwarning("Atencion", "Seleccione un pedido.")
                return
            p = self.sistema.buscar_pedido(int(sel[0]))
            if p.estado == "Cancelado" or p.estado == "Entregado":
                messagebox.showwarning("Atencion", "Este pedido no puede simularse.")
                return
            if p.estado != "En Camino":
                self.sistema.actualizar_estado(p.id_pedido, "En Camino", "Iniciando simulacion de recorrido")

            etapas = [
                f"[{p.zona}] Preparando pedido", "Pedido recogido en el local",
                f"Saliendo hacia {p.direccion}", "A 3 km del destino", "A 2 km del destino",
                "A 1 km del destino", f"Llegando a zona de {p.zona}", "Cerca del destino",
                f"Llegando a {p.direccion}", f"Entregando a {p.cliente}",
            ]
            t_est = p.tiempo_estimado()
            tiempo_por_paso = max(0.3, (t_est / 10))
            info.config(text=f"Destino: {p.direccion} | Zona: {p.zona} | Repartidor: {p.repartidor}")
            barra["value"] = 0
            barra["maximum"] = len(etapas)

            def paso(i=0):
                if i >= len(etapas):
                    self.sistema.actualizar_estado(p.id_pedido, "Entregado")
                    etiqueta_paso.config(text=f"Pedido #{p.id_pedido} entregado con exito!")
                    messagebox.showinfo("Entregado", f"Pedido #{p.id_pedido} entregado a {p.cliente}!")
                    self.pantalla_simulacro()
                    return
                etiqueta_paso.config(text=etapas[i])
                barra["value"] = i + 1
                self.after(int(tiempo_por_paso * 1000), lambda: paso(i + 1))

            paso()

        tk.Button(self.content, text="Iniciar Simulacro", bg=COLOR_ACENTO, fg="white",
                  relief="flat", padx=12, pady=6, command=iniciar).pack(anchor="w", pady=8)

    # ---------- 13. Ver Historial de Cambios ----------
    def pantalla_historial(self):
        self._limpiar_content("Historial de Cambios")
        tree = self._crear_treeview(self.content, [
            ("id", "ID", 50), ("cliente", "Cliente", 160), ("zona", "Zona", 90), ("estado", "Estado", 110)
        ], alto=15)
        tree.pack(fill="x", pady=8)
        for p in self.sistema.pedidos.values():
            tree.insert("", "end", iid=str(p.id_pedido),
                        values=(p.id_pedido, p.cliente, p.zona, p.estado), tags=(p.estado,))

        def ver(event=None):
            sel = tree.selection()
            if not sel:
                return
            p = self.sistema.buscar_pedido(int(sel[0]))
            texto = f"Historial de Cambios - Pedido #{p.id_pedido}\n{'=' * 45}\n"
            for entry in p.historial:
                texto += f"[{entry['estado']}] {entry['fecha']} - {entry['detalle']}\n"
            self._mostrar_texto_popup(f"Historial #{p.id_pedido}", texto)

        tree.bind("<Double-1>", ver)
        tk.Label(self.content, text="Doble click para ver el historial del pedido.",
                  bg=COLOR_FONDO, fg="#666").pack(anchor="w")

    # ---------- Salir ----------
    def al_cerrar(self):
        ok, msg = self.sistema.guardar_datos()
        if not ok:
            messagebox.showerror("Error al guardar", msg)
        self.destroy()


if __name__ == "__main__":
    app = App()
    app.mainloop()
