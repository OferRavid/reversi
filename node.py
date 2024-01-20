from game import Game
from util import *
import copy


class Node:
    def __init__(self, board, player, parent=None):
        self.board = board
        self.player = player
        self.parent = parent
        self.children = []
        self.value = 0
        self.set_value()
    
    def set_value(self):
        for row in self.board:
            for square in row:
                if square == self.player:
                    self.value += 1
                elif square == 0:
                    continue
                else:
                    self.value -= 1
    
    def get_children(self):
        next_player = abs(self.player - 2) + 1
        for move, lines in get_possible_moves(self.board, self.player).items():
            board_copy = copy.deepcopy(self.board)
            game = Game(board_copy)
            game.play_move(move[0], move[1], lines, self.player)
            child = Node(game.board, next_player, self)
            self.children.append(child)
    
    def get_min_child(self):
        if self.children == []:
            return
        return min(self.children, key=lambda x: x.value)
    
    def get_max_child(self):
        if self.children == []:
            return
        return max(self.children, key=lambda x: x.value)
    
    def __repr__(self) -> str:
        board = ""
        for row in self.board:
            board += f"\n{str(row)}"
        return board

