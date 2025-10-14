import pygame
from ui_components import Window, Button, Slider, Checkbox, TextInput, MasterWindow, set_theme

pygame.init()
SCREEN = pygame.display.set_mode((900, 600))
pygame.display.set_caption("UI Demo")
clock = pygame.time.Clock()

# Create a sample window
win = Window(50, 50, 400, 300, title="Main Window")
# win2 = Window(100, 50, 400, 300, title="Window 2")


running = True
while running:
    dt = clock.tick(60) / 1000.0
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        else:
            win.handle_event(event)
            # win2.handle_event(event)
            

    SCREEN.fill((0, 0, 0))

    win.draw(SCREEN)
    # win2.draw(SCREEN)
    

    pygame.display.flip()

pygame.quit()

