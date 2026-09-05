"""
Township - Asset Loader & Animation Engine
Handles flexible image loading, spritesheet slicing, and runtime animation
for smoke, windmill, water, and livestock (cows, chickens, pigs, sheep, fountains).
"""

import os
import math
import pygame
from typing import Dict, List, Optional, Tuple

class AssetLoader:
    def __init__(self, base_dir: str = None):
        if base_dir is None:
            base_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "assets")
        self.base_dir = base_dir
        self.image_cache: Dict[str, pygame.Surface] = {}
        self.spritesheet_cache: Dict[str, List[pygame.Surface]] = {}
        self._ensure_asset_directories()

    def _ensure_asset_directories(self):
        subdirs = [
            "backgrounds",
            "buildings",
            "spritesheets",
            "crops",
            "animals",
            "characters",
            "icons",
            "ui",
            "audio"
        ]
        for sub in subdirs:
            full_path = os.path.join(self.base_dir, sub)
            os.makedirs(full_path, exist_ok=True)

        guide_path = os.path.join(self.base_dir, "ASSET_GUIDE.md")
        if not os.path.exists(guide_path):
            with open(guide_path, "w", encoding="utf-8") as f:
                f.write(
"""# Township Custom Asset Replacement Guide

Drop your PNG or JPG files and spritesheets into the folders below.
The game automatically detects and loads them!

- `assets/backgrounds/`: `menu_background.png` or `menu_bg.png`, `grass.png`, `water.png`
- `assets/buildings/`: `cottage.png`, `bakery.png`, `cow_shed.png`, `feed_mill.png`, `pig_pen.png`, etc.
- `assets/spritesheets/`:
  - `smoke.png` (animated factory & bakery chimney smoke)
  - `windmill.png` (animated feed mill spinning wheel)
  - `water.png` (animated water canal ripples)
  - `cow.png` or `cow_sheet.png` (animated cows)
  - `chicken.png` or `chicken_sheet.png` (animated chickens)
  - `pig.png` or `pig_sheet.png` (animated pigs)
  - `sheep.png` or `sheep_sheet.png` (animated sheep)
  - `fountain.png` (animated town fountain water)
- `assets/crops/`: `wheat_0.png`, `wheat_1.png`, `wheat_2.png`, etc.
- `assets/characters/`: `ernie.png`, `mayor.png`, `antonio.png`, `jenny.png`, `sarah.png`, `emma.png`
- `assets/icons/`: `coin.png`, `tcash.png`, `bread.png`, `milk.png`, `bacon.png`, etc.
"""
                )

    def find_file(self, folder: str, candidate_names: List[str]) -> Optional[str]:
        """
        Searches for candidate filenames in assets/<folder> with various extensions.
        """
        folder_path = os.path.join(self.base_dir, folder)
        if not os.path.exists(folder_path):
            return None

        for name in candidate_names:
            # Check with and without extensions
            bases = [name] if '.' in name else [f"{name}.png", f"{name}.jpg", f"{name}.jpeg", f"{name}.webp"]
            for fname in bases:
                fpath = os.path.join(folder_path, fname)
                if os.path.exists(fpath):
                    return os.path.join(folder, fname)
        return None

    def load_first_available(self, folder: str, candidate_names: List[str], fallback_surface: Optional[pygame.Surface] = None, scale: Optional[Tuple[int, int]] = None) -> Optional[pygame.Surface]:
        rel_path = self.find_file(folder, candidate_names)
        if rel_path:
            return self.load_image(rel_path, fallback_surface=fallback_surface, scale=scale)
        if fallback_surface is not None:
            if scale and fallback_surface.get_size() != scale:
                return pygame.transform.smoothscale(fallback_surface, scale)
            return fallback_surface
        return None

    def load_image(self, rel_path: str, fallback_surface: Optional[pygame.Surface] = None, scale: Optional[Tuple[int, int]] = None) -> Optional[pygame.Surface]:
        cache_key = f"{rel_path}_{scale}"
        if cache_key in self.image_cache:
            return self.image_cache[cache_key]

        full_path = os.path.join(self.base_dir, rel_path)
        if os.path.exists(full_path):
            try:
                surf = pygame.image.load(full_path).convert_alpha()
                if scale:
                    surf = pygame.transform.smoothscale(surf, scale)
                self.image_cache[cache_key] = surf
                return surf
            except Exception as e:
                print(f"[AssetLoader] Error loading {rel_path}: {e}")

        if fallback_surface is not None:
            if scale and fallback_surface.get_size() != scale:
                fallback_surface = pygame.transform.smoothscale(fallback_surface, scale)
            self.image_cache[cache_key] = fallback_surface
            return fallback_surface

        return None

    def load_spritesheet(self, rel_path: str, frame_w: int, frame_h: int, col_count: Optional[int] = None, row_count: int = 1, fallback_frames: Optional[List[pygame.Surface]] = None) -> List[pygame.Surface]:
        cache_key = f"{rel_path}_{frame_w}_{frame_h}"
        if cache_key in self.spritesheet_cache:
            return self.spritesheet_cache[cache_key]

        full_path = os.path.join(self.base_dir, rel_path)
        if os.path.exists(full_path):
            try:
                sheet = pygame.image.load(full_path).convert_alpha()
                sheet_w, sheet_h = sheet.get_size()

                cols = col_count if col_count else (sheet_w // frame_w)
                rows = row_count if row_count else (sheet_h // frame_h)

                frames = []
                for r in range(rows):
                    for c in range(cols):
                        sub_rect = pygame.Rect(c * frame_w, r * frame_h, frame_w, frame_h)
                        frame_surf = pygame.Surface((frame_w, frame_h), pygame.SRCALPHA)
                        frame_surf.blit(sheet, (0, 0), sub_rect)
                        frames.append(frame_surf)

                if frames:
                    self.spritesheet_cache[cache_key] = frames
                    return frames
            except Exception as e:
                print(f"[AssetLoader] Error loading spritesheet {rel_path}: {e}")

        if fallback_frames:
            self.spritesheet_cache[cache_key] = fallback_frames
            return fallback_frames

        return []

class AnimatedSprite:
    def __init__(self, frames: List[pygame.Surface], fps: float = 6.0, loop: bool = True):
        self.frames = frames if frames else []
        self.fps = fps
        self.loop = loop
        self.frame_duration = 1.0 / max(0.1, fps)
        self.timer = 0.0
        self.current_idx = 0

    def update(self, dt: float):
        if len(self.frames) <= 1:
            return

        self.timer += dt
        if self.timer >= self.frame_duration:
            advance = int(self.timer // self.frame_duration)
            self.timer = self.timer % self.frame_duration

            if self.loop:
                self.current_idx = (self.current_idx + advance) % len(self.frames)
            else:
                self.current_idx = min(len(self.frames) - 1, self.current_idx + advance)

    def get_current_frame(self) -> Optional[pygame.Surface]:
        if not self.frames:
            return None
        return self.frames[self.current_idx]

class AnimationManager:
    """
    Manages global procedural and custom spritesheet animations:
    - Smoke puffs for chimneys
    - Rotating windmill blades for Feed Mill
    - Animated shimmering water waves for canals
    - Livestock animations: Cow, Chicken, Pig, Sheep
    - Fountain water splash
    """
    def __init__(self, asset_loader):
        self.loader = asset_loader
        self.animations: Dict[str, AnimatedSprite] = {}
        self._init_animations()

    def _init_animations(self):
        # 1. Smoke Animation (4 frames, 32x32)
        smoke_frames = self._build_procedural_smoke_frames()
        smoke_path = self.loader.find_file("spritesheets", ["smoke", "factory_smoke", "bakery_smoke", "smoke_sheet"])
        if smoke_path:
            frames = self.loader.load_spritesheet(smoke_path, 32, 32, fallback_frames=smoke_frames)
        else:
            frames = smoke_frames
        self.animations['smoke'] = AnimatedSprite(frames, fps=5.0)

        # 2. Windmill Animation (4 rotating frames, 48x48)
        windmill_frames = self._build_procedural_windmill_frames()
        wm_path = self.loader.find_file("spritesheets", ["windmill", "feedmill_wheel", "windmill_sheet"])
        if wm_path:
            frames = self.loader.load_spritesheet(wm_path, 48, 48, fallback_frames=windmill_frames)
        else:
            frames = windmill_frames
        self.animations['windmill'] = AnimatedSprite(frames, fps=6.0)

        # 3. Water Canal Animation (4 frames, 54x54)
        water_frames = self._build_procedural_water_frames()
        water_path = self.loader.find_file("spritesheets", ["water", "water_canal", "water_sheet"])
        if water_path:
            frames = self.loader.load_spritesheet(water_path, 54, 54, fallback_frames=water_frames)
        else:
            frames = water_frames
        self.animations['water'] = AnimatedSprite(frames, fps=4.0)

        # 4. Animated Cow (4 frames, 32x24)
        cow_frames = self._build_procedural_cow_frames()
        cow_path = self.loader.find_file("spritesheets", ["cow", "cow_sheet", "cow_anim"]) or self.loader.find_file("animals", ["cow_sheet", "cow"])
        if cow_path:
            frames = self.loader.load_spritesheet(cow_path, 32, 24, fallback_frames=cow_frames)
        else:
            frames = cow_frames
        self.animations['cow'] = AnimatedSprite(frames, fps=3.0)

        # 5. Animated Chicken (4 frames, 20x20)
        chicken_frames = self._build_procedural_chicken_frames()
        chk_path = self.loader.find_file("spritesheets", ["chicken", "chicken_sheet"]) or self.loader.find_file("animals", ["chicken_sheet", "chicken"])
        if chk_path:
            frames = self.loader.load_spritesheet(chk_path, 20, 20, fallback_frames=chicken_frames)
        else:
            frames = chicken_frames
        self.animations['chicken'] = AnimatedSprite(frames, fps=4.0)

        # 6. Animated Pig (4 frames, 32x24)
        pig_frames = self._build_procedural_pig_frames()
        pig_path = self.loader.find_file("spritesheets", ["pig", "pig_sheet", "pig_anim"]) or self.loader.find_file("animals", ["pig_sheet", "pig"])
        if pig_path:
            frames = self.loader.load_spritesheet(pig_path, 32, 24, fallback_frames=pig_frames)
        else:
            frames = pig_frames
        self.animations['pig'] = AnimatedSprite(frames, fps=3.0)

        # 7. Animated Sheep (4 frames, 32x24)
        sheep_frames = self._build_procedural_sheep_frames()
        sheep_path = self.loader.find_file("spritesheets", ["sheep", "sheep_sheet", "sheep_anim"]) or self.loader.find_file("animals", ["sheep_sheet", "sheep"])
        if sheep_path:
            frames = self.loader.load_spritesheet(sheep_path, 32, 24, fallback_frames=sheep_frames)
        else:
            frames = sheep_frames
        self.animations['sheep'] = AnimatedSprite(frames, fps=3.0)

        # 8. Animated Fountain (4 frames, 64x64)
        fountain_frames = self._build_procedural_fountain_frames()
        fnt_path = self.loader.find_file("spritesheets", ["fountain", "fountain_sheet"])
        if fnt_path:
            frames = self.loader.load_spritesheet(fnt_path, 64, 64, fallback_frames=fountain_frames)
        else:
            frames = fountain_frames
        self.animations['fountain'] = AnimatedSprite(frames, fps=6.0)

    def update(self, dt: float):
        for anim in self.animations.values():
            anim.update(dt)

    def get_frame(self, name: str) -> Optional[pygame.Surface]:
        anim = self.animations.get(name)
        if anim:
            return anim.get_current_frame()
        return None

    # Procedural Frame Builders
    def _build_procedural_smoke_frames(self) -> List[pygame.Surface]:
        frames = []
        for i in range(4):
            surf = pygame.Surface((32, 32), pygame.SRCALPHA)
            alpha = int(180 - i * 35)
            r1 = 4 + i * 2
            r2 = 6 + i * 2
            py = 22 - i * 5
            pygame.draw.circle(surf, (245, 245, 250, alpha), (14, py), r1)
            pygame.draw.circle(surf, (230, 230, 235, max(0, alpha - 25)), (18, py - 4), r2)
            frames.append(surf)
        return frames

    def _build_procedural_windmill_frames(self) -> List[pygame.Surface]:
        frames = []
        cx, cy = 24, 24
        for step in range(4):
            surf = pygame.Surface((48, 48), pygame.SRCALPHA)
            base_ang = step * (math.pi / 8)
            for a in range(4):
                angle = base_ang + a * (math.pi / 2)
                dx = int(math.cos(angle) * 18)
                dy = int(math.sin(angle) * 18)
                pygame.draw.line(surf, (250, 250, 250), (cx, cy), (cx + dx, cy + dy), 3)
            pygame.draw.circle(surf, (90, 60, 40), (cx, cy), 5)
            frames.append(surf)
        return frames

    def _build_procedural_water_frames(self) -> List[pygame.Surface]:
        frames = []
        for step in range(4):
            surf = pygame.Surface((54, 54))
            surf.fill((65, 168, 225))
            pygame.draw.rect(surf, (45, 138, 195), (0, 0, 54, 54), 2)
            shift = step * 3
            pygame.draw.arc(surf, (120, 215, 255), (6 + shift, 10, 24, 10), 0, math.pi, 2)
            pygame.draw.arc(surf, (120, 215, 255), (28 - shift, 28, 24, 10), 0, math.pi, 2)
            frames.append(surf)
        return frames

    def _build_procedural_cow_frames(self) -> List[pygame.Surface]:
        frames = []
        for step in range(4):
            surf = pygame.Surface((32, 24), pygame.SRCALPHA)
            bob = 1 if step in (1, 3) else 0
            # Body
            pygame.draw.ellipse(surf, (250, 250, 250), (4, 4 + bob, 24, 16))
            pygame.draw.circle(surf, (40, 40, 45), (10, 8 + bob), 4)
            pygame.draw.circle(surf, (40, 40, 45), (20, 12 + bob), 3)
            # Head & muzzle
            pygame.draw.circle(surf, (250, 250, 250), (24, 8 + bob), 6)
            muzzle_shift = 1 if step == 2 else 0
            pygame.draw.circle(surf, (255, 190, 195), (26 + muzzle_shift, 9 + bob), 4)
            # Horns
            pygame.draw.circle(surf, (240, 205, 120), (22, 3 + bob), 2)
            pygame.draw.circle(surf, (240, 205, 120), (26, 3 + bob), 2)
            frames.append(surf)
        return frames

    def _build_procedural_chicken_frames(self) -> List[pygame.Surface]:
        frames = []
        for step in range(4):
            surf = pygame.Surface((20, 20), pygame.SRCALPHA)
            peck = 2 if step == 1 else 0
            pygame.draw.circle(surf, (255, 250, 240), (10, 11 + peck), 6)
            pygame.draw.polygon(surf, (235, 55, 50), [(8, 4 + peck), (12, 4 + peck), (10, 7 + peck)])
            pygame.draw.polygon(surf, (245, 175, 35), [(14, 10 + peck), (18, 11 + peck), (14, 13 + peck)])
            pygame.draw.circle(surf, (30, 30, 35), (12, 9 + peck), 1)
            frames.append(surf)
        return frames

    def _build_procedural_pig_frames(self) -> List[pygame.Surface]:
        frames = []
        for step in range(4):
            surf = pygame.Surface((32, 24), pygame.SRCALPHA)
            bob = 1 if step in (1, 3) else 0
            # Body
            pygame.draw.ellipse(surf, (255, 185, 195), (4, 4 + bob, 24, 16))
            pygame.draw.circle(surf, (255, 175, 185), (22, 9 + bob), 6)
            # Snout
            snout_shift = 1 if step == 2 else 0
            pygame.draw.ellipse(surf, (255, 150, 165), (24 + snout_shift, 9 + bob, 6, 5))
            pygame.draw.circle(surf, (90, 45, 55), (26 + snout_shift, 9 + bob), 1)
            # Ears & curly tail
            pygame.draw.polygon(surf, (245, 145, 160), [(20, 4 + bob), (23, 1 + bob), (24, 5 + bob)])
            tail_ang = (step * math.pi / 4)
            pygame.draw.arc(surf, (255, 165, 175), (0, 6 + bob, 8, 8), tail_ang, tail_ang + math.pi, 2)
            frames.append(surf)
        return frames

    def _build_procedural_sheep_frames(self) -> List[pygame.Surface]:
        frames = []
        for step in range(4):
            surf = pygame.Surface((32, 24), pygame.SRCALPHA)
            bob = 1 if step in (1, 3) else 0
            for ox, oy in [(8, 8), (18, 8), (13, 5), (13, 11)]:
                pygame.draw.circle(surf, (250, 250, 255), (ox, oy + bob), 7)
            # Black face
            pygame.draw.ellipse(surf, (50, 50, 55), (20, 7 + bob, 8, 9))
            pygame.draw.circle(surf, (50, 50, 55), (19, 5 + bob), 2)
            frames.append(surf)
        return frames

    def _build_procedural_fountain_frames(self) -> List[pygame.Surface]:
        frames = []
        for step in range(4):
            surf = pygame.Surface((64, 64), pygame.SRCALPHA)
            cx, cy = 32, 32
            jet_h = 14 + step * 3
            pygame.draw.circle(surf, (220, 240, 255), (cx, cy - 6), 6)
            pygame.draw.line(surf, (255, 255, 255), (cx, cy - 6), (cx, cy - jet_h), 3)
            # Droplets
            pygame.draw.circle(surf, (190, 230, 255), (cx - 6 - step, cy - jet_h + 4), 2)
            pygame.draw.circle(surf, (190, 230, 255), (cx + 6 + step, cy - jet_h + 4), 2)
            frames.append(surf)
        return frames

# Singleton instances
_asset_loader = None
_anim_manager = None

def get_asset_loader() -> AssetLoader:
    global _asset_loader
    if _asset_loader is None:
        _asset_loader = AssetLoader()
    return _asset_loader

def get_animation_manager() -> AnimationManager:
    global _anim_manager
    if _anim_manager is None:
        _anim_manager = AnimationManager(get_asset_loader())
    return _anim_manager
