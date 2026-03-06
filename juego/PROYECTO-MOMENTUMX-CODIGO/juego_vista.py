import pygame
import math as M
import os

ANCHO, ALTO = 1000, 700

# ____________________________________________________________
def cargar_imagenes():
    # CORRECCIÓN: os.path.join para compatibilidad Windows/Linux/Mac
    ruta = os.path.join("img", "imagencancha.o2.png")
    cancha = pygame.image.load(ruta)
    cancha = pygame.transform.scale(cancha, (ANCHO, ALTO))
    return cancha

# ____________________________________________________________
def dibujar_fondo(pantalla, cancha):
    pantalla.fill((255, 255, 255))
    pantalla.blit(cancha, (0, 0))

# ____________________________________________________________
def dibujar_canon(pantalla, angulo):
    centro   = (ANCHO // 2, 680)
    longitud = 70
    fin_x = centro[0] + longitud * M.cos(M.radians(angulo))
    fin_y = centro[1] - longitud * M.sin(M.radians(angulo))
    pygame.draw.circle(pantalla, (0, 0, 0), centro, 30)
    pygame.draw.line(pantalla, (255, 0, 0), centro, (fin_x, fin_y), 10)

# ____________________________________________________________
def dibujar_trayectoria(pantalla, trayectoria):
    for punto in trayectoria:
        pygame.draw.circle(pantalla, (0, 0, 255),
                           (int(punto[0] + 500 + 1), int(680 - punto[1])), 2)

# ____________________________________________________________
def dibujar_balones(pantalla, balones):
    for balon in balones:
        pantalla.blit(balon.imagen, (int(balon.x) - 10, int(balon.y) - 10))

# ____________________________________________________________
def dibujar_ui(pantalla, estado):
    font   = pygame.font.Font(None, 36)
    tiempo = (pygame.time.get_ticks() - estado.inicio_tiempo) // 1000
    minutos, segundos = divmod(tiempo, 60)

    textos = {
        "angulo":     f"Ángulo: {estado.angulo}°",
        "tipo_angulo": estado.tipo_angulo(),
        "fuerza":     f"Fuerza: {estado.fuerza}",
        "vida":       f"Vidas: {estado.vida}",
        "puntos":     f"Puntos: {estado.puntos}",
        "tiros":      f"Tiros: {estado.tiros}",
        "tiempo":     f"Tiempo: {minutos:02d}:{segundos:02d}"
    }

    pantalla.blit(font.render(textos["angulo"],      True, (255, 255, 255)), (10, 5))
    pantalla.blit(font.render(textos["tipo_angulo"], True, (255, 255, 255)), (10, 30))
    pantalla.blit(font.render(textos["vida"],        True, (255, 255, 255)), (880, 5))
    pantalla.blit(font.render(textos["puntos"],      True, (255, 255, 255)), (880, 30))
    pantalla.blit(font.render(textos["tiros"],       True, (255, 255, 255)), (880, 60))
    pantalla.blit(font.render(textos["tiempo"],      True, (255, 255, 255)), (650, 5))
    pygame.draw.rect(pantalla, estado.color_fuerza(), (10, 61, estado.fuerza * 6, 20))
    pygame.draw.rect(pantalla, (255, 255, 255), (10, 60, 180, 20), 1)
    pantalla.blit(font.render(textos["fuerza"],      True, (255, 255, 255)), (10, 60))

# ____________________________________________________________
def dibujar_canastas(pantalla, canastas):
    for canasta in canastas:
        pantalla.blit(canasta.imagen, (canasta.x - 30, canasta.y - 14))
        pygame.draw.rect(pantalla, (255, 0, 0), canasta.borde_superior)
        pygame.draw.rect(pantalla, (255, 0, 0), canasta.borde_inferior)
        pygame.draw.rect(pantalla, (255, 0, 0), canasta.poste_izquierdo)
        pygame.draw.rect(pantalla, (255, 0, 0), canasta.poste_derecho)

# ____________________________________________________________
def pantalla_login(pantalla, db):
    """
    Muestra el menú de Login / Registro.
    Retorna (id_usuario, nombre) cuando el usuario inicia sesión correctamente.
    """
    # CORRECCIÓN: os.path.join para compatibilidad Windows/Linux/Mac
    ruta_fondo = os.path.join("img", "fondologin.jpg")
    fondo = pygame.image.load(ruta_fondo)
    fondo = pygame.transform.scale(fondo, (ANCHO, ALTO))

    fuente_titulo = pygame.font.SysFont(None, 60)
    fuente_normal = pygame.font.SysFont(None, 36)
    fuente_small  = pygame.font.SysFont(None, 28)

    # Campos de texto
    campos       = {"correo": "", "contrasena": "", "nombre": ""}
    campo_activo = "correo"
    modo         = "login"   # "login" o "registro"
    mensaje      = ""

    # Rectángulos de los campos
    rect_correo    = pygame.Rect(ANCHO // 2 - 150, 280, 300, 36)
    rect_contrasena= pygame.Rect(ANCHO // 2 - 150, 340, 300, 36)
    rect_nombre    = pygame.Rect(ANCHO // 2 - 150, 220, 300, 36)

    boton_accion   = pygame.Rect(ANCHO // 2 - 100, 410, 200, 45)
    boton_cambiar  = pygame.Rect(ANCHO // 2 - 120, 470, 240, 35)

    reloj = pygame.time.Clock()

    while True:
        pantalla.blit(fondo, (0, 0))

        # Título
        label = "INICIAR SESIÓN" if modo == "login" else "REGISTRARSE"
        pantalla.blit(fuente_titulo.render(label, True, (255, 255, 255)),
                      (ANCHO // 2 - fuente_titulo.size(label)[0] // 2, 140))

        # Campo nombre (solo en registro)
        if modo == "registro":
            color_n = (255, 255, 0) if campo_activo == "nombre" else (200, 200, 200)
            pygame.draw.rect(pantalla, (30, 30, 30), rect_nombre)
            pygame.draw.rect(pantalla, color_n, rect_nombre, 2)
            pantalla.blit(fuente_small.render("Nombre:", True, (255, 255, 255)),
                          (rect_nombre.x, rect_nombre.y - 22))
            pantalla.blit(fuente_normal.render(campos["nombre"], True, (255, 255, 255)),
                          (rect_nombre.x + 6, rect_nombre.y + 6))

        # Campo correo
        color_c = (255, 255, 0) if campo_activo == "correo" else (200, 200, 200)
        pygame.draw.rect(pantalla, (30, 30, 30), rect_correo)
        pygame.draw.rect(pantalla, color_c, rect_correo, 2)
        pantalla.blit(fuente_small.render("Correo:", True, (255, 255, 255)),
                      (rect_correo.x, rect_correo.y - 22))
        pantalla.blit(fuente_normal.render(campos["correo"], True, (255, 255, 255)),
                      (rect_correo.x + 6, rect_correo.y + 6))

        # Campo contraseña (oculta con *)
        color_p = (255, 255, 0) if campo_activo == "contrasena" else (200, 200, 200)
        pygame.draw.rect(pantalla, (30, 30, 30), rect_contrasena)
        pygame.draw.rect(pantalla, color_p, rect_contrasena, 2)
        pantalla.blit(fuente_small.render("Contraseña:", True, (255, 255, 255)),
                      (rect_contrasena.x, rect_contrasena.y - 22))
        pantalla.blit(fuente_normal.render("*" * len(campos["contrasena"]), True, (255, 255, 255)),
                      (rect_contrasena.x + 6, rect_contrasena.y + 6))

        # Botón acción
        pygame.draw.rect(pantalla, (50, 150, 250), boton_accion)
        label_boton = "Ingresar" if modo == "login" else "Registrar"
        pantalla.blit(fuente_normal.render(label_boton, True, (255, 255, 255)),
                      (boton_accion.x + boton_accion.width // 2 - fuente_normal.size(label_boton)[0] // 2,
                       boton_accion.y + 10))

        # Botón cambiar modo
        pygame.draw.rect(pantalla, (80, 80, 80), boton_cambiar)
        label_cambiar = "¿No tienes cuenta? Regístrate" if modo == "login" else "¿Ya tienes cuenta? Inicia sesión"
        pantalla.blit(fuente_small.render(label_cambiar, True, (220, 220, 220)),
                      (boton_cambiar.x + 8, boton_cambiar.y + 8))

        # Mensaje de error / éxito
        if mensaje:
            color_msg = (255, 80, 80) if "error" in mensaje.lower() or "incorrecto" in mensaje.lower() or "existe" in mensaje.lower() else (80, 255, 80)
            pantalla.blit(fuente_small.render(mensaje, True, color_msg),
                          (ANCHO // 2 - fuente_small.size(mensaje)[0] // 2, 520))

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                raise SystemExit

            elif event.type == pygame.MOUSEBUTTONDOWN:
                # Seleccionar campo activo
                if rect_correo.collidepoint(event.pos):
                    campo_activo = "correo"
                elif rect_contrasena.collidepoint(event.pos):
                    campo_activo = "contrasena"
                elif modo == "registro" and rect_nombre.collidepoint(event.pos):
                    campo_activo = "nombre"

                # Botón acción
                elif boton_accion.collidepoint(event.pos):
                    if modo == "login":
                        resultado = db.login_usuario(campos["correo"], campos["contrasena"])
                        if resultado:
                            id_usuario, nombre = resultado
                            return id_usuario, nombre
                        else:
                            mensaje = "Correo o contraseña incorrectos"
                    else:
                        if not campos["nombre"] or not campos["correo"] or not campos["contrasena"]:
                            mensaje = "Error: completa todos los campos"
                        else:
                            id_nuevo = db.registrar_usuario(
                                campos["nombre"], campos["correo"], campos["contrasena"]
                            )
                            if id_nuevo:
                                mensaje = "Registro exitoso, ahora inicia sesión"
                                modo = "login"
                                campos = {"correo": campos["correo"], "contrasena": "", "nombre": ""}
                            else:
                                mensaje = "Error: el correo ya existe"

                # Botón cambiar modo
                elif boton_cambiar.collidepoint(event.pos):
                    modo    = "registro" if modo == "login" else "login"
                    campos  = {"correo": "", "contrasena": "", "nombre": ""}
                    mensaje = ""

            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_TAB:
                    # Ciclar entre campos
                    orden = (["nombre", "correo", "contrasena"]
                             if modo == "registro" else ["correo", "contrasena"])
                    idx = orden.index(campo_activo) if campo_activo in orden else 0
                    campo_activo = orden[(idx + 1) % len(orden)]
                elif event.key == pygame.K_BACKSPACE:
                    campos[campo_activo] = campos[campo_activo][:-1]
                elif event.key == pygame.K_RETURN:
                    # Simular clic en botón acción
                    if modo == "login":
                        resultado = db.login_usuario(campos["correo"], campos["contrasena"])
                        if resultado:
                            id_usuario, nombre = resultado
                            return id_usuario, nombre
                        else:
                            mensaje = "Correo o contraseña incorrectos"
                    else:
                        if not campos["nombre"] or not campos["correo"] or not campos["contrasena"]:
                            mensaje = "Error: completa todos los campos"
                        else:
                            id_nuevo = db.registrar_usuario(
                                campos["nombre"], campos["correo"], campos["contrasena"]
                            )
                            if id_nuevo:
                                mensaje = "Registro exitoso, ahora inicia sesión"
                                modo = "login"
                                campos = {"correo": campos["correo"], "contrasena": "", "nombre": ""}
                            else:
                                mensaje = "Error: el correo ya existe"
                else:
                    if len(campos[campo_activo]) < 50:
                        campos[campo_activo] += event.unicode

        pygame.display.flip()
        reloj.tick(60)

# ____________________________________________________________
def pantalla_resultado(pantalla, estado, db):
    """Muestra puntos, tiros y el ranking actual del modo."""
    # CORRECCIÓN: os.path.join para compatibilidad Windows/Linux/Mac
    ruta_fondo = os.path.join("img", "fondologin.jpg")
    fondo  = pygame.image.load(ruta_fondo)
    fondo  = pygame.transform.scale(fondo, (ANCHO, ALTO))
    fuente = pygame.font.SysFont(None, 48)
    small  = pygame.font.SysFont(None, 32)

    ranking = db.obtener_ranking(id_modo=1, limite=5)

    boton_salir = pygame.Rect(ANCHO // 2 - 100, 600, 200, 50)
    reloj = pygame.time.Clock()

    while True:
        pantalla.blit(fondo, (0, 0))

        pantalla.blit(fuente.render("¡Partida terminada!", True, (255, 255, 100)),
                      (ANCHO // 2 - 180, 60))
        pantalla.blit(fuente.render(f"Puntos: {estado.puntos}", True, (255, 255, 255)),
                      (ANCHO // 2 - 100, 130))
        pantalla.blit(fuente.render(f"Tiros:  {estado.tiros}",  True, (255, 255, 255)),
                      (ANCHO // 2 - 100, 180))

        # Ranking
        pantalla.blit(fuente.render("Top 5 Ranking", True, (255, 215, 0)),
                      (ANCHO // 2 - 150, 260))
        for i, fila in enumerate(ranking):
            # CORRECCIÓN: cursor es dictionary=True → acceder por clave, no por índice
            nombre  = fila["nombre"]
            pts     = fila["puntos"]
            tiros_r = fila["tiros"]
            texto = f"{i+1}. {nombre}  —  {pts} pts  ({tiros_r} tiros)"
            pantalla.blit(small.render(texto, True, (220, 220, 220)),
                          (ANCHO // 2 - 230, 320 + i * 40))

        pygame.draw.rect(pantalla, (200, 50, 50), boton_salir)
        pantalla.blit(fuente.render("Salir", True, (255, 255, 255)),
                      (boton_salir.x + 55, boton_salir.y + 10))

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                raise SystemExit
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if boton_salir.collidepoint(event.pos):
                    return
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    return

        pygame.display.flip()
        reloj.tick(60)
