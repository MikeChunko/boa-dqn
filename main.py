# Implementation of Snake in pygame
import pygame as pyg
import random


# Returns x, y coords of food
def gen_food(snake, size_x, size_y, screen_x, screen_y):
    # Generate new coords until one doesn't cause a collision
    while True:
        x, y = (
            random.randrange(size_x, screen_x - size_x, 10),
            random.randrange(size_y, screen_y - size_y, 10),
        )
        sentinel = True
        for old_x, old_y in snake:
            if sentinel and (old_x == x and old_y == y):
                sentinel = False
        if sentinel:
            break

    return x, y


pyg.init()
pyg.font.init()
font, endfont = pyg.font.SysFont("Arial", 10), pyg.font.SysFont("Arial", 20)
screen_x = screen_y = 300
screen = pyg.display.set_mode((screen_x, screen_y))
red, green, blue = (200, 0, 0), (0, 200, 0), (0, 0, 200)
size_x = size_y = 10
pyg.display.update()
pyg.display.set_caption("Boa")
clock = pyg.time.Clock()


def display(screen, snake, food_x, food_y):
    screen.fill((0, 0, 0))
    for x, y in snake:
        pyg.draw.rect(screen, green, [x, y, size_x, size_y])
    pyg.draw.rect(screen, red, [food_x, food_y, size_x, size_y])

    for i in range(0, screen_x, 10):  # Border
        pyg.draw.rect(screen, blue, [i, 0, size_x, size_y])
        pyg.draw.rect(screen, blue, [i, screen_y - size_y, size_x, size_y])
        pyg.draw.rect(screen, blue, [0, i, size_x, size_x])
        pyg.draw.rect(screen, blue, [screen_x - size_x, i, size_x, size_y])


# Return 3 tuples, each holding a boolean value in the order (Left, Right, Up, Down)
# First tuple says if there is a border adjacent to the snake head in that direction
# Second tuple says if there is a segment adjacent to the snake head in that direction
# Third tuple says if there is food in that direction
def get_features(snake, food_x, food_y):
    b_l = b_r = b_u = b_d = s_l = s_r = s_u = s_d = f_u = f_l = f_r = f_d = False
    x, y = snake[-1]

    # Border
    if x == size_x:
        b_l = True
    elif x == screen_x - (2 * size_x):
        b_r = True

    if y == size_y:
        b_u = True
    elif y == screen_y - (2 * size_y):
        b_d = True

    # Segments
    for x_, y_ in snake[:-1]:
        if x_ + size_x == x:
            s_l = True
        elif x_ - size_x == x:
            s_r = True

        if y_ + size_y == y:
            s_u = True
        elif y_ - size_y == y:
            s_d = True

    # Food
    if food_x > x:
        f_r = True
    elif food_x < x:
        f_l = True

    if food_y > y:
        f_d = True
    elif food_y < y:
        f_u = True

    return (b_l, b_r, b_u, b_d), (s_l, s_r, s_u, s_d), (f_l, f_r, f_u, f_d)


def run_game():
    # List containing all segments of the snake
    snake = [(screen_x // 2, screen_y // 2),
             (screen_x // 2, screen_y // 2 - size_y),
             (screen_x // 2, screen_y // 2 - (2 * size_y))]

    food_x, food_y = gen_food(snake, size_x, size_y, screen_x, screen_y)
    eaten = False
    score = 0
    gameover = False
    d_x, d_y = 0, -size_y

    # Main loop

    while not gameover:

        # Handle actions
        for event in pyg.event.get():
            if event.type == pyg.QUIT:
                pyg.quit()
                quit()
            # Movement keys
            if event.type == pyg.KEYDOWN:
                if (event.key == pyg.K_LEFT or event.key == pyg.K_a):
                    if d_x <= 0:
                        d_x, d_y = -size_x, 0
                elif (event.key == pyg.K_RIGHT or event.key == pyg.K_d):
                    if d_x >= 0:
                        d_x, d_y = size_x, 0
                elif (event.key == pyg.K_UP or event.key == pyg.K_w):
                    if d_y <= 0:
                        d_x, d_y = 0, -size_y
                elif (event.key == pyg.K_DOWN or event.key == pyg.K_s):
                    if d_y >= 0:
                        d_x, d_y = 0, size_y

        # New segment position
        x, y = snake[-1]
        new_x, new_y = x + d_x, y + d_y

        # Check collisions
        if new_x == food_x and new_y == food_y:  # Food
            eaten = True
        elif new_x == 0 or new_x == screen_x - size_x or new_y == 0 or new_y == screen_y - size_y:  # Border
            gameover = True
        if d_x != 0 or d_y != 0:
            for x, y in snake:  # Snake
                if new_x == x and new_y == y:
                    gameover = True

        snake.append((new_x, new_y))

        # Food is eaten
        if eaten:
            food_x, food_y = gen_food(snake, size_x, size_y, screen_x, screen_y)
            eaten = False
            score += 100
        else:
            if score > 0:
                score -= 1
            snake.pop(0)

        # Draw
        display(screen, snake, food_x, food_y)
        textsurface = font.render("Score: {}".format(score), False, (255, 255, 255))
        screen.blit(textsurface, (0, 0))

        pyg.display.update()
        clock.tick(15)

    return snake, score, (food_x, food_y)


if __name__ == "__main__":
    while True:
        snake, score, (food_x, food_y) = run_game()

        # Game over state
        sentinel = True
        while sentinel:
            for event in pyg.event.get():
                if event.type == pyg.QUIT:
                    pyg.quit()
                    quit()
                if event.type == pyg.KEYDOWN and event.key == pyg.K_r:
                    sentinel = False

            display(screen, snake, food_x, food_y)
            textsurface = endfont.render("Game Over! Score: {}".format(score), True, (255, 255, 255))
            screen.blit(textsurface, textsurface.get_rect(center=(screen_x // 2, screen_y // 2)))
            textsurface = endfont.render("Press R to restart", True, (255, 255, 255))
            screen.blit(textsurface, textsurface.get_rect(center=(screen_x // 2, screen_y // 2 + 20)))

            pyg.display.update()
            clock.tick(15)
