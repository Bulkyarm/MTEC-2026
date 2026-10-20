"""
Entidades desenháveis do jogo: Arqueiro animado a partir do sprite em assets,
Flecha (wrapper visual do Projectile), Obstáculo e Alvo (bolha da cientista).

As demais entidades continuam desenhadas com primitivas do Pygame.
"""

import math
import os
import pygame
from settings import (
    COLOR_OBSTACLE, COLOR_TARGET, COLOR_TARGET_HIT,
    COLOR_WHITE, COLOR_BLACK, ARCHER_X, ARCHER_Y, GROUND_Y,
    GRAVITY, PIXELS_PER_METER,
)
from physics import Projectile


class Archer:
    """Representa o atirador, fixo do lado esquerdo da tela."""

    FRAME_SIZE = (130, 130)
    IDLE_FRAME_CENTERS = (100,)
    DRAW_FRAME_CENTERS = (100, 230, 365, 485, 615, 750)
    SHOOT_FRAME_CENTERS = (102, 245, 415, 575)
    REST_FRAME_CENTERS = (100, 250, 402, 550, 697, 835)

    def __init__(self, x=ARCHER_X, y=ARCHER_Y):
        self.x = x
        self.y = y
        self.width = 24
        self.height = 60
        self.fire_duration = 0.22
        self.draw_duration = 0.55
        self.fire_timer = 0.0
        self.draw_progress = 0.0
        self.animation_time = 0.0
        self.aiming = False
        self.has_drawn_arrow = False
        (
            self.idle_frames,
            self.draw_frames,
            self.shoot_frames,
            self.rest_frames,
        ) = self._load_frames()

    def _load_frames(self):
        assets_dir = os.path.join(os.path.dirname(__file__), "assets")
        sheet = pygame.image.load(os.path.join(assets_dir, "arqueiro.png"))
        frame_width, frame_height = self.FRAME_SIZE

        def crop_frames(centers, top):
            frames = []
            for center_x in centers:
                source_rect = pygame.Rect(
                    center_x - frame_width // 2,
                    top,
                    frame_width,
                    frame_height,
                )
                frame = pygame.Surface(self.FRAME_SIZE, pygame.SRCALPHA)
                frame.blit(sheet, (0, 0), source_rect)
                for frame_y in range(frame_height):
                    for frame_x in range(frame_width):
                        color = frame.get_at((frame_x, frame_y))
                        if (
                            color.r <= 12
                            and color.g <= 18
                            and color.b <= 36
                            and color.b >= color.g + 4
                        ):
                            frame.set_at(
                                (frame_x, frame_y),
                                (color.r, color.g, color.b, 0),
                            )
                frames.append(frame)
            return frames

        return (
            crop_frames(self.IDLE_FRAME_CENTERS, 71),
            crop_frames(self.DRAW_FRAME_CENTERS, 288),
            crop_frames(self.SHOOT_FRAME_CENTERS, 507),
            crop_frames(self.REST_FRAME_CENTERS, 720),
        )

    def fire(self):
        self.fire_timer = self.fire_duration
        self.aiming = False

    def update(self, dt, aiming=False):
        self.fire_timer = max(0.0, self.fire_timer - dt)
        self.animation_time += dt
        self.aiming = aiming
        if aiming:
            self.has_drawn_arrow = True
            self.draw_progress = min(
                1.0, self.draw_progress + dt / self.draw_duration
            )
        else:
            self.draw_progress = max(
                0.0, self.draw_progress - dt / self.fire_duration
            )

    def draw(self, surface, aim_angle_deg=45):
        if self.fire_timer > 0:
            progress = 1 - self.fire_timer / self.fire_duration
            frames = self.shoot_frames
            frame_index = min(len(frames) - 1, int(progress * len(frames)))
        elif self.aiming:
            frames = self.draw_frames
            frame_index = min(
                len(frames) - 1,
                int(self.draw_progress * len(frames)),
            )
        elif self.has_drawn_arrow:
            frames = self.rest_frames
            frame_index = int(self.animation_time * 8) % len(frames)
        else:
            frames = self.idle_frames
            frame_index = int(self.animation_time * 8) % len(frames)

        sprite = frames[frame_index]
        visible_bounds = sprite.get_bounding_rect()
        feet_y = self.y + GROUND_Y - ARCHER_Y
        sprite_rect = sprite.get_rect()
        sprite_rect.midbottom = (
            round(self.x),
            round(feet_y + sprite.get_height() - visible_bounds.bottom),
        )
        surface.blit(sprite, sprite_rect)

    def draw_bow(self, surface, aim_angle_deg=45, draw_arms=False):
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
        if draw_arms:
            body_top = self.y - self.height
            bow_shoulder = (self.x + 5, body_top + 16)
            draw_shoulder = (self.x - 7, body_top + 21)
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
        if draw_arms:
            pygame.draw.circle(surface, (224, 168, 126), elbow, 5)
            pygame.draw.circle(surface, (224, 168, 126), grip, 5)
            pygame.draw.circle(surface, (224, 168, 126), string_center, 4)

    def get_launch_point(self):
        return self.x + 40, self.y - 38

    def get_bow_launch_point(self, aim_angle_deg=45):
        angle_rad = math.radians(aim_angle_deg)
        aim_direction = (math.cos(angle_rad), -math.sin(angle_rad))
        string_rest = (
            self.x + 29,
            self.y - self.height // 2 - 4,
        )
        draw_distance = 20 * self.draw_progress
        return (
            string_rest[0] - aim_direction[0] * draw_distance,
            string_rest[1] - aim_direction[1] * draw_distance,
        )


class Obstacle:
    """Bloco/parede vertical que a flecha precisa transpor."""

    TERRAIN_SIDE_RECT = pygame.Rect(1008, 136, 50, 48)
    TERRAIN_TOP_RECT = pygame.Rect(1008, 110, 50, 18)
    terrain_side = None
    terrain_top = None

    def __init__(self, x, y, width, height, angle=0):
        self.rect = pygame.Rect(x, y, width, height)
        self.angle = angle
        self.points = self._polygon_points()
        self._textured_surface = None

    @classmethod
    def set_terrain_textures(cls, side, top):
        cls.terrain_side = side
        cls.terrain_top = top

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

    def set_y(self, y):
        self.rect.y = round(y)
        self.points = self._polygon_points()

    def draw(self, surface):
        if self.terrain_side is not None and self.terrain_top is not None:
            if self._textured_surface is None:
                self._textured_surface = pygame.Surface(
                    self.rect.size, pygame.SRCALPHA
                )
                tile_size = (
                    max(1, round(self.terrain_side.get_width() * 0.5)),
                    max(1, round(self.terrain_side.get_height() * 0.5)),
                )
                side_tile = pygame.transform.scale(
                    self.terrain_side, tile_size
                )
                top_tile = pygame.transform.scale(
                    self.terrain_top,
                    (
                        max(1, round(self.terrain_top.get_width() * 0.5)),
                        max(1, round(self.terrain_top.get_height() * 0.5)),
                    ),
                )
                top_height = min(top_tile.get_height(), self.rect.height)
                for tile_x in range(0, self.rect.width, top_tile.get_width()):
                    self._textured_surface.blit(top_tile, (tile_x, 0))
                for tile_y in range(top_height, self.rect.height, side_tile.get_height()):
                    for tile_x in range(0, self.rect.width, side_tile.get_width()):
                        self._textured_surface.blit(side_tile, (tile_x, tile_y))

            if self.angle:
                rotated_surface = pygame.transform.rotate(
                    self._textured_surface, -self.angle
                )
                surface.blit(
                    rotated_surface,
                    rotated_surface.get_rect(center=self.rect.center),
                )
            else:
                surface.blit(self._textured_surface, self.rect)
            return

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
