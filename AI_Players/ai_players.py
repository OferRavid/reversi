from copy import deepcopy
import math
from Game.game import *
from Game.util import *
import random
from AI_Players.ai_helper import *


class RandomPlayer(AIPlayer):
    """
        An AI player for the Reversi game that plays random moves.
    """
    def __init__(self, color: int, name="RandomPlayer", type="AI"):
        super().__init__(color, name, type)
    
    def find_move(self, game):
        possible_moves = get_possible_moves(game.board, self.color)
        moves = list(possible_moves.keys())
        i, j = moves[random.randrange(0, len(moves))]
        return i, j


class GreedyPlayer(AIPlayer):
    """
        An AI player for the Reversi game that chooses the move that captures the most squares.
    """
    def __init__(self, color: int, name="GreedyPlayer", type="AI"):
        super().__init__(color, name, type)

    def find_move(self, game:Game):
        best_move = None
        disk_amount = 0
        possible_moves = get_possible_moves(game.board, self.color)
        cur_discs = game.player_disk_count(self.color)
        for move, lines in possible_moves.items():
            amount = cur_discs + sum([len(line) for line in lines])
            # game_copy = copy.deepcopy(game)
            # game_copy.play_move(move[0], move[1], lines, self.color)
            # amount = game_copy.player_disk_count(self.color)
            if amount > disk_amount:
                best_move = move
                disk_amount = amount
        return best_move


class MinimaxPlayer(AIPlayer):
    """
        An AI player for the Reversi game that chooses a move according to the Min-Max algorithm
        with alpha-beta pruning.
        Before choosing a move according to the Min-Max algorithm, the player attempts to find a strong move.
        A strong move is a corner grab and/or a move that blocks the opponent from placing discs.
        evaluator: is the heuristic the player uses to evaluate a game state.
        depth: defines the max depth of the tree the algorithm explores children nodes.
    """
    def __init__(self, color: int, name="MinimaxPlayer", type="AI", evaluator=StaticEvaluator(), depth=6):
        super().__init__(color, name, type)
        self.evaluator = evaluator
        self.depth = depth
    
    def find_move(self, game):
        move = self.get_opening_move(game)
        if move:
            return move
        move = self.get_strong_move(game.board, game.current_player)
        if move:
            return move
        possible_moves = get_possible_moves(game.board, game.current_player)
        best_move_score = float("-inf")
        best_move = None
        for move, lines in possible_moves.items():
            temp_game = Game(deepcopy(game.board))
            temp_game.play_move(move[0], move[1], lines, game.current_player)
            new_board = temp_game.board
            move_score = self.min_max_alpha_beta(new_board, game.current_player, self.depth, False, float("-inf"), float("inf"))
            if move_score > best_move_score:
                best_move_score = move_score
                best_move = move
        return best_move
    
    def min_max_alpha_beta(self, board, player, depth, max, alpha, beta):
        game = Game(board)
        if depth == 0 or game.is_game_over():
            return self.evaluator.eval(board, player)
        
        possible_moves = {}
        other_player = 1 if player == 2 else 2
        if max:
            possible_moves = get_possible_moves(board, player)
        else:
            possible_moves = get_possible_moves(board, other_player)
        if not possible_moves:
            return self.min_max_alpha_beta(board, player, depth - 1, not max, alpha, beta)
        score = float("-inf") if max else float("inf")
        
        for move, lines in possible_moves.items():
            temp_game = Game(deepcopy(game.board))
            temp_game.play_move(move[0], move[1], lines, player if max else other_player)
            new_board = temp_game.board
            move_score = self.min_max_alpha_beta(new_board, player, depth - 1, not max, alpha, beta)
            if max:
                if move_score > score:
                    score = move_score
                if score > alpha:
                    alpha = score
            else:
                if move_score < score:
                    score = move_score
                if score < beta:
                    beta = score
            if beta <= alpha:
                break
        return score
    
    def get_strong_move(self, board, player):
        """
            This method iterates over the possible moves to check if a strong move is available.
            If such a move is possible, the moves value is calculated and the move with the max value
            is chosen.
            THe algorithm looks for strong moves in this order:
            1. A corner grab and blocking move.
            2. A corner grab move.
            3. A blocking move.
            If none of them is possible, it will find a move using the Min-Max algorithm.
        """
        possible_moves = get_possible_moves(board, player)
        corner_move, blocker_move = None, None
        best_corner, best_blocker = float("-inf"), float("-inf")
        for move, lines in possible_moves.items():
            temp_board = deepcopy(board)
            temp_game = Game(temp_board)
            temp_game.play_move(move[0], move[1], lines, player)
            if move in corners:
                move_value = self.evaluator.eval(temp_game.board, player)
                if move_value > best_corner:
                    best_corner = move_value
                    corner_move = move
            other_player = 1 if player == 2 else 2
            if len(get_possible_moves(temp_game.board, other_player)) == 0:
                move_value = self.evaluator.eval(temp_game.board, player)
                if move_value > best_blocker:
                    best_blocker = move_value
                    blocker_move = move
                    if blocker_move == corner_move:
                        return blocker_move
        if corner_move:
            return corner_move
        if blocker_move:
            return blocker_move
        return None


class MCTSPlayer(AIPlayer):
    """
        An AI player for the Reversi game that finds a move using the Monte Carlo Tree Search algorithm.
    """
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
        random.seed(time.time())
        current_node = root.children[random.randrange(0, len(root.children))]
        wins, loss, _, total_elapsed = rollout(current_node.state, self.num_sims)
        current_node.back_propagate(wins, loss, self.num_sims)
        exploration_param = self.num_sims

        for i in range(self.max_iter):
            current_node = root.select_child(exploration_param, maximize=True)
            while current_node.children:
                current_node = current_node.select_child(exploration_param, maximize=True)
            if current_node.played != 0:
                current_node.expand()
                if current_node.children:
                    current_node = current_node.select_child(exploration_param, maximize=True)
            wins, loss, _, elapsed = rollout(current_node.state, self.num_sims)
            total_elapsed += elapsed
            exploration_param += self.num_sims
            current_node.back_propagate(wins, loss, self.num_sims)
            exploration_param += self.num_sims
            if total_elapsed > 1.0:
                break
        child = root.select_child(0, maximize=False)
        move = child.move
        return move

