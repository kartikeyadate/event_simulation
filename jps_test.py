import sys, time, math, random, heapq, pygame
from operator import itemgetter
from collections import defaultdict
from colors import *

def get_dead_cells():
    f = open("unwalkablecells.txt","r")
    return f.read().split("), (")

def run():
    pygame.init()  # initialize the game engine
    w, h, s = 600, 600, 10   # set width and height of the screen
    clock = pygame.time.Clock()  # create a clock object
    FPS = 24  # set frame rate in frames per second.
    assert w % s == 0, "width must be divisible by size"
    assert h % s == 0, "height must be divisible by size"
    screen = pygame.display.set_mode((w, h))  # create screen
    screen.fill(white)  # set a white background
    ward = Space(w,h,s)
    pad_space(ward)
    origin = Piece("origin", 10, 5, s, ward, steelblue)
    target = Piece("target", 50, 5, s, ward, tomato)
    for i in range(50):
        ward.cells[(25, i)].walkable = False
        
    while 1:
        manage_events(screen, ward, Piece.Pieces)
        draw(screen, ward, Piece.Pieces)
        move(origin, target, ward, screen, green)
        pygame.display.update()
        clock.tick(FPS)

###################################################################################################
### HELPER FUNCTIONS

def pad_space(space):
    w, h = int(space.width/space.size), int(space.height/space.size)
    for i in range(0, h):
        space.cells[(0, i)].walkable = False
        space.cells[(w - 1, i)].walkable = False
    for i in range(0, w):
        space.cells[(i, 0)].walkable = False
        space.cells[(i, h - 1)].walkable = False

def select_cells(event, space, mpos):
    if event.type == pygame.MOUSEBUTTONDOWN:
        if mpos in space.cells.keys():
            space.cells[mpos].toggle_walkability()

def stop_sim(event):
    if event.type == pygame.QUIT:
        pygame.quit()
        sys.exit()

def manage_events(screen, space, pieces):
    mpos = tuple([int(math.floor(i / space.size)) for i in pygame.mouse.get_pos()])
    for event in pygame.event.get():
        stop_sim(event)
        select_cells(event, space, mpos)
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_UP:
                for p in pieces:
                    if p.is_selected:
                        p.move_up()
            elif event.key == pygame.K_DOWN:
                for p in pieces:
                    if p.is_selected:
                        p.move_down()
            elif event.key == pygame.K_LEFT:
                for p in pieces:
                    if p.is_selected:
                        p.move_left()
            elif event.key == pygame.K_RIGHT:
                for p in pieces:
                    if p.is_selected:
                        p.move_right()

def draw(screen, space, pieces):
    screen.fill(white)
    space.draw_space(screen)
    for p in pieces:
        p.draw_piece(screen)

def move(piece, target, space, screen, pathcolor):
    S = Search((piece.x, piece.y), (target.x, target.y), space)
    S.draw_route(S.path, screen, pathcolor)
    if len(S.path) > 1:
        piece.move(S.path[1])
        S.path.pop(0)

    
######################################################################################################
#CLASSES*****

class Space:
    def __init__(self, width, height, size):
        self.width = width
        self.height = height
        self.size = size  # size of each cell of the space
        self.cells = dict()  # A dictionary of all cells in the space
        self.create_cells()

    def create_cells(self):
        """Creates space as a dictionary of cells"""
        for i in range(int(self.width / self.size)):
            for j in range(int(self.height / self.size)):
                self.cells[(i, j)] = Cell(i, j, self.size)

    def inside(self, c):
        """Return true if space coordinate c is inside space"""
        (x, y) = c
        return 0 <= x < int(self.width / self.size) and 0 <= y < int(self.height / self.size)

    def passable(self, c):
        return c in self.cells.keys() and self.cells[c].walkable and not self.cells[c].occupied
    
    def neighbours(self, c, allcells=False):
        """returns grid coordinates for available 
        :type allcells: boolean
           (walkable, inbounds) neighbours of cell (c.x,c.y) """  # Pathfinding
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

    def draw_space(self, screen):
        for c in self.cells:
            self.cells[c].draw_cell(screen)

class Cell:
    def __init__(self, x, y, size):
        self.x = x
        self.y = y
        self.size = size
        self.walkable = True
        self.occupied = False
        self.cost = 1
        self.room = None  # The room that this cell belongs to.
        self.rect = pygame.Rect(self.x*self.size, self.y*self.size, self.size, self.size)

    def toggle_walkability(self):
        if self.walkable: self.walkable = False
        else: self.walkable = True
    
    def draw_cell(self, screen, color = steelblue, width = 1):
        if self.walkable:
            pygame.draw.rect(screen, color, self.rect, 1)
        if not self.walkable:
            pygame.draw.rect(screen, yellow, self.rect)

class Piece:
    Pieces = list()
    def __init__(self, name, x, y, size, space, color):
        self.name = name
        self.x = x
        self.y = y
        self.size = size
        self.space = space
        self.cell = self.space.cells[(self.x, self.y)]
        self.cell.occupied = True
        self.is_selected = False
        self.color = color
        Piece.Pieces.append(self)

    def draw_piece(self, screen, color = (0,0,0)):
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
        if (tx, ty) in self.space.cells.keys() and self.space.cells[tx, ty].walkable and not self.space.cells[tx, ty].occupied:
            self.x -= 1
            space.cells[(tx+1,ty)].walkable = True

    def move_right(self):
        """ Moves selected Person left by one cell """
        tx, ty = self.x + 1, self.y
        if (tx, ty) in self.space.cells.keys() and self.space.cells[tx, ty].walkable and not self.space.cells[tx, ty].occupied:
            self.x += 1
            space.cells[(tx-1,ty)].walkable = True

    def move_up(self):
        """ Moves selected Person left by one cell """
        tx, ty = self.x, self.y - 1
        if (tx, ty) in self.space.cells.keys() and self.space.cells[tx, ty].walkable and not self.space.cells[tx, ty].occupied:
            self.y -= 1
            space.cells[(tx,ty+1)].walkable = True

    def move_down(self):
        """ Moves selected Person left by one cell """
        tx, ty = self.x, self.y + 1
        if (tx, ty) in self.space.cells.keys() and self.space.cells[tx, ty].walkable and not self.space.cells[tx, ty].occupied:
            self.y += 1
            space.cells[(tx,ty-1)].walkable = True

    def toggle_selected(self, mpos):
        if mpos[0] == self.x and mpos[1] == self.y:
            if not self.is_selected:
                self.is_selected = True
            else:
                self.is_selected = False
            self.space.cells[mpos].walkable = True


################################################################################# SEARCH ####################################################################
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

    def get(self): #Gets the smallest element and removes it from the tree.
        return heapq.heappop(self.elements)[1]
    
    def length(self):
        return len(self.elements)
    
    def printqueue(self):
        print self.elements

class Search:
    def __init__(self, start, goal, space):
        self.start = start
        self.goal = goal
        self.space = space
        self.open_cells = PriorityQueue()
        self.came_from = dict()
        self.cost_so_far = dict()
        self.x = self.space.width/self.space.size
        self.y = self.space.height/self.space.size
        self.path = self.get_jps_path()        
        #self.path = self.get_path()        

    def get_jps_path(self):
        self.open_cells.put(self.start,0)
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
                new_cost = self.cost_so_far[loc] + cost
                self.cost_so_far[(cx, cy)] = self.cost_so_far[loc] + cost
                goal_cost = self.min_cost((cx, cy), self.goal)
                self.open_cells.put((cx, cy), self.cost_so_far[(cx, cy)] + goal_cost)
                self.came_from[(cx, cy)] = loc
                break
            if not self.space.cells[(cx + dx, cy)].walkable and self.space.cells[(cx + dx, cy + dy)].walkable:
                new_cost = self.cost_so_far[loc] + cost
                if (cx, cy) not in self.cost_so_far or new_cost < self.cost_so_far[(cx, cy)]:
                    self.cost_so_far[(cx, cy)] = self.cost_so_far[loc] + cost
                    goal_cost = self.min_cost((cx, cy), self.goal)
                    self.open_cells.put((cx, cy), self.cost_so_far[(cx, cy)] + goal_cost)
                    self.came_from[(cx, cy)] = loc
                    break
            else:
                if (cx, cy) not in self.cost_so_far or self.cost_so_far[loc] + cost < self.cost_so_far[(cx, cy)]:
                    self.cost_so_far[(cx, cy)] = self.cost_so_far[loc] + cost
                found = self.test_orthogonal((cx, cy), (dx, 0))
                if found:
                    goal_cost = self.min_cost((cx, cy), self.goal)
                    self.open_cells.put((cx, cy), self.cost_so_far[(cx, cy)] + goal_cost)
                    self.came_from[(cx, cy)] = loc

            if not self.space.cells[(cx, cy + dy)].walkable and self.space.cells[(cx + dx, cy + dy)].walkable:
                new_cost = self.cost_so_far[loc] + cost
                if (cx, cy) not in self.cost_so_far or new_cost < self.cost_so_far[(cx, cy)]:
                    self.cost_so_far[(cx, cy)] = self.cost_so_far[loc] + cost
                    goal_cost = self.min_cost((cx, cy), self.goal)
                    self.open_cells.put((cx, cy), self.cost_so_far[(cx, cy)] + goal_cost)
                    self.came_from[(cx, cy)] = loc
                    break
            else:
                if (cx, cy) not in self.cost_so_far or self.cost_so_far[loc] + cost < self.cost_so_far[(cx, cy)]:
                    self.cost_so_far[(cx, cy)] = self.cost_so_far[loc] + cost
                found = self.test_orthogonal((cx, cy), (0, dy))
                if found:
                    goal_cost = self.min_cost((cx, cy), self.goal)
                    self.open_cells.put((cx, cy), self.cost_so_far[(cx, cy)] + goal_cost)
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
                goal_cost = self.min_cost((cx, cy), self.goal)
                self.open_cells.put((cx, cy), self.cost_so_far[(cx, cy)] + goal_cost)
                self.came_from[(cx, cy)] = loc
                found = True
                return found
            if dx == 0:
                c1 = not self.space.cells[(cx + 1, cy)].walkable and self.space.cells[(cx + 1, cy + dy)].walkable
                c2 = not self.space.cells[(cx - 1, cy)].walkable and self.space.cells[(cx - 1, cy + dy)].walkable
                if c1 or c2:
                    new_cost = self.cost_so_far[loc] + cost
                    if (cx, cy) not in self.cost_so_far or new_cost < self.cost_so_far[(cx, cy)]:
                        self.cost_so_far[(cx, cy)] = self.cost_so_far[loc] + cost
                        goal_cost = self.min_cost((cx, cy), self.goal)
                        self.open_cells.put((cx, cy), self.cost_so_far[(cx, cy)] + goal_cost)
                        self.came_from[(cx, cy)] = loc
                        found = True
                        return found
            if dy == 0:
                c1 = not self.space.cells[(cx, cy + 1)].walkable and self.space.cells[(cx + dx, cy + 1)].walkable
                c2 = not self.space.cells[(cx, cy - 1)].walkable and self.space.cells[(cx + dx, cy - 1)].walkable                                
                if c1 or c2:
                    new_cost = self.cost_so_far[loc] + cost
                    if (cx, cy) not in self.cost_so_far or new_cost < self.cost_so_far[(cx, cy)]:
                        self.cost_so_far[(cx, cy)] = self.cost_so_far[loc] + cost
                        goal_cost = self.min_cost((cx, cy), self.goal)
                        self.open_cells.put((cx, cy), self.cost_so_far[(cx, cy)] + goal_cost)
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
        self.cost_so_far[self.start] = 0 # Keeps track of F costs.
        while not self.open_cells.empty():
            current = self.open_cells.get()
            if self.goal in self.space.neighbours(current): break
            elif current == self.goal: break
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
        h = int(self.space.size / 2)
        draw_this = list()
        for c in route:
            c = list(c)
            c[0] = c[0] * self.space.size + h
            c[1] = c[1] * self.space.size + h
            draw_this.append((c[0], c[1]))
        if len(draw_this) >= 2:
            pygame.draw.lines(screen, color, False, draw_this, 2)


    def origin_cost(self, c):
        costs = dict()
        for n in self.space.neighbours(c):
            if not (n[0] == c[0] or n[1] == c[1]): costs[n] = 14
            else: costs[n] = 10
        return costs

    def goal_cost(self, c):
        x1, y1 = self.goal
        costs = dict()
        for n in self.space.neighbours(c):
            x2, y2 = n
            if abs(y2 - y1) > abs(x2 - x1):
                final = 14 * abs(x2 - x1) + 10 * abs((y2 - y1) - (x2 - x1))
            else:
                final =  14 * abs(y2 - y1) + 10 * abs((y2 - y1) - (x2 - x1))
            costs[n] = final
        return costs



if __name__ == "__main__":
    run()
