import pygame
import numpy as np
import math
import sys

SCREEN_W  = 900
SCREEN_H  = 600
FPS       = 60
CELL      = 30
GRID_H    = SCREEN_H // CELL
GRID_W    = SCREEN_W // CELL
OUTER     = 2
INNER     = 6


C_GRASS   = ( 34, 120,  34)
C_TRACK   = ( 70,  70,  70)
C_KERB1   = (220,  20,  20)
C_KERB2   = (240, 240, 240)
C_START   = (255, 215,   0)
C_HUD     = (255, 255, 255)
C_SHADOW  = (  0,   0,   0, 80)

CAR_ACCEL    = 0.18
CAR_BRAKE    = 0.25
CAR_FRICTION = 0.96
CAR_STEER    = 3.2
MAX_SPEED    = 4.5

def make_track():
    grid = np.zeros((GRID_H, GRID_W), dtype=int)
    grid[OUTER:GRID_H - OUTER, OUTER:GRID_W - OUTER] = 1
    grid[INNER:GRID_H - INNER, INNER:GRID_W - INNER] = 0
    start_row = GRID_H - OUTER - 1
    mid_col   = GRID_W // 2
    grid[start_row, mid_col - 1:mid_col + 2] = 2
    return grid

def is_on_track(grid, px, py):

    c = int(px // CELL)
    r = int(py // CELL)
    if r < 0 or r >= GRID_H or c < 0 or c >= GRID_W:
        return False
    return grid[r, c] >= 1

def draw_track(surface, grid):
    for r in range(GRID_H):
        for c in range(GRID_W):
            v    = grid[r, c]
            rect = pygame.Rect(c * CELL, r * CELL, CELL, CELL)
            if v == 0:
                pygame.draw.rect(surface, C_GRASS, rect)
            elif v == 1:
                pygame.draw.rect(surface, C_TRACK, rect)
            elif v == 2:
                stripe = (c % 2 == 0)
                pygame.draw.rect(surface, C_KERB1 if stripe else C_KERB2, rect)


    for r in range(GRID_H):
        for c in range(GRID_W):
            if grid[r, c] >= 1:
                neighbors = [
                    (r-1,c),(r+1,c),(r,c-1),(r,c+1)
                ]
                for nr, nc in neighbors:
                    if 0 <= nr < GRID_H and 0 <= nc < GRID_W and grid[nr, nc] == 0:
                        rect = pygame.Rect(c * CELL, r * CELL, CELL, CELL)
                        stripe = ((r + c) % 2 == 0)
                        color  = C_KERB1 if stripe else C_KERB2
                        pygame.draw.rect(surface, color, rect)  # solid fill


def draw_f1_car(surface, x, y, angle_deg):

    car_surf = pygame.Surface((48, 22), pygame.SRCALPHA)

    pygame.draw.rect(car_surf, (180, 0, 0),     pygame.Rect( 4,  6, 38,  10))
    pygame.draw.rect(car_surf, (200, 20, 20),   pygame.Rect( 2,  7, 10,   8))
    pygame.draw.rect(car_surf, (220, 220, 220), pygame.Rect(18,  5,  8,  12))
    pygame.draw.rect(car_surf, ( 10, 10, 10),   pygame.Rect(20,  7,  5,   8))


    pygame.draw.rect(car_surf, (140,  0,  0),   pygame.Rect( 0,  3, 10,   3))
    pygame.draw.rect(car_surf, (140,  0,  0),   pygame.Rect( 0, 16, 10,   3))

    pygame.draw.rect(car_surf, (100,  0,  0),   pygame.Rect(38,  1, 6,   20))
    pygame.draw.rect(car_surf, (160,  0,  0),   pygame.Rect(40,  4, 4,   14))


    pygame.draw.rect(car_surf, ( 20, 20, 20),   pygame.Rect( 8,  0,  8,   5))
    pygame.draw.rect(car_surf, ( 20, 20, 20),   pygame.Rect( 8, 17,  8,   5))
    pygame.draw.rect(car_surf, ( 30, 30, 30),   pygame.Rect(32,  0,  8,   5))
    pygame.draw.rect(car_surf, ( 30, 30, 30),   pygame.Rect(32, 17,  8,   5))


    pygame.draw.rect(car_surf, (255, 200,  0),  pygame.Rect(12,  6, 16,   2))
    pygame.draw.rect(car_surf, (255, 200,  0),  pygame.Rect(12, 14, 16,   2))


    rotated = pygame.transform.rotate(car_surf, -angle_deg)
    rect    = rotated.get_rect(center=(int(x), int(y)))
    surface.blit(rotated, rect)

class Car:
    def __init__(self, start_row, start_col):
        self.x      = start_col * CELL + CELL // 2
        self.y      = start_row * CELL + CELL // 2
        self.angle  = 0.0
        self.speed  = 0.0
        self.laps   = 0
        self.crossed_start = False
        self.crashed       = False
        self.crash_timer   = 0

    def update(self, keys, grid):
        if self.crashed:
            self.speed *= 0.8
            self.crash_timer -= 1
            if self.crash_timer <= 0:
                self.crashed = False
            return


        if abs(self.speed) > 0.05:
            if keys[pygame.K_LEFT]:
                self.angle -= CAR_STEER * (self.speed / MAX_SPEED)
            if keys[pygame.K_RIGHT]:
                self.angle += CAR_STEER * (self.speed / MAX_SPEED)


        if keys[pygame.K_UP]:
            self.speed = min(self.speed + CAR_ACCEL, MAX_SPEED)
        elif keys[pygame.K_DOWN]:
            self.speed = max(self.speed - CAR_BRAKE, -MAX_SPEED * 0.4)
        else:
            self.speed *= CAR_FRICTION


        rad    = math.radians(self.angle)
        new_x  = self.x + math.cos(rad) * self.speed
        new_y  = self.y + math.sin(rad) * self.speed

        if is_on_track(grid, new_x, new_y):
            self.x, self.y = new_x, new_y
        else:

            self.speed      *= -0.3
            self.crashed     = True
            self.crash_timer = 20

    def reset(self, start_row, start_col):
        self.x      = start_col * CELL + CELL // 2
        self.y      = start_row * CELL + CELL // 2
        self.angle  = 0.0
        self.speed  = 0.0
        self.laps   = 0
        self.crashed      = False
        self.crash_timer  = 0

def draw_hud(surface, car, font, font_small):
    speed_kmh = abs(car.speed) / MAX_SPEED * 320
    lap_text  = font.render(f"LAP  {car.laps}", True, C_HUD)
    spd_text  = font.render(f"{speed_kmh:03.0f} km/h", True,
                             (255, 80, 80) if car.crashed else C_HUD)
    ctrl_text = font_small.render("↑ Accelerate   ↓ Brake   ← → Steer   R Reset", True, (180, 180, 180))

    surface.blit(lap_text,  (20, 15))
    surface.blit(spd_text,  (20, 50))
    surface.blit(ctrl_text, (20, SCREEN_H - 30))

    # speed bar
    bar_w = int((abs(car.speed) / MAX_SPEED) * 200)
    pygame.draw.rect(surface, (60, 60, 60),   pygame.Rect(20, 85, 200, 12), border_radius=4)
    pygame.draw.rect(surface, (220, 30, 30),  pygame.Rect(20, 85, bar_w, 12), border_radius=4)

    if car.crashed:
        crash_surf = font.render("CRASH!", True, (255, 60, 60))
        surface.blit(crash_surf, (SCREEN_W // 2 - 50, 20))


def main():
    pygame.init()
    screen = pygame.display.set_mode((SCREEN_W, SCREEN_H))
    pygame.display.set_caption("CEAM Week 4")
    clock  = pygame.time.Clock()


    grid      = make_track()
    start_row = GRID_H - OUTER - 1
    start_col = GRID_W // 2
    car       = Car(start_row, start_col)


    track_surf = pygame.Surface((SCREEN_W, SCREEN_H))
    draw_track(track_surf, grid)

    while True:
        clock.tick(FPS)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    pygame.quit()
                    sys.exit()
                if event.key == pygame.K_r:
                    car.reset(start_row, start_col)

        keys = pygame.key.get_pressed()
        car.update(keys, grid)


        screen.blit(track_surf, (0, 0))
        draw_f1_car(screen, car.x, car.y, car.angle)
        pygame.display.flip()

if __name__ == "__main__":
    main()
