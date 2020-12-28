"""
Basic module for handling finite automata

Includes the following classes:
    Automaton
    State
    Transition
    Event
    Variable
    BinaryExpression
"""

class Automaton:

    def __init__(self, states, transitions):
        self.states = states
        self.transitions = transitions

        # Edges data structure works better while constructing the WMOD file than the default transitions
        # This is currently a temporary construction
        self.edges = {}
        for transition in transitions:
            if transition.source in self.edges.keys():
                if transition.target in self.edges[transition.source].keys():
                    self.edges[transition.source][transition.target]["label"].append(transition.label)

                else:
                    edge = {}
                    edge["label"] = [transition.label]
                    self.edges[transition.source][transition.target] = edge

            else:
                targetDict = {}
                edge = {}
                edge["label"] = [transition.label]

                targetDict[transition.target] = edge
                self.edges[transition.source] = targetDict

class ExtendedAutomaton(Automaton):

    def __init__(self, states, transitions):
        Automaton.__init__(self, states, transitions)

    def addGuard(self, source, target, guard):
        if(target in self.edges[source].keys()):
            self.edges[source][target]["guard"] = guard
        else:
            print("No edge from {} to {} was found".format(source,target))

    def addAction(self, source, target, action):
        if(target in self.edges[source].keys()):
            self.edges[source][target]["action"] = action
        else:
            print("No edge from {} to {} was found".format(source,target))



class State:

    def __init__(self, name, **kwargs):
        
        self.name = name
        self.initial = kwargs.get("initial",False)
        self.accepting = kwargs.get("accepting",False)


class Transition:

    def __init__(self, source, target, label):

        self.source = source
        self.target = target
        self.label = label


class Event:

    def __init__(self, name, kind="CONTROLLABLE", observable=True):

        self.name = name
        self.kind = Kind
        self.observable = observable



class Variable:

    def __init__(self, name, varRange, initial):

        self.name = name
        self.varRange = varRange
        self.initial = initial

class BinaryExpression:

    def __init__(self):

        self.name = "s"





s1 = State("S1",initial=True)
s2 = State("S1",accepting=True)

t1 = Transition("S1","S2","a")
t2 = Transition("S2","S2","b")
t3 = Transition("S2","S1","a")

aut = ExtendedAutomaton([s1,s2],[t1,t2,t3])

aut.addAction("S1","S2",BinaryExpression())
aut.addGuard("S1","S1",BinaryExpression())
print(aut.edges["S1"]["S2"]["action"])








