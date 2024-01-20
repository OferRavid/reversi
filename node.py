from game import Game
from util import *
import copy


class Node:
    def __init__(self, board, player, parent=None):
        self.board = board
        self.player = player
        self.parent = parent
        self.value = 0
        self.set_value()
    
    def set_value(self):
        for row in self.board:
            for square in row:
                if square == self.player:
                    self.value += 1
    
    def get_children(self):
        self.children = []
        next_player = abs(self.player - 2) + 1
        for move, lines in get_possible_moves(self.board, self.player).items():
            board_copy = copy.deepcopy(self.board)
            game = Game(board_copy)
            game.play_move(move[0], move[1], lines, self.player)
            child = Node(game.board, next_player, self)
            self.children.append(child)
    
    def print_board(self):
        for row in self.board:
            print(row)
