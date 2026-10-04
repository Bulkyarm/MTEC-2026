"""
Base de dados das cientistas do jogo, organizadas em 7 fases (áreas da ciência).
Cada fase tem 5 cientistas. Cada cientista é o "alvo" de uma rodada e também
quem fornece, através do balão de diálogo (NPC/botão de ajuda), uma dica de
fórmula de lançamento oblíquo para aquela rodada.

Os fatos apresentados são resumos curtos e factuais sobre a contribuição de
cada cientista. Revise/expanda o texto conforme a curadoria do projeto.
"""

# Dicas de fórmula de lançamento oblíquo, uma para cada rodada (0 a 4) de cada fase.
# A ideia é que, ao longo de uma fase, o jogador conheça progressivamente as
# fórmulas necessárias para calcular ângulo e velocidade corretos.
HINTS = [
    "Decomponha a velocidade inicial: Vx = v0 * cos(theta) e Vy = v0 * sen(theta). "
    "Isso mostra o quanto da força vai para frente e o quanto vai para cima.",

    "Para saber até onde a flecha alcança, use: R = (v0^2 * sen(2*theta)) / g. "
    "Repare que o alcance depende do SENO DO DOBRO do ângulo.",

    "Para saber a altura máxima da flecha, use: H = (v0^2 * sen(theta)^2) / (2*g). "
    "Ângulos maiores tendem a dar mais altura, mas menos alcance.",

    "O tempo total que a flecha fica no ar é: T = (2 * v0 * sen(theta)) / g. "
    "Isso ajuda a prever quando ela vai começar a cair.",

    "Dica de ouro: um ângulo de 45 graus tende a MAXIMIZAR o alcance para uma "
    "mesma velocidade inicial. Mas cuidado, os obstáculos podem exigir outro ângulo!",
]

PHASES = [
    {
        "area": "Física",
        "cor_tema": (76, 130, 201),
        "scientists": [
            {
                "name": "Marie Curie",
                "fact": "Pioneira no estudo da radioatividade, descobriu os elementos "
                        "polônio e rádio. Foi a primeira pessoa a ganhar dois prêmios "
                        "Nobel em ciências diferentes (Física, 1903, e Química, 1911).",
            },
            {
                "name": "Lise Meitner",
                "fact": "Física que ajudou a explicar teoricamente a fissão nuclear, "
                        "processo que mais tarde se tornaria a base da energia nuclear.",
            },
            {
                "name": "Chien-Shiung Wu",
                "fact": "Realizou o experimento que derrubou a chamada 'lei da "
                        "conservação da paridade', um marco na física de partículas.",
            },
            {
                "name": "Cecilia Payne-Gaposchkin",
                "fact": "Em sua tese de doutorado (1925), foi a primeira a mostrar que "
                        "as estrelas são compostas majoritariamente de hidrogênio e hélio.",
            },
            {
                "name": "Hertha Ayrton",
                "fact": "Física e engenheira, pesquisou o arco elétrico e o "
                        "movimento ondulatório da areia sob a água. Foi a primeira "
                        "mulher a apresentar um trabalho próprio na Royal Society.",
            },
        ],
    },
    {
        "area": "Química",
        "cor_tema": (201, 130, 76),
        "scientists": [
            {
                "name": "Dorothy Hodgkin",
                "fact": "Usou cristalografia por raios X para determinar a estrutura "
                        "da penicilina, da insulina e da vitamina B12. Ganhou o Nobel "
                        "de Química em 1964.",
            },
            {
                "name": "Rosalind Franklin",
                "fact": "Suas imagens de difração de raios X foram essenciais para a "
                        "descoberta da estrutura em dupla hélice do DNA.",
            },
            {
                "name": "Stephanie Kwolek",
                "fact": "Química que inventou o Kevlar, material super-resistente "
                        "usado em coletes à prova de balas e diversos equipamentos.",
            },
            {
                "name": "Alice Ball",
                "fact": "Desenvolveu o primeiro tratamento injetável eficaz contra a "
                        "hanseníase, conhecido como 'Método Ball'.",
            },
            {
                "name": "Gertrude B. Elion",
                "fact": "Desenvolveu métodos inovadores para criação de "
                        "medicamentos, incluindo tratamentos contra leucemia. "
                        "Ganhou o Nobel de Medicina em 1988.",
            },
        ],
    },
    {
        "area": "Biologia e Medicina",
        "cor_tema": (76, 201, 120),
        "scientists": [
            {
                "name": "Jane Goodall",
                "fact": "Primatóloga conhecida por seu estudo de décadas sobre o "
                        "comportamento de chimpanzés selvagens na Tanzânia.",
            },
            {
                "name": "Elizabeth Blackwell",
                "fact": "Foi a primeira mulher a se formar em medicina nos "
                        "Estados Unidos, abrindo caminho para outras médicas.",
            },
            {
                "name": "Virginia Apgar",
                "fact": "Anestesiologista que criou o Índice de Apgar, usado até "
                        "hoje para avaliar rapidamente a saúde de recém-nascidos.",
            },
            {
                "name": "Rita Levi-Montalcini",
                "fact": "Descobriu o Fator de Crescimento Nervoso (NGF), essencial "
                        "para entender o desenvolvimento do sistema nervoso. "
                        "Ganhou o Nobel de Medicina em 1986.",
            },
            {
                "name": "Tu Youyou",
                "fact": "Descobriu a artemisinina, composto que revolucionou o "
                        "tratamento da malária. Ganhou o Nobel de Medicina em 2015.",
            },
        ],
    },
    {
        "area": "Matemática e Computação",
        "cor_tema": (170, 100, 201),
        "scientists": [
            {
                "name": "Ada Lovelace",
                "fact": "Escreveu o que é considerado o primeiro algoritmo "
                        "destinado a ser processado por uma máquina, sendo "
                        "reconhecida como pioneira da programação.",
            },
            {
                "name": "Katherine Johnson",
                "fact": "Matemática da NASA cujos cálculos de trajetória foram "
                        "fundamentais para as primeiras missões espaciais tripuladas dos EUA.",
            },
            {
                "name": "Grace Hopper",
                "fact": "Cientista da computação que ajudou a criar um dos "
                        "primeiros compiladores, base para linguagens de "
                        "programação modernas.",
            },
            {
                "name": "Hypatia de Alexandria",
                "fact": "Matemática e astrônoma da Antiguidade, lecionou "
                        "matemática e filosofia em Alexandria, sendo uma das "
                        "primeiras mulheres matemáticas documentadas na história.",
            },
            {
                "name": "Mary Jackson",
                "fact": "Primeira engenheira negra da NASA, trabalhou em "
                        "cálculos aerodinâmicos para o programa espacial americano.",
            },
        ],
    },
    {
        "area": "Astronomia",
        "cor_tema": (201, 76, 130),
        "scientists": [
            {
                "name": "Caroline Herschel",
                "fact": "Descobriu diversos cometas e foi a primeira mulher a "
                        "receber um salário como cientista, no Reino Unido.",
            },
            {
                "name": "Henrietta Leavitt",
                "fact": "Descobriu a relação entre período e luminosidade das "
                        "estrelas variáveis Cefeidas, usada até hoje para medir "
                        "distâncias no universo.",
            },
            {
                "name": "Vera Rubin",
                "fact": "Suas observações sobre a rotação de galáxias forneceram "
                        "fortes evidências da existência da matéria escura.",
            },
            {
                "name": "Maria Mitchell",
                "fact": "Primeira astrônoma profissional dos Estados Unidos, "
                        "ficou famosa por descobrir um cometa em 1847.",
            },
            {
                "name": "Jocelyn Bell Burnell",
                "fact": "Descobriu os primeiros pulsares (estrelas de nêutrons "
                        "em rotação), um marco importante da radioastronomia.",
            },
        ],
    },
    {
        "area": "Geologia e Ciências da Terra",
        "cor_tema": (76, 180, 170),
        "scientists": [
            {
                "name": "Inge Lehmann",
                "fact": "Sismóloga dinamarquesa que, em 1936, apresentou evidências de que a Terra possui um núcleo interno sólido.",
            },
            {
                "name": "Marie Tharp",
                "fact": "Geóloga e cartógrafa que ajudou a criar o primeiro mapa detalhado do fundo do oceano Atlântico e revelou a dorsal mesoatlântica.",
            },
            {
                "name": "Florence Bascom",
                "fact": "Geóloga pioneira, foi uma das primeiras mulheres a trabalhar para o Serviço Geológico dos Estados Unidos.",
            },
            {
                "name": "Eunice Newton Foote",
                "fact": "Cientista que realizou experimentos em 1856 mostrando que o dióxido de carbono aquece mais ao receber radiação solar.",
            },
            {
                "name": "Alice Wilson",
                "fact": "Geóloga canadense que pesquisou a geologia do vale do rio Ottawa e foi a primeira geóloga mulher do Serviço Geológico do Canadá.",
            },
        ],
    },
    {
        "area": "Engenharia",
        "cor_tema": (201, 170, 76),
        "scientists": [
            {
                "name": "Emily Warren Roebling",
                "fact": "Assumiu responsabilidades centrais de supervisão na construção da Ponte do Brooklyn, concluída em 1883.",
            },
            {
                "name": "Edith Clarke",
                "fact": "Engenheira elétrica que desenvolveu métodos de cálculo para sistemas de energia e se tornou professora de engenharia na Universidade do Texas.",
            },
            {
                "name": "Beatrice Shilling",
                "fact": "Engenheira aeronáutica britânica que desenvolveu uma solução para melhorar o funcionamento dos motores de aviões de combate durante a Segunda Guerra Mundial.",
            },
            {
                "name": "Hedy Lamarr",
                "fact": "Atriz e inventora que, com George Antheil, patenteou um sistema de salto de frequência para orientar torpedos por rádio.",
            },
            {
                "name": "Elsie MacGill",
                "fact": "Engenheira aeronáutica canadense, foi a primeira mulher a obter diploma nessa área e liderou a produção de aviões Hawker Hurricane no Canadá.",
            },
        ],
    },
]


def get_hint_for_round(round_index: int) -> str:
    """Retorna a dica de fórmula correspondente à rodada (0 a 4) dentro da fase."""
    return HINTS[round_index % len(HINTS)]


def get_calculation_hint(distance_m: float, height_difference_m: float) -> str:
    """Monta uma dica com os valores da posição atual do alvo."""
    return (
        f"Dica de calculo: use x = {distance_m:.1f} m e y = {height_difference_m:+.1f} m. "
        "Na formula da trajetoria, substitua esses valores: "
        "y = x*tan(theta) - (g*x^2)/(2*v0^2*cos(theta)^2), com g = 9,8 m/s^2. "
        "Escolha theta e v0 que facam o resultado de y ficar proximo do valor indicado."
    )
