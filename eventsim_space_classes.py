#!/usr/bin/python3.5

import sys, time, math, random, heapq, pygame
from operator import itemgetter
from collections import defaultdict
from colors import *
from PIL import Image

class Cell:
    C = dict()
    def __init__(self, x, y, s):
        self.x = x
        self.y = y
        self.s = s
        self.rect = pygame.Rect(self.x * self.s, self.y * self.s, self.s, self.s)
        Cell.C[(self.x, self.y)] = self
        self.cell_type = None
        self.color = None
        Cell.S = self.s

    def neighbours(self):
        x, y = self.x, self.y
        results = [(x + 1, y), (x - 1, y), (x, y + 1), (x, y - 1),
                   (x + 1, y + 1), (x + 1, y - 1), (x - 1, y + 1), (x - 1, y - 1)]
        nbrs = (r for r in results if r in Cell.C.keys())
        return nbrs
    
    def draw(self, screen, drawing_type = None, color = None):
        r = max(2, int(self.size/2.5))
        if drawing_type == "grid":
            pygame.draw.rect(screen, color, self.rect, 1)
        elif drawing_type == "graph":
            cent = (self.x * self.s + int(self.s/2), self.y * self.s + int(self.s/2))
            pygame.draw.circle(screen, color, cent, r)
        
    @staticmethod
    def create_space(i, j):
        """
        Creates a space of size i pixels x j pixels. i is the width, j is the height.
        """
        for x in range(int(i/Cell.S)):
            for y in range(int(j/Cell.S)):
                Cell(i, j, s)
        for c in Cell.C:
            Cell.C[c].nbrs = Cell.C[c].neighbours() #Stores a generator object containing the neighbours of this cell

    @staticmethod
    def create_space_from_image(i, j, img):
        """
        Takes a picture of a floor plan as input and generates a cell array from it. 
        Four kinds of spaces must be specified in the picture:
        1. thresholds - red (255,0,0)
        2. walls (or barriers) - black (0, 0, 0)
        3. spaces (or zones) - white (255, 255, 255)
        4. areas to be ignored - green (0, 255, 0)
        """
        spaces = {"threshold":(255,0,0), "wall":(0,0,0), "space": (255, 255, 255), "ignore":(0, 255, 0)}
        img = Image.open(img)
        width, height = img.size
        print(width, height)
        rgbvals = dict()
        distinctvals = set()
        for i in range(width):
            for j in range(height):
                rgbvals[(i,j)] = img.getpixel((i,j))
                r,g,b = rgbvals[(i,j)]
                r = 1.0*r/(s*s)
                g = 1.0*g/(s*s)
                b = 1.0*b/(s*s)
                rgbvals[(i,j)] = (r, g, b)
                
        for i in range(int(w/s)):
            for j in range(int(h/s)):
                Cell(i, j, s)
        colors = dict()
        for c in Cell.C:
            x1, y1 = Cell.C[c].rect.topleft
            x2, y2 = Cell.C[c].rect.bottomright
            for i in range(x1, x2):
                for j in range(y1, y2):
                    if (i,j) in rgbvals:
                        colors[c].append(rgbvals[(i,j)])
            colors[c] = tuple([int(sum(i)) for i in zip(*colors[c])])
            distances = list()
            for k in spaces:
                distances.append((coldist(colors[c], spaces[k]), spaces[k]))
            closest = sorted(distances, key = itemgetter(0))[0]
            Cell.C[c].color = closest[1]

            
            
class Collection:
    C = dict()
    def __init__(self, ID, cell_type, start_cell):
        self.ID = ID
        self.zone_type = zone_type
        self.start_cell = start_cell
        self.cells = set()
        self.neighbours = list()
        pass

    def collect_cells(self):
        """
        This depends on the idea that two different cells can never have an identical set of neighbours. 
        This always holds true unless you have exactly three sells arranged in a 3x1 array (in this case the middle cell is the only neighbour to the cells on the end. 
        """
        visited = set() #keep track of visited cells.
        for c in Cell.C[self.start_cell].nbrs:
            if c not in visited and Cell.C[c].color == Cell.C[self.start_cell].nbrs:
                self.cells.add(c)
            visited.add(c)
           
        for c in self.cells:
            for n in Cell.C[c].nbrs:
                if n not in visited and Cell.C[n].color == Cell.C[c].nbrs:
                    self.cells.add(n)
                visited.add(n)                        
                                        
                        
            
                

class Search_Graph:
    def __init__():
        pass
