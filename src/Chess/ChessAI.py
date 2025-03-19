import random
import ChessEngine

"""
Possible improvements:
Menu to select AI/Human
use numpy arrays instead of 2d arrays
investigate using bitboards 
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
ZOBRIST_TABLE = [[random.getrandbits(64) for _ in range(12)] for _ in range(64)]  #64 squares x 12 pieces
CHECKMATE = 1000
STALEMATE = 0 #better than a losing position (-x) but worse than a winning position (+x)
DEPTH = 1 #maximum depth, must be (>2) for realistic bot gameplay (Can be kept at 1 due to iterative deepening)
transposition_table = {}  #global dictionary to store evaluated positions

"""
Returns the move corresponding to the chosen agent action
"""

def findAgentMove(gameState, validMoves, Action):
    #get starting sq and ending sq from Action obj...
    actionMove = ChessEngine.Move("","",gameState.board)
    for move in validMoves:
        if move.__eq__(actionMove):
            return move
    return None

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
        for move in validMoves:
            if move.__eq__(ChessEngine.Move(startingSqr, endingSqr, gameState.board)):
                return move
        return None
    elif len(gameState.moveLog) in blackArray:
        chosenMove = blackMoves[blackArray.index(len(gameState.moveLog))] #e7 -> e5
        chosenMoveParts = chosenMove.split(" -> ")#e7,e5
        startingSqr = (ChessEngine.Move.ranksToRows[chosenMoveParts[0][1]], ChessEngine.Move.filesToCols[chosenMoveParts[0][0]])#e7 / 4,1
        endingSqr = (ChessEngine.Move.ranksToRows[chosenMoveParts[1][1]], ChessEngine.Move.filesToCols[chosenMoveParts[1][0]])#e5 / 4,3
        for move in validMoves:
            if move.__eq__(ChessEngine.Move(startingSqr, endingSqr, gameState.board)):
                return move
        return None
"""
Returns a random valid move from the list of validMoves
"""

def findRandomMove(validMoves):
    return validMoves[random.randint(0, len(validMoves)-1)]

"""
Finds the best move frmo the list of validMoves based on some heuristic (pieceScore)
"""

def findBestMove(gameState, validMoves):
    random.shuffle(validMoves)
    #findMoveNegaMaxAlphaBeta(gameState, validMoves, DEPTH, -CHECKMATE, CHECKMATE, 1 if gameState.whiteToMove else -1)
    chosenMove = iterativeDeepeningSearch(gameState, validMoves, DEPTH)
    return chosenMove

""" 
Iterative Deepening for better move ordering 
"""

def iterativeDeepeningSearch(gameState, validMoves, maxDepth):
    bestMove = None
    for depth in range(1, maxDepth + 1):
        score, move = findMoveNegaMaxAlphaBeta(gameState, validMoves, depth, -CHECKMATE, CHECKMATE, 1 if gameState.whiteToMove else -1)
        if move:
            bestMove = move  #store the best move found so far
    return bestMove

""" 
Negamax with Alpha-Beta Pruning and Transposition Table 
"""

def findMoveNegaMaxAlphaBeta(gameState, validMoves, depth, alpha, beta, turnMultiplier):
    global transposition_table
    position_hash = gameState.getHash(ZOBRIST_TABLE)  #unique position identifier (using Zobrist hashing)
    #check Transposition Table**
    if position_hash in transposition_table:
        stored_depth, stored_score, stored_move, flag = transposition_table[position_hash]
        if stored_depth >= depth:  #only used if stored depth is >= current search depth
            if flag == "EXACT":
                return stored_score, stored_move
            elif flag == "LOWERBOUND" and stored_score > alpha:
                alpha = stored_score
            elif flag == "UPPERBOUND" and stored_score < beta:
                beta = stored_score
            if alpha >= beta:  #cutoff if possible
                return stored_score, stored_move
    if depth == 0:
        return quiescenceSearch(gameState, alpha, beta, turnMultiplier), None  #capture stability check
    maxScore = -CHECKMATE
    bestMove = None
    #move ordering (sorted by heuristics)
    validMoves.sort(key=lambda m: scoreMove(m, gameState), reverse=True)
    for move in validMoves:
        gameState.makeMove(move)
        nextMoves = gameState.getValidMoves()
        score, _ = findMoveNegaMaxAlphaBeta(gameState, nextMoves, depth - 1, -beta, -alpha, -turnMultiplier)
        score = -score
        gameState.undoMove()
        if score > maxScore:
            maxScore = score
            bestMove = move
        alpha = max(alpha, maxScore)
        if alpha >= beta:
            break  #beta cutoff
    #store in Transposition Table
    if maxScore <= alpha:
        flag = "UPPERBOUND"
    elif maxScore >= beta:
        flag = "LOWERBOUND"
    else:
        flag = "EXACT"
    transposition_table[position_hash] = (depth, maxScore, bestMove, flag)
    return maxScore, bestMove


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
    if gameState.inCheck():
        return 8
    if move.isPawnPromotion:
        return 6
    if move.isEnpassantMove:
        return 4
    if move.isCastleMove:
        return 2
    return 1

""" 
Evaluates "noisy" positions deeper to avoid the horizon effect 
"""

def quiescenceSearch(gameState, alpha, beta, turnMultiplier):
    standPat = turnMultiplier * scoreBoard(gameState)
    if standPat >= beta:  #cutoff if the position is already good enough
        return beta
    if alpha < standPat:
        alpha = standPat  #improve alpha
    #get only captures (and maybe checks)
    captureMoves = [move for move in gameState.getValidMoves() if move.pieceCaptured != "--" or move.pieceCaptured[0] == "k"]
    for move in sorted(captureMoves, key=lambda m: scoreMove(m, gameState), reverse=True):
        gameState.makeMove(move)
        score = -quiescenceSearch(gameState, -beta, -alpha, -turnMultiplier)
        gameState.undoMove()
        if score >= beta:
            return beta  #beta cutoff
        if score > alpha:
            alpha = score  #update best score
    return alpha