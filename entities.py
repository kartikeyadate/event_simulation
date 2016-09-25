#j/usr/bin/python3.5 
#entities.py This file contains class definitions for the Cell, Collection, Actor, Target, Move, Meet and Search 
import sys, time, math, random, heapq, pygame, copy, itertools
from PIL import Image
from operator import itemgetter
from collections import defaultdict
from colors import *

################################################################################
#######################CLASSES DESCRIBING SPACE: CELL, COLLECTION###############
################################################################################
class Cell(object):
    """
    Creates a square cell object of size s pixels at coordinate (x, y)
    """
    C = dict()
    def __init__(self, x, y, s):
        """
        Initializes a cell object at location x, y.
        The object is a square cell of size s pixels.
        If the width of the space is w pixels and the height of the space is h pixels,
        then the location (x,y) of each cell is given by (w/s, h/s)
        """
        self.x = x
        self.y = y
        self.s = s
        self.rect = pygame.Rect(self.x * self.s, self.y * self.s, self.s, self.s)
        self.color = None
        self.is_barrier = False
        self.is_occupied = False
        self.is_personal =False
        self.in_zone = False
        self.in_threshold = False
        self.zone = None
        self.threshold = None
        self.nbrs = list()
        self.zones = set()
        self.poison = 0

        Cell.C[(self.x, self.y)] = self
        Cell.size = self.s

    def draw(self, screen, drawing_type = None, color = None):
        """
        Draws a cell as a grid square or as a circle.
        Requires a pygame screen object to be specified.
        If a color is not specified the native color (self.color) is used.
        """
        r = max(2, int(Cell.size/2.5))
        if color is None:
            color = self.color
        if drawing_type == "graph":
            pygame.draw.circle(screen, color, (self.x * self.s + int(self.s/2), self.y * self.s + int(self.s/2)), r)
        if drawing_type == "grid":
            pygame.draw.rect(screen, color, self.rect, 1)

    def __repr__(self):
        if self.in_threshold:
            return "Location: " + '('+str(self.x)\
            + ', ' + str(self.y) + '); In threshold '\
            + str(self.threshold) + "; Adjacent Zones : "\
            + ', '.join([str(i) for i in self.zones])
        if self.in_zone:
            return "Location: " + '('+str(self.x) + ', ' + str(self.y) + '); In zone '\
            + str(self.zone) + "; Adjacent thresholds: "\
            + ', '.join([str(i) for i in Collection.Z[self.zone].thresholds])\
            + "; Actors: "\
            + ', '.join([str(i) for i in Collection.Z[self.zone].actors])
        if not self.in_zone and not self.in_threshold:
            return "Location: " + '('+str(self.x) + ', ' + str(self.y) + ')'

    def neighbours(self, radius = 1):
        """
        Returns a list of cells neighbouring this cell.
        Moore neighbours are considered.
        """
        x, y = self.x, self.y
        results = [(x + 1, y), (x - 1, y), (x, y + 1), (x, y - 1), (x + 1, y + 1), (x + 1, y - 1), (x - 1, y + 1), (x - 1, y - 1)]
        if radius == 2:
            for r in results:
                a, b = r
                results += [(a + 1, b), (a - 1, b), (a, b + 1), (a, b - 1), (a + 1, b + 1), (a + 1, b - 1), (a - 1, b + 1), (a - 1, b - 1)]
            results = list(set(results))
        nbrs = [r for r in results if r in Cell.C.keys()]
        return nbrs

    def orthogonal_neighbours(self, radius = 1):
        """
        Returns a list of cells von Neumann neighbours this cell.
        """
        x, y = self.x, self.y
        results = [(x + 1, y), (x - 1, y), (x, y + 1), (x, y - 1)]
        if radius == 2:
            for r in results:
                a, b = r
                results += [(a + 1, b), (a - 1, b), (a, b + 1), (a, b - 1)]
            results = list(set(results))
        nbrs = [r for r in results if r in Cell.C.keys()]
        return nbrs

    @staticmethod
    def assign_neighbours():
        """
        Stores the neighbours of each cell in the space in the nbrs
        variable of the space.
        """
        for c in Cell.C:
            Cell.C[c].nbrs = Cell.C[c].neighbours()

    @staticmethod
    def create_space(w, h, s):
        """
        Creates a 2 dimensional array of cells in a space of
        width w and height h pixels. Each cell is a square of size s pixels.
        The location of each cell is (w/s, h/s).
        """
        for i in range(int(w/s)):
            for j in range(int(h/s)):
                Cell(i, j, s)
        Cell.assign_neighbours()

    @staticmethod
    def draw_space(screen, drawing_type = "graph", color = None):
        """
        Draws every cell in the dictionary.
        By default, cells are graph as circles
        using the "graph" flag for drawing_type.
        """
        for c in Cell.C.keys():
            Cell.C[c].draw(screen, drawing_type = drawing_type, color = color)

    @staticmethod
    def draw_barriers(screen, drawing_type = "graph", color = None):
        """
        Draws all barrier cells.
        """
        for c in Cell.C.keys():
            if Cell.C[c].is_barrier:
                Cell.C[c].draw(screen, drawing_type = drawing_type, color = color)

    @staticmethod
    def create_space_from_plan(s, img, spaces = {"threshold":(255,0,0), "wall":(0,0,0), "space": (255, 255, 255), "ignore":(0, 255, 0), "equipment":(255, 255, 0)}):
        """
        Creates a 2 dimensional array of cells in a space of width w and height h pixels.
        Each size is a square of size s pixels. T
        he keyword argument spaces contains a dictionary of cell types
        and the colors associated which each cell type.
        This method adds the correct color classification to each space type
        based on this dictionary.
        By default the four types of spaces are defined, and the picture
        used for this program (the img argument) should be a floor plan
        containing these four colors.
        'threshold': (255,0,0) [red],
        'wall': (0,0,0) [black],
        'space': (255, 255, 255) [white],
        'ignore': (0, 255, 0) [green]
        'equipment':(255, 255, 0) [yellow]
        Requires PIL (Python Image Library)
        The resulting space has w pixels width and h pixels height,
        where w and h are the width and height of the picture used as input.
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
            #Set walls.
            if Cell.C[c].color == (0, 0, 0):
                Cell.C[c].is_barrier = True

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
    A Collection of Cells which is either a Threshold or a Zone.
    Zones are stored in the dictionary Collection.Z,
    Thresholds are stored in the dictionary Collection.T.
    """
    Z = dict()
    T = dict()
    TG = dict()
    def __init__(self, ID, TYPE):
        self.ID = ID
        self.TYPE = TYPE
        self.cells = set() #keys (x,y) of cells in collection
        self.center = None
        self.graph = dict() #search graph for a zone.
        self.thresholds = set() #thresholds attached to current zone.
        self.threshold_cells = set() #keys (x,y) of cells contained in thresholds attached to current zone.
        self.zones = set() #zones connected by current threshold (if collection is a threshold)
        self.tnbrs = set() #neighbouring thresholds for current threshold (if collection is threshold)
        self.available = True #whether of not the current threshold is available to the search.
        self.actors = set()
        if self.TYPE == "t":
            Collection.T[self.ID] = self
        if self.TYPE == "z":
            Collection.Z[self.ID] = self

    def __repr__(self):
        if self.TYPE == "t":
            return "Type: " + self.TYPE + '; ID: ' + self.ID + "; Zones: " + ', '.join([i for i in self.zones])
        elif self.TYPE == "z":
            return "Type: " + self.TYPE + '; ID: ' + self.ID + "; Thresholds: " + ', '.join([i for i in self.thresholds]) + "; Actors: " + ', '.join([i for i in self.actors])

    def create_zone_graph(self):
        """
        Create a cell-neighbour graph.
        """
        all_cells = self.cells.union(self.threshold_cells)
        for c in all_cells:
            self.graph[c] = [i for i in Cell.C[c].nbrs if i in all_cells and not Cell.C[i].is_barrier]
        xs = [i[0] for i in self.cells]
        ys = [i[1] for i in self.cells]
        xmid = int(0.5*(max(xs) + min(xs)))
        ymid = int(0.5*(max(ys) + min(ys)))
        self.center = (xmid*Cell.size, ymid*Cell.size)

    def draw(self, screen, color = None):
        """Draw this collection"""
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
        """
        Draws all zones.
        """
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

        num =0
        while len(zone_cells) > 0:
            cells = Collection.alt_collect(zone_cells)
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

        Collection.correct_cell_allocation()
        Collection.create_threshold_graph()
        Collection.create_zone_graphs()

    @staticmethod
    def add_orthogonal(p, zone_cells):
        orthos = set()
        c = list(p)
        while tuple(c) in zone_cells:
            orthos.add(tuple(c))
            c[0] = c[0] + 1

        c = list(p)
        while tuple(c) in zone_cells:
            orthos.add(tuple(c))
            c[0] = c[0] - 1

        c = list(p)
        while tuple(c) in zone_cells:
            orthos.add(tuple(c))
            c[1] = c[1] - 1

        c = list(p)
        while tuple(c) in zone_cells:
            orthos.add(tuple(c))
            c[1] = c[1] + 1

        return orthos

    @staticmethod
    def alt_collect(zone_cells):
        p = sorted(list(zone_cells), key = itemgetter(0,1))[0]
        cells = set()
        c = list(p)
        while tuple(c) in zone_cells:
            orthos = Collection.add_orthogonal(tuple(c), zone_cells)
            cells = cells.union(orthos)
            c[0] = c[0] + 1
            c[1] = c[1] + 1

        c = list(p)
        while tuple(c) in zone_cells:
            orthos = Collection.add_orthogonal(tuple(c), zone_cells)
            cells = cells.union(orthos)
            c[0] = c[0] - 1
            c[1] = c[1] + 1

        c = list(p)
        while tuple(c) in zone_cells:
            orthos = Collection.add_orthogonal(tuple(c), zone_cells)
            cells = cells.union(orthos)
            c[0] = c[0] - 1
            c[1] = c[1] - 1

        c = list(p)
        while tuple(c) in zone_cells:
            orthos = Collection.add_orthogonal(tuple(c), zone_cells)
            cells = cells.union(orthos)
            c[0] = c[0] + 1
            c[1] = c[1] - 1

        return cells

    @staticmethod
    def collect(zone_cells):
        p = sorted(list(zone_cells), key = itemgetter(0,1))[0]
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
        #Work on zones first.
        cwb = dict()
        for z in Collection.Z.keys():
            cells_with_neighbours = list()
            for c in Collection.Z[z].cells:
                cells_with_neighbours += [i for i in Cell.C[c].nbrs if (Cell.C[i].in_zone and not Cell.C[i].in_threshold and not Cell.C[i].is_barrier)]
            cwb[z] = set(cells_with_neighbours)

        combos = itertools.combinations(cwb.keys(), 2)
        rem = set()
        for (a,b) in combos:
            if len(cwb[a].intersection(cwb[b])) > 0:
                if str(min(int(a), int(b))) == a:
                    Collection.Z[a].cells = Collection.Z[a].cells.union(Collection.Z[b].cells)
                    cwb[a] = cwb[a].union(cwb[b])
                    rem.add(b)
                elif str(min(int(a), int(b))) == b:
                    Collection.Z[b].cells = Collection.Z[b].cells.union(Collection.Z[a].cells)
                    cwb[b] = cwb[b].union(cwb[a])
                    rem.add(a)

        for k in rem:
            del Collection.Z[k]

        cwb = dict()
        for t in Collection.T.keys():
            cells = Collection.T[t].cells
            cells_with_neighbours = list()
            for c in cells:
                cells_with_neighbours += [i for i in Cell.C[c].orthogonal_neighbours() if (Cell.C[i].in_threshold and not Cell.C[i].in_zone and not Cell.C[i].is_barrier)]
            cwb[t] = set(cells_with_neighbours)

        combos = itertools.combinations(cwb.keys(), 2)
        rem = set()
        for (a,b) in combos:
            if len(cwb[a].intersection(cwb[b])) > 0:
                if str(min(int(a), int(b))) == a:
                    Collection.T[a].cells = Collection.T[a].cells.union(Collection.T[b].cells)
                    cwb[a] = cwb[a].union(cwb[b])
                    rem.add(b)
                elif str(min(int(a), int(b))) == b:
                    Collection.T[b].cells = Collection.T[b].cells.union(Collection.T[a].cells)
                    cwb[b] = cwb[b].union(cwb[a])
                    rem.add(a)

        for k in rem:
            del Collection.T[k]

        for z in Collection.Z.keys():
            for c in Collection.Z[z].cells:
                Cell.C[c].in_zone = True
                Cell.C[c].zone = z
                Cell.C[c].in_threshold = False
                Cell.C[c].threshold = None

        for t in Collection.T.keys():
            for c in Collection.T[t].cells:
                Cell.C[c].in_threshold = True
                Cell.C[c].threshold = t
                Cell.C[c].in_zone = False
                Cell.C[c].zone = None

        #So far, we have organized all the cells in the space into thresholds and zones.
        #Next, we have to store the thresholds neighbouring each zone.
        #All neighbouring cells of a cell in zone which are threshold_cells
        #need not constitute all the threshold cells in the zone.
        #So, use the threshold_cell found to identify the threshold.
        #The use threshold.cells to find all threshold cells.

        for z in Collection.Z.keys():
            for c in Collection.Z[z].cells:
                for n in Cell.C[c].nbrs:
                    if Cell.C[n].in_threshold:
                        t = Cell.C[n].threshold
                        if t in Collection.T.keys():
                            th_cells = Collection.T[t].cells
                            Collection.Z[z].thresholds.add(t)
                            Collection.Z[z].threshold_cells = Collection.Z[z].threshold_cells.union(th_cells)

        #For every zone, the thresholds connected to it and the threshold cells attached to it are now stored.

        for t in Collection.T.keys():
            for c in Collection.T[t].cells:
                for n in Cell.C[c].nbrs:
                    if Cell.C[n].in_zone:
                        Collection.T[t].zones.add(Cell.C[n].zone)

            for c in Collection.T[t].cells:
                Cell.C[c].zones = Collection.T[t].zones

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
            for z in Collection.T[t].zones:
                if z in Collection.Z.keys():
                    cells = cells.union(Collection.Z[z].threshold_cells)
            cells = cells.difference(Collection.T[t].cells)
            for c in Collection.T[t].cells:
                Collection.TG[c] = cells

    @staticmethod
    def create_zone_graphs():
        for z in Collection.Z.keys():
            Collection.Z[z].create_zone_graph()


################################################################################
#######################CLASSES DESCRIBING ACTORS: ACTOR, COCKROACHES ###########
################################################################################

class Actor(object):
    """
    Definition of the actor.
    """
    A = dict()
    def __init__(self, name, x = None, y = None, color = None, zone = None, threshold = None, facing = (1,0), unavailable = set(), actor_type = None, sociability = random.choice([0.5, 0.6,0.7,0.8,0.9,1.0]), friends = set()):
        self.name = name
        self.actor_type = actor_type
        self.friends = friends
        self.sociability = sociability
        self.in_meeting = False
        self.x = x
        self.y = y
        self.color = color
        self.personal_space = set()
        if zone is not None and self.x is None and self.y is None:
            self.initialize_in_zone(zone)
        self.zone = zone
        Collection.Z[self.zone].actors.add(self.name)
        self.color = color if color is not None else crimson
        self.threshold = threshold
        if self.threshold is not None:
            Collection.T[self.threshold].actors.add(self.name)
        self.facing = facing
        self.unavailable = set()
        self.set_personal_space()
        Actor.A[self.name] = self
        Cell.C[(self.x, self.y)].is_occupied = True

    def initialize_in_zone(self, z):
        """
        If a zone is specified, this initializes the actor in a randomly chosen position in this zone.
        """
        options = Collection.Z[z].cells
        ox, oy = self.x, self.y
        if ox is not None and oy is not None:
            self.remove_personal_space()
        self.x, self.y = random.choice([i for i in list(options) if not Cell.C[i].is_occupied])
        self.zone = Cell.C[(self.x, self.y)].zone
        if ox is not None and oy is not None:
            Cell.C[(ox, oy)].is_occupied = False
        Cell.C[(self.x, self.y)].is_occupied = True
        self.set_personal_space()

    def remove_personal_space(self):
        """
        Removes the personal space of the actor in the current position.
        """
        for c in Cell.C[(self.x, self.y)].nbrs:
            if not Cell.C[c].is_barrier:
                if Cell.C[c].in_threshold or Cell.C[c].in_zone:
                    Cell.C[c].is_personal = False
                    if c in self.personal_space:
                        self.personal_space.remove(c)

    def set_personal_space(self):
        """
        Sets the personal space of the actor in current position.
        Currently, personal space is the Moore neighbourhood of the current position.
        """
        for c in Cell.C[(self.x, self.y)].nbrs:
            if not Cell.C[c].is_barrier:
                if Cell.C[c].in_threshold or Cell.C[c].in_zone:
                    Cell.C[c].is_personal = True
                    self.personal_space.add(c)

    def add_friends(self, friends):
        if type(friends) == set:
            for f in friends:
                print(f)
                self.friends.add(f)
        if type(friends) == str:
            self.friends.add(friends)

    def move(self, c):
        """
        Movess actor from current position to a new position c.
        """
        ox, oy = self.x, self.y
        cx, cy = c
        if not Cell.C[(cx, cy)].is_occupied:
            self.remove_personal_space()
            self.x, self.y = cx, cy
            self.set_personal_space()
            Cell.C[(ox, oy)].is_occupied = False
            Cell.C[(self.x, self.y)].is_occupied = True
            old_z = Cell.C[(ox, oy)].zone
            self.zone = Cell.C[(self.x, self.y)].zone

            # update the zone's information about the actors in it.
            if old_z != self.zone:
                if self.zone is not None:
                    Collection.Z[self.zone].actors.add(self.name)
                if old_z is not None and self.name in Collection.Z[old_z].actors:
                    Collection.Z[old_z].actors.remove(self.name)

            # update the threshold's information about the actors in it.
            old_t = Cell.C[(ox, oy)].threshold
            self.threshold = Cell.C[(self.x, self.y)].threshold
            if old_t != self.threshold:
                if self.threshold is not None:
                    Collection.T[self.threshold].actors.add(self.name)
                if old_t is not None and self.name is Collection.T[old_t].actors:
                    Collection.T[old_t].actors.remove(self.name)

    def kill(self):
        """
        Destroy actor object and remove it from Actor.A dictionary.
        """
        if self.zone is not None:
            if self.name in Collection.Z[self.zone].actors:
                Collection.Z[self.zone].actors.remove(self.name)

        if self.threshold is not None:
            if self.name in Collection.T[self.threshold].actors:
                Collection.T[self.threshold].actors.remove(self.name)

        Cell.C[(self.x, self.y)].is_occupied = False
        self.remove_personal_space()
        del Actor.A[self.name]
        del self

    def draw(self, screen, min_size = 4):
        """
        Draws this object in pygame as a circle or radius min_size
        Requires a screen object.
        """
        center = self.x*Cell.size + Cell.size // 2, self.y*Cell.size + Cell.size // 2
        radius = max(min_size, int(Cell.size/2))
        pygame.draw.circle(screen, self.color, center, radius)

        if self.in_meeting:
            color = gold
        else:
            color = tomato

        for c in self.personal_space:
            Cell.C[c].draw(screen, drawing_type = "graph", color = color)

    @staticmethod
    def draw_all_actors(screen, min_size = 4):
        """
        Draws all actors in the Actor.A dictionary.
        Requires a screen object.
        The minimum size of each actor can be specified in min_size.
        """
        for a in Actor.A:
            Actor.A[a].draw(screen, min_size = min_size)

    @staticmethod
    def update_zones():
        for a in Actor.A:
            if Actor.A[a].zone is None:
                c = Actor.A[a].x, Actor.A[a].y
                print(Cell.C[c].zones)

class Target:
    """Defines a target cell. Target cells are not occupied."""
    T = dict()
    def __init__(self, name, x = None, y = None, zone = None):
        self.x = x
        self.y = y
        self.name = name
        self.zone = zone
        if self.x is None and self.y is None:
            self.initialize()
        Target.T[self.name] = self

    def initialize(self):
        """
        If a cell location is not specified, initializes in a random cell in given zone.
        If a zone is not specified, initializes in a randomly chosen zone from available zones.
        """
        if self.zone is not None:
            options = Collection.Z[self.zone].cells
            ox, oy = self.x, self.y
            self.x, self.y = random.choice([i for i in list(options) if not Cell.C[i].is_occupied])
        elif self.zone is None:
            possible_zones = [i for i in Collection.Z.keys()]
            self.zone = random.choice(possible_zones)
            self.x, self.y = random.choice([i for i in list(options) if not Cell.C[i].is_occupied])

################################################################################
######## CLASSES FOR SEARCH ####################################################
################################################################################

class PriorityQueue:
    """
    A wrapper class around python's heapq class.
    An instance of this class is used to store the list of open cells.
    """

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
    """
    A definition of the A* search algorithm.
    Based on Amit Patel's description and implementation.
    See:W://www-cs-students.stanford.edu/~amitp/gameprog.html
    Is used to conduct the threshold and zone searches in Move.
    start: a tuple (x, y)
    goal: a tuple (x, y)
    graph: A dictionary of each node and its neighbours
    """
    def __init__(self, start, goal, graph = None, threshold = None, ignore = set()):
        self.start = start
        self.goal = goal
        self.graph = graph
        self.threshold = threshold #the name of this element of the search object should be changed. Could be confused with the space element threshold.
        self.open_cells = PriorityQueue()
        self.came_from = dict()
        self.cost_so_far = dict()
        self.ignore = ignore
        self.path = self.get_path()

    def min_cost(self, a, b):
        """
        Returns the smallest distance between cells a and b.
        Orthogonals and diagonals are considered.
        """
        x1, y1 = a
        x2, y2 = b
        if abs(y2 - y1) > abs(x2 - x1):
            return 1.4142 * abs(x2 - x1) + 1.0 *abs((abs(y2 - y1) - abs(x2 - x1)))
        elif abs(y2 - y1) < abs(x2 - x1):
            return 1.4142 * abs(y2 - y1) + 1.0 *abs((abs(y2 - y1) - abs(x2 - x1)))
        elif abs(y2 - y1) == abs (x2 - x1):
            return 1.4142 * abs(y2 - y1)

    def get_path(self):
        """
        Returns a list of cells which is the shortest path between the start and the goal.
        If a path is not available, returns None.
        Ignores cells in the ignore set if specified.
        Ignores occupied cells.
        """
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
            neighbours = (i for i in neighbours if not i in self.ignore)
            #Avoid infested cells.
            #Neighbours = (i for i in neighbours if Cockroach.Poison[i] <= self.threshold)
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
        """
        Returns a path in the form of a list of cells.
        Is used at the end of the get_path method.
        If private functions were possible, this would be one.
        Returns None if a path is not available.
        """
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
        """
        Draws the path, if available in self.path in pygame.
        Requires a screen object as argument.
        The color of the line can be specified in the color keyword argument.
        """
        draw_this = [Cell.C[p].rect.center for p in self.path]
        if len(draw_this) > 1:
            pygame.draw.lines(screen, color, False, draw_this, 1)

######################################################################################################
###################################### EVENT CLASSES #################################################
class Spawn:
    def __init__(self, name=None, color=khaki, tf=None, start_in=None, target=None, screen=None, interval=range(5, 60), unavailable=None, actor_type=None, graph=None):
        self.name = name
        self.color = color
        self.tf = tf
        self.start_in = start_in
        self.target = target
        self.screen = screen
        self.interval = interval
        self.unavailable = unavailable
        self.actor_type = actor_type
        self.graph = graph
        self.go()

    def go(self):
        num = int(self.name)
        inter = random.choice(self.interval)
        if self.tf % inter == 0:
            v_name = str(num) + "_" + self.actor_type
            Actor(v_name, zone = self.start_in, color = self.color, actor_type = self.actor_type)
            num += 1

        done = set()
        for actor in Actor.A.keys():
            if Actor.A[actor].actor_type == self.actor_type:
                if(Actor.A[actor].x, Actor.A[actor].y) in Cell.C[(self.target.x, self.target.y)].nbrs:
                    done.add(actor)

        for d in done:
            Actor.A[d].kill()
            print("Killed", d)

        for actor in Actor.A.keys():
            if Actor.A[actor].actor_type == self.actor_type:
                Move(Actor.A[actor], self.target, self.screen, self.graph, self.unavailable)

        self.name = str(num)

class Move:
    def __init__(self, actor, target, screen, graph=dict(), unavailable=set()):
        self.actor = actor
        self.target = target
        self.screen = screen
        self.graph = graph
        self.unavailable = unavailable
        self.done = self.check_done()
        self.go()

    def check_done(self):
        return (self.actor.x, self.actor.y) in Cell.C[(self.target.x, self.target.y)].nbrs

    def go(self, ignore=set()):
        if not self.actor.in_meeting:
            if self.actor.zone == self.target.zone:
                ZS = self.zone_search((self.actor.x, self.actor.y), (self.target.x, self.target.y), ignore=ignore)
                if ZS.path is not None and len(ZS.path) > 1:
                    ZS.draw_route(self.screen, color=red)
                    self.actor.move(ZS.path[1])
                    ZS.path.pop(0)

            elif self.actor.zone != self.target.zone:
                S = self.threshold_search()
                if S.path is not None:
                    S.draw_route(self.screen, color=verylightgrey)
                    ZS = self.zone_search(S.path[0], S.path[1], ignore=ignore)
                    if ZS.path is None:
                        ignore.add(S.path[1])
                        options = [i for i in Cell.C[S.path[1]].nbrs if Cell.C[i].in_threshold]
                        if len(options) > 0:
                            ZS = self.zone_search(S.path[0], options[0], ignore=ignore)

                    if ZS.path is not None:
                        ZS.draw_route(self.screen, color=red)
                        self.actor.move(ZS.path[1])
                        ZS.path.pop(0)

    def threshold_search(self, ignore=set()):
        A = self.actor.x, self.actor.y
        B = self.target.x, self.target.y

        #Avoid stepping into other actors' personal space.
        for actor in Actor.A.keys():
            if actor != self.actor.name and actor != self.target.name:
                if Actor.A[actor].threshold is not None:
                    ignore = ignore.union(Actor.A[actor].personal_space)
                if Actor.A[actor].zone is not None:
                    z = Actor.A[actor].zone
                    intersect = Actor.A[actor].personal_space.intersection(Collection.Z[z].threshold_cells)
                    if len(intersect) > 0:
                        ignore = ignore.union(intersect)


        #Avoid using zones which are unavailable.
        for u in self.unavailable:
            for c in Collection.Z[u].threshold_cells:
                ignore.add(c)

        if A not in self.graph:
            self.graph[A] = [i for i in Collection.Z[Cell.C[A].zone].threshold_cells]
        if B not in self.graph:
            self.graph[B] = [i for i in Collection.Z[Cell.C[B].zone].threshold_cells]

        return Search(A, B, graph=self.graph, ignore=ignore)

    def zone_search(self, a, b, ignore=set()):
        zone = self.get_zone(a, b)
        if zone is None:
            print("Valid zone was not returned!")
        for actor in Collection.Z[zone].actors:
            if actor != self.actor.name and actor != self.target.name:
                ignore = ignore.union(Actor.A[actor].personal_space)

        return Search(a, b, graph=Collection.Z[zone].graph, ignore=ignore)

    def get_zone(self, start, target):
        if not Cell.C[start].zones.isdisjoint(Cell.C[target].zones):
            if Cell.C[start].zone is not None:
                return Cell.C[start].zone
            elif Cell.C[start].zone is None and Cell.C[target].zone is not None:
                return Cell.C[target].zone
            else:
                return list(Cell.C[start].zones.intersection(Cell.C[target].zones))[0]

        elif Cell.C[start].zones.isdisjoint(Cell.C[target].zones):
            if Cell.C[start].zone is not None:
                return Cell.C[start].zone
            if Cell.C[target].zone is not None:
                return Cell.C[target].zone

class Unplanned:
    """
    Checks all the actors for all possible meetings between 2 actors.
    The conditions required to satisfy a meeting are:
    1. both actors in question should not be in a meeting.
    2. the actors' personal space should overlap.
    """
    M = dict()
    Completed = set()
    def __init__(self, ID, actors=set(), duration=25, status="not_initialized"):
        """
        Initialize a meeting object
        """
        self.ID = ID
        self.actors = actors
        self.duration = duration
        self.status = status
        self.state = 0
        Unplanned.M[self.ID] = self

    def update(self, step = 1):
        """
        Update the status of a meeting.
        The status is an integer.
        If the status is equal to the assigned duration,
        the status of the meeting is changed to 'completed'.
        If status is greater than zero and less and duration,
        the status of the meeting is 'in_progress'.
        """
        self.state += step
        if self.state < self.duration:
            self.status = "in_progress"
        elif self.state >= self.duration:
            self.status = "completed"
        else:
            self.status = "not_initialized"

    def report_status(self):
        """ Report current status of the meeting."""
        return self.status

    @staticmethod
    def check_all():
        """
        Check the status of all meetings in the meeting dictionary.
        """
        for a in Actor.A:
            if not Actor.A[a].in_meeting:
                for b in Actor.A[a].friends:
                    if not Actor.A[b].in_meeting:
                        if not Actor.A[a].personal_space.isdisjoint(Actor.A[b].personal_space):
                            m = "_".join(sorted([a,b]))
                            if m not in Unplanned.Completed:
                                if 0.5*(Actor.A[a].sociability + Actor.A[b].sociability) > 0.3:
                                    meet = Unplanned(m, actors = {a, b}, duration = random.choice(list(range(5, 50))), status = "not_initialized")
                                    Unplanned.M[meet.ID] = meet
                                    Actor.A[a].in_meeting = True
                                    Actor.A[b].in_meeting = True


    @staticmethod
    def update_all():
        """
        Updates the status of all events stored in the Unplanned.M dictionary.
        If an event is complete, it is destroyed. The status of Actors in the meeting
        is set to False.
        """
        remove = set()
        if len(Unplanned.M) > 0:
            for m in Unplanned.M.keys():
                if Unplanned.M[m].status == "completed":
                    Unplanned.Completed.add(m)
                    for a in Unplanned.M[m].actors:
                        Actor.A[a].in_meeting = False
                    remove.add(m)
                else:
                    Unplanned.M[m].update()
        for r in remove:
            del Unplanned.M[r]

class Room:
    def __init__(self, zones = set()):
        self.__zones = zones




