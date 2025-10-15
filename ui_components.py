import pygame
from typing import Tuple, Callable, Optional

pygame.init()

CURRENT_THEME = None


# define some system cursors
RESIZE_NWSE_CURSOR = pygame.cursors.Cursor(pygame.SYSTEM_CURSOR_SIZENWSE)
RESIZE_NESW_CURSOR = pygame.cursors.Cursor(pygame.SYSTEM_CURSOR_SIZENESW)
RESIZE_NS_CURSOR = pygame.cursors.Cursor(pygame.SYSTEM_CURSOR_SIZENS)
RESIZE_WE_CURSOR = pygame.cursors.Cursor(pygame.SYSTEM_CURSOR_SIZEWE)
ARROW_CURSOR = pygame.cursors.Cursor(pygame.SYSTEM_CURSOR_ARROW)


class Theme:
    def __init__(self, **kwargs):
        self.__dict__.update(kwargs)

THEMES = {
    "light": Theme(
        WINDOW_BG=(255, 255, 255), TEXT=(0, 0, 0), SUBTEXT=(102, 102, 102),
        BORDER=(179, 179, 179), ACCENT=(0, 120, 215), HEADER=(176, 176, 176),
        FONT = pygame.font.SysFont("Arial", 16),
        SMALL_FONT = pygame.font.SysFont("Arial", 14)
    ),
    "dark": Theme(
        WINDOW_BG=(40, 40, 44), TEXT=(220, 220, 230), SUBTEXT=(153, 153, 163),
        BORDER=(60, 60, 65), ACCENT=(10, 130, 255), HEADER=(60, 60, 65),
        FONT = pygame.font.SysFont("Arial", 16),
        SMALL_FONT = pygame.font.SysFont("Arial", 14)
    )
}

def set_theme(name: str = None):
    global CURRENT_THEME
    if name in ["light", "dark"]:
        CURRENT_THEME = THEMES[name]
    else:
        # Toggle theme
        if CURRENT_THEME == THEMES["light"]:
            CURRENT_THEME = THEMES["dark"]
        else:
            CURRENT_THEME = THEMES["light"]
         
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
            color = CURRENT_THEME.ACCENT
        elif self.hover:
            color = CURRENT_THEME.BORDER
        else:
            color = CURRENT_THEME.WINDOW_BG

        pygame.draw.rect(surf, color, self.rect, border_radius=6)
        pygame.draw.rect(surf, CURRENT_THEME.BORDER, self.rect, 1, border_radius=6)
        txt = CURRENT_THEME.FONT.render(self.text, True, CURRENT_THEME.TEXT)
        surf.blit(txt, txt.get_rect(center=self.rect.center))

class Checkbox(Widget):
    def __init__(self, rect: pygame.Rect,text: str, on_change: Optional[Callable] = None):
        super().__init__(rect)
        self.checked = False
        self.on_change = on_change
        self.text = text
        self.hover = False

        # create a text box inside the checkbox for label
        self.txt_rect = pygame.Rect(0,0,10,10)


        # create a small checkbox rect in middle of widget
        self.box_size = 20
        self.box_rect = pygame.Rect(0,0,5,5)
        
    def handle_event(self, event):
        if event.type == pygame.MOUSEMOTION:
            self.hover = self.box_rect.collidepoint(event.pos)

        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.box_rect.collidepoint(event.pos):
                self.checked = not self.checked
                if self.on_change:
                    self.on_change(self.checked)
                return True
        return False

    def draw(self, surf):
        # update text rect in case widget was resized
        txt = CURRENT_THEME.FONT.render(self.text, True, CURRENT_THEME.TEXT)
        surf.blit(txt, txt.get_rect(center=self.rect.center))


        # update box rect in case widget was resized
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
    def __init__(self, rect: pygame.Rect, text: str, min_val: float, max_val: float, value: float, on_change: Optional[Callable] = None):
        super().__init__(rect)
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
                if self.on_change:
                    self.on_change(self.value)
                return True
        elif event.type == pygame.MOUSEBUTTONUP and event.button == 1:
            if self.dragging:
                self.dragging = False
                return True
        elif event.type == pygame.MOUSEMOTION:
            self.hover = self.rect.collidepoint(event.pos)
            
            if self.dragging:
                self.value = self._pos_to_value(event.pos[0])
                if self.on_change:
                    self.on_change(self.value)
                return True
        return False

    def draw(self, surf):
        # Clip drawing to the widget's rect
        clip_rect = surf.get_clip()
        surf.set_clip(self.rect)

        # Redraw the background
        pygame.draw.rect(surf, CURRENT_THEME.WINDOW_BG, self.rect, border_radius=6)

        # Divide the rect for label and slider
        label_height = self.rect.height // 2
        slider_height = self.rect.height // 2
        label_rect = pygame.Rect(self.rect.x, self.rect.y, self.rect.width, label_height)
        slider_rect = pygame.Rect(self.rect.x, self.rect.y + label_height, self.rect.width, slider_height)

        # Draw the label
        val_txt = CURRENT_THEME.SMALL_FONT.render(f"{self.text} : {self.value:.2f}", True, CURRENT_THEME.TEXT)
        val_txt_rect = val_txt.get_rect(center=label_rect.center)
        surf.blit(val_txt, val_txt_rect)

        # Draw the slider track
        track_height = max(4, min(8, int(slider_rect.height * 0.4)))
        track_y = slider_rect.centery
        track_padding = max(8, int(self.rect.width * 0.1))
        track_rect = pygame.Rect(self.rect.x + track_padding, track_y - track_height // 2, self.rect.width - 2 * track_padding, track_height)
        pygame.draw.rect(surf, CURRENT_THEME.HEADER, track_rect, border_radius=4)

        # Draw the fill
        fill_w = int((self.value - self.min_val) / (self.max_val - self.min_val) * track_rect.width)
        if fill_w > 0:
            pygame.draw.rect(surf, CURRENT_THEME.ACCENT, (track_rect.x, track_rect.y, fill_w, track_rect.height), border_radius=4)

        # Draw the knob
        knob_size = max(8, min(16, track_height * 2))
        kx = self._value_to_pos()
        knob_rect = pygame.Rect(kx - knob_size // 2, track_y - knob_size // 2, knob_size, knob_size)
        pygame.draw.rect(surf, CURRENT_THEME.WINDOW_BG, knob_rect, border_radius=knob_size // 2)
        pygame.draw.rect(surf, CURRENT_THEME.BORDER, knob_rect, 1, border_radius=knob_size // 2)

        # Draw hover effect
        if self.hover or self.dragging:
            pygame.draw.rect(surf, CURRENT_THEME.BORDER, self.rect, 1, border_radius=8)

        # Reset the clipping rectangle
        surf.set_clip(clip_rect)

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
                if self.on_change:
                    self.on_change(self.text)
                return True
            elif event.unicode:
                self.text = self.text[:self.cursor] + event.unicode + self.text[self.cursor:]
                self.cursor += 1
                if self.on_change:
                    self.on_change(self.text)
                return True
        return False

    def draw(self, surf):
        pygame.draw.rect(surf, CURRENT_THEME.WINDOW_BG, self.rect, border_radius=6)
        pygame.draw.rect(surf, CURRENT_THEME.BORDER, self.rect, 1, border_radius=6)
        if self._is_placeholder and self.placeholder:
            txt = CURRENT_THEME.FONT.render(self.placeholder, True, CURRENT_THEME.SUBTEXT)
        else:
            txt = CURRENT_THEME.FONT.render(self.text, True, CURRENT_THEME.TEXT)
        surf.blit(txt, (self.rect.x + 8, self.rect.y + (self.rect.height - txt.get_height()) / 2))
        if self.active:
            # cursor blinking
            self.cursor_timer += 1 / 60.0
            if self.cursor_timer > 0.5:
                self.cursor_visible = not self.cursor_visible
                self.cursor_timer = 0.0
            if self.cursor_visible:
                # compute cursor x
                pre = CURRENT_THEME.FONT.render(self.text[:self.cursor], True, CURRENT_THEME.TEXT)
                cx = self.rect.x + 8 + pre.get_width()
                pygame.draw.line(surf, CURRENT_THEME.TEXT, (cx, self.rect.y + 6), (cx, self.rect.y + self.rect.height - 6), 2)

# Final Window class 
class Window(Widget):
    def __init__(self, x ,y,w,h, title: str = "Window"):
        self.rect = pygame.Rect(x, y, w, h)
        self.header = pygame.Rect(x, y, w, 28)
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
        self.resize_margin = 10
        self.Grid = (5,2)
        self.padding = 5
        self._parent_master = None
        self.isMain = False
        self.D_info = True

        # add grid layout
        self.layout = GridLayout(pygame.Rect(0, 0, 1, 1), self.Grid[0], self.Grid[1], self.padding)

        # control buttons
        if not self.isMain:
            self.close_btn = Button(pygame.Rect(0, 0, 28, 20), "X", self._close)
        self.min_btn = Button(pygame.Rect(0, 0, 28, 20), "_", self._minimize)

        # check if main window (no close button)
        if title == "Main":
            self.isMain = True

        # Cursors
        self.current_cursor = ARROW_CURSOR
        pygame.mouse.set_cursor(self.current_cursor)

    # Add to grid layout
    def add_button(self, row: int, col: int, text: str, on_click: Optional[Callable] = None) -> Button:
        # initialy making a dummy rect, will be updated by layout
        btn = Button(pygame.Rect(0,0,1,1), text, on_click)
        self.layout.add_widget(btn,row,col)
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

    def calculate_Resize_Border(self):
        """Calculate rectangles for resize borders and corners."""
        r = self.rect
        margin = self.resize_margin

        # Corners
        nw_margin = pygame.Rect(r.x, r.y, margin, margin)
        ne_margin = pygame.Rect(r.right - margin, r.y, margin, margin)
        sw_margin = pygame.Rect(r.x, r.bottom - margin, margin, margin)
        se_margin = pygame.Rect(r.right - margin, r.bottom - margin, margin, margin)

        # Sides (excluding corners)
        left_margin = pygame.Rect(r.x, r.y + margin, margin, r.height - 2 * margin)
        right_margin = pygame.Rect(r.right - margin, r.y + margin, margin, r.height - 2 * margin)
        top_margin = pygame.Rect(r.x + margin, r.y, r.width - 2 * margin, margin)
        bottom_margin = pygame.Rect(r.x + margin, r.bottom - margin, r.width - 2 * margin, margin)

        return {
            'nw': nw_margin,
            'ne': ne_margin,
            'sw': sw_margin,
            'se': se_margin,
            'w': left_margin,
            'e': right_margin,
            'n': top_margin,
            's': bottom_margin
        }


    def handle_event(self, event):
        if not self.visible:
            return False
            
        if not self.minimized:
            self.header = pygame.Rect(self.rect.x, self.rect.y, self.rect.width, 28)

        # handle control buttons first
        if not self.isMain:
            self.close_btn.rect.topleft = (self.rect.right - 32, self.rect.y + 4)
            if not self.isMain:
                if self.close_btn.handle_event(event):
                    return True
        self.min_btn.rect.topleft = (self.rect.right - 64, self.rect.y + 4)
        if self.min_btn.handle_event(event):
            return True

        # pass event to layout widgets first, so they get priority
        if self.layout and self.layout.handle_event(event):
            return True

        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            mx, my = event.pos
            # 1. Check if the user clicked on a resize border

            margins = self.calculate_Resize_Border()
            for key, margin in margins.items():
                if margin.collidepoint(mx, my) and not self.dragging:
                    self.resize_dir = key
                    self.resizing = True
                    self.offset = (mx, my)
                    self.clamp_to_screen()                  
                    return True
                
                
            # 2. Check if the user clicked on the header for dragging
            if self.header.collidepoint(mx, my):
                self.dragging = True
                self.offset = (mx - self.rect.x, my - self.rect.y)
                return True

        elif event.type == pygame.MOUSEBUTTONUP and event.button == 1:
            self.dragging = False
            self.resizing = False
            self.resize_dir = None

        elif event.type == pygame.MOUSEMOTION:
            mx, my = event.pos
            # Change cursor if over resize borders   
            margins = self.calculate_Resize_Border()
            for key, margin in margins.items():

                if margin.collidepoint(mx, my) and not self.dragging:
                    if key in ['nw', 'se']:
                        if self.current_cursor != RESIZE_NWSE_CURSOR:
                            pygame.mouse.set_cursor(RESIZE_NWSE_CURSOR)
                            self.current_cursor = RESIZE_NWSE_CURSOR
                    elif key in ['ne', 'sw']:
                        if self.current_cursor != RESIZE_NESW_CURSOR:
                            pygame.mouse.set_cursor(RESIZE_NESW_CURSOR)
                            self.current_cursor = RESIZE_NESW_CURSOR
                    elif key in ['n', 's']:
                        if self.current_cursor != RESIZE_NS_CURSOR:
                            pygame.mouse.set_cursor(RESIZE_NS_CURSOR)
                            self.current_cursor = RESIZE_NS_CURSOR
                    elif key in ['e', 'w']:
                        if self.current_cursor != RESIZE_WE_CURSOR:
                            pygame.mouse.set_cursor(RESIZE_WE_CURSOR)
                            self.current_cursor = RESIZE_WE_CURSOR

                    break
                
                else:
                    if self.current_cursor != ARROW_CURSOR:
                        pygame.mouse.set_cursor(ARROW_CURSOR)
                        self.current_cursor = ARROW_CURSOR

                    

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
        bg = CURRENT_THEME.WINDOW_BG 
        text_col = CURRENT_THEME.TEXT 
        border_col = CURRENT_THEME.BORDER 

        # window body
        if not self.minimized:
            pygame.draw.rect(surf, bg, self.rect, border_radius=10)
            pygame.draw.rect(surf, border_col, self.rect, 1, border_radius=10)
        # header
        header = pygame.Rect(self.rect.x, self.rect.y, self.rect.width, 28)
        header_col = CURRENT_THEME.HEADER
        pygame.draw.rect(surf, header_col, header, border_radius=10)
        # title
        title_s = CURRENT_THEME.FONT.render(self.title, True, text_col)
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
            # draw Widget using layout
            self.layout.draw(surf)

        # debug info
        self.debug_info(surf)

    def _draw_control_icon(self, surf, rect, kind: str):

        # Draw the background circle for the icon
        circle_center = rect.center
        circle_radius = min(rect.width, rect.height) // 2
        
        if kind == "close":
            pygame.draw.circle(surf, (255, 0, 0), circle_center, circle_radius)
            # # Draw the 'X'
            # pygame.draw.line(surf, (255, 255, 255), rect.topleft, rect.bottomright, 2)
            # pygame.draw.line(surf, (255, 255, 255), rect.topright, rect.bottomleft, 2)
        elif kind == "min":
            pygame.draw.circle(surf, (255, 230, 0), circle_center, circle_radius)
            # # Draw the '-'
            # pygame.draw.line(surf, (255, 255, 255), (rect.x + 4, rect.centery), (rect.right - 4, rect.centery), 2)


    def debug_info(self, surf):
        show_margin = True

        if not self.D_info:
            return True
        info = f"Pos: ({self.rect.x},{self.rect.y}) Size: ({self.rect.width}x{self.rect.height})"
        txt = CURRENT_THEME.SMALL_FONT.render(info, True, (200, 0, 0))
        surf.blit(txt, (self.rect.x + 10, self.rect.bottom - 20))

        if show_margin:
            margins = self.calculate_Resize_Border()
            for margin in margins.values():
                pygame.draw.rect(surf, (0, 200, 0), margin, 1)

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

        # pygame.draw.rect(surf, BORDER, self.rect,1)

        # Draw a visual grid for debugging purposes (optional)
        # cell_width = self.rect.width / self.cols
        # cell_height = self.rect.height / self.rows
        # for row in range(self.rows):
        #     for col in range(self.cols):
        #         x = self.rect.x + col * cell_width
        #         y = self.rect.y + row * cell_height
        #         pygame.draw.rect(surf, (50, 50, 50), pygame.Rect(x, y, cell_width, cell_height), 1)

        # Draw each widget
        for widget in self.widgets.values():
            widget.draw(surf)

# Master Window Manager
class MasterWindow(Widget):
    def __init__(self):
        super().__init__(pygame.Rect(0, 0, 0, 0))
        self.child_windows = []

    def add_child(self, child_window):
        # Set a reference to the parent for z-ordering
        child_window._parent_master = self
        self.child_windows.append(child_window)

    def handle_event(self, event):
        # Iterate children from topmost to bottommost (reverse list)
        for child in reversed(self.child_windows):
            # Update child's absolute rect if it has a parent-relative position
            if hasattr(child, '_relative_rect') and getattr(self, 'rect', None) is not None:
                rel = child._relative_rect
                child.rect.x = self.rect.x + rel.x
                child.rect.y = self.rect.y + rel.y
            # Give the child a chance to handle the event. If it does,
            # bring it to front (move to end of list) and stop event propagation.
            if child.handle_event(event):
                try:
                    idx = self.child_windows.index(child)
                    self.child_windows.append(self.child_windows.pop(idx))
                except ValueError:
                    pass
                return True
        return False

    def draw(self, surf):
        
        # Then, draw all child windows
        for child in self.child_windows:
            child.draw(surf)