import sqlite3

def crear_tablas():
    """Crea la tabla de productos si no existe."""
    conn = sqlite3.connect("inventario.db")
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS productos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nombre TEXT NOT NULL,
            cantidad REAL NOT NULL,
            unidad TEXT NOT NULL,
            cantidad_por_porcion REAL DEFAULT 1,
            categoria TEXT DEFAULT 'General',
            fecha_vencimiento TEXT
        )
    """)
    conn.commit()
    conn.close()

def obtener_inventario():
    """Obtiene todos los productos formateados como diccionarios."""
    conn = sqlite3.connect("inventario.db")
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM productos")
    filas = cursor.fetchall()
    conn.close()
    return [dict(fila) for fila in filas]

def agregar_producto(nombre: str, cantidad: float, unidad: str, cantidad_por_porcion: float = 1, categoria: str = "General"):
    """Inserta un nuevo producto."""
    conn = sqlite3.connect("inventario.db")
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO productos (nombre, cantidad, unidad, cantidad_por_porcion, categoria)
        VALUES (?, ?, ?, ?, ?)
    """, (nombre, cantidad, unidad, cantidad_por_porcion, categoria))
    conn.commit()
    conn.close()

def eliminar_producto(producto_id: int):
    """Elimina un producto por ID."""
    conn = sqlite3.connect("inventario.db")
    cursor = conn.cursor()
    cursor.execute("DELETE FROM productos WHERE id = ?", (producto_id,))
    conn.commit()
    conn.close()

def actualizar_producto(producto_id: int, nombre: str, cantidad: float, unidad: str, categoria: str):
    """Actualiza los datos de un producto existente."""
    conn = sqlite3.connect("inventario.db")
    cursor = conn.cursor()
    cursor.execute("""
        UPDATE productos 
        SET nombre = ?, cantidad = ?, unidad = ?, categoria = ?
        WHERE id = ?
    """, (nombre, cantidad, unidad, categoria, producto_id))
    conn.commit()
    conn.close()