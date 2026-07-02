import datetime

class Pedido:  #asi se define una clase en python 
    def __init__(self, id_pedido, cliente, direccion, zona, total_productos):
        self.id_pedido = id_pedido
        self.cliente = cliente
        self.direccion = direccion
        self.zona = zona  # Ej: "Centro", "Norte", "Sur"
        self.total_productos = total_productos
        
        # El costo de envío puede variar según la zona de Resistencia
        self.costo_envio = self.calcular_envio()
        self.total_pagar = self.total_productos + self.costo_envio
        
        # Estados: 'Pendiente', 'En Camino', 'Entregado', 'Cancelado'
        self.estado = "Pendiente" 
        self.fecha_hora = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")

    def calcular_envio(self):
        # Lógica de costos por zona (adaptable a Resistencia)
        zonas_costos = {
            "Centro": 800,
            "Norte": 1200,
            "Sur": 1200,
            "Este": 1500,
            "Oeste": 1500
        }
        return zonas_costos.get(self.zona, 1000) # 1000 por defecto si no coincide

    def cambiar_estado(self, nuevo_estado):
        estados_validos = ["Pendiente", "En Camino", "Entregado", "Cancelado"]
        if nuevo_estado in estados_validos:
            self.estado = nuevo_estado
            return True
        return False


class GestionDelivery:
    def __init__(self):
        self.pedidos = {}  # Usamos un diccionario para buscar por ID rápidamente
        self.contador_id = 1

    def registrar_pedido(self, cliente, direccion, zona, total_productos):
        nuevo_pedido = Pedido(self.contador_id, cliente, direccion, zona, total_productos)
        self.pedidos[self.contador_id] = nuevo_pedido
        print(f"\n✅ Pedido #{self.contador_id} registrado con éxito.")
        self.contador_id += 1

    def actualizar_estado(self, id_pedido, nuevo_estado):
        if id_pedido in self.pedidos:
            if self.pedidos[id_pedido].cambiar_estado(nuevo_estado):
                print(f"\n🔄 Estado del pedido #{id_pedido} actualizado a '{nuevo_estado}'.")
            else:
                print("\n❌ Estado no válido.")
        else:
            print("\n❌ Pedido no encontrado.")

    def mostrar_pedidos(self):
        if not self.pedidos:
            print("\n📭 No hay pedidos registrados.")
            return
        
        print("\n=== LISTADO DE PEDIDOS ===")
        for p in self.pedidos.values():
            print(f"ID: {p.id_pedido} | Cliente: {p.cliente} | Zona: {p.zona} | Total: ${p.total_pagar} | Estado: [{p.estado}]")

    def mostrar_estadisticas(self):
        if not self.pedidos:
            print("\n📊 No hay datos para generar estadísticas.")
            return

        total_ventas = 0
        entregados = 0
        pedidos_por_zona = {}

        for p in self.pedidos.values():
            if p.estado == "Entregado":
                total_ventas += p.total_pagar
                entregados += 1
            
            # Conteo por zonas
            pedidos_por_zona[p.zona] = pedidos_por_zona.get(p.zona, 0) + 1

        print("\n📊 === ESTADÍSTICAS DEL SISTEMA ===")
        print(f"💰 Facturación Total (Solo Entregados): ${total_ventas}")
        print(f"📦 Total de Pedidos Realizados: {len(self.pedidos)}")
        print(f"✅ Entregas Exitosas: {entregados}")
        print("\n📍 Pedidos por Zona:")
        for zona, cant in pedidos_por_zona.items():
            print(f"  - {zona}: {cant} pedido(s)")
def menu():
    sistema = GestionDelivery()
    
    # Datos de prueba iniciales para no arrancar de cero al testear
    

    while True:
        print("\n--- SISTEMA DE DELIVERY ---")
        print("1. Registrar Nuevo Pedido")
        print("2. Mostrar Todos los Pedidos")
        print("3. Cambiar Estado de un Pedido")
        print("4. Ver Estadísticas y Reportes")
        print("5. Salir")
        
        opcion = input("Seleccione una opción: ")

        if opcion == "1":
            cliente = input("Nombre del Cliente: ")
            direccion = input("Dirección de entrega: ")
            print("Zonas válidas: Centro, Norte, Sur, Este, Oeste")
            zona = input("Zona: ").strip().capitalize()
            try:
                total_prod = float(input("Monto total de los productos: $"))
                sistema.registrar_pedido(cliente, direccion, zona, total_prod)
            except ValueError:
                print("❌ Monto inválido. Intente de nuevo.")

        elif opcion == "2":
            sistema.mostrar_pedidos()

        elif opcion == "3":
            try:
                id_p = int(input("Ingrese el ID del pedido: "))
                print("Estados: Pendiente, En Camino, Entregado, Cancelado")
                nuevo_est = input("Nuevo estado: ").strip().title()
                sistema.actualizar_estado(id_p, nuevo_est)
            except ValueError:
                print("❌ ID inválido.")

        elif opcion == "4":
            sistema.mostrar_estadisticas()

        elif opcion == "5":
            print("\n👋 Saliendo del sistema!")
            break
        else:
            print("❌ Opción incorrecta.")

if __name__ == "__main__":
    menu()