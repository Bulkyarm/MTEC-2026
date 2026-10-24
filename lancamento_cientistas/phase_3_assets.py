"""Mapeamento dos sprites da folha de arte da fase 3."""

"""Fasta ajustes finos, e a barrinha horizontal que fica em cima do botão.O botão fica do lado direito extremo da tela, e do lado dele a maquina"""

import os
from typing import NamedTuple

import pygame


class Phase3Assets(NamedTuple):
    idle: pygame.Surface
    walk: list[pygame.Surface]
    portrait: pygame.Surface
    camera: pygame.Surface
    diffraction_photo: pygame.Surface


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


def load_phase_3_assets(assets_dir):
    sheet = pygame.image.load(os.path.join(assets_dir, "fase3.png"))
    walk_rects = (
        pygame.Rect(398, 78, 66, 142),
        pygame.Rect(468, 78, 66, 142),
        pygame.Rect(538, 78, 66, 142),
        pygame.Rect(608, 78, 66, 142),
        pygame.Rect(678, 78, 66, 142),
    )
    return Phase3Assets(
        idle=pygame.transform.scale(
            _extract_sprite(sheet, pygame.Rect(34, 78, 68, 142)),
            (62, 130),
        ),
        walk=[
            pygame.transform.scale(_extract_sprite(sheet, rect), (62, 130))
            for rect in walk_rects
        ],
        portrait=pygame.transform.smoothscale(
            _extract_sprite(sheet, pygame.Rect(36, 716, 194, 220)),
            (92, 106),
        ),
        camera=pygame.transform.smoothscale(
            _extract_sprite(sheet, pygame.Rect(796, 116, 250, 292)),
            (142, 150),
        ),
        diffraction_photo=pygame.transform.smoothscale(
            sheet.subsurface(pygame.Rect(1148, 520, 316, 316)),
            (112, 112),
        ),
    )
