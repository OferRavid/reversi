import os
from tkinter import *
from tkinter import simpledialog
from PIL import Image, ImageTk
from Game.game import *
from Game.util import *
import datetime
from AI_Players.ai_players import *
from time import sleep
import random
from AI_Players.ai_helper import *


# ------------- classes definitions for maintaining the graphics

class Point:
    """
        Class for a point object
    """
    def __init__(self, x, y):
        self.x = x
        self.y = y


class Line:
    def __init__(self, p1: Point, p2: Point):
        self.p1 = p1
        self.p2 = p2
    
    def draw(self, canvas: Canvas, fill_color="black"):
        """
            Method to draw a line on a tkinter canvas.
        """
        x1 = self.p1.x
        y1 = self.p1.y
        x2 = self.p2.x
        y2 = self.p2.y
        canvas.create_line(x1, y1, x2, y2, fill=fill_color, width=3)
        canvas.pack(fill=BOTH, expand=1)


class Disk:
    def __init__(self, center: Point, radius, color):
        self._x = center.x
        self._y = center.y
        self._r = radius
        self._color = color
    
    def draw(self, canvas:Canvas):
        """
            Method for drawing disk on a tkinter canvas.
        """
        canvas.create_oval(
            self._x - self._r,
            self._y - self._r,
            self._x + self._r,
            self._y + self._r,
            outline=self._color,
            fill=self._color
        )
        canvas.pack(fill=BOTH, expand=1)
    
    def __repr__(self):
        return f"Center is: Point({self._x},{self._y}), radius is: {self._r}, color is: {self._color}"


class Cell:
    """
        Class for a cell in a Reversi board.
        Using 4 given values we define 4 lines: bottom, top, left and right.
    """
    def __init__(self, x1, y1, x2, y2):
        self._x1 = x1
        self._y1 = y1
        self._x2 = x2
        self._y2 = y2
        self.owner = 0
        self._top = Line(Point(x1, y1), Point(x2, y1))
        self._bottom = Line(Point(x1, y2), Point(x2, y2))
        self._left = Line(Point(x1, y1), Point(x1, y2))
        self._right = Line(Point(x2, y1), Point(x2, y2))
    
    def draw(self, canvas: Canvas):
        """
            Method to draw the cell on a tkinter canvas.
        """
        self._top.draw(canvas)
        self._bottom.draw(canvas)
        self._left.draw(canvas)
        self._right.draw(canvas)

    # def in_cell(self, x, y):
    #     return self._x1 <= x <= self._x2 and self._y1 <= y <= self._y2


# =========================================================================================
# -------------- The window class manages the Gui for the game
    
class Window:
    """
        This is the class that defines the gui window.
        Using tkinter we define a window with canvas and menubar for the Reversi game.
    """
    def __init__(self):
        self.__root = Tk()
        self.__root.title("Reversi")
        self.__root.resizable(False, False)
        self.__right = Frame(self.__root, bg="#CCCCCC", width=200)
        self.__right.pack(side=RIGHT, fill=BOTH)
        self.f_canvas = Canvas(self.__right, bg="#CCCCCC", width=160, height=400)
        self.f_canvas.pack(side=TOP, fill=BOTH, expand=True)
        self.height = 750
        self.width = 750
        self.__canvas = Canvas(self.__root, width=self.width, height=self.height)
        self.__canvas.pack(fill=BOTH)
        self.score_text = None
        self.__board = Board(self)
        self.manage_menubar()
        
        self.__running = False
        self.__root.protocol("WM_DELETE_WINDOW", self.close)

    # -------------- Methods for operating the window
    def redraw(self):
        self.__root.update_idletasks()
        self.__root.update()
    
    def wait_for_close(self):
        self.__running = True
        while self.__running:
            self.redraw()
        print("We hope you enjoyed playing Reversi! Goodbye...")
    
    def close(self):
        self.__running = False
        # self.save_game()
    
    # --------------- UI methods

    def manage_menubar(self):
        """
            This method defines the menubar and what each command in the menubar does.
        """
        self.__menubar = Menu(self.__root)
        self.__root.config(menu=self.__menubar)
        self.__file_menu = Menu(self.__menubar, tearoff=0)
        self.__file_menu.add_command(label="New Game", command=self.get_num_players_and_start_game)
        self.__file_menu.add_command(label="Replay", command=self.replay_game)
        self.__file_menu.add_separator()
        self.__file_menu.add_command(label="Save Game", command=self.save_game)
        self.__file_menu.add_command(label="Save Game As...", command=self.save_game_as)
        self.__file_menu.add_command(label="Load Game", command=self.load_game)
        self.__file_menu.add_command(label="Delete Save", command=self.delete_save)
        self.__file_menu.add_separator()
        self.__file_menu.add_command(label="Exit", command=self.close)
        self.__menubar.add_cascade(label="File", menu=self.__file_menu)
        self.__help_menu = Menu(self.__menubar, tearoff=0)
        self.__help_menu.add_command(label="About", command=self.show_info)
        self.__help_menu.add_command(label="Help", command=self.show_help_info)
        self.__menubar.add_cascade(label="Help", menu=self.__help_menu)
    
    def initialize_ui_text(self):
        """
            Method to initialize the text display.
        """
        self.score_text = self.f_canvas.create_text(70,45,text="Black's score: 2\n\nWhite's score: 2")
        self.turn_text = self.f_canvas.create_text(100,100,text="")
        self.move_sequence_text = Text(self.f_canvas,bg="white",width=25,height=30)
        self.move_sequence_text.pack(side=BOTTOM)

    def update_text_display(self, move_count, insert_text):
        """
            Method to manage the text display during the game.
        """
        self.f_canvas.itemconfig(self.score_text, text=f"Black's score: {self.__board.score[0]}\n\nWhite's score: {self.__board.score[1]}")
        if move_count % 2 == 0:
            insert_text += "\n"
        else:
            insert_text += "\t\t"
        self.move_sequence_text.insert(INSERT,f"{insert_text}")

    def restart_canvas(self):
        """
            Method to reset the canvas for when we try to load another game or replay current game.
        """
        self.__right.destroy()
        self.__canvas.destroy()
        self.__right = Frame(self.__root, bg="#CCCCCC", width=200)
        self.__right.pack(side=RIGHT, fill=BOTH)
        self.f_canvas = Canvas(self.__right, bg="#CCCCCC", width=160, height=400)
        self.f_canvas.pack(side=TOP, fill=BOTH, expand=True)
        self.__canvas = Canvas(self.__root, width=self.width, height=self.height)
        self.__canvas.pack(fill=BOTH)
    
    # --------------- menubar commands methods
        
    def get_human_players(self):
        '''
            Helper method for getting two human players.
        '''
        name1 = simpledialog.askstring(title="First player's name", prompt="Type player1's name:")
        if not name1:
            name1 = "Pennywise"
        name2 = simpledialog.askstring(title="Second player's name", prompt="Type player2's name:")
        if not name2:
            name2 = "Chucky"
        return self.get_player(name1, 1), self.get_player(name2, 2)

    def get_num_players_and_start_game(self):
        """
            This is the method for the 'New Game' menu command. Using 'simpledialog' we get user's input to start a new game
            with 1-2 human players.
            Another option is to choose 0 human players and just watch a game between RandomPlayer and GreedyPlayer.
        """
        human_players = simpledialog.askinteger("Start a new game", "Please type in the number of human players.", minvalue=0, maxvalue=2)
        if human_players is None:
            return
        p1, p2 = None, None
        if human_players == 0:
            p1 = RandomPlayer(1)
            p2 = GreedyPlayer(2)
        elif human_players == 1:
            difficulty = simpledialog.askinteger("Set difficulty", "Computer strength: 1 - weak, or 2 - strong", minvalue=1, maxvalue=2)
            random.seed(time.time())
            if not difficulty:
                difficulty = random.randint(1, 2)
            ai_name = random.choice(["RandomPlayer", "GreedyPlayer"])
            if difficulty == 2:
                ai_name = "MinimaxPlayer"
            name = simpledialog.askstring(title="Human player's name", prompt="Type player's name:")
            if not name:
                name = "Jason"
            p1 = self.get_player(name, 1)
            p2 = self.get_player(ai_name, 2)
        elif human_players == 2:
            p1, p2 = self.get_human_players()
        self.start_game(p1, p2)

    def start_game(self, p1, p2):
        """
            Method to start a game.
        """
        self.restart_canvas()
        self.__board = Board(self, p1, p2)
        self.initialize_ui_text()
        game = Game()
        self.__board.game_in_progress = True
        self.__board.play(game)

    def replay_game(self):
        """
            The method for the 'Replay' menu command. We switch the players' colors and restart a game switching players' turns.
        """
        if not self.__board.game_in_progress:
            raise Exception("Can't replay game if you haven't played yet!")
        p1 = self.__board.players[1]
        p2 = self.__board.players[2]
        p1 = self.get_player(p1.name, 2)
        p2 = self.get_player(p2.name, 1)
        self.start_game(p2, p1)
    
    def get_save_file_name(self, name1, name2):
        '''
            Helper method for resolving save file's name
        '''
        file_name = f"{name1}-{name2}"
        file_count = 1
        files = os.listdir('Saved_games')
        for file in files:
            if file.startswith(file_name):
                file_count += 1
        file_name += f"_{file_count}.txt"
        final_name = simpledialog.askstring(title="Save Game As...", prompt="Accept suggested file name or choose something else", initialvalue=file_name)
        if not final_name:
            print("Save was canceled or save name wasn't provided.")
            return
        if final_name != file_name:
            file_count = 1
            for file in files:
                if file.startswith(final_name):
                    file_count += 1
            if '.' in final_name:
                final_name = f"{'.'.join(final_name.rsplit('.', 1)[0])}_{file_count}.{final_name.split('.')[-1]}"
            else:
                final_name += f"_{file_count}.txt"
        return f"Saved_games/{final_name}"
    
    def write_save(self, path, name1, name2):
        '''
            Helper method for writing the game's details in the save file
        '''
        with open(path, 'w') as f:
            timestamp = datetime.datetime.now()
            game = self.__board.move_sequence
            f.write(f"{timestamp}\n{name1}-{name2}\n{game}")
    
    def save_game(self):
        """
            The method for the 'Save Game' menu command. If a save file for current game already exists, we just
            update the save file to current state. If not, we call the save_game_as method.
        """
        if self.__board.game_saved:
            path = self.__board.save_name
            try:
                self.write_save(path, self.__board.players[1].name, self.__board.players[2].name)
            except FileNotFoundError:
                print("Old save file is missing. Try using \'Save Game As...\' menu option.")

        else:
            self.save_game_as()

    def save_game_as(self):
        """
            The method for the 'Save Game As...' menu command.
        """
        if not self.__board.game_in_progress:
            raise Exception("Can't save a game if game is not in progress.")
        path = self.get_save_file_name(self.__board.players[1].name, self.__board.players[2].name)
        if path:
            self.__board.save_name = path
            self.__board.game_saved = True
            try:
                self.write_save(path, self.__board.players[1].name, self.__board.players[2].name)
            except FileExistsError:
                print("The file name you chose already exists. Try again with another name.")
        else:
            print("Game wasn't saved. If you didn't cancel, please try again and provide the name of the game's save file.")
    
    def get_save_file_content(self, path):
        """
            Helper method for parsing game information from save file.
        """
        names, sequence = [], ""
        with open(path) as f:
            lines = f.readlines()
            names = lines[1].strip('\n').split('-')
            sequence = lines[-1].strip('\n')
        return names, sequence
    
    def populate_board(self, game, sequence):
        """
            Helper method to set the board according to the save file data when loading saved game.
        """
        player, move_count = 0, 0
        for i in range(2, len(sequence) + 1, 2):
            move_notation = sequence[i-2:i]
            player = 2
            color = "White"
            if move_notation[0].isupper():
                player = 1
                color = "Black"
            game.current_player = player
            i, j = notation_to_move(move_notation)
            game.play(i, j, player, color)
            move_count += 1
            insert_text = f"{move_count}. {move_notation}"
            if move_count < 10:
                insert_text = f" {insert_text}"
            self.update_text_display(move_count, insert_text)
        return move_count, player
    
    def get_player(self, name, color):
        """
            Helper method for getting a player object by using the name of the player.
        """
        if name == "RandomPlayer":
            return RandomPlayer(color, name)
        elif name == "MinimaxPlayer":
            return MinimaxPlayer(color=color, name=name, evaluator=RealtimeEvaluator(), depth=6)
        elif name == "MCTSPlayer":
            return MCTSPlayer(color=color, name=name, num_sims=20, max_iter=50)
        elif name == "GreedyPlayer":
            return GreedyPlayer(color, name)
        else:
            return Player(color, name)

    def load_game_file(self, temp_win):
        '''
            This method gets the game's details from the save file and recreates the game as it was saved.
        '''
        temp_win.destroy()
        self.restart_canvas()
        path = f"Saved_games/{self.load_name.get()}"
        names, sequence = self.get_save_file_content(path)
        p1 = self.get_player(names[0], 1)
        p2 = self.get_player(names[1], 2)
        self.__board = Board(self, p1, p2)
        self.__board.save_name = path
        self.__board.game_saved = True
        self.initialize_ui_text()
        game = Game()
        self.__board.game_in_progress = True
        self.__board.move_sequence = sequence
        move_count, player = self.populate_board(game, sequence)
        
        for i in range(8):
            for j in range(8):
                self.__board.get_cells()[i][j].owner = game.board[i][j]
        self.__board.score = game.get_score()
        self.__board.move_count = move_count
        self.__board.current_player = player
        game.current_player = player
        self.__board.switch_player()
        game.switch_player()
        self.__board.draw_disks()
        self.__board.play(game)
    
    def load_game(self):
        """
            The method for the 'Load Game' menu command. Opening a window with list of all save files
            for the user to choose from and then loading the chosen save file.
        """
        games = os.listdir('Saved_games')
        if not games:
            print("There aren't any saved games to load.")
            return
        temp_win = Tk()
        temp_win.title("Load Game")
        Label(temp_win, text="Choose which game you want to load:")
        self.load_name = StringVar(temp_win)
        for game in games:
            Radiobutton(temp_win,
                        text=game,
                        indicatoron = 0,
                        width = 20,
                        padx = 20,
                        variable=self.load_name,
                        command=lambda: self.load_game_file(temp_win),
                        value=game).pack(anchor=W)
    

    # ------ methods for deleting old save files
            
    def delete_save_file(self, temp_win):
        """
            Helper method for deleting a saved game.
        """
        temp_win.destroy()
        path = f"Saved_games/{self.delete_name.get()}"
        print(path)
        os.remove(path)
    
    def delete_save(self):
        """
            The method for the 'Delete Save' menu command. Opening a window with list of all save files
            for the user to choose from and then deleting the chosen save file.
        """
        games = os.listdir('Saved_games')
        if not games:
            print("There aren't any saved games to delete.")
            return
        temp_win = Tk()
        temp_win.title("Delete save")
        Label(temp_win, text="Choose which save you want to delete:")
        self.delete_name = StringVar(temp_win)
        for game in games:
            Radiobutton(temp_win,
                        text=game,
                        indicatoron = 0,
                        width = 20,
                        padx = 20,
                        variable=self.delete_name,
                        command=lambda: self.delete_save_file(temp_win),
                        value=game).pack(anchor=W)

    def show_info(self):
        info = """
            This is a game called Reversi.
            It is a two players game, black vs. white.

            Each player in turn places a white and black
            colored disk to capture the other player's disks.
            To capture disks a player needs to place his disk
            on a line in a way that he traps the other player's
            disks in between 2 of his.\n
            The game ends when there are no more possible moves for any player.
            The winner is the player with the most disks of his color.
        """
        simpledialog.SimpleDialog(self.__root, text=info, default=1, cancel=1, title="About this game").go()
    
    def show_help_info(self):
        help = """
            To start a new game, press 'File' in the menubar and choose 'New Game'.
            You'll be prompted to provide the number of human players, 0 - if you
            want to watch two AI players play each other, 1 - to play against an AI
            player, and 2 - to play against another human player. If you chose 1
            (play agianst computer), you'll be asked what difficulty level you want
            the computer player to be: weak or strong.

            To replay a game, press 'File' in the menubar and choose 'Replay Game'.
            A new game will start with the same players as before, but with opposite
            colors from before.

            At any time you can save your current game in order to continue later.
            Press 'File' in the menubar and choose 'Save Game'.
            Your current game will be saved under the current time stamp.

            To load a saved game, press 'File' in the menubar and choose 'Load Game'.
            Choose from the list of saved games the game you want to continue.
        """
        simpledialog.SimpleDialog(self.__root, text=help, default=1, cancel=1, title="How to play").go()
    
    def get_canvas(self):
        return self.__canvas
    
    def get_root(self):
        return self.__root
    
    def get_frame(self):
        return self.__right


# =======================================================================================================
# --------------- The Board class defines and manages the game board for the Gui
class Board:
    """
        Class for the game board in the gui.
    """
    def __init__(self, win: Window=None, player1=None, player2=None):
        self._win = win
        if self._win:
            self.img = Image.open("imgs/wood.jpg")
            self.width = self._win.width
            self.height = self._win.height
            resized_img= self.img.resize((self.width, self.height))
            self.new_img = ImageTk.PhotoImage(resized_img)
            self.__canvas = self._win.get_canvas()
            self.background_image = self.__canvas.create_image(375,375,image=self.new_img)
            self.add_grid_labels()
            self.rect = self.__canvas.create_rectangle(75, 75, 675, 675, fill="#00C957")
        self.__cells = list()
        self.__disks = list()
        self.__cell_size = 75
        self.game_in_progress = False
        self.game_saved = False
        self.save_name = ""
        self.draw_grid()
        self.draw_disks()
        if player1 and player2:
            self.score = [2, 2]
            self.current_player = 1
            self.move_count = 0
            self.move_sequence = ""
            self.players = [None, player1, player2]
    
    
    # -------- Methods for initializing and drawing the game board
            
    def draw_grid(self):
        """
            Method for drawing the grid of the game board.
        """
        for i in range(8):
            row = []
            for j in range(8):
                x1 = (j + 1) * self.__cell_size
                x2 = x1 + self.__cell_size
                y1 = (i + 1) * self.__cell_size
                y2 = y1 + self.__cell_size
                new_cell = Cell(x1, y1, x2, y2)
                if i == 3:
                    if j == 3:
                        new_cell.owner = 2
                    elif j == 4:
                        new_cell.owner = 1
                if i == 4:
                    if j == 3:
                        new_cell.owner = 1
                    elif j == 4:
                        new_cell.owner = 2
                row.append(new_cell)
                if self._win:
                    new_cell.draw(self.__canvas)
            self.__cells.append(row)
    
    def add_grid_labels(self):
        """
            Method for adding letters to columns' headers and numbers to rows' headers.
            This isn't crucial for the game's logic. It's just for decoration.
        """
        margin1 = 110
        margin2 = 35
        alphabet = "ABCDEFGH"
        numbers = "12345678"
        for i in range(8):
            self.__canvas.create_text(margin1 + 75 * i, margin2, text=alphabet[i], font=("Times", 28, "bold"), fill="#CDAA7D")
            self.__canvas.create_text(margin2, margin1 + 75 * i, text=numbers[i], font=("Times", 28, "bold"), fill="#CDAA7D")
    
    def draw_disks(self):
        """
            Method for drawing disks on the board.
        """
        for i in range(8):
            row = []
            for j in range(8):
                x, y = self.get_mid(i, j)
                r = 0.40 * self.__cell_size
                color = "#00C957"
                if self.__cells[i][j].owner == 1:
                    color = "black"
                if self.__cells[i][j].owner == 2:
                    color = "white"
                disk = Disk(Point(x, y), r, color)
                if self._win:
                    disk.draw(self.__canvas)
                row.append(disk)
            self.__disks.append(row)
        if self.game_in_progress and not (self.players[1].type == "Human" or self.players[2].type == "Human"):
            self._win.redraw()
            sleep(0.5)
    
    def get_mid(self, i, j):
        return (j + 1.5) * self.__cell_size, (i + 1.5) * self.__cell_size
    
    def get_cells(self):
        return self.__cells
    
    def get_disks(self):
        return self.__disks
    
    # --------- Methods for running the game

    def flip_disks(self, i, j, lines):
        """
            Method for switching disks colors on squares that were captured by a move.
        """
        for line in lines:
            for u, v in line:
                self.__cells[u][v].owner = self.current_player
        self.__cells[i][j].owner = self.current_player
        self.draw_disks()
    
    def get_position(self,x,y):
        """
            Helper method for translating x,y values gotten from pressing the mouse button on the game board,
            to indexes of the relevant cell in the grid.
        """
        i = (y - self.__cell_size) // self.__cell_size
        j = (x - self.__cell_size) // self.__cell_size
        return i,j
    
    def mouse_pressed(self, event, game, color):
        """
            Method that places a move on the game board according to a mouse button pressed event.
        """
        i, j = self.get_position(event.x, event.y)
        try:
            self.play_move(i, j, game, color)
            self._win.redraw()
        except InvalidMoveError as e:
            print(str(e) + "\nTry again.")
        return self.play(game)
    
    def switch_player(self):
        """
            Method to switch between the players who is the next to play.
        """
        self.current_player = abs(self.current_player - 2) + 1
    
    def end_game(self):
        """
            Method for handling the game board when the game ends.
        """
        if self._win:
            self.__canvas.unbind('<Button-1>')
        print("Game over!")
        if self.score[0] == self.score[1]:
            if self._win:
                self._win.f_canvas.itemconfig(self._win.turn_text, text="It's a draw.")
            print("Game ended with a draw.")
            return 0
        winner = self.players[1]
        winner_disks = self.score[0]
        loser_disks = self.score[1]
        if self.score[1] > self.score[0]:
            winner = self.players[2]
            winner_disks = self.score[1]
            loser_disks = self.score[0]
        color = "Black" if winner.color == 1 else "White"
        print(f"{winner.name}({color}) has won: {winner_disks}-{loser_disks}.")
        if self._win:
            self._win.f_canvas.itemconfig(self._win.turn_text, text=f"{winner.name}({color}) has won.")
        return winner.color
    
    def play_move(self, i, j, game, color):
        """
            The method for placing a move on the board.
        """
        lines = game.play(i, j, self.current_player, color)
        self.score = game.get_score()
        self.move_count += 1
        self.move_sequence += move_to_notation(i, j, self.current_player)
        if self._win:
            insert_text =f"{self.move_count}. {self.move_sequence[-2:]}"
            if self.move_count < 10:
                insert_text = f" {insert_text}"
            self._win.update_text_display(self.move_count, insert_text)
        self.flip_disks(i, j, lines)
        self.switch_player()

    def play(self, game):
        """
            This is the main method for running the game.
        """
        color = "Black" if self.current_player == 1 else "White"
        if self._win:
            self._win.f_canvas.itemconfig(self._win.turn_text, text=f"{self.players[self.current_player].name}({color})'s turn")

        if self.score[0] + self.score[1] == 64:
            return self.end_game()
        cur_player = self.players[self.current_player]
        possible_moves = get_possible_moves(game.board, self.current_player)
        if not possible_moves:
            self.switch_player()
            possible_moves = get_possible_moves(game.board, self.current_player)
            if not possible_moves:
                return self.end_game()
            game.switch_player()
            return self.play(game)
        if cur_player.type == "Human":
            self.__canvas.bind('<Button-1>', lambda e: self.mouse_pressed(e, game, color))
        else:
            move = cur_player.find_move(game)
            if move:
                self.play_move(move[0], move[1], game, color)
            return self.play(game)
