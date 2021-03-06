from py_supremica import *

###
# Utility Functions
###

def coordEnc(i,j):
    return(str(i)+""+str(j))

def ePlacingStr(i,j):
    placingEnc = "a"
    return placingEnc+coordEnc(i,j)

def vHeightStr(i,j):
    heightEnc = "h"
    return heightEnc + coordEnc(i,j)

def eAltStr():
    return "_r2"

def inGrid(coord):

    if coord[0]*coord[1] == 0:
        return False
    elif coord[0] > M or coord[1] > N:
        return False
    else:
        return True

def neighborhood(coord):

    i = coord[0]
    j = coord[1]
    neighborhood = [(i,j+1),(i-1,j),(i,j-1),(i+1,j)]

    neigh = []
    for n in neighborhood:
        if (inGrid(n)):
            neigh.append(n)
    return neigh

###
# Setup
###

fileName = "gen/AddingG5"
moduleComment = "This is an autogenerated supervisor"

heightMap = [[1,1],[1,1]]

inTiles = [(1,1),(1,2),(2,1),(2,2)]
outTiles = [(1,1),(1,2),(2,1),(2,2)]

###
# Initialization
##

# HeightMap shape
M = len(heightMap)
N = len(heightMap[0])

# Init Module and add comment
mod = Module("Supervisor")
mod.comment = moduleComment

# Init alphabet
ga = Alphabet()
mod.alphabet = ga

# Define base events
ga.newEvent("getBrick")
ga.newEvent("l")
ga.newEvent("r")
ga.newEvent("u")
ga.newEvent("d")

for (i,j) in inTiles:
    ga.newEvent("in"+coordEnc(i,j))

for (i,j) in inTiles:
    ga.newEvent("out"+coordEnc(i,j))

# Position variables 
mod.addVariable("x","x==0",[0,N+1])
mod.addVariable("y","y==0",[0,M+1])

# heightmap shape constants (#observe)
mod.addConstant("M",M)
mod.addConstant("N",N)

# Initialize height variables, height constants and placing events

for i in range(1,M+1):
    for j in range(1,N+1):

        # Check if there is need for creation
        if(heightMap[i-1][j-1]>0):

            # Set height constants (#observe)
            constName = "H"+coordEnc(i,j)
            mod.addConstant(constName, heightMap[i-1][j-1])

            # Set addTile Events
            ga.newEvent(ePlacingStr(i,j))
            ga.newEvent(ePlacingStr(i,j) + eAltStr(), kind="CONTROLLABLE")

            # Set height variables
            mod.addVariable(vHeightStr(i,j),
                            vHeightStr(i,j) + "==0",
                            [0,heightMap[i-1][j-1]+1])


###
# Single Automata
###

### GR Automaton or G1 ###

gr = Automaton()

# Create states
gr.addState("OUT",initial=True, accepting=True)
gr.addState("IN")

# Add getBrick event
gr.addEdge("OUT","OUT",ga()["getBrick"])

# Add enter grid events
gr.addEdge("OUT","IN",ga()["in"+coordEnc(inTiles[0][0],inTiles[0][1])])
gr.setEdgeActions("OUT", "IN", "x="+str(inTiles[0][1])+";y="+str(inTiles[0][0]))
for i in range(len(inTiles)):
    if(i != 0):
        gr.addTransition("OUT","IN",ga()["in"+coordEnc(inTiles[i][0],inTiles[i][1])])
        gr.setEdgeActions("OUT", "IN", "x="+str(inTiles[i][1])+";y="+str(inTiles[i][0]),i)

# Add exit grid events
gr.addEdge("IN","OUT",ga()["out"+coordEnc(outTiles[0][0],outTiles[0][1])])
gr.setEdgeGuard("IN", "OUT", "x=="+str(outTiles[0][1])+"& y=="+ str(outTiles[0][0]))
gr.setEdgeActions("IN", "OUT", "x=0;y=0")
for i in range(len(outTiles)):
    if(i != 0):
        gr.addTransition("IN","OUT",ga()["out"+coordEnc(outTiles[i][0],outTiles[i][1])])
        gr.setEdgeGuard("IN", "OUT", "x=="+str(outTiles[i][1])+"& y=="+ str(outTiles[i][0]),i)
        gr.setEdgeActions("IN", "OUT", "x=0;y=0",i)


# Add movement in grid events
gr.addEdge("IN","IN",ga()["l"])
gr.setEdgeGuard("IN","IN","x>1")
gr.setEdgeActions("IN","IN","x-=1")

gr.addTransition("IN","IN",ga()["r"])
gr.setEdgeGuard("IN","IN","x<"+str(N),1)
gr.setEdgeActions("IN","IN","x+=1",1)

gr.addTransition("IN","IN",ga()["d"])
gr.setEdgeGuard("IN","IN","y<"+str(M),2)
gr.setEdgeActions("IN","IN","y+=1",2)

gr.addTransition("IN","IN",ga()["u"])
gr.setEdgeGuard("IN","IN","y>1",3)
gr.setEdgeActions("IN","IN","y-=1",3)

mod.automata["GR"] = gr

### GB Automaton or G2 ###

g_b = Automaton()

# Create states
g_b.addState("S0", initial=True,accepting=True)
g_b.addState("S1",accepting=True)

g_b.addEdge("S0","S1", ga()["getBrick"])

g_b.addEdge("S1","S0", ga()[ePlacingStr(1,1)])
for i in range(1,M+1):
    for j in range(1,N+1):
        if(not (i == 1 and j  == 1)):
            g_b.addEventToEdge("S1","S0", ga()[ePlacingStr(i,j)])


mod.automata["G_B"] = g_b

### E_M Automaton or G4 ##

e_m = Automaton(kind="SPEC")
e_m.addState("S0",initial = True, accepting =True)

l_guard = ""
u_guard = ""
r_guard = ""
d_guard = ""

for i in range(1,M+1):
    for j in range(1,N+1):

        if(j>1):
            l_guard+= "(x=="+str(j)+" & y=="+str(i)+") & ((-1 <= "+vHeightStr(i,j)+"-"+vHeightStr(i,j-1)+")&("+vHeightStr(i,j)+"-"+vHeightStr(i,j-1)+" <= 1))|"
        if(i>1):
            u_guard+= "(x=="+str(j)+" & y=="+str(i)+") & ((-1 <= "+vHeightStr(i,j)+"-"+vHeightStr(i-1,j)+")&("+vHeightStr(i,j)+"-"+vHeightStr(i-1,j)+" <= 1))|"
        if(j<N):
            r_guard+= "(x=="+str(j)+" & y=="+str(i)+") & ((-1 <= "+vHeightStr(i,j)+"-"+vHeightStr(i,j+1)+")&("+vHeightStr(i,j)+"-"+vHeightStr(i,j+1)+" <= 1))|"
        if(i<M):
            d_guard+= "(x=="+str(j)+" & y=="+str(i)+") & ((-1 <= "+vHeightStr(i,j)+"-"+vHeightStr(i+1,j)+")&("+vHeightStr(i,j)+"-"+vHeightStr(i+1,j)+" <= 1))|"

if(N>1):
    e_m.addEdge("S0","S0",ga()["r"])
    e_m.addEdge("S0","S0",ga()["l"])

    e_m.setEdgeGuard("S0","S0",r_guard,0)
    e_m.setEdgeGuard("S0","S0",l_guard,1)
if(M>1):
    fix = 2 if N>1 else 0
    e_m.addEdge("S0","S0",ga()["u"])
    e_m.addEdge("S0","S0",ga()["d"])

    e_m.setEdgeGuard("S0","S0",u_guard,0+fix)
    e_m.setEdgeGuard("S0","S0",d_guard,1+fix)

mod.automata["E_M"] = e_m

### G5 ###

G5 = Automaton(kind="SPEC")
G5.addState("S0",initial = True, accepting =True)

for i in range(len(inTiles+outTiles)):

    if i < len(inTiles):
        y = inTiles[i][0]
        x = inTiles[i][1]
        e_type = "in"
    else:
        y = outTiles[i-len(inTiles)][0]
        x = outTiles[i-len(inTiles)][1]
        e_type = "out"

    step_guard = vHeightStr(y,x) +"<= 1"
    G5.addEdge("S0", "S0", ga()[e_type+coordEnc(y, x)])
    G5.setEdgeGuard("S0", "S0", step_guard,i)


mod.automata["G5"] = G5

###
# Variable Automata
###

for i in range(1,M+1):

    ### Gadd_ix Automaton or G3 ###
    gadd_ix = Automaton()
    gadd_ix.addState("L1", initial=True, accepting=True)

    ### Gadd_ix Automaton (for external events) or G3 ###
    gadd_ix_r2 = Automaton()
    gadd_ix_r2.addState("L1", initial=True, accepting=True)

    for j in range(1,N+1):

        ### Populate G3's ###
        gadd_ix.addEdge("L1","L1",ga()[ePlacingStr(i,j)])
        gadd_ix.setEdgeActions("L1","L1",vHeightStr(i,j)+"+=1",j-1)

        guard = ""
        for n in neighborhood((i,j)):
            guard += "(x=="+str(n[1])+" & y=="+str(n[0])+")|"

        if ((i,j) in inTiles + outTiles):
            guard += "(x==0 & y==0)"

        gadd_ix.setEdgeGuard("L1","L1",guard,j-1)

        gadd_ix_r2.addEdge("L1","L1",ga()[ePlacingStr(i,j)+eAltStr()])
        gadd_ix_r2.setEdgeActions("L1","L1",vHeightStr(i,j)+"+=1",j-1)

        ### E_aij Automaton or G6 ###
        e_aij = Automaton(kind="SPEC")
        e_aij.addState("S0", initial=True, accepting=True)
        e_aij.addEdge("S0","S0",ga()[ePlacingStr(i,j)])
        e_aij.addEventToEdge("S0","S0",ga()[ePlacingStr(i,j)+"_r2"])

        guard = ""
        for n in neighborhood((i,j)):
            guard += "(x=="+str(n[1])+" & y=="+str(n[0])+") & (h"+coordEnc(i,j)+"==h"+coordEnc(n[0],n[1])+")|"

        if ((i,j) in inTiles + outTiles):
            guard += "(x==0 & y==0) & (h"+coordEnc(i,j)+"==0)|"

        e_aij.setEdgeGuard("S0","S0",guard)

        mod.automata["E_a"+coordEnc(i,j)] = e_aij


        ### E_Uij Automaton or G7 ###
        n_i = (i-1,j) in neighborhood((i,j)) and (i+1,j) in neighborhood((i,j))
        n_j = (i,j-1) in neighborhood((i,j)) and (i,j+1) in neighborhood((i,j))

        if( n_i or n_j):
            e_uij = Automaton(kind="SPEC")
            e_uij.addState("S0",initial=True, accepting=True)
            e_uij.addEdge("S0","S0",ga()[ePlacingStr(i,j)])
            e_uij.addEventToEdge("S0","S0",ga()[ePlacingStr(i,j)+"_r2"])
            guard = ""
            if(n_i):
                guard += "(h"+coordEnc(i,j)+" >= h"+coordEnc(i-1,j)+"  |  h"+coordEnc(i,j)+" >= h"+coordEnc(i+1,j)+")&"
            if(n_j):
                guard += "(h"+coordEnc(i,j)+" >= h"+coordEnc(i,j-1)+"  |  h"+coordEnc(i,j)+" >= h"+coordEnc(i,j+1)+")"
            e_uij.setEdgeGuard("S0","S0",guard)

            mod.automata["E_U"+coordEnc(i,j)] = e_uij

        ### E_Hij Automaton or G8 ###
        e_hij = Automaton(kind="SPEC")
        e_hij.addState("B0", initial=True)
        e_hij.addState("B1", accepting=True)

        e_hij.addEdge("B0","B0",ga()[ePlacingStr(i,j)])
        e_hij.addEventToEdge("B0","B0", ga()[ePlacingStr(i,j)+"_r2"])
        e_hij.setEdgeGuard("B0","B0",vHeightStr(i,j)+"<"+"H"+coordEnc(i,j)+"-1")

        e_hij.addEdge("B0","B1",ga()[ePlacingStr(i,j)])
        e_hij.addEventToEdge("B0","B1", ga()[ePlacingStr(i,j)+"_r2"])
        e_hij.setEdgeGuard("B0","B1",vHeightStr(i,j)+"=="+"H"+coordEnc(i,j)+"-1")

        mod.automata["E_H"+coordEnc(i,j)] = e_hij

    ### Finish G3's ###
    mod.automata["GAdd_"+str(i)+"X"] = gadd_ix
    mod.automata["GAdd_"+str(i)+"X"+eAltStr()] = gadd_ix_r2


#  Generate
mod.toWMOD(fileName)

