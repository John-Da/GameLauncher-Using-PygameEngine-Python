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

TOP_PADDING = 40
TITLE_TO_GRID_SPACE = 120
SIDE_PADDING = 96
BOTTOM_PADDING = 96

BUTTON_WIDTH = 100
BUTTON_HEIGHT = 50
BUTTON_PADDING = 20

screen = pygame.display.set_mode((WIDTH, HEIGHT), pygame.RESIZABLE)
pygame.display.set_caption("Game Library")

clock = pygame.time.Clock()
title_font = pygame.font.SysFont("arial", 56, bold=True)
font = pygame.font.SysFont("arial", 24)
button_font = pygame.font.SysFont("arial", 20, bold=True)

# ==========================
# LOAD GAMES
# ==========================
games = []

if os.path.exists(LIBRARY_FOLDER):
    for folder in os.listdir(LIBRARY_FOLDER):
        path = os.path.join(LIBRARY_FOLDER, folder)
        if os.path.isdir(path):

            game_file = None
            icon_file = None

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
                    icon = pygame.transform.smoothscale(
                        img, (ICON_SIZE, ICON_SIZE)
                    )

                games.append({
                    "name": folder,
                    "file": game_file,
                    "icon": icon
                })

print(f"✅ Loaded games: {len(games)}")

# ==========================
# JOYSTICK INIT
# ==========================
joystick = None
if pygame.joystick.get_count() > 0:
    joystick = pygame.joystick.Joystick(0)
    joystick.init()
    print("🎮 Controller connected:", joystick.get_name())

selected = 0
view_mode = "grid"
focus_mode = "games"
button_selected = 0

# ANALOG COOLDOWN
analog_last_move = 0
ANALOG_DELAY = 0.18


# ==========================
# HELPER FUNCTIONS
# ==========================
def draw_button(surface, text, rect, is_active, is_selected, mouse_pos):
    is_hover = rect.collidepoint(mouse_pos)

    if is_active:
        bg_color = (80, 120, 200)
        border_color = (100, 140, 220)
    elif is_selected:
        bg_color = (60, 60, 60)
        border_color = (255, 255, 255)
        border_width = 3
    elif is_hover:
        bg_color = (60, 60, 60)
        border_color = (100, 100, 100)
        border_width = 2
    else:
        bg_color = (40, 40, 40)
        border_color = (70, 70, 70)
        border_width = 2

    pygame.draw.rect(surface, bg_color, rect, border_radius=8)
    pygame.draw.rect(surface, border_color, rect, 2, border_radius=8)

    text_surf = button_font.render(text, True, (255, 255, 255))
    surface.blit(text_surf, text_surf.get_rect(center=rect.center))

    return is_hover


def launch_game(game_file):
    # game_dir = os.path.dirname(game_file)
    # subprocess.run([sys.executable, game_file], cwd=game_dir)
    subprocess.run(
        [sys.executable, game_file],
        cwd=os.path.dirname(game_file)  # VERY IMPORTANT
    )


# ==========================
# MAIN LOOP
# ==========================
running = True
while running:
    WIDTH, HEIGHT = screen.get_size()
    screen.fill((20, 20, 20))
    mouse_pos = pygame.mouse.get_pos()

    # HEADER BACKGROUND
    header_height = 100
    header_rect = pygame.Rect(0, 0, WIDTH, header_height)
    pygame.draw.rect(screen, (30, 30, 35), header_rect)
    pygame.draw.line(screen, (50, 50, 60), (0, header_height), (WIDTH, header_height), 2)

    # TITLE
    title = title_font.render("Game Library", True, (255, 255, 255))
    screen.blit(title, (SIDE_PADDING, header_height // 2 - title.get_height() // 2))

    # BUTTONS
    exit_rect = pygame.Rect(WIDTH - SIDE_PADDING - BUTTON_WIDTH,
                            (header_height - BUTTON_HEIGHT) // 2,
                            BUTTON_WIDTH, BUTTON_HEIGHT)

    list_rect = pygame.Rect(exit_rect.left - BUTTON_WIDTH - BUTTON_PADDING,
                            (header_height - BUTTON_HEIGHT) // 2,
                            BUTTON_WIDTH, BUTTON_HEIGHT)

    grid_rect = pygame.Rect(list_rect.left - BUTTON_WIDTH - BUTTON_PADDING,
                            (header_height - BUTTON_HEIGHT) // 2,
                            BUTTON_WIDTH, BUTTON_HEIGHT)

    grid_hover = draw_button(screen, "Grid", grid_rect, view_mode == "grid",
                             focus_mode == "buttons" and button_selected == 0,
                             mouse_pos)
    list_hover = draw_button(screen, "List", list_rect, view_mode == "list",
                             focus_mode == "buttons" and button_selected == 1,
                             mouse_pos)
    exit_hover = draw_button(screen, "Exit", exit_rect, False,
                             focus_mode == "buttons" and button_selected == 2,
                             mouse_pos)

    start_y = header_height + TITLE_TO_GRID_SPACE
    usable_width = WIDTH - SIDE_PADDING * 2
    usable_height = HEIGHT - start_y - BOTTOM_PADDING

    # ==========================
    # DRAW GAMES
    # ==========================
    if view_mode == "grid":
        cols = max(1, usable_width // (ICON_SIZE + PADDING))
        spacing_x = usable_width // cols

        for i, game in enumerate(games):
            row = i // cols
            col = i % cols

            x = SIDE_PADDING + col * spacing_x + spacing_x // 2
            y = start_y + row * (ICON_SIZE + 70)

            if y + ICON_SIZE // 2 > HEIGHT - BOTTOM_PADDING:
                continue

            rect = pygame.Rect(0, 0, ICON_SIZE, ICON_SIZE)
            rect.center = (x, y)
            screen.blit(game["icon"], rect)

            if i == selected and focus_mode == "games":
                pygame.draw.rect(screen, (255, 255, 255), rect.inflate(20, 20), 4, border_radius=10)

            name_text = font.render(game["name"], True, (255, 255, 255))
            screen.blit(name_text, (x - name_text.get_width() // 2,
                                    y + ICON_SIZE // 2 + 16))

    else:
        LIST_ITEM_HEIGHT = 100
        LIST_ICON_SIZE = 70
        LIST_LEFT_PADDING = 40

        for i, game in enumerate(games):
            y = start_y + i * LIST_ITEM_HEIGHT
            if y + LIST_ITEM_HEIGHT > HEIGHT - BOTTOM_PADDING:
                continue

            if i == selected and focus_mode == "games":
                body = pygame.Rect(SIDE_PADDING + LIST_LEFT_PADDING,
                                   y + 10,
                                   usable_width - LIST_LEFT_PADDING * 2,
                                   LIST_ITEM_HEIGHT - 20)
                pygame.draw.rect(screen, (40, 40, 40), body, border_radius=8)
                pygame.draw.rect(screen, (255, 255, 255), body, 2, border_radius=8)

            icon_rect = pygame.Rect(SIDE_PADDING + LIST_LEFT_PADDING + 30,
                                    y + (LIST_ITEM_HEIGHT - LIST_ICON_SIZE) // 2,
                                    LIST_ICON_SIZE, LIST_ICON_SIZE)

            screen.blit(pygame.transform.smoothscale(game["icon"],
                                                     (LIST_ICON_SIZE, LIST_ICON_SIZE)),
                        icon_rect)

            name_text = font.render(game["name"], True, (255, 255, 255))
            screen.blit(name_text, (icon_rect.right + 30,
                                    y + (LIST_ITEM_HEIGHT - name_text.get_height()) // 2))

    # ==========================
    # INPUT HANDLING
    # ==========================
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        elif event.type == pygame.VIDEORESIZE:
            screen = pygame.display.set_mode(event.size, pygame.RESIZABLE)

        # ---------------- KEYBOARD ----------------
        elif event.type == pygame.KEYDOWN:

            if event.key == pygame.K_TAB:
                if focus_mode == "games":
                    focus_mode = "buttons"
                    button_selected = 0
                else:
                    focus_mode = "games"

            elif focus_mode == "buttons":
                if event.key == pygame.K_RIGHT:
                    button_selected = min(2, button_selected + 1)
                elif event.key == pygame.K_LEFT:
                    button_selected = max(0, button_selected - 1)
                elif event.key == pygame.K_RETURN:
                    if button_selected == 0:
                        view_mode = "grid"
                    elif button_selected == 1:
                        view_mode = "list"
                    elif button_selected == 2:
                        running = False
                elif event.key == pygame.K_DOWN:
                    focus_mode = "games"

            elif focus_mode == "games":

                if event.key == pygame.K_UP and selected == 0:
                    focus_mode = "buttons"
                    button_selected = 0

                if view_mode == "grid":
                    cols = max(1, usable_width // (ICON_SIZE + PADDING))

                    if event.key == pygame.K_RIGHT:
                        selected = min(len(games) - 1, selected + 1)
                    elif event.key == pygame.K_LEFT:
                        selected = max(0, selected - 1)
                    elif event.key == pygame.K_DOWN:
                        selected = min(len(games) - 1, selected + cols)
                    elif event.key == pygame.K_UP:
                        selected = max(0, selected - cols)
                    elif event.key == pygame.K_RETURN and games:
                        launch_game(games[selected]["file"])

                else:
                    if event.key == pygame.K_DOWN:
                        selected = min(len(games) - 1, selected + 1)
                    elif event.key == pygame.K_UP:
                        selected = max(0, selected - 1)
                    elif event.key == pygame.K_RETURN and games:
                        launch_game(games[selected]["file"])

        # ---------------- MOUSE ----------------
        elif event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:
                if grid_rect.collidepoint(mouse_pos):
                    view_mode = "grid"
                elif list_rect.collidepoint(mouse_pos):
                    view_mode = "list"
                elif exit_rect.collidepoint(mouse_pos):
                    running = False

        # ---------------- D-PAD → keyboard ----------------
        elif event.type == pygame.JOYHATMOTION:
            dx, dy = event.value

            if dx == 1:
                pygame.event.post(pygame.event.Event(pygame.KEYDOWN, key=pygame.K_RIGHT))
            elif dx == -1:
                pygame.event.post(pygame.event.Event(pygame.KEYDOWN, key=pygame.K_LEFT))

            if dy == -1:
                pygame.event.post(pygame.event.Event(pygame.KEYDOWN, key=pygame.K_DOWN))
            elif dy == 1:
                pygame.event.post(pygame.event.Event(pygame.KEYDOWN, key=pygame.K_UP))

        # ---------------- A button → Enter ----------------
        elif event.type == pygame.JOYBUTTONDOWN:
            btn = event.button

            BTN_A = 0
            BTN_PLUS = 6
            BTN_MINUS = 4

            if btn == BTN_A:
                pygame.event.post(pygame.event.Event(pygame.KEYDOWN, key=pygame.K_RETURN))

            elif btn in (BTN_PLUS, BTN_MINUS):
                pygame.event.post(pygame.event.Event(pygame.KEYDOWN, key=pygame.K_TAB))

        # ---------------- ANALOG → keyboard arrows ----------------
        elif event.type == pygame.JOYAXISMOTION:
            now = time.time()
            if now - analog_last_move < ANALOG_DELAY:
                continue

            x_axis = joystick.get_axis(0)
            y_axis = joystick.get_axis(1)
            DEADZONE = 0.45

            moved = False

            if x_axis > DEADZONE:
                pygame.event.post(pygame.event.Event(pygame.KEYDOWN, key=pygame.K_RIGHT))
                moved = True
            elif x_axis < -DEADZONE:
                pygame.event.post(pygame.event.Event(pygame.KEYDOWN, key=pygame.K_LEFT))
                moved = True

            if y_axis > DEADZONE:
                pygame.event.post(pygame.event.Event(pygame.KEYDOWN, key=pygame.K_DOWN))
                moved = True
            elif y_axis < -DEADZONE:
                pygame.event.post(pygame.event.Event(pygame.KEYDOWN, key=pygame.K_UP))
                moved = True

            if moved:
                analog_last_move = now

    pygame.display.flip()
    clock.tick(FPS)

pygame.quit()
