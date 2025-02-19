import random

"""
Possible improvements:
Menu to select AI/Human
use numpy arrays instead of 2d arrays
investigate using bitboards 
create or use database of openings "opening book"
transposition table (zobrist alogrithm)
add 50 move draw and 3 move repeating draw rule or limit moves to the amount i can fit on screen 
move  ordering - look at checks, captures and threats first, prioritize castling/king safety, look at pawn moves last (this will improve alpha-beta pruning). Also start with moves that previously scored higher (will also improve pruning).
-Calculate both players moves given a position
-Change move calculation to make it more efficient. Instead of recalculating all moves, start with moves from previous board and change based on last move made
"""

"""
Time to run a full game at depth 3:

after piece positional scores - 24mins
"""

pieceScore = {"k":0, "q":10, "r":5, "b":3, "n":3, "p":1}
blackPawnScores = [ #heatmap to show where black pawns are most valuable
    [0,0,0,0,0,0,0,0],
    [1,1,1,0,0,1,1,1],
    [1,1,2,3,3,2,1,1],
    [1,2,3,4,4,3,2,1],
    [2,3,3,5,5,3,3,2],
    [5,6,6,7,7,6,6,5],
    [8,8,8,8,8,8,8,8],
    [8,8,8,8,8,8,8,8]
]
whitePawnScores = [ #heatmap to show where white pawns are most valuable
    [8,8,8,8,8,8,8,8],
    [8,8,8,8,8,8,8,8],
    [5,6,6,7,7,6,6,5],
    [2,3,3,5,5,3,3,2],
    [1,2,3,4,4,3,2,1],
    [1,1,2,3,3,2,1,1],
    [1,1,1,0,0,1,1,1],
    [0,0,0,0,0,0,0,0]
]
knightScores = [ #heatmap to show where knights are most valuable
    [1,1,1,1,1,1,1,1],
    [1,2,2,2,2,2,2,1],
    [1,2,3,3,3,3,2,1],
    [1,2,3,4,4,3,2,1],
    [1,2,3,4,4,3,2,1],
    [1,2,3,3,3,3,2,1],
    [1,2,2,2,2,2,2,1],
    [1,1,1,1,1,1,1,1]
]
bishopScores = [ #heatmap to show where bishops are most valuable
    [4,3,2,1,1,2,3,4],
    [3,4,3,2,2,3,4,3],
    [2,3,4,3,3,4,3,2],
    [1,2,3,4,4,3,2,1],
    [1,2,3,4,4,3,2,1],
    [2,3,4,3,3,4,3,2],
    [3,4,3,2,2,3,4,3],
    [4,3,2,1,1,2,3,4]
]
rookScores = [ #heatmap to show where rooks are most valuable
    [4,3,4,4,4,4,3,4],
    [4,4,4,4,4,4,4,4],
    [1,1,2,3,3,2,1,1],
    [1,2,3,4,4,3,2,1],
    [1,2,3,4,4,3,2,1],
    [1,1,2,2,2,2,1,1],
    [4,4,4,4,4,4,4,4],
    [4,3,4,4,4,4,3,4]
]
queenScores = [ #heatmap to show where queens are most valuable
    [1,1,1,3,1,1,1,1],
    [1,2,3,3,3,1,1,1],
    [1,4,3,3,3,4,2,1],
    [1,2,3,3,3,2,2,1],
    [1,2,3,3,3,2,2,1],
    [1,4,3,3,3,4,2,1],
    [1,1,2,3,3,1,1,1],
    [1,1,1,3,1,1,1,1]
]
piecePositionalScores = {"q":queenScores, "r":rookScores, "b":bishopScores, "n":knightScores, "pW":whitePawnScores, "pB":blackPawnScores}
CHECKMATE = 1000
STALEMATE = 0 #better than a losing position (-x) but worse than a winning position (+x)
DEPTH = 2 #maximum depth, must be (>2) for realistic bot gameplay

"""
Returns a random valid move from the list of validMoves
"""

def findRandomMove(validMoves):
    return validMoves[random.randint(0, len(validMoves)-1)]

"""
Finds the best move frmo the list of validMoves based on some heuristic (pieceScore)
"""

def findBestMoveNoRecursion(gameState, validMoves):
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
                    score = -turnMultiplier * scoreBoard(gameState.board)
                if score > opponentMaxScore:
                    opponentMaxScore = score
                gameState.undoMove()
        if opponentMaxScore < opponentMinMaxScore:
            opponentMinMaxScore = opponentMaxScore
            bestPlayerMove = playerMove
        gameState.undoMove()
    return bestPlayerMove

def findBestMove(gameState, validMoves):
    global nextMove
    nextMove = None
    random.shuffle(validMoves)
    findMoveNegaMaxAlphaBeta(gameState, validMoves, DEPTH, -CHECKMATE, CHECKMATE, 1 if gameState.whiteToMove else -1)
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

def findMoveNegaMaxAlphaBeta(gameState, validMoves, depth, alpha, beta, turnMultiplier):
    global nextMove
    if depth == 0:
        return turnMultiplier * scoreBoard(gameState)
    maxScore = -CHECKMATE
    for move in validMoves:
        gameState.makeMove(move)
        nextMoves = gameState.getValidMoves()
        score = -findMoveNegaMaxAlphaBeta(gameState, nextMoves, depth-1, -beta, -alpha, -turnMultiplier) #turnMult is either -1 (Black) or 1 (White), so -turnMult will switch color
        if score > maxScore:
            maxScore = score
            if depth == DEPTH:
                nextMove = move
        gameState.undoMove()
        if maxScore > alpha: #pruning
            alpha = maxScore
        if alpha >= beta:
            break
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
    for row in range(len(gameState.board)):
        for col in range(len(gameState.board[row])):
            square = gameState.board[row][col]
            if square != "--":
                piecePositionalScore=0
                #score by position
                if square[0] not in ["p","k"]:
                    piecePositionalScore = piecePositionalScores[square[0]][row][col]
                elif square[0] == "p":
                    piecePositionalScore = piecePositionalScores[square][row][col]
                if square[-1] == "W":
                    score += pieceScore[square[0]] + piecePositionalScore * .1 #scaling
                elif square[-1] == "B":
                    score -= pieceScore[square[0]] + piecePositionalScore * .1 #scaling
    return score

"""
Return a score for the board based on material (OLD)

def scoreMaterial(board):
    score = 0
    for row in board:
        for square in row:
            if square[-1] == "W":
                score += pieceScore[square[0]]
            elif square[-1] == "B":
                score -= pieceScore[square[0]]
    return score

"""