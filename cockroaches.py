#!/usr/bin/python

import sys, time, math, random, heapq, pygame
from operator import itemgetter

from collections import defaultdict
from colors import *

def run():
    pygame.init()
    #    w, h, s = 1400, 800, 5   # set width and height of the screen
    w, h, s = 1000, 750, 5  # set width and height of the screen
    clock = pygame.time.Clock()  # create a clock object
    FPS = 100  # set frame rate in frames per second.
    assert w % s == 0, "width must be divisible by size"
    assert h % s == 0, "height must be divisible by size"
    screen = pygame.display.set_mode((w, h))  # create screen
    screen.set_alpha(128)
    space = Space(w, h, s)  # Create the space.
    #    make_room_array(27, 15, (9, 9), (3, 3), space)
    make_room_array(19, 14, (10, 10), (1, 1), space)
    make_roaches(50, 3, 15, tomato)  # 1 DataMap
    make_roaches(50, 3, 5, gold)  # 2 DataMap
    make_roaches(50, 5, -25, lightgrey)  # 3 DataMap
    roaches_at = set([(c.x, c.y) for c in Cockroach.Roaches])
    all_cells = set(Room.available_cells)
    x, y = random.choice(list(all_cells.difference(roaches_at)))
    x1, y1 = random.choice(list(all_cells.difference(roaches_at)))
    p = Actor("p", x, y, s, space, cadetblue, 20)
    tg = Actor("tg", x1, y1, s, space, teal, 10)
    graph = make_threshold_graph()
    print(Room.rooms_for_threshold.keys())
    print(Room.thresholds_in_room.keys())
    print(len(space.cells.keys()), "cells")
    print(len(Room.rooms.keys()), "rooms")
    print(len(Room.rooms_for_threshold.keys()), "thresholds")
    
    while True:
        simulate(screen, space, Cockroach.Roaches, Actor.Actors, Cockroach.Poison, white)
#        move(p, tg, space, screen, gold)
        pygame.display.update()
        clock.tick(FPS)

##STURTEVANT

def make_threshold_graph():
    graph = defaultdict(list)
    for t in Room.rooms_for_threshold.keys():
        for r in Room.rooms_for_threshold[t]:
            for i in Room.thresholds_in_room[r]:
                if not i == t:
                    graph[t[0]].append(random.choice(i))
    for k in graph:
        graph[k] = list(set(graph[k]))
    return graph


def make_room_array(a, b, room_size, top_left, space):
    xs, ys = list(), list()
    allthresholds = list()
    alltop_lefts = list()
    x, y = top_left
    x_size, y_size = room_size
    for i in range(x, x + room_size[0] * a, room_size[0] + 1):
        for j in range(y, y + room_size[1] * b, room_size[1] + 1):
            Room(i, j, room_size[0], room_size[1], space)


def handle_events(space, screen):
    mpos = tuple([int(math.floor(i / space.s)) for i in pygame.mouse.get_pos()])
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()
        elif event.type == pygame.MOUSEBUTTONDOWN:
            if pygame.mouse.get_pressed()[2] == 1 and mpos in space.cells.keys():
                space.cells[mpos].toggle_walkability()
            for p in Actor.Actors:
                p.toggle_selected(mpos)
        move_actors_with_keys(event, Actor.Actors, mpos)


def move_actors_with_keys(event, actors, mpos):
    if event.type == pygame.KEYDOWN:
        if event.key == pygame.K_UP:
            for p in actors:
                if p.is_selected:
                    p.move_up()
        elif event.key == pygame.K_DOWN:
            for p in actors:
                if p.is_selected:
                    p.move_down()
        elif event.key == pygame.K_LEFT:
            for p in actors:
                if p.is_selected:
                    p.move_left()
        elif event.key == pygame.K_RIGHT:
            for p in actors:
                if p.is_selected:
                    p.move_right()


def draw_tl(tl, space, screen, color):
    space.cells[tl].draw_cell(screen, color)


def simulate(screen, space, roaches, actors, poison, color):
    handle_events(space, screen)
    move_roaches(roaches, space)
    draw(screen, space, roaches, actors, poison, color)


def move(actor, target, space, screen, pathcolor):
    S = Search((actor.x, actor.y), (target.x, target.y), space)
    S.draw_route(S.path, screen, pathcolor)
    if len(S.path) > 1:
        dx = (S.path[1][0] - S.path[0][0]) / abs(S.path[1][0] - S.path[0][0]) if S.path[1][0] != S.path[0][0] else 0
        dy = (S.path[1][1] - S.path[0][1]) / abs(S.path[1][1] - S.path[0][1]) if S.path[1][1] != S.path[0][1] else 0
        m = S.path[0][0] + dx, S.path[0][1] + dy
        actor.move(m)
#        actor.move(S.path[1])
        S.path.pop(0)


def stop_sim(event):
    if event.type == pygame.QUIT:
        pygame.quit()
        sys.exit()


def make_roaches(n, r, p, c):
    """Makes n roaches of size (radius) r, poison level p and color c in space"""
    count = 0
    while count < n:
        x, y = random.choice(Room.available_cells)
        Cockroach(x, y, r, p, c)
        count += 1


def move_roaches(roaches, space):
    for r in roaches:
        r.move_cockroach(space)
        


def draw(screen, space, roaches, actors, poison, color):
    space.draw_space(screen, color)
#    for p in actors:
#        draw_permissible_space(screen, space, p, poison, red)
    draw_poison(screen, space, poison, color)
    for p in actors: p.draw_actor(screen)
    for roach in roaches: roach.draw_cockroach(screen, space)
    for r in Room.rooms:
        Room.rooms[r].draw_room(screen, tomato)


def draw_poison(screen, space, poison, color):
    max_poison = max(poison.values())
    for c in poison:
        col = 255 - int(100.0 * poison[c] / max_poison)
        space.cells[c].draw_cell(screen, (col, col, col))


def draw_permissible_space(screen, space, actor, poison, color):
    """This evaluates the cost in each cell by comparing it to threshold for each actor."""
    for c in poison:
        if actor.poison_threshold <= poison[c]:
            space.cells[c].draw_cell(screen, tomato)
        elif actor.poison_threshold > poison[c]:
            space.cells[c].draw_cell(screen, white)


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

    def draw_cockroach(self, screen, space):
        pygame.draw.circle(screen, self.color, (int(self.x * space.s + space.s / 2), int(self.y * space.s + space.s / 2)), self.r)

    def move_cockroach(self, space):
        options = -1, 0, 1
        x = random.choice(options)
        y = random.choice(options)
        old_x, old_y = self.x, self.y
        new_x, new_y = self.x + x, self.y + y
        if space.inside((new_x, new_y)) and space.cells[(new_x, new_y)].walkable:
            if self.poison > 0:
                Cockroach.Poison[(old_x, old_y)] -= (self.poison - 1)
                if Cockroach.Poison[(old_x, old_y)] < 0:
                    Cockroach.Poison[(old_x, old_y)] = 0
            self.x, self.y = new_x, new_y
            Cockroach.Poison[(new_x, new_y)] += self.poison
            if Cockroach.Poison[(new_x, new_y)] < 0:
                Cockroach.Poison[(new_x, new_y)] = 0


class Cell:
    def __init__(self, x, y, s):
        self.x = x
        self.y = y
        self.s = s
        self.rect = pygame.Rect(self.x * self.s, self.y * self.s, self.s, self.s)
        self.walkable = True
        self.poison = 0
        self.occupied = False

    def toggle_walkability(self):
        if self.walkable:
            self.walkable = False
        else:
            self.walkable = True

    def draw_cell(self, screen, color=steelblue):
        if self.walkable:
            pygame.draw.rect(screen, color, self.rect)
        if not self.walkable:
            pygame.draw.rect(screen, yellow, self.rect)


class Space:
    def __init__(self, w, h, s):
        self.w = w
        self.h = h
        self.s = s  # size of each cell of the space
        self.cells = self.create_cells()

    def create_cells(self):
        """Creates space as a dictionary of cells"""
        allcells = dict()
        for i in range(int(self.w / self.s)):
            for j in range(int(self.h / self.s)):
                allcells[(i, j)] = Cell(i, j, self.s)
        return allcells

    def draw_space(self, screen, color):
        s = self.s
        for c in self.cells:
            self.cells[c].draw_cell(screen, color)

    def inside(self, c):
        return 0 <= c[0] < int(self.w / self.s) and 0 <= c[1] < int(self.h / self.s)

    def passable(self, c):
        return c in self.cells.keys() and self.cells[c].walkable and not self.cells[c].occupied

    def neighbours(self, c, allcells=False):
        x, y = c
        results = [(x + 1, y), (x - 1, y), (x, y + 1), (x, y - 1),
                   (x + 1, y + 1), (x + 1, y - 1), (x - 1, y + 1), (x - 1, y - 1)]
        if allcells:
            return filter(self.inside, results)
        results = filter(self.passable, results)
        return results

    def ordered_neighbours(self, c):
        ordered = [(self.cells[cell].cost, cell) for cell in self.neighbours(c)]
        return ordered

class Threshold:
    Graph = dict()
    def __init__(self, key_cell, cells):
        self.key_cell = key_cell
        self.cells = cells
        self.rooms = list()
        self.neighbours = list()
        Threshold.Graph[self.key_cell] = self.neighbours

class Room:
    rooms = defaultdict(list)
    thresholds_in_room = defaultdict(list)
    rooms_for_threshold = defaultdict(list)
    available_cells = list()

    def __init__(self, x, y, w, h, space):
        self.x = x
        self.y = y
        self.w = w
        self.h = h
        self.space = space
        self.thresholds = list()
        self.is_available = True
        self.collect_cells()
        Room.rooms[(self.x, self.y)] = self

    def collect_cells(self):
        allcells = dict()
        for i in range(self.x, self.x + self.w):
            for j in range(self.y, self.y + self.h):
                allcells[(i, j)] = self.space.cells[(i, j)]
                Room.available_cells.append((i, j))
        self.cells = allcells
        self.thresholds = self.generate_thresholds()
        for c in self.thresholds:
            allcells[c] = self.space.cells[c]
            Room.available_cells.append(c)

    def draw_room(self, screen, color):
        for c in self.cells.keys():
            topleft = self.cells[c].x * self.cells[c].s, self.cells[c].y * self.cells[c].s
            s = pygame.Surface((self.cells[c].s, self.cells[c].s))
            s.set_alpha(50)
            s.fill(color)
            screen.blit(s, topleft)

    def generate_thresholds(self):
        xs = sorted(list(set([i[0] for i in self.cells.keys()])))
        ys = sorted(list(set([i[1] for i in self.cells.keys()])))
        x_min, x_max = min(xs), max(xs)
        y_min, y_max = min(ys), max(ys)
        super_cells = list()
        for i in range(x_min - 1, x_max + 2):
            for j in range(y_min - 1, y_max + 2):
                super_cells.append((i, j))
        if len(xs) % 2 == 0:
            tholds = [((xs[len(xs) // 2 - 1], y_min - 1), (xs[len(xs) // 2], y_min - 1)),
                      ((xs[len(xs) // 2 - 1], y_max + 1), (xs[len(xs) // 2], y_max + 1))]
        elif not len(xs) % 2 == 0 and len(xs) > 3:
            tholds = [
                ((xs[len(xs) // 2 - 1], y_min - 1), (xs[len(xs) // 2], y_min - 1), (xs[len(xs) // 2 + 1], y_min - 1)),
                ((xs[len(xs) // 2 - 1], y_max + 1), (xs[len(xs) // 2], y_max + 1), (xs[len(xs) // 2 + 1], y_max - 1))]

        if len(ys) % 2 == 0:
            tholds += [((x_min - 1, ys[len(ys) // 2 - 1]), (x_min - 1, ys[len(ys) // 2])),
                       ((x_max + 1, ys[len(ys) // 2 - 1]), (x_max + 1, ys[len(ys) // 2]))]
        elif len(ys) % 2 != 0:
            tholds += [
                ((x_min - 1, ys[len(ys) // 2 - 1]), (x_min - 1, ys[len(ys) // 2]), (x_min - 1, ys[len(ys) // 2 + 1])),
                ((x_max + 1, ys[len(ys) // 2 - 1]), (x_max + 1, ys[len(ys) // 2]), (x_max + 1, ys[len(ys) // 2 + 1]))]

        threshold_cells = set()
        for t in tholds:
            Room.thresholds_in_room[(self.x, self.y)].append(t)
            Room.rooms_for_threshold[t].append((self.x, self.y))
            for c in t:
                threshold_cells.add(c)

        walls = list(set(super_cells).difference(set(self.cells.keys())).difference(threshold_cells))

        for w in walls:
            self.space.cells[w].walkable = False

        return threshold_cells


class Actor:
    Actors = list()

    def __init__(self, name, x, y, size, space, color, poison_threshold):
        self.name = name
        self.x = x
        self.y = y
        self.size = size
        self.space = space
        self.cell = self.space.cells[(self.x, self.y)]
        self.cell.occupied = True
        self.is_selected = False
        self.poison_threshold = poison_threshold
        self.color = color
        Actor.Actors.append(self)

    def draw_actor(self, screen):
        if self.is_selected:
            pygame.draw.circle(screen, red,
                               (int(self.x * self.size + self.size / 2), int(self.y * self.size + self.size / 2)),
                               int(self.size / 2))
        else:
            pygame.draw.circle(screen, self.color,
                               (int(self.x * self.size + self.size / 2), int(self.y * self.size + self.size / 2)),
                               int(self.size / 2))

    def move(self, new):
        """Move player to Grid Cell x, y. This is designed for A*"""
        self.x, self.y = new

    def move_left(self):
        """ Moves selected Person left by one cell """
        tx, ty = self.x - 1, self.y
        if (tx, ty) in self.space.cells.keys() and self.space.cells[tx, ty].walkable and not self.space.cells[
            tx, ty].occupied:
            self.x -= 1

    def move_right(self):
        """ Moves selected Person left by one cell """
        tx, ty = self.x + 1, self.y
        if (tx, ty) in self.space.cells.keys() and self.space.cells[tx, ty].walkable and not self.space.cells[
            tx, ty].occupied:
            self.x += 1

    def move_up(self):
        """ Moves selected Person left by one cell """
        tx, ty = self.x, self.y - 1
        if (tx, ty) in self.space.cells.keys() and self.space.cells[tx, ty].walkable and not self.space.cells[
            tx, ty].occupied:
            self.y -= 1

    def move_down(self):
        """ Moves selected Person left by one cell """
        tx, ty = self.x, self.y + 1
        if (tx, ty) in self.space.cells.keys() and self.space.cells[tx, ty].walkable and not self.space.cells[
            tx, ty].occupied:
            self.y += 1

    def toggle_selected(self, mpos):
        if mpos[0] == self.x and mpos[1] == self.y:
            if not self.is_selected:
                self.is_selected = True
            else:
                self.is_selected = False
            self.space.cells[mpos].walkable = True


#####################################################################################
#####################################################################################
#####################################################################################

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
    def __init__(self, start, goal, space):
        self.start = start
        self.goal = goal
        self.space = space
        self.open_cells = PriorityQueue()
        self.came_from = dict()
        self.cost_so_far = dict()
        self.x = self.space.w / self.space.s
        self.y = self.space.h / self.space.s
        self.path = self.get_jps_path()
        #self.path = self.get_path()

    def get_jps_path(self):
        self.open_cells.put(self.start, 0)
        self.came_from[self.start] = None
        self.cost_so_far[self.start] = 0
        orthogonals = (1, 0), (0, 1), (-1, 0), (0, -1)
        diagonals = (1, 1), (1, -1), (-1, -1), (-1, 1)
        while not self.open_cells.empty():
            current = self.open_cells.get()
            if current in self.space.neighbours(self.goal):
                break
            for d in orthogonals:
                self.test_orthogonal(current, d)
            for d in diagonals:
                self.test_diagonal(current, d)
        path = self.build_path()
        return path
        pass

    def test_diagonal(self, loc, d):
        cx, cy = loc
        dx, dy = d
        cost = 0
        while 0 < cx < self.x and 0 < cy < self.y:
            cx += dx
            cy += dy
            cost += 14
            if not self.space.cells[(cx, cy)].walkable:
                break
            if (cx, cy) in self.space.neighbours(self.goal):
                self.cost_so_far[(cx, cy)] = self.cost_so_far[loc] + cost
                self.open_cells.put((cx, cy), self.cost_so_far[(cx, cy)] + self.min_cost((cx, cy), self.goal))
                self.came_from[(cx, cy)] = loc
                break
            if not self.space.cells[(cx + dx, cy)].walkable and self.space.cells[(cx + dx, cy + dy)].walkable:
                new_cost = self.cost_so_far[loc] + cost
                if (cx, cy) not in self.cost_so_far or new_cost < self.cost_so_far[(cx, cy)]:
                    self.cost_so_far[(cx, cy)] = new_cost
                    self.open_cells.put((cx, cy), new_cost + self.min_cost((cx, cy), self.goal))
                    self.came_from[(cx, cy)] = loc
                    break
            else:
                if (cx, cy) not in self.cost_so_far or self.cost_so_far[loc] + cost < self.cost_so_far[(cx, cy)]:
                    self.cost_so_far[(cx, cy)] = self.cost_so_far[loc] + cost
                found = self.test_orthogonal((cx, cy), (dx, 0))
                if found:
                    self.open_cells.put((cx, cy), self.cost_so_far[(cx, cy)] + self.min_cost((cx, cy), self.goal))
                    self.came_from[(cx, cy)] = loc

            if not self.space.cells[(cx, cy + dy)].walkable and self.space.cells[(cx + dx, cy + dy)].walkable:
                new_cost = self.cost_so_far[loc] + cost
                if (cx, cy) not in self.cost_so_far or new_cost < self.cost_so_far[(cx, cy)]:
                    self.cost_so_far[(cx, cy)] = new_cost
                    self.open_cells.put((cx, cy), new_cost + self.min_cost((cx, cy), self.goal))
                    self.came_from[(cx, cy)] = loc
                    break
            else:
                if (cx, cy) not in self.cost_so_far or self.cost_so_far[loc] + cost < self.cost_so_far[(cx, cy)]:
                    self.cost_so_far[(cx, cy)] = self.cost_so_far[loc] + cost
                found = self.test_orthogonal((cx, cy), (0, dy))
                if found:
                    self.open_cells.put((cx, cy), self.cost_so_far[(cx, cy)] + self.min_cost((cx, cy), self.goal))
                    self.came_from[(cx, cy)] = loc

    def test_orthogonal(self, loc, d):
        found = False
        cx, cy = loc
        dx, dy = d
        cost = 0
        while 0 < cx < self.x and 0 < cy < self.y:
            cx += dx
            cy += dy
            cost += 10
            if not self.space.cells[(cx, cy)].walkable:
                return found
            if (cx, cy) in self.space.neighbours(self.goal):
                self.cost_so_far[(cx, cy)] = self.cost_so_far[loc] + cost
                self.open_cells.put((cx, cy), self.cost_so_far[(cx, cy)] + self.min_cost((cx, cy), self.goal))
                self.came_from[(cx, cy)] = loc
                found = True
                return found
            if dx == 0:
                c1 = not self.space.cells[(cx + 1, cy)].walkable and self.space.cells[(cx + 1, cy + dy)].walkable
                c2 = not self.space.cells[(cx - 1, cy)].walkable and self.space.cells[(cx - 1, cy + dy)].walkable
                if c1 or c2:
                    new_cost = self.cost_so_far[loc] + cost
                    if (cx, cy) not in self.cost_so_far or new_cost < self.cost_so_far[(cx, cy)]:
                        self.cost_so_far[(cx, cy)] = new_cost
                        self.open_cells.put((cx, cy), new_cost + self.min_cost((cx, cy), self.goal))
                        self.came_from[(cx, cy)] = loc
                        found = True
                        return found
            if dy == 0:
                c1 = not self.space.cells[(cx, cy + 1)].walkable and self.space.cells[(cx + dx, cy + 1)].walkable
                c2 = not self.space.cells[(cx, cy - 1)].walkable and self.space.cells[(cx + dx, cy - 1)].walkable
                if c1 or c2:
                    new_cost = self.cost_so_far[loc] + cost
                    if (cx, cy) not in self.cost_so_far or new_cost < self.cost_so_far[(cx, cy)]:
                        self.cost_so_far[(cx, cy)] = new_cost
                        self.open_cells.put((cx, cy), new_cost + self.min_cost((cx, cy), self.goal))
                        self.came_from[(cx, cy)] = loc
                        found = True
                        return found

    def min_cost(self, a, b):
        x1, y1 = a
        x2, y2 = b
        if abs(y2 - y1) > abs(x2 - x1):
            return 14 * abs(x2 - x1) + 10 * abs((y2 - y1) - (x2 - x1))
        else:
            return 14 * abs(y2 - y1) + 10 * abs((y2 - y1) - (x2 - x1))

    def get_path(self):
        self.open_cells.put(self.start, 0)
        self.came_from[self.start] = None
        self.cost_so_far[self.start] = 0  # Keeps track of F costs.
        while not self.open_cells.empty():
            current = self.open_cells.get()
            if self.goal in self.space.neighbours(current):
                break
            elif current == self.goal:
                break
            origin_costs = self.origin_cost(current)
            goal_costs = self.goal_cost(current)
            for loc in self.space.neighbours(current):
                F = origin_costs[loc]
                new_cost = self.cost_so_far[current] + F
                if loc not in self.cost_so_far or new_cost < self.cost_so_far[loc]:
                    self.cost_so_far[loc] = new_cost
                    priority = new_cost + goal_costs[loc]
                    self.open_cells.put(loc, priority)
                    self.came_from[loc] = current
        path = self.build_path()
        return path
    
    def get_threshold_path(self):
        pass
    

    def build_path(self):
        path = list()
        goal_nbrs = set(self.space.neighbours(self.goal))
        goal_nbrs.add(self.goal)
        for c in goal_nbrs:
            if c in self.came_from.keys():
                current = c
        path.append(current)
        while current != self.start:
            current = self.came_from[current]
            path.append(current)
        path.reverse()
        return path

    def draw_route(self, route, screen, color):
        """Draws the path on the screen"""
        h = int(self.space.s / 2)
        draw_this = list()
        for c in route:
            c = list(c)
            c[0] = c[0] * self.space.s + h
            c[1] = c[1] * self.space.s + h
            draw_this.append((c[0], c[1]))
        if len(draw_this) >= 2:
            pygame.draw.lines(screen, color, False, draw_this, 2)

    def origin_cost(self, c):
        costs = dict()
        for n in self.space.neighbours(c):
            if not (n[0] == c[0] or n[1] == c[1]):
                costs[n] = 14
            else:
                costs[n] = 10
        return costs

    def goal_cost(self, c):
        x1, y1 = self.goal
        costs = dict()
        for n in self.space.neighbours(c):
            x2, y2 = n
            if abs(y2 - y1) > abs(x2 - x1):
                final = 14 * abs(x2 - x1) + 10 * abs((y2 - y1) - (x2 - x1))
            else:
                final = 14 * abs(y2 - y1) + 10 * abs((y2 - y1) - (x2 - x1))
            costs[n] = final
        return costs


if __name__ == "__main__":
    run()
