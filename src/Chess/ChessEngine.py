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
            ["--", "--", "--", "--", "--", "--", "--", "--"],#8x8 2d array, each element has two chars representing the piece (typeCOLOR) or 2 dashes for no piece
            ["--", "--", "--", "--", "--", "--", "--", "--"],#could be using a numpy array
            ["--", "--", "--", "--", "--", "--", "--", "--"],
            ["pW", "pW", "pW", "pW", "pW", "pW", "pW", "pW"],
            ["rW", "nW", "bW", "qW", "kW", "bW", "nW", "rW"]]
        self.whiteToMove = True
        self.moveLog = []

    def makeMove(self, move):
        self.board[move.startRow][move.startCol] = "--" #piece is not at its start position anymore
        self.board[move.endRow][move.endCol] = move.pieceMoved #piece is now at its end position
        self.moveLog.append(move) #log the moves for display and more
        self.whiteToMove = not self.whiteToMove #swap whose turn it is

    def undoMove(self):
        if len(self.moveLog) != 0: #make sure there is a move to be undone
            move = self.moveLog.pop() #get the most recent move
            self.board[move.startRow][move.startCol] = move.pieceMoved #put the moved piece back to its start position
            self.board[move.endRow][move.endCol] = move.pieceCaptured #fill in the position it was moved to
            self.whiteToMove = not self.whiteToMove #swap whose turn it is
            print(Move.getChessNotation(move) + " was undone")

class Move:
    ranksToRows = {"1":7, "2":6, "3":5, "4":4,
                   "5":3, "6":2, "7":1, "8":0}
    rowsToRanks = {v:k for k,v in ranksToRows.items()}

    filesToCols = {"a":0, "b":1, "c":2, "d":3,
                   "e":4, "f":5, "g":6, "h":7,}
    colsToFiles = {v:k for k,v in filesToCols.items()}
    def __init__(self, startSq, endSq, board):
        self.startRow = startSq[0]
        self.startCol = startSq[1]
        self.endRow = endSq[0]
        self.endCol = endSq[1]
        self.pieceMoved = board[self.startRow][self.startCol]
        self.pieceCaptured = board[self.endRow][self.endCol] #will be -- if no piece is captured

    def getChessNotation(self):
        return self.getRankAndFile(self.startRow, self.startCol) + " -> " + self.getRankAndFile(self.endRow, self.endCol)

    def getRankAndFile(self, row, col):
        return self.colsToFiles[col] + self.rowsToRanks[row] #(5,5) -> F3

