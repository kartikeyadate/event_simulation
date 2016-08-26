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
    Collection.correct_cell_allocation()
    Collection.create_threshold_graph()
    Collection.create_zone_graphs()
    joe = Actor("joe", zone = random.choice(list(Collection.Z.keys())))
    target = Actor("target", zone = random.choice(list(Collection.Z.keys())), color = orange)
    tf = 0
    while True:
        tf += 1
        screen.fill(white)
        Cell.draw_barriers(screen)
        Collection.draw_everything(screen)
        joe.draw(screen)
        target.draw(screen)
        tg = Collection.TG
        search(joe, target, tg, screen)
        manage_events(screen)
        pygame.display.update()
        clock.tick(FPS)
    pass

################### EVENT FUNCTIONS ############################################################
        
def manage_events(screen):
    mpos = tuple([math.floor(i /Cell.size) for i in pygame.mouse.get_pos()])
    highlight_threshold(screen, mpos)
    highlight_zone(screen, mpos)
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit

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
    if a.zone == b.zone and (a.zone is not None or b.zone is not None):
        path = zone_search(a, b, a.zone)
        if path is not None:
            path.move()
    elif a.zone != b.zone:
        S = threshold_search(a, b, g)
        if S.path is not None:
            S.draw_route(screen, color = darkgrey)
            if len(S.path) > 1:
                s, g =  S.path[:2]
                ZS = zone_search(s,g)
                if ZS.path is not None:
                    ZS.draw_route(screen, color = red)

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


def get_zone(a, b):
    if Cell.C[a].zone is not None:
        return Cell.C[a].zone
    elif Cell.C[b].zone is not None:
        return Cell.C[b].zone
    elif Cell.C[b].zone is None and Cell.C[a].zone is None:
        zones = Cell.C[a].zones.intersection(Cell.C[b].zones)
        return zones[0]        
    
"""
def search(actor_a, actor_b, threshold_graph, screen):
    ax, ay = actor_a.x, actor_a.y
    bx, by = actor_b.x, actor_b.y
#    poison_threshold = actor_a.threshold
    if not Cell.C[(ax, ay)].zone == Cell.C[(bx, by)].zone:
        if (ax, ay) not in threshold_graph:
            threshold_graph[(ax,ay)] = [i for i in Collection.Z[Cell.C[(ax,ay)].zone].threshold_cells if not Cell.C[i].is_barrier]
        if (bx, by) not in threshold_graph:
            threshold_graph[(bx,by)] = [i for i in Collection.Z[Cell.C[(bx,by)].zone].threshold_cells if not Cell.C[i].is_barrier]
        S = Search((ax, ay), (bx, by), graph = threshold_graph)
        if S.path is not None:
            if len(S.path) > 1:
                S.draw_route(screen, color = verylightgrey)
                s, g = S.path[:2]
                z = Cell.C[s].zone
                search_graph = Collection.Z[z].graph
                if s not in search_graph:
                    search_graph[s] = Cell.C[s].nbrs
                if g not in search_graph:
                    search_graph[g] = Cell.C[s].nbrs
                s_internal = Search(s, g, graph = search_graph)
                if s_internal.path is not None and len(s_internal.path) > 1:
                    s_internal.draw_route(screen, color = white)
                    actor_a.move(s_internal.path[1])
                    s_internal.path.pop(0)
#                elif s_internal.path is None:
#                    print("No path found. Waiting for things to improve..")                

#        elif S.path is None:
#            print("No threshold available. Waiting for things to improve... ")

    elif Cell.C[(ax, ay)].zone == Cell.C[(bx, by)].zone:
        z = Cell.C[(ax, ay)].zone
        s, g = (ax, ay), (bx, by)
        search_graph = Collection.Z[z].graph
        if s not in search_graph:
            search_graph[s] = Cell.C[s].neighbours()
        if g not in search_graph:
            search_graph[g] = Cell.C[s].neighbours()
        s_internal = Search(s, g, search_graph)
        if s_internal.path is not None and len(s_internal.path) > 1:
            s_internal.draw_route(screen, color = midnightblue)
            actor_a.move(s_internal.path[1])
            s_internal.path.pop(0)
#        elif s_internal.path is None:
#            print("No path found. Waiting for things to improve..")                
"""        
 
def get_search_zone(c1, c2):
    C1 = Cell.C[c1].zones
    C2 = Cell.C[c2].zones
    intersection = C1.intersection(C2)
    sz = list(C1.intersection(C2))[0]
    if sz is None:
        print("No search zone found")
    else:        
       return sz


if __name__ == "__main__":
    run("Cardiology_2.png", s = 4)    

