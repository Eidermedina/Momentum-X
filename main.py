
import pymysql
import hashlib
from pydantic import BaseModel
from typing import List
from datetime import datetime
from pymysql.cursors import DictCursor
from fastapi import FastAPI, HTTPException

DB_HOST  = "localhost"
DB_NAME  = "momentumbase"
DB_USER  = "juan"
DB_PASWD = "12345"

cc = pymysql.connect(
    host        = DB_HOST,
    user        = DB_USER,
    password    = DB_PASWD,
    database    = DB_NAME,
    cursorclass = DictCursor
)
cursor_obj = cc.cursor()

app = FastAPI()

class Juego(BaseModel):
    id_juego: int
    nombre: str
    descripcion: str | None = None
    version: str
    licencia: str


class Modo(BaseModel):
    id_modo: int
    nombre: str
    descripcion: str | None = None
    activo: bool
    id_juego: int
    nombre_juego: str | None = None


class Usuario(BaseModel):
    id_usuario: int
    nombre: str
    correo: str
    fecha_registro: datetime
    activo: bool


class Partida(BaseModel):
    id_partida: int
    fecha_partida: datetime
    estado: str
    id_usuario: int
    id_modo: int
    nombre_usuario: str | None = None
    nombre_modo: str | None = None


class Puntaje(BaseModel):
    id_puntaje: int
    puntos: int
    tiros: int
    id_partida: int
    nombre_usuario: str | None = None
    nombre_modo: str | None = None


class Ranking(BaseModel):
    id_ranking: int
    fecha_ultima_partida: datetime
    usuario: str
    modo: str
    puntos: int
    tiros: int
    
@app.get("/")
async def root():
    return {"message": "API MomentumX funcionando"}

#Ruta para crear juego
@app.post("/insert/juego", tags=["Juego"])
async def insert_juego(nombre: str, descripcion: str, version: str, licencia: str):
    sql = "INSERT INTO juego (nombre, descripcion, version, licencia) VALUES ('" + \
        nombre + "','" + descripcion + "','" + version + "','" + licencia + "')"
    cursor_obj.execute(sql)
    cc.commit()
    return {"mensaje": "Juego creado"}

#Ruta para obtener informacion de un juego
@app.get("/select/juego", tags=["Juego"], response_model=List[Juego])
async def select_juegos():
    cursor_obj.execute("SELECT * FROM juego ORDER BY id_juego")
    return cursor_obj.fetchall()

#Ruta para obtener informacion de un juego por (id)
@app.get("/select/juego/{id}", tags=["Juego"])
async def select_juego(id: int):
    cursor_obj.execute("SELECT * FROM juego WHERE id_juego = " + str(id))
    row = cursor_obj.fetchone()
    if not row:
        raise HTTPException(status_code=404, detail="Juego no encontrado")
    return row

#Ruta para actualizar informacion de un juego
@app.put("/update/juego/{id}", tags=["Juego"])
async def update_juego(id: int, nombre: str, descripcion: str, version: str, licencia: str):
    cursor_obj.execute("SELECT id_juego FROM juego WHERE id_juego = " + str(id))
    if not cursor_obj.fetchone():
        raise HTTPException(status_code=404, detail="Juego no encontrado")
    sql = "UPDATE juego SET nombre='" + nombre + "', descripcion='" + descripcion + \
        "', version='" + version + "', licencia='" + licencia + \
        "' WHERE id_juego=" + str(id)
    cursor_obj.execute(sql)
    cc.commit()
    return {"mensaje": "Juego actualizado"}

#Ruta para eliminar un juego
@app.delete("/delete/juego/{id}", tags=["Juego"])
async def delete_juego(id: int):
    cursor_obj.execute("SELECT id_juego FROM juego WHERE id_juego = " + str(id))
    if not cursor_obj.fetchone():
        raise HTTPException(status_code=404, detail="Juego no encontrado")
    cursor_obj.execute("DELETE FROM juego WHERE id_juego = " + str(id))
    cc.commit()
    return {"mensaje": "Juego eliminado"}

#Ruta para insertar un modo
@app.post("/insert/modo", tags=["Modo"])
async def insert_modo(nombre: str, descripcion: str, activo: bool, id_juego: int):
    cursor_obj.execute("SELECT id_juego FROM juego WHERE id_juego = " + str(id_juego))
    if not cursor_obj.fetchone():
        raise HTTPException(status_code=404, detail="Juego no encontrado")
    sql = "INSERT INTO modo_juego (nombre, descripcion, activo, id_juego) VALUES ('" + \
        nombre + "','" + descripcion + "'," + str(int(activo)) + "," + str(id_juego) + ")"
    cursor_obj.execute(sql)
    cc.commit()
    return {"mensaje": "Modo creado"}

#Ruta para obtener informacion de un modo
@app.get("/select/modo", tags=["Modo"], response_model=List[Modo])
async def select_modos():
    cursor_obj.execute("""
        SELECT mj.*, j.nombre AS nombre_juego
        FROM modo_juego mj
        JOIN juego j ON mj.id_juego = j.id_juego
        ORDER BY mj.id_modo
    """)
    return cursor_obj.fetchall()

#Ruta para obtener informacion de un modo (id)
@app.get("/select/modo/{id}", tags=["Modo"])
async def select_modo(id: int):
    cursor_obj.execute("""
        SELECT mj.*, j.nombre AS nombre_juego
        FROM modo_juego mj
        JOIN juego j ON mj.id_juego = j.id_juego
        WHERE mj.id_modo = """ + str(id))
    row = cursor_obj.fetchone()
    if not row:
        raise HTTPException(status_code=404, detail="Modo no encontrado")
    return row

#Ruta para actualizar informacion de un modo
@app.put("/update/modo/{id}", tags=["Modo"])
async def update_modo(id: int, nombre: str, descripcion: str, activo: bool):
    cursor_obj.execute("SELECT id_modo FROM modo_juego WHERE id_modo = " + str(id))
    if not cursor_obj.fetchone():
        raise HTTPException(status_code=404, detail="Modo no encontrado")
    sql = "UPDATE modo_juego SET nombre='" + nombre + "', descripcion='" + descripcion + \
        "', activo=" + str(int(activo)) + " WHERE id_modo=" + str(id)
    cursor_obj.execute(sql)
    cc.commit()
    return {"mensaje": "Modo actualizado"}

#Ruta para eliminar un modo
@app.delete("/delete/modo/{id}", tags=["Modo"])
async def delete_modo(id: int):
    cursor_obj.execute("SELECT id_modo FROM modo_juego WHERE id_modo = " + str(id))
    if not cursor_obj.fetchone():
        raise HTTPException(status_code=404, detail="Modo no encontrado")
    cursor_obj.execute("DELETE FROM modo_juego WHERE id_modo = " + str(id))
    cc.commit()
    return {"mensaje": "Modo eliminado"}

#Ruta para insertar un usuario
@app.post("/insert/usuario", tags=["Usuario"])
async def insert_usuario(nombre: str, correo: str, contrasena_hash: str, activo: bool = True):
    cursor_obj.execute("SELECT id_usuario FROM usuario WHERE correo = '" + correo + "'")
    if cursor_obj.fetchone():
        raise HTTPException(status_code=400, detail="El correo ya está registrado")
    
    hash_pw = hashlib.sha256(contrasena_hash.encode()).hexdigest()
    
    sql = "INSERT INTO usuario (nombre, correo, contrasena_hash, fecha_registro, activo) VALUES ('" + \
        nombre + "','" + correo + "','" + hash_pw + "', NOW()," + str(int(activo)) + ")"
    cursor_obj.execute(sql)
    cc.commit()
    return {"mensaje": "Usuario creado"}

#Ruta para obtener informacion de un usuario
@app.get("/select/usuario", tags=["Usuario"], response_model=List[Usuario])
async def select_usuarios():
    cursor_obj.execute("SELECT id_usuario, nombre, correo, fecha_registro, activo FROM usuario ORDER BY id_usuario")
    return cursor_obj.fetchall()

#Ruta para obtener informacion de un usuario (id)
@app.get("/select/usuario/{id}", tags=["Usuario"])
async def select_usuario(id: int):
    cursor_obj.execute(
        "SELECT id_usuario, nombre, correo, fecha_registro, activo FROM usuario WHERE id_usuario = " + str(id)
    )
    row = cursor_obj.fetchone()
    if not row:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")
    return row

#Ruta para actualizar informacion de un usuario
@app.put("/update/usuario/{id}", tags=["Usuario"])
async def update_usuario(id: int, nombre: str, correo: str, activo: bool):
    cursor_obj.execute("SELECT id_usuario FROM usuario WHERE id_usuario = " + str(id))
    if not cursor_obj.fetchone():
        raise HTTPException(status_code=404, detail="Usuario no encontrado")
    sql = "UPDATE usuario SET nombre='" + nombre + "', correo='" + correo + \
        "', activo=" + str(int(activo)) + " WHERE id_usuario=" + str(id)
    cursor_obj.execute(sql)
    cc.commit()
    return {"mensaje": "Usuario actualizado"}

#Ruta para eliminar un usuario
@app.delete("/delete/usuario/{id}", tags=["Usuario"])
async def delete_usuario(id: int):
    cursor_obj.execute("SELECT id_usuario FROM usuario WHERE id_usuario = " + str(id))
    if not cursor_obj.fetchone():
        raise HTTPException(status_code=404, detail="Usuario no encontrado")
    cursor_obj.execute("DELETE FROM usuario WHERE id_usuario = " + str(id))
    cc.commit()
    return {"mensaje": "Usuario eliminado"}

#Ruta para insertar una partida
@app.post("/insert/partida", tags=["Partida"])
async def insert_partida(id_usuario: int, id_modo: int):
    cursor_obj.execute("SELECT id_usuario FROM usuario WHERE id_usuario = " + str(id_usuario))
    if not cursor_obj.fetchone():
        raise HTTPException(status_code=404, detail="Usuario no encontrado")
    cursor_obj.execute("SELECT id_modo FROM modo_juego WHERE id_modo = " + str(id_modo))
    if not cursor_obj.fetchone():
        raise HTTPException(status_code=404, detail="Modo no encontrado")
    sql = "INSERT INTO partida (fecha_partida, estado, id_usuario, id_modo) VALUES (NOW(), 'en_curso'," + \
        str(id_usuario) + "," + str(id_modo) + ")"
    cursor_obj.execute(sql)
    cc.commit()
    return {"mensaje": "Partida creada"}

#Ruta para obtener informacion de una partida
@app.get("/select/partida", tags=["Partida"], response_model=List[Partida])
async def select_partidas():
    cursor_obj.execute("""
        SELECT p.*, u.nombre AS nombre_usuario, mj.nombre AS nombre_modo
        FROM partida p
        JOIN usuario    u  ON p.id_usuario = u.id_usuario
        JOIN modo_juego mj ON p.id_modo    = mj.id_modo
        ORDER BY p.id_partida DESC
    """)
    return cursor_obj.fetchall()

#Ruta para obtener informacion de una partida (id)
@app.get("/select/partida/{id}", tags=["Partida"])
async def select_partida(id: int):
    cursor_obj.execute("""
        SELECT p.*, u.nombre AS nombre_usuario, mj.nombre AS nombre_modo
        FROM partida p
        JOIN usuario    u  ON p.id_usuario = u.id_usuario
        JOIN modo_juego mj ON p.id_modo    = mj.id_modo
        WHERE p.id_partida = """ + str(id))
    row = cursor_obj.fetchone()
    if not row:
        raise HTTPException(status_code=404, detail="Partida no encontrada")
    return row

#Ruta para actualizar informacion de una partida
@app.put("/update/partida/{id}", tags=["Partida"])
async def update_partida(id: int, estado: str):
    if estado not in ("en_curso", "finalizada", "abandonada"):
        raise HTTPException(status_code=400, detail="Estado inválido. Use: en_curso, finalizada, abandonada")
    cursor_obj.execute("SELECT id_partida FROM partida WHERE id_partida = " + str(id))
    if not cursor_obj.fetchone():
        raise HTTPException(status_code=404, detail="Partida no encontrada")
    cursor_obj.execute("UPDATE partida SET estado='" + estado + "' WHERE id_partida=" + str(id))
    cc.commit()
    return {"mensaje": "Partida actualizada"}

#Ruta para eliminar una partida
@app.delete("/delete/partida/{id}", tags=["Partida"])
async def delete_partida(id: int):
    cursor_obj.execute("SELECT id_partida FROM partida WHERE id_partida = " + str(id))
    if not cursor_obj.fetchone():
        raise HTTPException(status_code=404, detail="Partida no encontrada")
    cursor_obj.execute("DELETE FROM partida WHERE id_partida = " + str(id))
    cc.commit()
    return {"mensaje": "Partida eliminada"}

#Ruta para insertar un puntaje
@app.post("/insert/puntaje", tags=["Puntaje"])
async def insert_puntaje(puntos: int, tiros: int, id_partida: int):
    cursor_obj.execute("SELECT id_partida FROM partida WHERE id_partida = " + str(id_partida))
    if not cursor_obj.fetchone():
        raise HTTPException(status_code=404, detail="Partida no encontrada")
    cursor_obj.execute("SELECT id_puntaje FROM puntaje WHERE id_partida = " + str(id_partida))
    if cursor_obj.fetchone():
        raise HTTPException(status_code=400, detail="La partida ya tiene un puntaje registrado")
    sql = "INSERT INTO puntaje (puntos, tiros, id_partida) VALUES (" + \
        str(puntos) + "," + str(tiros) + "," + str(id_partida) + ")"
    cursor_obj.execute(sql)
    cc.commit()
    cursor_obj.execute("UPDATE partida SET estado='finalizada' WHERE id_partida=" + str(id_partida))
    cc.commit()
    return {"mensaje": "Puntaje registrado"}

#Ruta para obtener informacion de un puntaje
@app.get("/select/puntaje", tags=["Puntaje"], response_model=List[Puntaje])
async def select_puntajes():
    cursor_obj.execute("""
        SELECT pt.*, u.nombre AS nombre_usuario, mj.nombre AS nombre_modo
        FROM puntaje pt
        JOIN partida    p  ON pt.id_partida = p.id_partida
        JOIN usuario    u  ON p.id_usuario  = u.id_usuario
        JOIN modo_juego mj ON p.id_modo     = mj.id_modo
        ORDER BY pt.puntos DESC
    """)
    return cursor_obj.fetchall()
 
#Ruta para obtener informacion de un puntaje (id)
@app.get("/select/puntaje/{id}", tags=["Puntaje"])
async def select_puntaje(id: int):
    cursor_obj.execute("""
        SELECT pt.*, u.nombre AS nombre_usuario, mj.nombre AS nombre_modo
        FROM puntaje pt
        JOIN partida    p  ON pt.id_partida = p.id_partida
        JOIN usuario    u  ON p.id_usuario  = u.id_usuario
        JOIN modo_juego mj ON p.id_modo     = mj.id_modo
        WHERE pt.id_puntaje = """ + str(id))
    row = cursor_obj.fetchone()
    if not row:
        raise HTTPException(status_code=404, detail="Puntaje no encontrado")
    return row

#Ruta para actualizar informacion de un puntaje
@app.put("/update/puntaje/{id}", tags=["Puntaje"])
async def update_puntaje(id: int, puntos: int, tiros: int):
    cursor_obj.execute("SELECT id_puntaje FROM puntaje WHERE id_puntaje = " + str(id))
    if not cursor_obj.fetchone():
        raise HTTPException(status_code=404, detail="Puntaje no encontrado")
    sql = "UPDATE puntaje SET puntos=" + str(puntos) + ", tiros=" + str(tiros) + \
        " WHERE id_puntaje=" + str(id)
    cursor_obj.execute(sql)
    cc.commit()
    return {"mensaje": "Puntaje actualizado"}

#Ruta para eliminar un puntaje
@app.delete("/delete/puntaje/{id}", tags=["Puntaje"])
async def delete_puntaje(id: int):
    cursor_obj.execute("SELECT id_puntaje FROM puntaje WHERE id_puntaje = " + str(id))
    if not cursor_obj.fetchone():
        raise HTTPException(status_code=404, detail="Puntaje no encontrado")
    cursor_obj.execute("DELETE FROM puntaje WHERE id_puntaje = " + str(id))
    cc.commit()
    return {"mensaje": "Puntaje eliminado"}

#Ruta para insertar un ranking
@app.post("/insert/ranking", tags=["Ranking"])
async def insert_ranking(id_usuario: int, id_modo: int, id_puntaje: int):
    cursor_obj.execute("SELECT id_usuario FROM usuario WHERE id_usuario = " + str(id_usuario))
    if not cursor_obj.fetchone():
        raise HTTPException(status_code=404, detail="Usuario no encontrado")
    cursor_obj.execute("SELECT id_modo FROM modo_juego WHERE id_modo = " + str(id_modo))
    if not cursor_obj.fetchone():
        raise HTTPException(status_code=404, detail="Modo no encontrado")
    cursor_obj.execute("SELECT puntos FROM puntaje WHERE id_puntaje = " + str(id_puntaje))
    puntaje = cursor_obj.fetchone()
    if not puntaje:
        raise HTTPException(status_code=404, detail="Puntaje no encontrado")

    puntos_nuevos = puntaje["puntos"]

    cursor_obj.execute("""
        SELECT r.id_ranking, p.puntos AS mejor_puntos
        FROM ranking r
        JOIN puntaje p ON r.id_puntaje = p.id_puntaje
        WHERE r.id_usuario = """ + str(id_usuario) + " AND r.id_modo = " + str(id_modo))
    existente = cursor_obj.fetchone()

    if not existente:
        cursor_obj.execute(
            "INSERT INTO ranking (fecha_ultima_partida, id_usuario, id_modo, id_puntaje) VALUES (NOW()," +
            str(id_usuario) + "," + str(id_modo) + "," + str(id_puntaje) + ")"
        )
        cc.commit()
        return {"mensaje": "Ranking creado"}
    elif puntos_nuevos > existente["mejor_puntos"]:
        cursor_obj.execute(
            "UPDATE ranking SET id_puntaje=" + str(id_puntaje) +
            ", fecha_ultima_partida=NOW() WHERE id_usuario=" + str(id_usuario) +
            " AND id_modo=" + str(id_modo)
        )
        cc.commit()
        return {"mensaje": "Nuevo récord registrado"}
    else:
        return {"mensaje": "Puntaje no supera el récord actual"}

#Ruta para obtener informacion del ranking
@app.get("/select/ranking", tags=["Ranking"], response_model=List[Ranking])
async def select_ranking():
    cursor_obj.execute("""
        SELECT r.id_ranking, u.nombre AS usuario, mj.nombre AS modo,
               p.puntos, p.tiros, r.fecha_ultima_partida
        FROM ranking r
        JOIN usuario    u  ON r.id_usuario = u.id_usuario
        JOIN modo_juego mj ON r.id_modo    = mj.id_modo
        JOIN puntaje    p  ON r.id_puntaje = p.id_puntaje
        ORDER BY mj.nombre, p.puntos DESC
    """)
    return cursor_obj.fetchall()

#Ruta para obtener informacion del ranking (id)
@app.get("/select/ranking/{id_modo}", tags=["Ranking"])
async def select_ranking_por_modo(id_modo: int):
    cursor_obj.execute("SELECT id_modo FROM modo_juego WHERE id_modo = " + str(id_modo))
    if not cursor_obj.fetchone():
        raise HTTPException(status_code=404, detail="Modo no encontrado")
    cursor_obj.execute("""
        SELECT u.nombre AS usuario, p.puntos, p.tiros, r.fecha_ultima_partida
        FROM ranking r
        JOIN usuario u  ON r.id_usuario = u.id_usuario
        JOIN puntaje p  ON r.id_puntaje = p.id_puntaje
        WHERE r.id_modo = """ + str(id_modo) + " ORDER BY p.puntos DESC")
    return cursor_obj.fetchall()

#Ruta para actualizar informacion del ranking
@app.put("/update/ranking/{id}", tags=["Ranking"])
async def update_ranking(id: int, id_puntaje: int):
    cursor_obj.execute("SELECT id_ranking FROM ranking WHERE id_ranking = " + str(id))
    if not cursor_obj.fetchone():
        raise HTTPException(status_code=404, detail="Ranking no encontrado")
    cursor_obj.execute("SELECT id_puntaje FROM puntaje WHERE id_puntaje = " + str(id_puntaje))
    if not cursor_obj.fetchone():
        raise HTTPException(status_code=404, detail="Puntaje no encontrado")
    cursor_obj.execute(
        "UPDATE ranking SET id_puntaje=" + str(id_puntaje) +
        ", fecha_ultima_partida=NOW() WHERE id_ranking=" + str(id)
    )
    cc.commit()
    return {"mensaje": "Ranking actualizado"}

#Ruta para eliminar un ranking
@app.delete("/delete/ranking/{id}", tags=["Ranking"])
async def delete_ranking(id: int):
    cursor_obj.execute("SELECT id_ranking FROM ranking WHERE id_ranking = " + str(id))
    if not cursor_obj.fetchone():
        raise HTTPException(status_code=404, detail="Ranking no encontrado")
    cursor_obj.execute("DELETE FROM ranking WHERE id_ranking = " + str(id))
    cc.commit()
    return {"mensaje": "Ranking eliminado"}
