import math
import networkx as nx
import re
import os


class LocalizationModule:
    """
    Navigation module extracted from sml_using_algrthm.py.
    Feed it car position → get target coordinates + steering.
    No Pygame dependency.
    """

    def __init__(self, graph_path, visit_threshold=60.0):
        self.visit_threshold = visit_threshold
        self.G, self.pos = self._load_graph(graph_path)
        self.path = []
        self.target_index = 1
        self.goal_node = None
        self.start_node = None

    # ============== PUBLIC API ==============

    def set_goal(self, car_x, car_y, goal_node=None, goal_xy=None):
        """
        Equivalent to your mouse click in Pygame.
        Finds nearest node to car, calculates path to goal.
        Returns True if path found.
        """
        self.start_node = self._nearest_node(car_x, car_y)

        if goal_xy is not None:
            self.goal_node = self._nearest_node(goal_xy[0], goal_xy[1])
        elif goal_node is not None:
            self.goal_node = goal_node
        else:
            return False

        self.path = self._find_path(self.start_node, self.goal_node)
        self.target_index = 1 if len(self.path) > 1 else 0
        return len(self.path) > 1

    def update(self, car_x, car_y):
        """
        Equivalent to your CHECKPOINT LOGIC block.
        Call every loop tick with car position from camera.
        Returns dict with everything you need.
        """
        arrived = False
        target_x, target_y = car_x, car_y
        target_node = None
        distance = 0.0

        if len(self.path) > 1 and self.target_index < len(self.path):
            target_node = self.path[self.target_index]
            target_x, target_y = self.pos[target_node]
            distance = math.sqrt((car_x - target_x)**2 + (car_y - target_y)**2)

            # Same logic as your: if dist_to_target < VISIT_THRESHOLD
            if distance < self.visit_threshold:
                self.target_index += 1
                if self.target_index < len(self.path):
                    target_node = self.path[self.target_index]
                    target_x, target_y = self.pos[target_node]
                    distance = math.sqrt((car_x - target_x)**2 + (car_y - target_y)**2)
                else:
                    arrived = True

        return {
            "car_x": car_x,                  # current car position (what you fed in)
            "car_y": car_y,
            "target_x": target_x,            # WHERE TO DRIVE (map coordinates)
            "target_y": target_y,
            "target_node": target_node,       # node ID of current target
            "distance": distance,             # distance to target in map pixels
            "arrived": arrived,               # True = reached final goal
            "progress": self.target_index,    # same as your target_index
            "total_nodes": len(self.path),    # same as your len(path)
            "heading": math.atan2(target_y - car_y, target_x - car_x),  # angle to target
        }

    def get_steering_angle(self, car_x, car_y, car_angle):
        """
        Returns steering correction in radians.
        Positive = turn right, Negative = turn left.
        """
        state = self.update(car_x, car_y)
        if state["arrived"]:
            return 0.0

        error = state["heading"] - car_angle
        while error > math.pi:  error -= 2 * math.pi
        while error < -math.pi: error += 2 * math.pi
        return error

    def get_path_coords(self):
        """Returns full path as list of (x, y) map coordinates."""
        return [self.pos[n] for n in self.path if n in self.pos]

    def get_all_nodes(self):
        """Returns all graph nodes as {node_id: (x, y)}."""
        return dict(self.pos)

    # ============== PRIVATE (same as your functions) ==============

    def _load_graph(self, path):
        if not os.path.exists(path):
            return nx.Graph(), {}
        try:
            G = nx.read_graphml(path)
        except Exception:
            return nx.Graph(), {}

        pos = {}
        for node, data in G.nodes(data=True):
            x, y = None, None
            if 'x' in data and 'y' in data:
                x, y = float(data['x']), float(data['y'])
            else:
                for k, v in data.items():
                    s = str(v)
                    mx = re.search(r'x=["\']?([\d\.]+)["\']?', s)
                    my = re.search(r'y=["\']?([\d\.]+)["\']?', s)
                    if mx and my:
                        x, y = float(mx.group(1)), float(my.group(1))
                        break
            if x is not None:
                pos[node] = (x, y)

        for u, v in G.edges():
            if u in pos and v in pos:
                dist = math.sqrt((pos[u][0]-pos[v][0])**2 + (pos[u][1]-pos[v][1])**2)
                G[u][v]['weight'] = dist
        return G, pos

    def _find_path(self, start, end):
        try:
            return nx.dijkstra_path(self.G, start, end, weight='weight')
        except Exception:
            return []

    def _nearest_node(self, x, y):
        min_dist = float('inf')
        nearest = None
        for n, (nx_, ny_) in self.pos.items():
            d = math.sqrt((nx_ - x)**2 + (ny_ - y)**2)
            if d < min_dist:
                min_dist = d
                nearest = n
        return nearest