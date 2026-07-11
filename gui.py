import os
import flet as ft
import os
import sys
import ssl
import certifi

# Forzar a Python a usar los certificados de certifi (ideal para PyInstaller)
os.environ['SSL_CERT_FILE'] = certifi.where()
os.environ['REQUESTS_CA_BUNDLE'] = certifi.where()

# Opcional: Contexto SSL por defecto
try:
    ssl._create_default_https_context = ssl._create_unverified_context
except AttributeError:
    pass

from database import (
    obtener_inventario, 
    agregar_producto, 
    crear_tablas, 
    eliminar_producto, 
    actualizar_producto
)
from ia_service import generar_receta_con_inventario

def main(page: ft.Page):
    page.title = "🧊 Heladera Inteligente v1.0.0-Beta"
    page.theme_mode = ft.ThemeMode.DARK
    page.padding = 20
    page.scroll = ft.ScrollMode.AUTO

    crear_tablas()

    # Variable para almacenar la API Key cargada por el usuario
    api_key_usuario = os.getenv("GEMINI_API_KEY", "")

# --- DIÁLOGO DE CONFIGURACIÓN DE API KEY ---
    txt_input_key = ft.TextField(
        label="Google Gemini API Key",
        password=True,
        can_reveal_password=True,
        hint_text="AIzaSy...",
        autofocus=True
    )

    def guardar_key_click(e):
        nonlocal api_key_usuario
        if not txt_input_key.value.strip():
            page.snack_bar = ft.SnackBar(ft.Text("⚠️ Por favor ingresa una API Key válida."))
            page.snack_bar.open = True
            page.update()
            return

        api_key_usuario = txt_input_key.value.strip()
        dialogo_key.open = False
        page.snack_bar = ft.SnackBar(ft.Text("🔑 API Key configurada correctamente."))
        page.snack_bar.open = True
        page.update()

    def cerrar_dialogo_key(e):
        dialogo_key.open = False
        page.update()

    dialogo_key = ft.AlertDialog(
        modal=False,  # Permite cerrar o interactuar libremente
        title=ft.Row([
            ft.Row([
                ft.Icon(ft.Icons.KEY, color=ft.Colors.AMBER_400),
                ft.Text("Configurar Gemini API Key", size=18, weight=ft.FontWeight.BOLD)
            ], spacing=10),
            ft.IconButton(
                icon=ft.Icons.CLOSE, 
                tooltip="Cerrar", 
                on_click=cerrar_dialogo_key
            )
        ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
        content=ft.Column([
            ft.Text(
                "Para usar las funciones de IA de manera portable, ingresa tu API Key de Google AI Studio. "
                "Esta clave no se guardará en disco ni se compartirá.",
                size=12,
                color=ft.Colors.GREY_300
            ),
            txt_input_key
        ], tight=True, spacing=15),
        actions=[
            ft.TextButton("Cancelar", on_click=cerrar_dialogo_key),
            ft.ElevatedButton("Guardar", on_click=guardar_key_click)
        ]
    )
    page.overlay.append(dialogo_key)

    # Si no hay variable de entorno, abrir el diálogo al iniciar
    if not api_key_usuario:
        dialogo_key.open = True

    # --- COMPONENTES PRINCIPALES ---
    titulo = ft.Row([
        ft.Text("Mi Heladera Inteligente", size=28, weight=ft.FontWeight.BOLD, color=ft.Colors.BLUE_200),
        ft.IconButton(
            icon=ft.Icons.SETTINGS, 
            tooltip="Cambiar API Key", 
            on_click=lambda e: setattr(dialogo_key, "open", True) or page.update()
        )
    ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN)

    lista_inventario = ft.Column(spacing=15)

    UNIDADES_OPCIONES = [
        ft.dropdown.Option("unidades"),
        ft.dropdown.Option("gramos"),
        ft.dropdown.Option("kilogramos"),
        ft.dropdown.Option("litros"),
        ft.dropdown.Option("mililitros"),
        ft.dropdown.Option("paquetes"),
    ]

    CATEGORIAS_OPCIONES = [
        ft.dropdown.Option("Proteínas"),
        ft.dropdown.Option("Carbohidratos"),
        ft.dropdown.Option("Frutas y Verduras"),
        ft.dropdown.Option("Lácteos y Derivados"),
        ft.dropdown.Option("Aceites y Grasas"),
        ft.dropdown.Option("Almacén / Especias"),
        ft.dropdown.Option("Otros"),
    ]

    # --- DIÁLOGO DE EDICIÓN DE PRODUCTO ---
    edit_id = None
    edit_nombre = ft.TextField(label="Nombre")
    edit_cantidad = ft.TextField(label="Cantidad", keyboard_type=ft.KeyboardType.NUMBER)
    edit_unidad = ft.Dropdown(label="Unidad", options=UNIDADES_OPCIONES)
    edit_categoria = ft.Dropdown(label="Categoría", options=CATEGORIAS_OPCIONES)

    def guardar_edicion(e):
        nonlocal edit_id
        if edit_id and edit_nombre.value and edit_cantidad.value and edit_unidad.value and edit_categoria.value:
            try:
                cant = float(edit_cantidad.value.replace(",", "."))
                if cant <= 0:
                    raise ValueError()

                actualizar_producto(
                    edit_id, 
                    edit_nombre.value.strip().lower(), 
                    cant, 
                    edit_unidad.value,
                    edit_categoria.value
                )
                dialogo_editar.open = False
                actualizar_lista_ui()
                page.snack_bar = ft.SnackBar(ft.Text("¡Producto actualizado!"))
                page.snack_bar.open = True
            except ValueError:
                page.snack_bar = ft.SnackBar(ft.Text("⚠️ Ingrese una cantidad válida mayor a 0."))
                page.snack_bar.open = True

    def cancelar_edicion(e):
        dialogo_editar.open = False
        page.update()

    dialogo_editar = ft.AlertDialog(
        title=ft.Text("Editar Producto"),
        content=ft.Column([edit_nombre, edit_cantidad, edit_unidad, edit_categoria], tight=True, spacing=10),
        actions=[
            ft.TextButton("Cancelar", on_click=cancelar_edicion),
            ft.ElevatedButton("Guardar", on_click=guardar_edicion)
        ]
    )
    page.overlay.append(dialogo_editar)

    # --- ACCIONES ---
    def borrar_click(producto_id):
        eliminar_producto(producto_id)
        actualizar_lista_ui()
        page.snack_bar = ft.SnackBar(ft.Text("Producto eliminado."))
        page.snack_bar.open = True

    def abrir_editar(producto):
        nonlocal edit_id
        edit_id = producto['id']
        edit_nombre.value = producto['nombre']
        edit_cantidad.value = str(producto['cantidad'])
        edit_unidad.value = producto['unidad']
        edit_categoria.value = producto.get('categoria', 'Otros')
        dialogo_editar.open = True
        page.update()

    # --- REFRESCAR LISTA ---
    def actualizar_lista_ui():
        lista_inventario.controls.clear()
        productos = obtener_inventario()

        if not productos:
            lista_inventario.controls.append(
                ft.Text("La heladera está vacía. ¡Agrega algunos alimentos para comenzar!", color=ft.Colors.GREY_400)
            )
        else:
            categorias_map = {}
            for p in productos:
                cat = p.get('categoria') if isinstance(p, dict) else (p['categoria'] if 'categoria' in p.keys() and p['categoria'] else "Otros")
                if not cat:
                    cat = "Otros"
                if cat not in categorias_map:
                    categorias_map[cat] = []
                categorias_map[cat].append(p)

            iconos_cat = {
                "Proteínas": ft.Icons.SET_MEAL,
                "Carbohidratos": ft.Icons.BAKERY_DINING,
                "Frutas y Verduras": ft.Icons.LOCAL_GROCERY_STORE,
                "Lácteos y Derivados": ft.Icons.LOCAL_DRINK,
                "Aceites y Grasas": ft.Icons.OPACITY,
                "Almacén / Especias": ft.Icons.KITCHEN,
                "Otros": ft.Icons.CATEGORY,
            }

            for cat_nombre, items in categorias_map.items():
                icon = iconos_cat.get(cat_nombre, ft.Icons.CATEGORY)
                
                header_cat = ft.Row([
                    ft.Icon(icon, color=ft.Colors.BLUE_300, size=20),
                    ft.Text(f"{cat_nombre}", size=16, weight=ft.FontWeight.BOLD, color=ft.Colors.BLUE_200)
                ], spacing=8)

                col_productos = ft.Column(spacing=5)
                for p in items:
                    card = ft.Card(
                        content=ft.Container(
                            content=ft.Row([
                                ft.Column([
                                    ft.Text(f"{p['nombre'].capitalize()}", weight=ft.FontWeight.BOLD, size=15),
                                    ft.Text(f"Stock: {p['cantidad']} {p['unidad']}", color=ft.Colors.GREY_300, size=12)
                                ], expand=True),
                                ft.IconButton(
                                    icon=ft.Icons.EDIT, 
                                    icon_color=ft.Colors.BLUE_300, 
                                    tooltip="Editar",
                                    on_click=lambda e, prod=p: abrir_editar(prod)
                                ),
                                ft.IconButton(
                                    icon=ft.Icons.DELETE, 
                                    icon_color=ft.Colors.RED_400, 
                                    tooltip="Eliminar",
                                    on_click=lambda e, pid=p['id']: borrar_click(pid)
                                )
                            ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
                            padding=10
                        )
                    )
                    col_productos.controls.append(card)

                seccion_cat = ft.Column([header_cat, col_productos], spacing=8)
                lista_inventario.controls.append(seccion_cat)

        page.update()

    # --- FORMULARIO DE ALTA ---
    txt_nombre = ft.TextField(label="Producto", hint_text="ej. Huevos", width=250, dense=True)
    txt_cantidad = ft.TextField(label="Cant.", hint_text="ej. 12", width=90, keyboard_type=ft.KeyboardType.NUMBER, dense=True)
    dd_unidad = ft.Dropdown(label="Unidad", width=130, options=UNIDADES_OPCIONES, value="unidades", dense=True)
    dd_categoria = ft.Dropdown(label="Categoría", width=170, options=CATEGORIAS_OPCIONES, value="Proteínas", dense=True)

    def guardar_producto_click(e):
        if not txt_nombre.value or not txt_cantidad.value:
            page.snack_bar = ft.SnackBar(ft.Text("⚠️ Por favor completa el nombre y la cantidad."))
            page.snack_bar.open = True
            page.update()
            return

        try:
            cant = float(txt_cantidad.value.replace(",", "."))
            if cant <= 0:
                raise ValueError()

            agregar_producto(
                nombre=txt_nombre.value.strip().lower(),
                cantidad=cant,
                unidad=dd_unidad.value,
                cantidad_por_porcion=1,
                categoria=dd_categoria.value
            )
            txt_nombre.value = ""
            txt_cantidad.value = ""
            actualizar_lista_ui()
            page.snack_bar = ft.SnackBar(ft.Text("¡Producto guardado exitosamente!"))
            page.snack_bar.open = True
        except ValueError:
            page.snack_bar = ft.SnackBar(ft.Text("⚠️ Ingresa un número válido y mayor a 0."))
            page.snack_bar.open = True
            page.update()

    btn_agregar = ft.ElevatedButton("Agregar", icon=ft.Icons.ADD, on_click=guardar_producto_click)

    # --- ÁREA DE IA ---
    txt_receta_resultado = ft.Markdown(
        "Presiona el botón para que Gemini analice tu stock y te sugiera una receta.",
        selectable=True
    )
    loading_spinner = ft.ProgressRing(visible=False, width=20, height=20, stroke_width=2)

    def generar_receta_click(e):
        nonlocal api_key_usuario
        
        if not api_key_usuario:
            dialogo_key.open = True
            page.update()
            return

        productos = obtener_inventario()
        if not productos:
            page.snack_bar = ft.SnackBar(ft.Text("⚠️ Agrega al menos un ingrediente antes de generar una receta."))
            page.snack_bar.open = True
            page.update()
            return

        btn_ia.disabled = True
        loading_spinner.visible = True
        txt_receta_resultado.value = "⏳ *Consultando a Gemini con tu inventario...*"
        page.update()
        
        try:
            # Se pasa la clave cargada por el usuario
            resultado = generar_receta_con_inventario(productos, api_key=api_key_usuario)
            txt_receta_resultado.value = resultado
        except Exception as err:
            txt_receta_resultado.value = f"❌ Error al conectar con Gemini: {err}\n\nVerifica que la API Key sea válida."
        finally:
            btn_ia.disabled = False
            loading_spinner.visible = False
            page.update()

    btn_ia = ft.FilledButton(
        "🤖 Generar Receta con IA", 
        icon=ft.Icons.AUTO_AWESOME, 
        on_click=generar_receta_click,
        bgcolor=ft.Colors.DEEP_PURPLE_500,
        color=ft.Colors.WHITE
    )

    # --- ESTRUCTURA GENERAL ---
    page.add(
        titulo,
        ft.Divider(),
        ft.Text("➕ Agregar nuevo producto:", size=16, weight=ft.FontWeight.BOLD),
        ft.Row(
            [txt_nombre, txt_cantidad, dd_unidad, dd_categoria, btn_agregar], 
            alignment=ft.MainAxisAlignment.START,
            vertical_alignment=ft.CrossAxisAlignment.CENTER,
            spacing=10,
            wrap=True
        ),
        ft.Divider(),
        ft.Text("📦 Inventario por Categorías:", size=18, weight=ft.FontWeight.BOLD),
        lista_inventario,
        ft.Divider(),
        ft.Row([btn_ia, loading_spinner], alignment=ft.MainAxisAlignment.CENTER),
        ft.Container(
            content=txt_receta_resultado,
            padding=15,
            border_radius=10,
            bgcolor=ft.Colors.SURFACE_CONTAINER_HIGHEST,
            margin=ft.Margin(0, 10, 0, 0)
        )
    )

    actualizar_lista_ui()

if __name__ == "__main__":
    ft.app(target=main)