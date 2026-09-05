"""
Township - Procedural Sprites & Visual Asset Generator
Renders polished, high-resolution procedural surfaces for buildings,
crops, livestock, decorations, icons, characters, and match-3 gems.
"""

import math
import pygame
from config import TILE_SIZE

# Surface caching dictionary
_SPRITE_CACHE = {}

def get_surface(key: str, width: int, height: int) -> pygame.Surface:
    full_key = f"{key}_{width}_{height}"
    if full_key not in _SPRITE_CACHE:
        surf = pygame.Surface((width, height), pygame.SRCALPHA)
        _SPRITE_CACHE[full_key] = surf
    return _SPRITE_CACHE[full_key]

class SpriteManager:
    def __init__(self):
        if not pygame.font.get_init():
            pygame.font.init()
        self.tile_size = TILE_SIZE
        self.crops = {}
        self.buildings = {}
        self.decorations = {}
        self.roads = {}
        self.icons = {}
        self.characters = {}
        self.match3_gems = {}
        self._init_all()

    def _init_all(self):
        self._build_terrain_tiles()
        self._build_crop_sprites()
        self._build_building_sprites()
        self._build_decoration_sprites()
        self._build_icon_sprites()
        self._build_character_portraits()
        self._build_match3_sprites()

    # -------------------------------------------------------------
    # TERRAIN & PLOTS
    # -------------------------------------------------------------
    def _build_terrain_tiles(self):
        ts = self.tile_size

        # Grass Base
        grass = pygame.Surface((ts, ts))
        grass.fill((142, 204, 92))
        # Add slight texture speckles
        for x, y, r in [(6, 8, 3), (28, 14, 2), (18, 36, 3), (42, 40, 2), (36, 22, 2)]:
            pygame.draw.circle(grass, (155, 218, 102), (x, y), r)
            pygame.draw.circle(grass, (128, 188, 78), (x + 1, y + 1), 1)
        self.roads['grass'] = grass

        # Dirt Road
        dirt = pygame.Surface((ts, ts))
        dirt.fill((185, 145, 95))
        pygame.draw.rect(dirt, (168, 130, 80), (0, 0, ts, ts), 2)
        for x, y, r in [(10, 10, 2), (24, 30, 3), (38, 18, 2), (15, 42, 2)]:
            pygame.draw.circle(dirt, (160, 120, 72), (x, y), r)
        self.roads['road_dirt'] = dirt

        # Paved Road / Cobblestone
        paved = pygame.Surface((ts, ts))
        paved.fill((190, 184, 172))
        pygame.draw.rect(paved, (160, 154, 142), (0, 0, ts, ts), 1)
        half = ts // 2
        pygame.draw.line(paved, (160, 154, 142), (half, 0), (half, ts), 1)
        pygame.draw.line(paved, (160, 154, 142), (0, half), (ts, half), 1)
        pygame.draw.rect(paved, (210, 204, 192), (2, 2, half - 3, half - 3), border_radius=2)
        pygame.draw.rect(paved, (210, 204, 192), (half + 2, 2, half - 3, half - 3), border_radius=2)
        pygame.draw.rect(paved, (210, 204, 192), (2, half + 2, half - 3, half - 3), border_radius=2)
        pygame.draw.rect(paved, (210, 204, 192), (half + 2, half + 2, half - 3, half - 3), border_radius=2)
        self.roads['road_paved'] = paved

        # Water Canal
        water = pygame.Surface((ts, ts))
        water.fill((65, 168, 225))
        pygame.draw.rect(water, (45, 138, 195), (0, 0, ts, ts), 2)
        pygame.draw.arc(water, (110, 205, 245), (6, 12, 24, 10), 0, math.pi, 2)
        pygame.draw.arc(water, (110, 205, 245), (24, 28, 24, 10), 0, math.pi, 2)
        self.roads['water_canal'] = water

        # Field Plot (Empty Soil)
        plot = pygame.Surface((ts, ts), pygame.SRCALPHA)
        pygame.draw.rect(plot, (135, 92, 54), (2, 2, ts - 4, ts - 4), border_radius=4)
        pygame.draw.rect(plot, (115, 75, 40), (2, 2, ts - 4, ts - 4), 2, border_radius=4)
        # Plow furrows
        for y in range(10, ts - 8, 8):
            pygame.draw.line(plot, (110, 72, 38), (6, y), (ts - 6, y), 2)
            pygame.draw.line(plot, (155, 108, 65), (6, y + 2), (ts - 6, y + 2), 1)
        self.roads['field_plot'] = plot

    # -------------------------------------------------------------
    # CROPS (Growth Stages 0, 1, 2)
    # -------------------------------------------------------------
    def _build_crop_sprites(self):
        ts = self.tile_size
        crop_names = ['wheat', 'corn', 'carrot', 'sugarcane', 'cotton', 'strawberry']

        for crop in crop_names:
            stages = []
            # Stage 0: Sprout (Small green seedling)
            s0 = pygame.Surface((ts, ts), pygame.SRCALPHA)
            pygame.draw.circle(s0, (90, 175, 45), (ts // 2 - 6, ts // 2 + 4), 4)
            pygame.draw.circle(s0, (90, 175, 45), (ts // 2 + 6, ts // 2 + 4), 4)
            pygame.draw.line(s0, (65, 135, 30), (ts // 2, ts // 2 + 12), (ts // 2, ts // 2), 3)
            stages.append(s0)

            # Stage 1: Half-Grown Bush/Stems
            s1 = pygame.Surface((ts, ts), pygame.SRCALPHA)
            pygame.draw.circle(s1, (100, 190, 50), (ts // 2 - 8, ts // 2), 7)
            pygame.draw.circle(s1, (110, 205, 55), (ts // 2 + 8, ts // 2), 7)
            pygame.draw.circle(s1, (120, 215, 60), (ts // 2, ts // 2 - 6), 8)
            pygame.draw.line(s1, (70, 145, 35), (ts // 2, ts // 2 + 12), (ts // 2, ts // 2), 4)
            stages.append(s1)

            # Stage 2: Mature, Ready to harvest!
            s2 = pygame.Surface((ts, ts), pygame.SRCALPHA)
            cx, cy = ts // 2, ts // 2

            if crop == 'wheat':
                for offset in [-10, 0, 10]:
                    pygame.draw.line(s2, (190, 150, 40), (cx + offset, cy + 16), (cx + offset, cy - 8), 3)
                    # Grain heads
                    pygame.draw.ellipse(s2, (245, 210, 65), (cx + offset - 5, cy - 14, 10, 16))
                    pygame.draw.ellipse(s2, (220, 175, 40), (cx + offset - 4, cy - 12, 8, 12), 1)

            elif crop == 'corn':
                pygame.draw.rect(s2, (80, 160, 45), (cx - 14, cy - 8, 28, 24), border_radius=6)
                for offset in [-6, 6]:
                    pygame.draw.ellipse(s2, (250, 200, 30), (cx + offset - 5, cy - 14, 10, 18))
                    pygame.draw.line(s2, (215, 145, 20), (cx + offset, cy - 14), (cx + offset, cy - 18), 2)

            elif crop == 'carrot':
                pygame.draw.circle(s2, (65, 155, 40), (cx - 8, cy - 6), 8)
                pygame.draw.circle(s2, (75, 175, 45), (cx + 8, cy - 6), 8)
                pygame.draw.polygon(s2, (250, 115, 25), [(cx - 8, cy - 2), (cx + 8, cy - 2), (cx, cy + 16)])
                pygame.draw.polygon(s2, (220, 90, 15), [(cx - 8, cy - 2), (cx + 8, cy - 2), (cx, cy + 16)], 1)

            elif crop == 'sugarcane':
                for offset in [-9, 0, 9]:
                    pygame.draw.rect(s2, (120, 185, 65), (cx + offset - 3, cy - 16, 6, 32), border_radius=2)
                    pygame.draw.line(s2, (75, 130, 40), (cx + offset - 3, cy - 6), (cx + offset + 3, cy - 6), 2)
                    pygame.draw.line(s2, (75, 130, 40), (cx + offset - 3, cy + 6), (cx + offset + 3, cy + 6), 2)

            elif crop == 'cotton':
                pygame.draw.rect(s2, (70, 140, 50), (cx - 12, cy, 24, 16), border_radius=4)
                for pos in [(cx - 7, cy - 6), (cx + 7, cy - 6), (cx, cy - 12)]:
                    pygame.draw.circle(s2, (245, 245, 250), pos, 7)
                    pygame.draw.circle(s2, (215, 220, 230), pos, 7, 1)

            elif crop == 'strawberry':
                pygame.draw.circle(s2, (60, 150, 45), (cx, cy - 4), 12)
                for offset in [-7, 7]:
                    bx = cx + offset
                    pygame.draw.polygon(s2, (235, 45, 65), [(bx - 6, cy), (bx + 6, cy), (bx, cy + 12)])
                    # strawberry seeds
                    pygame.draw.circle(s2, (255, 225, 90), (bx - 2, cy + 4), 1)
                    pygame.draw.circle(s2, (255, 225, 90), (bx + 2, cy + 4), 1)

            stages.append(s2)
            self.crops[crop] = stages

    # -------------------------------------------------------------
    # BUILDINGS, FACTORIES & SHEDS
    # -------------------------------------------------------------
    def _build_building_sprites(self):
        ts = self.tile_size

        # 1. Cottage (2x2)
        w, h = 2 * ts, 2 * ts
        surf = pygame.Surface((w, h), pygame.SRCALPHA)
        # Shadow
        pygame.draw.ellipse(surf, (0, 0, 0, 40), (6, h - 22, w - 12, 20))
        # Walls
        pygame.draw.rect(surf, (245, 235, 215), (12, 38, w - 24, h - 50), border_radius=4)
        pygame.draw.rect(surf, (195, 175, 150), (12, 38, w - 24, h - 50), 2, border_radius=4)
        # Roof (Warm red/orange terracotta)
        pygame.draw.polygon(surf, (215, 75, 55), [(w // 2, 8), (w - 6, 44), (6, 44)])
        pygame.draw.polygon(surf, (175, 55, 40), [(w // 2, 8), (w - 6, 44), (6, 44)], 2)
        # Chimney with smoke
        pygame.draw.rect(surf, (170, 75, 50), (w - 28, 14, 10, 18))
        pygame.draw.circle(surf, (230, 230, 235, 160), (w - 23, 8), 5)
        pygame.draw.circle(surf, (235, 235, 240, 120), (w - 20, 2), 6)
        # Door & Windows
        pygame.draw.rect(surf, (135, 80, 45), (w // 2 - 8, h - 38, 16, 26), border_radius=3)
        pygame.draw.circle(surf, (245, 200, 50), (w // 2 + 4, h - 24), 2)
        pygame.draw.rect(surf, (120, 180, 235), (20, 48, 14, 16), border_radius=2)
        pygame.draw.rect(surf, (120, 180, 235), (w - 34, 48, 14, 16), border_radius=2)
        self.buildings['cottage'] = surf

        # 2. Townhouse (2x2)
        surf = pygame.Surface((w, h), pygame.SRCALPHA)
        pygame.draw.ellipse(surf, (0, 0, 0, 40), (6, h - 20, w - 12, 18))
        # 2-story blue/cream building
        pygame.draw.rect(surf, (235, 215, 180), (10, 26, w - 20, h - 38), border_radius=4)
        pygame.draw.rect(surf, (185, 160, 125), (10, 26, w - 20, h - 38), 2, border_radius=4)
        # Blue mansard roof
        pygame.draw.polygon(surf, (55, 125, 185), [(w // 2, 6), (w - 6, 28), (6, 28)])
        pygame.draw.polygon(surf, (35, 95, 150), [(w // 2, 6), (w - 6, 28), (6, 28)], 2)
        # Windows on 2 floors
        for wy in [36, 62]:
            pygame.draw.rect(surf, (135, 200, 245), (20, wy, 16, 16), border_radius=2)
            pygame.draw.rect(surf, (135, 200, 245), (w - 36, wy, 16, 16), border_radius=2)
        # Wooden double door
        pygame.draw.rect(surf, (125, 75, 40), (w // 2 - 10, h - 34, 20, 22), border_radius=2)
        self.buildings['townhouse'] = surf

        # 3. Apartment Block (3x2)
        w3, h2 = 3 * ts, 2 * ts
        surf = pygame.Surface((w3, h2), pygame.SRCALPHA)
        pygame.draw.ellipse(surf, (0, 0, 0, 45), (10, h2 - 20, w3 - 20, 18))
        # Modern brick structure
        pygame.draw.rect(surf, (215, 140, 115), (14, 18, w3 - 28, h2 - 28), border_radius=4)
        pygame.draw.rect(surf, (175, 105, 80), (14, 18, w3 - 28, h2 - 28), 2, border_radius=4)
        # Roof ledge
        pygame.draw.rect(surf, (160, 95, 70), (10, 14, w3 - 20, 8), border_radius=2)
        # Grid of windows
        for wx in range(24, w3 - 36, 24):
            for wy in [30, 56]:
                pygame.draw.rect(surf, (245, 245, 210), (wx, wy, 14, 16), border_radius=2)
                pygame.draw.rect(surf, (150, 90, 65), (wx, wy, 14, 16), 1, border_radius=2)
        # Central entrance
        pygame.draw.rect(surf, (80, 130, 175), (w3 // 2 - 12, h2 - 30, 24, 20), border_radius=2)
        self.buildings['apartment'] = surf

        # 4. Modern Condo (3x3)
        w3, h3 = 3 * ts, 3 * ts
        surf = pygame.Surface((w3, h3), pygame.SRCALPHA)
        pygame.draw.ellipse(surf, (0, 0, 0, 45), (12, h3 - 22, w3 - 24, 20))
        # Glass tower
        pygame.draw.rect(surf, (225, 235, 245), (20, 20, w3 - 40, h3 - 34), border_radius=6)
        pygame.draw.rect(surf, (140, 170, 200), (20, 20, w3 - 40, h3 - 34), 2, border_radius=6)
        # Glass panels
        for wy in range(32, h3 - 40, 20):
            pygame.draw.rect(surf, (100, 180, 230), (26, wy, w3 - 52, 14), border_radius=2)
        # Penthouse garden on top
        pygame.draw.rect(surf, (95, 175, 65), (28, 12, w3 - 56, 10), border_radius=3)
        self.buildings['modern_condo'] = surf

        # 5. Town Hall (3x3)
        surf = pygame.Surface((w3, h3), pygame.SRCALPHA)
        pygame.draw.ellipse(surf, (0, 0, 0, 50), (8, h3 - 24, w3 - 16, 22))
        # Grand neoclassical base
        pygame.draw.rect(surf, (245, 240, 230), (16, 48, w3 - 32, h3 - 62), border_radius=4)
        pygame.draw.rect(surf, (190, 180, 165), (16, 48, w3 - 32, h3 - 62), 2, border_radius=4)
        # Pediment triangle
        pygame.draw.polygon(surf, (230, 220, 205), [(w3 // 2, 28), (w3 - 14, 52), (14, 52)])
        pygame.draw.polygon(surf, (180, 170, 155), [(w3 // 2, 28), (w3 - 14, 52), (14, 52)], 2)
        # Clock tower & Golden Dome
        pygame.draw.rect(surf, (240, 235, 225), (w3 // 2 - 16, 12, 32, 20))
        pygame.draw.arc(surf, (245, 195, 45), (w3 // 2 - 14, 0, 28, 22), 0, math.pi, 14)
        pygame.draw.circle(surf, (245, 195, 45), (w3 // 2, 2), 4)
        # Clock
        pygame.draw.circle(surf, (255, 255, 255), (w3 // 2, 22), 7)
        pygame.draw.circle(surf, (60, 45, 35), (w3 // 2, 22), 7, 1)
        pygame.draw.line(surf, (60, 45, 35), (w3 // 2, 22), (w3 // 2, 18), 2)
        pygame.draw.line(surf, (60, 45, 35), (w3 // 2, 22), (w3 // 2 + 3, 22), 2)
        # Pillars
        for px in [30, 52, 74, 96, 118]:
            if px < w3 - 30:
                pygame.draw.line(surf, (215, 205, 190), (px, 52), (px, h3 - 16), 5)
        self.buildings['town_hall'] = surf

        # 6. School (3x2)
        surf = pygame.Surface((w3, h2), pygame.SRCALPHA)
        pygame.draw.ellipse(surf, (0, 0, 0, 40), (10, h2 - 20, w3 - 20, 18))
        pygame.draw.rect(surf, (205, 85, 75), (14, 26, w3 - 28, h2 - 36), border_radius=4)
        pygame.draw.rect(surf, (160, 60, 50), (14, 26, w3 - 28, h2 - 36), 2, border_radius=4)
        # Bell belfry
        pygame.draw.rect(surf, (240, 235, 225), (w3 // 2 - 10, 8, 20, 20), border_radius=2)
        pygame.draw.circle(surf, (245, 195, 45), (w3 // 2, 18), 5) # Bell
        # Windows & door
        for wx in [26, 48, w3 - 44, w3 - 66]:
            pygame.draw.rect(surf, (240, 245, 255), (wx, 40, 14, 18), border_radius=2)
        pygame.draw.rect(surf, (115, 70, 40), (w3 // 2 - 12, h2 - 30, 24, 20), border_radius=2)
        self.buildings['school'] = surf

        # 7. Fire Station (3x2)
        surf = pygame.Surface((w3, h2), pygame.SRCALPHA)
        pygame.draw.ellipse(surf, (0, 0, 0, 40), (10, h2 - 20, w3 - 20, 18))
        pygame.draw.rect(surf, (225, 60, 55), (14, 22, w3 - 28, h2 - 32), border_radius=4)
        # Siren on top
        pygame.draw.circle(surf, (255, 220, 40), (w3 // 2, 14), 6)
        # Garage Bay Door
        pygame.draw.rect(surf, (245, 245, 245), (24, 42, 48, 38), border_radius=2)
        for gy in range(48, 76, 8):
            pygame.draw.line(surf, (200, 200, 205), (24, gy), (72, gy), 2)
        # Office section
        pygame.draw.rect(surf, (120, 195, 245), (88, 36, 26, 18), border_radius=2)
        self.buildings['fire_station'] = surf

        # 8. Hospital (3x3)
        surf = pygame.Surface((w3, h3), pygame.SRCALPHA)
        pygame.draw.ellipse(surf, (0, 0, 0, 45), (12, h3 - 22, w3 - 24, 20))
        pygame.draw.rect(surf, (248, 250, 252), (18, 24, w3 - 36, h3 - 38), border_radius=6)
        pygame.draw.rect(surf, (190, 205, 220), (18, 24, w3 - 36, h3 - 38), 2, border_radius=6)
        # Red Cross emblem
        pygame.draw.circle(surf, (255, 255, 255), (w3 // 2, 48), 16)
        pygame.draw.circle(surf, (225, 60, 55), (w3 // 2, 48), 16, 2)
        pygame.draw.rect(surf, (225, 60, 55), (w3 // 2 - 4, 38, 8, 20), border_radius=1)
        pygame.draw.rect(surf, (225, 60, 55), (w3 // 2 - 10, 44, 20, 8), border_radius=1)
        # Emergency entrance
        pygame.draw.rect(surf, (100, 175, 230), (w3 // 2 - 20, h3 - 36, 40, 22), border_radius=3)
        self.buildings['hospital'] = surf

        # 9. Cinema (3x2)
        surf = pygame.Surface((w3, h2), pygame.SRCALPHA)
        pygame.draw.ellipse(surf, (0, 0, 0, 45), (10, h2 - 20, w3 - 20, 18))
        pygame.draw.rect(surf, (120, 45, 110), (14, 22, w3 - 28, h2 - 32), border_radius=4)
        # Marquee sign
        pygame.draw.rect(surf, (245, 195, 45), (20, 12, w3 - 40, 18), border_radius=3)
        # Little marquee bulbs
        for mx in range(24, w3 - 24, 10):
            pygame.draw.circle(surf, (255, 255, 220), (mx, 15), 2)
        # Doors & Posters
        pygame.draw.rect(surf, (245, 215, 80), (24, 42, 16, 24), border_radius=2)
        pygame.draw.rect(surf, (75, 180, 240), (w3 - 40, 42, 16, 24), border_radius=2)
        pygame.draw.rect(surf, (215, 60, 55), (w3 // 2 - 14, h2 - 32, 28, 22), border_radius=2)
        self.buildings['cinema'] = surf

        # -------------------------------------------------------------
        # FACTORIES
        # -------------------------------------------------------------
        # Feed Mill (2x2)
        surf = pygame.Surface((w, h), pygame.SRCALPHA)
        pygame.draw.ellipse(surf, (0, 0, 0, 40), (6, h - 20, w - 12, 18))
        # Silo & Hopper
        pygame.draw.rect(surf, (215, 195, 160), (14, 20, 36, h - 30), border_radius=4)
        pygame.draw.ellipse(surf, (185, 165, 130), (14, 12, 36, 16))
        # Mill building
        pygame.draw.rect(surf, (190, 85, 60), (48, 32, w - 60, h - 42), border_radius=3)
        # Windmill vanes
        cx, cy = w - 30, 42
        for angle in [0, 90, 180, 270]:
            rad = math.radians(angle)
            dx = int(math.cos(rad) * 16)
            dy = int(math.sin(rad) * 16)
            pygame.draw.line(surf, (245, 245, 245), (cx, cy), (cx + dx, cy + dy), 3)
        pygame.draw.circle(surf, (90, 60, 40), (cx, cy), 4)
        self.buildings['feed_mill'] = surf

        # Bakery (3x2)
        surf = pygame.Surface((w3, h2), pygame.SRCALPHA)
        pygame.draw.ellipse(surf, (0, 0, 0, 45), (10, h2 - 20, w3 - 20, 18))
        pygame.draw.rect(surf, (245, 230, 205), (14, 24, w3 - 28, h2 - 34), border_radius=4)
        # Brick oven texture
        pygame.draw.polygon(surf, (205, 95, 60), [(w3 // 2, 8), (w3 - 10, 28), (10, 28)])
        # Chimney with bakery smoke
        pygame.draw.rect(surf, (180, 80, 50), (w3 - 34, 12, 12, 20))
        pygame.draw.circle(surf, (240, 240, 245, 180), (w3 - 28, 4), 6)
        # Bread sign on wall
        pygame.draw.circle(surf, (240, 180, 60), (36, 44), 10)
        # Display window with pastries
        pygame.draw.rect(surf, (140, 205, 250), (w3 // 2 - 20, 40, 40, 22), border_radius=2)
        self.buildings['bakery'] = surf

        # Dairy Factory (3x2)
        surf = pygame.Surface((w3, h2), pygame.SRCALPHA)
        pygame.draw.ellipse(surf, (0, 0, 0, 45), (10, h2 - 20, w3 - 20, 18))
        # Clean white factory with stainless steel silos
        pygame.draw.rect(surf, (240, 245, 250), (14, 24, w3 - 28, h2 - 34), border_radius=4)
        # Silo 1 & 2
        for sx in [20, 46]:
            pygame.draw.rect(surf, (210, 225, 235), (sx, 12, 20, 46), border_radius=3)
            pygame.draw.ellipse(surf, (180, 200, 215), (sx, 6, 20, 12))
        # Blue roof trim
        pygame.draw.rect(surf, (55, 135, 205), (74, 22, w3 - 86, 8), border_radius=2)
        # Milk bottle icon on front
        pygame.draw.rect(surf, (255, 255, 255), (w3 - 38, 42, 12, 18), border_radius=2)
        pygame.draw.circle(surf, (70, 160, 235), (w3 - 32, 48), 3)
        self.buildings['dairy_factory'] = surf

        # Sugar Mill (3x2)
        surf = pygame.Surface((w3, h2), pygame.SRCALPHA)
        pygame.draw.ellipse(surf, (0, 0, 0, 45), (10, h2 - 20, w3 - 20, 18))
        pygame.draw.rect(surf, (230, 215, 195), (14, 26, w3 - 28, h2 - 36), border_radius=4)
        # Copper/brass vat
        pygame.draw.ellipse(surf, (215, 140, 60), (22, 16, 38, 30))
        # Sugar crystals chute
        pygame.draw.polygon(surf, (250, 250, 255), [(w3 - 40, 36), (w3 - 18, 36), (w3 - 26, 62), (w3 - 32, 62)])
        self.buildings['sugar_mill'] = surf

        # Textile Factory (3x3)
        surf = pygame.Surface((w3, h3), pygame.SRCALPHA)
        pygame.draw.ellipse(surf, (0, 0, 0, 50), (12, h3 - 22, w3 - 24, 20))
        pygame.draw.rect(surf, (195, 165, 140), (16, 28, w3 - 32, h3 - 42), border_radius=4)
        # Sawtooth industrial factory roof
        for rx in range(16, w3 - 32, 32):
            pygame.draw.polygon(surf, (140, 75, 60), [(rx, 28), (rx + 16, 12), (rx + 32, 28)])
        # Big spinning gear/wheel
        pygame.draw.circle(surf, (160, 165, 175), (w3 // 2, 60), 16)
        pygame.draw.circle(surf, (120, 125, 135), (w3 // 2, 60), 16, 3)
        self.buildings['textile_factory'] = surf

        # -------------------------------------------------------------
        # ANIMAL SHEDS
        # -------------------------------------------------------------
        # Cow Shed (3x2)
        surf = pygame.Surface((w3, h2), pygame.SRCALPHA)
        pygame.draw.ellipse(surf, (0, 0, 0, 45), (10, h2 - 20, w3 - 20, 18))
        # Red barn style shed
        pygame.draw.rect(surf, (210, 70, 60), (12, 16, w3 - 24, h2 - 26), border_radius=4)
        # Barn roof
        pygame.draw.polygon(surf, (245, 240, 235), [(w3 // 2, 4), (w3 - 8, 20), (8, 20)])
        # Straw bedding
        pygame.draw.rect(surf, (240, 210, 95), (16, 44, w3 - 32, h2 - 52), border_radius=3)
        # 3 Cute animated cows
        for cx in [32, 74, 116]:
            self._draw_cow(surf, cx, 54)
        self.buildings['cow_shed'] = surf

        # Chicken Coop (3x2)
        surf = pygame.Surface((w3, h2), pygame.SRCALPHA)
        pygame.draw.ellipse(surf, (0, 0, 0, 45), (10, h2 - 20, w3 - 20, 18))
        # Wooden coop
        pygame.draw.rect(surf, (190, 135, 75), (14, 18, w3 - 28, h2 - 28), border_radius=4)
        # Nests
        for cx in [30, 60, 90, 120]:
            pygame.draw.ellipse(surf, (230, 195, 90), (cx - 10, 52, 20, 14))
            self._draw_chicken(surf, cx, 48)
        self.buildings['chicken_coop'] = surf

        # Sheep Pen (3x2)
        surf = pygame.Surface((w3, h2), pygame.SRCALPHA)
        pygame.draw.ellipse(surf, (0, 0, 0, 45), (10, h2 - 20, w3 - 20, 18))
        # Fenced green pasture
        pygame.draw.rect(surf, (150, 210, 90), (14, 20, w3 - 28, h2 - 30), border_radius=4)
        # Fence rails
        for fx in range(14, w3 - 14, 16):
            pygame.draw.line(surf, (140, 90, 50), (fx, 22), (fx, 36), 3)
        pygame.draw.line(surf, (160, 105, 60), (14, 26), (w3 - 14, 26), 2)
        pygame.draw.line(surf, (160, 105, 60), (14, 32), (w3 - 14, 32), 2)
        # 3 Fluffy sheep
        for sx in [36, 76, 116]:
            self._draw_sheep(surf, sx, 52)
        self.buildings['sheep_pen'] = surf

        # Pig Pen (3x2)
        surf = pygame.Surface((w3, h2), pygame.SRCALPHA)
        pygame.draw.ellipse(surf, (0, 0, 0, 45), (10, h2 - 20, w3 - 20, 18))
        pygame.draw.rect(surf, (180, 140, 95), (14, 20, w3 - 28, h2 - 30), border_radius=4)
        # Mud patch
        pygame.draw.ellipse(surf, (135, 95, 60), (30, 44, 100, 36))
        # Fence rails
        for fx in range(14, w3 - 14, 16):
            pygame.draw.line(surf, (130, 85, 45), (fx, 22), (fx, 36), 3)
        pygame.draw.line(surf, (150, 95, 55), (14, 26), (w3 - 14, 26), 2)
        pygame.draw.line(surf, (150, 95, 55), (14, 32), (w3 - 14, 32), 2)
        # 3 Cute pigs
        for px in [38, 78, 118]:
            self._draw_pig(surf, px, 54)
        self.buildings['pig_pen'] = surf

        # -------------------------------------------------------------
        # HELIPAD & HELICOPTER (3x3)
        # -------------------------------------------------------------
        surf = pygame.Surface((w3, h3), pygame.SRCALPHA)
        # Concrete pad
        pygame.draw.rect(surf, (175, 170, 162), (10, 10, w3 - 20, h3 - 20), border_radius=8)
        pygame.draw.rect(surf, (140, 135, 128), (10, 10, w3 - 20, h3 - 20), 3, border_radius=8)
        # Yellow circle & H
        cx, cy = w3 // 2, h3 // 2
        pygame.draw.circle(surf, (245, 205, 45), (cx, cy), 42, 5)
        # Big "H"
        pygame.draw.line(surf, (245, 205, 45), (cx - 18, cy - 24), (cx - 18, cy + 24), 8)
        pygame.draw.line(surf, (245, 205, 45), (cx + 18, cy - 24), (cx + 18, cy + 24), 8)
        pygame.draw.line(surf, (245, 205, 45), (cx - 18, cy), (cx + 18, cy), 8)
        self.buildings['helipad'] = surf

        # Township Helicopter (Vibrant Orange & Yellow)
        heli = pygame.Surface((84, 60), pygame.SRCALPHA)
        hcx, hcy = 42, 32
        # Skids
        pygame.draw.line(heli, (80, 80, 90), (hcx - 22, hcy + 18), (hcx + 22, hcy + 18), 3)
        pygame.draw.line(heli, (80, 80, 90), (hcx - 12, hcy + 12), (hcx - 14, hcy + 18), 2)
        pygame.draw.line(heli, (80, 80, 90), (hcx + 12, hcy + 12), (hcx + 14, hcy + 18), 2)
        # Body
        pygame.draw.ellipse(heli, (245, 140, 35), (hcx - 24, hcy - 12, 48, 26))
        pygame.draw.ellipse(heli, (255, 175, 55), (hcx - 20, hcy - 10, 40, 20))
        # Cockpit windshield
        pygame.draw.ellipse(heli, (135, 215, 255), (hcx + 4, hcy - 8, 16, 18))
        # Tail boom & fin
        pygame.draw.rect(heli, (245, 140, 35), (hcx - 38, hcy - 4, 18, 6), border_radius=2)
        pygame.draw.polygon(heli, (225, 60, 55), [(hcx - 38, hcy - 12), (hcx - 34, hcy + 4), (hcx - 42, hcy + 4)])
        # Rotor mast & blades
        pygame.draw.rect(heli, (90, 90, 95), (hcx - 2, hcy - 18, 4, 8))
        pygame.draw.line(heli, (60, 60, 65), (hcx - 36, hcy - 18), (hcx + 36, hcy - 18), 3)
        self.buildings['helicopter'] = heli

    def _draw_cow(self, surf, x, y):
        # Body (white with black spots)
        pygame.draw.ellipse(surf, (250, 250, 250), (x - 12, y - 8, 24, 16))
        pygame.draw.circle(surf, (40, 40, 45), (x - 4, y - 2), 4)
        pygame.draw.circle(surf, (40, 40, 45), (x + 5, y + 2), 3)
        # Head & cute pink muzzle
        pygame.draw.circle(surf, (250, 250, 250), (x + 10, y - 6), 6)
        pygame.draw.circle(surf, (255, 190, 195), (x + 12, y - 4), 4)
        # Horns
        pygame.draw.circle(surf, (240, 205, 120), (x + 8, y - 11), 2)
        pygame.draw.circle(surf, (240, 205, 120), (x + 12, y - 11), 2)

    def _draw_chicken(self, surf, x, y):
        # Round body
        pygame.draw.circle(surf, (255, 250, 240), (x, y), 7)
        # Red comb & beak
        pygame.draw.polygon(surf, (235, 55, 50), [(x - 2, y - 9), (x + 2, y - 9), (x, y - 6)])
        pygame.draw.polygon(surf, (245, 175, 35), [(x + 5, y - 2), (x + 9, y), (x + 5, y + 2)])
        # Eye
        pygame.draw.circle(surf, (30, 30, 35), (x + 3, y - 2), 1)

    def _draw_sheep(self, surf, x, y):
        # Fluffy white body
        for ox, oy in [(-6, 0), (6, 0), (0, -4), (0, 3)]:
            pygame.draw.circle(surf, (250, 250, 255), (x + ox, y + oy), 7)
        # Black face
        pygame.draw.ellipse(surf, (50, 50, 55), (x + 7, y - 5, 8, 10))
        # Ears
        pygame.draw.circle(surf, (50, 50, 55), (x + 6, y - 6), 2)

    def _draw_pig(self, surf, x, y):
        # Cute pink body
        pygame.draw.ellipse(surf, (255, 185, 195), (x - 12, y - 8, 24, 16))
        pygame.draw.circle(surf, (255, 175, 185), (x + 8, y - 4), 7)
        # Snout
        pygame.draw.ellipse(surf, (255, 150, 165), (x + 11, y - 4, 7, 5))
        pygame.draw.circle(surf, (90, 45, 55), (x + 13, y - 4), 1)
        pygame.draw.circle(surf, (90, 45, 55), (x + 15, y - 4), 1)
        # Ears & curly tail
        pygame.draw.polygon(surf, (245, 145, 160), [(x + 6, y - 9), (x + 10, y - 13), (x + 11, y - 8)])
        pygame.draw.arc(surf, (255, 165, 175), (x - 16, y - 6, 8, 8), 0, math.pi * 1.5, 2)

    # -------------------------------------------------------------
    # DECORATIONS
    # -------------------------------------------------------------
    def _build_decoration_sprites(self):
        ts = self.tile_size

        # Oak Tree (1x1)
        tree = pygame.Surface((ts, ts), pygame.SRCALPHA)
        pygame.draw.ellipse(tree, (0, 0, 0, 35), (10, ts - 12, ts - 20, 10))
        pygame.draw.rect(tree, (120, 80, 45), (ts // 2 - 4, ts - 24, 8, 16), border_radius=2)
        # Leafy crown
        for ox, oy, r in [(-8, -12, 14), (8, -12, 14), (0, -20, 16), (0, -6, 12)]:
            pygame.draw.circle(tree, (85, 175, 55), (ts // 2 + ox, ts // 2 + oy), r)
            pygame.draw.circle(tree, (105, 195, 75), (ts // 2 + ox - 2, ts // 2 + oy - 2), r - 3)
        self.decorations['park_tree'] = tree

        # Pine Tree (1x1)
        pine = pygame.Surface((ts, ts), pygame.SRCALPHA)
        pygame.draw.ellipse(pine, (0, 0, 0, 35), (12, ts - 10, ts - 24, 8))
        pygame.draw.rect(pine, (110, 75, 40), (ts // 2 - 3, ts - 18, 6, 12))
        cx = ts // 2
        # 3 Green tiers
        pygame.draw.polygon(pine, (45, 125, 60), [(cx, ts - 38), (cx + 16, ts - 18), (cx - 16, ts - 18)])
        pygame.draw.polygon(pine, (55, 145, 70), [(cx, ts - 46), (cx + 13, ts - 28), (cx - 13, ts - 28)])
        pygame.draw.polygon(pine, (65, 165, 80), [(cx, ts - 52), (cx + 10, ts - 38), (cx - 10, ts - 38)])
        self.decorations['pine_tree'] = pine

        # Flower Bed (1x1)
        bed = pygame.Surface((ts, ts), pygame.SRCALPHA)
        pygame.draw.rect(bed, (130, 90, 55), (4, 4, ts - 8, ts - 8), border_radius=4)
        pygame.draw.rect(bed, (160, 115, 75), (4, 4, ts - 8, ts - 8), 2, border_radius=4)
        # Bright blossoms
        colors = [(245, 65, 85), (250, 205, 45), (145, 75, 215), (245, 135, 45)]
        coords = [(14, 14), (34, 14), (14, 34), (34, 34), (24, 24)]
        for i, (fx, fy) in enumerate(coords):
            c = colors[i % len(colors)]
            pygame.draw.circle(bed, c, (fx, fy), 5)
            pygame.draw.circle(bed, (255, 255, 255), (fx, fy), 2)
        self.decorations['flower_bed'] = bed

        # Town Fountain (2x2)
        w, h = 2 * ts, 2 * ts
        fnt = pygame.Surface((w, h), pygame.SRCALPHA)
        pygame.draw.ellipse(fnt, (0, 0, 0, 40), (8, h - 22, w - 16, 20))
        # Stone basin
        pygame.draw.circle(fnt, (185, 180, 172), (w // 2, h // 2), 36)
        pygame.draw.circle(fnt, (155, 150, 142), (w // 2, h // 2), 36, 4)
        # Sparkling water inside basin
        pygame.draw.circle(fnt, (75, 180, 235), (w // 2, h // 2), 31)
        # Pedestal & jet
        pygame.draw.circle(fnt, (215, 210, 202), (w // 2, h // 2), 12)
        pygame.draw.circle(fnt, (235, 245, 255), (w // 2, h // 2 - 4), 6)
        pygame.draw.line(fnt, (255, 255, 255), (w // 2, h // 2 - 4), (w // 2, h // 2 - 16), 3)
        self.decorations['fountain'] = fnt

        # Street Lamp (1x1)
        lamp = pygame.Surface((ts, ts), pygame.SRCALPHA)
        pygame.draw.ellipse(lamp, (0, 0, 0, 30), (ts // 2 - 8, ts - 8, 16, 6))
        pygame.draw.line(lamp, (50, 50, 55), (ts // 2, ts - 8), (ts // 2, 14), 3)
        pygame.draw.circle(lamp, (255, 240, 120, 160), (ts // 2, 14), 10)
        pygame.draw.circle(lamp, (255, 225, 80), (ts // 2, 14), 5)
        self.decorations['street_lamp'] = lamp

        # Gazebo (2x2)
        gaz = pygame.Surface((w, h), pygame.SRCALPHA)
        pygame.draw.ellipse(gaz, (0, 0, 0, 40), (8, h - 22, w - 16, 20))
        pygame.draw.circle(gaz, (245, 240, 230), (w // 2, h // 2), 34)
        # Roof cone
        pygame.draw.polygon(gaz, (190, 85, 75), [(w // 2, 8), (w - 12, h // 2 + 10), (12, h // 2 + 10)])
        pygame.draw.polygon(gaz, (150, 65, 55), [(w // 2, 8), (w - 12, h // 2 + 10), (12, h // 2 + 10)], 2)
        self.decorations['gazebo'] = gaz

    # -------------------------------------------------------------
    # ICONS & ITEM SPRITES
    # -------------------------------------------------------------
    def _build_icon_sprites(self):
        # 1. Coin (32x32)
        coin = pygame.Surface((32, 32), pygame.SRCALPHA)
        pygame.draw.circle(coin, (230, 165, 20), (16, 16), 14)
        pygame.draw.circle(coin, (255, 215, 50), (16, 16), 12)
        # Star on coin
        self._draw_star(coin, 16, 16, 6, 3, (220, 150, 15))
        self.icons['coin'] = coin

        # 2. Township Cash / T-Cash (32x24)
        tcash = pygame.Surface((32, 24), pygame.SRCALPHA)
        pygame.draw.rect(tcash, (65, 165, 85), (2, 2, 28, 20), border_radius=3)
        pygame.draw.rect(tcash, (85, 195, 105), (4, 4, 24, 16), border_radius=2)
        # "T$" symbol
        font = pygame.font.SysFont('Arial', 11, bold=True)
        t_text = font.render('T$', True, (255, 255, 255))
        tcash.blit(t_text, (tcash.get_width() // 2 - t_text.get_width() // 2, 4))
        self.icons['tcash'] = tcash

        # 3. XP Star (32x32)
        star = pygame.Surface((32, 32), pygame.SRCALPHA)
        self._draw_star(star, 16, 16, 14, 7, (245, 190, 30))
        self._draw_star(star, 16, 16, 10, 5, (255, 230, 85))
        self.icons['xp'] = star

        # 4. Barn Icon (32x32)
        barn = pygame.Surface((32, 32), pygame.SRCALPHA)
        pygame.draw.rect(barn, (215, 60, 55), (4, 12, 24, 16), border_radius=2)
        pygame.draw.polygon(barn, (245, 240, 235), [(16, 3), (28, 13), (4, 13)])
        # Barn X door
        pygame.draw.rect(barn, (245, 240, 235), (10, 18, 12, 10))
        pygame.draw.line(barn, (215, 60, 55), (10, 18), (22, 28), 2)
        pygame.draw.line(barn, (215, 60, 55), (22, 18), (10, 28), 2)
        self.icons['barn'] = barn

        # 5. Population Icon (32x32)
        pop = pygame.Surface((32, 32), pygame.SRCALPHA)
        pygame.draw.circle(pop, (65, 150, 225), (16, 11), 6)
        pygame.draw.ellipse(pop, (65, 150, 225), (7, 18, 18, 12))
        self.icons['pop'] = pop

        # 6. Barn Upgrade Tools (Nail, Paint, Hammer)
        nail = pygame.Surface((32, 32), pygame.SRCALPHA)
        pygame.draw.rect(nail, (180, 185, 195), (14, 8, 4, 18), border_radius=1)
        pygame.draw.rect(nail, (130, 135, 145), (11, 6, 10, 4), border_radius=1)
        self.icons['nail'] = nail

        paint = pygame.Surface((32, 32), pygame.SRCALPHA)
        pygame.draw.rect(paint, (220, 55, 55), (8, 10, 16, 16), border_radius=2)
        pygame.draw.rect(paint, (170, 175, 185), (6, 8, 20, 4), border_radius=1)
        pygame.draw.arc(paint, (90, 95, 105), (7, 2, 18, 14), 0, math.pi, 2)
        self.icons['paint'] = paint

        hammer = pygame.Surface((32, 32), pygame.SRCALPHA)
        pygame.draw.rect(hammer, (160, 110, 65), (14, 10, 4, 18), border_radius=1)
        pygame.draw.rect(hammer, (95, 100, 110), (8, 6, 16, 8), border_radius=2)
        self.icons['hammer'] = hammer

        # 7. Products & Goods Icons
        self._build_product_icons()

    def _draw_star(self, surf, cx, cy, r_outer, r_inner, color):
        points = []
        for i in range(10):
            r = r_outer if i % 2 == 0 else r_inner
            angle = -math.pi / 2 + i * (math.pi / 5)
            points.append((cx + int(math.cos(angle) * r), cy + int(math.sin(angle) * r)))
        pygame.draw.polygon(surf, color, points)

    def _build_product_icons(self):
        # Helper to generate 32x32 clean item icons
        def make_icon():
            return pygame.Surface((32, 32), pygame.SRCALPHA)

        # Wheat
        w = make_icon()
        pygame.draw.ellipse(w, (245, 205, 55), (10, 6, 12, 20))
        pygame.draw.line(w, (200, 160, 40), (16, 26), (16, 8), 2)
        self.icons['wheat'] = w

        # Corn
        c = make_icon()
        pygame.draw.ellipse(c, (250, 195, 30), (11, 7, 10, 18))
        pygame.draw.arc(c, (80, 160, 50), (4, 12, 16, 16), 0, math.pi, 3)
        self.icons['corn'] = c

        # Carrot
        cr = make_icon()
        pygame.draw.polygon(cr, (250, 120, 30), [(10, 10), (22, 10), (16, 28)])
        pygame.draw.circle(cr, (65, 155, 40), (16, 7), 5)
        self.icons['carrot'] = cr

        # Sugarcane
        sg = make_icon()
        pygame.draw.rect(sg, (130, 195, 75), (13, 5, 6, 22), border_radius=2)
        pygame.draw.line(sg, (85, 140, 45), (13, 12), (19, 12), 2)
        pygame.draw.line(sg, (85, 140, 45), (13, 19), (19, 19), 2)
        self.icons['sugarcane'] = sg

        # Cotton
        ct = make_icon()
        pygame.draw.circle(ct, (245, 245, 250), (16, 16), 9)
        pygame.draw.circle(ct, (215, 220, 230), (16, 16), 9, 2)
        self.icons['cotton'] = ct

        # Strawberry
        sb = make_icon()
        pygame.draw.polygon(sb, (235, 50, 70), [(8, 10), (24, 10), (16, 26)])
        pygame.draw.circle(sb, (65, 160, 50), (16, 8), 4)
        self.icons['strawberry'] = sb

        # Milk
        mk = make_icon()
        pygame.draw.rect(mk, (245, 248, 255), (10, 10, 12, 18), border_radius=2)
        pygame.draw.rect(mk, (70, 165, 240), (10, 16, 12, 6))
        self.icons['milk'] = mk

        # Egg
        eg = make_icon()
        pygame.draw.ellipse(eg, (250, 240, 225), (10, 6, 12, 18))
        pygame.draw.ellipse(eg, (225, 210, 190), (10, 6, 12, 18), 1)
        self.icons['egg'] = eg

        # Wool
        wl = make_icon()
        pygame.draw.circle(wl, (240, 245, 255), (16, 16), 11)
        pygame.draw.circle(wl, (190, 205, 225), (16, 16), 11, 2)
        self.icons['wool'] = wl

        # Feeds (Sacks)
        for feed, col in [('cow_feed', (140, 190, 80)), ('chicken_feed', (245, 185, 50)), ('sheep_feed', (245, 130, 45)), ('pig_feed', (240, 150, 165))]:
            fd = make_icon()
            pygame.draw.rect(fd, (215, 185, 145), (8, 8, 16, 20), border_radius=3)
            pygame.draw.circle(fd, col, (16, 18), 5)
            self.icons[feed] = fd

        # Bacon
        bcn = make_icon()
        pygame.draw.rect(bcn, (205, 65, 75), (6, 11, 20, 10), border_radius=2)
        pygame.draw.line(bcn, (250, 215, 215), (6, 14), (26, 14), 2)
        pygame.draw.line(bcn, (250, 215, 215), (6, 18), (26, 18), 2)
        self.icons['bacon'] = bcn

        # Bread
        br = make_icon()
        pygame.draw.ellipse(br, (215, 145, 60), (6, 10, 20, 14))
        pygame.draw.line(br, (170, 105, 35), (11, 13), (13, 17), 2)
        pygame.draw.line(br, (170, 105, 35), (17, 13), (19, 17), 2)
        self.icons['bread'] = br

        # Cookie
        ck = make_icon()
        pygame.draw.circle(ck, (225, 165, 75), (16, 16), 11)
        for cx, cy in [(13, 13), (19, 14), (16, 20), (12, 19)]:
            pygame.draw.circle(ck, (75, 45, 25), (cx, cy), 2)
        self.icons['cookie'] = ck

        # Bagel
        bg = make_icon()
        pygame.draw.circle(bg, (220, 155, 65), (16, 16), 11)
        pygame.draw.circle(bg, (0, 0, 0, 0), (16, 16), 4)
        self.icons['bagel'] = bg

        # Cheese
        ch = make_icon()
        pygame.draw.polygon(ch, (250, 205, 40), [(7, 24), (25, 24), (25, 10)])
        pygame.draw.circle(ch, (220, 175, 30), (16, 20), 2)
        self.icons['cheese'] = ch

        # Butter
        bt = make_icon()
        pygame.draw.rect(bt, (255, 230, 80), (7, 11, 18, 12), border_radius=2)
        self.icons['butter'] = bt

        # Yogurt
        yg = make_icon()
        pygame.draw.polygon(yg, (245, 248, 255), [(10, 8), (22, 8), (20, 26), (12, 26)])
        pygame.draw.circle(yg, (235, 65, 85), (16, 16), 3)
        self.icons['yogurt'] = yg

        # Sugar
        sg = make_icon()
        pygame.draw.polygon(sg, (240, 245, 255), [(16, 8), (24, 24), (8, 24)])
        self.icons['sugar'] = sg

        # Syrup
        syp = make_icon()
        pygame.draw.rect(syp, (185, 95, 35), (10, 10, 12, 16), border_radius=3)
        pygame.draw.rect(syp, (140, 70, 25), (13, 6, 6, 4))
        self.icons['syrup'] = syp

        # Fabric & Yarn
        fb = make_icon()
        pygame.draw.rect(fb, (65, 175, 235), (8, 8, 16, 16), border_radius=2)
        self.icons['fabric'] = fb

        yn = make_icon()
        pygame.draw.circle(yn, (225, 80, 120), (16, 16), 10)
        self.icons['yarn'] = yn

    # -------------------------------------------------------------
    # TOWNSPEOPLE CHARACTER PORTRAITS (64x64)
    # -------------------------------------------------------------
    def _build_character_portraits(self):
        chars = ['ernie', 'mayor', 'antonio', 'jenny', 'sarah', 'emma']
        for c in chars:
            surf = pygame.Surface((64, 64), pygame.SRCALPHA)
            cx, cy = 32, 32
            # Background circle badge
            pygame.draw.circle(surf, (245, 235, 215), (cx, cy), 30)
            pygame.draw.circle(surf, (215, 175, 130), (cx, cy), 30, 2)

            if c == 'ernie':
                # Ernie (Farmer Guide with green cap & friendly smile)
                # Head
                pygame.draw.circle(surf, (255, 215, 185), (cx, 30), 16)
                # Green cap
                pygame.draw.arc(surf, (65, 160, 50), (cx - 18, 10, 36, 26), 0, math.pi, 14)
                pygame.draw.rect(surf, (55, 140, 40), (cx - 10, 20, 24, 5), border_radius=2)
                # Blue shirt & brown overalls straps
                pygame.draw.ellipse(surf, (70, 145, 215), (cx - 18, 44, 36, 24))
                pygame.draw.line(surf, (150, 95, 50), (cx - 10, 44), (cx - 8, 62), 3)
                pygame.draw.line(surf, (150, 95, 50), (cx + 10, 44), (cx + 8, 62), 3)
                # Face details
                pygame.draw.circle(surf, (40, 40, 45), (cx - 6, 28), 2)
                pygame.draw.circle(surf, (40, 40, 45), (cx + 6, 28), 2)
                pygame.draw.arc(surf, (180, 55, 45), (cx - 6, 32, 12, 8), math.pi, 2 * math.pi, 2)

            elif c == 'mayor':
                # Mayor Bell (Distinguished with Top Hat & Moustache)
                pygame.draw.circle(surf, (250, 210, 180), (cx, 32), 15)
                # Black Top Hat
                pygame.draw.rect(surf, (45, 45, 50), (cx - 14, 8, 28, 16), border_radius=2)
                pygame.draw.rect(surf, (45, 45, 50), (cx - 20, 22, 40, 4), border_radius=2)
                pygame.draw.rect(surf, (215, 60, 55), (cx - 14, 20, 28, 3)) # Red hat ribbon
                # Suit & Red tie
                pygame.draw.ellipse(surf, (45, 45, 50), (cx - 18, 44, 36, 24))
                pygame.draw.polygon(surf, (220, 50, 45), [(cx - 4, 46), (cx + 4, 46), (cx, 58)])
                # Grey Moustache
                pygame.draw.ellipse(surf, (180, 180, 190), (cx - 10, 36, 20, 6))

            elif c == 'antonio':
                # Chef Antonio (Chef Hat & Moustache)
                pygame.draw.circle(surf, (255, 215, 185), (cx, 34), 15)
                # Big white toque
                pygame.draw.circle(surf, (255, 255, 255), (cx - 10, 16), 10)
                pygame.draw.circle(surf, (255, 255, 255), (cx + 10, 16), 10)
                pygame.draw.circle(surf, (255, 255, 255), (cx, 12), 12)
                pygame.draw.rect(surf, (240, 240, 245), (cx - 14, 20, 28, 8))
                # Red neckerchief
                pygame.draw.polygon(surf, (225, 55, 50), [(cx - 8, 46), (cx + 8, 46), (cx, 54)])
                # Curly moustache
                pygame.draw.arc(surf, (60, 40, 25), (cx - 12, 36, 12, 6), 0, math.pi, 2)
                pygame.draw.arc(surf, (60, 40, 25), (cx, 36, 12, 6), 0, math.pi, 2)

            elif c == 'jenny':
                # Officer Jenny (Police Chief)
                pygame.draw.circle(surf, (255, 215, 185), (cx, 32), 15)
                # Police Hat
                pygame.draw.polygon(surf, (40, 75, 140), [(cx - 18, 22), (cx + 18, 22), (cx + 14, 10), (cx - 14, 10)])
                pygame.draw.circle(surf, (245, 200, 40), (cx, 16), 4) # Gold badge
                # Blue uniform
                pygame.draw.ellipse(surf, (40, 75, 140), (cx - 18, 44, 36, 24))

            elif c == 'sarah':
                # Dr. Sarah
                pygame.draw.circle(surf, (255, 218, 190), (cx, 30), 15)
                # Blonde hair
                pygame.draw.arc(surf, (240, 195, 75), (cx - 16, 14, 32, 26), 0, math.pi, 10)
                # Glasses
                pygame.draw.circle(surf, (80, 80, 90), (cx - 6, 28), 5, 2)
                pygame.draw.circle(surf, (80, 80, 90), (cx + 6, 28), 5, 2)
                pygame.draw.line(surf, (80, 80, 90), (cx - 2, 28), (cx + 2, 28), 2)
                # White Doctor coat & Stethoscope
                pygame.draw.ellipse(surf, (255, 255, 255), (cx - 18, 44, 36, 24))
                pygame.draw.arc(surf, (70, 70, 80), (cx - 12, 44, 24, 16), math.pi, 2 * math.pi, 3)

            elif c == 'emma':
                # Emma (Florist)
                pygame.draw.circle(surf, (255, 220, 195), (cx, 32), 15)
                # Brown hair with flower crown
                pygame.draw.arc(surf, (120, 75, 45), (cx - 16, 14, 32, 26), 0, math.pi, 10)
                # Little flowers
                for fx in [cx - 10, cx, cx + 10]:
                    pygame.draw.circle(surf, (245, 95, 155), (fx, 20), 4)
                    pygame.draw.circle(surf, (255, 235, 90), (fx, 20), 2)
                # Green apron
                pygame.draw.ellipse(surf, (95, 175, 80), (cx - 18, 44, 36, 24))

            self.characters[c] = surf

    # -------------------------------------------------------------
    # MATCH-3 ADVENTURE GEMS (48x48)
    # -------------------------------------------------------------
    def _build_match3_sprites(self):
        gem_types = ['apple', 'carrot', 'sun', 'leaf', 'drop', 'berry']
        for g in gem_types:
            surf = pygame.Surface((48, 48), pygame.SRCALPHA)
            cx, cy = 24, 24

            if g == 'apple':
                # Red shiny apple
                pygame.draw.circle(surf, (235, 50, 60), (cx - 5, cy + 2), 14)
                pygame.draw.circle(surf, (235, 50, 60), (cx + 5, cy + 2), 14)
                pygame.draw.circle(surf, (255, 120, 130), (cx - 6, cy - 4), 4) # highlight
                # Stem & Leaf
                pygame.draw.line(surf, (110, 70, 40), (cx, cy - 10), (cx + 3, cy - 18), 3)
                pygame.draw.ellipse(surf, (90, 190, 60), (cx + 2, cy - 18, 8, 5))

            elif g == 'carrot':
                # Juicy carrot
                pygame.draw.polygon(surf, (250, 125, 30), [(cx - 12, cy - 6), (cx + 12, cy - 6), (cx, cy + 18)])
                pygame.draw.circle(surf, (75, 175, 50), (cx, cy - 10), 7)

            elif g == 'sun':
                # Radiant golden sun / lemon
                pygame.draw.circle(surf, (255, 205, 35), (cx, cy), 14)
                pygame.draw.circle(surf, (255, 235, 110), (cx - 4, cy - 4), 6)

            elif g == 'leaf':
                # Lush green clover / leaf
                for ox, oy in [(-7, -4), (7, -4), (0, 7)]:
                    pygame.draw.circle(surf, (75, 185, 60), (cx + ox, cy + oy), 9)
                pygame.draw.circle(surf, (255, 255, 255), (cx, cy + 1), 3)

            elif g == 'drop':
                # Crystal water drop
                pygame.draw.circle(surf, (65, 165, 245), (cx, cy + 4), 13)
                pygame.draw.polygon(surf, (65, 165, 245), [(cx - 13, cy + 4), (cx + 13, cy + 4), (cx, cy - 16)])
                pygame.draw.circle(surf, (165, 225, 255), (cx - 4, cy + 2), 4)

            elif g == 'berry':
                # Royal purple grape/plum
                pygame.draw.circle(surf, (155, 65, 215), (cx, cy), 14)
                pygame.draw.circle(surf, (205, 135, 245), (cx - 4, cy - 4), 5)

            self.match3_gems[g] = surf

# Singleton instance
_sprite_manager = None

def get_sprite_manager() -> SpriteManager:
    global _sprite_manager
    if _sprite_manager is None:
        _sprite_manager = SpriteManager()
    return _sprite_manager
