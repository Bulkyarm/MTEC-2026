"""Mapeamento dos sprites e objetos da folha de arte da fase 2."""

import os
from collections import deque
from typing import NamedTuple

import pygame


class Phase2Assets(NamedTuple):
    idle: pygame.Surface
    walk: list[pygame.Surface]
    bow_hold: pygame.Surface
    bow_draw: pygame.Surface
    bow_aim: pygame.Surface
    bow_shoot: pygame.Surface
    portrait: pygame.Surface
    empty_board: pygame.Surface
    chalk: pygame.Surface


def _extract_pose(sheet, rect, height):
    sprite = _extract(sheet, rect)
    bounds = sprite.get_bounding_rect()
    sprite = sprite.subsurface(bounds).copy()
    size = (round(sprite.get_width() * height / sprite.get_height()), height)
    return pygame.transform.smoothscale(sprite, size)


def _extract(sheet, rect):
    source = sheet.subsurface(rect)
    sprite = pygame.Surface(rect.size, pygame.SRCALPHA)
    colors = [
        [source.get_at((x, y))[:3] for x in range(rect.width)]
        for y in range(rect.height)
    ]
    black_background = [[False] * rect.width for _ in range(rect.height)]
    pending = deque()
    for x in range(rect.width):
        pending.append((x, 0))
        pending.append((x, rect.height - 1))
    for y in range(rect.height):
        pending.append((0, y))
        pending.append((rect.width - 1, y))

    while pending:
        x, y = pending.popleft()
        if black_background[y][x] or max(colors[y][x]) > 24:
            continue
        black_background[y][x] = True
        if x > 0:
            pending.append((x - 1, y))
        if x < rect.width - 1:
            pending.append((x + 1, y))
        if y > 0:
            pending.append((x, y - 1))
        if y < rect.height - 1:
            pending.append((x, y + 1))

    for y in range(rect.height):
        for x in range(rect.width):
            red, green, blue = colors[y][x]
            is_background = (
                red < 20
                and green < 43
                and blue < 78
                and blue > red * 1.2
                and blue > green * 1.15
            )
            sprite.set_at(
                (x, y),
                (red, green, blue, 0 if is_background or black_background[y][x] else 255),
            )
    return sprite


def load_phase_2_assets(assets_dir):
    sheet = pygame.image.load(os.path.join(assets_dir, "fase2.png"))
    walk_rects = (
        pygame.Rect(403, 72, 70, 145),
        pygame.Rect(481, 72, 70, 145),
        pygame.Rect(558, 72, 70, 145),
        pygame.Rect(635, 72, 70, 145),
        pygame.Rect(709, 72, 70, 145),
    )
    walk_sprites = [
        pygame.transform.scale(_extract(sheet, rect), (66, 138))
        for rect in walk_rects
    ]
    portrait = pygame.transform.smoothscale(
        _extract(sheet, pygame.Rect(34, 711, 188, 220)),
        (100, 116),
    )
    empty_board = pygame.transform.smoothscale(
        _extract(sheet, pygame.Rect(1191, 697, 322, 263)),
        (235, 192),
    )
    chalk = pygame.transform.smoothscale(
        _extract(sheet, pygame.Rect(840, 735, 100, 85)),
        (30, 26),
    )
    bow_poses = (
        pygame.Rect(52, 620, 95, 130),
        pygame.Rect(215, 620, 120, 130),
        pygame.Rect(390, 620, 120, 130),
        pygame.Rect(575, 620, 125, 130),
    )
    return Phase2Assets(
        idle=pygame.transform.scale(
            _extract(sheet, pygame.Rect(30, 72, 62, 145)),
            (66, 138),
        ),
        walk=walk_sprites,
        bow_hold=_extract_pose(sheet, bow_poses[0], 138),
        bow_draw=_extract_pose(sheet, bow_poses[1], 138),
        bow_aim=_extract_pose(sheet, bow_poses[2], 138),
        bow_shoot=_extract_pose(sheet, bow_poses[3], 138),
        portrait=portrait,
        empty_board=empty_board,
        chalk=chalk,
    )
