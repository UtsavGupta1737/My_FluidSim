import pygame
from ui_components import Window, Button, Slider, Checkbox, TextInput

pygame.init()
SCREEN = pygame.display.set_mode((900, 600))
pygame.display.set_caption("UI Demo")
clock = pygame.time.Clock()

# Create a sample window
win = Window(pygame.Rect(50, 50, 420, 300), "Settings")
# Add widgets using the Window helpers (x,y are relative to the window client area)
btn = win.add_button(20, 60, 120, 36, "Apply", lambda: print("Apply clicked"))
chk = win.add_checkbox(20, 110, 20, 20, checked=True, on_change=lambda v: print("Checked", v))
sld = win.add_slider(20, 150, 220, 30, 0, 100, 50, on_change=lambda v: print("Slider", v))
txt = win.add_textinput(20, 190, 200, 30, text="Hello")

running = True
while running:
    dt = clock.tick(60) / 1000.0
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        else:
            win.handle_event(event)

    SCREEN.fill((240, 240, 245))
    win.draw(SCREEN)

    pygame.display.flip()

pygame.quit()
