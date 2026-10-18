import os
import sqlite3
from pathlib import Path

from werkzeug.security import generate_password_hash

DB_NAME = os.environ.get('DATABASE_NAME', 'database.db')

def get_db():
    """Establece conexión con SQLite y permite acceso por nombre de columna."""
    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    """Crea las tablas e inserta los usuarios desde user.txt si la tabla está vacía."""
    conn = get_db()
    try:
        cursor = conn.cursor()

        # Tabla de Usuarios
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS usuarios (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE NOT NULL,
                password TEXT NOT NULL,
                rol TEXT NOT NULL,
                equipo TEXT NOT NULL
            )
        ''')

        # Tabla de Reportes
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS reportes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                nombre_archivo TEXT NOT NULL,
                total_registros INTEGER NOT NULL,
                html_tabla TEXT NOT NULL,
                fecha TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        conn.commit()

        # Verificar si la tabla de usuarios está vacía para poblarla desde user.txt
        cursor.execute("SELECT COUNT(*) FROM usuarios")
        total_usuarios = cursor.fetchone()[0]

        txt_path = Path(__file__).resolve().parent / 'user.txt'

        if total_usuarios == 0 and txt_path.exists():
            with txt_path.open('r', encoding='utf-8') as f:
                for linea in f:
                    linea = linea.strip()
                    if linea and not linea.startswith('#'):
                        # Espera líneas separadas por coma: username, password, rol, equipo
                        partes = [p.strip() for p in linea.split(',')]
                        if len(partes) == 4:
                            hashed_pw = generate_password_hash(partes[1])
                            cursor.execute(
                                "INSERT INTO usuarios (username, password, rol, equipo) VALUES (?, ?, ?, ?)",
                                (partes[0], hashed_pw, partes[2], partes[3])
                            )
            conn.commit()
    finally:
        conn.close()