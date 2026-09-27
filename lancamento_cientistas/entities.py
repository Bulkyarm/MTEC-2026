"""
Entidades desenháveis do jogo: Arqueiro, Flecha (wrapper visual do Projectile),
Obstáculo e Alvo (bolha da cientista).

Como não há imagens/sprites externos no projeto, tudo é desenhado com
primitivas do Pygame (retângulos, círculos, linhas), o que também facilita
ajustar cores e estilo depois.
"""

import math
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
        head_center = (self.x, self.y - self.height - 15)
        pygame.draw.circle(surface, (224, 168, 126), head_center, 14)
        pygame.draw.circle(surface, COLOR_BLACK, head_center, 14, width=2)

        hair_points = [
            (self.x - 14, self.y - self.height - 17),
            (self.x - 9, self.y - self.height - 31),
            (self.x + 7, self.y - self.height - 30),
            (self.x + 15, self.y - self.height - 16),
        ]
        pygame.draw.polygon(surface, (75, 43, 34), hair_points)
        pygame.draw.line(surface, (235, 198, 157),
                         (self.x - 6, self.y - self.height - 15),
                         (self.x - 2, self.y - self.height - 15), 2)

        body_rect = pygame.Rect(self.x - self.width // 2, self.y - self.height, self.width, self.height)
        pygame.draw.rect(surface, (39, 104, 128), body_rect, border_radius=6)
        pygame.draw.rect(surface, (28, 67, 84), body_rect, width=2, border_radius=6)
        pygame.draw.line(surface, (76, 171, 172),
                         (self.x, body_rect.top + 5), (self.x, body_rect.bottom - 4), 3)
        pygame.draw.line(surface, (76, 171, 172),
                         (body_rect.left + 5, body_rect.top + 17),
                         (body_rect.right - 5, body_rect.top + 17), 2)

        pygame.draw.line(surface, (224, 168, 126),
                         (self.x - 9, body_rect.top + 18),
                         (self.x + 22, body_rect.top + 10), 7)
        pygame.draw.line(surface, (235, 198, 157),
                         (self.x + 18, body_rect.top + 10),
                         (self.x + 29, body_rect.top + 4), 5)

        pygame.draw.line(surface, (58, 42, 65),
                         (self.x - 7, self.y - 3), (self.x - 14, self.y + 18), 7)
        pygame.draw.line(surface, (58, 42, 65),
                         (self.x + 7, self.y - 3), (self.x + 14, self.y + 18), 7)
        pygame.draw.line(surface, (20, 20, 25),
                         (self.x - 20, self.y + 18), (self.x - 8, self.y + 18), 5)
        pygame.draw.line(surface, (20, 20, 25),
                         (self.x + 8, self.y + 18), (self.x + 20, self.y + 18), 5)

        angle_rad = math.radians(aim_angle_deg)
        hand_x = self.x + 29
        hand_y = self.y - self.height // 2 - 4
        bow_center = (hand_x, hand_y)
        bow_radius = 30
        bow_points = []
        for index in range(13):
            bow_angle = math.radians(-70 + index * (140 / 12)) + angle_rad - math.radians(45)
            bow_points.append((
                hand_x + bow_radius * math.cos(bow_angle),
                hand_y - bow_radius * math.sin(bow_angle),
            ))
        pygame.draw.lines(surface, (137, 79, 38), False, bow_points, 6)
        pygame.draw.lines(surface, (218, 139, 65), False, bow_points, 2)

        aim_end = (
            hand_x + 28 * math.cos(angle_rad),
            hand_y - 28 * math.sin(angle_rad),
        )
        pygame.draw.line(surface, (235, 220, 175), bow_points[0], bow_points[-1], 2)
        pygame.draw.line(surface, (235, 220, 175), bow_points[0], aim_end, 1)
        pygame.draw.line(surface, (235, 220, 175), aim_end, bow_points[-1], 1)

    def get_launch_point(self):
        return self.x, self.y - self.height // 2


class Obstacle:
    """Bloco/parede vertical que a flecha precisa transpor."""

    def __init__(self, x, y, width, height):
        self.rect = pygame.Rect(x, y, width, height)

    def draw(self, surface):
        pygame.draw.rect(surface, COLOR_OBSTACLE, self.rect, border_radius=3)
        pygame.draw.rect(surface, (151, 108, 76), self.rect.inflate(-5, -5), border_radius=2)
        brick_height = 18
        for row_y in range(self.rect.top + 8, self.rect.bottom, brick_height):
            pygame.draw.line(
                surface, (91, 61, 51),
                (self.rect.left + 3, row_y), (self.rect.right - 3, row_y), 2,
            )
            offset = 0 if ((row_y - self.rect.top) // brick_height) % 2 == 0 else 7
            for column_x in range(self.rect.left + 5 + offset, self.rect.right, 14):
                pygame.draw.line(
                    surface, (91, 61, 51),
                    (column_x, row_y), (column_x, min(row_y + brick_height, self.rect.bottom - 3)), 2,
                )
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
        pygame.draw.circle(surface, (255, 168, 197), (self.x - 10, self.y - 11), 7)
        pygame.draw.arc(
            surface, (255, 212, 226),
            (self.x - self.radius + 7, self.y - self.radius + 7,
             self.radius * 2 - 14, self.radius * 2 - 14),
            math.radians(25), math.radians(155), 3,
        )
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
        px, py = self.get_pos()
        angle = math.atan2(-self.projectile.vy_initial + 9.8 * self.projectile.t,
                           self.projectile.vx)
        direction = (math.cos(angle), -math.sin(angle))
        point = (int(px), int(py))
        tail = (int(px - direction[0] * 24), int(py - direction[1] * 24))
        pygame.draw.line(surface, (126, 76, 38), tail, point, 4)
        pygame.draw.line(surface, (229, 180, 77), tail, point, 2)

        tip = (int(px + direction[0] * 9), int(py + direction[1] * 9))
        side = (-direction[1] * 4, direction[0] * 4)
        pygame.draw.polygon(surface, (205, 211, 220), [
            tip,
            (int(px + side[0]), int(py + side[1])),
            (int(px - side[0]), int(py - side[1])),
        ])

        feather_base = (int(px - direction[0] * 19), int(py - direction[1] * 19))
        feather_side = (-direction[1] * 5, direction[0] * 5)
        pygame.draw.polygon(surface, (220, 74, 92), [
            feather_base,
            (int(feather_base[0] - direction[0] * 8 + feather_side[0]),
             int(feather_base[1] - direction[1] * 8 + feather_side[1])),
            (int(feather_base[0] - direction[0] * 8 - feather_side[0]),
             int(feather_base[1] - direction[1] * 8 - feather_side[1])),
        ])
