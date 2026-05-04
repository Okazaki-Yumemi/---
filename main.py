import math
import os
import random
import sys
from copy import deepcopy

import pygame


WIDTH, HEIGHT = 1280, 720
FPS = 60

BG = (4, 8, 22)
PANEL = (13, 19, 43)
PANEL_2 = (18, 26, 56)
CYAN = (78, 214, 255)
CYAN_DARK = (24, 92, 128)
VIOLET = (153, 108, 255)
TEXT = (230, 238, 255)
MUTED = (148, 163, 184)
GREEN = (74, 222, 128)
AMBER = (251, 191, 36)
RED = (248, 113, 113)
WHITE = (255, 255, 255)

STATE_KEYS = [
    "ATP",
    "Glucose",
    "Glycogen",
    "Fat",
    "AminoAcidPool",
    "NADH",
    "NADPH",
    "ROS",
    "NH3",
    "CellHealth",
]

STATE_LABELS = {
    "ATP": "ATP",
    "Glucose": "Glucose",
    "Glycogen": "Glycogen",
    "Fat": "Fat",
    "AminoAcidPool": "Amino Acids",
    "NADH": "NADH",
    "NADPH": "NADPH",
    "ROS": "ROS",
    "NH3": "NH3",
    "CellHealth": "Cell Health",
}

CARDS = [
    {
        "id": "glycolysis",
        "name": "激活糖酵解",
        "pathway": "Glycolysis",
        "effect": {"Glucose": -12, "ATP": 16, "NADH": 6, "ROS": 2},
        "explain": "糖酵解快速供能，体现“投资—收获”和“抓住关键”。",
        "nodes": ["Glucose", "G-6-P", "Glycolysis", "Pyruvate"],
    },
    {
        "id": "tca",
        "name": "激活 TCA 循环",
        "pathway": "TCA",
        "effect": {"Glucose": -4, "NADH": 14, "ATP": 4},
        "explain": "TCA 将碳骨架深度氧化，产生还原当量。",
        "nodes": ["Acetyl-CoA", "TCA", "NADH"],
    },
    {
        "id": "etc",
        "name": "激活呼吸链",
        "pathway": "ETC",
        "effect": {"NADH": -16, "ATP": 24, "ROS": 8},
        "explain": "呼吸链利用电子传递和质子动力势生成 ATP，体现“藏器于势”。",
        "nodes": ["NADH", "ETC", "ATP"],
    },
    {
        "id": "ppp",
        "name": "激活 PPP",
        "pathway": "PPP",
        "effect": {"Glucose": -8, "NADPH": 18, "ATP": -2},
        "explain": "PPP 不直接追求 ATP，而是提供 NADPH 支持合成代谢和抗氧化，体现“势有进退，道以曲直”。",
        "nodes": ["G-6-P", "PPP", "NADPH"],
    },
    {
        "id": "antioxidant",
        "name": "抗氧化修复",
        "pathway": "Redox Repair",
        "effect": {"NADPH": -12, "ROS": -20, "CellHealth": 6},
        "explain": "NADPH 支持抗氧化系统，降低氧化应激。",
        "nodes": ["NADPH", "Antioxidant", "ROS"],
    },
    {
        "id": "glycogenolysis",
        "name": "分解糖原",
        "pathway": "Glycogenolysis",
        "effect": {"Glycogen": -16, "Glucose": 18},
        "explain": "糖原是短期储备，响应低血糖和运动需求。",
        "nodes": ["Glycogen", "Glucose"],
    },
    {
        "id": "glycogenesis",
        "name": "合成糖原",
        "pathway": "Glycogenesis",
        "effect": {"Glucose": -16, "Glycogen": 18, "ATP": -4},
        "explain": "富足时储备能量，体现有备无患。",
        "nodes": ["Glucose", "Glycogen"],
    },
    {
        "id": "lipolysis",
        "name": "脂肪动员",
        "pathway": "Lipolysis",
        "effect": {"Fat": -12, "NADH": 8, "ATP": 4},
        "explain": "脂肪是高效长期能源，但动员和利用需要条件。",
        "nodes": ["Fat", "Beta-oxidation", "NADH"],
    },
    {
        "id": "beta_oxidation",
        "name": "β-氧化",
        "pathway": "Beta oxidation",
        "effect": {"Fat": -10, "NADH": 16, "ATP": 4, "ROS": 3},
        "explain": "脂肪酸分解生成乙酰辅酶A和还原当量，与TCA和呼吸链连接。",
        "nodes": ["Fat", "Beta-oxidation", "Acetyl-CoA", "NADH"],
    },
    {
        "id": "gluconeogenesis",
        "name": "糖异生",
        "pathway": "Gluconeogenesis",
        "effect": {"ATP": -12, "AminoAcidPool": -6, "Glucose": 18, "NH3": 5},
        "explain": "糖异生耗能生糖，体现“逆势而行、协同调控”。",
        "nodes": ["Amino Acids", "Carbon Skeleton", "Gluconeogenesis", "Glucose"],
    },
    {
        "id": "urea",
        "name": "尿素循环",
        "pathway": "Urea Cycle",
        "effect": {"ATP": -10, "NH3": -24, "CellHealth": 4},
        "explain": "尿素循环消耗能量清除氨毒性，体现“牺牲能量以维持安全”。",
        "nodes": ["NH3", "Urea Cycle"],
    },
    {
        "id": "proteolysis",
        "name": "蛋白质分解",
        "pathway": "Proteolysis",
        "effect": {"AminoAcidPool": 16, "NH3": 8, "CellHealth": -3},
        "explain": "氨基酸可补充碳骨架，但会带来氨毒性压力。",
        "nodes": ["Amino Acids", "NH3", "Carbon Skeleton"],
    },
]

LEVELS = [
    {
        "name": "饭后状态",
        "context": "葡萄糖充足，细胞需要把高血糖信号转化为 ATP、糖原和还原力储备。",
        "initial": {
            "ATP": 55,
            "Glucose": 88,
            "Glycogen": 22,
            "Fat": 50,
            "AminoAcidPool": 46,
            "NADH": 34,
            "NADPH": 38,
            "ROS": 18,
            "NH3": 18,
            "CellHealth": 82,
        },
        "goals": [("Glucose", "<=", 70), ("ATP", ">=", 50), ("CellHealth", ">=", 70)],
        "strategy": "推荐：糖酵解 + 糖原合成 + 适度 PPP。",
    },
    {
        "name": "短跑缺氧",
        "context": "氧气供应跟不上爆发运动，电子传递效率下降，快速供能与 ROS 控制成为核心。",
        "initial": {
            "ATP": 34,
            "Glucose": 62,
            "Glycogen": 54,
            "Fat": 44,
            "AminoAcidPool": 42,
            "NADH": 72,
            "NADPH": 40,
            "ROS": 42,
            "NH3": 16,
            "CellHealth": 84,
        },
        "goals": [("ATP", ">=", 45), ("ROS", "<=", 72), ("CellHealth", ">=", 65)],
        "strategy": "推荐：糖酵解为主，少用呼吸链，适度抗氧化。",
        "modifier": {
            "card": "etc",
            "multiplier": {"ATP": 0.55, "ROS": 1.5},
            "note": "缺氧限制：呼吸链 ATP 收益降低，ROS 生成更明显。",
        },
    },
    {
        "name": "长期饥饿",
        "context": "外源葡萄糖不足，细胞必须切换到脂肪和氨基酸供能，同时管理氨毒性。",
        "initial": {
            "ATP": 46,
            "Glucose": 28,
            "Glycogen": 14,
            "Fat": 86,
            "AminoAcidPool": 52,
            "NADH": 40,
            "NADPH": 36,
            "ROS": 24,
            "NH3": 24,
            "CellHealth": 78,
        },
        "goals": [("Glucose", ">=", 42), ("ATP", ">=", 48), ("NH3", "<=", 62), ("CellHealth", ">=", 65)],
        "strategy": "推荐：脂肪动员 + β-氧化 + 糖异生 + 尿素循环。",
    },
    {
        "name": "氧化应激",
        "context": "ROS 已经偏高，NADPH 储备不足，过度追求 ATP 会进一步损伤细胞。",
        "initial": {
            "ATP": 54,
            "Glucose": 60,
            "Glycogen": 36,
            "Fat": 48,
            "AminoAcidPool": 44,
            "NADH": 46,
            "NADPH": 18,
            "ROS": 72,
            "NH3": 18,
            "CellHealth": 70,
        },
        "goals": [("ROS", "<=", 42), ("ATP", ">=", 45), ("CellHealth", ">=", 68)],
        "strategy": "推荐：PPP + 抗氧化修复 + 适度呼吸链。",
    },
    {
        "name": "高蛋白饮食",
        "context": "氨基酸池和 NH3 压力升高，需要把碳骨架纳入能量代谢，并及时解毒。",
        "initial": {
            "ATP": 52,
            "Glucose": 54,
            "Glycogen": 34,
            "Fat": 46,
            "AminoAcidPool": 84,
            "NADH": 38,
            "NADPH": 34,
            "ROS": 28,
            "NH3": 68,
            "CellHealth": 76,
        },
        "goals": [("NH3", "<=", 36), ("ATP", ">=", 48), ("Glucose", ">=", 40), ("CellHealth", ">=", 68)],
        "strategy": "推荐：尿素循环 + TCA + 适度糖异生。",
    },
]

SCREEN_TITLE = "TITLE"
SCREEN_MAIN_MENU = "MAIN_MENU"
SCREEN_TUTORIAL = "TUTORIAL"
SCREEN_SCENARIO_SELECT = "SCENARIO_SELECT"
SCREEN_GAME = "GAME"
SCREEN_RESULT = "RESULT"
SCREEN_ENCYCLOPEDIA = "ENCYCLOPEDIA"
SCREEN_FINAL_SUMMARY = "FINAL_SUMMARY"

SCENARIO_META = [
    {
        "subtitle": "富足中的分配",
        "knowledge": "葡萄糖可进入糖酵解、糖原合成或 PPP。",
        "idea": "富足时关键不是消耗一切，而是分流与储备。",
        "stars": 2,
        "cards": [0, 1, 6],
        "summary": "你在饭后状态下需要把过剩葡萄糖分配到供能、储备和还原力网络，体现代谢调控中的“富足分流”思想。",
    },
    {
        "subtitle": "快速供能与乳酸代价",
        "knowledge": "缺氧时呼吸链受限，糖酵解成为短期供能主线。",
        "idea": "抓住关键路径，同时承认代价。",
        "stars": 3,
        "cards": [1, 2, 3, 4],
        "summary": "短跑缺氧的核心不是盲目强化呼吸链，而是在 ATP 急需与 ROS 风险之间做短期取舍。",
    },
    {
        "subtitle": "逆势而行的糖异生",
        "knowledge": "饥饿时脂肪供能、糖异生和尿素循环需要协同。",
        "idea": "逆势而行必须付出能量成本。",
        "stars": 4,
        "cards": [5, 6, 9],
        "summary": "长期饥饿要求你动员脂肪并维持血糖，同时处理氨毒性，体现“逆势而行、协同调控”。",
    },
    {
        "subtitle": "产能与伤害同源",
        "knowledge": "氧化磷酸化能高效产能，也可能增加 ROS。",
        "idea": "效率越高，越需要配套防护。",
        "stars": 4,
        "cards": [6, 7, 8],
        "summary": "氧化应激关卡强调 NADPH 与抗氧化修复：产能系统和损伤压力往往来自同一套电子流。",
    },
    {
        "subtitle": "个性归氮，共性归碳",
        "knowledge": "氨基酸脱氨后，碳骨架可进入能量网络，氮必须安全排出。",
        "idea": "碳可再利用，氮要被清除。",
        "stars": 3,
        "cards": [5, 8, 9],
        "summary": "高蛋白饮食中，氨基酸碳骨架可供能，但 NH3 需要尿素循环付出 ATP 代价来清除。",
    },
]

EVENT_POOLS = [
    [
        {"name": "胰岛素信号增强", "effect": {"Glucose": -5, "Glycogen": 8}, "text": "胰岛素信号增强：葡萄糖更倾向进入储备。"},
        {"name": "血糖继续升高", "effect": {"Glucose": 12}, "text": "血糖继续升高：富足环境仍在扰动稳态。"},
    ],
    [
        {"name": "氧气不足", "effect": {"ROS": 8}, "text": "氧气不足：电子传递受限，ROS 压力上升。"},
        {"name": "肌肉急需 ATP", "effect": {"ATP": -12}, "text": "肌肉急需 ATP：能量账本被快速拉低。"},
    ],
    [
        {"name": "糖原耗尽", "effect": {"Glycogen": -10}, "text": "糖原耗尽：短期储备接近枯竭。"},
        {"name": "脂肪动员增强", "effect": {"Fat": -8, "NADH": 8}, "text": "脂肪动员增强：长期能源开始接管供能。"},
    ],
    [
        {"name": "ROS 突增", "effect": {"ROS": 18, "CellHealth": -5}, "text": "ROS 突增：氧化压力直接损伤细胞健康。"},
        {"name": "抗氧化需求上升", "effect": {"NADPH": -8, "ROS": -8}, "text": "抗氧化需求上升：NADPH 被用于降低氧化压力。"},
    ],
    [
        {"name": "氨基酸摄入增加", "effect": {"AminoAcidPool": 15, "NH3": 8}, "text": "氨基酸摄入增加：碳骨架增加，氮毒性也上升。"},
        {"name": "尿素循环负荷上升", "effect": {"ATP": -5, "NH3": -10}, "text": "肝脏尿素循环负荷上升：消耗 ATP 换取安全。"},
    ],
]

HORMONE_MODES = {
    "Normal": {"label": "Normal", "desc": "基础稳态模式：不改变卡牌效果。", "multipliers": {}},
    "Insulin": {
        "label": "Insulin 胰岛素",
        "desc": "促进葡萄糖利用和糖原合成，抑制糖异生。",
        "multipliers": {"glycogenesis": 1.25, "glycolysis": 1.12, "gluconeogenesis": 0.75},
    },
    "Glucagon": {
        "label": "Glucagon 胰高血糖素",
        "desc": "增强糖原分解和糖异生，削弱糖原合成。",
        "multipliers": {"glycogenolysis": 1.25, "gluconeogenesis": 1.2, "glycogenesis": 0.75},
    },
    "Adrenaline": {
        "label": "Adrenaline 肾上腺素",
        "desc": "增强快速供能，ROS 增长略快。",
        "multipliers": {"glycolysis": 1.18, "glycogenolysis": 1.18, "etc_ros": 1.15, "beta_oxidation_ros": 1.15},
    },
    "AMPK": {
        "label": "AMPK 应激",
        "desc": "增强分解代谢，削弱合成代谢，ATP 低时保护 CellHealth。",
        "multipliers": {"lipolysis": 1.15, "beta_oxidation": 1.12, "glycogenesis": 0.72, "ppp": 0.88},
    },
}

ENCYCLOPEDIA = [
    {"name": "G-6-P", "title": "糖代谢分流节点", "explain": "葡萄糖进入细胞后常被转化为 G-6-P，再进入糖酵解、PPP 或糖原代谢。", "role": "游戏中连接 Glucose、Glycolysis、PPP 与 Glycogen。", "idea": "同一底物，因需求不同而分流。", "level": 0},
    {"name": "PFK-1", "title": "糖酵解关键阀门", "explain": "PFK-1 是糖酵解的重要限速酶，受到能量状态调控。", "role": "对应糖酵解卡牌的关键控制思想。", "idea": "抓住关键，胜过平均用力。", "level": 0},
    {"name": "乳酸", "title": "缺氧下 NAD+ 再生的代价", "explain": "缺氧时丙酮酸可转为乳酸，以帮助再生 NAD+ 维持糖酵解。", "role": "短跑缺氧中提示少依赖呼吸链。", "idea": "短期续航往往伴随代价。", "level": 1},
    {"name": "NADH", "title": "呼吸链燃料", "explain": "NADH 携带高能电子，可被呼吸链利用产生 ATP。", "role": "TCA、β-氧化和呼吸链之间的桥梁。", "idea": "能量可以先被藏入势能。", "level": 1},
    {"name": "β-氧化", "title": "脂肪酸供能通路", "explain": "脂肪酸逐步分解产生乙酰辅酶A和还原当量。", "role": "长期饥饿中维持 ATP 的重要通路。", "idea": "长期能源要在合适情境下动员。", "level": 2},
    {"name": "糖异生", "title": "耗能维持血糖", "explain": "糖异生消耗 ATP，把非糖物质转化为葡萄糖。", "role": "低糖情境下维持 Glucose，但会带来 NH3 压力。", "idea": "逆势而行必须付出成本。", "level": 2},
    {"name": "NADPH", "title": "抗氧化与合成代谢还原力", "explain": "NADPH 支持脂质合成和谷胱甘肽抗氧化系统。", "role": "PPP 与抗氧化修复的核心资源。", "idea": "不直接产 ATP 的路径也可能更关键。", "level": 3},
    {"name": "ROS", "title": "产能系统的副产物", "explain": "电子传递过程可能产生 ROS，过量会损伤细胞。", "role": "限制呼吸链和 β-氧化滥用。", "idea": "效率与风险常常同源。", "level": 3},
    {"name": "尿素循环", "title": "清除氨毒性", "explain": "尿素循环消耗 ATP，把有毒的氨转化为尿素排出。", "role": "高蛋白饮食和饥饿中保护 CellHealth。", "idea": "牺牲能量以维持安全。", "level": 4},
    {"name": "氨基酸碳骨架", "title": "回归糖脂能量网络", "explain": "氨基酸脱氨后，碳骨架可进入 TCA 或糖异生。", "role": "连接蛋白质分解、糖异生和 TCA。", "idea": "个性归氮，共性归碳。", "level": 4},
]

MAP_NODES = {
    "Glucose": (345, 245),
    "G-6-P": (430, 245),
    "Glycolysis": (535, 245),
    "Pyruvate": (645, 245),
    "Acetyl-CoA": (735, 245),
    "TCA": (815, 245),
    "NADH": (815, 330),
    "ETC": (720, 330),
    "ATP": (620, 330),
    "PPP": (430, 330),
    "NADPH": (535, 330),
    "Antioxidant": (535, 410),
    "ROS": (640, 410),
    "Glycogen": (345, 330),
    "Fat": (575, 155),
    "Beta-oxidation": (705, 155),
    "Amino Acids": (345, 435),
    "NH3": (460, 435),
    "Urea Cycle": (585, 435),
    "Carbon Skeleton": (735, 435),
    "Gluconeogenesis": (815, 365),
}

MAP_EDGES = [
    ("Glucose", "G-6-P"),
    ("G-6-P", "Glycolysis"),
    ("Glycolysis", "Pyruvate"),
    ("Pyruvate", "Acetyl-CoA"),
    ("Acetyl-CoA", "TCA"),
    ("TCA", "NADH"),
    ("NADH", "ETC"),
    ("ETC", "ATP"),
    ("G-6-P", "PPP"),
    ("PPP", "NADPH"),
    ("NADPH", "Antioxidant"),
    ("Antioxidant", "ROS"),
    ("Glycogen", "Glucose"),
    ("Glucose", "Glycogen"),
    ("Fat", "Beta-oxidation"),
    ("Beta-oxidation", "Acetyl-CoA"),
    ("Amino Acids", "NH3"),
    ("NH3", "Urea Cycle"),
    ("Amino Acids", "Carbon Skeleton"),
    ("Carbon Skeleton", "TCA"),
    ("Carbon Skeleton", "Gluconeogenesis"),
]


def clamp(value):
    return max(0, min(100, int(round(value))))


def load_font(size, bold=False):
    win_dir = os.environ.get("WINDIR", r"C:\Windows")
    font_dir = os.path.join(win_dir, "Fonts")
    candidates = [
        "msyhbd.ttc" if bold else "msyh.ttc",
        "simhei.ttf",
        "simsun.ttc",
        "simsunb.ttf" if bold else "simsun.ttc",
    ]
    for filename in candidates:
        font_path = os.path.join(font_dir, filename)
        if os.path.exists(font_path):
            return pygame.font.Font(font_path, size)

    names = ["Microsoft YaHei", "SimHei", "SimSun", "Arial Unicode MS"]
    for name in names:
        font_path = pygame.font.match_font(name, bold=bold)
        if font_path:
            return pygame.font.Font(font_path, size)
    return pygame.font.SysFont(None, size, bold=bold)


def draw_text(surface, text, font, color, pos):
    surface.blit(font.render(text, True, color), pos)


def wrap_text(text, font, max_width):
    lines = []
    for paragraph in text.split("\n"):
        current = ""
        for char in paragraph:
            test = current + char
            if font.size(test)[0] <= max_width:
                current = test
            else:
                if current:
                    lines.append(current)
                current = char
        if current:
            lines.append(current)
    return lines


def draw_wrapped(surface, text, font, color, rect, line_gap=4):
    y = rect.y
    for line in wrap_text(text, font, rect.width):
        if y + font.get_height() > rect.bottom:
            break
        draw_text(surface, line, font, color, (rect.x, y))
        y += font.get_height() + line_gap


def rounded_rect(surface, rect, color, radius=10, border=None, border_width=1):
    pygame.draw.rect(surface, color, rect, border_radius=radius)
    if border:
        pygame.draw.rect(surface, border, rect, width=border_width, border_radius=radius)


def draw_arrow(surface, start, end, color, width=2):
    pygame.draw.line(surface, color, start, end, width)
    angle = math.atan2(end[1] - start[1], end[0] - start[0])
    head_len = 9
    left = (
        end[0] - head_len * math.cos(angle - math.pi / 6),
        end[1] - head_len * math.sin(angle - math.pi / 6),
    )
    right = (
        end[0] - head_len * math.cos(angle + math.pi / 6),
        end[1] - head_len * math.sin(angle + math.pi / 6),
    )
    pygame.draw.polygon(surface, color, [end, left, right])


def effect_to_text(effect):
    parts = []
    for key, value in effect.items():
        sign = "+" if value > 0 else ""
        parts.append(f"{key} {sign}{value}")
    return "  ".join(parts)

def lerp(a, b, t):
    return a + (b - a) * max(0.0, min(1.0, t))


def approach(current, target, speed, dt):
    return lerp(current, target, 1 - math.exp(-speed * dt))


def mix(c1, c2, t):
    t = max(0.0, min(1.0, t))
    return tuple(int(c1[i] + (c2[i] - c1[i]) * t) for i in range(3))


def inflate_center(rect, scale):
    w = int(rect.width * scale)
    h = int(rect.height * scale)
    return pygame.Rect(rect.centerx - w // 2, rect.centery - h // 2, w, h)


def draw_soft_glow(surface, rect, color, strength=28, radius=12):
    glow = pygame.Surface((rect.width + strength * 2, rect.height + strength * 2), pygame.SRCALPHA)
    for i in range(strength, 0, -7):
        alpha = int(9 * (i / strength) ** 1.7)
        pygame.draw.rect(
            glow,
            (*color, alpha),
            pygame.Rect(strength - i, strength - i, rect.width + i * 2, rect.height + i * 2),
            border_radius=radius + i,
        )
    surface.blit(glow, (rect.x - strength, rect.y - strength))


def edge_progress_point(start, end, progress):
    return (start[0] + (end[0] - start[0]) * progress, start[1] + (end[1] - start[1]) * progress)


class Game:
    STATUS_SMOOTH_SPEED = 6.0
    CARD_ANIM_SPEED = 13.0
    LOG_FADE_SPEED = 10.0
    PATH_DURATION = 1.35
    INPUT_LOCK_SECONDS = 1.65

    def __init__(self):
        pygame.init()
        pygame.display.set_caption("代谢之城 Cell City")
        self.screen = pygame.display.set_mode((WIDTH, HEIGHT))
        self.clock = pygame.time.Clock()
        self.font_xs = load_font(14)
        self.font_sm = load_font(16)
        self.font_md = load_font(20)
        self.font_lg = load_font(28, bold=True)
        self.font_title = load_font(38, bold=True)
        self.level_index = 0
        self.screen_state = SCREEN_TITLE
        self.tutorial_page = 0
        self.completed_levels = set()
        self.encyclopedia_return = SCREEN_TITLE
        self.result_from_level = 0
        self.hormone_mode = "Normal"
        self.hormone_switch_turn = -3
        self.event_popup = None
        self.card_scroll = 0
        self.mode = "playing"
        self.time = 0.0
        self.display_state = {}
        self.card_anim = [{"hover": 0.0, "select": 0.0, "flash": 0.0} for _ in CARDS]
        self.log_items = []
        self.input_locked = False
        self.input_lock_timer = 0.0
        self.path_timer = 0.0
        self.path_duration = self.PATH_DURATION
        self.active_edges = []
        self.pending_result = False
        self.execute_rect = pygame.Rect(960, 610, 132, 42)
        self.next_rect = pygame.Rect(1110, 610, 112, 42)
        self.reset_level()

    @property
    def level(self):
        return LEVELS[self.level_index]

    def reset_level(self):
        self.state = deepcopy(LEVELS[self.level_index]["initial"])
        self.display_state = {key: float(value) for key, value in self.state.items()}
        self.turn = 0
        self.selected = []
        self.card_scroll = 0
        self.active_nodes = []
        self.active_edges = []
        self.path_timer = 0.0
        self.pending_result = False
        self.input_locked = False
        self.input_lock_timer = 0.0
        self.hormone_mode = "Normal"
        self.hormone_switch_turn = -3
        self.event_popup = None
        self.log_items = []
        self.add_log(f"进入「{LEVELS[self.level_index]['name']}」。选择 2 张行动卡，调度代谢通量。")
        self.mode = "playing"

    def start_level(self, index):
        self.level_index = index
        self.reset_level()
        self.screen_state = SCREEN_GAME

    def can_switch_hormone(self):
        return self.turn - self.hormone_switch_turn >= 3 and not self.input_locked

    def set_hormone_mode(self, mode):
        if mode == self.hormone_mode or not self.can_switch_hormone():
            return
        self.hormone_mode = mode
        self.hormone_switch_turn = self.turn
        self.add_log(f"全局调控切换为 {HORMONE_MODES[mode]['label']}：{HORMONE_MODES[mode]['desc']}")

    def add_log(self, text):
        self.log_items.insert(0, {"text": text, "age": 0.0, "y": -18.0, "alpha": 0.0})
        self.log_items = self.log_items[:6]

    def modified_effect(self, card):
        effect = deepcopy(card["effect"])
        modifier = self.level.get("modifier")
        if modifier and modifier["card"] == card["id"]:
            for key, multiplier in modifier.get("multiplier", {}).items():
                if key in effect:
                    effect[key] = int(round(effect[key] * multiplier))
        mode = HORMONE_MODES[self.hormone_mode]
        multiplier = mode["multipliers"].get(card["id"], 1.0)
        if multiplier != 1.0:
            for key in list(effect.keys()):
                effect[key] = int(round(effect[key] * multiplier))
        if self.hormone_mode == "Adrenaline":
            ros_key = f"{card['id']}_ros"
            if "ROS" in effect and ros_key in mode["multipliers"]:
                effect["ROS"] = int(round(effect["ROS"] * mode["multipliers"][ros_key]))
        return effect

    def apply_homeostatic_pressure(self):
        s = self.state
        if s["ROS"] > 65:
            s["CellHealth"] -= math.ceil((s["ROS"] - 65) / 8)
        if s["NH3"] > 55:
            s["CellHealth"] -= math.ceil((s["NH3"] - 55) / 9)
        if s["ATP"] < 25:
            s["CellHealth"] -= 4
        if s["Glucose"] < 18:
            s["CellHealth"] -= 3
        if s["Glucose"] > 82:
            s["CellHealth"] -= 2
        if s["NADH"] > 85:
            s["ROS"] += 4
        if s["NADPH"] < 15 and s["ROS"] > 45:
            s["CellHealth"] -= 2
        if self.hormone_mode == "AMPK" and s["ATP"] < 35:
            s["CellHealth"] += 2
        for key in STATE_KEYS:
            s[key] = clamp(s[key])

    def apply_event(self):
        event = random.choice(EVENT_POOLS[self.level_index])
        for key, delta in event["effect"].items():
            self.state[key] = clamp(self.state[key] + delta)
        self.event_popup = {"text": event["text"], "age": 0.0}
        self.add_log("事件扰动：" + event["text"] + " 稳态不是静止，而是在扰动中重新调配。")
        self.apply_homeostatic_pressure()

    def execute_turn(self):
        if self.screen_state != SCREEN_GAME or self.input_locked or len(self.selected) != 2:
            return
        chosen = [CARDS[i] for i in self.selected]
        explanations = []
        active = set()
        edges = []
        old_selected = list(self.selected)
        for card in chosen:
            effect = self.modified_effect(card)
            for key, delta in effect.items():
                self.state[key] = clamp(self.state[key] + delta)
            explanations.append(f"{card['name']}：{card['explain']}")
            active.update(card["nodes"])
            for a, b in zip(card["nodes"], card["nodes"][1:]):
                if a in MAP_NODES and b in MAP_NODES:
                    edges.append((a, b))
        self.apply_homeostatic_pressure()
        self.turn += 1
        if self.turn % 3 == 0:
            self.apply_event()
        self.active_nodes = list(active)
        self.active_edges = edges
        self.path_timer = self.path_duration
        self.input_locked = True
        self.input_lock_timer = self.INPUT_LOCK_SECONDS
        self.add_log(f"第 {self.turn} 回合：" + "  ".join(explanations))
        for index in old_selected:
            self.card_anim[index]["flash"] = 1.0
        self.selected = []
        if self.turn >= 10 or self.state["CellHealth"] <= 0:
            self.pending_result = True

    def goal_met(self, goal):
        key, op, value = goal
        return self.state[key] >= value if op == ">=" else self.state[key] <= value

    def evaluate(self):
        checks = [
            self.state["ATP"] >= 50,
            35 <= self.state["Glucose"] <= 70,
            self.state["ROS"] <= 55,
            self.state["NH3"] <= 50,
            self.state["CellHealth"] >= 70,
        ]
        score = sum(20 for ok in checks if ok)
        passed = all(self.goal_met(goal) for goal in self.level["goals"])
        maxim = "稳态来自调度，而不是单一路径的极限输出。"
        if self.state["ROS"] > 65:
            maxim = "高能通量必须配套还原力，否则效率会转化为损伤。"
        if self.state["NH3"] > 60:
            maxim = "碳骨架可以被利用，氨毒性必须被付费清除。"
        if self.state["Glucose"] < 30:
            maxim = "缺糖时要逆势而行，但糖异生不能脱离能量账本。"
        if self.state["ATP"] < 40:
            maxim = "能量不足时，优先抓住最短的供能路径。"
        if passed and score >= 80:
            maxim = "能量、物质、还原力和毒性被纳入同一张动态账本。"
        return score, passed, maxim

    def update(self, dt):
        self.time += dt
        mouse = pygame.mouse.get_pos()
        for key in STATE_KEYS:
            self.display_state[key] = approach(self.display_state[key], self.state[key], self.STATUS_SMOOTH_SPEED, dt)
        for i, rect in enumerate(self.card_rects()):
            hovered = rect.collidepoint(mouse) and 150 <= mouse[1] <= 492 and self.screen_state == SCREEN_GAME and not self.input_locked
            self.card_anim[i]["hover"] = approach(self.card_anim[i]["hover"], 1.0 if hovered else 0.0, self.CARD_ANIM_SPEED, dt)
            self.card_anim[i]["select"] = approach(self.card_anim[i]["select"], 1.0 if i in self.selected else 0.0, self.CARD_ANIM_SPEED, dt)
            self.card_anim[i]["flash"] = max(0.0, self.card_anim[i]["flash"] - dt * 2.5)
        for item in self.log_items:
            item["age"] += dt
            item["y"] = approach(item["y"], 0.0, 12.0, dt)
            item["alpha"] = approach(item["alpha"], 255.0, self.LOG_FADE_SPEED, dt)
        if self.event_popup:
            self.event_popup["age"] += dt
            if self.event_popup["age"] > 2.4:
                self.event_popup = None
        if self.path_timer > 0:
            self.path_timer = max(0.0, self.path_timer - dt)
        elif self.active_edges and not self.input_locked:
            self.active_edges = []
            self.active_nodes = []
        if self.input_locked:
            self.input_lock_timer = max(0.0, self.input_lock_timer - dt)
            if self.input_lock_timer <= 0:
                self.input_locked = False
                if self.pending_result:
                    self.pending_result = False
                    self.result_from_level = self.level_index
                    self.screen_state = SCREEN_RESULT

    def draw_panel(self, rect, accent=CYAN):
        pulse = 0.45 + 0.25 * math.sin(self.time * 1.6)
        draw_soft_glow(self.screen, rect, accent, strength=18, radius=12)
        rounded_rect(self.screen, rect, PANEL, 12, mix((45, 78, 120), accent, pulse * 0.22), 1)

    def draw_background(self):
        self.screen.fill(BG)
        grid_color = (10, 22, 45)
        for x in range(0, WIDTH, 42):
            pygame.draw.line(self.screen, grid_color, (x, 0), (x, HEIGHT), 1)
        for y in range(0, HEIGHT, 42):
            pygame.draw.line(self.screen, grid_color, (0, y), (WIDTH, y), 1)
        for radius, alpha, center, color in [
            (250, 38, (220 + math.sin(self.time * 0.35) * 18, 80), CYAN),
            (300, 30, (1010, 90 + math.cos(self.time * 0.28) * 20), VIOLET),
            (180, 20, (690 + math.sin(self.time * 0.42) * 16, 430), CYAN),
        ]:
            glow = pygame.Surface((radius * 2, radius * 2), pygame.SRCALPHA)
            for r in range(radius, 0, -8):
                a = int(alpha * (r / radius) ** 2)
                pygame.draw.circle(glow, (*color, a), (radius, radius), r)
            self.screen.blit(glow, (center[0] - radius, center[1] - radius))

    def draw_menu_button(self, rect, text, accent=CYAN, enabled=True):
        self.draw_button(rect, text, enabled, accent)
        return rect

    def draw_title(self):
        self.draw_background()
        core = (WIDTH // 2, 245)
        for i in range(7):
            angle = self.time * (0.35 + i * 0.04) + i
            radius = 82 + i * 18
            x = core[0] + math.cos(angle) * radius
            y = core[1] + math.sin(angle * 0.8) * radius * 0.38
            pygame.draw.circle(self.screen, (*CYAN, 120), (int(x), int(y)), 3 + i % 3)
            pygame.draw.line(self.screen, (38, 108, 150), core, (int(x), int(y)), 1)
        draw_soft_glow(self.screen, pygame.Rect(core[0] - 90, core[1] - 90, 180, 180), CYAN, 45, 90)
        pygame.draw.circle(self.screen, (19, 39, 78), core, 58)
        pygame.draw.circle(self.screen, CYAN, core, 58, 2)
        title_alpha = 0.75 + 0.25 * math.sin(self.time * 1.4)
        draw_text(self.screen, "代谢之城 Cell City", self.font_title, mix(TEXT, CYAN, title_alpha * 0.25), (410, 95))
        draw_text(self.screen, "A Strategy Game of Metabolic Homeostasis", self.font_md, MUTED, (438, 145))
        draw_text(self.screen, "分子有代谢，反应成生命。", self.font_lg, CYAN, (470, 410))
        buttons = [
            ("开始游戏", SCREEN_MAIN_MENU),
            ("教程模式", SCREEN_TUTORIAL),
            ("生化图鉴", SCREEN_ENCYCLOPEDIA),
            ("退出游戏", "QUIT"),
        ]
        self.title_buttons = []
        for i, (label, target) in enumerate(buttons):
            rect = pygame.Rect(520, 468 + i * 54, 240, 42)
            self.draw_menu_button(rect, label, CYAN if i == 0 else VIOLET)
            self.title_buttons.append((rect, target))
        pygame.display.flip()

    def draw_main_menu(self):
        self.draw_background()
        self.draw_panel(pygame.Rect(330, 100, 620, 500), VIOLET)
        draw_text(self.screen, "主菜单", self.font_title, TEXT, (575, 150))
        items = [
            ("剧情模式", SCREEN_SCENARIO_SELECT, CYAN, True),
            ("挑战模式（开发中）", None, VIOLET, False),
            ("教程模式", SCREEN_TUTORIAL, VIOLET, True),
            ("生化图鉴", SCREEN_ENCYCLOPEDIA, VIOLET, True),
            ("返回标题", SCREEN_TITLE, VIOLET, True),
        ]
        self.menu_buttons = []
        for i, (label, target, color, enabled) in enumerate(items):
            rect = pygame.Rect(500, 235 + i * 62, 280, 44)
            self.draw_menu_button(rect, label, color, enabled)
            self.menu_buttons.append((rect, target, enabled))
        pygame.display.flip()

    def draw_tutorial(self):
        pages = [
            ("状态条说明", ["ATP：能量供应", "Glucose：糖代谢底物", "NADH：呼吸链燃料", "NADPH：抗氧化与合成代谢能力", "ROS / NH3：代谢压力", "Cell Health：细胞稳态水平"]),
            ("操作说明", ["每回合选择 2 张行动卡牌", "点击“执行本回合”更新状态", "观察代谢地图路径高亮和状态变化", "事件扰动会迫使你重新调配资源"]),
            ("胜利逻辑", ["不要追求单一指标最大化", "ATP 过低会失败", "ROS / NH3 过高会伤害细胞", "真正目标是动态稳态"]),
        ]
        self.draw_background()
        self.draw_panel(pygame.Rect(170, 90, 940, 520), CYAN)
        title, lines = pages[self.tutorial_page]
        draw_text(self.screen, f"教程 {self.tutorial_page + 1}/3：{title}", self.font_title, TEXT, (230, 145))
        y = 230
        for line in lines:
            draw_text(self.screen, "• " + line, self.font_md, CYAN if ":" in line or "：" in line else TEXT, (270, y))
            y += 56
        self.tutorial_prev = pygame.Rect(250, 540, 130, 42)
        self.tutorial_next = pygame.Rect(900, 540, 130, 42)
        self.tutorial_back = pygame.Rect(565, 540, 150, 42)
        self.draw_menu_button(self.tutorial_prev, "上一页", VIOLET, self.tutorial_page > 0)
        self.draw_menu_button(self.tutorial_next, "下一页", VIOLET, self.tutorial_page < 2)
        self.draw_menu_button(self.tutorial_back, "返回", CYAN)
        pygame.display.flip()

    def draw_scenario_select(self):
        self.draw_background()
        draw_text(self.screen, "选择生理情境", self.font_title, TEXT, (48, 42))
        draw_text(self.screen, "每个关卡都是一次稳态调度问题。完成后会解锁对应图鉴高亮。", self.font_sm, MUTED, (52, 92))
        self.scenario_rects = []
        for i, level in enumerate(LEVELS):
            meta = SCENARIO_META[i]
            col = i % 3
            row = i // 3
            rect = pygame.Rect(54 + col * 400, 145 + row * 235, 360, 190)
            self.scenario_rects.append(rect)
            self.draw_panel(rect, CYAN if i not in self.completed_levels else GREEN)
            draw_text(self.screen, f"{i + 1}. {level['name']}", self.font_md, TEXT, (rect.x + 18, rect.y + 16))
            draw_text(self.screen, meta["subtitle"], self.font_sm, CYAN, (rect.x + 18, rect.y + 48))
            draw_wrapped(self.screen, "背景：" + level["context"], self.font_xs, MUTED, pygame.Rect(rect.x + 18, rect.y + 76, 320, 36), 2)
            draw_wrapped(self.screen, "核心：" + meta["knowledge"], self.font_xs, TEXT, pygame.Rect(rect.x + 18, rect.y + 116, 320, 34), 2)
            draw_text(self.screen, "★" * meta["stars"] + "☆" * (5 - meta["stars"]), self.font_sm, AMBER, (rect.x + 18, rect.y + 154))
            if i in self.completed_levels:
                draw_text(self.screen, "已完成", self.font_sm, GREEN, (rect.x + 280, rect.y + 154))
        self.scenario_back = pygame.Rect(1040, 640, 150, 42)
        self.draw_menu_button(self.scenario_back, "返回菜单", VIOLET)
        pygame.display.flip()

    def draw_encyclopedia(self):
        self.draw_background()
        draw_text(self.screen, "生化图鉴", self.font_title, TEXT, (48, 38))
        draw_text(self.screen, "已完成关卡相关卡片会以绿色标记。", self.font_sm, MUTED, (52, 86))
        for i, card in enumerate(ENCYCLOPEDIA):
            col = i % 2
            row = i // 2
            rect = pygame.Rect(54 + col * 600, 125 + row * 105, 560, 88)
            highlighted = card["level"] in self.completed_levels
            self.draw_panel(rect, GREEN if highlighted else VIOLET)
            draw_text(self.screen, f"{card['name']}：{card['title']}", self.font_sm, GREEN if highlighted else CYAN, (rect.x + 14, rect.y + 10))
            draw_wrapped(self.screen, card["explain"] + " " + card["role"], self.font_xs, TEXT, pygame.Rect(rect.x + 14, rect.y + 34, 520, 24), 1)
            draw_text(self.screen, "思想：" + card["idea"], self.font_xs, MUTED, (rect.x + 14, rect.y + 63))
        self.encyclopedia_back = pygame.Rect(1050, 650, 150, 42)
        self.draw_menu_button(self.encyclopedia_back, "返回", CYAN)
        pygame.display.flip()

    def draw_top(self):
        rect = pygame.Rect(18, 14, 1244, 82)
        self.draw_panel(rect, CYAN)
        draw_text(self.screen, "代谢之城 Cell City", self.font_title, TEXT, (38, 24))
        draw_text(self.screen, "A Strategy Game of Metabolic Homeostasis", self.font_sm, MUTED, (42, 66))
        draw_text(self.screen, f"关卡 {self.level_index + 1}/5：{self.level['name']}", self.font_md, CYAN, (545, 26))
        draw_text(self.screen, f"回合 {self.turn}/10", self.font_md, VIOLET, (545, 58))
        goal_texts = []
        for key, op, value in self.level["goals"]:
            mark = "✓" if self.goal_met((key, op, value)) else "○"
            goal_texts.append(f"{mark} {key} {op} {value}")
        draw_wrapped(self.screen, "目标：" + "；".join(goal_texts), self.font_sm, TEXT, pygame.Rect(760, 25, 470, 50), 3)

    def draw_status(self):
        rect = pygame.Rect(18, 112, 250, 430)
        self.draw_panel(rect, CYAN)
        draw_text(self.screen, "状态条", self.font_md, CYAN, (36, 128))
        y = 166
        for key in STATE_KEYS:
            value = self.display_state[key]
            target_value = self.state[key]
            color = CYAN
            danger = False
            if key in ("ROS", "NH3"):
                danger = target_value >= 70
                color = RED if target_value >= 70 else AMBER if target_value >= 45 else GREEN
            if key == "CellHealth":
                danger = target_value < 40
                color = RED if target_value < 40 else AMBER if target_value < 70 else GREEN
            draw_text(self.screen, STATE_LABELS[key], self.font_xs, TEXT, (36, y))
            draw_text(self.screen, str(int(round(value))), self.font_xs, color, (225, y))
            bar = pygame.Rect(36, y + 22, 198, 11)
            if danger:
                draw_soft_glow(self.screen, bar.inflate(8, 8), RED, strength=12, radius=7)
            pygame.draw.rect(self.screen, (22, 31, 58), bar, border_radius=6)
            fill_rect = pygame.Rect(bar.x, bar.y, int(bar.width * value / 100), bar.height)
            pygame.draw.rect(self.screen, color, fill_rect, border_radius=6)
            shine = pygame.Rect(fill_rect.x + 2, fill_rect.y + 2, max(0, fill_rect.width - 4), 3)
            pygame.draw.rect(self.screen, mix(color, WHITE, 0.45), shine, border_radius=3)
            y += 37

    def draw_map(self):
        rect = pygame.Rect(288, 112, 560, 430)
        self.draw_panel(rect, CYAN)
        draw_text(self.screen, "代谢地图", self.font_md, CYAN, (306, 128))
        path_phase = 1.0 - self.path_timer / self.path_duration if self.path_duration else 1.0
        for start, end in MAP_EDGES:
            active = (start, end) in self.active_edges or (end, start) in self.active_edges
            draw_arrow(self.screen, MAP_NODES[start], MAP_NODES[end], CYAN if active else (68, 84, 116), 3 if active else 1)
            if active and self.path_timer > 0:
                for offset in (0.0, 0.33, 0.66):
                    p = (path_phase + offset) % 1.0
                    dot = edge_progress_point(MAP_NODES[start], MAP_NODES[end], p)
                    pygame.draw.circle(self.screen, (190, 245, 255), (int(dot[0]), int(dot[1])), 4)
        for name, pos in MAP_NODES.items():
            active = name in self.active_nodes
            label = self.font_xs.render(name, True, TEXT if active else (202, 213, 226))
            w = max(52, label.get_width() + 14)
            node_rect = pygame.Rect(pos[0] - w // 2, pos[1] - 13, w, 26)
            if active:
                pulse = 0.5 + 0.5 * math.sin(self.time * 9.0)
                draw_soft_glow(self.screen, node_rect.inflate(8 + int(pulse * 8), 8 + int(pulse * 8)), CYAN, strength=16, radius=9)
            rounded_rect(self.screen, node_rect, CYAN_DARK if active else (15, 23, 42), 7, CYAN if active else (71, 85, 105), 1)
            self.screen.blit(label, (node_rect.centerx - label.get_width() // 2, node_rect.centery - label.get_height() // 2))
        draw_wrapped(self.screen, self.level["context"], self.font_sm, MUTED, pygame.Rect(306, 486, 515, 42))

    def card_rects(self):
        rects = []
        x0, y0 = 874, 154 - self.card_scroll
        card_w, card_h = 176, 88
        for i, card in enumerate(CARDS):
            col = i % 2
            row = i // 2
            rects.append(pygame.Rect(x0 + col * 188, y0 + row * 98, card_w, card_h))
        return rects

    def draw_cards(self):
        area = pygame.Rect(864, 112, 398, 430)
        self.draw_panel(area, VIOLET)
        draw_text(self.screen, f"行动卡牌  已选 {len(self.selected)}/2", self.font_md, VIOLET, (882, 128))
        clip = self.screen.get_clip()
        self.screen.set_clip(pygame.Rect(872, 150, 380, 335))
        for i, rect in enumerate(self.card_rects()):
            if rect.bottom < 150 or rect.top > 492:
                continue
            card = CARDS[i]
            selected = i in self.selected
            anim = self.card_anim[i]
            lift = int(anim["hover"] * 5)
            scale = 1.0 + anim["select"] * 0.035 + anim["flash"] * 0.035
            draw_rect = inflate_center(rect.move(0, -lift), scale)
            glow_power = max(anim["hover"], anim["select"], anim["flash"])
            if glow_power > 0.05:
                draw_soft_glow(self.screen, draw_rect, CYAN if selected else VIOLET, strength=int(18 + glow_power * 18), radius=10)
            color = mix(PANEL_2, (21, 44, 73), max(anim["select"], anim["flash"] * 0.7))
            border = mix((71, 85, 105), CYAN if selected else VIOLET, max(anim["hover"], anim["select"], anim["flash"]))
            rounded_rect(self.screen, draw_rect, color, 10, border, 2 if selected or anim["flash"] > 0.1 else 1)
            draw_text(self.screen, card["name"], self.font_sm, TEXT, (draw_rect.x + 10, draw_rect.y + 8))
            draw_text(self.screen, card["pathway"], self.font_xs, VIOLET, (draw_rect.x + 10, draw_rect.y + 31))
            effect = self.modified_effect(card)
            draw_wrapped(self.screen, effect_to_text(effect), self.font_xs, CYAN, pygame.Rect(draw_rect.x + 10, draw_rect.y + 54, draw_rect.w - 18, 28), 0)
        self.screen.set_clip(clip)
        draw_wrapped(self.screen, self.level["strategy"], self.font_sm, MUTED, pygame.Rect(882, 492, 345, 38))

    def draw_button(self, rect, text, enabled=True, accent=CYAN):
        mouse = pygame.mouse.get_pos()
        pressed = pygame.mouse.get_pressed()[0] and rect.collidepoint(mouse)
        hover = rect.collidepoint(mouse) and enabled and not self.input_locked
        y = -3 if hover else 0
        scale = 0.97 if pressed and enabled else 1.0
        draw_rect = inflate_center(rect.move(0, y), scale)
        base = accent if enabled else (51, 65, 85)
        if hover:
            draw_soft_glow(self.screen, draw_rect, accent, strength=18, radius=9)
            base = mix(base, WHITE, 0.18)
        rounded_rect(self.screen, draw_rect, base, 9, mix(base, WHITE, 0.25), 1)
        label_color = BG if enabled and accent == CYAN else TEXT if enabled else MUTED
        text_surface = self.font_sm.render(text, True, label_color)
        self.screen.blit(text_surface, (draw_rect.centerx - text_surface.get_width() // 2, draw_rect.centery - text_surface.get_height() // 2))

    def draw_hormone_panel(self):
        draw_text(self.screen, "激素 / 全局调控", self.font_xs, VIOLET, (960, 572))
        self.hormone_rects = []
        modes = list(HORMONE_MODES.keys())
        for i, mode in enumerate(modes):
            rect = pygame.Rect(960 + (i % 3) * 86, 594 + (i // 3) * 28, 78, 22)
            enabled = self.can_switch_hormone() or mode == self.hormone_mode
            active = mode == self.hormone_mode
            color = CYAN if active else VIOLET
            rounded_rect(self.screen, rect, (19, 39, 78) if active else (20, 28, 55), 7, color if enabled else (71, 85, 105), 1)
            label = mode if mode != "Adrenaline" else "Adren."
            text_surface = self.font_xs.render(label, True, TEXT if enabled else MUTED)
            self.screen.blit(text_surface, (rect.centerx - text_surface.get_width() // 2, rect.centery - text_surface.get_height() // 2))
            self.hormone_rects.append((rect, mode))
        desc = HORMONE_MODES[self.hormone_mode]["desc"]
        draw_wrapped(self.screen, desc, self.font_xs, MUTED, pygame.Rect(960, 650, 260, 30), 1)

    def draw_log(self):
        rect = pygame.Rect(18, 558, 1244, 144)
        self.draw_panel(rect, CYAN)
        draw_text(self.screen, "事件日志 / 本回合解释", self.font_md, CYAN, (36, 574))
        y = 608
        for idx, item in enumerate(self.log_items[:3]):
            alpha = int(max(0, min(255, item["alpha"])))
            highlight = max(0.0, 1.0 - item["age"] / 1.8) if idx == 0 else 0.0
            line_rect = pygame.Rect(30, int(y + item["y"]) - 3, 905, 28)
            if highlight > 0.02:
                rounded_rect(self.screen, line_rect, mix((15, 23, 42), CYAN_DARK, highlight * 0.5), 7, mix((45, 78, 120), CYAN, highlight), 1)
            temp = pygame.Surface((910, 32), pygame.SRCALPHA)
            draw_wrapped(temp, item["text"], self.font_sm, (*TEXT, alpha), pygame.Rect(6, 3, 900, 26), 2)
            self.screen.blit(temp, (30, int(y + item["y"])))
            y += 30
        self.draw_hormone_panel()
        self.execute_rect = pygame.Rect(960, 690, 132, 30)
        self.next_rect = pygame.Rect(1110, 690, 112, 30)
        can_execute = len(self.selected) == 2 and self.screen_state == SCREEN_GAME and not self.input_locked
        self.draw_button(self.execute_rect, "执行本回合", can_execute, CYAN)
        self.draw_button(self.next_rect, "下一关", not self.input_locked, VIOLET)
        if self.level.get("modifier"):
            draw_wrapped(self.screen, self.level["modifier"]["note"], self.font_xs, AMBER, pygame.Rect(36, 682, 880, 20), 1)
        if self.event_popup:
            alpha = max(0.0, 1.0 - self.event_popup["age"] / 2.4)
            popup = pygame.Rect(350, 515, 580, 42)
            draw_soft_glow(self.screen, popup, AMBER, strength=22, radius=10)
            rounded_rect(self.screen, popup, (58, 41, 15), 10, AMBER, 1)
            draw_wrapped(self.screen, self.event_popup["text"], self.font_sm, mix(AMBER, TEXT, alpha * 0.5), pygame.Rect(370, 526, 540, 18), 1)

    def draw_result(self):
        self.draw_background()
        box = pygame.Rect(150, 80, 980, 560)
        draw_soft_glow(self.screen, box, CYAN, strength=35, radius=16)
        rounded_rect(self.screen, box, (8, 13, 32), 16, CYAN, 2)
        score, passed, maxim = self.evaluate()
        grade = "S" if score >= 90 else "A" if score >= 75 else "B" if score >= 55 else "C"
        title = "稳态达成" if passed else "稳态失衡"
        draw_text(self.screen, f"{self.level['name']} · {title}", self.font_title, GREEN if passed else AMBER, (205, 120))
        draw_text(self.screen, f"评分：{grade}  ({score})", self.font_lg, VIOLET, (850, 130))
        metrics = [
            ("ATP 稳定性", self.state["ATP"], self.state["ATP"] >= 50),
            ("血糖控制", self.state["Glucose"], 35 <= self.state["Glucose"] <= 70),
            ("ROS 控制", self.state["ROS"], self.state["ROS"] <= 55),
            ("NH3 控制", self.state["NH3"], self.state["NH3"] <= 50),
            ("Cell Health", self.state["CellHealth"], self.state["CellHealth"] >= 70),
        ]
        y = 210
        for label, value, ok in metrics:
            color = GREEN if ok else AMBER
            draw_text(self.screen, f"{label}: {value}", self.font_md, color, (220, y))
            pygame.draw.rect(self.screen, (22, 31, 58), pygame.Rect(420, y + 8, 260, 10), border_radius=6)
            pygame.draw.rect(self.screen, color, pygame.Rect(420, y + 8, int(260 * value / 100), 10), border_radius=6)
            y += 46
        summary = SCENARIO_META[self.level_index]["summary"] + " " + maxim
        draw_wrapped(self.screen, summary, self.font_md, TEXT, pygame.Rect(720, 215, 350, 190), 8)
        self.retry_rect = pygame.Rect(230, 548, 130, 44)
        self.result_next_rect = pygame.Rect(390, 548, 130, 44)
        self.result_select_rect = pygame.Rect(550, 548, 170, 44)
        self.result_book_rect = pygame.Rect(750, 548, 170, 44)
        self.draw_button(self.retry_rect, "重试本关", True, VIOLET)
        self.draw_button(self.result_next_rect, "下一关", True, CYAN)
        self.draw_button(self.result_select_rect, "返回关卡选择", True, VIOLET)
        self.draw_button(self.result_book_rect, "查看相关图鉴", True, VIOLET)
        pygame.display.flip()

    def draw_final(self):
        self.draw_background()
        box = pygame.Rect(210, 95, 860, 530)
        draw_soft_glow(self.screen, box, VIOLET, strength=40, radius=18)
        rounded_rect(self.screen, box, (8, 13, 32), 18, VIOLET, 2)
        draw_text(self.screen, "通关总结：代谢之道", self.font_title, CYAN, (260, 145))
        summary = "代谢不是追求单一最大化。ATP 并非越高越好，呼吸链越强也可能带来 ROS；葡萄糖不只是燃料，也可以储存或转入 PPP；氨基酸可以供能，但氨基必须安全排出；脂肪是高效能源，却需要在合适情境下动员。"
        draw_wrapped(self.screen, summary, self.font_md, TEXT, pygame.Rect(260, 215, 760, 120), 8)
        items = ["抓住关键", "动态平衡", "响应需求", "藏器于势", "逆势而行", "分合自然"]
        for i, item in enumerate(items):
            x = 285 + (i % 3) * 235
            y = 370 + (i // 3) * 72
            r = pygame.Rect(x, y, 180, 46)
            rounded_rect(self.screen, r, (24, 38, 80), 10, CYAN if i % 2 == 0 else VIOLET, 1)
            draw_text(self.screen, item, self.font_md, TEXT, (x + 48, y + 11))
        self.final_title_rect = pygame.Rect(370, 545, 140, 42)
        self.final_book_rect = pygame.Rect(565, 545, 140, 42)
        self.final_restart_rect = pygame.Rect(760, 545, 140, 42)
        self.draw_button(self.final_title_rect, "返回标题", True, VIOLET)
        self.draw_button(self.final_book_rect, "查看图鉴", True, VIOLET)
        self.draw_button(self.final_restart_rect, "重新开始", True, CYAN)
        pygame.display.flip()

    def draw(self):
        if self.screen_state == SCREEN_TITLE:
            self.draw_title()
            return
        if self.screen_state == SCREEN_MAIN_MENU:
            self.draw_main_menu()
            return
        if self.screen_state == SCREEN_TUTORIAL:
            self.draw_tutorial()
            return
        if self.screen_state == SCREEN_SCENARIO_SELECT:
            self.draw_scenario_select()
            return
        if self.screen_state == SCREEN_ENCYCLOPEDIA:
            self.draw_encyclopedia()
            return
        if self.screen_state == SCREEN_RESULT:
            self.draw_result()
            return
        if self.screen_state == SCREEN_FINAL_SUMMARY:
            self.draw_final()
            return
        self.draw_game()
        pygame.display.flip()

    def draw_game(self):
        self.draw_background()
        self.draw_top()
        self.draw_status()
        self.draw_map()
        self.draw_cards()
        self.draw_log()

    def handle_title_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            for rect, target in getattr(self, "title_buttons", []):
                if rect.collidepoint(event.pos):
                    if target == "QUIT":
                        pygame.quit()
                        sys.exit()
                    if target == SCREEN_ENCYCLOPEDIA:
                        self.encyclopedia_return = SCREEN_TITLE
                    self.screen_state = target

    def handle_main_menu_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            for rect, target, enabled in getattr(self, "menu_buttons", []):
                if enabled and rect.collidepoint(event.pos):
                    if target == SCREEN_ENCYCLOPEDIA:
                        self.encyclopedia_return = SCREEN_MAIN_MENU
                    self.screen_state = target

    def handle_tutorial_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.tutorial_prev.collidepoint(event.pos) and self.tutorial_page > 0:
                self.tutorial_page -= 1
            elif self.tutorial_next.collidepoint(event.pos) and self.tutorial_page < 2:
                self.tutorial_page += 1
            elif self.tutorial_back.collidepoint(event.pos):
                self.screen_state = SCREEN_MAIN_MENU
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_LEFT:
                self.tutorial_page = max(0, self.tutorial_page - 1)
            elif event.key == pygame.K_RIGHT:
                self.tutorial_page = min(2, self.tutorial_page + 1)
            elif event.key == pygame.K_ESCAPE:
                self.screen_state = SCREEN_MAIN_MENU

    def handle_scenario_select_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.scenario_back.collidepoint(event.pos):
                self.screen_state = SCREEN_MAIN_MENU
                return
            for i, rect in enumerate(getattr(self, "scenario_rects", [])):
                if rect.collidepoint(event.pos):
                    self.start_level(i)
                    return

    def handle_encyclopedia_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.encyclopedia_back.collidepoint(event.pos):
                self.screen_state = self.encyclopedia_return
        if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
            self.screen_state = self.encyclopedia_return

    def handle_result_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.retry_rect.collidepoint(event.pos):
                self.start_level(self.level_index)
            elif self.result_next_rect.collidepoint(event.pos):
                self.completed_levels.add(self.level_index)
                if self.level_index < len(LEVELS) - 1:
                    self.start_level(self.level_index + 1)
                else:
                    self.screen_state = SCREEN_FINAL_SUMMARY
            elif self.result_select_rect.collidepoint(event.pos):
                self.completed_levels.add(self.level_index)
                self.screen_state = SCREEN_SCENARIO_SELECT
            elif self.result_book_rect.collidepoint(event.pos):
                self.completed_levels.add(self.level_index)
                self.encyclopedia_return = SCREEN_RESULT
                self.screen_state = SCREEN_ENCYCLOPEDIA

    def handle_final_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.final_title_rect.collidepoint(event.pos):
                self.screen_state = SCREEN_TITLE
            elif self.final_book_rect.collidepoint(event.pos):
                self.encyclopedia_return = SCREEN_FINAL_SUMMARY
                self.screen_state = SCREEN_ENCYCLOPEDIA
            elif self.final_restart_rect.collidepoint(event.pos):
                self.completed_levels.clear()
                self.start_level(0)

    def handle_game_click(self, pos):
        if self.input_locked:
            return
        if self.execute_rect.collidepoint(pos):
            self.execute_turn()
            return
        if self.next_rect.collidepoint(pos):
            if self.level_index < len(LEVELS) - 1:
                self.level_index += 1
                self.reset_level()
            else:
                self.screen_state = SCREEN_FINAL_SUMMARY
            return
        for rect, mode in getattr(self, "hormone_rects", []):
            if rect.collidepoint(pos):
                self.set_hormone_mode(mode)
                return
        for i, rect in enumerate(self.card_rects()):
            if rect.collidepoint(pos) and 150 <= pos[1] <= 492:
                if i in self.selected:
                    self.selected.remove(i)
                elif len(self.selected) < 2:
                    self.selected.append(i)
                return

    def handle_game_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            self.handle_game_click(event.pos)
        if event.type == pygame.MOUSEWHEEL:
            self.handle_wheel(event.y)
        if event.type == pygame.KEYDOWN and event.key == pygame.K_RETURN:
            self.execute_turn()

    def handle_event(self, event):
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()
        if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
            if self.screen_state == SCREEN_GAME:
                self.screen_state = SCREEN_SCENARIO_SELECT
                return
            if self.screen_state in (SCREEN_MAIN_MENU, SCREEN_TUTORIAL, SCREEN_SCENARIO_SELECT, SCREEN_ENCYCLOPEDIA):
                self.screen_state = SCREEN_TITLE
                return
        handlers = {
            SCREEN_TITLE: self.handle_title_event,
            SCREEN_MAIN_MENU: self.handle_main_menu_event,
            SCREEN_TUTORIAL: self.handle_tutorial_event,
            SCREEN_SCENARIO_SELECT: self.handle_scenario_select_event,
            SCREEN_GAME: self.handle_game_event,
            SCREEN_RESULT: self.handle_result_event,
            SCREEN_ENCYCLOPEDIA: self.handle_encyclopedia_event,
            SCREEN_FINAL_SUMMARY: self.handle_final_event,
        }
        handlers.get(self.screen_state, self.handle_game_event)(event)

    def handle_wheel(self, y):
        mx, my = pygame.mouse.get_pos()
        if 864 <= mx <= 1262 and 112 <= my <= 542:
            max_scroll = 6 * 98 - 335 + 8
            self.card_scroll = max(0, min(max_scroll, self.card_scroll - y * 35))

    def run(self):
        while True:
            dt = self.clock.tick(FPS) / 1000.0
            for event in pygame.event.get():
                self.handle_event(event)
            self.update(dt)
            self.draw()


if __name__ == "__main__":
    Game().run()
