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
FIELD_OFFSET_X = SIDE_PANEL_WIDTH
FIELD_OFFSET_Y = 0
FIELD_WIDTH = SCREEN_WIDTH - 2 * SIDE_PANEL_WIDTH
FIELD_HEIGHT = SCREEN_HEIGHT

GRID_WIDTH, GRID_HEIGHT = 20, 20
CELL_SIZE = min(FIELD_WIDTH // GRID_WIDTH, FIELD_HEIGHT // GRID_HEIGHT)
FIELD_OFFSET_Y = (SCREEN_HEIGHT - CELL_SIZE * GRID_HEIGHT) // 2
FIELD_WIDTH = CELL_SIZE * GRID_WIDTH
FIELD_HEIGHT = CELL_SIZE * GRID_HEIGHT

TOWER_COST = {
    "archer": 100, "mage": 120, "cannon": 150,
    "miner": 40, "barracks": 200
}
TOWER_UPGRADE_COST = {
    "archer": 150, "mage": 180, "cannon": 200,
    "miner": 120, "barracks": 250
}

STARTING_MONEY = 400
STARTING_ORE = 50

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

MELEE = "mile"
RANGE = "range"

MAX_RAIDERS_PER_MINER = 2

HQ_CELLS = {(9,9), (9,10), (10,9), (10,10)}
HQ_CENTER_X = FIELD_OFFSET_X + 9.5 * CELL_SIZE
HQ_CENTER_Y = FIELD_OFFSET_Y + 9.5 * CELL_SIZE

HQ_HITBOX_X1 = FIELD_OFFSET_X + 9 * CELL_SIZE
HQ_HITBOX_Y1 = FIELD_OFFSET_Y + 9 * CELL_SIZE
HQ_HITBOX_X2 = HQ_HITBOX_X1 + 2 * CELL_SIZE
HQ_HITBOX_Y2 = HQ_HITBOX_Y1 + 2 * CELL_SIZE

LANES = {
    "left": [(0,10), (2,10), (2,8), (4,8), (4,10), (6,10), (6,12), (8,12), (8,10), (9,10)],
    "right": [(19,10), (17,10), (17,12), (15,12), (15,10), (13,10), (13,8), (11,8), (11,10), (10,10)],
    "top": [(10,0), (10,2), (12,2), (12,4), (10,4), (10,6), (8,6), (8,8), (10,8), (10,9)],
    "bottom": [(10,19), (10,17), (12,17), (12,15), (10,15), (10,13), (8,13), (8,11), (10,11), (10,10)]
}

ALL_PATH_CELLS = set()
for lane_cells in LANES.values():
    for i in range(len(lane_cells) - 1):
        x1, y1 = lane_cells[i]
        x2, y2 = lane_cells[i+1]
        if x1 == x2:
            step = 1 if y2 > y1 else -1
            for y in range(y1, y2 + step, step):
                ALL_PATH_CELLS.add((x1, y))
        elif y1 == y2:
            step = 1 if x2 > x1 else -1
            for x in range(x1, x2 + step, step):
                ALL_PATH_CELLS.add((x, y1))
ALL_PATH_CELLS.update(HQ_CELLS)

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
        self.max_hp = 51
        self.hp = self.max_hp
        self.damage = 20
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
        self.reward = 15
        self.attacking_tower = None
        self.burn_timer = 0
        self.poison_timer = 0
        self.slow_timer = 0
        self.phys_armor = 0.1
        self.mag_armor = 0.1
        self.evade = 0.15
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
        if not self.alive:
            return
        pygame.draw.rect(surface, self.color, (int(self.pos[0] - scaled(12)), int(self.pos[1] - scaled(12)), scaled(24), scaled(24)))
        pygame.draw.circle(surface, WHITE, (int(self.pos[0]), int(self.pos[1] - scaled(4))), scaled(6))
        pygame.draw.circle(surface, BLACK, (int(self.pos[0] - scaled(2)), int(self.pos[1] - scaled(5))), scaled(2))
        pygame.draw.circle(surface, BLACK, (int(self.pos[0] + scaled(2)), int(self.pos[1] - scaled(5))), scaled(2))
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
            "orc": {"hp": 100, "phys": 0, "mag": 0, "speed": scaled(1.0), "rise": False, "evade": 0.1,
                    "attack": MELEE, "color": GREEN, "atk_dmg": 10, "atk_range": base_range, "atk_cd": 60},
            "skeleton": {"hp": 50, "phys": 0.1, "mag": 0, "speed": scaled(0.77), "rise": True, "evade": 0,
                         "attack": MELEE, "color": WHITE, "atk_dmg": 8, "atk_range": base_range, "atk_cd": 50},
            "necromancer": {"hp": 400, "phys": 0, "mag": 0.8, "speed": scaled(0.63), "rise": False, "evade": 0,
                            "attack": RANGE, "color": PURPLE, "atk_dmg": 25, "atk_range": scaled(120), "atk_cd": 70},
            "ogr": {"hp": 800, "phys": 0.5, "mag": 0, "speed": scaled(0.47), "rise": False, "evade": 0,
                    "attack": MELEE, "color": ORANGE, "atk_dmg": 40, "atk_range": scaled(45), "atk_cd": 80},
            "dark_knight": {"hp": 350, "phys": 0.9, "mag": 0, "speed": scaled(0.7), "rise": False, "evade": 0,
                            "attack": MELEE, "color": DARK_RED, "atk_dmg": 30, "atk_range": base_range, "atk_cd": 55},
            "wurg": {"hp": 150, "phys": 0.1, "mag": 0.4, "speed": scaled(1.4), "rise": False, "evade": 0.3,
                     "attack": MELEE, "color": YELLOW, "atk_dmg": 15, "atk_range": base_range, "atk_cd": 45},
            "chaos_spawn": {"hp": 220, "phys": 0, "mag": 0.2, "speed": scaled(1.13), "rise": False, "evade": 0.7,
                            "attack": MELEE, "color": RED, "atk_dmg": 20, "atk_range": base_range, "atk_cd": 40},
            "hellbrute": {"hp": 1000, "phys": 0.9, "mag": 0.3, "speed": scaled(0.27), "rise": False, "evade": 0,
                          "attack": MELEE, "color": (200, 0, 200), "atk_dmg": 50, "atk_range": scaled(50), "atk_cd": 100}
        }
        s = stats[enemy_type]
        self.max_hp = s["hp"]
        self.hp = self.max_hp
        self.phys_armor = s["phys"]
        self.mag_armor = s["mag"]
        raw_speed = max(1, s["speed"])
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

        self.path = get_path_pixels(lane)
        self.path_index = 0
        self.pos = list(self.path[0])
        self.alive = True
        self.risen = False
        self.attacking_tower = None

        self.burn_timer = 0
        self.poison_timer = 0
        self.slow_timer = 0

        rewards = {"orc": 10, "skeleton": 5, "necromancer": 50, "ogr": 40, "dark_knight": 30,
                   "wurg": 20, "chaos_spawn": 25, "hellbrute": 60}
        self.reward = rewards[enemy_type]

    def move(self, towers, hq, enemies, allied_units, raider_camps):
        if not self.alive:
            return
        if self.attack_cooldown > 0:
            self.attack_cooldown -= 1

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
                        return
                    else:
                        self.attacking_tower = None
            else:
                self.attacking_tower = None

        targets = list(towers)
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
        else:
            self.pos[0] += (dx / dist) * self.speed
            self.pos[1] += (dy / dist) * self.speed

    def attack_tower(self, target):
        try:
            target.take_damage(self.attack_damage, "physical")
        except TypeError:
            target.take_damage(self.attack_damage)
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
        pygame.draw.rect(surface, YELLOW, (int(self.pos[0] - bar_width/2), int(self.pos[1] - scaled(25)), green_width, scaled(5)))


class SatanBoss(Enemy):
    def __init__(self, lane):
        super().__init__("hellbrute", lane)
        self.enemy_type = "satan"
        self.max_hp = 8000
        self.hp = self.max_hp
        raw_speed = max(1, scaled(15))
        self.speed = float(raw_speed)
        self.base_speed = float(raw_speed)
        self.phys_armor = 0.5
        self.mag_armor = 0.5
        self.evade = 0
        self.attack_range = scaled(60)
        self.attack_damage = 80
        self.attack_cooldown_max = 60
        self.attack_cooldown = 0
        self.color = (255, 0, 0)
        self.reward = 500
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
            cooldown = 300 if self.phase == 2 else 180
            if self.minion_timer >= cooldown:
                self.minion_timer = 0
                count = 2 if self.phase == 2 else 3
                for _ in range(count):
                    offset_x = random.randint(-CELL_SIZE, CELL_SIZE)
                    offset_y = random.randint(-CELL_SIZE, CELL_SIZE)
                    spawn_pos = (self.pos[0] + offset_x, self.pos[1] + offset_y)
                    lane = random.choice(list(LANES.keys()))
                    minion = Enemy("skeleton", lane)
                    minion.pos = list(spawn_pos)
                    minion.hp = minion.max_hp // 2
                    game.enemies.append(minion)

    def move(self, towers, hq, enemies, allied_units, raider_camps):
        if not self.alive:
            return
        if self.attack_cooldown > 0:
            self.attack_cooldown -= 1
        
        self.check_phase()
        
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
        
        pygame.draw.circle(surface, color, (int(self.pos[0]), int(self.pos[1])), rad)
        
        phase_txt = font_small.render(f"P{self.phase}", True, WHITE)
        surface.blit(phase_txt, (int(self.pos[0] - phase_txt.get_width()//2), int(self.pos[1] - rad - scaled(40))))
        
        bar_width = scaled(60)
        bar_y = int(self.pos[1] - rad - scaled(25))
        pygame.draw.rect(surface, RED, (int(self.pos[0] - bar_width/2), bar_y, bar_width, scaled(8)))
        green_width = bar_width * (self.hp / self.max_hp)
        pygame.draw.rect(surface, YELLOW, (int(self.pos[0] - bar_width/2), bar_y, int(green_width), scaled(8)))


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
            "miner": {"damage": 10, "range": scaled(100), "cooldown": 40, "color": ORE_COLOR, "proj_color": ORE_COLOR, "hp": 150, "dmg_type": "physical"},
            "barracks": {"damage": 0, "range": 0, "cooldown": 0, "color": (100, 60, 30), "proj_color": (100, 60, 30), "hp": 300, "dmg_type": "physical"}
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
        self.total_investment = TOWER_COST.get(tower_type, 0)
        self.specialization = None

        if tower_type == "miner":
            self.mining = True
            self.stored_ore = 0
            self.attack_mode = False
            self.mining_cooldown = 0
        elif tower_type == "barracks":
            self.spawn_point = find_nearest_path_cell(cell)
            self.allied_unit = None
            self.respawn_timer = 0
            self.respawn_cooldown = 300

    def upgrade(self):
        if self.level < 3:
            cost = TOWER_UPGRADE_COST[self.tower_type]
            self.level += 1
            if self.tower_type == "miner":
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

    def apply_specialization(self, spec_type):
        self.specialization = spec_type
        if spec_type == "ice":
            self.color = CYAN
            self.proj_color = (200, 230, 255)
            self.damage = 8
            self.range = scaled(110)
            self.cooldown_max = 25
            self.damage_type = "magical"
        elif spec_type == "fire":
            self.color = (220, 50, 0)
            self.proj_color = (255, 100, 0)
            self.damage = 22
            self.range = scaled(120)
            self.cooldown_max = 38
            self.damage_type = "magical"
        elif spec_type == "poison":
            self.color = (0, 150, 0)
            self.proj_color = (100, 255, 100)
            self.damage = 15
            self.range = scaled(140)
            self.cooldown_max = 30
            self.damage_type = "magical"
        elif spec_type == "lightning":
            self.color = GOLD
            self.proj_color = (255, 255, 0)
            self.damage = 35
            self.range = scaled(150)
            self.cooldown_max = 60
            self.damage_type = "magical"

    def take_damage(self, damage):
        self.hp -= damage
        if self.hp <= 0:
            self.hp = 0

    def find_target(self, enemies, raider_camps, raiders):
        if self.tower_type == "barracks" or self.damage == 0:
            return None
        in_range = []
        for e in enemies:
            if e.alive and math.hypot(e.pos[0] - self.x, e.pos[1] - self.y) <= self.range:
                in_range.append(e)
        for raider in raiders:
            if raider.alive and math.hypot(raider.pos[0] - self.x, raider.pos[1] - self.y) <= self.range:
                in_range.append(raider)
        for camp in raider_camps:
            if camp.hp > 0 and math.hypot(camp.x - self.x, camp.y - self.y) <= self.range:
                in_range.append(camp)
        if not in_range:
            return None
        enemies_in_range = [e for e in in_range if hasattr(e, 'path_index')]
        if enemies_in_range:
            return max(enemies_in_range, key=lambda e: e.path_index)
        return in_range[0]

    def update(self, enemies, game, raider_camps, raiders):
        if self.hp <= 0:
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
                    target = self.find_target(enemies, raider_camps, raiders)
                    if target:
                        self.projectiles.append([target, list((self.x, self.y))])
                        self.cooldown = self.cooldown_max
        else:
            if game.ore <= 0:
                return
            if self.cooldown > 0:
                self.cooldown -= 1
            if self.cooldown == 0:
                target = self.find_target(enemies, raider_camps, raiders)
                if target:
                    game.ore -= 1
                    self.projectiles.append([target, list((self.x, self.y))])
                    self.cooldown = self.cooldown_max

        for proj in self.projectiles[:]:
            target, pos = proj
            if not target.alive if hasattr(target, 'alive') else target.hp <= 0:
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
                    target.take_damage(self.damage, self.damage_type)
                
                if self.tower_type == "cannon" and not isinstance(target, RaiderCamp):
                    splash_radius = scaled(60)
                    splash_damage = int(self.damage * 0.5)
                    for e in enemies:
                        if e is not target and e.alive:
                            d = math.hypot(e.pos[0] - target.pos[0], e.pos[1] - target.pos[1])
                            if d <= splash_radius:
                                e.take_damage(splash_damage, self.damage_type)
                    for r in raiders:
                        if r is not target and r.alive:
                            d = math.hypot(r.pos[0] - target.pos[0], r.pos[1] - target.pos[1])
                            if d <= splash_radius:
                                r.take_damage(splash_damage, self.damage_type)
                
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
                        e.take_damage(int(self.damage * 0.5), self.damage_type)
                self.projectiles.remove(proj)
            else:
                pos[0] += (dx / dist) * speed
                pos[1] += (dy / dist) * speed

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
                pygame.draw.circle(leash_surf, (70, 130, 230, 40), (leash_r, leash_r), leash_r)
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
            pygame.draw.rect(surface, self.color, (self.x - rect_size//2, self.y - rect_size//2, rect_size, rect_size))
            if self.attack_mode:
                pygame.draw.line(surface, RED, (self.x, self.y), (self.x + scaled(20), self.y - scaled(20)), scaled(3))
        elif self.tower_type == "mage":
            rect_size = scaled(36)
            pygame.draw.rect(surface, self.color, (self.x - rect_size//2, self.y - rect_size//2, rect_size, rect_size))
            if self.specialization:
                spec_colors = {"ice": CYAN, "fire": (255, 100, 0), "poison": (100, 255, 100), "lightning": GOLD}
                spec_color = spec_colors.get(self.specialization, WHITE)
                pygame.draw.circle(surface, spec_color, (self.x, self.y - rect_size//2 - scaled(8)), scaled(6))
        else:
            if self.tower_type == "archer":
                pygame.draw.circle(surface, self.color, (self.x, self.y), scaled(20))
            elif self.tower_type == "cannon":
                rect_size = scaled(44)
                pygame.draw.rect(surface, self.color, (self.x - rect_size//2, self.y - rect_size//2, rect_size, rect_size))
                pygame.draw.circle(surface, RED, (self.x, self.y), scaled(8))

        for proj in self.projectiles:
            pygame.draw.circle(surface, self.proj_color, (int(proj[1][0]), int(proj[1][1])), scaled(5))

        bar_width = scaled(40)
        bar_y = self.y - scaled(40)
        pygame.draw.rect(surface, RED, (self.x - bar_width//2, bar_y, bar_width, scaled(6)))
        hp_ratio = self.hp / self.max_hp
        pygame.draw.rect(surface, YELLOW, (self.x - bar_width//2, bar_y, int(bar_width * hp_ratio), scaled(6)))


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
            pygame.draw.circle(surface, ORE_COLOR, (x, y), scaled(10))
        cx, cy = self.get_center()
        txt = font_small.render(str(self.amount), True, BLACK)
        surface.blit(txt, (cx - txt.get_width()//2, cy - txt.get_height()//2))


class Headquarters:
    def __init__(self):
        self.hp = 1000
        self.max_hp = 1000
        self.ore_generation_timer = 0
        self.attack_range = scaled(220)
        self.attack_damage = 30
        self.attack_cooldown_max = 60
        self.attack_cooldown = 0
        self.projectiles = []

    def take_damage(self, damage, damage_type=None):
        self.hp -= damage
        if self.hp < 0:
            self.hp = 0

    def find_targets(self, enemies, raiders, raider_camps):
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
        if game.first_wave_started:
            self.ore_generation_timer += 1
            if self.ore_generation_timer >= 180:
                self.ore_generation_timer = 0
                game.ore += 1
        
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
            FIELD_OFFSET_X + 9 * CELL_SIZE,
            FIELD_OFFSET_Y + 9 * CELL_SIZE,
            2 * CELL_SIZE,
            2 * CELL_SIZE
        )
        pygame.draw.rect(surface, GOLD, rect)
        pygame.draw.rect(surface, BLACK, rect, scaled(4))
        pygame.draw.rect(surface, RED, rect, scaled(3))
        center = (int(HQ_CENTER_X), int(HQ_CENTER_Y))
        pygame.draw.circle(surface, RED, center, scaled(15))
        pygame.draw.circle(surface, BLACK, center, scaled(15), scaled(2))
        
        for proj in self.projectiles:
            _, pos = proj
            pygame.draw.circle(surface, GOLD, (int(pos[0]), int(pos[1])), scaled(7))
            pygame.draw.circle(surface, WHITE, (int(pos[0]), int(pos[1])), scaled(4))
        
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
        self.towers = []
        self.allied_units = []
        self.raiders = []
        self.raider_camps = []
        self.veins = []
        self.selected_tower_type = None
        self.selected_tower = None
        self.victory = False
        self.defeat = False
        self.hq = Headquarters()
        self.radar_mode = False
        
        self.first_wave_started = False
        
        self.mage_upgrade_pending = False
        self.mage_to_upgrade = None
        
        self.radar_animation_active = False
        self.radar_animation_center = None
        self.radar_animation_timer = 0
        self.radar_animation_duration = 60
        self.radar_animation_radius = 0
        self.radar_animation_max_radius = 3 * CELL_SIZE
        
        self.raider_spawn_timer = 0
        self.raider_spawn_cooldown = 1200
        
        self.wave_interval = 7200
        self.wave_interval_timer = 0
        self.wave_delay = 420
        self.wave_delay_timer = 0
        self.wave_delay_active = False
        self.waves_completed = 0
        
        self.total_waves = 4

        self.waves = self.generate_waves()
        self.spawn_queue = []
        self.generate_veins()

    def generate_veins(self):
        all_vein_cells = set()
        for _ in range(10):
            size = random.choices([1,2,3,4], weights=[40,30,20,10])[0]
            attempts = 0
            while attempts < 100:
                base = (random.randint(1, GRID_WIDTH-2), random.randint(1, GRID_HEIGHT-2))
                if is_any_path_cell(base) or is_hq_cell(base):
                    attempts += 1
                    continue
                too_close = False
                for vc in all_vein_cells:
                    if abs(base[0]-vc[0]) < 2 and abs(base[1]-vc[1]) < 2:
                        too_close = True
                        break
                if too_close:
                    attempts += 1
                    continue
                vein_cells = [base]
                current = base
                for _ in range(size-1):
                    neighbors = []
                    for dx, dy in [(1,0),(-1,0),(0,1),(0,-1)]:
                        nx, ny = current[0]+dx, current[1]+dy
                        if 0 <= nx < GRID_WIDTH and 0 <= ny < GRID_HEIGHT:
                            if (nx,ny) not in vein_cells and not is_any_path_cell((nx,ny)) and not is_hq_cell((nx,ny)):
                                ok = True
                                for vc in all_vein_cells:
                                    if abs(nx-vc[0]) < 2 and abs(ny-vc[1]) < 2:
                                        ok = False
                                        break
                                if ok:
                                    neighbors.append((nx,ny))
                    if not neighbors:
                        break
                    chosen = random.choice(neighbors)
                    vein_cells.append(chosen)
                    current = chosen
                if len(vein_cells) == size:
                    vein = OreVein(vein_cells)
                    self.veins.append(vein)
                    for cell in vein_cells:
                        all_vein_cells.add(cell)
                    break
                attempts += 1

    def get_vein_at(self, cell):
        for vein in self.veins:
            if cell in vein.cells:
                return vein
        return None

    def reveal_area(self, center_cell):
        cost = 30
        if self.money >= cost and not self.radar_animation_active:
            self.money -= cost
            center_x = FIELD_OFFSET_X + center_cell[0] * CELL_SIZE + CELL_SIZE // 2
            center_y = FIELD_OFFSET_Y + center_cell[1] * CELL_SIZE + CELL_SIZE // 2
            self.radar_animation_center = (center_x, center_y)
            self.radar_animation_active = True
            self.radar_animation_timer = 0
            self.radar_animation_radius = 0
            self.radar_mode = False

    def update_radar_animation(self):
        if not self.radar_animation_active:
            return
        
        self.radar_animation_timer += 1
        progress = self.radar_animation_timer / self.radar_animation_duration
        self.radar_animation_radius = int(self.radar_animation_max_radius * progress)
        
        if self.radar_animation_center:
            cx, cy = self.radar_animation_center
            center_cell = ((cx - FIELD_OFFSET_X) // CELL_SIZE, (cy - FIELD_OFFSET_Y) // CELL_SIZE)
            
            for dx in range(-1, 2):
                for dy in range(-1, 2):
                    cell_x = center_cell[0] + dx
                    cell_y = center_cell[1] + dy
                    if 0 <= cell_x < GRID_WIDTH and 0 <= cell_y < GRID_HEIGHT:
                        cell_px = FIELD_OFFSET_X + cell_x * CELL_SIZE + CELL_SIZE // 2
                        cell_py = FIELD_OFFSET_Y + cell_y * CELL_SIZE + CELL_SIZE // 2
                        dist = math.hypot(cell_px - cx, cell_py - cy)
                        if dist <= self.radar_animation_radius:
                            vein = self.get_vein_at((cell_x, cell_y))
                            if vein:
                                vein.discovered = True
        
        if self.radar_animation_timer >= self.radar_animation_duration:
            self.radar_animation_active = False
            self.radar_animation_center = None

    def draw_radar_animation(self, surface):
        if not self.radar_animation_active or not self.radar_animation_center:
            return
        
        cx, cy = self.radar_animation_center
        
        if self.radar_animation_radius > 0:
            alpha = max(0, 255 - int(255 * (self.radar_animation_timer / self.radar_animation_duration)))
            radar_surf = pygame.Surface((self.radar_animation_radius * 2, self.radar_animation_radius * 2), pygame.SRCALPHA)
            pygame.draw.circle(radar_surf, (0, 255, 255, alpha), 
                             (self.radar_animation_radius, self.radar_animation_radius), 
                             self.radar_animation_radius, max(2, scaled(3)))
            surface.blit(radar_surf, (cx - self.radar_animation_radius, cy - self.radar_animation_radius))
            
            fill_surf = pygame.Surface((self.radar_animation_radius * 2, self.radar_animation_radius * 2), pygame.SRCALPHA)
            fill_alpha = max(0, 80 - int(80 * (self.radar_animation_timer / self.radar_animation_duration)))
            pygame.draw.circle(fill_surf, (0, 255, 255, fill_alpha), 
                             (self.radar_animation_radius, self.radar_animation_radius), 
                             self.radar_animation_radius)
            surface.blit(fill_surf, (cx - self.radar_animation_radius, cy - self.radar_animation_radius))
        
        if self.radar_animation_timer % 10 < 5:
            pygame.draw.circle(surface, CYAN, (cx, cy), max(4, scaled(6)))

    def generate_waves(self):
        waves = [
            [("orc", 15), ("skeleton", 10), ("wurg", 5)],
            [("orc", 20), ("dark_knight", 5), ("necromancer", 3), ("ogr", 3)],
            [("hellbrute", 2), ("dark_knight", 8), ("chaos_spawn", 10), ("wurg", 10)],
        ]
        return waves

    def start_wave(self, early=False):
        if self.wave <= self.total_waves and not self.wave_active and not self.wave_delay_active:
            if early and self.first_wave_started:
                self.ore += 15
                self.money += 30
            
            if not self.first_wave_started:
                self.first_wave_started = True
            
            if self.wave == 4:
                lane = random.choice(list(LANES.keys()))
                self.spawn_queue = [("satan", lane)]
            else:
                self.spawn_queue = []
                for enemy_type, count in self.waves[self.wave - 1]:
                    for _ in range(count):
                        lane = random.choice(list(LANES.keys()))
                        self.spawn_queue.append((enemy_type, lane))
                random.shuffle(self.spawn_queue)
            
            self.wave_active = True
            self.wave_timer = 0
            self.wave_delay_active = True
            self.wave_delay_timer = 0
            self.wave_interval_timer = 0

    def build_tower(self, tower_type, cell):
        if self.money < TOWER_COST[tower_type]:
            return False
        for t in self.towers:
            if t.cell == cell:
                return False
        if is_hq_cell(cell):
            return False
        if tower_type == "miner":
            vein = self.get_vein_at(cell)
            if not vein or not vein.discovered:
                return False
        elif tower_type == "barracks":
            if is_any_path_cell(cell):
                return False
            if self.get_vein_at(cell) is not None:
                return False
            has_nearby_path = False
            for dx in range(-3, 4):
                for dy in range(-3, 4):
                    if is_any_path_cell((cell[0]+dx, cell[1]+dy)):
                        has_nearby_path = True
                        break
                if has_nearby_path:
                    break
            if not has_nearby_path:
                return False
        else:
            if is_any_path_cell(cell):
                return False
            if self.get_vein_at(cell) is not None:
                return False
        self.towers.append(Tower(tower_type, cell))
        self.money -= TOWER_COST[tower_type]
        return True

    def upgrade_tower(self):
        if self.selected_tower and self.selected_tower.hp > 0:
            if self.selected_tower.tower_type == "mage" and self.selected_tower.level == 1:
                self.mage_upgrade_pending = True
                self.mage_to_upgrade = self.selected_tower
                return False
            
            cost = TOWER_UPGRADE_COST[self.selected_tower.tower_type]
            if self.money >= cost:
                if self.selected_tower.upgrade():
                    self.money -= cost
                    return True
        return False

    def apply_mage_specialization(self, spec_type):
        if self.mage_to_upgrade and self.mage_to_upgrade.hp > 0:
            cost = TOWER_UPGRADE_COST["mage"]
            if self.money >= cost:
                self.money -= cost
                self.mage_to_upgrade.level += 1
                self.mage_to_upgrade.apply_specialization(spec_type)
                self.mage_to_upgrade.total_investment += cost
                self.mage_upgrade_pending = False
                self.mage_to_upgrade = None
                return True
        return False

    def sell_tower(self, cell):
        for t in self.towers:
            if t.cell == cell:
                if t.tower_type == "barracks" and t.allied_unit is not None:
                    t.allied_unit.alive = False
                    t.allied_unit = None
                refund = int(t.total_investment * 0.7)
                self.money += refund
                if t == self.selected_tower:
                    self.selected_tower = None
                self.towers.remove(t)
                return True
        return False

    def toggle_miner_mode(self):
        if self.selected_tower and self.selected_tower.tower_type == "miner" and self.selected_tower.hp > 0:
            miner = self.selected_tower
            if miner.attack_mode:
                miner.attack_mode = False
                miner.mining = True
            else:
                miner.attack_mode = True
                miner.mining = False
            return True
        return False

    def update(self):
        if self.defeat or self.victory:
            return

        self.hq.update(self)
        if self.hq.hp <= 0:
            self.defeat = True
            return

        self.update_radar_animation()

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
                e_type, lane = self.spawn_queue.pop(0)
                if e_type == "satan":
                    self.enemies.append(SatanBoss(lane))
                else:
                    self.enemies.append(Enemy(e_type, lane))
                self.wave_timer = 0

        for enemy in self.enemies[:]:
            if isinstance(enemy, SatanBoss):
                enemy.spawn_minions(self)
                enemy.move(self.towers, self.hq, self.enemies, self.allied_units, self.raider_camps)
            else:
                enemy.move(self.towers, self.hq, self.enemies, self.allied_units, self.raider_camps)
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

        for t in self.towers[:]:
            if t.tower_type == "miner" and t.hp <= 0:
                camp = RaiderCamp(t.cell, (t.x, t.y))
                self.raider_camps.append(camp)
                self.towers.remove(t)
                if self.selected_tower is t:
                    self.selected_tower = None

        self.towers = [t for t in self.towers if t.hp > 0]
        if self.selected_tower and self.selected_tower.hp <= 0:
            self.selected_tower = None

        for tower in self.towers:
            tower.update(self.enemies, self, self.raider_camps, self.raiders)

        if self.wave_active and not self.spawn_queue and len(self.enemies) == 0:
            self.wave_active = False
            self.wave += 1
            self.waves_completed += 1
            if self.wave > self.total_waves:
                self.victory = True
            else:
                self.post_wave_event()

    def post_wave_event(self):
        if self.waves_completed % 2 == 0 and self.wave <= 3:
            if self.money >= 150:
                self.money -= 150
            else:
                if self.towers:
                    t = random.choice(self.towers)
                    if t.tower_type == "barracks" and t.allied_unit is not None:
                        t.allied_unit.alive = False
                        t.allied_unit = None
                    self.towers.remove(t)
                    if t == self.selected_tower:
                        self.selected_tower = None

    def draw_ui(self, surface):
        pygame.draw.rect(surface, PANEL_BG, (0, 0, SIDE_PANEL_WIDTH, SCREEN_HEIGHT))
        pygame.draw.rect(surface, PANEL_BG, (SCREEN_WIDTH - SIDE_PANEL_WIDTH, 0, SIDE_PANEL_WIDTH, SCREEN_HEIGHT))

        y_offset = scaled(60)
        x_indent = scaled(25)
        line_gap = scaled(80)

        texts = [
            f"Gold: {self.money}",
            f"Ore: {self.ore}",
            f"Wave: {self.wave}/{self.total_waves}"
        ]
        colors = [YELLOW, ORE_COLOR, WHITE]
        for txt, col in zip(texts, colors):
            rendered = font_medium.render(txt, True, col)
            surface.blit(rendered, (x_indent, y_offset))
            y_offset += line_gap
        
        if not self.first_wave_started:
            hint_txt = font_small.render("Press Start Wave to begin", True, CYAN)
            surface.blit(hint_txt, (x_indent, y_offset))
            y_offset += scaled(50)
        elif self.wave_delay_active:
            delay_seconds = (self.wave_delay - self.wave_delay_timer) / 60
            delay_txt = font_small.render(f"Enemies in: {delay_seconds:.1f}s", True, RED)
            surface.blit(delay_txt, (x_indent, y_offset))
            y_offset += scaled(50)
        elif not self.wave_active and self.wave <= self.total_waves:
            interval_seconds = (self.wave_interval - self.wave_interval_timer) / 60
            next_txt = font_small.render(f"Next wave: {interval_seconds:.0f}s", True, CYAN)
            surface.blit(next_txt, (x_indent, y_offset))
            y_offset += scaled(50)

        right_x = SCREEN_WIDTH - SIDE_PANEL_WIDTH + scaled(15)
        btn_width = SIDE_PANEL_WIDTH - scaled(30)
        start_y = scaled(30)
        btn_gap = scaled(15)
        tower_types = ["archer", "mage", "cannon", "miner", "barracks"]
        num_btns = len(tower_types) + 4
        max_btn_height = (SCREEN_HEIGHT - start_y*2 - btn_gap*(num_btns-1)) // num_btns
        btn_height = max(60, min(100, max_btn_height))

        btn_y = start_y
        for ttype in tower_types:
            rect = pygame.Rect(right_x, btn_y, btn_width, btn_height)
            color = GOLD if self.selected_tower_type == ttype else LIGHT_GRAY
            pygame.draw.rect(surface, color, rect)
            pygame.draw.rect(surface, BLACK, rect, 2)
            name_txt = font_small.render(ttype.capitalize(), True, BLACK)
            price_txt = font_small.render(f"${TOWER_COST[ttype]}", True, BLACK)
            surface.blit(name_txt, (rect.x + 8, rect.y + 8))
            surface.blit(price_txt, (rect.x + 8, rect.y + btn_height//2))
            btn_y += btn_height + btn_gap

        upgrade_rect = pygame.Rect(right_x, btn_y, btn_width, btn_height)
        color = GREEN if self.selected_tower else LIGHT_GRAY
        pygame.draw.rect(surface, color, upgrade_rect)
        pygame.draw.rect(surface, BLACK, upgrade_rect, 2)
        surface.blit(font_small.render("Upgrade", True, BLACK), (upgrade_rect.x + 8, upgrade_rect.y + scaled(8)))
        if self.selected_tower:
            cost = TOWER_UPGRADE_COST[self.selected_tower.tower_type]
            cost_txt = font_small.render(f"${cost}", True, BLACK)
            surface.blit(cost_txt, (upgrade_rect.x + 8, upgrade_rect.y + btn_height - scaled(28)))
        btn_y += btn_height + btn_gap

        start_rect = pygame.Rect(right_x, btn_y, btn_width, btn_height)
        can_start = not self.wave_active and not self.wave_delay_active and self.wave <= self.total_waves and not self.victory and not self.defeat
        color = GREEN if can_start else LIGHT_GRAY
        pygame.draw.rect(surface, color, start_rect)
        pygame.draw.rect(surface, BLACK, start_rect, 2)
        
        if self.wave_delay_active:
            btn_text = "Wave Starting..."
        elif self.wave_active:
            btn_text = "Wave Active"
        elif not self.first_wave_started:
            btn_text = "Start Wave"
        else:
            btn_text = "Start Wave (+15 Ore, +30 Gold)"
        surface.blit(font_small.render(btn_text, True, BLACK), (start_rect.x + 8, start_rect.y + btn_height//3))
        btn_y += btn_height + btn_gap

        miner_rect = pygame.Rect(right_x, btn_y, btn_width, btn_height)
        if self.selected_tower and self.selected_tower.tower_type == "miner":
            mode_text = "Attack Mode" if not self.selected_tower.attack_mode else "Mine Mode"
            color = RED if not self.selected_tower.attack_mode else GREEN
            pygame.draw.rect(surface, color, miner_rect)
            surface.blit(font_small.render(mode_text, True, BLACK), (miner_rect.x + 8, miner_rect.y + btn_height//3))
        else:
            pygame.draw.rect(surface, LIGHT_GRAY, miner_rect)
            surface.blit(font_small.render("No miner", True, BLACK), (miner_rect.x + 8, miner_rect.y + btn_height//3))
        pygame.draw.rect(surface, BLACK, miner_rect, 2)
        btn_y += btn_height + btn_gap

        radar_rect = pygame.Rect(right_x, btn_y, btn_width, btn_height)
        color = CYAN if self.radar_mode else LIGHT_GRAY
        pygame.draw.rect(surface, color, radar_rect)
        pygame.draw.rect(surface, BLACK, radar_rect, 2)
        surface.blit(font_small.render("Radar (30$)", True, BLACK), (radar_rect.x + 8, radar_rect.y + btn_height//3))

        if self.selected_tower and self.selected_tower.hp > 0:
            rect = pygame.Rect(self.selected_tower.x - scaled(25), self.selected_tower.y - scaled(25), scaled(50), scaled(50))
            pygame.draw.rect(surface, YELLOW, rect, scaled(3))

        if self.mage_upgrade_pending:
            overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
            overlay.fill((0, 0, 0, 150))
            surface.blit(overlay, (0, 0))
            
            menu_w = scaled(400)
            menu_h = scaled(300)
            menu_x = (SCREEN_WIDTH - menu_w) // 2
            menu_y = (SCREEN_HEIGHT - menu_h) // 2
            
            pygame.draw.rect(surface, PANEL_BG, (menu_x, menu_y, menu_w, menu_h))
            pygame.draw.rect(surface, GOLD, (menu_x, menu_y, menu_w, menu_h), scaled(3))
            
            title = font_medium.render("Choose Mage Specialization", True, WHITE)
            surface.blit(title, (menu_x + (menu_w - title.get_width()) // 2, menu_y + scaled(20)))
            
            specs = [
                ("Ice", CYAN, "ice"),
                ("Fire", (255, 100, 0), "fire"),
                ("Poison", (100, 255, 100), "poison"),
                ("Lightning", GOLD, "lightning")
            ]
            
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
            txt = font_large.render("VICTORY! Satan is defeated.", True, GOLD)
            txt_rect = txt.get_rect(center=(SCREEN_WIDTH//2, SCREEN_HEIGHT//2))
            surface.blit(txt, txt_rect)
        elif self.defeat:
            txt = font_large.render("DEFEAT", True, RED)
            txt_rect = txt.get_rect(center=(SCREEN_WIDTH//2, SCREEN_HEIGHT//2))
            surface.blit(txt, txt_rect)


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
            
            if game.mage_upgrade_pending:
                menu_w = scaled(400)
                menu_h = scaled(300)
                menu_x = (SCREEN_WIDTH - menu_w) // 2
                menu_y = (SCREEN_HEIGHT - menu_h) // 2
                
                specs = ["ice", "fire", "poison", "lightning"]
                btn_w = scaled(160)
                btn_h = scaled(60)
                gap = scaled(20)
                start_x = menu_x + (menu_w - 2 * btn_w - gap) // 2
                start_y_menu = menu_y + scaled(100)
                
                for i, spec in enumerate(specs):
                    row = i // 2
                    col = i % 2
                    bx = start_x + col * (btn_w + gap)
                    by = start_y_menu + row * (btn_h + gap)
                    
                    rect = pygame.Rect(bx, by, btn_w, btn_h)
                    if rect.collidepoint(pos):
                        game.apply_mage_specialization(spec)
                        break
                continue
            
            if pos[0] >= SCREEN_WIDTH - SIDE_PANEL_WIDTH:
                right_x = SCREEN_WIDTH - SIDE_PANEL_WIDTH + scaled(15)
                btn_width = SIDE_PANEL_WIDTH - scaled(30)
                start_y = scaled(30)
                tower_types = ["archer", "mage", "cannon", "miner", "barracks"]
                num_btns = len(tower_types) + 4
                max_btn_height = (SCREEN_HEIGHT - start_y*2 - scaled(15)*(num_btns-1)) // num_btns
                btn_height = max(60, min(100, max_btn_height))
                btn_gap = scaled(15)

                btn_y = start_y
                for ttype in tower_types:
                    rect = pygame.Rect(right_x, btn_y, btn_width, btn_height)
                    if rect.collidepoint(pos):
                        game.selected_tower_type = ttype
                        game.selected_tower = None
                        game.radar_mode = False
                        break
                    btn_y += btn_height + btn_gap

                upgrade_rect = pygame.Rect(right_x, btn_y, btn_width, btn_height)
                if upgrade_rect.collidepoint(pos):
                    game.upgrade_tower()
                btn_y += btn_height + btn_gap

                start_rect = pygame.Rect(right_x, btn_y, btn_width, btn_height)
                if start_rect.collidepoint(pos):
                    can_start = not game.wave_active and not game.wave_delay_active and game.wave <= game.total_waves and not game.victory and not game.defeat
                    if can_start:
                        game.start_wave(early=True)
                btn_y += btn_height + btn_gap

                miner_rect = pygame.Rect(right_x, btn_y, btn_width, btn_height)
                if miner_rect.collidepoint(pos):
                    game.toggle_miner_mode()
                btn_y += btn_height + btn_gap

                radar_rect = pygame.Rect(right_x, btn_y, btn_width, btn_height)
                if radar_rect.collidepoint(pos):
                    game.radar_mode = not game.radar_mode
                    game.selected_tower_type = None
                    game.selected_tower = None
            elif pos[0] < SIDE_PANEL_WIDTH:
                pass
            else:
                cell = cell_from_pos(pos)
                if 0 <= cell[0] < GRID_WIDTH and 0 <= cell[1] < GRID_HEIGHT:
                    if game.radar_mode:
                        game.reveal_area(cell)
                    else:
                        for t in game.towers:
                            if t.cell == cell and t.hp > 0:
                                game.selected_tower = t
                                game.selected_tower_type = None
                                break
                        else:
                            if game.selected_tower_type:
                                game.build_tower(game.selected_tower_type, cell)

        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_u:
                game.upgrade_tower()
            if event.key == pygame.K_s and pygame.key.get_mods() & pygame.KMOD_SHIFT:
                pos = pygame.mouse.get_pos()
                if pos[0] >= SIDE_PANEL_WIDTH and pos[0] < SCREEN_WIDTH - SIDE_PANEL_WIDTH:
                    cell = cell_from_pos(pos)
                    game.sell_tower(cell)
            if event.key == pygame.K_SPACE:
                can_start = not game.wave_active and not game.wave_delay_active and game.wave <= game.total_waves and not game.victory and not game.defeat
                if can_start:
                    game.start_wave(early=True)
            if event.key == pygame.K_m:
                game.toggle_miner_mode()
            if event.key == pygame.K_r:
                game.radar_mode = not game.radar_mode

    game.update()

    field_rect = pygame.Rect(FIELD_OFFSET_X, FIELD_OFFSET_Y, FIELD_WIDTH, FIELD_HEIGHT)
    pygame.draw.rect(screen, GREEN, field_rect)
    
    for x in range(GRID_WIDTH):
        for y in range(GRID_HEIGHT):
            rect = pygame.Rect(FIELD_OFFSET_X + x * CELL_SIZE, FIELD_OFFSET_Y + y * CELL_SIZE, CELL_SIZE, CELL_SIZE)
            cell = (x, y)
            if is_any_path_cell(cell):
                pygame.draw.rect(screen, BROWN, rect)
            else:
                pygame.draw.rect(screen, GREEN, rect)
                pygame.draw.rect(screen, GRAY, rect, 1)

    for vein in game.veins:
        vein.draw(screen)

    for tower in game.towers:
        tower.draw(screen)

    for camp in game.raider_camps:
        camp.draw(screen)

    for au in game.allied_units:
        au.draw(screen)

    for enemy in game.enemies:
        enemy.draw(screen)

    for raider in game.raiders:
        raider.draw(screen)

    game.hq.draw(screen)

    game.draw_radar_animation(screen)

    game.draw_ui(screen)

    pygame.display.flip()
    clock.tick(60)

pygame.quit()
sys.exit()