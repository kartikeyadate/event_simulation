#!/usr/bin/python

import sys, time
import math, random
import pygame

# Colors r,g,b
white = 255, 255, 255
black = 0, 0, 0
red = 255, 0, 0
darkred = 175, 0, 0
green = 0, 255, 0
blue = 0, 0, 255
yellow = 255, 255, 0
lightgrey = 175, 175, 175
darkgrey = 100, 100, 100

def run():
    pygame.init()  # initialize the game engine
    w, h, s = 640, 640,20   # set width and height of the screen
    clock = pygame.time.Clock()  # create a clock object
    FPS = 100  # set frame rate in frames per second.
    assert w % s == 0, "width must be divisible by size"
    assert h % s == 0, "height must be divisible by size"
    screen = pygame.display.set_mode((w, h))  # create screen
    screen.set_alpha(128)
    chess_board = Board(w, h, s)  # Create the space.
    # create the dictionary of cells which constitute space
    chess_board.create_cells()
    Piece("elephant_1", 2, 2, s, chess_board, "orthogonal", blue)
    Piece("pawn_1", 10, 10, s, chess_board, "one_orthogonal_step", darkred)
    Piece("camel_1", 5, 5, s, chess_board, "diagonal", darkgrey)
    Piece("queen_1", 8, 3 , s, chess_board, "queen", green)
    Piece("elephant_2", 6, 5, s, chess_board, "orthogonal", blue)
    Piece("pawn_2", 12, 3, s, chess_board, "one_orthogonal_step", darkred)
    Piece("camel_2", 5, 10, s, chess_board, "diagonal", darkgrey)
    Piece("queen_2", 1, 8 , s, chess_board, "queen", green)
    tf = 1  # total frames
    screen.fill(white)  # set a white background
    run_simulation = True
    while run_simulation:
        simulate(screen, chess_board, Piece.Pieces)
        tf += 1
#        if len(Piece.Pieces) > 1:
        if len(Piece.Pieces) > 0:
#        if len(Piece.Pieces) > 2:
            for p in Piece.Pieces:
                if p.is_alive:
                    p.make_move(screen)

                    p.draw_piece(screen)
                    p.draw_possible_moves(screen)
                    p.draw_safe_moves(screen)
                pygame.display.update()
                clock.tick(FPS)
        elif len(Piece.Pieces) <= 1:
            names = [p.name for p in Piece.Pieces]
            moves = [p.move_count for p in Piece.Pieces]
            print (' and '.join(names), "survived after", max(moves), "moves")
            break


def simulate(screen, space, pieces):
    mpos = tuple([math.floor(i / space.size) for i in pygame.mouse.get_pos()])
    for event in pygame.event.get():
        stop_sim(event)
        move_pieces_with_keys(event, pieces, mpos)
    screen.fill(white)
    space.draw_space(screen)
    for p in pieces:
        draw_piece_states(p, screen)

def draw_piece_states(piece, screen):
    piece.draw_piece(screen)
    piece.draw_possible_moves(screen)
    piece.draw_safe_moves(screen)

def stop_sim(event):
    if event.type == pygame.QUIT:
        pygame.quit()
        sys.exit()

def move_pieces_with_keys(event, pieces, mpos):
    if event.type == pygame.MOUSEBUTTONDOWN:
        for p in pieces:
            p.toggle_selected(mpos)
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

class Piece:
    Pieces = list()
    def __init__(self, name, x, y, size, space, legal_moves, color):
        self.name = name
        self.x = x
        self.y = y
        self.size = size
        self.space = space
        self.cell = self.space.cells[(self.x, self.y)]
        self.is_selected = False
        self.color = color
        self.legal_moves = legal_moves
        self.is_alive = True
        self.move_count = 0
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

    def possible_moves(self):
        my_cell = {(self.x, self.y)}
        occupied_cells, all_cells, possible_cells = set(), set(), set()
        other_occupied_cells = set()
        for p in Piece.Pieces: occupied_cells.add((p.x, p.y)) #find cells occupied by pieces
        other_occupied_cells = occupied_cells.difference(my_cell)
        for c in self.space.cells: all_cells.add(c) #get all cells
        board_width = int(self.space.width / self.space.size)
        board_height = int(self.space.height / self.space.size)
        possible_moves = set()
        if self.legal_moves == "one_orthogonal_step":
            possible_moves.add((self.x + 1, self. y))
            possible_moves.add((self.x, self. y + 1))
            possible_moves.add((self.x, self. y - 1))
            possible_moves.add((self.x - 1, self. y))

        elif self.legal_moves == "orthogonal":
            for i in range(self.x, board_width, 1):
                if (i, self.y) in other_occupied_cells: 
                    possible_moves.add((i, self.y))
                    break
                else: 
                    possible_moves.add((i, self.y))
            for i in range(self.x, -1, -1):
                if (i, self.y) in other_occupied_cells: 
                    possible_moves.add((i, self.y))
                    break
                else: 
                    possible_moves.add((i, self.y))
            for i in range(self.y, board_height, 1):
                if (self.x, i) in other_occupied_cells: 
                    possible_moves.add((self.x, i))
                    break
                else: 
                    possible_moves.add((self.x, i))
            for i in range(self.y, -1, -1):
                if (self.x, i) in other_occupied_cells: 
                    possible_moves.add((self.x, i))
                    break
                else: 
                    possible_moves.add((self.x, i))

        elif self.legal_moves == "diagonal":
            i, j = 1, 1
            while self.x + i < board_width and self.y + j < board_height:
                if (self.x + i, self.y + j) in other_occupied_cells:
                    possible_moves.add((self.x + i, self.y + j))
                    break
                possible_moves.add((self.x + i, self.y + j))
                i += 1
                j += 1
            i, j = 1, 1
            while self.x - i >= 0 and self.y - j >= 0:
                if (self.x - i, self.y - j) in other_occupied_cells:
                    possible_moves.add((self.x - i, self.y - j))
                    break
                possible_moves.add((self.x - i, self.y - j))
                i += 1
                j += 1
            i, j = 1, 1
            while self.x - i >= 0 and self.y + j < board_height:
                if (self.x - i, self.y + j) in other_occupied_cells:
                    possible_moves.add((self.x - i, self.y + j))
                    break
                possible_moves.add((self.x - i, self.y + j))
                i += 1
                j += 1
            i, j = 1, 1
            while self.x + i < board_width and self.y - j >= 0:
                if (self.x + i, self.y - j) in other_occupied_cells:
                    possible_moves.add((self.x + i, self.y - j))
                    break
                possible_moves.add((self.x + i, self.y - j))
                i += 1
                j += 1

        elif self.legal_moves == "queen":
            i, j = 1, 1
            while self.x + i < board_width and self.y + j < board_height:
                if (self.x + i, self.y + j) in other_occupied_cells:
                    possible_moves.add((self.x + i, self.y + j))
                    break
                possible_moves.add((self.x + i, self.y + j))
                i += 1
                j += 1

            i, j = 1, 1
            while self.x - i >= 0 and self.y - j >= 0:
                if (self.x - i, self.y - j) in other_occupied_cells:
                    possible_moves.add((self.x - i, self.y - j))
                    break
                possible_moves.add((self.x - i, self.y - j))
                i += 1
                j += 1

            i, j = 1, 1
            while self.x - i >= 0 and self.y + j < board_height:
                if (self.x - i, self.y + j) in other_occupied_cells:
                    possible_moves.add((self.x - i, self.y + j))
                    break
                possible_moves.add((self.x - i, self.y + j))
                i += 1
                j += 1

            i, j = 1, 1
            while self.x + i < board_width and self.y - j >= 0:
                if (self.x + i, self.y - j) in other_occupied_cells:
                    possible_moves.add((self.x + i, self.y - j))
                    break
                possible_moves.add((self.x + i, self.y - j))
                i += 1
                j += 1

            for i in range(self.x, board_width, 1):
                if (i, self.y) in other_occupied_cells: 
                    possible_moves.add((i, self.y))
                    break
                else: 
                    possible_moves.add((i, self.y))
            for i in range(self.x, -1, -1):
                if (i, self.y) in other_occupied_cells: 
                    possible_moves.add((i, self.y))
                    break
                else: 
                    possible_moves.add((i, self.y))
            for i in range(self.y, board_height, 1):
                if (self.x, i) in other_occupied_cells: 
                    possible_moves.add((self.x, i))
                    break
                else: 
                    possible_moves.add((self.x, i))
            for i in range(self.y, -1, -1):
                if (self.x, i) in other_occupied_cells: 
                    possible_moves.add((self.x, i))
                    break
                else: 
                    possible_moves.add((self.x, i))
        possible_cells = possible_moves.difference(my_cell)
        possible_cells = possible_cells.intersection(all_cells)
        return possible_cells
    
    def safe_moves(self):
        possible = self.possible_moves()
        my_piece = {(self.x, self.y)}
        threat_cells = list()
        for p in Piece.Pieces:
            if not (p.x == self.x and p.y == self.y):
                threat_cells += list(p.possible_moves())
        safe_cells = possible.difference(set(threat_cells))
        return safe_cells, threat_cells

    def kill_moves(self):
        possible = self.possible_moves()
        others = set()
        for p in Piece.Pieces:
            if not (p.x == self.x and p.y == self.y):
                others.add((p.x, p.y))
        kill_moves = others.intersection(possible)
        if len(kill_moves) > 0: 
            print("Kill move available after", self.move_count, "moves")
        return others.intersection(possible)

    def draw_possible_moves(self, screen):
        for c in self.possible_moves():
            self.space.cells[c].draw_cell(screen,(250,100,100), 2)

    def draw_safe_moves(self, screen):
        for c in self.safe_moves()[0]:
            self.space.cells[c].draw_cell(screen,(30,144,255), 2)

   
    def make_move(self, screen):
        safe, unsafe = self.safe_moves()
        kill = self.kill_moves()
        if len(kill) > 0:
            to = random.choice(list(kill))
            for p in Piece.Pieces:
                if p.x == to[0] and p.y == to[1]:
                    p.is_alive = False
                    print(p.name, "eliminated after", p.move_count, "moves")
                    Piece.Pieces.remove(p)
                    break
        elif len(safe) > 0:
            to = random.choice(list(safe))
        elif len(unsafe) > 0:
            print("Unsafe move forced!")
            to = random.choice(list(unsafe))
        (x,y) = self.x, self.y
        self.move(to)
        pygame.draw.rect(screen, white, self.space.cells[(x,y)])        
        self.space.cells[(x,y)].draw_cell(screen, lightgrey)
        self.move_count += 1



    def move(self, new):
        """Move player to Grid Cell x, y. This is designed for A*"""
        self.x, self.y = new

    def move_left(self):
        """ Moves selected Person left by one cell """
        tx, ty = self.x - 1, self.y
        if (tx, ty) in self.space.cells.keys() and self.space.cells[tx, ty].walkable:
            self.x -= 1
            self.space.cells[(self.x + 1, self.y)].walkable = True

    def move_right(self):
        """ Moves selected Person left by one cell """
        tx, ty = self.x + 1, self.y
        if (tx, ty) in self.space.cells.keys() and self.space.cells[tx, ty].walkable:
            self.x += 1
            self.space.cells[(self.x - 1, self.y)].walkable = True

    def move_up(self):
        """ Moves selected Person left by one cell """
        tx, ty = self.x, self.y - 1
        if (tx, ty) in self.space.cells.keys() and self.space.cells[tx, ty].walkable:
            self.y -= 1
            self.space.cells[(self.x, self.y + 1)].walkable = True

    def move_down(self):
        """ Moves selected Person left by one cell """
        tx, ty = self.x, self.y + 1
        if (tx, ty) in self.space.cells.keys() and self.space.cells[tx, ty].walkable:
            self.y += 1
            self.space.cells[(self.x, self.y - 1)].walkable = True

    def toggle_selected(self, mpos):
        if mpos[0] == self.x and mpos[1] == self.y:
            if not self.is_selected:
                self.is_selected = True
            else:
                self.is_selected = False


class Cell:
    def __init__(self, x, y, size):
        self.x = x
        self.y = y
        self.size = size
        self.walkable = True
        self.occupied = False
        self.room = None  # The room that this cell belongs to.
        self.rect = pygame.Rect(self.x*self.size, self.y*self.size, self.size, self.size)

    def toggle_walkability(self):
        if self.walkable:
            self.walkable = False
        else:
            self.walkable = True
    
    def set_unwalkable(self):
        self.walkable = False    
    
    def draw_cell(self, screen, color, width = 1):
        pygame.draw.rect(screen, color, self.rect, width)


class Board:
    def __init__(self, width, height, size):
        self.width = width
        self.height = height
        self.size = size  # size of each cell of the space
        self.cells = dict()  # A dictionary of all cells in the space
        self.is_neighbour = False

    def create_cells(self):
        """Creates space as a dictionary of cells"""
        for i in range(int(self.width / self.size)):
            for j in range(int(self.height / self.size)):
                self.cells[(i, j)] = Cell(i, j, self.size)

    def draw_space(self, screen):
        """Draw Grid on screen in a given color"""
        for c in self.cells:
            self.cells[c].draw_cell(screen, lightgrey)

    def inside(self, c):
        """Return true if space coordinate c is inside space"""
        (x, y) = c
        return 0 <= x < int(self.width / self.size) and 0 <= y < int(self.height / self.size)

    def passable(self, c):
        self.get_occupied_cells()
        return self.cells[c].walkable
    
    def neighbours(self, c, allcells=False):
        """returns grid coordinates for available 
        :type allcells: boolean
           (walkable, inbounds) neighbours of cell (c.x,c.y) """  # Pathfinding
        x, y = c
        results = [(x + 1, y), (x - 1, y),
                   (x, y + 1), (x, y - 1),
                   (x + 1, y + 1), (x + 1, y - 1),
                   (x - 1, y + 1), (x - 1, y - 1)]
        if allcells:
            return results
        results = filter(self.inside, results)
        results = filter(self.passable, results)
        return results
    

if __name__ == "__main__":
    run()

