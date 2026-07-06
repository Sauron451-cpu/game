import pygame
import math
import random
import sys
import heapq

pygame.init()

info = pygame.display.Info()
SCREEN_WIDTH = info.current_w
SCREEN_HEIGHT = info.current_h
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.FULLSCREEN)
pygame.display.set_caption("The Eternity Covenant")
clock = pygame.time.Clock()

GAME_TITLE = "The Eternity Covenant"

SCALE = SCREEN_HEIGHT / 1500

font_size_small = max(30, int(50 * SCALE))
font_size_medium = max(40, int(66 * SCALE))
font_size_large = max(58, int(98 * SCALE))
font_small = pygame.font.Font(None, font_size_small)
font_medium = pygame.font.Font(None, font_size_medium)
font_large = pygame.font.Font(None, font_size_large)

SIDE_PANEL_WIDTH = max(280, min(int(SCREEN_WIDTH * 0.23), 430))
AVAILABLE_MAP_WIDTH = SCREEN_WIDTH - 2 * SIDE_PANEL_WIDTH
VIEWPORT_SIZE = min(AVAILABLE_MAP_WIDTH, SCREEN_HEIGHT)
VIEWPORT_X = SIDE_PANEL_WIDTH + (AVAILABLE_MAP_WIDTH - VIEWPORT_SIZE) // 2
VIEWPORT_Y = (SCREEN_HEIGHT - VIEWPORT_SIZE) // 2
VIEWPORT_WIDTH = VIEWPORT_SIZE
VIEWPORT_HEIGHT = VIEWPORT_SIZE

MAP_ROWS = [
    "................................HHH....................",
    "................................HHH....................",
    "................................HHH....................",
    ".................................#.....................",
    ".......#########......########...#.....................",
    ".......#.......#......#......#...######................",
    ".......#.......#......#......#...#....#................",
    ".......####....########......#...#....#................",
    "..........#..................#####....##########.......",
    "..........#....................................#.......",
    "..........#...................................C#.......",
    "..........#..................................###.......",
    "..........#..................................#.........",
    ".....$....#####..............................#.........",
    "..............#..............................#.........",
    "..............#..............................#.........",
    "..............#..#######.....................#.........",
    "..............#..#.....#..........########...#.........",
    ".....#######..####.....#..........#......#...#.........",
    ".....#C....#...........#...####...#......#####.........",
    ".....#.....#...........#====~~=...#....................",
    ".....#.....#..........~~~~~=~~==###....................",
    ".....#.....#.........~~~~~~=~~~~~~.....................",
    ".....###...#######...~~CC~~=~~CC~~.....................",
    ".......#.........#..~~~CC~~=~~CC~~~.........$..........",
    ".......#.........#..~~~~~=====~~~~~....................",
    ".......#.........#..~~~~~=GGG=~~~~~....................",
    ".......#.........#..~=====GGG=~~~~~....................",
    ".......#.......#####==~~~=GGG=~~~~~.###############....",
    ".......#.......#....~~~~~=====~~~~~.#.............#....",
    ".......#.......#....~~~CC~~=~~CC~~~.#.............#....",
    ".......#.......#.....~~CC~~=~~CC~~..###...........#....",
    ".......#.......#####.~~~~~~=~~~~~~....#...........#....",
    ".......#...........#..~~~~~====~~.....#.......#####....",
    "...#####...........#....~~~=~~=.......#.......#........",
    "...#...............#.......#..#########.......#........",
    "...#...............#.......#..................#........",
    "...###.............#.......#..................#........",
    ".....#.............###.....#..................#........",
    "HHH..#...............#.....#..................#........",
    "HHH#####.............#.....#..................#........",
    "HHH....#.............#.....######.............#####....",
    ".......#......$......#..........#.................#....",
    ".......#.............#..........#.................#....",
    ".......#.............#..........#.................#....",
    ".......#.............#..........#...............###....",
    ".......#.............#..........#.....#####.....#......",
    ".......###############..........#.....#...#.....#......",
    "..............................###.....#...#.....#...HHH",
    "..............................#.......#...##########HHH",
    "..............................#.......#.............HHH",
    "..............................#......C#................",
    "..............................#########................",
    ".......................................................",
    ".......................................................",
]
GRID_WIDTH, GRID_HEIGHT = len(MAP_ROWS[0]), len(MAP_ROWS)
CELL_SIZE = max(28, int(54 * SCALE))
FIELD_OFFSET_X = 0
FIELD_OFFSET_Y = 0
FIELD_WIDTH = CELL_SIZE * GRID_WIDTH
FIELD_HEIGHT = CELL_SIZE * GRID_HEIGHT
FULL_MAP_ATTACK_RANGE = math.hypot(FIELD_WIDTH, FIELD_HEIGHT) + CELL_SIZE
MIN_ZOOM = max(VIEWPORT_WIDTH / FIELD_WIDTH, VIEWPORT_HEIGHT / FIELD_HEIGHT)
MAX_ZOOM = 1.9
START_ZOOM = min(MAX_ZOOM, max(MIN_ZOOM, 0.85))
EDGE_SCROLL_SIZE = max(16, int(22 * SCALE))
CAMERA_DRAG_THRESHOLD = max(6, int(10 * SCALE))

TOWER_COST = {
    "lamp": 200,
    "beacon": 100
}
TOWER_UPGRADE_COST = {
    "lamp": 200,
    "beacon": 140,
    "cannon": 200
}

STARTING_MONEY = 210
GENERATOR_INCOME_BY_LEVEL = {1: 4.25, 2: 7.65, 3: 15.3, 4: 30.6}
GENERATOR_TOWER_LIMIT_BY_LEVEL = {1: 6, 2: 10, 3: 13, 4: 16}
GENERATOR_UPGRADE_COST = {1: 300, 2: 600, 3: 1200}
ARTILLERY_COST = 400
REPAIR_CANNON_COST = 150

BUILDABLE_TOWER_TYPES = ["beacon", "lamp"]
LIGHT_TOWER_TYPES = {"lamp", "beacon"}
TOWER_DISPLAY_NAMES = {
    "lamp": "Farseeker",
    "beacon": "Observer",
    "cannon": "Cannon",
}
CANNON_DAMAGE_MULTIPLIER = 0.9
CANNON_LEVEL_DAMAGE_BONUS = 0.05
CANNON_SPECIALIZATION_SOURCES = {"sniper", "scatter", "gatling"}
LIGHT_SIZE_BY_LEVEL = {1: 5, 2: 7, 3: 9, 4: 11}
LAMP_LIGHT_WIDTH = 3
ACTION_COOLDOWN_FRAMES = {
    "build": 18,
    "rotate": 60,
    "sell": 20,
    "change_specialization": 150,
}
DIRECTIONS = [(0, -1), (1, 0), (0, 1), (-1, 0)]
ROTATABLE_LIGHT_TYPES = {"lamp"}
ROUTE_LIGHT_LOOKAHEAD_CELLS = 9
ROUTE_LIGHT_SWITCH_MIN_LIT = 4
ROUTE_LIGHT_SWITCH_RATIO = 0.45
ADAPTIVE_ROUTE_WAVE_INTERVAL = 3
ENEMY_COUNT_BASE_PER_HIVE = 5
ENEMY_COUNT_GROWTH_PER_WAVE = 0.5
ENEMY_STRENGTH_MULTIPLIER = 1.05
ENEMY_HEALTH_MULTIPLIER = 2.0
ENEMY_SPEED_MULTIPLIER = 1.5
ENEMY_HP_GROWTH_PER_WAVE = 0.20
ENEMY_SPEED_GROWTH_PER_WAVE = 0.04
ENEMY_DAMAGE_GROWTH_PER_WAVE = 0.10
ENEMY_REWARD_MULTIPLIER = 1.20
ENEMY_REWARD_GROWTH_PER_WAVE = 0.10
ENEMY_DARK_SPEED_MULTIPLIER = 7.0
DIMMER_START_WAVE = 3
DIMMER_LAMP_DISABLE_RADIUS = 3
DIMMER_LAMP_DISABLE_DURATION = 120
DIMMER_LAMP_DISABLE_COOLDOWN = 360

BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
GREEN = (34, 139, 34)
BROWN = (139, 69, 19)
GRAY = (128, 128, 128)
RED = (255, 0, 0)
YELLOW = (255, 255, 0)
PURPLE = (128, 0, 128)
CYAN = (0, 255, 255)
GOLD = (255, 215, 0)
UI_PANEL = (18, 22, 30)
UI_CARD = (35, 42, 55)
UI_CARD_HOT = (44, 56, 76)
UI_STROKE = (92, 116, 140)
UI_TEXT_DIM = (170, 185, 198)
UI_GOOD = (102, 235, 142)
UI_WARN = (255, 202, 78)
UI_BAD = (255, 100, 106)
LIGHT_BLUE = (130, 220, 255)
GENERATOR_BLUE = (80, 245, 255)
GENERATOR_RED = (248, 56, 0)
CANNON_BLUE = (0, 120, 248)
FOG_WHITE = (12, 16, 24)

MAP_ROAD_SYMBOLS = {"#", "="}
MAP_LIGHT_SYMBOLS = {"~", "="}

def map_cells_with_symbols(symbols):
    return {
        (x, y)
        for y, row in enumerate(MAP_ROWS)
        for x, symbol in enumerate(row)
        if symbol in symbols
    }

def get_cell_components(cells):
    remaining = set(cells)
    components = []
    while remaining:
        start = remaining.pop()
        stack = [start]
        component = {start}
        while stack:
            x, y = stack.pop()
            for neighbor in ((x + 1, y), (x - 1, y), (x, y + 1), (x, y - 1)):
                if neighbor in remaining:
                    remaining.remove(neighbor)
                    component.add(neighbor)
                    stack.append(neighbor)
        components.append(frozenset(component))
    return sorted(components, key=lambda component: (
        min(cell[1] for cell in component),
        min(cell[0] for cell in component),
        len(component)
    ))

def component_bounds(component):
    xs = [cell[0] for cell in component]
    ys = [cell[1] for cell in component]
    return min(xs), min(ys), max(xs), max(ys)

def require_square_component(component, size, name):
    min_x, min_y, max_x, max_y = component_bounds(component)
    if len(component) != size * size or max_x - min_x + 1 != size or max_y - min_y + 1 != size:
        raise ValueError(f"{name} must be {size}x{size}, got bounds {(min_x, min_y, max_x, max_y)}")

    expected = {
        (min_x + dx, min_y + dy)
        for dx in range(size)
        for dy in range(size)
    }
    if set(component) != expected:
        raise ValueError(f"{name} is not a filled {size}x{size} square")

def adjacent_path_cells(cells):
    return sorted(
        {
            neighbor
            for x, y in cells
            for neighbor in ((x + 1, y), (x - 1, y), (x, y + 1), (x, y - 1))
            if neighbor in PATH_CELLS
        },
        key=lambda cell: (cell[1], cell[0])
    )

def road_neighbors(cell):
    x, y = cell
    return sorted(
        neighbor
        for neighbor in ((x + 1, y), (x - 1, y), (x, y + 1), (x, y - 1))
        if neighbor in PATH_CELLS
    )

def find_road_route(start, goals, penalties=None):
    penalties = penalties or {}
    goals = set(goals)
    queue = [(0, 0, start, None)]
    visited = {}
    best_cost = {start: 0}
    order = 0

    while queue:
        cost, _, cell, previous = heapq.heappop(queue)
        if cell in visited:
            continue
        visited[cell] = previous

        if cell in goals:
            route = []
            current = cell
            while current is not None:
                route.append(current)
                current = visited[current]
            return list(reversed(route))

        for neighbor in road_neighbors(cell):
            if neighbor in visited:
                continue
            next_cost = cost + 1 + penalties.get(neighbor, 0)
            if next_cost < best_cost.get(neighbor, 1_000_000):
                best_cost[neighbor] = next_cost
                order += 1
                heapq.heappush(queue, (next_cost, order, neighbor, cell))

    raise ValueError(f"No road route from {start} to any generator entry")

def make_route_pair(start, goals):
    primary = find_road_route(start, goals)
    if len(primary) <= 8:
        return primary, primary[:]

    penalties = {cell: 8 for cell in primary[4:-4]}
    alternate = find_road_route(start, goals, penalties)
    return primary, alternate

PATH_CELLS = map_cells_with_symbols(MAP_ROAD_SYMBOLS)
START_LIGHT_CELLS = map_cells_with_symbols(MAP_LIGHT_SYMBOLS)
HQ_CELLS = map_cells_with_symbols({"G"})
require_square_component(frozenset(HQ_CELLS), 3, "Generator")
HQ_MIN_X, HQ_MIN_Y, _, _ = component_bounds(HQ_CELLS)
HQ_SIZE_CELLS = 3
HQ_CENTER_X = FIELD_OFFSET_X + (HQ_MIN_X + HQ_SIZE_CELLS / 2) * CELL_SIZE
HQ_CENTER_Y = FIELD_OFFSET_Y + (HQ_MIN_Y + HQ_SIZE_CELLS / 2) * CELL_SIZE
GENERATOR_CELLS = set(HQ_CELLS)

blue_components = get_cell_components(map_cells_with_symbols({"C"}))
INITIAL_CANNON_FOOTPRINTS = tuple(component for component in blue_components if len(component) == 4)
for index, footprint in enumerate(INITIAL_CANNON_FOOTPRINTS, start=1):
    require_square_component(footprint, 2, f"Starting cannon {index}")
BROKEN_CANNON_CELLS = tuple(sorted(next(iter(component)) for component in blue_components if len(component) == 1))
CANNON_CELLS = {
    cell
    for footprint in INITIAL_CANNON_FOOTPRINTS
    for cell in footprint
}

BASE_CASTLE_LIGHT_MARGIN = 0
CASTLE_LIGHT_ZONE = set(START_LIGHT_CELLS) | set(HQ_CELLS) | set(CANNON_CELLS)

SECRET_CELLS = tuple(sorted(map_cells_with_symbols({"$"}), key=lambda cell: (cell[1], cell[0])))
HIVE_COMPONENTS = get_cell_components(map_cells_with_symbols({"H"}))
HIVE_ROAD_KEYS = ("north", "west", "south_east")
if len(HIVE_COMPONENTS) != len(HIVE_ROAD_KEYS):
    raise ValueError("Map must contain exactly three 3x3 hives")
for index, footprint in enumerate(HIVE_COMPONENTS, start=1):
    require_square_component(footprint, 3, f"Hive {index}")
HIVE_FOOTPRINTS_BY_ROAD = dict(zip(HIVE_ROAD_KEYS, HIVE_COMPONENTS))

HQ_HITBOX_X1 = FIELD_OFFSET_X + HQ_MIN_X * CELL_SIZE
HQ_HITBOX_Y1 = FIELD_OFFSET_Y + HQ_MIN_Y * CELL_SIZE
HQ_HITBOX_X2 = HQ_HITBOX_X1 + HQ_SIZE_CELLS * CELL_SIZE
HQ_HITBOX_Y2 = HQ_HITBOX_Y1 + HQ_SIZE_CELLS * CELL_SIZE

HQ_ENTRY_CELLS = tuple(adjacent_path_cells(HQ_CELLS))
CASTLE_ROAD_CELLS = set(HQ_ENTRY_CELLS)
HIVE_SPAWN_CELLS_BY_ROAD = {
    road_key: adjacent_path_cells(footprint)[0]
    for road_key, footprint in HIVE_FOOTPRINTS_BY_ROAD.items()
}

LANES = {}
ROAD_BRANCHES = {}
for road_key in HIVE_ROAD_KEYS:
    primary, alternate = make_route_pair(HIVE_SPAWN_CELLS_BY_ROAD[road_key], HQ_ENTRY_CELLS)
    primary_name = f"{road_key}_a"
    alternate_name = f"{road_key}_b"
    LANES[primary_name] = primary
    LANES[alternate_name] = alternate
    ROAD_BRANCHES[road_key] = [primary_name, alternate_name]

ROAD_KEYS = list(ROAD_BRANCHES.keys())
PRIMARY_LANES = [branches[0] for branches in ROAD_BRANCHES.values()]
LANE_TO_BRANCHES = {
    lane_name: branches
    for branches in ROAD_BRANCHES.values()
    for lane_name in branches
}

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
        if cells[-1] not in CASTLE_ROAD_CELLS:
            raise ValueError(f"Lane '{lane_name}' must end at the castle road ring")
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

def scaled(val):
    return int(val * SCALE)

FONT_CACHE = {}

def ui_font(size):
    size = max(12, int(size))
    if size not in FONT_CACHE:
        FONT_CACHE[size] = pygame.font.Font(None, size)
    return FONT_CACHE[size]

def fitted_text_surface(text, color, max_width, max_height, max_size=None, min_size=14):
    text = str(text)
    max_size = int(max_size or font_size_small)
    min_size = max(10, int(min_size))
    for size in range(max_size, min_size - 1, -2):
        rendered = ui_font(size).render(text, True, color)
        if rendered.get_width() <= max_width and rendered.get_height() <= max_height:
            return rendered
    return ui_font(min_size).render(text, True, color)

def draw_fitted_text(surface, text, rect, color=WHITE, max_size=None, min_size=14, align="left", valign="center"):
    rendered = fitted_text_surface(text, color, rect.w, rect.h, max_size, min_size)
    if align == "center":
        x = rect.centerx - rendered.get_width() // 2
    elif align == "right":
        x = rect.right - rendered.get_width()
    else:
        x = rect.x
    if valign == "top":
        y = rect.y
    elif valign == "bottom":
        y = rect.bottom - rendered.get_height()
    else:
        y = rect.centery - rendered.get_height() // 2
    old_clip = surface.get_clip()
    surface.set_clip(rect.clip(surface.get_rect()))
    surface.blit(rendered, (x, y))
    surface.set_clip(old_clip)
    return rendered

def wrap_text_lines(text, font, max_width):
    wrapped = []
    raw_lines = str(text).splitlines() or [""]
    for raw_line in raw_lines:
        words = raw_line.split()
        if not words:
            wrapped.append("")
            continue
        line = ""
        for word in words:
            candidate = word if not line else f"{line} {word}"
            if font.size(candidate)[0] <= max_width:
                line = candidate
                continue
            if line:
                wrapped.append(line)
            line = word
        wrapped.append(line)
    return wrapped

def draw_multiline_text(surface, text, rect, color=WHITE, max_size=None, min_size=12, align="center"):
    max_size = int(max_size or font_size_small)
    min_size = max(10, int(min_size))
    chosen = None
    for size in range(max_size, min_size - 1, -2):
        font = ui_font(size)
        lines = wrap_text_lines(text, font, rect.w)
        rendered = [font.render(line, True, color) for line in lines]
        line_gap = max(2, size // 7)
        total_h = sum(line.get_height() for line in rendered) + line_gap * max(0, len(rendered) - 1)
        max_w = max((line.get_width() for line in rendered), default=0)
        if total_h <= rect.h and max_w <= rect.w:
            chosen = (rendered, line_gap, total_h)
            break
    if chosen is None:
        font = ui_font(min_size)
        lines = wrap_text_lines(text, font, rect.w)
        rendered = [font.render(line, True, color) for line in lines]
        line_gap = max(2, min_size // 7)
        total_h = sum(line.get_height() for line in rendered) + line_gap * max(0, len(rendered) - 1)
        chosen = (rendered, line_gap, total_h)

    rendered, line_gap, total_h = chosen
    y = rect.centery - total_h // 2
    if total_h > rect.h:
        y = rect.y
    else:
        y = max(rect.y, min(y, rect.bottom - total_h))
    old_clip = surface.get_clip()
    surface.set_clip(rect.clip(surface.get_rect()))
    for line in rendered:
        if align == "center":
            x = rect.centerx - line.get_width() // 2
        elif align == "right":
            x = rect.right - line.get_width()
        else:
            x = rect.x
        surface.blit(line, (x, y))
        y += line.get_height() + line_gap
    surface.set_clip(old_clip)

def draw_card(surface, rect, fill=UI_CARD, stroke=UI_STROKE, radius=None):
    radius = scaled(6) if radius is None else radius
    pygame.draw.rect(surface, fill, rect, border_radius=radius)
    pygame.draw.rect(surface, stroke, rect, max(1, scaled(2)), border_radius=radius)

def mix_color(color, target, amount):
    amount = max(0, min(1, amount))
    return tuple(int(c + (t - c) * amount) for c, t in zip(color, target))

def ui_pulse(speed=0.006):
    return 0.5 + 0.5 * math.sin(pygame.time.get_ticks() * speed)

def draw_progress_bar(surface, rect, fraction, fill=UI_GOOD, back=(14, 17, 23), stroke=BLACK):
    fraction = max(0, min(1, fraction))
    pygame.draw.rect(surface, back, rect, border_radius=scaled(3))
    if fraction > 0:
        filled = rect.copy()
        filled.w = max(1, int(rect.w * fraction))
        pygame.draw.rect(surface, fill, filled, border_radius=scaled(3))
    pygame.draw.rect(surface, stroke, rect, max(1, scaled(1)), border_radius=scaled(3))

def draw_square_dot(surface, color, center, size, border_color=None, border_width=0):
    size = max(1, int(size))
    rect = pygame.Rect(int(center[0] - size // 2), int(center[1] - size // 2), size, size)
    pygame.draw.rect(surface, color, rect)
    if border_color and border_width > 0:
        pygame.draw.rect(surface, border_color, rect, border_width)

def cells_world_rect(cells):
    min_x = min(cell[0] for cell in cells)
    max_x = max(cell[0] for cell in cells)
    min_y = min(cell[1] for cell in cells)
    max_y = max(cell[1] for cell in cells)
    return pygame.Rect(
        FIELD_OFFSET_X + min_x * CELL_SIZE,
        FIELD_OFFSET_Y + min_y * CELL_SIZE,
        (max_x - min_x + 1) * CELL_SIZE,
        (max_y - min_y + 1) * CELL_SIZE
    )

def cells_world_center(cells):
    rect = cells_world_rect(cells)
    return rect.centerx, rect.centery


class Enemy:
    def __init__(self, enemy_type, lane):
        self.enemy_type = enemy_type
        self.lane = lane
        base_range = scaled(40)
        stats = {
            "orc": {"hp": 72, "phys": 0.1, "mag": -0.3, "speed": scaled(1.0), "evade": 0.03,
                    "color": GREEN, "atk_dmg": 9, "atk_range": base_range, "atk_cd": 65,
                    "vulnerable_to": {}},
            "wurg": {"hp": 68, "phys": 0.0, "mag": 0.1, "speed": scaled(1.5), "evade": 0.12,
                     "color": YELLOW, "atk_dmg": 11, "atk_range": base_range, "atk_cd": 55,
                     "vulnerable_to": {}},
            "dimmer": {"hp": 54, "phys": 0.0, "mag": -0.2, "speed": scaled(0.9), "evade": 0.02,
                       "color": (45, 45, 70), "atk_dmg": 7, "atk_range": base_range, "atk_cd": 70,
                       "vulnerable_to": {"cannon": 1.35}},
            "hellbrute": {"hp": 480, "phys": 0.3, "mag": 0.05, "speed": scaled(0.38), "evade": 0,
                          "color": (200, 0, 200), "atk_dmg": 32, "atk_range": scaled(50), "atk_cd": 110,
                          "vulnerable_to": {"cannon": 1.8}}
        }
        s = stats[enemy_type]
        self.max_hp = int(s["hp"] * ENEMY_HEALTH_MULTIPLIER * ENEMY_STRENGTH_MULTIPLIER)
        self.hp = self.max_hp
        self.phys_armor = s["phys"]
        self.mag_armor = s["mag"]
        self.speed = float(max(1, s["speed"]) * ENEMY_SPEED_MULTIPLIER)
        self.base_speed = self.speed
        self.evade = s["evade"]
        self.color = s["color"]
        self.attack_damage = max(1, s["atk_dmg"] * ENEMY_STRENGTH_MULTIPLIER)
        self.attack_range = s["atk_range"]
        self.attack_cooldown_max = s["atk_cd"]
        self.attack_cooldown = 0
        self.vulnerable_to = s["vulnerable_to"]
        self.path = get_path_pixels(lane)
        self.path_index = 0
        self.pos = list(self.path[0])
        self.alive = True
        self.attacking_hq = False
        self.switched_lane = False
        self.lamp_disable_cooldown = 0
        self.reward = {"orc": 9, "wurg": 11, "dimmer": 14, "hellbrute": 45}[enemy_type]

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
        if not branches or len(branches) < 2 or self.lane != branches[0]:
            return False
        self.lane = branches[1]
        self.path = get_path_pixels(self.lane)
        self.path_index = min(self.path_index, max(0, len(self.path) - 2))
        self.pos = list(self.path[self.path_index])
        self.attacking_hq = False
        self.switched_lane = True
        return True

    def current_move_speed(self, game):
        if game is not None and not game.is_position_lit(self.pos):
            return self.speed * ENEMY_DARK_SPEED_MULTIPLIER
        return self.speed

    def move(self, hq, game=None):
        if not self.alive:
            return
        if self.attack_cooldown > 0:
            self.attack_cooldown -= 1

        self.maybe_switch_for_light(game)
        move_speed = self.current_move_speed(game)

        if hq.hp > 0 and distance_to_hq_hitbox(self.pos) <= self.attack_range:
            if self.attack_cooldown <= 0:
                hq.take_damage(self.attack_damage)
                self.attack_cooldown = self.attack_cooldown_max
            self.attacking_hq = True
            return

        self.attacking_hq = False
        if self.path_index >= len(self.path) - 1:
            if hq.hp > 0 and self.attack_cooldown <= 0:
                hq.take_damage(self.attack_damage)
                self.attack_cooldown = self.attack_cooldown_max
            return

        target_pos = self.path[self.path_index + 1]
        dx = target_pos[0] - self.pos[0]
        dy = target_pos[1] - self.pos[1]
        dist = math.hypot(dx, dy)
        if dist < move_speed * 1.5 or dist < 5:
            self.pos = list(target_pos)
            self.path_index += 1
        else:
            self.pos[0] += (dx / dist) * move_speed
            self.pos[1] += (dy / dist) * move_speed

    def damage_multiplier_for_source(self, armor, damage_source):
        if damage_source == "gatling":
            return max(0.35, 1.25 - armor * 2.5)
        if damage_source == "scatter":
            return max(0.55, 1.05 - armor * 1.15)
        if damage_source == "sniper":
            return 1.08 + max(0, armor) * 0.8
        return max(0.1, 1 - armor)

    def vulnerability_multiplier_for_source(self, damage_source):
        if damage_source in self.vulnerable_to:
            return self.vulnerable_to[damage_source]
        if damage_source in CANNON_SPECIALIZATION_SOURCES and "cannon" in self.vulnerable_to:
            cannon_bonus = self.vulnerable_to["cannon"] - 1
            if damage_source == "gatling":
                return 1 + cannon_bonus * 0.35
            if damage_source == "scatter":
                return 1 + cannon_bonus * 0.65
            return self.vulnerable_to["cannon"]
        return 1

    def effective_damage(self, damage, damage_type, damage_source=None):
        armor = self.phys_armor if damage_type == "physical" else self.mag_armor
        effective = damage * self.damage_multiplier_for_source(armor, damage_source)
        effective *= self.vulnerability_multiplier_for_source(damage_source)
        return max(1, effective)

    def take_damage(self, damage, damage_type, damage_source=None):
        effective = self.effective_damage(damage, damage_type, damage_source)
        if random.random() < self.evade:
            effective = 0
        self.hp -= effective
        if self.hp <= 0:
            self.alive = False

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
        pygame.draw.rect(surface, RED, (int(self.pos[0] - bar_width / 2), int(self.pos[1] - scaled(25)), bar_width, scaled(5)))
        green_width = bar_width * max(0, self.hp / self.max_hp)
        pygame.draw.rect(surface, YELLOW, (int(self.pos[0] - bar_width / 2), int(self.pos[1] - scaled(25)), green_width, scaled(5)))

class Tower:
    def __init__(self, tower_type, cell, fixed=False, cells=None):
        self.tower_type = tower_type
        self.cells = set(cells) if cells is not None else {cell}
        self.cell = min(self.cells)
        self.fixed = fixed
        self.x, self.y = cells_world_center(self.cells)
        self.level = 1
        stats = {
            "cannon": {"damage": int(80 * CANNON_DAMAGE_MULTIPLIER), "range": FULL_MAP_ATTACK_RANGE, "cooldown": 52, "color": CANNON_BLUE, "hp": 220},
            "lamp": {"damage": 0, "range": 0, "cooldown": 0, "color": LIGHT_BLUE, "hp": 105},
            "beacon": {"damage": 0, "range": 0, "cooldown": 0, "color": GENERATOR_BLUE, "hp": 170},
        }
        s = stats[tower_type]
        self.damage = s["damage"]
        self.range = s["range"]
        self.cooldown_max = s["cooldown"]
        self.cooldown = 0
        self.color = s["color"]
        self.max_hp = s["hp"]
        self.hp = self.max_hp
        self.shot_effects = []
        self.damage_type = "physical"
        self.splash_radius = scaled(60) if tower_type == "cannon" else 0
        self.splash_damage_multiplier = 0.5
        self.total_investment = 0 if fixed else TOWER_COST.get(tower_type, 0)
        self.specialization = None
        self.direction_index = 1
        self.broken = False
        self.disabled_timer = 0
        self.is_powered = False

    def contains_cell(self, cell):
        return cell in self.cells

    def world_rect(self):
        return cells_world_rect(self.cells)

    def upgrade(self):
        if self.level >= 4:
            return False
        cost = TOWER_UPGRADE_COST[self.tower_type]
        self.level += 1
        if self.tower_type in LIGHT_TOWER_TYPES:
            self.max_hp = int(self.max_hp * 1.25)
            self.hp = self.max_hp
        elif self.tower_type == "cannon" and self.specialization:
            self.apply_specialization(self.specialization)
            self.max_hp = int(self.max_hp * 1.3)
            self.hp = self.max_hp
        self.total_investment += cost
        return True

    def rotate(self):
        if self.tower_type not in ROTATABLE_LIGHT_TYPES or self.hp <= 0:
            return False
        self.direction_index = (self.direction_index + 1) % len(DIRECTIONS)
        return True

    def apply_specialization(self, spec_type):
        if self.tower_type != "cannon":
            return
        self.specialization = spec_type
        level_bonus = 1 + max(0, self.level - 1) * CANNON_LEVEL_DAMAGE_BONUS
        if spec_type == "sniper":
            self.color = (255, 220, 90)
            self.damage = int(180 * CANNON_DAMAGE_MULTIPLIER * level_bonus)
            self.range = FULL_MAP_ATTACK_RANGE
            self.cooldown_max = max(34, int(72 - max(0, self.level - 2) * 8))
            self.splash_radius = 0
            self.splash_damage_multiplier = 0
        elif spec_type == "scatter":
            self.color = (255, 145, 70)
            self.damage = int(95 * 0.5 * CANNON_DAMAGE_MULTIPLIER * level_bonus)
            self.range = FULL_MAP_ATTACK_RANGE
            self.cooldown_max = max(28, int(48 - max(0, self.level - 2) * 6))
            self.splash_radius = scaled(115)
            self.splash_damage_multiplier = 1.0
        elif spec_type == "gatling":
            self.color = (120, 230, 140)
            self.damage = int(58 * 0.75 * CANNON_DAMAGE_MULTIPLIER * level_bonus)
            self.range = FULL_MAP_ATTACK_RANGE
            current_cooldown = (16 - max(0, self.level - 2) * 2) / 2
            self.cooldown_max = max(4, int(round(current_cooldown / 0.75)))
            self.splash_radius = 0
            self.splash_damage_multiplier = 0
        self.cooldown = min(self.cooldown, self.cooldown_max)

    def can_attack_target(self, enemy, game):
        if not enemy.alive:
            return False
        if math.hypot(enemy.pos[0] - self.x, enemy.pos[1] - self.y) > self.range:
            return False
        if self.tower_type == "cannon":
            return game is not None and game.is_target_lit(enemy)
        return True

    def find_target(self, enemies, game=None):
        if self.damage <= 0:
            return None
        in_range = [
            enemy for enemy in enemies
            if self.can_attack_target(enemy, game)
        ]
        if not in_range:
            return None
        return min(in_range, key=self.cannon_target_priority)

    def distance_to_target(self, target):
        return math.hypot(target.pos[0] - self.x, target.pos[1] - self.y)

    def path_target_priority(self, target):
        remaining = max(0, len(target.path) - 1 - target.path_index)
        return (remaining, self.distance_to_target(target))

    def estimated_damage_to(self, target):
        return target.effective_damage(self.damage, self.damage_type, self.damage_source())

    def damage_source(self):
        if self.tower_type == "cannon" and self.specialization:
            return self.specialization
        return self.tower_type

    def cannon_target_priority(self, target):
        hp = max(1, getattr(target, "hp", 1))
        shots_to_kill = math.ceil(hp / self.estimated_damage_to(target))
        path_priority = self.path_target_priority(target)
        return (path_priority[0], shots_to_kill, path_priority[1])

    def update(self, enemies, game):
        for effect in self.shot_effects[:]:
            effect["timer"] -= 1
            if effect["timer"] <= 0:
                self.shot_effects.remove(effect)

        if self.disabled_timer > 0:
            self.disabled_timer -= 1

        if self.hp <= 0 or self.broken or self.damage <= 0:
            return
        if self.cooldown > 0:
            self.cooldown -= 1
        if self.cooldown == 0:
            target = self.find_target(enemies, game)
            if target:
                self.fire_laser(target, enemies, game)
                self.cooldown = self.cooldown_max

    def fire_laser(self, target, enemies, game):
        tx, ty = target.pos
        damage_source = self.damage_source()
        target.take_damage(self.damage, self.damage_type, damage_source)
        splash_damage = int(self.damage * self.splash_damage_multiplier)
        if self.splash_radius > 0 and splash_damage > 0:
            for enemy in enemies:
                if enemy is not target and enemy.alive:
                    if self.tower_type == "cannon" and (game is None or not game.is_target_lit(enemy)):
                        continue
                    if math.hypot(enemy.pos[0] - tx, enemy.pos[1] - ty) <= self.splash_radius:
                        enemy.take_damage(splash_damage, self.damage_type, damage_source)
        self.add_shot_effect(tx, ty)

    def add_shot_effect(self, tx, ty):
        shot_color = (255, 232, 72)
        spec = self.specialization or "sniper"
        if spec == "scatter":
            self.shot_effects.append({
                "kind": "shell",
                "x1": self.x,
                "y1": self.y,
                "x2": tx,
                "y2": ty,
                "timer": 18,
                "duration": 18,
                "color": shot_color,
            })
            return

        if spec == "gatling":
            dx = tx - self.x
            dy = ty - self.y
            distance = max(1, math.hypot(dx, dy))
            self.shot_effects.append({
                "kind": "gatling",
                "x1": self.x,
                "y1": self.y,
                "x2": tx,
                "y2": ty,
                "segment_len": min(max(scaled(80), distance * 0.24), scaled(180)),
                "timer": 10,
                "duration": 10,
                "color": shot_color,
            })
            return

        dx = tx - self.x
        dy = ty - self.y
        distance = max(1, math.hypot(dx, dy))
        self.shot_effects.append({
            "kind": "sniper",
            "x1": self.x,
            "y1": self.y,
            "x2": tx,
            "y2": ty,
            "segment_len": min(max(scaled(110), distance * 0.32), scaled(260)),
            "timer": 10,
            "duration": 10,
            "color": shot_color,
        })

    def draw(self, surface):
        if self.hp <= 0:
            return
        if self.tower_type in LIGHT_TOWER_TYPES:
            rect_size = scaled(34 if self.tower_type == "lamp" else 42)
            is_disabled = self.disabled_timer > 0
            is_powered = getattr(self, "is_powered", False) and not is_disabled
            if is_disabled:
                body_color = (82, 82, 82)
            elif is_powered:
                body_color = self.color if self.level == 1 else (170, 240, 255)
            else:
                body_color = (92, 108, 116)
            pygame.draw.rect(surface, body_color, (self.x - rect_size // 2, self.y - rect_size // 2, rect_size, rect_size))
            pygame.draw.rect(surface, BLACK, (self.x - rect_size // 2, self.y - rect_size // 2, rect_size, rect_size), max(1, scaled(2)))
            if is_powered:
                glow_radius = scaled(10 + 4 * self.level)
                pygame.draw.circle(surface, (255, 255, 205), (int(self.x), int(self.y)), glow_radius)
                pygame.draw.circle(surface, GENERATOR_BLUE, (int(self.x), int(self.y)), max(2, glow_radius // 2), max(1, scaled(2)))
            if self.tower_type == "lamp" and is_powered:
                dx, dy = DIRECTIONS[self.direction_index]
                length = scaled(24)
                end = (self.x + dx * length, self.y + dy * length)
                width = max(2, scaled(4))
                pygame.draw.line(surface, BLACK, (self.x, self.y), end, width)
                pygame.draw.line(surface, (255, 255, 180), (self.x, self.y), end, max(1, width // 2))
                pygame.draw.circle(surface, (255, 255, 180), (int(end[0]), int(end[1])), scaled(8))
        elif self.tower_type == "cannon":
            cannon_color = GRAY if self.broken else self.color
            rect = self.world_rect().inflate(-scaled(6), -scaled(6))
            pygame.draw.rect(surface, cannon_color, rect)
            pygame.draw.rect(surface, BLACK, rect, max(1, scaled(2)))
            draw_square_dot(surface, RED, (self.x, self.y), scaled(20), WHITE, max(1, scaled(1)))
            if self.broken:
                pygame.draw.line(surface, RED, rect.topleft, rect.bottomright, max(2, scaled(3)))
                pygame.draw.line(surface, RED, rect.topright, rect.bottomleft, max(2, scaled(3)))

        for effect in self.shot_effects:
            color = effect["color"]
            if effect["kind"] == "shell":
                progress = 1 - effect["timer"] / effect["duration"]
                x = effect["x1"] + (effect["x2"] - effect["x1"]) * progress
                y = effect["y1"] + (effect["y2"] - effect["y1"]) * progress
                size = max(7, scaled(12))
                rect = pygame.Rect(int(x - size / 2), int(y - size / 2), size, size)
                pygame.draw.rect(surface, BLACK, rect.inflate(max(2, scaled(3)), max(2, scaled(3))))
                pygame.draw.rect(surface, color, rect)
            else:
                width = max(2, scaled(4 if effect["kind"] == "gatling" else 5))
                start = (effect["x1"], effect["y1"])
                end = (effect["x2"], effect["y2"])
                if effect["kind"] in ("gatling", "sniper"):
                    dx = effect["x2"] - effect["x1"]
                    dy = effect["y2"] - effect["y1"]
                    distance = max(1, math.hypot(dx, dy))
                    nx = dx / distance
                    ny = dy / distance
                    progress = 1 - effect["timer"] / effect["duration"]
                    head = min(distance, progress * distance)
                    tail = max(0, head - effect["segment_len"])
                    start = (effect["x1"] + nx * tail, effect["y1"] + ny * tail)
                    end = (effect["x1"] + nx * head, effect["y1"] + ny * head)
                pygame.draw.line(surface, BLACK, start, end, width + max(1, scaled(2)))
                pygame.draw.line(surface, color, start, end, width)

class Hive:
    def __init__(self, road_key):
        self.road_key = road_key
        self.primary_lane = ROAD_BRANCHES[road_key][0]
        self.cells = set(HIVE_FOOTPRINTS_BY_ROAD[road_key])
        self.cell = min(self.cells)
        self.spawn_cell = HIVE_SPAWN_CELLS_BY_ROAD[road_key]
        self.x, self.y = cells_world_center(self.cells)
        self.hp = 1
        self.max_hp = 1
        self.is_alive = True
        self.is_visible = False

    def contains_cell(self, cell):
        return self.is_alive and self.is_visible and cell in self.cells

    def draw(self, surface):
        if not self.is_alive or not self.is_visible:
            return
        rect = cells_world_rect(self.cells).inflate(-scaled(4), -scaled(4))
        pygame.draw.rect(surface, PURPLE, rect)
        pygame.draw.rect(surface, BLACK, rect, max(1, scaled(2)))
        label = font_small.render("Hive", True, WHITE)
        surface.blit(label, label.get_rect(center=(int(self.x), int(self.y))))


class MapBonus:
    COLORS = {
        "currency": GOLD,
        "broken_cannon": CANNON_BLUE,
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
        self.hp = max(0, self.hp - damage)

    def update(self, game):
        self.income_buffer += self.income_per_second / 60
        if self.income_buffer >= 1:
            income = int(self.income_buffer)
            self.income_buffer -= income
            game.money += income
            game.light_earned += income

    def draw(self, surface):
        if self.hp <= 0:
            return
        rect = pygame.Rect(
            FIELD_OFFSET_X + HQ_MIN_X * CELL_SIZE,
            FIELD_OFFSET_Y + HQ_MIN_Y * CELL_SIZE,
            HQ_SIZE_CELLS * CELL_SIZE,
            HQ_SIZE_CELLS * CELL_SIZE
        )
        pygame.draw.rect(surface, GENERATOR_RED, rect)
        pygame.draw.rect(surface, BLACK, rect, scaled(4))
        pygame.draw.rect(surface, WHITE, rect, scaled(2))
        center = (int(HQ_CENTER_X), int(HQ_CENTER_Y))
        inner = rect.inflate(-scaled(18), -scaled(18))
        pygame.draw.rect(surface, (255, 96, 48), inner)
        draw_square_dot(surface, GENERATOR_RED, center, scaled(28), BLACK, max(1, scaled(2)))
        bar_width = scaled(80)
        bar_y = rect.top - scaled(20)
        pygame.draw.rect(surface, RED, (int(HQ_CENTER_X - bar_width / 2), bar_y, bar_width, scaled(10)))
        green_width = bar_width * (self.hp / self.max_hp)
        pygame.draw.rect(surface, YELLOW, (int(HQ_CENTER_X - bar_width / 2), bar_y, int(green_width), scaled(10)))

class Game:
    def __init__(self, show_start=True):
        self.screen_state = "start" if show_start else "playing"
        self.money = STARTING_MONEY
        self.wave = 1
        self.wave_active = False
        self.wave_timer = 0
        self.enemies = []
        self.towers = [
            Tower("cannon", min(footprint), fixed=True, cells=footprint)
            for footprint in INITIAL_CANNON_FOOTPRINTS
        ]
        self.selected_tower_type = None
        self.selected_tower = None
        self.selected_hive = None
        self.action_cooldowns = {action: 0 for action in ACTION_COOLDOWN_FRAMES}
        self.build_direction_index = 1
        self.victory = False
        self.defeat = False
        self.paused = False
        self.exit_confirm_open = False
        self.hq = Headquarters()
        self.hives = [Hive(road_key) for road_key in ROAD_KEYS]
        self.bonuses = self.generate_bonuses()
        self.notification_text = ""
        self.notification_timer = 0
        self.enemies_killed = 0
        self.light_earned = 0
        self.bonuses_collected = 0
        
        self.first_wave_started = False
        
        self.tower_specialization_pending = False
        self.tower_to_specialize = None
        self.lit_cells = self.get_castle_light_zone() | set(GENERATOR_CELLS)
        self.revealed_cells = set(self.lit_cells)
        self.fog_surface = pygame.Surface((FIELD_WIDTH, FIELD_HEIGHT), pygame.SRCALPHA)
        self.fog_dirty = True

        self.wave_interval = 0
        self.wave_interval_timer = 0
        self.wave_delay = 300
        self.wave_delay_timer = 0
        self.wave_delay_active = False
        
        self.total_waves = 999

        self.spawn_queue = []
        self.wave_spawn_total = 0
        self.zoom = START_ZOOM
        self.camera_x = HQ_CENTER_X - VIEWPORT_WIDTH / self.zoom / 2
        self.camera_y = HQ_CENTER_Y - VIEWPORT_HEIGHT / self.zoom / 2
        self.dragging_camera = False
        self.last_drag_pos = None
        self.drag_start_pos = None
        self.drag_moved = False
        self.camera_drag_button = None
        self.clamp_camera()
        self.update_lighting()
        if self.screen_state == "playing":
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

    def begin_camera_drag(self, pos, button):
        self.dragging_camera = True
        self.last_drag_pos = pos
        self.drag_start_pos = pos
        self.drag_moved = False
        self.camera_drag_button = button

    def update_camera_drag(self, event):
        if not self.dragging_camera:
            return
        if self.drag_start_pos is not None:
            dx = event.pos[0] - self.drag_start_pos[0]
            dy = event.pos[1] - self.drag_start_pos[1]
            if math.hypot(dx, dy) >= CAMERA_DRAG_THRESHOLD:
                self.drag_moved = True
        if self.drag_moved:
            self.pan_camera(-event.rel[0] * 1.8 / self.zoom, -event.rel[1] * 1.8 / self.zoom)
        self.last_drag_pos = event.pos

    def end_camera_drag(self, button):
        if not self.dragging_camera or self.camera_drag_button != button:
            return False
        should_click = button == 3 and not self.drag_moved
        self.dragging_camera = False
        self.last_drag_pos = None
        self.drag_start_pos = None
        self.drag_moved = False
        self.camera_drag_button = None
        return should_click

    def update_camera(self):
        return

    def get_castle_light_zone(self):
        cells = set(CASTLE_LIGHT_ZONE)
        margin = BASE_CASTLE_LIGHT_MARGIN + max(0, self.hq.level - 1) * 2
        for x in range(HQ_MIN_X - margin, HQ_MIN_X + HQ_SIZE_CELLS + margin):
            for y in range(HQ_MIN_Y - margin, HQ_MIN_Y + HQ_SIZE_CELLS + margin):
                if 0 <= x < GRID_WIDTH and 0 <= y < GRID_HEIGHT:
                    cells.add((x, y))
        return cells

    def generate_bonuses(self):
        bonuses = [MapBonus(cell, "currency") for cell in SECRET_CELLS]
        bonuses.extend(MapBonus(cell, "broken_cannon") for cell in BROKEN_CANNON_CELLS)
        return bonuses

    def notify(self, text, duration=120):
        self.notification_text = text
        self.notification_timer = duration

    def is_start_screen(self):
        return self.screen_state == "start"

    def is_tutorial_screen(self):
        return self.screen_state == "tutorial"

    def ask_exit_to_menu(self):
        if self.screen_state != "playing":
            return False
        self.exit_confirm_open = True
        self.dragging_camera = False
        self.last_drag_pos = None
        self.drag_start_pos = None
        self.drag_moved = False
        self.camera_drag_button = None
        return True

    def cancel_exit_confirm(self):
        self.exit_confirm_open = False

    def toggle_pause(self):
        if self.screen_state != "playing" or self.exit_confirm_open or self.defeat or self.victory:
            return False
        self.paused = not self.paused
        self.notify("Paused" if self.paused else "Resumed")
        return True

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
            self.light_earned += 100
            self.notify("+100 light found")
        elif bonus.bonus_type == "broken_cannon":
            tower = Tower("cannon", bonus.cell, fixed=True)
            tower.broken = True
            tower.total_investment = 0
            self.towers.append(tower)
            self.notify("Broken cannon found")
        bonus.is_collected = True
        self.bonuses_collected += 1
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

    def get_lane_total_light_pressure(self, lane):
        cells = LANES.get(lane, [])
        if not cells:
            return 0, 0, 0
        lit_count = sum(1 for cell in cells if self.is_lit(cell))
        return lit_count, len(cells), lit_count / len(cells)

    def is_adaptive_route_wave(self):
        return self.wave > 0 and self.wave % ADAPTIVE_ROUTE_WAVE_INTERVAL == 0

    def choose_least_lit_lane(self, road_key):
        branches = ROAD_BRANCHES.get(road_key, [])
        if not branches:
            return None
        return min(
            branches,
            key=lambda lane: (
                self.get_lane_total_light_pressure(lane)[2],
                self.get_lane_total_light_pressure(lane)[0],
                lane,
            )
        )

    def choose_spawn_lane(self, hive):
        if self.is_adaptive_route_wave():
            lane = self.choose_least_lit_lane(hive.road_key)
            if lane:
                return lane
        return hive.primary_lane

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
        self.remove_spawn_queue_road(hive.road_key)
        self.selected_hive = None
        self.notify("Hive destroyed")
        if all(not hive.is_alive for hive in self.hives):
            self.victory = True
            self.notify("All hives destroyed")
        return True

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
        return any(cell in current_lit for cell in tower.cells)

    def calculate_lit_cells(self, excluded_tower=None, update_power_flags=False):
        castle_light_zone = self.get_castle_light_zone()
        lit = set(castle_light_zone) | set(GENERATOR_CELLS)
        if update_power_flags:
            for tower in self.towers:
                if tower.tower_type in LIGHT_TOWER_TYPES:
                    tower.is_powered = False
        changed = True
        while changed:
            changed = False
            for tower in self.towers:
                if tower is excluded_tower:
                    continue
                if self.light_source_has_power(tower, lit):
                    if update_power_flags:
                        tower.is_powered = True
                    for cell in self.get_light_coverage(tower):
                        if cell not in lit:
                            lit.add(cell)
                            changed = True
        return lit

    def update_lighting(self):
        lit = self.calculate_lit_cells(update_power_flags=True)
        self.lit_cells = lit
        light_tower_cells = {
            cell
            for tower in self.towers
            if tower.tower_type in LIGHT_TOWER_TYPES and tower.hp > 0
            for cell in tower.cells
        }
        self.revealed_cells = set(lit) | light_tower_cells
        self.fog_dirty = True
        if hasattr(self, "hives"):
            for hive in self.hives:
                hive.is_visible = hive.is_alive and any(self.is_lit(cell) for cell in hive.cells)
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
        if hasattr(target, "pos"):
            return self.is_position_lit(target.pos)
        return False

    def can_place_light_building(self, cell):
        if not (0 <= cell[0] < GRID_WIDTH and 0 <= cell[1] < GRID_HEIGHT):
            return False
        if is_hq_cell(cell) or is_any_path_cell(cell):
            return False
        if any(hive.is_alive and cell in hive.cells for hive in getattr(self, "hives", [])):
            return False
        if any((not bonus.is_collected) and bonus.cell == cell for bonus in getattr(self, "bonuses", [])):
            return False
        for tower in self.towers:
            if tower.hp > 0 and tower.contains_cell(cell):
                return False
        return self.is_lit(cell)

    def is_revealed(self, cell):
        return cell in self.revealed_cells or self.is_lit(cell)

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

    def queued_enemy_count(self):
        total = 0
        for batch in self.spawn_queue:
            total += 1 if isinstance(batch, tuple) else len(batch)
        return total

    def remove_spawn_queue_road(self, road_key):
        filtered_queue = []
        for batch in self.spawn_queue:
            if isinstance(batch, tuple):
                if batch[1] != road_key:
                    filtered_queue.append(batch)
                continue
            filtered_batch = [entry for entry in batch if entry[1] != road_key]
            if filtered_batch:
                filtered_queue.append(filtered_batch)
        self.spawn_queue = filtered_queue

    def create_wave_enemy(self, enemy_type, road_key, lane=None):
        hive = self.get_hive_by_road_key(road_key)
        if not hive or not hive.is_alive:
            return None
        if lane not in ROAD_BRANCHES.get(road_key, []):
            lane = hive.primary_lane
        enemy = Enemy(enemy_type, lane)
        enemy.pos = list(get_path_pixels(lane)[0])
        enemy.path_index = 0
        if self.is_adaptive_route_wave():
            enemy.switched_lane = True
        wave_steps = max(0, self.wave - 1)
        hp_bonus = 1 + wave_steps * ENEMY_HP_GROWTH_PER_WAVE
        speed_bonus = 1 + wave_steps * ENEMY_SPEED_GROWTH_PER_WAVE
        damage_bonus = 1 + wave_steps * ENEMY_DAMAGE_GROWTH_PER_WAVE
        reward_bonus = 1 + wave_steps * ENEMY_REWARD_GROWTH_PER_WAVE
        enemy.max_hp = int(enemy.max_hp * hp_bonus)
        enemy.hp = enemy.max_hp
        enemy.speed *= speed_bonus
        enemy.base_speed = enemy.speed
        enemy.attack_damage = max(1, enemy.attack_damage * damage_bonus)
        enemy.reward = int(enemy.reward * ENEMY_REWARD_MULTIPLIER * reward_bonus)
        return enemy

    def tick_action_cooldowns(self):
        for action in self.action_cooldowns:
            if self.action_cooldowns[action] > 0:
                self.action_cooldowns[action] -= 1

    def can_use_action(self, action):
        return self.action_cooldowns.get(action, 0) <= 0

    def cooldown_button_title(self, title, action):
        frames_left = self.action_cooldowns.get(action, 0)
        if frames_left <= 0:
            return title
        return f"{title} {math.ceil(frames_left / 60)}s"

    def action_cooldown_progress(self, action):
        frames_left = self.action_cooldowns.get(action, 0)
        total = ACTION_COOLDOWN_FRAMES.get(action, 0)
        if frames_left <= 0 or total <= 0:
            return None
        return 1 - frames_left / total

    def start_action_cooldown(self, action):
        if action in ACTION_COOLDOWN_FRAMES:
            self.action_cooldowns[action] = ACTION_COOLDOWN_FRAMES[action]

    def start_wave(self, early=False):
        if not self.wave_active and not self.wave_delay_active and any(hive.is_alive for hive in self.hives):
            if early and self.first_wave_started:
                self.money += 22
                self.light_earned += 22
            
            if not self.first_wave_started:
                self.first_wave_started = True
            
            self.spawn_queue = []
            base_count = ENEMY_COUNT_BASE_PER_HIVE + int((self.wave - 1) * ENEMY_COUNT_GROWTH_PER_WAVE)
            count_per_hive = max(1, int(base_count * self.hive_spawn_multiplier()))
            active_hives = [hive for hive in self.hives if hive.is_alive]
            spawn_lanes = {
                hive.road_key: self.choose_spawn_lane(hive)
                for hive in active_hives
            }
            for index in range(count_per_hive):
                spawn_batch = []
                for hive in active_hives:
                    spawn_batch.append((self.enemy_type_for_wave(index), hive.road_key, spawn_lanes[hive.road_key]))
                if spawn_batch:
                    self.spawn_queue.append(spawn_batch)
            
            self.wave_active = True
            self.wave_timer = 0
            self.wave_spawn_total = self.queued_enemy_count()
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
            cost = TOWER_UPGRADE_COST.get(self.selected_tower.tower_type)
            if cost is None:
                return False
            if self.selected_tower.tower_type == "cannon" and self.selected_tower.level == 1 and not self.selected_tower.specialization:
                if self.money < cost:
                    self.notify("Need more light for upgrade")
                    return False
                self.tower_specialization_pending = True
                self.tower_to_specialize = self.selected_tower
                return False
            if self.money >= cost:
                if self.selected_tower.upgrade():
                    self.money -= cost
                    self.update_lighting()
                    return True
        return False

    def apply_tower_specialization(self, spec_type):
        if self.tower_to_specialize and self.tower_to_specialize.hp > 0:
            is_free_change = (
                self.tower_to_specialize.tower_type == "cannon"
                and self.tower_to_specialize.level >= 3
                and self.tower_to_specialize.specialization is not None
            )
            if is_free_change:
                if self.tower_to_specialize.specialization != spec_type:
                    self.start_action_cooldown("change_specialization")
                self.tower_to_specialize.apply_specialization(spec_type)
                self.tower_specialization_pending = False
                self.tower_to_specialize = None
                return True

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
            self.notify("Need more light for upgrade")
        return False

    def cancel_tower_specialization(self):
        self.tower_specialization_pending = False
        self.tower_to_specialize = None

    def begin_tower_specialization_change(self):
        if (
            self.selected_tower
            and self.selected_tower.tower_type == "cannon"
            and self.selected_tower.level >= 3
            and self.selected_tower.specialization
            and self.can_use_action("change_specialization")
        ):
            self.tower_specialization_pending = True
            self.tower_to_specialize = self.selected_tower
            return True
        return False

    def can_sell_tower(self, tower):
        if not tower or tower.hp <= 0:
            return False
        if getattr(tower, "fixed", False):
            return False
        if not self.can_use_action("sell"):
            return False
        lit_without_tower = self.calculate_lit_cells(excluded_tower=tower)
        return any(cell in lit_without_tower for cell in tower.cells)

    def sell_tower(self, cell):
        if not self.can_use_action("sell"):
            return False
        for t in self.towers:
            if t.contains_cell(cell):
                if getattr(t, "fixed", False):
                    return False
                if not self.can_sell_tower(t):
                    self.notify("Tower must be lit to sell")
                    return False
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

    def panel_sizes(self):
        return {
            "pad": max(14, scaled(20)),
            "gap": max(8, scaled(10)),
            "button_h": max(52, scaled(64)),
            "metric_h": max(58, scaled(68)),
            "title_h": max(52, scaled(64)),
        }

    def wave_state_text(self):
        if self.paused:
            return "Paused"
        if self.wave_delay_active:
            seconds = max(0, math.ceil((self.wave_delay - self.wave_delay_timer) / 60))
            return f"Attack in {seconds}s"
        if self.wave_active:
            return "Wave active"
        return "Preparing"

    def draw_metric_card(self, surface, rect, icon_type, label, value, accent=CYAN):
        draw_card(surface, rect, UI_CARD)
        icon_size = min(rect.h - scaled(12), scaled(34))
        icon_x = rect.x + scaled(20)
        self.draw_stat_icon(surface, icon_type, (icon_x, rect.centery), icon_size)
        text_x = rect.x + scaled(44)
        label_rect = pygame.Rect(text_x, rect.y + scaled(5), rect.right - text_x - scaled(8), rect.h // 2)
        value_rect = pygame.Rect(text_x, rect.y + rect.h // 2 - scaled(2), rect.right - text_x - scaled(8), rect.h // 2)
        draw_fitted_text(surface, label, label_rect, UI_TEXT_DIM, max_size=font_size_small - 4, min_size=12)
        draw_fitted_text(surface, value, value_rect, WHITE, max_size=font_size_medium, min_size=14)
        pygame.draw.rect(surface, accent, (rect.x, rect.y, max(3, scaled(4)), rect.h), border_radius=scaled(4))

    def draw_context_line(self, surface, label, value, rect, accent=UI_TEXT_DIM):
        draw_card(surface, rect, (26, 32, 43), (56, 70, 86), radius=scaled(4))
        label_rect = pygame.Rect(rect.x + scaled(10), rect.y + scaled(4), rect.w - scaled(20), rect.h // 2)
        value_rect = pygame.Rect(rect.x + scaled(10), rect.y + rect.h // 2 - scaled(2), rect.w - scaled(20), rect.h // 2)
        draw_fitted_text(surface, label, label_rect, accent, max_size=font_size_small - 4, min_size=12)
        draw_fitted_text(surface, value, value_rect, WHITE, max_size=font_size_small, min_size=12)

    def get_left_build_buttons(self):
        buttons = []
        sizes = self.panel_sizes()
        btn_width = SIDE_PANEL_WIDTH - sizes["pad"] * 2
        btn_height = sizes["button_h"]
        btn_gap = sizes["gap"]
        left_x = sizes["pad"]
        start_y = SCREEN_HEIGHT - sizes["pad"] - len(BUILDABLE_TOWER_TYPES) * btn_height - (len(BUILDABLE_TOWER_TYPES) - 1) * btn_gap
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
                "cooldown": "build",
            })
        return buttons

    def get_pause_button(self):
        sizes = self.panel_sizes()
        pause_y = (
            sizes["pad"]
            + 4 * (sizes["metric_h"] + sizes["gap"])
            + sizes["gap"]
        )
        return {
            "title": "Resume" if self.paused else "Pause",
            "enabled": not self.defeat and not self.victory,
            "selected": self.paused,
            "rect": pygame.Rect(sizes["pad"], pause_y, SIDE_PANEL_WIDTH - sizes["pad"] * 2, sizes["button_h"]),
        }

    def get_menu_button(self):
        sizes = self.panel_sizes()
        pause_button = self.get_pause_button()
        return {
            "title": "Menu",
            "enabled": self.paused,
            "selected": False,
            "rect": pygame.Rect(
                sizes["pad"],
                pause_button["rect"].bottom + sizes["gap"],
                SIDE_PANEL_WIDTH - sizes["pad"] * 2,
                sizes["button_h"],
            ),
        }

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
                    "title": self.cooldown_button_title("Rotate", "rotate"),
                    "cost": None,
                    "enabled": self.can_use_action("rotate"),
                    "selected": False,
                    "cooldown": "rotate",
                })

            if (
                self.selected_tower.tower_type == "cannon"
                and self.selected_tower.level >= 3
                and self.selected_tower.specialization
            ):
                buttons.append({
                    "action": "change_specialization",
                    "title": self.cooldown_button_title("Change", "change_specialization"),
                    "cost": None,
                    "enabled": self.can_use_action("change_specialization"),
                    "selected": False,
                    "cooldown": "change_specialization",
                })

            buttons.append({
                "action": "sell_selected",
                "title": "Remove",
                "cost": None,
                "enabled": self.can_sell_tower(self.selected_tower),
                "selected": False,
                "danger": True,
                "cooldown": "sell",
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
        sizes = self.panel_sizes()
        right_x = SCREEN_WIDTH - SIDE_PANEL_WIDTH + sizes["pad"]
        btn_width = SIDE_PANEL_WIDTH - sizes["pad"] * 2
        btn_height = sizes["button_h"]
        btn_gap = sizes["gap"]
        buttons = self.get_right_panel_buttons()
        start_y = SCREEN_HEIGHT - sizes["pad"] - len(buttons) * btn_height - max(0, len(buttons) - 1) * btn_gap
        return buttons, right_x, btn_width, start_y, btn_gap, btn_height

    def run_right_panel_action(self, action):
        if action.startswith("build:"):
            tower_type = action.split(":", 1)[1]
            if self.selected_tower_type == tower_type:
                self.clear_selection()
            else:
                self.selected_tower_type = tower_type
                self.selected_tower = None
                self.selected_hive = None
        elif action == "upgrade_tower":
            self.upgrade_tower()
        elif action == "rotate_tower":
            self.rotate_selected_tower()
        elif action == "change_specialization":
            self.begin_tower_specialization_change()
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
        pause_button = self.get_pause_button()
        if pause_button["rect"].collidepoint(pos):
            if pause_button["enabled"]:
                self.toggle_pause()
            return True

        menu_button = self.get_menu_button()
        if self.paused and menu_button["rect"].collidepoint(pos):
            self.ask_exit_to_menu()
            return True

        for button in self.get_left_build_buttons():
            if button["rect"].collidepoint(pos):
                if button["enabled"]:
                    tower_type = button["action"].split(":", 1)[1]
                    if self.selected_tower_type == tower_type:
                        self.clear_selection()
                    else:
                        self.selected_tower_type = tower_type
                        self.selected_tower = None
                        self.selected_hive = None
                return True
        return False

    def handle_world_left_click(self, pos):
        if not self.is_in_viewport(pos):
            return False
        cell = cell_from_pos(self.screen_to_world(pos))
        if not (0 <= cell[0] < GRID_WIDTH and 0 <= cell[1] < GRID_HEIGHT):
            return False

        for bonus in self.bonuses:
            if bonus.contains_cell(cell) and self.is_lit(bonus.cell):
                self.collect_bonus(bonus)
                return True

        for hive in self.hives:
            if hive.contains_cell(cell):
                self.selected_hive = hive
                self.selected_tower = None
                self.selected_tower_type = None
                return True

        for tower in self.towers:
            if tower.contains_cell(cell) and tower.hp > 0:
                self.select_or_toggle_tower(tower)
                return True

        if self.selected_tower_type:
            self.build_tower(self.selected_tower_type, cell)
        else:
            self.selected_tower = None
            self.selected_hive = None
        return True

    def handle_world_right_click(self, pos):
        if self.is_in_viewport(pos):
            cell = cell_from_pos(self.screen_to_world(pos))
            if 0 <= cell[0] < GRID_WIDTH and 0 <= cell[1] < GRID_HEIGHT:
                if self.sell_tower(cell):
                    self.notify("Tower sold")
                    return True
        self.selected_tower_type = None
        self.selected_tower = None
        self.selected_hive = None
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
        icon_size = max(18, scaled(24))
        self.draw_energy_icon(surface, (x + icon_size // 2, y + icon_size // 2), icon_size)
        text_rect = pygame.Rect(x + icon_size + scaled(4), y - scaled(2), scaled(58), icon_size + scaled(4))
        draw_fitted_text(surface, int(amount), text_rect, text_color, max_size=font_size_small, min_size=12)

    def draw_panel_button(self, surface, rect, title, cost=None, enabled=True, selected=False, danger=False, hovered=False, cooldown_progress=None):
        if selected:
            color = UI_CARD_HOT
            stroke = CYAN
        elif danger:
            color = (130, 48, 54) if enabled else (70, 48, 52)
            stroke = UI_BAD if enabled else (92, 70, 74)
        elif enabled:
            color = (48, 84, 66)
            stroke = UI_GOOD
        else:
            color = (48, 52, 59)
            stroke = (82, 86, 94)

        if hovered:
            pulse = ui_pulse()
            color = mix_color(color, WHITE, 0.08 if enabled else 0.04)
            stroke = mix_color(stroke, WHITE if enabled else UI_TEXT_DIM, 0.22 + pulse * 0.16)
            outer = rect.inflate(max(4, scaled(5)), max(4, scaled(5)))
            pygame.draw.rect(surface, stroke, outer, max(2, scaled(3)), border_radius=scaled(8))

        draw_card(surface, rect, color, stroke, radius=scaled(6))
        text_color = WHITE if enabled else (150, 154, 160)
        title_width = rect.w - scaled(20)
        if cost is not None:
            title_width -= scaled(86)
        title_rect = pygame.Rect(rect.x + scaled(10), rect.y + scaled(4), title_width, rect.h - scaled(8))
        draw_fitted_text(surface, title, title_rect, text_color, max_size=font_size_small, min_size=12)
        if cost is not None:
            cost_x = rect.right - scaled(82)
            self.draw_cost(surface, cost, (cost_x, rect.y + (rect.h - max(22, scaled(28))) // 2), WHITE if enabled else (150, 154, 160))
        if cooldown_progress is not None:
            bar_h = max(6, scaled(8))
            bar_rect = pygame.Rect(rect.x + scaled(10), rect.bottom - bar_h - scaled(7), rect.w - scaled(20), bar_h)
            pygame.draw.rect(surface, (20, 24, 31), bar_rect, border_radius=scaled(3))
            fill_rect = bar_rect.copy()
            fill_rect.w = max(2, int(bar_rect.w * max(0, min(1, cooldown_progress))))
            pygame.draw.rect(surface, UI_WARN, fill_rect, border_radius=scaled(3))
            pygame.draw.rect(surface, mix_color(UI_WARN, WHITE, 0.25), bar_rect, max(1, scaled(1)), border_radius=scaled(3))

    def draw_right_panel_buttons(self, surface):
        buttons, right_x, btn_width, start_y, btn_gap, btn_height = self.get_right_panel_layout()
        mouse_pos = pygame.mouse.get_pos()
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
                rect.collidepoint(mouse_pos),
                self.action_cooldown_progress(button.get("cooldown")),
            )

    def draw_left_panel(self, surface):
        sizes = self.panel_sizes()
        pad = sizes["pad"]
        gap = sizes["gap"]
        panel_rect = pygame.Rect(0, 0, SIDE_PANEL_WIDTH, SCREEN_HEIGHT)
        pygame.draw.rect(surface, UI_PANEL, panel_rect)
        pygame.draw.line(surface, UI_STROKE, (SIDE_PANEL_WIDTH - 1, 0), (SIDE_PANEL_WIDTH - 1, SCREEN_HEIGHT), max(1, scaled(2)))

        y = pad
        card_w = SIDE_PANEL_WIDTH - pad * 2
        card_h = sizes["metric_h"]
        total_hives = len(self.hives)
        alive_hives = sum(1 for hive in self.hives if hive.is_alive)
        stats = [
            ("heart", "Generator", f"{int(self.hq.hp)}/{int(self.hq.max_hp)}", UI_BAD),
            ("energy", "Light", str(int(self.money)), GOLD),
            ("tower", "Lamps", f"{self.built_light_tower_count()}/{self.hq.scout_limit}", GENERATOR_BLUE),
            ("target", "Hives", f"{total_hives - alive_hives}/{total_hives}", UI_WARN),
        ]
        for icon_type, label, value, accent in stats:
            rect = pygame.Rect(pad, y, card_w, card_h)
            self.draw_metric_card(surface, rect, icon_type, label, value, accent)
            y += card_h + gap

        pause_button = self.get_pause_button()
        self.draw_panel_button(
            surface,
            pause_button["rect"],
            pause_button["title"],
            None,
            pause_button["enabled"],
            pause_button["selected"],
            hovered=pause_button["rect"].collidepoint(pygame.mouse.get_pos()),
        )

        if self.paused:
            menu_button = self.get_menu_button()
            self.draw_panel_button(
                surface,
                menu_button["rect"],
                menu_button["title"],
                None,
                menu_button["enabled"],
                menu_button["selected"],
                hovered=menu_button["rect"].collidepoint(pygame.mouse.get_pos()),
            )

        build_buttons = self.get_left_build_buttons()
        if build_buttons:
            label_y = build_buttons[0]["rect"].y - scaled(46)
            label_rect = pygame.Rect(pad, label_y, card_w, scaled(32))
            draw_fitted_text(surface, "Build", label_rect, UI_TEXT_DIM, max_size=font_size_small, min_size=12)
        for button in build_buttons:
            self.draw_panel_button(
                surface,
                button["rect"],
                button["title"],
                button["cost"],
                button["enabled"],
                button["selected"],
                hovered=button["rect"].collidepoint(pygame.mouse.get_pos()),
                cooldown_progress=self.action_cooldown_progress(button.get("cooldown")),
            )

    def draw_right_panel_context(self, surface):
        sizes = self.panel_sizes()
        panel_x = SCREEN_WIDTH - SIDE_PANEL_WIDTH
        pad = sizes["pad"]
        gap = sizes["gap"]
        content_x = panel_x + pad
        content_w = SIDE_PANEL_WIDTH - pad * 2
        pygame.draw.rect(surface, UI_PANEL, (panel_x, 0, SIDE_PANEL_WIDTH, SCREEN_HEIGHT))
        pygame.draw.line(surface, UI_STROKE, (panel_x, 0), (panel_x, SCREEN_HEIGHT), max(1, scaled(2)))

        buttons, _, _, button_start_y, _, _ = self.get_right_panel_layout()
        context_bottom = button_start_y - gap
        title_rect = pygame.Rect(content_x, pad, content_w, sizes["title_h"])

        if self.selected_tower and self.selected_tower.hp > 0:
            name = self.get_tower_display_name(self.selected_tower.tower_type)
            draw_fitted_text(surface, f"{name} LVL {self.selected_tower.level}", title_rect, WHITE, max_size=font_size_medium, min_size=15)
            y = title_rect.bottom + gap
            hp_rect = pygame.Rect(content_x, y, content_w, max(44, scaled(54)))
            draw_card(surface, hp_rect, UI_CARD)
            hp_label = pygame.Rect(hp_rect.x + scaled(10), hp_rect.y + scaled(4), hp_rect.w - scaled(20), hp_rect.h // 2)
            draw_fitted_text(surface, "HP", hp_label, UI_TEXT_DIM, max_size=font_size_small - 4, min_size=12)
            hp_bar = pygame.Rect(hp_rect.x + scaled(10), hp_rect.y + hp_rect.h // 2 + scaled(4), hp_rect.w - scaled(20), max(8, scaled(12)))
            draw_progress_bar(surface, hp_bar, self.selected_tower.hp / self.selected_tower.max_hp, UI_GOOD)
            y = hp_rect.bottom + gap

            lines = []
            if self.selected_tower.tower_type == "cannon":
                status = "Broken" if self.selected_tower.broken else (self.selected_tower.specialization or "Base")
                lines = [
                    ("Damage", self.selected_tower.damage),
                    ("Cooldown", f"{self.selected_tower.cooldown_max}f"),
                    ("Mode", status),
                ]
            elif self.selected_tower.tower_type in LIGHT_TOWER_TYPES:
                powered = "Disabled" if self.selected_tower.disabled_timer > 0 else ("Powered" if self.selected_tower.is_powered else "No power")
                pattern = "Beam" if self.selected_tower.tower_type == "lamp" else "Beacon"
                lines = [
                    ("Status", powered),
                    ("Pattern", pattern),
                    ("Level", self.selected_tower.level),
                ]
            for label, value in lines:
                line_h = max(42, scaled(50))
                if y + line_h > context_bottom:
                    break
                self.draw_context_line(surface, label, value, pygame.Rect(content_x, y, content_w, line_h))
                y += line_h + gap
        elif self.selected_hive and self.selected_hive.is_alive:
            draw_fitted_text(surface, "Hive", title_rect, WHITE, max_size=font_size_medium, min_size=16)
            y = title_rect.bottom + gap
            self.draw_context_line(surface, "State", "Visible", pygame.Rect(content_x, y, content_w, max(42, scaled(50))), PURPLE)
            y += max(42, scaled(50)) + gap
            self.draw_context_line(surface, "Artillery cost", ARTILLERY_COST, pygame.Rect(content_x, y, content_w, max(42, scaled(50))), GOLD)
        else:
            draw_fitted_text(surface, f"Generator LVL {self.hq.level}", title_rect, WHITE, max_size=font_size_medium, min_size=16)
            y = title_rect.bottom + gap
            hp_rect = pygame.Rect(content_x, y, content_w, max(44, scaled(54)))
            draw_card(surface, hp_rect, UI_CARD)
            draw_fitted_text(surface, f"{int(self.hq.hp)}/{int(self.hq.max_hp)} HP", pygame.Rect(hp_rect.x + scaled(10), hp_rect.y, hp_rect.w - scaled(20), hp_rect.h // 2), WHITE, max_size=font_size_small, min_size=12)
            hp_bar = pygame.Rect(hp_rect.x + scaled(10), hp_rect.y + hp_rect.h // 2 + scaled(4), hp_rect.w - scaled(20), max(8, scaled(12)))
            draw_progress_bar(surface, hp_bar, self.hq.hp / self.hq.max_hp, UI_WARN)
            y = hp_rect.bottom + gap
            lines = [
                ("Income", f"{self.hq.income_per_second}/s"),
                ("Lamp limit", self.hq.scout_limit),
                ("Upgrade", self.hq.upgrade_cost() if self.hq.upgrade_cost() is not None else "Max"),
            ]
            for label, value in lines:
                line_h = max(42, scaled(50))
                if y + line_h > context_bottom:
                    break
                self.draw_context_line(surface, label, value, pygame.Rect(content_x, y, content_w, line_h))
                y += line_h + gap
        self.draw_right_panel_buttons(surface)

    def get_specialization_options(self):
        return [
            ("Sniper", "Strong shot.\nGood vs armor.", (255, 220, 90), "sniper"),
            ("Howitzer", "Area blast.\nHalf damage.", (255, 145, 70), "scatter"),
            ("Gatling", "Fast bursts.\nBest vs light.", (120, 230, 140), "gatling"),
        ]

    def get_specialization_layout(self):
        menu_w = min(max(640, scaled(760)), SCREEN_WIDTH - scaled(80))
        menu_h = max(300, scaled(360))
        menu_rect = pygame.Rect(0, 0, menu_w, menu_h)
        menu_rect.center = (SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2)

        pad = max(26, scaled(34))
        gap = max(20, scaled(26))
        title_h = max(54, scaled(66))
        card_h = menu_h - pad * 2 - title_h - scaled(18)
        card_w = (menu_w - pad * 2 - gap * 2) // 3
        card_y = menu_rect.y + pad + title_h + scaled(12)
        card_rects = [
            pygame.Rect(menu_rect.x + pad + index * (card_w + gap), card_y, card_w, card_h)
            for index in range(3)
        ]
        return menu_rect, card_rects

    def handle_specialization_click(self, pos):
        menu_rect, card_rects = self.get_specialization_layout()
        for rect, (_, _, _, spec) in zip(card_rects, self.get_specialization_options()):
            if rect.collidepoint(pos):
                self.apply_tower_specialization(spec)
                return True
        if not menu_rect.collidepoint(pos):
            self.cancel_tower_specialization()
            return True
        return False

    def draw_specialization_modal(self, surface):
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 155))
        surface.blit(overlay, (0, 0))

        menu_rect, card_rects = self.get_specialization_layout()
        draw_card(surface, menu_rect, (27, 28, 31), (56, 60, 66), radius=scaled(10))
        title_rect = pygame.Rect(menu_rect.x + scaled(24), menu_rect.y + scaled(18), menu_rect.w - scaled(48), max(54, scaled(66)))
        draw_fitted_text(surface, "Choose modification", title_rect, WHITE, max_size=font_size_medium + scaled(8), min_size=24, align="center")

        current_spec = self.tower_to_specialize.specialization if self.tower_to_specialize else None
        mouse_pos = pygame.mouse.get_pos()
        for rect, (name, description, accent, spec) in zip(card_rects, self.get_specialization_options()):
            selected = spec == current_spec
            hovered = rect.collidepoint(mouse_pos)
            fill = (34, 36, 41) if selected else (27, 28, 31)
            stroke = CYAN if selected else (56, 60, 66)
            if hovered:
                pulse = ui_pulse()
                fill = mix_color(fill, accent, 0.10)
                stroke = mix_color(accent, WHITE, 0.12 + pulse * 0.16)
                outer = rect.inflate(max(6, scaled(8)), max(6, scaled(8)))
                pygame.draw.rect(surface, stroke, outer, max(2, scaled(3)), border_radius=scaled(12))
            draw_card(surface, rect, fill, stroke, radius=scaled(10))

            name_rect = pygame.Rect(rect.x + scaled(12), rect.y + scaled(16), rect.w - scaled(24), max(42, scaled(50)))
            draw_fitted_text(surface, name, name_rect, WHITE, max_size=font_size_small + scaled(8), min_size=20, align="center")

            desc_rect = pygame.Rect(rect.x + scaled(14), name_rect.bottom + scaled(8), rect.w - scaled(28), rect.bottom - name_rect.bottom - scaled(20))
            draw_multiline_text(surface, description, desc_rect, UI_TEXT_DIM, max_size=font_size_small + scaled(2), min_size=16, align="center")

            if selected:
                pygame.draw.rect(surface, accent, rect, max(2, scaled(3)), border_radius=scaled(10))
            if hovered:
                glow_rect = pygame.Rect(rect.x + scaled(14), rect.y + scaled(10), rect.w - scaled(28), max(4, scaled(5)))
                pygame.draw.rect(surface, accent, glow_rect, border_radius=scaled(3))

    def draw_top_status(self, surface):
        pad = max(10, scaled(14))
        gap = max(8, scaled(10))
        card_h = max(52, scaled(64))
        max_w = VIEWPORT_WIDTH - pad * 2
        card_w = max(88, (max_w - gap * 3) // 4)
        total_w = card_w * 4 + gap * 3
        x = VIEWPORT_X + (VIEWPORT_WIDTH - total_w) // 2
        y = VIEWPORT_Y + pad
        alive_hives = sum(1 for hive in self.hives if hive.is_alive)
        spawned_left = self.queued_enemy_count()
        active_count = len(self.enemies)
        items = [
            ("wave", "Wave", self.wave, CYAN),
            ("target", "State", self.wave_state_text(), UI_WARN if self.wave_delay_active else UI_GOOD),
            ("target", "Enemies", f"{active_count}+{spawned_left}", UI_BAD),
            ("energy", "Zoom", f"{int(self.zoom * 100)}%", GENERATOR_BLUE),
        ]
        for index, (icon_type, label, value, accent) in enumerate(items):
            rect = pygame.Rect(x + index * (card_w + gap), y, card_w, card_h)
            self.draw_metric_card(surface, rect, icon_type, label, value, accent)

        bar_rect = pygame.Rect(x, y + card_h + max(4, scaled(6)), total_w, max(7, scaled(9)))
        if self.wave_delay_active and self.wave_delay > 0:
            progress = self.wave_delay_timer / self.wave_delay
            fill = UI_WARN
        elif self.wave_active and self.wave_spawn_total > 0:
            remaining = self.queued_enemy_count() + len(self.enemies)
            progress = 1 - remaining / max(1, self.wave_spawn_total)
            fill = UI_GOOD
        else:
            progress = 1.0 if alive_hives == 0 else 0.0
            fill = CYAN
        draw_progress_bar(surface, bar_rect, progress, fill)

    def draw_pause_overlay(self, surface):
        overlay = pygame.Surface((VIEWPORT_WIDTH, VIEWPORT_HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 105))
        surface.blit(overlay, (VIEWPORT_X, VIEWPORT_Y))
        card_w = min(max(330, scaled(430)), VIEWPORT_WIDTH - scaled(60))
        card_h = max(150, scaled(190))
        rect = pygame.Rect(0, 0, card_w, card_h)
        rect.center = (VIEWPORT_X + VIEWPORT_WIDTH // 2, VIEWPORT_Y + VIEWPORT_HEIGHT // 2)
        draw_card(surface, rect, (22, 28, 38), CYAN, radius=scaled(8))
        title_rect = pygame.Rect(rect.x + scaled(18), rect.y + scaled(18), rect.w - scaled(36), rect.h // 2)
        draw_fitted_text(surface, "Paused", title_rect, WHITE, max_size=font_size_large + scaled(8), min_size=28, align="center")
        state_rect = pygame.Rect(rect.x + scaled(18), rect.y + rect.h // 2, rect.w - scaled(36), rect.h // 3)
        draw_fitted_text(surface, f"Wave {self.wave} - {len(self.enemies)} enemies alive", state_rect, UI_TEXT_DIM, max_size=font_size_small + scaled(4), min_size=16, align="center")

    def draw_menu_action_button(self, surface, rect, title, fill=(48, 84, 66), stroke=UI_GOOD):
        hovered = rect.collidepoint(pygame.mouse.get_pos())
        if hovered:
            pulse = ui_pulse()
            hover_stroke = mix_color(stroke, WHITE, 0.22 + pulse * 0.16)
            outer = rect.inflate(max(5, scaled(7)), max(5, scaled(7)))
            pygame.draw.rect(surface, hover_stroke, outer, max(2, scaled(3)), border_radius=scaled(10))
            fill = mix_color(fill, WHITE, 0.09)
            stroke = hover_stroke
        draw_card(surface, rect, fill, stroke, radius=scaled(8))
        label_rect = rect.inflate(-scaled(18), -scaled(8))
        draw_fitted_text(surface, title, label_rect, WHITE, max_size=font_size_medium + scaled(10), min_size=22, align="center")

    def get_start_buttons(self):
        button_w = min(max(300, scaled(390)), SCREEN_WIDTH - scaled(80))
        button_h = max(72, scaled(88))
        gap = max(16, scaled(22))
        play_rect = pygame.Rect(0, 0, button_w, button_h)
        tutorial_rect = pygame.Rect(0, 0, button_w, button_h)
        play_rect.center = (SCREEN_WIDTH // 2, int(SCREEN_HEIGHT * 0.56))
        tutorial_rect.center = (SCREEN_WIDTH // 2, play_rect.centery + button_h + gap)
        return {
            "play": play_rect,
            "tutorial": tutorial_rect,
        }

    def get_start_button_rect(self):
        return self.get_start_buttons()["play"]

    def handle_start_click(self, pos):
        for action, rect in self.get_start_buttons().items():
            if rect.collidepoint(pos):
                return action
        return None

    def draw_start_screen(self, surface):
        surface.fill((8, 12, 18))
        grid_color = (18, 27, 38)
        step = max(42, scaled(64))
        for x in range(0, SCREEN_WIDTH + step, step):
            pygame.draw.line(surface, grid_color, (x, 0), (x - scaled(160), SCREEN_HEIGHT), max(1, scaled(2)))
        for y in range(0, SCREEN_HEIGHT + step, step):
            pygame.draw.line(surface, (14, 22, 32), (0, y), (SCREEN_WIDTH, y), max(1, scaled(1)))

        title_rect = pygame.Rect(scaled(40), int(SCREEN_HEIGHT * 0.20), SCREEN_WIDTH - scaled(80), max(86, scaled(126)))
        draw_fitted_text(surface, GAME_TITLE, title_rect, GOLD, max_size=max(font_size_large + scaled(12), scaled(124)), min_size=32, align="center")

        subtitle_rect = pygame.Rect(scaled(60), title_rect.bottom + scaled(8), SCREEN_WIDTH - scaled(120), max(34, scaled(44)))
        draw_fitted_text(surface, "Light roads. Stop hives. Save the Generator.", subtitle_rect, UI_TEXT_DIM, max_size=font_size_small + scaled(5), min_size=18, align="center")

        buttons = self.get_start_buttons()
        self.draw_menu_action_button(surface, buttons["play"], "Play", (48, 84, 66), UI_GOOD)
        self.draw_menu_action_button(surface, buttons["tutorial"], "Tutorial", (44, 56, 76), CYAN)

        tips = [
            ("Build", "Light first.\nThen place towers."),
            ("Fight", "Cannons hit enemies\ninside light."),
            ("Move", "Hold RMB to pan.\nWheel to zoom."),
        ]
        card_gap = max(12, scaled(16))
        card_w = min(max(180, scaled(260)), (SCREEN_WIDTH - scaled(100) - card_gap * 2) // 3)
        card_h = max(92, scaled(112))
        total_w = card_w * 3 + card_gap * 2
        x = (SCREEN_WIDTH - total_w) // 2
        y = min(SCREEN_HEIGHT - card_h - scaled(34), buttons["tutorial"].bottom + scaled(42))
        for index, (label, text) in enumerate(tips):
            rect = pygame.Rect(x + index * (card_w + card_gap), y, card_w, card_h)
            draw_card(surface, rect, (22, 28, 38), (56, 70, 86), radius=scaled(7))
            draw_fitted_text(surface, label, pygame.Rect(rect.x + scaled(12), rect.y + scaled(8), rect.w - scaled(24), rect.h // 3), CYAN, max_size=font_size_small + scaled(5), min_size=16, align="center")
            draw_multiline_text(surface, text, pygame.Rect(rect.x + scaled(12), rect.y + rect.h // 3, rect.w - scaled(24), rect.h * 2 // 3 - scaled(6)), UI_TEXT_DIM, max_size=font_size_small, min_size=14)

    def get_tutorial_buttons(self):
        gap = max(16, scaled(22))
        button_w = min(max(190, scaled(250)), (SCREEN_WIDTH - scaled(120)) // 2)
        button_h = max(66, scaled(80))
        y = SCREEN_HEIGHT - button_h - scaled(34)
        back_rect = pygame.Rect(SCREEN_WIDTH // 2 - button_w - gap // 2, y, button_w, button_h)
        play_rect = pygame.Rect(SCREEN_WIDTH // 2 + gap // 2, y, button_w, button_h)
        return {
            "back": back_rect,
            "play": play_rect,
        }

    def handle_tutorial_click(self, pos):
        for action, rect in self.get_tutorial_buttons().items():
            if rect.collidepoint(pos):
                return action
        return None

    def draw_tutorial_card(self, surface, rect, title, body, accent):
        draw_card(surface, rect, (22, 28, 38), (56, 70, 86), radius=scaled(7))
        stripe_w = max(4, scaled(5))
        pygame.draw.rect(surface, accent, (rect.x, rect.y, stripe_w, rect.h), border_radius=scaled(4))
        title_rect = pygame.Rect(rect.x + scaled(18), rect.y + scaled(12), rect.w - scaled(32), max(42, scaled(50)))
        body_rect = pygame.Rect(rect.x + scaled(18), title_rect.bottom + scaled(6), rect.w - scaled(32), rect.bottom - title_rect.bottom - scaled(16))
        draw_fitted_text(surface, title, title_rect, WHITE, max_size=font_size_small + scaled(8), min_size=20)
        draw_multiline_text(surface, body, body_rect, UI_TEXT_DIM, max_size=font_size_small + scaled(3), min_size=16, align="left")

    def draw_tutorial_screen(self, surface):
        surface.fill((8, 12, 18))
        step = max(42, scaled(64))
        for x in range(0, SCREEN_WIDTH + step, step):
            pygame.draw.line(surface, (17, 25, 36), (x, 0), (x - scaled(150), SCREEN_HEIGHT), max(1, scaled(1)))
        for y in range(0, SCREEN_HEIGHT + step, step):
            pygame.draw.line(surface, (13, 20, 30), (0, y), (SCREEN_WIDTH, y), max(1, scaled(1)))

        title_rect = pygame.Rect(scaled(40), scaled(30), SCREEN_WIDTH - scaled(80), max(70, scaled(88)))
        draw_fitted_text(surface, "How to play", title_rect, GOLD, max_size=font_size_large + scaled(10), min_size=32, align="center")
        subtitle_rect = pygame.Rect(scaled(60), title_rect.bottom, SCREEN_WIDTH - scaled(120), max(42, scaled(52)))
        draw_fitted_text(surface, "Build light, upgrade cannons, destroy every hive.", subtitle_rect, UI_TEXT_DIM, max_size=font_size_small + scaled(6), min_size=18, align="center")

        cards = [
            ("Goal", "Keep Generator alive.\nDestroy every hive.", UI_GOOD),
            ("Light", "Build light towers.\nEnemies fight inside light.", GENERATOR_BLUE),
            ("Build", "Pick a tower.\nClick a lit empty cell.", GOLD),
            ("Cannons", "Upgrade cannons.\nPick Sniper, Howitzer,\nor Gatling.", UI_WARN),
            ("Camera", "Hold RMB to move.\nWheel to zoom.", CYAN),
            ("Waves", "Space starts wave.\nPause opens Menu.", UI_BAD),
        ]

        buttons = self.get_tutorial_buttons()
        grid_w = min(max(720, scaled(980)), SCREEN_WIDTH - scaled(80))
        gap = max(12, scaled(16))
        card_w = (grid_w - gap * 2) // 3
        top = subtitle_rect.bottom + scaled(32)
        bottom_limit = buttons["play"].y - scaled(30)
        title_h = max(42, scaled(50))
        body_font_size = font_size_small + scaled(3)
        body_font = ui_font(body_font_size)
        body_w = card_w - scaled(32)
        line_gap = max(2, body_font_size // 7)
        needed_heights = []
        for _, body, _ in cards:
            wrapped = wrap_text_lines(body, body_font, body_w)
            body_h = len(wrapped) * body_font.get_height() + line_gap * max(0, len(wrapped) - 1)
            needed_heights.append(scaled(12) + title_h + scaled(6) + body_h + scaled(16))
        desired_card_h = max(max(needed_heights), max(128, scaled(150)))
        available_card_h = max(92, (bottom_limit - top - gap) // 2)
        card_h = min(desired_card_h, available_card_h)
        total_h = card_h * 2 + gap
        start_x = (SCREEN_WIDTH - grid_w) // 2
        start_y = top + max(0, (bottom_limit - top - total_h) // 2)
        for index, (title, body, accent) in enumerate(cards):
            row = index // 3
            col = index % 3
            rect = pygame.Rect(start_x + col * (card_w + gap), start_y + row * (card_h + gap), card_w, card_h)
            self.draw_tutorial_card(surface, rect, title, body, accent)

        self.draw_menu_action_button(surface, buttons["back"], "Back", (44, 56, 76), CYAN)
        self.draw_menu_action_button(surface, buttons["play"], "Play", (48, 84, 66), UI_GOOD)

    def get_game_over_layout(self):
        card_w = min(max(620, scaled(860)), SCREEN_WIDTH - scaled(80))
        card_h = max(450, scaled(560))
        card_rect = pygame.Rect(0, 0, card_w, card_h)
        card_rect.center = (SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2)

        gap = max(16, scaled(22))
        button_w = min(max(180, scaled(230)), (card_w - gap * 3) // 2)
        button_h = max(66, scaled(80))
        button_y = card_rect.bottom - scaled(34) - button_h
        menu_rect = pygame.Rect(card_rect.centerx - button_w - gap // 2, button_y, button_w, button_h)
        again_rect = pygame.Rect(card_rect.centerx + gap // 2, button_y, button_w, button_h)

        summary_rect = pygame.Rect(
            card_rect.x + scaled(28),
            card_rect.y + max(165, scaled(190)),
            card_rect.w - scaled(56),
            button_y - (card_rect.y + max(165, scaled(190))) - scaled(18),
        )
        return card_rect, menu_rect, again_rect, summary_rect

    def handle_game_over_click(self, pos):
        if not (self.victory or self.defeat):
            return None
        _, menu_rect, again_rect, _ = self.get_game_over_layout()
        if menu_rect.collidepoint(pos):
            return "menu"
        if again_rect.collidepoint(pos):
            return "play_again"
        return None

    def get_match_summary_items(self):
        total_hives = len(self.hives)
        destroyed_hives = sum(1 for hive in self.hives if not hive.is_alive)
        completed_wave = max(1, self.wave - 1) if self.victory else self.wave
        return [
            ("Wave", completed_wave),
            ("Kills", self.enemies_killed),
            ("Hives", f"{destroyed_hives}/{total_hives}"),
            ("Light", int(self.light_earned)),
            ("Bonuses", self.bonuses_collected),
        ]

    def draw_match_summary_panel(self, surface, summary_rect):
        pad = max(12, scaled(18))
        gap = max(8, scaled(10))
        title_h = max(36, scaled(44))
        title_rect = pygame.Rect(summary_rect.x, summary_rect.y, summary_rect.w, title_h)
        draw_fitted_text(surface, "Run Summary", title_rect, WHITE, max_size=font_size_small + scaled(6), min_size=18, align="center")

        stats = self.get_match_summary_items()
        stats_x = summary_rect.x
        stats_y = title_rect.bottom + max(5, scaled(6))
        stats_w = summary_rect.w
        stats_h = summary_rect.bottom - stats_y
        card_w = max(64, (stats_w - gap * (len(stats) - 1)) // len(stats))
        for index, (label, value) in enumerate(stats):
            rect = pygame.Rect(stats_x + index * (card_w + gap), stats_y, card_w, stats_h)
            draw_card(surface, rect, (30, 38, 51), (62, 78, 96), radius=scaled(5))
            label_rect = pygame.Rect(rect.x + scaled(8), rect.y + scaled(4), rect.w - scaled(16), rect.h // 2)
            value_rect = pygame.Rect(rect.x + scaled(8), rect.y + rect.h // 2 - scaled(2), rect.w - scaled(16), rect.h // 2)
            draw_fitted_text(surface, label, label_rect, UI_TEXT_DIM, max_size=font_size_small + scaled(1), min_size=12, align="center")
            draw_fitted_text(surface, value, value_rect, WHITE, max_size=font_size_small + scaled(6), min_size=16, align="center")

    def draw_game_over_overlay(self, surface):
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 170))
        surface.blit(overlay, (0, 0))

        card_rect, menu_rect, again_rect, summary_rect = self.get_game_over_layout()
        accent = GOLD if self.victory else UI_BAD
        fill = (24, 30, 42) if self.victory else (42, 24, 30)
        title = "VICTORY!" if self.victory else "DEFEAT"
        detail = "All hives destroyed." if self.victory else "Generator destroyed."

        draw_card(surface, card_rect, fill, accent, radius=scaled(8))
        title_rect = pygame.Rect(card_rect.x + scaled(24), card_rect.y + scaled(32), card_rect.w - scaled(48), max(72, scaled(96)))
        draw_fitted_text(surface, title, title_rect, accent, max_size=font_size_large + scaled(10), min_size=32, align="center")
        detail_rect = pygame.Rect(card_rect.x + scaled(32), title_rect.bottom, card_rect.w - scaled(64), max(42, scaled(58)))
        draw_fitted_text(surface, detail, detail_rect, UI_TEXT_DIM, max_size=font_size_small + scaled(6), min_size=18, align="center")

        self.draw_match_summary_panel(surface, summary_rect)
        self.draw_menu_action_button(surface, menu_rect, "Menu", (44, 56, 76), CYAN)
        self.draw_menu_action_button(surface, again_rect, "Again", (48, 84, 66), UI_GOOD)

    def get_exit_confirm_layout(self):
        card_w = min(max(350, scaled(520)), SCREEN_WIDTH - scaled(80))
        card_h = max(250, scaled(300))
        card_rect = pygame.Rect(0, 0, card_w, card_h)
        card_rect.center = (SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2)

        gap = max(16, scaled(22))
        button_w = min(max(150, scaled(200)), (card_w - gap * 3) // 2)
        button_h = max(64, scaled(76))
        button_y = card_rect.bottom - scaled(30) - button_h
        yes_rect = pygame.Rect(card_rect.centerx - button_w - gap // 2, button_y, button_w, button_h)
        no_rect = pygame.Rect(card_rect.centerx + gap // 2, button_y, button_w, button_h)
        return card_rect, yes_rect, no_rect

    def handle_exit_confirm_click(self, pos):
        if not self.exit_confirm_open:
            return None
        _, yes_rect, no_rect = self.get_exit_confirm_layout()
        if yes_rect.collidepoint(pos):
            return "menu"
        if no_rect.collidepoint(pos):
            self.cancel_exit_confirm()
            return "cancel"
        return None

    def draw_exit_confirm_overlay(self, surface):
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 150))
        surface.blit(overlay, (0, 0))

        card_rect, yes_rect, no_rect = self.get_exit_confirm_layout()
        draw_card(surface, card_rect, (24, 30, 42), UI_WARN, radius=scaled(8))
        title_rect = pygame.Rect(card_rect.x + scaled(24), card_rect.y + scaled(28), card_rect.w - scaled(48), max(58, scaled(74)))
        draw_fitted_text(surface, "Exit to menu?", title_rect, UI_WARN, max_size=font_size_medium + scaled(10), min_size=24, align="center")
        detail_rect = pygame.Rect(card_rect.x + scaled(32), title_rect.bottom, card_rect.w - scaled(64), max(42, scaled(56)))
        draw_fitted_text(surface, "Current run will be lost.", detail_rect, UI_TEXT_DIM, max_size=font_size_small + scaled(5), min_size=18, align="center")

        self.draw_menu_action_button(surface, yes_rect, "Yes", (130, 48, 54), UI_BAD)
        self.draw_menu_action_button(surface, no_rect, "No", (48, 84, 66), UI_GOOD)

    def draw_notification(self, surface):
        if self.notification_timer <= 0 or not self.notification_text:
            return
        text = fitted_text_surface(self.notification_text, WHITE, VIEWPORT_WIDTH - scaled(80), scaled(44), font_size_medium, 14)
        center_y = VIEWPORT_Y + max(92, scaled(120))
        rect = text.get_rect(center=(SCREEN_WIDTH // 2, center_y))
        bg = rect.inflate(scaled(34), scaled(18))
        draw_card(surface, bg, (24, 30, 42), CYAN, radius=scaled(6))
        surface.blit(text, rect)

    def draw_fog(self, surface):
        if self.fog_dirty:
            self.fog_surface.fill((0, 0, 0, 0))
            for x in range(GRID_WIDTH):
                for y in range(GRID_HEIGHT):
                    if not self.is_revealed((x, y)):
                        rect = pygame.Rect(x * CELL_SIZE, y * CELL_SIZE, CELL_SIZE, CELL_SIZE)
                        pygame.draw.rect(self.fog_surface, FOG_WHITE + (255,), rect)
            self.fog_dirty = False
        surface.blit(self.fog_surface, (FIELD_OFFSET_X, FIELD_OFFSET_Y))

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
            if self.can_place_light_building(cell):
                preview_tower = self.make_preview_tower(self.selected_tower_type, cell)

        if not preview_tower:
            return
        self.draw_light_outline(surface, self.get_light_coverage(preview_tower), CYAN)

    def draw_build_cell_preview(self, surface):
        if not self.selected_tower_type:
            return
        mouse_pos = pygame.mouse.get_pos()
        if not self.is_in_viewport(mouse_pos):
            return
        cell = cell_from_pos(self.screen_to_world(mouse_pos))
        if not (0 <= cell[0] < GRID_WIDTH and 0 <= cell[1] < GRID_HEIGHT):
            return
        rect = pygame.Rect(
            FIELD_OFFSET_X + cell[0] * CELL_SIZE,
            FIELD_OFFSET_Y + cell[1] * CELL_SIZE,
            CELL_SIZE,
            CELL_SIZE,
        ).inflate(-scaled(3), -scaled(3))
        can_place = self.can_place_light_building(cell)
        color = CYAN if can_place else UI_BAD
        pygame.draw.rect(surface, BLACK, rect.inflate(scaled(4), scaled(4)), max(1, scaled(3)))
        pygame.draw.rect(surface, color, rect, max(2, scaled(4)))

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

        for bonus in self.bonuses:
            bonus.draw(surface)

        for hive in self.hives:
            hive.draw(surface)

        for tower in self.towers:
            tower.draw(surface)

        for enemy in self.enemies:
            enemy.draw(surface)

        self.hq.draw(surface)
        self.draw_fog(surface)
        self.draw_build_cell_preview(surface)
        self.draw_light_preview(surface)

        if self.selected_tower and self.selected_tower.hp > 0:
            rect = self.selected_tower.world_rect().inflate(scaled(8), scaled(8))
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
        if self.screen_state != "playing":
            return

        if self.exit_confirm_open:
            return

        if self.defeat or self.victory:
            return

        if self.notification_timer > 0:
            self.notification_timer -= 1

        if self.paused:
            return

        if self.tower_specialization_pending:
            return

        self.tick_action_cooldowns()

        self.hq.update(self)
        if self.hq.hp <= 0:
            self.defeat = True
            return

        if self.wave_delay_active:
            self.wave_delay_timer += 1
            if self.wave_delay_timer >= self.wave_delay:
                self.wave_delay_active = False
                self.wave_timer = 39

        if not self.wave_active and not self.wave_delay_active and self.first_wave_started:
            self.wave_interval_timer += 1
            if self.wave_interval_timer >= self.wave_interval and self.wave <= self.total_waves:
                self.start_wave(early=False)

        if self.wave_active and not self.wave_delay_active and self.spawn_queue:
            self.wave_timer += 1
            if self.wave_timer >= 40:
                spawn_batch = self.spawn_queue.pop(0)
                if isinstance(spawn_batch, tuple):
                    spawn_batch = [spawn_batch]
                for e_type, road_key, lane in spawn_batch:
                    enemy = self.create_wave_enemy(e_type, road_key, lane)
                    if enemy:
                        self.enemies.append(enemy)
                self.wave_timer = 0

        for enemy in self.enemies[:]:
            enemy.move(self.hq, self)
            if not enemy.alive:
                if enemy.hp <= 0:
                    self.money += enemy.reward
                    self.light_earned += enemy.reward
                    self.enemies_killed += 1
                self.enemies.remove(enemy)

        self.update_dimmers()
        self.update_lighting()

        for tower in self.towers:
            tower.update(self.enemies, self)

        if self.wave_active and not self.spawn_queue and len(self.enemies) == 0:
            self.wave_active = False
            self.wave += 1
            self.wave_interval_timer = 0
            if all(not hive.is_alive for hive in self.hives):
                self.victory = True

    def draw_ui(self, surface):
        self.draw_left_panel(surface)
        self.draw_right_panel_context(surface)
        self.draw_top_status(surface)

        if self.paused:
            self.draw_pause_overlay(surface)

        if self.tower_specialization_pending:
            self.draw_specialization_modal(surface)

        if self.victory or self.defeat:
            self.draw_game_over_overlay(surface)
        elif self.exit_confirm_open:
            self.draw_exit_confirm_overlay(surface)

        self.draw_notification(surface)


game = Game(show_start=True)
world_surface = pygame.Surface((FIELD_WIDTH, FIELD_HEIGHT))
running = True

while running:
    screen.fill(BLACK)

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if event.type == pygame.KEYDOWN:
            if game.is_start_screen():
                if event.key in (pygame.K_RETURN, pygame.K_SPACE):
                    game = Game(show_start=False)
                elif event.key == pygame.K_t:
                    game.screen_state = "tutorial"
                elif event.key == pygame.K_ESCAPE:
                    running = False
                continue
            if game.is_tutorial_screen():
                if event.key in (pygame.K_RETURN, pygame.K_SPACE):
                    game = Game(show_start=False)
                elif event.key == pygame.K_ESCAPE:
                    game.screen_state = "start"
                continue
            if game.victory or game.defeat:
                if event.key in (pygame.K_RETURN, pygame.K_SPACE):
                    game = Game(show_start=False)
                elif event.key == pygame.K_ESCAPE:
                    game = Game(show_start=True)
                continue
            if game.exit_confirm_open:
                if event.key in (pygame.K_RETURN, pygame.K_y):
                    game = Game(show_start=True)
                elif event.key in (pygame.K_ESCAPE, pygame.K_n):
                    game.cancel_exit_confirm()
                continue
            if event.key == pygame.K_ESCAPE:
                if game.tower_specialization_pending:
                    game.cancel_tower_specialization()
                else:
                    running = False
            if event.key == pygame.K_p:
                game.toggle_pause()

        if game.is_start_screen() or game.is_tutorial_screen() or game.victory or game.defeat:
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                pos = pygame.mouse.get_pos()
                if game.is_start_screen():
                    action = game.handle_start_click(pos)
                elif game.is_tutorial_screen():
                    action = game.handle_tutorial_click(pos)
                else:
                    action = game.handle_game_over_click(pos)
                if action in ("play", "play_again"):
                    game = Game(show_start=False)
                elif action == "tutorial":
                    game.screen_state = "tutorial"
                elif action == "back":
                    game.screen_state = "start"
                elif action == "menu":
                    game = Game(show_start=True)
            continue

        if game.exit_confirm_open:
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                pos = pygame.mouse.get_pos()
                action = game.handle_exit_confirm_click(pos)
                if action == "menu":
                    game = Game(show_start=True)
            continue

        if event.type == pygame.MOUSEWHEEL:
            pos = pygame.mouse.get_pos()
            if game.is_in_viewport(pos):
                game.zoom_at(pos, 1.12 ** event.y)

        if event.type == pygame.MOUSEBUTTONUP:
            if event.button == 3:
                pos = getattr(event, "pos", pygame.mouse.get_pos())
                should_handle_click = game.end_camera_drag(event.button)
                if should_handle_click:
                    game.handle_world_right_click(pos)

        if event.type == pygame.MOUSEMOTION and game.dragging_camera:
            game.update_camera_drag(event)

        if event.type == pygame.MOUSEBUTTONDOWN:
            pos = pygame.mouse.get_pos()
            if event.button == 3 and game.is_in_viewport(pos):
                game.begin_camera_drag(pos, event.button)
                continue
            if event.button == 3:
                if not game.is_in_viewport(pos):
                    game.selected_tower_type = None
                    game.selected_tower = None
                    game.selected_hive = None
                continue
            if event.button != 1:
                continue
            
            if game.tower_specialization_pending:
                game.handle_specialization_click(pos)
                continue
            
            if pos[0] >= SCREEN_WIDTH - SIDE_PANEL_WIDTH:
                game.handle_right_panel_click(pos)
            elif pos[0] < SIDE_PANEL_WIDTH:
                game.handle_left_panel_click(pos)
            elif game.is_in_viewport(pos):
                game.handle_world_left_click(pos)

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

    if game.is_start_screen():
        game.draw_start_screen(screen)
    elif game.is_tutorial_screen():
        game.draw_tutorial_screen(screen)
    else:
        if not game.exit_confirm_open and not game.tower_specialization_pending and not game.victory and not game.defeat:
            game.update_camera()
        game.update()

        game.draw_world(world_surface)
        game.blit_world(screen, world_surface)
        game.draw_ui(screen)

    pygame.display.flip()
    clock.tick(60)

pygame.quit()
sys.exit()
