import arcade
LETTERS_DICTIONARY = {'A':1,'B':3,'C':3}

class Letter(arcade.Sprite):
    #Hidden attributes
    #Attribute _points: Number of points associated with each letter, according to Scrabble rules

    def __init__(self, alphabet):
        filename = "images/"+alphabet+".png"
        super().__init__(filename)
        self._points = LETTERS_DICTIONARY[alphabet]
