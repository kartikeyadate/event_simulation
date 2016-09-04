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
    pygame.display.set_caption("IDEALIZED HOSPITAL WARD")
    Collection.generate_zones_and_thresholds()
    background = pygame.image.load(img).convert()
    target = Actor("target", x = 38, y = 7, zone = "13", color = black)
    make_actors(40)
    tf = 0
    v_num = 0
    g = Collection.TG
    while True:
        tf += 1
        screen.fill(white) #screen.blit(background,(0,0))
        conduct_searches(screen)
        v_num = spawn_visitors(v_num, tf, g, target, screen, start_in = "65", interval = range(5, 60), unavailable = {"21", "31", "33", "47"})
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
            #Collection.Z[z].draw(screen, color = powderblue)
            label(screen, z)

def highlight_threshold(screen, mpos):
    for t in Collection.T:
        if mpos in Collection.T[t].cells:
            for c in Collection.TG[mpos]:
                Cell.C[c].draw(screen, drawing_type = "graph", color = tomato)

def label(screen, z):
    f = pygame.font.SysFont("monospace", 12)
    l = f.render(Collection.Z[z].ID, True, (10, 10, 10))
    screen.blit(l, Collection.Z[z].center)

################################################################################
################### SEARCH FUNCTIONS ###########################################
################################################################################
def conduct_searches(screen):
    a = [i for i in Actor.A.keys() if i.isdigit() and int(i) % 2 != 0]
    t = [i for i in Actor.A.keys() if i.isdigit() and int(i) % 2 == 0]
    s = min(len(a), len(t))
    tg = Collection.TG
    for i in range(s):
        Move(Actor.A[str(a[i])], Actor.A[str(t[i])], screen, graph = tg)

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
        if a.isdigit():
            new_pos = random.choice(list(Collection.Z[random.choice(available_zones)].cells))
            Actor.A[a].move(new_pos)

def spawn_visitors(num, tf, graph, target, screen, start_in = None, interval = range(5, 25), unavailable = set()):
    """
    Spawns visitors at time interval interval measured by time frame tf.
    Visitors are actors identified with a "v" as the last character in their alphanumeric name.
    Visitors move towards their target and die after reaching it.
    """
    inter = random.choice(interval)
    if tf % inter == 0:
        v_name = str(num) + "v"
        Actor(v_name, zone = start_in, color = teal)
        num += 1

    done = set()
    for actor in Actor.A.keys():
        if actor[-1] == "v":
            if (Actor.A[actor].x, Actor.A[actor].y) in Cell.C[(target.x, target.y)].nbrs:
                done.add(actor)

    for d in done:
        Actor.A[d].kill()
        print("Killed", d)

    #print("Actor dictionary has: ", list(Actor.A.keys()))
    for actor in Actor.A.keys():
        if actor[-1] == "v":
            Move(Actor.A[actor], target, screen, graph = graph, unavailable = unavailable)

    return num

################################################################################
###################### RUN #####################################################
################################################################################

if __name__ == "__main__":
    run("cardio_alt.png", s = 7)
