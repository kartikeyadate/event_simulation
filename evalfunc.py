#!/usr/bin/python3.5
#evalfunc.py.
#This file contains the program used in the 2017 eCAADe paper. It describes the partial knowledge problem.

import sys
import math
import random
import pygame
from colors import *
from entities import *

def run(img, s=5):
    pygame.init()
    clock = pygame.time.Clock()
    frame = 4
    #Setup space
    w, h = Cell.create_space_from_plan(s, img)
    Collection.generate_zones_and_thresholds()
    print("Created space consisting of ", len(Cell.C), "cells.")
    screen = pygame.display.set_mode((w, h))  # create screen
    pygame.display.set_caption("THE PARTIAL KNOWLEDGE PROBLEM")
    background = pygame.image.load(img).convert()
    #A = Actor("A", x = 14, y = 6, zone = "0", unavailable = {"2"}, color = steelblue)
    A = Actor("A", x = 12, y = 6, zone = "0", color = steelblue)


    B = Actor("B", x = 42, y = 14, zone = "4", color = tomato)
    tf = 0
    g = Collection.TG
    Collection.check_diagonal_thresholds()
    pause = False
    while True:
        tf += 1
        if tf == 7:
            for c in Collection.Z["2"].threshold_cells:
                Cell.C[c].is_occupied = True

        if tf == 23:
            for c in Collection.Z["2"].threshold_cells:
                Cell.C[c].is_occupied = False


        g = Collection.TG
        screen.fill(white)
        Cell.draw_barriers(screen)
        Collection.draw_everything(screen)
        Actor.draw_all_actors(screen, min_size = 6)
        if not pause:
            Move(A, B, screen, unavailable = A.unavailable , graph=g)
            pass
        else:
            f = pygame.font.SysFont("monospace", 16)
            l = f.render("Paused", True, (10, 10, 10))
            screen.blit(l, (100, 50))

        label_all(screen, s)
        pause,tf = manage_io_events(screen,tf, highlight = True, report = True, pause=pause)
        pygame.display.update()
        #print(pause)

        clock.tick(frame)

################################################################################
################### EVENT FUNCTIONS ############################################
################################################################################

def reset_actor(x = 14, y = 6):
    Actor.A["A"].move((x,y))

def manage_io_events(screen,tf, highlight = False, report = False, possible = None, pause = False):
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
                reset_actor()
                tf = 0
                #reset_actor_positions(actor_type = "BLUE", possible = possible)
                #reset_actor_positions(actor_type = "RED", possible = possible)
            if event.key == pygame.K_p:
                if not pause:
                    pause = True
                else:
                    pause = False
    return pause,tf


def highlight_zone(screen, mpos):
    for z in Collection.Z:
        if mpos in Collection.Z[z].cells:
            Collection.Z[z].draw(screen, color = lightgrey)
            label(screen, z)

def highlight_threshold(screen, mpos):
    for t in Collection.T:
        if mpos in Collection.T[t].cells:
            for c in Collection.TG[mpos]:
                Cell.C[c].draw(screen, drawing_type = "graph", color = tomato)

def label(screen, z):
    f = pygame.font.SysFont("monospace", 16)
    l = f.render(Collection.Z[z].ID, True, (10, 10, 10))
    screen.blit(l, Collection.Z[z].center)

def label_all(screen, s):
    f = pygame.font.SysFont("monospace", 20)
    for z in Collection.Z.keys():
        l = f.render("Z"+Collection.Z[z].ID, True, (10, 10, 10))
        screen.blit(l, Collection.Z[z].center)

    for t in Collection.T.keys():
        posx = min([i[0] for i in list(Collection.T[t].cells)])
        posy = min([i[1] for i in list(Collection.T[t].cells)])
        posx = posx*s - 2*s
        posy = posy*s - 2*s
        l = f.render("T"+Collection.T[t].ID, True, (10, 10, 10))
        screen.blit(l, (posx, posy))



################################################################################
################### SEARCH FUNCTIONS ###########################################
################################################################################
def conduct_searches(screen, actor_type = None):
    """
    Conducts n/2 searches among the population of n actors.
    """
    a = [i for i in Actor.A.keys() if Actor.A[i].actor_type == "BLUE"]
    t = [i for i in Actor.A.keys() if Actor.A[i].actor_type == "RED"]
    s = min(len(a), len(t))
    tg = Collection.TG
    for i in range(s):
        Move(Actor.A[str(a[i])], Actor.A[str(t[i])], screen, graph = tg)


################################################################################
################### ACTOR FUNCTIONS ############################################
################################################################################

def infest(n=100, zones = set(), p=10):
    c = 0
    while c < n:
        z = random.choice(list(zones))
        x, y = random.choice(list(Collection.Z[z].cells))
        Cockroach(x,y,4,p,blue)
        c+=1

def update_infestation():
    for r in Cockroach.Roaches:
        r.move_cockroach_randomly()


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
    Unplanned.Completed = set()

def make_actors(v_name = None, n = None, actor_type = None, color = None, threshold = None, unavailable = set(), locations = None):
    """
    Initialize n actors in available zones.
    """
    if v_name is None:
        v_name = 0
    if n is not None and locations is None:
        max_act = v_name + n
        available_zones = [i for i in Collection.Z.keys() if len(Collection.Z[i].thresholds) > 0]
        while v_name < max_act:
            v_name += 1
            actor_name = str(v_name) + "_" + actor_type
            Actor(actor_name, zone = random.choice(available_zones), color = color, threshold=threshold, unavailable = unavailable, actor_type = actor_type)

    if n is None and locations is not None:
        for (x_pos, y_pos, z) in locations:
            v_name += 1
            actor_name = str(v_name) + "_" + actor_type
            Actor(actor_name, x = x_pos, y = y_pos, zone = z, color = color, unavailable = unavailable, actor_type = actor_type)

    return v_name

def spawn_actors(name, tf, graph, target, screen, start_in = None, interval = range(5, 25), unavailable = set(), actor_type = None):
    """
    Spawns visitors at time interval interval measured by time frame tf.
    Visitors are actors identified with a "v" as the last character in their alphanumeric name.
    Visitors move towards their target and die after reaching it.
    """
    num = int(name)
    #initialize new actors.
    inter = random.choice(interval)
    if tf % inter == 0:
        v_name = str(num) + "_" + actor_type
        Actor(v_name, zone = start_in, color = darkkhaki, actor_type = actor_type)
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
        #print("Killed", d)

    # for all remaining actors, move them towards target.
    for actor in Actor.A.keys():
        if Actor.A[actor].actor_type == actor_type:
            Move(Actor.A[actor], target, screen, graph = graph, unavailable = unavailable)

    return str(num)

def setup_friends():
    a = {i for i in Actor.A.keys() if Actor.A[i].actor_type == "BLUE"}
    for act in a:
        Actor.A[act].friends = a.difference({act})

    a = {i for i in Actor.A.keys() if Actor.A[i].actor_type == "RED"}
    for act in a:
        Actor.A[act].friends = a.difference({act})

################################################################################
######################### INTERACTIONS #########################################
################################################################################
def meetings():
    pass

################################################################################
###################### RUN #####################################################
################################################################################

if __name__ == "__main__":
   run("bg.png", s = 15)



