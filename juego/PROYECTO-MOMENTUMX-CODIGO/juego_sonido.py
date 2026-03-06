import pygame

class Sonidos:
    sonido_encestar = ''
    sonido_rebote = ''
    sonido_vida = ''
    canal = ''
    def __init__(self):
        self.sonido_encestar = pygame.mixer.Sound('audios/Audio_cestas.mp3')
        self.sonido_rebote = pygame.mixer.Sound('audios/Audio_rebote.mp3')
        self.sonido_vida = pygame.mixer.Sound('audios/Audio_vida.mp3')
        self.canal = pygame.mixer.Channel(0)

    def play_encestar(self): self.canal.play(self.sonido_encestar)
    def play_rebote(self): self.canal.play(self.sonido_rebote)
    def play_vida(self): self.canal.play(self.sonido_vida)