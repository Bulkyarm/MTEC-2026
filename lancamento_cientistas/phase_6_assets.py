"""Mapeamento dos sprites da folha de arte da fase 6."""

import os
from typing import NamedTuple

import pygame


class Phase6Assets(NamedTuple):
    idle: pygame.Surface
    walk: list[pygame.Surface]
    looking: pygame.Surface
    portrait: pygame.Surface
    laboratory: pygame.Surface
    laboratory_foreground: pygame.Surface
    transposon_frames: list[pygame.Surface]


def _extract_sprite(sheet, rect):
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


def load_phase_6_assets(assets_dir):
    sheet = pygame.image.load(os.path.join(assets_dir, "fase6.png"))
    walk_rects = (
        pygame.Rect(395, 78, 68, 142),
        pygame.Rect(467, 78, 68, 142),
        pygame.Rect(539, 78, 68, 142),
        pygame.Rect(611, 78, 68, 142),
        pygame.Rect(683, 78, 68, 142),
    )
    transposon_rects = (
        pygame.Rect(794, 416, 137, 88),
        pygame.Rect(953, 416, 139, 88),
        pygame.Rect(1092, 416, 150, 88),
    )
    laboratory = pygame.transform.smoothscale(
        _extract_sprite(sheet, pygame.Rect(790, 683, 404, 282)),
        (283, 198),
    )
    return Phase6Assets(
        idle=pygame.transform.scale(
            _extract_sprite(sheet, pygame.Rect(31, 78, 67, 142)),
            (58, 126),
        ),
        walk=[
            pygame.transform.scale(_extract_sprite(sheet, rect), (58, 126))
            for rect in walk_rects
        ],
        looking=pygame.transform.scale(
            _extract_sprite(sheet, pygame.Rect(580, 273, 62, 138)),
            (58, 126),
        ),
        portrait=pygame.transform.smoothscale(
            _extract_sprite(sheet, pygame.Rect(31, 711, 193, 222)),
            (88, 102),
        ),
        laboratory=laboratory,
        laboratory_foreground=laboratory.subsurface(
            pygame.Rect(0, 84, laboratory.get_width(), 114)
        ).copy(),
        transposon_frames=[
            pygame.transform.smoothscale(_extract_sprite(sheet, rect), (112, 72))
            for rect in transposon_rects
        ],
    )
