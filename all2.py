import pygame
import math
import random
import sys

pygame.init()

info = pygame.display.Info()
SCREEN_WIDTH = info.current_w
SCREEN_HEIGHT = info.current_h
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.FULLSCREEN)
pygame.display.set_caption("The Eternity Covenant")
clock = pygame.time.Clock()

BASE_CELL_SIZE = 75
BASE_SCREEN_HEIGHT = 1500
SCALE = SCREEN_HEIGHT / BASE_SCREEN_HEIGHT
CELL_SIZE = int(BASE_CELL_SIZE * SCALE)

GRID_WIDTH, GRID_HEIGHT = 20, 20
FIELD_WIDTH = GRID_WIDTH * CELL_SIZE
FIELD_HEIGHT = GRID_HEIGHT * CELL_SIZE

PANEL_HEIGHT_RATIO = 0.09
PANEL_HEIGHT = max(80, int(SCREEN_HEIGHT * PANEL_HEIGHT_RATIO))

GAME_AREA_TOP = 0
GAME_AREA_HEIGHT = SCREEN_HEIGHT - PANEL_HEIGHT
FIELD_OFFSET_X = (SCREEN_WIDTH - FIELD_WIDTH) // 2
FIELD_OFFSET_Y = (GAME_AREA_HEIGHT - FIELD_HEIGHT) // 2

TOWER_COST = {
    "archer": 100, "mage": 120, "cannon": 150, "ice": 80,
    "fire": 110, "poison": 130, "lightning": 160
}
TOWER_UPGRADE_COST = {
    "archer": 150, "mage": 180, "cannon": 200, "ice": 100,
    "fire": 160, "poison": 190, "lightning": 220
}
HELLIFY_COST = 30

STARTING_MONEY = 400
STARTING_FAITH = 50
STARTING_MADNESS = 50
MAX_FAITH = 100
MAX_MADNESS = 100

# Цвета
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
GREEN = (34, 139, 34)
BROWN = (139, 69, 19)
GRAY = (128, 128, 128)
RED = (255, 0, 0)
BLUE = (0, 0, 255)
YELLOW = (255, 255, 0)
PURPLE = (128, 0, 128)
ORANGE = (255, 165, 0)
CYAN = (0, 255, 255)
GOLD = (255, 215, 0)
DARK_RED = (139, 0, 0)
LIGHT_GRAY = (200, 200, 200)
PANEL_BG = (50, 50, 50)

MELEE = "mile"
RANGE = "range"

# Шрифты с масштабированием
font_size_small = max(12, int(18 * SCALE))
font_size_medium = max(14, int(24 * SCALE))
font_size_large = max(20, int(36 * SCALE))
font_small = pygame.font.Font(None, font_size_small)
font_medium = pygame.font.Font(None, font_size_medium)
font_large = pygame.font.Font(None, font_size_large)

waypoints = [
    (0, 2), (4, 2), (4, 6), (8, 6), (8, 2), (12, 2), (12, 6),
    (8, 6), (8, 10), (4, 10), (4, 14), (8, 14), (8, 18), (12, 18),
    (16, 18), (16, 14), (14, 10), (18, 10), (18, 6), (16, 2), (20, 2)
]

def get_path_pixels():
    return [(FIELD_OFFSET_X + x * CELL_SIZE + CELL_SIZE // 2,
             FIELD_OFFSET_Y + y * CELL_SIZE + CELL_SIZE // 2) for (x, y) in waypoints]

path_pixels = get_path_pixels()

def cell_from_pos(pos):
    x, y = pos
    grid_x = (x - FIELD_OFFSET_X) // CELL_SIZE
    grid_y = (y - FIELD_OFFSET_Y) // CELL_SIZE
    return grid_x, grid_y

def is_path_cell(cell):
    for i in range(len(waypoints) - 1):
        x1, y1 = waypoints[i]
        x2, y2 = waypoints[i + 1]
        if x1 == x2:
            for y in range(min(y1, y2), max(y1, y2) + 1):
                if cell == (x1, y):
                    return True
        elif y1 == y2:
            for x in range(min(x1, x2), max(x1, x2) + 1):
                if cell == (x, y1):
                    return True
    return False

def scaled(val):
    return int(val * SCALE)

class Enemy:
    def __init__(self, enemy_type):
        self.enemy_type = enemy_type
        base_range = scaled(40)
        stats = {
            "orc": {"hp": 100, "phys": 0, "mag": 0, "speed": scaled(1.5), "rise": False, "evade": 0.1,
                    "attack": MELEE, "color": GREEN, "atk_dmg": 10, "atk_range": base_range, "atk_cd": 60},
            "skeleton": {"hp": 50, "phys": 0.1, "mag": 0, "speed": scaled(1.15), "rise": True, "evade": 0,
                         "attack": MELEE, "color": WHITE, "atk_dmg": 8, "atk_range": base_range, "atk_cd": 50},
            "necromancer": {"hp": 400, "phys": 0, "mag": 0.8, "speed": scaled(0.95), "rise": False, "evade": 0,
                            "attack": RANGE, "color": PURPLE, "atk_dmg": 25, "atk_range": scaled(120), "atk_cd": 70},
            "ogr": {"hp": 800, "phys": 0.5, "mag": 0, "speed": scaled(0.7), "rise": False, "evade": 0,
                    "attack": MELEE, "color": ORANGE, "atk_dmg": 40, "atk_range": scaled(45), "atk_cd": 80},
            "dark_knight": {"hp": 350, "phys": 0.9, "mag": 0, "speed": scaled(1.05), "rise": False, "evade": 0,
                            "attack": MELEE, "color": DARK_RED, "atk_dmg": 30, "atk_range": base_range, "atk_cd": 55},
            "wurg": {"hp": 150, "phys": 0.1, "mag": 0.4, "speed": scaled(2.1), "rise": False, "evade": 0.3,
                     "attack": MELEE, "color": YELLOW, "atk_dmg": 15, "atk_range": base_range, "atk_cd": 45},
            "chaos_spawn": {"hp": 220, "phys": 0, "mag": 0.2, "speed": scaled(1.7), "rise": False, "evade": 0.7,
                            "attack": MELEE, "color": RED, "atk_dmg": 20, "atk_range": base_range, "atk_cd": 40},
            "hellbrute": {"hp": 1000, "phys": 0.9, "mag": 0.3, "speed": scaled(0.4), "rise": False, "evade": 0,
                          "attack": MELEE, "color": (200, 0, 200), "atk_dmg": 50, "atk_range": scaled(50), "atk_cd": 100}
        }
        s = stats[enemy_type]
        self.max_hp = s["hp"]
        self.hp = self.max_hp
        self.phys_armor = s["phys"]
        self.mag_armor = s["mag"]
        self.speed = s["speed"]
        self.base_speed = s["speed"]
        self.can_rise = s["rise"]
        self.evade = s["evade"]
        self.attack_type = s["attack"]
        self.color = s["color"]
        self.attack_damage = s["atk_dmg"]
        self.attack_range = s["atk_range"]
        self.attack_cooldown_max = s["atk_cd"]
        self.attack_cooldown = 0

        self.path_index = 0
        self.pos = list(path_pixels[0])
        self.alive = True
        self.risen = False
        self.attacking_tower = None

        self.burn_timer = 0
        self.poison_timer = 0
        self.slow_timer = 0

        rewards = {"orc": 10, "skeleton": 5, "necromancer": 50, "ogr": 40, "dark_knight": 30, "wurg": 20, "chaos_spawn": 25, "hellbrute": 60}
        self.reward = rewards[enemy_type]
        self.souls_value = 1

    def move(self, towers):
        if not self.alive:
            return
        if self.attack_cooldown > 0:
            self.attack_cooldown -= 1

        if self.attacking_tower:
            if not self.attacking_tower.hp > 0:
                self.attacking_tower = None
            else:
                dist = math.hypot(self.pos[0] - self.attacking_tower.x, self.pos[1] - self.attacking_tower.y)
                if dist <= self.attack_range:
                    if self.attack_cooldown <= 0:
                        self.attack_tower(self.attacking_tower)
                    return
                else:
                    self.attacking_tower = None

        target_tower = None
        for tower in towers:
            if tower.hp <= 0:
                continue
            dist = math.hypot(self.pos[0] - tower.x, self.pos[1] - tower.y)
            if dist <= self.attack_range:
                if target_tower is None or dist < math.hypot(self.pos[0] - target_tower.x, self.pos[1] - target_tower.y):
                    target_tower = tower
        if target_tower:
            self.attacking_tower = target_tower
            return

        if self.path_index >= len(path_pixels) - 1:
            self.alive = False
            return
        target = path_pixels[self.path_index + 1]
        dx = target[0] - self.pos[0]
        dy = target[1] - self.pos[1]
        dist = math.hypot(dx, dy)
        if dist < self.speed * 1.5:
            self.pos = list(target)
            self.path_index += 1
        else:
            self.pos[0] += (dx / dist) * self.speed
            self.pos[1] += (dy / dist) * self.speed

    def attack_tower(self, tower):
        tower.take_damage(self.attack_damage)
        self.attack_cooldown = self.attack_cooldown_max

    def take_damage(self, damage, damage_type):
        if damage_type == "physical":
            effective = damage * (1 - self.phys_armor)
        else:
            effective = damage * (1 - self.mag_armor)
        if random.random() < self.evade:
            effective = 0
        self.hp -= effective
        if self.hp <= 0:
            self.alive = False

    def apply_effects(self):
        if self.burn_timer > 0:
            self.hp -= 2
            if self.hp <= 0:
                self.alive = False
            self.burn_timer -= 1
        if self.poison_timer > 0:
            self.hp -= 1
            if self.hp <= 0:
                self.alive = False
            self.poison_timer -= 1

    def draw(self, surface):
        if self.enemy_type in ["orc", "ogr", "dark_knight"]:
            pygame.draw.rect(surface, self.color, (int(self.pos[0] - scaled(15)), int(self.pos[1] - scaled(15)), scaled(30), scaled(30)))
        elif self.enemy_type == "skeleton":
            pygame.draw.circle(surface, self.color, (int(self.pos[0]), int(self.pos[1])), scaled(15))
        elif self.enemy_type == "necromancer":
            pygame.draw.polygon(surface, self.color, [
                (int(self.pos[0]), int(self.pos[1] - scaled(15))),
                (int(self.pos[0] - scaled(12)), int(self.pos[1] + scaled(10))),
                (int(self.pos[0] + scaled(12)), int(self.pos[1] + scaled(10)))
            ])
        elif self.enemy_type == "wurg":
            pygame.draw.ellipse(surface, self.color, (int(self.pos[0] - scaled(12)), int(self.pos[1] - scaled(18)), scaled(24), scaled(36)))
        elif self.enemy_type == "chaos_spawn":
            pygame.draw.rect(surface, self.color, (int(self.pos[0] - scaled(10)), int(self.pos[1] - scaled(20)), scaled(20), scaled(40)))
        elif self.enemy_type == "hellbrute":
            pygame.draw.circle(surface, self.color, (int(self.pos[0]), int(self.pos[1])), scaled(20))
        bar_width = scaled(30)
        pygame.draw.rect(surface, RED, (int(self.pos[0] - bar_width/2), int(self.pos[1] - scaled(25)), bar_width, scaled(5)))
        green_width = bar_width * (self.hp / self.max_hp)
        pygame.draw.rect(surface, GREEN, (int(self.pos[0] - bar_width/2), int(self.pos[1] - scaled(25)), green_width, scaled(5)))

class SatanBoss(Enemy):
    def __init__(self):
        super().__init__("hellbrute")
        self.enemy_type = "satan"
        self.max_hp = 5000
        self.hp = self.max_hp
        self.speed = scaled(40)
        self.base_speed = self.speed
        self.phys_armor = 0.5
        self.mag_armor = 0.5
        self.evade = 0
        self.attack_range = scaled(60)
        self.attack_damage = 80
        self.attack_cooldown_max = 60
        self.attack_cooldown = 0
        self.color = (255, 0, 0)
        self.reward = 500
        self.souls_value = 100
        self.phase = 1
        self.phase2_threshold = 0.6 * self.max_hp
        self.phase3_threshold = 0.3 * self.max_hp

    def move(self, towers):
        if not self.alive:
            return
        if self.path_index >= len(path_pixels) - 1:
            self.alive = False
            return
        target = path_pixels[self.path_index + 1]
        dx = target[0] - self.pos[0]
        dy = target[1] - self.pos[1]
        dist = math.hypot(dx, dy)
        if dist < self.speed * 1.5:
            self.pos = list(target)
            self.path_index += 1
        else:
            self.pos[0] += (dx / dist) * self.speed
            self.pos[1] += (dy / dist) * self.speed

    def take_damage(self, damage, damage_type):
        effective = damage * (1 - self.phys_armor) if damage_type == "physical" else damage * (1 - self.mag_armor)
        self.hp -= effective
        if self.hp <= 0:
            self.alive = False
        if self.phase == 1 and self.hp <= self.phase2_threshold:
            self.phase = 2
            self.speed = scaled(70)
        elif self.phase == 2 and self.hp <= self.phase3_threshold:
            self.phase = 3

    def draw(self, surface):
        rad = scaled(30)
        pygame.draw.circle(surface, self.color, (int(self.pos[0]), int(self.pos[1])), rad)
        pygame.draw.circle(surface, BLACK, (int(self.pos[0]), int(self.pos[1])), rad, scaled(3))
        horn_len = scaled(20)
        pygame.draw.polygon(surface, BLACK, [
            (int(self.pos[0] - scaled(10)), int(self.pos[1] - scaled(25))),
            (int(self.pos[0] + scaled(10)), int(self.pos[1] - scaled(25))),
            (int(self.pos[0]), int(self.pos[1] - rad - horn_len))
        ])
        bar_width = scaled(60)
        bar_y = int(self.pos[1] - rad - scaled(25))
        pygame.draw.rect(surface, RED, (int(self.pos[0] - bar_width/2), bar_y, bar_width, scaled(8)))
        green_width = bar_width * (self.hp / self.max_hp)
        pygame.draw.rect(surface, GREEN, (int(self.pos[0] - bar_width/2), bar_y, green_width, scaled(8)))

class Tower:
    def __init__(self, tower_type, cell):
        self.tower_type = tower_type
        self.cell = cell
        self.x = FIELD_OFFSET_X + cell[0] * CELL_SIZE + CELL_SIZE//2
        self.y = FIELD_OFFSET_Y + cell[1] * CELL_SIZE + CELL_SIZE//2
        self.level = 1
        base_range = scaled(150)
        stats = {
            "archer": {"damage": 15, "range": base_range, "cooldown": 30, "color": BLUE, "proj_color": CYAN, "hp": 150, "dmg_type": "physical"},
            "mage": {"damage": 20, "range": scaled(120), "cooldown": 40, "color": PURPLE, "proj_color": (255, 0, 255), "hp": 120, "dmg_type": "magical"},
            "cannon": {"damage": 25, "range": scaled(130), "cooldown": 50, "color": ORANGE, "proj_color": (255, 100, 0), "hp": 200, "dmg_type": "physical"},
            "ice": {"damage": 5, "range": scaled(100), "cooldown": 20, "color": CYAN, "proj_color": (200, 230, 255), "hp": 100, "dmg_type": "magical"},
            "fire": {"damage": 18, "range": scaled(110), "cooldown": 35, "color": (220, 50, 0), "proj_color": (255, 100, 0), "hp": 130, "dmg_type": "magical"},
            "poison": {"damage": 12, "range": scaled(130), "cooldown": 25, "color": (0, 150, 0), "proj_color": (100, 255, 100), "hp": 110, "dmg_type": "magical"},
            "lightning": {"damage": 30, "range": scaled(140), "cooldown": 55, "color": GOLD, "proj_color": (255, 255, 0), "hp": 100, "dmg_type": "magical"},
            "chimera_archer":   {"damage": 40, "range": scaled(180), "cooldown": 20, "color": GOLD, "proj_color": GOLD, "hp": 350, "dmg_type": "physical"},
            "chimera_mage":     {"damage": 55, "range": scaled(140), "cooldown": 25, "color": GOLD, "proj_color": GOLD, "hp": 280, "dmg_type": "magical"},
            "chimera_cannon":   {"damage": 65, "range": scaled(150), "cooldown": 35, "color": GOLD, "proj_color": GOLD, "hp": 450, "dmg_type": "physical"},
            "chimera_ice":      {"damage": 15, "range": scaled(120), "cooldown": 12, "color": GOLD, "proj_color": GOLD, "hp": 250, "dmg_type": "magical"},
            "chimera_fire":     {"damage": 50, "range": scaled(130), "cooldown": 22, "color": GOLD, "proj_color": GOLD, "hp": 300, "dmg_type": "magical"},
            "chimera_poison":   {"damage": 35, "range": scaled(160), "cooldown": 15, "color": GOLD, "proj_color": GOLD, "hp": 270, "dmg_type": "magical"},
            "chimera_lightning":{"damage": 80, "range": scaled(170), "cooldown": 40, "color": GOLD, "proj_color": GOLD, "hp": 260, "dmg_type": "magical"},
            "hell_archer":   {"damage": 25, "range": scaled(160), "cooldown": 25, "color": DARK_RED, "proj_color": (255, 80, 80), "hp": 200, "dmg_type": "physical"},
            "hell_mage":     {"damage": 30, "range": scaled(130), "cooldown": 35, "color": DARK_RED, "proj_color": (200, 0, 200), "hp": 160, "dmg_type": "magical"},
            "hell_cannon":   {"damage": 35, "range": scaled(140), "cooldown": 45, "color": DARK_RED, "proj_color": (255, 160, 0), "hp": 250, "dmg_type": "physical"},
            "hell_ice":      {"damage": 10, "range": scaled(110), "cooldown": 15, "color": DARK_RED, "proj_color": (180, 210, 255), "hp": 130, "dmg_type": "magical"},
            "hell_fire":     {"damage": 28, "range": scaled(120), "cooldown": 30, "color": DARK_RED, "proj_color": (255, 140, 0), "hp": 170, "dmg_type": "magical"},
            "hell_poison":   {"damage": 22, "range": scaled(140), "cooldown": 20, "color": DARK_RED, "proj_color": (120, 255, 120), "hp": 140, "dmg_type": "magical"},
            "hell_lightning":{"damage": 45, "range": scaled(150), "cooldown": 50, "color": DARK_RED, "proj_color": (255, 255, 100), "hp": 130, "dmg_type": "magical"}
        }
        s = stats[tower_type]
        self.damage = s["damage"]
        self.range = s["range"]
        self.cooldown_max = s["cooldown"]
        self.cooldown = 0
        self.color = s["color"]
        self.proj_color = s["proj_color"]
        self.max_hp = s["hp"]
        self.hp = self.max_hp
        self.projectiles = []
        self.damage_type = s["dmg_type"]

    def upgrade(self):
        if self.level < 3 and not self.tower_type.startswith(("chimera", "hell")):
            self.level += 1
            self.damage = int(self.damage * 1.5)
            self.range = int(self.range * 1.1)
            self.cooldown_max = max(5, self.cooldown_max - 5)
            self.max_hp = int(self.max_hp * 1.3)
            self.hp = self.max_hp
            return True
        return False

    def take_damage(self, damage):
        self.hp -= damage
        if self.hp <= 0:
            self.hp = 0

    def find_target(self, enemies):
        in_range = [e for e in enemies if e.alive and math.hypot(e.pos[0] - self.x, e.pos[1] - self.y) <= self.range]
        if not in_range:
            return None
        return max(in_range, key=lambda e: e.path_index)

    def update(self, enemies):
        if self.hp <= 0:
            return
        if self.cooldown > 0:
            self.cooldown -= 1
        if self.cooldown == 0:
            target = self.find_target(enemies)
            if target:
                self.projectiles.append([target, list((self.x, self.y))])
                self.cooldown = self.cooldown_max

        for proj in self.projectiles[:]:
            target, pos = proj
            if not target.alive:
                self.projectiles.remove(proj)
                continue
            dx = target.pos[0] - pos[0]
            dy = target.pos[1] - pos[1]
            dist = math.hypot(dx, dy)
            speed = scaled(8)
            if dist < speed:
                target.take_damage(self.damage, self.damage_type)
                if self.tower_type in ("ice", "chimera_ice", "hell_ice"):
                    target.slow_timer = 60
                    target.speed = target.base_speed * 0.5
                elif self.tower_type in ("fire", "chimera_fire", "hell_fire"):
                    target.burn_timer = 40
                elif self.tower_type in ("poison", "chimera_poison", "hell_poison"):
                    target.poison_timer = 80
                elif self.tower_type in ("lightning", "chimera_lightning", "hell_lightning"):
                    chain_targets = []
                    for e in enemies:
                        if e is not target and e.alive:
                            d = math.hypot(e.pos[0] - target.pos[0], e.pos[1] - target.pos[1])
                            if d <= scaled(120):
                                chain_targets.append((d, e))
                    chain_targets.sort(key=lambda x: x[0])
                    for _, e in chain_targets[:2]:
                        e.take_damage(int(self.damage * 0.5), self.damage_type)
                self.projectiles.remove(proj)
            else:
                pos[0] += (dx / dist) * speed
                pos[1] += (dy / dist) * speed

    def draw(self, surface):
        if self.hp <= 0:
            return
        if self.tower_type.startswith('chimera'):
            points = []
            for i in range(8):
                angle = math.radians(45 * i)
                outer_x = self.x + scaled(22) * math.cos(angle)
                outer_y = self.y + scaled(22) * math.sin(angle)
                points.append((outer_x, outer_y))
                inner_x = self.x + scaled(10) * math.cos(angle + math.radians(22.5))
                inner_y = self.y + scaled(10) * math.sin(angle + math.radians(22.5))
                points.append((inner_x, inner_y))
            pygame.draw.polygon(surface, self.color, points)
            pygame.draw.polygon(surface, BLACK, points, scaled(2))
            pygame.draw.circle(surface, (255, 255, 255), (self.x, self.y), scaled(8))
        elif self.tower_type.startswith('hell'):
            points = []
            for i in range(5):
                angle = math.radians(72 * i - 90)
                outer_x = self.x + scaled(20) * math.cos(angle)
                outer_y = self.y + scaled(20) * math.sin(angle)
                points.append((outer_x, outer_y))
                inner_x = self.x + scaled(8) * math.cos(angle + math.radians(36))
                inner_y = self.y + scaled(8) * math.sin(angle + math.radians(36))
                points.append((inner_x, inner_y))
            pygame.draw.polygon(surface, self.color, points)
            pygame.draw.polygon(surface, BLACK, points, scaled(2))
        else:
            if self.tower_type == "archer":
                pygame.draw.circle(surface, self.color, (self.x, self.y), scaled(20))
                pygame.draw.polygon(surface, BLACK, [(self.x, self.y - scaled(20)), (self.x - scaled(10), self.y - scaled(30)), (self.x + scaled(10), self.y - scaled(30))])
            elif self.tower_type == "mage":
                rect_size = scaled(36)
                pygame.draw.rect(surface, self.color, (self.x - rect_size//2, self.y - rect_size//2, rect_size, rect_size))
                pygame.draw.circle(surface, WHITE, (self.x, self.y), scaled(10))
            elif self.tower_type == "cannon":
                rect_size = scaled(44)
                pygame.draw.rect(surface, self.color, (self.x - rect_size//2, self.y - rect_size//2, rect_size, rect_size))
                pygame.draw.rect(surface, BLACK, (self.x - scaled(8), self.y - scaled(30), scaled(16), scaled(10)))
            elif self.tower_type == "ice":
                pygame.draw.polygon(surface, self.color, [
                    (self.x, self.y - scaled(22)),
                    (self.x - scaled(18), self.y + scaled(10)),
                    (self.x + scaled(18), self.y + scaled(10))
                ])
            elif self.tower_type == "fire":
                pygame.draw.polygon(surface, self.color, [
                    (self.x, self.y - scaled(22)),
                    (self.x - scaled(18), self.y + scaled(14)),
                    (self.x + scaled(18), self.y + scaled(14))
                ])
                pygame.draw.polygon(surface, YELLOW, [
                    (self.x, self.y - scaled(15)),
                    (self.x - scaled(10), self.y + scaled(5)),
                    (self.x + scaled(10), self.y + scaled(5))
                ])
            elif self.tower_type == "poison":
                points = []
                for i in range(6):
                    angle = math.radians(60 * i - 30)
                    px = self.x + scaled(20) * math.cos(angle)
                    py = self.y + scaled(20) * math.sin(angle)
                    points.append((px, py))
                pygame.draw.polygon(surface, self.color, points)
            elif self.tower_type == "lightning":
                pts = [(self.x - scaled(10), self.y - scaled(20)), (self.x + scaled(5), self.y - scaled(5)),
                       (self.x - scaled(5), self.y + scaled(5)), (self.x + scaled(10), self.y + scaled(15))]
                pygame.draw.lines(surface, self.color, False, pts, scaled(4))

        for proj in self.projectiles:
            pygame.draw.circle(surface, self.proj_color, (int(proj[1][0]), int(proj[1][1])), scaled(5))

        bar_width = scaled(40)
        bar_y = self.y - scaled(40)
        pygame.draw.rect(surface, RED, (self.x - bar_width//2, bar_y, bar_width, scaled(6)))
        hp_ratio = self.hp / self.max_hp
        pygame.draw.rect(surface, GREEN, (self.x - bar_width//2, bar_y, int(bar_width * hp_ratio), scaled(6)))

class Game:
    def __init__(self):
        self.money = STARTING_MONEY
        self.faith = STARTING_FAITH
        self.madness = STARTING_MADNESS
        self.souls = 0
        self.lives = 20
        self.wave = 1
        self.wave_active = False
        self.wave_timer = 0
        self.enemies = []
        self.towers = []
        self.selected_tower_type = None
        self.hellify_mode = False
        self.victory = False
        self.defeat = False
        self.merge_selection = []  

        self.waves = self.generate_waves()
        self.spawn_queue = []

    def generate_waves(self):
        waves = [
            [("orc", 5), ("skeleton", 3)],
            [("orc", 8), ("wurg", 4)],
            [("skeleton", 10), ("necromancer", 1)],
            [("dark_knight", 3), ("ogr", 2)],
            [("chaos_spawn", 6), ("wurg", 5)],
            [("necromancer", 2), ("hellbrute", 1)],
            [("orc", 10), ("ogr", 3), ("skeleton", 5)],
            [("dark_knight", 5), ("chaos_spawn", 7)],
            [("hellbrute", 2), ("necromancer", 3)],
            [("hellbrute", 3), ("ogr", 4), ("chaos_spawn", 8)],
            [("dark_knight", 7), ("wurg", 8), ("necromancer", 2)],
            [("ogr", 5), ("hellbrute", 3)],
            [("chaos_spawn", 10), ("necromancer", 4)],
            [("hellbrute", 4), ("dark_knight", 6), ("wurg", 10)],
            [("orc", 15), ("skeleton", 15)],
            [("chaos_spawn", 12), ("ogr", 5)],
            [("necromancer", 5), ("hellbrute", 4)],
            [("dark_knight", 10), ("wurg", 12)],
            [("hellbrute", 5), ("ogr", 6), ("chaos_spawn", 8)],
            [("necromancer", 7), ("hellbrute", 5)],
            [("dark_knight", 12), ("chaos_spawn", 10)],
            [("ogr", 8), ("hellbrute", 6)],
            [("wurg", 15), ("necromancer", 6)],
            [("hellbrute", 8), ("dark_knight", 10)],
        ]
        waves.append([])  
        return waves

    def start_wave(self):
        if self.wave <= 25 and not self.wave_active:
            if self.wave == 25:
                self.spawn_queue = ["satan"]
            else:
                self.spawn_queue = []
                for enemy_type, count in self.waves[self.wave - 1]:
                    for _ in range(count):
                        self.spawn_queue.append(enemy_type)
                random.shuffle(self.spawn_queue)
            self.wave_active = True
            self.wave_timer = 0

    def merge_towers(self):
      
        if len(self.merge_selection) == 3:
            types = {t.tower_type for t in self.merge_selection}
            if len(types) == 1:
                base_type = list(types)[0]
                if not base_type.startswith(('chimera', 'hell')):
                    cost = int(0.6 * TOWER_COST[base_type] * 3)
                    if self.money >= cost:
                   
                        cell = self.merge_selection[0].cell
                        for t in self.merge_selection:
                            self.towers.remove(t)
                        chimera_type = 'chimera_' + base_type
                        self.towers.append(Tower(chimera_type, cell))
                        self.money -= cost
                        self.merge_selection.clear()
                        return
       
        if self.selected_tower_type is None or self.selected_tower_type.startswith(('chimera', 'hell')):
            return
        base_type = self.selected_tower_type
        towers_of_type = [t for t in self.towers if t.tower_type == base_type]
        if len(towers_of_type) >= 3:
            cost = int(0.6 * TOWER_COST[base_type] * 3)
            if self.money >= cost:
                for t in towers_of_type[:3]:
                    self.towers.remove(t)
                cell = towers_of_type[0].cell
                chimera_type = 'chimera_' + base_type
                self.towers.append(Tower(chimera_type, cell))
                self.money -= cost
        self.merge_selection.clear()

    def hellify_tower(self, cell):
        for t in self.towers:
            if t.cell == cell and not t.tower_type.startswith(('chimera', 'hell')):
                if self.souls >= HELLIFY_COST:
                    base_type = t.tower_type
                    self.towers.remove(t)
                    self.towers.append(Tower('hell_' + base_type, cell))
                    self.souls -= HELLIFY_COST
                    return True
        return False

    def update(self):
        if self.defeat or self.victory:
            return

        for enemy in self.enemies:
            if enemy.alive:
                enemy.apply_effects()

        for enemy in self.enemies:
            if enemy.slow_timer > 0:
                enemy.slow_timer -= 1
                if enemy.slow_timer == 0:
                    enemy.speed = enemy.base_speed

        if self.wave_active and self.spawn_queue:
            self.wave_timer += 1
            if self.wave_timer >= 40:
                e_type = self.spawn_queue.pop(0)
                if e_type == "satan":
                    self.enemies.append(SatanBoss())
                else:
                    self.enemies.append(Enemy(e_type))
                self.wave_timer = 0

        for enemy in self.enemies[:]:
            if isinstance(enemy, SatanBoss):
                enemy.move(self.towers)
            else:
                enemy.move(self.towers)
            if not enemy.alive:
                if isinstance(enemy, Enemy) and enemy.can_rise and not enemy.risen:
                    enemy.risen = True
                    enemy.hp = enemy.max_hp // 2
                    enemy.alive = True
                    enemy.speed *= 0.8
                else:
                    if enemy.hp <= 0:
                        self.money += enemy.reward
                        self.souls += enemy.souls_value
                        self.madness = min(MAX_MADNESS, self.madness + 1)
                    self.enemies.remove(enemy)
                    continue
            if enemy.path_index >= len(path_pixels) - 1:
                self.lives -= 1
                self.enemies.remove(enemy)
                if self.lives <= 0:
                    self.defeat = True

        self.towers = [t for t in self.towers if t.hp > 0]

        for tower in self.towers:
            tower.update(self.enemies)

        if self.wave_active and not self.spawn_queue and len(self.enemies) == 0:
            self.wave_active = False
            self.wave += 1
            if self.wave > 25:
                self.victory = True
            else:
                self.post_wave_event()

    def post_wave_event(self):
        if self.wave % 5 == 0 and self.wave < 25:
            if self.madness >= 70 and random.random() < 0.5:
                towers_list = [t for t in self.towers if not t.tower_type.startswith('chimera')]
                if len(towers_list) >= 2:
                    for _ in range(2):
                        t = random.choice(towers_list)
                        self.towers.remove(t)
                        towers_list.remove(t)
                self.souls += 50
            else:
                if self.money >= 150:
                    self.money -= 150
                else:
                    if self.towers:
                        t = random.choice(self.towers)
                        self.towers.remove(t)

    def build_tower(self, tower_type, cell):
        if self.money < TOWER_COST[tower_type]:
            return False
        if is_path_cell(cell):
            return False
        for t in self.towers:
            if t.cell == cell:
                return False
        self.towers.append(Tower(tower_type, cell))
        self.money -= TOWER_COST[tower_type]
        return True

    def upgrade_tower(self, cell):
        for t in self.towers:
            if t.cell == cell and t.level < 3 and not t.tower_type.startswith(('chimera', 'hell')):
                cost = TOWER_UPGRADE_COST[t.tower_type]
                if self.money >= cost:
                    t.upgrade()
                    self.money -= cost
                    return True
        return False

    def sell_tower(self, cell):
        for t in self.towers:
            if t.cell == cell:
                refund = int(TOWER_COST[t.tower_type] * 0.7 * t.level) if not t.tower_type.startswith(('chimera', 'hell')) else 0
                self.money += refund
                self.towers.remove(t)
           
                if t in self.merge_selection:
                    self.merge_selection.remove(t)
                return True
        return False

    def draw_ui(self, surface):
   
        panel_height = scaled(50)
        pygame.draw.rect(surface, (20, 20, 20), (0, 0, SCREEN_WIDTH, panel_height))

        seg_size = scaled(12)
        gap = scaled(2)
        segments = 10

        faith_segments = int(self.faith / MAX_FAITH * segments)
        for i in range(segments):
            x = scaled(20) + i * (seg_size + gap)
            y = scaled(15)
            color = CYAN if i < faith_segments else (60, 60, 60)
            pygame.draw.rect(surface, color, (x, y, seg_size, seg_size))
            pygame.draw.rect(surface, WHITE, (x, y, seg_size, seg_size), 1)
        faith_label = font_small.render("Faith", True, WHITE)
        surface.blit(faith_label, (scaled(20), scaled(32)))

        madness_segments = int(self.madness / MAX_MADNESS * segments)
        for i in range(segments):
            x = scaled(200) + i * (seg_size + gap)
            y = scaled(15)
            color = PURPLE if i < madness_segments else (60, 60, 60)
            pygame.draw.rect(surface, color, (x, y, seg_size, seg_size))
            pygame.draw.rect(surface, WHITE, (x, y, seg_size, seg_size), 1)
        madness_label = font_small.render("Madness", True, WHITE)
        surface.blit(madness_label, (scaled(200), scaled(32)))

        souls_text = font_medium.render(f"Souls: {self.souls}", True, GOLD)
        surface.blit(souls_text, (scaled(400), scaled(15)))
        lives_text = font_medium.render(f"Lives: {self.lives}", True, RED)
        surface.blit(lives_text, (scaled(600), scaled(15)))
        money_text = font_medium.render(f"Gold: {self.money}", True, YELLOW)
        surface.blit(money_text, (scaled(750), scaled(15)))
        wave_text = font_medium.render(f"Wave: {self.wave}/25", True, WHITE)
        surface.blit(wave_text, (scaled(950), scaled(15)))

        # Нижняя панель управления
        panel_y = SCREEN_HEIGHT - PANEL_HEIGHT
        pygame.draw.rect(surface, PANEL_BG, (0, panel_y, SCREEN_WIDTH, PANEL_HEIGHT))

        num_buttons = 10
        total_button_width = SCREEN_WIDTH - scaled(20)
        btn_width = total_button_width // num_buttons - scaled(5)
        btn_height = PANEL_HEIGHT - scaled(20)
        start_x = scaled(10)

        tower_types = ["archer", "mage", "cannon", "ice", "fire", "poison", "lightning"]
        for i, ttype in enumerate(tower_types):
            btn_rect = pygame.Rect(start_x + i * (btn_width + scaled(5)), panel_y + scaled(10), btn_width, btn_height)
            color = LIGHT_GRAY if self.selected_tower_type != ttype else GOLD
            pygame.draw.rect(surface, color, btn_rect)
            pygame.draw.rect(surface, BLACK, btn_rect, 2)
            txt = font_small.render(f"{ttype.capitalize()} ${TOWER_COST[ttype]}", True, BLACK)
            txt_rect = txt.get_rect(center=btn_rect.center)
            surface.blit(txt, txt_rect)

        start_btn = pygame.Rect(start_x + 7 * (btn_width + scaled(5)), panel_y + scaled(10), btn_width, btn_height)
        if not self.wave_active and self.wave <= 25 and not self.victory and not self.defeat:
            pygame.draw.rect(surface, GREEN, start_btn)
        else:
            pygame.draw.rect(surface, LIGHT_GRAY, start_btn)
        txt = font_small.render("Start Wave", True, WHITE)
        txt_rect = txt.get_rect(center=start_btn.center)
        surface.blit(txt, txt_rect)

        hellify_btn = pygame.Rect(start_btn.x + btn_width + scaled(5), panel_y + scaled(10), btn_width, btn_height)
        btn_color = GOLD if self.hellify_mode else DARK_RED
        pygame.draw.rect(surface, btn_color, hellify_btn)
        txt = font_small.render("Hellify", True, WHITE)
        txt_rect = txt.get_rect(center=hellify_btn.center)
        surface.blit(txt, txt_rect)

        merge_btn = pygame.Rect(hellify_btn.x + btn_width + scaled(5), panel_y + scaled(10), btn_width, btn_height)
        pygame.draw.rect(surface, GOLD, merge_btn)
        txt = font_small.render("Merge", True, BLACK)
        txt_rect = txt.get_rect(center=merge_btn.center)
        surface.blit(txt, txt_rect)

        if self.victory:
            txt = font_large.render("VICTORY! Satan is defeated.", True, GOLD)
            txt_rect = txt.get_rect(center=(SCREEN_WIDTH//2, SCREEN_HEIGHT//2))
            surface.blit(txt, txt_rect)
        elif self.defeat:
            txt = font_large.render("DEFEAT", True, RED)
            txt_rect = txt.get_rect(center=(SCREEN_WIDTH//2, SCREEN_HEIGHT//2))
            surface.blit(txt, txt_rect)

        # Подсветка выделенных башен (жёлтая рамка)
        for t in self.merge_selection:
            if t.hp > 0:
                rect = pygame.Rect(t.x - scaled(25), t.y - scaled(25), scaled(50), scaled(50))
                pygame.draw.rect(surface, YELLOW, rect, scaled(3))

game = Game()
running = True

while running:
    screen.fill(BLACK)

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                running = False

        if event.type == pygame.MOUSEBUTTONDOWN:
            pos = pygame.mouse.get_pos()
            panel_y = SCREEN_HEIGHT - PANEL_HEIGHT

            # Обработка кликов в нижней панели
            if pos[1] >= panel_y:
                num_buttons = 10
                total_button_width = SCREEN_WIDTH - scaled(20)
                btn_width = total_button_width // num_buttons - scaled(5)
                start_x = scaled(10)
                tower_types = ["archer", "mage", "cannon", "ice", "fire", "poison", "lightning"]
                for i, ttype in enumerate(tower_types):
                    btn_rect = pygame.Rect(start_x + i * (btn_width + scaled(5)), panel_y + scaled(10), btn_width, PANEL_HEIGHT - scaled(20))
                    if btn_rect.collidepoint(pos):
                        game.selected_tower_type = ttype
                        game.hellify_mode = False
                        game.merge_selection.clear()  # сброс выделения при смене типа
                        break
                start_btn = pygame.Rect(start_x + 7 * (btn_width + scaled(5)), panel_y + scaled(10), btn_width, PANEL_HEIGHT - scaled(20))
                if start_btn.collidepoint(pos) and not game.wave_active and game.wave <= 25:
                    game.start_wave()
                hellify_btn = pygame.Rect(start_btn.x + btn_width + scaled(5), panel_y + scaled(10), btn_width, PANEL_HEIGHT - scaled(20))
                if hellify_btn.collidepoint(pos):
                    game.hellify_mode = not game.hellify_mode
                    game.selected_tower_type = None
                    game.merge_selection.clear()
                merge_btn = pygame.Rect(hellify_btn.x + btn_width + scaled(5), panel_y + scaled(10), btn_width, PANEL_HEIGHT - scaled(20))
                if merge_btn.collidepoint(pos):
                    game.merge_towers()
            else:
                # Клик по игровому полю
                cell = cell_from_pos(pos)
                if 0 <= cell[0] < GRID_WIDTH and 0 <= cell[1] < GRID_HEIGHT:
                    # Проверяем, зажат ли Shift для ручного выделения башен
                    keys = pygame.key.get_pressed()
                    if keys[pygame.K_LSHIFT] or keys[pygame.K_RSHIFT]:
                        # Найти башню в этой клетке
                        for t in game.towers:
                            if t.cell == cell and not t.tower_type.startswith(('chimera', 'hell')):
                                # Если башня уже выделена – убираем, иначе добавляем (не более трёх)
                                if t in game.merge_selection:
                                    game.merge_selection.remove(t)
                                else:
                                    if len(game.merge_selection) < 3:
                                        game.merge_selection.append(t)
                                break
                    else:
                        # Обычный клик: строим или Hellify
                        if game.hellify_mode:
                            game.hellify_tower(cell)
                        elif game.selected_tower_type:
                            game.build_tower(game.selected_tower_type, cell)

        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_u and pygame.key.get_mods() & pygame.KMOD_SHIFT:
                pos = pygame.mouse.get_pos()
                if pos[1] < SCREEN_HEIGHT - PANEL_HEIGHT:
                    cell = cell_from_pos(pos)
                    if 0 <= cell[0] < GRID_WIDTH and 0 <= cell[1] < GRID_HEIGHT:
                        game.upgrade_tower(cell)
            if event.key == pygame.K_s:
                pos = pygame.mouse.get_pos()
                if pos[1] < SCREEN_HEIGHT - PANEL_HEIGHT:
                    cell = cell_from_pos(pos)
                    game.sell_tower(cell)
            if event.key == pygame.K_SPACE and not game.wave_active and game.wave <= 25:
                game.start_wave()
            if event.key == pygame.K_m:
                game.merge_towers()
            if event.key == pygame.K_h:
                game.hellify_mode = not game.hellify_mode
                game.merge_selection.clear()

    game.update()

    # Отрисовка поля
    field_rect = pygame.Rect(FIELD_OFFSET_X, FIELD_OFFSET_Y, FIELD_WIDTH, FIELD_HEIGHT)
    pygame.draw.rect(screen, GREEN, field_rect)
    for x in range(GRID_WIDTH):
        for y in range(GRID_HEIGHT):
            rect = pygame.Rect(FIELD_OFFSET_X + x * CELL_SIZE, FIELD_OFFSET_Y + y * CELL_SIZE, CELL_SIZE, CELL_SIZE)
            if is_path_cell((x, y)):
                pygame.draw.rect(screen, BROWN, rect)
            else:
                pygame.draw.rect(screen, GREEN, rect)
            pygame.draw.rect(screen, GRAY, rect, 1)
    if len(path_pixels) > 1:
        pygame.draw.lines(screen, BROWN, False, path_pixels, scaled(8))

    for tower in game.towers:
        tower.draw(screen)
    for enemy in game.enemies:
        enemy.draw(screen)

    game.draw_ui(screen)
    pygame.display.flip()
    clock.tick(60)

pygame.quit()
sys.exit()