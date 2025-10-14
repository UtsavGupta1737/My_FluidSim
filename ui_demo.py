import pygame
from ui_components import Window

pygame.init()
SCREEN = pygame.display.set_mode((900, 600))
pygame.display.set_caption("UI Demo")
clock = pygame.time.Clock()
FPS = 60
font = pygame.font.SysFont("Arial", 18)

# Create a sample window
win = Window(50, 50, 400, 300, title="Main Window")
win2 = Window(500, 50, 400, 300, title="Window 2")
win.add_button(0,0, "Click Me", win2._close)
win.add_button(0,1, "Don't Click Me", win2._close)
win.add_checkbox(1,0, "Tick Me")
win.add_checkbox(1,1, "Don't Tick Me")
win.add_slider(2,0, "Volume", 0, 100, 50)
win.add_slider(2,1, "Brightness", 0, 100, 50)
win.add_textinput(3,0, "Name")
win.add_textinput(3,1, "Age")


running = True
while running:
    dt = clock.tick(FPS) / 1000.0
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        else:
            win.handle_event(event)
            win2.handle_event(event)
            

    SCREEN.fill((0, 0, 0))

    win.draw(SCREEN)
    win2.draw(SCREEN)

    info = f"FPS: {int(clock.get_fps())} "
    surf = font.render(info, True, (220, 220, 220))
    SCREEN.blit(surf, (10, 600 - 24))
    

    pygame.display.flip()

pygame.quit()

