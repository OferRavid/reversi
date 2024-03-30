import unittest
from Game.game import *
from AI_Players.ai_players import *
from GUI.graphics import Board
from Game.util import *


class Tests(unittest.TestCase):
    # =========================
    # -------- Testing gui's board

    def test_board_draw_grid(self):
        board = Board()
        cells = board.get_cells()
        self.assertEqual(8, len(cells))
        self.assertEqual(8, len(cells[0]))
        for row in cells:
            for cell in row:
                self.assertIn(cell.owner, [0, 1, 2])
    
    def test_board_draw_disks(self):
        board = Board()
        disks = board.get_disks()
        self.assertEqual(8, len(disks))
        self.assertEqual(8, len(disks[0]))
        for row in disks:
            for disk in row:
                self.assertTrue(disk._color == "#00C957"
                                or disk._color == "black"
                                or disk._color == "white")
    
    def test_board_flip_disks(self):
        p1, p2 = RandomPlayer(1), RandomPlayer(2)
        board = Board(player1=p1,player2=p2)
        game = Game()
        player = board.current_player
        moves = get_possible_moves(game.board, player)
        for move, lines in moves.items():
            board_copy = deepcopy(board)
            cells = board_copy.get_cells()
            board_copy.flip_disks(move[0], move[1], lines)
            for line in lines:
                for i, j in line:
                    self.assertEqual(cells[i][j].owner, player)
            self.assertEqual(cells[move[0]][move[1]].owner, player)
    
    def test_board_switch_player(self):
        p1, p2 = RandomPlayer(1), RandomPlayer(2)
        board = Board(player1=p1,player2=p2)
        other_player = abs(board.current_player - 2) + 1
        board.switch_player()
        self.assertEqual(board.current_player, other_player)

    def test_board_play_move(self):
        p1, p2 = RandomPlayer(1), RandomPlayer(2)
        board = Board(player1=p1,player2=p2)
        game = Game()
        player = board.current_player
        moves = get_possible_moves(game.board, player)
        for move, lines in moves.items():
            board_copy = deepcopy(board)
            cells = board_copy.get_cells()
            game_copy = deepcopy(game)
            board_copy.play_move(move[0], move[1], game_copy, "Black")
            for line in lines:
                for i, j in line:
                    self.assertEqual(cells[i][j].owner, player)
            self.assertEqual(cells[move[0]][move[1]].owner, player)
            self.assertEqual(board_copy.score, [4, 1])
            self.assertEqual(board_copy.move_count, 1)
            self.assertEqual(board_copy.move_sequence, move_to_notation(move[0], move[1], player))
            self.assertEqual(board_copy.current_player, 2)
    
    def test_board_game(self):
        p1, p2 = RandomPlayer(1), RandomPlayer(2)
        board = Board(player1=p1,player2=p2)
        game = Game()
        result = board.play(game)
        self.assertIn(result, [0, 1, 2])
    
    # ============================
    # --------- Testing game
    
    def test_game_set_score(self):
        board = [
            [0, 0, 0, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0, 0, 0, 0],
            [0, 0, 2, 1, 0, 0, 0, 0],
            [0, 0, 2, 1, 1, 0, 0, 0],
            [0, 0, 2, 2, 1, 0, 0, 0],
            [0, 0, 1, 0, 2, 1, 0, 0],
            [0, 0, 0, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0, 0, 0, 0],
        ]
        game = Game(board)
        self.assertEqual(game.black_score, 6)
        self.assertEqual(game.white_score, 5)
    
    def test_game_switch_player(self):
        game = Game()
        other_player = abs(game.current_player - 2) + 1
        game.switch_player()
        self.assertEqual(game.current_player, other_player)
    
    def test_game_flip_disks(self):
        game = Game()
        player = game.current_player
        moves = get_possible_moves(game.board, player)
        for _, lines in moves.items():
            game_copy = deepcopy(game)
            game_copy.flip_disks(lines, player)
            for line in lines:
                for i, j in line:
                    self.assertEqual(game_copy.board[i][j], player)
    
    def test_game_play_move(self):
        game = Game()
        player = game.current_player
        moves = get_possible_moves(game.board, player)
        move = random.choice(list(moves.keys()))
        game.play_move(move[0], move[1], moves[move], player)
        for line in moves[move]:
                for i, j in line:
                    self.assertEqual(game.board[i][j], player)
        self.assertEqual(game.board[move[0]][move[1]], player)
        self.assertEqual(game.black_score, 4)
        self.assertEqual(game.white_score, 1)
        self.assertEqual(game.move_sequence, move_to_notation(move[0], move[1], player))
        self.assertFalse(player == game.current_player)
        self.assertFalse(game.is_game_over())
    
    def test_game_set_winner(self):
        board1 = [
            [0, 0, 0, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0, 0, 0, 0],
            [0, 0, 1, 1, 0, 0, 0, 0],
            [0, 0, 1, 1, 1, 0, 0, 0],
            [0, 0, 1, 1, 1, 0, 0, 0],
            [0, 0, 1, 0, 1, 1, 0, 0],
            [0, 0, 0, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0, 0, 0, 0],
        ]
        board2 = [
            [1, 1, 1, 1, 1, 1, 1, 1],
            [1, 1, 1, 1, 1, 2, 2, 2],
            [1, 1, 1, 1, 1, 2, 2, 2],
            [1, 1, 1, 1, 1, 2, 2, 2],
            [2, 2, 2, 2, 1, 2, 2, 2],
            [2, 2, 2, 2, 2, 2, 2, 2],
            [2, 2, 2, 2, 2, 2, 2, 2],
            [2, 2, 2, 2, 2, 2, 2, 2],
        ]
        game1 = Game(board1)
        game2 = Game(board2)
        self.assertTrue(game1.is_game_over())
        self.assertTrue(game2.is_game_over())
        game1.set_winner()
        game2.set_winner()
        self.assertEqual(game1.winner, 1)
        self.assertEqual(game2.winner, 2)


if __name__ == "__main__":
    unittest.main()