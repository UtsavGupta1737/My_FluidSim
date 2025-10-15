import pygame
from ui_components import Window, MasterWindow, set_theme

pygame.init()
SCREEN = pygame.display.set_mode((900, 600))
pygame.display.set_caption("UI Demo")
clock = pygame.time.Clock()
FPS = 60
font = pygame.font.SysFont("Arial", 18)

# Create a master window to manage all other windows
master_window = MasterWindow()

# set Theme colors
set_theme("light")

# Create child windows and add them to the master
win = Window(50, 50, 400, 300, title="Window 1")
win2 = Window(500, 50, 400, 300, title="Window 2")

master_window.add_child(win)
master_window.add_child(win2)

# Now, add widgets to the child windows
win.add_button(0, 0, "Click Me",lambda: set_theme())
win.add_button(0, 1, "Click Me", lambda: win2._close())
win.add_checkbox(1, 0, "Tick Me", on_change=lambda v: print(f"Checkbox: {v}"))
win.add_checkbox(1, 1, "Don't Tick Me", on_change=lambda v: print(f"Checkbox: {v}"))
win.add_slider(2, 0, "Volume", 0, 100, 50)
win.add_slider(2, 1, "Brightness", 0, 100, 50)
win.add_textinput(3, 0, "Name", lambda v: print(v))
win.add_textinput(3, 1, "Age", lambda v: print(v))



running = True
while running:
    dt = clock.tick(FPS) / 1000.0
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        else:
            # Only handle events for the master window
            master_window.handle_event(event)
            
    SCREEN.fill((0, 0, 0))

    # Only draw the master window
    master_window.draw(SCREEN)

    info = f"FPS: {int(clock.get_fps())} "
    surf = font.render(info, True, (220, 220, 220))
    SCREEN.blit(surf, (10, 600 - 24))
    
    pygame.display.flip()

pygame.quit()