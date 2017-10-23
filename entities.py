#!/usr/bin/python3.6
#entities.py This file contains class definitions for the Cell, Collection, Actor, Target, Move, Meet, Step, Event and the search classes.
import sys, time, math, random, heapq, pygame, copy, itertools
from PIL import Image
from operator import itemgetter
from collections import defaultdict
from colors import *

#######################CLASSES DESCRIBING SPACE: CELL, COLLECTION###############
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
        self.threshold = None
        self.zones = set()
        self.nbrs = list()
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
        return "Location: " + ','.join((str(self.x),str(self.y))) + "; Zones: " + ",".join(list(self.zones)) + "; Threshold: " + str(self.threshold)

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
        nbrs = [r for r in results if r in Cell.C.keys() and not Cell.C[r].is_barrier]
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
        nbrs = [r for r in results if r in Cell.C.keys() and not Cell.C[r].is_barrier]
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
    def __init__(self, ID, TYPE, cells = set(), thresholds = set(), threshold_cells = set()):
        self.ID = ID
        self.TYPE = TYPE
        self.cells = cells #keys (x,y) of cells in collection
        self.center = None
        self.center_cell = None
        self.graph = dict() #search graph for a zone.
        self.thresholds = thresholds #thresholds attached to current zone.
        self.threshold_cells = threshold_cells #keys (x,y) of cells contained in thresholds attached to current zone.
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
        self.center_cell = (xmid,ymid)

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
    def mzt(x,y,tl=(1,1)):
        """
        Generates a two dimensional array of zones in the given cell space. Each zone has x * y cells.
        """
        xmax = max([i[0] for i in Cell.C.keys()]) #max x value for cells.
        ymax = max([i[1] for i in Cell.C.keys()]) #max y value for cells.
        sx, sy = tl
        xc = (xmax-sx)//x
        yc = (ymax-sy)//y
        name = 0
        for i in range(sx, xmax-x, x+1):
            for j in range(sy, ymax-y, y+1):
                zone = Collection(str(name), "z")
                zone_cells = set()
                for p in range(i+1,i+x+1):
                    for q in range(j+1,j+y+1):
                        zone_cells.add((p,q))
                zone.cells = zone_cells
                for c in zone_cells:
                    Cell.C[c].zones.add(str(name))
                    Cell.C[c].in_zone = True
                name += 1

        thresholds = set()
        for z in Collection.Z.keys():
            cells = list(Collection.Z[z].cells)
            xs = [i[0] for i in cells]
            ys = [i[1] for i in cells]
            xmi,ymi = min(xs), min(ys)
            xma,yma = max(xs), max(ys)
            length = len(range(xmi-1,xma+2))
            med = xmi-1 + length//2
            if length % 2 == 0:
                ignore = med-2,med-1,med,med+1
            if length % 2 != 0:
                ignore = med-2,med-1,med,med+1,med+2
            tcellsupper = set()
            tcellslower = set()
            for i in range(xmi-1,xma+2):
                if i not in ignore:
                    Cell.C[(i,ymi-1)].is_barrier = True
                    Cell.C[(i,yma+1)].is_barrier = True
                if i in ignore:
                    tcellsupper.add((i,ymi-1))
                    tcellslower.add((i,yma+1))
            thresholds.add(tuple(tcellsupper))
            thresholds.add(tuple(tcellslower))

            length = len(range(ymi-1,yma+2))
            med = ymi-1 + length//2
            tcellsupper = set()
            tcellslower = set()

            if length % 2 == 0:
                ignore = med-2,med-1,med,med+1
            if length % 2 != 0:
                ignore = med-2,med-1,med,med+1,med+2
            for i in range(ymi-1,yma+2):
                if i not in ignore:
                    Cell.C[(xmi-1,i)].is_barrier = True
                    Cell.C[(xma+1,i)].is_barrier = True
                if i in ignore:
                    tcellsupper.add((xmi-1,i))
                    tcellslower.add((xma+1,i))
            thresholds.add(tuple(tcellsupper))
            thresholds.add(tuple(tcellslower))

        Cell.assign_neighbours()
        tn = 0
        for threshold in thresholds:
            thres = Collection(str(tn), "t", cells = threshold)
            tb = set()
            for c in threshold:
                Cell.C[c].threshold = str(tn)
                nbrs = Cell.C[c].nbrs
                tb = tb.union(nbrs)
            zs = set()
            for c in tb:
                zones = Cell.C[c].zones
                zs = zs.union(zones)
            thres.zones = zs
            for c in threshold:
                Cell.C[c].zones = zs
                Cell.C[c].in_threshold = True
            tn += 1

        tzmap = defaultdict(list)
        for t in Collection.T.keys():
            for z in Collection.T[t].zones:
                tzmap[z].append(t)

        for k, v in tzmap.items():
            Collection.Z[k].thresholds = v
            tcs = set()
            for t in v:
                cells = set(Collection.T[t].cells)
                tcs = tcs.union(cells)
            Collection.Z[k].threshold_cells = tcs
        Collection.generate_graphs()

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
                Cell.C[cell].zones.add(str(num))
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
                Cell.C[c].zones.add(z)
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
            thresholds = set()
            threshold_cells = set()
            for c in Collection.Z[z].cells:
                for n in Cell.C[c].nbrs:
                    if Cell.C[n].in_threshold:
                        t = Cell.C[n].threshold
                        if t in Collection.T.keys():
                            th_cells = Collection.T[t].cells
                            thresholds.add(t)
                            threshold_cells = threshold_cells.union(th_cells)
            Collection.Z[z].thresholds = thresholds
            Collection.Z[z].threshold_cells = threshold_cells


        #For every zone, the thresholds connected to it and the threshold cells attached to it are now stored.

        for t in Collection.T.keys():
            for c in Collection.T[t].cells:
                for n in Cell.C[c].nbrs:
                    if Cell.C[n].in_zone:
                        zones = Cell.C[n].zones
                        for z in zones:
                            Collection.T[t].zones.add(z)

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
    def check_diagonal_thresholds():
        for t in Collection.T.keys():
            xs = [i[0] for i in Collection.T[t].cells]
            ys = [i[1] for i in Collection.T[t].cells]

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

    @staticmethod
    def generate_graphs():
        Collection.create_zone_graphs()
        Collection.create_threshold_graph()

    @staticmethod
    def test_assignments():
        for z in Collection.Z.keys():
            for x in Collection.Z[z].cells:
                if len(Cell.C[x].zones) == 0:
                    print(z, x)
            t = Collection.Z[z].thresholds
            for (a,b) in itertools.combinations(t,2):
                az = Collection.T[a].zones
                bz = Collection.T[b].zones
                if z not in az.intersection(bz):
                    print(z, t, (a,b), (az,bz))
        for t in Collection.T.keys():
            print(t, len(Collection.T[t].cells), Collection.T[t].cells)

#######################CLASSES DESCRIBING ACTORS: ACTOR, COCKROACHES ###########
class Actor(object):
    """
    Definition of the actor.
    """
    A = dict()
    def __init__(self, name, x = None, y = None, color = None, zone = None, threshold = None, facing = (1,0), unavailable = set(), actor_type = None, sociability = random.choice([0.5,0.6,0.7,0.8,0.9,1.0]), friends = set(), state = "idle"):
        self.name = name
        self.actor_type = actor_type
        self.friends = friends
        self.sociability = sociability
        self.state = state #"idle", "in_move", "in_meet", "going_to_meet"
        self.x = x
        self.y = y
        self.color = color
        self.personal_space = set()
        if zone is not None and self.x is None and self.y is None:
            self.initialize_in_zone(zone)
        if zone is None and (self.x is not None and self.y is not None):
            self.zone = self.assign_zone()
        self.zone = zone
        self.prev_zone = None
        Collection.Z[self.zone].actors.add(self.name)
        self.color = color if color is not None else crimson
        self.threshold = threshold
        if self.threshold is not None:
            Collection.T[self.threshold].actors.add(self.name)
        self.facing = facing
        self.unavailable = unavailable
        self.set_personal_space()
        self.size = 0
        self.locations = None
        self.event = None
        Actor.A[self.name] = self
        Cell.C[(self.x, self.y)].is_occupied = True

    def assign_zone(self):
        possible = Cell.C[(self.x, self.y)].zones
        return random.choice(list(possible))

    def initialize_in_zone(self, z):
        """
        If a zone is specified, this initializes the actor in a randomly chosen position in this zone.
        """
        options = Collection.Z[z].cells
        ox, oy = self.x, self.y
        if ox is not None and oy is not None:
            self.remove_personal_space()
        self.x, self.y = random.choice([i for i in list(options) if not Cell.C[i].is_occupied])

        if len(Cell.C[(self.x, self.y)].zones) == 1:
            self.zone = list(Cell.C[(self.x, self.y)].zones)[0]
        elif len(Cell.C[(self.x, self.y)].zones) == 2:
            self.zone = random.choice(list(Cell.C[(self.x, self.y)].zones))
            self.threshold = Cell.C[(self.x, self.y)].threshold

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
        Moves actor from current position to a new position c.
        """
        ox, oy = self.x, self.y
        cx, cy = c
        oldzs = Cell.C[(ox,oy)].zones
        newzs = Cell.C[(cx,cy)].zones
        #Entering a threshold
        if len(oldzs) == 1 and len(newzs) == 2:
            old_z = list(oldzs)[0]
            new_z = list(newzs.intersection(oldzs))[0]

        #Continuing in the same zone
        if len(oldzs) == 1 and len(newzs) == 1:
            old_z = list(oldzs)[0]
            new_z = list(newzs)[0]
        #Entering a zone from a threshold
        if len(oldzs) == 2 and len(newzs) == 1:
            old_z = list(oldzs.difference(newzs))[0]
            new_z = list(newzs)[0]

        #Conitnuing in a threshold
        if len(oldzs) == 2 and len(newzs) == 2:
            inter = newzs.intersection(oldzs)
            new_z = list(inter)[0]
            old_z = new_z

        old_t = Cell.C[(ox,oy)].threshold
        new_t = Cell.C[(ox,oy)].threshold

        if not Cell.C[(cx, cy)].is_occupied:
            self.remove_personal_space()
            self.x, self.y = cx, cy
            self.set_personal_space()
            Cell.C[(ox, oy)].is_occupied = False
            Cell.C[(self.x, self.y)].is_occupied = True
            self.zone = new_z
            self.prev_zone = old_z
            #update the zone's information about actors in it.
            if self.prev_zone != self.zone:
                Collection.Z[self.zone].actors.add(self.name)
                if self.name in Collection.Z[self.prev_zone].actors:
                    Collection.Z[self.prev_zone].actors.remove(self.name)
            # update the threshold's information about the actors in it.
            if new_t != old_t:
                self.threshold = new_t
                if old_t is not None:
                    Collection.T[old_t].remove(self.name)
                if new_t is not None:
                    Collection.T[new_t].add(self.name)

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

    def draw_personal_space(self, screen, min_size = 4):
        """
        Draws this object in pygame as a circle or radius min_size
        Requires a screen object.
        """
        if self.state == "idle":
            color = lightgrey
        if self.state == "in_move":
            color = teal
        if self.state == "in_meet":
            color = salmon
        if self.state == "going_to_meet":
            color = orange

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
            Actor.A[a].draw_personal_space(screen, min_size=min_size)

        for a in Actor.A:
            Actor.A[a].draw(screen, min_size = min_size)

    @staticmethod
    def update_zones():
        for a in Actor.A:
            if Actor.A[a].zone is None:
                c = Actor.A[a].x, Actor.A[a].y
                print(Cell.C[c].zones)

    @staticmethod
    def possible_unscheduled(group):
        """
        If two or more actors which are in idle or in_move states
        are in the same zone, a meeting between them is possible.
        """
        zones = defaultdict(list)
        for a in group:
            if Actor.A[a].event == None:
                zone = Actor.A[a].zone
                zones[zone].append(a)
        possible_meetings = list()
        for zone in zones:
            if len(zones[zone]) > 1:
                zones[zone] = tuple(sorted(zones[zone]))
                possible_meetings.append((zone, zones[zone]))
        return possible_meetings

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

    @staticmethod
    def total_poison():
        return sum(Cockroach.Poison.values())

    def draw_cockroach(self, screen):
        center = self.x*Cell.size + Cell.size // 2, self.y*Cell.size + Cell.size // 2
        radius = Cell.size // 2
        pygame.draw.circle(screen, self.color, center, radius)

    def move_antidote_intelligently(self):
        """The cleaner cockroaches do not perform random walks. Instead they move to the worst infested cell."""

        if self.poison <= 0:
            target = [(Cockroach.Poison[i],i) for i in Cell.C[(self.x, self.y)].nbrs if not Cell.C[(self.x, self.y)].is_barrier]
            total_poison = sum([j[0] for j in target])
            if total_poison > 0:
                target = random.choice([i for i in target if i == max(target)])
                self.x, self.y = target[1][0], target[1][1]
            else:
                self.x, self.y = random.choice(Cell.C.keys())
            Cockroach.Poison[(self.x, self.y)] += self.poison
            if Cockroach.Poison[(self.x, self.y)] < 0:
                Cockroach.Poison[(self.x, self.y)] = 0

    def move_antidote_randomly(self):
        """Cockroach performs a random walk depositing poison, moving poison (positive or negative) from cell to cell."""
        if self.poison <= 0:
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

    def move_cockroach_intelligently(self):
        """The cleaner cockroaches do not perform random walks. Instead they move to the worst infested cell."""
        if self.poison > 0:
            options = -1, 0, 1
            x = random.choice(options)
            y = random.choice(options)
            old_x, old_y = self.x, self.y
            new_x, new_y = self.x + x, self.y + y
            if (new_x, new_y) in Cell.C.keys() and not Cell.C[(new_x, new_y)].is_barrier:
                Cockroach.Poison[(old_x, old_y)] -= (self.poison - 1)
                if Cockroach.Poison[(old_x, old_y)] < 0:
                    Cockroach.Poison[(old_x, old_y)] = 0
                self.x, self.y = new_x, new_y
                Cockroach.Poison[(new_x, new_y)] += self.poison
                if Cockroach.Poison[(new_x, new_y)] < 0:
                    Cockroach.Poison[(new_x, new_y)] = 0

    def move_cockroach_randomly(self):
        """Cockroach performs a random walk depositing poison, moving poison (positive or negative) from cell to cell."""
        if self.poison > 0:
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

class Target:
    """Defines a target cell. Target cells are not occupied."""
    T = dict()
    def __init__(self, name, size=9, x = None, y = None, zone = None):
        self.name = name
        self.x = x
        self.y = y
        self.size = size #1,4,9 or 16 cells - 1x1, 2x2, 3x3 or 4x4
        self.zone = zone
        self.personal_space = set()
        self.locations = set()
        self.occupied_locations = set()
        self.current = None
        if self.x is not None and self.y is not None:
            self.set_personal_space()
        if self.x is None and self.y is None:
            self.initialize()
        self.current_event = None
        self.exclusive = False
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
        self.set_personal_space()

    def draw_target(self, screen):
        for c in self.locations:
            Cell.C[c].draw(screen, color=chocolate)

    def set_personal_space(self):
        """
        Sets the personal space of the target in current position.
        Currently, personal space is the Moore neighbourhood of the current position.
        """
        x,y = self.x, self.y
        cells = list()
        if self.size == 1:
            cells.append((x,y))
        if self.size == 4:
            possibles = [comb for comb in itertools.combinations(Cell.C[(x,y)].nbrs,4) if (x,y) in comb]
        if self.size == 9:
            possibles = Cell.C[(x,y)].nbrs
        for c in possibles:
            for d in Cell.C[c].nbrs:
                if not Cell.C[d].is_barrier:
                    if Cell.C[d].in_threshold or Cell.C[d].in_zone:
                        self.personal_space.add(c)
        self.locations = set(possibles)

    def available(self, apart_from = set()):
        """
        Returns whether or not a target is available.
        """
        other_actors = Collection.Z[self.zone].actors.difference(apart_from)
        locations = {(Actor.A[i].x, Actor.A[i].y) for i in other_actors}
        in_target = locations.intersection(self.locations)
        return len(in_target) == 0

    def kill(self):
        if self.name in Target.T:
            Target.T.pop(self.name)
        del self


    @staticmethod
    def draw_all_targets(screen):
        for t in Target.T:
            Target.T[t].draw_target(screen)

############################ CLASSES FOR SEARCH ################################
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
        #print(sorted(list(Collection.TG.keys()), key=itemgetter(0,1)))
        #print(sorted(list(self.graph.keys()),key=itemgetter(0,1)))
        self.open_cells.put(self.start, 0)
        self.came_from[self.start] = None
        self.cost_so_far[self.start] = 0
        while not self.open_cells.empty():
            current = self.open_cells.get()
            if current == self.goal:
                self.came_from[self.goal] = current
                break
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
            pygame.draw.aalines(screen, color, False, draw_this, 1)

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
        self.target_location = self.process_target(target)
        self.screen = screen
        self.graph = graph
        self.unavailable = unavailable
        self.unavailable = self.unavailable.union(self.actor.unavailable)
        self.done = self.check_done()
        if self.done:
            self.actor.state = "idle"
        if not self.done:
            self.go()


    def min_dist(self, a, b):
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

    def process_target(self, target):
        if target.size > 1 and type(target.locations) is set:
            apos = self.actor.x, self.actor.y
            distances = list()
            for tpos in target.locations:
                if not Cell.C[tpos].is_occupied:
                    distances.append((self.min_dist(apos,tpos), tpos))
            if len(distances) >= 2:
                answer = random.choice(sorted(distances, key=itemgetter(0))[:2])[1]
            elif len(distances) == 1:
                answer = distances[0][1]
            elif len(distances) == 0:
                answer = random.choice(list(target.locations))
            return answer
        else:
            return target.x, target.y

    def check_done(self):
        if type(self.target) == Target:
            return (self.actor.x, self.actor.y) == (self.target.x, self.target.y)
        elif type(self.target) == Actor:
            tz = Cell.C[(self.target.x, self.target.y)].nbrs
            return (self.actor.x, self.actor.y) in tz

    def go(self, ignore=set()):
        if self.actor.state in ("going_to_meet", "idle", "in_move"):
            if self.actor.zone == self.target.zone:
                #print(self.actor.name, (self.actor.x, self.actor.y), self.target_location)
                ZS = self.zone_search((self.actor.x, self.actor.y), self.target_location, ignore=ignore)
                if ZS.path is not None and len(ZS.path) > 1:
                    if self.actor.state != "going_to_meet":
                        self.actor.state = "in_move"
                    ZS.draw_route(self.screen, color=red)
                    self.actor.move(ZS.path[1])
                    ZS.path.pop(0)

            elif self.actor.zone != self.target.zone:
                S = self.threshold_search()
                if S.path is not None:
                    if self.actor.state != "going_to_meet":
                        self.actor.state = "in_move"
                    S.draw_route(self.screen, color=black)
                    ZS = self.zone_search(S.path[0], S.path[1], ignore=ignore)
                    if ZS.path is None:
                        ignore.add(S.path[1])
                        options = [i for i in Cell.C[S.path[1]].nbrs if Cell.C[i].in_threshold]
                        if len(options) > 0:
                            ZS = self.zone_search(S.path[0], options[0], ignore=ignore)

                    if ZS.path is not None:
                        if self.actor.state != "going_to_meet":
                            self.actor.state = "in_move"
                        ZS.draw_route(self.screen, color=red)
                        self.actor.move(ZS.path[1])
                        ZS.path.pop(0)

    def threshold_search(self, ignore=set()):
        A = self.actor.x, self.actor.y
        B = self.target.x, self.target.y
        AZ = Cell.C[A].zones
        AZ = list(AZ)[0]
        BZ = Cell.C[B].zones
        BZ = list(BZ)[0]
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
            self.graph[A] = [i for i in Collection.Z[AZ].threshold_cells]
        if B not in self.graph:
            self.graph[B] = [i for i in Collection.Z[BZ].threshold_cells]

        return Search(A, B, graph=self.graph, ignore=ignore)

    def zone_search(self, a, b, ignore=set()):
        zone = self.get_zone(a, b)
        if zone is None:
            print("Valid zone was not returned!")
            print(a, Cell.C[a].zones)
            print(b, Cell.C[b].zones)
        for actor in Collection.Z[zone].actors:
            if actor != self.actor.name and actor != self.target.name:
                if actor in Actor.A.keys():
                    ignore = ignore.union(Actor.A[actor].personal_space)

        return Search(a, b, graph=Collection.Z[zone].graph, ignore=ignore)

    def get_zone(self, start, target):
        sz = Cell.C[start].zones
        tz = Cell.C[target].zones
        common = sz.intersection(tz)
        if len(common) >= 1:
            return list(common)[0]
        else:
            return None

    def evaluate(self):
        pass

class Meet:
    """
    Defines a meeting. Ways in which a meeting can be defined:
        1. A set of actors meet at a given target.
        2. A set of actors meet in a given zone.
    A meeting has the following states:
        1. "not_initialized"
        2. "in_progress"
        3. "completed"
        4. "suspended"
    A meeting has a specified duration given in timesteps.
    """
    M = dict()
    def __init__(self, ID, participants = list(), zone = None, target = None, target_specified = False, space = set(), state = "not_initialized", start_at = 0, progress = 0, duration = random.choice(range(25,36))):
        if len(participants) < 2:
            print("At least two actors are required for a meeting to occur. Less than two have been specified.")
            return
        if target_specified and self.zone is None and self.target is None:
            print("The location of this meeting has not been adequately given. Specify zone or target.")
            return
        self.ID = ID
        self.participants = participants #expected participants of a scheduled meeting, actual participants in any meeting.
        self.zone = zone
        self.target = target
        self.target_specified = target_specified
        self.state = state  #possible states: "not_initialized", "in_progress", "completed", "suspended"
        self.start_at = start_at
        self.progress = progress #timesteps towards duration.
        self.duration = duration #scheduled length of the meeting.
        self.space = space
        Meet.M[self.ID] = self

    def locate(self):
        """
        This function locates a meeting given the information specified.
        If a target has been specified in the meeting definition, the target is assigned to the meeting.
        Where it is relevant, the current position of the participants (participants)
        is taken into account.
        To define a scheduled meeting, actors and at least the meeting zone or the meeting target should be provided.
        To define an unscheduled meeting, the actors involved should be in the same zone and target_specified should be false.
        """
        if len(list(Target.T.keys())) > 0:
            t = max(list(Target.T.keys()))
        else:
            t = 0

        zones = {Actor.A[i].zone for i in self.participants}
        if len(zones) < 1:
            print("None of the actors appear to be in a zone:", (self.ID, self.zone, self.participants))
            return

        if self.target_specified:
            if self.zone is None:
                self.zone = self.target.zone
            elif self.target is None:
                if len(zones) == 1:
                    tx, ty = self.centroid()
                    t += 1
                    self.target = Target(t,x=tx,y=ty,zone=self.zone)
                elif len(zones) > 1:
                    tx, ty = Collection.Z[self.zone].center_cell
                    t += 1
                    self.target = Target(t,x=tx,y=ty,zone=self.zone)

        elif not self.target_specified:
            if self.target is None:
                if len(zones) == 1:
                    if self.zone is None:
                        self.zone = list(zones)[0]
                    tx, ty = self.centroid()
                    t += 1
                    self.target = Target(t,x=tx,y=ty,zone=self.zone)
                elif len(zones) > 1:
                    print("Meeting location cannot be determined as the zone in which meeting is to occur cannot be identified.")
                    return

    def centroid(self):
        xs,ys = list(), list()
        for p in self.participants:
            px,py = Actor.A[p].x, Actor.A[p].y
            xs.append(px)
            ys.append(py)
        tx = int(round(1.0*sum(xs)/len(xs),0))
        ty = int(round(1.0*sum(ys)/len(ys),0))
        return tx,ty

    def update(self):
        if self.spatial_conditions():
            if self.state == "in_progress" and self.progress < self.duration:
                self.progress += 1
                return None
            elif self.state == "in_progress" and self.progress == self.duration:
                self.state = "completed"

    def start(self):
        for p in self.participants:
            self.space = self.space.union(Actor.A[p].personal_space)
            Actor.A[p].state = "in_meet"
        self.state = "in_progress"
        self.progress += 1

    def spatial_conditions(self):
        if len(self.participants) <= 1:
            return False
        else:
            satisfied = True
            if self.target is None:
                return False
            for p in self.participants:
                if not (satisfied and (Actor.A[p].x, Actor.A[p].y) in self.target.locations):
                    return False
            return satisfied

    def proceed(self,screen):
        if len(self.participants) < 2:
            return False
        if self.state == "not_initialized":
            if self.spatial_conditions():
                self.start()
            else:
                provide = dict()
                for p in self.participants:
                    Actor.A[p].state = "going_to_meet"
                    if self.target is not None:
                        available_locations = {i for i in self.target.locations if not Cell.C[i].is_occupied}
                    else:
                        available_locations = set()
                    if len(available_locations) > 0:
                        x,y = random.choice(list(available_locations))
                        available_locations.remove((x,y))
                        provide[p] = x,y
                    else:
                        print("Location is not available")

                for p in provide:
                    self.target.x, self.target.y = provide[p]
                    Move(Actor.A[p], self.target, screen, graph=Collection.TG, unavailable=Actor.A[p].unavailable)

        elif self.state == "in_progress":
            self.update()

    def kill(self):
        self.participants = list(self.participants)
        while self.participants:
            p = self.participants.pop()
            Actor.A[p].state = "idle"
            Actor.A[p].event = None
        if self.target is not None:
            self.target.kill()
        del self

    def add_participant(self, p, screen):
        Actor.A[p].state = "going_to_meet"
        Move(Actor.A[p],self.target,screen,graph=Collection.TG,unavailable=Actor.A[p].unavailable)
        if (Actor.A[p].x, Actor.A[p].y) in self.target.locations:
            self.participants.add(p)
            Actor.A[p].state = "in_meet"

class Event:
    """
    Describes an event.
    An event is an entity involving one of more actors completing one or more tasks in a given sequence.
    """
    E = dict()
    def __init__(self, name):
        self.name = name
        self.steps = list()#a sequence of steps
        self.current_stage = 0 #total number of stages = len(steps), current step = current index of the list steps
        self.stages = len(self.steps)
        Event.E[self.name] = self

    def add_step(self, step):
        self.steps.append(step)
        self.stages = len(self.steps)

    def execute(self, screen):
        if self.current_stage < self.stages:
            self.steps[self.current_stage].proceed(screen)
            if self.steps[self.current_stage].state == "completed":
                self.current_stage += 1

    def report(self):
        for s in self.steps:
            for a in s.actors:
                print(Actor.A[a].state)

#The Step class holds either a meet or a move event.

class Step:
    S = dict()
    def __init__(self, name, event, actors = set(), target = None, duration = random.choice(range(10,40))):
        self.name = name
        self.event = event
        self.actors = actors
        self.target = target #Target object
        self.duration = duration
        self.state = "not_initialized" #possible states "not_initialized", "in_progress", "completed"
        self.progress = 0
        self.me = None
        self.mo = None
        Step.S[(self.name,self.event)] = self

    def update(self):
        if self.state == "in_progress" and self.progress < self.duration:
            self.progress += 1
            print(self.event, self.progress, self.duration)
        elif self.state == "in_progress" and self.progress == self.duration:
            self.state = "completed"
            while self.actors:
                p = self.actors.pop()
                Actor.A[p].event = None
                Actor.A[p].state = "idle"

    def start(self):
        if self.state == "not_initialized" and self.tests():
            self.progress += 1
            self.state = "in_progress"

    def tests(self):
        return self.spatial_test() and self.social_test()

    def spatial_test(self):
        """
        Checks to see two things:
            1. All actors in the current step are in the target.
            2. No other actors are in the target.
        """
        locations = set()
        for a in self.actors:
            x,y = Actor.A[a].x, Actor.A[a].y
            locations.add((x,y))
        return self.target.available(apart_from = self.actors) and locations.issubset(self.target.locations)

    def social_test(self):
        result = True
        for a in self.actors:
            if Actor.A[a].event != self.event:
                result = False
        return result

    def proceed(self, screen):
        if len(self.actors) > 1:
            if self.tests():
                if self.state == "not_initialized" and self.progress == 0:
                    self.start()
                elif self.state == "in_progress":
                    self.update()
            else:
                if not self.me and not self.mo and len(self.actors) > 1:
                    if len(Meet.M) > 0:
                        me = [int(i) for i in Meet.M.keys() if i.isdigit()]
                        if len(me) > 0:
                            me = max(me)
                        else:
                            me = 0
                    else:
                        me = 0
                    me += 1
                    self.me = Meet(str(me), participants = self.actors, zone = self.target.zone, target = self.target, duration = 1)
                    self.me.proceed(screen)
                else:
                    self.me.proceed(screen)
                if self.me.state == "in_progress":
                    for a in self.actors:
                        if Actor.A[a].event is None:
                            Actor.A[a].event = self.event
        elif len(self.actors) == 1:
            pass

