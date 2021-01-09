import arcade
LETTERS_DICTIONARY = {'A':1,'B':3,'C':3}

class Letter(arcade.Sprite):
    """
    Attribute letter_string: A string that denotes which alphabet each Letter object represents
    Attribute points: Number of points associated with each letter, according to Scrabble rules
    """

    def __init__(self, alphabet):
        filename = "images/"+alphabet+".png"
        super().__init__(filename)
        self.points = LETTERS_DICTIONARY[alphabet]
        self.letter_string = alphabet
