#!/usr/bin/python3.6
#simulate.py This file contains the description of the instance of the simulation.

import sys
import math
import random
import pygame
from colors import *
from entities import *

def run(img = "cardio.png", s=5):
    pygame.init()
    clock = pygame.time.Clock()
    frame = 100
    w, h = 1500,600
    s = 10
    Cell.create_space(w,h,s)
    Collection.mzt(22,18,tl=(1,1))
    zones = list(Collection.Z.keys())
    unavailable = set()
    one = "a","b","c","d","e","f","g","h", "i", "j", "k"
    two = "p","q","r","s","t","u","v","w", "x", "y", "z"
    groups = one, two
    for o in one:
        Actor(o, zone = random.choice(zones), color = tomato)
    for o in two:
        Actor(o, zone = random.choice(zones), color = steelblue)

    screen = pygame.display.set_mode((w, h))  # create screen
    pygame.display.set_caption("UNSCHEDULED MEETINGS")
    #background = pygame.image.load(img).convert()
    """
    unscheduled_one = Meet("all_u_one", "u", all_participants = list(one))
    unscheduled_two = Meet("all_u_two", "u", all_participants = list(two))
    uns = [unscheduled_two]
    """
    ulog = set()
    m = 0
    tf = 0
    Collection.test_assignments()
    count = 0
    while True:
        tf += 1
        screen.fill(white)
        ulog, m = decisions(screen, groups, ulog, m)
        if len(ulog) > count:
            count = len(ulog)
            print(str(len(ulog)) + " different meetings have occured.")

        Cell.draw_barriers(screen,color=black)
        Collection.draw_everything(screen)
        #Target.draw_all_targets(screen)
        Actor.draw_all_actors(screen, min_size = 6)
        manage_io_events(screen, highlight = True, report = False)
        pygame.display.update()
        clock.tick(frame)

def manage_io_events(screen, highlight = False, report = False, possible = None):
    mpos = tuple([math.floor(i /Cell.size) for i in pygame.mouse.get_pos()])
    if report:
        if mpos in Cell.C.keys() and (Cell.C[mpos].in_zone or Cell.C[mpos].in_threshold or Cell.C[mpos].is_barrier):
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
            Collection.Z[z].draw(screen, color = coral)
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

def reset_actor_positions():
    zones = set(Collection.Z.keys())
    for a in Actor.A.keys():
        u = Actor.A[a].unavailable
        z = random.choice(list(zones.difference(u)))
        cells = Collection.Z[z].cells
        newpos = random.choice(list(cells))
        Actor.A[a].move(newpos)
        Actor.A[a].state = "idle"

def move(screen, one, two, engaged):
    """
    All scheduled moves
    """
    actors = len(one)
    for i in range(actors):
        if i not in engaged:
            Move(Actor.A[one[i]],Actor.A[two[i]],screen,graph=Collection.TG)

def decisions(screen, groups, log, me):
    one, two = groups
    actors = min(len(one), len(two))
    for i in range(actors):
        if Actor.A[one[i]].state != "going_to_meet":
            Move(Actor.A[one[i]], Actor.A[two[i]], screen, graph=Collection.TG, unavailable=Actor.A[one[i]].unavailable)

    possibles = Actor.possible_unscheduled(one)
    #Create possible new meetings.
    for (z,p) in possibles:
        print((z, tuple(p)), z,tuple(p) in log)
        if (z,tuple(p)) not in log and str(me) not in Meet.M.keys():
            m = Meet(str(me), current_participants = p, zone = z, duration = random.choice(range(15, 40)))
            #print('Added meeting between ' + ', '.join(p) + ' in zone ' + z)
            me +=1

    #Update existing meetings.
    torem = set()
    for m in Meet.M.keys():
        if Meet.M[m].state == "not_initialized":
            Meet.M[m].locate()
        out = Meet.M[m].proceed(screen)
        if out is not None:
            log.add(out)
    print(len(log), "meetings added.")
    #print(me, log)

    return log, me


if __name__ == "__main__":
    run()
