from random import randint

import pygame

# Константы для размеров поля и сетки:
SCREEN_WIDTH, SCREEN_HEIGHT = 640, 480
GRID_SIZE = 20
GRID_WIDTH = SCREEN_WIDTH // GRID_SIZE
GRID_HEIGHT = SCREEN_HEIGHT // GRID_SIZE

# Направления движения:
UP = (0, -1)
DOWN = (0, 1)
LEFT = (-1, 0)
RIGHT = (1, 0)

# Цвет фона - черный:
BOARD_BACKGROUND_COLOR = (0, 0, 0)

# Цвет границы ячейки
BORDER_COLOR = (93, 216, 228)

# Цвет яблока
APPLE_COLOR = (255, 0, 0)

# Цвет змейки
SNAKE_COLOR = (0, 255, 0)

# Скорость движения змейки:
SPEED = 20

# Настройка игрового окна:
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT), 0, 32)

# Заголовок окна игрового поля:
pygame.display.set_caption('Змейка')

# Настройка времени:
clock = pygame.time.Clock()


# Тут опишите все классы игры.
class GameObject:
    """Базовый класс для игровых объектов."""

    def __init__(self, position=(0, 0), body_color=None):
        self.position = position
        self.body_color = body_color

    def draw(self):
        """Метод для отрисовки игрового объекта."""
        pass


class Apple(GameObject):
    """Класс, описывающий яблоко на игровом поле."""

    def __init__(self):
        super().__init__(
            position=(0, 0),
            body_color=APPLE_COLOR
        )
        self.randomize_position()

    def randomize_position(self):
        """Устанавливает яблоку случайную позицию на игровом поле."""
        self.position = (
            randint(0, GRID_WIDTH - 1) * GRID_SIZE,
            randint(0, GRID_HEIGHT - 1) * GRID_SIZE
        )

    def draw(self):
        """Отрисовывает яблоко на игровом поле."""
        rect = pygame.Rect(
            self.position,
            (GRID_SIZE, GRID_SIZE)
        )
        pygame.draw.rect(screen, self.body_color, rect)
        pygame.draw.rect(screen, BORDER_COLOR, rect, 1)


class Snake(GameObject):
    """Класс, описывающий змейку."""

    def __init__(self):
        position = (SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2)

        super().__init__(
            position=position,
            body_color=SNAKE_COLOR
        )

        self.length = 1
        self.positions = [position]
        self.direction = RIGHT
        self.next_direction = None
        self.last = None

    def get_head_position(self):
        """Возвращает координаты головы змейки."""
        return self.positions[0]

    def move(self):
        """Перемещает змейку на одну клетку."""
        head_x, head_y = self.get_head_position()
        direction_x, direction_y = self.direction

        new_head = (
            (head_x + direction_x * GRID_SIZE) % SCREEN_WIDTH,
            (head_y + direction_y * GRID_SIZE) % SCREEN_HEIGHT
        )

        self.positions.insert(0, new_head)

        if len(self.positions) > self.length:
            self.last = self.positions.pop()
        else:
            self.last = None

    def reset(self):
        """Сбрасывает змейку в начальное состояние."""
        position = (SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2)

        self.length = 1
        self.positions = [position]
        self.direction = RIGHT
        self.next_direction = None
        self.last = None

    def update_direction(self):
        """Обновляет направление движения змейки."""
        if self.next_direction:
            self.direction = self.next_direction
            self.next_direction = None

    def draw(self):
        """Отрисовывает змейку на игровом поле."""
        for position in self.positions:
            rect = pygame.Rect(
                position,
                (GRID_SIZE, GRID_SIZE)
            )
            pygame.draw.rect(
                screen,
                self.body_color,
                rect
            )
            pygame.draw.rect(
                screen,
                BORDER_COLOR,
                rect,
                1
            )

        if self.last:
            last_rect = pygame.Rect(
                self.last,
                (GRID_SIZE, GRID_SIZE)
            )
            pygame.draw.rect(
                screen,
                BOARD_BACKGROUND_COLOR,
                last_rect
            )


def handle_keys(game_object):
    """Обрабатывает нажатия клавиш."""
    directions = {
        pygame.K_UP: (UP, DOWN),
        pygame.K_DOWN: (DOWN, UP),
        pygame.K_LEFT: (LEFT, RIGHT),
        pygame.K_RIGHT: (RIGHT, LEFT)
    }

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            raise SystemExit

        if event.type == pygame.KEYDOWN and event.key in directions:
            new_direction, opposite_direction = directions[event.key]

            if game_object.direction != opposite_direction:
                game_object.next_direction = new_direction


def main():
    """Запускает игру и управляет основным игровым циклом."""
    pygame.init()

    # Создаём объекты игры.
    snake = Snake()
    apple = Apple()

    while True:
        clock.tick(SPEED)

        # Обрабатываем нажатия клавиш.
        handle_keys(snake)

        # Обновляем направление движения.
        snake.update_direction()

        # Перемещаем змейку.
        snake.move()

        # Проверяем, съела ли змейка яблоко.
        if snake.get_head_position() == apple.position:
            snake.length += 1
            apple.randomize_position()

        # Проверяем столкновение головы с телом змейки.
        if snake.get_head_position() in snake.positions[1:]:
            snake.reset()
            apple.randomize_position()
            screen.fill(BOARD_BACKGROUND_COLOR)

        # Отрисовываем объекты.
        apple.draw()
        snake.draw()

        # Обновляем экран.
        pygame.display.update()


if __name__ == '__main__':
    main()
