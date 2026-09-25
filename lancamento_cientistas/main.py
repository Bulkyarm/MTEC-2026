"""
Lançamento das Cientistas
--------------------------
Jogo educativo de lançamento oblíquo (física) em Python + Pygame.

Execução:
    pip install pygame
    python main.py

Controles:
    - Digite o ângulo (graus) e a velocidade inicial nos campos de texto.
    - Clique no "?" ao lado do arqueiro para ver uma dica de fórmula da
      cientista da rodada atual.
    - Clique em "Lançar!" para disparar a flecha.
"""

import sys
import pygame

from settings import (
    SCREEN_WIDTH, SCREEN_HEIGHT, FPS, TITLE, COLOR_BG, COLOR_GROUND,
    COLOR_WHITE, COLOR_ACCENT, COLOR_GRAY, COLOR_SUCCESS, COLOR_FAIL,
    GROUND_Y, MIN_ANGLE, MAX_ANGLE, MIN_VELOCITY, MAX_VELOCITY,
    ROUNDS_PER_PHASE, TOTAL_PHASES,
)
from entities import Archer, Arrow
from ui import InputBox, Button, HelpNPC, DialogBox
from game_state import GameState
from data.scientists import get_hint_for_round
from levels import build_round

# ---------------------------------------------------------------- #
# Estados possíveis do jogo (máquina de estados simples)
STATE_MENU = "menu"
STATE_PHASE_INTRO = "phase_intro"
STATE_AIMING = "aiming"
STATE_LAUNCHED = "launched"
STATE_GALLERY = "gallery"
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

        self.archer = Archer()
        self.dialog = DialogBox(SCREEN_WIDTH, SCREEN_HEIGHT)

        self.buttons = []
        self.input_angle = None
        self.input_velocity = None
        self.help_npc = None
        self.obstacles = []
        self.target = None
        self.arrow = None
        self.result_message = None
        self.last_result_success = False

        self._build_menu_buttons()

    # ------------------------------------------------------------ #
    # Construção de telas
    # ------------------------------------------------------------ #

    def _build_menu_buttons(self):
        cx = SCREEN_WIDTH // 2 - 110
        self.buttons = [
            Button(cx, 260, 220, 50, "Iniciar Jogo", self.font_medium, self._on_start_click),
            Button(cx, 325, 220, 50, "Galeria", self.font_medium, self._on_gallery_click),
            Button(cx, 390, 220, 50, "Sair", self.font_medium, self._on_quit_click),
        ]

    def _build_gallery_buttons(self):
        self.buttons = [
            Button(SCREEN_WIDTH // 2 - 90, SCREEN_HEIGHT - 70, 180, 44,
                   "Voltar ao Menu", self.font_medium, self._on_back_to_menu),
        ]

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
        launch_btn = Button(650, SCREEN_HEIGHT - 92, 140, 46, "Lancar!",
                             self.font_medium, self._on_launch_click)
        self.buttons = [launch_btn]

        launch_x, launch_y = self.archer.get_launch_point()
        self.help_npc = HelpNPC(launch_x - 10, launch_y - 70)

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
        self.state = STATE_PHASE_INTRO
        self._build_phase_intro_buttons()

    def _on_gallery_click(self):
        self.state = STATE_GALLERY
        self._build_gallery_buttons()

    def _on_quit_click(self):
        pygame.quit()
        sys.exit()

    def _on_back_to_menu(self):
        self.state = STATE_MENU
        self._build_menu_buttons()

    def _on_restart_click(self):
        self.game_state.reset()
        self.state = STATE_PHASE_INTRO
        self._build_phase_intro_buttons()

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
        self.arrow = Arrow(launch_x, launch_y, angle, velocity)
        self.state = STATE_LAUNCHED

    # ------------------------------------------------------------ #
    # Fluxo de rodada
    # ------------------------------------------------------------ #

    def _start_round(self):
        scientist = self.game_state.current_scientist()
        self.obstacles, self.target = build_round(
            self.game_state.phase_index, self.game_state.round_index, scientist["name"]
        )
        self._build_aiming_widgets()
        self.state = STATE_AIMING

    def _finish_launch(self, success: bool, reason: str):
        self.last_result_success = success
        self.arrow = None
        if success:
            self.game_state.register_hit()
            scientist = self.game_state.current_scientist()
            self.dialog.show(
                f"Acertou! {scientist['name']}",
                scientist["fact"],
            )
        else:
            self.dialog.show("Nao foi dessa vez...", reason)

    def _advance_after_result(self):
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

    def _draw_aiming_or_launched(self):
        self._draw_background()
        self._draw_hud()

        aim_angle = self.input_angle.get_value() or 45
        self.archer.draw(self.screen, aim_angle_deg=aim_angle)

        for obstacle in self.obstacles:
            obstacle.draw(self.screen)
        self.target.draw(self.screen, self.font_target)

        if self.state == STATE_AIMING:
            self.help_npc.draw(self.screen, self.font_npc)
            self.input_angle.draw(self.screen)
            self.input_velocity.draw(self.screen)
            for button in self.buttons:
                button.draw(self.screen)
        elif self.state == STATE_LAUNCHED and self.arrow:
            self.arrow.draw(self.screen)

    def _draw_gallery(self):
        self._draw_background()
        self._draw_text_center("Galeria de Cientistas", self.font_title, COLOR_ACCENT, 50)

        unlocked = self.game_state.unlocked
        if not unlocked:
            self._draw_text_center("Nenhuma cientista desbloqueada ainda. Va jogar!",
                                    self.font_small, COLOR_GRAY, 120)
        else:
            y = 100
            for entry in unlocked[:8]:
                line = f"{entry['name']} ({entry['phase']})"
                surf = self.font_small.render(line, True, COLOR_WHITE)
                self.screen.blit(surf, (60, y))
                y += 30

        for button in self.buttons:
            button.draw(self.screen)

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

                if self.dialog.visible:
                    was_success_dialog = (self.state == STATE_LAUNCHED)
                    self.dialog.handle_event(event)
                    if not self.dialog.visible and was_success_dialog:
                        self._advance_after_result()
                    continue

                if self.state == STATE_MENU:
                    for button in self.buttons:
                        button.handle_event(event)

                elif self.state == STATE_PHASE_INTRO:
                    for button in self.buttons:
                        button.handle_event(event)

                elif self.state == STATE_AIMING:
                    self.input_angle.handle_event(event)
                    self.input_velocity.handle_event(event)
                    for button in self.buttons:
                        button.handle_event(event)
                    if event.type == pygame.MOUSEBUTTONDOWN and self.help_npc.is_clicked(event.pos):
                        scientist = self.game_state.current_scientist()
                        hint = get_hint_for_round(self.game_state.round_index)
                        self.dialog.show(f"Dica de {scientist['name']}", hint)

                elif self.state == STATE_GALLERY:
                    for button in self.buttons:
                        button.handle_event(event)

                elif self.state == STATE_GAME_OVER:
                    for button in self.buttons:
                        button.handle_event(event)

            # updates que não dependem de eventos
            if self.state == STATE_LAUNCHED and self.arrow and not self.dialog.visible:
                self._update_launched(dt)

            # desenho
            if self.state == STATE_MENU:
                self._draw_menu()
            elif self.state == STATE_PHASE_INTRO:
                self._draw_phase_intro()
            elif self.state in (STATE_AIMING, STATE_LAUNCHED):
                self._draw_aiming_or_launched()
            elif self.state == STATE_GALLERY:
                self._draw_gallery()
            elif self.state == STATE_GAME_OVER:
                self._draw_game_over()

            self.dialog.draw(self.screen)
            pygame.display.flip()


if __name__ == "__main__":
    Game().run()
