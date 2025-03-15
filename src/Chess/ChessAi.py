import random
import ChessEngine

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
DEPTH = 1 #maximum depth, must be (>2) for realistic bot gameplay

"""
Returns the next move in the opening book
"""

def findOpeningBookMove(gameState, blackString, whiteString, validMoves):
    blackMoves = blackString.strip('\n').split(", ")
    whiteMoves = whiteString.strip('\n').split(", ")
    whiteArray = [0,2,4,6,8,10]
    blackArray = [1,3,5,7,9,11]
    if len(gameState.moveLog) in whiteArray:
        chosenMove = whiteMoves[whiteArray.index(len(gameState.moveLog))] #e7 -> e5
        chosenMoveParts = chosenMove.split(" -> ")#e7,e5
        startingSqr = (ChessEngine.Move.ranksToRows[chosenMoveParts[0][1]], ChessEngine.Move.filesToCols[chosenMoveParts[0][0]])#e7 / 4,1
        endingSqr = (ChessEngine.Move.ranksToRows[chosenMoveParts[1][1]], ChessEngine.Move.filesToCols[chosenMoveParts[1][0]])#e5 / 4,3
        moveMatch = None
        for move in validMoves:
            if startingSqr[0] * 1000 + startingSqr[1] * 100 + endingSqr[0] * 10 + endingSqr[1] == move.moveID:
                moveMatch = move
        return moveMatch
    elif len(gameState.moveLog) in blackArray:
        chosenMove = blackMoves[blackArray.index(len(gameState.moveLog))] #e7 -> e5
        chosenMoveParts = chosenMove.split(" -> ")#e7,e5
        startingSqr = (ChessEngine.Move.ranksToRows[chosenMoveParts[0][1]], ChessEngine.Move.filesToCols[chosenMoveParts[0][0]])#e7 / 4,1
        endingSqr = (ChessEngine.Move.ranksToRows[chosenMoveParts[1][1]], ChessEngine.Move.filesToCols[chosenMoveParts[1][0]])#e5 / 4,3
        moveMatch = None
        for move in validMoves:
            if startingSqr[0] * 1000 + startingSqr[1] * 100 + endingSqr[0] * 10 + endingSqr[1] == move.moveID:
                moveMatch = move
        return moveMatch
"""
Returns a random valid move from the list of validMoves
"""

def findRandomMove(validMoves):
    return validMoves[random.randint(0, len(validMoves)-1)]

"""
Finds the best move frmo the list of validMoves based on some heuristic (pieceScore)
"""

def findBestMove(gameState, validMoves):
    global nextMove
    nextMove = None
    random.shuffle(validMoves)
    findMoveNegaMaxAlphaBeta(gameState, validMoves, DEPTH, -CHECKMATE, CHECKMATE, 1 if gameState.whiteToMove else -1)
    return nextMove

def findMoveNegaMaxAlphaBeta(gameState, validMoves, depth, alpha, beta, turnMultiplier):
    global nextMove
    if depth == 0:
        return turnMultiplier * scoreBoard(gameState)
    maxScore = -CHECKMATE
    validMoves.sort(key = lambda move: scoreMove(move, gameState), reverse = True)
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
Assign a score to a move for move ordering 
"""

def scoreMove(move, gameState):
    if move.pieceCaptured != "--":
        victim = move.pieceCaptured
        attacker = move.pieceMoved
        return 10 * pieceScore[victim[0]] - pieceScore[attacker[0]]  #MostValuableVictim-LeastValuableAttacker prioritization (MVV-LVA)
    if move.pieceCaptured[0] == "k":
        return 5
    if move.isPawnPromotion:
        return 7
    if move.isCastleMove:
        return 2
    return 0
