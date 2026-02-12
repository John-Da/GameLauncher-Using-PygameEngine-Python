import pygame
import os
import subprocess
import sys
import time

pygame.init()
pygame.joystick.init()

# ==========================
# CONFIG
# ==========================
WIDTH, HEIGHT = 1000, 700
FPS = 60
LIBRARY_FOLDER = "library"

ICON_SIZE = 110
PADDING = 60
TITLE_TO_GRID_SPACE = 120
SIDE_PADDING = 96
BOTTOM_PADDING = 96

BUTTON_WIDTH = 100
BUTTON_HEIGHT = 50
BUTTON_PADDING = 20

# SCROLLING CONFIG
scroll_y = 0
target_scroll_y = 0
scroll_speed = 0.2  # Increased for snappier response

screen = pygame.display.set_mode((WIDTH, HEIGHT), pygame.RESIZABLE)
pygame.display.set_caption("Game Library")

clock = pygame.time.Clock()
title_font = pygame.font.SysFont("arial", 56, bold=True)
font = pygame.font.SysFont("arial", 24)
header_font = pygame.font.SysFont("arial", 20, bold=True)  # For List Headers
button_font = pygame.font.SysFont("arial", 20, bold=True)


# ==========================
# HELPERS
# ==========================
def get_dir_size(path):
    total_size = 0
    for dirpath, dirnames, filenames in os.walk(path):
        for f in filenames:
            fp = os.path.join(dirpath, f)
            total_size += os.path.getsize(fp)
    return f"{total_size / (1024 * 1024):.1f} MB"


def launch_game(game_file):
    subprocess.run([sys.executable, game_file], cwd=os.path.dirname(game_file))


def draw_button(surface, text, rect, is_active, is_selected, mouse_pos):
    is_hover = rect.collidepoint(mouse_pos)
    if is_active:
        bg_color, border_color = (80, 120, 200), (100, 140, 220)
    elif is_selected:
        bg_color, border_color = (60, 60, 60), (255, 255, 255)
    elif is_hover:
        bg_color, border_color = (60, 60, 60), (100, 100, 100)
    else:
        bg_color, border_color = (40, 40, 40), (70, 70, 70)

    pygame.draw.rect(surface, bg_color, rect, border_radius=8)
    pygame.draw.rect(surface, border_color, rect, 2 if not is_selected else 3, border_radius=8)
    text_surf = button_font.render(text, True, (255, 255, 255))
    surface.blit(text_surf, text_surf.get_rect(center=rect.center))
    return is_hover


# ==========================
# LOAD GAMES
# ==========================
games = []
if os.path.exists(LIBRARY_FOLDER):
    for folder in os.listdir(LIBRARY_FOLDER):
        path = os.path.join(LIBRARY_FOLDER, folder)
        if os.path.isdir(path):
            game_file, icon_file = None, None
            for f in os.listdir(path):
                if f.endswith(".py") and f != "__init__.py":
                    game_file = os.path.abspath(os.path.join(path, f))
                if f.lower().startswith("icon"):
                    icon_file = os.path.join(path, f)
            if game_file:
                icon = pygame.Surface((ICON_SIZE, ICON_SIZE))
                icon.fill((70, 70, 70))
                if icon_file:
                    img = pygame.image.load(icon_file).convert_alpha()
                    icon = pygame.transform.smoothscale(img, (ICON_SIZE, ICON_SIZE))

                games.append({
                    "name": folder,
                    "file": game_file,
                    "icon": icon,
                    "size": get_dir_size(path)
                })

# ==========================
# JOYSTICK INIT
# ==========================
joystick = None
if pygame.joystick.get_count() > 0:
    joystick = pygame.joystick.Joystick(0)
    joystick.init()

selected = 0
view_mode = "grid"
focus_mode = "games"
button_selected = 0
analog_last_move = 0
ANALOG_DELAY = 0.15

# ==========================
# MAIN LOOP
# ==========================
running = True
while running:
    WIDTH, HEIGHT = screen.get_size()
    screen.fill((20, 20, 20))
    mouse_pos = pygame.mouse.get_pos()

    # Lerp Scroll
    scroll_y += (target_scroll_y - scroll_y) * scroll_speed
    header_height = 100
    start_y = header_height + TITLE_TO_GRID_SPACE
    usable_width = WIDTH - SIDE_PADDING * 2

    if view_mode == "grid":
        cols = max(1, usable_width // (ICON_SIZE + PADDING))
        spacing_x = usable_width // cols
        for i, game in enumerate(games):
            row, col = i // cols, i % cols
            x = SIDE_PADDING + col * spacing_x + spacing_x // 2
            y = start_y + row * (ICON_SIZE + 90)
            draw_y = y - scroll_y

            if -ICON_SIZE < draw_y < HEIGHT:
                rect = pygame.Rect(0, 0, ICON_SIZE, ICON_SIZE)
                rect.center = (x, draw_y)
                screen.blit(game["icon"], rect)
                if i == selected and focus_mode == "games":
                    pygame.draw.rect(screen, (255, 255, 255), rect.inflate(20, 20), 4, border_radius=10)
                    # Instant target update for controller
                    if draw_y > HEIGHT - BOTTOM_PADDING: target_scroll_y += (ICON_SIZE + 90)
                    if draw_y < start_y: target_scroll_y -= (ICON_SIZE + 90)

                name_text = font.render(game["name"], True, (255, 255, 255))
                screen.blit(name_text, (x - name_text.get_width() // 2, draw_y + ICON_SIZE // 2 + 16))

    else:
        # LIST VIEW HEADERS
        LIST_ITEM_HEIGHT = 80
        list_start_y = start_y

        # Header Row (Static position relative to scroll)
        header_y = list_start_y - 40 - scroll_y
        if header_y > header_height:
            h_name = header_font.render("GAME NAME", True, (255, 255, 255))
            h_size = header_font.render("SIZE", True, (200, 200, 200))
            screen.blit(h_name, (SIDE_PADDING + 140, header_y))
            screen.blit(h_size, (WIDTH - SIDE_PADDING - 150, header_y))
            pygame.draw.line(screen, (40, 40, 45), (SIDE_PADDING + 40, header_y + 30),
                             (WIDTH - SIDE_PADDING - 40, header_y + 30), 1)

        for i, game in enumerate(games):
            y = list_start_y + i * LIST_ITEM_HEIGHT
            draw_y = y - scroll_y

            if -LIST_ITEM_HEIGHT < draw_y < HEIGHT:
                if i == selected and focus_mode == "games":
                    body = pygame.Rect(SIDE_PADDING + 40, draw_y, usable_width - 80, LIST_ITEM_HEIGHT - 10)
                    pygame.draw.rect(screen, (40, 40, 40), body, border_radius=8)
                    pygame.draw.rect(screen, (255, 255, 255), body, 2, border_radius=8)
                    # Scroll tracking
                    if draw_y + LIST_ITEM_HEIGHT > HEIGHT - BOTTOM_PADDING: target_scroll_y += LIST_ITEM_HEIGHT
                    if draw_y < list_start_y: target_scroll_y -= LIST_ITEM_HEIGHT

                icon_rect = pygame.Rect(SIDE_PADDING + 60, draw_y + 5, 60, 60)
                screen.blit(pygame.transform.smoothscale(game["icon"], (60, 60)), icon_rect)

                name_text = font.render(game["name"], True, (255, 255, 255))
                size_text = font.render(game["size"], True, (150, 150, 150))

                screen.blit(name_text,
                            (icon_rect.right + 20, draw_y + (LIST_ITEM_HEIGHT - name_text.get_height()) // 2 - 5))
                screen.blit(size_text,
                            (WIDTH - SIDE_PADDING - 150, draw_y + (LIST_ITEM_HEIGHT - size_text.get_height()) // 2 - 5))

    # HEADER UI (Drawn last)
    pygame.draw.rect(screen, (30, 30, 35), (0, 0, WIDTH, header_height))
    pygame.draw.line(screen, (50, 50, 60), (0, header_height), (WIDTH, header_height), 2)

    title_surf = title_font.render("Game Library", True, (255, 255, 255))
    screen.blit(title_surf, (SIDE_PADDING, header_height // 2 - title_surf.get_height() // 2))

    count_text = font.render(str(len(games)), True, (200, 200, 200))
    count_rect = count_text.get_rect(midleft=(SIDE_PADDING + title_surf.get_width() + 20, header_height // 2))
    pygame.draw.rect(screen, (60, 60, 65), count_rect.inflate(20, 10), border_radius=15)
    screen.blit(count_text, count_rect)

    exit_rect = pygame.Rect(WIDTH - SIDE_PADDING - BUTTON_WIDTH, (header_height - BUTTON_HEIGHT) // 2, BUTTON_WIDTH,
                            BUTTON_HEIGHT)
    list_rect = pygame.Rect(exit_rect.left - BUTTON_WIDTH - BUTTON_PADDING, (header_height - BUTTON_HEIGHT) // 2,
                            BUTTON_WIDTH, BUTTON_HEIGHT)
    grid_rect = pygame.Rect(list_rect.left - BUTTON_WIDTH - BUTTON_PADDING, (header_height - BUTTON_HEIGHT) // 2,
                            BUTTON_WIDTH, BUTTON_HEIGHT)

    draw_button(screen, "Grid", grid_rect, view_mode == "grid", focus_mode == "buttons" and button_selected == 0,
                mouse_pos)
    draw_button(screen, "List", list_rect, view_mode == "list", focus_mode == "buttons" and button_selected == 1,
                mouse_pos)
    draw_button(screen, "Exit", exit_rect, False, focus_mode == "buttons" and button_selected == 2, mouse_pos)

    target_scroll_y = max(0, target_scroll_y)

    # ==========================
    # INPUTS
    # ==========================
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.VIDEORESIZE:
            screen = pygame.display.set_mode(event.size, pygame.RESIZABLE)
        elif event.type == pygame.MOUSEWHEEL:
            target_scroll_y -= event.y * 60

        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_TAB:
                focus_mode = "buttons" if focus_mode == "games" else "games"
            elif focus_mode == "buttons":
                if event.key == pygame.K_RIGHT:
                    button_selected = min(2, button_selected + 1)
                elif event.key == pygame.K_LEFT:
                    button_selected = max(0, button_selected - 1)
                elif event.key == pygame.K_DOWN:
                    focus_mode = "games"
                elif event.key == pygame.K_RETURN:
                    if button_selected == 0:
                        view_mode = "grid"
                    elif button_selected == 1:
                        view_mode = "list"
                    elif button_selected == 2:
                        running = False
            elif focus_mode == "games":
                cols = max(1, usable_width // (ICON_SIZE + PADDING)) if view_mode == "grid" else 1
                if event.key == pygame.K_UP and selected < cols:
                    focus_mode, target_scroll_y = "buttons", 0

                if view_mode == "grid":
                    if event.key == pygame.K_RIGHT:
                        selected = min(len(games) - 1, selected + 1)
                    elif event.key == pygame.K_LEFT:
                        selected = max(0, selected - 1)
                    elif event.key == pygame.K_DOWN:
                        selected = min(len(games) - 1, selected + cols)
                    elif event.key == pygame.K_UP:
                        selected = max(0, selected - cols)
                else:
                    if event.key == pygame.K_DOWN:
                        selected = min(len(games) - 1, selected + 1)
                    elif event.key == pygame.K_UP:
                        selected = max(0, selected - 1)

                if event.key == pygame.K_RETURN and games: launch_game(games[selected]["file"])

        elif event.type == pygame.JOYHATMOTION:
            dx, dy = event.value
            if dx != 0: pygame.event.post(
                pygame.event.Event(pygame.KEYDOWN, key=pygame.K_RIGHT if dx == 1 else pygame.K_LEFT))
            if dy != 0: pygame.event.post(
                pygame.event.Event(pygame.KEYDOWN, key=pygame.K_DOWN if dy == -1 else pygame.K_UP))

        elif event.type == pygame.JOYBUTTONDOWN:
            if event.button == 0:
                pygame.event.post(pygame.event.Event(pygame.KEYDOWN, key=pygame.K_RETURN))
            elif event.button in (4, 6):
                pygame.event.post(pygame.event.Event(pygame.KEYDOWN, key=pygame.K_TAB))

        elif event.type == pygame.JOYAXISMOTION:
            now = time.time()
            if now - analog_last_move > ANALOG_DELAY:
                x_axis, y_axis = joystick.get_axis(0), joystick.get_axis(1)
                if abs(x_axis) > 0.45:
                    pygame.event.post(
                        pygame.event.Event(pygame.KEYDOWN, key=pygame.K_RIGHT if x_axis > 0 else pygame.K_LEFT))
                    analog_last_move = now
                if abs(y_axis) > 0.45:
                    pygame.event.post(
                        pygame.event.Event(pygame.KEYDOWN, key=pygame.K_DOWN if y_axis > 0 else pygame.K_UP))
                    analog_last_move = now

    pygame.display.flip()
    clock.tick(FPS)

pygame.quit()