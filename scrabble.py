import os
import copy
import math
import random
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
LETTER_DECK = ["a" for i in range(9)] + \
              ["b" for i in range(2)] + \
              ["c" for i in range(2)] + \
              ["d" for i in range(4)] + \
              ["e" for i in range(12)] + \
              ["f" for i in range(2)] + \
              ["g" for i in range(3)] + \
              ["h" for i in range(2)] + \
              ["i" for i in range(9)] + \
              ["j" for i in range(1)] + \
              ["k" for i in range(1)] + \
              ["l" for i in range(4)] + \
              ["m" for i in range(2)] + \
              ["n" for i in range(6)] + \
              ["o" for i in range(8)] + \
              ["p" for i in range(2)] + \
              ["q" for i in range(1)] + \
              ["r" for i in range(6)] + \
              ["s" for i in range(4)] + \
              ["t" for i in range(6)] + \
              ["u" for i in range(4)] + \
              ["v" for i in range(2)] + \
              ["w" for i in range(2)] + \
              ["x" for i in range(1)] + \
              ["y" for i in range(2)] + \
              ["z" for i in range(1)]

STARTING_HAND = ["a" for i in range(2)] + \
                ["c"] +\
                ["e"] +\
                ["k"] +\
                ["n"] + \
                ["s"]
PLAYER_SLOTS = [[1100, 300 + SLOT_HEIGHT * i] for i in range(7)]


class SubmitButton(arcade.gui.UIFlatButton):
    def __init__(self, game, *args, **kwargs):
        self.game = game
        super(SubmitButton, self).__init__(*args, **kwargs)

    def on_click(self):
        self.game.check_board()


class InfoButton(arcade.gui.UIFlatButton):
    def on_click(self):
        print('Made by Shreya, Rauno and Ricky.')


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


def submit_click(self, game):
    game.check_board()


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
        for i in range(len(PLAYER_SLOTS)):
            self.create_letter(STARTING_HAND[i],
                               PLAYER_SLOTS[i][0], PLAYER_SLOTS[i][1],
                               i)
        self.heldLetter = None
        submit_button = SubmitButton(self, 'Submit move', center_x=1100, center_y=150, width=250)
        info_button = InfoButton('i', center_x=1250, center_y=875, width=50)
        ui_manager.add_ui_element(submit_button)
        ui_manager.add_ui_element(info_button)

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
            if len(self.pending_blocks) > 0:
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
        empty_slots = []
        for block in self.pending_blocks:
            self.inactive_blocks.append(block)
            empty_slots.append(block.home_slot_index)
        self.update_score()
        self.populate(empty_slots)
        self.pending_blocks = arcade.SpriteList()

    def populate(self, slots):
        new = self.new_letters(len(slots))
        for i in range(len(slots)):
            self.create_letter(new[i],
                               PLAYER_SLOTS[slots[i]][0], PLAYER_SLOTS[slots[i]][1],
                               slots[i])

    def create_letter(self, character, x, y, home_slot_index):
        new_letter = Letter(character)
        new_letter.center_x = x
        new_letter.center_y = y
        new_letter.home_slot_index = home_slot_index
        self.active_blocks.append(new_letter)

        return new_letter

    def update_score(self):
        for i in range(SLOT_COUNT_X):
            for j in range(SLOT_COUNT_Y):
                if self.board_temp[i][j] != self.board[i][j]:
                    self.score += self.letter_score(self.board_temp[i][j])
        self.board = []
        for i in range(SLOT_COUNT_X):
            self.board.append(copy.copy(self.board_temp[i]))

    def letter_score(self, letter_to_score):
        return LETTERS_DICTIONARY[letter_to_score.letter_string]

    def new_letters(self, tiles):
        # tiles is the number of new letters to generate(initially 7)
        letters = []
        for i in range(tiles):
            choice = random.choice(LETTER_DECK)
            letters.append(choice)
            LETTER_DECK.remove(choice)
        return letters


if __name__ == "__main__":
    window = arcade.Window(SCREEN_WIDTH, SCREEN_HEIGHT, SCREEN_TITLE)
    ui_manager = UIManager()
    mainView = MainView()
    mainView.setup()
    window.show_view(mainView)
    arcade.run()
