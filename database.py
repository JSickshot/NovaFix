import sqlite3

DB = "novafix_pos.db"

def crear_tablas():
    conn = sqlite3.connect(DB)
    c = conn.cursor()

    #tickts
    c.execute('''
    CREATE TABLE IF NOT EXISTS tickets (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        folio TEXT UNIQUE,
        cliente TEXT,
        telefono TEXT,
        equipo TEXT,
        falla TEXT,
        estado TEXT,
        fecha_ingreso TEXT,
        fecha_entrega TEXT
    )
    ''')

    #inv
    c.execute('''
    CREATE TABLE IF NOT EXISTS inventario (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        pieza TEXT UNIQUE,
        descripcion TEXT,
        stock INTEGER
    )
    ''')

    c.execute('''
    CREATE TABLE IF NOT EXISTS usuarios (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE,
        password TEXT,
        rol TEXT
    )
    ''')

    #usr
    usuarios_default = [
        ("Cesar", "Icaros300$", "admin"),
        ("Julio", "Sickshot28$nf", "admin"),
        ("Vania", "Apokolips28$", "admin")
    ]

    for u in usuarios_default:
        try:
            c.execute("INSERT INTO usuarios (username, password, rol) VALUES (?, ?, ?)", u)
        except sqlite3.IntegrityError:
            pass

    conn.commit()
    conn.close()
