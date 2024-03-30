import math
from Game.util import *
from Game.game import *


# ===============================================================================================================
# ----------------- These classes define the heuristics of the Min-Max algorithm ---------------------------------
# ---------------------------------------------------------------------------------------------------------------
class Evaluator:
    """
        Interface for evaluator classes.
    """
    def eval(self, board, player):
        pass


class StaticEvaluator(Evaluator):
    """
        The static evaluator is a basic evaluator that calculates the value of a game state using
        the same formula at all stages of the game.
        The formula uses three values that are calculated based of the game state.
    """
    def eval(self, board, player):
        """
            The formula for the evaluation of game state.
        """
        return 2 * self.mobility_evaluation(board, player) + self.disc_difference(board, player) + 1000 * self.corners_evaluation(board, player)
    
    def mobility_evaluation(self, board, player):
        """
            This calculates the mobility of the game state.
            The mobility is a value that represents the player's possible moves vs. the opponent's possible moves.
        """
        other_player = 1 if player == 2 else 2
        player_moves_count = len(get_possible_moves(board, player))
        other_player_moves_count = len(get_possible_moves(board, other_player))
        return 100 * (player_moves_count - other_player_moves_count) / (player_moves_count + other_player_moves_count + 1)

    def disc_difference(self, board, player):
        """
            This calculates state's disc difference between the players.
        """
        other_player = 1 if player == 2 else 2
        game = Game(board)
        player_disc_count = game.player_disk_count(player)
        other_player_disc_count = game.player_disk_count(other_player)
        return 100 * (player_disc_count - other_player_disc_count) / (player_disc_count + other_player_disc_count)

    def corners_evaluation(self, board, player):
        """
            This calculates the state's value based of corners captured by each player.
        """
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
        """
            This method predicts who is supposed to place the last disc given current state's remaining
            empty squares.
            If the amount of remaining squares is even, the function returns -1, otherwise it returns 1.
        """
        remainder = 64 - Game(board).get_total_disk_count()
        return -1 if remainder % 2 == 0 else 1


class DynamicEvaluator(StaticEvaluator):
    """
        This is a dynamic evaluator that uses the evaluation methods inherited from the static evaluator, but
        uses a dynamic formula that calculates the game state value based on the current stage of the game.
    """
    def eval(self, board, player):
        game = Game(board)
        if game.is_game_over():
            return 1000 * self.disc_difference(board, player)
        disc_count = game.get_total_disk_count()
        
        if disc_count < 20:
            return (1000 * self.corners_evaluation(board, player) +
                    50 * self.mobility_evaluation(board, player))
        elif disc_count < 59:
            return (1000 * self.corners_evaluation(board, player) +
                    20 * self.mobility_evaluation(board, player) +
                    10 * self.disc_difference(board, player) +
                    100 * self.remainder_evaluation(board))
        else:
            return (1000 * self.corners_evaluation(board, player) +
                    100 * self.mobility_evaluation(board, player) +
                    500 * self.disc_difference(board, player) +
                    500 * self.remainder_evaluation(board))


class RealtimeEvaluator(StaticEvaluator):
    """
        This evaluator uses a set of weights to calculate a formula that gets updated in realtime
        to get a more accurate value of a game state.
    """
    def __init__(self):
        self.set_weights_for_disc_counts()

    def set_weights_for_disc_counts(self):
        """
            This method creates the list of weights to be used by the evaluator based of amount
            of discs placed on the game's board to help define the realtime formula for each state.
        """
        # initialize a list of lists of weights to be used for each disc count during the game
        self.weights_for_disc_count = []

        # dc: disc count
        for dc in range(65):
            # determine which list of weights to use
            weight = 0
            for i in range(len(timings_list)):
                if dc <= timings_list[i]:
                    weight = i
                    break
            
            if weight == 0:
                self.weights_for_disc_count.append(weights_list[0])
                continue
                
            # linearly interpolate between the list of weights given for the
            # current number of moves and the previous list of weights
            factor = (dc - timings_list[weight - 1]) / (timings_list[weight] - timings_list[weight - 1])
            current_weights = []
            for i in range(len(weights_list[weight])):
                current_weights.append(round(factor * weights_list[weight][i] + (1 - factor) * weights_list[weight - 1][i]))
            self.weights_for_disc_count.append(current_weights)
    
    def eval(self, board, player):
        """
            This calculates the state's value using a realtime formula based of the weights corresponding to state's
            disc count in the list of weights.
            The formula uses some evaluation methods inherited from static evaluator plus several other methods that
            realtime evaluator defines: frontier_evaluation, placement_evaluation, stability_evaluation and
            corner_grab_possibility.
        """
        game = Game(board)
        disc_count = game.get_total_disk_count()

        weights = self.weights_for_disc_count[disc_count]

        return (weights[0] * self.mobility_evaluation(board, player) +
                weights[1] * self.frontier_evaluation(board, player) +
                weights[2] * self.disc_difference(board, player) +
                weights[3] * self.placement_evaluation(board, player) +
                weights[4] * self.stability_evaluation(board, player) +
                weights[5] * self.corner_grab_possibility(board, player)
            )
    
    def frontier_evaluation(self, board, player):
        """
            The frontier is the number of empty squares adjacent to opponent's squares, which represents the
            potential mobility of the player.
            The value is player's frontier in relation to the opponent's frontier.
        """
        other_player = 1 if player == 2 else 2
        player_frontier = get_frontier_squares(board, other_player)
        other_player_frontier = get_frontier_squares(board, player)

        return (
            100 *
            (len(player_frontier) - len(other_player_frontier)) /
            (len(player_frontier) + len(other_player_frontier) + 1)
        )
    
    def placement_evaluation(self, board, player):
        """
            Each square on the board has a value that represents its strength vs. weakness.
            The value is calculated by calculating the value of player's captured squares in relation to the
            value of the opponent's captured squares.
        """
        other_player = 1 if player == 2 else 2
        player_placement_value = 0
        other_player_placement_value = 0
        for i in range(8):
            for j in range(8):
                if board[i][j] == player:
                    player_placement_value += square_static_weights[i][j]
                elif board[i][j] == other_player:
                    other_player_placement_value += square_static_weights[i][j]
        return player_placement_value - other_player_placement_value
    
    def stability_evaluation(self, board, player):
        """
            Calculates the number of stable squares captured by player in relation to number of stable squares
            captured by the opponent.
            Stable squares are squares that cannot be recaptured.
        """
        other_player = 1 if player == 2 else 2
        player_stable_discs_count = len(get_stable_discs(board, player))
        other_player_stable_discs_count = len(get_stable_discs(board, other_player))
        return (
            100 *
            (player_stable_discs_count - other_player_stable_discs_count) /
            (player_stable_discs_count + other_player_stable_discs_count + 1)
        )
    
    def corner_grab_possibility(self, board, player):
        """
            A value representing if the state allows the player to capture a corner.
            Value is 100 if yes and 0 if not.
        """
        moves = list(get_possible_moves(board, player).keys())
        for move in moves:
            if move in corners:
                return 100
        return 0


# ==============================================================================================
# ------------------------------- Monte Carlo Tree Search --------------------------------------
# ----------------------------------------------------------------------------------------------

class MCTSNode:
    """
        A node in the MCTS algorithm.
        Each node represents a state of the game resulted by the move.
        Each node (except root) has a parent node to help propagate up the tree.
        Children are nodes added to the tree using the expand method.
        played is a number representing the number of games simulated on a node or one of its
        descendants.
        wins is the number of simulations resulted in wins for the MCTSPlayer played through node
        or one of its descendants.
    """
    def __init__(self, state:Game, move=None, parent=None):
        self.state = state
        self.move = move
        self.parent = parent
        self.children = []
        self.played = 0
        self.wins = 0

    def expand(self):
        """
            Adding children for a node in the tree by finding the possible moves of the state's
            current player and playing each move on the state to create the new states.
        """
        possible_moves = get_possible_moves(self.state.board, self.state.current_player)

        for move, lines in possible_moves.items():
            child_state = deepcopy(self.state)
            child_state.play_move(move[0], move[1], lines, self.state.current_player)
            self.children.append(MCTSNode(child_state, move, parent=self))
    
    def back_propagate(self, wins, loss, played):
        """
            This method climbs up the tree and updates all nodes on the way by the relevant values.
        """
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
    
    def select_child(self, exploration_param, maximize):
        """
            This method handles the selection stage of the MCTS algorithm.
            maximize is a boolean value that's true if the selection is mid algorithm and false for
            final selection. This is to minimize the exploration vs. exploitation relation.
            Each selection is done by maximizing the Upper Confidence Bound formula on the children of
            current node, the UCB is refined based on several variables:
            - inner_score - higher if the node's move is near the middle of the board and gets lower
                            the farther away from the middle the node's move is.
            - greed_penalty - this value is higher the more squares are captured by the MCTSPlayer by
                            the node's move.
            - move_score - a value representing a great move (corner grab) or a bad/very bad move
                            (a square near a corner).
        """
        index_best_score = 0
        best_ucb_score = None

        if maximize:
            best_ucb_score = float("-inf")
        else:
            best_ucb_score = float("inf")

        for i, child in enumerate(self.children):
            ucb_score = child.calculate_ucb(exploration_param, 3)

            inner_score = ucb_score / math.sqrt((child.move[0] - 3.5) ** 2 + (child.move[1] - 3.5) ** 2)
            
            greed_penalty = ucb_score * (child.state.black_score - self.state.black_score) / (child.state.black_score + child.state.white_score) ** 4
            if self.state.current_player == 2:
                greed_penalty = ucb_score * (child.state.white_score - self.state.white_score) / (child.state.black_score + child.state.white_score) ** 4

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
                    final_ucb_score = ucb_score + inner_score + move_score - greed_penalty
                if final_ucb_score > best_ucb_score:
                    best_ucb_score = final_ucb_score
                    index_best_score = i

            else:
                if child.state.black_score + child.state.white_score > 50:
                    final_ucb_score = ucb_score
                else:
                    final_ucb_score = ucb_score - inner_score - move_score + greed_penalty
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

