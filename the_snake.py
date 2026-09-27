import sys
from random import randint

import pygame as pg

SCREEN_WIDTH, SCREEN_HEIGHT = 640, 480
GRID_SIZE = 20
GRID_WIDTH = SCREEN_WIDTH // GRID_SIZE
GRID_HEIGHT = SCREEN_HEIGHT // GRID_SIZE

UP = (0, -1)
DOWN = (0, 1)
LEFT = (-1, 0)
RIGHT = (1, 0)

# Вынес цвета в отдельные константы, чтобы было проще их менять.
BLACK = (0, 0, 0)
CYAN = (93, 216, 228)
RED = (255, 0, 0)
GREEN = (0, 255, 0)

BOARD_BACKGROUND_COLOR = BLACK
BORDER_COLOR = CYAN
APPLE_COLOR = RED
SNAKE_COLOR = GREEN

SPEED = 20

# Начальные позиции вынес в отдельные константы,
# чтобы не дублировать координаты в коде.
DEFAULT_POSITION = (0, 0)
INITIAL_SNAKE_POSITION = (
    SCREEN_WIDTH // 2,
    SCREEN_HEIGHT // 2
)

# Вынес направления в словарь, чтобы не создавать его
# каждый раз при обработке нажатия клавиш.
DIRECTIONS = {
    pg.K_UP: UP,
    pg.K_DOWN: DOWN,
    pg.K_LEFT: LEFT,
    pg.K_RIGHT: RIGHT,
}

# Сохраняю противоположные направления отдельно,
# чтобы не разрешать змейке сразу разворачиваться.
OPPOSITE_DIRECTIONS = {
    UP: DOWN,
    DOWN: UP,
    LEFT: RIGHT,
    RIGHT: LEFT,
}

screen = pg.display.set_mode(
    (SCREEN_WIDTH, SCREEN_HEIGHT),
    0,
    32
)
pg.display.set_caption('Змейка')
clock = pg.time.Clock()


class GameObject:
    """Базовый класс игрового объекта."""

    def __init__(
        self,
        position=DEFAULT_POSITION,
        body_color=None
    ):
        self.position = position
        self.body_color = body_color

    def draw(self):
        """Метод для отрисовки игрового объекта."""
        raise NotImplementedError

    def draw_cell(self, position, color=None):
        """Отрисовывает одну клетку игрового объекта."""
        # Вынес общую отрисовку клетки сюда,
        # чтобы не повторять один и тот же код
        # в Apple и Snake.
        if color is None:
            color = self.body_color

        rect = pg.Rect(
            position,
            (GRID_SIZE, GRID_SIZE)
        )
        pg.draw.rect(screen, color, rect)
        pg.draw.rect(
            screen,
            BORDER_COLOR,
            rect,
            1
        )


class Apple(GameObject):
    """Класс яблока."""

    def __init__(self, occupied_positions=()):
        super().__init__(body_color=APPLE_COLOR)

        # Передаю позиции змейки, чтобы яблоко
        # не появилось внутри неё.
        self.randomize_position(occupied_positions)

    def randomize_position(self, occupied_positions=()):
        """Выбирает свободную позицию для яблока."""
        while True:
            position = (
                randint(0, GRID_WIDTH - 1) * GRID_SIZE,
                randint(0, GRID_HEIGHT - 1) * GRID_SIZE
            )

            # Проверяю, что выбранная клетка свободна.
            if position not in occupied_positions:
                self.position = position
                return

    def draw(self):
        """Отрисовывает яблоко."""
        self.draw_cell(self.position)


class Snake(GameObject):
    """Класс змейки."""

    def __init__(
        self,
        position=INITIAL_SNAKE_POSITION,
        body_color=SNAKE_COLOR
    ):
        # Оставляю возможность изменить позицию
        # и цвет при создании змейки.
        super().__init__(
            position=position,
            body_color=body_color
        )

        self.length = 1
        self.positions = [position]
        self.direction = RIGHT
        self.last = None

    def get_head_position(self):
        """Возвращает позицию головы змейки."""
        return self.positions[0]

    def move(self):
        """Перемещает змейку на одну клетку."""
        head_x, head_y = self.get_head_position()
        direction_x, direction_y = self.direction

        new_head = (
            (
                head_x + direction_x * GRID_SIZE
            ) % SCREEN_WIDTH,
            (
                head_y + direction_y * GRID_SIZE
            ) % SCREEN_HEIGHT
        )

        self.positions.insert(0, new_head)
        self.position = new_head

        # Удаляю хвост, если сегментов стало больше,
        # чем должна иметь змейка.
        if len(self.positions) > self.length:
            self.last = self.positions.pop()
        else:
            self.last = None

    def reset(self):
        """Возвращает змейку в начальное состояние."""
        # Возвращаю змейку в начальное положение.
        self.position = INITIAL_SNAKE_POSITION
        self.length = 1
        self.positions = [INITIAL_SNAKE_POSITION]
        self.direction = RIGHT
        self.last = None

    def update_direction(self, new_direction):
        """Изменяет направление движения змейки."""
        # Не позволяю змейке сразу развернуться
        # в обратную сторону.
        if new_direction != OPPOSITE_DIRECTIONS[self.direction]:
            self.direction = new_direction

    def draw(self):
        """Отрисовывает голову змейки и очищает хвост."""
        # При обычном движении мне достаточно очистить
        # старый хвост и нарисовать новую голову.
        if self.last:
            self.draw_cell(
                self.last,
                BOARD_BACKGROUND_COLOR
            )

        self.draw_cell(self.get_head_position())


def handle_keys(game_object):
    """Обрабатывает нажатия клавиш."""
    for event in pg.event.get():
        if event.type == pg.QUIT:
            # Корректно завершаю работу программы.
            pg.quit()
            sys.exit()

        if event.type != pg.KEYDOWN:
            continue

        if event.key == pg.K_ESCAPE:
            # Добавляю возможность закрыть игру клавишей Esc.
            pg.quit()
            sys.exit()

        if event.key in DIRECTIONS:
            game_object.update_direction(
                DIRECTIONS[event.key]
            )


def main():
    """Запускает основной игровой цикл."""
    pg.init()

    snake = Snake()

    # Передаю позиции змейки, чтобы яблоко сразу
    # появилось в свободной клетке.
    apple = Apple(snake.positions)

    while True:
        clock.tick(SPEED)

        handle_keys(snake)
        snake.move()

        if snake.get_head_position() == apple.position:
            snake.length += 1

            # После съедания яблока выбираю новую
            # свободную клетку.
            apple.randomize_position(snake.positions)

        elif snake.get_head_position() in snake.positions[4:]:
            # При столкновении возвращаю змейку
            # в начальное состояние.
            snake.reset()

            # После сброса снова выбираю свободное
            # место для яблока.
            apple.randomize_position(snake.positions)

            screen.fill(BOARD_BACKGROUND_COLOR)

        apple.draw()
        snake.draw()

        pg.display.update()


if __name__ == '__main__':
    main()
