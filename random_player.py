import random
from util import *
from game import AIPlayer
from time import sleep


class RandomPlayer(AIPlayer):
    def __init__(self, color: int, name="Randy", type="AI", is_simulation=False):
        super().__init__(color, name, type)
        self.is_simulation = is_simulation
    
    def find_move(self, game):
        move = self.get_opening_move(game)
        if move:
            return move[0], move[1]
        possible_moves = get_possible_moves(game.board, self.color)
        moves = list(possible_moves.keys())
        i, j = moves[random.randint(0, len(moves) - 1)]
        if not self.is_simulation:
            sleep_time = random.random() + random.randint(0,2)
            sleep(sleep_time)
        return i, j