class InvalidMoveError(RuntimeError): ...

# ------------------------------------------------------------------------------------------------------
#       Functions to calculate possible moves and the lines of disks captured by these moves
# ======================================================================================================

def find_lines(board, i, j, player):
    """
        Find all the uninterupted lines of stones that would be captured if player
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
        Returns moves dictionary of all possible {(row,column): [lines]} that player can play on
        the current board. 
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
# These functions help the game to follow after the opening moves to make it easier and faster to find a move.
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

def get_openings():
    with open("opening_moves.txt") as f:
        lines = f.readlines()
        openings = []
        for line in lines:
            if line[1].isdigit():
                openings.append(line.split('\t')[0])
    return openings

def get_openings_names():
    with open("opening_moves.txt") as f:
        lines = f.readlines()
        names = []
        for line in lines:
            if line[1].isdigit():
                names.append(line.split('|')[1].strip())
    return names

