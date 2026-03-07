import networkx

from graph.graph import Graph
from world.object import Object_2D

from .config import _POSITION_KEY, _COLOR_KEY, GREEN_COLOR, EPSILON_RADIUS

def colorCheckpoint(graph: Graph, object:Object_2D):
    objectCoords = object.getCoords()
    objectCoords = (int(objectCoords[0] * object.getScreenScale()), int(objectCoords[1] * object.getScreenScale()))
    nodes = graph.getNodes()
    
    for node in nodes:
        coords = nodes[node][_POSITION_KEY]
        
        # print(f"{coords}   {objectCoords}provera?", end="\r")
        if epsilonRadius(objectCoords, coords, EPSILON_RADIUS):
            # print("DODAJEM NODE U VISITED")
            graph.changeNodeColor(node, GREEN_COLOR)
            graph.addVisitedNode(node)
        
        
def epsilonRadius(coords_1, coords_2, epsilon=0.1):
    if abs(coords_1[0] - coords_2[0]) < epsilon and abs(coords_1[1] - coords_2[1]) < epsilon:
        return True
    
    return False