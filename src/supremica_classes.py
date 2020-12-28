"""
Temporary module containing Supremica's WMOD data structures interactions

Includes the following classes:
    Event
    EventList
    Component
    ComponentList
    Module
"""

import xml.etree.ElementTree as ET
from xml.dom import minidom
from automata import *


class Event:

    def __init__(self, name, kind):
        self.name = name
        self.kind = kind

    def toXML(self):

        e = ET.Element("EventDecl")
        e.set("Name", self.name)
        e.set("Kind", self.kind)

        return e

class EventList:

    def __init__(self, *events):
        self.events = events

    def toXML(self):

        elist = ET.Element("EventDeclList")
        for e in self.events:
            elist.append(e.toXML())

        return elist

class Component:
    def __init__(self, name, kind):
        self.name = name
        self.kind = kind

        self.root = ET.Element("SimpleComponent")
        self.root.set("Name", self.name)
        self.root.set("Kind", self.kind)

    def toXML(self):

        
        return self.root

    def Build(self, automaton):

        graph = ET.SubElement(self.root,"Graph")

        nodeList = ET.SubElement(graph,"NodeList")
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

                for label in automaton.edges[source][target]:
                    labelBlock = ET.SubElement(edge,"LabelBlock")
                    eventLabel = ET.SubElement(labelBlock,"SimpleIdentifier")
                    eventLabel.set("Name",label)

class ComponentList:
    def __init__(self, *components):
        self.components = components

    def toXML(self):

        clist = ET.Element("ComponentList")
        for c in self.components:
            clist.append(c.toXML())

        return clist

class Module:

    def __init__(self):
        self.root = ET.Element("Module")
        self.root.set("xmlns","http://waters.sourceforge.net/xsd/module")
        self.root.set("xmlns:B","http://waters.sourceforge.net/xsd/base")
        self.root.set("Name","SupremicaModuleName")

    def toWMOD(self, fileName):

        rough = ET.tostring(self.root, encoding="windows-1252").decode("windows-1252")
        reparsed = minidom.parseString(rough).toprettyxml(indent="  ")

        with open(fileName+".wmod","w") as f:
            f.write(reparsed)

    def append(self,element):
        
        self.root.append(element.toXML())