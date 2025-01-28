import random

pieceScore = {"k":0, "q":10, "r":5, "b":3, "n":3, "p":1}
checkmateScore = 1000
stalemateScore = 0 #better than a losing position (-x) but worse than a winning position (+x)

"""
Returns a random valid move from the list of validMoves
"""

def findRandomMove(validMoves):
    return validMoves[random.randint(0, len(validMoves)-1)]

"""
Finds the best move frmo the list of validMoves based on some heuristic (pieceScore)
"""

def findBestMove(gameState, validMoves):
    turnMultiplier = 1 if gameState.whiteToMove else -1
    opponentMinMaxScore = checkmateScore
    bestPlayerMove = None
    random.shuffle(validMoves)
    for playerMove in validMoves:
        gameState.makeMove(playerMove)
        opponentMoves = gameState.getValidMoves()
        opponentMaxScore = -checkmateScore
        for opponentMove in opponentMoves:
            gameState.makeMove(opponentMove)
            if gameState.checkmate:
                score = -turnMultiplier * checkmateScore
            elif gameState.stalemate:
                score = stalemateScore
            else:
                score = -turnMultiplier * scoreMaterial(gameState.board)
            if score > opponentMaxScore:
                opponentMaxScore = score
            gameState.undoMove()
        if opponentMaxScore < opponentMinMaxScore:
            opponentMinMaxScore = opponentMaxScore
            bestPlayerMove = playerMove
        gameState.undoMove()
    return bestPlayerMove

"""
Return a score for the board based on material
"""

def scoreMaterial(board):
    score = 0
    for row in board:
        for square in row:
            if square[-1] == "W":
                score += pieceScore[square[0]]
            elif square[-1] == "B":
                score -= pieceScore[square[0]]
    return score