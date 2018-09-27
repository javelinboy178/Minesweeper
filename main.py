import tkinter as tk
from tkinter import ttk
from tkinter import *
import random
import sys
import os


class Minesweeper(tk.Tk):
    # root function contains all classes of pages to be used
    def __init__(self, *args, **kwargs):
        tk.Tk.__init__(self, *args, **kwargs)

        container = tk.Frame(self)

        container.pack(side="top", fill="both", expand=True)
        container.grid_rowconfigure(0, weight=1)
        container.grid_columnconfigure(0, weight=1)
        # set aside some var in controller to be able to pass them back and forth between threads
        # also sets some default var if the player doesn't want to change and just play defaults
        self.settings = {"number of mines": StringVar(value='10'),
                         "number of squares": StringVar(value='6')}
        # some variables used in setting up the game board
        # these variables allow for updating Game thread without drawing board untill ready
        self.checking = True
        self.one_time = 0

        self.frames = {}
        for F in (StartPage, Settings, Game, Loss, Win, Loading):
            frame = F(container, self)
            self.frames[F] = frame
            frame.grid(row=0, column=0, sticky=tk.N + tk.S + tk.E + tk.W)
        self.show_frame(StartPage)

        #Menubar is pretty obvious
        menubar = Menu(self)
        filemenu = Menu(menubar, tearoff=0)
        filemenu.add_command(label="New Game", command=self.new_game)
        filemenu.add_command(label="Quit", command=sys.exit)
        menubar.add_cascade(label="File", menu=filemenu)
        self.config(menu=menubar)

    # used to change between frames
    def show_frame(self, cont):
        frame = self.frames[cont]
        frame.tkraise()

    # Used so that the continue button on settings frame will draw the board also
    def set_checking(self):
        self.one_time = 1

    # Resets the entire program
    def new_game(self):
        python = sys.executable
        os.execl(python, python, *sys.argv)


# Just startpage Class has start and quit buttons
class StartPage(tk.Frame):

    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)

        label = tk.Label(self, text="Minesweeper!!", font="Helvetica 20 bold")
        label.pack()
        self.controller = controller
        button1 = ttk.Button(self, text="Start Game", command=lambda: controller.show_frame(Settings))
        button1.pack()

        button2 = ttk.Button(self, text="Quit Game", command=sys.exit)
        button2.pack()


# Settings page allows user to set game board var
# and passes it into the controller for later use
class Settings(tk.Frame):
    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)
        self.controller = controller

        mines_label = tk.Label(self, text="Number of mines?")
        mines_label.pack()

        mines_entry = tk.Entry(self, width=2, textvariable=self.controller.settings["number of mines"])
        mines_entry.pack()

        squares_label = tk.Label(self, text="Number of squares? (Per Line)")
        squares_label.pack()

        squares_entry = tk.Entry(self, width=1, textvariable=self.controller.settings["number of squares"])
        squares_entry.pack()

        # Extra function used to draw game board
        button1 = tk.Button(self, text="Continue", command=lambda: [controller.show_frame(Loading),
                                                                    controller.set_checking(), ])
        button1.pack()


# This page is used because the Game board can take a bit to draw if the var are big enough
class Loading(tk.Frame):
    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)
        title = tk.Label(self, text="Loading your game", font="Helvetica 20 bold")
        title.pack()


# This is the main game frame pretty self explanitory
class Game(tk.Frame):
    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)

        title = tk.Label(self, text="Minesweeper!!")
        title.grid(column=0, row=0)
        # Label to show how many mines are in the game board gets updated in update_screen function
        self.controller = controller
        self.mines_text = tk.Label(self, text=self.controller.settings["number of mines"].get())
        self.mines_text.grid(column=5, row=0)

        # Sets initial variables most are re initialized later to make sure there is no holdover
        self.frames_list = []
        self.btn_list = []
        self.btn_dct = {}
        self.number_buttons_found = 0
        self.number_of_mines = 0
        self.number_of_squares = 0
        self.update_screen()
        self.do_nothing = 0

    # Function to wait untill settings frame continue button is pressed then it will go through and draw the game
    # board the try/except is added to make sure when the player is changing the var in the settings screen it does not
    # fail when the tk.Entry is a NAN
    def update_screen(self):
        if self.controller.checking:
            try:
                self.number_of_mines = self.controller.settings["number of mines"].get()
                text_for_mines = "mines: " + self.controller.settings["number of mines"].get()
                self.mines_text.configure(text=text_for_mines)
                self.number_of_squares = self.controller.settings["number of squares"].get()
                self.number_of_mines = int(self.number_of_mines)
                self.number_of_squares = int(self.number_of_squares)
            except:
                pass

        # Uses the one_time var to make sure only runs once while watching for the two var to line up
        # runs through all the required functions to draw the board(Create_frames_and_buttons)
        # sets buttons with mines and numbers(populate_mines, populate_numbers)
        # creates a dictionary that stores the button mine and number values for later use(dct_populate)
        # then wipes the buttons to just show the blank button(wipe_buttons)
        # pulls up the game frame after it is all populated
        # sets the checking var to False so it no longer tries to run this function
        if self.controller.one_time == 1:
            self.create_frames_and_buttons()
            self.populate_mines()
            self.populate_numbers()
            self.dct_populate()
            self.wipe_buttons()
            self.controller.show_frame(Game)
            self.controller.checking = False
        else:
            pass
            # This is used to essentially pause while updating without pausing the entire program
            self.mines_text.after(1000, self.update_screen)

    # Create a button grid based on the number of squares per line
    # then assigns them an index(ndex) so when the command is ran it knows what button ran it
    # the text and font are used to ensure button looks right bg="background color"
    def create_frames_and_buttons(self):
        ndex = 0
        i = 0
        x = 0
        self.frames_list = []
        self.btn_list = []
        for i in range(self.number_of_squares):
            for x in range(self.number_of_squares):
                self.frames_list.append(Frame(self, width=100, height=100))
                self.frames_list[ndex].propagate(False)
                self.frames_list[ndex].grid(row=i + 5, column=x, sticky="NSEW", padx=2, pady=2)
                self.btn_list.append(Button(self.frames_list[ndex], text="", font="Helvetica 16 bold",
                                            bg="light blue", command=lambda ndex=ndex: self.check_button(ndex)))
                self.btn_list[ndex].pack(expand=True, fill=BOTH)
                x += 1
                ndex += 1

    # uses randrange to randomly populate the buttons with mines while making sure not to go past the total
    # number of mines chosen by player(or default)
    def populate_mines(self):
        mines_remain = self.number_of_mines

        while mines_remain > 0:
            i = random.randrange(len(self.btn_list))
            if self.btn_list[i]["text"] == "":
                self.btn_list[i].configure(text="mine!!")
                mines_remain -= 1
            else:
                pass

    # after all the mines are populated goes to every other square counts the mines around it
    # and adds that number as text to button to be used as a dictionary value that the game later uses

    def populate_numbers(self):
        i = 0
        right_row = [self.number_of_squares - 1]
        running_total = self.number_of_squares - 1
        while running_total < (self.number_of_squares ** 2) - 1:
            running_total += self.number_of_squares
            right_row.append(running_total)
        left_row = [0]
        running_total = 0
        while running_total < (self.number_of_squares ** 2) - self.number_of_squares:
            running_total += self.number_of_squares
            left_row.append(running_total)

        # this entire while function goes through each buttons checks left right up down and diagional to check
        # for mines all the extra variables are to make sure it doesnt try to out of range the index by reaching
        # the end (like top row, bottom row, left row, right row) all based off of the controller var that the
        # player sets (or default)
        while i < len(self.btn_list):
            mines_nearby = 0
            if self.btn_list[i]["text"] != "mine!!":
                if i not in right_row:
                    if self.btn_list[i + 1]["text"] == "mine!!":
                        mines_nearby += 1
                if i not in left_row:
                    if self.btn_list[i - 1]["text"] == "mine!!":
                        mines_nearby += 1
                if i > (self.number_of_squares - 1):
                    if self.btn_list[i - self.number_of_squares]["text"] == "mine!!":
                        mines_nearby += 1
                if i < (self.number_of_squares * self.number_of_squares - self.number_of_squares):
                    if self.btn_list[i + self.number_of_squares]["text"] == "mine!!":
                        mines_nearby += 1
                if i not in right_row and i not in left_row and (
                        self.number_of_squares * self.number_of_squares - self.number_of_squares) > i > (
                        self.number_of_squares - 1):
                    if self.btn_list[i - (self.number_of_squares - 1)]["text"] == "mine!!":
                        mines_nearby += 1
                    if self.btn_list[i + (self.number_of_squares - 1)]["text"] == "mine!!":
                        mines_nearby += 1
                    if self.btn_list[i - (self.number_of_squares + 1)]["text"] == "mine!!":
                        mines_nearby += 1
                    if self.btn_list[i + (self.number_of_squares + 1)]["text"] == "mine!!":
                        mines_nearby += 1

            if self.btn_list[i]["text"] != "mine!!":
                self.btn_list[i].configure(text=mines_nearby)
            i += 1

    # this goes through each button and if it is a mine it sets the dictionary button # value to true
    # and if it is false it sets the dictionary button # to False and sets a number to mines around it using previous
    # function(populate_numbers)
    def dct_populate(self):
        i = 0
        self.btn_dct = {}
        while i < len(self.btn_list):
            if self.btn_list[i]["text"] == "mine!!":
                self.btn_dct["button %s mine" % i] = True
                self.btn_dct["button %s mine nearby" % i] = 0
            else:
                self.btn_dct["button %s mine" % i] = False
                self.btn_dct["button %s mine nearby" % i] = self.btn_list[i]["text"]
            i += 1

    # resets the text var of each button that was used to populate the dictionary
    # So the player cant cheat
    def wipe_buttons(self):
        i = 0
        while i < len(self.btn_list):
            self.btn_list[i].configure(text="")
            i += 1

    # When the button is clicked uses button index to check if it is a mines or not
    # if mine then raises you loose frame
    # if not then shows the number of mines nearby in proper color per the origional minesweeper
    def check_button(self, ndex):
        if self.btn_dct["button %s mine" % ndex]:
            self.controller.show_frame(Loss)
        else:
            if self.btn_dct["button %s mine nearby" % ndex] == 1:
                self.btn_list[ndex].configure(text=self.btn_dct["button %s mine nearby" % ndex], fg="blue",
                                              bg="light grey", command="")
            elif self.btn_dct["button %s mine nearby" % ndex] == 2:
                self.btn_list[ndex].configure(text=self.btn_dct["button %s mine nearby" % ndex], fg="green",
                                              bg="light grey", command="")
            elif self.btn_dct["button %s mine nearby" % ndex] == 3:
                self.btn_list[ndex].configure(text=self.btn_dct["button %s mine nearby" % ndex], fg="red",
                                              bg="light grey", command="")
            elif self.btn_dct["button %s mine nearby" % ndex] == 4:
                self.btn_list[ndex].configure(text=self.btn_dct["button %s mine nearby" % ndex], fg="purple",
                                              bg="light grey", command="")
            elif self.btn_dct["button %s mine nearby" % ndex] == 5:
                self.btn_list[ndex].configure(text=self.btn_dct["button %s mine nearby" % ndex], fg="maroon",
                                              bg="light grey", command="")
            elif self.btn_dct["button %s mine nearby" % ndex] == 6:
                self.btn_list[ndex].configure(text=self.btn_dct["button %s mine nearby" % ndex], fg="turquoise",
                                              bg="light grey", command="")
            elif self.btn_dct["button %s mine nearby" % ndex] == 7:
                self.btn_list[ndex].configure(text=self.btn_dct["button %s mine nearby" % ndex], fg="black",
                                              bg="light grey", command="")
            elif self.btn_dct["button %s mine nearby" % ndex] == 8:
                self.btn_list[ndex].configure(text=self.btn_dct["button %s mine nearby" % ndex], fg="grey",
                                              bg="light grey", command="")
            elif self.btn_dct["button %s mine nearby" % ndex] == 0:
                self.btn_list[ndex].configure(text=self.btn_dct["button %s mine nearby" % ndex], fg="yellow",
                                              bg="light grey", command="")

            # this variable is used to check if you beat the game or not(aka clicked on all not mine buttons)
            self.number_buttons_found += 1

        # pretty staight forward every time button is pressed it checks to see if game is won
        self.check_win()

    # you have to have clicked on every non mine square (total number of squares - number of mines)
    def check_win(self):
        if self.number_buttons_found == (len(self.btn_list) - self.number_of_mines):
            self.controller.show_frame(Win)


class Loss(tk.Frame):
    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)

        label = tk.Label(self, text="BOOM You Loose!!", font="Helvetica 22 bold")
        label.pack()


class Win(tk.Frame):
    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)

        label = tk.Label(self, text="YOU WIN!!", font="Helvetica 22 bold")
        label.pack()


app = Minesweeper()
app.mainloop()
