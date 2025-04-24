import pygame
import sys
import random
import time
import psycopg2

# PostgreSQL-пен байланыс
conn = psycopg2.connect(
    dbname="snake_game",           # База аты (pgAdmin-де жасадыңыз)
    user="postgres",               # Әдепкі пайдаланушы
    password="12345678",      # Өз пароліңізбен ауыстырыңыз
    host="localhost"
)
cur = conn.cursor()

# Пайдаланушы енгізу
username = input("Enter your username: ")

cur.execute("SELECT id FROM users WHERE username = %s", (username,))
user = cur.fetchone()

if user:
    user_id = user[0]
    cur.execute("SELECT level, score FROM user_score WHERE user_id = %s ORDER BY saved_at DESC LIMIT 1", (user_id,))
    last_game = cur.fetchone()
    if last_game:
        print(f"Welcome back {username}! Last level: {last_game[0]}, Last score: {last_game[1]}")
    else:
        print(f"Welcome {username}!")
else:
    cur.execute("INSERT INTO users (username) VALUES (%s) RETURNING id", (username,))
    user_id = cur.fetchone()[0]
    conn.commit()
    print(f"New user {username} added.")

pygame.init()

SCREEN_WIDTH = 400
SCREEN_HEIGHT = 400
GRID_SIZE = 20

SPEED = 5
SCORE = 0
LEVEL = 1

WHITE = (255, 255, 255)
GREEN = (0, 255, 0)
RED = (255, 0, 0)
BLACK = (0, 0, 0)

font = pygame.font.SysFont("Verdana", 20)

screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Snake Game")

class Food:
    def __init__(self, snake_body):
        self.position = self.generate_position(snake_body)
        self.weight = random.choice([1, 2, 3])
        self.spawn_time = time.time()
        self.lifetime = random.randint(5, 10)

    def generate_position(self, snake_body):
        while True:
            x = random.randint(0, (SCREEN_WIDTH // GRID_SIZE) - 1) * GRID_SIZE
            y = random.randint(0, (SCREEN_HEIGHT // GRID_SIZE) - 1) * GRID_SIZE
            if (x, y) not in snake_body:
                return (x, y)

    def is_expired(self):
        return time.time() - self.spawn_time > self.lifetime

snake = [(100, 100), (80, 100), (60, 100)]
snake_dir = (GRID_SIZE, 0)

food = Food(snake)

clock = pygame.time.Clock()
running = True

while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    keys = pygame.key.get_pressed()
    if keys[pygame.K_UP] and snake_dir != (0, GRID_SIZE):
        snake_dir = (0, -GRID_SIZE)
    if keys[pygame.K_DOWN] and snake_dir != (0, -GRID_SIZE):
        snake_dir = (0, GRID_SIZE)
    if keys[pygame.K_LEFT] and snake_dir != (GRID_SIZE, 0):
        snake_dir = (-GRID_SIZE, 0)
    if keys[pygame.K_RIGHT] and snake_dir != (-GRID_SIZE, 0):
        snake_dir = (GRID_SIZE, 0)

    new_head = (snake[0][0] + snake_dir[0], snake[0][1] + snake_dir[1])

    if new_head in snake or new_head[0] < 0 or new_head[0] >= SCREEN_WIDTH or new_head[1] < 0 or new_head[1] >= SCREEN_HEIGHT:
        running = False

    snake.insert(0, new_head)

    if new_head == food.position:
        SCORE += food.weight
        if SCORE % 5 == 0:
            LEVEL += 1
            SPEED += 1
        food = Food(snake)
    else:
        snake.pop()

    if food.is_expired():
        food = Food(snake)

    screen.fill(WHITE)

    for segment in snake:
        pygame.draw.rect(screen, GREEN, (*segment, GRID_SIZE, GRID_SIZE))

    if food.weight == 1:
        color = RED
    elif food.weight == 2:
        color = (255, 165, 0)
    else:
        color = (128, 0, 128)

    pygame.draw.rect(screen, color, (*food.position, GRID_SIZE, GRID_SIZE))

    score_text = font.render(f"Score: {SCORE}  Level: {LEVEL}", True, BLACK)
    screen.blit(score_text, (10, 10))

    pygame.display.update()
    clock.tick(SPEED)

# 🟩 Ойын біткен соң базаға сақтау
cur.execute("INSERT INTO user_score (user_id, level, score) VALUES (%s, %s, %s)", (user_id, LEVEL, SCORE))
conn.commit()
print("Score saved to database.")

cur.close()
conn.close()

pygame.quit()
sys.exit()