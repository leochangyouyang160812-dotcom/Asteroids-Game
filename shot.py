import pygame
from constants import ASTEROID_MIN_RADIUS, SHOT_RADIUS, LINE_WIDTH, EXPLOSIVE_SHOT_RADIUS
from circleshape import CircleShape
class Shot(CircleShape):
	def __init__(self, x, y, radius=SHOT_RADIUS):
		self.velocity = pygame.Vector2(0, 0)
		super().__init__(x, y, radius)
	def draw(self, screen):
		pygame.draw.circle(screen, "white", self.position, self.radius, LINE_WIDTH)
	def update(self, dt):
		self.position = self.position + self.velocity * dt
	def on_hit(self, asteroid, asteroids):
		asteroid.split()
		self.kill()
		return 1
class PiercingShot(Shot):
	def __init__(self, x, y):
		super().__init__(x, y, SHOT_RADIUS)
	def on_hit(self, asteroid, asteroids):
		asteroid.split()
		return 1	
class ExplosiveShot(Shot):
	def __init__(self, x, y):
		super().__init__(x, y, EXPLOSIVE_SHOT_RADIUS)
	def on_hit(self, asteroid, asteroids):
		points_map = {
			ASTEROID_MIN_RADIUS: 1,
			ASTEROID_MIN_RADIUS * 2: 3,
			ASTEROID_MIN_RADIUS * 3: 1,
		}
		points = points_map.get(int(asteroid.radius), 1)
		asteroid.split()
		self.kill()
		for other in list(asteroids):
			if other is not asteroid:
				if self.position.distance_to(other.position) < self.radius * 3:
					other.kill()
		return points
class MachineGunShot(Shot):
	def __init__(self, x, y):
		super().__init__(x, y, SHOT_RADIUS)

SHOT_CLASSES = {
	"normal": Shot,
	"machine_gun": MachineGunShot,
	"piercing": PiercingShot,
	"explosive": ExplosiveShot,
}
