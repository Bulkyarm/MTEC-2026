"""Mapeamento dos sprites e objetos da folha de arte da fase 2."""

import os
from typing import NamedTuple

import pygame


class Phase2Assets(NamedTuple):
    idle: pygame.Surface
    walk: list[pygame.Surface]
    portrait: pygame.Surface
    empty_board: pygame.Surface


def _extract(sheet, rect):
    source = sheet.subsurface(rect)
    sprite = pygame.Surface(rect.size, pygame.SRCALPHA)
    for y in range(rect.height):
        for x in range(rect.width):
            red, green, blue, _ = source.get_at((x, y))
            is_background = (
                red < 20
                and green < 43
                and blue < 78
                and blue > red * 1.2
                and blue > green * 1.15
            )
            sprite.set_at((x, y), (red, green, blue, 0 if is_background else 255))
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
        (190, 155),
    )
    return Phase2Assets(
        idle=pygame.transform.scale(
            _extract(sheet, pygame.Rect(30, 72, 62, 145)),
            (66, 138),
        ),
        walk=walk_sprites,
        portrait=portrait,
        empty_board=empty_board,
    )
