import math
from util import *
from game import *


class Evaluator:
    def eval(self, board, player):
        pass


class StaticEvaluator(Evaluator):
    def eval(self, board, player):
        return 2 * self.mobility_evaluation(board, player) + self.disc_difference(board, player) + 1000 * self.corners_evaluation(board, player)
    
    def mobility_evaluation(self, board, player):
        other_player = 1 if player == 2 else 2
        player_moves_count = len(get_possible_moves(board, player))
        other_player_moves_count = len(get_possible_moves(board, other_player))
        return 100 * (player_moves_count - other_player_moves_count) / (player_moves_count + other_player_moves_count + 1)

    def disc_difference(self, board, player):
        other_player = 1 if player == 2 else 2
        game = Game(board)
        player_disc_count = game.player_disk_count(player)
        other_player_disc_count = game.player_disk_count(other_player)
        return 100 * (player_disc_count - other_player_disc_count) / (player_disc_count + other_player_disc_count)

    def corners_evaluation(self, board, player):
        other_player = 1 if player == 2 else 2
        player_corners = 0
        other_player_corners = 0
        for i, j in corners:
            if board[i][j] == player:
                player_corners += 1
            elif board[i][j] == other_player:
                other_player_corners += 1
        return 100 * (player_corners - other_player_corners) / (player_corners + other_player_corners + 1)
    
    def remainder_evaluation(self, board):
        remainder = 64 - Game(board).get_total_disk_count()
        return -1 if remainder % 2 == 0 else 1


class DynamicEvaluator(StaticEvaluator):
    def eval(self, board, player):
        game = Game(board)
        if game.is_game_over():
            return 1000 * self.disc_difference(board, player)
        disc_count = game.get_total_disk_count()
        
        if disc_count < 24:
            return (1000 * self.corners_evaluation(board, player) + 
                    self.mobility_evaluation(board, player))
        elif disc_count < 54:
            return (1000 * self.corners_evaluation(board, player) + 
                    20 * self.mobility_evaluation(board, player) +
                    10 * self.disc_difference(board, player) +
                    100 * self.remainder_evaluation(board))
        else:
            return (1000 * self.corners_evaluation(board, player) + 
                    100 * self.mobility_evaluation(board, player) +
                    500 * self.disc_difference(board, player) +
                    500 * self.remainder_evaluation(board))


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