import math
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
    names = ["microsoftyahei", "simhei", "simsun", "arialunicode", "arial"]
    for name in names:
        font_path = pygame.font.match_font(name, bold=bold)
        if font_path:
            return pygame.font.Font(font_path, size)
    return pygame.font.SysFont("arial", size, bold=bold)


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
        pygame.display.set_caption("???? Cell City")
        self.screen = pygame.display.set_mode((WIDTH, HEIGHT))
        self.clock = pygame.time.Clock()
        self.font_xs = load_font(14)
        self.font_sm = load_font(16)
        self.font_md = load_font(20)
        self.font_lg = load_font(28, bold=True)
        self.font_title = load_font(38, bold=True)
        self.level_index = 0
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
        self.active_nodes = []
        self.active_edges = []
        self.path_timer = 0.0
        self.pending_result = False
        self.input_locked = False
        self.input_lock_timer = 0.0
        self.log_items = []
        self.add_log(f"???{LEVELS[self.level_index]['name']}???? 2 ????????????")
        self.mode = "playing"

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
        for key in STATE_KEYS:
            s[key] = clamp(s[key])

    def execute_turn(self):
        if self.mode != "playing" or self.input_locked or len(self.selected) != 2:
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
            explanations.append(f"{card['name']}?{card['explain']}")
            active.update(card["nodes"])
            for a, b in zip(card["nodes"], card["nodes"][1:]):
                if a in MAP_NODES and b in MAP_NODES:
                    edges.append((a, b))
        self.apply_homeostatic_pressure()
        self.turn += 1
        self.active_nodes = list(active)
        self.active_edges = edges
        self.path_timer = self.path_duration
        self.input_locked = True
        self.input_lock_timer = self.INPUT_LOCK_SECONDS
        self.add_log(f"? {self.turn} ???" + "  ".join(explanations))
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
        maxim = "????????????????????"
        if self.state["ROS"] > 65:
            maxim = "???????????????????????"
        if self.state["NH3"] > 60:
            maxim = "????????????????????"
        if self.state["Glucose"] < 30:
            maxim = "??????????????????????"
        if self.state["ATP"] < 40:
            maxim = "??????????????????"
        if passed and score >= 80:
            maxim = "???????????????????????"
        return score, passed, maxim

    def update(self, dt):
        self.time += dt
        mouse = pygame.mouse.get_pos()
        for key in STATE_KEYS:
            self.display_state[key] = approach(self.display_state[key], self.state[key], self.STATUS_SMOOTH_SPEED, dt)
        for i, rect in enumerate(self.card_rects()):
            hovered = rect.collidepoint(mouse) and 150 <= mouse[1] <= 492 and self.mode == "playing" and not self.input_locked
            self.card_anim[i]["hover"] = approach(self.card_anim[i]["hover"], 1.0 if hovered else 0.0, self.CARD_ANIM_SPEED, dt)
            self.card_anim[i]["select"] = approach(self.card_anim[i]["select"], 1.0 if i in self.selected else 0.0, self.CARD_ANIM_SPEED, dt)
            self.card_anim[i]["flash"] = max(0.0, self.card_anim[i]["flash"] - dt * 2.5)
        for item in self.log_items:
            item["age"] += dt
            item["y"] = approach(item["y"], 0.0, 12.0, dt)
            item["alpha"] = approach(item["alpha"], 255.0, self.LOG_FADE_SPEED, dt)
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
                    self.mode = "result"

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

    def draw_top(self):
        rect = pygame.Rect(18, 14, 1244, 82)
        self.draw_panel(rect, CYAN)
        draw_text(self.screen, "???? Cell City", self.font_title, TEXT, (38, 24))
        draw_text(self.screen, "A Strategy Game of Metabolic Homeostasis", self.font_sm, MUTED, (42, 66))
        draw_text(self.screen, f"?? {self.level_index + 1}/5?{self.level['name']}", self.font_md, CYAN, (545, 26))
        draw_text(self.screen, f"?? {self.turn}/10", self.font_md, VIOLET, (545, 58))
        goal_texts = []
        for key, op, value in self.level["goals"]:
            mark = "?" if self.goal_met((key, op, value)) else "?"
            goal_texts.append(f"{mark} {key} {op} {value}")
        draw_wrapped(self.screen, "???" + "?".join(goal_texts), self.font_sm, TEXT, pygame.Rect(760, 25, 470, 50), 3)

    def draw_status(self):
        rect = pygame.Rect(18, 112, 250, 430)
        self.draw_panel(rect, CYAN)
        draw_text(self.screen, "???", self.font_md, CYAN, (36, 128))
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
        draw_text(self.screen, "????", self.font_md, CYAN, (306, 128))
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
        draw_text(self.screen, f"????  ?? {len(self.selected)}/2", self.font_md, VIOLET, (882, 128))
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

    def draw_log(self):
        rect = pygame.Rect(18, 558, 1244, 144)
        self.draw_panel(rect, CYAN)
        draw_text(self.screen, "???? / ?????", self.font_md, CYAN, (36, 574))
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
        self.execute_rect = pygame.Rect(960, 610, 132, 42)
        self.next_rect = pygame.Rect(1110, 610, 112, 42)
        can_execute = len(self.selected) == 2 and self.mode == "playing" and not self.input_locked
        self.draw_button(self.execute_rect, "?????", can_execute, CYAN)
        self.draw_button(self.next_rect, "???", not self.input_locked, VIOLET)
        if self.level.get("modifier"):
            draw_wrapped(self.screen, self.level["modifier"]["note"], self.font_xs, AMBER, pygame.Rect(960, 666, 260, 22), 1)

    def draw_result(self):
        overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        overlay.fill((2, 6, 23, 210))
        self.screen.blit(overlay, (0, 0))
        box = pygame.Rect(250, 130, 780, 460)
        draw_soft_glow(self.screen, box, CYAN, strength=35, radius=16)
        rounded_rect(self.screen, box, (8, 13, 32), 16, CYAN, 2)
        score, passed, maxim = self.evaluate()
        title = "????" if passed else "????"
        draw_text(self.screen, title, self.font_title, GREEN if passed else AMBER, (290, 165))
        draw_text(self.screen, f"???{score}", self.font_lg, VIOLET, (780, 170))
        y = 230
        for key, op, value in self.level["goals"]:
            ok = self.goal_met((key, op, value))
            text = f"{'??' if ok else '???'}?{key} {op} {value}??? {self.state[key]}"
            draw_text(self.screen, text, self.font_md, GREEN if ok else RED, (300, y))
            y += 35
        draw_wrapped(self.screen, "?????" + maxim, self.font_md, CYAN, pygame.Rect(300, 380, 680, 70), 6)
        self.retry_rect = pygame.Rect(565, 510, 130, 44)
        self.result_next_rect = pygame.Rect(720, 510, 150, 44)
        self.draw_button(self.retry_rect, "????", True, VIOLET)
        self.draw_button(self.result_next_rect, "?????", True, CYAN)

    def draw_final(self):
        overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        overlay.fill((2, 6, 23, 230))
        self.screen.blit(overlay, (0, 0))
        box = pygame.Rect(210, 95, 860, 530)
        draw_soft_glow(self.screen, box, VIOLET, strength=40, radius=18)
        rounded_rect(self.screen, box, (8, 13, 32), 18, VIOLET, 2)
        draw_text(self.screen, "????", self.font_title, CYAN, (260, 145))
        summary = "?????????????????????????????????????????"
        draw_wrapped(self.screen, summary, self.font_lg, TEXT, pygame.Rect(260, 215, 760, 100), 8)
        items = ["????", "????", "????", "????", "????", "????"]
        for i, item in enumerate(items):
            x = 285 + (i % 3) * 235
            y = 355 + (i // 3) * 72
            r = pygame.Rect(x, y, 180, 46)
            rounded_rect(self.screen, r, (24, 38, 80), 10, CYAN if i % 2 == 0 else VIOLET, 1)
            draw_text(self.screen, item, self.font_md, TEXT, (x + 48, y + 11))
        self.final_restart_rect = pygame.Rect(550, 540, 180, 44)
        self.draw_button(self.final_restart_rect, "????", True, CYAN)

    def draw(self):
        self.draw_background()
        self.draw_top()
        self.draw_status()
        self.draw_map()
        self.draw_cards()
        self.draw_log()
        if self.mode == "result":
            self.draw_result()
        elif self.mode == "final":
            self.draw_final()
        pygame.display.flip()

    def handle_click(self, pos):
        if self.mode == "result":
            if self.retry_rect.collidepoint(pos):
                self.reset_level()
            elif self.result_next_rect.collidepoint(pos):
                if self.level_index < len(LEVELS) - 1:
                    self.level_index += 1
                    self.reset_level()
                else:
                    self.mode = "final"
            return
        if self.mode == "final":
            if self.final_restart_rect.collidepoint(pos):
                self.level_index = 0
                self.reset_level()
            return
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
                self.mode = "final"
            return
        for i, rect in enumerate(self.card_rects()):
            if rect.collidepoint(pos) and 150 <= pos[1] <= 492:
                if i in self.selected:
                    self.selected.remove(i)
                elif len(self.selected) < 2:
                    self.selected.append(i)
                return

    def handle_wheel(self, y):
        mx, my = pygame.mouse.get_pos()
        if 864 <= mx <= 1262 and 112 <= my <= 542:
            max_scroll = 6 * 98 - 335 + 8
            self.card_scroll = max(0, min(max_scroll, self.card_scroll - y * 35))

    def run(self):
        while True:
            dt = self.clock.tick(FPS) / 1000.0
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                    self.handle_click(event.pos)
                if event.type == pygame.MOUSEWHEEL:
                    self.handle_wheel(event.y)
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        pygame.quit()
                        sys.exit()
                    if event.key == pygame.K_RETURN:
                        self.execute_turn()
            self.update(dt)
            self.draw()


if __name__ == "__main__":
    Game().run()
