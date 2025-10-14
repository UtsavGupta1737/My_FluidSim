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
DARK_BG = (18, 18, 20)
DARK_WINDOW_BG = (28, 28, 30)
DARK_TEXT = (230, 230, 230)
THEME = "light"


class Widget:
    def __init__(self, rect: pygame.Rect):
        self.rect = rect
        self.visible = True

    def handle_event(self, event):
        return False
        self.resizing = False
        self.resize_dir = None  # 'n','s','e','w','ne','nw','se','sw'
        self.min_width = 120
        self.min_height = 40

    def draw(self, surf):
        pass


        self.resize_margin = 8

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
    def __init__(self, x ,y,w,h, title: str = "Window"):
        self.rect = pygame.Rect(x, y, w, h)
        self.title = title
        self.visible = True
        self.minimized = False
        self.dragging = False
        self.offset = (0, 0)
        self.widgets = []
        self.isMain = False
        self.resizing = False
        self.resize_dir = None  # 'n','s','e','w','ne','nw','se','sw'
        self.min_width = 200
        self.min_height = 100
        self.resize_margin = 5


        # Check if this window is a Main window
        if self.title.lower() == "main window":
            self.isMain = True

        # control buttons
        if not self.isMain:
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
        if not self.isMain:
            self.close_btn.rect.topleft = (self.rect.right - 32, self.rect.y + 4)
        self.min_btn.rect.topleft = (self.rect.right - 64, self.rect.y + 4)
        # give controls priority so they receive clicks before drag
        if not self.isMain:
            if getattr(self, 'show_close', True):
                if self.close_btn.handle_event(event):
                    return True
        if getattr(self, 'show_min', True):
            if self.min_btn.handle_event(event):
                # print("Minimize button clicked")
                return True

        # if not self.minimized:
        # detect resize start (edges/corners)
        mx, my = None, None
        if event.type in (pygame.MOUSEBUTTONDOWN, pygame.MOUSEMOTION, pygame.MOUSEBUTTONUP):
            mx, my = event.pos
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if not self.minimized:
                # check corners/edges
                r = self.rect
                left = mx - r.x
                top = my - r.y
                right = r.right - mx
                bottom = r.bottom - my
                dir = None
                if left <= self.resize_margin and top <= self.resize_margin:
                    dir = 'nw'
                elif right <= self.resize_margin and top <= self.resize_margin:
                    dir = 'ne'
                elif left <= self.resize_margin and bottom <= self.resize_margin:
                    dir = 'sw'
                elif right <= self.resize_margin and bottom <= self.resize_margin:
                    dir = 'se'
                # elif top <= self.resize_margin:
                #     dir = 'n'
                elif bottom <= self.resize_margin:
                    dir = 's'
                elif left <= self.resize_margin:
                    dir = 'w'
                elif right <= self.resize_margin:
                    dir = 'e'
                if dir:
                    self.resizing = True
                    self.resize_dir = dir
                    self.offset = (mx, my)
                    return True
            if header.collidepoint((mx, my)):
                # start dragging only if not clicking a control
                self.dragging = True
                self.offset = (mx - self.rect.x, my - self.rect.y)
                return True
        elif event.type == pygame.MOUSEBUTTONUP and event.button == 1:
            self.dragging = False
            self.resizing = False
            self.resize_dir = None
        elif event.type == pygame.MOUSEMOTION:
            if self.dragging:
                self.rect.x = event.pos[0] - self.offset[0]
                self.rect.y = event.pos[1] - self.offset[1]
                return True
            if self.resizing and self.resize_dir:
                mx, my = event.pos
                dx = mx - self.offset[0]
                dy = my - self.offset[1]
                r = self.rect
                if 'e' in self.resize_dir:
                    new_w = max(self.min_width, r.width + dx)
                    r.width = new_w
                    self.offset = (mx, self.offset[1])
                if 's' in self.resize_dir:
                    new_h = max(self.min_height, r.height + dy)
                    r.height = new_h
                    self.offset = (self.offset[0], my)
                if 'w' in self.resize_dir:
                    # move left edge
                    new_x = r.x + dx
                    new_w = max(self.min_width, r.right - new_x)
                    if new_w != r.width:
                        r.x = r.right - new_w
                        r.width = new_w
                        self.offset = (mx, self.offset[1])
                # if 'n' in self.resize_dir:
                #     new_y = r.y + dy
                #     new_h = max(self.min_height, r.bottom - new_y)
                #     if new_h != r.height:
                #         r.y = r.bottom - new_h
                #         r.height = new_h
                #         self.offset = (self.offset[0], my)
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
        # select colors per theme
        bg = WINDOW_BG if THEME == "light" else DARK_WINDOW_BG
        text_col = TEXT if THEME == "light" else DARK_TEXT
        border_col = BORDER if THEME == "light" else (50, 50, 55)

        # window body
        if not self.minimized:
            pygame.draw.rect(surf, bg, self.rect, border_radius=10)
            pygame.draw.rect(surf, border_col, self.rect, 1, border_radius=10)
        # header
        header = pygame.Rect(self.rect.x, self.rect.y, self.rect.width, 28)
        header_col = (245, 245, 248) if THEME == "light" else (40, 40, 44)
        pygame.draw.rect(surf, header_col, header, border_radius=10)
        # title
        title_s = FONT.render(self.title, True, text_col)
        surf.blit(title_s, (self.rect.x + 10, self.rect.y + 6))
        # controls (draw icons ourselves for consistent look)
        if not self.isMain:
            if getattr(self, 'show_close', True):
                self._draw_control_icon(surf, self.close_btn.rect, "close")
        if getattr(self, 'show_min', True):
            self._draw_control_icon(surf, self.min_btn.rect, "min")
        if not self.minimized:
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
            # draw resize grip
            grip_rect = pygame.Rect(self.rect.right - 12, self.rect.bottom - 12, 10, 10)
            pygame.draw.rect(surf, (200, 200, 200), grip_rect)

    def _draw_control_icon(self, surf, rect, kind: str):
        # background
        pygame.draw.rect(surf, WINDOW_BG if THEME == "light" else DARK_WINDOW_BG, rect, border_radius=6)
        pygame.draw.rect(surf, BORDER if THEME == "light" else (60, 60, 65), rect, 1, border_radius=6)
        cx = rect.centerx
        cy = rect.centery
        if kind == "close":
            # draw an X
            pygame.draw.line(surf, (200, 60, 60), (cx - 6, cy - 6), (cx + 6, cy + 6), 2)
            pygame.draw.line(surf, (200, 60, 60), (cx + 6, cy - 6), (cx - 6, cy + 6), 2)
        elif kind == "min":
            pygame.draw.line(surf, (100, 100, 110), (cx - 6, cy + 3), (cx + 6, cy + 3), 2)





class MasterWindow(Window):
    """A window that can host other windows as embedded child windows."""
    def __init__(self, rect: pygame.Rect, title: str = "Master", window_class: str = None, class_props: dict = None):
        super().__init__(rect, title)
        self.child_windows = []
        self.managed_windows = []  # list of (window, name, button)
        # master shouldn't be closeable
        self.show_close = False
        # window class and default properties for child windows
        self.window_class = window_class
        self.class_props = class_props or {}

    def add_window(self, window: Window, x: int, y: int):
        # position window relative to master and add to children list
        window.rect.x = self.rect.x + x
        window.rect.y = self.rect.y + y
        # inherit window_class if not set
        if getattr(window, 'window_class', None) is None and self.window_class is not None:
            window.window_class = self.window_class
        # apply class_props defaults where the window doesn't explicitly set them
        for k, v in self.class_props.items():
            if not hasattr(window, k) or getattr(window, k) is None:
                setattr(window, k, v)
        self.child_windows.append(window)

    def manage_window(self, window: Window, name: str):
        """Add a managed window with a toggle button in the master window header area."""
        # create a small button inside master to toggle visibility
        btn_w = 100
        btn_h = 22
        # position buttons stacked from left in the header area
        x_off = 10 + len(self.managed_windows) * (btn_w + 6)
        # button rect (absolute for initial creation)
        btn_rect = pygame.Rect(self.rect.x + x_off, self.rect.y + 4, btn_w, btn_h)
        def toggle(win=window):
            win.visible = not win.visible
            # if making visible, bring to front
            if win.visible and win in self.child_windows:
                try:
                    idx = self.child_windows.index(win)
                    self.child_windows.append(self.child_windows.pop(idx))
                except ValueError:
                    pass

        # create a Button (do not add to master.widgets) and store a relative rect
        btn = Button(btn_rect, name, toggle)
        btn._relative_rect = pygame.Rect(x_off, 4, btn_w, btn_h)
        self.managed_windows.append((window, name, btn))

    def handle_event(self, event):
        if not self.visible:
            return False
        # first, allow managed buttons to handle events
        for _, _, btn in self.managed_windows:
            # compute absolute rect for button based on master position
            rel = btn._relative_rect
            abs_rect = pygame.Rect(self.rect.x + rel.x, self.rect.y + rel.y, rel.width, rel.height)
            orig = btn.rect
            btn.rect = abs_rect
            try:
                if btn.handle_event(event):
                    return True
            finally:
                btn.rect = orig

        # translate event coordinates into child window space and forward
        for cw in reversed(self.child_windows):
            if cw.handle_event(event):
                # bring clicked child to front (z-order) by moving it to end
                try:
                    idx = self.child_windows.index(cw)
                    self.child_windows.append(self.child_windows.pop(idx))
                except ValueError:
                    pass
                return True
        # fallback to normal window behavior
        return super().handle_event(event)

    def draw(self, surf):
        # draw master body and then draw child windows clipped inside
        super().draw(surf)
        # draw managed buttons at top-left area
        for _, _, btn in self.managed_windows:
            # draw using relative rect (translate)
            orig = btn.rect
            btn.rect = pygame.Rect(self.rect.x + btn._relative_rect.x, self.rect.y + btn._relative_rect.y, btn._relative_rect.width, btn._relative_rect.height)
            try:
                btn.draw(surf)
            finally:
                btn.rect = orig
        for cw in self.child_windows:
            cw.draw(surf)


def set_theme(name: str):
    global THEME, WINDOW_BG, TEXT
    if name not in ("light", "dark"):
        return
    THEME = name
    if THEME == "dark":
        WINDOW_BG = DARK_WINDOW_BG
        TEXT = DARK_TEXT
    else:
        WINDOW_BG = (255, 255, 255)
        TEXT = (30, 30, 30)
