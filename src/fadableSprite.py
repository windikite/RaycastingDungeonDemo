from resourceLoader import resource_path
import pygame

class FadableSprite(pygame.sprite.Sprite):
    def __init__(self, image_path, center, fade_speed=300, default_alpha=255, orientation="front"):
        super().__init__()
        # 1) load once, keep an un‑modified copy
        self.image_path = image_path
        self.character_orientation = orientation
        self.character_state = "idle"
        self.original = pygame.image.load(resource_path(image_path + '_' + self.character_orientation + '_' + self.character_state + '.png')).convert_alpha()
        self.image    = self.original.copy()
        self.rect     = self.image.get_rect(center=center)
        
        # 2) alpha state
        self.alpha        = default_alpha          # current alpha
        self.target_alpha = default_alpha          # where we want to go
        self.fade_speed   = fade_speed # alpha‑per‑second
        self.image.set_alpha(self.alpha)

    def set_target_alpha(self, a: int):
        """Call this whenever selection changes."""
        self.target_alpha = max(0, min(255, a))

    def update(self, dt: float):
        """Move self.alpha toward self.target_alpha by fade_speed*dt, then apply."""
        if self.alpha < self.target_alpha:
            self.alpha = min(self.target_alpha, self.alpha + self.fade_speed * dt)
        elif self.alpha > self.target_alpha:
            self.alpha = max(self.target_alpha, self.alpha - self.fade_speed * dt)
        
        # 3) re‑blit image copy with new alpha
        self.image = self.original.copy()
        self.image.set_alpha(int(self.alpha))