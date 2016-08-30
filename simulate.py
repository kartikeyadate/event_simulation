#!/usr/bin/python3.5

import sys, time, math, random, heapq, pygame
from operator import itemgetter
from collections import defaultdict
from colors import *
from entities import *

def run(img, s = 5):
    pygame.init()
    clock = pygame.time.Clock()
    FPS = 5
    w, h = Cell.create_space_from_plan(s, img) #Create a dictionary of all cells.
    print("Created space consisting of ", len(Cell.C), "cells.")
    screen = pygame.display.set_mode((w, h))  # create screen

    Collection.generate_zones_and_thresholds()
    background = pygame.image.load(img).convert()
    make_actors(80)
    tf = 0
    while True:
        tf += 1
        screen.fill(white)
        screen.blit(background,(0,0))
        #Cell.draw_barriers(screen)
        #Collection.draw_everything(screen)
        Actor.draw_all_actors(screen, min_size = 6)
        conduct_searches(screen)
        manage_events(screen, highlight = True, report = False)
        pygame.display.update()
        clock.tick(FPS)

################### EVENT FUNCTIONS ############################################################

def manage_events(screen, highlight = False, report = False):
    mpos = tuple([math.floor(i /Cell.size) for i in pygame.mouse.get_pos()])

    if report:
        if mpos in Cell.C.keys():
            print(Cell.C[mpos])

    if highlight:
        highlight_threshold(screen, mpos)
        highlight_zone(screen, mpos)

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE:
                reset_actor_positions()


def highlight_zone(screen, mpos):
    for z in Collection.Z:
        if mpos in Collection.Z[z].cells:
            Collection.Z[z].draw(screen, color = steelblue)

def highlight_threshold(screen, mpos):
    for t in Collection.T:
        if mpos in Collection.T[t].cells:
            for c in Collection.TG[mpos]:
                Cell.C[c].draw(screen, drawing_type = "graph", color = tomato)


################### SEARCH FUNCTIONS ############################################################

def search(a, b, g, screen):
    if a.zone == b.zone:
        ZS = zone_search((a.x, a.y), (b.x, b.y))
        if ZS.path is not None and len(ZS.path) > 1:
            ZS.draw_route(screen, color = red)
            a.move(ZS.path[1])
            ZS.path.pop(0)

    elif a.zone != b.zone:
        S = threshold_search(a, b, g)
        if S.path is not None:
            S.draw_route(screen, color = darkgrey)
            if len(S.path) > 1:
                ZS = zone_search(S.path[0], S.path[1])
                if ZS.path is not None:
                    ZS.draw_route(screen, color = red)
                    a.move(ZS.path[1])
                    ZS.path.pop(0)



def threshold_search(a, b, g):
    ax, ay = a.x, a.y
    bx, by = b.x, b.y
    if (ax, ay) not in g:
        g[(ax,ay)] = [i for i in Collection.Z[Cell.C[(ax,ay)].zone].threshold_cells if not Cell.C[i].is_barrier]
    if (bx, by) not in g:
        g[(bx,by)] = [i for i in Collection.Z[Cell.C[(bx,by)].zone].threshold_cells if not Cell.C[i].is_barrier]
    return Search((ax, ay), (bx, by), graph = g)

def zone_search(a, b):
    zone = get_zone(a, b)
    return Search(a, b, graph = Collection.Z[zone].graph)


def get_zone(start, target):
    if not Cell.C[start].zones.isdisjoint(Cell.C[target].zones):
        if Cell.C[start].zone is not None:
            return Cell.C[start].zone
        if Cell.C[target].zone is not None:
            return Cell.C[target].zone
        else:
            return list(Cell.C[start].zones.intersection(Cell.C[target].zones))[0]
    elif Cell.C[start].zones.isdisjoint(Cell.C[target].zones):
        if Cell.C[start].zone is not None:
            return Cell.C[start].zone
        if Cell.C[target].zone is not None:
            return Cell.C[target].zone

def conduct_searches(screen):
    a = [i for i in Actor.A.keys() if int(i) % 2 != 0]
    t = [i for i in Actor.A.keys() if int(i) % 2 == 0]
    s = min(len(a), len(t))
    tg = Collection.TG
    for i in range(s):
        search(Actor.A[str(a[i])], Actor.A[str(t[i])], tg, screen)

############################################# ACTOR FUNCTIONS ########################################

def make_actors(n):
    available_zones = [i for i in Collection.Z.keys() if len(Collection.Z[i].thresholds) > 0]
    c = 0
    while c < n:
        Actor(str(c), zone = random.choice(available_zones))
        c += 1

def reset_actor_positions():
    available_zones = [i for i in Collection.Z.keys() if len(Collection.Z[i].thresholds) > 0]
    for a in Actor.A:
        new_pos = random.choice(list(Collection.Z[random.choice(available_zones)].cells))
        Actor.A[a].move(new_pos)





if __name__ == "__main__":
    run("second.png", s = 7)
