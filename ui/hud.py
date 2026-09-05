"""
Township - Modern Head-Up Display (HUD) & Floating Dock
Renders the top status bar (Level, XP bar, Coins, T-Cash, Population, Barn),
the in-game menu gear button, the floating action dock, and animated toasts.
"""

import pygame
from typing import Tuple
from config import (
    COLOR_PANEL_BG, COLOR_PANEL_BORDER, COLOR_PANEL_HEADER,
    COLOR_TEXT_DARK, COLOR_TEXT_LIGHT, COLOR_GOLD, COLOR_TCASH,
    get_xp_for_level
)
from sound_manager import get_sound_manager
from ui.components import GlassPill, ModernButton

class HUD:
    def __init__(self, state, sprite_manager):
        self.state = state
        self.sprites = sprite_manager
        self.btn_menu = ModernButton(
            pygame.Rect(0, 0, 95, 38),
            "MENU",
            color=(100, 110, 125),
            hover_color=(125, 135, 150),
            border_radius=10
        )

    def update(self, mouse_pos: Tuple[int, int]):
        self.btn_menu.update(mouse_pos)

    def render(self, surface: pygame.Surface, font_bold, font_regular, font_small):
        w, h = surface.get_size()
        self._render_top_bar(surface, w, font_bold, font_regular, font_small)
        self._render_bottom_dock(surface, w, h, font_bold, font_small)
        self._render_toasts(surface, w, h, font_bold)

    def _render_top_bar(self, surface: pygame.Surface, screen_w: int, font_bold, font_reg, font_small):
        bar_h = 58

        # Floating frosted top panel
        top_bar = pygame.Surface((screen_w, bar_h), pygame.SRCALPHA)
        top_bar.fill((252, 248, 238, 235))
        surface.blit(top_bar, (0, 0))
        pygame.draw.line(surface, (215, 205, 190), (0, bar_h), (screen_w, bar_h), 2)

        # 1. Level & XP Circular Badge (Left)
        lvl_rect = pygame.Rect(16, 9, 42, 42)
        pygame.draw.circle(surface, (60, 145, 230), lvl_rect.center, 21)
        pygame.draw.circle(surface, (30, 95, 175), lvl_rect.center, 21, 2)
        lvl_txt = font_bold.render(str(self.state.level), True, (255, 255, 255))
        surface.blit(lvl_txt, (lvl_rect.centerx - lvl_txt.get_width() // 2, lvl_rect.centery - lvl_txt.get_height() // 2))

        # XP progress bar
        curr_lvl_xp = get_xp_for_level(self.state.level)
        next_lvl_xp = get_xp_for_level(self.state.level + 1)
        needed = max(1, next_lvl_xp - curr_lvl_xp)
        progress = min(1.0, max(0.0, (self.state.xp - curr_lvl_xp) / needed))

        xp_bar_w = 115
        pygame.draw.rect(surface, (220, 215, 205), (66, 21, xp_bar_w, 16), border_radius=8)
        if progress > 0:
            pygame.draw.rect(surface, (95, 195, 60), (66, 21, int(xp_bar_w * progress), 16), border_radius=8)
        pygame.draw.rect(surface, (180, 170, 160), (66, 21, xp_bar_w, 16), 1, border_radius=8)

        xp_star = self.sprites.icons.get('xp')
        if xp_star:
            surface.blit(xp_star, (52, 13))

        xp_txt = font_small.render(f"{self.state.xp}/{next_lvl_xp}", True, COLOR_TEXT_DARK)
        surface.blit(xp_txt, (66 + (xp_bar_w - xp_txt.get_width()) // 2, 22))

        # 2. Population Pill (Center-Left)
        pop_x = 215
        pop_icon = self.sprites.icons.get('pop')
        GlassPill.draw(
            surface,
            pygame.Rect(pop_x, 12, 125, 34),
            pop_icon,
            f"{self.state.population}/{self.state.population_cap}",
            font_bold,
            text_color=(45, 105, 180)
        )

        # 3. Barn Capacity Pill (Center)
        barn_x = 350
        barn_icon = self.sprites.icons.get('barn')
        GlassPill.draw(
            surface,
            pygame.Rect(barn_x, 12, 130, 34),
            barn_icon,
            f"{self.state.get_barn_count()}/{self.state.barn_capacity}",
            font_bold,
            text_color=(185, 55, 45)
        )

        # 4. Coins Pill
        coins_x = screen_w - 460
        coin_icon = self.sprites.icons.get('coin')
        GlassPill.draw(
            surface,
            pygame.Rect(coins_x, 12, 160, 34),
            coin_icon,
            f"{self.state.coins:,}",
            font_bold,
            text_color=(200, 135, 20)
        )

        # 5. Township Cash Pill
        tcash_x = screen_w - 285
        tcash_icon = self.sprites.icons.get('tcash')
        GlassPill.draw(
            surface,
            pygame.Rect(tcash_x, 12, 165, 34),
            tcash_icon,
            f"{self.state.tcash} T$",
            font_bold,
            text_color=COLOR_TCASH
        )

        # 6. In-Game Menu Button (Top Right)
        self.btn_menu.rect = pygame.Rect(screen_w - 110, 10, 95, 38)
        self.btn_menu.draw(surface, font_bold)

    def _render_bottom_dock(self, surface: pygame.Surface, screen_w: int, screen_h: int, font_bold, font_small):
        dock_h = 72
        dock_y = screen_h - dock_h - 10

        buttons = [
            {'id': 'build', 'label': 'Build', 'color': (95, 186, 60), 'sub': 'Shop'},
            {'id': 'orders', 'label': 'Orders', 'color': (245, 150, 40), 'sub': 'Helicopter'},
            {'id': 'barn', 'label': 'Barn', 'color': (215, 75, 60), 'sub': 'Storage'},
            {'id': 'match3', 'label': 'Event', 'color': (155, 75, 225), 'sub': 'Match-3'},
            {'id': 'daily', 'label': 'Daily', 'color': (52, 152, 219), 'sub': 'Bonus'},
            {'id': 'quests', 'label': 'Ernie', 'color': (240, 185, 45), 'sub': 'Quests'},
            {'id': 'save', 'label': 'Save', 'color': (110, 120, 130), 'sub': 'Game'}
        ]

        btn_w = 110
        spacing = 14
        total_w = len(buttons) * btn_w + (len(buttons) - 1) * spacing
        start_x = (screen_w - total_w) // 2

        # Floating dock shadow & container
        pygame.draw.rect(surface, (0, 0, 0, 40), (start_x - 16, dock_y + 4, total_w + 32, dock_h), border_radius=18)
        pygame.draw.rect(surface, (252, 248, 238), (start_x - 16, dock_y, total_w + 32, dock_h), border_radius=18)
        pygame.draw.rect(surface, (215, 205, 190), (start_x - 16, dock_y, total_w + 32, dock_h), 2, border_radius=18)

        for i, b in enumerate(buttons):
            bx = start_x + i * (btn_w + spacing)
            by = dock_y + 9
            rect = pygame.Rect(bx, by, btn_w, 54)
            pygame.draw.rect(surface, b['color'], rect, border_radius=12)
            pygame.draw.rect(surface, (255, 255, 255, 110), rect, 2, border_radius=12)

            lbl = font_bold.render(b['label'], True, (255, 255, 255))
            sub = font_small.render(b['sub'], True, (240, 240, 240))
            surface.blit(lbl, (rect.centerx - lbl.get_width() // 2, rect.y + 8))
            surface.blit(sub, (rect.centerx - sub.get_width() // 2, rect.y + 30))

    def _render_toasts(self, surface: pygame.Surface, screen_w: int, screen_h: int, font_bold):
        start_y = 75
        for t in self.state.toasts:
            alpha = min(255, int(255 * (t['timer'] / 0.5))) if t['timer'] < 0.5 else 255
            txt_surf = font_bold.render(t['message'], True, t['color'])
            tw, th = txt_surf.get_width() + 32, txt_surf.get_height() + 16

            box = pygame.Surface((tw, th), pygame.SRCALPHA)
            pygame.draw.rect(box, (35, 30, 25, 215), (0, 0, tw, th), border_radius=12)
            pygame.draw.rect(box, t['color'], (0, 0, tw, th), 2, border_radius=12)
            box.blit(txt_surf, (16, 8))

            if alpha < 255:
                box.set_alpha(alpha)

            surface.blit(box, ((screen_w - tw) // 2, start_y))
            start_y += th + 10

    def handle_click(self, mx: int, my: int, screen_w: int, screen_h: int) -> str:
        # Check Top Menu button
        if self.btn_menu.handle_click((mx, my)):
            return "menu"

        dock_h = 72
        dock_y = screen_h - dock_h - 10
        if my < dock_y:
            return "none"

        buttons = ['build', 'orders', 'barn', 'match3', 'daily', 'quests', 'save']
        btn_w = 110
        spacing = 14
        total_w = len(buttons) * btn_w + (len(buttons) - 1) * spacing
        start_x = (screen_w - total_w) // 2

        for i, b_id in enumerate(buttons):
            bx = start_x + i * (btn_w + spacing)
            by = dock_y + 9
            rect = pygame.Rect(bx, by, btn_w, 54)
            if rect.collidepoint(mx, my):
                get_sound_manager().play('click')
                return b_id

        return "none"
