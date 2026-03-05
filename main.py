# coding=utf-8

# ==============================
# IMPORTACIONES
# ==============================
import hashlib
import pymysql
from pymysql.cursors import DictCursor
from fastapi import FastAPI, HTTPException

# ==============================
# CONFIGURACIÓN BASE DE DATOS
# ==============================
DB_HOST  = "localhost"
DB_NAME  = "momentumxdb"
DB_USER  = "eiderusuario"
DB_PASWD = "123456"

# ==============================
# CONEXIÓN — se abre por petición
# ==============================
def get_cursor():
    """
    Abre una conexión fresca a la BD y retorna (conexion, cursor).
    Cada endpoint la llama, la usa y la cierra al terminar.
    """
    try:
        conn = pymysql.connect(
            host        = DB_HOST,
            user        = DB_USER,
            password    = DB_PASWD,
            database    = DB_NAME,
            cursorclass = DictCursor
        )
        return conn, conn.cursor()
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error de conexión a la BD: {str(e)}")

# ==============================
# CREAR API
# ==============================
app = FastAPI()

@app.get("/")
async def root():
    return {"message": "API MomentumX funcionando 🚀"}


# =========================================================
# ======================== JUEGO ==========================
# =========================================================

@app.post("/juego")
async def crear_juego(nombre: str, descripcion: str, version: str, licencia: str):
    conn, cur = get_cursor()
    try:
        cur.execute(
            "INSERT INTO juego (nombre, descripcion, version, licencia) VALUES (%s, %s, %s, %s)",
            (nombre, descripcion, version, licencia)
        )
        conn.commit()
        return {"mensaje": "Juego creado", "id": cur.lastrowid}
    finally:
        cur.close()
        conn.close()

@app.get("/juego")
async def listar_juegos():
    conn, cur = get_cursor()
    try:
        cur.execute("SELECT * FROM juego")
        return cur.fetchall()
    finally:
        cur.close()
        conn.close()

@app.get("/juego/{id}")
async def obtener_juego(id: int):
    conn, cur = get_cursor()
    try:
        cur.execute("SELECT * FROM juego WHERE id_juego = %s", (id,))
        juego = cur.fetchone()
        if not juego:
            raise HTTPException(status_code=404, detail="Juego no encontrado")
        return juego
    finally:
        cur.close()
        conn.close()

@app.put("/juego/{id}")
async def actualizar_juego(id: int, nombre: str, descripcion: str, version: str, licencia: str):
    conn, cur = get_cursor()
    try:
        cur.execute("SELECT id_juego FROM juego WHERE id_juego = %s", (id,))
        if not cur.fetchone():
            raise HTTPException(status_code=404, detail="Juego no encontrado")
        cur.execute(
            "UPDATE juego SET nombre=%s, descripcion=%s, version=%s, licencia=%s WHERE id_juego=%s",
            (nombre, descripcion, version, licencia, id)
        )
        conn.commit()
        return {"mensaje": "Juego actualizado"}
    finally:
        cur.close()
        conn.close()

@app.delete("/juego/{id}")
async def eliminar_juego(id: int):
    conn, cur = get_cursor()
    try:
        cur.execute("SELECT id_juego FROM juego WHERE id_juego = %s", (id,))
        if not cur.fetchone():
            raise HTTPException(status_code=404, detail="Juego no encontrado")
        cur.execute("DELETE FROM juego WHERE id_juego = %s", (id,))
        conn.commit()
        return {"mensaje": "Juego eliminado"}
    finally:
        cur.close()
        conn.close()


# =========================================================
# ======================= MODO JUEGO ======================
# =========================================================

@app.post("/modo")
async def crear_modo(nombre: str, descripcion: str, activo: bool, id_juego: int):
    conn, cur = get_cursor()
    try:
        cur.execute("SELECT id_juego FROM juego WHERE id_juego = %s", (id_juego,))
        if not cur.fetchone():
            raise HTTPException(status_code=404, detail="Juego no encontrado")
        cur.execute(
            "INSERT INTO modo_juego (nombre, descripcion, activo, id_juego) VALUES (%s, %s, %s, %s)",
            (nombre, descripcion, activo, id_juego)
        )
        conn.commit()
        return {"mensaje": "Modo creado", "id": cur.lastrowid}
    finally:
        cur.close()
        conn.close()

@app.get("/modo")
async def listar_modos():
    conn, cur = get_cursor()
    try:
        cur.execute("""
            SELECT mj.*, j.nombre AS nombre_juego
            FROM modo_juego mj
            JOIN juego j ON mj.id_juego = j.id_juego
        """)
        return cur.fetchall()
    finally:
        cur.close()
        conn.close()

@app.get("/modo/{id}")
async def obtener_modo(id: int):
    conn, cur = get_cursor()
    try:
        cur.execute("""
            SELECT mj.*, j.nombre AS nombre_juego
            FROM modo_juego mj
            JOIN juego j ON mj.id_juego = j.id_juego
            WHERE mj.id_modo = %s
        """, (id,))
        modo = cur.fetchone()
        if not modo:
            raise HTTPException(status_code=404, detail="Modo no encontrado")
        return modo
    finally:
        cur.close()
        conn.close()

@app.put("/modo/{id}")
async def actualizar_modo(id: int, nombre: str, descripcion: str, activo: bool):
    conn, cur = get_cursor()
    try:
        cur.execute("SELECT id_modo FROM modo_juego WHERE id_modo = %s", (id,))
        if not cur.fetchone():
            raise HTTPException(status_code=404, detail="Modo no encontrado")
        cur.execute(
            "UPDATE modo_juego SET nombre=%s, descripcion=%s, activo=%s WHERE id_modo=%s",
            (nombre, descripcion, activo, id)
        )
        conn.commit()
        return {"mensaje": "Modo actualizado"}
    finally:
        cur.close()
        conn.close()

@app.delete("/modo/{id}")
async def eliminar_modo(id: int):
    conn, cur = get_cursor()
    try:
        cur.execute("SELECT id_modo FROM modo_juego WHERE id_modo = %s", (id,))
        if not cur.fetchone():
            raise HTTPException(status_code=404, detail="Modo no encontrado")
        cur.execute("DELETE FROM modo_juego WHERE id_modo = %s", (id,))
        conn.commit()
        return {"mensaje": "Modo eliminado"}
    finally:
        cur.close()
        conn.close()


# =========================================================
# ======================== USUARIO ========================
# =========================================================

@app.post("/usuario")
async def crear_usuario(nombre: str, correo: str, contrasena: str, activo: bool = True):
    """
    CORRECCIÓN: el parámetro ahora se llama 'contrasena' (texto plano).
    La API hashea con SHA-256 antes de guardar, igual que el juego.
    """
    conn, cur = get_cursor()
    try:
        cur.execute("SELECT id_usuario FROM usuario WHERE correo = %s", (correo,))
        if cur.fetchone():
            raise HTTPException(status_code=400, detail="El correo ya está registrado")
        # Hashear la contraseña con SHA-256
        contrasena_hash = hashlib.sha256(contrasena.encode()).hexdigest()
        cur.execute(
            "INSERT INTO usuario (nombre, correo, contrasena_hash, fecha_registro, activo) VALUES (%s, %s, %s, NOW(), %s)",
            (nombre, correo, contrasena_hash, activo)
        )
        conn.commit()
        return {"mensaje": "Usuario creado", "id": cur.lastrowid}
    finally:
        cur.close()
        conn.close()

@app.get("/usuario")
async def listar_usuarios():
    conn, cur = get_cursor()
    try:
        # Nunca se devuelve contrasena_hash
        cur.execute("SELECT id_usuario, nombre, correo, fecha_registro, activo FROM usuario")
        return cur.fetchall()
    finally:
        cur.close()
        conn.close()

@app.get("/usuario/{id}")
async def obtener_usuario(id: int):
    conn, cur = get_cursor()
    try:
        cur.execute(
            "SELECT id_usuario, nombre, correo, fecha_registro, activo FROM usuario WHERE id_usuario = %s", (id,)
        )
        usuario = cur.fetchone()
        if not usuario:
            raise HTTPException(status_code=404, detail="Usuario no encontrado")
        return usuario
    finally:
        cur.close()
        conn.close()

@app.put("/usuario/{id}")
async def actualizar_usuario(id: int, nombre: str, correo: str, activo: bool):
    conn, cur = get_cursor()
    try:
        cur.execute("SELECT id_usuario FROM usuario WHERE id_usuario = %s", (id,))
        if not cur.fetchone():
            raise HTTPException(status_code=404, detail="Usuario no encontrado")
        cur.execute(
            "UPDATE usuario SET nombre=%s, correo=%s, activo=%s WHERE id_usuario=%s",
            (nombre, correo, activo, id)
        )
        conn.commit()
        return {"mensaje": "Usuario actualizado"}
    finally:
        cur.close()
        conn.close()

@app.delete("/usuario/{id}")
async def eliminar_usuario(id: int):
    conn, cur = get_cursor()
    try:
        cur.execute("SELECT id_usuario FROM usuario WHERE id_usuario = %s", (id,))
        if not cur.fetchone():
            raise HTTPException(status_code=404, detail="Usuario no encontrado")
        cur.execute("DELETE FROM usuario WHERE id_usuario = %s", (id,))
        conn.commit()
        return {"mensaje": "Usuario eliminado"}
    finally:
        cur.close()
        conn.close()


# =========================================================
# ======================== PARTIDA ========================
# =========================================================

@app.post("/partida")
async def crear_partida(id_usuario: int, id_modo: int):
    conn, cur = get_cursor()
    try:
        cur.execute("SELECT id_usuario FROM usuario WHERE id_usuario = %s", (id_usuario,))
        if not cur.fetchone():
            raise HTTPException(status_code=404, detail="Usuario no encontrado")
        cur.execute("SELECT id_modo FROM modo_juego WHERE id_modo = %s", (id_modo,))
        if not cur.fetchone():
            raise HTTPException(status_code=404, detail="Modo no encontrado")
        cur.execute(
            "INSERT INTO partida (fecha_partida, estado, id_usuario, id_modo) VALUES (NOW(), 'en_curso', %s, %s)",
            (id_usuario, id_modo)
        )
        conn.commit()
        return {"mensaje": "Partida creada", "id": cur.lastrowid}
    finally:
        cur.close()
        conn.close()

@app.get("/partida")
async def listar_partidas():
    conn, cur = get_cursor()
    try:
        cur.execute("""
            SELECT p.*, u.nombre AS nombre_usuario, mj.nombre AS nombre_modo
            FROM partida p
            JOIN usuario    u  ON p.id_usuario = u.id_usuario
            JOIN modo_juego mj ON p.id_modo    = mj.id_modo
            ORDER BY p.id_partida DESC
        """)
        return cur.fetchall()
    finally:
        cur.close()
        conn.close()

@app.get("/partida/{id}")
async def obtener_partida(id: int):
    conn, cur = get_cursor()
    try:
        cur.execute("""
            SELECT p.*, u.nombre AS nombre_usuario, mj.nombre AS nombre_modo
            FROM partida p
            JOIN usuario    u  ON p.id_usuario = u.id_usuario
            JOIN modo_juego mj ON p.id_modo    = mj.id_modo
            WHERE p.id_partida = %s
        """, (id,))
        partida = cur.fetchone()
        if not partida:
            raise HTTPException(status_code=404, detail="Partida no encontrada")
        return partida
    finally:
        cur.close()
        conn.close()

@app.put("/partida/{id}")
async def actualizar_partida(id: int, estado: str):
    if estado not in ("en_curso", "finalizada", "abandonada"):
        raise HTTPException(status_code=400, detail="Estado inválido. Use: en_curso, finalizada, abandonada")
    conn, cur = get_cursor()
    try:
        cur.execute("SELECT id_partida FROM partida WHERE id_partida = %s", (id,))
        if not cur.fetchone():
            raise HTTPException(status_code=404, detail="Partida no encontrada")
        cur.execute("UPDATE partida SET estado=%s WHERE id_partida=%s", (estado, id))
        conn.commit()
        return {"mensaje": "Partida actualizada"}
    finally:
        cur.close()
        conn.close()

@app.delete("/partida/{id}")
async def eliminar_partida(id: int):
    conn, cur = get_cursor()
    try:
        cur.execute("SELECT id_partida FROM partida WHERE id_partida = %s", (id,))
        if not cur.fetchone():
            raise HTTPException(status_code=404, detail="Partida no encontrada")
        cur.execute("DELETE FROM partida WHERE id_partida = %s", (id,))
        conn.commit()
        return {"mensaje": "Partida eliminada"}
    finally:
        cur.close()
        conn.close()


# =========================================================
# ======================== PUNTAJE ========================
# =========================================================

@app.post("/puntaje")
async def crear_puntaje(puntos: int, tiros: int, id_partida: int):
    conn, cur = get_cursor()
    try:
        cur.execute("SELECT id_partida FROM partida WHERE id_partida = %s", (id_partida,))
        if not cur.fetchone():
            raise HTTPException(status_code=404, detail="Partida no encontrada")
        cur.execute("SELECT id_puntaje FROM puntaje WHERE id_partida = %s", (id_partida,))
        if cur.fetchone():
            raise HTTPException(status_code=400, detail="La partida ya tiene un puntaje registrado")
        cur.execute(
            "INSERT INTO puntaje (puntos, tiros, id_partida) VALUES (%s, %s, %s)",
            (puntos, tiros, id_partida)
        )
        conn.commit()
        id_puntaje = cur.lastrowid
        # Marcar partida como finalizada automáticamente
        cur.execute("UPDATE partida SET estado='finalizada' WHERE id_partida=%s", (id_partida,))
        conn.commit()
        return {"mensaje": "Puntaje registrado", "id": id_puntaje}
    finally:
        cur.close()
        conn.close()

@app.get("/puntaje")
async def listar_puntajes():
    conn, cur = get_cursor()
    try:
        cur.execute("""
            SELECT pt.*, u.nombre AS nombre_usuario, mj.nombre AS nombre_modo
            FROM puntaje pt
            JOIN partida    p  ON pt.id_partida = p.id_partida
            JOIN usuario    u  ON p.id_usuario  = u.id_usuario
            JOIN modo_juego mj ON p.id_modo     = mj.id_modo
            ORDER BY pt.puntos DESC
        """)
        return cur.fetchall()
    finally:
        cur.close()
        conn.close()

@app.get("/puntaje/{id}")
async def obtener_puntaje(id: int):
    conn, cur = get_cursor()
    try:
        cur.execute("""
            SELECT pt.*, u.nombre AS nombre_usuario, mj.nombre AS nombre_modo
            FROM puntaje pt
            JOIN partida    p  ON pt.id_partida = p.id_partida
            JOIN usuario    u  ON p.id_usuario  = u.id_usuario
            JOIN modo_juego mj ON p.id_modo     = mj.id_modo
            WHERE pt.id_puntaje = %s
        """, (id,))
        puntaje = cur.fetchone()
        if not puntaje:
            raise HTTPException(status_code=404, detail="Puntaje no encontrado")
        return puntaje
    finally:
        cur.close()
        conn.close()

@app.put("/puntaje/{id}")
async def actualizar_puntaje(id: int, puntos: int, tiros: int):
    conn, cur = get_cursor()
    try:
        cur.execute("SELECT id_puntaje FROM puntaje WHERE id_puntaje = %s", (id,))
        if not cur.fetchone():
            raise HTTPException(status_code=404, detail="Puntaje no encontrado")
        cur.execute(
            "UPDATE puntaje SET puntos=%s, tiros=%s WHERE id_puntaje=%s",
            (puntos, tiros, id)
        )
        conn.commit()
        return {"mensaje": "Puntaje actualizado"}
    finally:
        cur.close()
        conn.close()

@app.delete("/puntaje/{id}")
async def eliminar_puntaje(id: int):
    conn, cur = get_cursor()
    try:
        cur.execute("SELECT id_puntaje FROM puntaje WHERE id_puntaje = %s", (id,))
        if not cur.fetchone():
            raise HTTPException(status_code=404, detail="Puntaje no encontrado")
        cur.execute("DELETE FROM puntaje WHERE id_puntaje = %s", (id,))
        conn.commit()
        return {"mensaje": "Puntaje eliminado"}
    finally:
        cur.close()
        conn.close()


# =========================================================
# ======================== RANKING ========================
# =========================================================

@app.post("/ranking")
async def crear_o_actualizar_ranking(id_usuario: int, id_modo: int, id_puntaje: int):
    conn, cur = get_cursor()
    try:
        cur.execute("SELECT id_usuario FROM usuario WHERE id_usuario = %s", (id_usuario,))
        if not cur.fetchone():
            raise HTTPException(status_code=404, detail="Usuario no encontrado")
        cur.execute("SELECT id_modo FROM modo_juego WHERE id_modo = %s", (id_modo,))
        if not cur.fetchone():
            raise HTTPException(status_code=404, detail="Modo no encontrado")
        cur.execute("SELECT puntos FROM puntaje WHERE id_puntaje = %s", (id_puntaje,))
        puntaje = cur.fetchone()
        if not puntaje:
            raise HTTPException(status_code=404, detail="Puntaje no encontrado")

        puntos_nuevos = puntaje["puntos"]

        cur.execute("""
            SELECT r.id_ranking, p.puntos AS mejor_puntos
            FROM ranking r
            JOIN puntaje p ON r.id_puntaje = p.id_puntaje
            WHERE r.id_usuario = %s AND r.id_modo = %s
        """, (id_usuario, id_modo))
        existente = cur.fetchone()

        if not existente:
            cur.execute(
                "INSERT INTO ranking (fecha_ultima_partida, id_usuario, id_modo, id_puntaje) VALUES (NOW(), %s, %s, %s)",
                (id_usuario, id_modo, id_puntaje)
            )
            conn.commit()
            return {"mensaje": "Ranking creado"}
        elif puntos_nuevos > existente["mejor_puntos"]:
            cur.execute(
                "UPDATE ranking SET id_puntaje=%s, fecha_ultima_partida=NOW() WHERE id_usuario=%s AND id_modo=%s",
                (id_puntaje, id_usuario, id_modo)
            )
            conn.commit()
            return {"mensaje": "Nuevo récord registrado"}
        else:
            return {"mensaje": "Puntaje no supera el récord actual"}
    finally:
        cur.close()
        conn.close()

@app.get("/ranking")
async def listar_ranking():
    conn, cur = get_cursor()
    try:
        cur.execute("""
            SELECT r.id_ranking, u.nombre AS usuario, mj.nombre AS modo,
                   p.puntos, p.tiros, r.fecha_ultima_partida
            FROM ranking r
            JOIN usuario    u  ON r.id_usuario = u.id_usuario
            JOIN modo_juego mj ON r.id_modo    = mj.id_modo
            JOIN puntaje    p  ON r.id_puntaje = p.id_puntaje
            ORDER BY mj.nombre, p.puntos DESC
        """)
        return cur.fetchall()
    finally:
        cur.close()
        conn.close()

@app.get("/ranking/modo/{id_modo}")
async def ranking_por_modo(id_modo: int):
    """
    CORRECCIÓN: ruta cambiada a /ranking/modo/{id_modo} para evitar
    conflicto con /ranking/{id} (DELETE/PUT por id_ranking).
    """
    conn, cur = get_cursor()
    try:
        cur.execute("SELECT id_modo FROM modo_juego WHERE id_modo = %s", (id_modo,))
        if not cur.fetchone():
            raise HTTPException(status_code=404, detail="Modo no encontrado")
        cur.execute("""
            SELECT u.nombre AS usuario, p.puntos, p.tiros, r.fecha_ultima_partida
            FROM ranking r
            JOIN usuario u  ON r.id_usuario = u.id_usuario
            JOIN puntaje p  ON r.id_puntaje = p.id_puntaje
            WHERE r.id_modo = %s
            ORDER BY p.puntos DESC
        """, (id_modo,))
        return cur.fetchall()
    finally:
        cur.close()
        conn.close()

@app.get("/ranking/usuario/{id_usuario}")
async def ranking_por_usuario(id_usuario: int):
    """NUEVO: consulta todos los récords de un usuario en todos los modos."""
    conn, cur = get_cursor()
    try:
        cur.execute("SELECT id_usuario FROM usuario WHERE id_usuario = %s", (id_usuario,))
        if not cur.fetchone():
            raise HTTPException(status_code=404, detail="Usuario no encontrado")
        cur.execute("""
            SELECT mj.nombre AS modo, p.puntos, p.tiros, r.fecha_ultima_partida
            FROM ranking r
            JOIN modo_juego mj ON r.id_modo    = mj.id_modo
            JOIN puntaje    p  ON r.id_puntaje = p.id_puntaje
            WHERE r.id_usuario = %s
            ORDER BY p.puntos DESC
        """, (id_usuario,))
        return cur.fetchall()
    finally:
        cur.close()
        conn.close()

@app.put("/ranking/{id}")
async def actualizar_ranking(id: int, id_puntaje: int):
    conn, cur = get_cursor()
    try:
        cur.execute("SELECT id_ranking FROM ranking WHERE id_ranking = %s", (id,))
        if not cur.fetchone():
            raise HTTPException(status_code=404, detail="Ranking no encontrado")
        cur.execute("SELECT id_puntaje FROM puntaje WHERE id_puntaje = %s", (id_puntaje,))
        if not cur.fetchone():
            raise HTTPException(status_code=404, detail="Puntaje no encontrado")
        cur.execute(
            "UPDATE ranking SET id_puntaje=%s, fecha_ultima_partida=NOW() WHERE id_ranking=%s",
            (id_puntaje, id)
        )
        conn.commit()
        return {"mensaje": "Ranking actualizado"}
    finally:
        cur.close()
        conn.close()

@app.delete("/ranking/{id}")
async def eliminar_ranking(id: int):
    conn, cur = get_cursor()
    try:
        cur.execute("SELECT id_ranking FROM ranking WHERE id_ranking = %s", (id,))
        if not cur.fetchone():
            raise HTTPException(status_code=404, detail="Ranking no encontrado")
        cur.execute("DELETE FROM ranking WHERE id_ranking = %s", (id,))
        conn.commit()
        return {"mensaje": "Ranking eliminado"}
    finally:
        cur.close()
        conn.close()
