"""
game/world.py - World Map System (Expanded)
=============================================
Tile-based map system dengan peta lebih luas dan interaktif.
"""

import random
from engine.renderer import TILE_SIZE

# Tile types
TILE_GRASS = 0
TILE_WALL = 1
TILE_WATER = 2
TILE_PATH = 3
TILE_DOOR = 4
TILE_NPC = 5
TILE_CHEST = 6
TILE_DUNGEON_ENTRANCE = 7
TILE_FLOOR = 8
TILE_STAIRS_DOWN = 9
TILE_STAIRS_UP = 10
TILE_BOSS = 11
TILE_SAVE_POINT = 12
TILE_HOUSE = 13
TILE_TREE = 14
TILE_FLOWER = 15
TILE_FENCE = 16
TILE_BRIDGE = 17
TILE_SIGN = 18
TILE_BARREL = 19
TILE_LAMP = 20
TILE_FOUNTAIN = 21
TILE_SHOP = 22

WALKABLE = {TILE_GRASS, TILE_PATH, TILE_DOOR, TILE_NPC, TILE_CHEST,
            TILE_DUNGEON_ENTRANCE, TILE_FLOOR, TILE_STAIRS_DOWN,
            TILE_STAIRS_UP, TILE_BOSS, TILE_SAVE_POINT, TILE_BRIDGE,
            TILE_SIGN, TILE_FOUNTAIN, TILE_SHOP, TILE_FLOWER}


class GameMap:
    def __init__(self, name, width, height, tiles, npcs=None, encounters=True, floor=1):
        self.name = name
        self.width = width
        self.height = height
        self.tiles = tiles
        self.npcs = npcs or {}
        self.encounters = encounters
        self.floor = floor
        self.opened_chests = set()

    def get_tile(self, x, y):
        if 0 <= x < self.width and 0 <= y < self.height:
            return self.tiles[y][x]
        return TILE_WALL

    def is_walkable(self, x, y):
        return self.get_tile(x, y) in WALKABLE

    def check_encounter(self):
        if not self.encounters:
            return False
        return random.random() < 0.07


def create_town_map():
    """Create larger town map (48x36)."""
    W, H = 48, 36
    tiles = [[TILE_GRASS for _ in range(W)] for _ in range(H)]

    # Border walls
    for x in range(W):
        tiles[0][x] = TILE_WALL
        tiles[H-1][x] = TILE_WALL
    for y in range(H):
        tiles[y][0] = TILE_WALL
        tiles[y][W-1] = TILE_WALL

    # Main roads (cross shape)
    for x in range(3, W-3):
        tiles[17][x] = TILE_PATH
        tiles[18][x] = TILE_PATH
    for y in range(3, H-3):
        tiles[y][23] = TILE_PATH
        tiles[y][24] = TILE_PATH

    # Secondary paths
    for x in range(8, 20):
        tiles[10][x] = TILE_PATH
    for x in range(28, 40):
        tiles[10][x] = TILE_PATH
    for x in range(10, 38):
        tiles[27][x] = TILE_PATH
    for y in range(10, 18):
        tiles[y][12] = TILE_PATH
    for y in range(18, 28):
        tiles[y][35] = TILE_PATH

    # Trees around border
    for x in range(2, W-2):
        if tiles[1][x] == TILE_GRASS:
            tiles[1][x] = TILE_TREE
        if tiles[H-2][x] == TILE_GRASS and x % 3 != 0:
            tiles[H-2][x] = TILE_TREE
    for y in range(2, H-2):
        if tiles[y][1] == TILE_GRASS:
            tiles[y][1] = TILE_TREE
        if tiles[y][W-2] == TILE_GRASS and y % 3 != 0:
            tiles[y][W-2] = TILE_TREE

    # Forest area (top-left)
    for y in range(3, 9):
        for x in range(3, 10):
            if (x + y) % 2 == 0:
                tiles[y][x] = TILE_TREE

    # Flower garden
    for y in range(3, 7):
        for x in range(28, 35):
            if (x + y) % 2 == 0:
                tiles[y][x] = TILE_FLOWER

    # Water pond (top-right)
    for y in range(4, 9):
        for x in range(38, 45):
            tiles[y][x] = TILE_WATER
    tiles[4][37] = TILE_GRASS
    tiles[8][37] = TILE_GRASS

    # Bridge over water
    tiles[6][37] = TILE_BRIDGE
    tiles[6][38] = TILE_BRIDGE

    # ---- BUILDINGS ----
    def place_building(tx, ty, w=5, h=4, tile_type=TILE_HOUSE):
        for y in range(ty, ty + h):
            for x in range(tx, tx + w):
                if 0 <= x < W and 0 <= y < H:
                    tiles[y][x] = tile_type
        # Door
        dx = tx + w // 2
        dy = ty + h
        if 0 <= dy < H:
            tiles[dy][dx] = TILE_DOOR
            tiles[dy][dx-1] = TILE_PATH
            tiles[dy][dx+1] = TILE_PATH

    # Houses
    place_building(5, 12, 5, 4)   # House 1
    place_building(15, 12, 5, 4)  # House 2
    place_building(28, 12, 5, 4)  # House 3
    place_building(37, 12, 5, 4)  # House 4

    # Shop
    place_building(7, 21, 6, 4, TILE_SHOP)
    # Inn
    place_building(33, 21, 6, 4, TILE_HOUSE)

    # Fences around houses
    for x in range(4, 11):
        tiles[11][x] = TILE_FENCE
    for x in range(14, 21):
        tiles[11][x] = TILE_FENCE

    # Lamps along main road
    for x in range(5, W-5, 6):
        if tiles[16][x] == TILE_GRASS:
            tiles[16][x] = TILE_LAMP
        if tiles[19][x] == TILE_GRASS:
            tiles[19][x] = TILE_LAMP

    # Barrels near shop
    tiles[25][8] = TILE_BARREL
    tiles[25][9] = TILE_BARREL
    tiles[25][12] = TILE_BARREL

    # Signs
    tiles[17][10] = TILE_SIGN
    tiles[17][33] = TILE_SIGN

    # Fountain in town center
    tiles[16][23] = TILE_FOUNTAIN
    tiles[16][24] = TILE_FOUNTAIN
    tiles[15][23] = TILE_FOUNTAIN
    tiles[15][24] = TILE_FOUNTAIN

    # Save point
    tiles[19][24] = TILE_SAVE_POINT

    # NPCs
    tiles[18][14] = TILE_NPC  # Elder
    tiles[17][30] = TILE_NPC  # Guard
    tiles[10][12] = TILE_NPC  # Child
    tiles[27][35] = TILE_NPC  # Adventurer
    tiles[25][10] = TILE_NPC  # Merchant
    tiles[18][37] = TILE_NPC  # Healer

    # Dungeon entrance (bottom right)
    for x in range(40, 45):
        tiles[33][x] = TILE_PATH
    tiles[33][45] = TILE_DUNGEON_ENTRANCE
    # Path to dungeon
    for y in range(28, 34):
        tiles[y][42] = TILE_PATH

    # Chest in hidden spot
    tiles[5][5] = TILE_CHEST

    npcs = {
        (14, 18): {
            'name': 'Elder Marcus',
            'dialog': [
                "Selamat datang di Crystal Village, pejuang muda.",
                "Crystal Dragon telah bangkit di dungeon di tenggara...",
                "Ia mengancam seluruh kerajaan kita!",
                "Hanya pejuang terpilih yang bisa mengalahkannya.",
                "Pergilah, dan semoga Crystal memberkatimu!",
            ]
        },
        (30, 17): {
            'name': 'Guard Roland',
            'dialog': [
                "Hati-hati di dungeon! Monster di sana sangat kuat.",
                "Pastikan kamu membawa Potion yang cukup.",
                "Lantai 3 dungeon adalah sarang sang Dragon...",
            ]
        },
        (12, 10): {
            'name': 'Little Mira',
            'dialog': [
                "Hei kakak! Mau main petak umpet?",
                "Eh... kakak sibuk ya? Hehe...",
                "Ada chest tersembunyi di hutan lho!",
            ]
        },
        (35, 27): {
            'name': 'Adventurer Kai',
            'dialog': [
                "Aku sudah mencoba masuk dungeon...",
                "Tapi Dark Knight di lantai 3 terlalu kuat!",
                "Tip: Skeleton lemah terhadap Holy magic.",
                "Dan Dragon lemah terhadap Ice!",
            ]
        },
        (10, 25): {
            'name': 'Merchant Nina',
            'dialog': [
                "Selamat datang di toko saya!",
                "*Kamu mendapat 3 Potion dan 2 Ether!*",
            ],
            'action': 'shop'
        },
        (37, 18): {
            'name': 'Priestess Aria',
            'dialog': [
                "Biarkan aku menyembuhkan lukamu...",
                "*HP dan MP seluruh party dipulihkan!*",
            ],
            'action': 'heal'
        },
    }

    # Sign interactions
    npcs[(10, 17)] = {'name': 'Sign', 'dialog': ["← Shop    Town Center →"]}
    npcs[(33, 17)] = {'name': 'Sign', 'dialog': ["← Town Center    Dungeon →"]}

    return GameMap('Crystal Village', W, H, tiles, npcs, encounters=False)


def create_dungeon_maps():
    """Create 3-floor dungeon."""
    dungeons = []
    W, H = 40, 30

    # --- Floor 1 ---
    t1 = [[TILE_WALL for _ in range(W)] for _ in range(H)]
    # Main corridors
    for y in range(3, 27):
        for x in range(3, 8):
            t1[y][x] = TILE_FLOOR
    for x in range(3, 25):
        t1[14][x] = TILE_FLOOR
        t1[15][x] = TILE_FLOOR
    for y in range(10, 27):
        for x in range(22, 28):
            t1[y][x] = TILE_FLOOR
    # Rooms
    for y in range(4, 10):
        for x in range(12, 20):
            t1[y][x] = TILE_FLOOR
    for y in range(18, 25):
        for x in range(12, 20):
            t1[y][x] = TILE_FLOOR
    # Side room
    for y in range(4, 10):
        for x in range(30, 37):
            t1[y][x] = TILE_FLOOR
    for x in range(25, 31):
        t1[7][x] = TILE_FLOOR

    t1[3][3] = TILE_STAIRS_UP
    t1[25][25] = TILE_STAIRS_DOWN
    t1[6][16] = TILE_CHEST
    t1[21][15] = TILE_CHEST
    t1[6][33] = TILE_CHEST
    t1[14][10] = TILE_SAVE_POINT
    dungeons.append(GameMap('Dungeon B1', W, H, t1, encounters=True, floor=1))

    # --- Floor 2 ---
    t2 = [[TILE_WALL for _ in range(W)] for _ in range(H)]
    for y in range(3, 27):
        t2[y][4] = TILE_FLOOR
        t2[y][5] = TILE_FLOOR
    for x in range(4, 36):
        t2[6][x] = TILE_FLOOR
        t2[7][x] = TILE_FLOOR
        t2[20][x] = TILE_FLOOR
        t2[21][x] = TILE_FLOOR
    for y in range(6, 22):
        t2[y][18] = TILE_FLOOR
        t2[y][19] = TILE_FLOOR
        t2[y][34] = TILE_FLOOR
        t2[y][35] = TILE_FLOOR
    for x in range(18, 36):
        t2[13][x] = TILE_FLOOR
        t2[14][x] = TILE_FLOOR
    # Open rooms
    for y in range(9, 12):
        for x in range(8, 15):
            t2[y][x] = TILE_FLOOR
    for y in range(23, 27):
        for x in range(25, 33):
            t2[y][x] = TILE_FLOOR

    t2[3][4] = TILE_STAIRS_UP
    t2[13][34] = TILE_STAIRS_DOWN
    t2[20][28] = TILE_CHEST
    t2[10][11] = TILE_CHEST
    t2[7][25] = TILE_SAVE_POINT
    dungeons.append(GameMap('Dungeon B2', W, H, t2, encounters=True, floor=2))

    # --- Floor 3 (Boss) ---
    t3 = [[TILE_WALL for _ in range(W)] for _ in range(H)]
    # Grand hall
    for y in range(4, 26):
        for x in range(4, 36):
            t3[y][x] = TILE_FLOOR
    # Pillars
    for py in [8, 14, 20]:
        for px in [10, 16, 24, 30]:
            t3[py][px] = TILE_WALL
    t3[4][4] = TILE_STAIRS_UP
    t3[14][20] = TILE_BOSS
    t3[24][18] = TILE_CHEST
    t3[6][8] = TILE_SAVE_POINT
    dungeons.append(GameMap('Dragon Lair', W, H, t3, encounters=False, floor=3))

    return dungeons


class WorldManager:
    def __init__(self):
        self.maps = {}
        self.current_map = None
        self.dungeon_floors = []

    def init(self):
        self.maps['town'] = create_town_map()
        self.dungeon_floors = create_dungeon_maps()
        for i, d in enumerate(self.dungeon_floors):
            self.maps[f'dungeon_{i}'] = d
        self.current_map = self.maps['town']

    def get_map(self, name):
        return self.maps.get(name)

    def switch_map(self, name):
        if name in self.maps:
            self.current_map = self.maps[name]
            return True
        return False
