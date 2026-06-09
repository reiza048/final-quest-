import pygame
import math

PALETTES = {
    'warrior': {
        '.': None, 'k': (20,20,20), 'S': (230,190,150), 's': (200,160,120),
        'w': (255,255,255), 'p': (30,30,60), 'H': (100,60,30), 'h': (70,40,20),
        'A': (180,40,40), 'a': (140,30,30), 'L': (60,50,80), 'l': (40,35,55),
        'B': (120,80,40), 'b': (90,60,30), 'W': (180,180,200), 'M': (180,140,120),
    },
    'mage': {
        '.': None, 'k': (20,20,20), 'S': (230,195,160), 's': (200,165,130),
        'w': (255,255,255), 'p': (30,30,60), 'H': (220,220,240), 'h': (180,180,210),
        'A': (100,50,160), 'a': (70,35,120), 'L': (80,40,130), 'l': (60,30,100),
        'B': (100,50,140), 'b': (70,35,100), 'W': (160,120,60), 'M': (180,140,120),
    },
    'healer': {
        '.': None, 'k': (20,20,20), 'S': (235,200,170), 's': (205,170,140),
        'w': (255,255,255), 'p': (30,50,30), 'H': (80,50,30), 'h': (55,35,20),
        'A': (240,240,230), 'a': (200,210,190), 'L': (60,120,70), 'l': (40,90,50),
        'B': (80,60,40), 'b': (60,45,30), 'W': (200,170,60), 'M': (180,140,120),
    },
}

CHAR_DOWN_STAND = [
    "................",
    ".....kHHHk......",
    "....kHHHHHk.....",
    "....kHHHHHk.....",
    "...kkSSSSSk.....",
    "...kSwpwpSk.....",
    "...kSSSMSSk.....",
    "...kkSSSSk......",
    "...kAAAAAkk.....",
    "..kAAAAAAkWk....",
    "..kAAaAAkWk.....",
    "..kAAAAAkk......",
    "...kAAAAk.......",
    "...kLLkLLk......",
    "...kLLkLLk......",
    "...kLlkLlk......",
    "..kBBk.kBBk.....",
    "..kbbk.kbbk.....",
    "................",
    "................",
]

CHAR_DOWN_WALK1 = [
    "................",
    ".....kHHHk......",
    "....kHHHHHk.....",
    "....kHHHHHk.....",
    "...kkSSSSSk.....",
    "...kSwpwpSk.....",
    "...kSSSMSSk.....",
    "...kkSSSSk......",
    "...kAAAAAkk.....",
    "..kAAAAAAkWk....",
    "..kAAaAAkWk.....",
    "..kAAAAAkk......",
    "...kAAAAk.......",
    "..kLLk.kLLk.....",
    "..kLLk..kLk.....",
    "..kLlk..klk.....",
    ".kBBk...kBBk....",
    ".kbbk...kbbk....",
    "................",
    "................",
]

CHAR_DOWN_WALK2 = [
    "................",
    ".....kHHHk......",
    "....kHHHHHk.....",
    "....kHHHHHk.....",
    "...kkSSSSSk.....",
    "...kSwpwpSk.....",
    "...kSSSMSSk.....",
    "...kkSSSSk......",
    "...kAAAAAkk.....",
    "..kAAAAAAkWk....",
    "..kAAaAAkWk.....",
    "..kAAAAAkk......",
    "...kAAAAk.......",
    "..kLLk.kLLk.....",
    "..kLk..kLLk.....",
    "..klk..kLlk.....",
    ".kBBk...kBBk....",
    ".kbbk...kbbk....",
    "................",
    "................",
]

CHAR_UP_STAND = [
    "................",
    ".....kHHHk......",
    "....kHHHHHk.....",
    "....kHHHHHk.....",
    "...kHHHHHHHk....",
    "...kHHHHHHHk....",
    "...kkSSSSSk.....",
    "....kSSSSk......",
    "...kAAAAAkk.....",
    "..kAAaAAAkAk....",
    "..kAAAAAAkAk....",
    "..kAAAAAkk......",
    "...kAAAAk.......",
    "...kLLkLLk......",
    "...kLLkLLk......",
    "...kLlkLlk......",
    "..kBBk.kBBk.....",
    "..kbbk.kbbk.....",
    "................",
    "................",
]

CHAR_LEFT_STAND = [
    "................",
    "....kHHHk.......",
    "...kHHHHk.......",
    "...kHHHHk.......",
    "...kSSSSk.......",
    "...kwpSSk.......",
    "...kMSSSk.......",
    "....kSSk........",
    "...kAAAAk.......",
    "..WkAAAAkk......",
    "..WkAaAAk.......",
    "...kAAAAk.......",
    "...kAAAk........",
    "...kLLLk........",
    "...kLLLk........",
    "...kLllk........",
    "...kBBBk........",
    "...kbbbk........",
    "................",
    "................",
]

SLIME_PALETTE = {
    '.': None, 'k': (20,40,20), 'G': (80,200,80), 'g': (60,160,60),
    'L': (120,230,120), 'w': (255,255,255), 'p': (20,20,20),
}

SLIME_SPRITE = [
    ".......kkkk.......",
    "......kLLLLk......",
    ".....kLLLLLLk.....",
    "....kGLLLLLLGk....",
    "...kGGLLLLLLGGk...",
    "..kGGGwpGGwpGGGk..",
    "..kGGGGGGGGGGGGk..",
    "..kGGGGGmmGGGGGk..",
    ".kGGGGGGGGGGGGGGk.",
    ".kgGGGGGGGGGGGGgk.",
    ".kggGGGGGGGGGGggk.",
    "..kgggGGGGGGgggk..",
    "...kkgggggggggkk..",
    ".....kkkkkkkk.....",
]

GOBLIN_PALETTE = {
    '.': None, 'k': (20,20,10), 'G': (100,150,60), 'g': (70,110,40),
    'S': (120,170,70), 'w': (255,255,200), 'p': (200,40,40),
    'B': (100,70,40), 'b': (70,50,30), 'W': (160,160,170),
}

GOBLIN_SPRITE = [
    "....kkk...kkk...",
    "...kGGGkkkGGGk..",
    "...kGGGGGGGGGk..",
    "..kGGGGGGGGGGGk.",
    "..kGwpGGGGGwpGk.",
    "..kGGGGGGGGGGGk.",
    "..kGGGGkkGGGGGk.",
    "...kGGGGGGGGGk..",
    "...kkSSSSSSSk...",
    "..kBkSSSSSSSk...",
    "..kWkSSgSSSSk...",
    "..kkBSSSSSSSk...",
    "....kSSSSSSk....",
    "....kBBkkBBk....",
    "....kBBkkBBk....",
    "...kbbkkkbbk....",
    "...kkkk.kkkk....",
]

SKELETON_PALETTE = {
    '.': None, 'k': (40,35,30), 'W': (230,225,210), 'w': (200,195,180),
    'D': (50,45,40), 'e': (180,40,40), 'g': (80,75,70),
}

SKELETON_SPRITE = [
    "....kkkkkkk.....",
    "...kWWWWWWWk....",
    "..kWWeWWWeWWk...",
    "..kWWWWWWWWWk...",
    "..kWWWDDDWWWk...",
    "...kWWWWWWWk....",
    "....kkWWWkk.....",
    "..kkkkWWWkkkk...",
    ".kwWWkWWWkWWwk..",
    "..kwWkwwwkWwk...",
    "...kkwwwwwkk....",
    "....kwwwwwk.....",
    "....kwwkwwk.....",
    "....kwwkwwk.....",
    "...kwwk.kwwk....",
    "...kkkk.kkkk....",
]

DRAGON_PALETTE = {
    '.': None, 'k': (40,10,10), 'R': (200,50,40), 'r': (160,35,30),
    'D': (130,25,20), 'O': (240,150,50), 'Y': (255,220,80),
    'w': (255,255,220), 'W': (220,60,50), 'e': (255,255,100),
}

DRAGON_SPRITE = [
    "..........kk............kk..........",
    ".........kRRk..........kRRk.........",
    "........kRRRRk........kRRRRk........",
    ".......kRRRRRRkkkkkkkRRRRRRk........",
    "......kRRRRRRRRRRRRRRRRRRRRRk.......",
    ".....kRRRewRRRRRRRRRRRewRRRRk.......",
    ".....kRRRRRRRRRRRRRRRRRRRRRRk......",
    "....kRRRRRRRRRRRRRRRRRRRRRRRRk.....",
    "...kDRRRRRRRRRRRRRRRRRRRRRRRDk.....",
    "..kDDRRRRRRRRRRRRRRRRRRRRRRDDk.....",
    "..kDDRRRRRRRRRRRRRRRRRRRRRRDDk.....",
    "..kDDDRRRRRRRRRRRRRRRRRRRRDDDk.....",
    "...kDDDRRRRRRRRRRRRRRRRRRDDDk......",
    "....kDDDRRRRRRRRRRRRRRRRDDDk.......",
    ".....kDDDDrrrrrrrrrrrDDDDk.........",
    "......kkDDDrrrrrrrrrDDDkk..........",
    ".......kkkkrrrrrrrrrkkkk...........",
    "...........krrk..krrk..............",
    "..........kRRRk.kRRRk..............",
    "..........kkkk...kkkk..............",
]

KNIGHT_PALETTE = {
    '.': None, 'k': (10,10,20), 'A': (50,40,70), 'a': (35,28,50),
    'S': (80,70,100), 'P': (120,50,180), 'p': (80,30,130),
    'w': (200,200,220), 'e': (220,40,40), 'W': (160,160,180),
}

KNIGHT_SPRITE = [
    "....kkkkkkk.....",
    "...kAAAAAAPk....",
    "..kAAAAAAAAPk...",
    "..kAAeAAAAeAk...",
    "..kAAAAAAAAAPk..",
    "..kAAAAkkAAAk...",
    "...kAAAAAAPk....",
    "...kkSSSSSkk....",
    "..kWkSSSSSkWk...",
    "..kWkSSSSSk.k...",
    "..kWkSSpSSk.....",
    "...kkSSSSSk.....",
    "....kSSSSk......",
    "....kAAkAAk.....",
    "...kAAk.kAAk....",
    "...kAAk.kAAk....",
    "..kAAk...kAAk...",
    "..kkkk...kkkk...",
]

def render_sprite_data(data, palette, scale=2):
    """Convert string-grid sprite data to a pygame Surface."""
    if not data:
        return pygame.Surface((16, 16), pygame.SRCALPHA)
    h = len(data)
    w = max(len(row) for row in data)
    surf = pygame.Surface((w, h), pygame.SRCALPHA)
    for y, row in enumerate(data):
        for x, ch in enumerate(row):
            color = palette.get(ch)
            if color:
                surf.set_at((x, y), color)
    if scale != 1:
        surf = pygame.transform.scale(surf, (w * scale, h * scale))
    return surf

class SpriteManager:
    """Manages all game sprites."""

    def __init__(self):
        self.char_sprites = {}  # {class: {direction: [frames]}}
        self.monster_sprites = {}
        self.tile_cache = {}

    def init(self):
        """Generate all sprites."""
        self._generate_characters()
        self._generate_monsters()

    def _generate_characters(self):
        """Generate character sprites for all classes."""
        classes = ['warrior', 'mage', 'healer']
        frames_data = {
            'down': [CHAR_DOWN_STAND, CHAR_DOWN_WALK1, CHAR_DOWN_STAND, CHAR_DOWN_WALK2],
            'up': [CHAR_UP_STAND, CHAR_UP_STAND, CHAR_UP_STAND, CHAR_UP_STAND],
            'left': [CHAR_LEFT_STAND, CHAR_LEFT_STAND, CHAR_LEFT_STAND, CHAR_LEFT_STAND],
        }
        for cls in classes:
            pal = PALETTES[cls]
            self.char_sprites[cls] = {}
            for direction, frames in frames_data.items():
                rendered = []
                for frame in frames:
                    rendered.append(render_sprite_data(frame, pal, scale=2))
                self.char_sprites[cls][direction] = rendered
            # Right = flip of left
            self.char_sprites[cls]['right'] = [
                pygame.transform.flip(f, True, False)
                for f in self.char_sprites[cls]['left']
            ]

    def _generate_monsters(self):
        """Generate monster battle sprites."""
        self.monster_sprites['slime'] = render_sprite_data(SLIME_SPRITE, SLIME_PALETTE, scale=3)
        self.monster_sprites['goblin'] = render_sprite_data(GOBLIN_SPRITE, GOBLIN_PALETTE, scale=3)
        self.monster_sprites['skeleton'] = render_sprite_data(SKELETON_SPRITE, SKELETON_PALETTE, scale=3)
        self.monster_sprites['knight'] = render_sprite_data(KNIGHT_SPRITE, KNIGHT_PALETTE, scale=3)
        self.monster_sprites['dragon'] = render_sprite_data(DRAGON_SPRITE, DRAGON_PALETTE, scale=3)

    def get_char_frame(self, char_class, direction, frame_index):
        """Get a character animation frame."""
        cls_data = self.char_sprites.get(char_class, self.char_sprites.get('warrior'))
        dir_frames = cls_data.get(direction, cls_data.get('down'))
        return dir_frames[frame_index % len(dir_frames)]

    def get_monster_sprite(self, sprite_type):
        """Get a monster sprite."""
        return self.monster_sprites.get(sprite_type, self.monster_sprites.get('slime'))

    def get_battle_char_sprite(self, char_class):
        """Get character sprite for battle (right-facing, scaled up)."""
        frame = self.get_char_frame(char_class, 'right', 0)
        return pygame.transform.scale(frame, (frame.get_width() * 2, frame.get_height() * 2))
