from py_supremica import *


## Setup ##
largura = 1
comprimento = 2

heightMap = [[1,1]]

inTiles = [(1,1)]
outTiles = [(1,2)]


## Initialization ##

mod = Module("Sup_1x2")
mod.comment = "First Supervisor Test"

ga = Alphabet()
mod.alphabet = ga

ga.newEvent("getBrick")

for i in inTiles:
    ga.newEvent("in")

for i in outTiles:
    ga.newEvent("out")

mod.addVariable("x","x==0",[0,"C"])
mod.addVariable("y","y==0",[0,"L"])


## Algorithm ##

mod.addConstant("L",largura)
mod.addConstant("C",comprimento)

for i in range(len(heightMap)):
    for j in range(len(heightMap[i])):

        # Set height constants
        constName = "H"+str(i+1)+"."+str(j+1)
        mod.addConstant(constName, heightMap[i][j])

        # Set addTile Events
        ga.newEvent("a"+str(i+1)+"."+str(j+1))
        ga.newEvent("a"+str(i+1)+"."+str(j+1) + "_r2", kind="UNCONTROLLABLE" )



# GR Automaton

gr = Automaton()

gr.addState("OUT",initial=True, accepting=True)
gr.addState("IN")




aut = Automaton()
aut.addState("S0")
aut.addEdge("S0","S0",ga.newEvent("p"))
mod.automata["provisorio"] = aut


mod.toWMOD("gen/Sup_1x2")

