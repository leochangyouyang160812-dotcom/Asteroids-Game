import random
import pygame
from circleshape import CircleShape
from constants import *
POWERUP_TYPES = ["cooldown", "speed", "healing", "phasing"]
class Powerup(CircleShape):
	def __init__(self, x, y):
		super().__init__(x, y, POWERUP_RADIUS)
		self.type = random.choice(POWERUP_TYPES)
		colors = {
			"cooldown": "cyan",
			"speed": "orange",
			"healing": "green",
			"phasing": "purple"
		}
		self.color = colors[self.type]
	def draw(self, screen):
		pygame.draw.circle(screen, self.color, self.position, self.radius, LINE_WIDTH)
	def update(self, dt):
		self.position += self.velocity * dt
