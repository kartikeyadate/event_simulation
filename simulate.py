#!/usr/bin/python3.5 
#simulate.py This file contains the description of the instance of the simulation.

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
    Collection.generate_zones_and_thresholds()
    ### Sets of zones by zone type.
    corridor = {"13", "14", "15", "16", "3", "6", "22", "28", "34", "41", "51", "58", "65", "70", "71", "72", "73", "79", "84", "89", "44", "45", "46", "47"}
    day_room = {"50", "54", "57", "62", "64", "69"}
    nurse_station = {"21", "31", "33"}
    patient_rooms = {"0", "1", "2","4", "7", "18", "23", "30", "35", "43", "52", "59", "66", "74", "80", "85", "90"}
    #############################################################
    print("Created space consisting of ", len(Cell.C), "cells.")
    screen = pygame.display.set_mode((w, h))  # create screen
    pygame.display.set_caption("IDEALIZED HOSPITAL WARD")
    background = pygame.image.load(img).convert()
    target = Actor("target", x = 38, y = 7, zone = "13", color = black)
    v_name = make_actors(v_name = 0, n = 50, actor_type = "staff")
    v_name = make_actors(v_name = v_name, actor_type = "nurses", color = green, locations = ((50, 43, "21"), (55, 43, "21"), (60, 43, "21"), (78, 43, "33"), (83, 43, "33"), (88, 43, "33")))
    v_num = int(v_name)
    tf = 0
    g = Collection.TG
    while True:
        tf += 1
        screen.fill(white) #screen.blit(background,(0,0))
        conduct_searches(screen, actor_type = "staff")
        v_num = spawn_actors(v_num, tf, g, target, screen, start_in = "70", interval = range(5, 60), unavailable = {"21", "31", "33"}, actor_type = "visitor")
        Cell.draw_barriers(screen)
        Collection.draw_everything(screen)
        Actor.draw_all_actors(screen, min_size = 5)
        manage_io_events(screen, highlight = True, report = True, possible = corridor)
        pygame.display.update()
        clock.tick(FPS)

################################################################################
################### EVENT FUNCTIONS ############################################
################################################################################
def manage_io_events(screen, highlight = False, report = False, possible = None):
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
                reset_actor_positions(actor_type = "staff", possible = possible)

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
def conduct_searches(screen, actor_type = None):
    """
    Conducts n/2 searches among the population of n actors.
    """
    a = [i for i in Actor.A.keys() if actor_type in i and int(i.split("_")[0]) % 2 != 0]
    t = [i for i in Actor.A.keys() if actor_type in i and int(i.split("_")[0]) % 2 == 0]
    s = min(len(a), len(t))
    tg = Collection.TG
    for i in range(s):
        Move(Actor.A[str(a[i])], Actor.A[str(t[i])], screen, graph = tg)

################################################################################
################### ACTOR FUNCTIONS ############################################
################################################################################
def make_actors(v_name = None, n = None, actor_type = None, color = None, locations = None):
    """
    Initialize n actors in available zones.
    """
    if v_name is None:
        v_name = 0
    if n is not None and locations is None:
        available_zones = [i for i in Collection.Z.keys() if len(Collection.Z[i].thresholds) > 0]
        while v_name < n:
            v_name += 1
            actor_name = str(v_name) + "_" + actor_type
            Actor(actor_name, zone = random.choice(available_zones), color = color, actor_type = actor_type)

    if n is None and locations is not None:
        for (x_pos, y_pos, z) in locations:
            v_name += 1
            actor_name = str(v_name) + "_" + actor_type
            Actor(actor_name, x = x_pos, y = y_pos, zone = z, color = color, actor_type = actor_type)
    return v_name

def reset_actor_positions(actor_type = None, possible = None):
    """
    Resets the positions of all actors in all available zones.
    An available zone is one which has at least one threshold.
    """
    if possible is None:
        available_zones = [i for i in Collection.Z.keys() if len(Collection.Z[i].thresholds) > 0]
    else:
        available_zones = list(possible)
    for a in Actor.A:
        if actor_type in a:
            new_pos = random.choice(list(Collection.Z[random.choice(available_zones)].cells))
            Actor.A[a].move(new_pos)

def spawn_actors(num, tf, graph, target, screen, start_in = None, interval = range(5, 25), unavailable = set(), actor_type = None):
    """
    Spawns visitors at time interval interval measured by time frame tf.
    Visitors are actors identified with a "v" as the last character in their alphanumeric name.
    Visitors move towards their target and die after reaching it.
    """

    #initialize new actors.
    inter = random.choice(interval)
    if tf % inter == 0:
        v_name = str(num) + "_" + actor_type
        Actor(v_name, zone = start_in, color = teal, actor_type = actor_type)
        num += 1

    # identify actors who have reached their target.
    done = set()
    for actor in Actor.A.keys():
        if Actor.A[actor].actor_type == actor_type:
            if (Actor.A[actor].x, Actor.A[actor].y) in Cell.C[(target.x, target.y)].nbrs:
                done.add(actor)

    # destroy actors who have reached their target.
    for d in done:
        Actor.A[d].kill()
        print("Killed", d)

    # for all remaining actors, move them towards target.
    for actor in Actor.A.keys():
        if Actor.A[actor].actor_type == actor_type:
            Move(Actor.A[actor], target, screen, graph = graph, unavailable = unavailable)

    return num

################################################################################
######################### INTERACTIONS #########################################
################################################################################
def meetings():
    pass

################################################################################
###################### RUN #####################################################
################################################################################

if __name__ == "__main__":
   run("cardio_alt.png", s = 7)
