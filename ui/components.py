"""
Township - Modern UI Component Library
Reusable widgets with hover animations, shadows, rounded borders,
glassmorphism-style pills, and consistent typography.
"""

import pygame
from typing import Optional, Tuple, Callable
from sound_manager import get_sound_manager

class ModernButton:
    def __init__(
        self,
        rect: pygame.Rect,
        label: str,
        color: Tuple[int, int, int] = (95, 186, 60),
        hover_color: Optional[Tuple[int, int, int]] = None,
        text_color: Tuple[int, int, int] = (255, 255, 255),
        icon: Optional[pygame.Surface] = None,
        sublabel: Optional[str] = None,
        border_radius: int = 10,
        enabled: bool = True
    ):
        self.rect = pygame.Rect(rect)
        self.label = label
        self.color = color
        if hover_color:
            self.hover_color = hover_color
        else:
            self.hover_color = tuple(min(255, c + 25) for c in color)
        self.text_color = text_color
        self.icon = icon
        self.sublabel = sublabel
        self.border_radius = border_radius
        self.enabled = enabled
        self.is_hovered = False

    def update(self, mouse_pos: Tuple[int, int]):
        if not self.enabled:
            self.is_hovered = False
            return
        self.is_hovered = self.rect.collidepoint(mouse_pos)

    def draw(self, surface: pygame.Surface, font_bold, font_small=None):
        draw_rect = self.rect.copy()
        base_color = self.color if self.enabled else (180, 180, 180)
        fill_color = self.hover_color if (self.is_hovered and self.enabled) else base_color

        # Subtle shadow
        if self.enabled:
            shadow_rect = draw_rect.move(0, 3)
            pygame.draw.rect(surface, (0, 0, 0, 45), shadow_rect, border_radius=self.border_radius)

        # Main button background
        pygame.draw.rect(surface, fill_color, draw_rect, border_radius=self.border_radius)
        # Top highlight border
        pygame.draw.rect(surface, (255, 255, 255, 90), draw_rect, 2, border_radius=self.border_radius)

        # Draw content
        cx = draw_rect.centerx
        cy = draw_rect.centery

        if self.icon:
            # Shift content to accommodate icon
            icon_w = self.icon.get_width()
            txt_surf = font_bold.render(self.label, True, self.text_color)
            total_w = icon_w + 8 + txt_surf.get_width()
            start_x = cx - total_w // 2

            surface.blit(self.icon, (start_x, cy - self.icon.get_height() // 2))
            surface.blit(txt_surf, (start_x + icon_w + 8, cy - txt_surf.get_height() // 2))
        else:
            if self.sublabel and font_small:
                txt_surf = font_bold.render(self.label, True, self.text_color)
                sub_surf = font_small.render(self.sublabel, True, (240, 240, 240))
                surface.blit(txt_surf, (cx - txt_surf.get_width() // 2, draw_rect.y + 7))
                surface.blit(sub_surf, (cx - sub_surf.get_width() // 2, draw_rect.y + 28))
            else:
                txt_surf = font_bold.render(self.label, True, self.text_color)
                surface.blit(txt_surf, (cx - txt_surf.get_width() // 2, cy - txt_surf.get_height() // 2))

    def handle_click(self, mouse_pos: Tuple[int, int]) -> bool:
        if self.enabled and self.rect.collidepoint(mouse_pos):
            get_sound_manager().play('click')
            return True
        return False

class ModernCard:
    @staticmethod
    def draw(
        surface: pygame.Surface,
        rect: pygame.Rect,
        bg_color: Tuple[int, int, int] = (255, 255, 255),
        border_color: Tuple[int, int, int] = (220, 215, 205),
        border_radius: int = 12,
        header_color: Optional[Tuple[int, int, int]] = None,
        header_height: int = 40
    ):
        r = pygame.Rect(rect)
        # Drop shadow
        shadow_rect = r.move(0, 4)
        pygame.draw.rect(surface, (0, 0, 0, 35), shadow_rect, border_radius=border_radius)

        # Card body
        pygame.draw.rect(surface, bg_color, r, border_radius=border_radius)
        if border_color:
            pygame.draw.rect(surface, border_color, r, 2, border_radius=border_radius)

        # Header accent band
        if header_color:
            pygame.draw.rect(
                surface,
                header_color,
                (r.x, r.y, r.width, header_height),
                border_top_left_radius=border_radius,
                border_top_right_radius=border_radius
            )
            pygame.draw.line(surface, border_color, (r.x, r.y + header_height), (r.x + r.width, r.y + header_height), 2)

class ModernProgressBar:
    @staticmethod
    def draw(
        surface: pygame.Surface,
        rect: pygame.Rect,
        progress: float,  # 0.0 to 1.0
        bar_color: Tuple[int, int, int] = (95, 195, 60),
        bg_color: Tuple[int, int, int] = (220, 215, 205),
        label: Optional[str] = None,
        font=None,
        border_radius: int = 8
    ):
        r = pygame.Rect(rect)
        pygame.draw.rect(surface, bg_color, r, border_radius=border_radius)

        prog_clamped = max(0.0, min(1.0, progress))
        if prog_clamped > 0:
            fill_w = max(border_radius * 2, int(r.width * prog_clamped))
            fill_rect = pygame.Rect(r.x, r.y, min(r.width, fill_w), r.height)
            pygame.draw.rect(surface, bar_color, fill_rect, border_radius=border_radius)

        pygame.draw.rect(surface, (170, 160, 150), r, 1, border_radius=border_radius)

        if label and font:
            txt_surf = font.render(label, True, (45, 40, 35))
            surface.blit(txt_surf, (r.centerx - txt_surf.get_width() // 2, r.centery - txt_surf.get_height() // 2))

class GlassPill:
    @staticmethod
    def draw(
        surface: pygame.Surface,
        rect: pygame.Rect,
        icon: Optional[pygame.Surface],
        text: str,
        font,
        text_color: Tuple[int, int, int] = (50, 40, 30),
        bg_color: Tuple[int, int, int, int] = (255, 255, 255, 220),
        border_color: Tuple[int, int, int] = (195, 175, 140)
    ):
        r = pygame.Rect(rect)
        pill_surf = pygame.Surface((r.width, r.height), pygame.SRCALPHA)
        pygame.draw.rect(pill_surf, bg_color, (0, 0, r.width, r.height), border_radius=r.height // 2)
        pygame.draw.rect(pill_surf, border_color, (0, 0, r.width, r.height), 2, border_radius=r.height // 2)
        surface.blit(pill_surf, (r.x, r.y))

        if icon:
            surface.blit(icon, (r.x + 6, r.centery - icon.get_height() // 2))
            txt_surf = font.render(text, True, text_color)
            surface.blit(txt_surf, (r.x + icon.get_width() + 10, r.centery - txt_surf.get_height() // 2))
        else:
            txt_surf = font.render(text, True, text_color)
            surface.blit(txt_surf, (r.centerx - txt_surf.get_width() // 2, r.centery - txt_surf.get_height() // 2))
