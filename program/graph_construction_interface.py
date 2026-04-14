import pygame
import math
import random
import time
import json
from pathlib import Path

########################################################################################
# Class
class Mouse:
    """
    Animations and actions for mouse
    """
    def __init__(self) -> None:
        self.mode:str = None
        self.x, self.y = 0, 0
        self.x_real, self.y_real = self.x, self.y
        self.press:bool = False
        self.click:bool = False
        self.side:int = None
        self.drag:bool = False
        self.color:list[int, int, int] = [200, 160, 160]
        self.color_normal:list[int, int, int] = [200, 160, 160]
        self.color_right:list[int, int, int] = [120, 210, 150]
        self.color_left:list[int, int, int] = [250, 100, 130]
        self.alpha:int = 255
        self.max_alpha:int = 255
        self.radius:int = 7
        self.effect_press:float = 1

    def animation(self) -> None:
        global TEXTRENDER

        x_temp, y_temp = pygame.mouse.get_pos()
        self.x, self.y = exp_mean(self.x, x_temp, alpha = 0.5), exp_mean(self.y, y_temp, alpha = 0.5)
        self.effect_press = exp_mean(self.effect_press, 1, alpha = 0.04)
        self.color = [exp_mean(c, self.color_normal[i], alpha = 0.04) for i, c in enumerate(self.color)]
        pygame.draw.circle(MOUSESURF, (*[round(c) for c in self.color], self.alpha), (self.x, self.y), self.radius, round(self.effect_press))

        self.click:bool = False
        if event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:
                #print(f"Mouse Press: {pygame.mouse.get_pos()} (left)")
                self.press:bool = True
                self.effect_press:float = exp_mean(self.effect_press, 10, alpha = 0.08)
                self.color:list[float] = [exp_mean(c, self.color_left[i], alpha = 0.08) for i, c in enumerate(self.color)]
                self.side:int = 1

            if event.button == 3:
                #print(f"Mouse Press: {pygame.mouse.get_pos()} (right)")
                self.press:bool = True
                self.effect_press:float = exp_mean(self.effect_press, 10, alpha = 0.08)
                self.color:list[float] = [exp_mean(c, self.color_right[i], alpha = 0.08) for i, c in enumerate(self.color)]
                self.side:int = 3

        else:
            if self.press & (self.side == 1):
               self.click:bool = True
               self.press:bool = False
               print(f"Mouse Click: {pygame.mouse.get_pos()} (left)")

            elif self.press & (self.side == 3):
               self.click:bool = True
               self.press:bool = False
               print(f"Mouse Click: {pygame.mouse.get_pos()} (right)")

        text_surface = TEXTRENDER.render(f"Mode: {self.mode if self.mode != None else '~'}", True, (255, 255, 255))
        rect_text = text_surface.get_rect()
        SCREEN.blit(text_surface, rect_text)


    def find_event(self, event) -> None:
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                print("Press (esc)!")
                self.mode = None

            elif event.key == pygame.K_n:
                print("Press (n)!")
                self.mode = "(N)ode"

            elif event.key == pygame.K_c:
                print("Press (c)!")
                self.mode = "(C)onnection"

            else:
                self.mode = None

class Grid:
    def animation(self) -> None:
        global MAXSCREENX, MAXSCREENY, GRIDSURF, SCREENX, SCREENY

        for line_x in range(0, MAXSCREENX+101, 100):
            pygame.draw.line(GRIDSURF, (255, 255, 255, 30), (line_x-SCREENX%100, 0), (line_x-SCREENX%100, MAXSCREENY), 3)

        for line_y in range(0, MAXSCREENY+101, 100):
            pygame.draw.line(GRIDSURF, (255, 255, 255, 30), (0, line_y-SCREENY%100), (MAXSCREENX, line_y-SCREENY%100), 3)

        x, y = pygame.mouse.get_pos()
        n:float = 0.05
        n_:float = 1- n
        if x < n*MAXSCREENX:
            SCREENX -= max(0, int((n*MAXSCREENX - x)/3))
        elif x > n_*MAXSCREENX:
            SCREENX += max(0, int((x - n_*MAXSCREENX)/3))
        if y < n*MAXSCREENY:
            SCREENY -= max(0, int((n*MAXSCREENY - y)/3))
        elif y > n_*MAXSCREENY:
            SCREENY += max(0, int((y - n_*MAXSCREENY)/3))


class Nodes:
    def __init__(self) -> None:
        self.pos:list[int, int] = []
        self.ids:list[int] = []
        self.names:list[str] = []
        self.conections:list[str] = []

    def animation(self) -> None:
        for pos in self.pos:
            pygame.draw.circle(NODESURF, (*[round(c) for c in self.color], self.alpha), (self.x, self.y), self.radius, round(self.effect_press))

class Log:
    """
    Class to read logs
    """
    def __init__(self) -> None:
        self.logs:list = []

    def __call__(self, log:str) -> None:
        self.log.append(log)

########################################################################################
# Functions
def projection_mouse_pos() -> (float, float):
    """
    Screen mouse pos to real mouse pos
    """
    global MAXSCREENX, MAXSCREENY, SCREENX, SCREENY
    x, y = pygame.mouse.get_pos()
    return MAXSCREENX + SCREENX, MAXSCREENY + SCREENY


def exp_mean(pos_past, pos_now, alpha = 0.2) -> float:
    return pos_past*(1-alpha) + pos_now*alpha

########################################################################################
# Global definitions
MAXSCREENX:int = 1350
MAXSCREENY:int = 900
SCREENX:int = 0
SCREENY:int = 0
FPS:int = 30
MOUSE:Mouse = Mouse()
LOG:Log = Log()
GRID:Grid = Grid()

# Colors
COLORBOTTON = (45, 50, 50)

pygame.init()
CLOCK = pygame.time.Clock()
SCREEN = pygame.display.set_mode((MAXSCREENX, MAXSCREENY))
MOUSESURF = pygame.Surface((MAXSCREENX, MAXSCREENY), pygame.SRCALPHA)
GRIDSURF = pygame.Surface((MAXSCREENX, MAXSCREENY), pygame.SRCALPHA)
NODESURF = pygame.Surface((MAXSCREENX, MAXSCREENY), pygame.SRCALPHA)

TEXTRENDER = pygame.font.SysFont("arial", 30)

pygame.display.set_caption("GCI 0.0.1")

running:bool = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        MOUSE.find_event(event)

    # Clean screen
    MOUSESURF.fill((0, 0, 0, 0))
    GRIDSURF.fill((0, 0, 0, 0))
    NODESURF.fill((0, 0, 0, 0))

    # Draw in screen
    SCREEN.fill(COLORBOTTON)

    # Logic
    MOUSE.animation()
    GRID.animation()

    SCREEN.blit(NODESURF, (0, 0))
    SCREEN.blit(GRIDSURF, (0, 0))
    SCREEN.blit(MOUSESURF, (0, 0))

    pygame.display.flip()
    CLOCK.tick(FPS)

pygame.quit()
