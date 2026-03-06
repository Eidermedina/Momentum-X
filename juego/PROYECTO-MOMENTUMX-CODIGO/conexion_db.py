import mysql.connector
import hashlib

# ======================================================
# CREDENCIALES — ajustadas a tu MariaDB en XAMPP
# BD: momentumbase | usuario: juan | contraseña: 12345
# ======================================================
DB_HOST = "localhost"
DB_NAME = "momentumbase"
DB_USER = "juan"
DB_PASS = "12345"

class ConexionDB:

    def __init__(self):
        try:
            self.conexion = mysql.connector.connect(
                host     = DB_HOST,
                user     = DB_USER,
                password = DB_PASS,
                database = DB_NAME
            )
            self.cursor = self.conexion.cursor(dictionary=True)
        except mysql.connector.Error as e:
            raise RuntimeError(
                f"\n❌ No se pudo conectar a la base de datos.\n"
                f"   Host: {DB_HOST} | BD: {DB_NAME} | Usuario: {DB_USER}\n"
                f"   Error: {e}\n"
                f"   Verifica que XAMPP esté corriendo y que la BD exista."
            )

    # ____________________________________________________________
    # USUARIO

    def registrar_usuario(self, nombre, correo, contrasena):
        """Registra usuario nuevo. Retorna id_usuario o None si el correo ya existe."""
        self.cursor.execute(
            "SELECT id_usuario FROM usuario WHERE correo = %s", (correo,)
        )
        if self.cursor.fetchone():
            return None

        hash_pw = hashlib.sha256(contrasena.encode()).hexdigest()
        sql = """
            INSERT INTO usuario (nombre, correo, contrasena_hash, fecha_registro, activo)
            VALUES (%s, %s, %s, NOW(), TRUE)
        """
        self.cursor.execute(sql, (nombre, correo, hash_pw))
        self.conexion.commit()
        return self.cursor.lastrowid

    def login_usuario(self, correo, contrasena):
        """Verifica credenciales. Retorna (id_usuario, nombre) o None."""
        hash_pw = hashlib.sha256(contrasena.encode()).hexdigest()
        self.cursor.execute(
            """SELECT id_usuario, nombre FROM usuario
               WHERE correo = %s AND contrasena_hash = %s AND activo = TRUE""",
            (correo, hash_pw)
        )
        fila = self.cursor.fetchone()
        if fila:
            return fila["id_usuario"], fila["nombre"]
        return None

    # ____________________________________________________________
    # PARTIDA

    def crear_partida(self, id_usuario, id_modo=1):
        """Crea partida en estado 'en_curso'. Retorna id_partida."""
        sql = """
            INSERT INTO partida (fecha_partida, estado, id_usuario, id_modo)
            VALUES (NOW(), 'en_curso', %s, %s)
        """
        self.cursor.execute(sql, (id_usuario, id_modo))
        self.conexion.commit()
        return self.cursor.lastrowid

    def finalizar_partida(self, id_partida):
        """Marca la partida como finalizada."""
        self.cursor.execute(
            "UPDATE partida SET estado = 'finalizada' WHERE id_partida = %s",
            (id_partida,)
        )
        self.conexion.commit()

    def abandonar_partida(self, id_partida):
        """Marca la partida como abandonada."""
        self.cursor.execute(
            "UPDATE partida SET estado = 'abandonada' WHERE id_partida = %s",
            (id_partida,)
        )
        self.conexion.commit()

    # ____________________________________________________________
    # PUNTAJE

    def guardar_puntaje(self, id_partida, puntos, tiros):
        """Guarda el puntaje final. Retorna id_puntaje."""
        sql = """
            INSERT INTO puntaje (puntos, tiros, id_partida)
            VALUES (%s, %s, %s)
        """
        self.cursor.execute(sql, (puntos, tiros, id_partida))
        self.conexion.commit()
        return self.cursor.lastrowid

    # ____________________________________________________________
    # RANKING

    def actualizar_ranking(self, id_usuario, id_modo, id_puntaje, puntos_nuevos):
        """Inserta o actualiza el ranking. Solo actualiza si el puntaje es mayor."""
        self.cursor.execute(
            """SELECT r.id_ranking, p.puntos
               FROM ranking r
               JOIN puntaje p ON r.id_puntaje = p.id_puntaje
               WHERE r.id_usuario = %s AND r.id_modo = %s""",
            (id_usuario, id_modo)
        )
        existente = self.cursor.fetchone()

        if not existente:
            self.cursor.execute(
                """INSERT INTO ranking (fecha_ultima_partida, id_usuario, id_modo, id_puntaje)
                   VALUES (NOW(), %s, %s, %s)""",
                (id_usuario, id_modo, id_puntaje)
            )
        else:
            if puntos_nuevos > existente["puntos"]:
                self.cursor.execute(
                    """UPDATE ranking
                       SET id_puntaje = %s, fecha_ultima_partida = NOW()
                       WHERE id_usuario = %s AND id_modo = %s""",
                    (id_puntaje, id_usuario, id_modo)
                )
        self.conexion.commit()

    def obtener_ranking(self, id_modo=1, limite=10):
        """Retorna el ranking de un modo ordenado por puntos DESC."""
        sql = """
            SELECT u.nombre, p.puntos, p.tiros, r.fecha_ultima_partida
            FROM ranking r
            JOIN usuario u ON r.id_usuario = u.id_usuario
            JOIN puntaje p ON r.id_puntaje = p.id_puntaje
            WHERE r.id_modo = %s
            ORDER BY p.puntos DESC
            LIMIT %s
        """
        self.cursor.execute(sql, (id_modo, limite))
        return self.cursor.fetchall()
