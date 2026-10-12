"""Mapeamento dos sprites da folha de arte da fase 5."""


"""
Retirar a mesa de lá, melhorar a textura da arma e a animação de liberação de energia.
"""

import os
from typing import NamedTuple

import pygame


class Phase5Assets(NamedTuple):
    idle: pygame.Surface
    walk: list[pygame.Surface]
    talking: pygame.Surface
    portrait: pygame.Surface
    neutron_frames: list[pygame.Surface]
    atom: pygame.Surface
    nucleus: pygame.Surface
    fission_result: pygame.Surface
    lab_cabinet: pygame.Surface


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


def load_phase_5_assets(assets_dir):
    sheet = pygame.image.load(os.path.join(assets_dir, "fase5.png"))
    walk_rects = (
        pygame.Rect(397, 78, 67, 142),
        pygame.Rect(469, 78, 67, 142),
        pygame.Rect(541, 78, 67, 142),
        pygame.Rect(613, 78, 67, 142),
        pygame.Rect(685, 78, 67, 142),
    )
    neutron_rects = (
        pygame.Rect(814, 91, 72, 58),
        pygame.Rect(914, 96, 61, 52),
        pygame.Rect(1017, 91, 72, 58),
        pygame.Rect(1118, 85, 73, 66),
    )
    return Phase5Assets(
        idle=pygame.transform.scale(
            _extract_sprite(sheet, pygame.Rect(32, 78, 65, 142)),
            (58, 126),
        ),
        walk=[
            pygame.transform.scale(_extract_sprite(sheet, rect), (58, 126))
            for rect in walk_rects
        ],
        talking=pygame.transform.scale(
            _extract_sprite(sheet, pygame.Rect(242, 273, 76, 140)),
            (68, 126),
        ),
        portrait=pygame.transform.smoothscale(
            _extract_sprite(sheet, pygame.Rect(31, 711, 198, 222)),
            (88, 102),
        ),
        neutron_frames=[
            pygame.transform.smoothscale(_extract_sprite(sheet, rect), (42, 36))
            for rect in neutron_rects
        ],
        atom=pygame.transform.smoothscale(
            _extract_sprite(sheet, pygame.Rect(792, 278, 202, 190)),
            (132, 124),
        ),
        nucleus=pygame.transform.smoothscale(
            _extract_sprite(sheet, pygame.Rect(1040, 327, 108, 104)),
            (72, 72),
        ),
        fission_result=pygame.transform.smoothscale(
            _extract_sprite(sheet, pygame.Rect(960, 526, 406, 112)),
            (280, 78),
        ),
        lab_cabinet=pygame.transform.smoothscale(
            _extract_sprite(sheet, pygame.Rect(1267, 716, 246, 250)),
            (165, 168),
        ),
    )
