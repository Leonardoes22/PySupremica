# Basic scripting testground

import xml.etree.ElementTree as ET
from xml.dom import minidom
from supremica_classes import *
from automata import *


s1 = State("S1",initial=True)
s2 = State("S2",accepting=True)

t1 = Transition("S1","S2","a")
t2 = Transition("S2","S2","b")
t3 = Transition("S2","S1","a")

aut = Automaton([s1,s2],[t1,t2,t3])

comp = Component("Nome","PLANT")
comp.Build(aut)


mod = Module()
mod.append(ComponentList(comp))
mod.toWMOD("gen/SecondAutomataTest")



