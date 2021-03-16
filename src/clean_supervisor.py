import xml.etree.ElementTree as ET
import re
import tkinter as tk
from tkinter import filedialog
from xml.dom import minidom

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


# Select File
root = tk.Tk()
root.withdraw()

#root.call('wm', 'attributes', '.', '-topmost', True)
file_path = filedialog.askopenfilename()
#%gui tk
filename = file_path.split('/')[-1].replace('.xml','')
filefolder = "\\".join(file_path.split('/')[:-1])

root = ET.parse(file_path).getroot()
automaton = list(root)[0]
events = list(automaton)[0]
states = list(automaton)[1]
transitions = list(automaton)[2]


###
# Fix state labels and supervisor name
###

sup_name = automaton.attrib["name"]
sup_name = sup_name.replace("sup(","")
sup_name = sup_name.replace(")","")

tag_list = sup_name.split('||')
tag_index = {}

last_tile = ""
for i in range(len(tag_list)):

    tag_index[tag_list[i]] = i
    if(tag_list[i][0]=="h" and tag_list[i]>last_tile):
        last_tile = tag_list[i]

shape = last_tile.replace("h","")
M = int(shape[0])
N = int(shape[1])

print("LastTile",M,N)

def fix_state(state):
    state_tags = state.split('.')
    new_state = "q0." # for legacy compatibility
    new_state += state_tags[tag_index["G_B"]]
    new_state += "."+state_tags[tag_index["y"]]
    new_state += "."+state_tags[tag_index["x"]]
    
    for i in range(1,M+1):
        for j in range(1,N+1):
            new_state += "."+state_tags[tag_index[f"h{i}{j}"]]

    return new_state

for state in states:

    state.set("name",fix_state(state.attrib['name']))
automaton.set('name',f"{filename}||{M}||{N}")

###
# Fix multiple events and correct transitions event ids
###
event_alias = {}
good_label = {}

id_count = 0
for e in list(events):

    label = e.attrib['label']
    cut_label = label.split('.')

    if len(cut_label)>1:
        if cut_label[0] in good_label.keys():
            event_alias[e.attrib['id']] = good_label[cut_label[0]]
            events.remove(e)
        else:
            good_label[cut_label[0]] = str(id_count)
            event_alias[e.attrib['id']] = str(id_count)
            e.set('id',str(id_count))
            e.set('label',cut_label[0])
            id_count = id_count + 1
    else:
        event_alias[e.attrib['id']] = str(id_count)
        e.set('id',str(id_count))
        id_count = id_count + 1

for t in transitions:
    if(t.attrib['event'] in event_alias.keys()):
        t.set('event',event_alias[t.attrib['event']])


# Export to File
#rough = ET.tostring(root, encoding="windows-1252").decode("windows-1252")
#reparsed = minidom.parseString(rough).toprettyxml(indent="  ")

with open(file_path,'w') as f:
    f.write(ET.tostring(root, encoding="unicode"))