import os
import math
import arcade
import arcade.gui
from arcade.gui import UIManager
from letters import *
from wordchecker import *
import random

SCREEN_WIDTH = 1280
SCREEN_HEIGHT = 900
BOARD_WIDTH = 900
BOARD_HEIGHT = 900
SLOT_WIDTH = 60
SLOT_HEIGHT = 60
# SCREEN_HEIGHT = 720
SCREEN_TITLE = "Snakes and Scrabbles"
# Dictionary for storing all letters and their respective point values
# (https://www.thewordfinder.com/scrabble-point-values.php)
LETTERS_DICTIONARY = {'A': 1, 'B': 3, 'C': 3, 'D': 2, 'E': 1, 'F': 4, 'G':2,
'H':4, 'I':1, 'J':8, 'K':5, 'L':1, 'M':3, 'N':1, 'O':1, 'P':3, 'Q':10, 'R':1,
'S':1, 'T':1, 'U':1, 'V':4, 'W':4, 'X':8, 'Y':4, 'Z':10}


class ScrabbleGame(arcade.Window):
    """
    Attribute tile: A SpriteList that stores all the letters a player starts their game round with
    """


class DoneButton(arcade.gui.UIFlatButton):
    def on_click(self):
        print('Done')


class HelpButton(arcade.gui.UIFlatButton):
    def on_click(self):
        print('Help')


class GameViewButton(arcade.gui.UIFlatButton):
    def on_click(self):
        GameView = ScrabbleGame()
        GameView.setup()
        window.show_view(GameView)


class MainView(arcade.View):
    def __init__(self):
        super().__init__()

    def on_draw(self):
        arcade.start_render()
        arcade.draw_text("Scrabble", 500, 500, arcade.color.BLACK, font_size=80)

    def on_show_view(self):
        self.setup()
        arcade.set_background_color(arcade.color.WHITE)

    def setup(self):
        arcade.start_render()
        button = GameViewButton('Play', center_x=650, center_y=400, width=250)
        ui_manager.add_ui_element(button)


class ScrabbleGame(arcade.View):
    """
    Attribute tile: A SpriteList that stores all the letters a player starts their game round with
    """

    def __init__(self):
        super().__init__()

        arcade.set_background_color(arcade.color.GREEN)
        file_path = os.path.dirname(os.path.abspath(__file__))
        os.chdir(file_path)

        self.background = None

        # Selectable and movable letter blocks
        self.active_blocks = arcade.SpriteList()
        # Homeward bound and temporarily unselectable letter blocks
        self.moving_blocks = arcade.SpriteList()
        # Temporarily placed and unselectable blocks
        self.pending_blocks = arcade.SpriteList()
        # Unselectable and unmovable letter blocks
        self.inactive_blocks = arcade.SpriteList()

        self.heldLetter = None

        # Transposed board matrix with rows as tuples: [*zip(*self.board)]
        # Transposed board matrix with rows as lists: list(map(list, [*zip(*self.board)]))
        self.board = [[None for j in range(15)] for i in range(15)]
        # Wordchecker object attribute for word checking functionality
        self.Wordchecker = WordChecker()
        self.score = 0

    # Call to restart game
    def setup(self):
        ui_manager.purge_ui_elements()
        self.background = arcade.load_texture(os.path.join("images", "table.png"))
        vertical_offset = 210
        letters_in_deck = self.new_deck(7)
        for alphabet in letters_in_deck:
            new_letter = Letter(alphabet)
            new_letter.center_x = 1100
            new_letter.center_y = new_letter.center_y + vertical_offset
            vertical_offset = vertical_offset + 100
            self.active_blocks.append(new_letter)
        self.heldLetter = None
        button = DoneButton('Done', center_x=1100, center_y=150, width=250)
        button2 = HelpButton('i', center_x=1250, center_y=875, width=50)
        ui_manager.add_ui_element(button)
        ui_manager.add_ui_element(button2)

    # Called to calculate new frame
    def on_update(self, delta_time):
        self.active_blocks.on_update(delta_time)
        self.inactive_blocks.on_update(delta_time)
        self.moving_blocks.on_update(delta_time)

        for block in self.moving_blocks:
            if not block.movement:
                self.moving_blocks.remove(block)
                if block.is_home():
                    self.active_blocks.append(block)
                else:
                    self.pending_blocks.append(block)

    # Called on frame draw
    def on_draw(self):
        arcade.start_render()
        arcade.draw_lrwh_rectangle_textured(0, 0,
                                            BOARD_WIDTH, BOARD_HEIGHT,
                                            self.background)
        self.active_blocks.draw()
        self.inactive_blocks.draw()
        self.pending_blocks.draw()
        self.moving_blocks.draw()
        score_text = "Score: " + str(self.score)
        arcade.draw_text(score_text, 950, 880,
                         arcade.color.BLACK, 20, width=500, align="center",
                         anchor_x="center", anchor_y="center")

    # Checks board when the RETURN (ENTER) key is pressed
    def on_key_press(self, symbol: int, modifiers: int):
        if symbol == arcade.key.RETURN:
            self.check_board()

    def on_mouse_press(self, x, y, button, key_modifiers):
        """ Called when the user presses a mouse button. """
        self.heldLetter = (arcade.get_sprites_at_point((x, y), self.active_blocks) or [None])[0]

    def on_mouse_release(self, x: float, y: float, button: int, modifiers: int):
        """ Called when the user presses a mouse button. """
        if self.heldLetter is not None:
            self.active_blocks.remove(self.heldLetter)
            self.moving_blocks.append(self.heldLetter)
            if len(arcade.get_sprites_at_point((x, y), self.inactive_blocks)) == 0 and x < BOARD_WIDTH:
                self.heldLetter.place(self.nearest_cell(x, y))
            else:
                self.heldLetter.return_home()
            self.heldLetter = None

    def on_mouse_motion(self, x: float, y: float, dx: float, dy: float):
        """ User moves mouse """
        if self.heldLetter is not None:
            self.heldLetter.center_x += dx
            self.heldLetter.center_y += dy

    def nearest_cell(self, x, y):
        return [SLOT_WIDTH * math.floor(x/SLOT_WIDTH) + SLOT_WIDTH / 2,
                SLOT_HEIGHT * math.floor(y/SLOT_HEIGHT) + SLOT_HEIGHT / 2]

    def check_board(self):
        word_to_check = ''
        # Check if placement is valid
        for block in self.pending_blocks:
            word_to_check = word_to_check + block.letter_string
        if self.Wordchecker.check(word_to_check.lower()) == True and len(word_to_check) > 1:
            self.inactive_blocks.append(block)
            new_score = self.word_score(word_to_check)
        # If not, revert last move
        else:
            for block in self.pending_blocks:
                block.return_home()
                self.moving_blocks.append(block)
            self.pending_blocks = arcade.SpriteList()

    def word_score(self, word):
        for letters in word:
            self.score = LETTERS_DICTIONARY[letters] + self.score
        return self.score

    def new_deck(self, tiles):
        #tiles is the number of new letters to generate(initially 7)
        index = []
        letters_deck = []
        for tile in range(tiles):
            random_num = random.randint(0,8) #generate a list of random numbers
            while random_num in index:
                random_num = random.randint(0,8)
            index.append(random_num)
        for number in index:
            new_letter = list(LETTERS_DICTIONARY.items())[number]
            letters_deck.append(new_letter)
        dict_deck_letters = dict(letters_deck)
        return dict_deck_letters




if __name__ == "__main__":
    window = arcade.Window(SCREEN_WIDTH, SCREEN_HEIGHT, SCREEN_TITLE)
    ui_manager = UIManager()
    mainView = MainView()
    mainView.setup()
    window.show_view(mainView)
    arcade.run()
