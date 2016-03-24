import sys, time, math, random, heapq, pygame
from operator import itemgetter
from collections import defaultdict
from colors import *

def draw(x, y, s, screen, color, fill = False):
    if not fill:
        pygame.draw.rect(screen, color, (x*s, y*s, s, s), 1)
    if fill:
        pygame.draw.rect(screen, color, (x*s, y*s, s, s))    

def check_orthogonal_cells(start, x, y, screen, color):
    directions = (1, 0), (0, 1), (-1, 0), (0, -1)
    cx, cy = start
    for d in directions:
        dx, dy = d
        while 0 < cx < x and 0 < cy < y:
            cx += dx
            cy += dy
            if 0 < cx < x and 0 < cy < y:
                draw(cx, cy, s, screen, color)
        cx, cy = start            
        
def check_diagonal_cells(start, x, y, screen, color):
    directions = (1, 1), (-1, 1), (-1, -1), (1, -1)
    cx, cy = start
    for d in directions:
        dx, dy = d
        while 0 < cx < x and 0 < cy < y:
            cx += dx
            cy += dy
            check_orthogonal_cells((cx, cy), x, y, screen, color)
        cx, cy = start
        
pygame.init()
w, h, s = 600, 600, 10
clock = pygame.time.Clock()  # create a clock object
screen = pygame.display.set_mode((w, h))  # create screen
x = w/s
y = h/s
start = random.choice(range(x)), random.choice(range(y))
end = random.choice(range(x)), random.choice(range(y))
while True:
    screen.fill(white)
    for i in range(x):
        for j in range(y):
            draw(i, j, s, screen, lightgrey)
    draw(start[0], start[1], s, screen, blue, fill = True)
    draw(end[0], end[1], s, screen, gold, fill = True)
    check_orthogonal_cells(start, x, y, screen, yellow)
#    check_diagonal_cells(start, x, y, screen, yellow)
    pygame.display.update()
    clock.tick(24)
