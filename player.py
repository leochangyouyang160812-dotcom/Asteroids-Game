import pygame
from shot import Shot, MachineGunShot, PiercingShot, ExplosiveShot, SHOT_CLASSES
from circleshape import CircleShape
from constants import *
_last_shoot_mode = "normal"
class Player(CircleShape):
	def __init__(self, x, y):
		super().__init__(x, y, PLAYER_RADIUS)
		self.cooldown = 0
		self.lives = 3
		self.invincibility_timer = RESPAWN_INVINCIBILITY
		self.visible = True
		self.rotation = 0
		self.shoot_mode = "normal"
		self.speed = PLAYER_SPEED
		self.shoot_cooldown = PLAYER_SHOOT_COOLDOWN_SECONDS
		self.color = "white"
		self.phasing = False
		self.machine_gun_cooldown = MACHINE_GUN_COOLDOWN
		global _last_shoot_mode
		self.shoot_mode = _last_shoot_mode
	def triangle(self):
		forward = pygame.Vector2(0, 1).rotate(self.rotation)
		right = pygame.Vector2(0, 1).rotate(self.rotation + 90) * self.radius / 1.5
		a = self.position + forward * self.radius
		b = self.position - forward * self.radius - right
		c = self.position - forward * self.radius + right
		return [a, b, c]
	def draw(self, screen):
		if not self.visible:
			return
		if (pygame.time.get_ticks() // 100) % 2 == 0:
			super().draw(screen)
		pygame.draw.polygon(screen, self.color, self.triangle(), LINE_WIDTH)
	def update(self, dt):
		if self.cooldown > 0:
			self.cooldown -= dt
		if self.invincibility_timer > 0:
			self.invincibility_timer -= dt
			self.visible = not self.visible
		else:
			self.visible = True
		keys = pygame.key.get_pressed()

		if keys[pygame.K_a]:
			self.rotate(-dt)
		if keys[pygame.K_d]:
			self.rotate(dt)
		if keys[pygame.K_w]:
			self.move(dt)
		if keys[pygame.K_s]:
			self.move(-dt)
		if keys[pygame.K_SPACE]:
			self.shoot()
		self.position += self.velocity * dt
	def rotate(self, dt):
		self.rotation += PLAYER_TURN_SPEED * dt
	def move(self, dt):
		unit_vector = pygame.Vector2(0, 1)
		rotated_vector = unit_vector.rotate(self.rotation)
		rotated_with_speed_vector = rotated_vector * PLAYER_SPEED * dt
		self.position += rotated_with_speed_vector
	def shoot(self):
		cooldown = MACHINE_GUN_COOLDOWN if self.shoot_mode == "machine_gun" else PLAYER_SHOOT_COOLDOWN_SECONDS
		if self.cooldown > 0:
			return
		self.cooldown = cooldown
		shot_class = SHOT_CLASSES[self.shoot_mode]
		shot = shot_class(self.position.x, self.position.y)
		shot.velocity = pygame.Vector2(0, 1).rotate(self.rotation) * PLAYER_SHOOT_SPEED

	def respawn(self):
		self.invincibility_timer = RESPAWN_INVINCIBILITY

