from py_supremica import *

###
# Utility Functions
###
def coordEnc(i,j):

    return(str(i)+""+str(j))

def neighborhood(coord):

    i = coord[0]
    j = coord[1]
    return [(i,j+1),(i-1,j),(i,j-1),(i+1,j)]

def inGrid(coord):

    if coord[0]*coord[1] == 0:
        return False
    elif coord[0] > largura or coord[1] > comprimento:
        return False
    else:
        return True

def neighborhoodIn(coord):
    neigh = []
    for n in neighborhood(coord):
        if (inGrid(n)):
            neigh.append(n)
    return neigh

###
# Setup 
###

# File name
fileName = "gen/Sup_3x3alskjdlakdsj"

# Structure

#heightMap = [[1,1],[1,1]]
#heightMap = [[1,1]]
"""
heightMap = [[0,0,0,0,0,0,0,0,0],
             [0,1,1,1,1,1,1,1,0],
             [0,1,2,2,2,2,2,1,0],
             [0,1,2,3,3,3,2,1,0],
             [0,1,2,3,4,3,2,1,0],
             [0,1,2,3,3,3,2,1,0],
             [0,1,2,2,2,2,2,1,0],
             [0,1,1,1,1,1,1,1,0],
             [0,0,0,0,0,0,0,0,0]]
"""

heightMap = [[1,1,1],
             [1,2,1],
             [1,1,1]]


# In and Out Tiles
inTiles = [(1,1)]
outTiles = [(1,3)]

###
# Initialization 
###

largura = len(heightMap)
comprimento = len(heightMap[0])

mod = Module("sup")
mod.comment = "First Supervisor Test"

ga = Alphabet()
mod.alphabet = ga

ga.newEvent("getBrick")
ga.newEvent("l")
ga.newEvent("r")
ga.newEvent("u")
ga.newEvent("d")

for i in inTiles:
    ga.newEvent("in")

for i in outTiles:
    ga.newEvent("out")

mod.addVariable("x","x==0",[0,comprimento+1])
mod.addVariable("y","y==0",[0,largura+1])

mod.addConstant("L",largura)
mod.addConstant("C",comprimento)

for i in range(1,largura+1):
    for j in range(1,comprimento+1):

        # Set height constants
        constName = "H"+coordEnc(i,j)
        mod.addConstant(constName, heightMap[i-1][j-1])

        # Set addTile Events
        ga.newEvent("a"+coordEnc(i,j))
        ga.newEvent("a"+coordEnc(i,j) + "_r2", kind="CONTROLLABLE")

        # Set height variables
        mod.addVariable("h"+coordEnc(i,j),"h"+coordEnc(i,j)+ "==0", [0,heightMap[i-1][j-1]+1])


###
# Plants
###

# GR Automaton

gr = Automaton()

gr.addState("OUT",initial=True, accepting=True)
gr.addState("IN")

gr.addEdge("OUT","OUT",ga()["getBrick"])
gr.addEdge("OUT","IN",ga()["in"])
gr.setEdgeActions("OUT", "IN", "x=1;y=1")

gr.addEdge("IN","OUT",ga()["out"])
gr.setEdgeGuard("IN", "OUT", "x=="+str(outTiles[0][1])+"& y=="+ str(outTiles[0][0]))
gr.setEdgeActions("IN", "OUT", "x=0;y=0")

gr.addEdge("IN","IN",ga()["l"])
gr.setEdgeGuard("IN","IN","x>1")
gr.setEdgeActions("IN","IN","x-=1")

gr.addTransition("IN","IN",ga()["r"])
gr.setEdgeGuard("IN","IN","x<"+str(comprimento),1)
gr.setEdgeActions("IN","IN","x+=1",1)

gr.addTransition("IN","IN",ga()["d"])
gr.setEdgeGuard("IN","IN","y<"+str(largura),2)
gr.setEdgeActions("IN","IN","y+=1",2)

gr.addTransition("IN","IN",ga()["u"])
gr.setEdgeGuard("IN","IN","y>1",3)
gr.setEdgeActions("IN","IN","y-=1",3)

mod.automata["GR"] = gr


# G_B 

g_b = Automaton()

g_b.addState("S0", initial=True,accepting=True)
g_b.addState("S1",accepting=True)

g_b.addEdge("S0","S1", ga()["getBrick"])
g_b.addEdge("S1","S0", ga()["a11"])

for i in range(1,largura+1):
    for j in range(1,comprimento+1):
        if(not (i == 1 and j  == 1)):
            g_b.addEventToEdge("S1","S0", ga()["a"+coordEnc(i,j)])

            

mod.automata["G_B"] = g_b


# GAdd_iX and GAdd_iX_r2

for i in range(1,largura+1):

    gadd_ix = Automaton()
    gadd_ix.addState("L1", initial=True, accepting=True)

    gadd_ix_r2 = Automaton()
    gadd_ix_r2.addState("L1", initial=True, accepting=True)

    for j in range(1,comprimento+1):

        gadd_ix.addEdge("L1","L1",ga()["a"+coordEnc(i,j)])
        gadd_ix.setEdgeActions("L1","L1","h"+coordEnc(i,j)+"+=1",j-1)

        guard = ""
        for n in neighborhood((i,j)):
            if(inGrid(n)):
                guard += "(x=="+str(n[1])+" & y=="+str(n[0])+")|"

        if ((i,j) in inTiles + outTiles):
            guard += "(x==0 & y==0)"

        gadd_ix.setEdgeGuard("L1","L1",guard,j-1)

        gadd_ix_r2.addEdge("L1","L1",ga()["a"+coordEnc(i,j)+"_r2"])
        gadd_ix_r2.setEdgeActions("L1","L1","h"+coordEnc(i,j)+"+=1",j-1)

    mod.automata["GAdd_"+str(i)+"X"] = gadd_ix
    mod.automata["GAdd_"+str(i)+"X_r2"] = gadd_ix_r2



###
# Specifications
###

# E_Hij, E_aij and E_Uij

for i in range(1,largura+1):

    for j in range(1,comprimento+1):

        # E_Hij
        e_hij = Automaton(kind="SPEC")
        e_hij.addState("B0", initial=True)
        e_hij.addState("B1", accepting=True)

        e_hij.addEdge("B0","B0",ga()["a"+coordEnc(i,j)])
        e_hij.addEventToEdge("B0","B0", ga()["a"+coordEnc(i,j)+"_r2"])
        e_hij.setEdgeGuard("B0","B0","h"+coordEnc(i,j)+"<"+"H"+coordEnc(i,j)+"-1")

        e_hij.addEdge("B0","B1",ga()["a"+coordEnc(i,j)])
        e_hij.addEventToEdge("B0","B1", ga()["a"+coordEnc(i,j)+"_r2"])
        e_hij.setEdgeGuard("B0","B1","h"+coordEnc(i,j)+"=="+"H"+coordEnc(i,j)+"-1")

        mod.automata["E_H"+coordEnc(i,j)] = e_hij

        #E_aij
        e_aij = Automaton(kind="SPEC")
        e_aij.addState("S0", initial=True, accepting=True)
        e_aij.addEdge("S0","S0",ga()["a"+coordEnc(i,j)])
        e_aij.addEventToEdge("S0","S0",ga()["a"+coordEnc(i,j)+"_r2"])

        guard = ""
        for n in neighborhood((i,j)):
            if(inGrid(n)):
                guard += "(x=="+str(n[1])+" & y=="+str(n[0])+") & (h"+coordEnc(i,j)+"==h"+coordEnc(n[0],n[1])+")|"

        if ((i,j) in inTiles + outTiles):
            guard += "(x==0 & y==0) & (h"+coordEnc(i,j)+"==0)|"

        e_aij.setEdgeGuard("S0","S0",guard)

        mod.automata["E_a"+coordEnc(i,j)] = e_aij

        #E_Uij

        n_i = (i-1,j) in neighborhoodIn((i,j)) and (i+1,j) in neighborhoodIn((i,j))
        n_j = (i,j-1) in neighborhoodIn((i,j)) and (i,j+1) in neighborhoodIn((i,j))

        if( n_i or n_j):
            e_uij = Automaton(kind="SPEC")
            e_uij.addState("S0",initial=True, accepting=True)
            e_uij.addEdge("S0","S0",ga()["a"+coordEnc(i,j)])
            e_uij.addEventToEdge("S0","S0",ga()["a"+coordEnc(i,j)+"_r2"])
            guard = ""
            if(n_i):
                guard += "(h"+coordEnc(i,j)+" >= h"+coordEnc(i-1,j)+"  |  h"+coordEnc(i,j)+" >= h"+coordEnc(i+1,j)+")&"
            if(n_j):
                guard += "(h"+coordEnc(i,j)+" >= h"+coordEnc(i,j-1)+"  |  h"+coordEnc(i,j)+" >= h"+coordEnc(i,j+1)+")"
            e_uij.setEdgeGuard("S0","S0",guard)

            mod.automata["E_U"+coordEnc(i,j)] = e_uij



# E_M


e_m = Automaton(kind="SPEC")
e_m.addState("S0",initial = True, accepting =True)

e_m.addEdge("S0","S0",ga()["r"])
e_m.addEdge("S0","S0",ga()["u"])
e_m.addEdge("S0","S0",ga()["l"])
e_m.addEdge("S0","S0",ga()["d"])

l_guard = ""
u_guard = ""
r_guard = ""
d_guard = ""

for i in range(1,largura+1):
    for j in range(1,comprimento+1):

        if(j>1):
            l_guard+= "(x=="+str(j)+" & y=="+str(i)+") & ((-1 <= h"+coordEnc(i,j)+"-h"+coordEnc(i,j-1)+")&(h"+coordEnc(i,j)+"-h"+coordEnc(i,j-1)+" <= 1))|"
        if(i>1):
            u_guard+= "(x=="+str(j)+" & y=="+str(i)+") & ((-1 <= h"+coordEnc(i,j)+"-h"+coordEnc(i-1,j)+")&(h"+coordEnc(i,j)+"-h"+coordEnc(i-1,j)+" <= 1))|"
        if(j<comprimento):
            r_guard+= "(x=="+str(j)+" & y=="+str(i)+") & ((-1 <= h"+coordEnc(i,j)+"-h"+coordEnc(i,j+1)+")&(h"+coordEnc(i,j)+"-h"+coordEnc(i,j+1)+" <= 1))|"
        if(i<largura):
            d_guard+= "(x=="+str(j)+" & y=="+str(i)+") & ((-1 <= h"+coordEnc(i,j)+"-h"+coordEnc(i+1,j)+")&(h"+coordEnc(i,j)+"-h"+coordEnc(i+1,j)+" <= 1))|"

if(comprimento>1):
    e_m.setEdgeGuard("S0","S0",r_guard,0)
    e_m.setEdgeGuard("S0","S0",l_guard,2)
if(largura>1):
    e_m.setEdgeGuard("S0","S0",u_guard,1)
    e_m.setEdgeGuard("S0","S0",d_guard,3)

mod.automata["E_M"] = e_m

#  Generate
mod.toWMOD(fileName)



