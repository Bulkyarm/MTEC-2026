"""
Componentes de interface reutilizáveis: caixa de input numérico, botão
clicável e caixa de diálogo (usada tanto para a dica da cientista quanto
para o feedback de acerto/erro).
"""

import pygame
from settings import (
    COLOR_INPUT_BG, COLOR_INPUT_ACTIVE, COLOR_WHITE, COLOR_GRAY,
    COLOR_BUTTON, COLOR_BUTTON_HOVER, COLOR_BLACK, COLOR_DIALOG_BG,
    COLOR_ACCENT, COLOR_SUCCESS, COLOR_FAIL, MIN_ANGLE, MAX_ANGLE,
    MIN_VELOCITY, MAX_VELOCITY, GRAVITY,
)
from physics import (
    solve_initial_speed, solve_launch_angle,
    build_speed_calculation_steps, build_angle_calculation_steps,
)


class InputBox:
    """Campo de texto simples, aceitando apenas números (inteiros ou decimais)."""

    def __init__(self, x, y, w, h, label="", initial_text="", font=None,
                 min_value=None, max_value=None):
        self.rect = pygame.Rect(x, y, w, h)
        self.label = label
        self.text = initial_text
        self.active = False
        self.replace_on_next_input = False
        self.font = font or pygame.font.SysFont("arial", 22)
        self.label_font = pygame.font.SysFont("arial", 18)
        self.min_value = min_value
        self.max_value = max_value

    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            self.active = self.rect.collidepoint(event.pos)
            self.replace_on_next_input = self.active
        elif event.type == pygame.KEYDOWN and self.active:
            if event.key == pygame.K_BACKSPACE:
                self.replace_on_next_input = False
                self.text = self.text[:-1]
            elif event.key in (pygame.K_RETURN, pygame.K_TAB):
                self.active = False
            elif event.unicode.isdigit() or (event.unicode == "." and "." not in self.text):
                if self.replace_on_next_input:
                    self.text = event.unicode
                    self.replace_on_next_input = False
                else:
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

    def __init__(self, x, y, radius=26, symbol="?"):
        self.x = x
        self.y = y
        self.radius = radius
        self.symbol = symbol
        self.rect = pygame.Rect(x - radius, y - radius, radius * 2, radius * 2)

    def is_clicked(self, pos):
        return self.rect.collidepoint(pos)

    def draw(self, surface, font):
        pygame.draw.circle(surface, COLOR_ACCENT, (self.x, self.y), self.radius)
        pygame.draw.circle(surface, COLOR_BLACK, (self.x, self.y), self.radius, width=2)
        q_surf = font.render(self.symbol, True, COLOR_BLACK)
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
        self.height = 208
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
        for i, line in enumerate(lines[:6]):
            line_surf = self.text_font.render(line, True, COLOR_WHITE)
            surface.blit(line_surf, (self.x + 20, self.y + 48 + i * 24))

        hint_surf = self.text_font.render("(clique em qualquer lugar para fechar)", True, COLOR_GRAY)
        surface.blit(hint_surf, (self.x + 20, self.y + self.height - 26))


class ConfirmationDialog:
    """Confirmacao modal para acoes que reiniciam a partida."""

    def __init__(self, screen_width, screen_height, font, on_confirm, on_cancel):
        self.rect = pygame.Rect(0, 0, 440, 210)
        self.rect.center = (screen_width // 2, screen_height // 2)
        self.title_font = pygame.font.SysFont("arial", 26, bold=True)
        self.message_font = pygame.font.SysFont("arial", 18)
        self.visible = False
        self.confirm_button = Button(
            self.rect.x + 225, self.rect.bottom - 62, 180, 42,
            "Reiniciar", font, on_confirm,
        )
        self.cancel_button = Button(
            self.rect.x + 35, self.rect.bottom - 62, 160, 42,
            "Cancelar", font, on_cancel,
        )

    def show(self):
        self.visible = True

    def hide(self):
        self.visible = False

    def handle_event(self, event):
        if not self.visible:
            return
        self.confirm_button.handle_event(event)
        self.cancel_button.handle_event(event)

    def draw(self, surface):
        if not self.visible:
            return
        shade = pygame.Surface(surface.get_size(), pygame.SRCALPHA)
        shade.fill((0, 0, 0, 190))
        surface.blit(shade, (0, 0))
        pygame.draw.rect(surface, COLOR_DIALOG_BG, self.rect, border_radius=8)
        pygame.draw.rect(surface, COLOR_ACCENT, self.rect, width=2, border_radius=8)
        title = self.title_font.render("Reiniciar jogo?", True, COLOR_ACCENT)
        surface.blit(title, (self.rect.x + 35, self.rect.y + 28))
        message = self.message_font.render(
            "O progresso atual sera apagado.", True, COLOR_WHITE,
        )
        surface.blit(message, (self.rect.x + 35, self.rect.y + 78))
        self.cancel_button.draw(surface)
        self.confirm_button.draw(surface)


class TrajectoryCalculator:
    """Calcula a variavel desconhecida da equacao da trajetoria."""

    def __init__(self, screen_width, screen_height, font, on_apply):
        self.width = 900
        self.height = 580
        self.x = (screen_width - self.width) // 2
        self.y = (screen_height - self.height) // 2
        self.font = font
        self.small_font = pygame.font.SysFont("arial", 16)
        self.calculation_font = pygame.font.SysFont("arial", 14)
        self.title_font = pygame.font.SysFont("arial", 26, bold=True)
        self.on_apply = on_apply
        self.visible = False
        self.mode = "speed"
        self.horizontal_distance = 0.0
        self.height_difference = 0.0
        self.default_angle = "45"
        self.default_speed = "20"
        self.result = None
        self.result_kind = None
        self.result_message = ""
        self.result_is_valid = False
        self.is_calculating = False
        self.calculation_duration = 2.4
        self.calculation_elapsed = 0.0
        self.pending_value = None
        self.calculation_steps = []
        self.calculation_step_durations = []
        self.calculation_character_interval = 0.025
        self.calculation_pause = 0.35
        self.calculation_duration = 0.0

        self.input_box = InputBox(
            self.x + 35, self.y + 148, 220, 46,
            label="Angulo informado (graus)", initial_text=self.default_angle,
            font=font, min_value=MIN_ANGLE, max_value=MAX_ANGLE,
        )
        self.calculate_button = Button(
            self.x + 285, self.y + 148, 170, 46, "Calcular", font,
            self.start_calculation,
        )
        self.speed_mode_button = Button(
            self.x + 35, self.y + 92, 400, 42, "Angulo -> velocidade", font,
            lambda: self.set_mode("speed"),
        )
        self.angle_mode_button = Button(
            self.x + 465, self.y + 92, 400, 42, "Velocidade -> angulo", font,
            lambda: self.set_mode("angle"),
        )
        self.apply_button = Button(
            self.x + 620, self.y + 530, 245, 44, "Usar no campo de jogo", font,
            self.apply_result,
        )
        self.close_button = Button(
            self.x + 35, self.y + 530, 140, 44, "Fechar", font,
            self.close,
        )

    def show(self, horizontal_distance, height_difference, angle, speed):
        self.horizontal_distance = horizontal_distance
        self.height_difference = height_difference
        self.default_angle = f"{angle:g}"
        self.default_speed = f"{speed:g}"
        self.visible = True
        self.set_mode("speed")

    def set_mode(self, mode):
        self.mode = mode
        self.result = None
        self.result_kind = None
        self.result_message = ""
        self.result_is_valid = False
        self.is_calculating = False
        self.pending_value = None
        self.calculation_steps = []
        self.calculation_step_durations = []
        if mode == "speed":
            self.input_box.label = "Angulo informado (graus)"
            self.input_box.min_value = MIN_ANGLE
            self.input_box.max_value = MAX_ANGLE
            self.input_box.text = self.default_angle
        else:
            self.input_box.label = "Velocidade informada (m/s)"
            self.input_box.min_value = MIN_VELOCITY
            self.input_box.max_value = MAX_VELOCITY
            self.input_box.text = self.default_speed
        self.input_box.active = False
        self.input_box.replace_on_next_input = False

    def start_calculation(self):
        self.calculation_steps = []
        self.calculation_step_durations = []
        value = self.input_box.get_value()
        if value is None or not self.input_box.is_valid():
            self.calculate()
            return

        try:
            if self.mode == "speed":
                self.calculation_steps = build_speed_calculation_steps(
                    self.horizontal_distance, self.height_difference, value,
                )
            else:
                self.calculation_steps = build_angle_calculation_steps(
                    self.horizontal_distance, self.height_difference, value,
                )
        except ValueError as error:
            self.calculation_steps = []
            self.result = None
            self.result_is_valid = False
            self.result_message = str(error)
            return

        self.result = None
        self.result_kind = None
        self.result_message = ""
        self.result_is_valid = False
        self.pending_value = value
        self.calculation_elapsed = 0.0
        self.calculation_step_durations = [
            len(step) * self.calculation_character_interval + self.calculation_pause
            for step in self.calculation_steps
        ]
        self.calculation_duration = sum(self.calculation_step_durations)
        self.is_calculating = True

    def update(self, dt):
        if not self.is_calculating:
            return
        self.calculation_elapsed = min(
            self.calculation_elapsed + dt, self.calculation_duration,
        )
        if self.calculation_elapsed >= self.calculation_duration:
            value = self.pending_value
            self.is_calculating = False
            self.pending_value = None
            self.calculate(value)

    def calculate(self, value=None):
        if value is None:
            value = self.input_box.get_value()
        if value is None or not self.input_box.is_valid():
            self.result = None
            self.result_is_valid = False
            if self.mode == "speed":
                self.result_message = f"Informe um angulo entre {MIN_ANGLE} e {MAX_ANGLE} graus."
            else:
                self.result_message = f"Informe uma velocidade entre {MIN_VELOCITY} e {MAX_VELOCITY} m/s."
            return

        try:
            if self.mode == "speed":
                result = solve_initial_speed(
                    self.horizontal_distance, self.height_difference, value,
                )
                self.result_kind = "speed"
                self.result_message = f"Velocidade inicial: {result:.2f} m/s"
                self.result_is_valid = MIN_VELOCITY <= result <= MAX_VELOCITY
                if not self.result_is_valid:
                    self.result_message += f" (fora do limite de {MIN_VELOCITY} a {MAX_VELOCITY} m/s)"
            else:
                result = solve_launch_angle(
                    self.horizontal_distance, self.height_difference, value,
                )
                self.result_kind = "angle"
                self.result_message = f"Angulo: {result:.2f} graus"
                self.result_is_valid = MIN_ANGLE <= result <= MAX_ANGLE
                if not self.result_is_valid:
                    self.result_message += f" (fora do limite de {MIN_ANGLE} a {MAX_ANGLE} graus)"
            self.result = result
        except ValueError as error:
            self.result = None
            self.result_kind = None
            self.result_is_valid = False
            self.result_message = str(error)

    def apply_result(self):
        if self.result_is_valid and self.result is not None:
            self.on_apply(
                self.mode, self.input_box.get_value(),
                self.result_kind, self.result,
            )
            self.close()

    def close(self):
        self.visible = False
        self.is_calculating = False
        self.pending_value = None

    def handle_event(self, event):
        if not self.visible:
            return
        if self.is_calculating:
            self.close_button.handle_event(event)
            return
        self.input_box.handle_event(event)
        for button in (
            self.speed_mode_button, self.angle_mode_button,
            self.calculate_button, self.apply_button, self.close_button,
        ):
            if button is self.apply_button and not self.result_is_valid:
                continue
            button.handle_event(event)

    def draw(self, surface):
        if not self.visible:
            return

        shade = pygame.Surface(surface.get_size(), pygame.SRCALPHA)
        shade.fill((0, 0, 0, 175))
        surface.blit(shade, (0, 0))
        panel = pygame.Rect(self.x, self.y, self.width, self.height)
        pygame.draw.rect(surface, COLOR_DIALOG_BG, panel, border_radius=8)
        pygame.draw.rect(surface, COLOR_ACCENT, panel, width=2, border_radius=8)

        title = self.title_font.render("Calculadora de trajetoria", True, COLOR_ACCENT)
        surface.blit(title, (self.x + 35, self.y + 20))
        formula = self.small_font.render(
            "y = x*tan(theta) - (g*x^2)/(2*v0^2*cos^2(theta))",
            True, COLOR_WHITE,
        )
        surface.blit(formula, (self.x + 35, self.y + 48))
        values = self.small_font.render(
            f"x = {self.horizontal_distance:.1f} m    y = {self.height_difference:+.1f} m    g = {GRAVITY:.1f} m/s^2",
            True, COLOR_GRAY,
        )
        surface.blit(values, (self.x + 35, self.y + 70))

        for button, selected in (
            (self.speed_mode_button, self.mode == "speed"),
            (self.angle_mode_button, self.mode == "angle"),
        ):
            pygame.draw.rect(
                surface, COLOR_BUTTON_HOVER if selected else COLOR_INPUT_BG,
                button.rect, border_radius=6,
            )
            pygame.draw.rect(surface, COLOR_ACCENT if selected else COLOR_GRAY,
                             button.rect, width=2, border_radius=6)
            text = button.font.render(button.text, True, COLOR_WHITE)
            surface.blit(text, text.get_rect(center=button.rect.center))

        self.input_box.draw(surface)
        if not self.is_calculating:
            self.calculate_button.draw(surface)
        if self.calculation_steps:
            elapsed = self.calculation_elapsed
            visible_steps = []
            for index, (step, step_duration) in enumerate(zip(
                self.calculation_steps, self.calculation_step_durations,
            )):
                character_duration = len(step) * self.calculation_character_interval
                if self.is_calculating and elapsed < step_duration:
                    visible_characters = min(
                        len(step), int(elapsed / self.calculation_character_interval),
                    )
                    visible_steps.append((step[:visible_characters], True))
                    break

                visible_steps.append((step, False))
                if self.is_calculating:
                    elapsed -= step_duration
            for index, (text, is_current) in enumerate(visible_steps):
                step_surface = self.calculation_font.render(
                    text, True, COLOR_ACCENT if is_current else COLOR_WHITE,
                )
                surface.blit(step_surface, (self.x + 35, self.y + 205 + index * 16))
        if self.is_calculating:
            progress_rect = pygame.Rect(self.x + 35, self.y + 523, 830, 7)
            pygame.draw.rect(surface, COLOR_INPUT_BG, progress_rect, border_radius=4)
            fill_rect = progress_rect.copy()
            fill_rect.width = round(progress_rect.width * self.calculation_elapsed / self.calculation_duration)
            if fill_rect.width:
                pygame.draw.rect(surface, COLOR_ACCENT, fill_rect, border_radius=4)
        if self.result_message and not self.is_calculating and not self.result_is_valid:
            message_color = COLOR_FAIL
            message_y = self.y + 205 + len(self.calculation_steps) * 16 + 4
            message_lines = []
            current_line = ""
            for word in self.result_message.split():
                candidate = f"{current_line} {word}".strip()
                if (current_line and
                        self.calculation_font.size(candidate)[0] > self.width - 70):
                    message_lines.append(current_line)
                    current_line = word
                else:
                    current_line = candidate
            if current_line:
                message_lines.append(current_line)

            for line in message_lines:
                message = self.calculation_font.render(line, True, message_color)
                surface.blit(message, (self.x + 35, message_y))
                message_y += self.calculation_font.get_linesize()
        self.close_button.draw(surface)
        if self.result_is_valid:
            self.apply_button.draw(surface)
