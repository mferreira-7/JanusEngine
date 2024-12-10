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
            ["rW", "nW", "bW", "qW", "kW", "bW", "nW", "rW"]
        ]
        self.moveFunctions = {"p":self.getPawnMoves, "r":self.getRookMoves, "n":self.getKnightMoves,
                              "b":self.getBishopMoves, "q":self.getQueenMoves, "k":self.getKingMoves}
        self.whiteToMove = True
        self.moveLog = []
        self.whiteKingLocation = (7, 4)
        self.blackKingLocation = (0, 4)
        self.checkmate = False
        self.stalemate = False

    """
    Take a move object and apply it to the board
    """

    def makeMove(self, move):
        self.board[move.startRow][move.startCol] = "--" #piece is not at its start position anymore
        self.board[move.endRow][move.endCol] = move.pieceMoved #piece is now at its end position
        self.moveLog.append(move) #log the moves for display and more
        self.whiteToMove = not self.whiteToMove #swap whose turn it is
        #update king location tuple
        if move.pieceMoved == "kW":
            self.whiteKingLocation = (move.endRow, move.endCol)
        elif move.pieceMoved == "kB":
            self.blackKingLocation = (move.endRow, move.endCol)

    """
    Undo the most recent move
    """

    def undoMove(self):
        if len(self.moveLog) != 0: #make sure there is a move to be undone
            move = self.moveLog.pop() #get the most recent move
            self.board[move.startRow][move.startCol] = move.pieceMoved #put the moved piece back to its start position
            self.board[move.endRow][move.endCol] = move.pieceCaptured #fill in the position it was moved to
            self.whiteToMove = not self.whiteToMove #swap whose turn it is
            #revert the update to king location tuple
            if move.pieceMoved == "kW":
                self.whiteKingLocation = (move.startRow, move.startCol)
            elif move.pieceMoved == "kB":
                self.blackKingLocation = (move.startRow, move.startCol)
        else:
            print("There are no moves to undo")

    """
    All moves (including check avoidance)
    """

    def getValidMoves(self):
        moves = self.getAllPossibleMoves()
        for i in range(len(moves)-1, -1, -1): #iterating through list going backwards to avoid removal bugs
            self.makeMove(moves[i])
            self.whiteToMove = not self.whiteToMove
            if self.inCheck():
                moves.remove(moves[i])
            self.whiteToMove = not self.whiteToMove
            self.undoMove()
        if len(moves) == 0: #checkmate or stalemate
            if self.inCheck():
                self.checkmate = True
            else:
                self.stalemate = True
        else:
            self.checkmate = False
            self.stalemate = False
        return moves

    """
    Determines if the current player is in check
    """

    def inCheck(self):
        if self.whiteToMove:
            return self.squareUnderAttack(self.whiteKingLocation[0], self.whiteKingLocation[1])
        else:
            return self.squareUnderAttack(self.blackKingLocation[0], self.blackKingLocation[1])

    """
    Determines if the enemy can attack square (row, col)
    """

    def squareUnderAttack(self, row, col):
        self.whiteToMove = not self.whiteToMove #switch to opponent POV
        opponentMoves = self.getAllPossibleMoves()
        self.whiteToMove = not self.whiteToMove #switch POV back
        for move in opponentMoves:
            if move.endRow == row and move.endCol == col: #square is under attack
                return True
        return False
    """
    All moves (excluding check avoidance)
    """

    def getAllPossibleMoves(self): #This helper method is used to collate all moves so getValidMoves can pick which ones are valid at any point
        moves = []
        for row in range(len(self.board)): #num of rows
            for col in range(len(self.board[row])): #num of column in given row
                turn = self.board[row][col][-1]
                if (turn == "W" and self.whiteToMove) or (turn == "B" and not self.whiteToMove):
                    piece = self.board[row][col][0]
                    self.moveFunctions[piece](row, col, moves) #calls the appropriate move function using the piece char
        return moves

    """
    get all possible moves for pawn located at row, col and add them to the list
    """

    def getPawnMoves(self, row, col, moves):
        if self.whiteToMove: #white pawn to move
            if self.board[row-1][col] == "--": #checking one square ahead
                moves.append(Move((row, col), (row-1, col), self.board))
                if row == 6 and self.board[row - 2][col] == "--": #checking two squares ahead (only if the first square is empty)
                    moves.append(Move((row, col), (row-2, col), self.board))
            if col-1 >= 0: #captures to the left diagonal
                if self.board[row-1][col-1][-1] == "B":
                    moves.append(Move((row, col), (row-1, col-1), self.board))
            if col+1 <= 7: #captures to the right diagonal
                if self.board[row-1][col+1][-1] == "B":
                    moves.append(Move((row, col), (row-1, col+1), self.board))
        else: #black pawn to move
            if self.board[row + 1][col] == "--":  # checking one square ahead
                moves.append(Move((row, col), (row + 1, col), self.board))
                if row == 1 and self.board[row + 2][col] == "--":  # checking two squares ahead (only if the first square is empty)
                    moves.append(Move((row, col), (row + 2, col), self.board))
            if col - 1 >= 0:  # captures to the left diagonal
                if self.board[row + 1][col - 1][-1] == "W":
                    moves.append(Move((row, col), (row + 1, col - 1), self.board))
            if col + 1 <= 7:  # captures to the right diagonal
                if self.board[row + 1][col + 1][-1] == "W":
                    moves.append(Move((row, col), (row + 1, col + 1), self.board))

    """
    get all possible moves for rook located at row, col and add them to the list
    """

    def getRookMoves(self, row, col, moves):
        possibleDirections = ((-1,0), (0,-1), (1,0), (0,1)) #4 directions
        enemyPieceColor = "B" if self.whiteToMove else "W"
        for direction in possibleDirections:
            for i in range(1, 8):
                endRow = row + direction[0] * i
                endCol = col + direction[1] * i
                if 0 <= endRow < 8 and 0 <= endCol < 8: #on the board
                    endPiece = self.board[endRow][endCol]
                    if endPiece == "--": #empty square
                        moves.append(Move((row, col), (endRow, endCol), self.board))
                    elif endPiece[-1] == enemyPieceColor: #enemy piece on square
                        moves.append(Move((row, col), (endRow, endCol), self.board))
                        break
                    else: #friendly piece on square
                        break
                else: #off the board
                    break



    """
    get all possible moves for knight located at row, col and add them to the list
    """

    def getKnightMoves(self, row, col, moves):
        possibleDestinations = ((-2,-1), (-2,1), (-1,-2), (-1,2), (1,-2), (1,2), (2,-1), (2,1)) #8 L shapes destinations
        friendlyPieceColor = "B" if not self.whiteToMove else "W"
        for destination in possibleDestinations:
            endRow = row + destination[0]
            endCol = col + destination[1]
            if 0 <= endRow < 8 and 0 <= endCol < 8:
                endPiece = self.board[endRow][endCol]
                if endPiece[-1] != friendlyPieceColor: #square not occupied by a friendly piece
                    moves.append(Move((row, col), (endRow, endCol), self.board))

    """
    get all possible moves for bishop located at row, col and add them to the list
    """

    def getBishopMoves(self, row, col, moves):
        possibleDirections = ((-1,-1), (-1,1), (1,-1), (1,1)) #4 diagonals
        enemyPieceColor = "B" if self.whiteToMove else "W"
        for direction in possibleDirections:
            for i in range(1, 8):
                endRow = row + direction[0] * i
                endCol = col + direction[1] * i
                if 0 <= endRow < 8 and 0 <= endCol < 8: #on the board
                    endPiece = self.board[endRow][endCol]
                    if endPiece == "--": #empty square
                        moves.append(Move((row, col), (endRow, endCol), self.board))
                    elif endPiece[-1] == enemyPieceColor: #enemy piece on square
                        moves.append(Move((row, col), (endRow, endCol), self.board))
                        break
                    else: #friendly piece on square
                        break
                else: #off the board
                    break

    """
    get all possible moves for queen located at row, col and add them to the list
    """

    def getQueenMoves(self, row, col, moves): #queen is just rook + bishop (all 8 directions)
        self.getRookMoves(row, col, moves)
        self.getBishopMoves(row, col, moves)


    """
    get all possible moves for king located at row, col and add them to the list
    """

    def getKingMoves(self, row, col, moves):
        possibleDirections = ((-1,-1), (-1,0), (-1,1), (0,-1), (0,1), (1,-1), (1,0), (1,1)) #8 directions
        friendlyPieceColor = "B" if not self.whiteToMove else "W"
        for i in range(8):
            endRow = row + possibleDirections[i][0]
            endCol = col + possibleDirections[i][1]
            if 0 <= endRow < 8 and 0 <= endCol < 8:
                endPiece = self.board[endRow][endCol]
                if endPiece[-1] != friendlyPieceColor: #square not occupied by a friendly piece
                    moves.append(Move((row, col), (endRow, endCol), self.board))


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
        if self.pieceCaptured == "--":
            return self.getRankAndFile(self.startRow, self.startCol) + " -> " + self.getRankAndFile(self.endRow, self.endCol)
        else:
            return self.getRankAndFile(self.startRow, self.startCol) + " -> " + self.getRankAndFile(self.endRow, self.endCol) + " [" + self.pieceMoved + " takes " + self.pieceCaptured + "]"

    def getRankAndFile(self, row, col):
        return self.colsToFiles[col] + self.rowsToRanks[row] #(5,5) -> F3