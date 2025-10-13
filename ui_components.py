import pygame
from typing import Tuple, Callable, Optional

pygame.init()
FONT = pygame.font.SysFont("Segoe UI", 16)
SMALL_FONT = pygame.font.SysFont("Segoe UI", 14)

# Basic colors inspired by Win11 soft palette
BG = (243, 244, 246)
WINDOW_BG = (255, 255, 255)
ACCENT = (79, 70, 229)
TEXT = (30, 30, 30)
SUBTEXT = (100, 100, 110)
BORDER = (220, 220, 225)


class Widget:
    def __init__(self, rect: pygame.Rect):
        self.rect = rect
        self.visible = True

    def handle_event(self, event):
        return False

    def draw(self, surf):
        pass


class Button(Widget):
    def __init__(self, rect: pygame.Rect, text: str, on_click: Optional[Callable] = None):
        super().__init__(rect)
        self.text = text
        self.on_click = on_click
        self.hover = False

    def handle_event(self, event):
        if event.type == pygame.MOUSEMOTION:
            self.hover = self.rect.collidepoint(event.pos)
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.rect.collidepoint(event.pos):
                if self.on_click:
                    self.on_click()
                return True
        return False

    def draw(self, surf):
        color = (230, 230, 250) if self.hover else (245, 245, 250)
        pygame.draw.rect(surf, color, self.rect, border_radius=8)
        pygame.draw.rect(surf, BORDER, self.rect, 1, border_radius=8)
        txt = FONT.render(self.text, True, TEXT)
        surf.blit(txt, txt.get_rect(center=self.rect.center))


class Checkbox(Widget):
    def __init__(self, rect: pygame.Rect, checked=False, on_change: Optional[Callable] = None):
        super().__init__(rect)
        self.checked = checked
        self.on_change = on_change

    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.rect.collidepoint(event.pos):
                self.checked = not self.checked
                if self.on_change:
                    self.on_change(self.checked)
                return True
        return False

    def draw(self, surf):
        pygame.draw.rect(surf, WINDOW_BG, self.rect)
        pygame.draw.rect(surf, BORDER, self.rect, 1, border_radius=4)
        if self.checked:
            inner = self.rect.inflate(-6, -6)
            pygame.draw.rect(surf, ACCENT, inner, border_radius=3)


class Slider(Widget):
    def __init__(self, rect: pygame.Rect, min_val: float, max_val: float, value: float, on_change: Optional[Callable] = None):
        super().__init__(rect)
        self.min_val = min_val
        self.max_val = max_val
        self.value = value
        self.on_change = on_change
        self.dragging = False

    def _value_to_pos(self):
        ratio = (self.value - self.min_val) / (self.max_val - self.min_val)
        return int(self.rect.x + 8 + ratio * (self.rect.width - 16))

    def _pos_to_value(self, x):
        ratio = (x - (self.rect.x + 8)) / (self.rect.width - 16)
        ratio = max(0.0, min(1.0, ratio))
        return self.min_val + ratio * (self.max_val - self.min_val)

    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.rect.collidepoint(event.pos):
                self.dragging = True
                self.value = self._pos_to_value(event.pos[0])
                if self.on_change:
                    self.on_change(self.value)
                return True
        elif event.type == pygame.MOUSEBUTTONUP and event.button == 1:
            if self.dragging:
                self.dragging = False
                return True
        elif event.type == pygame.MOUSEMOTION:
            if self.dragging:
                self.value = self._pos_to_value(event.pos[0])
                if self.on_change:
                    self.on_change(self.value)
                return True
        return False

    def draw(self, surf):
        # track
        track_rect = pygame.Rect(self.rect.x + 8, self.rect.centery - 4, self.rect.width - 16, 8)
        pygame.draw.rect(surf, (235, 235, 240), track_rect, border_radius=4)
        # fill
        fill_w = int((self.value - self.min_val) / (self.max_val - self.min_val) * track_rect.width)
        if fill_w > 0:
            pygame.draw.rect(surf, ACCENT, (track_rect.x, track_rect.y, fill_w, track_rect.height), border_radius=4)
        # knob
        kx = self._value_to_pos()
        knob = pygame.Rect(kx - 8, self.rect.centery - 12, 16, 24)
        pygame.draw.rect(surf, WINDOW_BG, knob, border_radius=8)
        pygame.draw.rect(surf, BORDER, knob, 1, border_radius=8)
        # value label
        val_txt = SMALL_FONT.render(f"{self.value:.2f}", True, SUBTEXT)
        surf.blit(val_txt, (self.rect.right + 8, self.rect.centery - val_txt.get_height() / 2))


class TextInput(Widget):
    def __init__(self, rect: pygame.Rect, text: str = "", on_change: Optional[Callable] = None):
        super().__init__(rect)
        # treat initial text as a placeholder until user types
        self.placeholder = text
        self.text = "" if text else text
        self._is_placeholder = True if text else False
        self.active = False
        self.on_change = on_change
        self.cursor = 0
        self.cursor_visible = True
        self.cursor_timer = 0.0

    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            self.active = self.rect.collidepoint(event.pos)
            # if activating and we had a placeholder, position cursor at end
            if self.active and self._is_placeholder:
                self.text = ""
                self._is_placeholder = False
                self.cursor = 0
            return self.active
        if not self.active:
            return False
        if event.type == pygame.KEYDOWN:
            # if we had placeholder and user started typing with a non-special key, clear it
            if self._is_placeholder and event.unicode:
                self.text = ""
                self._is_placeholder = False
                self.cursor = 0
            if event.key == pygame.K_BACKSPACE:
                if self.cursor > 0:
                    self.text = self.text[:self.cursor - 1] + self.text[self.cursor:]
                    self.cursor -= 1
                    if self.on_change:
                        self.on_change(self.text)
                return True
            elif event.key == pygame.K_DELETE:
                self.text = self.text[:self.cursor] + self.text[self.cursor + 1:]
                if self.on_change:
                    self.on_change(self.text)
                return True
            elif event.key == pygame.K_LEFT:
                self.cursor = max(0, self.cursor - 1)
                return True
            elif event.key == pygame.K_RIGHT:
                self.cursor = min(len(self.text), self.cursor + 1)
                return True
            elif event.key == pygame.K_RETURN:
                # lose focus or trigger
                self.active = False
                return True
            elif event.unicode:
                self.text = self.text[:self.cursor] + event.unicode + self.text[self.cursor:]
                self.cursor += 1
                if self.on_change:
                    self.on_change(self.text)
                return True
        return False

    def draw(self, surf):
        pygame.draw.rect(surf, WINDOW_BG, self.rect, border_radius=6)
        pygame.draw.rect(surf, BORDER, self.rect, 1, border_radius=6)
        if self._is_placeholder and self.placeholder:
            txt = FONT.render(self.placeholder, True, SUBTEXT)
        else:
            txt = FONT.render(self.text, True, TEXT)
        surf.blit(txt, (self.rect.x + 8, self.rect.y + (self.rect.height - txt.get_height()) / 2))
        if self.active:
            # cursor blinking
            self.cursor_timer += 1 / 60.0
            if self.cursor_timer > 0.5:
                self.cursor_visible = not self.cursor_visible
                self.cursor_timer = 0.0
            if self.cursor_visible:
                # compute cursor x
                pre = FONT.render(self.text[:self.cursor], True, TEXT)
                cx = self.rect.x + 8 + pre.get_width()
                pygame.draw.line(surf, TEXT, (cx, self.rect.y + 6), (cx, self.rect.y + self.rect.height - 6), 2)


class Window:
    def __init__(self, rect: pygame.Rect, title: str = "Window"):
        self.rect = rect
        self.title = title
        self.visible = True
        self.minimized = False
        self.dragging = False
        self.offset = (0, 0)
        self.widgets = []
        # control buttons
        self.close_btn = Button(pygame.Rect(0, 0, 28, 20), "X", self._close)
        self.min_btn = Button(pygame.Rect(0, 0, 28, 20), "_", self._minimize)

    def add(self, widget: Widget):
        # store widget's rect relative to window origin
        rel_x = widget.rect.x - self.rect.x
        rel_y = widget.rect.y - self.rect.y
        widget._relative_rect = pygame.Rect(rel_x, rel_y, widget.rect.width, widget.rect.height)
        self.widgets.append(widget)

    # convenience factory helpers that create widgets using coordinates relative to the window
    def add_button(self, x: int, y: int, w: int, h: int, text: str, on_click: Optional[Callable] = None) -> Button:
        rect = pygame.Rect(self.rect.x + x, self.rect.y + y, w, h)
        btn = Button(rect, text, on_click)
        self.add(btn)
        return btn

    def add_checkbox(self, x: int, y: int, w: int, h: int, checked: bool = False, on_change: Optional[Callable] = None) -> Checkbox:
        rect = pygame.Rect(self.rect.x + x, self.rect.y + y, w, h)
        chk = Checkbox(rect, checked=checked, on_change=on_change)
        self.add(chk)
        return chk

    def add_slider(self, x: int, y: int, w: int, h: int, min_val: float, max_val: float, value: float, on_change: Optional[Callable] = None) -> Slider:
        rect = pygame.Rect(self.rect.x + x, self.rect.y + y, w, h)
        s = Slider(rect, min_val, max_val, value, on_change=on_change)
        self.add(s)
        return s

    def add_textinput(self, x: int, y: int, w: int, h: int, text: str = "", on_change: Optional[Callable] = None) -> TextInput:
        rect = pygame.Rect(self.rect.x + x, self.rect.y + y, w, h)
        t = TextInput(rect, text=text, on_change=on_change)
        self.add(t)
        return t

    def _close(self):
        self.visible = False

    def _minimize(self):
        self.minimized = not self.minimized

    def handle_event(self, event):
        if not self.visible:
            return False
        # header area
        header = pygame.Rect(self.rect.x, self.rect.y, self.rect.width, 28)
        # place control buttons
        self.close_btn.rect.topleft = (self.rect.right - 32, self.rect.y + 4)
        self.min_btn.rect.topleft = (self.rect.right - 64, self.rect.y + 4)
        # give controls priority so they receive clicks before drag
        if self.close_btn.handle_event(event):
            return True
        if self.min_btn.handle_event(event):
            return True

        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if header.collidepoint(event.pos):
                # start dragging only if not clicking a control
                self.dragging = True
                self.offset = (event.pos[0] - self.rect.x, event.pos[1] - self.rect.y)
                return True
        elif event.type == pygame.MOUSEBUTTONUP and event.button == 1:
            self.dragging = False
        elif event.type == pygame.MOUSEMOTION:
            if self.dragging:
                self.rect.x = event.pos[0] - self.offset[0]
                self.rect.y = event.pos[1] - self.offset[1]
                return True

        if self.minimized:
            return False

        # translate widget events to absolute coords and forward
        for w in self.widgets:
            rel = getattr(w, '_relative_rect', w.rect)
            abs_rect = pygame.Rect(self.rect.x + rel.x, self.rect.y + rel.y, rel.width, rel.height)
            orig = w.rect
            w.rect = abs_rect
            try:
                if w.handle_event(event):
                    return True
            finally:
                w.rect = orig
        return False

    def draw(self, surf):
        if not self.visible:
            return
        # window body
        pygame.draw.rect(surf, WINDOW_BG, self.rect, border_radius=10)
        pygame.draw.rect(surf, BORDER, self.rect, 1, border_radius=10)
        # header
        header = pygame.Rect(self.rect.x, self.rect.y, self.rect.width, 28)
        pygame.draw.rect(surf, (245, 245, 248), header, border_radius=10)
        # title
        title_s = FONT.render(self.title, True, TEXT)
        surf.blit(title_s, (self.rect.x + 10, self.rect.y + 6))
        # controls
        # draw controls (they use absolute rects)
        self.close_btn.draw(surf)
        self.min_btn.draw(surf)
        if self.minimized:
            return
        # draw widgets
        for w in self.widgets:
            rel = getattr(w, '_relative_rect', w.rect)
            abs_rect = pygame.Rect(self.rect.x + rel.x, self.rect.y + rel.y, rel.width, rel.height)
            orig = w.rect
            w.rect = abs_rect
            try:
                w.draw(surf)
            finally:
                w.rect = orig
