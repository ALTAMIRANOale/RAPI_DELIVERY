import datetime
import json
import os
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


# ========== MODELO ==========
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


# ========== PANTALLA DE INICIO (SPLASH MULTI-SECCIÓN) ==========
class SplashScreen(tk.Frame):
    TEXTO_PUBLICITARIO = "Rapi\nLa forma más rápida\nde recibir lo que necesitás\ncuando lo necesitás,\nen toda Argentina."
    TEXTO_SECCION2 = "Selecciona tu entorno\npara optimizar tus rutas\ny gestionar tus pedidos\nde forma inmediata."

    def __init__(self, parent, on_continuar):
        super().__init__(parent, bg="white")
        self.on_continuar = on_continuar
        self.pack(fill="both", expand=True)

        self.canvas = tk.Canvas(self, bg="white", highlightthickness=0)
        self.canvas.pack(fill="both", expand=True)

        self._ya_inicio = False
        self.seccion_actual = 1
        self.opcion_seleccionada = tk.StringVar(value="")
        self.canvas.bind("<Configure>", self._al_dibujar_primera_vez)

    def _al_dibujar_primera_vez(self, event):
        if self._ya_inicio:
            return
        self._ya_inicio = True
        self.ancho = event.width
        self.alto = event.height
        self._mostrar_seccion1()

    def _mostrar_seccion1(self):
        self.canvas.delete("all")
        self.texto_id = self.canvas.create_text(
            self.ancho // 2, -100,
            text=self.TEXTO_PUBLICITARIO,
            font=("Segoe UI", 14, "bold"),
            fill="#1F2733",
            width=self.ancho - 40,
            justify="center"
        )
        self._animar_caida(-100, self.alto // 2 - 80, self._dibujar_boton_seccion1)

    def _mostrar_seccion2(self):
        self.canvas.delete("all")
        self.texto_id = self.canvas.create_text(
            self.ancho // 2, -100,
            text=self.TEXTO_SECCION2,
            font=("Segoe UI", 13, "bold"),
            fill="#1F2733",
            width=self.ancho - 40,
            justify="center"
        )
        self._animar_caida(-100, self.alto // 2 - 120, self._dibujar_elementos_seccion2)

    def _animar_caida(self, y_actual, y_destino, callback):
        if y_actual < y_destino:
            paso = max(3, int((y_destino - y_actual) * 0.1) + 1)
            nuevo_y = y_actual + paso
            self.canvas.coords(self.texto_id, self.ancho // 2, nuevo_y)
            self.after(16, lambda: self._animar_caida(nuevo_y, y_destino, callback))
        else:
            self.canvas.coords(self.texto_id, self.ancho // 2, y_destino)
            callback()

    def _dibujar_boton_seccion1(self):
        cx = self.ancho // 2
        cy = self.alto - 100
        radio = 30

        circulo = self.canvas.create_oval(
            cx - radio, cy - radio, cx + radio, cy + radio,
            fill="#C62828", outline="black", width=2
        )
        flecha = self.canvas.create_polygon(
            cx - 8, cy - 10,
            cx - 8, cy + 10,
            cx + 12, cy,
            fill="white", outline=""
        )

        for item in (circulo, flecha):
            self.canvas.tag_bind(item, "<Enter>", lambda e: self.canvas.config(cursor="hand2"))
            self.canvas.tag_bind(item, "<Leave>", lambda e: self.canvas.config(cursor=""))
            self.canvas.tag_bind(item, "<Button-1>", lambda e: self._ir_a_seccion2())

    def _dibujar_elementos_seccion2(self):
        frame_opciones = tk.Frame(self.canvas, bg="white")
        self.canvas.create_window(self.ancho // 2, self.alto // 2 + 50, window=frame_opciones, anchor="center")

        opciones = ["Modo Gestión Principal", "Modo Monitoreo Rápido", "Modo Soporte Técnico"]
        for opt in opciones:
            rb = tk.Radiobutton(
                frame_opciones, text=opt, variable=self.opcion_seleccionada, value=opt,
                bg="white", font=("Segoe UI", 10), activebackground="white",
                command=self._actualizar_boton_seccion2
            )
            rb.pack(anchor="w", pady=4)

        cx = self.ancho // 2
        cy = self.alto - 100
        radio = 30

        self.circulo_s2 = self.canvas.create_oval(
            cx - radio, cy - radio, cx + radio, cy + radio,
            fill="#9E9E9E", outline="black", width=2
        )
        self.flecha_s2 = self.canvas.create_polygon(
            cx - 8, cy - 10,
            cx - 8, cy + 10,
            cx + 12, cy,
            fill="white", outline=""
        )

    def _actualizar_boton_seccion2(self):
        if self.opcion_seleccionada.get():
            self.canvas.itemconfig(self.circulo_s2, fill="#C62828")
            for item in (self.circulo_s2, self.flecha_s2):
                self.canvas.tag_bind(item, "<Enter>", lambda e: self.canvas.config(cursor="hand2"))
                self.canvas.tag_bind(item, "<Leave>", lambda e: self.canvas.config(cursor=""))
                self.canvas.tag_bind(item, "<Button-1>", lambda e: self._finalizar())

    def _ir_a_seccion2(self):
        self.seccion_actual = 2
        self._mostrar_seccion2()

    def _finalizar(self):
        self.destroy()
        self.on_continuar()


# ========== INTERFAZ GRAFICA PRINCIPAL ==========
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
        self.geometry("480x750")
        self.minsize(400, 600)
        self.configure(bg=COLOR_FONDO)

        self.sistema = GestionDelivery()
        self.protocol("WM_DELETE_WINDOW", self.al_cerrar)

        self.splash = SplashScreen(self, on_continuar=self._iniciar_app_principal)

    def _iniciar_app_principal(self):
        self._construir_layout()
        self.pantalla_listar()

        if self.sistema.mensaje_carga:
            self.after(300, lambda: messagebox.showinfo("Datos", self.sistema.mensaje_carga))

    def _construir_layout(self):
        sidebar = tk.Frame(self, bg=COLOR_SIDEBAR, height=110)
        sidebar.pack(side="top", fill="x")

        tk.Label(sidebar, text="RAPI DELIVERY", bg=COLOR_SIDEBAR, fg=COLOR_SIDEBAR_TXT,
                  font=("Segoe UI", 13, "bold"), pady=4).pack(fill="x")

        self.lbl_contador = tk.Label(sidebar, text="", bg=COLOR_SIDEBAR, fg="#9AA5B1",
                                       font=("Segoe UI", 9))
        self.lbl_contador.pack(fill="x")

        frame_menu_cb = tk.Frame(sidebar, bg=COLOR_SIDEBAR, pady=4)
        frame_menu_cb.pack(fill="x", padx=10)
        
        tk.Label(frame_menu_cb, text="Menú:", bg=COLOR_SIDEBAR, fg="white", font=("Segoe UI", 9)).pack(side="left", padx=5)
        
        self.var_menu_nav = tk.StringVar()
        cb_menu = ttk.Combobox(frame_menu_cb, textvariable=self.var_menu_nav, state="readonly", font=("Segoe UI", 10))
        cb_menu['values'] = [opt[0] for opt in self.OPCIONES_MENU] + ["Salir"]
        cb_menu.pack(side="left", fill="x", expand=True, padx=5)
        cb_menu.bind("<<ComboboxSelected>>", self._navegar_menu)

        contenedor = tk.Frame(self, bg=COLOR_FONDO)
        contenedor.pack(side="bottom", fill="both", expand=True)

        self.lbl_titulo = tk.Label(contenedor, text="", bg=COLOR_FONDO, font=("Segoe UI", 12, "bold"),
                                     anchor="w", padx=15, pady=6)
        self.lbl_titulo.pack(fill="x")

        self.content = tk.Frame(contenedor, bg=COLOR_FONDO, padx=15, pady=4)
        self.content.pack(fill="both", expand=True)

    def _navegar_menu(self, event):
        seleccion = self.var_menu_nav.get()
        if seleccion == "Salir":
            self.al_cerrar()
            return
        for texto, metodo in self.OPCIONES_MENU:
            if texto == seleccion:
                getattr(self, metodo)()
                break

    def _limpiar_content(self, titulo):
        for w in self.content.winfo_children():
            w.destroy()
        self.lbl_titulo.config(text=titulo)
        self.lbl_contador.config(text=f"Pedidos activos: {len(self.sistema.pedidos)}")

    def _combo(self, parent, valores, valor_defecto=None, width=22):
        var = tk.StringVar(value=valor_defecto if valor_defecto else (valores[0] if valores else ""))
        cb = ttk.Combobox(parent, textvariable=var, values=valores, state="readonly", width=width)
        return cb, var

    def _fila(self, parent, etiqueta):
        f = tk.Frame(parent, bg=COLOR_FONDO)
        f.pack(fill="x", pady=4)
        tk.Label(f, text=etiqueta, bg=COLOR_FONDO, width=15, anchor="w",
                  font=("Segoe UI", 9)).pack(side="left")
        return f

    def _crear_treeview(self, parent, columnas, alto=12):
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
        top.geometry("400x480")
        txt = tk.Text(top, wrap="word", font=("Consolas", 9))
        txt.insert("1.0", texto)
        txt.config(state="disabled")
        txt.pack(fill="both", expand=True, padx=10, pady=10)

    # ---------- 1. Registrar Nuevo Pedido ----------
    def pantalla_registrar(self):
        self._limpiar_content("Registrar Nuevo Pedido")
        form = tk.Frame(self.content, bg=COLOR_FONDO)
        form.pack(anchor="nw", fill="x")

        f1 = self._fila(form, "Cliente:")
        e_cliente = tk.Entry(f1, width=24)
        e_cliente.pack(side="left")

        f2 = self._fila(form, "Direccion:")
        e_direccion = tk.Entry(f2, width=24)
        e_direccion.pack(side="left")

        f3 = self._fila(form, "Telefono:")
        e_telefono = tk.Entry(f3, width=24)
        e_telefono.pack(side="left")

        f4 = self._fila(form, "Zona:")
        cb_zona, var_zona = self._combo(f4, list(ZONAS_CONFIG.keys()))
        cb_zona.pack(side="left")

        f5 = self._fila(form, "Monto productos:")
        e_monto = tk.Entry(f5, width=24)
        e_monto.pack(side="left")

        f6 = self._fila(form, "Metodo de pago:")
        cb_pago, var_pago = self._combo(f6, METODOS_PAGO)
        cb_pago.pack(side="left")

        f7 = self._fila(form, "Prioridad:")
        cb_prio, var_prio = self._combo(f7, PRIORIDADES, "Normal")
        cb_prio.pack(side="left")

        f8 = self._fila(form, "Repartidor:")
        nombres_rep = [f"{r['nombre']} (★ {r['calificacion']})" for r in REPARTIDORES]
        cb_rep, var_rep = self._combo(f8, nombres_rep, width=22)
        cb_rep.pack(side="left")

        f9 = self._fila(form, "Observaciones:")
        e_obs = tk.Entry(f9, width=24)
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

            repartidor_limpio = var_rep.get().split(" (")[0]

            nuevo, id_creado = self.sistema.registrar_pedido(
                cliente, direccion, telefono, var_zona.get(), monto,
                var_pago.get(), var_prio.get(), e_obs.get().strip(), repartidor_limpio
            )
            self._mostrar_texto_popup(f"Pedido #{id_creado} registrado", nuevo.ticket_texto())
            self.pantalla_registrar()

        tk.Button(form, text="Registrar Pedido", bg=COLOR_ACENTO, fg="white",
                  font=("Segoe UI", 9, "bold"), padx=10, pady=4, relief="flat",
                  command=registrar).pack(anchor="w", pady=8)

    # ---------- 2. Buscar Pedido ----------
    def pantalla_buscar(self):
        self._limpiar_content("Buscar Pedido")
        top = tk.Frame(self.content, bg=COLOR_FONDO)
        top.pack(fill="x")
        tk.Label(top, text="ID / Cliente:", bg=COLOR_FONDO).pack(side="left")
        e_busqueda = tk.Entry(top, width=18)
        e_busqueda.pack(side="left", padx=4)

        tree = self._crear_treeview(self.content, [
            ("id", "ID", 40), ("cliente", "Cliente", 130), ("zona", "Zona", 80),
            ("total", "Total", 80), ("estado", "Estado", 90)
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
                  relief="flat", padx=6).pack(side="left", padx=4)

        def ver_detalle(event):
            sel = tree.selection()
            if sel:
                p = self.sistema.buscar_pedido(int(sel[0]))
                if p:
                    self._mostrar_texto_popup(f"Pedido #{p.id_pedido}", p.mostrar_completo_texto())

        tree.bind("<Double-1>", ver_detalle)
        tree.pack(fill="both", expand=True, pady=8)
        self._poblar_tree(tree, list(self.sistema.pedidos.values()))

    # ---------- 3. Editar Pedido ----------
    def pantalla_editar(self):
        self._limpiar_content("Editar Pedido")
        tree = self._crear_treeview(self.content, [
            ("id", "ID", 40), ("cliente", "Cliente", 130), ("zona", "Zona", 80),
            ("total", "Total", 80), ("estado", "Estado", 90)
        ], alto=6)
        tree.pack(fill="x", pady=4)
        self._poblar_tree(tree, list(self.sistema.pedidos.values()))

        form_frame = tk.Frame(self.content, bg=COLOR_FONDO)
        form_frame.pack(fill="x", pady=6)

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
            e_cliente = tk.Entry(f1, width=24)
            e_cliente.insert(0, p.cliente)
            e_cliente.pack(side="left")

            f2 = self._fila(form_frame, "Direccion:")
            e_direccion = tk.Entry(f2, width=24)
            e_direccion.insert(0, p.direccion)
            e_direccion.pack(side="left")

            f3 = self._fila(form_frame, "Zona:")
            cb_zona, var_zona = self._combo(f3, list(ZONAS_CONFIG.keys()), p.zona)
            cb_zona.pack(side="left")

            def guardar():
                kwargs = {}
                if e_cliente.get().strip() and e_cliente.get().strip() != p.cliente:
                    kwargs["cliente"] = e_cliente.get().strip()
                if e_direccion.get().strip() and e_direccion.get().strip() != p.direccion:
                    kwargs["direccion"] = e_direccion.get().strip()
                if var_zona.get() != p.zona:
                    kwargs["zona"] = var_zona.get()

                if kwargs:
                    cambios, _ = self.sistema.editar_pedido(p.id_pedido, **kwargs)
                    messagebox.showinfo("Actualizado", f"Campos actualizados: {', '.join(cambios)}")
                self.pantalla_editar()

            tk.Button(form_frame, text="Guardar", bg=COLOR_ACENTO, fg="white",
                      relief="flat", padx=10, pady=4, command=guardar).pack(anchor="w", pady=6)

        tree.bind("<<TreeviewSelect>>", cargar_formulario)

    # ---------- 4. Cambiar Estado ----------
    def pantalla_cambiar_estado(self):
        self._limpiar_content("Cambiar Estado")
        tree = self._crear_treeview(self.content, [
            ("id", "ID", 40), ("cliente", "Cliente", 130), ("estado", "Estado", 90)
        ], alto=8)
        tree.pack(fill="x", pady=4)
        self._poblar_tree(tree, list(self.sistema.pedidos.values()))

        panel = tk.Frame(self.content, bg=COLOR_FONDO)
        panel.pack(fill="x", pady=6)

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

            def aplicar():
                ok, msg = self.sistema.actualizar_estado(p.id_pedido, var_estado.get(), "Cambio manual")
                if ok:
                    messagebox.showinfo("OK", "Estado actualizado.")
                    self.pantalla_cambiar_estado()

            tk.Button(panel, text="Aplicar", bg=COLOR_ACENTO, fg="white",
                      relief="flat", padx=10, pady=4, command=aplicar).pack(anchor="w", pady=6)

        tree.bind("<<TreeviewSelect>>", actualizar_panel)

    # ---------- 5. Cancelar Pedido ----------
    def pantalla_cancelar(self):
        self._limpiar_content("Cancelar Pedido")
        tree = self._crear_treeview(self.content, [
            ("id", "ID", 40), ("cliente", "Cliente", 130), ("estado", "Estado", 90)
        ], alto=8)
        tree.pack(fill="x", pady=4)
        self._poblar_tree(tree, [p for p in self.sistema.pedidos.values() if p.estado != "Cancelado"])

        panel = tk.Frame(self.content, bg=COLOR_FONDO)
        panel.pack(fill="x", pady=6)
        f1 = self._fila(panel, "Motivo:")
        cb_motivo, var_motivo = self._combo(f1, MOTIVOS_CANCELACION, MOTIVOS_CANCELACION[0])
        cb_motivo.pack(side="left")

        def cancelar():
            sel = tree.selection()
            if not sel:
                return
            ok, msg = self.sistema.actualizar_estado(int(sel[0]), "Cancelado", var_motivo.get())
            if ok:
                messagebox.showinfo("Cancelado", "Pedido cancelado.")
                self.pantalla_cancelar()

        tk.Button(self.content, text="Cancelar Seleccionado", bg="#C62828", fg="white",
                  relief="flat", padx=10, pady=4, command=cancelar).pack(anchor="w", pady=4)

    # ---------- 6. Listar Todos los Pedidos ----------
    def pantalla_listar(self):
        self._limpiar_content("Listado de Pedidos")
        tree = self._crear_treeview(self.content, [
            ("id", "ID", 40), ("cliente", "Cliente", 130), ("zona", "Zona", 80),
            ("total", "Total", 80), ("estado", "Estado", 90)
        ], alto=16)
        tree.pack(fill="both", expand=True, pady=4)
        self._poblar_tree(tree, list(self.sistema.pedidos.values()))

    # ---------- 7. Mostrar Pedido Completo ----------
    def pantalla_mostrar_completo(self):
        self._limpiar_content("Pedido Completo")
        tree = self._crear_treeview(self.content, [
            ("id", "ID", 40), ("cliente", "Cliente", 130), ("estado", "Estado", 90)
        ], alto=12)
        tree.pack(fill="both", expand=True, pady=4)
        self._poblar_tree(tree, list(self.sistema.pedidos.values()))

        def mostrar(event=None):
            sel = tree.selection()
            if sel:
                p = self.sistema.buscar_pedido(int(sel[0]))
                self._mostrar_texto_popup(f"Pedido #{p.id_pedido}", p.mostrar_completo_texto())

        tree.bind("<Double-1>", mostrar)

    # ---------- 8. Generar Ticket ----------
    def pantalla_ticket(self):
        self._limpiar_content("Generar Ticket")
        tree = self._crear_treeview(self.content, [
            ("id", "ID", 40), ("cliente", "Cliente", 130), ("estado", "Estado", 90)
        ], alto=12)
        tree.pack(fill="both", expand=True, pady=4)
        self._poblar_tree(tree, list(self.sistema.pedidos.values()))

        def generar():
            sel = tree.selection()
            if not sel:
                return
            p = self.sistema.buscar_pedido(int(sel[0]))
            self._mostrar_texto_popup(f"Ticket #{p.id_pedido}", p.ticket_texto())

        tk.Button(self.content, text="Generar Ticket", bg=COLOR_ACENTO,
                  fg="white", relief="flat", padx=10, pady=4, command=generar).pack(anchor="w", pady=4)

    # ---------- 9. Ordenar Pedidos ----------
    def pantalla_ordenar(self):
        self._limpiar_content("Ordenar Pedidos")
        criterios = ["Mayor a menor total", "Menor a mayor total", "Por cliente (A-Z)"]
        top = tk.Frame(self.content, bg=COLOR_FONDO)
        top.pack(fill="x")
        cb, var = self._combo(top, criterios, criterios[0], width=20)
        cb.pack(side="left", padx=4)

        tree = self._crear_treeview(self.content, [
            ("id", "ID", 40), ("cliente", "Cliente", 130), ("total", "Total", 80), ("estado", "Estado", 90)
        ], alto=14)
        tree.pack(fill="both", expand=True, pady=6)

        def aplicar():
            lista = self.sistema.ordenar_pedidos(var.get())
            self._poblar_tree(tree, lista)

        tk.Button(top, text="Ordenar", command=aplicar, bg=COLOR_ACENTO, fg="white",
                  relief="flat", padx=8).pack(side="left", padx=4)

    # ---------- 10. Ranking de Zonas ----------
    def pantalla_ranking(self):
        self._limpiar_content("Ranking de Zonas")
        ingresos, conteo = self.sistema.ranking_zonas()

        for i, (zona, monto) in enumerate(sorted(ingresos.items(), key=lambda x: x[1], reverse=True)):
            tk.Label(self.content, text=f"#{i+1} {zona}: ${monto:.2f} ({conteo.get(zona,0)} ped)",
                      bg=COLOR_FONDO, font=("Segoe UI", 10)).pack(anchor="w", pady=3)

    # ---------- 11. Ver Estadisticas ----------
    def pantalla_estadisticas(self):
        self._limpiar_content("Estadisticas")
        s = self.sistema.calcular_estadisticas()
        
        marco = tk.Frame(self.content, bg="white", padx=10, pady=10, relief="solid", bd=1)
        marco.pack(fill="both", expand=True)

        tk.Label(marco, text=f"Facturación Total: ${s['total_ventas']:.2f}", bg="white", font=("Segoe UI", 11, "bold")).pack(anchor="w")
        tk.Label(marco, text=f"Entregados: {s['entregados']} | Cancelados: {s['cancelados']}", bg="white").pack(anchor="w", pady=5)

    # ---------- 12. Simulacro de Recorrido ----------
    def pantalla_simulacro(self):
        self._limpiar_content("Simulacro de Recorrido")
        disponibles = [p for p in self.sistema.pedidos.values() if p.estado in ("En Camino", "Pendiente")]
        tree = self._crear_treeview(self.content, [
            ("id", "ID", 40), ("cliente", "Cliente", 130), ("estado", "Estado", 90)
        ], alto=6)
        tree.pack(fill="x", pady=4)
        for p in disponibles:
            tree.insert("", "end", iid=str(p.id_pedido), values=(p.id_pedido, p.cliente, p.estado))

        barra = ttk.Progressbar(self.content, length=300, mode="determinate")
        barra.pack(anchor="w", pady=4)

        def iniciar():
            sel = tree.selection()
            if not sel:
                return
            p = self.sistema.buscar_pedido(int(sel[0]))
            self.sistema.actualizar_estado(p.id_pedido, "En Camino", "Simulación")
            
            barra["value"] = 0
            barra["maximum"] = 5
            def paso(i=0):
                if i >= 5:
                    self.sistema.actualizar_estado(p.id_pedido, "Entregado")
                    messagebox.showinfo("Éxito", "Pedido Entregado")
                    self.pantalla_simulacro()
                    return
                barra["value"] = i + 1
                self.after(500, lambda: paso(i + 1))
            paso()

        tk.Button(self.content, text="Iniciar", bg=COLOR_ACENTO, fg="white",
                  relief="flat", padx=10, pady=4, command=iniciar).pack(anchor="w", pady=4)

    # ---------- 13. Ver Historial ----------
    def pantalla_historial(self):
        self._limpiar_content("Historial de Cambios")
        tree = self._crear_treeview(self.content, [
            ("id", "ID", 40), ("cliente", "Cliente", 130), ("estado", "Estado", 90)
        ], alto=10)
        tree.pack(fill="x", pady=4)
        for p in self.sistema.pedidos.values():
            tree.insert("", "end", iid=str(p.id_pedido), values=(p.id_pedido, p.cliente, p.estado))

        def ver(event=None):
            sel = tree.selection()
            if not sel:
                return
            p = self.sistema.buscar_pedido(int(sel[0]))
            texto = ""
            for entry in p.historial:
                texto += f"[{entry['estado']}] {entry['fecha']} - {entry['detalle']}\n"
            self._mostrar_texto_popup(f"Historial #{p.id_pedido}", texto)

        tree.bind("<Double-1>", ver)

    def al_cerrar(self):
        self.sistema.guardar_datos()
        self.destroy()


if __name__ == "__main__":
    app = App()
    app.mainloop()