from tkinter import *
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
        self.__right = Frame(self.__root, bg="saddle brown", width=200)
        self.__right.pack(side=RIGHT, fill=BOTH)
        self.__canvas = Canvas(self.__root, height=750, width=750)
        self.__canvas.pack(fill=BOTH)
        self.__board = Board(self)
        self.__menubar = Menu(self.__root)
        self.__root.config(menu=self.__menubar)
        self.__file_menu = Menu(self.__menubar, tearoff=0)
        self.__sub_menu = Menu(self.__file_menu, tearoff=0)
        self.__sub_menu.add_command(label="Human vs Human", command=self.reset_board)
        self.__sub_menu.add_command(label="Human vs Computer", command=self.reset_board)
        self.__sub_menu.add_command(label="Computer vs Human", command=self.reset_board)
        self.__sub_menu.add_command(label="Computer vs Computer", command=self.reset_board)
        self.__file_menu.add_cascade(label="New Game", menu=self.__sub_menu)
        self.__file_menu.add_separator()
        self.__file_menu.add_command(label="Exit", command=self.close)
        self.__menubar.add_cascade(label="File", menu=self.__file_menu)
        self.__running = False
        self.__root.protocol("WM_DELETE_WINDOW", self.close)
    
    def redraw(self):
        self.__root.update_idletasks()
        self.__root.update()
    
    def wait_for_close(self):
        self.__running = True
        while self.__running:
            self.redraw()
        print("window closed...")
    
    def close(self):
        self.__running = False

    def reset_board(self):
        self.__board = Board(self)
    
    def get_canvas(self):
        return self.__canvas


class Board:
    def __init__(self, win: Window):
        self._win = win
        img = Image.open("wood.jpg")
        resized_img= img.resize((750,750))
        self.__new_img = ImageTk.PhotoImage(resized_img)
        self.__canvas = self._win.get_canvas()
        self.__canvas.create_image(375,375,image=self.__new_img)
        self.add_grid_labels()
        self.__canvas.create_rectangle(75, 75, 675, 675, fill="#00C957")
        self.__cells = []
        self.__cell_size = 75
        self.draw_grid()
        self.draw_disks()

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
    
    def get_cells(self):
        return self.__cells
