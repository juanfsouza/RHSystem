import sqlite3

class Database:
    def __init__(self):
        self.conn = sqlite3.connect("rh_system.db")
        self.create_tables()

    def create_tables(self):
        with self.conn:
            self.conn.execute("""
                CREATE TABLE IF NOT EXISTS usuarios (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    numero TEXT,
                    nome TEXT,
                    email TEXT
                );
            """)
            self.conn.execute("""
                CREATE TABLE IF NOT EXISTS agendamentos (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    usuario_id INTEGER,
                    data_horario TEXT,
                    FOREIGN KEY (usuario_id) REFERENCES usuarios(id)
                );
            """)

    def insert_user(self, numero, nome, email):
        with self.conn:
            self.conn.execute("INSERT INTO usuarios (numero, nome, email) VALUES (?, ?, ?)", (numero, nome, email))

    def get_all_users(self):
        cursor = self.conn.execute("SELECT numero, nome, email FROM usuarios")
        return [{"numero": row[0], "nome": row[1], "email": row[2]} for row in cursor]

    def insert_schedule(self, numero, data):
        with self.conn:
            user_id = self.conn.execute("SELECT id FROM usuarios WHERE numero = ?", (numero,)).fetchone()[0]
            self.conn.execute("INSERT INTO agendamentos (usuario_id, data_horario) VALUES (?, ?)", (user_id, data))
