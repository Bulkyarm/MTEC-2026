"""Mapeamento dos sprites da folha de arte da fase 7."""

import os
from typing import NamedTuple

import pygame


class Phase7Assets(NamedTuple):
    idle: pygame.Surface
    walk: list[pygame.Surface]
    binoculars: pygame.Surface
    portrait: pygame.Surface
    launcher: pygame.Surface
    web_frames: list[pygame.Surface]
    chimp_frames: list[pygame.Surface]
    forest_scene: pygame.Surface
    forest_scene_clear: pygame.Surface


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


def load_phase_7_assets(assets_dir):
    sheet = pygame.image.load(os.path.join(assets_dir, "fase7.png"))
    walk_rects = (
        pygame.Rect(252, 78, 68, 128),
        pygame.Rect(324, 78, 68, 128),
        pygame.Rect(396, 78, 68, 128),
        pygame.Rect(468, 78, 68, 128),
        pygame.Rect(540, 78, 68, 128),
        pygame.Rect(612, 78, 68, 128),
        pygame.Rect(684, 78, 68, 128),
    )
    web_rects = (
        pygame.Rect(970, 505, 58, 58),
        pygame.Rect(1075, 505, 58, 58),
        pygame.Rect(1282, 472, 58, 58),
        pygame.Rect(1448, 505, 58, 58),
    )
    chimp_rects = (
        pygame.Rect(1070, 164, 72, 88),
        pygame.Rect(1142, 250, 72, 88),
        pygame.Rect(1070, 337, 72, 88),
    )
    forest_image = pygame.image.load(
        os.path.join(assets_dir, "cenarioFase7.png")
    ).convert()
    image_width, image_height = forest_image.get_size()
    scale = max(1000 / image_width, 600 / image_height)
    scaled_size = (round(image_width * scale), round(image_height * scale))
    scaled_forest = pygame.transform.smoothscale(forest_image, scaled_size)
    crop_rect = pygame.Rect(0, 0, 1000, 600)
    crop_rect.center = scaled_forest.get_rect().center
    forest_scene = scaled_forest.subsurface(crop_rect).copy()

    forest_without_chimp = forest_image.copy()
    forest_without_chimp.blit(
        forest_image,
        (1260, 198),
        pygame.Rect(1362, 198, 105, 120),
    )
    scaled_forest_clear = pygame.transform.smoothscale(
        forest_without_chimp, scaled_size,
    )
    forest_scene_clear = scaled_forest_clear.subsurface(crop_rect).copy()

    return Phase7Assets(
        idle=pygame.transform.scale(
            _extract_sprite(sheet, pygame.Rect(32, 78, 68, 128)),
            (76, 146),
        ),
        walk=[
            pygame.transform.scale(_extract_sprite(sheet, rect), (76, 146))
            for rect in walk_rects
        ],
        binoculars=pygame.transform.scale(
            _extract_sprite(sheet, pygame.Rect(252, 456, 68, 132)),
            (76, 146),
        ),
        portrait=pygame.transform.smoothscale(
            _extract_sprite(sheet, pygame.Rect(30, 702, 205, 226)),
            (88, 102),
        ),
        launcher=pygame.transform.smoothscale(
            _extract_sprite(sheet, pygame.Rect(800, 508, 105, 91)),
            (83, 72),
        ),
        web_frames=[
            pygame.transform.smoothscale(_extract_sprite(sheet, rect), (34, 34))
            for rect in web_rects
        ],
        chimp_frames=[
            pygame.transform.scale(_extract_sprite(sheet, rect), (62, 76))
            for rect in chimp_rects
        ],
        forest_scene=forest_scene,
        forest_scene_clear=forest_scene_clear,
    )
