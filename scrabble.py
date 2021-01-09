import arcade
import os

from letters import *

SCREEN_WIDTH = 1280
SCREEN_HEIGHT = 900
# SCREEN_HEIGHT = 720
SCREEN_TITLE = "Basic board"
#dictionary for storing all letters and their respective points(https://www.thewordfinder.com/scrabble-point-values.php)
LETTERS_DICTIONARY = {'A': 1, 'B': 3, 'C': 3}


class ScrabbleGame(arcade.Window):
    """
    Attribute tile: A SpriteList that stores all the letters a player starts their game round with
    """

    def __init__(self, width, height, title):
        super().__init__(width, height, title)

        arcade.set_background_color(arcade.color.GREEN)

        file_path = os.path.dirname(os.path.abspath(__file__))
        os.chdir(file_path)

        self.background = None

        self.tile = arcade.SpriteList()

        self.heldLetter = None
        self.heldLetter_InitialPos = None

    # Call to restart game
    def setup(self):
        self.background = arcade.load_texture(os.path.join("images", "table.png"))
        vertical_offset = 400
        for alphabet in LETTERS_DICTIONARY:
            new_letter = Letter(alphabet)
            new_letter.center_x = 1100
            new_letter.center_y = new_letter.center_y + vertical_offset
            vertical_offset = vertical_offset + 150
            self.tile.append(new_letter)
        self.heldLetter = None
        self.heldLetter_InitialPos = ()

    # Called to calculate new frame
    def on_update(self, delta_time):
        pass

    # Called on frame draw
    def on_draw(self):
        arcade.start_render()

        arcade.draw_lrwh_rectangle_textured(0, 0,
                                            900, 900,
                                            self.background)
        for letters in self.tile:
            letters.draw()

    def on_mouse_press(self, x, y, button, key_modifiers):
        """ Called when the user presses a mouse button. """
        self.heldLetter = arcade.get_sprites_at_point((x, y), self.tile)[0]

    def on_mouse_release(self, x: float, y: float, button: int, modifiers: int):
        """ Called when the user presses a mouse button. """
        self.heldLetter = None

    def on_mouse_motion(self, x: float, y: float, dx: float, dy: float):
        """ User moves mouse """
        if self.heldLetter is not None:
            self.heldLetter.center_x += dx
            self.heldLetter.center_y += dy


if __name__ == "__main__":
    window = ScrabbleGame(SCREEN_WIDTH, SCREEN_HEIGHT, SCREEN_TITLE)
    window.setup()
    arcade.run()
