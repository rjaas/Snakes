import os
import copy
import math
import arcade
import arcade.gui
from arcade.gui import UIManager
from letters import *
from wordchecker import *

SCREEN_WIDTH = 1280
SCREEN_HEIGHT = 900
BOARD_WIDTH = 900
BOARD_HEIGHT = 900
SLOT_WIDTH = 60
SLOT_HEIGHT = 60
SLOT_COUNT_X = 15
SLOT_COUNT_Y = 15
# SCREEN_HEIGHT = 720
SCREEN_TITLE = "Snakes and Scrabbles"
# Dictionary for storing all letters and their respective point values
# (https://www.thewordfinder.com/scrabble-point-values.php)
LETTER_DECK = ["a" for i in range(2)] + \
              ["b"] + \
              ["c"]


class DoneButton(arcade.gui.UIFlatButton):
    def on_click(self):
        print('Done')


class HelpButton(arcade.gui.UIFlatButton):
    def on_click(self):
        print('Help')


class GameViewButton(arcade.gui.UIFlatButton):
    def on_click(self):
        game_view = ScrabbleGame()
        game_view.setup()
        window.show_view(game_view)


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
        self.board = [[None for j in range(SLOT_COUNT_X)] for i in range(SLOT_COUNT_Y)]
        self.board_temp = copy.deepcopy(self.board)

        # Wordchecker object attribute for word checking functionality
        self.word_checker = WordChecker()
        self.score = 0

    # Call to restart game
    def setup(self):
        ui_manager.purge_ui_elements()
        self.background = arcade.load_texture(os.path.join("images", "table.png"))
        vertical_offset = 400
        for letter in LETTER_DECK:
            new_letter = Letter(letter)
            new_letter.center_x = 1100
            new_letter.center_y = new_letter.center_y + vertical_offset
            vertical_offset = vertical_offset + 150
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
        arcade.draw_text(score_text, 1100, 100,
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
                letter_x, letter_y = self.nearest_cell(x, y)
                self.heldLetter.place(letter_x, letter_y)
                self.board_temp[int((letter_x-SLOT_WIDTH/2)/SLOT_WIDTH)][int((letter_y - SLOT_HEIGHT/2)/SLOT_HEIGHT)] = self.heldLetter
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

    def get_strings(self):
        strings = []
        for row in self.board_temp:
            string_builder = ""
            for letter in row:
                if letter is not None:
                    string_builder += letter.letter_string
                elif len(string_builder) > 0:
                    # Only remember strings longer than one letter
                    if len(string_builder) > 1:
                        strings.append(string_builder)
                    string_builder = ""

        for col in [*zip(*self.board_temp)]:
            string_builder = ""
            for letter in col:
                if letter is not None:
                    string_builder += letter.letter_string
                elif len(string_builder) > 0:
                    if len(string_builder) > 1:
                        strings.append(string_builder)
                    string_builder = ""

        return strings

    def check_board(self):
        # Check if placement is valid
        strings = self.get_strings()
        for s in strings:
            # If not, revert last move
            if not (self.word_checker.check(s) or self.word_checker.check(s[::-1])):
                for block in self.pending_blocks:
                    block.return_home()
                    self.moving_blocks.append(block)
                self.board_temp = copy.deepcopy(self.board)
                self.pending_blocks = arcade.SpriteList()
                return
        # If all checks passed, place the letter blocks
        for block in self.pending_blocks:
            self.inactive_blocks.append(block)
        self.update_score()
        self.pending_blocks = arcade.SpriteList()

    def update_score(self):
        for i in range(SLOT_COUNT_X):
            for j in range(SLOT_COUNT_Y):
                if self.board_temp[i][j] != self.board[i][j]:
                    self.score += self.letter_score(self.board_temp[i][j])

    def letter_score(self, letter):
        return LETTERS_DICTIONARY[letter.letter_string]


if __name__ == "__main__":
    window = arcade.Window(SCREEN_WIDTH, SCREEN_HEIGHT, SCREEN_TITLE)
    ui_manager = UIManager()
    mainView = MainView()
    mainView.setup()
    window.show_view(mainView)
    arcade.run()
