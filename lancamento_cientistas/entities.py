"""
Entidades desenháveis do jogo: Arqueiro, Flecha (wrapper visual do Projectile),
Obstáculo e Alvo (bolha da cientista).

Como não há imagens/sprites externos no projeto, tudo é desenhado com
primitivas do Pygame (retângulos, círculos, linhas), o que também facilita
ajustar cores e estilo depois.
"""

import pygame
from settings import (
    COLOR_ACCENT, COLOR_OBSTACLE, COLOR_TARGET, COLOR_TARGET_HIT,
    COLOR_WHITE, COLOR_BLACK, ARCHER_X, ARCHER_Y, GROUND_Y,
)
from physics import Projectile


class Archer:
    """Representa o atirador, fixo do lado esquerdo da tela."""

    def __init__(self, x=ARCHER_X, y=ARCHER_Y):
        self.x = x
        self.y = y
        self.width = 24
        self.height = 60

    def draw(self, surface, aim_angle_deg=45):
        # corpo simples
        body_rect = pygame.Rect(self.x - self.width // 2, self.y - self.height, self.width, self.height)
        pygame.draw.rect(surface, COLOR_WHITE, body_rect, border_radius=6)

        # "arco" indicando o ângulo de mira atual, só decorativo
        import math
        angle_rad = math.radians(aim_angle_deg)
        bow_len = 40
        end_x = self.x + bow_len * math.cos(angle_rad)
        end_y = (self.y - self.height // 2) - bow_len * math.sin(angle_rad)
        pygame.draw.line(
            surface, COLOR_ACCENT,
            (self.x, self.y - self.height // 2),
            (end_x, end_y), 4,
        )

    def get_launch_point(self):
        return self.x, self.y - self.height // 2


class Obstacle:
    """Bloco/parede vertical que a flecha precisa transpor."""

    def __init__(self, x, width, height):
        self.rect = pygame.Rect(x, GROUND_Y - height, width, height)

    def draw(self, surface):
        pygame.draw.rect(surface, COLOR_OBSTACLE, self.rect, border_radius=3)
        pygame.draw.rect(surface, COLOR_BLACK, self.rect, width=2, border_radius=3)

    def collides_with_point(self, px, py, radius=6):
        return self.rect.collidepoint(px, py) or self.rect.inflate(radius, radius).collidepoint(px, py)


class Target:
    """A bolha-alvo contendo o nome da cientista da rodada atual."""

    def __init__(self, x, y, name, radius=32):
        self.x = x
        self.y = y
        self.name = name
        self.radius = radius
        self.hit = False

    def draw(self, surface, font):
        color = COLOR_TARGET_HIT if self.hit else COLOR_TARGET
        pygame.draw.circle(surface, color, (self.x, self.y), self.radius)
        pygame.draw.circle(surface, COLOR_BLACK, (self.x, self.y), self.radius, width=2)

        # nome da cientista, quebrado em até duas linhas se necessário
        words = self.name.split(" ")
        line1 = words[0]
        line2 = " ".join(words[1:])
        text1 = font.render(line1, True, COLOR_WHITE)
        text2 = font.render(line2, True, COLOR_WHITE) if line2 else None

        surface.blit(text1, text1.get_rect(center=(self.x, self.y - 8)))
        if text2:
            surface.blit(text2, text2.get_rect(center=(self.x, self.y + 10)))

    def collides_with_point(self, px, py):
        dist_sq = (px - self.x) ** 2 + (py - self.y) ** 2
        return dist_sq <= self.radius ** 2


class Arrow:
    """Wrapper visual do Projectile: desenha a flecha e checa colisões a cada frame."""

    def __init__(self, origin_x_px, origin_y_px, angle_deg, v0):
        self.projectile = Projectile(origin_x_px, origin_y_px, angle_deg, v0)
        self.trail = []  # pontos já percorridos, para desenhar o rastro

    def update(self, dt):
        self.projectile.update(dt)
        pos = self.projectile.get_screen_pos()
        self.trail.append(pos)
        if len(self.trail) > 400:
            self.trail.pop(0)

    def get_pos(self):
        return self.projectile.get_screen_pos()

    def draw(self, surface):
        # rastro
        if len(self.trail) > 1:
            pygame.draw.lines(surface, (150, 160, 180), False, self.trail, 2)
        # flecha (um pequeno círculo + linha indicando direção)
        px, py = self.get_pos()
        pygame.draw.circle(surface, COLOR_ACCENT, (int(px), int(py)), 6)
