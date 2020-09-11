import sys
import random

import pygame


WIDTH = 600
HEIGHT = 600

ROWS = 8
COLS = 8
TILE_WIDTH = 64
TILE_HEIGHT = 64
PADDING_X = 44
PADDING_Y = 44

WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GREEN = (50,205,50)
YELLOW = (255,255,0)
BLUE = (0, 0 ,255)
GRAY = (224, 224, 224)


def who_goes_first():
    if random.randint(0, 1) == 0:
        return 'Player'
    else:
        return 'Computer'


def get_player_move(board, tile):
    for row in range(ROWS):
        for col in range(COLS):
            if board[row][col]['rect'].collidepoint(pygame.mouse.get_pos()):
                if is_valid_move(board, tile, row, col):
                    return [row, col]
    return False


def get_computer_move(board, tile):
    valid_moves = get_valid_moves(board, tile)
    random.shuffle(valid_moves)

    for row, col in valid_moves:
        if is_on_corner(row, col):
            return [row, col]

    best_move = None
    best_score = -1
    for row, col in valid_moves:
        copy_board = get_board_copy(board)
        make_move(copy_board, tile, row, col)
        score = get_score_of_board(copy_board)[tile]
        if score > best_score:
            best_score = score
            best_move = [row, col]

    return best_move


def make_move(board, tile, row, col):
    global changed_tiles
    changed_tiles = []
    tiles_to_flip = is_valid_move(board, tile, row, col)
    if tiles_to_flip == False:
        return False
    board[row][col]['value'] = tile
    changed_tiles.append([row, col])
    for row, col in tiles_to_flip:
        board[row][col]['value'] = tile
        changed_tiles.append([row, col])

    return True


def get_new_board():
    board = [[] for _ in range(8)]
    for row in range(ROWS):
        for col in range(COLS):
            tile = pygame.Rect(PADDING_X + TILE_WIDTH * row, PADDING_Y + TILE_HEIGHT * col, TILE_WIDTH, TILE_HEIGHT)
            board[row].append({
                'rect': tile,
                'value': ' '
            })
    return board


def get_valid_moves(board, tile):
    valid_moves = []
    for row in range(ROWS):
        for col in range(COLS):
            if is_valid_move(board, tile, row, col):
                valid_moves.append([row, col])
    
    return valid_moves


def get_board_with_valid_moves(board, tile):
    board_copy = get_board_copy(board)

    for row, col in get_valid_moves(board_copy, tile):
        board_copy[row][col]['value'] = '.'
    return board_copy


def get_board_copy(board):
    board_copy = get_new_board()
    for row in range(ROWS):
        for col in range(COLS):
            board_copy[row][col]['value'] = board[row][col]['value']

    return board_copy


def get_score_of_board(board):
    x_score = 0
    o_score = 0
    for row in range(ROWS):
        for col in range(COLS):
            if board[row][col]['value'] == 'X':
                x_score += 1
            if board[row][col]['value'] == 'O':
                o_score += 1
    
    return {'X': x_score, 'O': o_score}


def is_valid_move(board, tile, row_start, col_start):
    if board[row_start][col_start]['value'] != ' ' or not is_on_board(row_start, col_start):
        return False
    
    if tile == 'X':
        other_tile = 'O'
    else:
        other_tile = 'X'

    tiles_to_flip = []
    for r_dir, c_dir in [[0, 1], [1, 1], [1, 0], [1, -1], [0, -1], [-1, -1], [-1, 0], [-1, 1]]:
        row, col = row_start, col_start
        row += r_dir
        col += c_dir

        while is_on_board(row, col) and board[row][col]['value'] == other_tile:
            row += r_dir
            col += c_dir

            if is_on_board(row, col) and board[row][col]['value'] == tile:
                while True:
                    row -= r_dir
                    col -= c_dir
                    if row == row_start and col == col_start:
                        break
                    tiles_to_flip.append([row, col])
    
    if len(tiles_to_flip) == 0:
        return False
    
    return tiles_to_flip


def is_on_corner(row, col):
    return (row == 0 or row == ROWS - 1) and (col == 0 or col == COLS - 1)


def is_on_board(row, col):
    return row >= 0 and row <= ROWS - 1 and col >= 0 and col <= COLS - 1


def new_game(p_tile, c_tile):
    global board, turn, changed_tiles, show_hints, game_over, playing
    global player_tile, computer_tile
    playing = True
    game_over = False
    show_hints = False
    changed_tiles = []
    turn = who_goes_first()
    board = get_new_board()
    board[3][3]['value'] = 'X'
    board[3][4]['value'] = 'O'
    board[4][3]['value'] = 'O'
    board[4][4]['value'] = 'X'
    player_tile = p_tile
    computer_tile = c_tile


def draw_menu():
    screen.blit(tile_font.render('Reversi game', 1, BLACK), (160, 128))
    screen.blit(text_font.render('Press H for hints', 1, BLACK), (220, 450))


    white_button = pygame.Rect(100, 320, 180, 50)
    black_button = pygame.Rect(350, 320, 180, 50)

    white_color = GRAY
    black_color = GRAY

    mouse = pygame.mouse.get_pos()
    click = pygame.mouse.get_pressed()

    if white_button.collidepoint(mouse):
        white_color = GREEN
        if click[0]:
            new_game('O', 'X')
            return
    if black_button.collidepoint(mouse):
        black_color = GREEN
        if click[0]:
            new_game('X', 'O')
            return

    pygame.draw.rect(screen, white_color, white_button)
    pygame.draw.rect(screen, black_color, black_button)

    white_label = text_font.render(f'Play for White', 1, BLACK)
    screen.blit(white_label, (120, 333))

    black_label = text_font.render(f'Play for Black', 1, BLACK)
    screen.blit(black_label, (370, 333))


def draw_game_over(board):
    global game_over
    scores = get_score_of_board(board)
    black_score, white_score = scores['X'], scores['O']
    if black_score > white_score:
        screen.blit(tile_font.render('Black Win!', 1, BLACK), (200, 128))
    elif white_score > black_score:
        screen.blit(tile_font.render('White Win!', 1, BLACK), (190, 128))
    else:
        screen.blit(tile_font.render('Draw', 1, BLACK), (250, 128))

    
    draw_score(board)
    
    main_menu_button = pygame.Rect(230, 320, 150, 60)
    main_menu_color = BLUE

    mouse = pygame.mouse.get_pos()
    click = pygame.mouse.get_pressed()

    if main_menu_button.collidepoint(mouse):
        main_menu_color = GREEN
        if click[0]:
            game_over = False
            return

    pygame.draw.rect(screen, main_menu_color, main_menu_button)

    label = text_font.render(f'Main menu', 1, WHITE)
    screen.blit(label, (250, 340))


def draw_board(board):
    if show_hints:
        board_with_valid_moves = get_board_with_valid_moves(board, player_tile)
    for row in range(ROWS):
        for col in range(COLS):
            if show_hints:
                draw_tile(board_with_valid_moves, row, col)
            else:
                draw_tile(board, row, col)


def draw_score(board):
    scores = get_score_of_board(board)
    x_score, o_score = scores['X'], scores['O']

    x_label = text_font.render(f'X: {x_score}', 1, BLACK)
    screen.blit(x_label, (44, 16))

    o_label = text_font.render(f'O: {o_score}', 1, BLACK)
    screen.blit(o_label, (500, 16))


def draw_tile(board, row, col):
    x = PADDING_X + TILE_WIDTH * row
    y = PADDING_Y + TILE_HEIGHT * col
    color = GREEN
    if [row, col] in changed_tiles:
        color = YELLOW
    if board[row][col]['rect'].collidepoint(pygame.mouse.get_pos()):
        color = BLUE
    pygame.draw.rect(screen, color, board[row][col]['rect'])

    pygame.draw.rect(screen, WHITE, (x, y, TILE_WIDTH, 1))
    pygame.draw.rect(screen, WHITE, (x, y, 1, TILE_HEIGHT))

    pygame.draw.rect(screen, WHITE, (x, y + TILE_HEIGHT, TILE_WIDTH, 1))
    pygame.draw.rect(screen, WHITE, (x + TILE_WIDTH, y, 1, TILE_HEIGHT))

    value = board[row][col]['value']

    if value != ' ':
        if value == '.':
            pygame.draw.circle(screen, GRAY, (x + TILE_WIDTH // 2, y + TILE_HEIGHT // 2), 12)
        else:
            circle_color = BLACK if value == 'X' else WHITE
            pygame.draw.circle(screen, circle_color, (x + TILE_WIDTH // 2, y + TILE_HEIGHT // 2), 24)


board = get_new_board()
turn = who_goes_first()
changed_tiles = []
show_hints = False
game_over = False
playing = False
pygame.init()
text_font = pygame.font.Font(None, 32)
tile_font = pygame.font.Font(None, 64)
clock = pygame.time.Clock()
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Reversi")
player_tile, computer_tile = 'X', 'O'

while True:
    clock.tick(30)
    mouse_pressed = False
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()
        elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            mouse_pressed = True
        elif event.type == pygame.KEYDOWN and playing:
            if event.key == pygame.K_h:
                show_hints = not show_hints

    screen.fill(WHITE)

    if playing:
        draw_board(board)
        draw_score(board)

        turn_label = text_font.render(f'Turn: {turn}', 1, BLACK)
        screen.blit(turn_label, (226, 16))

        player_valid_moves = get_valid_moves(board, player_tile)
        computer_valid_moves = get_valid_moves(board, computer_tile)

        if player_valid_moves == [] and computer_valid_moves == []:
            game_over = True
            playing = False
        elif turn == 'Player':
            if player_valid_moves != []:
                if mouse_pressed:
                    move = get_player_move(board, player_tile)
                    if move:
                        make_move(board, player_tile, move[0], move[1])
                        turn = 'Computer'
            else:
                turn = 'Computer'
        elif turn == 'Computer':
            if computer_valid_moves != []:
                move = get_computer_move(board, computer_tile)
                if move:
                    make_move(board, computer_tile, move[0], move[1])
                turn = 'Player'
            else:
                turn = 'Player'
    elif game_over:
        draw_game_over(board)
    else:
        draw_menu()
    pygame.display.update()
