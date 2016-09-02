#!/usr/bin/python3.5 
#simulate.py This file contains the description of the instance of the simulation.
#To run the simulation, run ./simulate.py in the unix terminal

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
    make_actors(50)
    tf = 0
    while True:
        tf += 1
        screen.fill(white)
        #screen.blit(background,(0,0))
        conduct_searches(screen)
        Cell.draw_barriers(screen)
        Collection.draw_everything(screen)
        Actor.draw_all_actors(screen, min_size = 5)
        manage_events(screen, highlight = True, report = False)
        pygame.display.update()
        clock.tick(FPS)

################################################################################
################### EVENT FUNCTIONS ############################################
################################################################################

def manage_events(screen, highlight = False, report = False):
    mpos = tuple([math.floor(i /Cell.size) for i in pygame.mouse.get_pos()])
    if report:
        if mpos in Cell.C.keys():
            print(Cell.C[mpos])
    if highlight:
        highlight_threshold(screen, mpos)
        highlight_zone(screen, mpos)
    for event in pygame.event.get():
        if event.type == pygame.QUIT or (event.type == pygame.KEYDOWN and event.key == pygame.K_q):
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

################################################################################
################### SEARCH FUNCTIONS ###########################################
################################################################################

def search(a, b, g, screen):
    if a.zone == b.zone:
        ZS = zone_search((a.x, a.y), (b.x, b.y), a, b)
        if ZS.path is not None and len(ZS.path) > 1:
            ZS.draw_route(screen, color = red)
            a.move(ZS.path[1])
            ZS.path.pop(0)

    elif a.zone != b.zone:
        S = threshold_search(a, b, g)
        if S.path is not None:
            S.draw_route(screen, color = lightgrey)
            ZS = zone_search(S.path[0], S.path[1], a, b)
            if ZS.path is not None:
                ZS.draw_route(screen, color = red)
                a.move(ZS.path[1])
                ZS.path.pop(0)

def threshold_search(a, b, g):
    A = a.x, a.y
    B = b.x, b.y

    ignore = set()
    for actor in Actor.A.keys():
        if actor != a.name and actor != b.name:
            if Actor.A[actor].threshold is not None:
                ignore = ignore.union(Actor.A[actor].personal_space)
            if Actor.A[actor].zone is not None:
                z = Actor.A[actor].zone
                intersect = Actor.A[actor].personal_space.intersection(Collection.Z[z].threshold_cells)
                if len(intersect) > 0:
                    ignore = ignore.union(intersect)


    if A not in g:
        g[A] = [i for i in Collection.Z[Cell.C[A].zone].threshold_cells]
    if B not in g:
        g[B] = [i for i in Collection.Z[Cell.C[B].zone].threshold_cells]
    return Search(A, B, graph = g, ignore = ignore)

def zone_search(a, b, act, tar):
    zone = get_zone(a, b)
    if zone is None:
        print("Valid zone was not returned!")
    ignore = set()
    for actor in Collection.Z[zone].actors:
        if actor != act.name and actor!= tar.name:
            ignore = ignore.union(Actor.A[actor].personal_space)

    return Search(a, b, graph = Collection.Z[zone].graph, ignore = ignore)

def get_zone(start, target):
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

def conduct_searches(screen):
    a = [i for i in Actor.A.keys() if int(i) % 2 != 0]
    t = [i for i in Actor.A.keys() if int(i) % 2 == 0]
    s = min(len(a), len(t))
    tg = Collection.TG
    for i in range(s):
        search(Actor.A[str(a[i])], Actor.A[str(t[i])], tg, screen)

################################################################################
################### ACTOR FUNCTIONS ############################################
################################################################################

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

################################################################################
###################### RUN #####################################################
################################################################################

if __name__ == "__main__":
    run("cardio_alt.png", s = 7)
