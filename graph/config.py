from screen.config import SCREEN_SIZE

TEST_MAP_GRAPH = "data/staza_graf.graphml"

SCALE_FACTOR = SCREEN_SIZE / 5000
"""
Zasto 5000 ?
Pa zato sto je graf pravljen na slici 5000 x 5000
"""

EPSILON_RADIUS = SCREEN_SIZE / 100.0

_POSITION_KEY = "pos"
_COLOR_KEY = "color"

MAX_VISITED_NODES = 5

BLUE_COLOR = (0, 150, 255)
GREEN_COLOR = (170, 255, 0)