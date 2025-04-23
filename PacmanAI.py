import pygame
import sys
import math
import random
from queue import PriorityQueue

pygame.init()

CELL_SIZE = 30
COLS = 20
ROWS = 14
WIDTH, HEIGHT = COLS * CELL_SIZE, ROWS * CELL_SIZE
WIN = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Pacman AI")

BLACK = (0, 0, 0)
YELLOW = (255, 255, 0)
RED = (255, 0, 0)
BLUE = (0, 0, 255)
WHITE = (255, 255, 255)
GREEN = (0, 255, 0)

clock = pygame.time.Clock()
font = pygame.font.Font(None, 36)

MAP = [
    [1]*COLS,
    [1]+[0]*18+[1],
    [1]+[0]*18+[1],
    [1]+[0]*18+[1],
    [1]+[0,1,1,0,0,0,0,1,0,1,0,0,0,1,0,0,1,0]+[1],
    [1]+[0]*18+[1],
    [1]+[0]*18+[1],
    [1]+[0]*18+[1],
    [1]+[0]*18+[1],
    [1]+[0]*18+[1],
    [1]+[0]*18+[1],
    [1]+[0]*18+[1],
    [1]+[0]*18+[1],
    [1]*COLS
]

pacman_pos = [0, 0]
ghost_pos = [0, 0]
pacman_speed = 3
ghost_speed = 2
pacman_direction = (0, 0)
game_mode = None
score = 0

food_map = [[1 if MAP[y][x] == 0 else 0 for x in range(COLS)] for y in range(ROWS)]

def draw_text(text, color, x, y):
    text_surface = font.render(text, True, color)
    text_rect = text_surface.get_rect(center=(x, y))
    WIN.blit(text_surface, text_rect)

def draw_map():
    for y in range(ROWS):
        for x in range(COLS):
            if MAP[y][x] == 1:
                rect = pygame.Rect(x * CELL_SIZE, y * CELL_SIZE, CELL_SIZE, CELL_SIZE)
                pygame.draw.rect(WIN, BLUE, rect)
            elif food_map[y][x] == 1:
                rect = pygame.Rect(x * CELL_SIZE, y * CELL_SIZE, CELL_SIZE, CELL_SIZE)
                pygame.draw.circle(WIN, WHITE, rect.center, 4)

def draw_characters():
    pygame.draw.circle(WIN, YELLOW, (int(pacman_pos[0]), int(pacman_pos[1])), CELL_SIZE // 2 - 2)
    pygame.draw.circle(WIN, RED, (int(ghost_pos[0]), int(ghost_pos[1])), CELL_SIZE // 2 - 4)

def is_walkable(x, y):
    col = int(x // CELL_SIZE)
    row = int(y // CELL_SIZE)
    if 0 <= col < COLS and 0 <= row < ROWS:
        return MAP[row][col] == 0
    return False

def get_grid_pos(position):
    """Chuyển đổi tọa độ pixel thành chỉ số ô trên bản đồ."""
    x, y = position
    col = int(x // CELL_SIZE)
    row = int(y // CELL_SIZE)
    return col, row

def move_pacman_manual(direction):
    global score
    new_x = pacman_pos[0] + direction[0] * pacman_speed
    new_y = pacman_pos[1] + direction[1] * pacman_speed
    if is_walkable(new_x, new_y):
        pacman_pos[0] = new_x
        pacman_pos[1] = new_y
        col, row = get_grid_pos(pacman_pos)
        if food_map[row][col] == 1:
            food_map[row][col] = 0
            score += 10


def a_star(start, goal):
    open_set = PriorityQueue()
    open_set.put((0, start))
    came_from = {}
    g_score = {start: 0}
    f_score = {start: heuristic(start, goal)}

    while not open_set.empty():
        _, current = open_set.get()

        if current == goal:
            path = []
            while current in came_from:
                path.append(current)
                current = came_from[current]
            path.reverse()
            return path

        for dx, dy in [(-1,0), (1,0), (0,-1), (0,1)]:
            neighbor = (current[0] + dx, current[1] + dy)
            if 0 <= neighbor[0] < COLS and 0 <= neighbor[1] < ROWS and MAP[neighbor[1]][neighbor[0]] == 0:
                tentative_g_score = g_score[current] + 1
                if neighbor not in g_score or tentative_g_score < g_score[neighbor]:
                    came_from[neighbor] = current
                    g_score[neighbor] = tentative_g_score
                    f_score[neighbor] = tentative_g_score + heuristic(neighbor, goal)
                    open_set.put((f_score[neighbor], neighbor))

    return []

def heuristic(a, b):
    return abs(a[0] - b[0]) + abs(a[1] - b[1])

# Tìm ô chứa thức ăn gần nhất và an toàn nhất
def find_best_food_target():
    pac_col, pac_row = get_grid_pos(pacman_pos)
    ghost_col, ghost_row = get_grid_pos(ghost_pos)
    best_food = None
    max_distance = -1

    for row in range(ROWS):
        for col in range(COLS):
            if food_map[row][col] == 1:
                dist_to_ghost = heuristic((col, row), (ghost_col, ghost_row))
                if dist_to_ghost > max_distance:
                    max_distance = dist_to_ghost
                    best_food = (col, row)
    return best_food


def find_safe_position():
    pac_col, pac_row = get_grid_pos(pacman_pos)
    ghost_col, ghost_row = get_grid_pos(ghost_pos)
    max_dist = -1
    safest_spot = (pac_col, pac_row)

    for row in range(ROWS):
        for col in range(COLS):
            if MAP[row][col] == 0:  # ô trống
                dist_to_ghost = heuristic((col, row), (ghost_col, ghost_row))
                if dist_to_ghost > max_dist:
                    max_dist = dist_to_ghost
                    safest_spot = (col, row)

    return safest_spot

def ai_move_pacman():
    global pacman_pos, score, food_map
    pac_grid = get_grid_pos(pacman_pos)
    ghost_grid = get_grid_pos(ghost_pos)
    distance_to_ghost = heuristic(pac_grid, ghost_grid)
    danger_threshold = 4

    def is_path_safe(path):
        """Kiểm tra nếu mọi ô trong đường đi đều cách ghost đủ xa"""
        return all(heuristic(cell, ghost_grid) >= danger_threshold for cell in path)

    target_grid = None

    # Tìm thức ăn an toàn gần nhất
    food_targets = [(col, row) for row in range(ROWS) for col in range(COLS)
                    if food_map[row][col] == 1]
    if food_targets:  # Nếu có thức ăn còn lại
        food_targets.sort(key=lambda pos: heuristic(pac_grid, pos))  # Ưu tiên thức ăn gần nhất
        for pos in food_targets:
            path = a_star(pac_grid, pos)
            if path and is_path_safe(path):
                target_grid = pos
                break

    if not target_grid:
        # Nếu không có thức ăn an toàn gần, tìm vị trí an toàn
        target_grid = find_safe_position()

    if target_grid:
        path = a_star(pac_grid, target_grid)
        if path:
            next_grid_cell = path[0]
            target_x = next_grid_cell[0] * CELL_SIZE + CELL_SIZE // 2
            target_y = next_grid_cell[1] * CELL_SIZE + CELL_SIZE // 2

            dx = target_x - pacman_pos[0]
            dy = target_y - pacman_pos[1]
            dist = math.hypot(dx, dy)

            if dist > 0:
                pacman_pos[0] += (dx / dist) * pacman_speed
                pacman_pos[1] += (dy / dist) * pacman_speed

            # Kiểm tra ăn thức ăn khi đến trung tâm ô
            current_grid = get_grid_pos(pacman_pos)
            if food_map[current_grid[1]][current_grid[0]] == 1:
                food_map[current_grid[1]][current_grid[0]] = 0
                score += 10

def check_win():
    """Kiểm tra xem Pacman đã ăn hết thức ăn chưa."""
    return all(all(not food for food in row) for row in food_map)

def game_over_screen():
    WIN.fill(BLACK)
    draw_text("Game Over!", RED, WIDTH // 2, HEIGHT // 2 - 50)
    draw_text("Score: {}".format(score), WHITE, WIDTH // 2, HEIGHT // 2)
    draw_text("Press any key to play again!", WHITE, WIDTH // 2, HEIGHT // 2 + 50)
    pygame.display.flip()
    waiting = True
    while waiting:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                waiting = False
                reset_game()

def game_win_screen():
    WIN.fill(BLACK)
    draw_text("You Win!", GREEN, WIDTH // 2, HEIGHT // 2 - 50)
    draw_text("Final Score: {}".format(score), WHITE, WIDTH // 2, HEIGHT // 2)
    draw_text("Press any key to play again!", WHITE, WIDTH // 2, HEIGHT // 2 + 50)
    pygame.display.flip()
    waiting = True
    while waiting:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                waiting = False
                reset_game()

def game_pause():
    draw_text("Game Paused", YELLOW, WIDTH // 2, HEIGHT // 2)
    draw_text("Press P to resume", WHITE, WIDTH // 2, HEIGHT // 2 + 50)
    pygame.display.flip()

    paused = True
    while paused:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_p:
                    paused = False
                    pygame.mixer.music.unpause() # Nếu có nhạc nền

def move_ghost():
    dx = pacman_pos[0] - ghost_pos[0]
    dy = pacman_pos[1] - ghost_pos[1]
    dist = math.hypot(dx, dy)
    if dist == 0: return
    dx = (dx / dist) * ghost_speed
    dy = (dy / dist) * ghost_speed

    next_x = ghost_pos[0] + dx
    next_y = ghost_pos[1] + dy

    if is_walkable(next_x, ghost_pos[1]):
        ghost_pos[0] = next_x
    if is_walkable(ghost_pos[0], next_y):
        ghost_pos[1] = next_y

def check_collision():
    return math.hypot(pacman_pos[0] - ghost_pos[0], pacman_pos[1] - ghost_pos[1]) < CELL_SIZE // 2

def reset_game():
    global pacman_pos, ghost_pos, pacman_direction, game_mode, score, food_map
    pacman_pos = [CELL_SIZE + CELL_SIZE // 2, CELL_SIZE + CELL_SIZE // 2]
    ghost_pos = [CELL_SIZE * (COLS - 1) - CELL_SIZE // 2, CELL_SIZE * (ROWS - 1) - CELL_SIZE // 2]
    pacman_direction = (0, 0)
    game_mode = None
    score = 0
    food_map = [[1 if MAP[y][x] == 0 else 0 for x in range(COLS)] for y in range(ROWS)]
    main_menu()

def main_menu():
    global game_mode, pacman_pos, ghost_pos, pacman_direction
    WIN.fill(BLACK)
    draw_text("Pacman AI", YELLOW, WIDTH // 2, HEIGHT // 2 - 100)
    draw_text("1. Yourself", GREEN, WIDTH // 2, HEIGHT // 2 - 30)
    draw_text("2. AI", BLUE, WIDTH // 2, HEIGHT // 2 + 30)
    pygame.display.flip()

    waiting = True
    while waiting:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_1:
                    game_mode = 'manual'
                    waiting = False
                elif event.key == pygame.K_2:
                    game_mode = 'ai'
                    waiting = False

    if game_mode == 'manual':
        pacman_pos = [CELL_SIZE + CELL_SIZE // 2, CELL_SIZE + CELL_SIZE // 2]
    elif game_mode == 'ai':
        pacman_pos = [CELL_SIZE * (COLS - 3) + CELL_SIZE // 2, CELL_SIZE * (ROWS - 2) + CELL_SIZE // 2]

    ghost_pos = [CELL_SIZE * (COLS - 1) - CELL_SIZE // 2, CELL_SIZE * (ROWS - 1) - CELL_SIZE // 2]
    pacman_direction = (0, 0)

def main():
    global pacman_direction, game_mode

    main_menu()

    paused = False  # State to track if game is paused
    while True:
        if game_mode is None:
            continue

        clock.tick(60)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_p:  # Pause game when pressing 'P'
                    paused = not paused  # Toggle pause state
                    if paused:
                        pygame.mixer.music.pause()  # Pause the music if any
                        game_pause()  # Show the pause screen
                    else:
                        pygame.mixer.music.unpause()  # Resume the music

                # Manual control for Pacman
                if not paused and game_mode == 'manual':
                    if event.key == pygame.K_LEFT:
                        pacman_direction = (-1, 0)
                    elif event.key == pygame.K_RIGHT:
                        pacman_direction = (1, 0)
                    elif event.key == pygame.K_UP:
                        pacman_direction = (0, -1)
                    elif event.key == pygame.K_DOWN:
                        pacman_direction = (0, 1)

        if paused:
            continue  # Skip the rest of the game loop if paused

        WIN.fill(BLACK)
        draw_map()
        draw_characters()
        draw_text(f"Score: {score}", WHITE, WIDTH // 2, 20)
        pygame.display.update()

        if game_mode == 'manual':
            move_pacman_manual(pacman_direction)
        elif game_mode == 'ai':
            ai_move_pacman()

        move_ghost()

        if check_win():
            game_win_screen()
            continue # Quan trọng: Tránh kiểm tra va chạm sau khi đã thắng
        elif check_collision():
            game_over_screen()
            continue # Quan trọng: Kết thúc vòng lặp sau khi game over

if __name__ == "__main__":
    main()