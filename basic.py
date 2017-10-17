#!/usr/bin/python3.5
#entities.py This file contains class definitions for the Cell, Collection, Actor, Target, Move, Meet and Search
import sys, time, math, random, heapq, pygame, copy, itertools
from PIL import Image
from operator import itemgetter
from collections import defaultdict
from colors import *


class Cell:
    C = dict()
    def __init__(self, x, y, s):
        """
        Initializes a cell object. Requires x,y positions and size s.
        """
        self.x = x
        self.y = y
        self.s = s
        self.rect = pygame.Rect(self.x * self.s, self.y * self.s, self.s, self.s)
        self.prop = {"wall": False, "occupied": False, "in_zone": False, "in_threshold": False}
        self.zones = set()
        self.threshold = None
        self.nbrs = list()
        Cell.C[(self.x,self.y)] = self

    def __repr__(self):
        if self.in_threshold:
            return "Location: " + '('+str(self.x) + ', ' + str(self.y) + '), in threshold ' + str(self.threshold)
        if self.in_zone:
            return "Location: " + '('+str(self.x) + ', ' + str(self.y) + '), in zone '+ str(self.zone)
        if not self.in_zone and not self.in_threshold:
            return "Location: " + '('+str(self.x) + ', ' + str(self.y) + ')'

    def draw(self, screen, drawing_type = "graph", color = None):
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



