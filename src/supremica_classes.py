import xml.etree.ElementTree as ET
from xml.dom import minidom


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

    def toXML(self):

        c = ET.Element("SimpleComponent")
        c.set("Name", self.name)
        c.set("Kind", self.kind)

        graph = ET.SubElement(c,"Graph")

        nodeList = ET.SubElement(graph,"NodeList")
        node = ET.SubElement(nodeList,"SimpleNode")
        node.set("Name","s0")
        node.set("Initial", "true")

        edgeList = ET.SubElement(graph,"EdgeList")
        edge = ET.SubElement(edgeList,"Edge")
        edge.set("Source", "s0")
        edge.set("Target", "s0")

        label = ET.SubElement(edge,"LabelBlock")
        iden = ET.SubElement(label,"SimpleIdentifier")
        iden.set("Name","event0")

        return c

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