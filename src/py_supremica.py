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

    def __init__(self):
        self.states = []
        self.edges = {}
        self.alphabet = set()

    def addState(self, name, **kwargs):
        s = self.State(name, **kwargs)
        self.states.append(s)
        return s

    def addEdge(self,source,target,event):


        if source in self.edges.keys():
            if target in self.edges[source].keys():
                print("Edge from {} to {} already created".format(source,target))
                return 

            else:
                edge = {}
                edge["label"] = [event]
                self.edges[source][target] = edge

        else:
            targetDict = {}
            edge = {}

            edge["label"] = [event]
            targetDict[target] = edge
            self.edges[source] = targetDict

        self.alphabet.add(event)

    def addEventToEdge(self,source,target,event):
        self.edges[source][target]["label"].append(event)

    def setEdgeGuard(self,source,target,guard):
        self.edges[source][target]["guard"] = guard
    
    def setEdgeActions(self,source,target, actions):
        self.edges[source][target]["actions"] = actions


    class State:

        def __init__(self, name, **kwargs):
            
            self.name = name
            self.initial = kwargs.get("initial",False)
            self.accepting = kwargs.get("accepting",False)


class Alphabet:


    def __init__(self):
        self.alphabet = set()
    
    def newEvent(self,name, kind="CONTROLLABLE", observable=True):
        e = self.Event(name, kind, observable)
        self.alphabet.add(e)
        return e

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
        for event in self.alphabet():
            eventDecl = ET.SubElement(eventDeclList,"EventDecl")
            eventDecl.set("Kind", event.kind)
            eventDecl.set("Name", event.name)


        # Add components
        componentList = ET.SubElement(root,"ComponentList")
        for aut in self.automata:
            simpleComponent = ET.SubElement(componentList,"SimpleComponent")
            simpleComponent.set("Name",aut)
            simpleComponent.set("Kind","PLANT")
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
                    edge = ET.SubElement(edgeList,"Edge")
                    edge.set("Source", source)
                    edge.set("Target", target)

                    labelBlock = ET.SubElement(edge,"LabelBlock")
                    for label in automaton.edges[source][target]["label"]:
                        eventLabel = ET.SubElement(labelBlock,"SimpleIdentifier")
                        eventLabel.set("Name",label.name)


                    has_guard = "guard" in automaton.edges[source][target].keys()
                    has_actions = "actions" in automaton.edges[source][target].keys()
                    if (has_actions or has_guard):
                        guardActionBlock = ET.SubElement(edge,"GuardActionBlock")
                        
                        if(has_guard):
                            guards = ET.SubElement(guardActionBlock,"Guards")
                            guards.append(GuardExpression(automaton.edges[source][target]["guard"]))
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
        tree = parse_expression(exp)
    else:
        tree = exp
    

    binExp = ET.Element("BinaryExpression")
    binExp.set("Operator",tree[1])

    if(isinstance(tree[0],type(tree)) or isinstance(tree[2],type(tree))):
        

        binExp.append(GuardExpression(tree[0]))
        binExp.append(GuardExpression(tree[2]))


    else:

        buildBinExpLeaf(tree,binExp)
        

    return binExp

