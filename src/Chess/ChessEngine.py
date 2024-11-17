"""
Stores information about the current state of the chess game
Determines legal moves from the current state
Logs past moves, so they can be reversed
"""

class GameState:
    def __init__(self):
        self.board = [
            ["rB", "nB", "bB", "qB", "kB", "bB", "nB", "rB"],
            ["pB", "pB", "pB", "pB", "pB", "pB", "pB", "pB"],
            ["--", "--", "--", "--", "--", "--", "--", "--"],
            ["--", "--", "--", "--", "--", "--", "--", "--"], #8x8 2d array, each element has two chars representing the piece (typeCOLOR) or 2 dashes for no piece
            ["--", "--", "--", "--", "--", "--", "--", "--"], #could be using a numpy array
            ["--", "--", "--", "--", "--", "--", "--", "--"],
            ["pW", "pW", "pW", "pW", "pW", "pW", "pW", "pW"],
            ["rW", "nW", "bW", "qW", "kW", "bW", "nW", "rW"]]
        self.whiteToMove = True
        self.moveLog = []
