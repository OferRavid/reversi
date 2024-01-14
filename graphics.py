from tkinter import *
from tkinter import simpledialog
from tkinter import messagebox
from PIL import Image, ImageTk


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
        self.__board = Board(self)
        self.manage_ui()
        
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
    
    def manage_ui(self):
        self.manage_menubar()
        self.initialize_ui_text()

    def manage_menubar(self):
        self.__menubar = Menu(self.__root)
        self.__root.config(menu=self.__menubar)
        self.__file_menu = Menu(self.__menubar, tearoff=0)
        self.__file_menu.add_command(label="New Game", command=self.get_num_players_and_start_game)
        self.__file_menu.add_command(label="Replay Game", command=self.restart)
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
        self.score_text = self.f_canvas.create_text(70,45,text=f"Black's score: {self.__board.score[0]}\n\nWhite's score: {self.__board.score[1]}")
        self.turn_text = self.f_canvas.create_text(55,100,text="")
        self.move_count = 0
        self.move_sequence_text = Text(self.f_canvas,bg="white",width=25,height=30)
        self.move_sequence_text.pack(side=BOTTOM)

    def update_text_display(self):
        # self.f_canvas.itemconfig(self.turn_text, text=f"{self.players[self.current_player].name}({self.players[self.current_player].color})'s turn")
        self.f_canvas.itemconfig(self.score_text, text=f"Black's score: {self.__board.score[0]}\n\nWhite's score: {self.__board.score[1]}")
        # insert_text =f"{self.move_count}. {self.__board.game.move_sequence[-2:]}"
        # if self.move_count % 2 == 0:
        #     insert_text += "\n"
        # else:
        #     insert_text += "\t\t"
        # self.move_sequence_text.insert(INSERT,f"{insert_text}")

    def get_num_players_and_start_game(self):
        human_players = simpledialog.askinteger("Start a new game", "Please type in the number of human players.", minvalue=0, maxvalue=2)
        if human_players == 0:
            pass
        elif human_players == 1:
            dificulty = simpledialog.askinteger("Set dificulty", "Computer strength: 1 - weak, or 2 - strong", minvalue=1, maxvalue=2)
        elif human_players == 2:
            pass
    
    def restart(self):
        pass

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
        simpledialog.SimpleDialog(self.__root,text=info,default=1,cancel=1,title="About this game").go()
    
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
        simpledialog.SimpleDialog(self.__root,text=help,default=1,cancel=1,title="How to play").go()
    
    def get_canvas(self):
        return self.__canvas
    
    def get_root(self):
        return self.__root
    
    def get_frame(self):
        return self.__right
    
    def get_board(self):
        return self.__board


class Board:
    def __init__(self, win: Window):
        self._win = win
        self.img = Image.open("wood.jpg")
        resized_img= self.img.resize((750,750))
        self.__new_img = ImageTk.PhotoImage(resized_img)
        self.__canvas = self._win.get_canvas()
        self.background_image = self.__canvas.create_image(375,375,image=self.__new_img)
        self.add_grid_labels()
        self.rect = self.__canvas.create_rectangle(75, 75, 675, 675, fill="#00C957")
        self.__canvas.bind('<Button-1>', self.mouse_pressed)
        self.__cells = []
        self.__cell_size = 75
        self.draw_grid()
        self.draw_disks()
        self.score = [2, 2]

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
    
    def get_position(self,x,y):
        i = (x - self.__cell_size) // self.__cell_size
        j = (y - self.__cell_size) // self.__cell_size
        return i,j
    
    def mouse_pressed(self, event):
        i, j = self.get_position(event.x, event.y)
    
    def get_cells(self):
        return self.__cells
