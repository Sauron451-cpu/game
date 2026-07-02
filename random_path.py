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
    "archer": 100, "cannon": 150, "mortar": 200, "greek_fire": 300,
    "miner": 50
}
TOWER_UPGRADE_COST = {
    "archer": 50, "cannon": 50, "mortar": 50, "greek_fire": 50,
    "miner": 50
}

STARTING_MONEY = 500
STARTING_ORE = 50
ORE_PER_VEIN_CELL = 200
ENEMY_REWARD_MULTIPLIER = 1.0
CASTLE_GOLD_INCOME = 10
CASTLE_GOLD_INTERVAL = 60
MINER_ORE_PER_TICK = 5
BROKEN_TOWER_REPAIR_COST = 10
BROKEN_TOWER_COUNT = 6
SCOUT_REVEAL_SIZE = 3
CASTLE_REVEAL_SIZE = 6
BASE_SCOUT_COST = 20
SCOUT_COST_STEP = 8
MAX_SCOUT_COST = 120
WAVE_INTERVAL = 600
FIRST_WAVE_DELAY = 600
TOWER_ORE_COST = {
    "archer": 0, "cannon": 1, "mortar": 2, "greek_fire": 4,
    "miner": 0
}

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

MOB_DISPLAY_NAMES = {
    "orc": "Воин",
    "hellbrute": "Бронированный",
    "wurg": "Наездник",
    "raider": "Обычный разбойник",
    "armored_raider": "Бронированный разбойник",
    "satan": "Герцог",
}

MELEE = "mile"
RANGE = "range"

ENEMY_DISPLAY_NAMES = {
    "soldier": "Soldier",
    "knight": "Knight",
    "rider": "Rider",
    "cart": "Cart",
    "raider": "Bandit",
    "armored_raider": "Armored Bandit",
    "duke": "Duke",
}

TOWER_DISPLAY_NAMES = {
    "archer": "Crossbow",
    "cannon": "Cannon",
    "mortar": "Mortar",
    "greek_fire": "Greek Fire",
    "miner": "Miner",
}

MAX_RAIDERS_PER_MINER = 2

HQ_CELLS = {(9,9), (9,10), (10,9), (10,10)}
HQ_ATTACK_CELLS = {
    (9, 8), (10, 8),
    (8, 9), (11, 9),
    (8, 10), (11, 10),
    (9, 11), (10, 11)
}
HQ_CENTER_X = FIELD_OFFSET_X + 9.5 * CELL_SIZE
HQ_CENTER_Y = FIELD_OFFSET_Y + 9.5 * CELL_SIZE

HQ_HITBOX_X1 = FIELD_OFFSET_X + 9 * CELL_SIZE
HQ_HITBOX_Y1 = FIELD_OFFSET_Y + 9 * CELL_SIZE
HQ_HITBOX_X2 = HQ_HITBOX_X1 + 2 * CELL_SIZE
HQ_HITBOX_Y2 = HQ_HITBOX_Y1 + 2 * CELL_SIZE

def generate_path(start, target, occupied_cells):
    """Генерирует путь шириной ровно 1 клетка от start до target"""
    path = [start]
    visited = {start}
    visited.update(occupied_cells)
    current = start
    
    hq_cells = {(9,9), (9,10), (10,9), (10,10)}
    hq_attack_cells = {
        (9, 8), (10, 8),
        (8, 9), (11, 9),
        (8, 10), (11, 10),
        (9, 11), (10, 11)
    }
    
    while current != target:
        neighbors = []
        for dx, dy in [(0,1), (0,-1), (1,0), (-1,0)]:
            nx, ny = current[0]+dx, current[1]+dy
            if 0 <= nx < 20 and 0 <= ny < 20:
                if (nx, ny) not in visited:
                    if (nx, ny) in hq_cells:
                        continue
                    if (nx, ny) in hq_attack_cells and (nx, ny) != target:
                        continue
                    neighbors.append((nx, ny))
        
        if not neighbors:
            return None
            
        # Сортируем по расстоянию до цели
        neighbors.sort(key=lambda p: abs(p[0]-target[0]) + abs(p[1]-target[1]))
        
        # С вероятностью 80% выбираем лучший вариант, иначе случайный
        if random.random() < 0.8:
            best_dist = abs(neighbors[0][0]-target[0]) + abs(neighbors[0][1]-target[1])
            best_neighbors = [n for n in neighbors if abs(n[0]-target[0]) + abs(n[1]-target[1]) == best_dist]
            next_cell = random.choice(best_neighbors)
        else:
            next_cell = random.choice(neighbors)
            
        path.append(next_cell)
        visited.add(next_cell)
        current = next_cell
        
        if len(path) > 400:
            return None
            
    return path

def generate_map_layout():
    """Генерирует карту с дорогами шириной 1 клетка"""
    hq_cells = {(9,9), (9,10), (10,9), (10,10)}
    
    # Собираем все клетки по краям карты
    edges = []
    for x in range(20):
        edges.append((x, 0))
        edges.append((x, 19))
    for y in range(20):
        edges.append((0, y))
        edges.append((19, y))
        
    # Выбираем 3 стартовые точки на краях
    starts = []
    attempts = 0
    while len(starts) < 3 and attempts < 1000:
        p = random.choice(edges)
        valid = True
        for s in starts:
            if abs(p[0]-s[0]) + abs(p[1]-s[1]) < 6:
                valid = False
                break
        if valid:
            starts.append(p)
        attempts += 1
        
    if len(starts) < 3:
        starts = [(17,0), (0,13), (15,19)]
        
    # Точки входа вокруг HQ
    top_entries = [(9, 8), (10, 8)]
    left_entries = [(8, 9), (8, 10)]
    right_entries = [(11, 9), (11, 10)]
    bottom_entries = [(9, 11), (10, 11)]
    
    available_targets = top_entries + left_entries + right_entries + bottom_entries
    random.shuffle(available_targets)
    targets = available_targets[:3]
    
    lanes = {}
    path_cells = set()
    lane_names = ["lane_1", "lane_2", "lane_3"]
    
    for i in range(3):
        start = starts[i]
        target = targets[i]
        
        path = None
        gen_attempts = 0
        while path is None and gen_attempts < 100:
            path = generate_path(start, target, path_cells)
            gen_attempts += 1
            
        if path is None:
            # Fallback: создаем простой путь, который точно заканчивается в HQ
            path = []
            x, y = start
            # Сначала идем к целевой точке входа
            while x != target[0]:
                path.append((x, y))
                x += 1 if target[0] > x else -1
            while y != target[1]:
                path.append((x, y))
                y += 1 if target[1] > y else -1
            path.append(target)
            
            # Теперь находим смежную клетку HQ
            hq_adj = None
            for dx, dy in [(0,1), (0,-1), (1,0), (-1,0)]:
                nx, ny = target[0]+dx, target[1]+dy
                if (nx, ny) in hq_cells:
                    hq_adj = (nx, ny)
                    break
            
            # Если не нашли смежную клетку HQ, используем ближайшую
            if hq_adj is None:
                hq_adj = min(hq_cells, key=lambda cell: abs(cell[0]-target[0]) + abs(cell[1]-target[1]))
            
            path.append(hq_adj)
        else:
            # Добавляем клетку HQ в конец пути
            hq_adj = None
            for dx, dy in [(0,1), (0,-1), (1,0), (-1,0)]:
                nx, ny = target[0]+dx, target[1]+dy
                if (nx, ny) in hq_cells:
                    hq_adj = (nx, ny)
                    break
            
            # Если не нашли смежную клетку HQ, используем ближайшую
            if hq_adj is None:
                hq_adj = min(hq_cells, key=lambda cell: abs(cell[0]-target[0]) + abs(cell[1]-target[1]))
            
            path.append(hq_adj)
            
        lanes[lane_names[i]] = path
        # Добавляем все клетки пути кроме последней (она будет добавлена следующей дорогой или это HQ)
        path_cells.update(path[:-1])
        
    return lanes, path_cells

LANES, PATH_CELLS = generate_map_layout()

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

def is_near_path_cell(cell, distance=1):
    return any(abs(cell[0] - pc[0]) <= distance and abs(cell[1] - pc[1]) <= distance for pc in PATH_CELLS)

def is_hq_cell(cell):
    return cell in HQ_CELLS

def distance_to_hq_hitbox(pos):
    x, y = pos
    closest_x = max(HQ_HITBOX_X1, min(x, HQ_HITBOX_X2))
    closest_y = max(HQ_HITBOX_Y1, min(y, HQ_HITBOX_Y2))
    return math.hypot(x - closest_x, y - closest_y)

def can_attack_hq_from_pos(pos):
    cell = cell_from_pos(pos)
    return cell in HQ_ATTACK_CELLS

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
    def __init__(self, target_miner, spawn_pos, from_camp=False, raider_type="normal"):
        self.target_miner = target_miner
        self.raider_type = raider_type
        self.pos = list(spawn_pos)
        self.max_hp = 95 if raider_type == "armored" else 100
        self.hp = self.max_hp
        self.damage = 18 if raider_type == "armored" else 10
        self.attack_range = scaled(40)
        raw_speed = 25 if raider_type == "armored" else max(1, scaled(1.0))
        self.speed = float(raw_speed)
        self.base_speed = self.speed
        self.attack_cooldown_max = 95 if raider_type == "armored" else 60
        self.attack_cooldown = 0
        self.alive = True
        self.color = (95, 95, 105) if raider_type == "armored" else RAIDER_COLOR
        self.reward = 45 if raider_type == "armored" else 0
        self.attacking_tower = None
        self.burn_timer = 0
        self.poison_timer = 0
        self.slow_timer = 0
        self.phys_armor = 0.35 if raider_type == "armored" else -0.2
        self.mag_armor = 0.12 if raider_type == "armored" else -0.2
        self.evade = 0 if raider_type == "armored" else 0.08
        self.path_index = 0
        self.path = []
        self.lane = None
        self.can_rise = False
        self.risen = False
        self.enemy_type = "armored_raider" if raider_type == "armored" else "raider"
        self.display_name = ENEMY_DISPLAY_NAMES[self.enemy_type]
        self.from_camp = from_camp

    def move(self, towers, hq, enemies, allied_units, raider_camps):
        if not self.alive:
            return
        if self.attack_cooldown > 0:
            self.attack_cooldown -= 1

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
            
            if self.target_miner is None:
                if hq.hp > 0:
                    if can_attack_hq_from_pos(self.pos):
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

        if isinstance(self.target_miner, Tower) and self.target_miner.hp > 0:
            tx, ty = self.target_miner.x, self.target_miner.y
            dist = math.hypot(self.pos[0] - tx, self.pos[1] - ty)
            if dist <= self.attack_range:
                if self.attack_cooldown <= 0:
                    self.target_miner.take_damage(self.damage)
                    self.attack_cooldown = self.attack_cooldown_max
                return
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
        if self.raider_type == "armored" and damage_source == "cannon":
            effective *= 2.2
        if self.raider_type == "armored" and damage_source == "archer":
            effective *= 0.65
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
        body_size = scaled(30) if self.raider_type == "armored" else scaled(24)
        pygame.draw.rect(surface, self.color, (int(self.pos[0] - body_size//2), int(self.pos[1] - body_size//2), body_size, body_size))
        if self.raider_type == "armored":
            pygame.draw.rect(surface, (190, 190, 200), (int(self.pos[0] - body_size//2), int(self.pos[1] - body_size//2), body_size, body_size), max(1, scaled(3)))
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
            raider_type = "normal"
            raider = Raider(None, (self.x, self.y), from_camp=True, raider_type=raider_type)
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
        self.display_name = ENEMY_DISPLAY_NAMES[enemy_type]
        self.lane = lane
        base_range = scaled(40)
        stats = {
            "soldier": {"hp": 100, "phys": 0.0, "mag": 0.0, "speed": scaled(1.0), "rise": False, "evade": 0.0,
                    "attack": MELEE, "color": GREEN, "atk_dmg": 20, "atk_range": base_range, "atk_cd": 65,
                    "vulnerable_to": {"castle": 1.0, "archer": 1.0, "cannon": 1.0, "mortar": 1.0, "greek_fire": 1.0}},
            "rider": {"hp": 120, "phys": 0.0, "mag": 0.0, "speed": scaled(1.5), "rise": False, "evade": 0.08,
                     "attack": MELEE, "color": YELLOW, "atk_dmg": 40, "atk_range": base_range, "atk_cd": 55,
                     "vulnerable_to": {"castle": 1.0, "archer": 1.0, "cannon": 1.0, "mortar": 1.0, "greek_fire": 1.0}},
            "knight": {"hp": 120, "phys": 0.0, "mag": 0.0, "speed": scaled(0.5), "rise": False, "evade": 0,
                          "attack": MELEE, "color": (200, 0, 200), "atk_dmg": 30, "atk_range": scaled(50), "atk_cd": 110,
                          "vulnerable_to": {"castle": 0.6, "archer": 0.6, "cannon": 1.2, "mortar": 1.2, "greek_fire": 1.0}},
            "cart": {"hp": 400, "phys": 0.0, "mag": 0.0, "speed": scaled(1.0), "rise": False, "evade": 0.0,
                     "attack": MELEE, "color": (155, 105, 55), "atk_dmg": 0, "atk_range": base_range, "atk_cd": 90,
                     "vulnerable_to": {"castle": 0.8, "archer": 0.8, "cannon": 1.2, "mortar": 1.2, "greek_fire": 2.0}}
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
        self.vulnerable_to = s.get("vulnerable_to", {})

        self.path = get_path_pixels(lane)
        self.path_index = 0
        self.pos = list(self.path[0])
        self.alive = True
        self.risen = False
        self.attacking_tower = None
        self.spawned_soldiers = False

        self.burn_timer = 0
        self.poison_timer = 0
        self.slow_timer = 0

        rewards = {"soldier": 20, "rider": 30, "knight": 25, "cart": 10}
        self.reward = rewards[enemy_type]

    def spawn_soldiers(self, game, count=2):
        if self.spawned_soldiers:
            return
        self.spawned_soldiers = True
        for _ in range(count):
            lane = random.choice(list(LANES.keys()))
            soldier = Enemy("soldier", lane)
            soldier.pos = [
                self.pos[0] + random.randint(-CELL_SIZE // 3, CELL_SIZE // 3),
                self.pos[1] + random.randint(-CELL_SIZE // 3, CELL_SIZE // 3)
            ]
            soldier.path_index = min(self.path_index, len(soldier.path) - 1)
            game.enemies.append(soldier)

    def move(self, towers, hq, enemies, allied_units, raider_camps):
        if not self.alive:
            return
        if self.attack_cooldown > 0:
            self.attack_cooldown -= 1

        if self.enemy_type == "cart":
            if self.path_index >= len(self.path) - 1:
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
            return

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
                    if can_attack_hq_from_pos(self.pos):
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
                self.attacking_tower = None
            else:
                self.attacking_tower = None

        targets = [tower for tower in towers if tower.tower_type == "miner"]
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
                if not can_attack_hq_from_pos(self.pos):
                    continue
                dist = 0
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
        if self.enemy_type == "soldier":
            pygame.draw.rect(surface, self.color, (int(self.pos[0] - scaled(15)), int(self.pos[1] - scaled(15)), scaled(30), scaled(30)))
        elif self.enemy_type == "rider":
            pygame.draw.rect(surface, self.color, (int(self.pos[0] - scaled(14)), int(self.pos[1] - scaled(18)), scaled(28), scaled(36)))
            draw_square_dot(surface, WHITE, (self.pos[0], self.pos[1] - scaled(5)), scaled(8))
        elif self.enemy_type == "knight":
            pygame.draw.rect(surface, self.color, (int(self.pos[0] - scaled(18)), int(self.pos[1] - scaled(18)), scaled(36), scaled(36)))
        elif self.enemy_type == "cart":
            pygame.draw.rect(surface, self.color, (int(self.pos[0] - scaled(22)), int(self.pos[1] - scaled(14)), scaled(44), scaled(28)))
            pygame.draw.rect(surface, BLACK, (int(self.pos[0] - scaled(22)), int(self.pos[1] - scaled(14)), scaled(44), scaled(28)), max(1, scaled(2)))
        bar_width = scaled(30)
        pygame.draw.rect(surface, RED, (int(self.pos[0] - bar_width/2), int(self.pos[1] - scaled(25)), bar_width, scaled(5)))
        green_width = bar_width * (self.hp / self.max_hp)
        pygame.draw.rect(surface, YELLOW, (int(self.pos[0] - bar_width/2), int(self.pos[1] - scaled(25)), green_width, scaled(5)))


class SatanBoss(Enemy):
    def __init__(self, lane):
        super().__init__("knight", lane)
        self.enemy_type = "duke"
        self.display_name = ENEMY_DISPLAY_NAMES[self.enemy_type]
        self.max_hp = 2000
        self.hp = self.max_hp
        raw_speed = max(0.1, scaled(0.1))
        self.speed = float(raw_speed)
        self.base_speed = float(raw_speed)
        self.phys_armor = 0.28
        self.mag_armor = 0.28
        self.vulnerable_to = {"castle": 0.5, "archer": 0.5, "cannon": 0.5, "mortar": 0.5, "greek_fire": 0.5}
        self.evade = 0
        self.attack_range = scaled(60)
        self.attack_damage = 50
        self.attack_cooldown_max = 85
        self.attack_cooldown = 0
        self.color = (255, 0, 0)
        self.reward = 0
        self.phase = 1
        self.minion_timer = 0
        self.minion_cooldown = 300
        self.destroy_timer = 0
        self.destroy_cooldown = 300

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
                self.speed = self.base_speed
                self.slow_timer = 0
            elif self.phase == 3:
                self.speed = self.base_speed
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
                    lane = random.choice(list(LANES.keys()))
                    minion = Enemy("soldier", lane)
                    minion.pos = list(spawn_pos)
                    minion.hp = minion.max_hp // 2
                    game.enemies.append(minion)

    def destroy_random_tower(self, towers):
        if self.destroy_timer > 0:
            self.destroy_timer -= 1
            return

        candidates = [tower for tower in towers if tower.hp > 0]
        if candidates:
            target = random.choice(candidates)
            target.hp = 0
            self.destroy_timer = self.destroy_cooldown

    def move(self, towers, hq, enemies, allied_units, raider_camps):
        if not self.alive:
            return
        if self.attack_cooldown > 0:
            self.attack_cooldown -= 1
        self.destroy_random_tower(towers)
        
        self.check_phase()
        
        if self.phase >= 2:
            self.slow_timer = 0
            self.speed = self.base_speed
        
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
            if can_attack_hq_from_pos(self.pos):
                if self.attack_cooldown <= 0:
                    hq.take_damage(self.attack_damage)
                    self.attack_cooldown = self.attack_cooldown_max
                return
        
        if self.path_index >= len(self.path) - 1:
            if hq.hp > 0 and can_attack_hq_from_pos(self.pos):
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
    def __init__(self, tower_type, cell):
        self.tower_type = tower_type
        self.cell = cell
        self.x = FIELD_OFFSET_X + cell[0] * CELL_SIZE + CELL_SIZE//2
        self.y = FIELD_OFFSET_Y + cell[1] * CELL_SIZE + CELL_SIZE//2
        self.level = 1
        base_range = scaled(150)
        stats = {
            "archer": {"damage": 50, "range": base_range, "cooldown": 20, "color": BLUE, "proj_color": CYAN, "hp": 150, "dmg_type": "ordinary"},
            "cannon": {"damage": 110, "range": base_range, "cooldown": 50, "color": ORANGE, "proj_color": (255, 100, 0), "hp": 200, "dmg_type": "piercing"},
            "mortar": {"damage": 100, "range": scaled(260), "cooldown": 90, "color": (110, 110, 120), "proj_color": LIGHT_GRAY, "hp": 200, "dmg_type": "piercing"},
            "greek_fire": {"damage": 60, "range": scaled(90), "cooldown": 50, "color": (220, 50, 0), "proj_color": (255, 80, 0), "hp": 160, "dmg_type": "fire"},
            "miner": {"damage": 10, "range": scaled(100), "cooldown": 40, "color": ORE_COLOR, "proj_color": ORE_COLOR, "hp": 100, "dmg_type": "physical"},
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
        self.stun_timer = 0

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
        if self.tower_type != "miner":
            return
        if self.tower_type == "miner" and getattr(self, "closed", False):
            return
        self.hp -= damage
        if self.hp <= 0:
            self.hp = 0

    def find_target(self, enemies, raider_camps, raiders, game):
        if self.tower_type == "barracks" or self.damage == 0:
            return None
        in_range = []
        for e in enemies:
            if (e.alive and game.is_pos_revealed(e.pos)
                    and math.hypot(e.pos[0] - self.x, e.pos[1] - self.y) <= self.range):
                in_range.append(e)
        for raider in raiders:
            if (raider.alive and game.is_pos_revealed(raider.pos)
                    and math.hypot(raider.pos[0] - self.x, raider.pos[1] - self.y) <= self.range):
                in_range.append(raider)
        for camp in raider_camps:
            if (camp.hp > 0 and game.is_pos_revealed((camp.x, camp.y))
                    and math.hypot(camp.x - self.x, camp.y - self.y) <= self.range):
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
        if self.stun_timer > 0:
            self.stun_timer -= 1
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
                        mined = min(MINER_ORE_PER_TICK, vein.amount)
                        vein.amount -= mined
                        self.stored_ore += mined
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
                    self.projectiles.append([target, list((self.x, self.y))])
                    self.cooldown = self.cooldown_max

        for proj in self.projectiles[:]:
            target, pos = proj
            if not target.alive if hasattr(target, 'alive') else target.hp <= 0:
                self.projectiles.remove(proj)
                continue
            if not game.is_target_revealed(target):
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
                
                if self.tower_type == "mortar" and not isinstance(target, RaiderCamp):
                    splash_radius = scaled(75)
                    splash_damage = int(self.damage * 0.5)
                    for e in enemies:
                        if e is not target and e.alive and game.is_pos_revealed(e.pos):
                            d = math.hypot(e.pos[0] - target.pos[0], e.pos[1] - target.pos[1])
                            if d <= splash_radius:
                                e.take_damage(splash_damage, self.damage_type, self.tower_type)
                    for r in raiders:
                        if r is not target and r.alive and game.is_pos_revealed(r.pos):
                            d = math.hypot(r.pos[0] - target.pos[0], r.pos[1] - target.pos[1])
                            if d <= splash_radius:
                                r.take_damage(splash_damage, self.damage_type, self.tower_type)

                if self.tower_type == "greek_fire" and not isinstance(target, RaiderCamp):
                    for _ in range(2):
                        target.take_damage(self.damage, self.damage_type, self.tower_type)
                    spread_radius = scaled(45)
                    for e in enemies:
                        if e is not target and e.alive and game.is_pos_revealed(e.pos):
                            d = math.hypot(e.pos[0] - target.pos[0], e.pos[1] - target.pos[1])
                            if d <= spread_radius:
                                e.take_damage(self.damage, self.damage_type, self.tower_type)
                    for r in raiders:
                        if r is not target and r.alive and game.is_pos_revealed(r.pos):
                            d = math.hypot(r.pos[0] - target.pos[0], r.pos[1] - target.pos[1])
                            if d <= spread_radius:
                                r.take_damage(self.damage, self.damage_type, self.tower_type)
                
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
                        if e is not target and e.alive and game.is_pos_revealed(e.pos):
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
        else:
            if self.tower_type == "archer":
                rect_size = scaled(38)
                pygame.draw.rect(surface, self.color, (self.x - rect_size//2, self.y - rect_size//2, rect_size, rect_size))
                pygame.draw.rect(surface, CYAN, (self.x - rect_size//2, self.y - rect_size//2, rect_size, rect_size), max(1, scaled(2)))
            elif self.tower_type == "cannon":
                rect_size = scaled(44)
                pygame.draw.rect(surface, self.color, (self.x - rect_size//2, self.y - rect_size//2, rect_size, rect_size))
                draw_square_dot(surface, RED, (self.x, self.y), scaled(16))
            elif self.tower_type == "mortar":
                rect_size = scaled(46)
                pygame.draw.rect(surface, self.color, (self.x - rect_size//2, self.y - rect_size//2, rect_size, rect_size))
                pygame.draw.rect(surface, BLACK, (self.x - scaled(8), self.y - scaled(22), scaled(16), scaled(30)))
            elif self.tower_type == "greek_fire":
                rect_size = scaled(40)
                pygame.draw.rect(surface, self.color, (self.x - rect_size//2, self.y - rect_size//2, rect_size, rect_size))
                draw_square_dot(surface, (255, 230, 0), (self.x, self.y), scaled(16), RED, max(1, scaled(2)))

        for proj in self.projectiles:
            draw_square_dot(surface, self.proj_color, proj[1], scaled(10), WHITE, max(1, scaled(1)))

        if self.stun_timer > 0:
            stun_size = scaled(46)
            pygame.draw.rect(surface, CYAN, (self.x - stun_size//2, self.y - stun_size//2, stun_size, stun_size), max(2, scaled(4)))

        if self.tower_type == "miner":
            bar_width = scaled(40)
            bar_y = self.y - scaled(40)
            pygame.draw.rect(surface, RED, (self.x - bar_width//2, bar_y, bar_width, scaled(6)))
            hp_ratio = self.hp / self.max_hp
            pygame.draw.rect(surface, YELLOW, (self.x - bar_width//2, bar_y, int(bar_width * hp_ratio), scaled(6)))


class BrokenTower:
    def __init__(self, cell, tower_type="archer"):
        self.cell = cell
        self.tower_type = tower_type
        self.x = FIELD_OFFSET_X + cell[0] * CELL_SIZE + CELL_SIZE//2
        self.y = FIELD_OFFSET_Y + cell[1] * CELL_SIZE + CELL_SIZE//2

    def repair(self, game):
        if game.money < BROKEN_TOWER_REPAIR_COST:
            return False
        if any(t.cell == self.cell and t.hp > 0 for t in game.towers):
            return False
        game.money -= BROKEN_TOWER_REPAIR_COST
        tower = Tower(self.tower_type, self.cell)
        tower.total_investment = BROKEN_TOWER_REPAIR_COST
        game.towers.append(tower)
        game.reveal_cardinal_neighbors(self.cell)
        game.broken_towers.remove(self)
        game.selected_broken_tower = None
        game.hovered_broken_tower = None
        game.last_click_broken_tower = None
        game.selected_tower = tower
        game.selected_tower_type = None
        return True

    def draw(self, surface):
        size = scaled(36)
        left = self.x - size // 2
        top = self.y - size // 2
        pygame.draw.rect(surface, (95, 95, 95), (left, top, size, size))
        pygame.draw.rect(surface, (45, 45, 45), (left, top, size, size), max(2, scaled(3)))
        crack = [
            (self.x - scaled(10), self.y - scaled(14)),
            (self.x - scaled(2), self.y - scaled(4)),
            (self.x - scaled(8), self.y + scaled(6)),
            (self.x + scaled(7), self.y + scaled(14)),
        ]
        pygame.draw.lines(surface, BLACK, False, crack, max(2, scaled(3)))
        txt = font_small.render(str(BROKEN_TOWER_REPAIR_COST), True, WHITE)
        surface.blit(txt, (self.x - txt.get_width()//2, self.y - size//2 - txt.get_height()))


class OreVein:
    def __init__(self, cells):
        self.cells = set(cells)
        self.amount = len(self.cells) * ORE_PER_VEIN_CELL
        self.discovered = False

    def depleted(self):
        return self.amount <= 0

    def get_center(self):
        avg_x = sum(c[0] for c in self.cells) / len(self.cells)
        avg_y = sum(c[1] for c in self.cells) / len(self.cells)
        return FIELD_OFFSET_X + avg_x * CELL_SIZE + CELL_SIZE//2, FIELD_OFFSET_Y + avg_y * CELL_SIZE + CELL_SIZE//2

    def draw(self, surface):
        if not self.discovered:
            return
        hovered = False
        mouse_cell = cell_from_pos(pygame.mouse.get_pos())
        for cell in self.cells:
            x = FIELD_OFFSET_X + cell[0] * CELL_SIZE + CELL_SIZE//2
            y = FIELD_OFFSET_Y + cell[1] * CELL_SIZE + CELL_SIZE//2
            if mouse_cell == cell:
                hovered = True
            if self.depleted():
                pit_size = scaled(28)
                pygame.draw.rect(surface, (45, 38, 34), (x - pit_size//2, y - pit_size//2, pit_size, pit_size))
                pygame.draw.rect(surface, BLACK, (x - pit_size//2, y - pit_size//2, pit_size, pit_size), max(1, scaled(2)))
            else:
                draw_square_dot(surface, ORE_COLOR, (x, y), scaled(18), BLACK, max(1, scaled(1)))
        if self.depleted() or not hovered:
            return
        cx, cy = self.get_center()
        txt = font_small.render(str(self.amount), True, BLACK)
        surface.blit(txt, (cx - txt.get_width()//2, cy - txt.get_height()//2))


class Headquarters:
    def __init__(self):
        self.hp = 1000
        self.max_hp = 1000
        self.gold_generation_timer = 0
        self.attack_range = scaled(220)
        self.attack_damage = 40
        self.attack_cooldown_max = 60
        self.attack_cooldown = 0
        self.projectiles = []
        self.hit_flash_timer = 0
        self.hit_flash_duration = 60

    def take_damage(self, damage, damage_type=None):
        self.hp -= damage
        self.hit_flash_timer = self.hit_flash_duration
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
        return [c[1] for c in candidates[:3]]

    def update(self, game):
        if self.hit_flash_timer > 0:
            self.hit_flash_timer -= 1
        if game.first_wave_started:
            self.gold_generation_timer += 1
            if self.gold_generation_timer >= CASTLE_GOLD_INTERVAL:
                self.gold_generation_timer = 0
                game.money += CASTLE_GOLD_INCOME
        
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
                    target.take_damage(self.attack_damage, "ordinary", "castle")
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
        draw_square_dot(surface, RED, center, scaled(30), BLACK, max(1, scaled(2)))
        
        for proj in self.projectiles:
            _, pos = proj
            draw_square_dot(surface, GOLD, pos, scaled(14), WHITE, max(1, scaled(2)))
        
        bar_width = scaled(80)
        bar_y = rect.top - scaled(20)
        pygame.draw.rect(surface, RED, (int(HQ_CENTER_X - bar_width/2), bar_y, bar_width, scaled(10)))
        green_width = bar_width * (self.hp / self.max_hp)
        pygame.draw.rect(surface, YELLOW, (int(HQ_CENTER_X - bar_width/2), bar_y, int(green_width), scaled(10)))

    def draw_hit_flash(self, surface):
        if self.hit_flash_timer <= 0:
            return
        pulse = self.hit_flash_timer / self.hit_flash_duration
        max_alpha = int(120 * pulse)
        steps = 12
        edge = max(4, scaled(18))
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        for i in range(steps):
            alpha = max(0, int(max_alpha * (1 - i / steps)))
            thickness = edge
            offset = i * edge
            color = (255, 0, 0, alpha)
            pygame.draw.rect(overlay, color, (offset, offset, SCREEN_WIDTH - offset * 2, thickness))
            pygame.draw.rect(overlay, color, (offset, SCREEN_HEIGHT - offset - thickness, SCREEN_WIDTH - offset * 2, thickness))
            pygame.draw.rect(overlay, color, (offset, offset, thickness, SCREEN_HEIGHT - offset * 2))
            pygame.draw.rect(overlay, color, (SCREEN_WIDTH - offset - thickness, offset, thickness, SCREEN_HEIGHT - offset * 2))
        surface.blit(overlay, (0, 0))


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
        self.broken_towers = []
        self.selected_tower_type = None
        self.selected_tower = None
        self.selected_broken_tower = None
        self.hovered_broken_tower = None
        self.last_click_tower = None
        self.last_click_broken_tower = None
        self.last_click_time = 0
        self.elapsed_frames = 0
        self.tutorial_step = 0
        self.tutorial_done = False
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
        self.revealed_cells = set()
        self.scout_count = 0
        self.reveal_square_around((10, 10), CASTLE_REVEAL_SIZE)
        
        self.raider_spawn_timer = 0
        self.raider_spawn_cooldown = 1800
        
        self.wave_interval = WAVE_INTERVAL
        self.wave_interval_timer = 0
        self.wave_delay = 0
        self.wave_delay_timer = 0
        self.wave_delay_active = False
        self.waves_completed = 0
        
        self.total_waves = 3

        self.waves = self.generate_waves()
        self.spawn_queue = []
        self.current_wave_spawn_total = 0
        self.generate_veins()
        self.generate_broken_towers()

    def generate_veins(self):
        all_vein_cells = set()
        start_cells = [
            cell for cell in self.revealed_cells
            if not is_near_path_cell(cell, 1) and not is_hq_cell(cell)
        ]
        if start_cells:
            start_cell = min(start_cells, key=lambda cell: abs(cell[0] - 10) + abs(cell[1] - 10))
            self.veins.append(OreVein([start_cell]))
            all_vein_cells.add(start_cell)
        for _ in range(10):
            size = random.choices([1,2,3,4], weights=[15,40,30,15])[0]
            attempts = 0
            while attempts < 100:
                base = (random.randint(1, GRID_WIDTH-2), random.randint(1, GRID_HEIGHT-2))
                if is_near_path_cell(base, 1) or is_hq_cell(base):
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
                            if (nx,ny) not in vein_cells and not is_near_path_cell((nx,ny), 1) and not is_hq_cell((nx,ny)):
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
        self.update_discovered_veins()

    def generate_broken_towers(self):
        candidates = []
        for x in range(GRID_WIDTH):
            for y in range(GRID_HEIGHT):
                cell = (x, y)
                if is_any_path_cell(cell) or is_hq_cell(cell):
                    continue
                if self.get_vein_at(cell) is not None:
                    continue
                near_road = any(abs(x - px) + abs(y - py) == 1 for px, py in PATH_CELLS)
                if near_road:
                    candidates.append(cell)
        random.shuffle(candidates)
        for cell in candidates[:BROKEN_TOWER_COUNT]:
            self.broken_towers.append(BrokenTower(cell))

    def get_vein_at(self, cell):
        for vein in self.veins:
            if cell in vein.cells:
                return vein
        return None

    def get_broken_tower_at(self, cell):
        for broken in self.broken_towers:
            if broken.cell == cell:
                return broken
        return None

    def get_hovered_broken_tower(self):
        pos = pygame.mouse.get_pos()
        if not (FIELD_OFFSET_X <= pos[0] < FIELD_OFFSET_X + FIELD_WIDTH and FIELD_OFFSET_Y <= pos[1] < FIELD_OFFSET_Y + FIELD_HEIGHT):
            return None
        cell = cell_from_pos(pos)
        if not (0 <= cell[0] < GRID_WIDTH and 0 <= cell[1] < GRID_HEIGHT):
            return None
        broken = self.get_broken_tower_at(cell)
        if broken and self.is_revealed(cell):
            self.hovered_broken_tower = broken
            return broken
        self.hovered_broken_tower = None
        return None

    def get_active_broken_tower(self):
        hovered = self.get_hovered_broken_tower()
        if hovered:
            return hovered
        if self.selected_broken_tower in self.broken_towers:
            return self.selected_broken_tower
        if self.hovered_broken_tower in self.broken_towers:
            return self.hovered_broken_tower
        self.selected_broken_tower = None
        self.hovered_broken_tower = None
        return None

    def get_repair_button_rect(self):
        return pygame.Rect(scaled(20), SCREEN_HEIGHT - scaled(150), SIDE_PANEL_WIDTH - scaled(40), scaled(90))

    def update_discovered_veins(self):
        for vein in self.veins:
            if any(cell in self.revealed_cells for cell in vein.cells):
                vein.discovered = True

    def get_square_cells(self, center_cell, size):
        cx, cy = center_cell
        start = -(size // 2)
        end = size - size // 2
        cells = []
        for dx in range(start, end):
            for dy in range(start, end):
                cell = (cx + dx, cy + dy)
                if 0 <= cell[0] < GRID_WIDTH and 0 <= cell[1] < GRID_HEIGHT:
                    cells.append(cell)
        return cells

    def reveal_square_around(self, center_cell, size):
        for cell in self.get_square_cells(center_cell, size):
            self.revealed_cells.add(cell)
        if hasattr(self, "veins"):
            self.update_discovered_veins()

    def get_cardinal_neighbor_cells(self, center_cell):
        cx, cy = center_cell
        cells = []
        for dx, dy in ((0, -1), (1, 0), (0, 1), (-1, 0)):
            cell = (cx + dx, cy + dy)
            if 0 <= cell[0] < GRID_WIDTH and 0 <= cell[1] < GRID_HEIGHT:
                cells.append(cell)
        return cells

    def reveal_cardinal_neighbors(self, center_cell):
        for cell in self.get_cardinal_neighbor_cells(center_cell):
            self.revealed_cells.add(cell)
        if hasattr(self, "veins"):
            self.update_discovered_veins()

    def is_pos_revealed(self, pos):
        cell = cell_from_pos(pos)
        return 0 <= cell[0] < GRID_WIDTH and 0 <= cell[1] < GRID_HEIGHT and self.is_revealed(cell)

    def is_target_revealed(self, target):
        if isinstance(target, RaiderCamp):
            return self.is_pos_revealed((target.x, target.y))
        if hasattr(target, "pos"):
            return self.is_pos_revealed(target.pos)
        return True

    def is_revealed(self, cell):
        return cell in self.revealed_cells or is_hq_cell(cell)

    def get_active_miners(self):
        return [
            tower for tower in self.towers
            if (tower.tower_type == "miner" and tower.hp > 0 and tower.mining
                and not tower.attack_mode and tower.mode_transition_timer == 0)
        ]

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

    def get_scout_cost(self):
        return min(MAX_SCOUT_COST, BASE_SCOUT_COST + self.scout_count * SCOUT_COST_STEP)

    def reveal_area(self, center_cell):
        cost = self.get_scout_cost()
        if self.money >= cost:
            self.money -= cost
            self.scout_count += 1
            self.radar_animation_center = None
            self.radar_animation_active = False
            self.radar_animation_timer = 0
            self.radar_animation_radius = 0
            self.reveal_square_around(center_cell, SCOUT_REVEAL_SIZE)

    def draw_scout_preview(self, surface):
        if not self.radar_mode:
            return
        pos = pygame.mouse.get_pos()
        if not (FIELD_OFFSET_X <= pos[0] < FIELD_OFFSET_X + FIELD_WIDTH and
                FIELD_OFFSET_Y <= pos[1] < FIELD_OFFSET_Y + FIELD_HEIGHT):
            return

        center_cell = cell_from_pos(pos)
        cells = self.get_square_cells(center_cell, SCOUT_REVEAL_SIZE)
        if not cells:
            return

        inset = max(2, scaled(3))
        border = max(2, scaled(4))
        min_x = min(cell[0] for cell in cells)
        max_x = max(cell[0] for cell in cells)
        min_y = min(cell[1] for cell in cells)
        max_y = max(cell[1] for cell in cells)
        outline = pygame.Rect(
            FIELD_OFFSET_X + min_x * CELL_SIZE + inset,
            FIELD_OFFSET_Y + min_y * CELL_SIZE + inset,
            (max_x - min_x + 1) * CELL_SIZE - inset * 2,
            (max_y - min_y + 1) * CELL_SIZE - inset * 2
        )
        pygame.draw.rect(surface, CYAN, outline, border)

    def draw_tower_reveal_preview(self, surface):
        if self.radar_mode or not self.selected_tower_type:
            return
        pos = pygame.mouse.get_pos()
        if not (FIELD_OFFSET_X <= pos[0] < FIELD_OFFSET_X + FIELD_WIDTH and
                FIELD_OFFSET_Y <= pos[1] < FIELD_OFFSET_Y + FIELD_HEIGHT):
            return

        center_cell = cell_from_pos(pos)
        inset = max(2, scaled(4))
        border = max(2, scaled(4))
        for cell in self.get_cardinal_neighbor_cells(center_cell):
            rect = pygame.Rect(
                FIELD_OFFSET_X + cell[0] * CELL_SIZE + inset,
                FIELD_OFFSET_Y + cell[1] * CELL_SIZE + inset,
                CELL_SIZE - inset * 2,
                CELL_SIZE - inset * 2
            )
            pygame.draw.rect(surface, CYAN, rect, border)

    def get_tower_preview_range(self, tower_type):
        ranges = {
            "archer": scaled(150),
            "cannon": scaled(150),
            "mortar": scaled(260),
            "greek_fire": scaled(90),
            "miner": scaled(100),
        }
        return ranges.get(tower_type, 0)

    def draw_range_outline(self, surface, center_x, center_y, range_radius, color):
        cells = set()
        for x in range(GRID_WIDTH):
            for y in range(GRID_HEIGHT):
                cell_center = (
                    FIELD_OFFSET_X + x * CELL_SIZE + CELL_SIZE // 2,
                    FIELD_OFFSET_Y + y * CELL_SIZE + CELL_SIZE // 2
                )
                if math.hypot(cell_center[0] - center_x, cell_center[1] - center_y) <= range_radius:
                    cells.add((x, y))

        width = max(3, scaled(6))
        for x, y in cells:
            left = FIELD_OFFSET_X + x * CELL_SIZE
            top = FIELD_OFFSET_Y + y * CELL_SIZE
            right = left + CELL_SIZE
            bottom = top + CELL_SIZE
            if (x, y - 1) not in cells:
                pygame.draw.line(surface, color, (left, top), (right, top), width)
            if (x + 1, y) not in cells:
                pygame.draw.line(surface, color, (right, top), (right, bottom), width)
            if (x, y + 1) not in cells:
                pygame.draw.line(surface, color, (right, bottom), (left, bottom), width)
            if (x - 1, y) not in cells:
                pygame.draw.line(surface, color, (left, bottom), (left, top), width)

    def draw_build_range_preview(self, surface):
        if self.radar_mode or not self.selected_tower_type:
            return
        if self.selected_tower_type == "miner":
            return
        pos = pygame.mouse.get_pos()
        if not (FIELD_OFFSET_X <= pos[0] < FIELD_OFFSET_X + FIELD_WIDTH and
                FIELD_OFFSET_Y <= pos[1] < FIELD_OFFSET_Y + FIELD_HEIGHT):
            return

        cell = cell_from_pos(pos)
        center_x = FIELD_OFFSET_X + cell[0] * CELL_SIZE + CELL_SIZE // 2
        center_y = FIELD_OFFSET_Y + cell[1] * CELL_SIZE + CELL_SIZE // 2
        range_radius = self.get_tower_preview_range(self.selected_tower_type)
        if range_radius > 0:
            self.draw_range_outline(surface, center_x, center_y, range_radius, RED)

    def draw_selected_tower_range(self, surface):
        if not self.selected_tower or self.selected_tower.hp <= 0:
            return
        if self.selected_tower.tower_type == "miner" and not self.selected_tower.attack_mode:
            return
        if self.selected_tower.range > 0 and self.selected_tower.damage > 0:
            self.draw_range_outline(surface, self.selected_tower.x, self.selected_tower.y, self.selected_tower.range, RED)

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
                            self.revealed_cells.add((cell_x, cell_y))
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
        center_cell = ((cx - FIELD_OFFSET_X) // CELL_SIZE, (cy - FIELD_OFFSET_Y) // CELL_SIZE)
        reveal_progress = self.radar_animation_timer / self.radar_animation_duration
        max_steps = max(1, SCOUT_REVEAL_SIZE // 2)
        active_steps = int(max_steps * reveal_progress) + 1
        alpha = max(45, 190 - int(120 * reveal_progress))
        for dx in range(-active_steps, active_steps + 1):
            for dy in range(-active_steps, active_steps + 1):
                cell = (center_cell[0] + dx, center_cell[1] + dy)
                if 0 <= cell[0] < GRID_WIDTH and 0 <= cell[1] < GRID_HEIGHT:
                    rect = pygame.Rect(
                        FIELD_OFFSET_X + cell[0] * CELL_SIZE + scaled(3),
                        FIELD_OFFSET_Y + cell[1] * CELL_SIZE + scaled(3),
                        CELL_SIZE - scaled(6),
                        CELL_SIZE - scaled(6)
                    )
                    pygame.draw.rect(surface, (0, 255, 255, alpha), rect)
                    pygame.draw.rect(surface, CYAN, rect, max(1, scaled(2)))
        if self.radar_animation_timer % 10 < 5:
            draw_square_dot(surface, CYAN, (cx, cy), scaled(14), WHITE, max(1, scaled(2)))

    def generate_waves(self):
        waves = [
            [("soldier", 36), ("rider", 12)],
            [("soldier", 36), ("rider", 24), ("knight", 4), ("cart", 2)],
            [("soldier", 32), ("rider", 24), ("knight", 20), ("cart", 4)],
        ]
        return waves

    def start_wave(self, early=False):
        if self.wave <= self.total_waves and not self.wave_active and not self.wave_delay_active:
            is_first_wave = not self.first_wave_started
            if early and self.first_wave_started:
                self.ore += 15
                self.money += 30
            
            if is_first_wave:
                self.first_wave_started = True
            
            self.spawn_queue = []
            for enemy_type, count in self.waves[self.wave - 1]:
                for _ in range(count):
                    lane = random.choice(list(LANES.keys()))
                    self.spawn_queue.append((enemy_type, lane))
            random.shuffle(self.spawn_queue)
            if self.wave == self.total_waves:
                lane = random.choice(list(LANES.keys()))
                boss_index = max(0, min(len(self.spawn_queue), int(len(self.spawn_queue) * 0.7)))
                self.spawn_queue.insert(boss_index, ("duke", lane))
            self.current_wave_spawn_total = len(self.spawn_queue)
            
            self.wave_active = True
            self.wave_timer = 39
            self.wave_delay = FIRST_WAVE_DELAY if is_first_wave else 0
            self.wave_delay_active = is_first_wave
            self.wave_delay_timer = 0
            self.wave_interval_timer = 0

    def build_tower(self, tower_type, cell):
        if self.money < TOWER_COST[tower_type]:
            return False
        if not self.is_revealed(cell):
            return False
        for t in self.towers:
            if t.cell == cell:
                return False
        if self.get_broken_tower_at(cell) is not None:
            return False
        if is_hq_cell(cell):
            return False
        if tower_type == "miner":
            vein = self.get_vein_at(cell)
            if not vein or not vein.discovered or vein.depleted():
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
        self.reveal_cardinal_neighbors(cell)
        self.money -= TOWER_COST[tower_type]
        return True

    def upgrade_tower(self):
        if self.selected_tower and self.selected_tower.hp > 0:
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
                refund = int(t.total_investment * 0.5)
                self.money += refund
                if t == self.selected_tower:
                    self.selected_tower = None
                self.towers.remove(t)
                return True
        return False

    def toggle_miner_mode(self):
        if self.selected_tower and self.selected_tower.tower_type == "miner" and self.selected_tower.hp > 0:
            miner = self.selected_tower
            if miner.mode_transition_timer > 0:
                return False
            miner.mode_transition_timer = miner.mode_transition_max
            return True
        return False

    def get_elapsed_time_text(self):
        total_seconds = self.elapsed_frames // 60
        minutes = total_seconds // 60
        seconds = total_seconds % 60
        return f"{minutes:02}:{seconds:02}"

    def tutorial_active(self):
        return self.first_wave_started and not self.tutorial_done

    def get_tutorial_button_rect(self):
        panel_w = min(FIELD_WIDTH - scaled(80), scaled(920))
        panel_h = scaled(230)
        panel_x = FIELD_OFFSET_X + (FIELD_WIDTH - panel_w) // 2
        panel_y = SCREEN_HEIGHT - panel_h - scaled(35)
        btn_w = scaled(170)
        btn_h = scaled(46)
        return pygame.Rect(
            panel_x + panel_w - btn_w - scaled(24),
            panel_y + panel_h - btn_h - scaled(20),
            btn_w,
            btn_h
        )

    def advance_tutorial(self):
        if not self.tutorial_active():
            return False
        self.tutorial_step += 1
        if self.tutorial_step >= 5:
            self.tutorial_done = True
            self.tutorial_step = 4
        return True

    def wrap_text(self, text, used_font, max_width):
        words = text.split()
        lines = []
        current = ""
        for word in words:
            candidate = word if not current else f"{current} {word}"
            if used_font.size(candidate)[0] <= max_width:
                current = candidate
            else:
                if current:
                    lines.append(current)
                current = word
        if current:
            lines.append(current)
        return lines

    def draw_fog(self, surface):
        for x in range(GRID_WIDTH):
            for y in range(GRID_HEIGHT):
                if not self.is_revealed((x, y)):
                    rect = pygame.Rect(
                        FIELD_OFFSET_X + x * CELL_SIZE,
                        FIELD_OFFSET_Y + y * CELL_SIZE,
                        CELL_SIZE,
                        CELL_SIZE
                    )
                    pygame.draw.rect(surface, (210, 215, 220), rect)
                    pygame.draw.rect(surface, (165, 170, 176), rect, max(1, scaled(1)))

    def update(self):
        if self.defeat or self.victory:
            return
        if self.tutorial_active():
            return
        if self.first_wave_started:
            self.elapsed_frames += 1

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
                    raider_type = "normal"
                    raider = Raider(target, spawn_pos, from_camp=False, raider_type=raider_type)
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
                if e_type == "duke":
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
                    if enemy.enemy_type == "cart":
                        enemy.spawn_soldiers(self)
                    if enemy.hp <= 0:
                        self.money += int(enemy.reward * ENEMY_REWARD_MULTIPLIER)
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
                        self.money += int(raider.reward * ENEMY_REWARD_MULTIPLIER)
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
            self.wave_interval_timer = 0
            if self.wave > self.total_waves:
                self.victory = True
            else:
                self.post_wave_event()

    def post_wave_event(self):
        pass

    def draw_tutorial_overlay(self, surface):
        if not self.tutorial_active():
            return

        stage = max(0, min(4, self.tutorial_step))

        right_x = SCREEN_WIDTH - SIDE_PANEL_WIDTH + scaled(15)
        btn_width = SIDE_PANEL_WIDTH - scaled(30)
        start_y = scaled(30)
        btn_gap = scaled(15)
        tower_types = ["archer", "cannon", "mortar", "greek_fire", "miner"]
        num_btns = len(tower_types) + 3
        max_btn_height = (SCREEN_HEIGHT - start_y*2 - btn_gap*(num_btns-1)) // num_btns
        btn_height = max(60, min(100, max_btn_height))
        step = btn_height + btn_gap

        resource_rect = pygame.Rect(scaled(8), scaled(35), SIDE_PANEL_WIDTH - scaled(16), scaled(330))
        scout_rect = pygame.Rect(right_x, start_y + (len(tower_types) + 2) * step, btn_width, btn_height)
        miner_rect = pygame.Rect(right_x, start_y + 3 * step, btn_width, btn_height)
        tower_rect = pygame.Rect(right_x, start_y, btn_width, btn_height * 3 + btn_gap * 2)
        road_cell = min(PATH_CELLS, key=lambda c: abs(c[0] - 10) + abs(c[1] - 10))
        road_rect = pygame.Rect(
            FIELD_OFFSET_X + road_cell[0] * CELL_SIZE,
            FIELD_OFFSET_Y + road_cell[1] * CELL_SIZE,
            CELL_SIZE,
            CELL_SIZE
        )

        steps = [
            (resource_rect, "Resources", "Gold buys scouts, buildings, and upgrades. Ore is ammo for shots."),
            (scout_rect, "Scout", "Click Scout, then click fog on the map. It reveals a 3x3 square."),
            (miner_rect, "Mines", "Build Miner on revealed ore veins. Miners create Ore for your towers."),
            (tower_rect, "Towers", "Pick a combat building here, then place it on open land."),
            (road_rect, "Roads", "Brown road tiles are for enemies. You cannot build on roads."),
        ]
        target_rect, title, body = steps[stage]

        pulse = 3 + (self.elapsed_frames // 12) % 2
        highlight_rect = target_rect.inflate(scaled(14), scaled(14))
        highlight_rect.clamp_ip(pygame.Rect(0, 0, SCREEN_WIDTH, SCREEN_HEIGHT))

        dim_color = (0, 0, 0, 165)
        dim_rects = [
            pygame.Rect(0, 0, SCREEN_WIDTH, highlight_rect.top),
            pygame.Rect(0, highlight_rect.bottom, SCREEN_WIDTH, SCREEN_HEIGHT - highlight_rect.bottom),
            pygame.Rect(0, highlight_rect.top, highlight_rect.left, highlight_rect.height),
            pygame.Rect(highlight_rect.right, highlight_rect.top, SCREEN_WIDTH - highlight_rect.right, highlight_rect.height),
        ]
        for dim_rect in dim_rects:
            if dim_rect.width > 0 and dim_rect.height > 0:
                dim = pygame.Surface((dim_rect.width, dim_rect.height), pygame.SRCALPHA)
                dim.fill(dim_color)
                surface.blit(dim, dim_rect)

        highlight = pygame.Surface((highlight_rect.width, highlight_rect.height), pygame.SRCALPHA)
        pygame.draw.rect(highlight, (255, 245, 120, 28), highlight.get_rect())
        surface.blit(highlight, highlight_rect)
        pygame.draw.rect(surface, GOLD, highlight_rect, max(2, scaled(3 + pulse)))

        panel_w = min(FIELD_WIDTH - scaled(80), scaled(920))
        panel_h = scaled(230)
        panel_x = FIELD_OFFSET_X + (FIELD_WIDTH - panel_w) // 2
        panel_y = SCREEN_HEIGHT - panel_h - scaled(35)
        panel_rect = pygame.Rect(panel_x, panel_y, panel_w, panel_h)

        panel = pygame.Surface((panel_w, panel_h), pygame.SRCALPHA)
        panel.fill((20, 24, 28, 238))
        surface.blit(panel, (panel_x, panel_y))
        pygame.draw.rect(surface, CYAN, panel_rect, max(2, scaled(3)))

        title_txt = font_medium.render(f"{stage + 1}/5  {title}", True, GOLD)
        surface.blit(title_txt, (panel_x + scaled(28), panel_y + scaled(22)))
        text_x = panel_x + scaled(28)
        text_y = panel_y + scaled(88)
        text_max_w = panel_w - scaled(230)
        for line in self.wrap_text(body, font_small, text_max_w):
            body_txt = font_small.render(line, True, WHITE)
            surface.blit(body_txt, (text_x, text_y))
            text_y += scaled(42)

        next_rect = self.get_tutorial_button_rect()
        pygame.draw.rect(surface, GOLD, next_rect)
        pygame.draw.rect(surface, BLACK, next_rect, max(1, scaled(2)))
        button_text = "Done" if stage == 4 else "Next"
        button_txt = font_small.render(button_text, True, BLACK)
        surface.blit(
            button_txt,
            (
                next_rect.centerx - button_txt.get_width() // 2,
                next_rect.centery - button_txt.get_height() // 2
            )
        )

        start = (panel_rect.centerx, panel_rect.top)
        end = target_rect.center
        pygame.draw.line(surface, GOLD, start, end, max(4, scaled(7)))
        angle = math.atan2(end[1] - start[1], end[0] - start[0])
        head = scaled(22)
        left = (
            end[0] - math.cos(angle - 0.55) * head,
            end[1] - math.sin(angle - 0.55) * head
        )
        right = (
            end[0] - math.cos(angle + 0.55) * head,
            end[1] - math.sin(angle + 0.55) * head
        )
        pygame.draw.polygon(surface, GOLD, [end, left, right])

    def draw_ui(self, surface):
        pygame.draw.rect(surface, PANEL_BG, (0, 0, SIDE_PANEL_WIDTH, SCREEN_HEIGHT))
        pygame.draw.rect(surface, PANEL_BG, (SCREEN_WIDTH - SIDE_PANEL_WIDTH, 0, SIDE_PANEL_WIDTH, SCREEN_HEIGHT))

        y_offset = scaled(60)
        x_indent = scaled(25)
        line_gap = scaled(80)

        texts = [
            f"Gold: {self.money}",
            f"Ore: {self.ore}",
            f"Wave: {self.wave}/{self.total_waves}",
            f"Time: {self.get_elapsed_time_text()}"
        ]
        colors = [YELLOW, ORE_COLOR, WHITE, CYAN]
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

        active_broken = self.get_active_broken_tower()
        if active_broken:
            repair_rect = self.get_repair_button_rect()
            can_repair = self.money >= BROKEN_TOWER_REPAIR_COST
            repair_color = GREEN if can_repair else LIGHT_GRAY
            title = font_small.render("Broken Tower", True, WHITE)
            surface.blit(title, (repair_rect.x, repair_rect.y - scaled(42)))
            pygame.draw.rect(surface, repair_color, repair_rect)
            pygame.draw.rect(surface, BLACK, repair_rect, max(1, scaled(2)))
            label = font_small.render("Repair", True, BLACK)
            price = font_small.render(f"${BROKEN_TOWER_REPAIR_COST}", True, BLACK)
            surface.blit(label, (repair_rect.x + scaled(10), repair_rect.y + scaled(12)))
            surface.blit(price, (repair_rect.x + scaled(10), repair_rect.y + scaled(50)))

        right_x = SCREEN_WIDTH - SIDE_PANEL_WIDTH + scaled(15)
        btn_width = SIDE_PANEL_WIDTH - scaled(30)
        start_y = scaled(30)
        btn_gap = scaled(15)
        tower_types = ["archer", "cannon", "mortar", "greek_fire", "miner"]
        show_miner_mode = self.selected_tower and self.selected_tower.tower_type == "miner"
        num_btns = len(tower_types) + 3 + (1 if show_miner_mode else 0)
        max_btn_height = (SCREEN_HEIGHT - start_y*2 - btn_gap*(num_btns-1)) // num_btns
        btn_height = max(60, min(100, max_btn_height))

        btn_y = start_y
        for ttype in tower_types:
            rect = pygame.Rect(right_x, btn_y, btn_width, btn_height)
            color = GOLD if self.selected_tower_type == ttype else LIGHT_GRAY
            pygame.draw.rect(surface, color, rect)
            pygame.draw.rect(surface, BLACK, rect, 2)
            name_txt = font_small.render(TOWER_DISPLAY_NAMES.get(ttype, ttype.capitalize()), True, BLACK)
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

        if show_miner_mode:
            miner_rect = pygame.Rect(right_x, btn_y, btn_width, btn_height)
            if self.selected_tower.mode_transition_timer > 0:
                mode_text = "Switching..."
                color = CYAN
            elif self.selected_tower.closed:
                mode_text = "Open Miner"
                color = GREEN
            else:
                mode_text = "Close Miner"
                color = RED
            pygame.draw.rect(surface, color, miner_rect)
            surface.blit(font_small.render(mode_text, True, BLACK), (miner_rect.x + 8, miner_rect.y + btn_height//3))
            pygame.draw.rect(surface, BLACK, miner_rect, 2)
            btn_y += btn_height + btn_gap

        radar_rect = pygame.Rect(right_x, btn_y, btn_width, btn_height)
        color = CYAN if self.radar_mode else LIGHT_GRAY
        pygame.draw.rect(surface, color, radar_rect)
        pygame.draw.rect(surface, BLACK, radar_rect, 2)
        surface.blit(font_small.render(f"Scout (${self.get_scout_cost()})", True, BLACK), (radar_rect.x + 8, radar_rect.y + btn_height//3))

        if self.selected_tower and self.selected_tower.hp > 0:
            rect = pygame.Rect(self.selected_tower.x - scaled(25), self.selected_tower.y - scaled(25), scaled(50), scaled(50))
            pygame.draw.rect(surface, YELLOW, rect, scaled(3))

        active_broken = self.get_active_broken_tower()
        if active_broken:
            rect = pygame.Rect(active_broken.x - scaled(25), active_broken.y - scaled(25), scaled(50), scaled(50))
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
            txt = font_large.render("VICTORY! Duke is defeated.", True, GOLD)
            txt_rect = txt.get_rect(center=(SCREEN_WIDTH//2, SCREEN_HEIGHT//2))
            surface.blit(txt, txt_rect)
            time_txt = font_medium.render(f"Time: {self.get_elapsed_time_text()}", True, CYAN)
            time_rect = time_txt.get_rect(center=(SCREEN_WIDTH//2, SCREEN_HEIGHT//2 + scaled(90)))
            surface.blit(time_txt, time_rect)
        elif self.defeat:
            txt = font_large.render("DEFEAT", True, RED)
            txt_rect = txt.get_rect(center=(SCREEN_WIDTH//2, SCREEN_HEIGHT//2))
            surface.blit(txt, txt_rect)
            time_txt = font_medium.render(f"Time: {self.get_elapsed_time_text()}", True, CYAN)
            time_rect = time_txt.get_rect(center=(SCREEN_WIDTH//2, SCREEN_HEIGHT//2 + scaled(90)))
            surface.blit(time_txt, time_rect)


def get_play_button_rect():
    btn_w = max(scaled(300), SCREEN_WIDTH // 5)
    btn_h = max(scaled(90), SCREEN_HEIGHT // 14)
    return pygame.Rect(
        (SCREEN_WIDTH - btn_w) // 2,
        int(SCREEN_HEIGHT * 0.58),
        btn_w,
        btn_h
    )


def draw_main_menu(surface):
    surface.fill((22, 35, 34))
    title = font_large.render("The Eternity Covenant", True, GOLD)
    title_rect = title.get_rect(center=(SCREEN_WIDTH // 2, int(SCREEN_HEIGHT * 0.28)))
    surface.blit(title, title_rect)

    subtitle = font_medium.render("Build. Scout. Hold the road.", True, WHITE)
    subtitle_rect = subtitle.get_rect(center=(SCREEN_WIDTH // 2, int(SCREEN_HEIGHT * 0.39)))
    surface.blit(subtitle, subtitle_rect)

    play_rect = get_play_button_rect()
    mouse_over = play_rect.collidepoint(pygame.mouse.get_pos())
    play_color = CYAN if mouse_over else LIGHT_GRAY
    pygame.draw.rect(surface, play_color, play_rect)
    pygame.draw.rect(surface, BLACK, play_rect, scaled(4))

    play_txt = font_medium.render("PLAY", True, BLACK)
    play_txt_rect = play_txt.get_rect(center=play_rect.center)
    surface.blit(play_txt, play_txt_rect)

    hint = font_small.render("After Play: 10 seconds before wave 1", True, CYAN)
    hint_rect = hint.get_rect(center=(SCREEN_WIDTH // 2, play_rect.bottom + scaled(60)))
    surface.blit(hint, hint_rect)


game = Game()
game_state = "menu"
running = True

while running:
    screen.fill(BLACK)

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                running = False

        if game_state == "menu":
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                if get_play_button_rect().collidepoint(pygame.mouse.get_pos()):
                    game = Game()
                    game.start_wave(early=False)
                    game_state = "playing"
            if event.type == pygame.KEYDOWN and event.key in (pygame.K_RETURN, pygame.K_SPACE):
                game = Game()
                game.start_wave(early=False)
                game_state = "playing"
            continue

        if event.type == pygame.MOUSEBUTTONDOWN:
            pos = pygame.mouse.get_pos()
            if game.tutorial_active() and event.button == 1:
                if game.get_tutorial_button_rect().collidepoint(pos):
                    game.advance_tutorial()
                continue
            if event.button == 3:
                if SIDE_PANEL_WIDTH <= pos[0] < SCREEN_WIDTH - SIDE_PANEL_WIDTH:
                    cell = cell_from_pos(pos)
                    if 0 <= cell[0] < GRID_WIDTH and 0 <= cell[1] < GRID_HEIGHT:
                        game.sell_tower(cell)
                continue
            if event.button != 1:
                continue
            
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
                tower_types = ["archer", "cannon", "mortar", "greek_fire", "miner"]
                show_miner_mode = game.selected_tower and game.selected_tower.tower_type == "miner"
                num_btns = len(tower_types) + 3 + (1 if show_miner_mode else 0)
                max_btn_height = (SCREEN_HEIGHT - start_y*2 - scaled(15)*(num_btns-1)) // num_btns
                btn_height = max(60, min(100, max_btn_height))
                btn_gap = scaled(15)

                btn_y = start_y
                panel_handled = False
                for ttype in tower_types:
                    rect = pygame.Rect(right_x, btn_y, btn_width, btn_height)
                    if rect.collidepoint(pos):
                        game.selected_tower_type = ttype
                        game.selected_tower = None
                        game.selected_broken_tower = None
                        game.radar_mode = False
                        panel_handled = True
                        break
                    btn_y += btn_height + btn_gap

                if not panel_handled:
                    upgrade_rect = pygame.Rect(right_x, btn_y, btn_width, btn_height)
                    if upgrade_rect.collidepoint(pos):
                        game.upgrade_tower()
                        panel_handled = True
                    btn_y += btn_height + btn_gap

                if not panel_handled:
                    start_rect = pygame.Rect(right_x, btn_y, btn_width, btn_height)
                    if start_rect.collidepoint(pos):
                        can_start = not game.wave_active and not game.wave_delay_active and game.wave <= game.total_waves and not game.victory and not game.defeat
                        if can_start:
                            game.start_wave(early=True)
                        panel_handled = True
                    btn_y += btn_height + btn_gap

                if show_miner_mode and not panel_handled:
                    miner_rect = pygame.Rect(right_x, btn_y, btn_width, btn_height)
                    if miner_rect.collidepoint(pos):
                        game.toggle_miner_mode()
                        panel_handled = True
                    btn_y += btn_height + btn_gap

                if not panel_handled:
                    radar_rect = pygame.Rect(right_x, btn_y, btn_width, btn_height)
                    if radar_rect.collidepoint(pos):
                        game.radar_mode = not game.radar_mode
                        game.selected_tower_type = None
                        game.selected_tower = None
                        game.selected_broken_tower = None
            elif pos[0] < SIDE_PANEL_WIDTH:
                repair_target = game.get_active_broken_tower()
                if repair_target and game.get_repair_button_rect().collidepoint(pos):
                    repair_target.repair(game)
            else:
                cell = cell_from_pos(pos)
                if 0 <= cell[0] < GRID_WIDTH and 0 <= cell[1] < GRID_HEIGHT:
                    if game.radar_mode:
                        game.reveal_area(cell)
                    else:
                        broken = game.get_broken_tower_at(cell)
                        if broken and game.is_revealed(cell):
                            now = pygame.time.get_ticks()
                            if game.last_click_broken_tower is broken and now - game.last_click_time <= 350:
                                broken.repair(game)
                                game.last_click_time = 0
                            else:
                                game.selected_broken_tower = broken
                                game.selected_tower = None
                                game.selected_tower_type = None
                                game.last_click_broken_tower = broken
                                game.last_click_time = now
                            continue
                        for t in game.towers:
                            if t.cell == cell and t.hp > 0:
                                now = pygame.time.get_ticks()
                                if game.last_click_tower is t and now - game.last_click_time <= 350:
                                    game.selected_tower = t
                                    game.upgrade_tower()
                                    game.last_click_tower = None
                                    game.last_click_time = 0
                                else:
                                    game.selected_tower = t
                                    game.last_click_tower = t
                                    game.last_click_time = now
                                game.selected_tower_type = None
                                game.selected_broken_tower = None
                                break
                        else:
                            if game.selected_tower_type:
                                game.build_tower(game.selected_tower_type, cell)
                                game.selected_broken_tower = None

        if event.type == pygame.KEYDOWN:
            if game.tutorial_active() and event.key in (pygame.K_RETURN, pygame.K_SPACE):
                game.advance_tutorial()
                continue
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
                if game.radar_mode:
                    game.selected_tower_type = None
                    game.selected_tower = None
                    game.selected_broken_tower = None

    if game_state == "menu":
        draw_main_menu(screen)
        pygame.display.flip()
        clock.tick(60)
        continue

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

    for broken in game.broken_towers:
        broken.draw(screen)

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

    game.draw_fog(screen)
    game.hq.draw_hit_flash(screen)

    game.draw_scout_preview(screen)
    game.draw_build_range_preview(screen)
    game.draw_selected_tower_range(screen)

    game.draw_radar_animation(screen)

    game.draw_ui(screen)
    game.draw_tutorial_overlay(screen)

    pygame.display.flip()
    clock.tick(60)

pygame.quit()
sys.exit()