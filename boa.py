# Implementation of Snake in pygame
import numpy as np
import pygame as pyg
from boa_nn import Agent
from random import randrange, randint
from keras.utils import to_categorical


def define_parameters():
    params = dict()
    params["epsilon_decay_linear"] = 1/75
    params["learning_rate"] = 0.0005
    params["first_layer_size"] = 15
    params["second_layer_size"] = 15
    params["third_layer_size"] = 15
    params["episodes"] = 150
    params["memory_size"] = 2500
    params["batch_size"] = 500
    params["weights_path"] = "weights.hdf5"
    params["train"] = True
    return params


class Boa:
    def __init__(self, screen_x = 300, screen_y = 300):
        self.font, self.endfont = pyg.font.SysFont("Arial", 10), pyg.font.SysFont("Arial", 20)
        self.screen_x, self.screen_y = screen_x, screen_y
        self.screen = pyg.display.set_mode((self.screen_x, self.screen_y))
        self.red, self.green, self.blue = (200, 0, 0), (0, 200, 0), (0, 0, 200)
        self.size_x = self.size_y = 10
        pyg.display.update()
        pyg.display.set_caption("Boa")
        self.clock = pyg.time.Clock()

        # List containing all segments of the snake
        self.snake = [(screen_x // 2, screen_y // 2)]

        self.gen_food()
        self.eaten = False
        self.score = 0
        self.gameover = False
        self.d_x, self.d_y = 0, -self.size_y
        self.dir = 2  # 0 for left, 1 for right, 2 for up, 3 for down
        self.delta_score = 0


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


    # Return an int and two tuples
    # The int is the snake's direction
    # The first holds boolean values for whether or not there is immediate danger to the left, forward, and right
    # The second holds boolean values for whether or not there is food to the left, forward, and right
    def get_features(self):
        b_l = b_r = b_u = b_d = f_u = f_l = f_r = f_d = 0
        danger_forward = danger_left = danger_right = 0
        food_forward = food_left = food_right = food_behind = 0
        dir_left = dir_right = dir_up = dir_down = 0
        x, y = self.snake[-1]

        # Border
        if x == self.size_x:
            b_l = 1
        elif x == self.screen_x - (2 * self.size_x):
            b_r = 1

        if y == self.size_y:
            b_u = 1
        elif y == self.screen_y - (2 * self.size_y):
            b_d = 1

        # Segments
        for x_, y_ in self.snake[:-1]:
            if x_ + self.size_x == x:
                b_l = 1
            elif x_ - self.size_x == x:
                b_r = 1

            if y_ + self.size_y == y:
                b_u = 1
            elif y_ - self.size_y == y:
                b_d = 1

        # Food
        if self.food_x > x:
            f_r = 1
        elif self.food_x < x:
            f_l = 1

        if self.food_y > y:
            f_d = 1
        elif self.food_y < y:
            f_u = 1

        # Change to left/forward/right
        if self.dir == 0:
            danger_left, danger_forward, danger_right = b_d, b_l, b_u
            food_left, food_forward, food_right, food_behind = f_d, f_l, f_u, f_r
            dir_left = 1
        elif self.dir == 1:
            danger_left, danger_forward, danger_right = b_u, b_r, b_d
            food_left, food_forward, food_right, food_behind = f_u, f_r, f_d, f_l
            dir_right = 1
        elif self.dir == 2:
            danger_left, danger_forward, danger_right = b_l, b_u, b_r
            food_left, food_forward, food_right, food_behind = f_l, f_u, f_r, f_d
            dir_up = 1
        else:
            danger_left, danger_forward, danger_right = b_r, b_d, b_l
            food_left, food_forward, food_right, food_behind = f_r, f_d, f_l, f_u
            dir_down = 1

        return [danger_forward, danger_right, danger_left, dir_left, dir_right, dir_up, dir_down, food_forward, food_left, food_right, food_behind]


    def process_manual_input(self, input):
        if input == 1:  # Forward
            self.process_input(self.dir)
        elif input == 0:  # Left
            if self.dir <= 1:
                self.process_input(3 - self.dir)
            else:
                self.process_input(self.dir - 2)
        else:  # Right
            if self.dir <= 1:
                self.process_input(self.dir + 2)
            else:
                self.process_input(3 - self.dir)


    def process_input(self, input):
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
    def step(self, tick=15, input=1):
        # Handle actions
        self.process_manual_input(input)
        self.delta_score = 0

        # New segment position
        x, y = self.snake[-1]
        new_x, new_y = x + self.d_x, y + self.d_y

        # Check collisions
        if new_x == self.food_x and new_y == self.food_y:  # Food
            self.eaten = True
        elif new_x == 0 or new_x == self.screen_x - self.size_x or new_y == 0 or new_y == self.screen_y - self.size_y:  # Border
            self.gameover = True
            self.delta_score -= 10
        if self.d_x != 0 or self.d_y != 0:
            for x, y in self.snake:  # Snake
                if new_x == x and new_y == y:
                    self.gameover = True
                    self.delta_score -= 10

        self.snake.append((new_x, new_y))

        # Food is eaten
        if self.eaten:
            self.gen_food()
            self.eaten = False
            self.delta_score += 10
        else:
            self.snake.pop(0)

        self.score += self.delta_score

        # Draw
        self.display()
        textsurface = self.font.render("Score: {}".format(self.score), False, (255, 255, 255))
        self.screen.blit(textsurface, (0, 0))

        pyg.display.update()
        self.clock.tick(tick)


if __name__ == "__main__":
    pyg.init()
    pyg.font.init()
    tick = 4000
    params = define_parameters()
    num_games = 0
    agent = Agent(params)

    while num_games < params["episodes"]:
        game = Boa()
        num_steps = 0
        max_steps = 1000  # Prevent infinite looping with the game

        while not game.gameover and num_steps < max_steps:
            if not params["train"]:
                agent.epsilon = 0
            else:
                # Epsilon determines randomness factor
                agent.epsilon = 1 - (num_games * params["epsilon_decay_linear"])

            num_steps += 1
            state_old = np.asarray(game.get_features())

            if randint(0, 1) < agent.epsilon:  # Random action
                final_input = randint(0, 2)
                final_move = to_categorical(randint(0, 2), num_classes=3)
            else:  # Predict action based on nn
                prediction = agent.model.predict(state_old.reshape((1, 11)))
                final_move = to_categorical(np.argmax(prediction[0]), num_classes=3)

                if np.array_equal(final_move, [1, 0, 0]):
                    final_input = 1
                if np.array_equal(final_move, [0, 1, 0]):
                    final_input = 2
                else:
                    final_input = 0

            game.step(tick=tick, input=final_input)
            state_new = np.asarray(game.get_features())
            reward = game.delta_score

            if reward > 0:
                max_steps += 500

            if params["train"]:
                # Train short memory based on the new action and state
                agent.train_short_memory(state_old, final_move, reward, state_new, game.gameover)
                # Store into long term memory
                agent.remember(state_old, final_move, reward, state_new, game.gameover)

        num_games += 1
        print("Game: {}, Score: {}".format(num_games, game.score))

        if params["train"]:
            agent.replay_new(params["batch_size"])

    # Save the calculated weights for later use
    if params["train"]:
        agent.model.save_weights(params["weights_path"])
