from .config import TEST_MAP_GRAPH, SCALE_FACTOR, SCREEN_SIZE, BLUE_COLOR, _POSITION_KEY, _COLOR_KEY, MAX_VISITED_NODES

from typing import Union
import pygame
from pygame import Surface
from pathlib import Path
import networkx

from collections import deque

class Graph:
    def __init__(self, screenSize:int, path: str = TEST_MAP_GRAPH):
        self.screenSize: int = screenSize
        
        self.path: Path = Path(__file__).resolve().parent
        self.path = Path(self.path / path)
        
        self.graph:networkx.Graph = None
        self.nodes: dict = {}
        
        self.visitedNodes = deque()
        
        self.loadGraph()
        
        
    def loadGraph(self):
        if self.path.exists():
            self.graph = networkx.read_graphml(self.path.absolute())
            
            # self.position = networkx.spring_layout(self.graph, scale=SCALE_FACTOR, center=(SCREEN_SIZE//2, SCREEN_SIZE//2))
            
            for node, data in self.graph.nodes(data=True):
                x, y = None, None
                if 'x' in data and 'y' in data:
                    x, y = float(data['x'])  * SCALE_FACTOR, float(data['y']) * SCALE_FACTOR
                    
                    self.nodes[node] = {_POSITION_KEY:(x,y), _COLOR_KEY:(BLUE_COLOR)}
        
    def draw(self, surface: Surface):
        for node in self.nodes:
            coords = self.nodes[node][_POSITION_KEY]
            color = self.nodes[node][_COLOR_KEY]
            pygame.draw.circle(surface, color, (int(coords[0]), int(coords[1])), 10)
            pass
        
    def changeNodeColor(self, node, color):
        self.nodes[node][_COLOR_KEY] = color
        
    def getNodes(self):
        return self.nodes
    
    def addVisitedNode(self, node):
        
        if node not in self.visitedNodes:
            self.visitedNodes.append(node)
        
        if len(self.visitedNodes) > MAX_VISITED_NODES:
            node = self.visitedNodes.popleft()
            self.nodes[node][_COLOR_KEY] = BLUE_COLOR