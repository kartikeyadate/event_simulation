#!/usr/bin/python3.6
#simulate.py This file contains the description of the instance of the simulation.

import sys
import math
import random
import pygame
from colors import *
from entities import *

def run():
    pygame.init()
    clock = pygame.time.Clock()
    frame = 100
    w, h = 800, 600
    s = 10
    Cell.create_space(w,h,s)
    Collection.mzt(22,18,tl=(1,1))
    zones = list(Collection.Z.keys())
    unavailable = set()
    one = "a","b","c","d","e","f","g","h", "i", "j", "k", "l", "m", "n", "o"
    #two = "p","q","r","s","t","u","v","w", "x", "y", "z"
    for o in one:
        Actor(o, zone = random.choice(zones), color = tomato)

    screen = pygame.display.set_mode((w, h))  # create screen
    pygame.display.set_caption("SCHEDULED MEETINGS")

    create_events(steps=7)
    ulog = set()
    tf = 0
    mid = "uns_0"
    #Collection.test_assignments()
    while True:
        tf += 1
        screen.fill(white)
        mid, ulog = execute(screen, one, mid, ulog)
        Cell.draw_barriers(screen,color=black)
        Collection.draw_everything(screen)
        #Target.draw_all_targets(screen)
        Actor.draw_all_actors(screen, min_size = 6)
        manage_io_events(screen, highlight = True, report = False)
        pygame.display.update()
        clock.tick(frame)

def create_events(steps = 5):
    e = Event("A")
    s = 0
    zones = list(Collection.Z.keys())
    actors = list(Actor.A.keys())
    stepcount = 1
    t = 0
    used = set()
    while s < steps:
        z = random.choice(list(set(zones).difference(used)))
        used.add(z)
        sx,sy = Collection.Z[z].center_cell
        meeting = random.choice(range(3,6))
        sact = random.sample(actors,meeting)
        step = Step(str(stepcount), e.name, actors = set(sact), target = Target(str(t), x=sx, y=sy, zone = z), duration = random.choice(range(15,40)))
        e.add_step(step)
        s += 1

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
                reset_events()

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

def reset_events():
    for m in Meet.M.keys():
        Meet.M[m].kill()

    for e in Event.E.keys():
        Event.E[e].current_stage = 0
        for s in Event.E[e].steps:
            s.state = "not_initialized"
            s.progress = 0

    create_events()


def move(screen, one, two, engaged):
    """
    All scheduled moves
    """
    actors = len(one)
    for i in range(actors):
        if i not in engaged:
            Move(Actor.A[one[i]],Actor.A[two[i]],screen,graph=Collection.TG)

def execute(screen, group,uns,log):
    """
    c = int(uns.split("_")[1])
    possible = Actor.possible_unscheduled(group)
    possible = set(possible).difference(log)
    for (zone, actors) in possible:
        c += 1
        uns = "uns_" + str(c)
        Meet(uns, current_participants = list(actors), zone = zone, duration = random.choice(range(10,30)))

    for m in Meet.M.keys():
        if "uns_" in m and Meet.M[m].state == "completed":
            ma = Meet.M[m].current_participants
            mz = Meet.M[m].zone
            log.add((mz,tuple(sorted(ma))))
            Meet.M[m].kill()
        else:
            Meet.M[m].locate()
            Meet.M[m].proceed(screen)
    """

    for e in Event.E.keys():
        Event.E[e].execute(screen)

    return uns, log



if __name__ == "__main__":
    run()
