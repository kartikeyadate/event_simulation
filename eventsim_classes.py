import sys, time, math, random, heapq, pygame
from operator import itemgetter
from collections import defaultdict
from colors import *

################################################################################
################################################################################
#### SPACE CLASSES #############################################################
################################################################################
################################################################################

class Cell:
    C = dict()
    T = defaultdict(list)
    def __init__(self, x, y, s):
        self.x, self.y, self.s = x, y, s
        self.is_barrier = False
        self.is_occupied = False
        self.in_zone = False
        self.in_threshold = False
        self.zones = set()
        self.rect = pygame.Rect(self.x * self.s, self.y * self.s, self.s, self.s)
        Cell.C[(self.x, self.y)] = self
        Cell.size = self.s

  
    def neighbours(self):
        x, y = self.x, self.y
        results = [(x + 1, y), (x - 1, y), (x, y + 1), (x, y - 1),
                   (x + 1, y + 1), (x + 1, y - 1), (x - 1, y + 1), (x - 1, y - 1)]
        nbrs = list()
        for r in results:
            if r in list(Cell.C.keys()):
                nbrs.append(r)
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

class Zone:
    Z = dict()
    def __init__(self,ID, cells = None, zone_type = None):
        self.ID = ID
        self.cells = dict()
        self.threshold_cells = list()
        self.thresholds = list()
        self.zone_type = zone_type
        self.graph = dict()
        Zone.Z[self.ID] = self

    def highlight_zone(self, screen, drawing_type = None):
        for c in self.cells:
            Cell.C[c].highlight_cell(screen, green, drawing_type = drawing_type)

        for c in self.threshold_cells:
            if Cell.C[c].is_barrier:
                Cell.C[c].highlight_cell(screen, steelblue, drawing_type = drawing_type)            
            if not Cell.C[c].is_barrier:
                Cell.C[c].highlight_cell(screen, darkgreen, drawing_type = drawing_type)
        
    def make_walls(self):
        xs = [x[0] for x in list(self.cells.keys())]
        ys = [x[1] for x in list(self.cells.keys())]
        x_min, x_max = min(xs), max(xs)
        y_min, y_max = min(ys), max(ys)
        t1, t2 = list(), list()
        for i in range(x_min - 1, x_max + 2, 1):
            Cell.C[(i,y_min - 1)].in_threshold = True
            Cell.C[(i,y_max + 1)].in_threshold = True
            self.threshold_cells.append((i, y_min - 1))
            self.threshold_cells.append((i, y_max + 1))        
            t1.append((i, y_min - 1))
            t2.append((i, y_max + 1))
        self.thresholds.append(sorted(t1, key = itemgetter(0)))
        self.thresholds.append(sorted(t2, key = itemgetter(0)))        
        t1, t2 = list(), list()
        for i in range(y_min - 1, y_max + 2, 1):
            Cell.C[(x_min - 1, i)].in_threshold = True
            Cell.C[(x_max + 1, i)].in_threshold = True
            self.threshold_cells.append((x_min - 1, i))    
            self.threshold_cells.append((x_max + 1, i))
            t1.append((x_min - 1, i))
            t2.append((x_max + 1, i))
        self.thresholds.append(sorted(t1, key = itemgetter(1)))
        self.thresholds.append(sorted(t2, key = itemgetter(1)))        

    def refine_thresholds(self):
        for t in self.thresholds:
            if len(t) % 2 == 0:
                for c in t[:len(t)//2 - 2]:
                    Cell.C[c].is_barrier = True
                for c in t[len(t)//2 + 2:]:
                    Cell.C[c].is_barrier = True
            if len(t) % 2 == 1:
                for c in t[:len(t)//2 - 1]:
                    Cell.C[c].is_barrier = True
                for c in t[len(t)//2 + 2:]:
                    Cell.C[c].is_barrier = True
                    
        for t in self.thresholds:
            for c in t:
                if not Cell.C[c].is_barrier:
                    Cell.T[c].append(self.ID)

        for c in self.threshold_cells:
            if Cell.C[c].is_barrier:
                self.threshold_cells.remove(c)
            if not Cell.C[c].is_barrier:
                Cell.C[c].zones.add(self.ID)
                
    def make_search_graph(self):
        cells = list(self.cells.keys()) + list(self.threshold_cells)
        cells = list(set(cells))
        for c in cells:
            self.graph[c] = [i for i in Cell.C[c].neighbours() if not Cell.C[i].is_barrier and (i in cells)]
    

################################################################################
################################################################################
#### ACTOR CLASSES #############################################################
################################################################################
################################################################################


class Actor:
    A = dict()
    def __init__(self, name, x = None, y = None, color = None, zone = None, threshold = None):
        self.name = name
        self.x = x
        self.y = y
        self. threshold = threshold
        if zone is not None:
            self.initialize_in_zone(zone)
            
        self.color = color if color is not None else crimson
        self.zone = zone
        Actor.A[self.name] = self
        Cell.C[(self.x, self.y)].is_occupied = True

    def initialize_in_zone(self, z):
        options = list(set(Zone.Z[z].cells.keys()))
        self.x, self.y = random.choice(options)

    def print_pos(self):
        print(self.name,":",self.x, self.y)
                
    def draw_actor(self, screen):
        center = self.x*Cell.size + Cell.size // 2, self.y*Cell.size + Cell.size // 2
        radius = Cell.size // 2
        pygame.draw.circle(screen, self.color, center, radius)
    
    def move(self, c):
        old = self.x, self.y
        if not Cell.C[c].is_occupied:
            self.x, self.y = c
            Cell.C[old].is_occupied = False
            Cell.C[c].is_occupied = True

    def move_with_keys(self, key):
        pass



class Cockroach:
    Roaches = list()
    Poison = defaultdict(int)

    def __init__(self, x, y, r, poison, color):
        self.x = x
        self.y = y
        self.r = r
        self.poison = poison
        self.color = color
        Cockroach.Poison[(x, y)] = 0
        Cockroach.Roaches.append(self)

    def draw_cockroach(self, screen):
        center = self.x*Cell.size + Cell.size // 2, self.y*Cell.size + Cell.size // 2
        radius = Cell.size // 2
        pygame.draw.circle(screen, self.color, center, radius)

    def move_cockroach(self):
        options = -1, 0, 1
        x = random.choice(options)
        y = random.choice(options)
        old_x, old_y = self.x, self.y
        new_x, new_y = self.x + x, self.y + y
        if (new_x, new_y) in Cell.C.keys() and not Cell.C[(new_x, new_y)].is_barrier:
            if self.poison > 0:
                Cockroach.Poison[(old_x, old_y)] -= (self.poison - 1)
                if Cockroach.Poison[(old_x, old_y)] < 0:
                    Cockroach.Poison[(old_x, old_y)] = 0
            self.x, self.y = new_x, new_y
            Cockroach.Poison[(new_x, new_y)] += self.poison
            if Cockroach.Poison[(new_x, new_y)] < 0:
                Cockroach.Poison[(new_x, new_y)] = 0
            

################################################################################
################################################################################
######## CLASSES FOR SEARCH ####################################################
################################################################################
################################################################################


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


class Search:
   
    def __init__(self, start, goal, graph = None, threshold = None):
        self.start = start
        self.goal = goal
        self.graph = graph
        self.threshold = threshold
        self.open_cells = PriorityQueue()
        self.came_from = dict()
        self.cost_so_far = dict()
        self.path = self.get_path()

    def min_cost(self, a, b):
        x1, y1 = a
        x2, y2 = b
        if abs(y2 - y1) > abs(x2 - x1):
            return 1.4142 * abs(x2 - x1) + 1.0 *abs((abs(y2 - y1) - abs(x2 - x1)))
        elif abs(y2 - y1) < abs(x2 - x1):
            return 1.4142 * abs(y2 - y1) + 1.0 *abs((abs(y2 - y1) - abs(x2 - x1)))
        elif abs(y2 - y1) == abs (x2 - x1):
            return 1.4142 * abs(y2 - y1)

    def get_path(self):
        self.open_cells.put(self.start, 0)
        self.came_from[self.start] = None
        self.cost_so_far[self.start] = 0
        while not self.open_cells.empty():
            current = self.open_cells.get()
            if current in self.graph[self.goal]:
                self.came_from[self.goal] = current
                break
            #Avoid occupied cells.                
            neighbours = [i for i in self.graph[current] if not Cell.C[i].is_occupied]
            #Avoid infested cells.
            neighbours = [i for i in neighbours if Cockroach.Poison[i] <= self.threshold]
            if len(neighbours) > 0:
                for loc in neighbours:
                    new_cost = self.cost_so_far[current] + self.min_cost(current, loc)
                    if loc not in self.cost_so_far or new_cost < self.cost_so_far[loc]:
                        self.cost_so_far[loc] = new_cost
                        priority = new_cost + self.min_cost(current, self.goal)
                        self.open_cells.put(loc, priority)
                        self.came_from[loc] = current
        return self.build_path()                        
            

    def build_path(self):
        path = list()
        goal_nbrs = self.graph[self.goal]
        if self.goal in self.came_from.keys():
            current = self.goal
            path.append(current)
        else:
            return None
        while current != self.start:
            if current in self.came_from:
                current = self.came_from[current]
                path.append(current)
            else:
                path = None
        if path is not None:
            path.reverse()
            self.path = path
            return path
        else:
            return None

    def draw_route(self, screen, color = white):
        draw_this = list()
        for p in self.path:
            draw_this.append(Cell.C[p].rect.center)
        if len(draw_this) >= 2:
            pygame.draw.lines(screen, color, False, draw_this, 1)
