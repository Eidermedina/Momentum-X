import pygame
import sys
import os
from juego_modelo import EstadoJuego, GRAVEDAD, db
from juego_vista import (cargar_imagenes, dibujar_fondo, dibujar_canon,
                          dibujar_trayectoria, dibujar_canastas, dibujar_balones,
                          dibujar_ui, pantalla_login, pantalla_resultado)
from juego_controlador import manejar_eventos, actualizar_balones
from juego_sonido import Sonidos
import os
# Cambiar el directorio de trabajo a donde está el script
os.chdir(os.path.dirname(os.path.abspath(__file__)))
pygame.init()

ANCHO, ALTO = 1000, 700
pantalla    = pygame.display.set_mode((ANCHO, ALTO))
pygame.display.set_caption("MOMENTUM X")
FPS = 60

# CORRECCIÓN: os.path.join para compatibilidad Windows/Linux/Mac
fondo_menu1 = pygame.image.load(os.path.join("img", "fondoinicio.png"))
fondo_menu1 = pygame.transform.scale(fondo_menu1, (ANCHO, ALTO))
fondo_menu2 = pygame.image.load(os.path.join("img", "fondominijuego.png"))
fondo_menu2 = pygame.transform.scale(fondo_menu2, (ANCHO, ALTO))

# ____________________________________________________________
def menu_principal():
    """Pantalla de bienvenida — primero pide login."""
    fuente_titulo = pygame.font.SysFont(None, 90)
    fuente_boton  = pygame.font.SysFont(None, 50)
    titulo        = fuente_titulo.render("MOMENTUM X", True, (255, 255, 255))

    boton_iniciar = pygame.Rect(400, 300, 200, 60)
    boton_salir   = pygame.Rect(400, 400, 200, 60)

    while True:
        pantalla.blit(fondo_menu1, (0, 0))
        pantalla.blit(titulo, (ANCHO // 2 - titulo.get_width() // 2, 150))
        pygame.draw.rect(pantalla, (50, 150, 250), boton_iniciar)
        pygame.draw.rect(pantalla, (200, 50, 50),  boton_salir)

        pantalla.blit(fuente_boton.render("Iniciar", True, (255, 255, 255)),
                      (boton_iniciar.x + 50, boton_iniciar.y + 10))
        pantalla.blit(fuente_boton.render("Salir",   True, (255, 255, 255)),
                      (boton_salir.x   + 50, boton_salir.y   + 10))

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if boton_iniciar.collidepoint(event.pos):
                    # — LOGIN antes de entrar a los minijuegos —
                    id_usuario, nombre = pantalla_login(pantalla, db)
                    menu_minijuegos(id_usuario, nombre)
                elif boton_salir.collidepoint(event.pos):
                    pygame.quit()
                    sys.exit()

        pygame.display.flip()
        pygame.time.Clock().tick(60)

# ____________________________________________________________
def menu_minijuegos(id_usuario, nombre):
    fuente_titulo2 = pygame.font.SysFont(None, 90)
    fuente_boton   = pygame.font.SysFont(None, 40)
    fuente_user    = pygame.font.SysFont(None, 32)

    titulo_y   = 150
    ancho_boton= 200
    alto_boton = 60
    margen_x   = (ANCHO - 2 * ancho_boton) // 3
    margen_y   = 100

    boton_1 = pygame.Rect(margen_x,                               titulo_y + margen_y,                         ancho_boton, alto_boton)
    boton_2 = pygame.Rect(margen_x + ancho_boton + margen_x,      titulo_y + margen_y,                         ancho_boton, alto_boton)
    boton_3 = pygame.Rect(margen_x,                               titulo_y + margen_y + alto_boton + margen_y, ancho_boton, alto_boton)
    boton_4 = pygame.Rect(margen_x + ancho_boton + margen_x,      titulo_y + margen_y + alto_boton + margen_y, ancho_boton, alto_boton)

    while True:
        pantalla.blit(fondo_menu2, (0, 0))

        titulo = fuente_titulo2.render("MINIJUEGOS", True, (255, 255, 255))
        pantalla.blit(titulo, (ANCHO // 2 - titulo.get_width() // 2, 150))

        # Mostrar usuario logueado
        pantalla.blit(fuente_user.render(f"👤 {nombre}", True, (200, 255, 200)), (20, 20))

        for boton, texto in [
            (boton_1, "MOMENTUM X"),
            (boton_2, "Próximo"),
            (boton_3, "Próximo"),
            (boton_4, "Próximo"),
        ]:
            pygame.draw.rect(pantalla, (50, 150, 250), boton)
            surf = fuente_boton.render(texto, True, (255, 255, 255))
            pantalla.blit(surf, (boton.x + (boton.width  - surf.get_width())  // 2,
                                 boton.y + (boton.height - surf.get_height()) // 2))

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if boton_1.collidepoint(event.pos):
                    jugar_baloncesto(id_usuario)
                elif boton_2.collidepoint(event.pos):
                    print("Juego 2 — próximamente")
                elif boton_3.collidepoint(event.pos):
                    print("Juego 3 — próximamente")
                elif boton_4.collidepoint(event.pos):
                    print("Juego 4 — próximamente")

        pygame.display.flip()
        pygame.time.Clock().tick(60)

# ____________________________________________________________
def jugar_baloncesto(id_usuario):
    """Loop principal del minijuego de baloncesto."""
    cancha  = cargar_imagenes()
    reloj   = pygame.time.Clock()
    sonidos = Sonidos()

    # Crear partida en la BD al iniciar
    id_partida = db.crear_partida(id_usuario, id_modo=1)
    estado     = EstadoJuego(id_usuario, id_partida)

    TIEMPO_LIMITE = 2 * 60 * 1000  # 2 minutos en ms

    jugando = True
    while jugando:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                # Marcar como abandonada si cierra la ventana
                db.abandonar_partida(id_partida)
                pygame.quit()
                sys.exit()
            manejar_eventos(event, estado)

        tiempo_transcurrido = pygame.time.get_ticks() - estado.inicio_tiempo
        tiempo_agotado      = tiempo_transcurrido > TIEMPO_LIMITE

        if estado.vida <= 0 or tiempo_agotado:
            # Guardar resultado y mostrar pantalla final
            estado.guardar_resultado(tiempo_agotado=tiempo_agotado)
            pantalla_resultado(pantalla, estado, db)
            jugando = False
            break

        actualizar_balones(estado, gravedad=GRAVEDAD, sonidos=sonidos)
        trayectoria = estado.calcular_trayectoria(gravedad=GRAVEDAD)

        dibujar_fondo(pantalla, cancha)
        dibujar_canon(pantalla, estado.angulo)
        dibujar_trayectoria(pantalla, trayectoria)
        dibujar_canastas(pantalla, estado.cestas)
        dibujar_balones(pantalla, estado.balones)
        dibujar_ui(pantalla, estado)

        pygame.display.flip()
        reloj.tick(FPS)

# ____________________________________________________________
if __name__ == "__main__":
    menu_principal()
