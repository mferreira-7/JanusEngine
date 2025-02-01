import random

pieceScore = {"k":0, "q":10, "r":5, "b":3, "n":3, "p":1}
CHECKMATE = 1000
STALEMATE = 0 #better than a losing position (-x) but worse than a winning position (+x)
DEPTH = 1 #maximum depth, must be (>2) for realistic bot gameplay

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
    opponentMinMaxScore = CHECKMATE
    bestPlayerMove = None
    random.shuffle(validMoves)
    for playerMove in validMoves:
        gameState.makeMove(playerMove)
        opponentMoves = gameState.getValidMoves()
        if gameState.stalemate:
            opponentMaxScore = -STALEMATE
        elif gameState.checkmate:
            opponentMaxScore = -CHECKMATE
        else:
            opponentMaxScore = -CHECKMATE
            for opponentMove in opponentMoves:
                gameState.makeMove(opponentMove)
                gameState.getValidMoves()
                if gameState.checkmate:
                    score = CHECKMATE
                elif gameState.stalemate:
                    score = STALEMATE
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

def findBestMove(gameState, validMoves): #reassigned
    global nextMove
    nextMove = None
    random.shuffle(validMoves)
    findMoveNegaMax(gameState, validMoves, DEPTH, 1 if gameState.whiteToMove else -1)
    return nextMove


def findMoveMinMax(gameState, validMoves, depth, whiteToMove):
    global nextMove #just learned this :)
    if depth == 0:
        return scoreBoard(gameState)
    if whiteToMove: #maximise
        maxScore = -CHECKMATE
        for move in validMoves:
            gameState.makeMove(move)
            nextMoves = gameState.getValidMoves()
            score = findMoveMinMax(gameState, nextMoves, depth-1, False)
            if score > maxScore:
                maxScore = score
                if depth == DEPTH:
                    nextMove = move
            gameState.undoMove()
        return maxScore
    else: #minimise
        minScore = CHECKMATE
        for move in validMoves:
            gameState.makeMove(move)
            nextMoves = gameState.getValidMoves()
            score = findMoveMinMax(gameState, nextMoves, depth-1, True)
            if score < minScore:
                minScore = score
                if depth == DEPTH:
                    nextMove = move
            gameState.undoMove()
        return minScore

def findMoveNegaMax(gameState, validMoves, depth, turnMultiplier):
    global nextMove
    if depth == 0:
        return turnMultiplier * scoreBoard(gameState)
    maxScore = -CHECKMATE
    for move in validMoves:
        gameState.makeMove(move)
        nextMoves = gameState.getValidMoves()
        score = -findMoveNegaMax(gameState, nextMoves, depth-1, -turnMultiplier) #turnMult is either -1 (Black) or 1 (White), so -turnMult will switch color
        if score > maxScore:
            maxScore = score
            if depth == DEPTH:
                nextMove = move
        gameState.undoMove()
    return maxScore

"""
positive score is good for white, negative score is good for black
"""

def scoreBoard(gameState):
    if gameState.checkmate:
        if gameState.whiteToMove:
            return -CHECKMATE #black win
        else:
            return CHECKMATE #white win
    elif gameState.stalemate:
        return STALEMATE

    score = 0
    for row in gameState.board:
        for square in row:
            if square[-1] == "W":
                score += pieceScore[square[0]]
            elif square[-1] == "B":
                score -= pieceScore[square[0]]
    return score

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