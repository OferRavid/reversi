from time import sleep
from tkinter import BOTH, BOTTOM, INSERT, RIGHT, TOP, Button, Canvas, Entry, Label, StringVar, Text, font
from util import *

class Player:
    def __init__(self, color, name, type="Human"):
        self.name = name
        self.color = color
        self.type = type

    def find_move(self, manager):
        """
            Returns the move chosen by human player by recognizing clicks on the screen
        """
        pass


class AIPlayer(Player):
    def __init__(self, color, name, type="AI"):
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
    
    def flip_disks(self, lines):
        for line in lines:
            for i, j in line:
                self.board[i][j] = self.current_player

    def play_move(self, i, j, lines):
        self.flip_disks(lines)
        self.board[i][j] = self.current_player
    
    def play(self, i, j, player, color):
        if self.board[i][j] != 0:
            raise InvalidMoveError("Square is already taken.")
        lines = find_lines(self.board, i, j, player)
        if not lines:
            raise InvalidMoveError(f"{color} player isn't allowed to place disk in this square.")
        self.play_move(i, j, lines)
        return lines


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
            
            self._gui_board.draw_disks()
            self.update_score()
            self.switch_player()
            self.update_text_display()
            self.current_move = None
            
    

