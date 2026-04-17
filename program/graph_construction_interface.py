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
        self.alpha_zoom:int = 0

    def animation(self) -> None:
        global TEXTRENDER, ZOOM

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

            elif event.button == 3:
                #print(f"Mouse Press: {pygame.mouse.get_pos()} (right)")
                self.press:bool = True
                self.effect_press:float = exp_mean(self.effect_press, 10, alpha = 0.08)
                self.color:list[float] = [exp_mean(c, self.color_right[i], alpha = 0.08) for i, c in enumerate(self.color)]
                self.side:int = 3

        elif event.type == pygame.MOUSEWHEEL:
            if event.y > 0:
                ZOOM = max(0.25, min(4, ZOOM*0.95))
                print(f"Scroll up! {ZOOM:0.04f}")
                self.alpha_zoom:float = 255

            elif event.y < 0:
                ZOOM = max(0.25, min(4, ZOOM*1.05))
                print(f"Scroll up! {ZOOM:0.04f}")
                self.alpha_zoom:float = 255
            event.y = 0

        else:
            if self.press & (self.side == 1):
               self.click:bool = True
               self.press:bool = False
               print(f"Mouse Click: {pygame.mouse.get_pos()} (left)")

            elif self.press & (self.side == 3):
               self.click:bool = True
               self.press:bool = False
               print(f"Mouse Click: {pygame.mouse.get_pos()} (right)")


        if self.alpha_zoom > 0:
            self.alpha_zoom -= 3
            pygame.draw.line(MOUSESURF, (200, 210, 200, self.alpha_zoom),
                            (self.x+29, self.y-20), (self.x+29, self.y+20), 2)
            pygame.draw.circle(MOUSESURF, (255, 255, 255, self.alpha_zoom),
                               (self.x+30, self.y+ZOOM*10 - 20), 6, 6)


        text_surface = TEXTRENDER.render(f"Mode: {self.mode if self.mode != None else '~'}\n{x_temp*ZOOM + SCREENX, y_temp*ZOOM + SCREENY}", True, (255, 255, 255))
        rect_text = text_surface.get_rect()
        SCREEN.blit(text_surface, rect_text)

    def find_event(self, event) -> None:
        global ZOOM

        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                print("Press (esc)!")
                self.mode = None
            elif event.key == pygame.K_h:
                print("Press (h)!")
                self.mode = "(H)elp"
            elif event.key == pygame.K_i:
                print("Press (i)!")
                self.mode = "(I)nfo"
            elif event.key == pygame.K_n:
                print("Press (n)!")
                self.mode = "(N)ode"
            elif event.key == pygame.K_c:
                print("Press (c)!")
                self.mode = "(C)onnection"
            elif event.key == pygame.K_b:
                print("Press (b)!")
                self.mode = "(B)oth connection"
            elif (event.key == pygame.K_KP_PLUS) | (event.key == pygame.K_PAGEUP):
                ZOOM = max(0.25, min(4, ZOOM-0.25))
                print(f"Press (+)! {ZOOM:0.04f}")
                self.alpha_zoom:float = 255
                self.mode = "(+ | PGUP) Zoon in"
            elif (event.key == pygame.K_KP_MINUS) | (event.key == pygame.K_PAGEDOWN):
                ZOOM = max(0.25, min(4, ZOOM+0.25))
                print(f"Press (-)! {ZOOM:0.04f}")
                self.alpha_zoom:float = 255
                self.mode = "(- | PGDOWN) Zoon out"
            elif event.key == pygame.K_u:
                print("Press (u)!")
                self.mode = "(U)ndo"
            elif event.key == pygame.K_r:
                print("Press (r)!")
                self.mode = "(R)emove"

            else:
                self.mode = None


    def logic(self) -> None:
        global NODES, MAXSCREENX, MAXSCREENY, GRIDSURF, SCREENX, SCREENY, ZOOM

        if (self.mode == "(N)ode") & (self.click == True) & (self.side == 1):
            pos_x, pos_y = projection_mouse_pos()
            can_put:bool = True
            for index, (pos_x_temp, pos_y_temp) in enumerate(NODES.pos):
                if (abs(pos_x_temp - pos_x) < 50) and (abs(pos_y_temp - pos_y) < 50):
                    can_put:bool = False
                    NODES.warnings[index] = 120
                    print(f"Not possible!")
                    break

            if can_put:
                NODES.create_node((pos_x, pos_y))

        elif (self.mode == "(R)emove") & (self.click == True) & (self.side == 1):
            pos_x, pos_y = projection_mouse_pos()
            can_put:bool = True
            for index, (pos_x_temp, pos_y_temp) in enumerate(NODES.pos):
                if (abs(pos_x_temp - pos_x) < 30) and (abs(pos_y_temp - pos_y) < 30):
                    NODES.remove(index)
                    break

        elif self.mode == "(I)nfo":
            self.alpha_zoom:int = 255


class Grid:
    def animation(self) -> None:
        global MAXSCREENX, MAXSCREENY, GRIDSURF, SCREENX, SCREENY, ZOOM

        diff:int = round(100*1/ZOOM)
        for line_x in range(0, MAXSCREENX+diff+1, diff):
            pygame.draw.line(GRIDSURF, (255, 255, 255, 30), (line_x-SCREENX/ZOOM%diff, 0), (line_x-SCREENX/ZOOM%diff, MAXSCREENY), 3)

        for line_y in range(0, MAXSCREENY+diff+1, diff):
            pygame.draw.line(GRIDSURF, (255, 255, 255, 30), (0, line_y-SCREENY/ZOOM%diff), (MAXSCREENX, line_y-SCREENY/ZOOM%diff), 3)

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
        self.colors:list[int, int, int] = []
        self.ids:list[int] = []
        self.names:list[str] = []
        self.connections:list[str] = []
        self.warnings:list[int] = []

    def remove(self, i:int) -> None:
        del self.pos[i]
        del self.colors[i]
        del self.ids[i]
        del self.names[i]
        del self.connections[i]
        del self.warnings[i]

    def animation(self) -> None:
        global SCREENX, SCREENY, ZOOM

        x, y = pygame.mouse.get_pos()
        for i, pos in enumerate(self.pos):
            x_pos, y_pos = (pos[0] - SCREENX)/ZOOM, (pos[1] - SCREENY)/ZOOM
            len_:int = round(20*1/ZOOM)
            pygame.draw.circle(NODESURF, (*self.colors[i], 255),
                                          [x_pos, y_pos], len_, round(4*1/ZOOM*255/self.colors[i][2]))

            if (x - x_pos)*(x - x_pos) + (y - y_pos)*(y - y_pos) < len_**2*1.2:
                self.colors[i][2] = max(self.colors[i][2] - 10, 80)
            else:
                self.colors[i][2] = min(self.colors[i][2] + 10, 255)

            if self.warnings[i] > 0:
                pygame.draw.rect(MOUSESURF, (255, 0, 0, self.warnings[i]), (x_pos-50, y_pos-50, 100, 100))
                self.warnings[i] -= 5

    def create_node(self, pos:list[int, int]) -> None:
        self.pos.append(pos)
        self.colors.append([255, 255, 255])
        self.ids.append("".join([chr(int(random.uniform(65, 127))) for i in range(15)]))
        self.names.append(None)
        self.connections.append(None)
        self.warnings.append(0)
        print(self.pos, self.ids)

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
    global MAXSCREENX, MAXSCREENY, SCREENX, SCREENY, ZOOM
    x, y = pygame.mouse.get_pos()
    return x*ZOOM + SCREENX, y*ZOOM + SCREENY


def exp_mean(pos_past, pos_now, alpha = 0.2) -> float:
    return pos_past*(1-alpha) + pos_now*alpha

########################################################################################
# Global definitions
MAXSCREENX:int = 1350
MAXSCREENY:int = 900
ZOOM:float = 1
SCREENX:int = 0
SCREENY:int = 0
FPS:int = 30
MOUSE:Mouse = Mouse()
LOG:Log = Log()
GRID:Grid = Grid()
NODES:Nodes = Nodes()

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

    MOUSE.logic()

    # Clean screen
    MOUSESURF.fill((0, 0, 0, 0))
    GRIDSURF.fill((0, 0, 0, 0))
    NODESURF.fill((0, 0, 0, 0))

    # Draw in screen
    SCREEN.fill(COLORBOTTON)

    # Logic
    MOUSE.animation()
    NODES.animation()
    GRID.animation()

    SCREEN.blit(NODESURF, (0, 0))
    SCREEN.blit(GRIDSURF, (0, 0))
    SCREEN.blit(MOUSESURF, (0, 0))

    pygame.display.flip()
    CLOCK.tick(FPS)

pygame.quit()
