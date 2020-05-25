# Implementation of Snake in pygame
import pygame as pyg
from random import randrange


class Boa:
    def __init__(self, screen_x = 300, screen_y = 300):
        pyg.init()
        pyg.font.init()
        self.font, self.endfont = pyg.font.SysFont("Arial", 10), pyg.font.SysFont("Arial", 20)
        self.screen_x, self.screen_y = screen_x, screen_y
        self.screen = pyg.display.set_mode((self.screen_x, self.screen_y))
        self.red, self.green, self.blue = (200, 0, 0), (0, 200, 0), (0, 0, 200)
        self.size_x = self.size_y = 10
        pyg.display.update()
        pyg.display.set_caption("Boa")
        self.clock = pyg.time.Clock()

        # List containing all segments of the snake
        self.snake = [(screen_x // 2, screen_y // 2),
                      (screen_x // 2, screen_y // 2 - self.size_y),
                      (screen_x // 2, screen_y // 2 - (2 * self.size_y))]

        self.gen_food()
        self.eaten = False
        self.score = 0
        self.gameover = False
        self.d_x, self.d_y = 0, -self.size_y
        self.dir = 2  # 0 for left, 1 for right, 2 for up, 3 for down


    def gen_food(self):
        # Generate new coords until one doesn't cause a collision
        while True:
            x, y = (
                randrange(self.size_x, self.screen_x - self.size_x, 10),
                randrange(self.size_y, self.screen_y - self.size_y, 10),
            )
            sentinel = True
            for old_x, old_y in self.snake:
                if sentinel and (old_x == x and old_y == y):
                    sentinel = False
            if sentinel:
                break

        self.food_x, self.food_y = x, y


    def display(self):
        self.screen.fill((0, 0, 0))
        for x, y in self.snake:
            pyg.draw.rect(self.screen, self.green, [x, y, self.size_x, self.size_y])
        pyg.draw.rect(self.screen, self.red, [self.food_x, self.food_y, self.size_x, self.size_y])

        for i in range(0, self.screen_x, 10):  # Border
            pyg.draw.rect(self.screen, self.blue, [i, 0, self.size_x, self.size_y])
            pyg.draw.rect(self.screen, self.blue, [i, self.screen_y - self.size_y, self.size_x, self.size_y])
            pyg.draw.rect(self.screen, self.blue, [0, i, self.size_x, self.size_x])
            pyg.draw.rect(self.screen, self.blue, [self.screen_x - self.size_x, i, self.size_x, self.size_y])


    # Return two tuples
    # The first holds boolean values for whether or not there is immediate danger to the left, forward, and right
    # The second holds boolean values for whether or not there is food to the left, forward, and right
    def get_features(self):
        b_l = b_r = b_u = b_d = f_u = f_l = f_r = f_d = False
        danger_forward = danger_left = danger_right = False
        food_forward = food_left = food_right = False
        x, y = self.snake[-1]

        # Border
        if x == self.size_x:
            b_l = True
        elif x == self.screen_x - (2 * self.size_x):
            b_r = True

        if y == self.size_y:
            b_u = True
        elif y == self.screen_y - (2 * self.size_y):
            b_d = True

        # Segments
        for x_, y_ in self.snake[:-1]:
            if x_ + self.size_x == x:
                b_l = True
            elif x_ - self.size_x == x:
                b_r = True

            if y_ + self.size_y == y:
                b_u = True
            elif y_ - self.size_y == y:
                b_d = True

        # Food
        if self.food_x > x:
            f_r = True
        elif self.food_x < x:
            f_l = True

        if self.food_y > y:
            f_d = True
        elif self.food_y < y:
            f_u = True

        # Change to left/forward/right
        if self.dir == 0:
            danger_left, danger_forward, danger_right = b_d, b_l, b_u
            food_left, food_forward, food_right = f_d, f_l, f_u
        elif self.dir == 1:
            danger_left, danger_forward, danger_right = b_u, b_r, b_d
            food_left, food_forward, food_right = f_u, f_r, f_d
        elif self.dir == 2:
            danger_left, danger_forward, danger_right = b_l, b_u, b_r
            food_left, food_forward, food_right = f_l, f_u, f_r
        else:
            danger_left, danger_forward, danger_right = b_r, b_d, b_l
            food_left, food_forward, food_right = f_r, f_d, f_l

        return (danger_left, danger_forward, danger_right), (food_left, food_forward, food_right)


    def get_keyboard_input(self):
        for event in pyg.event.get():
            if event.type == pyg.QUIT:
                pyg.quit()
                quit()
            # Movement keys
            if event.type == pyg.KEYDOWN:
                if (event.key == pyg.K_LEFT or event.key == pyg.K_a):
                    self.get_input(0)
                elif (event.key == pyg.K_RIGHT or event.key == pyg.K_d):
                    self.get_input(1)
                elif (event.key == pyg.K_UP or event.key == pyg.K_w):
                    self.get_input(2)
                elif (event.key == pyg.K_DOWN or event.key == pyg.K_s):
                    self.get_input(3)


    def get_manual_input(self, input):
        if input == 1:  # Forward
            self.get_input(self.dir)
        elif input == 0:  # Left
            if self.dir <= 1:
                self.get_input(3 - self.dir)
            else:
                self.get_input(self.dir - 2)
        else:  # Right
            if self.dir <= 1:
                self.get_input(self.dir + 2)
            else:
                self.get_input(3 - self.dir)


    def get_input(self, input):
        if input == 0 and self.d_x <= 0:  # Left
            self.d_x, self.d_y = -self.size_x, 0
            self.dir = 0
        elif input == 1 and self.d_x >= 0:  # Right
            self.d_x, self.d_y = self.size_x, 0
            self.dir = 1
        elif input == 2 and self.d_y <= 0:  # Up
            self.d_x, self.d_y = 0, -self.size_y
            self.dir = 2
        elif input == 3 and self.d_y >= 0:  # Down
            self.d_x, self.d_y = 0, self.size_y
            self.dir = 3


    # input: -1 for keyboard input, 0 for left, 1 for forward, 2 for right
    # difficulty: 0 for no score decrease from moving, 1 for yes
    def step(self, tick=15, input=-1, difficulty=0):
        # Handle actions
        if input == -1:
            self.get_keyboard_input()
        else:
            self.get_manual_input(input)

        # New segment position
        x, y = self.snake[-1]
        new_x, new_y = x + self.d_x, y + self.d_y

        # Check collisions
        if new_x == self.food_x and new_y == self.food_y:  # Food
            self.eaten = True
        elif new_x == 0 or new_x == self.screen_x - self.size_x or new_y == 0 or new_y == self.screen_y - self.size_y:  # Border
            self.gameover = True
        if self.d_x != 0 or self.d_y != 0:
            for x, y in self.snake:  # Snake
                if new_x == x and new_y == y:
                    self.gameover = True

        self.snake.append((new_x, new_y))

        # Food is eaten
        if self.eaten:
            self.gen_food()
            self.eaten = False
            self.score += 100
        else:
            if difficulty == True and self.score > 0:
                self.score -= 1
            self.snake.pop(0)

        # Draw
        self.display()
        textsurface = self.font.render("Score: {}".format(self.score), False, (255, 255, 255))
        self.screen.blit(textsurface, (0, 0))

        print(self.get_features())

        pyg.display.update()
        self.clock.tick(tick)


if __name__ == "__main__":
    tick = .5
    while True:
        game = Boa()
        while not game.gameover:
            game.step(tick=tick, input=-1)

        # Game over state
        sentinel = True
        while sentinel:
            for event in pyg.event.get():
                if event.type == pyg.QUIT:
                    pyg.quit()
                    quit()
                if event.type == pyg.KEYDOWN and event.key == pyg.K_r:
                    sentinel = False

            game.display()
            textsurface = game.endfont.render("Game Over! Score: {}".format(game.score), True, (255, 255, 255))
            game.screen.blit(textsurface, textsurface.get_rect(center=(game.screen_x // 2, game.screen_y // 2)))
            textsurface = game.endfont.render("Press R to restart", True, (255, 255, 255))
            game.screen.blit(textsurface, textsurface.get_rect(center=(game.screen_x // 2, game.screen_y // 2 + 20)))


            pyg.display.update()
            game.clock.tick(tick)
