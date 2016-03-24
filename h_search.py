#!/usr/bin/python3.5

import sys, time, math, random, heapq, pygame
from operator import itemgetter
from collections import defaultdict
from colors import *
from eventsim_classes import *


def run():
    pygame.init()
    w, h, s = 1400, 800, 10
#    w, h, s = 1100, 600, 10
    clock = pygame.time.Clock()  # create a clock object
    FPS = 5  # set frame rate in frames per second.
    screen = pygame.display.set_mode((w, h))  # create screen
    create_space(w, h, s) #Create a dictionary of all cells.
    print("Created space of width " + repr(w) + " pixels, height " + repr(h) + " pixels and " +  repr(int(w/s)*int(h/s)) + " cells")
    print("Creating zones, thresholds and search graphs. This may take a while.... ")
    threshold_graph = create_zones(w, h, s, zone_size = 13) #Create zones, thresholds, walls search graphs
    poison_threshold = 20
    create_actors(50, poison_threshold)
    infested_zones = choose_zones_to_infest(3)
    for zone in infested_zones:
        make_roaches(25, 3, 15, tomato, z = zone)
        make_roaches(8, 5, -40, lightgrey, z = zone)
    make_roaches(350, 3, 20, tomato)  # 1 DataMap        
    make_roaches(75, 5, -50, lightgrey)  # 3 DataMap
    move_actors(infested_zones)
    tf = 0
    while True:
        tf += 1
        start = time.clock()
        screen.fill(white)
        move_roaches()
        draw_space(screen, drawing_type = "graph")
        draw_poison(screen, white, poison_threshold, drawing_type = "graph")
        draw_actors(screen)
#        conduct_searches(threshold_graph, screen)        
#        if tf > 100 and tf % 2:
        if tf > 50:        
            conduct_searches(threshold_graph, screen)
        manage_events(screen, threshold_graph)
        pygame.display.update()
        if tf % 100 == 0:
            print(1.0/(time.clock() - start), "fps")
        clock.tick(FPS)
        
def manage_events(screen, graph):
    mpos = tuple([math.floor(i /Cell.size) for i in pygame.mouse.get_pos()])
    event_highlight_zone(screen, mpos, graph)
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit
        if event.type == pygame.MOUSEBUTTONDOWN:
            if mpos in Cell.C and pygame.mouse.get_pressed()[2] == 1:
                Cell.C[mpos].in_barrier = True
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE:
                reset_actors() 
                            
def event_highlight_zone(screen, mpos, graph):
    for z in Zone.Z:
        if mpos in Zone.Z[z].cells:
            Zone.Z[z].highlight_zone(screen, drawing_type = "graph")
    if mpos in graph:
        for cell in graph[mpos]:
            Cell.C[cell].highlight_cell(screen, darkolivegreen, drawing_type = "graph")

def create_space(w, h, s):
    for i in range(int(w/s)):
        for j in range(int(h/s)):
            Cell(i, j, s)
#zone_size - how many cells in a zone
def create_zones(w, h, s, top_left = (3, 3), zone_size = 20):
    ID = 0
    #number of equal zones possible in a given space and a given zone size
    number_of_zones = len(range(top_left[0], int(w/s) - zone_size, zone_size))*len(range(top_left[1], int(h/s) - zone_size, zone_size))
    print("Total number of zones: ", number_of_zones)
    for i in range(top_left[0], int(w/s) - zone_size, zone_size):
        for j in range(top_left[1], int(h/s) - zone_size, zone_size):
            zone = Zone(str(ID))
            #i is the x coordinate of the top left cell of the zone, actual visualized zone size is smaller in one
            # unit then zone_size that is why end of range is minus 1. this builds the wall between zones
            for x in range(i, i + zone_size - 1):
                for y in range(j, j + zone_size - 1):
                    #the value of the dictionary is the instance itself! the cell with x,y coordinates that we want
                    Cell.C[(x, y)].in_zone = True
                    #Add zone ID to the cells belonging to zones.
                    Cell.C[(x, y)].zones.add(str(ID))
                    zone.cells[(x, y)] = Cell.C[(x, y)]
            zone.make_walls()
            zone.refine_thresholds()
            zone.make_search_graph()
            print("Created Zone ", str(ID))
            ID += 1
#check for duplicates
    for c in Cell.T:
        Cell.T[c] = list(set(Cell.T[c]))
    
    threshold_graph = defaultdict(list)    
    for t in Cell.T:
        for zone in Cell.T[t]:
            #.thresholds contains lists of cells which are the borders of the th zone
            for th in Zone.Z[zone].thresholds:
                #for each list of cells take only the threshold, meaning cells which are not walls,
                # this is because when we defined .thresholds we did not know if a cell is a wall
                nb = [i for i in th if not Cell.C[i].is_barrier]
                #all the neighbooring threshold cells which are not in the same threshold
                if t not in nb:
                    threshold_graph[t] += nb

    return threshold_graph    

def create_actors(n, threshold):
    count = 0
    zone_ids = list(Zone.Z.keys())
    allcolors = (midnightblue, teal, darkgreen, red, None)
    while count < n:
        Actor(str(count), color = random.choice(allcolors), zone = random.choice(zone_ids), threshold = threshold)
        count += 1

def move_actors(infested_zones):
    clean_zones = list(set([i for i in Zone.Z.keys()]).difference(set(infested_zones)))
    for a in Actor.A:
        x, y = Actor.A[a].x, Actor.A[a].y
        for z in infested_zones:
            if z in Cell.C[x,y].zones:
                Actor.A[a].initialize_in_zone(random.choice(clean_zones))

def reset_actors():
    zones = [i for i in Zone.Z.keys()]
    for a in Actor.A:
        x, y = Actor.A[a].x, Actor.A[a].y
        Actor.A[a].initialize_in_zone(random.choice(zones))


def choose_zones_to_infest(n):
    allzones = [i for i in Zone.Z.keys()]
    zones_to_infest = list()
    count = 0
    while count < n:
        z = random.choice(allzones)
        allzones.remove(z)
        zones_to_infest.append(z)
        count += 1
        
    return zones_to_infest
        
################################################################################
################################################################################
##################### COCKROACH FUNCTIONS ######################################
################################################################################
################################################################################

def make_roaches(n, r, p, c, z = None):
    """Makes n roaches of size (radius) r, poison level p and color c in zone z"""
    count = 0
    while count < n:
        if z is None:
            zone = random.choice(list(Zone.Z.keys()))
            x, y = random.choice(list(Zone.Z[zone].cells.keys()))
            Cockroach(x, y, r, p, c)
            count += 1
        elif z is not None:
            x, y = random.choice(list(Zone.Z[z].cells.keys()))
            Cockroach(x, y, r, p, c)
            count += 1

def move_roaches():
    for r in Cockroach.Roaches:
        r.move_cockroach()


################################################################################
################################################################################
####################SEARCH FUNCTIONS ###########################################
################################################################################
################################################################################

def search(actor_a, actor_b, threshold_graph, screen):
    ax, ay = actor_a.x, actor_a.y
    bx, by = actor_b.x, actor_b.y
    poison_threshold = actor_a.threshold
    if not Cell.C[(ax, ay)].zones == Cell.C[(bx, by)].zones:
        if (ax, ay) not in threshold_graph:
            threshold_graph[(ax,ay)] = [i for i in Zone.Z[list(Cell.C[(ax,ay)].zones)[0]].threshold_cells if not Cell.C[i].is_barrier]
        if (bx, by) not in threshold_graph:
            threshold_graph[(bx,by)] = [i for i in Zone.Z[list(Cell.C[(bx,by)].zones)[0]].threshold_cells if not Cell.C[i].is_barrier]
        S = Search((ax, ay), (bx, by), graph = threshold_graph, threshold = poison_threshold)
        if S.path is not None:
            if len(S.path) > 1:
                S.draw_route(screen, color = verylightgrey)
                s, g = S.path[:2]
                z = get_search_zone(s, g)            
                search_graph = Zone.Z[z].graph
                if s not in search_graph:
                    search_graph[s] = Cell.C[s].neighbours()
                if g not in search_graph:
                    search_graph[g] = Cell.C[s].neighbours()
                s_internal = Search(s, g, graph = search_graph, threshold = poison_threshold)
                if s_internal.path is not None and len(s_internal.path) > 1:
                    s_internal.draw_route(screen, color = midnightblue)
                    actor_a.move(s_internal.path[1])
                    s_internal.path.pop(0)
                elif s_internal.path is None:
                    print("No path found. Waiting for things to improve..")                
        elif S.path is None:
            print("No threshold available. Waiting for things to improve... ")
                
    elif Cell.C[(ax, ay)].zones == Cell.C[(bx, by)].zones:
        z = get_search_zone((ax, ay),(bx, by))
        s, g = (ax, ay), (bx, by)
        search_graph = Zone.Z[z].graph
        if s not in search_graph:
            search_graph[s] = Cell.C[s].neighbours()
        if g not in search_graph:
            search_graph[g] = Cell.C[s].neighbours()
        s_internal = Search(s, g, search_graph, threshold = poison_threshold)
        if s_internal.path is not None and len(s_internal.path) > 1:
            s_internal.draw_route(screen, color = midnightblue)
            actor_a.move(s_internal.path[1])
            s_internal.path.pop(0)
        elif s_internal.path is None:
            print("No path found. Waiting for things to improve..")                
        
 
def get_search_zone(c1, c2):
    C1 = Cell.C[c1].zones
    C2 = Cell.C[c2].zones
    intersection = C1.intersection(C2)
    sz = list(C1.intersection(C2))[0]
    if sz is None:
        print("No search zone found")
    else:        
       return sz
                
def conduct_searches(threshold_graph, screen):
    actors = len(Actor.A)
    """
    search(Actor.A['0'], Actor.A['1'], threshold_graph, screen)
    search(Actor.A['2'], Actor.A['0'], threshold_graph, screen)
    search(Actor.A['1'], Actor.A['3'], threshold_graph, screen)            
    """
    for i in range(0, actors, 2):
        if str(i) in Actor.A.keys() and str(i+1) in Actor.A.keys():
            search(Actor.A[str(i)], Actor.A[str(i+1)], threshold_graph, screen)        

############ DRAWING FUNCTIONS #################################################

def draw_actors(screen):
    for a in Actor.A:
        Actor.A[a].draw_actor(screen)
            
def draw_space(screen, drawing_type = "graph"):
    for c in Cell.C:
        Cell.C[c].draw_cell(screen, drawing_type = drawing_type)

def draw_poison(screen, color, threshold, drawing_type = None):
    for c in Cockroach.Poison:
        if Cockroach.Poison[c] >= threshold:
            Cell.C[c].draw_acceptable(screen, color, drawing_type = drawing_type)


if __name__ == "__main__":
    run()

