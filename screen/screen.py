from .config import SCREEN_SIZE, IMAGE_PATH, COLOR_BLACK
from world.object import Object_2D

import pygame
from pathlib import Path

class Screen:
    def __init__(self, width: int = SCREEN_SIZE, height: int = SCREEN_SIZE, image_path: str = IMAGE_PATH):
        
        pygame.init()
        self.width:int = width
        self.height:int = height
        
        self.screen = pygame.display.set_mode((self.width, self.height))
        pygame.display.set_caption("Simulator")
        
        self.current_path:Path = Path(__file__).resolve().parent
        self.image_path: Path = Path(self.current_path / image_path)
        print(f"Loading picture \"{self.image_path.absolute()}\"")
        if self.image_path.exists():
            print("Succesfully loaded image")
            self.map_surface = pygame.image.load(self.image_path.absolute()).convert()
            self.map_surface = pygame.transform.scale(self.map_surface, self.screen.get_size())
        else:
            print("Could not load picture")
            self.map_surface = pygame.Surface((self.width, self.height))
            self.map_surface.fill(COLOR_BLACK)
            
    def update(self, entities = None):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False
            
        self.screen.blit(self.map_surface, (0,0))
        
        if entities:
            for entity in entities:
                entity: Object_2D
                entity.draw(self.screen)
        
        pygame.display.flip()
        return True
    
    def size(self):
        return self.width
    
    def getSurface(self):
        return self.map_surface
    
    def quit(self):
        pygame.quit()