from .object import Object_2D
from .config import WHEEL_DISTANCE, CAR_ACTUAL_LENGHT, CAR_IMAGE_PATH

import math
from pathlib import Path
import pygame

class Car_2D(Object_2D):
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
        super().__init__(startX, startY, startAngle, degrees)
        
        
    def setWheelAngle(self, angle: float, degrees: bool = False):
        """
        Set car wheel angle
        
        :param angle: Angle in radians
        :type angle: float
        :param degrees: False (default) for radians / True for degrees
        :type degrees: bool
        """
        
        if degrees:
            angle = math.radians(angle)
        self.angularSpeed = self.speed / WHEEL_DISTANCE * math.tan(angle)
        
    def init_draw(self, surfaceSize: int, worldSize: float, image_path: str = CAR_IMAGE_PATH):
        self.screenScale = float(surfaceSize) / worldSize
        self.heightScaled = self.screenScale * CAR_ACTUAL_LENGHT
        
        self.current_path:Path = Path(__file__).resolve().parent
        self.image_path: Path = Path(self.current_path / image_path)
        
        self.image = pygame.image.load(self.image_path.absolute()).convert_alpha()
        org_w, org_h = self.image.get_size()
        aspect_ratio = org_w / org_h
        
        self.rect = self.image.get_rect(center=(self.X, self.Y))
        
        new_w = int(self.heightScaled * aspect_ratio)
        self.surface = pygame.transform.smoothscale(self.image, (new_w, self.heightScaled))
        self.surface = pygame.transform.rotate(self.surface, -90)
        self.lastAngle = 0
           
    def __repr__(self):
        repr = f"Car object (X, Y, THETA) : ({self.X:.3}, {self.Y:.3}, {self.angle:.3})"
        return repr