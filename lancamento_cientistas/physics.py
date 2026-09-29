"""
Física do lançamento oblíquo (movimento parabólico).

Todas as contas internas usam metros/segundos; a conversão para pixels
acontece só na hora de desenhar (settings.PIXELS_PER_METER).
"""

import math
from settings import GRAVITY, PIXELS_PER_METER


def solve_initial_speed(horizontal_distance_m: float, height_difference_m: float,
                        angle_deg: float) -> float:
    """Isola v0 na equacao da trajetoria para um angulo conhecido."""
    if horizontal_distance_m <= 0 or not 0 < angle_deg < 90:
        raise ValueError("A distancia deve ser positiva e o angulo deve estar entre 0 e 90 graus.")

    angle_rad = math.radians(angle_deg)
    denominator = 2 * math.cos(angle_rad) ** 2 * (
        horizontal_distance_m * math.tan(angle_rad) - height_difference_m
    )
    if denominator <= 0:
        raise ValueError("Esse angulo nao alcanca a altura do alvo.")

    return math.sqrt(GRAVITY * horizontal_distance_m ** 2 / denominator)


def solve_launch_angle(horizontal_distance_m: float, height_difference_m: float,
                       initial_speed: float) -> float:
    """Retorna o menor angulo positivo que atinge o alvo para uma velocidade."""
    if horizontal_distance_m <= 0 or initial_speed <= 0:
        raise ValueError("A distancia e a velocidade devem ser positivas.")

    coefficient = GRAVITY * horizontal_distance_m ** 2 / (2 * initial_speed ** 2)
    discriminant = horizontal_distance_m ** 2 - 4 * coefficient * (coefficient + height_difference_m)
    if discriminant < 0:
        raise ValueError("Essa velocidade nao alcanca o alvo.")

    root = math.sqrt(discriminant)
    tangent_values = (
        (horizontal_distance_m - root) / (2 * coefficient),
        (horizontal_distance_m + root) / (2 * coefficient),
    )
    valid_angles = [
        math.degrees(math.atan(tangent))
        for tangent in tangent_values
        if tangent > 0
    ]
    if not valid_angles:
        raise ValueError("Essa velocidade nao alcanca o alvo em um angulo positivo.")

    return min(valid_angles)


def build_speed_calculation_steps(horizontal_distance_m: float,
                                  height_difference_m: float,
                                  angle_deg: float) -> list[str]:
    """Monta as etapas numericas para isolar a velocidade inicial."""
    speed = solve_initial_speed(horizontal_distance_m, height_difference_m, angle_deg)
    angle_rad = math.radians(angle_deg)
    tangent = math.tan(angle_rad)
    cosine_squared = math.cos(angle_rad) ** 2
    horizontal_component = horizontal_distance_m * tangent
    vertical_term = horizontal_component - height_difference_m
    numerator = GRAVITY * horizontal_distance_m ** 2
    cosine_factor = 2 * cosine_squared
    denominator = cosine_factor * vertical_term
    speed_squared = numerator / denominator

    return [
        "y = x*tan(theta) - g*x^2/(2*v0^2*cos^2(theta))",
        f"{height_difference_m:+.2f} = {horizontal_distance_m:.2f}*tan({angle_deg:.2f}) - ("
        f"{GRAVITY:.2f}*{horizontal_distance_m:.2f}^2)/(2*v0^2*cos^2({angle_deg:.2f}))",
        f"tan({angle_deg:.2f}) = {tangent:.4f}; cos^2({angle_deg:.2f}) = {cosine_squared:.4f}",
        "v0 = sqrt(g*x^2 / (2*cos^2(theta)*(x*tan(theta)-y)))",
        f"x*tan(theta) = {horizontal_distance_m:.2f}*{tangent:.4f} = {horizontal_component:.4f}",
        f"{horizontal_component:.4f} - ({height_difference_m:+.2f}) = {vertical_term:.4f}",
        f"{GRAVITY:.2f}*{horizontal_distance_m:.2f}^2 = {numerator:.2f}",
        f"2*{cosine_squared:.4f} = {cosine_factor:.4f}",
        f"{cosine_factor:.4f}*{vertical_term:.4f} = {denominator:.4f}",
        f"v0^2 = {numerator:.2f}/{denominator:.4f} = {speed_squared:.4f}",
        f"sqrt({speed_squared:.4f}) = {speed:.4f}",
        f"v0 = {speed:.2f} m/s",
    ]


def build_angle_calculation_steps(horizontal_distance_m: float,
                                  height_difference_m: float,
                                  initial_speed: float) -> list[str]:
    """Monta as etapas numericas para isolar o menor angulo positivo."""
    angle = solve_launch_angle(horizontal_distance_m, height_difference_m, initial_speed)
    numerator = GRAVITY * horizontal_distance_m ** 2
    velocity_squared = initial_speed ** 2
    denominator = 2 * velocity_squared
    coefficient = numerator / denominator
    coefficient_plus_height = coefficient + height_difference_m
    horizontal_squared = horizontal_distance_m ** 2
    four_coefficient = 4 * coefficient
    discriminant_product = four_coefficient * coefficient_plus_height
    discriminant = horizontal_squared - discriminant_product
    root = math.sqrt(discriminant)
    tangent_candidates = (
        (horizontal_distance_m - root) / (2 * coefficient),
        (horizontal_distance_m + root) / (2 * coefficient),
    )
    tangent = math.tan(math.radians(angle))
    selected_root = (
        "-" if tangent_candidates[0] > 0 and tangent_candidates[0] <= tangent_candidates[1]
        else "+"
    )

    return [
        "y = x*tan(theta) - g*x^2/(2*v0^2*cos^2(theta))",
        f"{height_difference_m:+.2f} = {horizontal_distance_m:.2f}*tan(theta) - "
        f"({GRAVITY:.2f}*{horizontal_distance_m:.2f}^2)/(2*{initial_speed:.2f}^2*cos^2(theta))",
        "t = tan(theta); 1/cos^2(theta) = 1+t^2",
        f"{GRAVITY:.2f}*{horizontal_distance_m:.2f}^2 = {numerator:.2f}",
        f"2*{initial_speed:.2f}^2 = {denominator:.4f}",
        f"C = {numerator:.2f}/{denominator:.4f} = {coefficient:.4f}",
        f"C*t^2 - x*t + (C+y) = 0; C = {coefficient:.4f}",
        f"{coefficient:.4f} + ({height_difference_m:+.2f}) = {coefficient_plus_height:.4f}",
        f"{horizontal_distance_m:.2f}^2 = {horizontal_squared:.4f}",
        f"4*{coefficient:.4f} = {four_coefficient:.4f}",
        f"{four_coefficient:.4f}*{coefficient_plus_height:.4f} = {discriminant_product:.4f}",
        f"{horizontal_squared:.4f} - {discriminant_product:.4f} = {discriminant:.4f}",
        f"sqrt({discriminant:.4f}) = {root:.4f}",
        f"{horizontal_distance_m:.2f} {selected_root} {root:.4f} = "
        f"{horizontal_distance_m + (root if selected_root == '+' else -root):.4f}",
        f"2*{coefficient:.4f} = {2 * coefficient:.4f}",
        f"t = ({horizontal_distance_m:.2f} {selected_root} sqrt(D))/(2*C) = {tangent:.4f}",
        f"theta = arctan({tangent:.4f}) = {angle:.2f} graus",
    ]


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
