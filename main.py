import pygame
import random
import math
from dataclasses import dataclass, asdict
from typing import List, Tuple

# Configuration
WIDTH, HEIGHT = 1000, 700
BG_COLOR = (30, 30, 40)
FPS = 60

pygame.init()
font = pygame.font.SysFont("Arial", 16)

@dataclass
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





def draw_ui(screen, balls, paused):
    info = f"Balls: {len(balls)} | {'Paused' if paused else 'Running'} | FPS: {int(clock.get_fps())}"
    surf = font.render(info, True, (220, 220, 220))
    screen.blit(surf, (10, HEIGHT - 24))

    hint = "LeftClick: add | RightClick: remove | Space: pause"
    surf2 = font.render(hint, True, (180, 180, 180))
    screen.blit(surf2, (10, HEIGHT - 44))


def main():
    global clock
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("Ball Collision Simulation")
    clock = pygame.time.Clock()

    balls: List[Ball] = [random_ball(WIDTH, HEIGHT) for _ in range(12)]
    paused = False

    running = True
    while running:
        dt = clock.tick(FPS) / 1000.0
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.MOUSEBUTTONDOWN:
                mx, my = pygame.mouse.get_pos()
                if event.button == 1:  # left -> add ball at mouse
                    b = random_ball(WIDTH, HEIGHT)
                    b.x, b.y = mx, my
                    balls.append(b)
                elif event.button == 3:  # right -> remove nearest
                    if balls:
                        nearest = min(balls, key=lambda bb: (bb.x - mx) ** 2 + (bb.y - my) ** 2)
                        balls.remove(nearest)
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    paused = not paused

        if not paused:
            # integrate
            for b in balls:
                b.x += b.vx * dt * 60
                b.y += b.vy * dt * 60
                # damping
                b.vx *= 0.999
                b.vy *= 0.999

            # collisions
            n = len(balls)
            for i in range(n):
                for j in range(i + 1, n):
                    resolve_ball_collision(balls[i], balls[j])

            for b in balls:
                resolve_wall_collision(b, WIDTH, HEIGHT)

        screen.fill(BG_COLOR)
        for b in balls:
            pygame.draw.circle(screen, b.color, (int(b.x), int(b.y)), b.radius)
            # velocity vector
            vx = int(b.vx * 8)
            vy = int(b.vy * 8)
            pygame.draw.line(screen, (255, 255, 255), (int(b.x), int(b.y)), (int(b.x + vx), int(b.y + vy)), 1)

        draw_ui(screen, balls, paused)
        pygame.display.flip()

    pygame.quit()


if __name__ == "__main__":
    main()
