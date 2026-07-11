from database import crear_tablas, agregar_producto, obtener_inventario, restar_stock
from ia_service import generar_receta_con_inventario

def mostrar_menu():
    print("\n" + "="*40)
    print(" 🧊 HELADERA INTELIGENTE - MENÚ")
    print("="*40)
    print("1. Ver inventario actual")
    print("2. Agregar / Cargar producto")
    print("3. Restar producto (Consumo manual)")
    print("4. Evaluar si el stock alcanza para el mes")
    print("5. 🤖 Generar sugerencia de receta con IA (Gemini)")
    print("6. Salir")
    print("="*40)

def menu_ver_inventario():
    productos = obtener_inventario()
    print("\n--- 📦 INVENTARIO ACTUAL ---")
    if not productos:
        print("La heladera está vacía.")
        return

    for p in productos:
        porciones = p['cantidad'] // p['cantidad_por_porcion']
        vencimiento = p['fecha_vencimiento'] if p['fecha_vencimiento'] else "Sin fecha"
        print(f"• ID {p['id']} | {p['nombre'].capitalize()}: {p['cantidad']} {p['unidad']}")
        print(f"  ├─ Porción aprox: {p['cantidad_por_porcion']}{p['unidad']} ({int(porciones)} comidas dispon.)")
        print(f"  └─ Categoría: {p['categoria']} | Vence: {vencimiento}")

def menu_agregar_producto():
    print("\n--- ➕ AGREGAR PRODUCTO ---")
    nombre = input("Nombre del producto (ej. arroz, huevo): ").strip()
    if not nombre:
        print("El nombre no puede estar vacío.")
        return

    try:
        cantidad = float(input("Cantidad total a ingresar: "))
        unidad = input("Unidad de medida (gramos, unidades, ml, etc.): ").strip()
        cantidad_porcion = float(input(f"¿Cuántos {unidad} se usan por cada comida/ración?: "))
        categoria = input("Categoría (Proteína, Carbohidrato, Verdura, etc.): ").strip()
        fecha_venc = input("Fecha de vencimiento (YYYY-MM-DD) [Opcional - Enter para omitir]: ").strip()
        
        if fecha_venc == "":
            fecha_venc = None

        agregar_producto(nombre, cantidad, unidad, cantidad_porcion, categoria, fecha_venc)
    except ValueError:
        print("❌ Error: Ingresa un número válido para cantidades.")

def menu_restar_producto():
    print("\n--- ➖ RESTAR / CONSUMIR PRODUCTO ---")
    nombre = input("Nombre del producto consumido: ").strip()
    try:
        cantidad = float(input("Cantidad a restar: "))
        restar_stock(nombre, cantidad)
    except ValueError:
        print("❌ Error: Ingresa un número válido para la cantidad.")

def menu_evaluar_mes():
    print("\n--- 📊 EVALUACIÓN DE STOCK MENSUAL (120 COMIDAS) ---")
    productos = obtener_inventario()
    if not productos:
        print("La heladera está vacía. No hay alimentos para evaluar.")
        return

    total_porciones = 0
    por_categoria = {}

    for p in productos:
        porciones = p['cantidad'] // p['cantidad_por_porcion']
        total_porciones += porciones
        cat = p['categoria'].capitalize()
        por_categoria[cat] = por_categoria.get(cat, 0) + porciones

    print(f"\nResumen:")
    print(f"• Comidas totales proyectadas: {int(total_porciones)} / 120 necesarias")
    for cat, cant in por_categoria.items():
        print(f"  - {cat}: {int(cant)} porciones")

    if total_porciones >= 120:
        print("\n✅ ¡Felicitaciones! Tienes stock suficiente para cubrir el plan mensual.")
    else:
        faltantes = 120 - total_porciones
        print(f"\n⚠️ ALERTA: No alcanzas a cubrir el mes. Te faltan aprox. {int(faltantes)} porciones de comida.")

def menu_receta_ia():
    print("\n--- 🤖 SUGERENCIA DE RECETA CON GEMINI ---")
    productos = obtener_inventario()
    resultado = generar_receta_con_inventario(productos)
    print("\n" + resultado)

def iniciar_app():
    crear_tablas()
    
    while True:
        mostrar_menu()
        opcion = input("Selecciona una opción (1-6): ").strip()
        
        if opcion == "1":
            menu_ver_inventario()
        elif opcion == "2":
            menu_agregar_producto()
        elif opcion == "3":
            menu_restar_producto()
        elif opcion == "4":
            menu_evaluar_mes()
        elif opcion == "5":
            menu_receta_ia()
        elif opcion == "6":
            print("\n¡Hasta luego! Guardando cambios en la heladera...")
            break
        else:
            print("Opción inválida. Intenta nuevamente.")

if __name__ == "__main__":
    iniciar_app()