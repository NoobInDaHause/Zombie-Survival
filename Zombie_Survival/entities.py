import pygame
import random
import typing as t


class Bullet:
    def __init__(self, x: int, y: int, facing_left: bool):
        self.size = 40
        image = pygame.image.load("assets/images/Bullet.png").convert_alpha()
        self.image = pygame.transform.scale(image, (self.size, self.size))
        self.rect = self.image.get_rect(center=(x, y))
        self.speed = 10
        self.facing_left = facing_left

    def move(self):
        """Move the bullet in the direction the player is facing."""
        if self.facing_left:
            self.rect.x -= self.speed
        else:
            self.rect.x += self.speed

    def draw(self, surface: pygame.Surface):
        """Draw the bullet on the surface."""
        surface.blit(self.image, self.rect)

    def off_screen(self, screen_width: int):
        """Check if the bullet is off the screen."""
        return self.rect.x < 0 or self.rect.x > screen_width


class Player:
    def __init__(self, x: int, y: int, sounds: t.List[pygame.mixer.Sound]):
        self.size = 256
        self.rect = pygame.Rect(x, y, self.size, self.size)
        self.images: t.Dict[str, t.List[pygame.Surface]] = self.load_images()
        self.facing_left = False
        self.action_type = "idle"  # idle, shoot, hurt, dead, walk
        self.frame_index = 0
        self.image = self.images[self.action_type][self.frame_index]
        self.update_time = pygame.time.get_ticks()
        self.alive = True
        self.health = 100
        self.hit = False
        self.shooting = False
        self.walking = False
        self.bullets: t.List[Bullet] = []
        self.ammo = 8
        self.reloading = False
        self.sounds = sounds

    def load_images(self):
        image_dict = {
            "idle": [],
            "shoot": [],
            "hurt": [],
            "dead": [],
            "walk": [],
            "reload": [],
        }

        sheets = {
            "shoot": ("assets/images/player/Shoot.png", 12),
            "walk": ("assets/images/player/Walk.png", 8),
            "hurt": ("assets/images/player/Hurt.png", 2),
            "dead": ("assets/images/player/Dead.png", 4),
            "idle": ("assets/images/player/Idle.png", 6),
            "reload": ("assets/images/player/Reload.png", 12),
        }

        for action, (path, frame_count) in sheets.items():
            sheet = pygame.image.load(path).convert_alpha()
            sheet_width, sheet_height = sheet.get_size()
            frame_width = sheet_width // frame_count
            frame_height = sheet_height

            for i in range(frame_count):
                frame_rect = pygame.Rect(i * frame_width, 0, frame_width, frame_height)
                frame = sheet.subsurface(frame_rect)
                frame = pygame.transform.scale(frame, (self.size, self.size))
                image_dict[action].append(frame)

        return image_dict

    def move(self, screen_width: int, game_over: bool):
        SPEED = 3
        dx = 0
        self.walking = False
        self.attack_type = "idle"

        if not game_over:
            key = pygame.key.get_pressed()

            if self.shooting == False and self.reloading == False and self.hit == False:
                if key[pygame.K_a]:
                    dx = -SPEED
                    self.walking = True
                    self.facing_left = True
                if key[pygame.K_d]:
                    dx = SPEED
                    self.walking = True
                    self.facing_left = False

            if key[pygame.K_SPACE] and not self.shooting and self.ammo > 0:
                self.shoot()
            if key[pygame.K_r] and not self.reloading and self.ammo != 8:
                self.sounds[1].play()
                self.reloading = True

            if self.rect.left + dx < -64:
                dx = -self.rect.left - 64
            if self.rect.right + dx > screen_width + 64:
                dx = screen_width - self.rect.right + 64

            self.rect.x += dx

    def update(self):
        if self.health <= 0:
            self.health = 0
            self.alive = False
            self.update_action("dead")
        elif self.hit == True:
            self.update_action("hurt")
        elif self.shooting == True:
            self.update_action("shoot")
        elif self.reloading == True:
            self.update_action("reload")
        elif self.walking == True:
            self.update_action("walk")
        else:
            self.update_action("idle")

        animation_cooldown = 100
        self.image = self.images[self.action_type][self.frame_index]
        if pygame.time.get_ticks() - self.update_time > animation_cooldown:
            self.frame_index += 1
            self.update_time = pygame.time.get_ticks()
        if self.frame_index >= len(self.images[self.action_type]):
            if self.alive == False:
                self.frame_index = len(self.images[self.action_type]) - 1
            else:
                self.frame_index = 0
                if self.action_type == "shoot":
                    self.shooting = False
                if self.action_type == "reload":
                    self.reloading = False
                    self.ammo = 8
                if self.action_type == "hurt":
                    self.hit = False
                    self.shooting = False
                    self.health -= 20
                    self.sounds[2].play()

        self.bullets = [
            bullet for bullet in self.bullets if not bullet.off_screen(1280)
        ]

    def update_action(self, new_action: str):
        if new_action != self.action_type:
            self.action_type = new_action
            self.frame_index = 0
            self.update_time = pygame.time.get_ticks()

    def get_hitbox(self):
        return self.rect.inflate(-self.rect.width * 0.9, -self.rect.height * 0.9)

    def shoot(self):
        if not self.shooting:
            self.shooting = True
            self.ammo -= 1
            self.sounds[0].play()

            bullet = Bullet(
                self.rect.centerx + (30 if not self.facing_left else -30),
                self.rect.centery + 45,
                self.facing_left,
            )
            self.bullets.append(bullet)

    def draw(self, surface: pygame.Surface):
        img = pygame.transform.flip(self.image, self.facing_left, False)
        to_add = 50 if not self.facing_left else -50

        surface.blit(
            img,
            (self.rect.x + (to_add if self.action_type == "shoot" else 0), self.rect.y),
        )

        for bullet in self.bullets:
            bullet.move()
            bullet.draw(surface)


class Zombie:
    def __init__(self, x: int, y: int, facing_left: bool):
        self.size = 256
        self.rect = pygame.Rect(x, y, self.size, self.size)
        self.facing_left = facing_left
        self.frame_index = 0
        self.alive = True
        self.update_time = pygame.time.get_ticks()
        self.images: t.Dict[str, t.List[pygame.Surface]] = self.load_images()
        self.action_type = "walk"  # walk, dead
        self.image = self.images[self.action_type][self.frame_index]
        self.hit = False

    def load_images(self):
        image_dict = {"dead": [], "walk": [], "idle": []}

        sheets = {
            "walk": ("assets/images/zombie/Walk.png", 10),
            "dead": ("assets/images/zombie/Dead.png", 5),
            "idle": ("assets/images/zombie/Idle.png", 6),
        }

        for action, (path, frame_count) in sheets.items():
            sheet = pygame.image.load(path).convert_alpha()
            sheet_width, sheet_height = sheet.get_size()
            frame_width = sheet_width // frame_count
            frame_height = sheet_height

            for i in range(frame_count):
                frame_rect = pygame.Rect(i * frame_width, 0, frame_width, frame_height)
                frame = sheet.subsurface(frame_rect)
                frame = pygame.transform.scale(frame, (self.size, self.size))
                image_dict[action].append(frame)

        return image_dict

    def move(self, game_over: bool):
        if not game_over:
            SPEED = random.choice([0.5, 1, 1.5, 2])
            if not self.hit:
                if self.facing_left:
                    dx = -SPEED
                else:
                    dx = SPEED

                self.rect.x += dx

    def update(self, game_over: bool):
        if self.hit:
            self.update_action("dead")
        else:
            self.update_action("idle" if game_over else "walk")

        animation_cooldown = 100

        self.image = self.images[self.action_type][self.frame_index]

        if pygame.time.get_ticks() - self.update_time > animation_cooldown:
            self.frame_index += 1
            self.update_time = pygame.time.get_ticks()

        if self.frame_index >= len(self.images[self.action_type]):
            if self.action_type == "dead":
                self.alive = False
            else:
                self.frame_index = 0

    def update_action(self, new_action: str):
        if new_action != self.action_type:
            self.action_type = new_action
            self.frame_index = 0
            self.update_time = pygame.time.get_ticks()

    def get_hitbox(self):
        hitbox = self.rect.inflate(-self.rect.width * 0.8, -self.rect.height * 0.8)
        return hitbox

    def draw(self, surface: pygame.Surface):
        """Draw the current image."""
        img = pygame.transform.flip(self.image, self.facing_left, False)

        surface.blit(img, (self.rect.x, self.rect.y))
