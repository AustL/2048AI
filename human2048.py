import numpy as np
import random
import pygame

SCREEN_SIZE = 500
TILE_SIZE = SCREEN_SIZE // 5
GAP = SCREEN_SIZE // 25
SCORE_HEIGHT = 100

BACKGROUND = (187, 173, 160)
COLOURS = {
    0: (205, 193, 180),
    2: (238, 228, 218),
    4: (242, 224, 200),
    8: (242, 177, 121),
    16: (245, 149, 99),
    32: (246, 124, 95),
    64: (246, 94, 59),
    128: (237, 207, 114),
    256: (237, 204, 97),
    512: (237, 200, 80),
    1024: (237, 197, 63),
    2048: (238, 194, 46)
}

pygame.init()

win = pygame.display.set_mode((SCREEN_SIZE, SCREEN_SIZE + SCORE_HEIGHT))
pygame.display.set_caption('2048')
clock = pygame.time.Clock()

font = pygame.font.Font('sourcesanspro.ttf', 60)


class Block:
    def __init__(self, value):
        self.value = value
        self.colour = COLOURS[value]

    def draw(self, x, y):
        pygame.draw.rect(win, self.colour, (x, y, TILE_SIZE, TILE_SIZE))
        if self.value != 0:
            text = font.render(str(self.value), 1, (120, 120, 120))
            win.blit(text, text.get_rect(center=(x + TILE_SIZE // 2, y + TILE_SIZE // 2)))

    def __add__(self, other):
        if self.value == other.value:
            return Block(self.value * 2)

    def __eq__(self, other):
        if self.value == other.value:
            return True
        return False


class Grid:
    def __init__(self):
        self.blocks = list([Block(0) for _ in range(4)] for _ in range(4))
        self.new_turn()
        self.score = 0

    def __gt__(self, other):
        if self.score > other.score:
            return True
        return False

    def new_turn(self):
        for _ in range(2):
            new_spawn(self.blocks)

    def draw(self):
        for i in range(4):
            for j in range(4):
                x = GAP + i * (TILE_SIZE + GAP)
                y = SCORE_HEIGHT + GAP + j * (TILE_SIZE + GAP)
                self.blocks[j][i].draw(x, y)

        text = font.render(str(self.score), 1, (50, 50, 50))

        win.blit(text, text.get_rect(center=(SCREEN_SIZE // 2, SCORE_HEIGHT // 2)))

    def shift(self):
        for row in self.blocks:
            for index, block in enumerate(row):
                if block.value == 0:
                    row.pop(index)
                    row.insert(0, Block(0))

        self.blocks = np.flip(self.blocks, 1).tolist()
        self.merge()
        self.blocks = np.flip(self.blocks, 1).tolist()

    def check_end(self):
        for row in self.blocks:
            for block in row:
                if block.value == 0:
                    return False

        arr = convert(self.blocks)

        for direction in range(4):
            arr = np.rot90(arr, direction).tolist()
            for row in arr:
                for index in range(len(row) - 1):
                    if row[index + 1] == row[index] and row[index] != 0:
                        row[index] = row[index] + row[index + 1]
                        row.pop(index + 1)
                        row.append(0)

            arr = np.rot90(arr, 4 - direction).tolist()

            if arr != convert(self.blocks):
                return False

        return True

    def merge(self):
        for row in self.blocks:
            for index in range(len(row) - 1):
                if row[index + 1] == row[index] and row[index].value != 0:
                    row[index] = row[index] + row[index + 1]
                    row.pop(index + 1)
                    row.append(Block(0))
                    self.score += row[index].value

    def move(self, direction):
        original = convert(self.blocks)

        if direction == 'right':
            self.shift()

        elif direction == 'left':
            self.blocks = np.flip(self.blocks, 1).tolist()

            self.shift()

            self.blocks = np.flip(self.blocks, 1).tolist()

        elif direction == 'down':
            self.blocks = np.rot90(self.blocks, 1).tolist()

            self.shift()

            self.blocks = np.rot90(self.blocks, 3).tolist()

        elif direction == 'up':
            self.blocks = np.rot90(self.blocks, 3).tolist()

            self.shift()

            self.blocks = np.rot90(self.blocks, 1).tolist()

        if original != convert(self.blocks):
            self.blocks = new_spawn(self.blocks)


def convert(arr):
    output = []
    for row in arr:
        output.append(list((map(lambda x: x.value, row))))
    return output


def new_spawn(arr):
    choices = np.argwhere(np.array(arr) == Block(0)).tolist()
    x, y = tuple(random.choice(choices))

    block = Block(2)

    if random.random() > 0.9:
        block = Block(4)

    arr[x][y] = block

    return arr


def draw(grid):
    win.fill(BACKGROUND)
    grid.draw()


def end(score):
    s = pygame.Surface((1000, 750), pygame.SRCALPHA)
    s.fill((255, 255, 255, 200))
    win.blit(s, (0, 0))

    text = font.render('Congratulations!', 1, (0, 0, 0))
    text2 = font.render('Your Score: {}'.format(score), 1, (0, 0, 0))

    win.blit(text, text.get_rect(center=(SCREEN_SIZE // 2, (SCREEN_SIZE + SCORE_HEIGHT) // 2 - 50)))
    win.blit(text2, text2.get_rect(center=(SCREEN_SIZE // 2, (SCREEN_SIZE + SCORE_HEIGHT) // 2 + 50)))

    pygame.display.update()

    play = True
    while play:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                play = False
                pygame.quit()

            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    play = False
                    main()


def main():
    grid = Grid()

    play = True
    while play:
        clock.tick(30)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                play = False
                pygame.quit()

            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_LEFT:
                    grid.move('left')
                elif event.key == pygame.K_RIGHT:
                    grid.move('right')
                elif event.key == pygame.K_UP:
                    grid.move('up')
                elif event.key == pygame.K_DOWN:
                    grid.move('down')

        if play:
            draw(grid)
            pygame.display.update()

            if grid.check_end():
                end(grid.score)


main()
