import random
from time import sleep
from tkinter import BOTH, BOTTOM, INSERT, RIGHT, TOP, Button, Canvas, Entry, Label, StringVar, Text, font
from util import *


class Player:
    def __init__(self, color: int, name, type="Human"):
        self.name = name
        self.color = color
        self.type = type

    def find_move(self, game):
        """
            Returns the move chosen by human player by recognizing clicks on the screen
        """
        pass


class AIPlayer(Player):
    def __init__(self, color: int, name, type="AI"):
        super().__init__(color, name, type)
    
    def find_move(self, game):
        pass

    def get_opening_move(self, game):
        sequence = game.move_sequence
        openings = get_openings()
        possible_openings = []
        if not sequence:
            possible_openings = openings
        else:
            for opening in openings:
                if opening.startswith(sequence) and opening != sequence:
                    possible_openings.append(opening)
        if not possible_openings:
            return None
        opening = possible_openings[random.randint(0, len(possible_openings) - 1)]
        i, j = notation_to_move(opening[len(sequence): len(sequence) + 2])
        return (i, j)
        

class Game:
    def __init__(self, board=None):
        if board:
            self.board = board
        else:
            self.board = [
                [0, 0, 0, 0, 0, 0, 0, 0],
                [0, 0, 0, 0, 0, 0, 0, 0],
                [0, 0, 0, 0, 0, 0, 0, 0],
                [0, 0, 0, 2, 1, 0, 0, 0],
                [0, 0, 0, 1, 2, 0, 0, 0],
                [0, 0, 0, 0, 0, 0, 0, 0],
                [0, 0, 0, 0, 0, 0, 0, 0],
                [0, 0, 0, 0, 0, 0, 0, 0],
            ]
        self.score = [2, 2]
        self.current_player = 1
        self.move_sequence = ""

    def get_score(self):
        return self.score
    
    def switch_player(self):
        self.current_player = abs(self.current_player - 2) + 1
    
    def flip_disks(self, lines, player):
        for line in lines:
            for i, j in line:
                self.board[i][j] = player
                self.score[player - 1] += 1
                other_player = abs(player - 2)
                self.score[other_player] -= 1

    def play_move(self, i, j, lines, player):
        self.flip_disks(lines, player)
        self.board[i][j] = player
        self.score[player - 1] += 1
        notation = move_to_notation(i, j, player)
        self.move_sequence += notation
    
    def play(self, i, j, player, color):
        if self.board[i][j] != 0:
            raise InvalidMoveError("Square is already taken.")
        lines = find_lines(self.board, i, j, player)
        if not lines:
            raise InvalidMoveError(f"{color} player isn't allowed to place a disk in this square.")
        self.play_move(i, j, lines, player)
        return lines

    def __repr__(self) -> str:
        board = ""
        for row in self.board:
            board += f"\n{str(row)}"
        return board
