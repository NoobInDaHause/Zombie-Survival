import pygame
import random

from entities import Player, Zombie

pygame.init()
pygame.mixer.init()

WIDTH, HEIGHT = 1280, 720
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Zombie Survival")

clock = pygame.time.Clock()
FPS = 60

bg_image = pygame.image.load("assets/images/Background.png").convert_alpha()

pygame.mixer.music.load("assets/sounds/BGM.mp3")
pygame.mixer.music.set_volume(0.5)
pygame.mixer.music.play(-1, 0.0, 5000)
shoot_fx = pygame.mixer.Sound("assets/sounds/Shoot.mp3")
shoot_fx.set_volume(0.1)
reload_fx = pygame.mixer.Sound("assets/sounds/Reload.mp3")
reload_fx.set_volume(0.1)
no_ammo_fx = pygame.mixer.Sound("assets/sounds/Empty_Gunshot.mp3")
no_ammo_fx.set_volume(0.1)
pain_fx = pygame.mixer.Sound("assets/sounds/Pain.mp3")
pain_fx.set_volume(0.1)
sound_list = [shoot_fx, reload_fx, pain_fx]

game_over_fx = pygame.mixer.Sound("assets/sounds/Game_Over.mp3")
game_over_fx.set_volume(0.5)
game_over = False
played_game_over = False

score = 0


def draw_bg():
    scaled_bg = pygame.transform.scale(bg_image, (WIDTH, HEIGHT))
    screen.blit(scaled_bg, (0, 0))


def draw_hp(health: int):
    hp_font = pygame.font.Font(None, 36)
    hp_text = hp_font.render(f"Health: {health}", True, (0, 255, 0))
    hp_rect = hp_text.get_rect(center=(75, 25))
    screen.blit(hp_text, hp_rect)


def draw_game_over():
    if game_over:
        go_font = pygame.font.Font(None, 300)
        go_text = go_font.render("GAME OVER", True, (255, 0, 0))
        go_rect = go_text.get_rect(center=(640, 350))
        screen.blit(go_text, go_rect)


def draw_ammo(ammo: int):
    ammo_font = pygame.font.Font(None, 36)
    text = ammo_font.render(f"Ammo: {ammo}", True, (255, 255, 255))
    text_rect = text.get_rect(center=(1200, 25))
    screen.blit(text, text_rect)

    if ammo == 0:
        reload_font = pygame.font.Font(None, 50)
        reload_text = reload_font.render(f"RELOAD!", True, (255, 0, 0))
        reloadtext_rect = reload_text.get_rect(center=(WIDTH // 2, HEIGHT - 25))
        screen.blit(reload_text, reloadtext_rect)


def draw_score():
    score_font = pygame.font.Font(None, 36)
    score_text = score_font.render(f"Kills: {score}", True, (255, 255, 255))
    score_rect = score_text.get_rect(center=(640, 25))
    screen.blit(score_text, score_rect)


player = Player(500, 310, sound_list)


def generate_zombie():
    which = random.choice([True, False])
    x = WIDTH if which else -128

    return Zombie(x, 310, which)


zombies = [
    generate_zombie(),
    generate_zombie(),
    generate_zombie(),
    generate_zombie(),
    generate_zombie(),
]

run = True
while run:
    clock.tick(FPS)

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            run = False
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE and player.ammo == 0:
                no_ammo_fx.stop()
                no_ammo_fx.play()

    if player.alive is False:
        game_over = True

    if game_over and not played_game_over:
        game_over_fx.play()
        pygame.mixer.music.stop()
        played_game_over = True

    player.move(WIDTH, game_over)
    player.update()

    for zombie in zombies[:]:
        zombie.move(game_over)
        zombie.update(game_over)

        for bullet in player.bullets[:]:
            if zombie.get_hitbox().colliderect(bullet.rect) and zombie.alive:
                zombie.hit = True
                dead = pygame.mixer.Sound("assets/sounds/Zombie_Death.mp3")
                dead.set_volume(0.5)
                dead.play()
                score += 1
                player.bullets.remove(bullet)
                break

        if zombie.get_hitbox().colliderect(player.get_hitbox()) and zombie.alive:
            player.hit = True
            zombie.alive = False

            zombies.remove(zombie)
            zombies.append(generate_zombie())
            continue

    draw_bg()
    draw_game_over()
    draw_score()
    draw_ammo(player.ammo)
    draw_hp(player.health)
    for zombie in zombies[:]:
        if zombie.hit and not zombie.alive:
            zombies.remove(zombie)
            zombies.append(generate_zombie())
        else:
            zombie.draw(screen)
    player.draw(screen)

    pygame.display.update()

pygame.quit()
