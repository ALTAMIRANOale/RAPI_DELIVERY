import datetime
import json
import os
import time
import random
import sys

# ========== COLORES ANSI ==========
VERDE = "\033[92m"
AMARILLO = "\033[93m"
AZUL = "\033[94m"
ROJO = "\033[91m"
MAGENTA = "\033[95m"
CIAN = "\033[96m"
RESET = "\033[0m"
NEGRITA = "\033[1m"

COLORES_ESTADO = {
    "Pendiente": AMARILLO,
    "En Camino": AZUL,
    "Entregado": VERDE,
    "Cancelado": ROJO
}

ARCHIVO_DATOS = "pedidos.txt"

ZONAS_CONFIG = {
    "Centro": {"costo": 800, "tiempo": 15},
    "Norte": {"costo": 1200, "tiempo": 25},
    "Sur": {"costo": 1200, "tiempo": 25},
    "Este": {"costo": 1500, "tiempo": 30},
    "Oeste": {"costo": 1500, "tiempo": 30}
}

MOTIVOS_CANCELACION = ["Sin stock", "Cliente no responde", "Pedido duplicado",
                       "Cliente cancelo", "Direccion incorrecta", "Otro"]

REPARTIDORES = [
    {"nombre": "Carlos Gomez", "telefono": "3624-123456", "calificacion": 4.8},
    {"nombre": "Maria Lopez", "telefono": "3624-234567", "calificacion": 4.9},
    {"nombre": "Jose Ramirez", "telefono": "3624-345678", "calificacion": 4.7},
    {"nombre": "Ana Martinez", "telefono": "3624-456789", "calificacion": 4.6},
    {"nombre": "Pedro Fernandez", "telefono": "3624-567890", "calificacion": 4.5},
]

OPCIONES_MENU = [
    ("1", "Registrar Nuevo Pedido"),
    ("2", "Buscar Pedido"),
    ("3", "Editar Pedido"),
    ("4", "Cambiar Estado de un Pedido"),
    ("5", "Cancelar Pedido con Motivo"),
    ("6", "Listar Todos los Pedidos"),
    ("7", "Mostrar Pedido Completo"),
    ("8", "Generar Ticket"),
    ("9", "Ordenar Pedidos"),
    ("10", "Ranking de Zonas"),
    ("11", "Ver Estadisticas Completas"),
    ("12", "Simulacro de Recorrido"),
    ("13", "Ver Historial de Cambios"),
    ("14", "Salir"),
]


def pausa():
    input(f"\n{CIAN}Presione Enter para continuar...{RESET}")


def limpiar():
    os.system("cls" if os.name == "nt" else "clear")


def validar_entero(mensaje):
    while True:
        try:
            return int(input(mensaje))
        except ValueError:
            print(f"{ROJO}Ingrese un numero valido.{RESET}")


def validar_flotante(mensaje):
    while True:
        try:
            valor = float(input(mensaje))
            if valor < 0:
                print(f"{ROJO}El valor no puede ser negativo.{RESET}")
                continue
            return valor
        except ValueError:
            print(f"{ROJO}Ingrese un monto valido.{RESET}")


def validar_telefono(mensaje):
    while True:
        tel = input(mensaje).strip()
        if tel and any(c.isdigit() for c in tel):
            return tel
        print(f"{ROJO}Ingrese un telefono valido.{RESET}")


def seleccionar_opcion(mensaje, opciones_validas):
    while True:
        op = input(mensaje).strip()
        if op in opciones_validas:
            return op
        print(f"{ROJO}Opcion incorrecta.{RESET}")


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
        estados_validos = ["Pendiente", "En Camino", "Entregado", "Cancelado"]
        if nuevo_estado not in estados_validos:
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

    def mostrar_completo(self):
        color_estado = COLORES_ESTADO.get(self.estado, "")
        t_est = self.tiempo_estimado()
        return (
            f"\n{color_estado}{'=' * 55}{RESET}\n"
            f"{NEGRITA}  PEDIDO COMPLETO #{self.id_pedido}{RESET}\n"
            f"{color_estado}{'=' * 55}{RESET}\n"
            f"{CIAN}Cliente:{RESET}       {self.cliente}\n"
            f"{CIAN}Direccion:{RESET}     {self.direccion}\n"
            f"{CIAN}Telefono:{RESET}      {self.telefono}\n"
            f"{CIAN}Zona:{RESET}           {self.zona}\n"
            f"{CIAN}Prioridad:{RESET}      {self.prioridad}\n"
            f"{CIAN}Estado:{RESET}         {color_estado}[{self.estado}]{RESET}\n"
            f"{CIAN}Metodo de Pago:{RESET} {self.metodo_pago}\n"
            f"{CIAN}Repartidor:{RESET}     {self.repartidor}\n"
            f"{CIAN}Subtotal:{RESET}      ${self.total_productos:.2f}\n"
            f"{CIAN}Envio:{RESET}         ${self.costo_envio:.2f}\n"
            f"{CIAN}Descuento:{RESET}     -${self.descuento:.2f}\n"
            f"{NEGRITA}{CIAN}Total:{RESET}{NEGRITA}         ${self.total_pagar:.2f}{RESET}\n"
            f"{CIAN}Tiempo Estimado:{RESET} {t_est} min\n"
            f"{CIAN}Fecha/Hora:{RESET}     {self.fecha_hora}\n"
            f"{CIAN}Observaciones:{RESET}  {self.observaciones or '(sin observaciones)'}\n"
        )

    def ticket(self):
        t_est = self.tiempo_estimado()
        return (
            f"\n{'=' * 42}\n"
            f" {NEGRITA}RAPI DELIVERY - TICKET #{self.id_pedido}{RESET}\n"
            f"{'=' * 42}\n"
            f" Cliente:    {self.cliente}\n"
            f" Direccion:  {self.direccion}\n"
            f" Telefono:   {self.telefono}\n"
            f" Zona:       {self.zona}\n"
            f" Prioridad:  {self.prioridad}\n"
            f" Pago:       {self.metodo_pago}\n"
            f" Repartidor: {self.repartidor}\n"
            f"{'-' * 42}\n"
            f" Productos:  ${self.total_productos:.2f}\n"
            f" Envio:      ${self.costo_envio:.2f}\n"
            f" Descuento: -${self.descuento:.2f}\n"
            f"{NEGRITA} TOTAL:      ${self.total_pagar:.2f}{RESET}\n"
            f"{'-' * 42}\n"
            f" Estado:     {self.estado}\n"
            f" Fecha:      {self.fecha_hora}\n"
            f" T. Estimado: {t_est} min\n"
            f"{'=' * 42}\n"
            f" {NEGRITA}Gracias por elegirnos!{RESET}\n"
            f"{'=' * 42}\n"
        )

    def to_dict(self):
        return {
            "id_pedido": self.id_pedido,
            "cliente": self.cliente,
            "direccion": self.direccion,
            "telefono": self.telefono,
            "zona": self.zona,
            "total_productos": self.total_productos,
            "metodo_pago": self.metodo_pago,
            "prioridad": self.prioridad,
            "observaciones": self.observaciones,
            "repartidor": self.repartidor,
            "costo_envio": self.costo_envio,
            "descuento": self.descuento,
            "total_pagar": self.total_pagar,
            "estado": self.estado,
            "fecha_hora": self.fecha_hora,
            "historial": self.historial
        }

    @staticmethod
    def from_dict(data):
        p = Pedido(
            data["id_pedido"], data["cliente"], data["direccion"],
            data["telefono"], data["zona"], data["total_productos"],
            data.get("metodo_pago", "Efectivo"),
            data.get("prioridad", "Normal"),
            data.get("observaciones", ""),
            data.get("repartidor", "No asignado")
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
        self.cargar_datos()

    def guardar_datos(self):
        try:
            data = {
                "contador_id": self.contador_id,
                "pedidos": {str(k): v.to_dict() for k, v in self.pedidos.items()}
            }
            with open(ARCHIVO_DATOS, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
        except Exception as e:
            print(f"{ROJO}Error al guardar: {e}{RESET}")

    def cargar_datos(self):
        try:
            if os.path.exists(ARCHIVO_DATOS):
                with open(ARCHIVO_DATOS, "r", encoding="utf-8") as f:
                    data = json.load(f)
                self.contador_id = data.get("contador_id", 1)
                self.pedidos = {}
                for k, v in data.get("pedidos", {}).items():
                    self.pedidos[int(k)] = Pedido.from_dict(v)
                print(f"{VERDE}Datos cargados: {len(self.pedidos)} pedido(s).{RESET}")
        except Exception as e:
            print(f"{AMARILLO}No se pudieron cargar datos previos: {e}{RESET}")
            self.pedidos = {}
            self.contador_id = 1

    def registrar_pedido(self, cliente, direccion, telefono, zona, total_productos,
                         metodo_pago="Efectivo", prioridad="Normal", observaciones="",
                         repartidor="No asignado"):
        nuevo = Pedido(self.contador_id, cliente, direccion, telefono, zona,
                       total_productos, metodo_pago, prioridad, observaciones, repartidor)
        self.pedidos[self.contador_id] = nuevo
        print(f"\n{VERDE}[OK] Pedido #{self.contador_id} registrado con exito.{RESET}")
        print(nuevo.ticket())
        self.contador_id += 1
        self.guardar_datos()

    def actualizar_estado(self, id_pedido, nuevo_estado, motivo=""):
        if id_pedido not in self.pedidos:
            return False, "Pedido no encontrado"
        ok, msg = self.pedidos[id_pedido].cambiar_estado(nuevo_estado, motivo)
        if ok:
            self.guardar_datos()
        return ok, msg

    def buscar_pedido(self, id_pedido):
        return self.pedidos.get(id_pedido)

    def editar_pedido(self, id_pedido, **kwargs):
        if id_pedido not in self.pedidos:
            return None, "Pedido no encontrado"
        cambios = self.pedidos[id_pedido].editar(**kwargs)
        self.guardar_datos()
        return cambios, ""

    def mostrar_pedidos(self):
        if not self.pedidos:
            print(f"\n{AMARILLO}[!] No hay pedidos registrados.{RESET}")
            return
        print(f"\n{NEGRITA}{'=' * 60}{RESET}")
        print(f"{NEGRITA}  LISTADO DE PEDIDOS ({len(self.pedidos)} total){RESET}")
        print(f"{NEGRITA}{'=' * 60}{RESET}")
        for p in self.pedidos.values():
            color = COLORES_ESTADO.get(p.estado, "")
            print(f"  ID: {str(p.id_pedido).ljust(3)} | {p.cliente.ljust(15)} | Zona: {p.zona.ljust(7)} "
                  f"| ${p.total_pagar:>7.2f} | Estado: {color}[{p.estado}]{RESET}")

    def mostrar_estadisticas(self):
        if not self.pedidos:
            print(f"\n{AMARILLO}[!] No hay datos para generar estadisticas.{RESET}")
            return

        total_ventas = 0
        entregados = 0
        cancelados = 0
        pendientes = 0
        en_camino = 0
        pedidos_por_zona = {}
        ingresos_por_zona = {}
        montos = []
        metodos_pago = {}

        for p in self.pedidos.values():
            total_ventas += p.total_pagar
            montos.append(p.total_pagar)
            pedidos_por_zona[p.zona] = pedidos_por_zona.get(p.zona, 0) + 1
            ingresos_por_zona[p.zona] = ingresos_por_zona.get(p.zona, 0) + p.total_pagar
            metodos_pago[p.metodo_pago] = metodos_pago.get(p.metodo_pago, 0) + 1
            if p.estado == "Entregado":
                entregados += 1
            elif p.estado == "Cancelado":
                cancelados += 1
            elif p.estado == "En Camino":
                en_camino += 1
            elif p.estado == "Pendiente":
                pendientes += 1

        pedido_promedio = round(sum(montos) / len(montos), 2) if montos else 0
        mayor_venta = max(montos) if montos else 0
        menor_venta = min(montos) if montos else 0

        if ingresos_por_zona:
            zona_mas_ingreso = max(ingresos_por_zona, key=ingresos_por_zona.get)
            zona_menos_ingreso = min(ingresos_por_zona, key=ingresos_por_zona.get)
        else:
            zona_mas_ingreso = zona_menos_ingreso = "N/A"

        print(f"\n{NEGRITA}{'=' * 55}{RESET}")
        print(f"{NEGRITA}  ESTADISTICAS COMPLETAS DEL SISTEMA{RESET}")
        print(f"{NEGRITA}{'=' * 55}{RESET}")

        print(f"\n{CIAN}Vision General:{RESET}")
        print(f"  {VERDE}[OK] Entregados:{RESET}      {entregados}")
        print(f"  {AMARILLO}[..] Pendientes:{RESET}     {pendientes}")
        print(f"  {AZUL}[->] En Camino:{RESET}       {en_camino}")
        print(f"  {ROJO}[X] Cancelados:{RESET}      {cancelados}")
        print(f"  [*] Total Pedidos:    {len(self.pedidos)}")

        print(f"\n{CIAN}Facturacion:{RESET}")
        print(f"  Facturacion Total:  ${total_ventas:.2f}")
        print(f"  Pedido Promedio:    ${pedido_promedio}")
        print(f"  Mayor Venta:        ${mayor_venta:.2f}")
        print(f"  Menor Venta:        ${menor_venta:.2f}")

        print(f"\n{CIAN}Pedidos por Zona:{RESET}")
        for zona, cant in sorted(pedidos_por_zona.items(), key=lambda x: x[1], reverse=True):
            ingreso = ingresos_por_zona.get(zona, 0)
            print(f"  - {zona}: {cant} pedido(s) | ${ingreso:.2f}")

        print(f"\n{CIAN}Ranking de Zonas:{RESET}")
        print(f"  [1] Mayor ingreso: {zona_mas_ingreso} (${ingresos_por_zona.get(zona_mas_ingreso, 0):.2f})")
        print(f"  [U] Menor ingreso: {zona_menos_ingreso} (${ingresos_por_zona.get(zona_menos_ingreso, 0):.2f})")

        if pedidos_por_zona:
            zona_mas_pedidos = max(pedidos_por_zona, key=pedidos_por_zona.get)
            zona_menos_pedidos = min(pedidos_por_zona, key=pedidos_por_zona.get)
            print(f"  [+] Zona con mas pedidos: {zona_mas_pedidos} ({pedidos_por_zona[zona_mas_pedidos]})")
            print(f"  [-] Zona con menos pedidos: {zona_menos_pedidos} ({pedidos_por_zona[zona_menos_pedidos]})")

        print(f"\n{CIAN}Metodos de Pago:{RESET}")
        for metodo, cant in metodos_pago.items():
            print(f"  - {metodo}: {cant} pedido(s)")

    def ranking_zonas(self):
        if not self.pedidos:
            print(f"\n{AMARILLO}No hay datos para ranking.{RESET}")
            return

        ingresos = {}
        conteo = {}
        for p in self.pedidos.values():
            if p.estado == "Entregado":
                ingresos[p.zona] = ingresos.get(p.zona, 0) + p.total_pagar
            conteo[p.zona] = conteo.get(p.zona, 0) + 1

        print(f"\n{NEGRITA}{'=' * 50}{RESET}")
        print(f"{NEGRITA}  RANKING DE ZONAS{RESET}")
        print(f"{NEGRITA}{'=' * 50}{RESET}")

        zonas_orden = sorted(ingresos.items(), key=lambda x: x[1], reverse=True)
        print(f"\n{CIAN}Por facturacion (entregados):{RESET}")
        for i, (zona, ingreso) in enumerate(zonas_orden):
            medalla = ["#1", "#2", "#3"][i] if i < 3 else f"#{i+1}"
            print(f"  {medalla} {zona}: ${ingreso:.2f} ({conteo.get(zona, 0)} pedidos)")

        print(f"\n{CIAN}Por cantidad de pedidos:{RESET}")
        zonas_cant = sorted(conteo.items(), key=lambda x: x[1], reverse=True)
        for i, (zona, cant) in enumerate(zonas_cant):
            medalla = ["#1", "#2", "#3"][i] if i < 3 else f"#{i+1}"
            print(f"  {medalla} {zona}: {cant} pedido(s)")

    def ordenar_pedidos(self, criterio):
        if not self.pedidos:
            print(f"\n{AMARILLO}No hay pedidos para ordenar.{RESET}")
            return

        lista = list(self.pedidos.values())

        if criterio == "1":
            lista.sort(key=lambda p: p.total_pagar, reverse=True)
            titulo = "Mayor a menor total"
        elif criterio == "2":
            lista.sort(key=lambda p: p.total_pagar)
            titulo = "Menor a mayor total"
        elif criterio == "3":
            lista.sort(key=lambda p: p.cliente.lower())
            titulo = "Por cliente (A-Z)"
        elif criterio == "4":
            lista.sort(key=lambda p: p.zona)
            titulo = "Por zona"
        elif criterio == "5":
            lista.sort(key=lambda p: p.fecha_hora, reverse=True)
            titulo = "Mas recientes primero"
        else:
            print(f"{ROJO}Criterio no valido.{RESET}")
            return

        print(f"\n{NEGRITA}Pedidos ordenados: {titulo}{RESET}")
        print(f"{'=' * 65}")
        for p in lista:
            color = COLORES_ESTADO.get(p.estado, "")
            print(f"  #{p.id_pedido} | {p.cliente.ljust(15)} | Zona: {p.zona.ljust(7)} | "
                  f"${p.total_pagar:>7.2f} | {color}[{p.estado}]{RESET}")

    def simulacro_recorrido(self, id_pedido):
        pedido = self.pedidos.get(id_pedido)
        if not pedido:
            print(f"\n{ROJO}Pedido no encontrado.{RESET}")
            return

        if pedido.estado != "En Camino":
            print(f"{AMARILLO}El pedido debe estar en estado 'En Camino' para simular.{RESET}")
            return

        t_est = pedido.tiempo_estimado()
        pasos = 10
        tiempo_por_paso = t_est / pasos
        etapas = [
            f"[{pedido.zona}] Preparando pedido",
            f"Pedido recogido en el local",
            f"Saliendo hacia {pedido.direccion}",
            f"A 3 km del destino",
            f"A 2 km del destino",
            f"A 1 km del destino",
            f"Llegando a zona de {pedido.zona}",
            f"Cerca del destino",
            f"Llegando a {pedido.direccion}",
            f"Entregando a {pedido.cliente}"
        ]

        print(f"\n{NEGRITA}** Simulacro de Recorrido - Pedido #{id_pedido} **{RESET}")
        print(f"  {CIAN}Destino:{RESET} {pedido.direccion}, Zona {pedido.zona}")
        print(f"  {CIAN}Tiempo estimado:{RESET} {t_est} min")
        print(f"  {CIAN}Repartidor:{RESET} {pedido.repartidor}")
        print(f"{'-' * 50}")

        for i in range(pasos):
            progreso = (i + 1) / pasos
            ancho = 30
            lleno = int(ancho * progreso)
            barra = f"{VERDE}{chr(219) * lleno}{chr(176) * (ancho - lleno)}{RESET}"
            pct = int(progreso * 100)
            print(f"\r  {barra} {pct}%  {etapas[i]}", end="")
            time.sleep(tiempo_por_paso)

        print()
        print(f"\n{VERDE}[OK] Pedido #{id_pedido} entregado con exito a {pedido.cliente}!{RESET}")
        print(f"{NEGRITA}Gracias por elegirnos!{RESET}")

        pedido.estado = "Entregado"
        pedido.historial.append({
            "fecha": datetime.datetime.now().strftime("%Y-%m-%d %H:%M"),
            "estado": "Entregado",
            "detalle": "Pedido entregado (simulacion de recorrido)"
        })
        self.guardar_datos()

    def historial_cambios(self, id_pedido):
        pedido = self.pedidos.get(id_pedido)
        if not pedido:
            print(f"\n{ROJO}Pedido no encontrado.{RESET}")
            return

        print(f"\n{NEGRITA}Historial de Cambios - Pedido #{id_pedido}{RESET}")
        print(f"{'=' * 65}")
        for entry in pedido.historial:
            color = COLORES_ESTADO.get(entry["estado"], "")
            print(f"  {color}[{entry['estado']}]{RESET} {entry['fecha']} - {entry['detalle']}")


def menu():
    sistema = GestionDelivery()

    while True:
        limpiar()
        print(f"\n{NEGRITA}{'=' * 50}{RESET}")
        print(f"{NEGRITA}  SISTEMA DE DELIVERY - RAPI DELIVERY{RESET}")
        print(f"{NEGRITA}{'=' * 50}{RESET}")
        print(f"  Pedidos activos: {len(sistema.pedidos)}")
        print(f"{'-' * 50}")
        for key, label in OPCIONES_MENU:
            print(f"  {key}. {label}")
        print(f"{'-' * 50}")

        opcion = input(f"\n{CIAN}Seleccione una opcion: {RESET}").strip()

        if opcion == "1":
            print(f"\n{NEGRITA}--- REGISTRAR NUEVO PEDIDO ---{RESET}")
            cliente = input("Nombre del Cliente: ").strip()
            while not cliente:
                print(f"{ROJO}El nombre no puede estar vacio.{RESET}")
                cliente = input("Nombre del Cliente: ").strip()

            direccion = input("Direccion de entrega: ").strip()
            while not direccion:
                print(f"{ROJO}La direccion no puede estar vacia.{RESET}")
                direccion = input("Direccion de entrega: ").strip()

            telefono = validar_telefono("Telefono del Cliente: ")

            print(f"\n--- Seleccione la Zona de Entrega ---")
            for k, v in ZONAS_CONFIG.items():
                print(f"  - {k} (Envio: ${v['costo']}, ~{v['tiempo']} min)")
            zona = input("Zona: ").strip().capitalize()
            while zona not in ZONAS_CONFIG:
                print(f"{ROJO}Zona no valida. Opciones: {', '.join(ZONAS_CONFIG.keys())}{RESET}")
                zona = input("Zona: ").strip().capitalize()

            total_prod = validar_flotante("Monto total de los productos: $")

            print(f"\n--- Metodo de Pago ---")
            print("1. Efectivo\n2. Tarjeta de Debito\n3. Tarjeta de Credito\n4. Transferencia\n5. Mercado Pago")
            op_pago = seleccionar_opcion("Seleccione (1-5): ", {"1", "2", "3", "4", "5"})
            metodos = {"1": "Efectivo", "2": "Tarjeta de Debito", "3": "Tarjeta de Credito",
                       "4": "Transferencia", "5": "Mercado Pago"}
            metodo_pago = metodos[op_pago]

            print(f"\n--- Prioridad ---")
            print("1. Alta\n2. Normal\n3. Baja")
            op_prio = seleccionar_opcion("Seleccione (1-3): ", {"1", "2", "3"})
            prioridades = {"1": "Alta", "2": "Normal", "3": "Baja"}
            prioridad = prioridades[op_prio]

            observaciones = input("Observaciones (opcional): ").strip()

            print(f"\n--- Repartidor ---")
            for i, r in enumerate(REPARTIDORES, 1):
                print(f"{i}. {r['nombre']} - {r['telefono']} (Calif: {r['calificacion']})")
            op_rep = seleccionar_opcion("Seleccione repartidor (1-5): ", {"1", "2", "3", "4", "5"})
            repartidor = REPARTIDORES[int(op_rep) - 1]["nombre"]

            sistema.registrar_pedido(cliente, direccion, telefono, zona, total_prod,
                                     metodo_pago, prioridad, observaciones, repartidor)
            pausa()

        elif opcion == "2":
            id_p = validar_entero("Ingrese el ID del pedido: ")
            pedido = sistema.buscar_pedido(id_p)
            if pedido:
                print(pedido.mostrar_completo())
            else:
                print(f"\n{ROJO}Pedido #{id_p} no encontrado.{RESET}")
            pausa()

        elif opcion == "3":
            id_p = validar_entero("Ingrese el ID del pedido a editar: ")
            pedido = sistema.buscar_pedido(id_p)
            if not pedido:
                print(f"\n{ROJO}Pedido no encontrado.{RESET}")
                pausa()
                continue

            print(f"\n{NEGRITA}Editando Pedido #{id_p}{RESET}")
            print(f"{CIAN}Deje en blanco para mantener el valor actual.{RESET}")
            print(f"Cliente actual: {pedido.cliente}")
            nuevo_cliente = input("Nuevo cliente: ").strip() or None

            print(f"Direccion actual: {pedido.direccion}")
            nueva_direccion = input("Nueva direccion: ").strip() or None

            print(f"Telefono actual: {pedido.telefono}")
            nuevo_telefono = input("Nuevo telefono: ").strip() or None

            print(f"Zona actual: {pedido.zona}")
            nueva_zona = input("Nueva zona: ").strip().capitalize() or None
            if nueva_zona and nueva_zona not in ZONAS_CONFIG:
                print(f"{AMARILLO}Zona no valida, se mantiene la actual.{RESET}")
                nueva_zona = None

            print(f"Monto actual: ${pedido.total_productos:.2f}")
            nuevo_monto_str = input("Nuevo monto: $").strip()
            nuevo_monto = float(nuevo_monto_str) if nuevo_monto_str else None

            kwargs = {}
            if nuevo_cliente: kwargs["cliente"] = nuevo_cliente
            if nueva_direccion: kwargs["direccion"] = nueva_direccion
            if nuevo_telefono: kwargs["telefono"] = nuevo_telefono
            if nueva_zona: kwargs["zona"] = nueva_zona
            if nuevo_monto is not None: kwargs["total_productos"] = nuevo_monto

            if kwargs:
                cambios, msg = sistema.editar_pedido(id_p, **kwargs)
                if cambios:
                    print(f"{VERDE}[OK] Pedido #{id_p} actualizado: {', '.join(cambios)}{RESET}")
                else:
                    print(f"{ROJO}{msg}{RESET}")
            else:
                print(f"{AMARILLO}No se realizaron cambios.{RESET}")
            pausa()

        elif opcion == "4":
            print(f"\n{NEGRITA}--- CAMBIAR ESTADO ---{RESET}")
            id_p = validar_entero("Ingrese el ID del pedido: ")
            pedido = sistema.buscar_pedido(id_p)
            if not pedido:
                print(f"{ROJO}Pedido no encontrado.{RESET}")
                pausa()
                continue

            print(f"Estado actual: {COLORES_ESTADO.get(pedido.estado, '')}[{pedido.estado}]{RESET}")
            print("\nNuevo estado:")
            print("1. Pendiente\n2. En Camino\n3. Entregado\n4. Cancelado")
            op_est = seleccionar_opcion("Seleccione (1-4): ", {"1", "2", "3", "4"})
            mapa = {"1": "Pendiente", "2": "En Camino", "3": "Entregado", "4": "Cancelado"}
            nuevo_est = mapa[op_est]

            motivo = ""
            if nuevo_est == "Cancelado":
                print(f"\n{ROJO}--- Motivo de Cancelacion ---{RESET}")
                for i, m in enumerate(MOTIVOS_CANCELACION, 1):
                    print(f"{i}. {m}")
                op_mot = seleccionar_opcion("Seleccione motivo (1-6): ",
                                            {str(i) for i in range(1, len(MOTIVOS_CANCELACION) + 1)})
                motivo = MOTIVOS_CANCELACION[int(op_mot) - 1]
                if motivo == "Otro":
                    motivo = input("Especifique el motivo: ").strip()

            ok, msg = sistema.actualizar_estado(id_p, nuevo_est, motivo)
            if ok:
                color = COLORES_ESTADO.get(nuevo_est, "")
                print(f"{VERDE}[OK] Estado del pedido #{id_p} actualizado a {color}[{nuevo_est}]{RESET}")
            else:
                print(f"{ROJO}[X] {msg}{RESET}")
            pausa()

        elif opcion == "5":
            print(f"\n{NEGRITA}--- CANCELAR PEDIDO ---{RESET}")
            id_p = validar_entero("Ingrese el ID del pedido a cancelar: ")
            pedido = sistema.buscar_pedido(id_p)
            if not pedido:
                print(f"{ROJO}Pedido no encontrado.{RESET}")
                pausa()
                continue

            if pedido.estado == "Cancelado":
                print(f"{AMARILLO}El pedido ya esta cancelado.{RESET}")
                pausa()
                continue

            print(f"\n{ROJO}--- Motivo de Cancelacion ---{RESET}")
            for i, m in enumerate(MOTIVOS_CANCELACION, 1):
                print(f"{i}. {m}")
            op_mot = seleccionar_opcion("Seleccione motivo (1-6): ",
                                        {str(i) for i in range(1, len(MOTIVOS_CANCELACION) + 1)})
            motivo = MOTIVOS_CANCELACION[int(op_mot) - 1]
            if motivo == "Otro":
                motivo = input("Especifique el motivo: ").strip()

            ok, msg = sistema.actualizar_estado(id_p, "Cancelado", motivo)
            if ok:
                print(f"{ROJO}[X] Pedido #{id_p} cancelado. Motivo: {motivo}{RESET}")
            else:
                print(f"{ROJO}{msg}{RESET}")
            pausa()

        elif opcion == "6":
            sistema.mostrar_pedidos()
            pausa()

        elif opcion == "7":
            id_p = validar_entero("Ingrese el ID del pedido: ")
            pedido = sistema.buscar_pedido(id_p)
            if pedido:
                print(pedido.mostrar_completo())
            else:
                print(f"{ROJO}Pedido no encontrado.{RESET}")
            pausa()

        elif opcion == "8":
            id_p = validar_entero("Ingrese el ID del pedido: ")
            pedido = sistema.buscar_pedido(id_p)
            if pedido:
                print(pedido.ticket())
            else:
                print(f"{ROJO}Pedido no encontrado.{RESET}")
            pausa()

        elif opcion == "9":
            print(f"\n{NEGRITA}--- ORDENAR PEDIDOS ---{RESET}")
            print("1. Mayor a menor total")
            print("2. Menor a mayor total")
            print("3. Por cliente (A-Z)")
            print("4. Por zona")
            print("5. Mas recientes primero")
            criterio = seleccionar_opcion("Seleccione criterio (1-5): ", {"1", "2", "3", "4", "5"})
            sistema.ordenar_pedidos(criterio)
            pausa()

        elif opcion == "10":
            sistema.ranking_zonas()
            pausa()

        elif opcion == "11":
            sistema.mostrar_estadisticas()
            pausa()

        elif opcion == "12":
            id_p = validar_entero("Ingrese el ID del pedido para simular: ")
            pedido = sistema.buscar_pedido(id_p)
            if not pedido:
                print(f"{ROJO}Pedido no encontrado.{RESET}")
                pausa()
                continue
            if pedido.estado == "Cancelado":
                print(f"{ROJO}No se puede simular un pedido cancelado.{RESET}")
                pausa()
                continue
            if pedido.estado == "Entregado":
                print(f"{AMARILLO}El pedido ya fue entregado.{RESET}")
                pausa()
                continue

            sistema.actualizar_estado(id_p, "En Camino", "Iniciando simulacion de recorrido")
            sistema.simulacro_recorrido(id_p)
            pausa()

        elif opcion == "13":
            id_p = validar_entero("Ingrese el ID del pedido: ")
            sistema.historial_cambios(id_p)
            pausa()

        elif opcion == "14":
            print(f"\n{VERDE}Saliendo del sistema!{RESET}")
            print(f"{NEGRITA}Gracias por usar RAPI DELIVERY!{RESET}")
            sistema.guardar_datos()
            break

        else:
            print(f"{ROJO}Opcion incorrecta.{RESET}")
            pausa()


if __name__ == "__main__":
    menu()
