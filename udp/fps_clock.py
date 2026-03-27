"""
FPS Clock - održava konstantan FPS bez dodatnih dependencies
"""
import time

class FPSClock:
    """
    Održava konstantan FPS (frame rate)
    
    Primer:
        clock = FPSClock(30)  # 30 FPS
        while True:
            # ... radi nešto ...
            clock.tick()  # Automatski čeka da bi održao 30 FPS
            print(f"Current FPS: {clock.get_fps()}")
    """
    
    def __init__(self, target_fps: int = 30):
        """
        Args:
            target_fps: Ciljani FPS (npr. 30, 60)
        """
        self.target_fps = target_fps
        self.frame_time = 1.0 / target_fps
        self.last_time = time.time()
        self.frames = 0
        self.fps = target_fps
        self.last_fps_update = time.time()
    
    def tick(self) -> float:
        """
        Čeka koliko je potrebno da bi se održao target FPS
        
        Returns:
            Vreme čekanja (u sekundama)
        """
        current_time = time.time()
        elapsed = current_time - self.last_time
        wait_time = self.frame_time - elapsed
        
        # Čekaj samo ako je potrebno
        if wait_time > 0:
            time.sleep(wait_time)
            current_time = time.time()
        
        # Update za sledeći frame
        self.last_time = current_time
        self.frames += 1
        
        # Ažurira FPS brojač svaku sekundu
        if current_time - self.last_fps_update >= 1.0:
            self.fps = self.frames
            self.frames = 0
            self.last_fps_update = current_time
        
        return max(0, wait_time)
    
    def get_fps(self) -> int:
        """Vraća trenutni FPS"""
        return self.fps
    
    def set_target_fps(self, fps: int):
        """Promeni target FPS"""
        self.target_fps = fps
        self.frame_time = 1.0 / fps
