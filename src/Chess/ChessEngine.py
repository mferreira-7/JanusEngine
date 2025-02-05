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
        self.enpassantPossible = () #sqr where enpassant is possible
        self.currentCastlingRights = CastleRights(True, True, True, True)
        self.castleRightsLog = [CastleRights(self.currentCastlingRights.wks, self.currentCastlingRights.bks,
                                             self.currentCastlingRights.wqs, self.currentCastlingRights.bqs)]

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
        #pawn promotion
        if move.isPawnPromotion:
            self.board[move.endRow][move.endCol] = "q" + move.pieceMoved[-1]
        #enpassant
        if move.isEnpassantMove:
            self.board[move.startRow][move.endCol] = "--"
        #update enpassant possibility (only on pawn's two sqr advances)
        if move.pieceMoved[0] == "p" and abs(move.startRow - move.endRow) == 2:
            self.enpassantPossible = ((move.startRow + move.endRow) // 2, move.startCol)
        else:
            self.enpassantPossible = ()
        #castle move
        if move.isCastleMove:
            if move.endCol - move.startCol == 2: #kingside castle
                self.board[move.endRow][move.endCol - 1] = self.board[move.endRow][move.endCol + 1]
                self.board[move.endRow][move.endCol + 1] = "--"
            else: #queenside casle
                self.board[move.endRow][move.endCol + 1] = self.board[move.endRow][move.endCol - 2]
                self.board[move.endRow][move.endCol - 2] = "--"
        #update castling rights (rook or king move)
        self.updateCastleRights(move)
        self.castleRightsLog.append(CastleRights(self.currentCastlingRights.wks, self.currentCastlingRights.bks,
                                             self.currentCastlingRights.wqs, self.currentCastlingRights.bqs))

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
            #undo enpassant move
            if move.isEnpassantMove:
                self.board[move.endRow][move.endCol] = "--"
                self.board[move.startRow][move.endCol] = move.pieceCaptured
                self.enpassantPossible = (move.endRow, move.endCol)
            #undo enpassant possibility after a 2 sqr move
            if move.pieceMoved[0] == "p" and abs(move.startRow - move.endRow) == 2:
                self.enpassantPossible = ()
            #undo castling rights
            self.castleRightsLog.pop() #remove most recent castle right
            self.currentCastlingRights = self.castleRightsLog[-1] #make NEW most recent castle rights the current castle rights
            #undo castle move
            if move.isCastleMove:
                if move.endCol - move.startCol == 2: #kingside castle
                    self.board[move.endRow][move.endCol + 1] = self.board[move.endRow][move.endCol - 1]
                    self.board[move.endRow][move.endCol - 1] = "--"
                else: #queenside castle
                    self.board[move.endRow][move.endCol - 2] = self.board[move.endRow][move.endCol + 1]
                    self.board[move.endRow][move.endCol + 1] = "--"
            self.checkmate = False
            self.stalemate = False
        else:
            print("There are no moves to undo")


    """
    Update the castling rights based on the most recent move
    """

    def updateCastleRights(self, move):
        if move.pieceMoved == "kW":
            self.currentCastlingRights.wks = False
            self.currentCastlingRights.wqs = False
        elif move.pieceMoved == "kB":
            self.currentCastlingRights.bks = False
            self.currentCastlingRights.bqs = False
        elif move.pieceMoved == "rW":
            if move.startRow == 7:
                if move.startCol == 0: #left rook
                    self.currentCastlingRights.wqs = False
                elif move.startCol == 7: #right rook
                    self.currentCastlingRights.wks = False
        elif move.pieceMoved == "rB":
            if move.startRow == 0:
                if move.startCol == 0: #left rook
                    self.currentCastlingRights.bqs = False
                elif move.startCol == 7: #right rook
                    self.currentCastlingRights.bks = False
        #if the rook is taken
        if move.pieceCaptured == "rW":
            if move.endRow == 7:
                if move.endCol == 0:
                    self.currentCastlingRights.wqs = False
                elif move.endCol == 7:
                    self.currentCastlingRights.wks = False
        elif move.pieceCaptured == "rB":
            if move.endRow == 0:
                if move.endCol == 0:
                    self.currentCastlingRights.bqs = False
                elif move.endCol == 7:
                    self.currentCastlingRights.bks = False


    """
    All moves (including check avoidance)
    """

    def getValidMoves(self):
        tempEnpassantPossible = self.enpassantPossible
        tempCastleRights = CastleRights(self.currentCastlingRights.wks, self.currentCastlingRights.bks,
                                        self.currentCastlingRights.wqs, self.currentCastlingRights.bqs)
        moves = self.getAllPossibleMoves()
        if self.whiteToMove:
            self.getCastleMoves(self.whiteKingLocation[0], self.whiteKingLocation[1], moves)
        else:
            self.getCastleMoves(self.blackKingLocation[0], self.blackKingLocation[1], moves)
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
        self.enpassantPossible = tempEnpassantPossible
        self.currentCastlingRights = tempCastleRights
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
                elif (row-1, col-1) == self.enpassantPossible:
                    moves.append(Move((row, col), (row - 1, col - 1), self.board, isEnpassantMove=True))
            if col+1 <= 7: #captures to the right diagonal
                if self.board[row-1][col+1][-1] == "B":
                    moves.append(Move((row, col), (row-1, col+1), self.board))
                elif (row-1, col+1) == self.enpassantPossible:
                    moves.append(Move((row, col), (row - 1, col + 1), self.board, isEnpassantMove=True))

        else: #black pawn to move
            if self.board[row + 1][col] == "--":  # checking one square ahead
                moves.append(Move((row, col), (row + 1, col), self.board))
                if row == 1 and self.board[row + 2][col] == "--":  # checking two squares ahead (only if the first square is empty)
                    moves.append(Move((row, col), (row + 2, col), self.board))
            if col - 1 >= 0:  # captures to the left diagonal
                if self.board[row + 1][col - 1][-1] == "W":
                    moves.append(Move((row, col), (row + 1, col - 1), self.board))
                elif (row+1, col-1) == self.enpassantPossible:
                    moves.append(Move((row, col), (row + 1, col - 1), self.board, isEnpassantMove=True))
            if col + 1 <= 7:  # captures to the right diagonal
                if self.board[row + 1][col + 1][-1] == "W":
                    moves.append(Move((row, col), (row + 1, col + 1), self.board))
                elif (row+1, col+1) == self.enpassantPossible:
                    moves.append(Move((row, col), (row + 1, col + 1), self.board, isEnpassantMove=True))

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

    """
    generate all castle moves for king located at row, col and add them to the list
    """

    def getCastleMoves(self, row, col, moves):
        if self.squareUnderAttack(row, col):
            return #Case 1 - cannot castle if in check
        if (self.whiteToMove and self.currentCastlingRights.wks) or (not self.whiteToMove and self.currentCastlingRights.bks):
            self.getKingSideCastleMoves(row, col, moves)
        if (self.whiteToMove and self.currentCastlingRights.wqs) or (not self.whiteToMove and self.currentCastlingRights.bqs):
            self.getQueenSideCastleMoves(row, col, moves)

    def getKingSideCastleMoves(self, row, col, moves):
        if self.board[row][col+1] == "--" and self.board[row][col+2] == "--": #Case 2 - cannot castle if either of the two sqrs are occupied
            if not self.squareUnderAttack(row, col+1) and not self.squareUnderAttack(row, col+2): #Case 3 - cannot castle if either of the two sqrs are under attack
                moves.append(Move((row, col), (row, col+2), self.board, isCastleMove = True))

    def getQueenSideCastleMoves(self, row, col, moves):
        if self.board[row][col-1] == "--" and self.board[row][col-2] == "--" and self.board[row][col-3] == "--": #Case 2 - three sqrs for Qside but same logic
            if not self.squareUnderAttack(row, col-1) and not self.squareUnderAttack(row, col-2): #Case 3
                moves.append(Move((row, col), (row, col-2), self.board, isCastleMove = True))

class CastleRights:
    def  __init__(self, wks, bks, wqs, bqs):
        self.wks = wks
        self.bks = bks
        self.wqs = wqs
        self.bqs = bqs

class Move:
    ranksToRows = {"1":7, "2":6, "3":5, "4":4,
                   "5":3, "6":2, "7":1, "8":0}
    rowsToRanks = {v:k for k,v in ranksToRows.items()}
    #Both used to map rows/cols to ranks/files and vice versa
    filesToCols = {"a":0, "b":1, "c":2, "d":3,
                   "e":4, "f":5, "g":6, "h":7,}
    colsToFiles = {v:k for k,v in filesToCols.items()}
    def __init__(self, startSq, endSq, board, isEnpassantMove=False, isCastleMove=False):
        self.startRow = startSq[0]
        self.startCol = startSq[1]
        self.endRow = endSq[0]
        self.endCol = endSq[1]
        self.pieceMoved = board[self.startRow][self.startCol]
        self.pieceCaptured = board[self.endRow][self.endCol] #will be -- if no piece is captured
        self.isPawnPromotion = (self.pieceMoved == "pW" and self.endRow == 0) or (self.pieceMoved == "pB" and self.endRow == 7)
        self.isEnpassantMove = isEnpassantMove
        if self.isEnpassantMove:
            self.pieceCaptured = "pW" if self.pieceMoved == "pB" else "pB"
        self.isCastleMove = isCastleMove
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