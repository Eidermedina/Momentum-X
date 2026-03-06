import pygame
import math
import random
import os
from conexion_db import ConexionDB

ANCHO, ALTO = 1000, 700
GRAVEDAD    = 0.5
ID_MODO     = 1
RADIO_BALON = 15   # radio real del balón (imagen es 30x30)

try:
    db = ConexionDB()
except Exception as e:
    raise RuntimeError(
        f"No se pudo conectar a la base de datos: {e}\n"
        "Verifica que XAMPP esté corriendo y que la BD 'momentumbase' exista.\n"
        "Usuario: juan | Contraseña: 12345"
    )

# ____________________________________________________________
class Canasta:

    def __init__(self, x, y, ancho=90, alto=52, grosor=4):
        self.x      = x
        self.y      = y
        self.ancho  = ancho
        self.alto   = alto
        self.grosor = grosor

        # Los 4 bordes físicos de la canasta
        self.borde_superior  = pygame.Rect(x,                    y,          ancho,  grosor)
        self.borde_inferior  = pygame.Rect(x,                    y + alto,   ancho,  grosor)
        self.poste_izquierdo = pygame.Rect(x,                    y,          grosor, alto)
        self.poste_derecho   = pygame.Rect(x + ancho - grosor,   y,          grosor, alto)

        ruta_imagen = os.path.join("img", "imagencanasta.02.png")
        self.imagen = pygame.image.load(ruta_imagen)
        self.imagen = pygame.transform.scale(self.imagen, (ancho + 60, alto + 80))

    def area_anotacion(self):
        """
        Zona de anotación: franja delgada justo DENTRO del borde superior.
        El balón solo anota si entra por arriba, no por los lados ni por abajo.
        """
        margen = self.grosor + 2
        return pygame.Rect(
            self.x + self.grosor + 2,   # dentro del poste izquierdo
            self.y + margen,            # justo debajo del borde superior
            self.ancho - self.grosor * 2 - 4,   # ancho interior
            RADIO_BALON + 4             # altura = solo una franja angosta
        )

# ____________________________________________________________
class Balon:

    def __init__(self, x, y, vel_x, vel_y):
        self.x     = x
        self.y     = y
        self.vel_x = vel_x
        self.vel_y = vel_y

        ruta_imagen = os.path.join("img", "imagenbalon.o2.png")
        self.imagen = pygame.image.load(ruta_imagen)
        self.imagen = pygame.transform.scale(self.imagen, (30, 30))

    def actualizar(self, gravedad):
        self.x     += self.vel_x
        self.y     += self.vel_y
        self.vel_y += gravedad

    def rect(self):
        """Rect del balón centrado en su posición."""
        return pygame.Rect(self.x - RADIO_BALON, self.y - RADIO_BALON,
                           RADIO_BALON * 2, RADIO_BALON * 2)

# ____________________________________________________________
class EstadoJuego:

    def __init__(self, id_usuario, id_partida):
        self.id_usuario    = id_usuario
        self.id_partida    = id_partida
        self.vida          = 5
        self.puntos        = 0
        self.tiros         = 0
        self.angulo        = 90
        self.fuerza        = 3
        self.balones       = []
        self.cestas        = [self.generar_canasta()]
        self.inicio_tiempo = pygame.time.get_ticks()

    def generar_canasta(self):
        x = random.choice([random.randint(100, 400), random.randint(600, 900)])
        y = random.randint(70, 500)
        return Canasta(x, y)

    def tipo_angulo(self):
        if self.angulo < 90:
            return "Ángulo agudo"
        elif self.angulo == 90:
            return "Ángulo recto"
        elif self.angulo < 180:
            return "Ángulo obtuso"
        else:
            return "Ángulo llano"

    def color_fuerza(self):
        f = self.fuerza
        if f < 7:
            return (0, 255, 0)
        elif 7 <= f <= 14:
            return (255, 255, 0)
        elif 15 <= f <= 22:
            return (255, 165, 0)
        else:
            return (255, 0, 0)

    def calcular_trayectoria(self, gravedad):
        puntos = []
        t = 0
        while t < 60:
            x = (self.fuerza * math.cos(math.radians(self.angulo))) * t
            y = (self.fuerza * math.sin(math.radians(self.angulo)) * t) - (0.5 * gravedad * t ** 2)
            puntos.append((x, y))
            t += 0.5
        return puntos

    def guardar_resultado(self, tiempo_agotado=False):
        id_puntaje = db.guardar_puntaje(self.id_partida, self.puntos, self.tiros)
        if tiempo_agotado:
            db.abandonar_partida(self.id_partida)
        else:
            db.finalizar_partida(self.id_partida)
        db.actualizar_ranking(self.id_usuario, ID_MODO, id_puntaje, self.puntos)
