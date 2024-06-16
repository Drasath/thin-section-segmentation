# Acyclic Modifier Graph (AMG) class
# Author: Lars Hidding, 2024
#
# It is a Directed Acyclic Graph (DAG) that represents user actions
# in a linear way with the possibility for multiple concurring timelines.
# An AMG can be recorded and played back to reproduce the user actions.
# TODO - Put this in the readme. LH
# TODO - Add debug logging functionality. LH

import json

class Node():
    def __init__(self, value):
        self.parent = None
        self.value = value
        self.children = []
    
    def __str__(self):
        return str(self.value) if self.children == [] else str(self.value) + " -> " + str(self.children)

    def __repr__(self):
        return str(self)

    def to_JSON(self):
        return {
            "value": self.value,
            "children": [child.toJSON() for child in self.children]
        }

    def add_child(self, node):
        self.children.append(node)
        node.parent = self

class AMG():
    def __init__(self):
        self.root: Node = None
        self.activeNode = None
    
    def addNode(self, node):
        if self.root == None:
            self.root = node
            self.activeNode = node
        else:
            self.activeNode.add_child(node)
            self.activeNode = node

    def selectNode(self, node: Node):
        self.activeNode = node

    def to_JSON(self) -> str:
        if self.root == None:
            return '{}'
        return json.dumps(self.root.to_JSON(), indent=4)
    
    def __str__(self):
        if self.root == None:
            return "Empty AMG"
        return str(self.root)
