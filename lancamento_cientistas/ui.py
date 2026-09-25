"""
Componentes de interface reutilizáveis: caixa de input numérico, botão
clicável e caixa de diálogo (usada tanto para a dica da cientista quanto
para o feedback de acerto/erro).
"""

import pygame
from settings import (
    COLOR_INPUT_BG, COLOR_INPUT_ACTIVE, COLOR_WHITE, COLOR_GRAY,
    COLOR_BUTTON, COLOR_BUTTON_HOVER, COLOR_BLACK, COLOR_DIALOG_BG,
    COLOR_ACCENT,
)


class InputBox:
    """Campo de texto simples, aceitando apenas números (inteiros ou decimais)."""

    def __init__(self, x, y, w, h, label="", initial_text="", font=None,
                 min_value=None, max_value=None):
        self.rect = pygame.Rect(x, y, w, h)
        self.label = label
        self.text = initial_text
        self.active = False
        self.font = font or pygame.font.SysFont("arial", 22)
        self.label_font = pygame.font.SysFont("arial", 18)
        self.min_value = min_value
        self.max_value = max_value

    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            self.active = self.rect.collidepoint(event.pos)
        elif event.type == pygame.KEYDOWN and self.active:
            if event.key == pygame.K_BACKSPACE:
                self.text = self.text[:-1]
            elif event.key in (pygame.K_RETURN, pygame.K_TAB):
                self.active = False
            elif event.unicode.isdigit() or (event.unicode == "." and "." not in self.text):
                self.text += event.unicode

    def get_value(self):
        try:
            return float(self.text)
        except ValueError:
            return None

    def is_valid(self):
        value = self.get_value()
        if value is None:
            return False
        if self.min_value is not None and value < self.min_value:
            return False
        if self.max_value is not None and value > self.max_value:
            return False
        return True

    def draw(self, surface):
        label_surf = self.label_font.render(self.label, True, COLOR_WHITE)
        surface.blit(label_surf, (self.rect.x, self.rect.y - 22))

        bg_color = COLOR_INPUT_ACTIVE if self.active else COLOR_INPUT_BG
        pygame.draw.rect(surface, bg_color, self.rect, border_radius=6)
        border_color = COLOR_ACCENT if self.active else COLOR_GRAY
        pygame.draw.rect(surface, border_color, self.rect, width=2, border_radius=6)

        text_surf = self.font.render(self.text, True, COLOR_WHITE)
        surface.blit(text_surf, (self.rect.x + 10, self.rect.y + (self.rect.h - text_surf.get_height()) // 2))


class Button:
    """Botão clicável simples, com callback opcional."""

    def __init__(self, x, y, w, h, text, font=None, on_click=None):
        self.rect = pygame.Rect(x, y, w, h)
        self.text = text
        self.font = font or pygame.font.SysFont("arial", 22, bold=True)
        self.on_click = on_click
        self.hovered = False

    def handle_event(self, event):
        if event.type == pygame.MOUSEMOTION:
            self.hovered = self.rect.collidepoint(event.pos)
        elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.rect.collidepoint(event.pos) and self.on_click:
                self.on_click()

    def draw(self, surface):
        color = COLOR_BUTTON_HOVER if self.hovered else COLOR_BUTTON
        pygame.draw.rect(surface, color, self.rect, border_radius=8)
        pygame.draw.rect(surface, COLOR_BLACK, self.rect, width=2, border_radius=8)
        text_surf = self.font.render(self.text, True, COLOR_WHITE)
        surface.blit(text_surf, text_surf.get_rect(center=self.rect.center))


class HelpNPC:
    """
    Representa a cientista da rodada como um NPC clicável (avatar simples)
    posicionado perto do arqueiro. Ao ser clicada, abre o balão de dica.
    """

    def __init__(self, x, y, radius=26):
        self.x = x
        self.y = y
        self.radius = radius
        self.rect = pygame.Rect(x - radius, y - radius, radius * 2, radius * 2)

    def is_clicked(self, pos):
        return self.rect.collidepoint(pos)

    def draw(self, surface, font):
        pygame.draw.circle(surface, COLOR_ACCENT, (self.x, self.y), self.radius)
        pygame.draw.circle(surface, COLOR_BLACK, (self.x, self.y), self.radius, width=2)
        q_surf = font.render("?", True, COLOR_BLACK)
        surface.blit(q_surf, q_surf.get_rect(center=(self.x, self.y)))


class DialogBox:
    """
    Caixa de diálogo genérica usada para: (a) dica de fórmula da cientista,
    e (b) feedback de acerto/erro após o lançamento.
    """

    def __init__(self, screen_width, screen_height):
        self.visible = False
        self.title = ""
        self.message = ""
        self.width = int(screen_width * 0.7)
        self.height = 160
        self.x = (screen_width - self.width) // 2
        self.y = screen_height - self.height - 30
        self.title_font = pygame.font.SysFont("arial", 22, bold=True)
        self.text_font = pygame.font.SysFont("arial", 18)

    def show(self, title, message):
        self.title = title
        self.message = message
        self.visible = True

    def hide(self):
        self.visible = False

    def handle_event(self, event):
        if self.visible and event.type == pygame.MOUSEBUTTONDOWN:
            self.hide()

    def _wrap_text(self, text, max_width):
        words = text.split(" ")
        lines = []
        current = ""
        for word in words:
            test = f"{current} {word}".strip()
            if self.text_font.size(test)[0] <= max_width:
                current = test
            else:
                lines.append(current)
                current = word
        if current:
            lines.append(current)
        return lines

    def draw(self, surface):
        if not self.visible:
            return
        rect = pygame.Rect(self.x, self.y, self.width, self.height)
        pygame.draw.rect(surface, COLOR_DIALOG_BG, rect, border_radius=10)
        pygame.draw.rect(surface, COLOR_ACCENT, rect, width=2, border_radius=10)

        title_surf = self.title_font.render(self.title, True, COLOR_ACCENT)
        surface.blit(title_surf, (self.x + 20, self.y + 14))

        lines = self._wrap_text(self.message, self.width - 40)
        for i, line in enumerate(lines[:4]):
            line_surf = self.text_font.render(line, True, COLOR_WHITE)
            surface.blit(line_surf, (self.x + 20, self.y + 48 + i * 24))

        hint_surf = self.text_font.render("(clique em qualquer lugar para fechar)", True, COLOR_GRAY)
        surface.blit(hint_surf, (self.x + 20, self.y + self.height - 26))
