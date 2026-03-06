import pygame as py
import math as m
from juego_modelo import Balon, RADIO_BALON

# ____________________________________________________________
def manejar_eventos(event, estado):
    if event.type == py.KEYDOWN:
        if event.key == py.K_LEFT:
            estado.angulo = min(estado.angulo + 3, 180)
        elif event.key == py.K_RIGHT:
            estado.angulo = max(estado.angulo - 5, 0)
        elif event.key == py.K_SPACE:
            disparar_balon(estado)
        elif event.key == py.K_UP:
            estado.fuerza = min(estado.fuerza + 2, 30)
        elif event.key == py.K_DOWN:
            estado.fuerza = max(estado.fuerza - 1, 1)

# ____________________________________________________________
def disparar_balon(estado):
    rad   = m.radians(estado.angulo)
    vel_x =  estado.fuerza * m.cos(rad)
    vel_y = -estado.fuerza * m.sin(rad)
    estado.balones.append(Balon(500, 680, vel_x, vel_y))

# ____________________________________________________________
def _verificar_rebote(balon, canasta, sonidos):
    """
    Verifica colisión del balón con cada borde de la canasta
    y aplica el rebote físico correcto según la dirección de llegada.

    Regla:
      - El balón NUNCA anota por los lados ni por abajo: SIEMPRE rebota.
      - La anotación solo se detecta en actualizar_balones() mediante area_anotacion(),
        que es una franja interior DEBAJO del borde superior.

    Retorna True si hubo algún rebote.
    """
    rb = balon.rect()

    # ── Poste izquierdo ──────────────────────────────────────
    if rb.colliderect(canasta.poste_izquierdo):
        if balon.vel_x > 0:
            # Viene desde la izquierda → rebota hacia la izquierda
            balon.x     = canasta.poste_izquierdo.left - RADIO_BALON - 1
            balon.vel_x = -abs(balon.vel_x) * 0.75
        else:
            # Viene desde dentro → rebota hacia dentro
            balon.x     = canasta.poste_izquierdo.right + RADIO_BALON + 1
            balon.vel_x = abs(balon.vel_x) * 0.75
        sonidos.play_rebote()
        return True

    # ── Poste derecho ─────────────────────────────────────────
    if rb.colliderect(canasta.poste_derecho):
        if balon.vel_x < 0:
            # Viene desde la derecha → rebota hacia la derecha
            balon.x     = canasta.poste_derecho.right + RADIO_BALON + 1
            balon.vel_x = abs(balon.vel_x) * 0.75
        else:
            # Viene desde dentro → rebota hacia dentro
            balon.x     = canasta.poste_derecho.left - RADIO_BALON - 1
            balon.vel_x = -abs(balon.vel_x) * 0.75
        sonidos.play_rebote()
        return True

    # ── Borde superior ────────────────────────────────────────
    # Solo rebota si el centro del balón NO está dentro del hueco interior
    # (si estuviera dentro y bajando, area_anotacion() lo capturaría primero)
    if rb.colliderect(canasta.borde_superior):
        interior_x = (canasta.x + canasta.grosor + 2 <= balon.x <=
                       canasta.x + canasta.ancho - canasta.grosor - 2)
        if not interior_x or balon.vel_y < 0:
            # Golpea el marco lateral o viene subiendo → rebota
            if balon.vel_y > 0:
                balon.y     = canasta.borde_superior.top - RADIO_BALON - 1
                balon.vel_y = -abs(balon.vel_y) * 0.75
            else:
                balon.y     = canasta.borde_superior.bottom + RADIO_BALON + 1
                balon.vel_y = abs(balon.vel_y) * 0.75
            sonidos.play_rebote()
            return True

    # ── Borde inferior ────────────────────────────────────────
    if rb.colliderect(canasta.borde_inferior):
        if balon.vel_y < 0:
            balon.y     = canasta.borde_inferior.bottom + RADIO_BALON + 1
            balon.vel_y = abs(balon.vel_y) * 0.75
        else:
            balon.y     = canasta.borde_inferior.top - RADIO_BALON - 1
            balon.vel_y = -abs(balon.vel_y) * 0.75
        sonidos.play_rebote()
        return True

    return False

# ____________________________________________________________
def actualizar_balones(estado, gravedad, sonidos):
    for balon in estado.balones[:]:

        if balon not in estado.balones:
            continue

        balon.actualizar(gravedad)
        balon_eliminado = False

        # ── Anotación: SOLO bajando por la franja superior interior ──
        for canasta in estado.cestas[:]:
            zona = canasta.area_anotacion()
            if balon.vel_y > 0 and zona.collidepoint(balon.x, balon.y):
                estado.puntos += 1
                estado.tiros  += 1
                estado.balones.remove(balon)
                estado.cestas.remove(canasta)
                estado.cestas.append(estado.generar_canasta())
                sonidos.play_encestar()
                balon_eliminado = True
                break

        if balon_eliminado:
            continue

        # ── Rebotes ──────────────────────────────────────────
        for canasta in estado.cestas:
            if _verificar_rebote(balon, canasta, sonidos):
                break

        # ── Pérdida: balón sale por abajo ──────────────────────
        if balon in estado.balones and balon.y > 700:
            estado.vida  -= 1
            estado.tiros += 1
            estado.balones.remove(balon)
            sonidos.play_vida()
