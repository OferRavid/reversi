from tkinter import *
from tkinter import simpledialog
from PIL import Image, ImageTk
from game import *
from util import *


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
        x1 = self.p1.x
        y1 = self.p1.y
        x2 = self.p2.x
        y2 = self.p2.y
        canvas.create_line(x1, y1, x2, y2, fill=fill_color, width=3)
        canvas.pack(fill=BOTH, expand=1)


class Disk:
    def __init__(self, center: Point, radius):
        self._x = center.x
        self._y = center.y
        self._r = radius
    
    def draw(self, canvas, color):
        canvas.create_oval(
            self._x - self._r, 
            self._y - self._r, 
            self._x + self._r, 
            self._y + self._r, 
            outline=color, 
            fill=color
        )
        canvas.pack(fill=BOTH, expand=1)


class Cell:
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
        self._top.draw(canvas)
        self._bottom.draw(canvas)
        self._left.draw(canvas)
        self._right.draw(canvas)

    def in_cell(self, x, y):
        return self._x1 <= x <= self._x2 and self._y1 <= y <= self._y2


class Window:
    def __init__(self):
        self.__root = Tk()
        self.__root.title("Reversi")
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

    def redraw(self):
        self.__root.update_idletasks()
        self.__root.update()
    
    def wait_for_close(self):
        self.__running = True
        while self.__running:
            self.redraw()
        print("Thank you for playing Reversi! Goodbye...")
    
    def close(self):
        self.__running = False

    def manage_menubar(self):
        self.__menubar = Menu(self.__root)
        self.__root.config(menu=self.__menubar)
        self.__file_menu = Menu(self.__menubar, tearoff=0)
        self.__file_menu.add_command(label="New Game", command=self.get_num_players_and_start_game)
        self.__file_menu.add_command(label="Replay Game", command=self.replay_game)
        self.__file_menu.add_separator()
        self.__file_menu.add_command(label="Save Game", command=self.save_game)
        self.__file_menu.add_command(label="Load Game", command=self.load_game)
        self.__file_menu.add_separator()
        self.__file_menu.add_command(label="Exit", command=self.close)
        self.__menubar.add_cascade(label="File", menu=self.__file_menu)
        self.__help_menu = Menu(self.__menubar, tearoff=0)
        self.__help_menu.add_command(label="About", command=self.show_info)
        self.__help_menu.add_command(label="Help", command=self.show_help_info)
        self.__menubar.add_cascade(label="Help", menu=self.__help_menu)
    
    def initialize_ui_text(self):
        self.score_text = self.f_canvas.create_text(70,45,text="Black's score: 2\n\nWhite's score: 2")
        self.turn_text = self.f_canvas.create_text(100,100,text="")
        self.move_sequence_text = Text(self.f_canvas,bg="white",width=25,height=30)
        self.move_sequence_text.pack(side=BOTTOM)

    def update_text_display(self, move_count, insert_text):
        self.f_canvas.itemconfig(self.score_text, text=f"Black's score: {self.__board.score[0]}\n\nWhite's score: {self.__board.score[1]}")
        if move_count % 2 == 0:
            insert_text += "\n"
        else:
            insert_text += "\t\t"
        self.move_sequence_text.insert(INSERT,f"{insert_text}")

    def restart_canvas(self):
        self.__right.destroy()
        self.__canvas.destroy()
        self.__right = Frame(self.__root, bg="#CCCCCC", width=200)
        self.__right.pack(side=RIGHT, fill=BOTH)
        self.f_canvas = Canvas(self.__right, bg="#CCCCCC", width=160, height=400)
        self.f_canvas.pack(side=TOP, fill=BOTH, expand=True)
        self.__canvas = Canvas(self.__root, width=self.width, height=self.height)
        self.__canvas.pack(fill=BOTH)

    def get_num_players_and_start_game(self):
        human_players = simpledialog.askinteger("Start a new game", "Please type in the number of human players.", minvalue=0, maxvalue=2)
        if human_players == 0:
            pass
        elif human_players == 1:
            dificulty = simpledialog.askinteger("Set dificulty", "Computer strength: 1 - weak, or 2 - strong", minvalue=1, maxvalue=2)
        elif human_players == 2:
            if self.score_text:
                self.restart_canvas()
                self.__board = Board(self)
            name1 = simpledialog.askstring(title="First player's name", prompt="Type player1's name:")
            if not name1:
                name1 = "Pennywise"
            name2 = simpledialog.askstring(title="Second player's name", prompt="Type player2's name:")
            if not name2:
                name2 = "Chucky"
            p1 = Player("Black", name1)
            p2 = Player("White", name2)
            self.__board = Board(self, p1, p2)
            self.initialize_ui_text()
            game = Game()
            self.__board.play(game)

    
    def replay_game(self):
        if not self.__board.players:
            raise Exception("Can't replay game if you haven't played yet!")
        p1 = self.__board.players[1]
        p2 = self.__board.players[2]
        p1.color = "White"
        p2.color = "Black"
        self.restart_canvas()
        self.__board = Board(self, p2, p1)
        self.initialize_ui_text()
        game = Game()
        self.__board.play(game)

    def save_game(self):
        pass

    def load_game(self):
        pass

    def show_info(self):
        info = """
            This is a game called Reversi.
            It is a two players game, black vs. white.

            Each player in turn places a white and black
            colored disk to capture the other player's disks.
            To capture disks a player needs to place his disk
            on a line in a way that he traps the other player's 
            disks inbetween 2 of his.\n
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
            (play agianst computer), you'll be asked what dificulty level you want
            the computer player to be: weak or strong.

            To replay a game, press 'File' in the menubar and choose 'Replay Game'.
            A new game will start with the same players as before, but with opposite 
            colors from before.

            At any time you can save your current game in order to continue later.
            Press 'File' in the menubar and choose 'Save Game'.
            Your current game will be saved under the current time stamp.

            To load a saved game, press 'File' in the menubar and choos 'Load Game'.
            Choose from the list of saved games the game you want to continue.
        """
        simpledialog.SimpleDialog(self.__root, text=help, default=1, cancel=1, title="How to play").go()
    
    def get_canvas(self):
        return self.__canvas
    
    def get_root(self):
        return self.__root
    
    def get_frame(self):
        return self.__right


class Board:
    def __init__(self, win: Window, player1=None, player2=None):
        self._win = win
        self.img = Image.open("wood.jpg")
        resized_img= self.img.resize((750,750))
        self.__new_img = ImageTk.PhotoImage(resized_img)
        self.__canvas = self._win.get_canvas()
        self.background_image = self.__canvas.create_image(375,375,image=self.__new_img)
        self.add_grid_labels()
        self.rect = self.__canvas.create_rectangle(75, 75, 675, 675, fill="#00C957")
        self.__cells = []
        self.__cell_size = 75
        self.draw_grid()
        self.draw_disks()
        if player1 and player2:
            self.score = [2, 2]
            self.current_player = 1
            self.move_count = 0
            self.move_sequence = ""
            self.players = [None, player1, player2]

    def draw_grid(self):
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
                new_cell.draw(self.__canvas)
            self.__cells.append(row)
    
    def add_grid_labels(self):
        margin1 = 110
        margin2 = 35
        alphabet = "ABCDEFGH"
        numbers = "12345678"
        for i in range(8):
            self.__canvas.create_text(margin1 + 75 * i, margin2, text=alphabet[i], font=("Times", 28, "bold"), fill="#CDAA7D")
            self.__canvas.create_text(margin2, margin1 + 75 * i, text=numbers[i], font=("Times", 28, "bold"), fill="#CDAA7D")
    
    def draw_disks(self):
        for i in range(8):
            for j in range(8):
                x, y = self.get_mid(i, j)
                r = 0.40 * self.__cell_size
                disk = Disk(Point(x, y), r)
                color = "#00C957"
                if self.__cells[i][j].owner == 1:
                    color = "black"
                if self.__cells[i][j].owner == 2:
                    color = "white"
                disk.draw(self.__canvas, color)
    
    def get_mid(self, i, j):
        return (j + 1.5) * self.__cell_size, (i + 1.5) * self.__cell_size
    
    def flip_disks(self, i, j, lines):
        for line in lines:
            for u, v in line:
                self.__cells[u][v].owner = self.current_player
        self.__cells[i][j].owner = self.current_player
        self.draw_disks()
    
    def get_position(self,x,y):
        i = (y - self.__cell_size) // self.__cell_size
        j = (x - self.__cell_size) // self.__cell_size
        return i,j
    
    def mouse_pressed(self, event, game, color):
        i, j = self.get_position(event.x, event.y)
        try:
            lines = game.play(i, j, self.current_player, color)
            self.score = game.get_score()
            self.move_count += 1
            self.move_sequence += move_to_notation(i, j, self.current_player)
            insert_text =f"{self.move_count}. {self.move_sequence[-2:]}"
            self._win.update_text_display(self.move_count, insert_text)
            self.flip_disks(i, j, lines)
            self.switch_player()
            game.switch_player()
        except InvalidMoveError as e:
            print(e.__str__() + "\nTry again.")
        return self.play(game)
    
    def switch_player(self):
        self.current_player = abs(self.current_player - 2) + 1
    
    def end_game(self):
        print("Game over!")
        if self.score[0] == self.score[1]:
            print("Game ended with a draw.")
            return
        winner = self.players[1]
        disks = self.score[0]
        if self.score[1] > self.score[0]:
            winner = self.players[2]
            disks = self.score[1]
        print(f"{winner.name}({winner.color}) won with {disks} disks.")
        return

    def play(self, game):
        self._win.f_canvas.itemconfig(self._win.turn_text, text=f"{self.players[self.current_player].name}({self.players[self.current_player].color})'s turn")

        if self.score[0] + self.score[1] == 64:
            return self.end_game()
        cur_player = self.players[self.current_player]
        possible_moves = get_possible_moves(game.board, self.current_player)
        if not possible_moves:
            self.switch_player()
            game.switch_player()
            possible_moves = get_possible_moves(game.board, self.current_player)
            if not possible_moves:
                return self.end_game
            return self.play(game)
        if cur_player.type == "Human":
            self.__canvas.bind('<Button-1>', lambda e: self.mouse_pressed(e, game, cur_player.color))

