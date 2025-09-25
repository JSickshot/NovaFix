import sqlite3
import os

# Nombre de la base de datos
DB = os.path.join(os.path.dirname(__file__), "novafix_pos.db")

def init_db():
    conn = sqlite3.connect(DB)
    c = conn.cursor()

    # Tabla de usuarios
    c.execute("""
    CREATE TABLE IF NOT EXISTS usuarios (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE NOT NULL,
        password TEXT NOT NULL,
        rol TEXT NOT NULL
    )
    """)

    # Tabla de clientes
    c.execute("""
    CREATE TABLE IF NOT EXISTS clientes (
        cliente_id INTEGER PRIMARY KEY AUTOINCREMENT,
        nombre TEXT NOT NULL,
        apellido TEXT,
        telefono TEXT,
        email TEXT,
        direccion TEXT,
        ciudad TEXT,
        codigo_postal TEXT,
        fecha_registro TEXT
    )
    """)

    # Tabla de inventario
    c.execute("""
    CREATE TABLE IF NOT EXISTS inventario (
        pieza_id INTEGER PRIMARY KEY AUTOINCREMENT,
        pieza TEXT UNIQUE NOT NULL,
        descripcion TEXT,
        stock INTEGER DEFAULT 0,
        precio_unitario REAL DEFAULT 0
    )
    """)

    # Tabla de tickets
    c.execute("""
    CREATE TABLE IF NOT EXISTS tickets (
        ticket_id INTEGER PRIMARY KEY AUTOINCREMENT,
        folio TEXT NOT NULL,
        cliente_id INTEGER,
        fecha_ingreso TEXT,
        descripcion_equipo TEXT,
        diagnostico TEXT,
        estado TEXT,
        costo_total REAL DEFAULT 0,
        anticipo REAL DEFAULT 0,
        FOREIGN KEY (cliente_id) REFERENCES clientes(cliente_id)
    )
    """)

    # Tabla de ventas
    c.execute("""
    CREATE TABLE IF NOT EXISTS ventas (
        venta_id INTEGER PRIMARY KEY AUTOINCREMENT,
        ticket_id INTEGER,
        pieza_id INTEGER,
        cantidad INTEGER,
        precio_unitario REAL,
        FOREIGN KEY (ticket_id) REFERENCES tickets(ticket_id),
        FOREIGN KEY (pieza_id) REFERENCES inventario(pieza_id)
    )
    """)

    # Usuario inicial (sistemas)
    c.execute("SELECT * FROM usuarios WHERE username='julio'")
    if not c.fetchone():
        c.execute("INSERT INTO usuarios (username,password,rol) VALUES (?,?,?)",
                  ("julio", "1234", "sistemas"))

    conn.commit()
    conn.close()


def verificar_esquema():
    """
    Verifica que todas las tablas y columnas necesarias existan.
    Si falta alguna columna, la agrega automáticamente.
    """
    conn = sqlite3.connect(DB)
    c = conn.cursor()

    # --- Usuarios ---
    c.execute("PRAGMA table_info(usuarios)")
    cols = [col[1] for col in c.fetchall()]
    if "rol" not in cols:
        c.execute("ALTER TABLE usuarios ADD COLUMN rol TEXT DEFAULT 'ventas'")

    # --- Clientes ---
    c.execute("PRAGMA table_info(clientes)")
    cols = [col[1] for col in c.fetchall()]
    for col, tipo in [
        ("apellido", "TEXT"),
        ("telefono", "TEXT"),
        ("email", "TEXT"),
        ("direccion", "TEXT"),
        ("ciudad", "TEXT"),
        ("codigo_postal", "TEXT"),
        ("fecha_registro", "TEXT"),
    ]:
        if col not in cols:
            c.execute(f"ALTER TABLE clientes ADD COLUMN {col} {tipo}")

    # --- Inventario ---
    c.execute("PRAGMA table_info(inventario)")
    cols = [col[1] for col in c.fetchall()]
    for col, tipo, default in [
        ("descripcion", "TEXT", "''"),
        ("stock", "INTEGER", "0"),
        ("precio_unitario", "REAL", "0"),
    ]:
        if col not in cols:
            c.execute(f"ALTER TABLE inventario ADD COLUMN {col} {tipo} DEFAULT {default}")

    # --- Tickets ---
    c.execute("PRAGMA table_info(tickets)")
    cols = [col[1] for col in c.fetchall()]
    for col, tipo, default in [
        ("descripcion_equipo", "TEXT", "''"),
        ("diagnostico", "TEXT", "''"),
        ("estado", "TEXT", "''"),
        ("costo_total", "REAL", "0"),
        ("anticipo", "REAL", "0"),
    ]:
        if col not in cols:
            c.execute(f"ALTER TABLE tickets ADD COLUMN {col} {tipo} DEFAULT {default}")

    # --- Ventas ---
    c.execute("PRAGMA table_info(ventas)")
    cols = [col[1] for col in c.fetchall()]
    for col, tipo in [
        ("cantidad", "INTEGER"),
        ("precio_unitario", "REAL"),
    ]:
        if col not in cols:
            c.execute(f"ALTER TABLE ventas ADD COLUMN {col} {tipo}")

    conn.commit()
    conn.close()
