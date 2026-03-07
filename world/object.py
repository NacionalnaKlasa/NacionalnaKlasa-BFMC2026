import math
from pygame import Surface
import pygame

class Object_2D:
    def __init__(self, startX: float = 0.0, startY: float = 0.0, startAngle: float = 0.0, degrees: bool = False):
        """        
        :param startX: Starting X position in the world
        :type startX: float
        :param startY: Starting Y position in the world
        :type startY: float
        :param startAngle: Starting angle in radians in the world
        :type startAngle: float
        :param degrees: False (default) for radians / True for degrees
        """
        self.X: float = startX
        self.Y: float = startY
        self.speed: float = 0.0
        
        if degrees:
            startAngle = math.radians(startAngle)
        self.angle: float = startAngle
        self.angularSpeed: float = 0
        
        self.screenScale: float = 1.0
        self.surface: Surface = None
        
    def update(self, dt: float):
        """
        Update object position based on dt.\n
        Set speed and angle in order for object to move
        
        :param dt: Time in seconds
        :type dt: float
        """
        self._calculateCoordinates(dt)
        self._calculateAngles(dt)
        
    def _calculateCoordinates(self, dt):
        self.X += self.speed * dt * math.cos(self.angle)
        self.Y += self.speed * dt * math.sin(self.angle)
        
    def _calculateAngles(self, dt):
        self.angle += self.angularSpeed * dt
        self.angle = self.angle % (2 * math.pi)
        
    def draw(self, surface: Surface):
        angle = math.degrees(self.angle)
        car = pygame.transform.rotate(self.surface, -angle)
        
        pos_x = int(self.X * self.screenScale)
        pos_y = int(self.Y * self.screenScale)
        self.rect = car.get_rect(center=(pos_x, pos_y))     
        
        surface.blit(car, self.rect)
        # pygame.draw.circle(surface, (255,255,255), (self.X * self.screenScale, self.Y * self.screenScale), 7)
        
    def setSpeed(self, speed: float):
        """      
        Set current speed of object in m/s
        
        :param speed: Speed in m/s
        :type speed: float
        """
        self.speed = speed
        
    def getSpeed(self) -> float:
        """
        Get current speed of object in m/s
        """
        return self.speed
    
    def setAngularSpeed(self, angularSpeed: float, degrees: bool = False):
        """
        Setting angular speed of object (default is in radians)
                
        :param angularSpeed: Angular speed of object
        :type angularSpeed: float
        
        :param degrees: False (default) for radians / True for degrees
        """
        if degrees:
            angularSpeed = math.radians(angularSpeed)
            
        self.angularSpeed = angularSpeed
        
    def getAngularSpeed(self) -> float:
        """
        Returns angular speed in rad/s
        """
        return self.angularSpeed
    
    def setAngle(self, angle: float, degrees: bool = False):
        if degrees:
            angle = math.radians(angle)
            
        self.angle = angle
        
    def getCoords(self):
        return (self.X, self.Y)
    
    def getScreenScale(self):
        return self.screenScale