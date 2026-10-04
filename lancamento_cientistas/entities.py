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
    GRAVITY, PIXELS_PER_METER,
)
from physics import Projectile


class Archer:
    """Representa o atirador, fixo do lado esquerdo da tela."""

    def __init__(self, x=ARCHER_X, y=ARCHER_Y):
        self.x = x
        self.y = y
        self.width = 24
        self.height = 60
        self.fire_duration = 0.22
        self.fire_timer = 0.0
        self.draw_progress = 0.0

    def fire(self):
        self.fire_timer = self.fire_duration

    def update(self, dt, aiming=False):
        self.fire_timer = max(0.0, self.fire_timer - dt)
        target_progress = 1.0 if aiming else self.fire_timer / self.fire_duration
        progress_step = min(1.0, dt * 12)
        self.draw_progress += (target_progress - self.draw_progress) * progress_step

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
        pygame.draw.ellipse(surface, (24, 37, 47), (body_rect.left - 3, body_rect.bottom - 8, 30, 13))
        pygame.draw.rect(surface, (39, 104, 128), body_rect, border_radius=6)
        pygame.draw.polygon(surface, (53, 132, 145), [
            (body_rect.left + 4, body_rect.top + 5),
            (self.x, body_rect.top + 10),
            (self.x - 2, body_rect.bottom - 7),
            (body_rect.left + 4, body_rect.bottom - 5),
        ])
        pygame.draw.rect(surface, (28, 67, 84), body_rect, width=2, border_radius=6)
        pygame.draw.line(surface, (185, 145, 83),
                         (body_rect.left + 3, body_rect.top + 32),
                         (body_rect.right - 3, body_rect.top + 32), 5)
        pygame.draw.circle(surface, (239, 204, 129), (self.x, body_rect.top + 32), 4)
        pygame.draw.line(surface, (76, 171, 172),
                         (self.x - 2, body_rect.top + 8), (self.x - 2, body_rect.bottom - 8), 2)

        pygame.draw.line(surface, (58, 42, 65),
                         (self.x - 7, self.y - 3), (self.x - 14, self.y + 18), 7)
        pygame.draw.line(surface, (58, 42, 65),
                         (self.x + 7, self.y - 3), (self.x + 14, self.y + 18), 7)
        pygame.draw.line(surface, (20, 20, 25),
                         (self.x - 20, self.y + 18), (self.x - 8, self.y + 18), 5)
        pygame.draw.line(surface, (20, 20, 25),
                         (self.x + 8, self.y + 18), (self.x + 20, self.y + 18), 5)

        angle_rad = math.radians(aim_angle_deg)
        aim_direction = (math.cos(angle_rad), -math.sin(angle_rad))
        perpendicular = (math.sin(angle_rad), math.cos(angle_rad))
        grip = (self.x + 29, self.y - self.height // 2 - 4)
        draw_distance = 20 * self.draw_progress
        bow_points = []
        for index in range(13):
            t = index / 6 - 1
            bow_points.append((
                grip[0] + aim_direction[0] * 7 * (1 - t * t)
                + perpendicular[0] * 27 * t,
                grip[1] + aim_direction[1] * 7 * (1 - t * t)
                + perpendicular[1] * 27 * t,
            ))
        pygame.draw.lines(surface, (137, 79, 38), False, bow_points, 6)
        pygame.draw.lines(surface, (218, 139, 65), False, bow_points, 2)

        string_rest = (
            (bow_points[0][0] + bow_points[-1][0]) / 2,
            (bow_points[0][1] + bow_points[-1][1]) / 2,
        )
        string_center = (
            string_rest[0] - aim_direction[0] * draw_distance,
            string_rest[1] - aim_direction[1] * draw_distance,
        )
        bow_shoulder = (self.x + 5, body_rect.top + 16)
        draw_shoulder = (self.x - 7, body_rect.top + 21)
        arm_dx = string_center[0] - draw_shoulder[0]
        arm_dy = string_center[1] - draw_shoulder[1]
        arm_length = max(1, math.hypot(arm_dx, arm_dy))
        elbow_bend = (-arm_dy / arm_length, arm_dx / arm_length)
        if elbow_bend[0] > 0:
            elbow_bend = (-elbow_bend[0], -elbow_bend[1])
        elbow_offset = 6 + 7 * self.draw_progress
        elbow = (
            draw_shoulder[0] + arm_dx * 0.48 + elbow_bend[0] * elbow_offset,
            draw_shoulder[1] + arm_dy * 0.48 + elbow_bend[1] * elbow_offset,
        )

        pygame.draw.line(surface, (224, 168, 126), bow_shoulder, grip, 8)
        pygame.draw.line(surface, (245, 195, 151),
                         (bow_shoulder[0] + 3, bow_shoulder[1] - 2), grip, 3)
        pygame.draw.line(surface, (224, 168, 126), draw_shoulder, elbow, 8)
        pygame.draw.line(surface, (224, 168, 126), elbow, string_center, 7)
        pygame.draw.line(surface, (245, 195, 151),
                         (draw_shoulder[0] + 2, draw_shoulder[1] - 2), elbow, 3)
        pygame.draw.line(surface, (245, 195, 151),
                         (elbow[0] + 1, elbow[1] - 1), string_center, 2)

        pygame.draw.line(surface, (235, 220, 175), bow_points[0], bow_points[-1], 2)
        pygame.draw.line(surface, (235, 220, 175), bow_points[0], string_center, 1)
        pygame.draw.line(surface, (235, 220, 175), string_center, bow_points[-1], 1)
        pygame.draw.circle(surface, (224, 168, 126), elbow, 5)
        pygame.draw.circle(surface, (224, 168, 126), grip, 5)
        pygame.draw.circle(surface, (224, 168, 126), string_center, 4)

    def get_launch_point(self):
        return self.x, self.y - self.height // 2


class Obstacle:
    """Bloco/parede vertical que a flecha precisa transpor."""

    def __init__(self, x, y, width, height, angle=0):
        self.rect = pygame.Rect(x, y, width, height)
        self.angle = angle
        self.points = self._polygon_points()

    def _polygon_points(self, inset=0):
        center_x, center_y = self.rect.center
        half_width = self.rect.width / 2 - inset
        half_height = self.rect.height / 2 - inset
        angle_rad = math.radians(self.angle)
        cos_angle = math.cos(angle_rad)
        sin_angle = math.sin(angle_rad)
        corners = [
            (-half_width, -half_height),
            (half_width, -half_height),
            (half_width, half_height),
            (-half_width, half_height),
        ]
        return [
            (
                round(center_x + x * cos_angle - y * sin_angle),
                round(center_y + x * sin_angle + y * cos_angle),
            )
            for x, y in corners
        ]

    def draw(self, surface):
        if self.angle:
            pygame.draw.polygon(surface, COLOR_OBSTACLE, self.points)
            pygame.draw.polygon(surface, (151, 108, 76), self._polygon_points(3))
            pygame.draw.polygon(surface, COLOR_BLACK, self.points, width=2)
            return

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
        if not self.angle:
            return self.rect.collidepoint(px, py) or self.rect.inflate(radius, radius).collidepoint(px, py)

        inside = False
        previous = self.points[-1]
        for current in self.points:
            x1, y1 = previous
            x2, y2 = current
            if (y1 > py) != (y2 > py):
                crossing_x = (x2 - x1) * (py - y1) / (y2 - y1) + x1
                if px < crossing_x:
                    inside = not inside

            segment_x = x2 - x1
            segment_y = y2 - y1
            segment_length_sq = segment_x ** 2 + segment_y ** 2
            projection = 0 if not segment_length_sq else max(
                0, min(1, ((px - x1) * segment_x + (py - y1) * segment_y) / segment_length_sq)
            )
            closest_x = x1 + projection * segment_x
            closest_y = y1 + projection * segment_y
            if (px - closest_x) ** 2 + (py - closest_y) ** 2 <= radius ** 2:
                return True
            previous = current

        return inside


class Target:
    """A bolha-alvo contendo o nome da cientista da rodada atual."""

    def __init__(self, x, y, name, radius=32, fall_speed_multiplier=1.0):
        self.x = x
        self.y = y
        self.initial_y = y
        self.name = name
        self.radius = radius
        self.fall_speed_multiplier = fall_speed_multiplier
        self.hit = False
        self.falling = False
        self.fall_elapsed = 0.0

    def start_falling(self):
        self.y = self.initial_y
        self.fall_elapsed = 0.0
        self.falling = True

    def update(self, dt):
        if not self.falling:
            return
        self.fall_elapsed += dt
        acceleration_px = GRAVITY * PIXELS_PER_METER * self.fall_speed_multiplier
        self.y = self.initial_y + 0.5 * acceleration_px * self.fall_elapsed ** 2

    def draw(self, surface, font):
        color = COLOR_TARGET_HIT if self.hit else COLOR_TARGET
        center_x, center_y = round(self.x), round(self.y)
        pygame.draw.circle(surface, color, (center_x, center_y), self.radius)
        pygame.draw.circle(surface, (255, 168, 197), (center_x - 10, center_y - 11), 7)
        pygame.draw.arc(
            surface, (255, 212, 226),
            (center_x - self.radius + 7, center_y - self.radius + 7,
             self.radius * 2 - 14, self.radius * 2 - 14),
            math.radians(25), math.radians(155), 3,
        )
        pygame.draw.circle(surface, COLOR_BLACK, (center_x, center_y), self.radius, width=2)

        # nome da cientista, quebrado em até duas linhas se necessário
        words = self.name.split(" ")
        line1 = words[0]
        line2 = " ".join(words[1:])
        text1 = font.render(line1, True, COLOR_WHITE)
        text2 = font.render(line2, True, COLOR_WHITE) if line2 else None

        surface.blit(text1, text1.get_rect(center=(center_x, center_y - 8)))
        if text2:
            surface.blit(text2, text2.get_rect(center=(center_x, center_y + 10)))

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
        velocity_y_screen = -(self.projectile.vy_initial - 9.8 * self.projectile.t)
        angle = math.atan2(velocity_y_screen, self.projectile.vx)
        direction = (math.cos(angle), math.sin(angle))
        point = (int(px), int(py))
        tail = (int(px - direction[0] * 29), int(py - direction[1] * 29))
        head_base = (int(px + direction[0] * 8), int(py + direction[1] * 8))
        pygame.draw.line(surface, (87, 49, 29), tail, head_base, 5)
        pygame.draw.line(surface, (194, 137, 67), tail, head_base, 2)
        pygame.draw.line(surface, (245, 207, 125),
                         (int(tail[0] + direction[0] * 3), int(tail[1] + direction[1] * 3)),
                         (int(head_base[0] - direction[0] * 2), int(head_base[1] - direction[1] * 2)), 1)

        tip = (int(px + direction[0] * 16), int(py + direction[1] * 16))
        side = (-direction[1] * 5, direction[0] * 5)
        pygame.draw.polygon(surface, (205, 211, 220), [
            tip,
            (int(head_base[0] + side[0]), int(head_base[1] + side[1])),
            (int(head_base[0] - side[0]), int(head_base[1] - side[1])),
        ])
        pygame.draw.line(surface, (245, 248, 250), tip,
                         (int(head_base[0] + side[0]), int(head_base[1] + side[1])), 1)

        feather_base = (int(px - direction[0] * 19), int(py - direction[1] * 19))
        feather_side = (-direction[1] * 6, direction[0] * 6)
        for side_sign in (-1, 1):
            pygame.draw.polygon(surface, (186, 47, 62), [
                feather_base,
                (int(feather_base[0] - direction[0] * 10 + feather_side[0] * side_sign),
                 int(feather_base[1] - direction[1] * 10 + feather_side[1] * side_sign)),
                (int(feather_base[0] - direction[0] * 3 + feather_side[0] * side_sign * 0.45),
                 int(feather_base[1] - direction[1] * 3 + feather_side[1] * side_sign * 0.45)),
            ])
        pygame.draw.circle(surface, (224, 184, 111), tail, 3)
