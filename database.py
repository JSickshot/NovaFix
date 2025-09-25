import sqlite3

DB = "novafix_pos.db"

def crear_tablas():
    conn = sqlite3.connect(DB)
    c = conn.cursor()

    # Clientes
    c.execute('''
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
    ''')

    # Inventario
    c.execute('''
    CREATE TABLE IF NOT EXISTS inventario (
        pieza_id INTEGER PRIMARY KEY AUTOINCREMENT,
        pieza TEXT UNIQUE NOT NULL,
        descripcion TEXT,
        stock INTEGER NOT NULL,
        precio_unitario REAL
    )
    ''')

    # Tickets
    c.execute('''
    CREATE TABLE IF NOT EXISTS tickets (
        ticket_id INTEGER PRIMARY KEY AUTOINCREMENT,
        folio TEXT UNIQUE NOT NULL,
        cliente_id INTEGER NOT NULL,
        fecha_ingreso TEXT,
        descripcion_equipo TEXT,
        diagnostico TEXT,
        estado TEXT,
        costo_total REAL,
        FOREIGN KEY (cliente_id) REFERENCES clientes(cliente_id)
    )
    ''')

    # Ventas
    c.execute('''
    CREATE TABLE IF NOT EXISTS ventas (
        venta_id INTEGER PRIMARY KEY AUTOINCREMENT,
        ticket_id INTEGER NOT NULL,
        pieza_id INTEGER NOT NULL,
        cantidad INTEGER NOT NULL,
        precio_unitario REAL NOT NULL,
        FOREIGN KEY (ticket_id) REFERENCES tickets(ticket_id),
        FOREIGN KEY (pieza_id) REFERENCES inventario(pieza_id)
    )
    ''')

    # Usuarios
    c.execute('''
    CREATE TABLE IF NOT EXISTS usuarios (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE,
        password TEXT,
        rol TEXT
    )
    ''')

    try:
        c.execute("INSERT INTO usuarios (username, password, rol) VALUES (?, ?, ?)",
                  ("Julio", "1234", "sistemas"))
    except sqlite3.IntegrityError:
        pass

    conn.commit()
    conn.close()
