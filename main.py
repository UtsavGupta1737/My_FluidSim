import pygame
import random
import math
from dataclasses import dataclass, asdict
from typing import List, Tuple

# Import the UI components and the theme setup from the other files
from ui_components import set_theme, MasterWindow, Window


# Configuration
WIDTH, HEIGHT = 1000, 700
BG_COLOR = (30, 30, 40)
FPS = 60

pygame.init()
set_theme("dark")

@dataclass(eq=False)
class Ball:
    x: float
    y: float
    vx: float
    vy: float
    radius: int
    mass: float
    color: Tuple[int, int, int]

    def to_dict(self):
        return asdict(self)

    def __hash__(self):
        return id(self)

    def __eq__(self, other):
        return self is other


def random_ball(width, height):
    radius = random.randint(8, 24)
    x = random.uniform(radius, width - radius)
    y = random.uniform(radius, height - radius)
    vx = random.uniform(-200, 200) / 60.0
    vy = random.uniform(-200, 200) / 60.0
    mass = math.pi * radius * radius
    color = tuple(random.randint(50, 255) for _ in range(3))
    return Ball(x, y, vx, vy, radius, mass, color)


def resolve_wall_collision(ball: Ball, width, height):
    if ball.x - ball.radius < 0:
        ball.x = ball.radius
        ball.vx *= -1
    if ball.x + ball.radius > width:
        ball.x = width - ball.radius
        ball.vx *= -1
    if ball.y - ball.radius < 0:
        ball.y = ball.radius
        ball.vy *= -1
    if ball.y + ball.radius > height:
        ball.y = height - ball.radius
        ball.vy *= -1


class Grid:
    def __init__(self, width, height, cell_size):
        self.width = width
        self.height = height
        self.cell_size = cell_size
        self.cols = int(math.ceil(width / cell_size))
        self.rows = int(math.ceil(height / cell_size))
        self.cells = [[] for _ in range(self.cols * self.rows)]

    def clear(self):
        for cell in self.cells:
            cell.clear()

    def add(self, ball: Ball):
        min_x = int(max(0, (ball.x - ball.radius) / self.cell_size))
        max_x = int(min(self.cols - 1, (ball.x + ball.radius) / self.cell_size))
        min_y = int(max(0, (ball.y - ball.radius) / self.cell_size))
        max_y = int(min(self.rows - 1, (ball.y + ball.radius) / self.cell_size))

        for y in range(min_y, max_y + 1):
            for x in range(min_x, max_x + 1):
                self.cells[y * self.cols + x].append(ball)

    def get_nearby(self, ball: Ball) -> List[Ball]:
        min_x = int(max(0, (ball.x - ball.radius) / self.cell_size))
        max_x = int(min(self.cols - 1, (ball.x + ball.radius) / self.cell_size))
        min_y = int(max(0, (ball.y - ball.radius) / self.cell_size))
        max_y = int(min(self.rows - 1, (ball.y + ball.radius) / self.cell_size))

        nearby_balls = set()
        for y in range(min_y, max_y + 1):
            for x in range(min_x, max_x + 1):
                for b in self.cells[y * self.cols + x]:
                    nearby_balls.add(b)
        return list(nearby_balls)


def resolve_ball_collision(a: Ball, b: Ball):
    dx = b.x - a.x
    dy = b.y - a.y
    dist = math.hypot(dx, dy)
    if dist == 0:
        # jitter to avoid overlap exactly
        dist = 0.01
        dx = 0.01
    overlap = a.radius + b.radius - dist
    if overlap > 0:
        # push apart proportionally to mass
        push_x = dx / dist * overlap
        push_y = dy / dist * overlap
        total_mass = a.mass + b.mass
        a.x -= push_x * (b.mass / total_mass)
        a.y -= push_y * (b.mass / total_mass)
        b.x += push_x * (a.mass / total_mass)
        b.y += push_y * (a.mass / total_mass)

        # relative velocity
        nx = dx / dist
        ny = dy / dist
        dvx = b.vx - a.vx
        dvy = b.vy - a.vy
        rel_vel = dvx * nx + dvy * ny
        if rel_vel > 0:
            return
        # elastic collision impulse
        impulse = (2 * rel_vel) / (1/a.mass + 1/b.mass)
        a.vx += (impulse * nx) / a.mass
        a.vy += (impulse * ny) / a.mass
        b.vx -= (impulse * nx) / b.mass
        b.vy -= (impulse * ny) / b.mass


font = pygame.font.SysFont("Arial", 18)
clock = None  # will be set in main()   



def draw_ui(screen, balls, paused):
    info = f"Balls: {len(balls)} | {'Paused' if paused else 'Running'} | FPS: {int(clock.get_fps())}"
    surf = font.render(info, True, (220, 220, 220))
    screen.blit(surf, (10, HEIGHT - 24))

    hint = "LeftClick: add | RightClick: remove | Space: pause | Esc: exit"
    surf2 = font.render(hint, True, (180, 180, 180))
    screen.blit(surf2, (10, HEIGHT - 44))


def main():
    global clock, WIDTH, HEIGHT
    screen = pygame.display.set_mode((WIDTH, HEIGHT), pygame.RESIZABLE)
    pygame.display.set_caption("Ball Collision Simulation")
    clock = pygame.time.Clock()

    # Create the master UI window   
    master_window = MasterWindow()

    # Create the controls window
    controls_win = Window(10, 40, 250, 200, title="Main")
    master_window.add_child(controls_win)

    balls: List[Ball] = [random_ball(WIDTH, HEIGHT) for _ in range(12)]

    def on_ball_count_change(new_count_str):
        try:
            new_count = int(new_count_str)
            current_count = len(balls)
            if new_count > current_count:
                for _ in range(new_count - current_count):
                    balls.append(random_ball(WIDTH, HEIGHT))
            elif new_count < current_count:
                for _ in range(current_count - new_count):
                    if balls:
                        balls.pop()
        except ValueError:
            # Handle cases where the input is not a valid integer
            pass
    
    # Add a button to add balls
    controls_win.add_button(0, 0, "Add Ball", on_click=lambda: balls.append(random_ball(WIDTH, HEIGHT)))
    controls_win.add_button(4, 0, "Quit", on_click=lambda: pygame.event.post(pygame.event.Event(pygame.QUIT)))
    
    paused = False
    dragging = False
    drag_start_pos = None

    # Add a text input to control the number of balls
    controls_win.add_textinput(1, 0, "Ball Count", on_change=on_ball_count_change)
    
    # Set the theme
    set_theme("dark")

    grid = Grid(WIDTH, HEIGHT, 50)  # cell size of 50

    running = True
    while running:
        dt = clock.tick(FPS) / 1000.0
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif master_window.handle_event(event):
                pass  # event handled by UI
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:  # left -> start drag
                    dragging = True
                    drag_start_pos = event.pos
                elif event.button == 3:  # right -> remove nearest
                    mx, my = pygame.mouse.get_pos()
                    if balls:
                        nearest = min(balls, key=lambda bb: (bb.x - mx) ** 2 + (bb.y - my) ** 2)
                        balls.remove(nearest)
            elif event.type == pygame.MOUSEBUTTONUP:
                if event.button == 1 and dragging:
                    dragging = False
                    drag_end_pos = event.pos
                    
                    # calculate velocity based on drag vector
                    dx = drag_end_pos[0] - drag_start_pos[0]
                    dy = drag_end_pos[1] - drag_start_pos[1]

                    # create a new ball
                    b = random_ball(WIDTH, HEIGHT)
                    b.x, b.y = drag_start_pos
                    b.vx = dx * 0.1
                    b.vy = dy * 0.1
                    balls.append(b)
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    paused = not paused
                elif event.key == pygame.K_ESCAPE:
                    running = False

            

        if not paused:
            # integrate
            for b in balls:
                b.x += b.vx * dt * 60
                b.y += b.vy * dt * 60
                # damping
                b.vx *= 0.999
                b.vy *= 0.999

            # collisions
            grid.clear()
            for ball in balls:
                grid.add(ball)

            for ball in balls:
                nearby_balls = grid.get_nearby(ball)
                for other in nearby_balls:
                    if id(ball) < id(other):
                        resolve_ball_collision(ball, other)

            for b in balls:
                resolve_wall_collision(b, WIDTH, HEIGHT)

        screen.fill(BG_COLOR)
        for b in balls:
            pygame.draw.circle(screen, b.color, (int(b.x), int(b.y)), b.radius)
            # velocity vector
            vx = int(b.vx * 8)
            vy = int(b.vy * 8)
            pygame.draw.line(screen, (255, 255, 255), (int(b.x), int(b.y)), (int(b.x + vx), int(b.y + vy)), 1)

        if dragging:
            current_pos = pygame.mouse.get_pos()
            pygame.draw.line(screen, (255, 255, 255), drag_start_pos, current_pos, 2)

        draw_ui(screen, balls, paused)
        master_window.draw(screen)
        pygame.display.flip()

    pygame.quit()


if __name__ == "__main__":
    main()
