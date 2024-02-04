from graphics import Window, Board
from ai_players import *
from game import *

def main():
    win = Window()
    win.wait_for_close()
    # p1 = GreedyPlayer(1)
    # p2 = MCTSPlayer(2,"MCTSPlayer", "AI", 20, 30)
    # results = [0, 0, 0]
    # num_games = 10
    # for i in range(num_games):
    #     print(f"Playing game {i + 1} between greedy and MCTS players.")
    #     board = Board(player1=p1, player2=p2)
    #     game = Game()
    #     result = board.play(game)
    #     results[result] += 1
    # print(f"After {num_games} games between greedy and MCTS players. Here are the results:")
    # print(f"- {results[0]} games ended in a draw.")
    # print(f"- greedy player won {results[1]} games.")
    # print(f"- mcts player won {results[2]} games.")

main()
