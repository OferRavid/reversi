import random
from util import *
from game import AIPlayer
from time import sleep


class RandomPlayer(AIPlayer):
    def __init__(self, color, name="Randy", type="AI"):
        super().__init__(color, name, type)
    
    def find_move(self, game):
        move = self.get_opening_move(game)
        if move:
            return move[0], move[1]
        player = 1
        if self.color == "White":
            player = 2
        possible_moves = get_possible_moves(game.board, player)
        moves = list(possible_moves.keys())
        i, j = moves[random.randint(0, len(moves) - 1)]
        sleep_time = random.random() + random.randint(0,2)
        sleep(sleep_time)
        return i, j