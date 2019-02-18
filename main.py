import pygame
import sys
import random
from datetime import datetime, timedelta

from pygame.rect import Rect

import os
import pygame
import config as c


all_sprites = pygame.sprite.Group()

blocks_sprites = pygame.sprite.Group()



from text_object import TextObject


special_effects = dict(
    long_paddle=((200,100,100),
                 "long",
                 "normal"),
    slow_ball=((50,200,200),
                 "slow",
                 "normal"),
    extra_life=((255, 215, 0),
                "add_life",
                None))

assert os.path.isfile('sound_effects/brick_hit.wav')


screen_width = 800
screen_height = 600
background_image = 'images/453.jpg'
horizontal_borders = pygame.sprite.Group()
vertical_borders = pygame.sprite.Group()
ball_sprite = pygame.sprite.Group()
player = pygame.sprite.Group()


def load_image(name, color_key=None):
    fullname = os.path.join('data', name)
    try:
        image = pygame.image.load(fullname)
    except pygame.error as message:
        print('Cannot load image:', name)
        raise SystemExit(message)

    if color_key is not None:
        if color_key == -1:
            color_key = image.get_at((0, 0))
        image.set_colorkey(color_key)
        image = image.convert_alpha()
    return image

class Particle(pygame.sprite.Sprite):
    fire = [load_image("star.png")]
    for scale in (3, 5, 10):
        fire.append(pygame.transform.scale(fire[0], (scale, scale)))

    def __init__(self, pos, dx, dy):
        super().__init__(all_sprites)
        self.time_life = 50
        self.image = random.choice(self.fire)
        self.rect = self.image.get_rect()

        self.velocity = [dx, dy]
        self.rect.x, self.rect.y = pos

    def draw(self, surface):
        if  self.time_life> 0 :
            r = surface.blit(self.image, (self.rect.x, self.rect.y))



    def update(self):
        self.time_life -=1

        self.rect.x += self.velocity[0]
        self.rect.y += self.velocity[1]
        if  self.time_life< 0 :
            self.kill()



def create_particles(position):
    particle_count = 10
    numbers = range(-5, 6)
    for _ in range(particle_count):
        Particle(position, random.choice(numbers), random.choice(numbers))

class Border(pygame.sprite.Sprite):
    def __init__(self, x1, y1, x2, y2):
        super().__init__(all_sprites)
        if x1 == x2:
            self.add(vertical_borders)
            self.image = pygame.Surface([1, y2 - y1])
            self.rect = pygame.Rect(x1, y1, 1, y2 - y1)
        else:
            self.add(horizontal_borders)
            self.image = pygame.Surface([x2 - x1, 1])
            self.rect = pygame.Rect(x1, y1, x2 - x1, 1)


class Ball(pygame.sprite.Sprite):
    def __init__(self, x, y, r, color, speed):
        super().__init__(all_sprites)
        self.add(ball_sprite)
        self.rect = Rect(x - r, y - r, r * 2, r * 2)
        self.image = pygame.Surface((2 * r, 2 * r), pygame.SRCALPHA, 32)
        self.radius = r
        self.diameter = r * 2
        self.color = color
        self.speed = speed
        self.center = (x,y)
        self.vx = random.randint(-3, 3)
        self.vy = random.randrange(-3, 3)

    def draw(self, surface):
        r = pygame.draw.circle(surface, self.color, self.rect.topleft, self.radius)

    def update(self):
        self.rect = self.rect.move(self.speed)
        x,y = self.speed
        if pygame.sprite.spritecollideany(self, horizontal_borders):
            self.speed = (x,-y)
        if pygame.sprite.spritecollideany(self, vertical_borders):
            self.speed = (-x,y)
        if pygame.sprite.spritecollideany(self, player):
            self.speed = (-x+ random.randint(-1,1),-y)






Border(1, 1, screen_width - 1, 1)

Border(1, 1, 1, screen_height - 1)

Border(screen_width - 1, 1, screen_width - 1, screen_height - 1)


class Brick(pygame.sprite.Sprite):
    def __init__(self, x, y, w, h, color,group,special_effect=None):

        super().__init__(all_sprites)
        blocks_sprites.add(self)
        self.rect = Rect(x, y, w, h)

        self.image = pygame.Surface([w,h])
        self.color = color
        self.special_effect = special_effect

    def draw(self, surface):
        pygame.draw.rect(surface, self.color, self.rect)






class Player(pygame.sprite.Sprite):
    def __init__(self, x, y, w, h, color, offset):

        super().__init__(all_sprites)
        player.add(self)

        self.rect = Rect(x, y, w, h)
        self.image = pygame.Surface([w,h])
        self.color = color
        self.offset = offset
        self.moving_left = False
        self.moving_right = False

    def draw(self, surface):
        pygame.draw.rect(surface, self.color, self.rect)


    def update(self):
        if self.moving_left:
            dx = -int((min(self.offset, self.rect.left)))
        elif self.moving_right:
            dx = int(min(self.offset, c.screen_width - self.rect.right))
        else:
            return

        self.rect = self.rect.move(dx, 0)


def load_image(name, color_key=None):
    fullname = os.path.join('data', name)
    try:
        image = pygame.image.load(fullname)
    except pygame.error as message:
        print('Cannot load image:', name)
        raise SystemExit(message)
    image = image.convert_alpha()

    if color_key is not None:
        if color_key is -1:
            color_key = image.get_at((0, 0))
        image.set_colorkey(color_key)
    return image


class Game:
    def __init__(self, caption="game", width=screen_width, height=screen_height, frame_rate=50):
        self.background_image = pygame.image.load(background_image)
        self.frame_rate = frame_rate
        self.game_over = False
        self.objects = []
        pygame.mixer.pre_init(44100, 16, 2, 4096)
        pygame.init()
        pygame.font.init()
        self.surface = pygame.display.set_mode((width, height))
        pygame.display.set_caption(caption)
        self.clock = pygame.time.Clock()
        self.mouse_handlers = []
        self.sound_effects = {name: pygame.mixer.Sound(sound) for name, sound in c.sounds_effects.items()}
        self.reset_effect = None
        self.effect_start_time = None
        self.score = 0
        self.lives = 3
        self.start_level = False
        self.player = None
        self.bricks = None
        self.ball = None
        self.menu_buttons = []
        self.is_game_running = False
        self.create_objects()
        self.points_per_brick = 1



    def draw(self):
        for o in self.objects:
            o.draw(self.surface)

    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_LEFT:

                    self.player.moving_left = True
                    self.player.moving_right = False
                elif event.key == pygame.K_RIGHT:
                    self.player.moving_left = False
                    self.player.moving_right = True
            elif event.type == pygame.KEYUP:
                if event.key == pygame.K_LEFT:
                    self.player.moving_left = False
                    self.player.moving_right = False
                elif event.key == pygame.K_RIGHT:
                    self.player.moving_left = False
                    self.player.moving_right = False

    def run(self):
        while not self.game_over:
            self.surface.blit(self.background_image, (0, 0))

            self.handle_events()
            all_sprites.update()
            self.update()

            for o in self.objects:
                o.draw(self.surface)

            pygame.display.update()
            self.clock.tick(self.frame_rate)



    def set_points_per_brick(self, points):
        self.points_per_brick = points



    def new_game(self):
        self.is_game_running = True
        self.start_level = True

    def end_game(self):
        self.is_game_running = False
        self.game_over = True

    def create_menu(self):

        intro_text = ["Начать игру"]

        fon = pygame.transform.scale(load_image('123.jpg'), (screen_width, screen_height))
        self.surface.blit(fon, (0, 0))
        font = pygame.font.Font(None, 30)
        text_coord = 50
        for line in intro_text:
            string_rendered = font.render(line, 1, pygame.Color('white'))
            intro_rect = string_rendered.get_rect()
            text_coord += 10
            intro_rect.top = text_coord
            intro_rect.x = 10
            text_coord += intro_rect.height
            self.surface.blit(string_rendered, intro_rect)

        while True:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.end_game()
                elif event.type == pygame.KEYDOWN or event.type == pygame.MOUSEBUTTONDOWN:
                    self.new_game()
                    return
            pygame.display.flip()


    def create_objects(self):
        self.create_bricks()
        self.create_player()
        self.create_ball()
        self.create_labels()
        self.create_menu()

    def create_labels(self):
        self.score_label = TextObject(c.score_offset,
                                      c.status_offset_y,
                                      lambda: f'SCORE: {self.score}',
                                      c.text_color,
                                      c.font_name,
                                      c.font_size)
        self.objects.append(self.score_label)
        self.lives_label = TextObject(c.lives_offset,
                                      c.status_offset_y,
                                      lambda: f'LIVES: {self.lives}',
                                      c.text_color,
                                      c.font_name,
                                      c.font_size)
        self.objects.append(self.lives_label)

    def create_ball(self):
        speed = (random.randint(-2, 2), c.ball_speed)
        self.ball = Ball(c.screen_width // 2,
                         c.screen_height // 2,
                         c.ball_radius,
                         c.ball_color,
                         speed)
        self.objects.append(self.ball)

    def create_player(self):
        player = Player((screen_width - 100) // 2,
                        screen_height - 10 * 2,
                        100,
                        10,
                        (240, 248, 255),
                       5)

        self.player = player
        self.objects.append(self.player)

    def create_bricks(self):
        w = 60
        h = 20
        brick_count = screen_width // (w + 1)
        offset_x = (screen_width - brick_count * (w + 1)) // 2
        row_count = 6
        bricks = []
        for row in range(row_count):
            for col in range(brick_count):
                index = random.randint(0,2)
                brick_color, start_effect, reset_effect = list(special_effects.values())[index]
                brick = Brick(offset_x + col * (w + 1),
                              c.offset_y + row * (h + 1),
                              w,
                              h,
                              brick_color,

                              (start_effect, reset_effect))
                bricks.append(brick)
                self.objects.append(brick)
        self.bricks = bricks

    def handle_ball_collisions(self):

        def intersect(obj, ball):
            edges = dict(left=Rect(obj.left, obj.top, 1, obj.height),
                         right=Rect(obj.right, obj.top, 1, obj.height),
                         top=Rect(obj.left, obj.top, obj.width, 1),
                         bottom=Rect(obj.left, obj.bottom, obj.width, 1))
            collisions = set(edge for edge, rect in edges.items() if ball.rect.colliderect(rect))

            if not collisions:
                return None

            if len(collisions) == 1:
                return list(collisions)[0]

            if 'top' in collisions:
                if ball.rect.top >= obj.top:
                    return 'top'
                if ball.rect.left < obj.left:
                    return 'left'
                else:
                    return 'right'

            if 'bottom' in collisions:
                if ball.rect.top >= obj.bottom:
                    return 'bottom'
                if ball.rect.left < obj.left:
                    return 'left'
                else:
                    return 'right'


        s = self.ball.speed
        edge = intersect(self.player.rect, self.ball)
        if edge is not None:
            self.sound_effects['paddle_hit'].play()

        if self.ball.rect.top > c.screen_height:
            self.lives -= 1
            if self.lives == 0:
                self.game_over = True
            else:
                self.create_ball()

        if self.ball.rect.top < 0:
            self.ball.speed = (s[0], -s[1])

        if self.ball.rect.left < 0 or self.ball.rect.right > c.screen_width:
            self.ball.speed = (-s[0], s[1])

        for brick in self.bricks:
            edge = intersect(brick.rect, self.ball)
            if not edge:
                continue
            print(self.ball.rect.topleft)

            particle_count = 10
            numbers = range(-5, 6)
            for _ in range(particle_count):
                self.objects.append(Particle(self.ball.rect.topleft, random.choice(numbers), random.choice(numbers)))
            self.sound_effects['brick_hit'].play()
            self.bricks.remove(brick)
            self.objects.remove(brick)
            self.score += self.points_per_brick

            if edge in ('top', 'bottom'):
                self.ball.speed = (s[0], -s[1])
            else:
                self.ball.speed = (-s[0], s[1])




    def update(self):
        if not self.is_game_running:
            return

        if self.start_level:
            self.start_level = False
            self.show_message('ПРИГОТОВИТЬСЯ!')

        if not self.bricks:
            self.show_message('ПОБЕДА!!!')
            self.is_game_running = False
            self.game_over = True
            return


        if self.reset_effect:
            if datetime.now() - self.effect_start_time >= timedelta(seconds=c.effect_duration):
                self.reset_effect(self)
                self.reset_effect = None

        self.handle_ball_collisions()
        all_sprites.update()

        if self.game_over:
            self.show_message('КОНЕЦ ИГРЫ! СЧЕТ:'+str(self.score),10000)

    def show_message(self, text,time=500):


        fon = pygame.transform.scale(load_image('123.jpg'), (screen_width, screen_height))
        self.surface.blit(fon, (0, 0))
        font = pygame.font.Font(None, 30)
        text_coord = 50
        string_rendered = font.render(text, 1, pygame.Color('white'))
        intro_rect = string_rendered.get_rect()
        text_coord += 10
        intro_rect.top = text_coord
        intro_rect.x = 10
        text_coord += intro_rect.height
        self.surface.blit(string_rendered, intro_rect)
        for i in range(time):
            pygame.display.flip()

        return



game = Game()
game.run()