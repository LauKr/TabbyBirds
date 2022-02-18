import pygame
import neat
import time
import os
import random
import configparser
import InteractiveFlappies as interact  # InteractiveFlappies.py


pygame.font.init()
configParser = configparser.RawConfigParser()
configFilePath = os.path.join(os.path.dirname(__file__), 'game.cfg')
configParser.read(configFilePath)


# Game-Speed and difficulty in a sense
VELOCITY = configParser.getint("difficulty", "VELOCITY")
PIPE_DISTANCE = configParser.getint("difficulty", "PIPE_DISTANCE")
PIPE_GAP = configParser.getint("difficulty", "PIPE_GAP")


WIN_WIDTH = configParser.getint("window", "WIN_WIDTH")
WIN_HEIGHT = configParser.getint("window", "WIN_HEIGHT")


BIRD_IMGS = [pygame.transform.scale2x(pygame.image.load(os.path.join("imgs", "bird1.png"))),
             pygame.transform.scale2x(pygame.image.load(os.path.join("imgs", "bird2.png"))),
             pygame.transform.scale2x(pygame.image.load(os.path.join("imgs", "bird3.png")))]
PIPE_IMG = pygame.transform.scale2x(pygame.image.load(os.path.join("imgs", "pipe.png")))
BASE_IMG = pygame.transform.scale2x(pygame.image.load(os.path.join("imgs", "base.png")))
BG_IMG = pygame.transform.scale2x(pygame.image.load(os.path.join("imgs", "bg.png")))

STAT_FONT = pygame.font.SysFont(configParser.get("font", "FONT"), 50)


class Bird:
    IMGS = BIRD_IMGS
    MAX_ROTATION = 25
    ROT_VEL = 20
    ANIMATION_TIME = 5

    def __init__(self, x, y):
        """
        A bird with coordinates <x, y>.
        :param x:
        :param y:
        """
        self.x = x
        self.y = y
        self.tilt = 0
        self.tick_count = 0
        self.vel = 0
        self.height = self.y
        self.img_count = 0
        self.img = self.IMGS[0]

    def jump(self):
        self.vel = -10.5  # negative velocity as (0, 0) is the upper left corner of the window
        self.tick_count = 0
        self.height = self.y

    def move(self):
        self.tick_count += 1
        displacement = self.vel * self.tick_count + 1.5*self.tick_count**2
        if displacement >= 16:
            displacement = 16
        if displacement < 0:
            displacement -= 2
        self.y = self.y + displacement
        if displacement < 0 or self.y < self.height + 50:
            if self.tilt < self.MAX_ROTATION:
                self.tilt = self.MAX_ROTATION
        else:
            if self.tilt > -90:
                self.tilt -= self.ROT_VEL

    def draw(self, win):
        self.img_count += 1
        if self.img_count < self.ANIMATION_TIME:
            self.img = self.IMGS[0]
        elif self.img_count < 2 * self.ANIMATION_TIME:
            self.img = self.IMGS[1]
        elif self.img_count < 3*self.ANIMATION_TIME:
            self.img = self.IMGS[2]
        elif self.img_count < 4*self.ANIMATION_TIME:
            self.img = self.IMGS[1]
        elif self.img_count == 4*self.ANIMATION_TIME + 1:
            self.img = self.IMGS[0]
            self.img_count = 0

        if self.tilt <= -80:  # If the bird is diving don't flap
            self.img = self.IMGS[1]
            self.img_count = self.ANIMATION_TIME * 2

        rotated_image = pygame.transform.rotate(self.img, self.tilt)
        new_rectangle = rotated_image.get_rect(center=self.img.get_rect(topleft=(self.x, self.y)).center)
        win.blit(rotated_image, new_rectangle.topleft)

    def get_mask(self):
        return pygame.mask.from_surface(self.img)


class Pipe:
    VEL = VELOCITY

    def __init__(self, x, gap):
        """
        Pipe pair at position <x> with a y-gap of <gap>
        :param x:
        :param gap:
        """
        self.x = x
        self.height = 0
        self.gap = gap

        self.top = 0
        self.bottom = 0
        self.PIPE_TOP = pygame.transform.flip(PIPE_IMG, flip_x=False, flip_y=True)
        self.PIPE_BOTTOM = PIPE_IMG

        self.passed = False
        self.set_height()

    def set_height(self):
        self.height = random.randrange(40, 450)
        self.top = self.height - self.PIPE_TOP.get_height()
        self.bottom = self.height + self.gap

    def move(self):
        self.x -= self.VEL

    def draw(self, win):
        win.blit(self.PIPE_TOP, (self.x, self.top))
        win.blit(self.PIPE_BOTTOM, (self.x, self.bottom))

    def collide(self, bird) -> bool:
        bird_mask = bird.get_mask()
        top_mask = pygame.mask.from_surface(self.PIPE_TOP)
        bottom_mask = pygame.mask.from_surface(self.PIPE_BOTTOM)

        top_offset = (self.x - bird.x, self.top - round(bird.y))
        bottom_offset = (self.x - bird.x, self.bottom - round(bird.y))

        bottom_point = bird_mask.overlap(bottom_mask, bottom_offset)
        top_point = bird_mask.overlap(top_mask, top_offset)

        if bottom_point or top_point:
            return True
        return False


class Base:
    VEL = VELOCITY
    WIDTH = BASE_IMG.get_width()
    IMG = BASE_IMG

    def __init__(self, y):
        """
        Ground at y level <y>
        :param y:
        """
        self.y = y
        self.x1 = 0
        self.x2 = self.WIDTH

    def move(self):
        self.x1 -= self.VEL
        self.x2 -= self.VEL

        if self.x1 + self.WIDTH < 0:
            self.x1 = self.x2 + self.WIDTH
        if self.x2 + self.WIDTH < 0:
            self.x2 = self.x1 + self.WIDTH

    def draw(self, win):
        win.blit(self.IMG, (self.x1, self.y))
        win.blit(self.IMG, (self.x2, self.y))


def draw_window(win, bird, pipes, base, score):
    win.blit(BG_IMG, (0, 0))
    for pipe in pipes:
        pipe.draw(win)
    base.draw(win)
    bird.draw(win)
    text = STAT_FONT.render("Score: " + str(score), 1, (255, 255, 255))
    win.blit(text, (WIN_WIDTH - 10 - text.get_width(), 10))
    pygame.display.update()


def main(interactive: bool = True) -> None:
    global PIPE_GAP
    bird = Bird(230, 350)
    base = Base(730)
    pipes = []
    pygame.init()
    win = pygame.display.set_mode((WIN_WIDTH, WIN_HEIGHT))
    clock = pygame.time.Clock()
    if interactive:
        interact.begin_game(win)
        try:
            with open("game_variables.transfer", 'r') as f:
                lines = []
                for line in f:
                    lines.append(line)
            difficulty = lines[0][11]
            name = lines[1][5:-1]
            os.remove(os.path.join(os.path.dirname(__file__), "game_variables.transfer"))
            if difficulty == "1":
                PIPE_GAP = configParser.getint("difficulty", "PIPE_GAP_EASY")
            elif difficulty == "2":
                PIPE_GAP = configParser.getint("difficulty", "PIPE_GAP_HARD")
        except FileNotFoundError as err:
            print(err)
            raise FileNotFoundError
    run = True
    score = 0
    pipes.append(Pipe(700, PIPE_GAP))
    while run:
        clock.tick(30)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    bird.jump()
        bird.move()
        base.move()
        rem = []  # List with pipe objects to be removed
        add_pipe = False  # Has a pipe been passed and a new one has to be generated?
        for pipe in pipes:
            if pipe.collide(bird):
                run = False
            if pipe.x + pipe.PIPE_TOP.get_width() < 0:  # If pipe completely off screen
                rem.append(pipe)
            if not pipe.passed and pipe.x < bird.x:  # If bird passed the pipe...
                pipe.passed = True
                add_pipe = True  # ...add new pipe
            pipe.move()
        if add_pipe:
            score += 1
            pipes.append(Pipe(x=PIPE_DISTANCE, gap=PIPE_GAP))
        for r in rem:
            pipes.remove(r)
        if bird.y + bird.img.get_height() > 730:
            run = False
        draw_window(win, bird, pipes, base, score)
    if interactive:
        try:
            interact.end_game(win, score, name)
        except Exception:  # If name could not be imported; Should raise FileNotFoundError anyway
            interact.end_game(win, score, "Error")
    else:
        pygame.quit()
        quit()


if __name__ == '__main__':
    main()
