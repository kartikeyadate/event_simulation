#!/usr/bin/python3.5
#entities.py This file contains class definitions for the Cell, Collection, Actor, Target, Move, Meet and Search
import sys, time, math, random, heapq, pygame, copy, itertools
from PIL import Image
from operator import itemgetter
from collections import defaultdict
from colors import *


class Cell:
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
        self.costs = dict()
        self.is_barrier = False
        self.is_occupied = False
        self.is_personal = False
        self.in_zone = False
        self.in_threshold = False
        self.zone = None
        self.threshold = None
        self.nbrs = set()
        self.zones = set()



