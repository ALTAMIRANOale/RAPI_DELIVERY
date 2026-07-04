# RAPI DELIVERY - Documentación del Proyecto

## Resumen del Proyecto

Sistema de gestión de delivery desarrollado en Python como trabajo práctico. Partiendo de un código base funcional, se realizaron **21 mejoras** que transforman la app en un sistema completo, moderno y robusto para la administración de pedidos a domicilio en la ciudad de Resistencia.

---

## 1. Mejoras Implementadas (Las 20 funcionalidades)

### 1.1 Información del Repartidor
Se agregó una base de datos interna con 5 repartidores, cada uno con nombre, teléfono y calificación. Al registrar un pedido, el usuario selecciona el repartidor disponible. También se muestra esta información en pedidos completos y tickets.

### 1.2 Tiempo Estimado de Entrega
El sistema calcula automáticamente el tiempo estimado basado en la zona de entrega (Centro: 15min, Norte/Sur: 25min, Este/Oeste: 30min). La prioridad del pedido ajusta este tiempo (Alta: -5min, Baja: +5min).

### 1.3 Historial de Cambios de Pedidos
Cada pedido mantiene un registro cronológico completo de todos los cambios de estado y ediciones, con fecha, hora y detalle de cada modificación. Se puede visualizar desde el menú principal.

### 1.4 Prioridad del Pedido
Tres niveles de prioridad (Alta, Normal, Baja) que afectan el tiempo estimado de entrega. La prioridad se selecciona al registrar el pedido.

### 1.5 Método de Pago
Se incorporaron 5 métodos de pago: Efectivo, Tarjeta de Débito, Tarjeta de Crédito, Transferencia y Mercado Pago. Se muestran en pedidos, tickets y estadísticas.

### 1.6 Observaciones
Campo opcional para agregar notas al pedido (ej: "Dejar en portería", "Tocar timbre 3 veces").

### 1.7 Información del Cliente
Los datos del cliente se expandieron para incluir nombre, dirección, teléfono y zona, emulando una ficha completa de cliente.

### 1.8 Cancelar Pedido con Motivo
Al cancelar un pedido, se debe seleccionar un motivo de una lista predefinida (Sin stock, Cliente no responde, Pedido duplicado, Cliente canceló, Dirección incorrecta, Otro), lo que queda registrado en el historial.

### 1.9 Editar (Modificar) Pedido
Función completa de edición que permite modificar cliente, dirección, teléfono, zona y monto. Solo se cambian los campos que el usuario indique; los demás se mantienen. El sistema recalcula automáticamente envío, descuentos y total.

### 1.10 Mostrar Pedido Completo
Vista detallada de un pedido con toda su información: cliente, dirección, teléfono, zona, productos, envío, descuento, total, estado con color, fecha, prioridad, repartidor, método de pago, observaciones y tiempo estimado.

### 1.11 Colores según el Estado
Cada estado tiene un color ANSI distintivo:
| Estado | Color |
|--------|-------|
| Pendiente | Amarillo |
| En Camino | Azul |
| Entregado | Verde |
| Cancelado | Rojo |

### 1.12 Ticket de Pedido
Formato de ticket para imprimir/visualizar con diseño profesional, que incluye todos los datos del pedido y el mensaje final "¡Gracias por elegirnos!".

### 1.13 Guardar Datos en Archivo
Persistencia completa mediante archivo JSON (`pedidos.txt`). Los pedidos se guardan automáticamente tras cada operación (registro, edición, cambio de estado) y se cargan al iniciar el sistema.

### 1.14 Ranking de Zonas
Ranking visual con medallas (oro, plata, bronce) por facturación y cantidad de pedidos por zona. Permite identificar las zonas más rentables y con mayor actividad.

### 1.15 Estadísticas más Completas
Sistema de estadísticas expandido que incluye:
- Visión general por estado (entregados, pendientes, en camino, cancelados)
- Facturación total, pedido promedio, mayor y menor venta
- Pedidos e ingresos por zona
- Ranking de zonas (mejor y peor)
- Métodos de pago utilizados

### 1.16 Validación de Datos
Validaciones robustas en todos los campos:
- Menús numéricos con opciones acotadas
- Validación de montos (números positivos)
- Validación de teléfono (debe contener dígitos)
- Campos obligatorios no vacíos
- Zonas restringidas a las opciones disponibles

### 1.17 Ordenar Pedidos
Cinco criterios de ordenamiento: mayor a menor total, menor a mayor total, por cliente (A-Z), por zona y más recientes primero. Útil para analizar y presentar datos.

### 1.18 Menú más Atractivo
Menú principal renovado con 14 opciones organizadas numéricamente:
1. Registrar Nuevo Pedido
2. Buscar Pedido
3. Editar Pedido
4. Cambiar Estado
5. Cancelar Pedido
6. Listar Pedidos
7. Mostrar Pedido Completo
8. Generar Ticket
9. Ordenar Pedidos
10. Ranking de Zonas
11. Estadísticas Completas
12. Simulacro de Recorrido
13. Ver Historial
14. Salir

### 1.19 Cálculo Automático del Envío y Sistema de Descuentos
- **Envío**: Cálculo automático por zona (Centro: $800, Norte/Sur: $1200, Este/Oeste: $1500)
- **Descuentos**:
  - 5% de descuento en pedidos >= $5,000
  - 10% de descuento en pedidos >= $10,000

### 1.20 Simulacro de Recorrido y Tiempo Real del Pedido
Simulación visual con barra de progreso animada que muestra el recorrido del pedido en 10 etapas, desde la preparación hasta la entrega. Incluye:
- Barra de progreso en tiempo real
- Porcentaje de avance
- Descripción de cada etapa
- Tiempo real calculado según zona y prioridad

### 1.21 Selección de Pedidos con Lista Compacta y Búsqueda por Nombre
Antes de realizar cualquier operación que requiera un ID (editar, cancelar, cambiar estado, ver detalle, ticket, simulación, historial), el sistema muestra automáticamente una **lista compacta** de todos los pedidos con su ID, estado, cliente y total. Además, permite **buscar por nombre de cliente**:
- Si ingresa un número, busca por ID exacto
- Si ingresa texto, busca coincidencias parciales en el nombre del cliente
- Si hay múltiples resultados, los lista y solicita el ID exacto
- Si hay un solo resultado, lo selecciona automáticamente
- Si presiona Enter vacío, cancela la operación

Esto elimina la necesidad de memorizar IDs o cambiar de pantalla para consultar la lista.

---

## 2. Estructura del Código

### Archivos
- `app.py` - Código principal de la aplicación
- `pedidos.txt` - Archivo de datos (se genera automáticamente)
- `PRESENTACION.md` - Este documento

### Clases y Funciones Principales

```
app.py
├── Clase Pedido
│   ├── __init__() - Constructor con todos los datos del pedido
│   ├── calcular_envio() - Cálculo automático del envío por zona
│   ├── calcular_descuento() - Sistema de descuentos por monto
│   ├── tiempo_estimado() - Tiempo de entrega según zona y prioridad
│   ├── cambiar_estado() - Cambio de estado con validación y motivo
│   ├── editar() - Edición de campos con recálculo automático
│   ├── mostrar_completo() - Vista detallada del pedido
│   ├── ticket() - Generación de ticket formateado
│   ├── to_dict() - Serialización a diccionario
│   └── from_dict() - Deserialización desde diccionario
│
├── Clase GestionDelivery
│   ├── __init__() - Inicialización con carga de datos
│   ├── guardar_datos() - Persistencia a archivo JSON
│   ├── cargar_datos() - Carga desde archivo JSON
│   ├── registrar_pedido() - Registro con todos los datos
│   ├── actualizar_estado() - Cambio de estado con motivo
│   ├── buscar_pedido() - Búsqueda por ID
│   ├── editar_pedido() - Edición delegada con persistencia
│   ├── mostrar_pedidos() - Listado completo con colores
│   ├── mostrar_estadisticas() - Estadísticas expandidas
│   ├── ranking_zonas() - Ranking de zonas
│   ├── ordenar_pedidos() - Ordenamiento múltiple
│   ├── simulacro_recorrido() - Simulación visual de entrega
│   └── historial_cambios() - Visualización del historial
│
├── Funciones auxiliares
│   ├── pausa(), limpiar() - UI helpers
│   ├── validar_entero(), validar_flotante() - Validación numérica
│   ├── validar_telefono() - Validación de teléfono
│   ├── seleccionar_opcion() - Menú con opciones acotadas
│   ├── mostrar_lista_compacta() - Listado rápido de pedidos
│   └── seleccionar_pedido() - Busca pedido por ID o nombre del cliente
│
└── menu() - Función principal con ciclo interactivo
```

### Constantes y Configuración
- `COLORES_ESTADO` - Mapa de estados a colores ANSI
- `ZONAS_CONFIG` - Configuración de costos y tiempos por zona
- `MOTIVOS_CANCELACION` - Lista de motivos predefinidos
- `REPARTIDORES` - Base de datos de repartidores
- `OPCIONES_MENU` - Definición del menú principal

---

## 3. Decisiones Técnicas

### Persistencia con JSON
Se eligió JSON sobre formatos más simples como CSV o TXT plano porque:
- Soporta estructuras anidadas (historial, diccionarios)
- Es legible por humanos
- Fácil de parsear sin librerías externas
- Mantiene tipos de datos (números, strings, booleanos)

### Colores ANSI en Windows
Los códigos ANSI funcionan en Windows 10+ nativamente. Se usaron códigos como `\033[92m` para colorear estados, mejorando la experiencia visual sin dependencias externas.

### Sin Librerías Externas
Todo el código usa solo la biblioteca estándar de Python (`datetime`, `json`, `os`, `time`, `random`, `sys`), garantizando que funcione en cualquier entorno con Python 3.6+.

### Arquitectura
- **Clase Pedido**: Modelo de datos puro con lógica de negocio asociada
- **Clase GestionDelivery**: Fachada que orquesta la lógica y persistencia
- **Menú**: Capa de presentación desacoplada

---

## 4. Guion para Video de 5 Minutos

### Parte 1: Introducción (0:00 - 1:00) - "¿Qué es RAPI DELIVERY?"

```
¡Hola a todos! Hoy les voy a presentar RAPI DELIVERY, un sistema de gestión 
de pedidos para delivery desarrollado en Python.

Partimos de un código base funcional con lo básico: registrar pedidos, 
cambiar estados y ver estadísticas simples. Nuestro objetivo fue transformarlo 
en un sistema profesional, robusto y completo.

¿Qué logramos? Implementamos 20 mejoras que cubren desde información del 
cliente y repartidor, hasta simulación de recorridos en tiempo real, 
persistencia de datos, ranking de zonas, sistema de descuentos y mucho más.

Lo mejor de todo: todo el código usa solo la biblioteca estándar de Python, 
sin librerías externas. Vamos a verlo en acción.
```

### Parte 2: Registro y Gestión de Pedidos (1:00 - 2:00) - "De la creación al seguimiento"

```
Al ejecutar la app, nos encontramos con un menú de 14 opciones. 
Vamos a registrar un pedido: ingresamos cliente, dirección, teléfono, 
zona - donde el envío se calcula automáticamente según la zona de Resistencia.

Luego elegimos método de pago entre 5 opciones, asignamos prioridad - 
que afecta el tiempo de entrega - seleccionamos un repartidor con su 
nombre y calificación, y podemos agregar observaciones.

El sistema calcula automáticamente descuentos: 5% para pedidos mayores 
a $5,000 y 10% para mayores a $10,000. Al finalizar, se genera un ticket 
completo con el mensaje "¡Gracias por elegirnos!".

Un detalle muy práctico: cada vez que necesitamos buscar, editar o 
cancelar un pedido, el sistema muestra automáticamente una lista compacta 
con todos los pedidos y sus IDs. Además, podemos buscar directamente 
escribiendo el nombre del cliente - no hace falta memorizar IDs. 

Podemos ver la información completa con colores según el estado, 
editar cualquier campo, cambiar estados, o cancelar exigiendo 
un motivo de una lista predefinida.
```

### Parte 3: Análisis y Datos (2:00 - 3:00) - "Tomando decisiones con datos"

```
Una de las mejoras más potentes es el sistema de estadísticas completas. 
Nos muestra: facturación total, pedido promedio, mayor y menor venta, 
distribución por estados, ingresos por zona y métodos de pago.

El ranking de zonas con medallas de oro, plata y bronce nos permite 
identinar qué zonas generan más ingresos y cuáles tienen más pedidos. 
Esto es clave para decisiones de negocio.

También podemos ordenar los pedidos por 5 criterios diferentes: 
por total (mayor a menor o viceversa), por cliente, por zona, 
o por fecha. Y cada pedido mantiene un historial completo de todos 
los cambios que sufrió desde su creación.
```

### Parte 4: Simulación y Persistencia (3:00 - 4:00) - "En tiempo real"

```
Una funcionalidad muy interesante es el simulacro de recorrido. 
Cuando un pedido está "En Camino", podemos ejecutar la simulación: 
vemos una barra de progreso animada que avanza en tiempo real, 
mostrando 10 etapas del recorrido: desde la preparación del pedido 
hasta la entrega al cliente.

El tiempo de la simulación se calcula según la zona y la prioridad, 
dando una experiencia realista. Al finalizar, el pedido se marca 
automáticamente como "Entregado".

Todos los datos se guardan automáticamente en un archivo pedidos.txt 
en formato JSON. Al reiniciar la app, los pedidos se cargan 
automáticamente. No se pierde información entre sesiones.
```

### Parte 5: Cierre y Reflexión (4:00 - 5:00) - "Lo aprendido"

```
Para cerrar, quiero destacar algunos aspectos técnicos importantes:

1) Validación de datos en todos los campos - evitamos errores de 
   ingreso con menús acotados y validaciones robustas.

2) Colores ANSI para mejorar la experiencia visual del usuario 
   - cada estado tiene su propio color distintivo.

3) Arquitectura limpia con clases Pedido y GestionDelivery bien 
   diferenciadas, más funciones auxiliares reutilizables.

4) Código 100% Python estándar, sin dependencias externas.

En resumen, transformamos una app básica en un sistema de delivery 
completo y profesional, manteniendo la estructura original pero 
agregando valor real en cada funcionalidad.

¡Gracias por su atención! El código completo está disponible en el 
repositorio para su revisión.
```

---

## 5. Requisitos de Instalación y Ejecución

### Requisitos
- Python 3.6 o superior
- No requiere librerías externas

### Ejecución
```bash
python app.py
```

### Archivo de datos
Los pedidos se guardan automáticamente en `pedidos.txt` (formato JSON). Si el archivo se elimina, el sistema arranca limpio.
