from copy import deepcopy
import math
import time
from game import *
from util import *
from node import *
import random


class RandomPlayer(AIPlayer):
    def __init__(self, color: int, name="RandomPlayer", type="AI", is_simulation=False):
        super().__init__(color, name, type)
        self.is_simulation = is_simulation
    
    def find_move(self, game):
        possible_moves = get_possible_moves(game.board, self.color)
        moves = list(possible_moves.keys())
        i, j = moves[random.randint(0, len(moves) - 1)]
        return i, j


class GreedyPlayer(AIPlayer):
    def __init__(self, color: int, name="GreedyPlayer", type="AI"):
        super().__init__(color, name, type)

    def find_move(self, game):
        best_move = None
        disk_amount = 0
        possible_moves = get_possible_moves(game.board, self.color)
        for move, lines in possible_moves.items():
            game_copy = copy.deepcopy(game)
            game_copy.play_move(move[0], move[1], lines, self.color)
            amount = game_copy.count_disks(self.color)
            if amount > disk_amount:
                best_move = move
                disk_amount = amount
        return best_move


directions = [[1, 0], [1, 1], [1, -1], [0, 1], [-1, 1], [-1, -1], [-1, 0], [0, -1]]


class MinimaxPlayer(AIPlayer):
    def __init__(self, color: int, name="MinimaxPlayer", type="AI"):
        super().__init__(color, name, type)
    
    def get_potential_mobility(self, i, j, node):
        empty_count = 0
        for diry, dirx in directions:
            if node.board[i + diry][j + dirx] == 0:
                empty_count += 1
        
    
    def mobility(self, node: Node):
        node.get_children()
        mobility = len(node.children)
        for child in node.children:
            for i in range(8):
                for j in range(8):
                    if child.board[i][j] == child.player:
                        mobility -= self.get_potential_mobility(i, j, child)
                    if child.board[i][j] == 0:
                        continue
                    else:
                        mobility += self.get_potential_mobility(i, j, child)
        return mobility
    
    def stability(self, node: Node):

        return


class MCTSNode:
    def __init__(self, state:Game, move=None, parent=None, depth=0):
        self.state = state
        self.move = move
        self.parent = parent
        self.children = []
        self.played = 0
        self.wins = 0
        self.depth = depth

    def expand(self):
        possible_moves = get_possible_moves(self.state.board, self.state.current_player)

        for move, lines in possible_moves.items():
            child_state = deepcopy(self.state)
            child_state.play_move(move[0], move[1], lines, self.state.current_player)
            self.children.append(MCTSNode(child_state, move, parent=self, depth=self.depth + 1))
    
    def back_propagate(self, wins, loss, played):
        player = self.state.current_player
        self.wins += wins
        self.played += played
        parent = self.parent
        while parent:
            if parent.state.current_player == player:
                parent.wins += wins
            else:
                parent.wins += loss
            parent.played += played
            parent = parent.parent
    
    def select_child(self, exploraition_param, maximize):
        index_best_score = 0
        best_ucb_score = None

        if maximize:
            best_ucb_score = float("-inf")
        else:
            best_ucb_score = float("inf")

        for i, child in enumerate(self.children):
            ucb_score = child.calculate_ucb(exploraition_param, 3)

            inner_score = ucb_score / math.sqrt((child.move[0] - 3.5) ** 2 + (child.move[1] - 3.5) ** 2)
            
            greedPenalty = ucb_score * (child.state.black_score - self.state.black_score) / (child.state.black_score + child.state.white_score) ** 4
            if self.state.current_player == 2:
                greedPenalty = ucb_score * (child.state.white_score - self.state.white_score) / (child.state.black_score + child.state.white_score) ** 4

            move_score = 0.00
            if child.move in corners:
                move_score = ucb_score * 1.5
            if child.move in bad_moves:
                move_score = ucb_score * (-0.55)
            if child.move in very_bad_moves:
                move_score = ucb_score * (-100)

            if maximize:
                if child.state.black_score + child.state.white_score > 50:
                    final_ucb_score = ucb_score
                else:
                    final_ucb_score = ucb_score + inner_score + move_score - greedPenalty
                if final_ucb_score > best_ucb_score:
                    best_ucb_score = final_ucb_score
                    index_best_score = i

            else:
                if child.state.black_score + child.state.white_score > 50:
                    final_ucb_score = ucb_score
                else:
                    final_ucb_score = ucb_score - inner_score - move_score + greedPenalty
                if final_ucb_score < best_ucb_score and child.played > 0:
                    best_ucb_score = final_ucb_score
                    index_best_score = i

        return self.children[index_best_score]
    
    def calculate_ucb(self, num_games, c_param=3):
        return (
            (self.wins / (self.played + 1))
            + math.sqrt(c_param)
            * math.sqrt(math.log(num_games + 1) / (self.played + 1))
        )


class MCTSPlayer(AIPlayer):
    def __init__(self, color: int, name="MCTSPlayer", type="AI", num_sims=20, max_iter=300):
        super().__init__(color, name, type)
        self.num_sims = num_sims
        self.max_iter = max_iter
    
    def find_move(self, game:Game):
        move = self.get_opening_move(game)
        if move:
            return move
        root = MCTSNode(game)
        root.expand()
        current_node = root.select_child(0, maximize=False)
        wins, loss, _, total_elapsed = rollout(current_node.state, self.num_sims)
        current_node.back_propagate(wins, loss, self.num_sims)
        exploraition_param = self.num_sims

        for i in range(self.max_iter):
            current_node = root.select_child(exploraition_param, maximize=True)
            while current_node.children:
                current_node = current_node.select_child(exploraition_param, maximize=True)
            if current_node.played != 0:
                current_node.expand()
                if current_node.children:
                    current_node = current_node.select_child(exploraition_param, maximize=True)
            wins, loss, _, elapsed = rollout(current_node.state, self.num_sims)
            total_elapsed += elapsed
            exploraition_param += self.num_sims
            current_node.back_propagate(wins, loss, self.num_sims)
            exploraition_param += self.num_sims
            if total_elapsed > 1.0:
                break
        child = root.select_child(0, maximize=False)
        move = child.move
        return move

# ==============================================================
# -- Functions for simulating game

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


def rollout(game:Game, num_sims):
    turn = game.current_player
    wins, draws, elapsed = 0, 0, 0

    start = time.time()
    for _ in range(num_sims):
        temp_game = sim_semi_rand(game)
        if temp_game.winner == turn:
            wins += 1
        if temp_game.winner == 0:
            draws += 1

    elapsed = time.time() - start
    loss = num_sims - wins - draws

    return wins, loss, draws, elapsed

def sim_rand(state:Game):
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
        return sim_rand(new_state)
    return new_state

def sim_semi_rand(state:Game):
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
        return sim_semi_rand(new_state)
    return new_state