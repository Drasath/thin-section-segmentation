# Acyclic Modifier Graph (AMG) class
# Author: Lars Hidding, 2024
#
# It is a Directed Acyclic Graph (DAG) that represents user actions
# in a linear way with the possibility for multiple concurring timelines.
# An AMG can be recorded and played back to reproduce the user actions.
# TODO - Put this in the readme. LH

import json
import logging

class Node():
    def __init__(self, value):
        self.parent = None
        self.value = value
        self.children = []
        self.last_child = None
        self.index = None
    
    def __str__(self):
        return str(self.value) if self.children == [] else str(self.value) + " -> " + str(self.children)

    def __repr__(self):
        return str(self)

    def to_JSON(self):
        return {
            "value": self.value,
            "children": [child.to_JSON() for child in self.children]
        }

    def add_child(self, node):
        self.children.append(node)
        node.parent = self

class AMG():
    def __init__(self, parent):
        self.root: Node = None
        self.activeNode = None
        self.size = 0
        self.parent = parent
    
    def addNode(self, node):
        logging.debug(f"Adding modifier {node}")
        node.index = self.size
        self.size += 1
        if self.root == None:
            self.root = node
            self.activeNode = node
        else:
            self.activeNode.add_child(node)
            self.activeNode = node

        self.parent.store_file(self.size)

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
    
    def undo(self):
        if self.activeNode.parent == None:
            return
        self.activeNode.parent.last_child = self.activeNode
        self.activeNode = self.activeNode.parent

    def redo(self):
        if self.activeNode.last_child == None:
            return
        self.activeNode = self.activeNode.last_child
            
