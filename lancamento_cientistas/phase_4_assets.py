"""Mapeamento dos sprites da folha de arte da fase 4."""
"""Falata os obstaculos também"""

import os
from typing import NamedTuple

import pygame


class Phase4Assets(NamedTuple):
    idle: pygame.Surface
    walk: list[pygame.Surface]
    talking: pygame.Surface
    portrait: pygame.Surface
    machine: pygame.Surface
    furnace_lit: pygame.Surface
    furnace_unlit: pygame.Surface


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


def load_phase_4_assets(assets_dir):
    sheet = pygame.image.load(os.path.join(assets_dir, "fase4.png"))
    walk_rects = (
        pygame.Rect(400, 78, 65, 142),
        pygame.Rect(472, 78, 65, 142),
        pygame.Rect(544, 78, 65, 142),
        pygame.Rect(616, 78, 65, 142),
        pygame.Rect(688, 78, 65, 142),
    )
    machine = pygame.transform.smoothscale(
        _extract_sprite(sheet, pygame.Rect(786, 76, 290, 386)),
        (160, 205),
    )
    furnace_lit = pygame.transform.smoothscale(
        _extract_sprite(sheet, pygame.Rect(800, 580, 365, 300)),
        (205, 178),
    )
    furnace_unlit = furnace_lit.copy()
    pygame.draw.rect(furnace_unlit, (18, 19, 25), (24, 59, 54, 56))
    pygame.draw.line(furnace_unlit, (62, 57, 58), (29, 107), (70, 107), 4)
    pygame.draw.circle(furnace_unlit, (84, 66, 54), (39, 105), 4)
    pygame.draw.circle(furnace_unlit, (84, 66, 54), (59, 105), 4)

    return Phase4Assets(
        idle=pygame.transform.scale(
            _extract_sprite(sheet, pygame.Rect(35, 78, 65, 142)),
            (58, 126),
        ),
        walk=[
            pygame.transform.scale(_extract_sprite(sheet, rect), (58, 126))
            for rect in walk_rects
        ],
        talking=pygame.transform.scale(
            _extract_sprite(sheet, pygame.Rect(245, 274, 105, 140)),
            (96, 126),
        ),
        portrait=pygame.transform.smoothscale(
            _extract_sprite(sheet, pygame.Rect(38, 716, 190, 220)),
            (88, 102),
        ),
        machine=machine,
        furnace_lit=furnace_lit,
        furnace_unlit=furnace_unlit,
    )
