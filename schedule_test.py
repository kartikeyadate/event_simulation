#!/usr/bin/python

import sys, time, math, random, heapq, pygame
from operator import itemgetter
from eventsim_classes import *
from collections import defaultdict
from colors import *

def run():
    pygame.init()
    #    w, h, s = 1400, 800, 5   # set width and height of the screen
    w, h, s = 600, 600, 60  # set width and height of the screen
    create_space(w, h, s)
    clock = pygame.time.Clock()  # create a clock object
    FPS = 10  # set frame rate in frames per second.
    assert w % s == 0, "width must be divisible by size"
    assert h % s == 0, "height must be divisible by size"
    screen = pygame.display.set_mode((w, h))  # create screen
    screen.set_alpha(128)
    infest(2000, 3, 1, tomato) #POISON
#    infest(1000, 3, 1, steelblue) #POISON
    infest(1500, 3, -4, green) # ANTIDOTE
    while True:
        total_poison = Cockroach.total_poison()
        print "Total:", total_poison, "Average:", total_poison/len(Cell.C.keys())
        move_roaches(total_poison, 100)
        screen.fill(white)
        draw_space(screen, drawing_type = "graph")
        draw_poison(screen, drawing_type = "graph")
        manage_events(screen) 
        pygame.display.update()
        clock.tick(FPS)

def manage_events(screen):
    mpos = tuple([math.floor(i /Cell.size) for i in pygame.mouse.get_pos()])
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit
        
def create_space(w, h, s):
    for i in range(int(w/s)):
        for j in range(int(h/s)):
            Cell(i, j, s)
    Cell.assign_neighbours()            

def draw_space(screen, drawing_type = "graph"):
    for c in Cell.C:
        Cell.C[c].draw_cell(screen, drawing_type = drawing_type)

def infest(n, r, p, c):
    """Makes n roaches of size (radius) r, poison level p and color c in zone z"""
    count = 0
    while count < n:
        x, y = random.choice(list(Cell.C.keys()))
        Cockroach(x, y, r, p, c)
        count += 1

def draw_poison(screen, drawing_type = "grid"):
    max_poison = max(max(Cockroach.Poison.values()),1)
    for c in Cockroach.Poison:
        col = int(255.0 - 255.0*Cockroach.Poison[c]/max_poison)
        color = col, col, col
        Cell.C[c].draw_acceptable(screen, color, drawing_type = drawing_type)

def move_roaches(poison, threshold):
    for r in Cockroach.Roaches:
        r.move_cockroach_randomly()
        if poison > threshold:
            r.move_antidote_intelligently()        
        else:
            r.move_antidote_randomly()
   
if __name__ == "__main__":
    run()
