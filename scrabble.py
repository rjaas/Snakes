import arcade
import os

SCREEN_WIDTH = 1280
SCREEN_HEIGHT = 900
# SCREEN_HEIGHT = 720
SCREEN_TITLE = "Basic board"


class ScrabbleGame(arcade.Window):

    def __init__(self, width, height, title):
        super().__init__(width, height, title)

        arcade.set_background_color(arcade.color.GREEN)

        file_path = os.path.dirname(os.path.abspath(__file__))
        os.chdir(file_path)

        self.background = None

    # Call to restart game
    def setup(self):
        self.background = arcade.load_texture(os.path.join("images", "table.png"))

    # Called to calculate new frame
    def on_update(self, delta_time):
        pass

    # Called on frame draw
    def on_draw(self):
        arcade.start_render()

        arcade.draw_lrwh_rectangle_textured(0, 0,
                                            900, 900,
                                            self.background)


if __name__ == "__main__":
    window = ScrabbleGame(SCREEN_WIDTH, SCREEN_HEIGHT, SCREEN_TITLE)
    window.setup()
    arcade.run()
