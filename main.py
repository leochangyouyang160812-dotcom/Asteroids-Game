import asyncio
import random
import sys
import os
from powerup import Powerup
from shot import Shot, PiercingShot, ExplosiveShot, MachineGunShot
from logger import log_event
from asteroid import Asteroid
from asteroidfield import AsteroidField
from player import Player
from logger import log_state
from constants import *
import pygame


async def controls_menu(screen, player, high_score):
    font = pygame.font.SysFont(None, 48)
    small_font = pygame.font.SysFont(None, 36)
    cx = SCREEN_WIDTH // 2
    controls = [
        "W key  -  Forward",
        "S key  -  Back",
        "A / D key  -  Rotate",
        "Space  -  Shoot",
        "Up Arrow key  -  Use Special",
        "ESC key  -  Main Menu",
    ]
    while True:
        screen.fill("black")
        titles = font.render("CONTROLS", True, "white")
        screen.blit(titles, titles.get_rect(center=(cx, 120)))
        for i, line in enumerate(controls):
            text = small_font.render(line, True, "grey")
            screen.blit(text, text.get_rect(center=(cx, 240 + i * 60)))
        back = small_font.render("Press ESC to go back", True, "white")
        screen.blit(back, back.get_rect(center=(cx, SCREEN_HEIGHT - 60)))
        pygame.display.flip()
        await asyncio.sleep(0)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                return
            if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                return


async def weapons_menu(screen, player, high_score):
    selected_message = ""
    font = pygame.font.SysFont(None, 56)
    small_font = pygame.font.SysFont(None, 36)
    tiny_font = pygame.font.SysFont(None, 26)
    cx = SCREEN_WIDTH // 2
    weapons = [
        {"label": "Normal",      "mode": "normal",      "unlock": 0},
        {"label": "Piercing", "mode": "piercing", "unlock": UNLOCK_PIERCING},
        {"label": "Explosive",    "mode": "explosive",    "unlock": UNLOCK_EXPLOSIVE},
        {"label": "Machine Gun",   "mode": "machine_gun",   "unlock": UNLOCK_MACHINE_GUN, "small": True},
    ]
    for i, weapon in enumerate(weapons):
        weapon["rect"] = pygame.Rect(0, 0, 300, 60)
        weapon["rect"].center = (cx, 250 + i * 90)
    while True:
        screen.fill("black")
        title = font.render("SELECT WEAPON", True, "white")
        screen.blit(title, title.get_rect(center=(cx, 120)))
        mouse_pos = pygame.mouse.get_pos()
        for weapon in weapons:
            locked = high_score < weapon["unlock"]
            selected = weapon["mode"] == player.shoot_mode
            hovered = weapon["rect"].collidepoint(mouse_pos)
            if locked:
                color = "red"
                label_text = f"{weapon['label']} (unlock at {weapon['unlock']})"
            elif selected:
                color = "yellow"
                label_text = weapon["label"]
            elif hovered:
                color = "white"
                label_text = weapon["label"]
            else:
                color = "grey"
                label_text = weapon["label"]
            pygame.draw.rect(screen, color, weapon["rect"], 2, border_radius=8)
            render_font = tiny_font if weapon.get("small") else small_font
            label = render_font.render(label_text, True, color)
            screen.blit(label, label.get_rect(center=weapon["rect"].center))
        back = small_font.render("Press ESC to go back", True, "grey")
        screen.blit(back, back.get_rect(center=(cx, SCREEN_HEIGHT - 60)))
        if selected_message:
            msg = small_font.render(selected_message, True, "red")
            screen.blit(msg, msg.get_rect(center=(cx, SCREEN_HEIGHT - 100)))
        pygame.display.flip()
        await asyncio.sleep(0)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                return
            if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                return
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                for weapon in weapons:
                    if weapon["rect"].collidepoint(event.pos):
                        if high_score >= weapon["unlock"]:
                            player.shoot_mode = weapon["mode"]
                            import player as player_module
                            player_module._last_shoot_mode = weapon["mode"]
                            selected_message = ""
                        else:
                            selected_message = f"Reach a score of {weapon['unlock']} to unlock {weapon['label']}!"


async def game_over_menu(screen, score, high_score):
    font = pygame.font.SysFont(None, 80)
    mid_font = pygame.font.SysFont(None, 48)
    small_font = pygame.font.SysFont(None, 36)
    cx = SCREEN_WIDTH // 2
    cy = SCREEN_HEIGHT // 2
    while True:
        screen.fill("black")
        title = font.render("GAME OVER", True, "red")
        score_text = mid_font.render(f"Score: {score}", True, "white")
        high_score_text = mid_font.render(f"High Score: {high_score}", True, "yellow")
        prompt = small_font.render("R  -  Play Again          M  -  Main Menu", True, "grey")
        screen.blit(title, title.get_rect(center=(cx, cy - 160)))
        screen.blit(score_text, score_text.get_rect(center=(cx, cy - 60)))
        screen.blit(high_score_text, high_score_text.get_rect(center=(cx, cy + 20)))
        screen.blit(prompt, prompt.get_rect(center=(cx, cy + 120)))
        pygame.display.flip()
        await asyncio.sleep(0)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                return "quit"
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_r:
                    return "replay"
                elif event.key == pygame.K_m:
                    return "menu"


async def start_menu(screen, player, high_score):
    font_large = pygame.font.SysFont(None, 80)
    font_mid = pygame.font.SysFont(None, 56)
    font_small = pygame.font.SysFont(None, 42)
    cx = SCREEN_WIDTH // 2
    cy = SCREEN_HEIGHT // 2 + 60
    buttons = [
        {"label": "Controls",      "rect": pygame.Rect(0, 0, 220, 60), "font": font_small, "action": "controls"},
        {"label": "PLAY",          "rect": pygame.Rect(0, 0, 280, 80), "font": font_mid,   "action": "play"},
        {"label": "Weapons",       "rect": pygame.Rect(0, 0, 220, 60), "font": font_small, "action": "weapons"},
        {"label": "Reset Progress","rect": pygame.Rect(0, 0, 220, 60), "font": font_small, "action": "reset"},
    ]
    offsets = [-340, 0, 340]
    for i, btn in enumerate(buttons[:3]):
        btn["rect"].center = (cx + offsets[i], cy)
    buttons[3]["rect"].center = (cx, cy + 80)
    while True:
        screen.fill("black")
        title = font_large.render("ASTEROIDS", True, "white")
        screen.blit(title, title.get_rect(center=(cx, SCREEN_HEIGHT // 2 - 80)))
        mouse_pos = pygame.mouse.get_pos()
        for btn in buttons:
            hovered = btn["rect"].collidepoint(mouse_pos)
            color = "yellow" if hovered else "grey"
            pygame.draw.rect(screen, color, btn["rect"], 2, border_radius=8)
            label = btn["font"].render(btn["label"], True, color)
            screen.blit(label, label.get_rect(center=btn["rect"].center))
        pygame.display.flip()
        await asyncio.sleep(0)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                for btn in buttons:
                    if btn["rect"].collidepoint(event.pos):
                        if btn["action"] == "play":
                            return True
                        elif btn["action"] == "controls":
                            await controls_menu(screen, player, high_score)
                        elif btn["action"] == "weapons":
                            await weapons_menu(screen, player, high_score)
                        elif btn["action"] == "reset":
                            await reset_menu(screen, player)


async def confirm_menu(screen):
    font = pygame.font.SysFont(None, 48)
    small = pygame.font.SysFont(None, 36)
    cx = SCREEN_WIDTH // 2
    cy = SCREEN_HEIGHT // 2
    while True:
        screen.fill("black")
        warning = font.render("Return to main menu?", True, "white")
        prompt = small.render("Y  -  Yes         N  -  No", True, "grey")
        screen.blit(warning, warning.get_rect(center=(cx, cy - 40)))
        screen.blit(prompt, prompt.get_rect(center=(cx, cy + 40)))
        pygame.display.flip()
        await asyncio.sleep(0)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return "quit"
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_y:
                    return "menu"
                elif event.key == pygame.K_n:
                    return "game"


async def reset_menu(screen, player):
    font = pygame.font.SysFont(None, 48)
    small = pygame.font.SysFont(None, 36)
    cx = SCREEN_WIDTH // 2
    cy = SCREEN_HEIGHT // 2
    while True:
        screen.fill("black")
        warning = font.render("Reset high score and progress?", True, "white")
        prompt = small.render("Y  -  Yes     N  -  No", True, "grey")
        screen.blit(warning, warning.get_rect(center=(cx, cy - 40)))
        screen.blit(prompt, prompt.get_rect(center=(cx, cy + 40)))
        pygame.display.flip()
        await asyncio.sleep(0)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                return
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_y:
                    player.shoot_mode = "normal"
                    with open("highscore.txt", "w") as f:
                        f.write("0")
                    return
                elif event.key == pygame.K_n:
                    return


async def play_game(screen, shoot_mode="normal"):
    dt = 0
    score = 0
    high_score = 0
    powerup_timer = 0
    level = 1
    level_display_timer = 0
    level_font = pygame.font.SysFont(None, 72)
    asteroids_cleared = 0
    stored_powerup = None
    paused = False
    last_powerup_score = 0
    font = pygame.font.SysFont(None, 36)
    clock = pygame.time.Clock()

    updatable = pygame.sprite.Group()
    drawable = pygame.sprite.Group()
    asteroids = pygame.sprite.Group()
    shots = pygame.sprite.Group()
    powerups = pygame.sprite.Group()

    Player.containers = (updatable, drawable)
    Asteroid.containers = (asteroids, updatable, drawable)
    AsteroidField.containers = (updatable,)
    Shot.containers = (shots, updatable, drawable)
    MachineGunShot.containers = (shots, updatable, drawable)
    PiercingShot.containers = (shots, updatable, drawable)
    ExplosiveShot.containers = (shots, updatable, drawable)
    Powerup.containers = (powerups, updatable, drawable)

    player = Player(SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2)
    player.shoot_mode = shoot_mode
    asteroid_field = AsteroidField(asteroids)

    if os.path.exists("highscore.txt"):
        with open("highscore.txt", "r") as f:
            content = f.read().strip()
            if content:
                high_score = int(content)
            else:
                high_score = 0

    while True:
        log = log_state()
        line_spacing = 30

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    paused = True
                    result = await confirm_menu(screen)
                    if result == "quit":
                        return
                    elif result == "menu":
                        await main()
                    elif result == "game":
                        paused = False
                        clock.tick()
                        dt = 0
                elif event.key == pygame.K_UP and stored_powerup:
                    if stored_powerup == "cooldown":
                        player.color = "cyan"
                        if player.shoot_mode == "machine_gun":
                            player.machine_gun_cooldown -= 0.02
                            powerup_timer = 10
                            stored_powerup = None
                        else:
                            player.shoot_cooldown -= 0.02
                            powerup_timer = 10
                            stored_powerup = None
                    elif stored_powerup == "speed":
                        player.color = "orange"
                        player.speed += 4
                        powerup_timer = 10
                        stored_powerup = None
                    elif stored_powerup == "healing":
                        player.lives += 1
                        stored_powerup = None
                    elif stored_powerup == "phasing":
                        player.color = "purple"
                        player.phasing = True
                        powerup_timer = 5
                        stored_powerup = None

        if paused:
            pygame.display.flip()
            continue

        for asteroid in asteroids:
            if player.phasing:
                continue
            if player.invincibility_timer <= 0:
                if asteroid.collides_with(player):
                    player.lives -= 1
                    if player.lives > 0:
                        player.respawn()
                    else:
                        log_event("player_hit")
                        print(f"Score: {score}")
                        print(f"High Score: {high_score}")
                        print("Game over!")
                        with open("highscore.txt", "w") as f:
                            f.write(str(high_score))
                        result = await game_over_menu(screen, score, high_score)
                        if result == "replay":
                            await play_game(screen, shoot_mode=player.shoot_mode)
                        elif result == "menu":
                            await main()
                        return
        for shot in shots:
            hit = pygame.sprite.spritecollide(shot, asteroids, False, pygame.sprite.collide_circle)
            for asteroid in hit:
                log_event("asteroid_shot")
                points = shot.on_hit(asteroid, asteroids)
                score += points if points else 1
                if score > high_score:
                    high_score = score
                new_level = (score // 100) + 1
                if new_level > level:
                    level = new_level
                    level_display_timer = 4.0
                    asteroid_field.spawn_rate = max(0.2, ASTEROID_SPAWN_RATE_SECONDS * (0.85 ** (level - 1)))
                    asteroid_field.speed_min = min(150, 40 + (level - 1) * 5)
                    asteroid_field.speed_max = min(250, 100 + (level - 1) * 10)
                    print(f"Level {level}!")
                if score % 50 == 0 and score != last_powerup_score:
                    last_powerup_score = score
                    edge = random.randint(0, 3)
                    if edge == 0:
                        x, y = 0, random.randint(0, SCREEN_HEIGHT)
                        velocity = pygame.Vector2(1, 0) * POWERUP_SPEED
                    elif edge == 1:
                        x, y = SCREEN_WIDTH, random.randint(0, SCREEN_HEIGHT)
                        velocity = pygame.Vector2(-1, 0) * POWERUP_SPEED
                    elif edge == 2:
                        x, y = random.randint(0, SCREEN_WIDTH), 0
                        velocity = pygame.Vector2(0, 1) * POWERUP_SPEED
                    else:
                        x, y = random.randint(0, SCREEN_WIDTH), SCREEN_HEIGHT
                        velocity = pygame.Vector2(0, -1) * POWERUP_SPEED
                    p = Powerup(x, y)
                    p.velocity = velocity
                if not isinstance(shot, PiercingShot):
                    break

        for powerup in powerups:
            if player.collides_with(powerup):
                stored_powerup = powerup.type
                powerup.kill()

        screen.fill("black")
        for obj in drawable:
            obj.draw(screen)
        fps = int(clock.get_fps())
        fps_text = font.render(f"FPS: {fps}", True, "white")
        screen.blit(fps_text, (SCREEN_WIDTH - fps_text.get_width() - 10, 10))

        score_surface = font.render(f"Score: {score}", True, "white")
        high_score_surface = font.render(f"High Score: {high_score}", True, "white")
        player.lives_surface = font.render(f"Lives Remaining: {player.lives}", True, "white")
        screen.blit(score_surface, (10, 10))
        screen.blit(high_score_surface, (10, 10 + line_spacing))
        screen.blit(player.lives_surface, (10, 10 + (line_spacing * 2)))

        powerup_label = stored_powerup if stored_powerup else "none"
        special_surface = font.render(f"Special: {powerup_label}", True, "white")
        screen.blit(special_surface, (SCREEN_WIDTH - special_surface.get_width() - 10, SCREEN_HEIGHT - 40))

        if level_display_timer > 0:
            text = level_font.render(f"Level {level}", True, "white")
            rect = text.get_rect(center=(SCREEN_WIDTH / 2, 60))
            screen.blit(text, rect)

        pygame.display.flip()
        updatable.update(dt)

        if level_display_timer > 0:
            level_display_timer -= dt
        if powerup_timer > 0:
            powerup_timer -= dt
            if powerup_timer <= 0:
                powerup_timer = 0
                player.color = "white"
                player.speed = PLAYER_SPEED
                player.shoot_cooldown = PLAYER_SHOOT_COOLDOWN_SECONDS
                player.machine_gun_cooldown = MACHINE_GUN_COOLDOWN
                player.phasing = False
        dt = clock.tick(60) / 1000
        await asyncio.sleep(0)

async def main():
    pygame.init()
    pygame.font.init()
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    # Temporary player just for the menus (weapons/reset)
    Player.containers = ()
    temp_player = Player(0, 0)

    high_score = 0
    if os.path.exists("highscore.txt"):
        with open("highscore.txt", "r") as f:
            content = f.read().strip()
            if content:
                high_score = int(content)
    Player.containers = ()
    temp_player = Player(0, 0)

    if not await start_menu(screen, temp_player, high_score):
        return

    print(f"Starting Asteroids with pygame version: {pygame.version.ver}")
    print(f"Screen width: {SCREEN_WIDTH}")
    print(f"Screen height: {SCREEN_HEIGHT}")
    await play_game(screen, shoot_mode=temp_player.shoot_mode)

pygame.init()
pygame.font.init()
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
asyncio.run(main())
