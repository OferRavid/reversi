from copy import deepcopy
import random
import time


corners = [
    (0, 0), (0, 7), (7, 0), (7, 7)
]

# Bad moves are locations near a corner in vertical or horizontal directions
bad_moves = [
    (0, 1), (1, 0), (0, 6), (6, 0),
    (7, 1), (1, 7), (7, 6), (6, 7)
]

# Very bad moves are locations near corners in diagonal direction
very_bad_moves = [
    (1, 1), (1, 6), (6, 1), (6, 6)
]


directions = [[1, 0], [1, 1], [1, -1], [0, 1], [-1, 1], [-1, -1], [-1, 0], [0, -1]]


# =============================================================================================
# ----- Lists for use in realtime evaluator for min-max player --------------------------------

weights_list = [
    [8, 85, -40, 10, 210, 520],
    [8, 85, -40, 10, 210, 520],
    [33, -50, -15, 4, 416, 2153],
    [46, -50, -1, 3, 612, 4141],
    [51, -50, 62, 3, 595, 3184],
    [33, -5, 66, 2, 384, 2777],
    [44, 50, 163, 0, 443, 2568],
    [13, 50, 66, 0, 121, 986],
    [4, 50, 31, 0, 27, 192],
    [8, 500, 77, 0, 36, 299]
]

timings_list = [0, 55, 56, 57, 58, 59, 60, 61, 62, 63]


square_static_weights = [
    [100, -10,  8,  6,  6,  8, -10, 100],
    [-10,-250, -4, -4, -4, -4,-250, -10],
    [  8,  -4,  6,  4,  4,  6,  -4,   8],
    [  6,  -4,  4,  0,  0,  4,  -4,   6],
    [  6,  -4,  4,  0,  0,  4,  -4,   6],
    [  8,  -4,  6,  4,  4,  6,  -4,   8],
    [-10,-250, -4, -4, -4, -4,-250, -10],
    [100, -10,  8,  6,  6,  8, -10, 100]
]


class InvalidMoveError(RuntimeError): ...

# ------------------------------------------------------------------------------------------------------
#       Functions to calculate possible moves and the lines of disks captured by these moves
# ======================================================================================================

def find_lines(board, i, j, player):
    """
        Find all the uninterrupted lines of stones that would be captured if player
        plays row i and column j, and returns all these lines in a list.
        Lines can be vertical (up and down), horizontal (left to right and right to left) and diagonal.
    """
    lines = []
    # x_dir and y_dir are variables representing direction of lines on the x axis and y axis
    for x_dir, y_dir in [[0, 1], [1, 1], [1, 0], [1, -1],
                            [0, -1], [-1, -1], [-1, 0], [-1, 1]]:
        line = []
        cur_i = i + y_dir
        cur_j = j + x_dir
        found = False
        while 0 <= cur_i < 8 and 0 <= cur_j < 8:
            if board[cur_i][cur_j] == 0:
                break
            elif board[cur_i][cur_j] == player:
                found = True
                break
            else:
                line.append((cur_i,cur_j))
                cur_i += y_dir
                cur_j += x_dir
        if found and line:
            lines.append(line)
    return lines

def get_possible_moves(board, player):
    """
        Returns moves dictionary of all possible {move: list(lines)} that player can play on
        the current board.
        move: in the form of (row{i}, column{j})
        lines: a list of all uninterrupted lines of stones that would be captured if player
        plays row{i} and column{j}.
    """
    moves = {}
    for i in range(8):
        for j in range(8):
            if board[i][j] == 0:
                lines = find_lines(board, i, j, player)
                if lines:
                    moves[(i,j)] = lines
    return moves


#-------------------------------------------------------------------------------------------------------------
# These functions convert notation to indexes and vice versa to handle game moves and game text
# display + opening move notations
#=============================================================================================================
def notation_to_move(notation: str):
    """
        Converts a notation to indexes. For example: 'C2' => 1, 2
    """
    moves_dict = {
        'a': 0, 'b': 1, 'c': 2, 'd': 3,
        'e': 4, 'f': 5, 'g': 6, 'h': 7
    }
    i = int(notation[1]) - 1
    j = int(moves_dict[notation[0].lower()])
    return i, j

def move_to_notation(i, j, player):
    """
        Converts indexes to a notation. For example: 1, 2 => 'C2'
        The notation is in uppercase if player is 1.
    """
    notation_dict = {
        0: 'a', 1: 'b', 2: 'c', 3: 'd',
        4: 'e', 5: 'f', 6: 'g', 7: 'h'
    }
    notation = notation_dict[j]
    if player == 1:
        notation = notation.upper()
    notation += str(i + 1)
    return notation

# ==============================================================================
# ------- Functions for parsing opening sequences from the opening book --------

def get_openings():
    """
        Function to parse openings from the openings book.
    """
    with open("openings_book.txt") as f:
        lines = f.readlines()
        openings = []
        for line in lines:
            if line[1].isdigit():
                openings.append(line.split('\t')[0])
    return openings

def get_openings_names():
    """
        Function to parse name of openings corresponding to the openings in the
        openings book.
    """
    with open("openings_book.txt") as f:
        lines = f.readlines()
        names = []
        for line in lines:
            if line[1].isdigit():
                names.append(line.split('|')[1].strip())
    return names


# ==============================================================
# -- Functions for simulating a game

def rollout(game, num_sims):
    """
        This function is a vital part of the MCTS algorithm.
        It simulates random games from current state until terminal state.
        game: the current state of the game that we run the simulations on.
        num_sims: the number of games to be simulated.
    """
    turn = game.current_player
    wins, draws, elapsed = 0, 0, 0

    start = time.time()
    for _ in range(num_sims):
        temp_game = simulate_semi_randomly(game)
        if temp_game.winner == turn:
            wins += 1
        if temp_game.winner == 0:
            draws += 1

    elapsed = time.time() - start
    loss = num_sims - wins - draws

    return wins, loss, draws, elapsed

def simulate_randomly(state):
    """
        This is a function that simulates a random selection of moves in a game of Reversi.
        This function is used by the rollout method of MonteCarloPlayer (MCTS algorithm)
    """
    new_state = deepcopy(state)
    possible_moves = get_possible_moves(new_state.board, new_state.current_player)
    while possible_moves:
        random.seed(time.time())
        move = random.choice(list(possible_moves.keys()))
        new_state.play_move(move[0], move[1], possible_moves[move], new_state.current_player)
        new_state.switch_player()
        possible_moves = get_possible_moves(new_state.board, new_state.current_player)
    new_state.switch_player()
    if get_possible_moves(new_state.board, new_state.current_player):
        return simulate_randomly(new_state)
    return new_state

def simulate_semi_randomly(state):
    """
        This is a function that simulates a semi random selection of moves in a game of Reversi.
        It's semi random because when a random move is chosen, if it's adjacent to a corner in
        any direction, we choose a new random move, if it's adjacent to a corner diagonally, we
        choose a new random move.
        This function is used by the rollout method of MonteCarloPlayer (MCTS algorithm)
    """
    new_state = deepcopy(state)
    possible_moves = get_possible_moves(new_state.board, new_state.current_player)
    while possible_moves:
        random.seed(time.time())
        move = random.choice(list(possible_moves.keys()))
        if move in bad_moves or move in very_bad_moves:
            move = random.choice(list(possible_moves.keys()))
            if move in very_bad_moves:
                move = random.choice(list(possible_moves.keys()))
        new_state.play_move(move[0], move[1], possible_moves[move], new_state.current_player)
        new_state.switch_player()
        possible_moves = get_possible_moves(new_state.board, new_state.current_player)
    new_state.switch_player()
    if get_possible_moves(new_state.board, new_state.current_player):
        return simulate_semi_randomly(new_state)
    return new_state



# ==============================================================================================
# -------- Helper functions for realtime evaluator ---------------------------------------------

def get_frontier_squares(board, other_player):
    """
        This function finds all empty squares next to any square occupied by opponent.
    """
    frontier_squares = set()
    for i in range(8):
        for j in range(8):
            if board[i][j] == other_player:
                for dir_y, dir_x in directions:
                    neighbor_i = i + dir_y
                    neighbor_j = j + dir_x
                    if 0 <= neighbor_i <= 7 and 0 <= neighbor_j <= 7 and board[neighbor_i][neighbor_j] == 0:
                        frontier_squares.add((neighbor_i, neighbor_j))
    return frontier_squares

def get_stable_discs(board, player):
    """
        This function finds all the squares we occupy that cannot get captured by the opponent.
    """
    stable_discs = set()
    for i, j in corners:
        if board[i][j] == player:
            # stable_discs.add((i, j))
            for dir_y, dir_x in directions:
                new_i = i + dir_y
                new_j = j + dir_x
                while (
                    0 <= new_i <= 7
                    and 0 <= new_j <= 7
                    and board[new_i][new_j] == player
                    and (new_i, new_j) not in stable_discs
                ):
                    stable_discs.add((new_i, new_j))
                    new_i += dir_y
                    new_j += dir_x
    return stable_discs
