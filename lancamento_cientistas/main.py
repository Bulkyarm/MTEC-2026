"""
Lançamento das Cientistas
--------------------------
Jogo educativo de lançamento oblíquo (física) em Python + Pygame.

Execução:
    pip install pygame
    python main.py

Controles:
    - Digite o ângulo (graus) e a velocidade inicial nos campos de texto.
    - As duas dicas aparecem automaticamente antes da terceira tentativa.
    - A calculadora fica disponível na quarta tentativa.
    - Clique em "Lançar!" para disparar a flecha.
"""

import sys
import pygame

from settings import (
    SCREEN_WIDTH, SCREEN_HEIGHT, FPS, TITLE, COLOR_BG, COLOR_GROUND,
    COLOR_WHITE, COLOR_ACCENT, COLOR_GRAY, COLOR_SUCCESS, COLOR_FAIL,
    GROUND_Y, MIN_ANGLE, MAX_ANGLE, MIN_VELOCITY, MAX_VELOCITY,
    ROUNDS_PER_PHASE, TOTAL_PHASES, PIXELS_PER_METER, GRAVITY,
    DEVELOPER_MODE_ENABLED,
)
from entities import Archer, Arrow
from ui import (
    InputBox, Button, DialogBox, TrajectoryCalculator,
    ConfirmationDialog,
)
from game_state import GameState
from data.scientists import PHASES, get_hint_for_round, get_calculation_hint
from levels import build_round

# ---------------------------------------------------------------- #
# Estados possíveis do jogo (máquina de estados simples)
STATE_MENU = "menu"
STATE_PHASE_INTRO = "phase_intro"
STATE_AIMING = "aiming"
STATE_LAUNCHED = "launched"
STATE_DEV_MODE = "developer_mode"
STATE_GAME_OVER = "game_over"


class Game:
    def __init__(self):
        pygame.init()
        pygame.display.set_caption(TITLE)
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        self.clock = pygame.time.Clock()

        self.font_title = pygame.font.SysFont("arial", 42, bold=True)
        self.font_medium = pygame.font.SysFont("arial", 24)
        self.font_small = pygame.font.SysFont("arial", 18)
        self.font_target = pygame.font.SysFont("arial", 14, bold=True)
        self.font_npc = pygame.font.SysFont("arial", 26, bold=True)

        self.state = STATE_MENU
        self.game_state = GameState()
        self.game_state.reset()

        self.archer = Archer()
        self.dialog = DialogBox(SCREEN_WIDTH, SCREEN_HEIGHT)
        self.restart_button = Button(
            SCREEN_WIDTH - 180, 16, 160, 38, "Reiniciar jogo",
            self.font_small, self._request_restart,
        )
        self.quit_button = Button(
            SCREEN_WIDTH - 135, 60, 115, 34, "Fechar jogo",
            self.font_small, self._on_quit_click,
        )
        self.restart_confirmation = ConfirmationDialog(
            SCREEN_WIDTH, SCREEN_HEIGHT, self.font_small,
            self._on_restart_click, self._cancel_restart,
        )
        self.calculator = TrajectoryCalculator(
            SCREEN_WIDTH, SCREEN_HEIGHT, self.font_medium,
            self._apply_calculator_result,
        )

        self.buttons = []
        self.input_angle = None
        self.input_velocity = None
        self.obstacles = []
        self.target = None
        self.arrow = None
        self.attempt_count = 0
        self.result_message = None
        self.last_result_success = False
        self.result_pending = False
        self.layout_index = 0

        self._build_menu_buttons()

    # ------------------------------------------------------------ #
    # Construção de telas
    # ------------------------------------------------------------ #

    def _build_menu_buttons(self):
        cx = SCREEN_WIDTH // 2 - 110
        self.buttons = [
            Button(cx, 260, 220, 50, "Iniciar Jogo", self.font_medium, self._on_start_click),
        ]
        if DEVELOPER_MODE_ENABLED:
            self.buttons.append(Button(
                cx, 325, 220, 50, "Modo Desenvolvedor", self.font_medium,
                self._on_dev_mode_click,
            ))
        quit_y = 390 if DEVELOPER_MODE_ENABLED else 325
        self.buttons.append(
            Button(cx, quit_y, 220, 50, "Sair", self.font_medium, self._on_quit_click)
        )

    def _build_dev_mode_buttons(self):
        self.buttons = []
        for phase_index in range(TOTAL_PHASES):
            row = phase_index // 3
            column = phase_index % 3 if row < 2 else 1
            x = SCREEN_WIDTH // 2 - 354 + column * 244
            y = 150 + row * 112
            self.buttons.append(Button(
                x, y, 220, 50, f"Fase {phase_index + 1}", self.font_medium,
                lambda phase_index=phase_index: self._select_dev_phase(phase_index),
            ))
        self.buttons.append(Button(
            SCREEN_WIDTH // 2 - 90, SCREEN_HEIGHT - 70, 180, 44,
            "Voltar ao Menu", self.font_medium, self._on_back_to_menu,
        ))

    def _build_phase_intro_buttons(self):
        self.buttons = [
            Button(SCREEN_WIDTH // 2 - 90, SCREEN_HEIGHT - 100, 180, 50,
                   "Continuar", self.font_medium, self._start_round),
        ]

    def _build_aiming_widgets(self):
        self.input_angle = InputBox(
            300, SCREEN_HEIGHT - 90, 120, 40, label="Angulo (graus)",
            initial_text="45", font=self.font_medium,
            min_value=MIN_ANGLE, max_value=MAX_ANGLE,
        )
        self.input_velocity = InputBox(
            470, SCREEN_HEIGHT - 90, 120, 40, label="Velocidade inicial (m/s)",
            initial_text="20", font=self.font_medium,
            min_value=MIN_VELOCITY, max_value=MAX_VELOCITY,
        )
        self._refresh_aiming_buttons()

    def _refresh_aiming_buttons(self):
        launch_btn = Button(650, SCREEN_HEIGHT - 92, 140, 46, "Lancar!",
                            self.font_medium, self._on_launch_click)
        self.buttons = [launch_btn]
        if self.attempt_count >= 3:
            self.buttons.append(Button(
                810, SCREEN_HEIGHT - 92, 170, 46, "Calculadora",
                self.font_medium, self._open_calculator,
            ))

    def _build_game_over_buttons(self):
        self.buttons = [
            Button(SCREEN_WIDTH // 2 - 130, 360, 260, 48,
                   "Jogar Novamente", self.font_medium, self._on_restart_click),
            Button(SCREEN_WIDTH // 2 - 130, 420, 260, 48,
                   "Voltar ao Menu", self.font_medium, self._on_back_to_menu),
        ]

    # ------------------------------------------------------------ #
    # Callbacks de botões
    # ------------------------------------------------------------ #

    def _on_start_click(self):
        if self.game_state.is_game_complete():
            self.game_state.reset()
            self.layout_index = 0
        self.state = STATE_PHASE_INTRO
        self._build_phase_intro_buttons()

    def _on_dev_mode_click(self):
        if not DEVELOPER_MODE_ENABLED:
            return
        self.state = STATE_DEV_MODE
        self._build_dev_mode_buttons()

    def _select_dev_phase(self, phase_index):
        if not DEVELOPER_MODE_ENABLED:
            return
        self.game_state.phase_index = phase_index
        self.game_state.round_index = 0
        self.arrow = None
        self.result_pending = False
        self.calculator.close()
        self._start_round()

    def _on_quit_click(self):
        pygame.quit()
        sys.exit()

    def _on_back_to_menu(self):
        self.state = STATE_MENU
        self._build_menu_buttons()

    def _on_restart_click(self):
        self.restart_confirmation.hide()
        self.game_state.reset()
        self.layout_index = 0
        self.arrow = None
        self.calculator.close()
        self.state = STATE_PHASE_INTRO
        self._build_phase_intro_buttons()

    def _request_restart(self):
        self.restart_confirmation.show()

    def _cancel_restart(self):
        self.restart_confirmation.hide()

    def _on_launch_click(self):
        if not (self.input_angle.is_valid() and self.input_velocity.is_valid()):
            self.dialog.show(
                "Valores invalidos",
                f"Informe um angulo entre {MIN_ANGLE} e {MAX_ANGLE} graus e uma "
                f"velocidade entre {MIN_VELOCITY} e {MAX_VELOCITY} m/s.",
            )
            return
        angle = self.input_angle.get_value()
        velocity = self.input_velocity.get_value()
        launch_x, launch_y = self.archer.get_launch_point()
        self.attempt_count += 1
        self.archer.fire()
        self.arrow = Arrow(launch_x, launch_y, angle, velocity)
        if self.game_state.phase_index == 6:
            self.target.start_falling()
        self.state = STATE_LAUNCHED

    def _open_calculator(self):
        launch_x, launch_y = self.archer.get_launch_point()
        distance_m = (self.target.x - launch_x) / PIXELS_PER_METER
        height_difference_m = (launch_y - self.target.y) / PIXELS_PER_METER
        angle = self.input_angle.get_value() or 45
        velocity = self.input_velocity.get_value() or 20
        self.calculator.show(distance_m, height_difference_m, angle, velocity)

    def _apply_calculator_result(self, mode, known_value, result_kind, result):
        known_input = self.input_angle if mode == "speed" else self.input_velocity
        result_input = self.input_velocity if result_kind == "speed" else self.input_angle
        for input_box, value in ((known_input, known_value), (result_input, result)):
            input_box.text = f"{value:.2f}"
            input_box.active = False
            input_box.replace_on_next_input = False

    # ------------------------------------------------------------ #
    # Fluxo de rodada
    # ------------------------------------------------------------ #

    def _start_round(self):
        scientist = self.game_state.current_scientist()
        self.attempt_count = 0
        self.layout_index += 1
        self.obstacles, self.target = build_round(
            self.game_state.phase_index, self.game_state.round_index, scientist["name"],
            seed=self.layout_index,
        )
        self._build_aiming_widgets()
        self.state = STATE_AIMING

    def _finish_launch(self, success: bool, reason: str):
        self.last_result_success = success
        self.result_pending = True
        self.arrow = None
        if success:
            self.game_state.register_hit()
            scientist = self.game_state.current_scientist()
            self.dialog.show(
                f"Acertou! {scientist['name']}",
                scientist["fact"],
            )
        else:
            if self.attempt_count >= 4:
                if self.game_state.phase_index == 0:
                    reason += " O jogo sera reiniciado."
                else:
                    reason += " Voce voltara ao inicio da fase anterior."
            self.dialog.show("Tente novamente", reason)

    def _advance_after_result(self):
        self.result_pending = False
        if not self.last_result_success:
            if self.attempt_count >= 4:
                if self.game_state.phase_index == 0:
                    self.game_state.reset()
                    self.layout_index = 0
                else:
                    self.game_state.return_to_previous_phase()
                self.state = STATE_PHASE_INTRO
                self._build_phase_intro_buttons()
                return

            self.state = STATE_AIMING
            self._refresh_aiming_buttons()
            if self.attempt_count == 2:
                launch_x, launch_y = self.archer.get_launch_point()
                distance_m = (self.target.x - launch_x) / PIXELS_PER_METER
                height_difference_m = (launch_y - self.target.y) / PIXELS_PER_METER
                scientist = self.game_state.current_scientist()
                hints = (
                    f"1. {get_hint_for_round(self.game_state.round_index)}\n\n"
                    f"2. {get_calculation_hint(distance_m, height_difference_m)}"
                )
                self.dialog.show(f"Dicas de {scientist['name']}", hints)
            return

        still_playing = self.game_state.advance_round()
        if not still_playing:
            self.state = STATE_GAME_OVER
            self._build_game_over_buttons()
        elif self.game_state.round_index == 0:
            self.state = STATE_PHASE_INTRO
            self._build_phase_intro_buttons()
        else:
            self._start_round()

    # ------------------------------------------------------------ #
    # Update / física da flecha em voo
    # ------------------------------------------------------------ #

    def _update_launched(self, dt):
        self.arrow.update(dt)
        if self.game_state.phase_index == 6:
            self.target.update(dt)
        px, py = self.arrow.get_pos()

        # colisão com obstáculo
        for obstacle in self.obstacles:
            if obstacle.collides_with_point(px, py):
                self._finish_launch(False, "A flecha bateu em um obstaculo. Tente um "
                                            "angulo ou velocidade diferente.")
                return

        # colisão com o alvo
        if self.target.collides_with_point(px, py):
            self.target.hit = True
            self._finish_launch(True, "")
            return

        # saiu da tela ou caiu no chao sem acertar nada
        if px > SCREEN_WIDTH or px < 0:
            self._finish_launch(False, "A flecha saiu da tela sem acertar o alvo.")
        elif py >= GROUND_Y and self.arrow.projectile.t > 0.05:
            self._finish_launch(False, "A flecha caiu no chao antes de chegar ao alvo.")

    # ------------------------------------------------------------ #
    # Desenho
    # ------------------------------------------------------------ #

    def _draw_background(self):
        self.screen.fill(COLOR_BG)
        pygame.draw.rect(self.screen, COLOR_GROUND, (0, GROUND_Y, SCREEN_WIDTH, SCREEN_HEIGHT - GROUND_Y))

    def _draw_text_center(self, text, font, color, y):
        surf = font.render(text, True, color)
        self.screen.blit(surf, surf.get_rect(center=(SCREEN_WIDTH // 2, y)))

    def _draw_menu(self):
        self._draw_background()
        self._draw_text_center("Lancamento das Cientistas", self.font_title, COLOR_ACCENT, 140)
        self._draw_text_center("Aprenda lancamento obliquo acertando alvos com flechas",
                                self.font_small, COLOR_GRAY, 190)
        for button in self.buttons:
            button.draw(self.screen)

    def _draw_phase_intro(self):
        self._draw_background()
        phase = self.game_state.current_phase()
        self._draw_text_center(f"Fase {self.game_state.phase_index + 1} de {TOTAL_PHASES}",
                                self.font_medium, COLOR_GRAY, 200)
        self._draw_text_center(phase["area"], self.font_title, COLOR_ACCENT, 260)
        self._draw_text_center("Acerte as bolhas com o nome das cientistas dessa area!",
                                self.font_small, COLOR_WHITE, 320)
        self.restart_button.draw(self.screen)
        for button in self.buttons:
            button.draw(self.screen)

    def _draw_hud(self):
        score_surf = self.font_medium.render(f"Pontuacao: {self.game_state.score}", True, COLOR_WHITE)
        self.screen.blit(score_surf, (20, 20))
        progress_surf = self.font_small.render(
            f"Fase {self.game_state.phase_index + 1}/{TOTAL_PHASES}  -  "
            f"Rodada {self.game_state.round_index + 1}/{ROUNDS_PER_PHASE}",
            True, COLOR_GRAY,
        )
        self.screen.blit(progress_surf, (20, 52))
        attempts_surf = self.font_small.render(
            f"Tentativa {min(self.attempt_count + 1, 4)}/4",
            True, COLOR_GRAY,
        )
        self.screen.blit(attempts_surf, (20, 78))
        self.restart_button.draw(self.screen)

    def _draw_aiming_or_launched(self):
        self._draw_background()
        self._draw_hud()

        aim_angle = self.input_angle.get_value() or 45
        self.archer.draw(self.screen, aim_angle_deg=aim_angle)

        for obstacle in self.obstacles:
            obstacle.draw(self.screen)
        self.target.draw(self.screen, self.font_target)

        gravity_text = f"g = {GRAVITY:.1f} m/s^2"
        distance_surf = self.font_small.render(gravity_text, True, COLOR_WHITE)
        self.screen.blit(distance_surf, (SCREEN_WIDTH // 2 - distance_surf.get_width() // 2, 82))

        if self.state == STATE_AIMING:
            # self.help_npc.draw(self.screen, self.font_npc)
            # self.calculation_help_npc.draw(self.screen, self.font_npc)
            self.input_angle.draw(self.screen)
            self.input_velocity.draw(self.screen)
            for button in self.buttons:
                button.draw(self.screen)
        elif self.state == STATE_LAUNCHED and self.arrow:
            self.arrow.draw(self.screen)

    def _draw_dev_mode(self):
        self._draw_background()
        self._draw_text_center("Modo Desenvolvedor", self.font_title, COLOR_ACCENT, 65)
        self._draw_text_center("Selecione uma fase", self.font_small, COLOR_GRAY, 108)

        for phase_index, phase in enumerate(PHASES):
            button = self.buttons[phase_index]
            button.draw(self.screen)
            label = self.font_small.render(phase["area"], True, COLOR_WHITE)
            self.screen.blit(label, label.get_rect(center=(button.rect.centerx, button.rect.bottom + 18)))

        self.buttons[-1].draw(self.screen)

    def _draw_game_over(self):
        self._draw_background()
        self._draw_text_center("Parabens! Voce completou o jogo!", self.font_title, COLOR_SUCCESS, 220)
        self._draw_text_center(f"Pontuacao final: {self.game_state.score}",
                                self.font_medium, COLOR_WHITE, 280)
        self._draw_text_center(f"Cientistas desbloqueadas: {len(self.game_state.unlocked)}",
                                self.font_small, COLOR_GRAY, 315)
        for button in self.buttons:
            button.draw(self.screen)

    # ------------------------------------------------------------ #
    # Loop principal
    # ------------------------------------------------------------ #

    def run(self):
        while True:
            dt = self.clock.tick(FPS) / 1000.0

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()

                if self.state != STATE_MENU:
                    self.quit_button.handle_event(event)

                if self.dialog.visible:
                    self.dialog.handle_event(event)
                    if not self.dialog.visible and self.result_pending:
                        self._advance_after_result()
                    continue

                if self.restart_confirmation.visible:
                    self.restart_confirmation.handle_event(event)
                    continue

                if self.state == STATE_MENU:
                    for button in self.buttons:
                        button.handle_event(event)

                elif self.state == STATE_PHASE_INTRO:
                    for button in self.buttons:
                        button.handle_event(event)
                    self.restart_button.handle_event(event)

                elif self.state == STATE_AIMING:
                    if self.calculator.visible:
                        self.calculator.handle_event(event)
                    else:
                        self.input_angle.handle_event(event)
                        self.input_velocity.handle_event(event)
                        for button in self.buttons:
                            button.handle_event(event)
                        self.restart_button.handle_event(event)

                elif self.state == STATE_LAUNCHED:
                    self.restart_button.handle_event(event)

                elif self.state == STATE_DEV_MODE:
                    for button in self.buttons:
                        button.handle_event(event)

                elif self.state == STATE_GAME_OVER:
                    for button in self.buttons:
                        button.handle_event(event)

            # updates que não dependem de eventos
            self.archer.update(dt, aiming=self.state == STATE_AIMING)
            self.calculator.update(dt)
            if self.state == STATE_LAUNCHED and self.arrow and not self.dialog.visible:
                self._update_launched(dt)

            # desenho
            if self.state == STATE_MENU:
                self._draw_menu()
            elif self.state == STATE_PHASE_INTRO:
                self._draw_phase_intro()
            elif self.state in (STATE_AIMING, STATE_LAUNCHED):
                self._draw_aiming_or_launched()
            elif self.state == STATE_DEV_MODE:
                self._draw_dev_mode()
            elif self.state == STATE_GAME_OVER:
                self._draw_game_over()

            self.dialog.draw(self.screen)
            self.calculator.draw(self.screen)
            self.restart_confirmation.draw(self.screen)
            if self.state != STATE_MENU:
                self.quit_button.draw(self.screen)
            pygame.display.flip()


if __name__ == "__main__":
    Game().run()
