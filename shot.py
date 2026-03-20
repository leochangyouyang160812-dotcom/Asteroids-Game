import pygame
from constants import LINE_WIDTH
from circleshape import CircleShape
class Shot(CircleShape):
	def draw(self, screen):
		pygame.draw.circle(screen, "white", self.position, self.radius, LINE_WIDTH)
	def update(self, dt):
		self.position = self.position + self.velocity * dtclass 
	def __init__(self, x, y, radius):
		self.velocity = pygame.Vector2(0, 0)
		super().__init__(x, y, radius)
	def draw(self, screen):
		pygame.draw.circle(screen, "white", self.position, self.radius, LINE_WIDTH)
	def update(self, dt):
		self.position = self.position + self.velocity * dt
