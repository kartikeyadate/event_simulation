#!/usr/bin/python3.5

import sys, time, math, random, heapq, pygame, numpy
from operator import itemgetter
from PIL import Image
from collections import defaultdict
from colors import *

def run():
    pygame.init()
    w, h, s = 1500, 655, 5 #if no plan is provided.
    clock = pygame.time.Clock()  # create a clock object
    FPS = 1  # set frame rate in frames per second.
    screen = pygame.display.set_mode((w, h))  # create screen
    create_space(w, h, s, "Cardiology_2.png") #Create a dictionary of all cells.
    zone_size = 12  # The minimum zone size possible is 4. Program will break for sizes below 4.
    top_left = (1, 1)
    create_zones(w, h, s, top_left = top_left, zone_size = zone_size)
    threshold_graph = create_threshold_graph()
    pygame.display.set_caption("First Test Case")
    background = pygame.image.load("Cardiology_2.png").convert()

    frames = 0
    fps_measures = list()
    while True:
        ms1 = clock.tick()
        screen.fill(white)
        mpos = tuple([math.floor(i /Cell.size) for i in pygame.mouse.get_pos()])
        for event in pygame.event.get():
            mark_spaces(event, mpos)
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit
        draw_space_from_picture(screen, drawing_type = "grid")
        pygame.display.update()

###########################################################################################################
###########################################################################################################
#####################INITIALIZING SPACE, ACTORS, THRESHOLDS################################################

def coldist(a, b):
    x1, y1, z1 = a
    x2, y2, z2 = b
    return math.sqrt((x1-x2)**2 + (y1-y2)**2 + (z1-z2)**2)


def create_space(w, h, s, img):
    spaces = {"threshold":(255,0,0), "wall":(0,0,0), "space": (255, 255, 255), "ignore":(0, 255, 0), "equipment": (255, 255,0)}
    img = Image.open(img)
    width, height = img.size
    print(width, height)
    rgbvals = dict()
    distinctvals = set()
    for i in range(width):
        for j in range(height):
            rgbvals[(i,j)] = img.getpixel((i,j))
            if len(rgbvals[(i,j)]) == 4:
                r,g,b = rgbvals[(i,j)][:-1]
            elif len(rgbvals[(i,j)]) == 3:
                r,g,b = rgbvals[(i,j)]

            r = 1.0*r/(s*s)
            g = 1.0*g/(s*s)
            b = 1.0*b/(s*s)
            rgbvals[(i,j)] = (r, g, b)

    for i in range(int(w/s)):
        for j in range(int(h/s)):
            Cell(i, j, s)

    for c in Cell.C:
        x1, y1 = Cell.C[c].rect.topleft
        x2, y2 = Cell.C[c].rect.bottomright
        for i in range(x1, x2):
            for j in range(y1, y2):
                if (i,j) in rgbvals:
                    Cell.C[c].colors.append(rgbvals[(i,j)])
        Cell.C[c].colors = tuple([int(sum(i)) for i in zip(*Cell.C[c].colors)])
        distances = list()
        for k in spaces:
            distances.append((coldist(Cell.C[c].colors, spaces[k]), spaces[k]))
        closest = sorted(distances, key = itemgetter(0))[0]
        Cell.C[c].colors = closest[1]


def create_actors(n):
#        def __init__(self, name, x = None, y = None, color = None, zone = None, threshold = None):
    count = 0
    zone_ids = list(Zone.Z.keys())
    allcolors = (midnightblue, teal, darkgreen, red, None)
    while count < n:
        Actor(str(count), color = random.choice(allcolors), zone = random.choice(zone_ids))
        count += 1

def create_threshold_graph():
    graph = defaultdict(list)
    for z in Zone.Z:
        for c in Zone.Z[z].threshold_cells.keys():
            Cell.C[c].zones.add(z)

    for z in Zone.Z.keys():
        for c in Zone.Z[z].threshold_cells:

            if len(Cell.C[c].zones) == 1:
                Cell.C[c].in_zone = False

    for c in Cell.C:
        if Cell.C[c].in_threshold:
            invalid_thresholds = defaultdict(list)
            for z in Cell.C[c].zones:
                for threshold in Zone.Z[z].thresholds:
                    if c not in threshold:
                        for tc in threshold:
                            graph[c].append(tc)
    return graph

def create_zones(w, h, s, top_left = (3, 3), zone_size = random.choice(range(20,25))):
    ID = 0
    for i in range(top_left[0], int(w/s) - zone_size, zone_size):
        for j in range(top_left[1], int(h/s) - zone_size, zone_size):
            zone = Zone(str(ID))
            for x in range(i, i + zone_size - 1):
                for y in range(j, j + zone_size - 1):
                    Cell.C[(x, y)].in_zone = True
                    #Add zone ID to the cells belonging to zones.
                    Cell.C[(x, y)].zones.add(str(ID))
                    zone.cells[(x, y)] = Cell.C[(x, y)]
            zone.make_walls(zone_size)
            ID += 1

########################################################################################
########################################################################################
####################SEARCH FUNCTIONS ###################################################

def search_thresholds(threshold_graph, screen):
    starts, goals = list(), list()
    for n in range(len(list(Actor.A.keys()))):
        if n % 2 == 0:
            start = Actor.A[list(Actor.A.keys())[n]].x, Actor.A[list(Actor.A.keys())[n]].y
            starts.append(start)
        elif not n % 2 == 0:
            goal = Actor.A[list(Actor.A.keys())[n]].x, Actor.A[list(Actor.A.keys())[n]].y
            goals.append(goal)
    searches = len(starts)
    for s in range(searches):
        start, goal = starts[s], goals[s]
        if Cell.C[start].zones.difference(Cell.C[goal].zones) is not None:
            for n in (start, goal):
                if n not in threshold_graph:
                    threshold_graph[n] = Zone.Z[list(Cell.C[n].zones)[0]].threshold_cells.keys()

            S = Search(start, goal, threshold_graph)
            S.get_threshold_path()
            S.draw_threshold_route(screen, color = black)



#########################################################################################
#########################################################################################
##################DRAW FUNCTIONS ########################################################

def mark_spaces(event, mpos):
    if event.type == pygame.MOUSEBUTTONDOWN:
        if mpos in Cell.C and pygame.mouse.get_pressed()[2] == 1:
            Cell.C[mpos].in_zone = True
        if mpos in Cell.C and pygame.mouse.get_pressed()[0] == 1:
            print(mpos, Cell.C[mpos].colors)



def draw_space(screen, drawing_type = "grid"):
    for c in Cell.C:
        Cell.C[c].draw_cell(screen, drawing_type = drawing_type)

def highlight_neighbours(mpos, graph, screen):
    if mpos in graph:
        for c in graph[mpos]:
            Cell.C[c].highlight_cell(screen, steelblue, drawing_type = "graph")

def draw_actors(screen):
    for a in Actor.A:
        Actor.A[a].draw_actor(screen)

def draw_space_from_picture(screen, drawing_type = "grid"):
    for c in Cell.C:
        Cell.C[c].draw_cell_from_picture(screen, drawing_type = drawing_type)



##################################################
##################################################
######## CLASSES DEFINING THE SPACE ##############
##################################################
##################################################

class Cell:
    C = dict()
    def __init__(self, x, y, s):
        self.x, self.y, self.s = x, y, s
        self.is_barrier = False
        self.is_occupied = False
        self.in_zone = False
        self.in_threshold = False
        self.zones = set()
        self.rect = pygame.Rect(self.x * self.s, self.y * self.s, self.s, self.s)
        self.colors = list()
        Cell.C[(self.x, self.y)] = self
        Cell.size = self.s

    def draw_cell_from_picture(self, screen, drawing_type = None):
        color = self.colors
        r = max(2, int(Cell.size/2.5))
        if drawing_type == "graph":
            pygame.draw.circle(screen, color, (self.x * self.s + int(self.s/2), self.y * self.s + int(self.s/2)), r)
        if drawing_type == "grid":
            pygame.draw.rect(screen, color, self.rect, 1)


    def draw_cell(self, screen, drawing_type = None):
        if self.is_barrier:
            color = chocolate
        elif not self.is_barrier:
            color = lightgrey
        if self.in_threshold and self.in_zone:
            color = gold
        if self.in_zone and not self.in_threshold:
            color = wheat
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


class Zone:
    Z = dict()
    def __init__(self,ID, cells = None, zone_type = None):
        self.ID = ID
        self.cells = dict()
        self.threshold_cells = dict()
        self.thresholds = list()
        self.zone_type = zone_type
        Zone.Z[self.ID] = self

    def inside(self, c):
        return c in list(self.cells.keys())

    def passable(self, c):
        return not Cell.C[c].is_occupied and not Cell.C[c].is_barrier and (Cell.C[c].in_zone or Cell.C[c].in_threshold)

    def neighbours(self, c):
        results = [(x + 1, y), (x - 1, y), (x, y + 1), (x, y - 1),
                   (x + 1, y + 1), (x + 1, y - 1), (x - 1, y + 1), (x - 1, y - 1)]
        results = filter(self.inside, results)
        results = filter(self.passable, results)
        return results

    def make_walls(self, zone_size):
        xs = sorted([c[0] for c in self.cells.keys()])
        ys = sorted([c[1] for c in self.cells.keys()])
        x_min, x_max = min(xs), max(xs)
        y_min, y_max = min(ys), max(ys)
        if zone_size % 2 == 0:
            mx = (x_min - 1) + zone_size // 2
            my = (y_min - 1) + zone_size // 2

        else:
            mx = (x_min - 1) + zone_size // 2 + 1
            my = (y_min - 1) + zone_size // 2 + 1

        if zone_size % 2 == 0:
            tx = mx - 2, mx - 1, mx, mx + 1, mx + 2
            ty = my - 2, my - 1, my, my + 1, my + 2
        elif not zone_size % 2 == 0:
            tx = mx - 2, mx - 1, mx, mx + 1
            ty = my - 2, my - 1, my, my + 1

        t1 = tuple([(x, y_min - 1) for x in tx])
        t2 = tuple([(x, y_max + 1) for x in tx])
        t3 = tuple([(x_min - 1, y) for y in ty])
        t4 = tuple([(x_max + 1, y) for y in ty])
        self.thresholds = [t1, t2, t3, t4]

        for x in range(x_min - 1, x_max + 2):
            if not x in tx:
                Cell.C[(x, y_min - 1)].is_barrier = True
                Cell.C[(x, y_max + 1)].is_barrier = True
            if x in tx:
                Cell.C[(x, y_min - 1)].is_barrier = False
                Cell.C[(x, y_max + 1)].is_barrier = False
                Cell.C[(x, y_min - 1)].in_threshold = True
                Cell.C[(x, y_max + 1)].in_threshold = True
                Cell.C[(x, y_min - 1)].in_zone = True
                Cell.C[(x, y_max + 1)].in_zone = True
                self.threshold_cells[(x, y_min - 1)] = Cell.C[(x, y_min - 1)]
                self.threshold_cells[(x, y_max + 1)] = Cell.C[(x, y_max + 1)]
                self.cells[(x, y_min - 1)] = Cell.C[(x, y_min - 1)]
                self.cells[(x, y_max + 1)] = Cell.C[(x, y_max + 1)]

        for y in range(y_min - 1, y_max + 2):
            if not y in ty:
                Cell.C[(x_min - 1, y)].is_barrier = True
                Cell.C[(x_max + 1, y)].is_barrier = True
            if y in ty:
                Cell.C[(x_min - 1, y)].is_barrier = False
                Cell.C[(x_max + 1, y)].is_barrier = False
                Cell.C[(x_min - 1, y)].in_threshold = True
                Cell.C[(x_max + 1, y)].is_threshold = True
                Cell.C[(x_min - 1, y)].in_zone = True
                Cell.C[(x_max + 1, y)].is_zone = True

                self.threshold_cells[(x_min - 1, y)] = Cell.C[(x_min - 1, y)]
                self.threshold_cells[(x_max + 1, y)] = Cell.C[(x_max + 1, y)]
                self.cells[(x_min - 1, y)] = Cell.C[(x_min - 1, y)]
                self.cells[(x_max + 1, y)] = Cell.C[(x_max + 1, y)]


##################################################
##################################################
######## CLASSES DEFINING THE ACTOR ##############
##################################################
##################################################

class Actor:
    A = dict()
    def __init__(self, name, x = None, y = None, color = None, zone = None, threshold = None):
        self.name = name
        self.x = x
        self.y = y
        if zone is not None:
            self.initialize_in_zone(zone)

        self.color = color if color is not None else crimson
        self.zone = zone
        Actor.A[self.name] = self
        Cell.C[(self.x, self.y)].is_occupied = True

    def initialize_in_zone(self, z):
        options = list(set(Zone.Z[z].cells.keys()).difference(set(Zone.Z[z].threshold_cells.keys())))
        self.x, self.y = random.choice(options)

    def draw_actor(self, screen):
        center = self.x*Cell.size + Cell.size // 2, self.y*Cell.size + Cell.size // 2
        radius = Cell.size // 2
        pygame.draw.circle(screen, self.color, center, radius)

    def move(self, c):
        old = self.x, self.y
        self.x, self.y = c
        Cell.C[old].is_occupied = False
        Cell.C[c].is_occupied = True

    def move_with_keys(self, direction):
        pass


##################################################
##################################################
######## CLASSES FOR SEARCH ######################
##################################################
##################################################

class PriorityQueue:
    """A wrapper class around python's heapq class.
       An instance of this class
       is used to store the list of open cells."""

    def __init__(self):
        self.elements = []

    def empty(self):
        return len(self.elements) == 0

    def put(self, item, priority):
        heapq.heappush(self.elements, (priority, item))

    def get(self):
        return heapq.heappop(self.elements)[1]

    def length(self):
        return len(self.elements)

    def printqueue(self):
        print(self.elements)

class Search_Zone:
    def __init__(self, start, goal, zone):
        self.start = start
        self.goal = goal
        self.graph = zone
        self.open_cells = PriorityQueue()
        self.came_from = dict()
        self.cost_so_far = dict()

    def min_cost(self, a, b):
        x1, y1 = a
        x2, y2 = b
        if abs(y2 - y1) > abs(x2 - x1):
            return 14 * abs(x2 - x1) + 10 *abs((abs(y2 - y1) - abs(x2 - x1)))
        elif abs(y2 - y1) < abs(x2 - x1):
            return 14 * abs(y2 - y1) + 10 *abs((abs(y2 - y1) - abs(x2 - x1)))
        elif abs(y2 - y1) == abs (x2 - x1):
            return 14 * abs(y2 - y1)

class Search:
    def __init__(self, start, goal, graph = None):
        self.start = start
        self.goal = goal
        self.graph = graph
        self.open_cells = PriorityQueue()
        self.came_from = dict()
        self.cost_so_far = dict()

    def min_cost(self, a, b):
        x1, y1 = a
        x2, y2 = b
        if abs(y2 - y1) > abs(x2 - x1):
            return 14 * abs(x2 - x1) + 10 *abs((abs(y2 - y1) - abs(x2 - x1)))
        elif abs(y2 - y1) < abs(x2 - x1):
            return 14 * abs(y2 - y1) + 10 *abs((abs(y2 - y1) - abs(x2 - x1)))
        elif abs(y2 - y1) == abs (x2 - x1):
            return 14 * abs(y2 - y1)

    def get_threshold_path(self):
        self.open_cells.put(self.start, 0)
        self.came_from[self.start] = None
        self.cost_so_far[self.start] = 0
        while not self.open_cells.empty():
            current = self.open_cells.get()
            neighbours = self.graph[current]
            if current in self.graph[self.goal]:
                self.came_from[self.goal] = current
                break
            for loc in neighbours:
                new_cost = self.cost_so_far[current] + self.min_cost(current, loc)
                if loc not in self.cost_so_far or new_cost < self.cost_so_far[loc]:
                    self.cost_so_far[loc] = new_cost
                    priority = new_cost + self.min_cost(current, self.goal)
                    self.open_cells.put(loc, priority)
                    self.came_from[loc] = current
        path = self.build_threshold_path()
        return path

    def build_threshold_path(self):
        path = list()
        goal_nbrs = self.graph[self.goal]
        for c in goal_nbrs:
            if c in self.came_from.keys():
                current = c
        path.append(current)
        while current != self.start:
            current = self.came_from[current]
            path.append(current)
        path.reverse()
        self.path = path
        return path

    def draw_threshold_route(self, screen, color = white):
        draw_this = list()
        for p in self.path:
            draw_this.append(Cell.C[p].rect.center)
        if len(draw_this) >= 2:
            pygame.draw.lines(screen, color, False, draw_this, 1)





if __name__ == "__main__":
    run()
