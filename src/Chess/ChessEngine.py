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

    """
    Take a move object and apply it to the board
    """

    def makeMove(self, move):
        self.board[move.startRow][move.startCol] = "--" #piece is not at its start position anymore
        self.board[move.endRow][move.endCol] = move.pieceMoved #piece is now at its end position
        self.moveLog.append(move) #log the moves for display and more
        self.whiteToMove = not self.whiteToMove #swap whose turn it is

    """
    Undo the most recent move
    """

    def undoMove(self):
        if len(self.moveLog) != 0: #make sure there is a move to be undone
            move = self.moveLog.pop() #get the most recent move
            self.board[move.startRow][move.startCol] = move.pieceMoved #put the moved piece back to its start position
            self.board[move.endRow][move.endCol] = move.pieceCaptured #fill in the position it was moved to
            self.whiteToMove = not self.whiteToMove #swap whose turn it is
            print(Move.getChessNotation(move) + " was undone")
        else:
            print("There are no moves to undo")

    """
    All moves (including check avoidance)
    """

    def getValidMoves(self):
        return self.getAllPossibleMoves() #for now...

    """
    All moves (excluding check avoidance)
    """

    def getAllPossibleMoves(self): #This helper method is used to collate all moves so getValidMoves can pick which ones are valid at any point
        moves = []
        for row in range(len(self.board)): #num of rows
            for col in range(len(self.board[row])): #num of column in given row
                turn = self.board[row][col][-1]
                if (turn == "W" and self.whiteToMove) and (turn == "B" and not self.whiteToMove):
                    piece = self.board[row][col][0]
                    if piece == "p":
                        self.getPawnMoves(row, col, moves)
                    elif piece == "r":
                        self.getRookMoves(row, col, moves)
                    elif piece == "n":
                        self.getKnightMoves(row, col, moves)
                    elif piece == "b":
                        self.getBishopMoves(row, col, moves)
                    elif piece == "q":
                        self.getQueenMoves(row, col, moves)
                    elif piece == "k":
                        self.getKingMoves(row, col, moves)
        return moves

    """
    get all possible moves for pawn located at row, col and add them to the list
    """

    def getPawnMoves(self, row, col, moves):
        pass

    """
    get all possible moves for rook located at row, col and add them to the list
    """

    def getRookMoves(self, row, col, moves):
        pass

    """
    get all possible moves for knight located at row, col and add them to the list
    """

    def getKnightMoves(self, row, col, moves):
        pass

    """
    get all possible moves for bishop located at row, col and add them to the list
    """

    def getBishopMoves(self, row, col, moves):
        pass

    """
    get all possible moves for queen located at row, col and add them to the list
    """

    def getQueenMoves(self, row, col, moves):
        pass

    """
    get all possible moves for king located at row, col and add them to the list
    """

    def getKingMoves(self, row, col, moves):
        pass

class Move:
    ranksToRows = {"1":7, "2":6, "3":5, "4":4,
                   "5":3, "6":2, "7":1, "8":0}
    rowsToRanks = {v:k for k,v in ranksToRows.items()}
    #Both used to map rows/cols to ranks/files and vice versa
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
        self.moveID = self.startRow * 1000 + self.startCol * 100 + self.endRow * 10 + self.endCol #used to match Move objects

    """
    Overriding the equals method
    """

    def __eq__(self, other):
        if isinstance(other, Move):
            return self.moveID == other.moveID

    """
    Helpers to make move notation more readable
    """

    def getChessNotation(self):
        return self.getRankAndFile(self.startRow, self.startCol) + " -> " + self.getRankAndFile(self.endRow, self.endCol)

    def getRankAndFile(self, row, col):
        return self.colsToFiles[col] + self.rowsToRanks[row] #(5,5) -> F3