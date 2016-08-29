import sys, time, math, random, heapq, pygame, copy, itertools
from PIL import Image
from operator import itemgetter
from collections import defaultdict
from colors import *



######################################################################################
#######################CLASSES DESCRIBING SPACE: CELL, COLLECTION#####################
######################################################################################


class Cell(object):
    """
    Creates a square cell object of size s pixels at coordinate (x, y)
    """
    C = dict()
    def __init__(self, x, y, s):
        """
        Initializes a cell object at location x, y. The object is a square cell of size s pixels. If the width of the space is w pixels and the height of the space is h pixels, then the location (x,y) of each cell is given by (w/s, h/s)
        """
        self.x = x
        self.y = y
        self.s = s
        self.rect = pygame.Rect(self.x * self.s, self.y * self.s, self.s, self.s)
        self.color = None
        self.is_barrier = False
        self.is_occupied = False
        self.in_zone = False
        self.in_threshold = False
        self.zone = None
        self.threshold = None
        self.nbrs = list()
        self.zones = set()
        
        Cell.C[(self.x, self.y)] = self
        Cell.size = self.s

    def draw(self, screen, drawing_type = None, color = None):
        """
        Draws a cell as a grid square or as a circle. Requires a pygame screen object to be specified. If a color is not specified the native color of the cell (self.color) is used.
        """
        r = max(2, int(Cell.size/2.5))
        if color is None:
            color = self.color
        if drawing_type == "graph":
            pygame.draw.circle(screen, color, (self.x * self.s + int(self.s/2), self.y * self.s + int(self.s/2)), r)
        if drawing_type == "grid":
            pygame.draw.rect(screen, color, self.rect, 1)
        
    def neighbours(self):
        """
        Returns a list of cells neighbouring this cell. von Neumann neighbours are considered.
        """
        x, y = self.x, self.y
        results = [(x + 1, y), (x - 1, y), (x, y + 1), (x, y - 1),
                   (x + 1, y + 1), (x + 1, y - 1), (x - 1, y + 1), (x - 1, y - 1)]
        nbrs = [r for r in results if r in Cell.C.keys()]
        return nbrs

    def orthogonal_neighbours(self):
        """
        Returns a list of cells neighbouring this cell. von Neumann neighbours are considered.
        """
        x, y = self.x, self.y
        results = [(x + 1, y), (x - 1, y), (x, y + 1), (x, y - 1)]
        nbrs = [r for r in results if r in Cell.C.keys()]
        return nbrs

        

    @staticmethod
    def assign_neighbours():
        """
        Stores the neighbours of each cell in the space in the nbrs variable of the space.
        """
        for c in Cell.C:
            Cell.C[c].nbrs = Cell.C[c].neighbours()

    @staticmethod
    def create_space(w, h, s):
        """
        Creates a 2 dimensional array of cells in a space of width w and height h pixels. Each cell is a square of size s pixels. The location of each cell is (w/s, h/s).
        """
        for i in range(int(w/s)):
            for j in range(int(h/s)):
                Cell(i, j, s)
        Cell.assign_neighbours()

    @staticmethod
    def draw_space(screen, drawing_type = "graph", color = None):
        """
        Draws every cell in the dictionary. By default, cells are graph as circles using the "graph" flag for drawing_type.
        """
        for c in Cell.C.keys():
            Cell.C[c].draw(screen, drawing_type = drawing_type, color = color)

    @staticmethod
    def draw_barriers(screen, drawing_type = "graph", color = None):
        """
        Draws every cell in the dictionary. By default, cells are graph as circles using the "graph" flag for drawing_type.
        """
        for c in Cell.C.keys():
            if Cell.C[c].color == (0,0,0):
                Cell.C[c].draw(screen, drawing_type = drawing_type, color = color)


    @staticmethod
    def create_space_from_plan(s, img, spaces = {"threshold":(255,0,0), "wall":(0,0,0), "space": (255, 255, 255), "ignore":(0, 255, 0), "equipment":(255, 255, 0)}):
        """
        Creates a 2 dimensional array of cells in a space of width w and height h pixels. Each size is a square of size s pixels. The keyword argument spaces contains a dictionary of cell types and the colors associated which each cell type. This method adds the correct color classification to each space type based on this dictionary. By default the four types of spaces are defined, and the picture used for this program (the img argument) should be a floor plan containing these four colors.
        'threshold': (255,0,0) [red],
        'wall': (0,0,0) [black],
        'space': (255, 255, 255) [white],
        'ignore': (0, 255, 0) [green]
        'equipment':(255, 255, 0) [yellow]
        Requires PIL (Python Image Library)
        The resulting space has w pixels width and h pixels height, where w and h are the width and height of the picture used as input.
        """
        img = Image.open(img)
        width, height = img.size
        rgbvals = dict()
        distinctvals = set()
        for i in range(width):
            for j in range(height):
                rgbvals[(i,j)] = img.getpixel((i,j))
                if len(rgbvals[(i,j)]) == 4:
                    r,g,b = rgbvals[(i,j)][:-1]
                elif len(rgbvals[(i, j)]) == 3:
                    r,g,b = rgbvals[(i,j)]                    
                r = 1.0*r/(s*s)
                g = 1.0*g/(s*s)
                b = 1.0*b/(s*s)
                rgbvals[(i,j)] = (r, g, b)
                
        for i in range(int(width/s)):
            for j in range(int(height/s)):
                Cell(i, j, s)
                
        for c in Cell.C:
            x1, y1 = Cell.C[c].rect.topleft
            x2, y2 = Cell.C[c].rect.bottomright
            colors = list()
            for i in range(x1, x2):
                for j in range(y1, y2):
                    if (i,j) in rgbvals:
                        colors.append(rgbvals[(i,j)])
            Cell.C[c].color = tuple([int(sum(i)) for i in zip(*colors)])
            distances = list()
            for k in spaces:
                distances.append((Cell.coldist(Cell.C[c].color, spaces[k]), spaces[k]))
            closest = sorted(distances, key = itemgetter(0))[0]
            Cell.C[c].color = closest[1]

        Cell.assign_neighbours()
        return width, height

    @staticmethod
    def coldist(a, b):
        """
        Returns the distance between two three dimensional vectors.
        """
        x1, y1, z1 = a
        x2, y2, z2 = b
        return math.sqrt((x1-x2)**2 + (y1-y2)**2 + (z1-z2)**2)


class Collection(object):
    """
    A Collection of Cells which is either a Threshold or a Zone. Zones are stored in the dictionary Collection.Z, Thresholds are stored in the dictionary Collection.T.
    """
    Z = dict()
    T = dict()
    TG = dict()
    def __init__(self, ID, TYPE):
        self.ID = ID
        self.TYPE = TYPE
        self.cells = set()
        self.graph = dict()
        if self.TYPE == "z":
            Collection.Z[self.ID] = self
            self.thresholds = set()
            self.threshold_cells = set()
        if self.TYPE == "t":
            Collection.T[self.ID] = self
            self.zones = set()
            self.tnbrs = set()

    def create_zone_graph(self):
        all_cells = self.cells.union(self.threshold_cells)
        for c in all_cells:
            self.graph[c] = [i for i in Cell.C[c].nbrs if i in all_cells]

    def draw(self, screen, color = None):
        for c in self.cells:
            if self.TYPE == "z":
                if color is None:
                    Cell.C[c].draw(screen, drawing_type = "graph", color = powderblue)
                else:
                    Cell.C[c].draw(screen, drawing_type = "graph", color = color)                
            if self.TYPE == "t":
                if color is None:
                    Cell.C[c].draw(screen, drawing_type = "graph", color = khaki)            
                else:
                    Cell.C[c].draw(screen, drawing_type = "graph", color = color)                                    

    @staticmethod
    def draw_everything(screen, color = None):     
        for z in Collection.Z:
            for c in Collection.Z[z].cells:
                if color is None:
                    Cell.C[c].draw(screen, drawing_type = "graph", color = powderblue)
                else:
                    Cell.C[c].draw(screen, drawing_type = "graph", color = color)                

        for t in Collection.T:
            for c in Collection.T[t].cells:        
                if color is None:
                    Cell.C[c].draw(screen, drawing_type = "graph", color = khaki)
                else:
                    Cell.C[c].draw(screen, drawing_type = "graph", color = color)                
                                                


    @staticmethod
    def generate_zones_and_thresholds():
        zone_cells = set()
        threshold_cells = set()
        for c in Cell.C.keys():
            if Cell.C[c].color == (255, 255, 255):
                zone_cells.add(c)
            if Cell.C[c].color == (255, 0, 0):
                threshold_cells.add(c)                

        num = 0
        while len(zone_cells) > 0:    
            cells = Collection.collect(zone_cells)
            zone = Collection(str(num), "z")
            zone.cells = cells
            for cell in zone.cells:
                Cell.C[cell].in_zone = True
                Cell.C[cell].zone = str(num)
            zone_cells = zone_cells.difference(cells)
            num += 1

        num = 0
        while len(threshold_cells) > 0:    
            cells = Collection.collect(threshold_cells)
            threshold = Collection(str(num), "t")
            threshold.cells = cells
            for cell in threshold.cells:
                Cell.C[cell].in_threshold = True
                Cell.C[cell].threshold = str(num)
            threshold_cells = threshold_cells.difference(cells)
            num += 1

                
    @staticmethod
    def collect(zone_cells):
        p = random.choice(list(zone_cells))
        new_zone = set()
        c = list(p)
        while tuple(c) in zone_cells:
            new_zone.add(tuple(c))
            c[0] = c[0] - 1

        c = list(p)
        while tuple(c) in zone_cells:
            new_zone.add(tuple(c))
            c[0] = c[0] + 1
        
        first_row = copy.copy(new_zone)
        for cell in first_row:
            x = list(cell)
            while tuple(x) in zone_cells:
                new_zone.add(tuple(x))
                x[1] = x[1] + 1

            x = list(cell)
            while tuple(x) in zone_cells:
                new_zone.add(tuple(x))
                x[1] = x[1] - 1
            
        cells = new_zone
        return cells

    @staticmethod
    def correct_cell_allocation():
        cwb = dict()
        for z in Collection.Z.keys():
            cells = Collection.Z[z].cells
            cells_with_neighbours = list()
            for c in cells:
                cells_with_neighbours += [i for i in Cell.C[c].nbrs if (Cell.C[i].in_zone and not Cell.C[i].in_threshold and not Cell.C[i].is_barrier)]
            cwb[z] = set(cells_with_neighbours)
        combos = itertools.combinations(cwb.keys(), 2)
        tbr = set()
        for (a,b) in combos:
            common = cwb[a].intersection(cwb[b])
            if len(common) > 0:
                nid = str(min(int(a), int(b)))
                rem = str(max(int(a), int(b)))
                new_collection = Collection.Z[a].cells.union(Collection.Z[b].cells)
                Collection.Z[nid].cells = new_collection
                for cell in Collection.Z[nid].cells:
                    Cell.C[cell].in_zone = True
                    Cell.C[cell].zone = nid
                tbr.add(rem)

        for k in tbr:
            del Collection.Z[k]

        cwb = dict()
        for t in Collection.T.keys():
            cells = Collection.T[t].cells
            cells_with_neighbours = list()
            for c in cells:
                cells_with_neighbours += [i for i in Cell.C[c].orthogonal_neighbours() if (Cell.C[i].in_threshold and not Cell.C[i].in_zone and not Cell.C[i].is_barrier)]
            cwb[t] = set(cells_with_neighbours)
        combos = itertools.combinations(cwb.keys(), 2)
        tbr = set()
        for (a,b) in combos:
            common = cwb[a].intersection(cwb[b])
            if len(common) > 0:
                nid = str(min(int(a), int(b)))
                rem = str(max(int(a), int(b)))
                new_collection = Collection.T[a].cells.union(Collection.T[b].cells)
                Collection.T[nid].cells = new_collection
                for cell in Collection.T[nid].cells:
                    Cell.C[cell].in_threshold = True
                    Cell.C[cell].threshold = nid
                tbr.add(rem)

        for k in tbr:
            del Collection.T[k]

        for z in Collection.Z.keys():
            for c in Collection.Z[z].cells:
                Cell.C[c].in_zone = True
                Cell.C[c].zone = z
                Cell.C[c].in_threshold = False
           
        for t in Collection.T.keys():
            for c in Collection.T[t].cells:
                Cell.C[c].in_threshold = True
                Cell.C[c].threshold = t
                Cell.C[c].in_zone = False
                
        for z in Collection.Z.keys():
            for c in Collection.Z[z].cells:
                for n in Cell.C[c].nbrs:
                    if not Cell.C[n].is_barrier and Cell.C[n].in_threshold:
                        Collection.Z[z].thresholds.add(Cell.C[n].threshold)
                        Collection.Z[z].threshold_cells.add(n)
                        Cell.C[n].zones.add(z)
                        
        for t in Collection.T.keys():
            for c in Collection.T[t].cells:
                for n in Cell.C[c].nbrs:
                    if not Cell.C[n].is_barrier and Cell.C[n].in_zone:
                        Collection.T[t].zones.add(Cell.C[n].zone)
                        
        for t in Collection.T.keys():
            tnbrs = set()
            for z in Collection.T[t].zones:
                if z in Collection.Z.keys():
                    for threshold in Collection.Z[z].thresholds:
                        if threshold != t and threshold in Collection.T.keys():
                            tnbrs.add(threshold)
            Collection.T[t].tnbrs = tnbrs


    @staticmethod
    def create_threshold_graph():
        for t in Collection.T.keys():
            cells = set()
            for n in Collection.T[t].tnbrs:
                cells = cells.union(Collection.T[n].cells)
            for c in Collection.T[t].cells:
                Collection.TG[c] = cells

    @staticmethod
    def create_zone_graphs():
        for z in Collection.Z.keys():
            Collection.Z[z].create_zone_graph()
               
        
######################################################################################
#######################CLASSES DESCRIBING ACTORS: ACTOR, COCKROACHES #################
######################################################################################

class Actor(object):
    A = dict()
    def __init__(self, name, x = None, y = None, color = None, zone = None, threshold = None, facing = (1,0)):
        self.name = name
        self.x = x
        self.y = y
        self.color = color
        if zone is not None:
            self.initialize_in_zone(zone)
        self.zone = zone
        self.color = color if color is not None else crimson
        self.threshold = threshold
        self.facing = facing
        Actor.A[self.name] = self
        Cell.C[(self.x, self.y)].is_occupied = True

    def initialize_in_zone(self, z):
        options = set(Collection.Z[z].cells)
        ox, oy = self.x, self.y
        self.x, self.y = random.choice([i for i in list(options) if not Cell.C[i].is_occupied])
        self.zone = Cell.C[(self.x, self.y)].zone
        if ox is not None and oy is not None:
            Cell.C[(ox, oy)].is_occupied = False
        Cell.C[(self.x, self.y)].is_occupied = True

    def move(self, c):
        ox, oy = self.x, self.y
        cx, cy = c
        if not Cell.C[(cx, cy)].is_occupied:
            self.x, self.y = cx, cy
            Cell.C[(ox, oy)].is_occupied = False
            Cell.C[(self.x, self.y)].is_occupied = True

    def draw(self, screen, min_size = 4):
        center = self.x*Cell.size + Cell.size // 2, self.y*Cell.size + Cell.size // 2
        radius = max(min_size, int(Cell.size/2))        
        pygame.draw.circle(screen, self.color, center, radius)
        

################################################################################
######## CLASSES FOR SEARCH ####################################################
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
            neighbours = (i for i in self.graph[current] if not Cell.C[i].is_occupied)
            #Avoid infested cells.
#            neighbours = (i for i in neighbours if Cockroach.Poison[i] <= self.threshold)
            if neighbours is not None:
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
        draw_this = [Cell.C[p].rect.center for p in self.path]
        if len(draw_this) >= 2:
            pygame.draw.lines(screen, color, False, draw_this, 1)
