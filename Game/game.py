import random
from time import sleep
from tkinter import BOTH, BOTTOM, INSERT, RIGHT, TOP, Button, Canvas, Entry, Label, StringVar, Text, font
from Game.util import *


class Player:
    """
        The player base class. This is the class to represent human players.
        It's also a template for AI players' classes.
    """
    def __init__(self, color: int, name, type="Human"):
        self.name = name
        self.color = color
        self.type = type

    def find_move(self, game):
        """
            This method isn't used by human players.
            It is only used as template for classes that expands this class to implement.
        """
        pass


class AIPlayer(Player):
    """
        The AI player base class. All AI players expand this class.
    """
    def __init__(self, color: int, name, type="AI"):
        super().__init__(color, name, type)

    def get_opening_move(self, game):
        """
            This method is used by all AI players' classes.
            At the beginning of a game it finds a move according to known
            opening sequences to help with efficiency.
        """
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
        opening = possible_openings[random.randrange(0, len(possible_openings))]
        i, j = notation_to_move(opening[len(sequence): len(sequence) + 2])
        return (i, j)
        

class Game:
    """
        This is the class that defines the game's mechanics.
        board: a list of lists of 0, 1 or 2, representing the game board.
        black_score, white_score: the respective current scores of the players.
        current_player: 1 or 2, representing the player who's placing a move.
        move_sequence: a string of alphanumerics representing the sequence of moves played.
        winner: None (while the game isn't done), 0(draw), 1 or 2. Representing the winner of the game.
    """
    def __init__(self, board=None):
        if board:
            self.board = board
            self.set_score()
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
            self.black_score = 2
            self.white_score = 2
        self.current_player = 1
        self.move_sequence = ""
        self.winner = None
    
    def set_score(self):
        b_score, w_score = 0, 0
        for row in range(8):
            for col in range(8):
                if self.board[row][col] == 1:
                    b_score += 1
                elif self.board[row][col] == 2:
                    w_score += 1
        self.black_score = b_score
        self.white_score = w_score

    def get_score(self):
        return [self.black_score, self.white_score]
    
    def switch_player(self):
        self.current_player = abs(self.current_player - 2) + 1
    
    def flip_disks(self, lines, player):
        """
            Updates the board after move by switching the value in the cells to player.
            player: 1 or 2. The player who placed the move.
        """
        for line in lines:
            for i, j in line:
                self.board[i][j] = player
                if player == 1:
                    self.black_score += 1
                    self.white_score -= 1
                else:
                    self.black_score -= 1
                    self.white_score += 1
    
    def player_disk_count(self, player):
        disks = 0
        for row in self.board:
            for square in row:
                if square == player:
                    disks += 1
        return disks
    
    def get_total_disk_count(self):
        return self.player_disk_count(1) + self.player_disk_count(2)

    def play_move(self, i, j, lines, player):
        """
            Plays a move by updating the board and scores.
            After placing the move, adds it to the move sequence.
            Updates current_player to other player.
            If game is over, it sets the winner.
        """
        self.flip_disks(lines, player)
        self.board[i][j] = player
        if player == 1:
            self.black_score += 1
        else:
            self.white_score += 1
        notation = move_to_notation(i, j, player)
        self.move_sequence += notation
        self.switch_player()
        if self.is_game_over():
            self.set_winner()
    
    def play(self, i, j, player, color):
        """
            If the move is valid it plays it, otherwise raises relevant exception.
            Returns the lines of cells on the board captured by the move.
        """
        if self.board[i][j] != 0:
            raise InvalidMoveError("Square is already taken.")
        lines = find_lines(self.board, i, j, player)
        if not lines:
            raise InvalidMoveError(f"{color} player isn't allowed to place a disk in this square.")
        self.play_move(i, j, lines, player)
        return lines
    
    def is_game_over(self):
        return (
            self.get_total_disk_count() == 64
            or (
                not get_possible_moves(self.board, 1)
                and
                not get_possible_moves(self.board, 2)
            )
        )
    
    def set_winner(self):
        if self.black_score > self.white_score:
            self.winner = 1
        elif self.black_score < self.white_score:
            self.winner = 2
        else:
            self.winner = 0

    def __repr__(self) -> str:
        board = ""
        for row in self.board:
            board += f"\n{str(row)}"
        return board
    
    def play_game(self):
        """
            This is a simple game for the console for 2 human players.
        """
        while self.winner is None:
            print(self)
            if self.current_player == 1:
                print("Black's turn...")
            else:
                print("White's turn...")
            print(
                "Choose a move from: ",
                set(
                    [move_to_notation(move[0], move[1], self.current_player)
                    for move in list(get_possible_moves(self.board, self.current_player).keys())]
                )
            )
                
            try:
                move_input = input("Enter your choice (e.g., 'A1'): ")
                i, j = notation_to_move(move_input)
                color = "Black" if self.current_player == 1 else "White"
                self.play(i, j, self.current_player, color)
            except KeyError:
                print("Invalid input. Please enter a valid move.")
            except InvalidMoveError as e:
                print(str(e))
            except IndexError:
                print("Invalid input. Please enter a valid move.")
            except:
                print("An error occurred. Please try again.")
        print(self)
        if self.winner == 1:
            print("Black wins!")
        elif self.winner == 2:
            print("White wins!")
        else:
            print("It's a draw!")

if __name__ == "__main__":
    board = Game()
    board.play_game()
