#!/usr/bin/python3.5

import sys, time, math, random, heapq, pygame
from operator import itemgetter
from collections import defaultdict
from colors import *
#from eventsim_classes import *

def run():
    pygame.init()
    w, h, s = 900, 750, 5
#    w, h, s = 1100, 600, 10
    clock = pygame.time.Clock()  # create a clock object
    FPS = 10000  # set frame rate in frames per second.
    screen = pygame.display.set_mode((w, h))  # create screen
    create_space(w, h, s) #Create a dictionary of all cells.
    print("Created space of width " + repr(w) + " pixels, height " + repr(h) + " pixels and " +  repr(int(w/s)*int(h/s)) + " cells")
    print("Assigning neighbours to each cell... ")
    Cell.assign_neighbours()
    tf = 0
    while True:
        tf += 1
        start = time.clock()
        screen.fill(white)
        draw_space(screen, drawing_type = "graph")
        manage_events(screen)
        pygame.display.update()
#        print(round(1.0/(time.clock() - start),3), "fps")
        clock.tick(FPS)

def create_space(w, h, s):
    for i in range(int(w/s)):
        for j in range(int(h/s)):
            Cell(i, j, s)

def draw_space(screen, drawing_type = "graph"):
    for c in Cell.C:
        Cell.C[c].draw_cell(screen, drawing_type = drawing_type)

def manage_events(screen):
    mpos = tuple([math.floor(i /Cell.size) for i in pygame.mouse.get_pos()])
#    event_highlight_zone(screen, mpos, graph)
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit

class Actor:
    def __init__(self, ID, x = None, y = None):
        self.ID = ID
        self.x = x
        self.y = y
        self.personal_space = self.update_personal_space()


    def update_personal_space():
        p_space = dict()
        dirs = (1, 0), (0, 1), (-1, 0), (0, -1), \
                (1, 1), (1, -1), (-1, -1), (-1, 1)    
        p_space[(1,0)] = set(Cell.C[(self.x, self.y)].nbrs)

class Cell:
    C = dict()
    T = defaultdict(list)
    def __init__(self, x, y, s):
        self.x, self.y, self.s = x, y, s
        self.is_barrier = False
        self.is_occupied = False
        self.in_zone = False
        self.in_threshold = False
        self.in_meeting = False
        self.zones = set()
        self.nbrs = list()
        self.rect = pygame.Rect(self.x * self.s, self.y * self.s, self.s, self.s)
        Cell.C[(self.x, self.y)] = self
        Cell.size = self.s

  
    def neighbours(self):
        x, y = self.x, self.y
        results = [(x + 1, y), (x - 1, y), (x, y + 1), (x, y - 1),
                   (x + 1, y + 1), (x + 1, y - 1), (x - 1, y + 1), (x - 1, y - 1)]
        nbrs = [r for r in results if r in Cell.C.keys()]
        return nbrs
    
    def draw_cell(self, screen, drawing_type = None, color = None):
        r = max(2, int(Cell.size/2.5))
        if self.is_barrier:
            color = chocolate
        elif not self.is_barrier:
            color = lightgrey
        if self.in_threshold and not self.is_barrier:
            color = gold
        if self.in_zone and not self.in_threshold:
            color = wheat
        if self.in_meeting:
            color = green
        if drawing_type == "graph":
            pygame.draw.circle(screen, color, (self.x * self.s + int(self.s/2), self.y * self.s + int(self.s/2)), r)
        if drawing_type == "grid":
            pygame.draw.rect(screen, color, self.rect, 1)
    
    def draw_acceptable(self, screen, color, drawing_type = None):
        r = max(2, int(Cell.size/2.5))
        if drawing_type == "graph":
            pygame.draw.circle(screen, color, (self.x * self.s + int(self.s/2), self.y * self.s + int(self.s/2)), r)
        if drawing_type == "grid":
            pygame.draw.rect(screen, color, self.rect, 1)
                   
    
    def highlight_cell(self, screen, color, drawing_type = None):
        r = max(2, int(Cell.size/2.5))
        if drawing_type == "grid":
            pygame.draw.rect(screen, color, self.rect, 1)
        if drawing_type == "graph":
            pygame.draw.circle(screen, color, (self.x * self.s + int(self.s/2), self.y * self.s + int(self.s/2)), r)

    def is_orthogonal_neighbour(self, c):
        return c in [(self.x + 1, self.y), (self.x - 1, self.y), (self.x, self.y + 1), (self.x, self.y - 1)]

    @staticmethod
    def assign_neighbours():
        count = 0
        for c in Cell.C:
            Cell.C[c].nbrs = Cell.C[c].neighbours()
            count += 1
            if count % 1000 == 0:
                print (count, "neighbours assigned.. ")


if __name__ == "__main__":
    run()
