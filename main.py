import pygame
import time
import math

from world import World_2D, Car_2D
from screen import Screen
from graph import Graph

from graph.colorCheckpoint import colorCheckpoint

screen = Screen()
clock = pygame.time.Clock()

car = Car_2D(0.725, 3.4, -90, True)
world = World_2D()
graph = Graph(screen.size())

# car.setSpeed(0.5)
# car.setWheelAngle(math.radians(-15))
car.init_draw(screen.size(), world.size())
world.addEntity(car)

try:
    running = True
    while running:
        dt = clock.tick(24) / 1000.0
        running = screen.update(world.getEntities())

        colorCheckpoint(graph, car)
        graph.draw(screen.getSurface())
        world.update(dt)
except KeyboardInterrupt:
    print("\nUser pressed CTRL+C")
    screen.quit()
except Exception as e:
    print(e)