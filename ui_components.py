"""
This module provides a simple GUI toolkit for Pygame, including themed widgets 
like Buttons, Checkboxes, Sliders, and TextInputs. It also features a draggable, 
resizable Window class with a dynamic grid layout system for organizing widgets.
"""

import pygame
from typing import Tuple, Callable, Optional

pygame.init()

# --- Constants and Theming ---

CURRENT_THEME = None
HEADER_HEIGHT = 28
WINDOW_PADDING = 4
RESIZE_MARGIN = 10

RESIZE_NWSE_CURSOR = pygame.cursors.Cursor(pygame.SYSTEM_CURSOR_SIZENWSE)
RESIZE_NESW_CURSOR = pygame.cursors.Cursor(pygame.SYSTEM_CURSOR_SIZENESW)
RESIZE_NS_CURSOR = pygame.cursors.Cursor(pygame.SYSTEM_CURSOR_SIZENS)
RESIZE_WE_CURSOR = pygame.cursors.Cursor(pygame.SYSTEM_CURSOR_SIZEWE)
ARROW_CURSOR = pygame.cursors.Cursor(pygame.SYSTEM_CURSOR_ARROW)


class Theme:
    """A simple class to hold theme attributes like colors and fonts."""
    def __init__(self, **kwargs):
        self.__dict__.update(kwargs)

THEMES = {
    "light": Theme(
        WINDOW_BG=(255, 255, 255), TEXT=(0, 0, 0), SUBTEXT=(102, 102, 102),
        BORDER=(179, 179, 179), ACCENT=(0, 120, 215), HEADER=(176, 176, 176),
        FONT=pygame.font.SysFont("Arial", 16),
        SMALL_FONT=pygame.font.SysFont("Arial", 14)
    ),
    "dark": Theme(
        WINDOW_BG=(40, 40, 44), TEXT=(220, 220, 230), SUBTEXT=(153, 153, 163),
        BORDER=(60, 60, 65), ACCENT=(10, 130, 255), HEADER=(60, 60, 65),
        FONT=pygame.font.SysFont("Arial", 16),
        SMALL_FONT=pygame.font.SysFont("Arial", 14)
    )
}

def set_theme(name: str = None):
    """
    Sets the global theme for all UI components.
    If no name is provided, it toggles between 'light' and 'dark'.
    """
    global CURRENT_THEME
    if name in ["light", "dark"]:
        CURRENT_THEME = THEMES[name]
    else:
        if CURRENT_THEME == THEMES["light"]:
            CURRENT_THEME = THEMES["dark"]
        else:
            CURRENT_THEME = THEMES["light"]

# --- Base Widget Class ---

class Widget:
    """Base class for all UI elements."""
    def __init__(self, rect: pygame.Rect, grid_span: Tuple[int, int] = (1, 1)):
        self.rect = rect
        self.visible = True
        self.grid_span = grid_span  # (cols, rows)

    def handle_event(self, event):
        """Handles a single Pygame event. Returns True if the event was handled."""
        return False

    def draw(self, surf):
        """Draws the widget on the given surface."""
        pass

# --- UI Widget Implementations ---

class Info(Widget):
    """A widget to display a label and a dynamic value."""
    def __init__(self, rect: pygame.Rect, text: str, value_provider: Callable):
        super().__init__(rect, grid_span=(1, 1))
        self.text = text
        self.value_provider = value_provider

    def draw(self, surf):
        if not self.visible:
            return
        value = self.value_provider()
        display_text = f"{self.text}: {value}"
        txt_surface = CURRENT_THEME.FONT.render(display_text, True, CURRENT_THEME.TEXT)
        pygame.draw.rect(surf, CURRENT_THEME.WINDOW_BG, self.rect)
        surf.blit(txt_surface, txt_surface.get_rect(center=self.rect.center))

    def handle_event(self, event):
        return False

class Button(Widget):
    """A standard clickable button."""
    def __init__(self, rect: pygame.Rect, text: str, on_click: Optional[Callable] = None):
        super().__init__(rect, grid_span=(1, 1))
        self.text = text
        self.on_click = on_click
        self.hover = False
        self.clicked = False

    def handle_event(self, event):
        if event.type == pygame.MOUSEMOTION:
            self.hover = self.rect.collidepoint(event.pos)
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.rect.collidepoint(event.pos):
                self.clicked = True
                return True
        if event.type == pygame.MOUSEBUTTONUP and event.button == 1:
            if self.clicked and self.rect.collidepoint(event.pos):
                if self.on_click:
                    self.on_click()
                self.clicked = False
                return True
            self.clicked = False
        return False

    def draw(self, surf):
        color = CURRENT_THEME.WINDOW_BG
        if self.clicked:
            color = CURRENT_THEME.ACCENT
        elif self.hover:
            color = CURRENT_THEME.BORDER
        pygame.draw.rect(surf, color, self.rect, border_radius=6)
        pygame.draw.rect(surf, CURRENT_THEME.BORDER, self.rect, 1, border_radius=6)
        txt = CURRENT_THEME.FONT.render(self.text, True, CURRENT_THEME.TEXT)
        surf.blit(txt, txt.get_rect(center=self.rect.center))

class Checkbox(Widget):
    """A checkbox that can be toggled on or off."""
    def __init__(self, rect: pygame.Rect, text: str, on_change: Optional[Callable] = None):
        super().__init__(rect, grid_span=(1, 1))
        self.checked = False
        self.on_change = on_change
        self.text = text
        self.hover = False
        self.box_size = 20
        self.box_rect = pygame.Rect(0, 0, self.box_size, self.box_size)

    def handle_event(self, event):
        if event.type == pygame.MOUSEMOTION:
            self.hover = self.box_rect.collidepoint(event.pos)
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.box_rect.collidepoint(event.pos):
                self.checked = not self.checked
                if self.on_change:
                    self.on_change()
                return True
        return False

    def draw(self, surf):
        txt = CURRENT_THEME.FONT.render(self.text, True, CURRENT_THEME.TEXT)
        surf.blit(txt, txt.get_rect(center=self.rect.center))
        self.box_size = min(self.rect.height - 10, 20)
        self.box_rect = pygame.Rect(self.rect.x + 5, self.rect.y + (self.rect.height - self.box_size) // 2, self.box_size, self.box_size)
        if self.hover:
            pygame.draw.rect(surf, CURRENT_THEME.BORDER, self.box_rect.inflate(4, 4), border_radius=4)
        pygame.draw.rect(surf, CURRENT_THEME.WINDOW_BG, self.box_rect)
        pygame.draw.rect(surf, CURRENT_THEME.BORDER, self.box_rect, 2, border_radius=4)
        if self.checked:
            inner = self.box_rect.inflate(-6, -6)
            pygame.draw.rect(surf, CURRENT_THEME.ACCENT, inner, border_radius=3)

class Slider(Widget):
    """A slider for selecting a value within a given range. Spans 2 grid cells."""
    def __init__(self, rect: pygame.Rect, text: str, min_val: float, max_val: float, value: float, on_change: Optional[Callable] = None):
        super().__init__(rect, grid_span=(2, 1))
        self.min_val = min_val
        self.max_val = max_val
        self.value = value
        self.on_change = on_change
        self.dragging = False
        self.text = text
        self.hover = False

    def _value_to_pos(self):
        track_padding = max(8, int(self.rect.width * 0.1))
        track_width = self.rect.width - 2 * track_padding
        ratio = (self.value - self.min_val) / (self.max_val - self.min_val)
        return int(self.rect.x + track_padding + ratio * track_width)

    def _pos_to_value(self, x):
        track_padding = max(8, int(self.rect.width * 0.1))
        track_width = self.rect.width - 2 * track_padding
        ratio = (x - (self.rect.x + track_padding)) / track_width
        ratio = max(0.0, min(1.0, ratio))
        return self.min_val + ratio * (self.max_val - self.min_val)

    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.rect.collidepoint(event.pos):
                self.dragging = True
                self.value = self._pos_to_value(event.pos[0])
                if self.on_change: self.on_change(self.value)
                return True
        elif event.type == pygame.MOUSEBUTTONUP and event.button == 1:
            if self.dragging:
                self.dragging = False
                return True
        elif event.type == pygame.MOUSEMOTION:
            self.hover = self.rect.collidepoint(event.pos)
            if self.dragging:
                self.value = self._pos_to_value(event.pos[0])
                if self.on_change: self.on_change(self.value)
                return True
        return False

    def draw(self, surf):
        clip_rect = surf.get_clip()
        surf.set_clip(self.rect)
        pygame.draw.rect(surf, CURRENT_THEME.WINDOW_BG, self.rect, border_radius=6)
        label_height = self.rect.height // 2
        slider_height = self.rect.height // 2
        label_rect = pygame.Rect(self.rect.x, self.rect.y, self.rect.width, label_height)
        slider_rect = pygame.Rect(self.rect.x, self.rect.y + label_height, self.rect.width, slider_height)
        val_txt = CURRENT_THEME.SMALL_FONT.render(f"{self.text} : {self.value:.2f}", True, CURRENT_THEME.TEXT)
        surf.blit(val_txt, val_txt.get_rect(center=label_rect.center))
        track_height = max(4, min(8, int(slider_rect.height * 0.4)))
        track_y = slider_rect.centery
        track_padding = max(8, int(self.rect.width * 0.1))
        track_rect = pygame.Rect(self.rect.x + track_padding, track_y - track_height // 2, self.rect.width - 2 * track_padding, track_height)
        pygame.draw.rect(surf, CURRENT_THEME.HEADER, track_rect, border_radius=4)
        fill_w = int((self.value - self.min_val) / (self.max_val - self.min_val) * track_rect.width)
        if fill_w > 0:
            pygame.draw.rect(surf, CURRENT_THEME.ACCENT, (track_rect.x, track_rect.y, fill_w, track_rect.height), border_radius=4)
        knob_size = max(8, min(16, track_height * 2))
        kx = self._value_to_pos()
        knob_rect = pygame.Rect(kx - knob_size // 2, track_y - knob_size // 2, knob_size, knob_size)
        pygame.draw.rect(surf, CURRENT_THEME.WINDOW_BG, knob_rect, border_radius=knob_size // 2)
        pygame.draw.rect(surf, CURRENT_THEME.BORDER, knob_rect, 1, border_radius=knob_size // 2)
        if self.hover or self.dragging:
            pygame.draw.rect(surf, CURRENT_THEME.BORDER, self.rect, 1, border_radius=8)
        surf.set_clip(clip_rect)

class TextInput(Widget):
    """A text input field for user text entry."""
    def __init__(self, rect: pygame.Rect, text: str = "", on_change: Optional[Callable] = None):
        super().__init__(rect, grid_span=(1, 1))
        self.placeholder = text
        self.text = "" if text else text
        self._is_placeholder = bool(text)
        self.active = False
        self.on_change = on_change
        self.cursor = 0
        self.cursor_visible = True
        self.cursor_timer = 0.0

    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            self.active = self.rect.collidepoint(event.pos)
            if self.active and self._is_placeholder:
                self.text = ""
                self._is_placeholder = False
                self.cursor = 0
            return self.active
        if not self.active: return False
        if event.type == pygame.KEYDOWN:
            if self._is_placeholder and event.unicode:
                self.text = ""
                self._is_placeholder = False
                self.cursor = 0
            if event.key == pygame.K_BACKSPACE:
                if self.cursor > 0:
                    self.text = self.text[:self.cursor - 1] + self.text[self.cursor:]
                    self.cursor -= 1
                    if self.on_change: self.on_change(self.text)
                return True
            elif event.key == pygame.K_DELETE:
                self.text = self.text[:self.cursor] + self.text[self.cursor + 1:]
                if self.on_change: self.on_change(self.text)
                return True
            elif event.key == pygame.K_LEFT:
                self.cursor = max(0, self.cursor - 1)
                return True
            elif event.key == pygame.K_RIGHT:
                self.cursor = min(len(self.text), self.cursor + 1)
                return True
            elif event.key == pygame.K_RETURN:
                self.active = False
                if self.on_change: self.on_change(self.text)
                return True
            elif event.unicode:
                self.text = self.text[:self.cursor] + event.unicode + self.text[self.cursor:]
                self.cursor += 1
                if self.on_change: self.on_change(self.text)
                return True
        return False

    def draw(self, surf):
        pygame.draw.rect(surf, CURRENT_THEME.WINDOW_BG, self.rect, border_radius=6)
        pygame.draw.rect(surf, CURRENT_THEME.BORDER, self.rect, 1, border_radius=6)
        txt = CURRENT_THEME.FONT.render(self.placeholder if self._is_placeholder else self.text, True, CURRENT_THEME.SUBTEXT if self._is_placeholder else CURRENT_THEME.TEXT)
        surf.blit(txt, (self.rect.x + 8, self.rect.y + (self.rect.height - txt.get_height()) / 2))
        if self.active:
            self.cursor_timer += 1 / 60.0
            if self.cursor_timer > 0.5:
                self.cursor_visible = not self.cursor_visible
                self.cursor_timer = 0.0
            if self.cursor_visible:
                pre_text = self.text[:self.cursor]
                pre_surface = CURRENT_THEME.FONT.render(pre_text, True, CURRENT_THEME.TEXT)
                cursor_x = self.rect.x + 8 + pre_surface.get_width()
                pygame.draw.line(surf, CURRENT_THEME.TEXT, (cursor_x, self.rect.y + 6), (cursor_x, self.rect.y + self.rect.height - 6), 2)

# --- Window and Layout Management ---

class GridLayout:
    """A layout manager that arranges widgets in a dynamic grid."""
    def __init__(self, rect, cell_size=(120, 30), padding=WINDOW_PADDING):
        self.rect = rect
        self.cell_size = cell_size
        self.padding = padding
        self.widgets = []
        self.grid_map = {}

    def add_widget(self, widget):
        self.widgets.append(widget)

    def update_positions(self, parent_rect=None):
        """Recalculates widget positions, hiding those that don't fit."""
        if parent_rect is not None:
            self.rect = pygame.Rect(parent_rect.x, parent_rect.y + HEADER_HEIGHT, parent_rect.width, parent_rect.height - HEADER_HEIGHT)
        if not self.widgets: return

        cols = max(1, int(self.rect.width // self.cell_size[0]))
        cell_h = self.cell_size[1]
        self.grid_map = {}
        
        for widget in self.widgets:
            span_cols, span_rows = widget.grid_span
            row, col = 0, 0
            found = False
            
            # Find the next available spot for the widget
            while not found:
                # Check if widget would overflow vertically even at the current row
                if self.rect.y + (row * cell_h) + (span_rows * cell_h) > self.rect.bottom:
                    widget.visible = False
                    break # Stop trying to place this widget

                if (row, col) in self.grid_map:
                    col += 1
                    if col >= cols:
                        col = 0
                        row += 1
                    continue
                
                can_fit = True
                if col + span_cols > cols:
                    can_fit = False
                else:
                    for r_off in range(span_rows):
                        for c_off in range(span_cols):
                            if (row + r_off, col + c_off) in self.grid_map:
                                can_fit = False
                                break
                        if not can_fit: break
                
                if can_fit:
                    found = True
                else:
                    col += 1
                    if col >= cols:
                        col = 0
                        row += 1

            if not found: # Widget could not be placed (it overflows)
                widget.visible = False
                continue

            widget.visible = True
            # Occupy cells in the grid map
            for r_off in range(span_rows):
                for c_off in range(span_cols):
                    self.grid_map[(row + r_off, col + c_off)] = widget

            # Set widget's final screen rectangle
            cell_w = self.rect.width / cols
            x = self.rect.x + col * cell_w + self.padding
            y = self.rect.y + row * cell_h + self.padding
            width = span_cols * cell_w - (2 * self.padding)
            height = span_rows * cell_h - (2 * self.padding)
            widget.rect = pygame.Rect(x, y, width, height)

    def handle_event(self, event):
        for widget in self.widgets:
            # only if they are visible
            if not widget.visible: continue
            if widget.handle_event(event):
                return True
        return False

    def draw(self, surf):
        for widget in self.widgets:
            # only if they are visible
            if widget.visible:
                widget.draw(surf)

class Window(Widget):
    """A draggable, resizable window that automatically lays out its widgets."""
    def __init__(self, x=10, y=10, w=300, h=400, title: str = "Window"):
        super().__init__(pygame.Rect(x, y, w, h))
        self.header = pygame.Rect(x, y, w, HEADER_HEIGHT)
        self.title = title
        self.visible = True
        self.minimized = False
        self.dragging = False
        self.offset = (0, 0)
        self.resizing = False
        self.resize_dir = None
        self.min_width = 200
        self.min_height = 100
        self.resize_margin = RESIZE_MARGIN
        self.padding = WINDOW_PADDING
        self.isMain = (title == "Main")
        self.D_info = False

        self.layout = GridLayout(pygame.Rect(0, 0, 1, 1), cell_size=(120, 35), padding=self.padding)
        self.layout.update_positions(self.rect)

        if not self.isMain:
            self.close_btn = Button(pygame.Rect(0, 0, 28, 20), "X", self._close)
        self.min_btn = Button(pygame.Rect(0, 0, 28, 20), "_", self._minimize)
        
        self.current_cursor = ARROW_CURSOR
        pygame.mouse.set_cursor(self.current_cursor)

    def add_button(self, text: str, on_click: Optional[Callable] = None) -> Button:
        btn = Button(pygame.Rect(0, 0, 1, 1), text, on_click)
        self.layout.add_widget(btn)
        return btn
        
    def add_checkbox(self, text: str, on_change: Optional[Callable] = None) -> Checkbox:
        chk = Checkbox(pygame.Rect(0, 0, 1, 1), text=text, on_change=on_change)
        self.layout.add_widget(chk)
        return chk

    def add_slider(self, text: str, min_val: float, max_val: float, value: float, on_change: Optional[Callable] = None) -> Slider:
        s = Slider(pygame.Rect(0, 0, 1, 1), text, min_val, max_val, value, on_change=on_change)
        self.layout.add_widget(s)
        return s

    def add_textinput(self, text: str = "", on_change: Optional[Callable] = None) -> TextInput:
        t = TextInput(pygame.Rect(0, 0, 1, 1), text=text, on_change=on_change)
        self.layout.add_widget(t)
        return t

    def add_info(self, text: str, value_provider: Callable) -> Info:
        info = Info(pygame.Rect(0, 0, 1, 1), text, value_provider)
        self.layout.add_widget(info)
        return info

    def _close(self): self.visible = not self.visible
    def _minimize(self): self.minimized = not self.minimized

    def clamp_to_screen(self):
        surf = pygame.display.get_surface()
        if surf is None: return
        self.rect.width = max(self.min_width, self.rect.width)
        self.rect.height = max(self.min_height, self.rect.height)
        self.rect.clamp_ip(surf.get_rect())

    def calculate_Resize_Border(self):
        r, margin = self.rect, self.resize_margin
        off_set = self.resize_margin // 2
        return {
            'nw': pygame.Rect(r.x - off_set, r.y - off_set, margin, margin), 'ne': pygame.Rect(r.right - margin + off_set, r.y - off_set, margin, margin),
            'sw': pygame.Rect(r.x - off_set, r.bottom - margin + off_set, margin, margin), 'se': pygame.Rect(r.right - margin + off_set, r.bottom - margin + off_set, margin, margin),
            'w': pygame.Rect(r.x - off_set, r.y + margin, margin, r.height - 2 * margin), 'e': pygame.Rect(r.right - margin + off_set, r.y + margin, margin, r.height - 2 * margin),
            'n': pygame.Rect(r.x + margin, r.y - off_set, r.width - 2 * margin, margin), 's': pygame.Rect(r.x + margin, r.bottom - margin + off_set, r.width - 2 * margin, margin)
        }

    def handle_event(self, event):
        if not self.visible: return False
        self.header.topleft = self.rect.topleft
        self.header.width = self.rect.width
        if not self.isMain:
            self.close_btn.rect.topleft = (self.rect.right - 32, self.rect.y + 4)
            if self.close_btn.handle_event(event): return True
        self.min_btn.rect.topleft = (self.rect.right - 64, self.rect.y + 4)
        if self.min_btn.handle_event(event): return True
        if self.layout and not self.minimized and self.layout.handle_event(event): return True

        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            mx, my = event.pos
            if not self.minimized:
                for key, margin in self.calculate_Resize_Border().items():
                    if margin.collidepoint(mx, my) and not self.dragging:
                        self.resize_dir, self.resizing, self.offset = key, True, (mx, my)
                        return True
            if self.header.collidepoint(mx, my):
                self.dragging, self.offset = True, (mx - self.rect.x, my - self.rect.y)
                return True
        elif event.type == pygame.MOUSEBUTTONUP and event.button == 1:
            self.dragging, self.resizing, self.resize_dir = False, False, None
        elif event.type == pygame.KEYDOWN and event.key == pygame.K_F1:
            self.D_info = not self.D_info
        elif event.type == pygame.MOUSEMOTION:
            if not self.minimized and not self.resizing:
                margins, cursor_set = self.calculate_Resize_Border(), False
                for key, margin in margins.items():
                    if margin.collidepoint(event.pos):
                        if key in ['nw', 'se']: pygame.mouse.set_cursor(RESIZE_NWSE_CURSOR)
                        elif key in ['ne', 'sw']: pygame.mouse.set_cursor(RESIZE_NESW_CURSOR)
                        elif key in ['n', 's']: pygame.mouse.set_cursor(RESIZE_NS_CURSOR)
                        elif key in ['e', 'w']: pygame.mouse.set_cursor(RESIZE_WE_CURSOR)
                        cursor_set = True
                        break
                if not cursor_set: pygame.mouse.set_cursor(ARROW_CURSOR)
            if self.dragging:
                self.rect.topleft = (event.pos[0] - self.offset[0], event.pos[1] - self.offset[1])
                self.clamp_to_screen()
                return True
            if self.resizing and self.resize_dir:
                mx, my = event.pos
                dx, dy = mx - self.offset[0], my - self.offset[1]
                if 'e' in self.resize_dir: self.rect.width = max(self.min_width, self.rect.width + dx)
                if 's' in self.resize_dir: self.rect.height = max(self.min_height, self.rect.height + dy)
                if 'w' in self.resize_dir:
                    new_w = max(self.min_width, self.rect.width - dx)
                    self.rect.x += self.rect.width - new_w
                    self.rect.width = new_w
                if 'n' in self.resize_dir:
                    new_h = max(self.min_height, self.rect.height - dy)
                    self.rect.y += self.rect.height - new_h
                    self.rect.height = new_h
                self.offset = (mx, my)
                self.clamp_to_screen()
                return True
        return False

    def draw(self, surf):
        if not self.visible: return
        if not self.minimized:
            pygame.draw.rect(surf, CURRENT_THEME.WINDOW_BG, self.rect, border_radius=10)
            pygame.draw.rect(surf, CURRENT_THEME.BORDER, self.rect, 1, border_radius=10)
        header_rect = pygame.Rect(self.rect.x, self.rect.y, self.rect.width, HEADER_HEIGHT)
        pygame.draw.rect(surf, CURRENT_THEME.HEADER, header_rect, border_top_left_radius=10, border_top_right_radius=10)
        title_s = CURRENT_THEME.FONT.render(self.title, True, CURRENT_THEME.TEXT)
        surf.blit(title_s, (self.rect.x + 10, self.rect.y + 3))
        if not self.isMain:
            self.close_btn.rect.topleft = (self.rect.right - 32, self.rect.y + 4)
            self._draw_control_icon(surf, self.close_btn.rect, "close")
        self.min_btn.rect.topleft = (self.rect.right - 64, self.rect.y + 4)
        self._draw_control_icon(surf, self.min_btn.rect, "min")
        
        if not self.minimized:
            self.layout.update_positions(self.rect)
            self.layout.draw(surf)

        if self.D_info:
            self.debug_info(surf)

    def _draw_control_icon(self, surf, rect, kind: str):
        circle_center, circle_radius = rect.center, min(rect.width, rect.height) // 2
        if kind == "close": pygame.draw.circle(surf, (255, 95, 86), circle_center, circle_radius)
        elif kind == "min": pygame.draw.circle(surf, (255, 189, 46), circle_center, circle_radius)

    def debug_info(self, surf):
        if not self.D_info: return
        info = [f"Pos: ({self.rect.x},{self.rect.y}) Size: ({self.rect.width}x{self.rect.height})", f"Dragging: {self.dragging}, Resizing: {self.resizing}, Dir: {self.resize_dir}"]
        for i, line in enumerate(info):
            txt = CURRENT_THEME.SMALL_FONT.render(line, True, (250, 50, 50))
            surf.blit(txt, (self.rect.x + 10, self.rect.bottom - 20 * (i + 1)))
        for margin in self.calculate_Resize_Border().values():
            pygame.draw.rect(surf, (0, 200, 0), margin, 1)

class MasterWindow(Widget):
    """A top-level manager for all Window instances."""
    def __init__(self):
        super().__init__(pygame.Rect(0, 0, 0, 0))
        self.child_windows = {}

    def add_child(self, child_window):
        self.child_windows[child_window.title] = child_window

    def create_ui_from_layout(self, layout):
        """Dynamically creates windows and widgets from a layout definition."""
        for window_data in layout:
            win = Window(x=window_data["x"], y=window_data["y"], w=window_data["width"], h=window_data["height"], title=window_data["title"])
            self.add_child(win)
            for widget_data in window_data.get("widgets", []):
                widget_type = widget_data["type"]
                if widget_type == "button":
                    win.add_button(widget_data["text"], widget_data.get("on_click"))
                elif widget_type == "checkbox":
                    win.add_checkbox(widget_data["text"], widget_data.get("on_change"))
                elif widget_type == "textinput":
                    win.add_textinput(widget_data.get("text", ""), widget_data.get("on_change"))
                elif widget_type == "slider":
                    win.add_slider(widget_data["text"], widget_data["min_val"], widget_data["max_val"], widget_data["value"], widget_data.get("on_change"))
                elif widget_type == "info":
                    win.add_info(widget_data["text"], widget_data["value_provider"])

    def handle_event(self, event):
        """Handles events by passing them to child windows in reverse order (top-most first)."""
        for title, child in reversed(list(self.child_windows.items())):
            if child.handle_event(event):
                self.child_windows.pop(title)
                self.child_windows[title] = child
                return True
        return False

    def draw(self, surf):
        """Draws all child windows."""
        for child in self.child_windows.values():
            child.draw(surf)
