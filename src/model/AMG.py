# Acyclic Modifier Graph (AMG) class
# Author: Lars Hidding, 2024
#
# It is a Directed Acyclic Graph (DAG) that represents user actions
# in a linear way with the possibility for multiple concurring timelines.
# An AMG can be recorded and played back to reproduce the user actions.
# TODO - Put this in the readme. LH
# TODO - Add a method to play back the AMG. LH
# TODO - Add debug logging functionality. LH

import json

class AMG():
    def __init__(self, callback=None):
        self.root = None
        self.activeNode = None
        self.callback = callback
    
    def addNode(self, node):
        if self.root == None:
            self.root = node
            self.activeNode = node
        else:
            self.activeNode.add(node)
            self.activeNode = node
        self.update()

    def selectNode(self, node):
        self.activeNode = node
        self.update()
        return self.activeNode
    
    def update(self):
        if self.callback:
            self.callback()

    def toJSON(self):
        return json.dumps(self.root.toJSON(), indent=4)
    
    def __str__(self):
        return str(self.root)

# Node class for the AMG
class Node():
    def __init__(self, value):
        self.parent = None
        self.value = value
        self.children = []
    
    def add(self, node):
        self.children.append(node)
        node.parent = self
    
    def toJSON(self):
        return {
            "value": self.value,
            "children": [child.toJSON() for child in self.children]
        }

    def __str__(self):
        return str(self.value) if self.children == [] else str(self.value) + " -> " + str(self.children)

    def __repr__(self):
        return str(self) 
