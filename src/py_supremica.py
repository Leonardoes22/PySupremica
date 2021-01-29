"""
Basic module 

Includes the following classes:
    Automaton
        State
    Alphabet
        Event
    Module

"""

import xml.etree.ElementTree as ET
from xml.dom import minidom
from parsing_algorithm import *

class Automaton:

    def __init__(self,kind="PLANT"):
        self.states = []
        self.edges = {}
        self.alphabet = set()
        self.kind = kind

    def addState(self, name, **kwargs):
        s = self.State(name, **kwargs)
        self.states.append(s)
        return s

    def addEdge(self,source,target,event):

        if source in self.edges.keys():
            if target in self.edges[source].keys():
                print("Edge from {} to {} already created, adding transition.".format(source,target))
                self.addTransition(source,target,event) 

            else:
                
                self.edges[source][target] = [self.Transition(source,target,event)]

        else:
            targetDict = {}
            
            targetDict[target] = [self.Transition(source,target,event)]
            self.edges[source] = targetDict

        self.alphabet.add(event)

    def addTransition(self, source, target, event):
        self.edges[source][target].append(self.Transition(source,target,event))

    def addEventToEdge(self,source,target,event, index=0):
        self.edges[source][target][index].addEvent(event)

    def setEdgeGuard(self,source,target,guard, index=0):
        self.edges[source][target][index].setGuard(guard)
    
    def setEdgeActions(self,source,target, actions, index=0):
        self.edges[source][target][index].setActions(actions)


    class State:

        def __init__(self, name, **kwargs):
            
            self.name = name
            self.initial = kwargs.get("initial",False)
            self.accepting = kwargs.get("accepting",False)


    class Transition:

        def __init__(self, source, target, event):

            self.source = source
            self.target = target
            self.events = {event.name: event}
            self.guard = None
            self.actions = None

        def setGuard(self, guard):
            self.guard = guard

        def setActions(self, actions):
            self.actions = actions

        def addEvent(self, event):
            
            if event.name not in self.events:
                self.events[event.name] = event
            else:
                print("There is already an event named {}, please modify it or choose another name.".format(event.name))


class Alphabet:


    def __init__(self):
        self.alphabet = dict()
    
    def newEvent(self,name, kind="CONTROLLABLE", observable=True):
        if(name not in self.alphabet.keys()):
            e = self.Event(name, kind, observable)
            self.alphabet[name] = e
            return e
        else:
            print("An event named {} was already created, please edit it or choose another name.".format(name))
        

    def __call__(self):
        return self.alphabet

    class Event:

        def __init__(self, name, kind="CONTROLLABLE", observable=True):

            self.name = name
            self.kind = kind
            self.observable = observable

        def __repr__(self):
            return "Event("+self.name+")"


class Module:

    def __init__(self, name="New PySupremica Module"):

        self.alphabet = Alphabet()
        self.constants = {}
        self.variables = {}
        self.automata = {}
        self.comment = ""


    def addConstant(self, constName, constValue):

        if (not constName in self.constants.keys()):
            self.constants[constName] = constValue
        else:
            print("Could not create {}.A constant with this name already exists".format(constName))

    def addVariable(self, varName, initial, interval):
        if (not varName in self.variables.keys()):
            var = {"initial": initial, "range": interval }
            self.variables[varName] = var
        else:
            print("Could not create {}. A variable with this name already exists".format(varName))

    def toWMOD(self, fileName):

        # Initialize
        root = ET.Element("Module")
        root.set("xmlns","http://waters.sourceforge.net/xsd/module")
        root.set("xmlns:B","http://waters.sourceforge.net/xsd/base")
        root.set("Name","SupremicaModuleName")

        # Add comment
        comment = ET.SubElement(root,"B:Comment")
        comment.text = self.comment

        # Add constants
        if(self.constants):
            constantAliasList = ET.SubElement(root,"ConstantAliasList") 
        for const in self.constants:
            constantAlias = ET.SubElement(constantAliasList,"ConstantAlias")
            constantAlias.set("Name", const)
            constantAliasExpression = ET.SubElement(constantAlias,"ConstantAliasExpression")
            intConstant = ET.SubElement(constantAliasExpression,"IntConstant")
            intConstant.set("Value",self.constants[const].__str__())

        # Add alphabet
        eventDeclList = ET.SubElement(root,"EventDeclList")
        self.alphabet.newEvent(":accepting","PROPOSITION")
        for eventKey in self.alphabet():
            event = self.alphabet()[eventKey]
            eventDecl = ET.SubElement(eventDeclList,"EventDecl")
            eventDecl.set("Kind", event.kind)
            eventDecl.set("Name", event.name)


        # Add components
        componentList = ET.SubElement(root,"ComponentList")
        for aut in self.automata:
            simpleComponent = ET.SubElement(componentList,"SimpleComponent")
            simpleComponent.set("Name",aut)
            simpleComponent.set("Kind", self.automata[aut].kind)
            graph = ET.SubElement(simpleComponent,"Graph")

            nodeList = ET.SubElement(graph,"NodeList")

            automaton = self.automata[aut]

            for state in automaton.states:
                node = ET.SubElement(nodeList,"SimpleNode")
                node.set("Name",state.name)
                if(state.initial):
                    node.set("Initial", "true")
                if(state.accepting):
                    eventList = ET.SubElement(node,"EventList")
                    identifier = ET.SubElement(eventList,"SimpleIdentifier")
                    identifier.set("Name",":accepting")

            
            edgeList = ET.SubElement(graph,"EdgeList")
            for source in automaton.edges.keys():
                for target in automaton.edges[source].keys():
                    for transition in automaton.edges[source][target]:
                        edge = ET.SubElement(edgeList,"Edge")
                        edge.set("Source", source)
                        edge.set("Target", target)

                        labelBlock = ET.SubElement(edge,"LabelBlock")
                        for label in transition.events:
                            eventLabel = ET.SubElement(labelBlock,"SimpleIdentifier")
                            eventLabel.set("Name",label)


                        has_guard = transition.guard is not None
                        has_actions = transition.actions  is not None
                        if (has_actions or has_guard):
                            guardActionBlock = ET.SubElement(edge,"GuardActionBlock")
                            
                            if(has_guard):
                                guards = ET.SubElement(guardActionBlock,"Guards")
                                guards.append(GuardExpression(transition.guard))
                            if(has_actions):
                                actions = ET.SubElement(guardActionBlock,"Actions")
                                pass
                    

        # Add variables
        for var in self.variables:
            variable = self.variables[var]
            variableComponent = ET.SubElement(componentList,"VariableComponent")
            variableComponent.set("Name",var)

            interval = ET.SubElement(variableComponent,"VariableRange")
            binExp = ET.SubElement(interval,"BinaryExpression")
            binExp.set("Operator","..")
            for i in range(2):

                if(isinstance(variable["range"][i],int)):
                    operand = ET.SubElement(binExp, "IntConstant")
                    operand.set("Value",str(variable["range"][i]))
                else:
                    operand = ET.SubElement(binExp, "SimpleIdentifier")
                    operand.set("Name",variable["range"][i])
                
            initial = ET.SubElement(variableComponent,"VariableInitial")
            initial.append(GuardExpression(variable["initial"]))


        # Export to File
        rough = ET.tostring(root, encoding="windows-1252").decode("windows-1252")
        reparsed = minidom.parseString(rough).toprettyxml(indent="  ")

        with open(fileName+".wmod","w") as f:
            f.write(reparsed)






def buildBinExpLeaf(parentTree, parentBinExp):
    for i in range(3):
            if(i!=1 ):
                if(isInt(parentTree[i])):
                    operand = ET.SubElement(parentBinExp, "IntConstant")
                    operand.set("Value",str(parentTree[i]))
                else:
                    operand = ET.SubElement(parentBinExp, "SimpleIdentifier")
                    operand.set("Name",parentTree[i])

def GuardExpression(exp):
    
    if(isinstance(exp,str)):
        tree = parse_guard(exp)
    else:
        tree = exp
    

    binExp = ET.Element("BinaryExpression")
    binExp.set("Operator",tree[1])

    print("ARve:",tree)
    if(isinstance(tree[0],type(tree)) or isinstance(tree[2],type(tree))):
        
        binExp.append(GuardExpression(tree[0]))
        binExp.append(GuardExpression(tree[2]))


    else:

        buildBinExpLeaf(tree,binExp)
        

    return binExp

