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

SCALE = SCREEN_HEIGHT / 1500

font_size_small = max(36, int(54 * SCALE))
font_size_medium = max(42, int(72 * SCALE))
font_size_large = max(60, int(108 * SCALE))
font_small = pygame.font.Font(None, font_size_small)
font_medium = pygame.font.Font(None, font_size_medium)
font_large = pygame.font.Font(None, font_size_large)

SIDE_PANEL_WIDTH = int(SCREEN_WIDTH * 0.22)
AVAILABLE_MAP_WIDTH = SCREEN_WIDTH - 2 * SIDE_PANEL_WIDTH
VIEWPORT_SIZE = min(AVAILABLE_MAP_WIDTH, SCREEN_HEIGHT)
VIEWPORT_X = SIDE_PANEL_WIDTH + (AVAILABLE_MAP_WIDTH - VIEWPORT_SIZE) // 2
VIEWPORT_Y = (SCREEN_HEIGHT - VIEWPORT_SIZE) // 2
VIEWPORT_WIDTH = VIEWPORT_SIZE
VIEWPORT_HEIGHT = VIEWPORT_SIZE

GRID_WIDTH, GRID_HEIGHT = 40, 40
CELL_SIZE = max(28, int(54 * SCALE))
FIELD_OFFSET_X = 0
FIELD_OFFSET_Y = 0
FIELD_WIDTH = CELL_SIZE * GRID_WIDTH
FIELD_HEIGHT = CELL_SIZE * GRID_HEIGHT
MIN_ZOOM = max(VIEWPORT_WIDTH / FIELD_WIDTH, VIEWPORT_HEIGHT / FIELD_HEIGHT)
MAX_ZOOM = 1.9
START_ZOOM = min(MAX_ZOOM, max(MIN_ZOOM, 0.85))
EDGE_SCROLL_SIZE = max(16, int(22 * SCALE))

TOWER_COST = {
    "lamp": 100,
    "beacon": 150
}
TOWER_UPGRADE_COST = {
    "lamp": 140,
    "beacon": 200,
    "cannon": 200
}

STARTING_MONEY = 210
STARTING_ORE = 0
CASTLE_GOLD_INCOME = 6
CASTLE_GOLD_INTERVAL = 240
GENERATOR_INCOME_BY_LEVEL = {1: 2.5, 2: 5, 3: 10, 4: 20}
GENERATOR_TOWER_LIMIT_BY_LEVEL = {1: 6, 2: 12, 3: 18, 4: 24}
GENERATOR_UPGRADE_COST = {1: 300, 2: 600, 3: 1200}
ARTILLERY_COST = 400
REPAIR_CANNON_COST = 150
TOWER_ORE_COST = {
    "lamp": 0,
    "beacon": 0,
    "cannon": 0
}

BUILDABLE_TOWER_TYPES = ["lamp", "beacon"]
LIGHT_TOWER_TYPES = {"lamp", "beacon"}
TOWER_DISPLAY_NAMES = {
    "lamp": "Observer",
    "beacon": "Farseeker",
    "cannon": "Cannon",
    "mage": "Mage",
    "miner": "Miner",
    "barracks": "Barracks",
}
LIGHT_RADIUS_BY_TYPE = {"lamp": 3, "beacon": 1}
LIGHT_SIZE_BY_LEVEL = {1: 5, 2: 7, 3: 9, 4: 11}
LAMP_LIGHT_WIDTH = 3
ACTION_COOLDOWN_FRAMES = {
    "build": 18,
    "rotate": 12,
    "sell": 20,
}
DIRECTIONS = [(0, -1), (1, 0), (0, 1), (-1, 0)]
DIRECTION_NAMES = ["N", "E", "S", "W"]
ROTATABLE_LIGHT_TYPES = {"lamp"}
ROUTE_LIGHT_LOOKAHEAD_CELLS = 9
ROUTE_LIGHT_SWITCH_MIN_LIT = 4
ROUTE_LIGHT_SWITCH_RATIO = 0.45
ENEMY_HEALTH_MULTIPLIER = 2.0
ENEMY_SPEED_MULTIPLIER = 1.5
DIMMER_START_WAVE = 3
DIMMER_LAMP_DISABLE_RADIUS = 3
DIMMER_LAMP_DISABLE_DURATION = 120
DIMMER_LAMP_DISABLE_COOLDOWN = 360
LIGHT_DAMAGE_PER_SECOND = 0

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
PANEL_BG = (30, 30, 30)
ORE_COLOR = (180, 160, 100)
ALLY_COLOR = (70, 130, 230)
RAIDER_COLOR = (80, 20, 20)
CAMP_COLOR = (60, 40, 20)
LIGHT_BLUE = (130, 220, 255)
GENERATOR_BLUE = (80, 245, 255)
FOG_WHITE = (12, 16, 24)

MELEE = "mile"
RANGE = "range"

MAX_RAIDERS_PER_MINER = 2

HQ_MIN_X, HQ_MIN_Y = 19, 19
HQ_SIZE_CELLS = 2
HQ_CELLS = {
    (HQ_MIN_X + dx, HQ_MIN_Y + dy)
    for dx in range(HQ_SIZE_CELLS)
    for dy in range(HQ_SIZE_CELLS)
}
HQ_CENTER_X = FIELD_OFFSET_X + (HQ_MIN_X + HQ_SIZE_CELLS / 2) * CELL_SIZE
HQ_CENTER_Y = FIELD_OFFSET_Y + (HQ_MIN_Y + HQ_SIZE_CELLS / 2) * CELL_SIZE
GENERATOR_CELLS = set(HQ_CELLS)
BASE_CASTLE_LIGHT_MARGIN = 3
CASTLE_LIGHT_ZONE = {
    (x, y)
    for x in range(HQ_MIN_X - BASE_CASTLE_LIGHT_MARGIN, HQ_MIN_X + HQ_SIZE_CELLS + BASE_CASTLE_LIGHT_MARGIN)
    for y in range(HQ_MIN_Y - BASE_CASTLE_LIGHT_MARGIN, HQ_MIN_Y + HQ_SIZE_CELLS + BASE_CASTLE_LIGHT_MARGIN)
}
CANNON_CELLS = {
    (HQ_MIN_X - 1, HQ_MIN_Y - 1),
    (HQ_MIN_X + 2, HQ_MIN_Y - 1),
    (HQ_MIN_X - 1, HQ_MIN_Y + 2),
    (HQ_MIN_X + 2, HQ_MIN_Y + 2)
}

HQ_HITBOX_X1 = FIELD_OFFSET_X + HQ_MIN_X * CELL_SIZE
HQ_HITBOX_Y1 = FIELD_OFFSET_Y + HQ_MIN_Y * CELL_SIZE
HQ_HITBOX_X2 = HQ_HITBOX_X1 + 2 * CELL_SIZE
HQ_HITBOX_Y2 = HQ_HITBOX_Y1 + 2 * CELL_SIZE

LANES = {
    "north_a": [
        (6, 0), (6, 1), (6, 2), (6, 3), (6, 4), (6, 5),
        (7, 5), (8, 5), (9, 5), (10, 5), (11, 5), (12, 5),
        (12, 6), (12, 7), (12, 8), (12, 9), (12, 10),
        (13, 10), (14, 10), (15, 10), (16, 10), (16, 11),
        (16, 12), (16, 13), (16, 14), (16, 15), (16, 16),
        (17, 16), (18, 16), (19, 16), (19, 17), (19, 18), (19, 19)
    ],
    "north_b": [
        (30, 0), (30, 1), (30, 2), (30, 3), (30, 4), (30, 5),
        (30, 6), (30, 7), (29, 7), (28, 7), (27, 7), (26, 7),
        (26, 8), (26, 9), (26, 10), (26, 11), (26, 12), (26, 13),
        (25, 13), (24, 13), (23, 13), (23, 14), (23, 15),
        (23, 16), (23, 17), (23, 18), (22, 18), (22, 19),
        (21, 19), (20, 19)
    ],
    "west_a": [
        (0, 16), (1, 16), (2, 16), (3, 16), (4, 16), (5, 16),
        (6, 16), (7, 16), (8, 16), (9, 16), (10, 16), (11, 16),
        (12, 16), (13, 16), (13, 17), (13, 18), (13, 19),
        (13, 20), (14, 20), (15, 20), (16, 20), (17, 20),
        (18, 20), (19, 20)
    ],
    "west_b": [
        (0, 30), (1, 30), (2, 30), (3, 30), (4, 30), (5, 30),
        (6, 30), (7, 30), (8, 30), (9, 30), (10, 30), (10, 29),
        (10, 28), (10, 27), (10, 26), (10, 25), (11, 25),
        (12, 25), (13, 25), (14, 25), (15, 25), (16, 25),
        (16, 24), (16, 23), (16, 22), (17, 22), (18, 22),
        (19, 22), (19, 21), (19, 20)
    ],
    "south_east_a": [
        (39, 25), (38, 25), (37, 25), (36, 25), (35, 25),
        (34, 25), (33, 25), (32, 25), (32, 24), (32, 23),
        (32, 22), (32, 21), (31, 21), (30, 21), (29, 21),
        (28, 21), (27, 21), (26, 21), (25, 21), (24, 21),
        (24, 20), (23, 20), (22, 20), (21, 20), (20, 20)
    ],
    "south_east_b": [
        (31, 39), (31, 38), (31, 37), (31, 36), (31, 35),
        (31, 34), (30, 34), (29, 34), (28, 34), (27, 34),
        (26, 34), (26, 33), (26, 32), (26, 31), (26, 30),
        (26, 29), (25, 29), (24, 29), (23, 29), (22, 29),
        (22, 28), (22, 27), (22, 26), (22, 25), (22, 24),
        (21, 24), (20, 24), (20, 23), (20, 22), (20, 21), (20, 20)
    ]
}

ROAD_BRANCHES = {
    "north": ["north_a", "north_b"],
    "west": ["west_a", "west_b"],
    "south_east": ["south_east_a", "south_east_b"]
}
ROAD_KEYS = list(ROAD_BRANCHES.keys())
PRIMARY_LANES = [branches[0] for branches in ROAD_BRANCHES.values()]
LANE_TO_BRANCHES = {
    lane_name: branches
    for branches in ROAD_BRANCHES.values()
    for lane_name in branches
}

PATH_CELLS = set()
for lane_cells in LANES.values():
    PATH_CELLS.update(lane_cells)
PATH_CELLS.difference_update(HQ_CELLS)

ALL_PATH_CELLS = set(PATH_CELLS)
ALL_PATH_CELLS.update(HQ_CELLS)

def validate_map():
    for cell in PATH_CELLS | HQ_CELLS:
        x, y = cell
        if not (0 <= x < GRID_WIDTH and 0 <= y < GRID_HEIGHT):
            raise ValueError(f"Map cell outside grid: {cell}")

    for lane_name, cells in LANES.items():
        if len(cells) < 2:
            raise ValueError(f"Lane '{lane_name}' is too short")
        if cells[-1] not in HQ_CELLS:
            raise ValueError(f"Lane '{lane_name}' must end at HQ")
        for cell in cells[:-1]:
            if cell not in PATH_CELLS:
                raise ValueError(f"Lane '{lane_name}' uses non-path cell: {cell}")
        for current_cell, next_cell in zip(cells, cells[1:]):
            dx = abs(current_cell[0] - next_cell[0])
            dy = abs(current_cell[1] - next_cell[1])
            if dx + dy != 1:
                raise ValueError(f"Lane '{lane_name}' has disconnected cells: {current_cell} -> {next_cell}")

    for cell in CANNON_CELLS:
        x, y = cell
        if not (0 <= x < GRID_WIDTH and 0 <= y < GRID_HEIGHT):
            raise ValueError(f"Cannon cell outside grid: {cell}")
        if cell in PATH_CELLS or cell in HQ_CELLS:
            raise ValueError(f"Cannon cannot stand on a road or generator cell: {cell}")

validate_map()

MAP_CORNERS = [
    (FIELD_OFFSET_X + CELL_SIZE // 2, FIELD_OFFSET_Y + CELL_SIZE // 2),
    (FIELD_OFFSET_X + (GRID_WIDTH - 1) * CELL_SIZE + CELL_SIZE // 2, FIELD_OFFSET_Y + CELL_SIZE // 2),
    (FIELD_OFFSET_X + CELL_SIZE // 2, FIELD_OFFSET_Y + (GRID_HEIGHT - 1) * CELL_SIZE + CELL_SIZE // 2),
    (FIELD_OFFSET_X + (GRID_WIDTH - 1) * CELL_SIZE + CELL_SIZE // 2, FIELD_OFFSET_Y + (GRID_HEIGHT - 1) * CELL_SIZE + CELL_SIZE // 2)
]

def get_path_pixels(lane_name):
    cells = LANES[lane_name]
    return [(FIELD_OFFSET_X + x * CELL_SIZE + CELL_SIZE // 2,
             FIELD_OFFSET_Y + y * CELL_SIZE + CELL_SIZE // 2) for (x, y) in cells]

def cell_from_pos(pos):
    x, y = pos
    grid_x = (x - FIELD_OFFSET_X) // CELL_SIZE
    grid_y = (y - FIELD_OFFSET_Y) // CELL_SIZE
    return int(grid_x), int(grid_y)

def is_any_path_cell(cell):
    return cell in ALL_PATH_CELLS

def is_hq_cell(cell):
    return cell in HQ_CELLS

def distance_to_hq_hitbox(pos):
    x, y = pos
    closest_x = max(HQ_HITBOX_X1, min(x, HQ_HITBOX_X2))
    closest_y = max(HQ_HITBOX_Y1, min(y, HQ_HITBOX_Y2))
    return math.hypot(x - closest_x, y - closest_y)

def count_miner_attackers(miner, enemies, exclude_enemy=None):
    count = 0
    for e in enemies:
        if e is exclude_enemy:
            continue
        if e.alive and getattr(e, 'attacking_tower', None) is miner:
            count += 1
    return count

def find_nearest_path_cell(cell):
    best = None
    best_dist = float('inf')
    for pc in ALL_PATH_CELLS:
        if is_hq_cell(pc):
            continue
        d = abs(pc[0] - cell[0]) + abs(pc[1] - cell[1])
        if d < best_dist:
            best_dist = d
            best = pc
    if best is None:
        return None
    return (FIELD_OFFSET_X + best[0] * CELL_SIZE + CELL_SIZE // 2,
            FIELD_OFFSET_Y + best[1] * CELL_SIZE + CELL_SIZE // 2)

def scaled(val):
    return int(val * SCALE)

def draw_square_dot(surface, color, center, size, border_color=None, border_width=0):
    size = max(1, int(size))
    rect = pygame.Rect(int(center[0] - size // 2), int(center[1] - size // 2), size, size)
    pygame.draw.rect(surface, color, rect)
    if border_color and border_width > 0:
        pygame.draw.rect(surface, border_color, rect, border_width)


class AlliedUnit:
    LEASH_RADIUS_CELLS = 2

    def __init__(self, barracks):
        self.barracks = barracks
        self.home_pos = list(barracks.spawn_point)
        self.pos = list(barracks.spawn_point)
        self.max_hp = 80 + 40 * (barracks.level - 1)
        self.hp = self.max_hp
        self.damage = 15 + 8 * (barracks.level - 1)
        self.attack_range = scaled(38)
        self.speed = scaled(1.8)
        self.attack_cooldown_max = 40
        self.attack_cooldown = 0
        self.target = None
        self.alive = True
        self.color = ALLY_COLOR
        self.reward = 0
        self.leash_radius = self.LEASH_RADIUS_CELLS * CELL_SIZE

    def _distance_to_home(self):
        return math.hypot(self.pos[0] - self.home_pos[0], self.pos[1] - self.home_pos[1])

    def find_target(self, enemies):
        best = None
        best_dist = float('inf')
        for e in enemies:
            if not e.alive:
                continue
            home_to_enemy = math.hypot(e.pos[0] - self.home_pos[0], e.pos[1] - self.home_pos[1])
            if home_to_enemy > self.leash_radius:
                continue
            d = math.hypot(e.pos[0] - self.pos[0], e.pos[1] - self.pos[1])
            if d < best_dist:
                best_dist = d
                best = e
        return best

    def update(self, enemies):
        if not self.alive:
            return
        if self.attack_cooldown > 0:
            self.attack_cooldown -= 1

        if self.target is not None:
            if not self.target.alive:
                self.target = None
            else:
                home_to_target = math.hypot(self.target.pos[0] - self.home_pos[0],
                                            self.target.pos[1] - self.home_pos[1])
                if home_to_target > self.leash_radius:
                    self.target = None

        if self.target is None:
            self.target = self.find_target(enemies)

        if self._distance_to_home() > self.leash_radius:
            self.target = None
            dx = self.home_pos[0] - self.pos[0]
            dy = self.home_pos[1] - self.pos[1]
            d = math.hypot(dx, dy)
            if d > self.speed:
                self.pos[0] += (dx / d) * self.speed
                self.pos[1] += (dy / d) * self.speed
            else:
                self.pos[0] = self.home_pos[0]
                self.pos[1] = self.home_pos[1]
            return

        if self.target is not None and self.target.alive:
            tx, ty = self.target.pos
            dist = math.hypot(self.pos[0] - tx, self.pos[1] - ty)
            if dist <= self.attack_range:
                if self.attack_cooldown <= 0:
                    self.target.take_damage(self.damage, "physical")
                    self.attack_cooldown = self.attack_cooldown_max
                return
            dx = tx - self.pos[0]
            dy = ty - self.pos[1]
            d = math.hypot(dx, dy)
            if d > 0:
                self.pos[0] += (dx / d) * self.speed
                self.pos[1] += (dy / d) * self.speed
        else:
            dx = self.home_pos[0] - self.pos[0]
            dy = self.home_pos[1] - self.pos[1]
            d = math.hypot(dx, dy)
            if d > self.speed:
                self.pos[0] += (dx / d) * self.speed
                self.pos[1] += (dy / d) * self.speed
            else:
                self.pos[0] = self.home_pos[0]
                self.pos[1] = self.home_pos[1]

    def take_damage(self, damage, damage_type):
        if damage_type == "physical":
            effective = damage * 0.85
        else:
            effective = damage
        self.hp -= effective
        if self.hp <= 0:
            self.hp = 0
            self.alive = False

    def draw(self, surface):
        if not self.alive:
            return
        pygame.draw.polygon(surface, self.color, [
            (int(self.pos[0]), int(self.pos[1] - scaled(14))),
            (int(self.pos[0] - scaled(11)), int(self.pos[1])),
            (int(self.pos[0]), int(self.pos[1] + scaled(14))),
            (int(self.pos[0] + scaled(11)), int(self.pos[1]))
        ])
        if self.target and self.target.alive:
            tx, ty = self.target.pos
            dx = tx - self.pos[0]
            dy = ty - self.pos[1]
            d = math.hypot(dx, dy)
            if d > 0:
                sword_end = (int(self.pos[0] + dx / d * scaled(18)),
                             int(self.pos[1] + dy / d * scaled(18)))
                pygame.draw.line(surface, WHITE, (int(self.pos[0]), int(self.pos[1])),
                                 sword_end, max(2, scaled(3)))
        bar_width = scaled(26)
        pygame.draw.rect(surface, RED, (int(self.pos[0] - bar_width/2), int(self.pos[1] - scaled(22)), bar_width, scaled(4)))
        green_w = bar_width * (self.hp / self.max_hp)
        pygame.draw.rect(surface, GREEN, (int(self.pos[0] - bar_width/2), int(self.pos[1] - scaled(22)), int(green_w), scaled(4)))


class Raider:
    def __init__(self, target_miner, spawn_pos, from_camp=False):
        self.target_miner = target_miner
        self.pos = list(spawn_pos)
        self.max_hp = 42
        self.hp = self.max_hp
        self.damage = 14
        # ИСПРАВЛЕНО: радиус атаки такой же, как у обычных мобов при атаке HQ
        self.attack_range = scaled(40)
        raw_speed = max(1, scaled(1.0))
        self.speed = float(raw_speed)
        self.base_speed = self.speed
        # ИСПРАВЛЕНО: кулдаун атаки как у обычных мобов (1 секунда = 60 кадров)
        # Раньше было 1500 (25 секунд) — мародер почти не бил
        self.attack_cooldown_max = 60
        self.attack_cooldown = 0
        self.alive = True
        self.color = RAIDER_COLOR
        self.reward = 12
        self.attacking_tower = None
        self.burn_timer = 0
        self.poison_timer = 0
        self.slow_timer = 0
        self.phys_armor = 0.05
        self.mag_armor = 0.05
        self.evade = 0.08
        self.path_index = 0
        self.path = []
        self.lane = None
        self.can_rise = False
        self.risen = False
        self.enemy_type = "raider"
        self.from_camp = from_camp

    def move(self, towers, hq, enemies, allied_units, raider_camps):
        if not self.alive:
            return
        if self.attack_cooldown > 0:
            self.attack_cooldown -= 1

        # Если цель мертва — ищем новую или идём к HQ
        if self.target_miner is None or (isinstance(self.target_miner, Tower) and self.target_miner.hp <= 0):
            if not self.from_camp:
                new_target = None
                min_dist = float('inf')
                for t in towers:
                    if t.tower_type == "miner" and t.hp > 0:
                        d = math.hypot(self.pos[0] - t.x, self.pos[1] - t.y)
                        if d < min_dist:
                            min_dist = d
                            new_target = t
                if new_target:
                    self.target_miner = new_target
                else:
                    self.target_miner = None
            else:
                self.target_miner = None
            
            # Если нет добытчика — идём к HQ
            if self.target_miner is None:
                if hq.hp > 0:
                    dist = distance_to_hq_hitbox(self.pos)
                    if dist <= self.attack_range:
                        if self.attack_cooldown <= 0:
                            hq.take_damage(self.damage)
                            self.attack_cooldown = self.attack_cooldown_max
                        return
                    dx = HQ_CENTER_X - self.pos[0]
                    dy = HQ_CENTER_Y - self.pos[1]
                    d = math.hypot(dx, dy)
                    if d > 0:
                        self.pos[0] += (dx / d) * self.speed
                        self.pos[1] += (dy / d) * self.speed
                return

        # Атака добытчика — как обычные мобы атакуют HQ:
        # подходим на дистанцию атаки и бьём с кулдауном
        if isinstance(self.target_miner, Tower) and self.target_miner.hp > 0:
            tx, ty = self.target_miner.x, self.target_miner.y
            dist = math.hypot(self.pos[0] - tx, self.pos[1] - ty)
            if dist <= self.attack_range:
                # В радиусе атаки — бьём, если кулдаун готов
                if self.attack_cooldown <= 0:
                    self.target_miner.take_damage(self.damage)
                    self.attack_cooldown = self.attack_cooldown_max
                # Стоим на месте, пока кулдаун не закончится
                return
            # Вне радиуса — подходим ближе
            dx = tx - self.pos[0]
            dy = ty - self.pos[1]
            d = math.hypot(dx, dy)
            if d > 0:
                self.pos[0] += (dx / d) * self.speed
                self.pos[1] += (dy / d) * self.speed

    def take_damage(self, damage, damage_type, damage_source=None):
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
        if not self.alive:
            return
        pygame.draw.rect(surface, self.color, (int(self.pos[0] - scaled(12)), int(self.pos[1] - scaled(12)), scaled(24), scaled(24)))
        draw_square_dot(surface, WHITE, (self.pos[0], self.pos[1] - scaled(4)), scaled(12))
        draw_square_dot(surface, BLACK, (self.pos[0] - scaled(3), self.pos[1] - scaled(5)), scaled(3))
        draw_square_dot(surface, BLACK, (self.pos[0] + scaled(3), self.pos[1] - scaled(5)), scaled(3))
        bar_width = scaled(24)
        pygame.draw.rect(surface, RED, (int(self.pos[0] - bar_width/2), int(self.pos[1] - scaled(20)), bar_width, scaled(4)))
        green_width = bar_width * (self.hp / self.max_hp)
        pygame.draw.rect(surface, YELLOW, (int(self.pos[0] - bar_width/2), int(self.pos[1] - scaled(20)), int(green_width), scaled(4)))


class RaiderCamp:
    def __init__(self, cell, pos):
        self.cell = cell
        self.x = pos[0]
        self.y = pos[1]
        self.max_hp = 250
        self.hp = self.max_hp
        self.spawn_timer = 0
        self.spawn_cooldown = 1800
        self.damage_type = "physical"

    def take_damage(self, damage):
        self.hp -= damage
        if self.hp <= 0:
            self.hp = 0

    def update(self, game):
        if self.hp <= 0:
            return
        self.spawn_timer += 1
        if self.spawn_timer >= self.spawn_cooldown:
            self.spawn_timer = 0
            raider = Raider(None, (self.x, self.y), from_camp=True)
            raider.target_miner = None
            game.raiders.append(raider)

    def draw(self, surface):
        if self.hp <= 0:
            return
        rect_size = scaled(36)
        pygame.draw.rect(surface, CAMP_COLOR, (self.x - rect_size//2, self.y - rect_size//2, rect_size, rect_size))
        pygame.draw.polygon(surface, (100, 60, 30), [
            (self.x - scaled(14), self.y + scaled(10)),
            (self.x + scaled(14), self.y + scaled(10)),
            (self.x, self.y - scaled(10))
        ])
        pygame.draw.line(surface, BLACK, (self.x, self.y - scaled(10)), (self.x, self.y - scaled(20)), scaled(2))
        pygame.draw.polygon(surface, RED, [
            (self.x, self.y - scaled(20)),
            (self.x + scaled(8), self.y - scaled(17)),
            (self.x, self.y - scaled(14))
        ])
        ratio = self.spawn_timer / self.spawn_cooldown
        bar_w = rect_size
        pygame.draw.rect(surface, BLACK, (self.x - bar_w//2, self.y + rect_size//2 + scaled(3), bar_w, scaled(4)))
        pygame.draw.rect(surface, RED, (self.x - bar_w//2, self.y + rect_size//2 + scaled(3), int(bar_w * ratio), scaled(4)))
        bar_width = scaled(40)
        bar_y = self.y - scaled(30)
        pygame.draw.rect(surface, RED, (self.x - bar_width//2, bar_y, bar_width, scaled(6)))
        hp_ratio = self.hp / self.max_hp
        pygame.draw.rect(surface, YELLOW, (self.x - bar_width//2, bar_y, int(bar_width * hp_ratio), scaled(6)))


class Enemy:
    def __init__(self, enemy_type, lane):
        self.enemy_type = enemy_type
        self.lane = lane
        base_range = scaled(40)
        stats = {
            "orc": {"hp": 72, "phys": 0.1, "mag": -0.3, "speed": scaled(1.0), "rise": False, "evade": 0.03,
                    "attack": MELEE, "color": GREEN, "atk_dmg": 9, "atk_range": base_range, "atk_cd": 65,
                    "vulnerable_to": {"mage": 1.45}},
            "wurg": {"hp": 68, "phys": 0.0, "mag": 0.1, "speed": scaled(1.5), "rise": False, "evade": 0.12,
                     "attack": MELEE, "color": YELLOW, "atk_dmg": 11, "atk_range": base_range, "atk_cd": 55,
                     "vulnerable_to": {"archer": 1.6}},
            "dimmer": {"hp": 54, "phys": 0.0, "mag": -0.2, "speed": scaled(0.9), "rise": False, "evade": 0.02,
                       "attack": MELEE, "color": (45, 45, 70), "atk_dmg": 7, "atk_range": base_range, "atk_cd": 70,
                       "vulnerable_to": {"cannon": 1.35}},
            "hellbrute": {"hp": 480, "phys": 0.3, "mag": 0.05, "speed": scaled(0.38), "rise": False, "evade": 0,
                          "attack": MELEE, "color": (200, 0, 200), "atk_dmg": 32, "atk_range": scaled(50), "atk_cd": 110,
                          "vulnerable_to": {"cannon": 1.8}}
        }
        s = stats[enemy_type]
        self.max_hp = int(s["hp"] * ENEMY_HEALTH_MULTIPLIER)
        self.hp = self.max_hp
        self.phys_armor = s["phys"]
        self.mag_armor = s["mag"]
        raw_speed = max(1, s["speed"]) * ENEMY_SPEED_MULTIPLIER
        self.speed = float(raw_speed)
        self.base_speed = float(raw_speed)
        self.can_rise = s["rise"]
        self.evade = s["evade"]
        self.attack_type = s["attack"]
        self.color = s["color"]
        self.attack_damage = s["atk_dmg"]
        self.attack_range = s["atk_range"]
        self.attack_cooldown_max = s["atk_cd"]
        self.attack_cooldown = 0
        self.vulnerable_to = s.get("vulnerable_to", {})

        self.path = get_path_pixels(lane)
        self.path_index = 0
        self.pos = list(self.path[0])
        self.alive = True
        self.risen = False
        self.attacking_tower = None
        self.stall_timer = 0
        self.stall_switch_threshold = 240
        self.switched_lane = False

        self.burn_timer = 0
        self.poison_timer = 0
        self.slow_timer = 0

        self.lamp_disable_cooldown = 0

        rewards = {"orc": 9, "wurg": 11, "dimmer": 14, "hellbrute": 45}
        self.reward = rewards[enemy_type]

    def reset_stall(self):
        self.stall_timer = 0

    def add_stall(self):
        if self.switched_lane:
            return
        self.stall_timer += 1
        if self.stall_timer >= self.stall_switch_threshold and self.can_switch_before_fork():
            self.switch_to_alternate_lane()

    def can_switch_before_fork(self):
        branches = LANE_TO_BRANCHES.get(self.lane)
        if not branches or len(branches) < 2:
            return False
        if self.lane != branches[0] or self.switched_lane:
            return False
        fork_index = max(4, min(10, len(self.path) // 3))
        return self.path_index <= fork_index

    def should_switch_for_light(self, game):
        if game is None or not self.can_switch_before_fork():
            return False
        lit_count, checked_count = game.get_lane_light_pressure(self.lane, self.path_index)
        if checked_count <= 0:
            return False
        return (
            lit_count >= ROUTE_LIGHT_SWITCH_MIN_LIT
            and lit_count / checked_count >= ROUTE_LIGHT_SWITCH_RATIO
        )

    def maybe_switch_for_light(self, game):
        if self.should_switch_for_light(game):
            self.switch_to_alternate_lane()

    def switch_to_alternate_lane(self):
        branches = LANE_TO_BRANCHES.get(self.lane)
        if not branches or len(branches) < 2:
            return False
        if self.lane != branches[0]:
            return False
        new_lane = branches[1]
        progress_index = self.path_index
        self.lane = new_lane
        self.path = get_path_pixels(new_lane)
        self.path_index = min(progress_index, max(0, len(self.path) - 2))
        self.pos = list(self.path[self.path_index])
        self.attacking_tower = None
        self.switched_lane = True
        self.stall_timer = 0
        return True

    def move(self, towers, hq, enemies, allied_units, raider_camps, game=None):
        if not self.alive:
            return
        if self.attack_cooldown > 0:
            self.attack_cooldown -= 1
        if isinstance(self.attacking_tower, Tower):
            self.attacking_tower = None
        self.maybe_switch_for_light(game)

        if self.attacking_tower:
            if isinstance(self.attacking_tower, AlliedUnit):
                if not self.attacking_tower.alive:
                    self.attacking_tower = None
                else:
                    dist = math.hypot(self.pos[0] - self.attacking_tower.pos[0],
                                      self.pos[1] - self.attacking_tower.pos[1])
                    if dist <= self.attack_range:
                        if self.attack_cooldown <= 0:
                            self.attack_tower(self.attacking_tower)
                        self.add_stall()
                        return
                    else:
                        self.attacking_tower = None
            elif isinstance(self.attacking_tower, RaiderCamp):
                if self.attacking_tower.hp <= 0:
                    self.attacking_tower = None
                else:
                    dist = math.hypot(self.pos[0] - self.attacking_tower.x, self.pos[1] - self.attacking_tower.y)
                    if dist <= self.attack_range:
                        if self.attack_cooldown <= 0:
                            self.attack_tower(self.attacking_tower)
                        self.add_stall()
                        return
                    else:
                        self.attacking_tower = None
            elif isinstance(self.attacking_tower, Headquarters):
                if self.attacking_tower.hp <= 0:
                    self.attacking_tower = None
                else:
                    dist = distance_to_hq_hitbox(self.pos)
                    if dist <= self.attack_range:
                        if self.attack_cooldown <= 0:
                            self.attack_tower(self.attacking_tower)
                        return
                    else:
                        self.attacking_tower = None
            elif isinstance(self.attacking_tower, Tower) and self.attacking_tower.tower_type == "miner":
                if self.attacking_tower.hp <= 0:
                    self.attacking_tower = None
                else:
                    tx, ty = self.attacking_tower.x, self.attacking_tower.y
                    dist = math.hypot(self.pos[0] - tx, self.pos[1] - ty)
                    if dist <= self.attack_range:
                        if self.attack_cooldown <= 0:
                            self.attack_tower(self.attacking_tower)
                        self.add_stall()
                        return
                    else:
                        self.attacking_tower = None
            elif isinstance(self.attacking_tower, Tower):
                if self.attacking_tower.hp <= 0:
                    self.attacking_tower = None
                else:
                    tx, ty = self.attacking_tower.x, self.attacking_tower.y
                    dist = math.hypot(self.pos[0] - tx, self.pos[1] - ty)
                    if dist <= self.attack_range:
                        if self.attack_cooldown <= 0:
                            self.attack_tower(self.attacking_tower)
                        self.add_stall()
                        return
                    else:
                        self.attacking_tower = None
            else:
                self.attacking_tower = None

        targets = []
        if hq.hp > 0:
            targets.append(hq)
        for au in allied_units:
            if au.alive:
                targets.append(au)
        for camp in raider_camps:
            if camp.hp > 0:
                targets.append(camp)

        target = None
        target_dist = float('inf')
        for t in targets:
            if isinstance(t, AlliedUnit):
                if not t.alive:
                    continue
                dist = math.hypot(self.pos[0] - t.pos[0], self.pos[1] - t.pos[1])
            elif isinstance(t, RaiderCamp):
                if t.hp <= 0:
                    continue
                dist = math.hypot(self.pos[0] - t.x, self.pos[1] - t.y)
            elif isinstance(t, Headquarters):
                if t.hp <= 0:
                    continue
                dist = distance_to_hq_hitbox(self.pos)
            else:
                if t.hp <= 0:
                    continue
                if isinstance(t, Tower) and t.tower_type == "miner":
                    if count_miner_attackers(t, enemies, self) >= MAX_RAIDERS_PER_MINER:
                        continue
                tx, ty = t.x, t.y
                dist = math.hypot(self.pos[0] - tx, self.pos[1] - ty)
            if dist <= self.attack_range:
                priority = 0 if isinstance(t, AlliedUnit) else 1
                if dist < target_dist - 2 or (abs(dist - target_dist) <= 2 and priority == 0):
                    target = t
                    target_dist = dist
        
        if target:
            self.attacking_tower = target
            if not isinstance(target, Headquarters):
                self.add_stall()
            return

        if self.path_index >= len(self.path) - 1:
            if hq.hp > 0:
                self.attacking_tower = hq
            else:
                self.alive = False
            return
        
        target_pos = self.path[self.path_index + 1]
        dx = target_pos[0] - self.pos[0]
        dy = target_pos[1] - self.pos[1]
        dist = math.hypot(dx, dy)
        if dist < self.speed * 1.5 or dist < 5:
            self.pos = list(target_pos)
            self.path_index += 1
            self.reset_stall()
        else:
            self.pos[0] += (dx / dist) * self.speed
            self.pos[1] += (dy / dist) * self.speed
            self.reset_stall()

    def attack_tower(self, target):
        try:
            target.take_damage(self.attack_damage, "physical")
        except TypeError:
            target.take_damage(self.attack_damage)
        self.attack_cooldown = self.attack_cooldown_max

    def take_damage(self, damage, damage_type, damage_source=None):
        if damage_type == "physical":
            effective = damage * (1 - self.phys_armor)
        else:
            effective = damage * (1 - self.mag_armor)
        if damage_source in self.vulnerable_to:
            effective *= self.vulnerable_to[damage_source]
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
        if self.enemy_type == "orc":
            pygame.draw.rect(surface, self.color, (int(self.pos[0] - scaled(15)), int(self.pos[1] - scaled(15)), scaled(30), scaled(30)))
        elif self.enemy_type == "wurg":
            pygame.draw.rect(surface, self.color, (int(self.pos[0] - scaled(14)), int(self.pos[1] - scaled(18)), scaled(28), scaled(36)))
            draw_square_dot(surface, WHITE, (self.pos[0], self.pos[1] - scaled(5)), scaled(8))
        elif self.enemy_type == "dimmer":
            rect_size = scaled(32)
            rect = pygame.Rect(int(self.pos[0] - rect_size // 2), int(self.pos[1] - rect_size // 2), rect_size, rect_size)
            pygame.draw.rect(surface, self.color, rect)
            pygame.draw.rect(surface, PURPLE, rect, max(1, scaled(2)))
            draw_square_dot(surface, BLACK, (self.pos[0], self.pos[1]), scaled(14), LIGHT_BLUE, max(1, scaled(1)))
        elif self.enemy_type == "hellbrute":
            pygame.draw.rect(surface, self.color, (int(self.pos[0] - scaled(18)), int(self.pos[1] - scaled(18)), scaled(36), scaled(36)))
        bar_width = scaled(30)
        pygame.draw.rect(surface, RED, (int(self.pos[0] - bar_width/2), int(self.pos[1] - scaled(25)), bar_width, scaled(5)))
        green_width = bar_width * (self.hp / self.max_hp)
        pygame.draw.rect(surface, YELLOW, (int(self.pos[0] - bar_width/2), int(self.pos[1] - scaled(25)), green_width, scaled(5)))


class SatanBoss(Enemy):
    def __init__(self, lane):
        super().__init__("hellbrute", lane)
        self.enemy_type = "satan"
        self.max_hp = 3800
        self.hp = self.max_hp
        raw_speed = max(1, scaled(0.55))
        self.speed = float(raw_speed)
        self.base_speed = float(raw_speed)
        self.phys_armor = 0.35
        self.mag_armor = 0.35
        self.evade = 0
        self.attack_range = scaled(60)
        self.attack_damage = 50
        self.attack_cooldown_max = 85
        self.attack_cooldown = 0
        self.color = (255, 0, 0)
        self.reward = 375
        self.phase = 1
        self.minion_timer = 0
        self.minion_cooldown = 300

    def check_phase(self):
        hp_ratio = self.hp / self.max_hp
        if hp_ratio > 0.66:
            new_phase = 1
        elif hp_ratio > 0.33:
            new_phase = 2
        else:
            new_phase = 3
        
        if new_phase != self.phase:
            self.phase = new_phase
            if self.phase == 2:
                self.speed = self.base_speed * 1.5
                self.slow_timer = 0
            elif self.phase == 3:
                self.speed = self.base_speed * 2.0
                self.slow_timer = 0

    def spawn_minions(self, game):
        if self.phase >= 2:
            self.minion_timer += 1
            cooldown = 360 if self.phase == 2 else 240
            if self.minion_timer >= cooldown:
                self.minion_timer = 0
                count = 1 if self.phase == 2 else 2
                for _ in range(count):
                    offset_x = random.randint(-CELL_SIZE, CELL_SIZE)
                    offset_y = random.randint(-CELL_SIZE, CELL_SIZE)
                    spawn_pos = (self.pos[0] + offset_x, self.pos[1] + offset_y)
                    lane = random.choice(PRIMARY_LANES)
                    minion = Enemy("orc", lane)
                    minion.pos = list(spawn_pos)
                    minion.hp = minion.max_hp // 2
                    game.enemies.append(minion)

    def move(self, towers, hq, enemies, allied_units, raider_camps, game=None):
        if not self.alive:
            return
        if self.attack_cooldown > 0:
            self.attack_cooldown -= 1
        
        self.check_phase()
        self.maybe_switch_for_light(game)
        
        if self.phase >= 2:
            self.slow_timer = 0
            self.speed = self.base_speed * (1.5 if self.phase == 2 else 2.0)
        
        ally_target = None
        ally_dist = float('inf')
        for au in allied_units:
            if au.alive:
                d = math.hypot(self.pos[0] - au.pos[0], self.pos[1] - au.pos[1])
                if d <= self.attack_range and d < ally_dist:
                    ally_dist = d
                    ally_target = au
        if ally_target:
            if self.attack_cooldown <= 0:
                try:
                    ally_target.take_damage(self.attack_damage, "physical")
                except TypeError:
                    ally_target.take_damage(self.attack_damage)
                self.attack_cooldown = self.attack_cooldown_max
            return
        
        if hq.hp > 0:
            dist = distance_to_hq_hitbox(self.pos)
            if dist <= self.attack_range:
                if self.attack_cooldown <= 0:
                    hq.take_damage(self.attack_damage)
                    self.attack_cooldown = self.attack_cooldown_max
                return
        
        if self.path_index >= len(self.path) - 1:
            if hq.hp > 0:
                hq.take_damage(self.attack_damage)
                self.attack_cooldown = self.attack_cooldown_max
            else:
                self.alive = False
            return
        target = self.path[self.path_index + 1]
        dx = target[0] - self.pos[0]
        dy = target[1] - self.pos[1]
        dist = math.hypot(dx, dy)
        if dist < self.speed * 1.5 or dist < 5:
            self.pos = list(target)
            self.path_index += 1
        else:
            self.pos[0] += (dx / dist) * self.speed
            self.pos[1] += (dy / dist) * self.speed

    def draw(self, surface):
        rad = scaled(30)
        if self.phase == 1:
            color = (255, 0, 0)
        elif self.phase == 2:
            color = (255, 100, 0)
        else:
            color = (200, 0, 200)
        
        pygame.draw.rect(surface, color, (int(self.pos[0] - rad), int(self.pos[1] - rad), rad * 2, rad * 2))
        pygame.draw.rect(surface, WHITE, (int(self.pos[0] - rad), int(self.pos[1] - rad), rad * 2, rad * 2), max(1, scaled(3)))
        
        phase_txt = font_small.render(f"P{self.phase}", True, WHITE)
        surface.blit(phase_txt, (int(self.pos[0] - phase_txt.get_width()//2), int(self.pos[1] - rad - scaled(40))))
        
        bar_width = scaled(60)
        bar_y = int(self.pos[1] - rad - scaled(25))
        pygame.draw.rect(surface, RED, (int(self.pos[0] - bar_width/2), bar_y, bar_width, scaled(8)))
        green_width = bar_width * (self.hp / self.max_hp)
        pygame.draw.rect(surface, YELLOW, (int(self.pos[0] - bar_width/2), bar_y, int(green_width), scaled(8)))


class Tower:
    def __init__(self, tower_type, cell, fixed=False):
        self.tower_type = tower_type
        self.cell = cell
        self.fixed = fixed
        self.x = FIELD_OFFSET_X + cell[0] * CELL_SIZE + CELL_SIZE//2
        self.y = FIELD_OFFSET_Y + cell[1] * CELL_SIZE + CELL_SIZE//2
        self.level = 1
        base_range = scaled(150)
        stats = {
            "archer": {"damage": 15, "range": base_range, "cooldown": 30, "color": BLUE, "proj_color": CYAN, "hp": 150, "dmg_type": "physical"},
            "mage": {"damage": 20, "range": scaled(120), "cooldown": 40, "color": PURPLE, "proj_color": (255, 0, 255), "hp": 120, "dmg_type": "magical"},
            "cannon": {"damage": 80, "range": CELL_SIZE * max(GRID_WIDTH, GRID_HEIGHT) * 2, "cooldown": 52, "color": ORANGE, "proj_color": (255, 100, 0), "hp": 220, "dmg_type": "physical"},
            "miner": {"damage": 10, "range": scaled(100), "cooldown": 40, "color": ORE_COLOR, "proj_color": ORE_COLOR, "hp": 150, "dmg_type": "physical"},
            "barracks": {"damage": 0, "range": 0, "cooldown": 0, "color": (100, 60, 30), "proj_color": (100, 60, 30), "hp": 300, "dmg_type": "physical"},
            "lamp": {"damage": 0, "range": 0, "cooldown": 0, "color": LIGHT_BLUE, "proj_color": LIGHT_BLUE, "hp": 105, "dmg_type": "physical"},
            "beacon": {"damage": 0, "range": 0, "cooldown": 0, "color": GENERATOR_BLUE, "proj_color": GENERATOR_BLUE, "hp": 170, "dmg_type": "physical"}
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
        self.laser_beams = []
        self.damage_type = s["dmg_type"]
        self.splash_radius = scaled(60) if tower_type == "cannon" else 0
        self.splash_damage_multiplier = 0.5
        self.total_investment = 0 if fixed else TOWER_COST.get(tower_type, 0)
        self.specialization = None
        self.light_radius = LIGHT_RADIUS_BY_TYPE.get(tower_type, 0)
        self.direction_index = 1
        self.broken = False
        self.disabled_timer = 0
        self.is_powered = False

        if tower_type == "miner":
            self.mining = True
            self.stored_ore = 0
            self.attack_mode = False
            self.mining_cooldown = 0
            self.closed = False
            self.mode_transition_timer = 0
            self.mode_transition_max = 150
        elif tower_type == "barracks":
            self.spawn_point = find_nearest_path_cell(cell)
            self.allied_unit = None
            self.respawn_timer = 0
            self.respawn_cooldown = 300

    def upgrade(self):
        if self.level < 4:
            cost = TOWER_UPGRADE_COST[self.tower_type]
            self.level += 1
            if self.tower_type in LIGHT_TOWER_TYPES:
                self.max_hp = int(self.max_hp * 1.25)
                self.hp = self.max_hp
            elif self.tower_type == "miner":
                self.max_hp = int(self.max_hp * 1.3)
                self.hp = self.max_hp
            elif self.tower_type == "barracks":
                self.max_hp = int(self.max_hp * 1.4)
                self.hp = self.max_hp
                self.respawn_cooldown = max(120, self.respawn_cooldown - 60)
            else:
                self.damage = int(self.damage * 1.5)
                self.range = int(self.range * 1.1)
                self.cooldown_max = max(5, self.cooldown_max - 5)
                self.max_hp = int(self.max_hp * 1.3)
                self.hp = self.max_hp
            self.total_investment += cost
            return True
        return False

    def rotate(self):
        if self.tower_type not in ROTATABLE_LIGHT_TYPES or self.hp <= 0:
            return False
        self.direction_index = (self.direction_index + 1) % len(DIRECTIONS)
        return True

    def apply_specialization(self, spec_type):
        self.specialization = spec_type
        if self.tower_type == "cannon":
            if spec_type == "sniper":
                self.color = (255, 220, 90)
                self.damage = 150
                self.range = CELL_SIZE * max(GRID_WIDTH, GRID_HEIGHT) * 2
                self.cooldown_max = 78
                self.splash_radius = 0
                self.splash_damage_multiplier = 0
            elif spec_type == "scatter":
                self.color = (255, 145, 70)
                self.damage = 70
                self.range = CELL_SIZE * max(GRID_WIDTH, GRID_HEIGHT) * 2
                self.cooldown_max = 60
                self.splash_radius = scaled(115)
                self.splash_damage_multiplier = 0.75
            elif spec_type == "gatling":
                self.color = (120, 230, 140)
                self.damage = 44
                self.range = CELL_SIZE * 16
                self.cooldown_max = 16
                self.splash_radius = 0
                self.splash_damage_multiplier = 0
            self.cooldown = min(self.cooldown, self.cooldown_max)
            self.damage_type = "physical"
            return

    def take_damage(self, damage):
        return

    def find_target(self, enemies, raider_camps, raiders, game=None):
        if self.tower_type == "barracks" or self.damage == 0:
            return None
        in_range = []
        for e in enemies:
            if e.alive and math.hypot(e.pos[0] - self.x, e.pos[1] - self.y) <= self.range:
                if self.tower_type != "cannon" or game is None or game.is_target_lit(e):
                    in_range.append(e)
        for raider in raiders:
            if raider.alive and math.hypot(raider.pos[0] - self.x, raider.pos[1] - self.y) <= self.range:
                if self.tower_type != "cannon" or game is None or game.is_target_lit(raider):
                    in_range.append(raider)
        for camp in raider_camps:
            if camp.hp > 0 and math.hypot(camp.x - self.x, camp.y - self.y) <= self.range:
                if self.tower_type != "cannon" or game is None or game.is_target_lit(camp):
                    in_range.append(camp)
        if not in_range:
            return None
        if self.tower_type == "cannon":
            return min(in_range, key=self.cannon_target_priority)
        enemies_in_range = [e for e in in_range if hasattr(e, 'path_index')]
        if enemies_in_range:
            return min(enemies_in_range, key=self.path_target_priority)
        return min(in_range, key=lambda target: self.distance_to_target(target))

    def distance_to_target(self, target):
        if isinstance(target, RaiderCamp):
            tx, ty = target.x, target.y
        elif hasattr(target, "pos"):
            tx, ty = target.pos
        else:
            tx, ty = self.x, self.y
        return math.hypot(tx - self.x, ty - self.y)

    def path_target_priority(self, target):
        if hasattr(target, "path") and hasattr(target, "path_index"):
            remaining = max(0, len(target.path) - 1 - target.path_index)
            return (remaining, self.distance_to_target(target))
        return (10_000, self.distance_to_target(target))

    def estimated_damage_to(self, target):
        if isinstance(target, RaiderCamp):
            return max(1, self.damage)
        effective = self.damage
        if hasattr(target, "phys_armor") and hasattr(target, "mag_armor"):
            if self.damage_type == "physical":
                effective *= 1 - target.phys_armor
            else:
                effective *= 1 - target.mag_armor
        if hasattr(target, "vulnerable_to") and self.tower_type in target.vulnerable_to:
            effective *= target.vulnerable_to[self.tower_type]
        return max(1, effective)

    def cannon_target_priority(self, target):
        hp = max(1, getattr(target, "hp", 1))
        shots_to_kill = math.ceil(hp / self.estimated_damage_to(target))
        path_priority = self.path_target_priority(target)
        return (path_priority[0], shots_to_kill, path_priority[1])

    def update(self, enemies, game, raider_camps, raiders):
        for beam in self.laser_beams[:]:
            beam[4] -= 1
            if beam[4] <= 0:
                self.laser_beams.remove(beam)

        if self.disabled_timer > 0:
            self.disabled_timer -= 1

        if self.hp <= 0 or self.broken:
            return
        if self.tower_type == "barracks":
            if self.allied_unit is not None and not self.allied_unit.alive:
                self.allied_unit = None
            if self.allied_unit is None and self.spawn_point is not None:
                if self.respawn_timer > 0:
                    self.respawn_timer -= 1
                else:
                    new_unit = AlliedUnit(self)
                    self.allied_unit = new_unit
                    game.allied_units.append(new_unit)
                    self.respawn_timer = self.respawn_cooldown
            return
        if self.tower_type == "miner":
            if self.mode_transition_timer > 0:
                self.mode_transition_timer -= 1
                if self.mode_transition_timer == 0:
                    self.closed = not self.closed
                    self.mining = not self.closed
                return
            if self.closed:
                return
            if self.mining and not self.attack_mode:
                self.mining_cooldown += 1
                if self.mining_cooldown >= 30:
                    self.mining_cooldown = 0
                    vein = game.get_vein_at(self.cell)
                    if vein and vein.amount > 0:
                        vein.amount -= 1
                        self.stored_ore += 1
            if self.stored_ore > 0:
                game.ore += self.stored_ore
                self.stored_ore = 0
            if self.attack_mode:
                if self.cooldown > 0:
                    self.cooldown -= 1
                if self.cooldown == 0:
                    target = self.find_target(enemies, raider_camps, raiders, game)
                    if target:
                        self.projectiles.append([target, list((self.x, self.y))])
                        self.cooldown = self.cooldown_max
        else:
            if self.cooldown > 0:
                self.cooldown -= 1
            if self.cooldown == 0:
                target = self.find_target(enemies, raider_camps, raiders, game)
                if target and game.pay_shot(self):
                    if self.tower_type == "cannon":
                        self.fire_laser(target, enemies, raiders)
                    else:
                        self.projectiles.append([target, list((self.x, self.y))])
                    self.cooldown = self.cooldown_max

        for proj in self.projectiles[:]:
            target, pos = proj
            if not target.alive if hasattr(target, 'alive') else target.hp <= 0:
                self.projectiles.remove(proj)
                continue
            if self.tower_type == "cannon" and not game.is_target_lit(target):
                self.projectiles.remove(proj)
                continue
            if isinstance(target, RaiderCamp):
                tx, ty = target.x, target.y
            else:
                tx, ty = target.pos
            dx = tx - pos[0]
            dy = ty - pos[1]
            dist = math.hypot(dx, dy)
            speed = scaled(8)
            if dist < speed:
                if isinstance(target, RaiderCamp):
                    target.take_damage(self.damage)
                else:
                    target.take_damage(self.damage, self.damage_type, self.tower_type)
                
                if self.tower_type == "cannon" and not isinstance(target, RaiderCamp):
                    splash_radius = getattr(self, "splash_radius", scaled(60))
                    splash_damage = int(self.damage * getattr(self, "splash_damage_multiplier", 0.5))
                    if splash_radius > 0 and splash_damage > 0:
                        for e in enemies:
                            if e is not target and e.alive:
                                d = math.hypot(e.pos[0] - target.pos[0], e.pos[1] - target.pos[1])
                                if d <= splash_radius:
                                    e.take_damage(splash_damage, self.damage_type, self.tower_type)
                        for r in raiders:
                            if r is not target and r.alive:
                                d = math.hypot(r.pos[0] - target.pos[0], r.pos[1] - target.pos[1])
                                if d <= splash_radius:
                                    r.take_damage(splash_damage, self.damage_type, self.tower_type)
                
                if self.specialization == "ice" and not isinstance(target, RaiderCamp):
                    target.slow_timer = 60
                    target.speed = target.base_speed * 0.5
                elif self.specialization == "fire" and not isinstance(target, RaiderCamp):
                    target.burn_timer = 40
                elif self.specialization == "poison" and not isinstance(target, RaiderCamp):
                    target.poison_timer = 80
                elif self.specialization == "lightning" and not isinstance(target, RaiderCamp):
                    chain_targets = []
                    for e in enemies:
                        if e is not target and e.alive:
                            d = math.hypot(e.pos[0] - target.pos[0], e.pos[1] - target.pos[1])
                            if d <= scaled(120):
                                chain_targets.append((d, e))
                    chain_targets.sort(key=lambda x: x[0])
                    for _, e in chain_targets[:2]:
                        e.take_damage(int(self.damage * 0.5), self.damage_type, self.tower_type)
                self.projectiles.remove(proj)
            else:
                pos[0] += (dx / dist) * speed
                pos[1] += (dy / dist) * speed

    def fire_laser(self, target, enemies, raiders):
        if isinstance(target, RaiderCamp):
            tx, ty = target.x, target.y
            target.take_damage(self.damage)
        else:
            tx, ty = target.pos
            target.take_damage(self.damage, self.damage_type, self.tower_type)

            splash_radius = getattr(self, "splash_radius", scaled(60))
            splash_damage = int(self.damage * getattr(self, "splash_damage_multiplier", 0.5))
            if splash_radius > 0 and splash_damage > 0:
                for e in enemies:
                    if e is not target and e.alive:
                        d = math.hypot(e.pos[0] - tx, e.pos[1] - ty)
                        if d <= splash_radius:
                            e.take_damage(splash_damage, self.damage_type, self.tower_type)
                for r in raiders:
                    if r is not target and r.alive:
                        d = math.hypot(r.pos[0] - tx, r.pos[1] - ty)
                        if d <= splash_radius:
                            r.take_damage(splash_damage, self.damage_type, self.tower_type)

        self.laser_beams.append([self.x, self.y, tx, ty, 8])

    def draw(self, surface):
        if self.hp <= 0:
            return
        if self.tower_type == "barracks":
            rect_size = scaled(42)
            pygame.draw.rect(surface, self.color, (self.x - rect_size//2, self.y - rect_size//2, rect_size, rect_size))
            roof_pts = [(self.x - rect_size//2 - scaled(3), self.y - rect_size//2),
                        (self.x + rect_size//2 + scaled(3), self.y - rect_size//2),
                        (self.x, self.y - rect_size//2 - scaled(14))]
            pygame.draw.polygon(surface, RED, roof_pts)
            pygame.draw.rect(surface, BLACK, (self.x - scaled(6), self.y + scaled(4), scaled(12), scaled(16)))
            if self.spawn_point is not None:
                leash_r = AlliedUnit.LEASH_RADIUS_CELLS * CELL_SIZE
                leash_surf = pygame.Surface((leash_r * 2, leash_r * 2), pygame.SRCALPHA)
                step = max(1, CELL_SIZE)
                for sx in range(0, leash_r * 2, step):
                    for sy in range(0, leash_r * 2, step):
                        dx = abs(sx - leash_r)
                        dy = abs(sy - leash_r)
                        if dx + dy <= leash_r:
                            pygame.draw.rect(leash_surf, (70, 130, 230, 40), (sx, sy, step, step))
                surface.blit(leash_surf, (int(self.spawn_point[0]) - leash_r, int(self.spawn_point[1]) - leash_r))
            if self.allied_unit is None and self.respawn_timer > 0:
                ratio = 1 - (self.respawn_timer / self.respawn_cooldown)
                bar_w = rect_size
                pygame.draw.rect(surface, BLACK, (self.x - bar_w//2, self.y + rect_size//2 + scaled(3), bar_w, scaled(4)))
                pygame.draw.rect(surface, CYAN, (self.x - bar_w//2, self.y + rect_size//2 + scaled(3), int(bar_w * ratio), scaled(4)))
            if self.allied_unit is not None and self.allied_unit.alive:
                pygame.draw.line(surface, ALLY_COLOR, (self.x, self.y),
                                 (int(self.allied_unit.pos[0]), int(self.allied_unit.pos[1])), max(1, scaled(2)))
        elif self.tower_type == "miner":
            rect_size = scaled(30)
            color = GRAY if self.closed else self.color
            pygame.draw.rect(surface, color, (self.x - rect_size//2, self.y - rect_size//2, rect_size, rect_size))
            if self.mode_transition_timer > 0:
                ratio = 1 - self.mode_transition_timer / self.mode_transition_max
                pygame.draw.rect(surface, BLACK, (self.x - rect_size//2, self.y + rect_size//2 + scaled(3), rect_size, scaled(4)))
                pygame.draw.rect(surface, CYAN, (self.x - rect_size//2, self.y + rect_size//2 + scaled(3), int(rect_size * ratio), scaled(4)))
            elif self.attack_mode:
                pygame.draw.line(surface, RED, (self.x, self.y), (self.x + scaled(20), self.y - scaled(20)), scaled(3))
        elif self.tower_type in LIGHT_TOWER_TYPES:
            rect_size = scaled(34 if self.tower_type == "lamp" else 42)
            is_disabled = self.disabled_timer > 0
            is_powered = getattr(self, "is_powered", False) and not is_disabled
            if is_disabled:
                body_color = (82, 82, 82)
            elif is_powered:
                body_color = self.color if self.level == 1 else (170, 240, 255)
            else:
                body_color = (92, 108, 116)
            pygame.draw.rect(surface, body_color, (self.x - rect_size//2, self.y - rect_size//2, rect_size, rect_size))
            pygame.draw.rect(surface, BLACK, (self.x - rect_size//2, self.y - rect_size//2, rect_size, rect_size), max(1, scaled(2)))
            if is_powered:
                glow_radius = scaled(10 + 4 * self.level)
                pygame.draw.circle(surface, (255, 255, 205), (int(self.x), int(self.y)), glow_radius)
                pygame.draw.circle(surface, GENERATOR_BLUE, (int(self.x), int(self.y)), max(2, glow_radius // 2), max(1, scaled(2)))
            if self.tower_type == "lamp" and is_powered:
                dx, dy = DIRECTIONS[self.direction_index]
                length = scaled(24)
                end = (self.x + dx * length, self.y + dy * length)
                beam_color = (255, 255, 180)
                width = max(2, scaled(4))
                pygame.draw.line(surface, BLACK, (self.x, self.y), end, width)
                pygame.draw.line(surface, beam_color, (self.x, self.y), end, max(1, width // 2))
                pygame.draw.circle(surface, beam_color, (int(end[0]), int(end[1])), scaled(8))
        elif self.tower_type == "mage":
            rect_size = scaled(36)
            pygame.draw.rect(surface, self.color, (self.x - rect_size//2, self.y - rect_size//2, rect_size, rect_size))
            if self.specialization:
                spec_colors = {"ice": CYAN, "fire": (255, 100, 0), "poison": (100, 255, 100), "lightning": GOLD}
                spec_color = spec_colors.get(self.specialization, WHITE)
                draw_square_dot(surface, spec_color, (self.x, self.y - rect_size//2 - scaled(8)), scaled(12), BLACK, max(1, scaled(1)))
        else:
            if self.tower_type == "archer":
                rect_size = scaled(38)
                pygame.draw.rect(surface, self.color, (self.x - rect_size//2, self.y - rect_size//2, rect_size, rect_size))
                pygame.draw.rect(surface, CYAN, (self.x - rect_size//2, self.y - rect_size//2, rect_size, rect_size), max(1, scaled(2)))
            elif self.tower_type == "cannon":
                rect_size = scaled(44)
                cannon_color = GRAY if self.broken else self.color
                rect = pygame.Rect(self.x - rect_size//2, self.y - rect_size//2, rect_size, rect_size)
                pygame.draw.rect(surface, cannon_color, rect)
                draw_square_dot(surface, RED, (self.x, self.y), scaled(16))
                if self.broken:
                    pygame.draw.line(surface, RED, rect.topleft, rect.bottomright, max(2, scaled(3)))
                    pygame.draw.line(surface, RED, rect.topright, rect.bottomleft, max(2, scaled(3)))

        for proj in self.projectiles:
            draw_square_dot(surface, self.proj_color, proj[1], scaled(10), WHITE, max(1, scaled(1)))

        for x1, y1, x2, y2, timer in self.laser_beams:
            width = max(2, scaled(5))
            pygame.draw.line(surface, (255, 245, 170), (x1, y1), (x2, y2), width)
            pygame.draw.line(surface, RED, (x1, y1), (x2, y2), max(1, width // 2))

        return


class OreVein:
    def __init__(self, cells):
        self.cells = set(cells)
        self.amount = len(self.cells) * 100
        self.discovered = False

    def get_center(self):
        avg_x = sum(c[0] for c in self.cells) / len(self.cells)
        avg_y = sum(c[1] for c in self.cells) / len(self.cells)
        return FIELD_OFFSET_X + avg_x * CELL_SIZE + CELL_SIZE//2, FIELD_OFFSET_Y + avg_y * CELL_SIZE + CELL_SIZE//2

    def draw(self, surface):
        if not self.discovered or self.amount <= 0:
            return
        for cell in self.cells:
            x = FIELD_OFFSET_X + cell[0] * CELL_SIZE + CELL_SIZE//2
            y = FIELD_OFFSET_Y + cell[1] * CELL_SIZE + CELL_SIZE//2
            draw_square_dot(surface, ORE_COLOR, (x, y), scaled(18), BLACK, max(1, scaled(1)))
        cx, cy = self.get_center()
        txt = font_small.render(str(self.amount), True, BLACK)
        surface.blit(txt, (cx - txt.get_width()//2, cy - txt.get_height()//2))


class Hive:
    def __init__(self, road_key):
        self.road_key = road_key
        self.primary_lane = ROAD_BRANCHES[road_key][0]
        self.cell = LANES[self.primary_lane][0]
        self.x = FIELD_OFFSET_X + self.cell[0] * CELL_SIZE + CELL_SIZE // 2
        self.y = FIELD_OFFSET_Y + self.cell[1] * CELL_SIZE + CELL_SIZE // 2
        self.hp = 1
        self.is_alive = True
        self.is_visible = False

    def contains_cell(self, cell):
        return self.is_alive and self.is_visible and cell == self.cell

    def draw(self, surface):
        if not self.is_alive or not self.is_visible:
            return
        size = scaled(48)
        rect = pygame.Rect(int(self.x - size // 2), int(self.y - size // 2), size, size)
        pygame.draw.rect(surface, PURPLE, rect)
        pygame.draw.rect(surface, BLACK, rect, max(1, scaled(2)))
        label = font_small.render("Hive", True, WHITE)
        surface.blit(label, label.get_rect(center=(int(self.x), int(self.y))))


class MapBonus:
    COLORS = {
        "currency": GOLD,
        "cannon_upgrade": BLUE,
        "generator_upgrade": GREEN,
        "broken_cannon": GRAY,
    }

    def __init__(self, cell, bonus_type):
        self.cell = cell
        self.bonus_type = bonus_type
        self.is_collected = False
        self.is_visible = False
        self.x = FIELD_OFFSET_X + cell[0] * CELL_SIZE + CELL_SIZE // 2
        self.y = FIELD_OFFSET_Y + cell[1] * CELL_SIZE + CELL_SIZE // 2

    def contains_cell(self, cell):
        return self.is_visible and not self.is_collected and self.cell == cell

    def draw(self, surface):
        if self.is_collected or not self.is_visible:
            return
        size = scaled(30)
        color = self.COLORS[self.bonus_type]

        if self.bonus_type in {"cannon_upgrade", "generator_upgrade"}:
            points = [
                (self.x, self.y - size // 2),
                (self.x + size // 2, self.y),
                (self.x, self.y + size // 2),
                (self.x - size // 2, self.y),
            ]
            pygame.draw.polygon(surface, color, points)
            pygame.draw.polygon(surface, BLACK, points, max(1, scaled(2)))
            return

        rect = pygame.Rect(int(self.x - size // 2), int(self.y - size // 2), size, size)
        pygame.draw.rect(surface, color, rect)
        pygame.draw.rect(surface, BLACK, rect, max(1, scaled(2)))
        if self.bonus_type == "broken_cannon":
            pygame.draw.line(surface, RED, rect.topleft, rect.bottomright, max(2, scaled(3)))
            pygame.draw.line(surface, RED, rect.topright, rect.bottomleft, max(2, scaled(3)))


class Headquarters:
    def __init__(self):
        self.hp = 1000
        self.max_hp = 1000
        self.level = 1
        self.income_buffer = 0
        self.gold_generation_timer = 0
        self.attack_range = 0
        self.attack_damage = 0
        self.attack_cooldown_max = 60
        self.attack_cooldown = 0
        self.projectiles = []

    @property
    def income_per_second(self):
        return GENERATOR_INCOME_BY_LEVEL[self.level]

    @property
    def scout_limit(self):
        return GENERATOR_TOWER_LIMIT_BY_LEVEL[self.level]

    def upgrade_cost(self):
        return GENERATOR_UPGRADE_COST.get(self.level)

    def upgrade(self):
        if self.level >= 4:
            return False
        self.level += 1
        self.max_hp = int(self.max_hp * 1.2)
        self.hp = min(self.max_hp, self.hp + int(self.max_hp * 0.25))
        return True

    def take_damage(self, damage, damage_type=None):
        self.hp -= damage
        if self.hp < 0:
            self.hp = 0

    def find_targets(self, enemies, raiders, raider_camps):
        if self.attack_damage <= 0:
            return []
        candidates = []
        for e in enemies:
            if e.alive:
                d = math.hypot(e.pos[0] - HQ_CENTER_X, e.pos[1] - HQ_CENTER_Y)
                if d <= self.attack_range:
                    candidates.append((d, e))
        for r in raiders:
            if r.alive:
                d = math.hypot(r.pos[0] - HQ_CENTER_X, r.pos[1] - HQ_CENTER_Y)
                if d <= self.attack_range:
                    candidates.append((d, r))
        for c in raider_camps:
            if c.hp > 0:
                d = math.hypot(c.x - HQ_CENTER_X, c.y - HQ_CENTER_Y)
                if d <= self.attack_range:
                    candidates.append((d, c))
        candidates.sort(key=lambda x: x[0])
        return [c[1] for c in candidates[:2]]

    def update(self, game):
        self.income_buffer += self.income_per_second / 60
        if self.income_buffer >= 1:
            income = int(self.income_buffer)
            self.income_buffer -= income
            game.money += income
        
        if self.hp <= 0:
            return
        if self.attack_cooldown > 0:
            self.attack_cooldown -= 1
        
        for proj in self.projectiles[:]:
            target, pos = proj
            is_alive = False
            if hasattr(target, 'alive'):
                is_alive = target.alive
            elif hasattr(target, 'hp'):
                is_alive = target.hp > 0
            if not is_alive:
                self.projectiles.remove(proj)
                continue
            if isinstance(target, RaiderCamp):
                tx, ty = target.x, target.y
            else:
                tx, ty = target.pos
            dx = tx - pos[0]
            dy = ty - pos[1]
            dist = math.hypot(dx, dy)
            speed = scaled(10)
            if dist < speed:
                if isinstance(target, RaiderCamp):
                    target.take_damage(self.attack_damage)
                else:
                    target.take_damage(self.attack_damage, "magical")
                self.projectiles.remove(proj)
            else:
                pos[0] += (dx / dist) * speed
                pos[1] += (dy / dist) * speed
        
        if self.attack_cooldown <= 0:
            targets = self.find_targets(game.enemies, game.raiders, game.raider_camps)
            for t in targets:
                self.projectiles.append([t, [HQ_CENTER_X, HQ_CENTER_Y]])
            if targets:
                self.attack_cooldown = self.attack_cooldown_max

    def draw(self, surface):
        if self.hp <= 0:
            return
        rect = pygame.Rect(
            FIELD_OFFSET_X + HQ_MIN_X * CELL_SIZE,
            FIELD_OFFSET_Y + HQ_MIN_Y * CELL_SIZE,
            2 * CELL_SIZE,
            2 * CELL_SIZE
        )
        pygame.draw.rect(surface, GOLD, rect)
        pygame.draw.rect(surface, BLACK, rect, scaled(4))
        pygame.draw.rect(surface, GENERATOR_BLUE, rect, scaled(3))
        center = (int(HQ_CENTER_X), int(HQ_CENTER_Y))
        inner = rect.inflate(-scaled(18), -scaled(18))
        pygame.draw.rect(surface, (245, 255, 255), inner)
        draw_square_dot(surface, GENERATOR_BLUE, center, scaled(28), BLACK, max(1, scaled(2)))
        
        for proj in self.projectiles:
            _, pos = proj
            draw_square_dot(surface, GOLD, pos, scaled(14), WHITE, max(1, scaled(2)))
        
        bar_width = scaled(80)
        bar_y = rect.top - scaled(20)
        pygame.draw.rect(surface, RED, (int(HQ_CENTER_X - bar_width/2), bar_y, bar_width, scaled(10)))
        green_width = bar_width * (self.hp / self.max_hp)
        pygame.draw.rect(surface, YELLOW, (int(HQ_CENTER_X - bar_width/2), bar_y, int(green_width), scaled(10)))


class Game:
    def __init__(self):
        self.money = STARTING_MONEY
        self.ore = STARTING_ORE
        self.wave = 1
        self.wave_active = False
        self.wave_timer = 0
        self.enemies = []
        self.towers = [Tower("cannon", cell, fixed=True) for cell in sorted(CANNON_CELLS)]
        self.allied_units = []
        self.raiders = []
        self.raider_camps = []
        self.veins = []
        self.selected_tower_type = None
        self.selected_tower = None
        self.selected_hive = None
        self.action_cooldowns = {action: 0 for action in ACTION_COOLDOWN_FRAMES}
        self.build_direction_index = 1
        self.victory = False
        self.defeat = False
        self.hq = Headquarters()
        self.hives = [Hive(road_key) for road_key in ROAD_KEYS]
        self.bonuses = self.generate_bonuses()
        self.notification_text = ""
        self.notification_timer = 0
        
        self.first_wave_started = False
        
        self.tower_specialization_pending = False
        self.tower_to_specialize = None
        self.lit_cells = self.get_castle_light_zone() | set(GENERATOR_CELLS)
        self.shadow_cells = set()
        self.revealed_cells = set(self.lit_cells)
        
        self.raider_spawn_timer = 0
        self.raider_spawn_cooldown = 1800
        
        self.wave_interval = 0
        self.wave_interval_timer = 0
        self.wave_delay = 600
        self.wave_delay_timer = 0
        self.wave_delay_active = False
        
        self.total_waves = 999

        self.spawn_queue = []
        self.zoom = START_ZOOM
        self.camera_x = HQ_CENTER_X - VIEWPORT_WIDTH / self.zoom / 2
        self.camera_y = HQ_CENTER_Y - VIEWPORT_HEIGHT / self.zoom / 2
        self.dragging_camera = False
        self.last_drag_pos = None
        self.clamp_camera()
        self.update_lighting()
        self.start_wave(early=False)

    def clamp_camera(self):
        visible_w = VIEWPORT_WIDTH / self.zoom
        visible_h = VIEWPORT_HEIGHT / self.zoom
        max_x = max(0, FIELD_WIDTH - visible_w)
        max_y = max(0, FIELD_HEIGHT - visible_h)
        self.camera_x = max(0, min(self.camera_x, max_x))
        self.camera_y = max(0, min(self.camera_y, max_y))

    def is_in_viewport(self, pos):
        return (
            VIEWPORT_X <= pos[0] < VIEWPORT_X + VIEWPORT_WIDTH
            and VIEWPORT_Y <= pos[1] < VIEWPORT_Y + VIEWPORT_HEIGHT
        )

    def screen_to_world(self, pos):
        return (
            self.camera_x + (pos[0] - VIEWPORT_X) / self.zoom,
            self.camera_y + (pos[1] - VIEWPORT_Y) / self.zoom
        )

    def zoom_at(self, screen_pos, factor):
        old_world = self.screen_to_world(screen_pos)
        self.zoom = max(MIN_ZOOM, min(MAX_ZOOM, self.zoom * factor))
        self.camera_x = old_world[0] - (screen_pos[0] - VIEWPORT_X) / self.zoom
        self.camera_y = old_world[1] - (screen_pos[1] - VIEWPORT_Y) / self.zoom
        self.clamp_camera()

    def pan_camera(self, dx, dy):
        self.camera_x += dx
        self.camera_y += dy
        self.clamp_camera()

    def update_camera(self):
        keys = pygame.key.get_pressed()
        mouse_x, mouse_y = pygame.mouse.get_pos()
        speed = max(12, CELL_SIZE * 0.65) / self.zoom
        dx = 0
        dy = 0

        if keys[pygame.K_a] or keys[pygame.K_LEFT]:
            dx -= speed
        if keys[pygame.K_d] or keys[pygame.K_RIGHT]:
            dx += speed
        if keys[pygame.K_w] or keys[pygame.K_UP]:
            dy -= speed
        if keys[pygame.K_s] or keys[pygame.K_DOWN]:
            dy += speed

        if self.is_in_viewport((mouse_x, mouse_y)):
            if mouse_x <= VIEWPORT_X + EDGE_SCROLL_SIZE:
                dx -= speed
            elif mouse_x >= VIEWPORT_X + VIEWPORT_WIDTH - EDGE_SCROLL_SIZE:
                dx += speed
            if mouse_y <= VIEWPORT_Y + EDGE_SCROLL_SIZE:
                dy -= speed
            elif mouse_y >= VIEWPORT_Y + VIEWPORT_HEIGHT - EDGE_SCROLL_SIZE:
                dy += speed

        if dx or dy:
            self.pan_camera(dx, dy)

    def get_castle_light_zone(self):
        margin = BASE_CASTLE_LIGHT_MARGIN + max(0, self.hq.level - 1)
        cells = set()
        for x in range(HQ_MIN_X - margin, HQ_MIN_X + HQ_SIZE_CELLS + margin):
            for y in range(HQ_MIN_Y - margin, HQ_MIN_Y + HQ_SIZE_CELLS + margin):
                if 0 <= x < GRID_WIDTH and 0 <= y < GRID_HEIGHT:
                    cells.add((x, y))
        return cells

    def generate_bonuses(self):
        rng = random.Random(2026)
        bonus_types = (
            ["currency"] * 5
            + ["cannon_upgrade"] * 2
            + ["generator_upgrade"]
            + ["broken_cannon"] * 2
        )
        bonuses = []
        occupied = set(ALL_PATH_CELLS) | set(HQ_CELLS) | set(CANNON_CELLS)

        for bonus_type in bonus_types:
            for _ in range(400):
                cell = (rng.randint(2, GRID_WIDTH - 3), rng.randint(2, GRID_HEIGHT - 3))
                if cell in occupied or cell in CASTLE_LIGHT_ZONE:
                    continue
                if any(abs(cell[0] - path[0]) + abs(cell[1] - path[1]) < 3 for path in PATH_CELLS):
                    continue
                if any(abs(cell[0] - bonus.cell[0]) + abs(cell[1] - bonus.cell[1]) < 5 for bonus in bonuses):
                    continue
                bonuses.append(MapBonus(cell, bonus_type))
                occupied.add(cell)
                break

        return bonuses

    def notify(self, text, duration=120):
        self.notification_text = text
        self.notification_timer = duration

    def clear_selection(self):
        self.selected_tower_type = None
        self.selected_tower = None
        self.selected_hive = None

    def select_or_toggle_tower(self, tower):
        if self.selected_tower is tower:
            self.clear_selection()
            return False
        self.selected_tower = tower
        self.selected_tower_type = None
        self.selected_hive = None
        return True

    def built_light_tower_count(self):
        return sum(
            1 for tower in self.towers
            if tower.tower_type in LIGHT_TOWER_TYPES and tower.hp > 0 and not getattr(tower, "fixed", False)
        )

    def repair_selected_cannon(self):
        if not self.selected_tower or self.selected_tower.tower_type != "cannon" or not self.selected_tower.broken:
            return False
        if self.money < REPAIR_CANNON_COST:
            self.notify("Need more light to repair")
            return False
        self.money -= REPAIR_CANNON_COST
        self.selected_tower.broken = False
        self.notify("Cannon repaired")
        return True

    def upgrade_generator(self):
        cost = self.hq.upgrade_cost()
        if cost is None:
            return False
        if self.money < cost:
            self.notify("Need more light for generator upgrade")
            return False
        if self.hq.upgrade():
            self.money -= cost
            self.notify(f"Generator level {self.hq.level}")
            return True
        return False

    def collect_bonus(self, bonus):
        if bonus.is_collected or not bonus.is_visible:
            return False
        if bonus.bonus_type == "currency":
            self.money += 100
            self.notify("+100 light found")
        elif bonus.bonus_type == "cannon_upgrade":
            for tower in self.towers:
                if tower.tower_type == "cannon" and tower.hp > 0:
                    tower.upgrade()
            self.notify("All cannons upgraded")
        elif bonus.bonus_type == "generator_upgrade":
            self.hq.upgrade()
            self.notify("Generator upgraded")
        elif bonus.bonus_type == "broken_cannon":
            tower = Tower("cannon", bonus.cell, fixed=True)
            tower.broken = True
            tower.total_investment = 0
            self.towers.append(tower)
            self.notify("Broken cannon found")
        bonus.is_collected = True
        return True

    def get_lane_light_pressure(self, lane, start_index):
        cells = LANES.get(lane, [])
        if not cells:
            return 0, 0
        start = max(0, min(start_index, len(cells) - 1))
        end = min(len(cells), start + ROUTE_LIGHT_LOOKAHEAD_CELLS)
        segment = cells[start:end]
        lit_count = sum(1 for cell in segment if self.is_lit(cell))
        return lit_count, len(segment)

    def update_dimmers(self):
        for enemy in self.enemies:
            if not enemy.alive or enemy.enemy_type != "dimmer":
                continue
            if enemy.lamp_disable_cooldown > 0:
                enemy.lamp_disable_cooldown -= 1
                continue

            enemy_cell = cell_from_pos(enemy.pos)
            candidates = [
                tower for tower in self.towers
                if (
                    tower.hp > 0
                    and tower.tower_type in LIGHT_TOWER_TYPES
                    and getattr(tower, "disabled_timer", 0) <= 0
                    and abs(tower.cell[0] - enemy_cell[0]) + abs(tower.cell[1] - enemy_cell[1]) <= DIMMER_LAMP_DISABLE_RADIUS
                )
            ]
            if not candidates:
                continue

            tower = random.choice(candidates)
            tower.disabled_timer = DIMMER_LAMP_DISABLE_DURATION
            enemy.lamp_disable_cooldown = DIMMER_LAMP_DISABLE_COOLDOWN

    def apply_light_damage(self):
        if LIGHT_DAMAGE_PER_SECOND <= 0:
            return
        damage = LIGHT_DAMAGE_PER_SECOND / 60
        for enemy in self.enemies:
            if enemy.alive and self.is_position_lit(enemy.pos):
                enemy.take_damage(damage, "magical", "light")

    def can_artillery_strike(self):
        return (
            self.selected_hive is not None
            and self.selected_hive.is_alive
            and self.selected_hive.is_visible
            and self.money >= ARTILLERY_COST
        )

    def artillery_strike(self):
        if not self.selected_hive:
            return False
        if not self.selected_hive.is_visible or not self.selected_hive.is_alive:
            return False
        if self.money < ARTILLERY_COST:
            self.notify("Need 400 light for artillery")
            return False
        self.money -= ARTILLERY_COST
        hive = self.selected_hive
        hive.is_alive = False
        active_lanes = set(ROAD_BRANCHES[hive.road_key])
        self.enemies = [enemy for enemy in self.enemies if enemy.lane not in active_lanes]
        self.spawn_queue = [item for item in self.spawn_queue if item[1] != hive.road_key]
        self.selected_hive = None
        self.notify("Hive destroyed")
        if all(not hive.is_alive for hive in self.hives):
            self.victory = True
            self.notify("All hives destroyed")
        return True

    def get_vein_at(self, cell):
        for vein in self.veins:
            if cell in vein.cells:
                return vein
        return None

    def get_light_size(self, tower):
        level = max(1, min(4, tower.level))
        return LIGHT_SIZE_BY_LEVEL[level]

    def get_directed_light_cells(self, center_cell, direction_index, length, width):
        cells = set()
        cx, cy = center_cell
        dir_x, dir_y = DIRECTIONS[direction_index]
        side_x, side_y = -dir_y, dir_x
        half_width = max(0, width // 2)

        def add_cell(cell):
            if 0 <= cell[0] < GRID_WIDTH and 0 <= cell[1] < GRID_HEIGHT:
                cells.add(cell)

        for step in range(1, length + 1):
            base = (cx + dir_x * step, cy + dir_y * step)
            for offset in range(-half_width, half_width + 1):
                add_cell((base[0] + side_x * offset, base[1] + side_y * offset))

        return cells

    def get_beacon_light_cells(self, center_cell, size):
        cells = set()
        cx, cy = center_cell
        radius = size // 2
        edge_steps = 1 if size <= 7 else 2

        for dy in range(-radius, radius + 1):
            distance_from_edge = radius - abs(dy)
            corner_clip = max(0, edge_steps - distance_from_edge)
            half_width = radius - corner_clip
            for dx in range(-half_width, half_width + 1):
                cell = (cx + dx, cy + dy)
                if 0 <= cell[0] < GRID_WIDTH and 0 <= cell[1] < GRID_HEIGHT:
                    cells.add(cell)
        return cells

    def get_light_coverage(self, tower):
        size = self.get_light_size(tower)

        if tower.tower_type == "lamp":
            return self.get_directed_light_cells(tower.cell, tower.direction_index, size, LAMP_LIGHT_WIDTH)

        if tower.tower_type == "beacon":
            return self.get_beacon_light_cells(tower.cell, size)

        return set()

    def light_source_has_power(self, tower, current_lit):
        if tower.hp <= 0 or tower.tower_type not in LIGHT_TOWER_TYPES:
            return False
        if getattr(tower, "disabled_timer", 0) > 0:
            return False
        return tower.cell in current_lit

    def update_lighting(self):
        castle_light_zone = self.get_castle_light_zone()
        lit = set(castle_light_zone) | set(GENERATOR_CELLS)
        for tower in self.towers:
            if tower.tower_type in LIGHT_TOWER_TYPES:
                tower.is_powered = False
        changed = True
        while changed:
            changed = False
            for tower in self.towers:
                if self.light_source_has_power(tower, lit):
                    tower.is_powered = True
                    for cell in self.get_light_coverage(tower):
                        if cell not in lit:
                            lit.add(cell)
                            changed = True
        self.shadow_cells = set()
        self.lit_cells = lit
        light_tower_cells = {
            tower.cell
            for tower in self.towers
            if tower.tower_type in LIGHT_TOWER_TYPES and tower.hp > 0
        }
        self.revealed_cells = set(lit) | light_tower_cells
        if hasattr(self, "veins"):
            self.update_discovered_veins()
        if hasattr(self, "hives"):
            for hive in self.hives:
                hive.is_visible = hive.is_alive and self.is_position_lit((hive.x, hive.y))
        if hasattr(self, "bonuses"):
            for bonus in self.bonuses:
                if self.is_lit(bonus.cell):
                    bonus.is_visible = True

    def is_lit(self, cell):
        return cell in self.lit_cells or is_hq_cell(cell)

    def is_position_lit(self, pos):
        cell = cell_from_pos(pos)
        return 0 <= cell[0] < GRID_WIDTH and 0 <= cell[1] < GRID_HEIGHT and self.is_lit(cell)

    def is_target_lit(self, target):
        if isinstance(target, RaiderCamp):
            return self.is_position_lit((target.x, target.y))
        if hasattr(target, "pos"):
            return self.is_position_lit(target.pos)
        return False

    def can_place_light_building(self, cell):
        if not (0 <= cell[0] < GRID_WIDTH and 0 <= cell[1] < GRID_HEIGHT):
            return False
        if is_hq_cell(cell) or is_any_path_cell(cell):
            return False
        if any(hive.is_alive and hive.cell == cell for hive in getattr(self, "hives", [])):
            return False
        if any((not bonus.is_collected) and bonus.cell == cell for bonus in getattr(self, "bonuses", [])):
            return False
        for tower in self.towers:
            if tower.hp > 0 and tower.cell == cell:
                return False
        return self.is_lit(cell)

    def update_discovered_veins(self):
        for vein in self.veins:
            if any(cell in self.lit_cells for cell in vein.cells):
                vein.discovered = True

    def is_revealed(self, cell):
        return cell in self.revealed_cells or self.is_lit(cell)

    def can_pay_shot(self, tower):
        cost = TOWER_ORE_COST.get(tower.tower_type, 1)
        return self.ore >= cost

    def pay_shot(self, tower):
        cost = TOWER_ORE_COST.get(tower.tower_type, 1)
        if cost <= 0:
            return True
        if self.can_pay_shot(tower):
            self.ore -= cost
            return True
        return False

    def hive_spawn_multiplier(self):
        destroyed = sum(1 for hive in self.hives if not hive.is_alive)
        if destroyed >= 2:
            return 2.5
        if destroyed == 1:
            return 1.5
        return 1.0

    def enemy_type_for_wave(self, index):
        if self.wave >= 5 and index % 7 == 0:
            return "hellbrute"
        if self.wave >= DIMMER_START_WAVE and index % 6 == 4:
            return "dimmer"
        if self.wave >= 2 and index % 3 == 0:
            return "wurg"
        return "orc"

    def get_hive_by_road_key(self, road_key):
        for hive in self.hives:
            if hive.road_key == road_key:
                return hive
        return None

    def create_wave_enemy(self, enemy_type, road_key):
        hive = self.get_hive_by_road_key(road_key)
        if not hive or not hive.is_alive:
            return None
        lane = hive.primary_lane
        enemy = Enemy(enemy_type, lane)
        enemy.pos = [hive.x, hive.y]
        enemy.path_index = 0
        hp_bonus = 1 + max(0, self.wave - 1) * 0.12
        speed_bonus = 1 + max(0, self.wave - 1) * 0.035
        reward_bonus = 1 + max(0, self.wave - 1) * 0.1
        enemy.max_hp = int(enemy.max_hp * hp_bonus)
        enemy.hp = enemy.max_hp
        enemy.speed *= speed_bonus
        enemy.base_speed = enemy.speed
        enemy.reward = int(enemy.reward * reward_bonus)
        return enemy

    def tick_action_cooldowns(self):
        for action in self.action_cooldowns:
            if self.action_cooldowns[action] > 0:
                self.action_cooldowns[action] -= 1

    def can_use_action(self, action):
        return self.action_cooldowns.get(action, 0) <= 0

    def start_action_cooldown(self, action):
        if action in ACTION_COOLDOWN_FRAMES:
            self.action_cooldowns[action] = ACTION_COOLDOWN_FRAMES[action]

    def start_wave(self, early=False):
        if not self.wave_active and not self.wave_delay_active and any(hive.is_alive for hive in self.hives):
            if early and self.first_wave_started:
                self.money += 22
            
            if not self.first_wave_started:
                self.first_wave_started = True
            
            self.spawn_queue = []
            count_per_hive = max(1, int((5 + self.wave - 1) * self.hive_spawn_multiplier()))
            for hive in self.hives:
                if not hive.is_alive:
                    continue
                for index in range(count_per_hive):
                    self.spawn_queue.append((self.enemy_type_for_wave(index), hive.road_key))
            
            self.wave_active = True
            self.wave_timer = 0
            self.wave_delay_active = self.wave_delay > 0
            self.wave_delay_timer = 0
            self.wave_interval_timer = 0

    def build_tower(self, tower_type, cell):
        if tower_type not in BUILDABLE_TOWER_TYPES:
            return False
        if not self.can_use_action("build"):
            return False
        if self.money < TOWER_COST[tower_type]:
            self.notify("Need more light")
            return False
        if self.built_light_tower_count() >= self.hq.scout_limit:
            self.notify("Generator light limit reached")
            return False
        if not self.can_place_light_building(cell):
            self.notify("Build only on lit free cells")
            return False
        tower = Tower(tower_type, cell)
        if tower_type in ROTATABLE_LIGHT_TYPES:
            tower.direction_index = self.build_direction_index
        self.towers.append(tower)
        self.money -= TOWER_COST[tower_type]
        self.start_action_cooldown("build")
        self.update_lighting()
        self.notify(f"{TOWER_DISPLAY_NAMES.get(tower_type, tower_type)} built")
        return True

    def upgrade_tower(self):
        if self.selected_tower and self.selected_tower.hp > 0:
            if self.selected_tower.tower_type == "cannon" and self.selected_tower.level == 1 and not self.selected_tower.specialization:
                self.tower_specialization_pending = True
                self.tower_to_specialize = self.selected_tower
                return False
            
            cost = TOWER_UPGRADE_COST.get(self.selected_tower.tower_type)
            if cost is None:
                return False
            if self.money >= cost:
                if self.selected_tower.upgrade():
                    self.money -= cost
                    self.update_lighting()
                    return True
        return False

    def apply_tower_specialization(self, spec_type):
        if self.tower_to_specialize and self.tower_to_specialize.hp > 0:
            cost = TOWER_UPGRADE_COST.get(self.tower_to_specialize.tower_type)
            if cost is None:
                self.tower_specialization_pending = False
                self.tower_to_specialize = None
                return False
            if self.money >= cost:
                self.money -= cost
                self.tower_to_specialize.level += 1
                self.tower_to_specialize.apply_specialization(spec_type)
                self.tower_to_specialize.total_investment += cost
                self.tower_specialization_pending = False
                self.tower_to_specialize = None
                return True
        return False

    def sell_tower(self, cell):
        if not self.can_use_action("sell"):
            return False
        for t in self.towers:
            if t.cell == cell:
                if getattr(t, "fixed", False):
                    return False
                if t.tower_type == "barracks" and t.allied_unit is not None:
                    t.allied_unit.alive = False
                    t.allied_unit = None
                refund = int(t.total_investment * 0.5)
                self.money += refund
                if t == self.selected_tower:
                    self.selected_tower = None
                self.towers.remove(t)
                self.start_action_cooldown("sell")
                self.update_lighting()
                return True
        return False

    def sell_selected_tower(self):
        if self.selected_tower and self.selected_tower.hp > 0:
            return self.sell_tower(self.selected_tower.cell)
        return False

    def rotate_selected_tower(self):
        if not self.can_use_action("rotate"):
            return False
        if self.selected_tower and self.selected_tower.rotate():
            self.start_action_cooldown("rotate")
            self.update_lighting()
            return True
        if self.selected_tower_type in ROTATABLE_LIGHT_TYPES:
            self.build_direction_index = (self.build_direction_index + 1) % len(DIRECTIONS)
            self.start_action_cooldown("rotate")
            return True
        return False

    def get_tower_display_name(self, tower_type):
        return TOWER_DISPLAY_NAMES.get(tower_type, tower_type.capitalize())

    def get_left_build_buttons(self):
        buttons = []
        btn_width = SIDE_PANEL_WIDTH - scaled(40)
        btn_height = scaled(64)
        btn_gap = scaled(14)
        left_x = scaled(20)
        start_y = SCREEN_HEIGHT - scaled(40) - len(BUILDABLE_TOWER_TYPES) * btn_height - (len(BUILDABLE_TOWER_TYPES) - 1) * btn_gap
        for tower_type in BUILDABLE_TOWER_TYPES:
            buttons.append({
                "action": f"build:{tower_type}",
                "title": self.get_tower_display_name(tower_type),
                "cost": TOWER_COST[tower_type],
                "enabled": (
                    self.money >= TOWER_COST[tower_type]
                    and self.built_light_tower_count() < self.hq.scout_limit
                    and self.can_use_action("build")
                ),
                "selected": self.selected_tower_type == tower_type,
                "rect": pygame.Rect(left_x, start_y + len(buttons) * (btn_height + btn_gap), btn_width, btn_height),
            })
        return buttons

    def get_right_panel_buttons(self):
        buttons = []
        tower_cost = None
        if self.selected_tower:
            tower_cost = TOWER_UPGRADE_COST.get(self.selected_tower.tower_type)

            if self.selected_tower.tower_type == "cannon" and self.selected_tower.broken:
                buttons.append({
                    "action": "repair_cannon",
                    "title": "Repair",
                    "cost": REPAIR_CANNON_COST,
                    "enabled": self.money >= REPAIR_CANNON_COST,
                    "selected": False,
                })

            buttons.append({
                "action": "upgrade_tower",
                "title": "Upgrade",
                "cost": tower_cost,
                "enabled": (
                    tower_cost is not None
                    and self.selected_tower.level < 4
                    and self.money >= tower_cost
                ),
                "selected": False,
            })

            if self.selected_tower.tower_type in ROTATABLE_LIGHT_TYPES:
                buttons.append({
                    "action": "rotate_tower",
                    "title": "Rotate",
                    "cost": None,
                    "enabled": self.can_use_action("rotate"),
                    "selected": False,
                })

            buttons.append({
                "action": "sell_selected",
                "title": "Remove",
                "cost": None,
                "enabled": not getattr(self.selected_tower, "fixed", False) and self.can_use_action("sell"),
                "selected": False,
                "danger": True,
            })
        elif self.selected_hive:
            buttons.append({
                "action": "artillery",
                "title": "Artillery",
                "cost": ARTILLERY_COST,
                "enabled": self.can_artillery_strike(),
                "selected": self.selected_hive is not None,
            })
        else:
            gen_cost = self.hq.upgrade_cost()
            buttons.append({
                "action": "upgrade_generator",
                "title": "Generator",
                "cost": gen_cost,
                "enabled": gen_cost is not None and self.money >= gen_cost,
                "selected": False,
            })
        return buttons

    def get_right_panel_layout(self):
        right_x = SCREEN_WIDTH - SIDE_PANEL_WIDTH + scaled(20)
        btn_width = SIDE_PANEL_WIDTH - scaled(40)
        btn_height = scaled(64)
        btn_gap = scaled(14)
        buttons = self.get_right_panel_buttons()
        start_y = SCREEN_HEIGHT - scaled(40) - len(buttons) * btn_height - max(0, len(buttons) - 1) * btn_gap
        return buttons, right_x, btn_width, start_y, btn_gap, btn_height

    def run_right_panel_action(self, action):
        if action.startswith("build:"):
            tower_type = action.split(":", 1)[1]
            self.selected_tower_type = tower_type
            self.selected_tower = None
            self.selected_hive = None
        elif action == "upgrade_tower":
            self.upgrade_tower()
        elif action == "rotate_tower":
            self.rotate_selected_tower()
        elif action == "sell_selected":
            if self.sell_selected_tower():
                self.notify("Tower sold")
        elif action == "upgrade_generator":
            self.upgrade_generator()
        elif action == "repair_cannon":
            self.repair_selected_cannon()
        elif action == "artillery":
            self.artillery_strike()

    def handle_right_panel_click(self, pos):
        buttons, right_x, btn_width, start_y, btn_gap, btn_height = self.get_right_panel_layout()
        for index, button in enumerate(buttons):
            rect = pygame.Rect(right_x, start_y + index * (btn_height + btn_gap), btn_width, btn_height)
            if rect.collidepoint(pos):
                if button["enabled"]:
                    self.run_right_panel_action(button["action"])
                return True
        return False

    def handle_left_panel_click(self, pos):
        for button in self.get_left_build_buttons():
            if button["rect"].collidepoint(pos):
                if button["enabled"]:
                    self.selected_tower_type = button["action"].split(":", 1)[1]
                    self.selected_tower = None
                    self.selected_hive = None
                return True
        return False

    def draw_energy_icon(self, surface, center, size):
        x, y = center
        points = [
            (x + size * 0.05, y - size * 0.50),
            (x - size * 0.32, y + size * 0.08),
            (x - size * 0.04, y + size * 0.08),
            (x - size * 0.18, y + size * 0.50),
            (x + size * 0.34, y - size * 0.16),
            (x + size * 0.05, y - size * 0.16),
        ]
        pygame.draw.polygon(surface, GOLD, points)
        pygame.draw.polygon(surface, BLACK, points, max(1, scaled(2)))

    def draw_stat_icon(self, surface, icon_type, center, size):
        x, y = center
        if icon_type == "heart":
            pygame.draw.circle(surface, (255, 95, 105), (int(x - size * 0.22), int(y - size * 0.15)), int(size * 0.22))
            pygame.draw.circle(surface, (255, 95, 105), (int(x + size * 0.22), int(y - size * 0.15)), int(size * 0.22))
            pygame.draw.polygon(surface, (255, 95, 105), [
                (x - size * 0.45, y - size * 0.05),
                (x + size * 0.45, y - size * 0.05),
                (x, y + size * 0.50),
            ])
        elif icon_type == "energy":
            self.draw_energy_icon(surface, center, size)
        elif icon_type == "tower":
            rect = pygame.Rect(0, 0, size * 0.58, size * 0.68)
            rect.center = center
            pygame.draw.rect(surface, (130, 170, 180), rect)
            pygame.draw.rect(surface, BLACK, rect, max(1, scaled(2)))
            for i in range(3):
                tooth = pygame.Rect(rect.x + i * rect.w / 3, rect.y - size * 0.16, rect.w / 4, size * 0.18)
                pygame.draw.rect(surface, (130, 170, 180), tooth)
                pygame.draw.rect(surface, BLACK, tooth, max(1, scaled(1)))
        elif icon_type == "target":
            pygame.draw.circle(surface, (255, 95, 95), (int(x), int(y)), int(size * 0.42), max(2, scaled(4)))
            pygame.draw.circle(surface, WHITE, (int(x), int(y)), int(size * 0.24), max(2, scaled(3)))
            pygame.draw.circle(surface, (255, 95, 95), (int(x), int(y)), int(size * 0.08))
        elif icon_type == "wave":
            pygame.draw.rect(surface, (120, 170, 255), (x - size * 0.32, y - size * 0.30, size * 0.14, size * 0.62))
            pygame.draw.polygon(surface, (120, 170, 255), [
                (x - size * 0.18, y - size * 0.30),
                (x + size * 0.36, y - size * 0.16),
                (x - size * 0.18, y + size * 0.02),
            ])

    def draw_cost(self, surface, amount, pos, text_color=BLACK):
        if amount is None:
            return
        x, y = pos
        self.draw_energy_icon(surface, (x + scaled(14), y + scaled(16)), scaled(26))
        text = font_small.render(str(int(amount)), True, text_color)
        surface.blit(text, (x + scaled(34), y - scaled(2)))

    def draw_panel_button(self, surface, rect, title, cost=None, enabled=True, selected=False, danger=False):
        if selected:
            color = (86, 255, 82)
        elif danger:
            color = (255, 95, 95) if enabled else (120, 70, 70)
        elif enabled:
            color = (92, 255, 92)
        else:
            color = (190, 190, 190)
        pygame.draw.rect(surface, color, rect, border_radius=scaled(4))
        pygame.draw.rect(surface, BLACK, rect, max(1, scaled(2)), border_radius=scaled(4))
        title_text = font_small.render(title, True, BLACK)
        surface.blit(title_text, (rect.x + scaled(10), rect.y + (rect.h - title_text.get_height()) // 2))
        if cost is not None:
            cost_x = rect.right - scaled(82)
            self.draw_cost(surface, cost, (cost_x, rect.y + (rect.h - scaled(34)) // 2), BLACK)

    def draw_right_panel_buttons(self, surface):
        buttons, right_x, btn_width, start_y, btn_gap, btn_height = self.get_right_panel_layout()
        for index, button in enumerate(buttons):
            rect = pygame.Rect(right_x, start_y + index * (btn_height + btn_gap), btn_width, btn_height)
            self.draw_panel_button(
                surface,
                rect,
                button["title"],
                button.get("cost"),
                button["enabled"],
                button["selected"],
                button.get("danger", False),
            )

    def draw_left_panel(self, surface):
        x_indent = scaled(30)
        icon_x = x_indent + scaled(18)
        text_x = x_indent + scaled(62)
        y = scaled(70)
        row_gap = scaled(72)
        total_hives = len(self.hives)
        alive_hives = sum(1 for hive in self.hives if hive.is_alive)
        stats = [
            ("heart", f"{int(self.hq.hp)}/{int(self.hq.max_hp)}"),
            ("energy", str(int(self.money))),
            ("tower", f"{self.built_light_tower_count()}/{self.hq.scout_limit}"),
            ("target", f"{total_hives - alive_hives}/{total_hives}"),
            ("wave", f"G{self.hq.level}  W{self.wave}"),
        ]
        for icon_type, value in stats:
            self.draw_stat_icon(surface, icon_type, (icon_x, y + scaled(20)), scaled(44))
            rendered = font_medium.render(value, True, WHITE)
            surface.blit(rendered, (text_x, y))
            y += row_gap

        build_label = font_small.render("Build", True, WHITE)
        build_buttons = self.get_left_build_buttons()
        if build_buttons:
            label_y = build_buttons[0]["rect"].y - scaled(46)
            surface.blit(build_label, (scaled(24), label_y))
        for button in build_buttons:
            self.draw_panel_button(
                surface,
                button["rect"],
                button["title"],
                button["cost"],
                button["enabled"],
                button["selected"],
            )

    def draw_right_panel_context(self, surface):
        panel_x = SCREEN_WIDTH - SIDE_PANEL_WIDTH
        content_x = panel_x + scaled(20)
        info_y = SCREEN_HEIGHT - scaled(280)
        if self.selected_tower and self.selected_tower.hp > 0:
            name = self.get_tower_display_name(self.selected_tower.tower_type)
            name_text = font_small.render(name, True, WHITE)
            level_text = font_small.render(f"LVL {self.selected_tower.level}", True, WHITE)
            surface.blit(name_text, (content_x, info_y))
            surface.blit(level_text, (SCREEN_WIDTH - scaled(120), info_y))
        elif self.selected_hive and self.selected_hive.is_alive:
            surface.blit(font_small.render("Hive", True, WHITE), (content_x, info_y))
            hp_text = font_small.render(f"{int(self.selected_hive.hp)}/{int(self.selected_hive.max_hp)}", True, WHITE)
            surface.blit(hp_text, (content_x, info_y + scaled(42)))
        else:
            surface.blit(font_small.render(f"Generator LVL {self.hq.level}", True, WHITE), (content_x, info_y))
            hp_text = font_small.render(f"{int(self.hq.hp)}/{int(self.hq.max_hp)}", True, WHITE)
            surface.blit(hp_text, (content_x, info_y + scaled(42)))
        self.draw_right_panel_buttons(surface)

    def get_specialization_options(self):
        return [
            ("Sniper", (255, 220, 90), "sniper"),
            ("Scatter", (255, 145, 70), "scatter"),
            ("Gatling", (120, 230, 140), "gatling"),
        ]

    def draw_notification(self, surface):
        if self.notification_timer <= 0 or not self.notification_text:
            return
        text = font_medium.render(self.notification_text, True, WHITE)
        rect = text.get_rect(center=(SCREEN_WIDTH // 2, scaled(95)))
        bg = rect.inflate(scaled(34), scaled(18))
        pygame.draw.rect(surface, PANEL_BG, bg)
        pygame.draw.rect(surface, CYAN, bg, max(1, scaled(2)))
        surface.blit(text, rect)

    def draw_fog(self, surface):
        fog = pygame.Surface((FIELD_WIDTH, FIELD_HEIGHT), pygame.SRCALPHA)
        for x in range(GRID_WIDTH):
            for y in range(GRID_HEIGHT):
                if not self.is_revealed((x, y)):
                    rect = pygame.Rect(x * CELL_SIZE, y * CELL_SIZE, CELL_SIZE, CELL_SIZE)
                    pygame.draw.rect(fog, FOG_WHITE + (255,), rect)
        surface.blit(fog, (FIELD_OFFSET_X, FIELD_OFFSET_Y))

    def draw_light_outline(self, surface, cells, color=CYAN):
        if not cells:
            return
        line_width = max(2, scaled(3))
        edge_dirs = [
            ((0, -1), (0, 0), (1, 0)),
            ((1, 0), (1, 0), (1, 1)),
            ((0, 1), (0, 1), (1, 1)),
            ((-1, 0), (0, 0), (0, 1)),
        ]
        for x, y in cells:
            left = FIELD_OFFSET_X + x * CELL_SIZE
            top = FIELD_OFFSET_Y + y * CELL_SIZE
            for (dx, dy), start_mul, end_mul in edge_dirs:
                if (x + dx, y + dy) in cells:
                    continue
                start = (
                    left + start_mul[0] * CELL_SIZE,
                    top + start_mul[1] * CELL_SIZE
                )
                end = (
                    left + end_mul[0] * CELL_SIZE,
                    top + end_mul[1] * CELL_SIZE
                )
                pygame.draw.line(surface, BLACK, start, end, line_width + max(1, scaled(2)))
                pygame.draw.line(surface, color, start, end, line_width)

    def make_preview_tower(self, tower_type, cell):
        tower = Tower(tower_type, cell)
        if tower_type in ROTATABLE_LIGHT_TYPES:
            tower.direction_index = self.build_direction_index
        return tower

    def draw_light_preview(self, surface):
        mouse_pos = pygame.mouse.get_pos()
        preview_tower = None

        if (
            self.selected_tower
            and self.selected_tower.hp > 0
            and self.selected_tower.tower_type in LIGHT_TOWER_TYPES
            and getattr(self.selected_tower, "is_powered", False)
        ):
            preview_tower = self.selected_tower
        elif self.selected_tower_type in LIGHT_TOWER_TYPES and self.is_in_viewport(mouse_pos):
            cell = cell_from_pos(self.screen_to_world(mouse_pos))
            if 0 <= cell[0] < GRID_WIDTH and 0 <= cell[1] < GRID_HEIGHT and self.is_lit(cell):
                preview_tower = self.make_preview_tower(self.selected_tower_type, cell)

        if not preview_tower:
            return
        self.draw_light_outline(surface, self.get_light_coverage(preview_tower), CYAN)

    def draw_world(self, surface):
        surface.fill(GREEN)

        for x in range(GRID_WIDTH):
            for y in range(GRID_HEIGHT):
                rect = pygame.Rect(
                    FIELD_OFFSET_X + x * CELL_SIZE,
                    FIELD_OFFSET_Y + y * CELL_SIZE,
                    CELL_SIZE,
                    CELL_SIZE
                )
                if is_any_path_cell((x, y)):
                    pygame.draw.rect(surface, BROWN, rect)
                    inner = rect.inflate(-max(2, scaled(4)), -max(2, scaled(4)))
                    pygame.draw.rect(surface, (160, 90, 45), inner)
                else:
                    pygame.draw.rect(surface, GREEN, rect)

        for vein in self.veins:
            vein.draw(surface)

        for bonus in self.bonuses:
            bonus.draw(surface)

        for hive in self.hives:
            hive.draw(surface)

        for tower in self.towers:
            tower.draw(surface)

        for camp in self.raider_camps:
            camp.draw(surface)

        for au in self.allied_units:
            au.draw(surface)

        for enemy in self.enemies:
            enemy.draw(surface)

        for raider in self.raiders:
            raider.draw(surface)

        self.hq.draw(surface)
        self.draw_fog(surface)
        self.draw_light_preview(surface)

        if self.selected_tower and self.selected_tower.hp > 0:
            rect = pygame.Rect(
                self.selected_tower.x - scaled(25),
                self.selected_tower.y - scaled(25),
                scaled(50),
                scaled(50)
            )
            pygame.draw.rect(surface, YELLOW, rect, scaled(3))

        if self.selected_hive and self.selected_hive.is_alive and self.selected_hive.is_visible:
            rect = pygame.Rect(
                self.selected_hive.x - scaled(30),
                self.selected_hive.y - scaled(30),
                scaled(60),
                scaled(60)
            )
            pygame.draw.rect(surface, CYAN, rect, scaled(3))

    def blit_world(self, surface, world_surface):
        visible_w = max(1, min(FIELD_WIDTH, int(math.ceil(VIEWPORT_WIDTH / self.zoom))))
        visible_h = max(1, min(FIELD_HEIGHT, int(math.ceil(VIEWPORT_HEIGHT / self.zoom))))
        view_x = int(max(0, min(round(self.camera_x), FIELD_WIDTH - visible_w)))
        view_y = int(max(0, min(round(self.camera_y), FIELD_HEIGHT - visible_h)))
        view_rect = pygame.Rect(view_x, view_y, visible_w, visible_h)
        view = world_surface.subsurface(view_rect)
        scaled_view = pygame.transform.smoothscale(view, (VIEWPORT_WIDTH, VIEWPORT_HEIGHT))
        surface.blit(scaled_view, (VIEWPORT_X, VIEWPORT_Y))
        pygame.draw.rect(surface, BLACK, (VIEWPORT_X, VIEWPORT_Y, VIEWPORT_WIDTH, VIEWPORT_HEIGHT), max(1, scaled(2)))

    def update(self):
        if self.defeat or self.victory:
            return

        if self.notification_timer > 0:
            self.notification_timer -= 1
        self.tick_action_cooldowns()

        self.hq.update(self)
        if self.hq.hp <= 0:
            self.defeat = True
            return

        self.raider_spawn_timer += 1
        if self.raider_spawn_timer >= self.raider_spawn_cooldown:
            self.raider_spawn_timer = 0
            miners = [t for t in self.towers if t.tower_type == "miner" and t.hp > 0]
            if miners:
                target = random.choice(miners)
                min_dist = float('inf')
                nearest_corner = MAP_CORNERS[0]
                for corner in MAP_CORNERS:
                    d = math.hypot(corner[0] - target.x, corner[1] - target.y)
                    if d < min_dist:
                        min_dist = d
                        nearest_corner = corner
                for i in range(2):
                    offset_x = random.randint(-CELL_SIZE//4, CELL_SIZE//4)
                    offset_y = random.randint(-CELL_SIZE//4, CELL_SIZE//4)
                    spawn_pos = (nearest_corner[0] + offset_x, nearest_corner[1] + offset_y)
                    raider = Raider(target, spawn_pos, from_camp=False)
                    self.raiders.append(raider)

        if self.wave_delay_active:
            self.wave_delay_timer += 1
            if self.wave_delay_timer >= self.wave_delay:
                self.wave_delay_active = False
                self.wave_timer = 39

        if not self.wave_active and not self.wave_delay_active and self.first_wave_started:
            self.wave_interval_timer += 1
            if self.wave_interval_timer >= self.wave_interval and self.wave <= self.total_waves:
                self.start_wave(early=False)

        for enemy in self.enemies:
            if enemy.alive:
                enemy.apply_effects()
        for enemy in self.enemies:
            if enemy.slow_timer > 0:
                enemy.slow_timer -= 1
                if enemy.slow_timer == 0:
                    enemy.speed = enemy.base_speed

        if self.wave_active and not self.wave_delay_active and self.spawn_queue:
            self.wave_timer += 1
            if self.wave_timer >= 40:
                e_type, road_key = self.spawn_queue.pop(0)
                enemy = self.create_wave_enemy(e_type, road_key)
                if enemy:
                    self.enemies.append(enemy)
                self.wave_timer = 0

        for enemy in self.enemies[:]:
            if isinstance(enemy, SatanBoss):
                enemy.spawn_minions(self)
                enemy.move(self.towers, self.hq, self.enemies, self.allied_units, self.raider_camps, self)
            else:
                enemy.move(self.towers, self.hq, self.enemies, self.allied_units, self.raider_camps, self)
            if not enemy.alive:
                if isinstance(enemy, Enemy) and enemy.can_rise and not enemy.risen:
                    enemy.risen = True
                    enemy.hp = enemy.max_hp // 2
                    enemy.alive = True
                    enemy.speed *= 0.8
                else:
                    if enemy.hp <= 0:
                        self.money += enemy.reward
                    self.enemies.remove(enemy)
                    continue

        for raider in self.raiders[:]:
            if raider.alive:
                raider.apply_effects()
                if raider.slow_timer > 0:
                    raider.slow_timer -= 1
                    if raider.slow_timer == 0:
                        raider.speed = raider.base_speed
                raider.move(self.towers, self.hq, self.enemies, self.allied_units, self.raider_camps)
                if not raider.alive:
                    if raider.hp <= 0:
                        self.money += raider.reward
                    self.raiders.remove(raider)
                    continue
            else:
                if raider in self.raiders:
                    self.raiders.remove(raider)

        for camp in self.raider_camps[:]:
            if camp.hp > 0:
                camp.update(self)
            else:
                if camp in self.raider_camps:
                    self.raider_camps.remove(camp)

        for au in self.allied_units[:]:
            if au.alive:
                au.update(self.enemies)
            else:
                if au in self.allied_units:
                    self.allied_units.remove(au)

        self.update_dimmers()
        self.update_lighting()
        self.apply_light_damage()

        for tower in self.towers:
            tower.update(self.enemies, self, self.raider_camps, self.raiders)

        if self.wave_active and not self.spawn_queue and len(self.enemies) == 0:
            self.wave_active = False
            self.wave += 1
            self.wave_interval_timer = 0
            if all(not hive.is_alive for hive in self.hives):
                self.victory = True

    def draw_ui(self, surface):
        pygame.draw.rect(surface, PANEL_BG, (0, 0, SIDE_PANEL_WIDTH, SCREEN_HEIGHT))
        pygame.draw.rect(surface, PANEL_BG, (SCREEN_WIDTH - SIDE_PANEL_WIDTH, 0, SIDE_PANEL_WIDTH, SCREEN_HEIGHT))
        self.draw_left_panel(surface)
        self.draw_right_panel_context(surface)

        if self.tower_specialization_pending:
            overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
            overlay.fill((0, 0, 0, 150))
            surface.blit(overlay, (0, 0))
            
            menu_w = scaled(400)
            menu_h = scaled(300)
            menu_x = (SCREEN_WIDTH - menu_w) // 2
            menu_y = (SCREEN_HEIGHT - menu_h) // 2
            
            pygame.draw.rect(surface, PANEL_BG, (menu_x, menu_y, menu_w, menu_h))
            pygame.draw.rect(surface, GOLD, (menu_x, menu_y, menu_w, menu_h), scaled(3))
            
            title = font_medium.render("Choose Cannon Specialization", True, WHITE)
            surface.blit(title, (menu_x + (menu_w - title.get_width()) // 2, menu_y + scaled(20)))
            
            specs = self.get_specialization_options()
            
            btn_w = scaled(160)
            btn_h = scaled(60)
            gap = scaled(20)
            start_x = menu_x + (menu_w - 2 * btn_w - gap) // 2
            start_y_menu = menu_y + scaled(100)
            
            for i, (name, color, spec) in enumerate(specs):
                row = i // 2
                col = i % 2
                bx = start_x + col * (btn_w + gap)
                by = start_y_menu + row * (btn_h + gap)
                
                rect = pygame.Rect(bx, by, btn_w, btn_h)
                pygame.draw.rect(surface, color, rect)
                pygame.draw.rect(surface, BLACK, rect, scaled(2))
                
                txt = font_small.render(name, True, BLACK)
                surface.blit(txt, (bx + (btn_w - txt.get_width()) // 2, by + (btn_h - txt.get_height()) // 2))

        if self.victory:
            txt = font_large.render("VICTORY! All hives destroyed.", True, GOLD)
            txt_rect = txt.get_rect(center=(SCREEN_WIDTH//2, SCREEN_HEIGHT//2))
            surface.blit(txt, txt_rect)
        elif self.defeat:
            txt = font_large.render("DEFEAT", True, RED)
            txt_rect = txt.get_rect(center=(SCREEN_WIDTH//2, SCREEN_HEIGHT//2))
            surface.blit(txt, txt_rect)

        self.draw_notification(surface)


game = Game()
world_surface = pygame.Surface((FIELD_WIDTH, FIELD_HEIGHT))
running = True

while running:
    screen.fill(BLACK)

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                running = False

        if event.type == pygame.MOUSEWHEEL:
            pos = pygame.mouse.get_pos()
            if game.is_in_viewport(pos):
                game.zoom_at(pos, 1.12 ** event.y)

        if event.type == pygame.MOUSEBUTTONUP:
            if event.button == 2:
                game.dragging_camera = False
                game.last_drag_pos = None

        if event.type == pygame.MOUSEMOTION and game.dragging_camera:
            game.pan_camera(-event.rel[0] * 1.8 / game.zoom, -event.rel[1] * 1.8 / game.zoom)

        if event.type == pygame.MOUSEBUTTONDOWN:
            pos = pygame.mouse.get_pos()
            if event.button == 2 and game.is_in_viewport(pos):
                game.dragging_camera = True
                game.last_drag_pos = pos
                continue
            if event.button in (4, 5) and game.is_in_viewport(pos):
                game.zoom_at(pos, 1.12 if event.button == 4 else 1 / 1.12)
                continue
            if event.button == 3:
                if game.is_in_viewport(pos):
                    cell = cell_from_pos(game.screen_to_world(pos))
                    if 0 <= cell[0] < GRID_WIDTH and 0 <= cell[1] < GRID_HEIGHT:
                        if game.sell_tower(cell):
                            game.notify("Tower sold")
                        else:
                            game.selected_tower_type = None
                            game.selected_tower = None
                            game.selected_hive = None
                else:
                    game.selected_tower_type = None
                    game.selected_tower = None
                    game.selected_hive = None
                continue
            if event.button != 1:
                continue
            
            if game.tower_specialization_pending:
                menu_w = scaled(400)
                menu_h = scaled(300)
                menu_x = (SCREEN_WIDTH - menu_w) // 2
                menu_y = (SCREEN_HEIGHT - menu_h) // 2
                
                specs = game.get_specialization_options()
                btn_w = scaled(160)
                btn_h = scaled(60)
                gap = scaled(20)
                start_x = menu_x + (menu_w - 2 * btn_w - gap) // 2
                start_y_menu = menu_y + scaled(100)
                
                for i, (_, _, spec) in enumerate(specs):
                    row = i // 2
                    col = i % 2
                    bx = start_x + col * (btn_w + gap)
                    by = start_y_menu + row * (btn_h + gap)
                    
                    rect = pygame.Rect(bx, by, btn_w, btn_h)
                    if rect.collidepoint(pos):
                        game.apply_tower_specialization(spec)
                        break
                continue
            
            if pos[0] >= SCREEN_WIDTH - SIDE_PANEL_WIDTH:
                game.handle_right_panel_click(pos)
            elif pos[0] < SIDE_PANEL_WIDTH:
                game.handle_left_panel_click(pos)
            elif game.is_in_viewport(pos):
                cell = cell_from_pos(game.screen_to_world(pos))
                if 0 <= cell[0] < GRID_WIDTH and 0 <= cell[1] < GRID_HEIGHT:
                    handled = False
                    for bonus in game.bonuses:
                        if bonus.contains_cell(cell) and game.is_lit(bonus.cell):
                            game.collect_bonus(bonus)
                            handled = True
                            break
                    if handled:
                        continue

                    for hive in game.hives:
                        if hive.contains_cell(cell):
                            game.selected_hive = hive
                            game.selected_tower = None
                            game.selected_tower_type = None
                            handled = True
                            break
                    if handled:
                        continue

                    for t in game.towers:
                        if t.cell == cell and t.hp > 0:
                            game.select_or_toggle_tower(t)
                            break
                    else:
                        if game.selected_tower_type:
                            game.build_tower(game.selected_tower_type, cell)
                        else:
                            game.selected_tower = None
                            game.selected_hive = None

        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_u:
                game.upgrade_tower()
            if event.key == pygame.K_r:
                game.rotate_selected_tower()
            if event.key == pygame.K_s and pygame.key.get_mods() & pygame.KMOD_SHIFT:
                game.selected_tower_type = None
                game.selected_tower = None
                game.selected_hive = None
            if event.key == pygame.K_SPACE:
                can_start = not game.wave_active and not game.wave_delay_active and game.wave <= game.total_waves and not game.victory and not game.defeat
                if can_start:
                    game.start_wave(early=True)

    game.update_camera()
    game.update()

    game.draw_world(world_surface)
    game.blit_world(screen, world_surface)
    game.draw_ui(screen)

    pygame.display.flip()
    clock.tick(60)

pygame.quit()
sys.exit()
