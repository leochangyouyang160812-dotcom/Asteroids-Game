import sys
from shot import Shot
from logger import log_event
from asteroid import Asteroid
from asteroidfield import AsteroidField
from player import Player
from logger import log_state
from constants import SCREEN_WIDTH, SCREEN_HEIGHT
import pygame
def main():
	dt = 0
	pygame.init()
	clock = pygame.time.Clock()
	updatable = pygame.sprite.Group()
	drawable = pygame.sprite.Group()
	Player.containers = (updatable, drawable)
	screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
	player = Player(SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2)
	asteroids = pygame.sprite.Group()
	Asteroid.containers = (asteroids, updatable, drawable)
	AsteroidField.containers = (updatable,)
	asteroid_field = AsteroidField()
	shots = pygame.sprite.Group()
	Shot.containers = (shots, updatable, drawable)
	print(f"Starting Asteroids with pygame version: {pygame.version.ver}")
	print(f"Screen width: {SCREEN_WIDTH}")
	print(f"Screen height: {SCREEN_HEIGHT}")
	while True:
		dt = clock.tick(60) / 1000	
		log = log_state()
		updatable.update(dt)
		for asteroid in asteroids:
			if asteroid.collides_with(player):
				log_event("player_hit")	
				print("Game over!")
				sys.exit()
			for shot in shots:
				if asteroid.collides_with(shot):
					log_event("asteroid_shot")
					shot.kill()
					asteroid.split()
		screen.fill("black")
		for obj in drawable:
			obj.draw(screen)
		pygame.display.flip()
		for event in pygame.event.get():
			if event.type == pygame.QUIT:
				return
		
if __name__ == "__main__":
	main()
