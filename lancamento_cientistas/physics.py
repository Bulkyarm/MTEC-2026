"""
Física do lançamento oblíquo (movimento parabólico).

Todas as contas internas usam metros/segundos; a conversão para pixels
acontece só na hora de desenhar (settings.PIXELS_PER_METER).
"""

import math
from settings import GRAVITY, PIXELS_PER_METER


class Projectile:
    """
    Representa a flecha em voo, simulada passo a passo (não só pela fórmula
    fechada), para permitir checar colisão com obstáculos a cada instante.
    """

    def __init__(self, origin_x_px: int, origin_y_px: int, angle_deg: float, v0: float):
        self.origin_x_px = origin_x_px
        self.origin_y_px = origin_y_px

        angle_rad = math.radians(angle_deg)
        self.vx = v0 * math.cos(angle_rad)   # m/s
        self.vy_initial = v0 * math.sin(angle_rad)  # m/s (positivo = para cima)

        self.t = 0.0          # tempo decorrido (s)
        self.x_m = 0.0        # deslocamento horizontal (m)
        self.y_m = 0.0        # deslocamento vertical (m), positivo = para cima
        self.active = True
        self.landed = False

    def update(self, dt: float):
        """Avança a simulação em dt segundos."""
        if not self.active:
            return
        self.t += dt
        self.x_m = self.vx * self.t
        self.y_m = (self.vy_initial * self.t) - (0.5 * GRAVITY * self.t ** 2)

    def get_screen_pos(self):
        """Converte a posição atual (metros) para coordenadas de tela (pixels)."""
        px = self.origin_x_px + self.x_m * PIXELS_PER_METER
        # eixo Y da tela cresce para baixo, por isso o sinal negativo
        py = self.origin_y_px - self.y_m * PIXELS_PER_METER
        return px, py

    def get_velocity_components(self):
        """Retorna (Vx, Vy_inicial) em m/s, úteis para exibir na HUD."""
        return self.vx, self.vy_initial

    @staticmethod
    def compute_range(angle_deg: float, v0: float) -> float:
        """Alcance teórico R = (v0^2 * sen(2*theta)) / g, em metros."""
        angle_rad = math.radians(angle_deg)
        return (v0 ** 2 * math.sin(2 * angle_rad)) / GRAVITY

    @staticmethod
    def compute_max_height(angle_deg: float, v0: float) -> float:
        """Altura máxima teórica H = (v0^2 * sen(theta)^2) / (2*g), em metros."""
        angle_rad = math.radians(angle_deg)
        return (v0 ** 2 * math.sin(angle_rad) ** 2) / (2 * GRAVITY)

    @staticmethod
    def compute_time_of_flight(angle_deg: float, v0: float) -> float:
        """Tempo total de voo T = (2 * v0 * sen(theta)) / g, em segundos."""
        angle_rad = math.radians(angle_deg)
        return (2 * v0 * math.sin(angle_rad)) / GRAVITY
