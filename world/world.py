from .object import Object_2D
from .config import TEST_MAP_SIZE

class World_2D:
    def __init__(self, width: float = TEST_MAP_SIZE, height: float = TEST_MAP_SIZE):
        self.entities = {}
        self.nextID: int = 0
        
        self.width = width
        self.height = height
    
    def update(self, dt: float):
        for entity in self.entities.values():
            entity: Object_2D
            entity.update(dt)
            
    def addEntity(self, entity):
        currentID = self.nextID

        self.entities[currentID] = entity
        self.nextID += 1
        
        return currentID
        
    def getEntity(self, id: int):
        return self.entities.get(id)
    
    def getEntities(self) -> dict:
        return self.entities.values()
    
    def size(self):
        return self.width
    
    