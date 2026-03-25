import pygame
import random
from constants import *
from circleshape import CircleShape
from logger import log_event
class Asteroid(CircleShape):
	def __init__(self, x, y, radius):
		super().__init__(x, y, radius)
	def draw(self, screen):
		pygame.draw.circle(screen, "white", self.position, self.radius, LINE_WIDTH)
	def update(self, dt):
		self.position = self.position + self.velocity * dt
		if (
			self.position.x < -self.radius
			or self.position.x > SCREEN_WIDTH + self.radius
			or self.position.y < -self.radius
			or self.position.y > SCREEN_HEIGHT + self.radius
		):
			self.kill()
	def split(self):
		self.kill()
		if self.radius <= ASTEROID_MIN_RADIUS:
			return
		else:
			log_event("asteroid_split")
			random_degrees = random.uniform(20, 50)
			random_split1 = self.velocity.rotate(random_degrees)
			random_split2 = self.velocity.rotate(-random_degrees)
			new_rad = self.radius - ASTEROID_MIN_RADIUS
			asteroid1 = Asteroid(self.position.x, self.position.y, new_rad)
			asteroid1.velocity = random_split1 * 1.2
			asteroid2 = Asteroid(self.position.x, self.position.y, new_rad)
			asteroid2.velocity = random_split2 * 1.2
			
