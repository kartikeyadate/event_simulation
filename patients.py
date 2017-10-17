
import sys
import math
import random
from collections import defaultdict


#INPUT (from YY, YK)

nt = [20,22,22,25,25,25,25,25,28,28,30] #the time required to treat new patients
ft = [10,12,12,15,15,15,15,15,18,18,20] #the time required to treat existing patients
d = 10 #number of doctors
total = 480 #total number of minutes in the day
interval = [0,0,1,1,1,2,2,2,2,2,10,10] #Intervals at which patients arrive (either new or returning)
visitors = [0,0,0,0,1,1,1,2,2,3] #Number of visitors accompanying each patient.


#CALCULATION
def process(start, typ="new"):
    if typ == "new":
        dur = random.choice(nt)
    elif typ == "ret":
        dur = random.choice(ft)
    return start + dur

def simulate():
    t = 0
    tn = defaultdict(int)
    tf = defaultdict(int)
    v = defaultdict(int)

    pc = 0
    while t <= 480 - max(nt):
        typ = random.choice(["new", "ret"]) #pick a type of patient to add
        vis = random.choice(visitors) #pick the number of visitors accompanying the patient
        end = process(t,typ=typ) #get the treatment type

        #update the population of each type (new patient, returning patient, visitor) for the duration patient's treatment
        for i in range(t,end+1):
            v[i] += vis
            if typ == "new":
                tn[i] += 1

            elif typ == "ret":
                tf[i] += 1

        #find the time for the next patient to be added.
        nex = random.choice(interval)
        t += nex
        pc += 1

    return tn, tf, v, pc

def run(n=10000):
    Pn, Pf = defaultdict(int), defaultdict(int)
    V = defaultdict(int)
    count = 0
    PC = 0
    while count < n:
        tn, tf, vis, pc = simulate()
        i = set(tn.keys() + tf.keys())
        for x in i:
            Pn[x] += tn[x]
            Pf[x] += tf[x]
            V[x] += vis[x]

        PC += pc

        count+=1
        if count % 100 == 0:
            print(count)

    t = sorted(list(set(Pn.keys() + Pf.keys())))

    for x in t:
        print(x, round(Pn[x]/(0.1*n),1), round(Pf[x]/(0.1*n),1), round(V[x]/(0.1*n),1))

    print("Total patients processed:", int(round(1.0*PC/n,0)))



if __name__ == "__main__":
    run()










