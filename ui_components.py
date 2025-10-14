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
BORDER = (200, 200, 200)
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
        self.clicked = False

    def handle_event(self, event):
        if event.type == pygame.MOUSEMOTION:
            self.hover = self.rect.collidepoint(event.pos)
            # print(f"Button hover: {self.hover}")
        
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
        # Determine color based on state
        if self.clicked:
            color = (190, 190, 200)
        elif self.hover:
            color = (230, 230, 250)
        else:
            color = (245, 245, 250)
            
        pygame.draw.rect(surf, color, self.rect, border_radius=8)
        pygame.draw.rect(surf, BORDER, self.rect, 1, border_radius=8)
        txt = FONT.render(self.text, True, TEXT)
        surf.blit(txt, txt.get_rect(center=self.rect.center))

class Checkbox(Widget):
    def __init__(self, rect: pygame.Rect,text: str, on_change: Optional[Callable] = None):
        super().__init__(rect)
        self.checked = False
        self.on_change = on_change
        self.text = text

        # create a text box inside the checkbox for label
        self.txt_rect = pygame.Rect(0,0,10,10)


        # create a small checkbox rect in middle of widget
        self.box_size = 20
        self.box_rect = pygame.Rect(0,0,5,5)
        
    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.box_rect.collidepoint(event.pos):
                self.checked = not self.checked
                if self.on_change:
                    self.on_change(self.checked)
                return True
        return False

    def draw(self, surf):
        # update text rect in case widget was resized
        txt = FONT.render(self.text, True, TEXT)
        surf.blit(txt, txt.get_rect(center=self.rect.center))


        # update box rect in case widget was resized
        self.box_size = min(self.rect.height - 10, 20)
        self.box_rect = pygame.Rect(self.rect.x + 5, self.rect.y + (self.rect.height - self.box_size) // 2, self.box_size, self.box_size)


        pygame.draw.rect(surf, WINDOW_BG, self.box_rect)
        pygame.draw.rect(surf, BORDER, self.box_rect, 2, border_radius=4)
        if self.checked:
            inner = self.box_rect.inflate(-6, -6)
            pygame.draw.rect(surf, ACCENT, inner, border_radius=3)

class Slider(Widget):
    def __init__(self, rect: pygame.Rect, text: str, min_val: float, max_val: float, value: float, on_change: Optional[Callable] = None):
        super().__init__(rect)
        self.min_val = min_val
        self.max_val = max_val
        self.value = value
        self.on_change = on_change
        self.dragging = False
        self.text = text   

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
        track_rect = pygame.Rect(self.rect.x + 8, self.rect.centery + 8, self.rect.width - 16, 8)
        pygame.draw.rect(surf, (235, 235, 240), track_rect, border_radius=4)
        # fill
        fill_w = int((self.value - self.min_val) / (self.max_val - self.min_val) * track_rect.width)
        if fill_w > 0:
            pygame.draw.rect(surf, ACCENT, (track_rect.x, track_rect.y, fill_w, track_rect.height), border_radius=4)
        # knob
        kx = self._value_to_pos()
        knob = pygame.Rect(kx - 8, track_rect.centery - 8 , 16, 16)
        pygame.draw.rect(surf, WINDOW_BG, knob, border_radius=8)
        pygame.draw.rect(surf, BORDER, knob, 1, border_radius=8)
        # value label
        val_txt = SMALL_FONT.render(f"{self.text} : {self.value:.2f}", True, SUBTEXT)
        surf.blit(val_txt, (self.rect.x + 8, self.rect.centery-(val_txt.get_height() / 2)-8))

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

# Final Window class 
class Window(Widget):
    def __init__(self, x ,y,w,h, title: str = "Window"):
        self.rect = pygame.Rect(x, y, w, h)
        self.title = title
        self.visible = True
        self.minimized = False
        self.dragging = False
        self.offset = (0, 0)
        self.z = 0
        self.widgets = []
        self.resizing = False
        self.resize_dir = None  # 'n','s','e','w','ne','nw','se','sw'
        self.min_width = 200
        self.min_height = 100
        self.resize_margin = 5
        self.Grid = (5,2)
        self.padding = 5
        self._parent_master = None
        self.isMain = False

        # control buttons
        if not self.isMain:
            self.close_btn = Button(pygame.Rect(0, 0, 28, 20), "X", self._close)
        self.min_btn = Button(pygame.Rect(0, 0, 28, 20), "_", self._minimize)

        # add grid layout
        self.layout = GridLayout(pygame.Rect(x, y, self.rect.width, self.rect.height ), self.Grid[0], self.Grid[1], self.padding)
 
    def add(self, widget: Widget):
        # not needed anymore, kept for reference
        # store widget's rect relative to window origin
        rel_x = widget.rect.x - self.rect.x
        rel_y = widget.rect.y - self.rect.y
        widget._relative_rect = pygame.Rect(rel_x, rel_y, widget.rect.width, widget.rect.height)
        self.widgets.append(widget)

    # Add to grid layout
    def add_button(self, row: int, col: int, text: str, on_click: Optional[Callable] = None) -> Button:
        # initialy making a dummy rect, will be updated by layout
        btn = Button(pygame.Rect(0,0,1,1), text, on_click)
        self.layout.add_widget(btn,row,col)
        print(f"on_click: {on_click}")
        return btn
        
    def add_checkbox(self, row: int, col: int, text: str, on_change: Optional[Callable] = None) -> Checkbox:
        chk = Checkbox(pygame.Rect(0, 0, 1, 1), text=text, on_change=on_change)
        self.layout.add_widget(chk, row, col)
        return chk

    def add_slider(self, row: int, col: int, text: str, min_val: float, max_val: float, value: float, on_change: Optional[Callable] = None) -> Slider:
        s = Slider(pygame.Rect(0,0,1,1), text, min_val, max_val, value, on_change=on_change)
        self.layout.add_widget(s, row, col)
        return s

    def add_textinput(self, row: int, col: int, text: str = "", on_change: Optional[Callable] = None) -> TextInput:
        t = TextInput(pygame.Rect(0, 0, 1, 1), text=text, on_change=on_change)
        self.layout.add_widget(t, row, col)
        return t

    def _close(self):
        self.visible = not self.visible
        print(self.visible)

    def _minimize(self):
        self.minimized = not self.minimized

    def clamp_to_screen(self):
        """Ensure the window stays fully inside the pygame display surface."""
        surf = pygame.display.get_surface()
        if surf is None:
            return
        sw, sh = surf.get_size()
        # clamp size
        if self.rect.width > sw:
            self.rect.width = sw
        if self.rect.height > sh:
            self.rect.height = sh
        # clamp position
        self.rect.x = max(0, min(self.rect.x, sw - self.rect.width))
        self.rect.y = max(0, min(self.rect.y, sh - self.rect.height))

    def handle_event(self, event):
        if not self.visible:
            return False
            
        header = pygame.Rect(self.rect.x, self.rect.y, self.rect.width, 28)
        
        # pass event to layout widgets first, so they get priority
        if self.layout and self.layout.handle_event(event):
            return True

        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            mx, my = event.pos
            # 1. Check if the user clicked on a resize border
            r = self.rect
            left_margin = pygame.Rect(r.x, r.y, self.resize_margin, r.height)
            right_margin = pygame.Rect(r.right - self.resize_margin, r.y, self.resize_margin, r.height)
            top_margin = pygame.Rect(r.x, r.y, r.width, self.resize_margin)
            bottom_margin = pygame.Rect(r.x, r.bottom - self.resize_margin, r.width, self.resize_margin)
            
            if left_margin.collidepoint(mx, my): self.resize_dir = 'w'
            elif right_margin.collidepoint(mx, my): self.resize_dir = 'e'
            elif top_margin.collidepoint(mx, my): self.resize_dir = 'n'
            elif bottom_margin.collidepoint(mx, my): self.resize_dir = 's'
            
            if self.resize_dir:
                self.resizing = True
                self.offset = (mx, my)
                return True
                
            # 2. Check if the user clicked on the header for dragging
            if header.collidepoint(mx, my):
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
                self.clamp_to_screen()
                return True
            
            if self.resizing and self.resize_dir:
                mx, my = event.pos
                dx = mx - self.offset[0]
                dy = my - self.offset[1]
                r = self.rect
                
                if 'e' in self.resize_dir:
                    r.width = max(self.min_width, r.width + dx)
                if 's' in self.resize_dir:
                    r.height = max(self.min_height, r.height + dy)
                if 'w' in self.resize_dir:
                    new_x = r.x + dx
                    new_w = max(self.min_width, r.right - new_x)
                    if new_w != r.width:
                        r.x = r.right - new_w
                        r.width = new_w
                if 'n' in self.resize_dir:
                    new_y = r.y + dy
                    new_h = max(self.min_height, r.bottom - new_y)
                    if new_h != r.height:
                        r.y = r.bottom - new_h
                        r.height = new_h
                
                self.offset = (mx, my)
                self.clamp_to_screen()
                return True
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
        header_col = (220, 220, 248) if THEME == "light" else (40, 40, 44)
        pygame.draw.rect(surf, header_col, header, border_radius=10)
        # title
        title_s = FONT.render(self.title, True, text_col)
        surf.blit(title_s, (self.rect.x + 10, self.rect.y + 3))
        # ensure control icon rects are always computed from current rect (prevents lag)
        if not self.isMain:
            if getattr(self, 'show_close', True):
                self.close_btn.rect.topleft = (self.rect.right - 32, self.rect.y + 4)
                self._draw_control_icon(surf, self.close_btn.rect, "close")
        if getattr(self, 'show_min', True):
            self.min_btn.rect.topleft = (self.rect.right - 64, self.rect.y + 4)
            self._draw_control_icon(surf, self.min_btn.rect, "min")

        # update layout rect to match window size
        self.layout.update_positions(self.rect)

        if not self.minimized:
            # draw resize grip
            grip_rect = pygame.Rect(self.rect.right - 12, self.rect.bottom - 12, 10, 10)
            pygame.draw.rect(surf, (200, 200, 200), grip_rect)

            # draw Widget using layout
            self.layout.draw(surf)

    def _draw_control_icon(self, surf, rect, kind: str):
        # background
        # Calculate the circle's center and radius from the rect
        circle_center = rect.center
        circle_radius = min(rect.width, rect.height) // 2
        # pygame.draw.rect(surf, WINDOW_BG if THEME == "light" else DARK_WINDOW_BG, rect, border_radius=6)
        # pygame.draw.rect(surf, BORDER if THEME == "light" else (60, 60, 65), rect, 1, border_radius=6)
        # cx = rect.centerx
        # cy = rect.centery
        if kind == "close":
            pygame.draw.circle(surf, (255,0,0), circle_center, circle_radius) 
        elif kind == "min":
            pygame.draw.circle(surf, (255,234,0), circle_center, circle_radius)

# Grid Layout Manager
class GridLayout:
    def __init__(self, rect, rows, cols, padding=0):
        self.rect = rect
        self.rows = rows
        self.cols = cols
        self.padding = padding
        self.widgets = {} # Use a dictionary to store widgets by their row and column

    def add_widget(self, widget, row, col):
        if (row, col) in self.widgets:
            print(f"Warning: A widget already exists at row {row}, col {col}")
        self.widgets[(row, col)] = widget

    def update_positions(self,Rect=None):
        # print(f"Drawing GridLayout at {self.rect} with {self.rows} rows and {self.cols} cols")

        # update layout rect to match parent window size 
        # NOTE: We have to consider header height (28px) and some margin
        if Rect is not None:
            self.rect = pygame.Rect(Rect.x, Rect.y + 28, Rect.width, Rect.height - 28)

        # Calculate cell dimensions
        cell_width = self.rect.width / self.cols
        cell_height = self.rect.height / self.rows

        for (row, col), widget in self.widgets.items():
            # Calculate the top-left position for the widget
            x = self.rect.x + col * cell_width + self.padding
            y = self.rect.y + row * cell_height + self.padding

            # Calculate the widget's new dimensions
            width = cell_width - 2 * self.padding
            height = cell_height - 2 * self.padding

            # Update the widget's rect
            widget.rect = pygame.Rect(x, y, width, height)

    def handle_event(self, event):
        # Pass the event to each widget
        for widget in self.widgets.values():
            if widget.handle_event(event):
                # If a widget handles the event, stop processing and return True
                return True
        return False

    def draw(self, surf):
        # First, make sure widget positions are up to date
        self.update_positions()

        pygame.draw.rect(surf, (240, 240, 245), self.rect,1)

        # Draw a visual grid for debugging purposes (optional)
        cell_width = self.rect.width / self.cols
        cell_height = self.rect.height / self.rows
        for row in range(self.rows):
            for col in range(self.cols):
                x = self.rect.x + col * cell_width
                y = self.rect.y + row * cell_height
                pygame.draw.rect(surf, (50, 50, 50), pygame.Rect(x, y, cell_width, cell_height), 1)

        # Draw each widget
        for widget in self.widgets.values():
            widget.draw(surf)

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

# Master Window Manager
class MasterWindow(Window):
    def __init__(self,x , y, w, h, title: str = "Master Window"):
        super().__init__(x, y, w, h, title)
        self.child_windows = []
        self.isMain = True

    def add_child(self, child_window):
        # Set a reference to the parent for z-ordering
        child_window._parent_master = self
        self.child_windows.append(child_window)

    def handle_event(self, event):
        # We handle events for the master window first
        super().handle_event(event)
        
        # Then, we iterate through children in reverse for z-ordering
        for child in reversed(self.child_windows):
            if child.handle_event(event):
                # If a child window handled the event, we stop.
                # This ensures clicks go to the top window.
                return True
        return False

    def draw(self, surf):
        # First draw the master window itself
        super().draw(surf)
        
        # Then, draw all child windows
        for child in self.child_windows:
            child.draw(surf)






