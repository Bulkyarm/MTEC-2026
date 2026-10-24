"""
Lançamento das Cientistas
--------------------------
Jogo educativo de lançamento oblíquo (física) em Python + Pygame.

Execução:
    pip install -r requirements.txt
    python main.py

Controles:
    - Digite o ângulo (graus) e a velocidade inicial nos campos de texto.
    - As duas dicas aparecem automaticamente antes da terceira tentativa.
    - A calculadora fica disponível na quarta tentativa.
    - Clique em "Lançar!" para disparar a flecha.
"""

import os
import sys
import math
import pygame

from settings import (
    SCREEN_WIDTH, SCREEN_HEIGHT, FPS, TITLE, COLOR_BG, COLOR_GROUND,
    COLOR_WHITE, COLOR_ACCENT, COLOR_GRAY, COLOR_SUCCESS, COLOR_FAIL,
    GROUND_Y, MIN_ANGLE, MAX_ANGLE, MIN_VELOCITY, MAX_VELOCITY,
    ROUNDS_PER_PHASE, TOTAL_PHASES, PIXELS_PER_METER, GRAVITY,
    DEVELOPER_MODE_ENABLED,
)
from entities import Archer, Arrow, Obstacle
from phase_2_assets import load_phase_2_assets
from phase_3_assets import load_phase_3_assets
from phase_4_assets import load_phase_4_assets
from phase_5_assets import load_phase_5_assets
from phase_6_assets import load_phase_6_assets
from phase_7_assets import load_phase_7_assets
from ui import (
    InputBox, Button, DialogBox, TrajectoryCalculator,
    ConfirmationDialog,
)
from game_state import GameState
from game_audio import GameAudio
from data.scientists import PHASES, get_hint_for_round, get_calculation_hint
from levels import FIXED_SCENARIOS, PHASE_INTROS, build_round

PHASE_1_BUTTON_RADIUS = 18
PHASE_3_BUTTON_RADIUS = 20
PHASE_1_BUTTON_PRESS_DURATION = 0.12
PHASE_1_BUTTON_RETURN_DURATION = 0.12
PHASE_1_BUTTON_ANIMATION_DURATION = 0.42
PHASE_1_WALK_DURATION = 1.2
PHASE_1_WALK_FRAME_RATE = 10
PHASE_2_CHALK_FALL_DURATION = 0.65
PHASE_2_WALK_DURATION = 1.8
PHASE_2_PICKUP_DURATION = 0.55
PHASE_2_WRITE_DURATION = 1.8
PHASE_2_WALK_FRAME_RATE = 8
PHASE_2_SHOOT_DURATION = 0.22
PHASE_2_BOW_LAUNCH_ANCHOR = (0.80, 0.43)
PHASE_2_FORMULA = "Q = Σ pᵢ δqᵢ"
PHASE_3_WALK_FRAME_RATE = 8
PHASE_5_IMPACT_DURATION = 0.35
PHASE_5_SPLIT_DURATION = 0.9
PHASE_5_ENERGY_DURATION = 1.2
PHASE_6_WALK_FRAME_RATE = 8
PHASE_7_WEB_ATTACH_DURATION = 0.65
PHASE_7_BRANCH_ANCHOR = (836, 156)
OPENING_STORY_PARTS = (
    "Olá! Eu sou Alex. Gosto de aventuras, enigmas e desafios que parecem "
    "impossíveis, principalmente quando tenho meu arco e minhas flechas por "
    "perto. Mas a missão que recebi hoje é diferente de qualquer outra.",
    "Minha professora de História, Helena, está preparando uma aula sobre "
    "mulheres que transformaram a ciência. Ela quer mostrar como as ideias "
    "dessas cientistas ajudaram a mudar a maneira como entendemos o mundo.",
    "Para me ajudar, Helena me mostrou um caderno cheio de anotações, desenhos "
    "e pistas. Ele não guarda descobertas perdidas: reúne perguntas e desafios "
    "inspirados no trabalho de grandes cientistas. Cada página apresenta uma "
    "cientista e uma ideia importante que precisamos conhecer.",
    "Só que há um problema: para avançar pelas páginas, é preciso superar os "
    "desafios que protegem cada pista. Alguns alvos parecem distantes, outros "
    "estão em lugares difíceis de alcançar. Um lançamento mal calculado pode "
    "nos obrigar a tentar de novo!",
    "A primeira pista nos leva até Marie Curie, uma cientista que dedicou a "
    "vida a investigar fenômenos invisíveis. Seus estudos sobre a "
    "radioatividade abriram caminhos importantes para a ciência e ajudaram "
    "outras pessoas a explorar os mistérios da matéria.",
    "Depois, nossa jornada seguirá por outras histórias extraordinárias: "
    "ideias matemáticas que revelam relações profundas na natureza, imagens "
    "que ajudaram a investigar o DNA e invenções que anteciparam "
    "possibilidades da computação.",
    "Cada desafio vai exigir atenção e raciocínio. Observe a distância, "
    "escolha o ângulo e calcule a força do lançamento. A trajetória da flecha "
    "depende das suas decisões — e cada alvo acertado nos aproxima de uma "
    "nova pista para a aula da professora Helena.",
    "Nossa missão é percorrer todas as páginas, conhecer as cientistas e "
    "descobrir por que suas contribuições são tão importantes. Quando "
    "terminarmos, Helena terá uma aula cheia de histórias, perguntas e "
    "descobertas para compartilhar. Preparado, explorador? A primeira pista "
    "está esperando!",
)
OPENING_STORY_PART_DURATION = 12.0
OPENING_STORY_TYPING_SPEED = 30
# ---------------------------------------------------------------- #
# Estados possíveis do jogo (máquina de estados simples)
STATE_MENU = "menu"
STATE_OPENING_STORY = "opening_story"
STATE_PHASE_INTRO = "phase_intro"
STATE_AIMING = "aiming"
STATE_LAUNCHED = "launched"
STATE_DEV_MODE = "developer_mode"
STATE_PHASE_COMPLETE = "phase_complete"
STATE_GAME_OVER = "game_over"


class Game:
    def __init__(self):
        pygame.init()
        self.audio = GameAudio()
        pygame.display.set_caption(TITLE)
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        self.clock = pygame.time.Clock()

        self.font_title = pygame.font.SysFont("arial", 42, bold=True)
        self.font_medium = pygame.font.SysFont("arial", 24)
        self.font_small = pygame.font.SysFont("arial", 18)
        self.font_target = pygame.font.SysFont("arial", 14, bold=True)
        self.font_npc = pygame.font.SysFont("arial", 26, bold=True)

        assets_dir = os.path.join(os.path.dirname(__file__), "assets")
        terrain_sheet = pygame.image.load(
            os.path.join(assets_dir, "cenarioPadrao.png")
        ).convert()
        forest_rect = pygame.Rect(134, 61, 714, 428)
        forest_scene = terrain_sheet.subsurface(forest_rect)
        forest_scale = max(
            SCREEN_WIDTH / forest_rect.width,
            SCREEN_HEIGHT / forest_rect.height,
        )
        forest_size = (
            round(forest_rect.width * forest_scale),
            round(forest_rect.height * forest_scale),
        )
        scaled_forest = pygame.transform.scale(forest_scene, forest_size)
        self.phase_background = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
        self.phase_background.blit(
            scaled_forest,
            scaled_forest.get_rect(
                center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2)
            ),
        )
        Obstacle.set_terrain_textures(
            terrain_sheet.subsurface(Obstacle.TERRAIN_SIDE_RECT).copy(),
            terrain_sheet.subsurface(Obstacle.TERRAIN_TOP_RECT).copy(),
        )

        scientist_sprite = pygame.image.load(
            os.path.join(assets_dir, "phase_1_scientist.png")
        ).convert_alpha()
        machine_sprite = pygame.image.load(
            os.path.join(assets_dir, "phase_1_xray_machine.png")
        ).convert_alpha()
        scientist_height = 170
        scientist_size = (
            round(scientist_sprite.get_width() * scientist_height
                  / scientist_sprite.get_height()),
            scientist_height,
        )
        self.phase_1_scientist_sprite = pygame.transform.smoothscale(
            scientist_sprite, scientist_size
        )
        self.phase_1_machine_sprite = pygame.transform.smoothscale(machine_sprite, (118, 211))
        self.phase_1_walk_sprites = []
        for frame_index in range(5):
            walk_sprite = pygame.image.load(
                os.path.join(
                    assets_dir, f"phase_1_scientist_walk_{frame_index}.png"
                )
            ).convert_alpha()
            walk_size = (
                round(walk_sprite.get_width() * scientist_height
                      / walk_sprite.get_height()),
                scientist_height,
            )
            self.phase_1_walk_sprites.append(
                pygame.transform.smoothscale(walk_sprite, walk_size)
            )
        portrait_sprite = pygame.image.load(
            os.path.join(assets_dir, "phase_1_scientist_portrait.png")
        ).convert_alpha()
        self.phase_1_scientist_portrait = pygame.transform.smoothscale(
            portrait_sprite, (88, 100)
        )
        self.phase_2_assets = load_phase_2_assets(assets_dir)
        self.phase_3_assets = load_phase_3_assets(assets_dir)
        self.phase_4_assets = load_phase_4_assets(assets_dir)
        self.phase_5_assets = load_phase_5_assets(assets_dir)
        self.phase_6_assets = load_phase_6_assets(assets_dir)
        self.phase_7_assets = load_phase_7_assets(assets_dir)

        self.state = STATE_MENU
        self.game_state = GameState()
        self.game_state.reset()
        self.phase_intro_shade = pygame.Surface(
            (SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA,
        )
        self.phase_intro_shade.fill((0, 0, 0, 170))

        self.archer = Archer()
        self.dialog = DialogBox(SCREEN_WIDTH, SCREEN_HEIGHT)
        control_x = SCREEN_WIDTH - 180
        self.restart_button = Button(
            control_x, 12, 160, 34, "Reiniciar jogo",
            self.font_small, self._request_restart,
        )
        self.back_to_menu_button = Button(
            control_x, 52, 160, 34, "Voltar ao menu",
            self.font_small, self._on_back_to_menu,
        )
        self.quit_button = Button(
            control_x, 92, 160, 34, "Fechar jogo",
            self.font_small, self._on_quit_click,
        )
        audio_control_x = SCREEN_WIDTH - 430
        self.audio_volume_down_button = Button(
            audio_control_x + 42, 12, 38, 34, "-",
            self.font_small, lambda: self.audio.change_volume(-0.1),
        )
        self.audio_volume_up_button = Button(
            audio_control_x + 84, 12, 38, 34, "+",
            self.font_small, lambda: self.audio.change_volume(0.1),
        )
        self.audio_mute_button = Button(
            audio_control_x + 126, 12, 92, 34, "Mudo",
            self.font_small, self.audio.toggle_mute,
        )
        self.audio_label_position = (audio_control_x, 20)
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
        self.completed_phase_index = None
        self.result_message = None
        self.last_result_success = False
        self.result_pending = False
        self.layout_index = 0
        self.phase_1_button_animation_time = 0.0
        self.phase_1_animation_stage = None
        self.phase_1_walk_time = 0.0
        self.phase_1_scientist_x = 0
        self.opening_story_index = 0
        self.opening_story_elapsed = 0.0
        self.phase_2_animation_stage = None
        self.phase_2_animation_time = 0.0
        self.phase_2_scientist_x = 0
        self.phase_2_formula_progress = 0.0
        self.phase_2_shoot_time = 0.0
        self.phase_3_animation_stage = None
        self.phase_3_animation_time = 0.0
        self.phase_3_scientist_x = 0
        self.phase_3_photo_visible = False
        self.phase_3_wall_start_y = 0
        self.phase_4_animation_stage = None
        self.phase_4_animation_time = 0.0
        self.phase_4_scientist_x = 0
        self.phase_4_princess_landed = False
        self.phase_4_gear_angle = 0.0
        self.phase_5_animation_stage = None
        self.phase_5_animation_time = 0.0
        self.phase_6_animation_stage = None
        self.phase_6_animation_time = 0.0
        self.phase_6_scientist_x = 0
        self.phase_6_bar_start_y = 0
        self.phase_7_animation_stage = None
        self.phase_7_animation_time = 0.0
        self.phase_7_capture_position = None
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
                   "Comecar fase", self.font_medium, self._start_round),
        ]

    def _build_aiming_widgets(self):
        control_center_y = SCREEN_HEIGHT - 39
        self.input_angle = InputBox(
            300, control_center_y - 20, 120, 40, label="Angulo (graus)",
            initial_text="45", font=self.font_medium,
            min_value=MIN_ANGLE, max_value=MAX_ANGLE,
        )
        self.input_velocity = InputBox(
            470, control_center_y - 20, 120, 40, label="Velocidade inicial (m/s)",
            initial_text="20", font=self.font_medium,
            min_value=MIN_VELOCITY, max_value=MAX_VELOCITY,
        )
        self._refresh_aiming_buttons()

    def _refresh_aiming_buttons(self):
        button_y = SCREEN_HEIGHT - 39 - 23
        launch_btn = Button(650, button_y, 140, 46, "Lancar!",
                            self.font_medium, self._on_launch_click)
        self.buttons = [launch_btn]
        if self.attempt_count >= 3:
            self.buttons.append(Button(
                810, button_y, 170, 46, "Calculadora",
                self.font_medium, self._open_calculator,
            ))

    def _build_game_over_buttons(self):
        self.buttons = [
            Button(SCREEN_WIDTH // 2 - 130, 360, 260, 48,
                   "Jogar Novamente", self.font_medium, self._on_restart_click),
            Button(SCREEN_WIDTH // 2 - 130, 420, 260, 48,
                   "Voltar ao Menu", self.font_medium, self._on_back_to_menu),
        ]

    def _build_phase_complete_buttons(self, has_next_phase):
        button_x = SCREEN_WIDTH // 2 - 150
        self.buttons = [
            Button(
                button_x, 360, 300, 48,
                "Proxima fase" if has_next_phase else "Voltar ao Menu",
                self.font_medium,
                self._on_next_phase if has_next_phase else self._on_back_to_menu,
            ),
            Button(
                button_x, 420, 300, 48, "Refazer fase",
                self.font_medium, self._on_replay_phase,
            ),
        ]

    # ------------------------------------------------------------ #
    # Callbacks de botões
    # ------------------------------------------------------------ #

    def _on_start_click(self):
        if self.game_state.is_game_complete():
            self.game_state.reset()
            self.layout_index = 0
        self.opening_story_index = 0
        self.opening_story_elapsed = 0.0
        self.state = STATE_OPENING_STORY
        self.opening_story_skip_button = Button(
            SCREEN_WIDTH // 2 - 90, SCREEN_HEIGHT - 100, 180, 50,
            "Ignorar", self.font_medium, self._skip_opening_story,
        )
        self._build_phase_intro_buttons()

    def _opening_story_duration(self):
        return OPENING_STORY_PART_DURATION

    def _advance_opening_story(self):
        self.opening_story_index += 1
        self.opening_story_elapsed = 0.0
        if self.opening_story_index == len(OPENING_STORY_PARTS):
            self._finish_opening_story()

    def _skip_opening_story(self):
        self._finish_opening_story()

    def _finish_opening_story(self):
        self.audio.play("phase")
        self.state = STATE_PHASE_INTRO
        self._build_phase_intro_buttons()

    def _update_opening_story(self, dt):
        if self.state != STATE_OPENING_STORY:
            return
        self.opening_story_elapsed += dt
        if self.opening_story_elapsed >= self._opening_story_duration():
            self._advance_opening_story()

    def _draw_opening_story(self):
        self._draw_background()
        self.screen.blit(self.phase_intro_shade, (0, 0))

        panel = pygame.Rect(90, 105, SCREEN_WIDTH - 180, 365)
        pygame.draw.rect(
            self.screen, (25, 30, 48), panel, border_radius=16,
        )
        pygame.draw.rect(
            self.screen, COLOR_ACCENT, panel, width=3, border_radius=16,
        )

        title = self.dialog.title_font.render(
            "Uma missão especial", True, COLOR_ACCENT,
        )
        self.screen.blit(
            title, title.get_rect(center=(panel.centerx, panel.y + 52)),
        )

        text_font_size = 18
        text_font = pygame.font.SysFont("arial", text_font_size, bold=True)
        story = OPENING_STORY_PARTS[self.opening_story_index]
        visible_characters = min(
            len(story),
            int(self.opening_story_elapsed * OPENING_STORY_TYPING_SPEED),
        )

        text_x = panel.x + 34
        text_width = panel.width - 68
        text_area = pygame.Rect(text_x, panel.y + 100, text_width, 235)

        def wrap_story(text, font):
            lines = []
            current_line = ""
            for word in text.split():
                candidate = f"{current_line} {word}".strip()
                if font.size(candidate)[0] <= text_width or not current_line:
                    current_line = candidate
                else:
                    lines.append(current_line)
                    current_line = word
            if current_line:
                lines.append(current_line)
            return lines

        line_height = text_font.get_linesize() + 3
        while (
            len(wrap_story(story, text_font)) * line_height > text_area.height
            and text_font_size > 14
        ):
            text_font_size -= 1
            text_font = pygame.font.SysFont(
                "arial", text_font_size, bold=True,
            )
            line_height = text_font.get_linesize() + 3

        text_lines = wrap_story(story[:visible_characters], text_font)
        full_lines = wrap_story(story, text_font)
        text_y = text_area.y + max(
            0,
            (text_area.height - len(full_lines) * line_height) // 2,
        )
        previous_clip = self.screen.get_clip()
        self.screen.set_clip(text_area)
        for line in text_lines:
            line_surface = text_font.render(line, True, COLOR_WHITE)
            self.screen.blit(line_surface, (text_x, text_y))
            text_y += line_height
        self.screen.set_clip(previous_clip)
        self.opening_story_skip_button.draw(self.screen)

    def _on_dev_mode_click(self):
        if not DEVELOPER_MODE_ENABLED:
            return
        self.state = STATE_DEV_MODE
        self._build_dev_mode_buttons()

    def _select_dev_phase(self, phase_index):
        if not DEVELOPER_MODE_ENABLED:
            return
        self.audio.set_tension(0)
        self.game_state.phase_index = phase_index
        self.game_state.round_index = 0
        self.arrow = None
        self.result_pending = False
        self.calculator.close()
        self.state = STATE_PHASE_INTRO
        self._build_phase_intro_buttons()

    def _on_quit_click(self):
        pygame.quit()
        sys.exit()

    def _on_back_to_menu(self):
        self.audio.set_tension(0)
        self.arrow = None
        self.calculator.close()
        self.dialog.hide()
        self.result_pending = False
        self.state = STATE_MENU
        self._build_menu_buttons()

    def _on_next_phase(self):
        self.audio.set_tension(0)
        self.audio.play("phase")
        self.state = STATE_PHASE_INTRO
        self._build_phase_intro_buttons()

    def _on_replay_phase(self):
        if self.completed_phase_index is None:
            return
        self.audio.set_tension(0)
        phase_index = self.completed_phase_index
        self.game_state.reset()
        self.game_state.phase_index = phase_index
        self.game_state.round_index = 0
        self.game_state.save()
        self.state = STATE_PHASE_INTRO
        self._build_phase_intro_buttons()

    def _on_restart_click(self):
        self.audio.set_tension(0)
        self.restart_confirmation.hide()
        self.game_state.reset()
        self.layout_index = 0
        self.arrow = None
        self.phase_1_animation_stage = None
        self.phase_1_button_animation_time = 0.0
        self.phase_2_animation_stage = None
        self.phase_2_animation_time = 0.0
        self.phase_2_formula_progress = 0.0
        self.phase_2_shoot_time = 0.0
        self.phase_3_animation_stage = None
        self.phase_3_animation_time = 0.0
        self.phase_3_photo_visible = False
        self.phase_4_animation_stage = None
        self.phase_4_animation_time = 0.0
        self.phase_4_princess_landed = False
        self.phase_4_gear_angle = 0.0
        self.phase_5_animation_stage = None
        self.phase_5_animation_time = 0.0
        self.phase_6_animation_stage = None
        self.phase_6_animation_time = 0.0
        self.phase_7_animation_stage = None
        self.phase_7_animation_time = 0.0
        self.phase_7_capture_position = None
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
        launch_x, launch_y = self._get_launch_point()
        self.attempt_count += 1
        if self.game_state.phase_index != 1:
            self.archer.fire()
        else:
            self.phase_2_shoot_time = PHASE_2_SHOOT_DURATION
        self.audio.play("launch")
        self.arrow = Arrow(launch_x, launch_y, angle, velocity)
        if self.game_state.phase_index == 6:
            self.target.start_falling()
        self.state = STATE_LAUNCHED

    def _open_calculator(self):
        launch_x, launch_y = self._get_launch_point()
        distance_m = (self.target.x - launch_x) / PIXELS_PER_METER
        height_difference_m = (launch_y - self.target.y) / PIXELS_PER_METER
        angle = self.input_angle.get_value() or 45
        velocity = self.input_velocity.get_value() or 20
        self.calculator.show(distance_m, height_difference_m, angle, velocity)

    def _get_launch_point(self):
        if self.game_state.phase_index == 1:
            sprite = self.phase_2_assets.bow_aim
            anchor_x, anchor_y = PHASE_2_BOW_LAUNCH_ANCHOR
            sprite_top = GROUND_Y - sprite.get_height()
            return (
                round(self.phase_2_scientist_x + sprite.get_width() * anchor_x),
                round(sprite_top + sprite.get_height() * anchor_y),
            )
        if self.game_state.phase_index == 4:
            aim_angle = self.input_angle.get_value() or 45
            _, muzzle, _ = self._get_phase_5_gun_geometry(aim_angle)
            return tuple(muzzle)
        if self.game_state.phase_index == 6:
            aim_angle = self.input_angle.get_value() or 45
            _, muzzle = self._get_phase_7_launcher_geometry(aim_angle)
            return tuple(muzzle)
        return self.archer.get_launch_point()

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
        self.audio.set_tension(0)
        self.phase_1_button_animation_time = 0.0
        self.phase_1_animation_stage = None
        self.phase_2_animation_stage = None
        self.phase_2_animation_time = 0.0
        self.phase_2_formula_progress = 0.0
        self.phase_3_animation_stage = None
        self.phase_3_animation_time = 0.0
        self.phase_3_photo_visible = False
        self.phase_4_animation_stage = None
        self.phase_4_animation_time = 0.0
        self.phase_4_princess_landed = False
        self.phase_4_gear_angle = 0.0
        self.phase_5_animation_stage = None
        self.phase_5_animation_time = 0.0
        self.phase_6_animation_stage = None
        self.phase_6_animation_time = 0.0
        self.phase_7_animation_stage = None
        self.phase_7_animation_time = 0.0
        self.phase_7_capture_position = None
        if self.game_state.phase_index == 0:
            scene = FIXED_SCENARIOS[0]
            self.phase_1_scientist_x = scene["scientist_position"][0]
        elif self.game_state.phase_index == 1:
            self.phase_2_scientist_x = FIXED_SCENARIOS[1]["scientist_position"][0]
        elif self.game_state.phase_index == 2:
            scene = FIXED_SCENARIOS[2]
            self.phase_3_scientist_x = scene["scientist_position"][0]
        elif self.game_state.phase_index == 3:
            scene = FIXED_SCENARIOS[3]
            self.phase_4_scientist_x = scene["scientist_position"][0]
        elif self.game_state.phase_index == 5:
            scene = FIXED_SCENARIOS[5]
            self.phase_6_scientist_x = scene["scientist_position"][0]
        self.layout_index += 1
        self.obstacles, self.target = build_round(
            self.game_state.phase_index, self.game_state.round_index, scientist["name"],
            seed=self.layout_index,
        )
        if self.game_state.phase_index == 2:
            self.phase_3_wall_start_y = self.obstacles[1].rect.y
        elif self.game_state.phase_index == 5:
            self.phase_6_bar_start_y = self.obstacles[1].rect.y
        self._build_aiming_widgets()
        self.state = STATE_AIMING

    def _finish_launch(self, success: bool, reason: str):
        self.audio.play("hit" if success else "miss")
        self.audio.set_tension(0 if success else self.attempt_count)
        self.last_result_success = success
        self.result_pending = True
        self.arrow = None
        if success:
            self.game_state.register_hit()
            if self.game_state.phase_index == 0:
                self.phase_1_animation_stage = "button"
                self.phase_1_button_animation_time = PHASE_1_BUTTON_ANIMATION_DURATION
            elif self.game_state.phase_index == 1:
                self.phase_2_animation_stage = "chalk_fall"
                self.phase_2_animation_time = 0.0
            elif self.game_state.phase_index == 2:
                self.phase_3_animation_stage = "button_press"
                self.phase_3_animation_time = 0.0
                self.phase_3_photo_visible = False
            elif self.game_state.phase_index == 3:
                self.phase_4_animation_stage = "princess_fall"
                self.phase_4_animation_time = 0.0
                self.phase_4_princess_landed = False
            elif self.game_state.phase_index == 4:
                self.phase_5_animation_stage = "impact"
                self.phase_5_animation_time = 0.0
            elif self.game_state.phase_index == 5:
                self.phase_6_animation_stage = "bar_fall"
                self.phase_6_animation_time = 0.0
            elif self.game_state.phase_index == 6:
                self.phase_7_animation_stage = "web_attach"
                self.phase_7_animation_time = 0.0
                self.phase_7_capture_position = (self.target.x, self.target.y)
                self.target.falling = False
            else:
                self._advance_after_result()
        else:
            self.dialog.show("Tente novamente", reason)

    def _advance_after_result(self):
        self.result_pending = False
        if not self.last_result_success:
            self.state = STATE_AIMING
            self._refresh_aiming_buttons()
            if self.attempt_count == 2:
                launch_x, launch_y = self._get_launch_point()
                distance_m = (self.target.x - launch_x) / PIXELS_PER_METER
                height_difference_m = (launch_y - self.target.y) / PIXELS_PER_METER
                scientist = self.game_state.current_scientist()
                hints = (
                    f"1. {get_hint_for_round(self.game_state.round_index)}\n\n"
                    f"2. {get_calculation_hint(distance_m, height_difference_m)}"
                )
                self.dialog.show(f"Dicas de {scientist['name']}", hints)
            return

        completed_phase_index = self.game_state.phase_index
        still_playing = self.game_state.advance_round()
        if not still_playing or self.game_state.round_index == 0:
            self.completed_phase_index = completed_phase_index
            self.state = STATE_PHASE_COMPLETE
            self.audio.play("phase")
            self._build_phase_complete_buttons(still_playing)
        else:
            self._start_round()

    def _update_phase_4_animation(self, dt):
        if self.phase_4_animation_stage == "princess_fall":
            self.phase_4_animation_time += dt
            if self.phase_4_animation_time >= FIXED_SCENARIOS[3]["princess_fall_duration"]:
                self.phase_4_princess_landed = True
                self.phase_4_animation_stage = "fire_ignite"
                self.phase_4_animation_time = 0.0
        elif self.phase_4_animation_stage == "fire_ignite":
            self.phase_4_animation_time += dt
            if self.phase_4_animation_time >= FIXED_SCENARIOS[3]["fire_duration"]:
                self.phase_4_animation_stage = "machine_run"
                self.phase_4_animation_time = 0.0
        elif self.phase_4_animation_stage in ("machine_run", "talk"):
            self.phase_4_gear_angle = (self.phase_4_gear_angle + dt * 240) % 360
            if self.phase_4_animation_stage == "machine_run":
                self.phase_4_animation_time += dt
                if self.phase_4_animation_time >= FIXED_SCENARIOS[3]["machine_duration"]:
                    self.phase_4_animation_stage = "talk"
                    self.dialog.show(
                        "Ada Lovelace",
                        "Obrigada por me ajudar! Com o fogo aceso, a Máquina Analítica "
                        "pode funcionar e seguir instruções para realizar cálculos.",
                        portrait=self.phase_4_assets.portrait,
                        anchor="top",
                    )

    def _update_phase_5_animation(self, dt):
        if self.phase_5_animation_stage == "impact":
            self.phase_5_animation_time += dt
            if self.phase_5_animation_time >= PHASE_5_IMPACT_DURATION:
                self.phase_5_animation_stage = "split"
                self.phase_5_animation_time = 0.0
        elif self.phase_5_animation_stage == "split":
            self.phase_5_animation_time += dt
            if self.phase_5_animation_time >= PHASE_5_SPLIT_DURATION:
                self.phase_5_animation_stage = "energy"
                self.phase_5_animation_time = 0.0
        elif self.phase_5_animation_stage == "energy":
            self.phase_5_animation_time += dt
            if self.phase_5_animation_time >= PHASE_5_ENERGY_DURATION:
                self.phase_5_animation_stage = "complete"
                self.phase_5_animation_time = 0.0
                self.dialog.show(
                    "Lise Meitner",
                    "Obrigada por me ajudar a explicar a fissão nuclear! Quando um "
                    "nêutron atinge o núcleo de um átomo pesado, ele pode se dividir "
                    "em núcleos menores. Nesse processo, são liberados muita energia "
                    "e novos nêutrons.",
                    portrait=self.phase_5_assets.portrait,
                )

    def _update_phase_6_animation(self, dt):
        if self.phase_6_animation_stage == "bar_fall":
            self.phase_6_animation_time += dt
            scene = FIXED_SCENARIOS[5]
            duration = scene["bar_fall_duration"]
            progress = min(1.0, self.phase_6_animation_time / duration)
            wall = self.obstacles[1]
            wall.set_y(
                round(
                    self.phase_6_bar_start_y
                    + (GROUND_Y + wall.rect.height - self.phase_6_bar_start_y)
                    * progress
                )
            )
            if progress >= 1.0:
                self.phase_6_animation_stage = "walk"
                self.phase_6_animation_time = 0.0
        elif self.phase_6_animation_stage == "walk":
            self.phase_6_animation_time += dt
            scene = FIXED_SCENARIOS[5]
            duration = scene["walk_duration"]
            progress = min(1.0, self.phase_6_animation_time / duration)
            start_x = scene["scientist_position"][0]
            end_x = scene["scientist_end_x"]
            self.phase_6_scientist_x = round(start_x + (end_x - start_x) * progress)
            if progress >= 1.0:
                self.phase_6_animation_stage = "sit"
                self.phase_6_animation_time = 0.0
        elif self.phase_6_animation_stage == "sit":
            self.phase_6_animation_time += dt
            if self.phase_6_animation_time >= FIXED_SCENARIOS[5]["sit_duration"]:
                self.phase_6_animation_stage = "microscope"
                self.phase_6_animation_time = 0.0
        elif self.phase_6_animation_stage == "microscope":
            self.phase_6_animation_time += dt
            if self.phase_6_animation_time >= FIXED_SCENARIOS[5]["microscope_duration"]:
                self.phase_6_animation_stage = "transposon"
                self.phase_6_animation_time = 0.0
                self.dialog.show(
                    "Barbara McClintock",
                    "Observei que alguns genes podem mudar de lugar no DNA. Esses "
                    "segmentos, chamados transposons, podem influenciar características "
                    "do organismo. Por isso também são conhecidos como genes saltadores.",
                    portrait=self.phase_6_assets.portrait,
                    illustration=self.phase_6_assets.transposon_frames[0],
                )
        elif self.phase_6_animation_stage == "transposon" and self.dialog.visible:
            self.phase_6_animation_time += dt
            frame_duration = FIXED_SCENARIOS[5]["transposon_frame_duration"]
            frame_index = int(self.phase_6_animation_time / frame_duration) % len(
                self.phase_6_assets.transposon_frames
            )
            self.dialog.illustration = self.phase_6_assets.transposon_frames[frame_index]

    def _draw_phase_6_scene(self):
        scene = FIXED_SCENARIOS[5]
        self.screen.blit(self.phase_6_assets.laboratory, scene["laboratory_position"])

    def _draw_phase_6_scientist(self):
        scene = FIXED_SCENARIOS[5]
        stage = self.phase_6_animation_stage
        if stage == "walk":
            frame_index = int(
                self.phase_6_animation_time * PHASE_6_WALK_FRAME_RATE
            ) % len(self.phase_6_assets.walk)
            sprite = self.phase_6_assets.walk[frame_index]
        elif stage in ("sit", "microscope", "transposon"):
            sprite = self.phase_6_assets.looking
        else:
            sprite = self.phase_6_assets.idle
        if stage in ("microscope", "transposon"):
            foreground_x, foreground_y = scene["laboratory_position"]
            self.screen.blit(
                self.phase_6_assets.laboratory_foreground,
                (foreground_x, foreground_y + 84),
            )
        self._blit_grounded(sprite, self.phase_6_scientist_x)

    def _draw_phase_7_scene(self):
        forest = (
            self.phase_7_assets.forest_scene_clear
            if self.target.falling or self.target.hit
            else self.phase_7_assets.forest_scene
        )
        self.screen.blit(forest, (0, 0))
        self._draw_phase_7_cliff()
        if self.phase_7_animation_stage in ("web_attach", "caught"):
            self._draw_phase_7_capture_web()

    def _draw_phase_7_cliff(self):
        cliff_x, cliff_y = FIXED_SCENARIOS[6]["cliff_position"]
        cliff_width = 138
        cliff_bottom = GROUND_Y
        face = [
            (cliff_x, cliff_y + 4),
            (cliff_x + cliff_width, cliff_y + 4),
            (cliff_x + cliff_width - 8, cliff_bottom - 26),
            (cliff_x + cliff_width - 22, cliff_bottom),
            (cliff_x + 19, cliff_bottom),
            (cliff_x + 5, cliff_bottom - 18),
        ]
        pygame.draw.polygon(self.screen, (66, 76, 62), face)
        pygame.draw.polygon(
            self.screen, (43, 55, 48), face, width=3,
        )
        pygame.draw.polygon(
            self.screen, (95, 111, 78),
            [
                (cliff_x + 12, cliff_y + 19),
                (cliff_x + 47, cliff_y + 11),
                (cliff_x + 39, cliff_y + 42),
                (cliff_x + 9, cliff_y + 51),
            ],
        )
        pygame.draw.polygon(
            self.screen, (83, 98, 70),
            [
                (cliff_x + 77, cliff_y + 13),
                (cliff_x + 119, cliff_y + 21),
                (cliff_x + 112, cliff_y + 49),
                (cliff_x + 73, cliff_y + 43),
            ],
        )
        pygame.draw.polygon(
            self.screen, (51, 66, 54),
            [
                (cliff_x + 37, cliff_y + 53),
                (cliff_x + 72, cliff_y + 47),
                (cliff_x + 67, cliff_bottom - 8),
                (cliff_x + 31, cliff_bottom - 12),
            ],
        )
        pygame.draw.polygon(
            self.screen, (67, 88, 54),
            [
                (cliff_x - 3, cliff_y + 5),
                (cliff_x + 13, cliff_y - 2),
                (cliff_x + 34, cliff_y + 2),
                (cliff_x + 52, cliff_y - 4),
                (cliff_x + 72, cliff_y + 1),
                (cliff_x + 94, cliff_y - 3),
                (cliff_x + 117, cliff_y + 2),
                (cliff_x + cliff_width + 4, cliff_y + 7),
                (cliff_x + cliff_width, cliff_y + 16),
                (cliff_x, cliff_y + 14),
            ],
        )
        pygame.draw.line(
            self.screen, (133, 151, 83),
            (cliff_x + 3, cliff_y + 4),
            (cliff_x + cliff_width - 2, cliff_y + 6),
            3,
        )

    def _draw_phase_7_capture_web(self):
        if self.phase_7_capture_position is None:
            return

        center_x, center_y = (
            round(value) for value in self.phase_7_capture_position
        )
        anchor = PHASE_7_BRANCH_ANCHOR
        progress = min(
            1.0,
            self.phase_7_animation_time / PHASE_7_WEB_ATTACH_DURATION,
        )
        bag_outline_offsets = (
            (-30, -35),
            (-40, -24),
            (-45, -3),
            (-40, 19),
            (-27, 38),
            (0, 48),
            (27, 38),
            (40, 19),
            (45, -3),
            (40, -24),
            (30, -35),
        )
        bag_rect = pygame.Rect(center_x - 52, center_y - 43, 104, 101)
        bag_surface = pygame.Surface(bag_rect.size, pygame.SRCALPHA)
        bag_points = [
            (
                round(bag_rect.width / 2 + offset_x * progress),
                round(48 + offset_y * progress),
            )
            for offset_x, offset_y in bag_outline_offsets
        ]
        left_attachment, right_attachment = bag_points[0], bag_points[-1]
        attachment_color = (50, 68, 67)
        thread_color = (225, 247, 251)

        left_world = (bag_rect.left + left_attachment[0], bag_rect.top + left_attachment[1])
        right_world = (bag_rect.left + right_attachment[0], bag_rect.top + right_attachment[1])
        pygame.draw.line(self.screen, attachment_color, anchor, left_world, 5)
        pygame.draw.line(self.screen, attachment_color, anchor, right_world, 5)
        pygame.draw.line(self.screen, thread_color, anchor, left_world, 2)
        pygame.draw.line(self.screen, thread_color, anchor, right_world, 2)

        pygame.draw.polygon(bag_surface, (126, 205, 224, 28), bag_points)
        pygame.draw.lines(bag_surface, (39, 93, 111, 170), True, bag_points, 4)
        pygame.draw.lines(bag_surface, (225, 247, 251, 240), True, bag_points, 2)

        for offset_x in (-22, -8, 8, 22):
            pygame.draw.line(
                bag_surface,
                (219, 244, 250, 180),
                bag_points[0],
                (
                    round(bag_rect.width / 2 + offset_x * progress),
                    round(48 + 46 * progress),
                ),
                1,
            )
            pygame.draw.line(
                bag_surface,
                (219, 244, 250, 180),
                bag_points[-1],
                (
                    round(bag_rect.width / 2 + offset_x * progress),
                    round(48 + 46 * progress),
                ),
                1,
            )

        for row_y, row_half_width in (
            (-19, 38),
            (-3, 44),
            (14, 41),
            (29, 33),
            (40, 19),
        ):
            pygame.draw.arc(
                bag_surface,
                (219, 244, 250, 180),
                pygame.Rect(
                    round(bag_rect.width / 2 - row_half_width * progress),
                    round(48 + (row_y - 8) * progress),
                    round(2 * row_half_width * progress),
                    round(17 * progress),
                ),
                math.pi,
                2 * math.pi,
                1,
            )

        self.screen.blit(bag_surface, bag_rect)
        pygame.draw.circle(self.screen, attachment_color, anchor, 6)
        pygame.draw.circle(self.screen, thread_color, anchor, 3)

    def _update_phase_7_animation(self, dt):
        if self.phase_7_animation_stage != "web_attach":
            return

        self.phase_7_animation_time += dt
        if self.phase_7_animation_time >= PHASE_7_WEB_ATTACH_DURATION:
            self.phase_7_animation_stage = "caught"
            self.phase_7_animation_time = PHASE_7_WEB_ATTACH_DURATION
            self.dialog.show(
                "Jane Goodall",
                "A teia ficou presa ao galho e segurou o chimpanzé em segurança. "
                "Observar os chimpanzés em seu habitat natural nos ajuda a "
                "compreender seu comportamento.",
                portrait=self.phase_7_assets.portrait,
            )

    def _get_phase_7_launcher_geometry(self, aim_angle):
        scientist_x, scientist_y = FIXED_SCENARIOS[6]["scientist_position"]
        hand = pygame.Vector2(scientist_x + 48, scientist_y + 74)
        direction = pygame.Vector2(
            math.cos(math.radians(aim_angle)),
            -math.sin(math.radians(aim_angle)),
        )
        muzzle = hand + direction * 54
        return hand, muzzle

    def _draw_phase_7_scientist(self, aim_angle):
        scene = FIXED_SCENARIOS[6]
        scientist_x, scientist_y = scene["scientist_position"]
        self.screen.blit(self.phase_7_assets.idle, (scientist_x, scientist_y))

        hand, muzzle = self._get_phase_7_launcher_geometry(aim_angle)
        center = hand.lerp(muzzle, 0.48)
        launcher_angle = aim_angle - 30
        launcher = pygame.transform.rotate(
            self.phase_7_assets.launcher, launcher_angle,
        )
        self.screen.blit(launcher, launcher.get_rect(center=center))

    def _draw_phase_7_target(self):
        center = (round(self.target.x), round(self.target.y))
        if self.target.falling:
            frame_index = int(self.target.fall_elapsed * 8) % len(
                self.phase_7_assets.chimp_frames
            )
            frame = self.phase_7_assets.chimp_frames[frame_index]
            self.screen.blit(frame, frame.get_rect(center=center))
        elif self.phase_7_capture_position is not None:
            frame = self.phase_7_assets.chimp_frames[1]
            chimp_rect = frame.get_rect(center=self.phase_7_capture_position)
            self.screen.blit(frame, chimp_rect)
        elif not self.target.hit:
            color = COLOR_SUCCESS if self.target.hit else COLOR_WHITE
            pygame.draw.circle(self.screen, color, center, self.target.radius, width=2)
            pygame.draw.circle(self.screen, color, center, 4)

    def _draw_phase_7_web(self):
        elapsed = self.arrow.projectile.t
        frames = self.phase_7_assets.web_frames
        frame = frames[int(elapsed * 14) % len(frames)]
        velocity_y_screen = -(self.arrow.projectile.vy_initial - 9.8 * elapsed)
        angle = math.degrees(math.atan2(-velocity_y_screen, self.arrow.projectile.vx))
        rotated = pygame.transform.rotate(frame, angle)
        rect = rotated.get_rect(
            center=tuple(round(value) for value in self.arrow.get_pos()),
        )
        self.screen.blit(rotated, rect)

    def _draw_phase_5_scene(self):
        cabinet = self.phase_5_assets.lab_cabinet
        self.screen.blit(cabinet, (810, 345))

    def _get_phase_5_gun_geometry(self, aim_angle):
        scientist_x, _ = FIXED_SCENARIOS[4]["scientist_position"]
        scientist_y = (
            GROUND_Y - self.phase_5_assets.idle.get_bounding_rect().bottom
        )
        hand = pygame.Vector2(scientist_x + 43, scientist_y + 65)
        direction = pygame.Vector2(
            math.cos(math.radians(aim_angle)),
            -math.sin(math.radians(aim_angle)),
        )
        perpendicular = pygame.Vector2(direction.y, -direction.x)
        muzzle = hand + direction * 44
        return hand, muzzle, perpendicular

    def _draw_phase_5_scientist(self, aim_angle):
        scene = FIXED_SCENARIOS[4]
        sprite = (
            self.phase_5_assets.talking
            if self.phase_5_animation_stage == "complete"
            else self.phase_5_assets.idle
        )
        self._blit_grounded(sprite, scene["scientist_position"][0])

        hand, muzzle, perpendicular = self._get_phase_5_gun_geometry(aim_angle)
        direction = (muzzle - hand).normalize()
        down = -perpendicular
        barrel = [
            hand + direction * 10 + perpendicular * 5,
            muzzle + perpendicular * 4,
            muzzle - perpendicular * 4,
            hand + direction * 10 - perpendicular * 5,
        ]
        pygame.draw.polygon(self.screen, (37, 47, 68), barrel)
        pygame.draw.lines(self.screen, (104, 145, 183), True, barrel, 2)
        pygame.draw.line(
            self.screen, (161, 204, 231),
            muzzle + perpendicular * 3, muzzle - perpendicular * 3, 3,
        )
        handle = [
            hand + direction * 13 - perpendicular * 4,
            hand + direction * 22 - perpendicular * 5,
            hand + direction * 25 - perpendicular * 18,
            hand + direction * 16 - perpendicular * 18,
        ]
        pygame.draw.polygon(self.screen, (45, 50, 68), handle)
        pygame.draw.lines(self.screen, (104, 145, 183), True, handle, 2)
        pygame.draw.line(
            self.screen, (225, 185, 108), hand + direction * 12,
            hand + direction * 16 + down * 3, 2,
        )

    def _draw_phase_5_target(self):
        center = (round(self.target.x), round(self.target.y))
        stage = self.phase_5_animation_stage
        if stage is None or stage == "impact":
            atom_rect = self.phase_5_assets.atom.get_rect(center=center)
            self.screen.blit(self.phase_5_assets.atom, atom_rect)
            if stage == "impact":
                progress = min(1.0, self.phase_5_animation_time / PHASE_5_IMPACT_DURATION)
                radius = round(12 + 44 * progress)
                pygame.draw.circle(self.screen, (130, 220, 255), center, radius, 3)
                pygame.draw.circle(self.screen, COLOR_WHITE, center, round(radius * 0.55), 2)
            else:
                label = self.font_target.render("ÁTOMO DE URÂNIO", True, COLOR_WHITE)
                self.screen.blit(
                    label, label.get_rect(center=(center[0], center[1] + 76)),
                )
            return

        if stage == "split":
            progress = min(1.0, self.phase_5_animation_time / PHASE_5_SPLIT_DURATION)
            fragment_size = round(54 + 18 * progress)
            fragment = pygame.transform.smoothscale(
                self.phase_5_assets.nucleus, (fragment_size, fragment_size),
            )
            separation = round(34 * progress)
            for sign in (-1, 1):
                fragment_rect = fragment.get_rect(
                    center=(center[0] + sign * separation, center[1] + sign * 10),
                )
                self.screen.blit(fragment, fragment_rect)
            for angle in range(0, 360, 45):
                radians = math.radians(angle)
                distance = 28 + 38 * progress
                end = (
                    round(center[0] + math.cos(radians) * distance),
                    round(center[1] + math.sin(radians) * distance),
                )
                pygame.draw.line(self.screen, (255, 190, 74), center, end, 2)
            return

        result_rect = self.phase_5_assets.fission_result.get_rect(center=center)
        self.screen.blit(self.phase_5_assets.fission_result, result_rect)
        if stage == "energy":
            progress = min(1.0, self.phase_5_animation_time / PHASE_5_ENERGY_DURATION)
            pulse = round(20 + 34 * (0.5 + 0.5 * math.sin(progress * math.pi * 8)))
            glow = pygame.Surface((pulse * 2 + 4, pulse * 2 + 4), pygame.SRCALPHA)
            pygame.draw.circle(
                glow, (255, 174, 47, 72), (pulse + 2, pulse + 2), pulse,
            )
            self.screen.blit(
                glow, (center[0] - pulse - 2, center[1] - pulse - 2),
                special_flags=pygame.BLEND_RGBA_ADD,
            )

    def _draw_phase_5_neutron(self):
        elapsed = self.arrow.projectile.t
        frames = self.phase_5_assets.neutron_frames
        frame = frames[int(elapsed * 14) % len(frames)]
        velocity_y_screen = -(self.arrow.projectile.vy_initial - 9.8 * elapsed)
        angle = math.degrees(math.atan2(-velocity_y_screen, self.arrow.projectile.vx))
        rotated = pygame.transform.rotate(frame, angle)
        rotated_rect = rotated.get_rect(
            center=tuple(round(value) for value in self.arrow.get_pos()),
        )
        self.screen.blit(rotated, rotated_rect)

    def _draw_phase_4_scene(self):
        scene = FIXED_SCENARIOS[3]
        furnace = (
            self.phase_4_assets.furnace_lit
            if self.phase_4_princess_landed
            else self.phase_4_assets.furnace_unlit
        )
        self.screen.blit(furnace, scene["furnace_position"])
        self.screen.blit(self.phase_4_assets.machine, scene["machine_position"])
        if self.phase_4_animation_stage == "fire_ignite":
            glow = pygame.Surface((110, 90), pygame.SRCALPHA)
            glow_alpha = round(35 + 70 * (
                0.5 + 0.5 * pygame.math.Vector2(1, 0).rotate(
                    self.phase_4_animation_time * 720
                ).y
            ))
            pygame.draw.circle(glow, (255, 116, 36, glow_alpha), (55, 46), 42)
            self.screen.blit(glow, (scene["furnace_position"][0] + 37,
                                    scene["furnace_position"][1] + 68),
                             special_flags=pygame.BLEND_RGBA_ADD)
        if self.phase_4_animation_stage in ("machine_run", "talk"):
            self._draw_phase_4_gears()

        if self.phase_4_animation_stage == "princess_fall":
            sprite = self.phase_4_assets.idle
            progress = min(
                1.0,
                self.phase_4_animation_time
                / scene["princess_fall_duration"],
            )
            feet_y = round(
                -sprite.get_height()
                + (scene["princess_landing_y"] + sprite.get_height()) * progress
            )
        elif self.phase_4_princess_landed:
            sprite = (
                self.phase_4_assets.talking
                if self.phase_4_animation_stage == "talk"
                else self.phase_4_assets.idle
            )
            feet_y = scene["princess_landing_y"]
        else:
            return

        bounds = sprite.get_bounding_rect()
        sprite_rect = sprite.get_rect()
        sprite_rect.midbottom = (
            scene["princess_x"],
            feet_y + sprite.get_height() - bounds.bottom,
        )
        self.screen.blit(sprite, sprite_rect)

    def _draw_phase_4_gears(self):
        scene = FIXED_SCENARIOS[3]
        machine_x, machine_y = scene["machine_position"]
        for index, (center, radius, teeth) in enumerate((
            ((machine_x + 115, machine_y + 122), 12, 10),
            ((machine_x + 91, machine_y + 108), 8, 8),
        )):
            rotation = self.phase_4_gear_angle * (-1 if index else 1)
            points = []
            for index in range(teeth * 2):
                angle = (360 / (teeth * 2)) * index + rotation
                current_radius = radius if index % 2 == 0 else radius * 0.72
                radians = pygame.math.Vector2(1, 0).rotate(angle)
                points.append((
                    round(center[0] + radians.x * current_radius),
                    round(center[1] - radians.y * current_radius),
                ))
            pygame.draw.polygon(self.screen, (187, 126, 52), points)
            pygame.draw.circle(self.screen, (48, 39, 39), center, max(2, radius // 3))
            pygame.draw.circle(self.screen, (238, 188, 106), center, 2)

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
            if obstacle is self.target:
                continue
            if obstacle.collides_with_point(px, py):
                self._finish_launch(False, "A flecha bateu em um obstaculo. Tente um "
                                            "angulo ou velocidade diferente.")
                return

        # colisão com o alvo
        if self._target_collides_with_arrow(px, py):
            self.target.hit = True
            self._finish_launch(True, "")
            return

        # saiu da tela ou caiu no chao sem acertar nada
        if px > SCREEN_WIDTH or px < 0:
            self._finish_launch(False, "A flecha saiu da tela sem acertar o alvo.")
        elif py >= GROUND_Y and self.arrow.projectile.t > 0.05:
            self._finish_launch(False, "A flecha caiu no chao antes de chegar ao alvo.")

    def _target_collides_with_arrow(self, x, y):
        if self.game_state.phase_index in (0, 2):
            radius = (
                PHASE_1_BUTTON_RADIUS
                if self.game_state.phase_index == 0
                else PHASE_3_BUTTON_RADIUS
            )
            return (
                (x - self.target.x) ** 2 + (y - self.target.y) ** 2
                <= radius ** 2
            )
        return self.target.collides_with_point(x, y)

    def _draw_phase_1_button(self):
        pressed_amount = 0
        if self.phase_1_button_animation_time > 0:
            elapsed = PHASE_1_BUTTON_ANIMATION_DURATION - self.phase_1_button_animation_time
            if elapsed < PHASE_1_BUTTON_PRESS_DURATION:
                progress = elapsed / PHASE_1_BUTTON_PRESS_DURATION
            elif elapsed < PHASE_1_BUTTON_PRESS_DURATION + PHASE_1_BUTTON_RETURN_DURATION:
                progress = 1 - (
                    elapsed - PHASE_1_BUTTON_PRESS_DURATION
                ) / PHASE_1_BUTTON_RETURN_DURATION
            else:
                progress = 0
            pressed_amount = round(4 * progress)

        center = (round(self.target.x), round(self.target.y - pressed_amount))
        pygame.draw.circle(
            self.screen, (19, 67, 91),
            (center[0], center[1] + 5), PHASE_1_BUTTON_RADIUS,
        )
        pygame.draw.circle(
            self.screen, (42, 174, 205), center, PHASE_1_BUTTON_RADIUS,
        )
        pygame.draw.circle(
            self.screen, (151, 238, 245), center, PHASE_1_BUTTON_RADIUS, 2,
        )
        pygame.draw.ellipse(
            self.screen, (217, 255, 255),
            (
                center[0] - 8, center[1] - 11,
                10, 4,
            ),
        )

    def _update_phase_1_animation(self, dt):
        if self.phase_1_animation_stage == "button":
            self.phase_1_button_animation_time = max(
                0.0, self.phase_1_button_animation_time - dt
            )
            if self.phase_1_button_animation_time == 0:
                self.phase_1_animation_stage = "walk"
                self.phase_1_walk_time = PHASE_1_WALK_DURATION
        elif self.phase_1_animation_stage == "walk":
            self.phase_1_walk_time = max(0.0, self.phase_1_walk_time - dt)
            progress = 1 - self.phase_1_walk_time / PHASE_1_WALK_DURATION
            scene = FIXED_SCENARIOS[0]
            start_x = scene["scientist_position"][0]
            end_x = scene["scientist_machine_position"][0]
            self.phase_1_scientist_x = round(start_x + (end_x - start_x) * progress)
            if self.phase_1_walk_time == 0:
                self.phase_1_animation_stage = None
                self.dialog.show(
                    "Marie Curie",
                    "Obrigada por me ajudar a ligar a maquina de raio-X!",
                    portrait=self.phase_1_scientist_portrait,
                )

    def _update_phase_2_animation(self, dt):
        self.phase_2_shoot_time = max(0.0, self.phase_2_shoot_time - dt)
        if self.phase_2_animation_stage == "chalk_fall":
            self.phase_2_animation_time += dt
            if self.phase_2_animation_time >= PHASE_2_CHALK_FALL_DURATION:
                self.phase_2_animation_stage = "walk_to_chalk"
                self.phase_2_animation_time = 0.0
        elif self.phase_2_animation_stage == "walk_to_chalk":
            scene = FIXED_SCENARIOS[1]
            start_x = scene["scientist_position"][0]
            chalk_x = scene["chalk_position"][0] - 48
            end_x = scene["scientist_end_x"]
            duration = PHASE_2_WALK_DURATION * (
                (chalk_x - start_x) / (end_x - start_x)
            )
            self.phase_2_animation_time = min(
                duration, self.phase_2_animation_time + dt
            )
            progress = self.phase_2_animation_time / duration
            self.phase_2_scientist_x = round(
                start_x + (chalk_x - start_x) * progress
            )
            if self.phase_2_animation_time == duration:
                self.phase_2_animation_stage = "pickup"
                self.phase_2_animation_time = 0.0
        elif self.phase_2_animation_stage == "pickup":
            self.phase_2_animation_time = min(
                PHASE_2_PICKUP_DURATION, self.phase_2_animation_time + dt
            )
            if self.phase_2_animation_time == PHASE_2_PICKUP_DURATION:
                self.phase_2_animation_stage = "walk_to_board"
                self.phase_2_animation_time = 0.0
        elif self.phase_2_animation_stage == "walk_to_board":
            scene = FIXED_SCENARIOS[1]
            start_x = scene["chalk_position"][0] - 48
            end_x = scene["scientist_end_x"]
            duration = PHASE_2_WALK_DURATION * (
                (end_x - start_x)
                / (end_x - scene["scientist_position"][0])
            )
            self.phase_2_animation_time = min(
                duration, self.phase_2_animation_time + dt
            )
            progress = self.phase_2_animation_time / duration
            self.phase_2_scientist_x = round(
                start_x + (end_x - start_x) * progress
            )
            if self.phase_2_animation_time == duration:
                self.phase_2_animation_stage = "write"
                self.phase_2_animation_time = 0.0
        elif self.phase_2_animation_stage == "write":
            self.phase_2_animation_time = min(
                PHASE_2_WRITE_DURATION, self.phase_2_animation_time + dt
            )
            self.phase_2_formula_progress = (
                self.phase_2_animation_time / PHASE_2_WRITE_DURATION
            )
            if self.phase_2_animation_time == PHASE_2_WRITE_DURATION:
                self.phase_2_animation_stage = "done"
                self.dialog.show(
                    "Emmy Noether",
                    "Obrigada por me ajudar a registrar o Teorema de Noether! "
                    "As simetrias da natureza estão ligadas às grandezas que "
                    "permanecem constantes.",
                    portrait=self.phase_2_assets.portrait,
                )

    def _draw_phase_2_chalk(self, x, y):
        self.screen.blit(self.phase_2_assets.chalk, (round(x), round(y)))

    def _draw_phase_2_bar(self, obstacle):
        bar = obstacle.rect
        pygame.draw.rect(
            self.screen, (43, 32, 27), bar.inflate(4, 4), border_radius=6
        )
        pygame.draw.rect(self.screen, (101, 66, 44), bar, border_radius=5)
        pygame.draw.rect(
            self.screen, (142, 98, 62),
            (bar.x + 3, bar.y + 3, bar.width - 6, 8),
            border_radius=3,
        )
        pygame.draw.line(
            self.screen, (177, 130, 84),
            (bar.x + 8, bar.y + 4), (bar.right - 8, bar.y + 4), 2,
        )
        pygame.draw.line(
            self.screen, (67, 43, 32),
            (bar.x + 4, bar.bottom - 4), (bar.right - 4, bar.bottom - 4), 2,
        )
        for nail_x in range(bar.x + 18, bar.right - 8, 72):
            pygame.draw.circle(
                self.screen, (55, 43, 36), (nail_x, bar.centery), 3
            )
            pygame.draw.circle(
                self.screen, (184, 147, 103), (nail_x - 1, bar.centery - 1), 1
            )

    def _draw_phase_2_scene(self):
        scene = FIXED_SCENARIOS[1]
        self.screen.fill((42, 53, 58))
        for panel_x in range(70, SCREEN_WIDTH, 140):
            pygame.draw.line(
                self.screen, (47, 59, 63),
                (panel_x, 0), (panel_x, GROUND_Y - 12), 2,
            )
        pygame.draw.rect(
            self.screen, (76, 58, 45),
            (0, GROUND_Y, SCREEN_WIDTH, SCREEN_HEIGHT - GROUND_Y),
        )
        pygame.draw.rect(
            self.screen, (106, 78, 54),
            (0, GROUND_Y - 8, SCREEN_WIDTH, 8),
        )
        for floor_y in range(GROUND_Y + 18, SCREEN_HEIGHT, 18):
            pygame.draw.line(
                self.screen, (91, 69, 52),
                (0, floor_y), (SCREEN_WIDTH, floor_y), 1,
            )
        for plank_x in range(100, SCREEN_WIDTH, 150):
            pygame.draw.line(
                self.screen, (91, 69, 52),
                (plank_x, GROUND_Y), (plank_x, SCREEN_HEIGHT), 1,
            )

        board_x, board_y = scene["blackboard_position"]
        self.screen.blit(self.phase_2_assets.empty_board, (board_x, board_y))

        if self.phase_2_animation_stage == "chalk_fall":
            progress = min(
                1.0, self.phase_2_animation_time / PHASE_2_CHALK_FALL_DURATION
            )
            start_y = scene["chalk_position"][1]
            end_y = GROUND_Y - self.phase_2_assets.chalk.get_height()
            chalk_y = start_y + (end_y - start_y) * progress ** 2
            self._draw_phase_2_chalk(scene["chalk_position"][0], chalk_y)
        elif self.phase_2_animation_stage == "walk_to_chalk":
            self._draw_phase_2_chalk(
                scene["chalk_position"][0],
                GROUND_Y - self.phase_2_assets.chalk.get_height(),
            )
        elif self.phase_2_animation_stage in (None, "done"):
            if self.phase_2_formula_progress:
                self._draw_phase_2_chalk(
                    board_x + 26,
                    board_y + self.phase_2_assets.empty_board.get_height() - 43,
                )
            else:
                self._draw_phase_2_chalk(
                    scene["chalk_position"][0], scene["chalk_position"][1]
                )

        if self.phase_2_formula_progress:
            character_count = round(
                len(PHASE_2_FORMULA) * self.phase_2_formula_progress
            )
            formula = PHASE_2_FORMULA[:character_count]
            if formula:
                formula_font = pygame.font.SysFont("timesnewroman", 28)
                formula_surf = formula_font.render(
                    formula, True, (235, 239, 229)
                )
                formula_area = pygame.Rect(board_x + 31, board_y + 45, 172, 48)
                if formula_surf.get_width() > formula_area.width:
                    formula_surf = pygame.transform.smoothscale(
                        formula_surf,
                        (formula_area.width, formula_surf.get_height()),
                    )
                self.screen.blit(
                    formula_surf,
                    formula_surf.get_rect(center=formula_area.center),
                )

    def _draw_phase_2_scientist(self):
        if self.phase_2_shoot_time > 0:
            sprite = self.phase_2_assets.bow_shoot
        elif self.phase_2_animation_stage in ("walk_to_chalk", "walk_to_board"):
            frame_index = int(
                self.phase_2_animation_time * PHASE_2_WALK_FRAME_RATE
            ) % len(self.phase_2_assets.walk)
            sprite = self.phase_2_assets.walk[frame_index]
        elif self.phase_2_animation_stage == "pickup":
            sprite = pygame.transform.scale(self.phase_2_assets.idle, (66, 112))
        elif self.phase_2_animation_stage in ("write", "done"):
            sprite = self.phase_2_assets.idle
        elif self.state == STATE_AIMING:
            sprite = (
                self.phase_2_assets.bow_draw
                if self.archer.draw_progress < 1
                else self.phase_2_assets.bow_aim
            )
        else:
            sprite = self.phase_2_assets.bow_hold
        position = self._grounded_character_position(
            sprite, self.phase_2_scientist_x,
        )
        self.screen.blit(sprite, position)
        if self.phase_2_animation_stage in (
            "pickup", "walk_to_board", "write",
        ):
            self._draw_phase_2_chalk(
                self.phase_2_scientist_x + 46, position[1] + 54
            )

    def _update_phase_3_animation(self, dt):
        if self.phase_3_animation_stage == "button_press":
            self.phase_3_animation_time += dt
            if self.phase_3_animation_time >= FIXED_SCENARIOS[2]["button_press_duration"]:
                self.phase_3_animation_stage = "bar_fall"
                self.phase_3_animation_time = 0.0
        elif self.phase_3_animation_stage == "bar_fall":
            self.phase_3_animation_time += dt
            duration = FIXED_SCENARIOS[2]["bar_fall_duration"]
            progress = min(1.0, self.phase_3_animation_time / duration)
            wall = self.obstacles[1]
            wall.set_y(
                self.phase_3_wall_start_y
                + (GROUND_Y + wall.rect.height - self.phase_3_wall_start_y)
                * progress
            )
            if progress == 1.0:
                self.phase_3_animation_stage = "walk"
                self.phase_3_animation_time = FIXED_SCENARIOS[2]["walk_duration"]
        elif self.phase_3_animation_stage == "walk":
            duration = FIXED_SCENARIOS[2]["walk_duration"]
            self.phase_3_animation_time = max(
                0.0, self.phase_3_animation_time - dt
            )
            progress = 1 - self.phase_3_animation_time / duration
            scene = FIXED_SCENARIOS[2]
            start_x = scene["scientist_position"][0]
            end_x = scene["scientist_end_x"]
            self.phase_3_scientist_x = round(start_x + (end_x - start_x) * progress)
            if self.phase_3_animation_time == 0:
                self.phase_3_animation_stage = "photo"
                self.phase_3_animation_time = 0.0
        elif self.phase_3_animation_stage == "photo":
            self.phase_3_animation_time += dt
            if self.phase_3_animation_time >= FIXED_SCENARIOS[2]["photo_duration"]:
                self.phase_3_animation_stage = None
                self.phase_3_photo_visible = True
                self.dialog.show(
                    "Rosalind Franklin",
                    "Obrigada por me ajudar a acionar a câmera! A imagem 51, "
                    "obtida por difração de raios X, revelou pistas fundamentais "
                    "sobre a estrutura em dupla hélice do DNA.",
                    portrait=self.phase_3_assets.portrait,
                )

    def _draw_phase_3_button(self):
        center = (round(self.target.x), round(self.target.y))
        if self.phase_3_animation_stage == "button_press":
            progress = min(
                1.0,
                self.phase_3_animation_time
                / FIXED_SCENARIOS[2]["button_press_duration"],
            )
            center = (center[0], center[1] + round(4 * progress))
        pygame.draw.circle(
            self.screen, (91, 21, 30),
            (center[0], center[1] + 5), PHASE_3_BUTTON_RADIUS,
        )
        pygame.draw.circle(
            self.screen, (224, 58, 67), center, PHASE_3_BUTTON_RADIUS,
        )
        pygame.draw.circle(
            self.screen, (255, 173, 165), center, PHASE_3_BUTTON_RADIUS, 2,
        )
        pygame.draw.ellipse(
            self.screen, (255, 224, 213),
            (center[0] - 9, center[1] - 12, 12, 5),
        )

    def _draw_phase_3_scene(self):
        scene = FIXED_SCENARIOS[2]
        self.screen.blit(self.phase_3_assets.camera, scene["camera_position"])
        if not self.phase_3_photo_visible:
            return

        bubble = pygame.Rect(700, 112, 270, 183)
        tail_tip = (scene["camera_position"][0] + 73, scene["camera_position"][1] + 12)
        pygame.draw.polygon(
            self.screen, (248, 249, 245),
            [(bubble.left + 32, bubble.bottom - 2),
             (bubble.left + 64, bubble.bottom - 2), tail_tip],
        )
        pygame.draw.polygon(
            self.screen, (50, 69, 98),
            [(bubble.left + 32, bubble.bottom - 2),
             (bubble.left + 64, bubble.bottom - 2), tail_tip],
            width=2,
        )
        pygame.draw.rect(self.screen, (248, 249, 245), bubble, border_radius=20)
        pygame.draw.rect(self.screen, (50, 69, 98), bubble, width=3, border_radius=20)
        caption = self.font_small.render("Foto 51", True, (34, 44, 60))
        self.screen.blit(caption, caption.get_rect(center=(bubble.centerx, bubble.top + 22)))
        photo_rect = self.phase_3_assets.diffraction_photo.get_rect(
            center=(bubble.centerx, bubble.centery + 18)
        )
        self.screen.blit(self.phase_3_assets.diffraction_photo, photo_rect)

    def _draw_phase_3_scientist(self):
        scene = FIXED_SCENARIOS[2]
        sprite = self.phase_3_assets.idle
        if self.phase_3_animation_stage == "walk":
            frame_index = int(
                (scene["walk_duration"] - self.phase_3_animation_time)
                * PHASE_3_WALK_FRAME_RATE
            ) % len(self.phase_3_assets.walk)
            sprite = self.phase_3_assets.walk[frame_index]
        self.screen.blit(
            sprite, self._grounded_character_position(
                sprite, self.phase_3_scientist_x,
            ),
        )

    # ------------------------------------------------------------ #
    # Desenho
    # ------------------------------------------------------------ #

    def _grounded_character_position(self, sprite, x):
        return round(x), GROUND_Y - sprite.get_bounding_rect().bottom

    def _blit_grounded(self, sprite, x):
        self.screen.blit(sprite, self._grounded_character_position(sprite, x))

    def _draw_background(self):
        if (
            self.state in (
                STATE_OPENING_STORY, STATE_PHASE_INTRO, STATE_AIMING,
                STATE_LAUNCHED,
            )
            and self.game_state.phase_index < 6
        ):
            self.screen.blit(self.phase_background, (0, 0))
            return

        self.screen.fill(COLOR_BG)
        pygame.draw.rect(self.screen, COLOR_GROUND, (0, GROUND_Y, SCREEN_WIDTH, SCREEN_HEIGHT - GROUND_Y))

    def _draw_audio_controls(self):
        label = (
            "Mudo" if self.audio.muted
            else f"{round(self.audio.volume * 100)}%"
        )
        label_surface = self.font_small.render(label, True, COLOR_WHITE)
        self.screen.blit(label_surface, self.audio_label_position)
        self.audio_volume_down_button.draw(self.screen)
        self.audio_volume_up_button.draw(self.screen)
        self.audio_mute_button.text = "Som" if self.audio.muted else "Mudo"
        self.audio_mute_button.draw(self.screen)

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
        self.screen.blit(self.phase_intro_shade, (0, 0))

        intro = PHASE_INTROS[self.game_state.phase_index]
        panel = pygame.Rect(90, 105, SCREEN_WIDTH - 180, 365)
        pygame.draw.rect(
            self.screen, (25, 30, 48), panel, border_radius=16,
        )
        pygame.draw.rect(
            self.screen, COLOR_ACCENT, panel, width=3, border_radius=16,
        )

        phase_title = self.font_small.render(
            f"FASE {self.game_state.phase_index + 1} DE {TOTAL_PHASES}",
            True, COLOR_GRAY,
        )
        self.screen.blit(
            phase_title,
            phase_title.get_rect(center=(panel.centerx, panel.y + 32)),
        )
        title = self.font_title.render(intro["scientist"], True, COLOR_ACCENT)
        self.screen.blit(title, title.get_rect(center=(panel.centerx, panel.y + 78)))

        text_x = panel.x + 34
        text_width = panel.width - 68
        section_y = panel.y + 126
        for heading, message in (
            ("Quem foi?", intro["fact"]),
            ("Sua missao", intro["objective"]),
        ):
            heading_surface = self.font_medium.render(
                heading, True, COLOR_WHITE,
            )
            self.screen.blit(heading_surface, (text_x, section_y))
            section_y += 34

            lines = []
            current_line = ""
            for word in message.split():
                candidate = f"{current_line} {word}".strip()
                if self.font_small.size(candidate)[0] <= text_width:
                    current_line = candidate
                else:
                    lines.append(current_line)
                    current_line = word
            if current_line:
                lines.append(current_line)
            for line in lines:
                line_surface = self.font_small.render(line, True, COLOR_WHITE)
                self.screen.blit(line_surface, (text_x, section_y))
                section_y += 24
            section_y += 18

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
    def _draw_aiming_or_launched(self):
        self._draw_background()
        if self.game_state.phase_index == 0:
            phase_1_scene = FIXED_SCENARIOS[0]
            self.screen.blit(self.phase_1_machine_sprite, phase_1_scene["machine_position"])
            scientist_sprite = self.phase_1_scientist_sprite
            if self.phase_1_animation_stage == "walk":
                frame_index = int(
                    (PHASE_1_WALK_DURATION - self.phase_1_walk_time)
                    * PHASE_1_WALK_FRAME_RATE
                ) % len(self.phase_1_walk_sprites)
                scientist_sprite = self.phase_1_walk_sprites[frame_index]
            self.screen.blit(
                scientist_sprite,
                self._grounded_character_position(
                    scientist_sprite, self.phase_1_scientist_x,
                ),
            )
        elif self.game_state.phase_index == 1:
            self._draw_phase_2_scene()
        elif self.game_state.phase_index == 2:
            self._draw_phase_3_scene()
        elif self.game_state.phase_index == 3:
            self._draw_phase_4_scene()
        elif self.game_state.phase_index == 4:
            self._draw_phase_5_scene()
        elif self.game_state.phase_index == 5:
            self._draw_phase_6_scene()
        elif self.game_state.phase_index == 6:
            self._draw_phase_7_scene()
        self._draw_hud()

        aim_angle = self.input_angle.get_value() or 45
        if self.game_state.phase_index == 1:
            self._draw_phase_2_scientist()
        elif self.game_state.phase_index == 4:
            self._draw_phase_5_scientist(aim_angle)
        elif self.game_state.phase_index == 6:
            self._draw_phase_7_scientist(aim_angle)
        else:
            self.archer.draw(self.screen, aim_angle_deg=aim_angle)

        for obstacle in self.obstacles:
            if self.game_state.phase_index == 1:
                if not self.target.hit:
                    self._draw_phase_2_bar(obstacle)
            else:
                obstacle.draw(self.screen)
        if self.game_state.phase_index == 2:
            self._draw_phase_3_scientist()
        elif self.game_state.phase_index == 5:
            self._draw_phase_6_scientist()
        if self.game_state.phase_index == 0:
            self._draw_phase_1_button()
        elif self.game_state.phase_index == 2:
            self._draw_phase_3_button()
        elif self.game_state.phase_index == 4:
            self._draw_phase_5_target()
        elif self.game_state.phase_index == 6:
            self._draw_phase_7_target()
        elif self.game_state.phase_index not in (1, 5) or not self.target.hit:
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
            if self.game_state.phase_index == 4:
                self._draw_phase_5_neutron()
            elif self.game_state.phase_index == 6:
                self._draw_phase_7_web()
            else:
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

    def _draw_phase_complete(self):
        self._draw_background()
        is_game_complete = self.game_state.is_game_complete()
        title = (
            "Parabens! Voce completou o jogo!"
            if is_game_complete else "Fase concluida!"
        )
        self._draw_text_center(title, self.font_title, COLOR_SUCCESS, 220)
        self._draw_text_center(
            f"Pontuacao: {self.game_state.score}",
            self.font_medium, COLOR_WHITE, 280,
        )
        self._draw_text_center(
            "Escolha como deseja continuar",
            self.font_small, COLOR_GRAY, 315,
        )
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

                if (
                    event.type == pygame.MOUSEBUTTONDOWN
                    and event.button == 1
                    and (
                        self.state != STATE_LAUNCHED
                        or self.dialog.visible
                    )
                ):
                    self.audio.play("ui")

                audio_buttons = (
                    self.audio_volume_down_button,
                    self.audio_volume_up_button,
                    self.audio_mute_button,
                )
                for button in audio_buttons:
                    button.handle_event(event)
                if (
                    event.type == pygame.MOUSEBUTTONDOWN
                    and event.button == 1
                    and any(
                        button.rect.collidepoint(event.pos)
                        for button in audio_buttons
                    )
                ):
                    continue

                if self.state == STATE_OPENING_STORY:
                    self.opening_story_skip_button.handle_event(event)
                    continue

                if self.dialog.visible:
                    self.dialog.handle_event(event)
                    if not self.dialog.visible and self.result_pending:
                        self._advance_after_result()
                    continue

                if self.restart_confirmation.visible:
                    self.restart_confirmation.handle_event(event)
                    continue

                if self.state != STATE_MENU:
                    global_buttons = (
                        self.restart_button,
                        self.back_to_menu_button,
                        self.quit_button,
                    )
                    for button in global_buttons:
                        button.handle_event(event)
                    if (
                        event.type == pygame.MOUSEBUTTONDOWN
                        and event.button == 1
                        and any(button.rect.collidepoint(event.pos) for button in global_buttons)
                    ):
                        continue

                if self.state == STATE_MENU:
                    for button in self.buttons:
                        button.handle_event(event)

                elif self.state == STATE_PHASE_INTRO:
                    for button in self.buttons:
                        button.handle_event(event)

                elif self.state == STATE_AIMING:
                    if self.calculator.visible:
                        self.calculator.handle_event(event)
                    else:
                        self.input_angle.handle_event(event)
                        self.input_velocity.handle_event(event)
                        for button in self.buttons:
                            button.handle_event(event)

                elif self.state == STATE_DEV_MODE:
                    for button in self.buttons:
                        button.handle_event(event)

                elif self.state == STATE_GAME_OVER:
                    for button in self.buttons:
                        button.handle_event(event)
                elif self.state == STATE_PHASE_COMPLETE:
                    for button in self.buttons:
                        button.handle_event(event)

            # updates que não dependem de eventos
            self.archer.update(dt, aiming=self.state == STATE_AIMING)
            self.calculator.update(dt)
            self._update_opening_story(dt)
            if self.state == STATE_LAUNCHED and self.arrow and not self.dialog.visible:
                self._update_launched(dt)
            self._update_phase_1_animation(dt)
            self._update_phase_2_animation(dt)
            self._update_phase_3_animation(dt)
            self._update_phase_4_animation(dt)
            self._update_phase_5_animation(dt)
            self._update_phase_6_animation(dt)
            self._update_phase_7_animation(dt)

            # desenho
            if self.state == STATE_MENU:
                self._draw_menu()
            elif self.state == STATE_OPENING_STORY:
                self._draw_opening_story()
            elif self.state == STATE_PHASE_INTRO:
                self._draw_phase_intro()
            elif self.state in (STATE_AIMING, STATE_LAUNCHED):
                self._draw_aiming_or_launched()
            elif self.state == STATE_DEV_MODE:
                self._draw_dev_mode()
            elif self.state == STATE_GAME_OVER:
                self._draw_game_over()
            elif self.state == STATE_PHASE_COMPLETE:
                self._draw_phase_complete()

            self.dialog.draw(self.screen)
            self.calculator.draw(self.screen)
            self.restart_confirmation.draw(self.screen)
            if self.state not in (STATE_MENU, STATE_OPENING_STORY):
                self.restart_button.draw(self.screen)
                self.back_to_menu_button.draw(self.screen)
                self.quit_button.draw(self.screen)
            self._draw_audio_controls()
            pygame.display.flip()


if __name__ == "__main__":
    Game().run()
