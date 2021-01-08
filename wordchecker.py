class WordChecker:
    def __init__(self, lang="en-US"):
        if lang == "en-US":
            import nltk
            nltk.download('words')
            from nltk.corpus import words
            self.words = set(words.words())

    def check(self, word):
        if word in self.words:
            return True
        return False
