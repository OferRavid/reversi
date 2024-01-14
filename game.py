from time import sleep
from tkinter import BOTH, BOTTOM, INSERT, RIGHT, TOP, Button, Canvas, Entry, Label, StringVar, Text, font
from graphics import Cell, Window, Board


class Player:
    def __init__(self, color, name="Human"):
        self.name = name
        self.color = color

    def find_move(self, manager):
        """
            Returns the move chosen by human player by recognizing clicks on the screen
        """
        pass


class AIPlayer(Player):
    def __init__(self, color, name="AI"):
        super().__init__(color, name)
    
    def find_move(self, manager):
        pass


class Game:
    def __init__(self):
        self.board = [
            [0, 0, 0, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0, 0, 0, 0],
            [0, 0, 0, 2, 1, 0, 0, 0],
            [0, 0, 0, 1, 2, 0, 0, 0],
            [0, 0, 0, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0, 0, 0, 0]
        ]
        self.score = [2, 2]
        self.current_player = 1
        self.move_sequence = ""

    def get_score(self):
        black_score, white_score = 0, 0
        for row in self.board:
            for cell in row:
                if cell == 1:
                    black_score += 1
                elif cell == 2:
                    white_score += 1
        return [black_score, white_score]
    
    def switch_player(self):
        self.current_player = abs(self.current_player - 2) + 1
    
    def switch_disks(self, lines):
        for line in lines:
            for i, j in line:
                self.board[i][j] = self.current_player

    def play_move(self, i, j, lines):
        self.switch_disks(lines)
        self.board[i][j] = self.current_player

    def play_game(self):
        while self.score[0] + self.score[1] < 64:
            player = self.players[self.current_player]
            possible_moves = get_possible_moves(self.board, self.current_player)
            print(possible_moves)
            if not possible_moves:
                self.switch_player()
                if not get_possible_moves(self.board, self.current_player):
                    break
                continue
            i, j = 0, 0
            if player.type == "Human":
                self._canvas.focus_set()
                self._canvas.tag_bind(self._gui_board.rect,"<Button-1>",lambda e: self.mouse_pressed(e))
                i, j = self.current_move
                while (i,j) not in possible_moves:
                    message = f"Invalid move. {player.color} player can't place a disk on this square."
                    print(message)
                    self.name_instruction.configure(text=message)
                    sleep(0.1)
                    self.name_instruction.configure(text="")
                    self._canvas.tag_bind(self._gui_board.rect,"<Button-1>",lambda e: self.mouse_pressed(e))
                    i, j = self.current_move
            else:
                pass
            self.play_move(i, j, possible_moves[(i,j)])
            self.move_count += 1
            self.move_sequence += move_to_notation(i, j, self.current_player)
            self._gui_board.draw_disks()
            self.update_score()
            self.switch_player()
            self.update_text_display()
            self.current_move = None
            
    

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
    notation += str(i)
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

