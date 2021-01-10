import os
import arcade
LETTERS_DICTIONARY = {'A': 1, 'B': 3, 'C': 3, 'D': 2, 'E': 1, 'F': 4, 'G': 2}


class Letter(arcade.Sprite):
    """
    Attribute letter_string: A string that denotes which alphabet each Letter object represents
    Attribute points: Number of points associated with each letter, according to Scrabble rules
    """

    def __init__(self, alphabet):
        filename = os.path.join("images/", alphabet+".png")
        self.points = LETTERS_DICTIONARY[alphabet]
        self.letter_string = alphabet
        # Variable to track whether block is moving
        self.movement = False
        # Variable to track whether block has been placed on the board
        self.placed = False
        # Starting coordinates (values set in first update)
        self.home_x = None
        self.home_y = None
        # Coordinates of movement start
        self.return_x = None
        self.return_y = None
        # Coordinates of valid placement
        self.placement_x = None
        self.placement_y = None
        self.return_speed = 4
        super().__init__(filename)

    def on_update(self, delta_time: float = 1/60):
        if self.home_x is None:
            self.home_x = self.center_x
            self.home_y = self.center_y
        if self.movement:
            if self.placed:
                self.move(delta_time, self.placement_x, self.placement_y)
            else:
                self.move(delta_time, self.home_x, self.home_y)

    def move(self, delta_time, target_x, target_y):
        # Move on the x-axis, capped at target_x
        if self.return_x < target_x:
            self.center_x += max(round((target_x - self.return_x) * self.return_speed * delta_time), 1)
            self.center_x = min(self.center_x, target_x)
        else:
            self.center_x += min(round((target_x - self.return_x) * self.return_speed * delta_time), -1)
            self.center_x = max(self.center_x, target_x)

        # Move on the y-axis, capped at target_y
        if self.return_y < target_y:
            self.center_y += max(round((target_y - self.return_y) * self.return_speed * delta_time), 1)
            self.center_y = min(self.center_y, target_y)
        else:
            self.center_y += min(round((target_y - self.return_y) * self.return_speed * delta_time), -1)
            self.center_y = max(self.center_y, target_y)

        if self.center_x == target_x and self.center_y == target_y:
            self.movement = False

    def place(self, coordinates):
        self.movement = True
        self.placed = True
        self.return_x = self.center_x
        self.return_y = self.center_y
        self.placement_x = coordinates[0]
        self.placement_y = coordinates[1]

    def return_home(self):
        self.movement = True
        self.placed = False
        self.return_x = self.center_x
        self.return_y = self.center_y

    def is_home(self):
        return self.center_x == self.home_x and self.center_y == self.home_y
