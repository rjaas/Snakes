import arcade
import arcade.gui
from arcade.gui import UIManager
import os

SCREEN_WIDTH = 1280
SCREEN_HEIGHT = 900

class MyButton(arcade.gui.UIFlatButton):
    def on_click(self):
        print("Click button event")

class MainView(arcade.View):
    def __init__(self):
        super().__init__()
        self.ui_manager = UIManager()
    
    def on_draw(self):
        arcade.start_render()
        arcade.draw_text("Scrabble", 500, 500, arcade.color.BLACK, font_size=80)
    
    def on_show_view(self):
        self.setup()
        arcade.set_background_color(arcade.color.WHITE)
    
    def setup(self):
        button = MyButton('Play', center_x=200, center_y=200, width=250)
        button2 = MyButton('Help', center_x=300, center_y=300, width=250)
        self.ui_manager.add_ui_element(button)
        self.ui_manager.add_ui_element(button2)

class Game(arcade.View):
    def on_draw(self):
        arcade.start_render()

class Options(arcade.View):
    def on_draw(self):
        arcade.start_render()



if __name__ == "__main__":
    window = arcade.Window(SCREEN_WIDTH, SCREEN_HEIGHT, title="GUI")
    view = MainView()
    window.show_view(view)
    arcade.run()