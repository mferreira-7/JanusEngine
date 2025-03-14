"""
Handles user input and displays the current game state
"""
import pygame as pg
import ChessEngine, ChessAi
import random
from multiprocessing import Process, Queue

BOARD_WIDTH = BOARD_HEIGHT = 512  #this could be 400
MOVE_LOG_PANEL_WIDTH = 250
MOVE_LOG_PANEL_HEIGHT = BOARD_HEIGHT
DIMENSION = 8  #chess board is 8x8
SQ_SIZE = BOARD_HEIGHT // DIMENSION
MAX_FPS = 15  #possible animations
IMAGES = {}

"""
Initialising opening books
"""

with open("data/BlackGrandmasterOpenings.csv", "r") as file:
    bOpenings = []
    for row in file:
        bOpenings.append(row)
    bOpening = bOpenings[random.randint(0,24)]

with open("data/WhiteGrandmasterOpenings.csv", "r") as file:
    wOpenings = []
    for row in file:
        wOpenings.append(row)
    wOpening = wOpenings[random.randint(0,24)]

"""
Initialising the global dictionary to hold images, this will benefit performance
"""

def loadImages():
    pieces = ["rB", "nB", "bB", "qB", "kB", "pB", "pW", "rW", "nW", "bW", "qW", "kW"]
    for piece in pieces:
        IMAGES[piece] = pg.transform.scale(pg.image.load("images/" + piece + ".png"),(SQ_SIZE, SQ_SIZE))  #IMAGES["pB"] will return the black pawn image

"""
main function for handling user input and updating the graphics
"""

def main():
    pg.init()
    screen = pg.display.set_mode((BOARD_WIDTH+MOVE_LOG_PANEL_WIDTH, BOARD_HEIGHT))
    clock = pg.time.Clock()
    screen.fill(pg.Color('white'))
    moveLogFont = pg.font.SysFont("Arial", 12, False, False)
    gameState = ChessEngine.GameState()
    validMoves = gameState.getValidMoves()
    moveMade = False #debouncer for when a move is made
    loadImages()  #only once
    running = True
    sqSelected = () #tracks the last click of the user (row, col)
    playerClicks = [] #tracks a pair of player clicks [(6,4), (4,4)]
    gameOver = False
    playerOne = True #if human is playing white, this is true. if ai this is false
    playerTwo = True #as above but for black
    while running:
        humanTurn = (gameState.whiteToMove and playerOne) or (not gameState.whiteToMove and playerTwo)
        for event in pg.event.get():
            if event.type == pg.QUIT: #quit handler
                running = False
            elif event.type == pg.MOUSEBUTTONDOWN: #mouse handler
                if not gameOver and humanTurn:
                    location = pg.mouse.get_pos() #(x, y) position of mouse
                    col = location[0] // SQ_SIZE
                    row = location[1] // SQ_SIZE
                    if sqSelected == (row, col) or col >= 8: #user clicked the same sq twice or clicked move log
                        sqSelected = () #deselect
                        playerClicks = [] #clear clicks
                    else:
                        sqSelected = (row, col)
                        playerClicks.append(sqSelected)
                    if len(playerClicks) == 2: #2nd click
                        move = ChessEngine.Move(playerClicks[0], playerClicks[1], gameState.board)
                        for i in range(len(validMoves)):
                            if move == validMoves[i]:
                                gameState.makeMove(validMoves[i])
                                print(str(move.getChessNotation()))
                                moveMade = True
                                sqSelected = ()  # reset clicks
                                playerClicks = []
                        if not moveMade:
                            playerClicks = [sqSelected]
            elif event.type == pg.KEYDOWN: #key handler
                if event.key == pg.K_z:
                    gameState.undoMove()
                    moveMade = True
                    gameOver = False
                if event.key == pg.K_r:
                    gameState = ChessEngine.GameState()
                    validMoves = gameState.getValidMoves()
                    sqSelected = ()
                    playerClicks = []
                    moveMade = False
                    gameOver = False
                if event.key == pg.K_1:
                    controller = "human" if playerOne is False else "bot"
                    playerOne = not playerOne
                    print("White is now a " + controller)
                if event.key == pg.K_2:
                    controller = "human" if playerTwo is False else "bot"
                    playerTwo = not playerTwo
                    print("Black is now a " + controller)
        #ai move finder
        if not gameOver and not humanTurn:
            AIMove = ChessAi.findOpeningBookMove(gameState, bOpening, wOpening, validMoves)
            if AIMove is None:
                AIMove = ChessAi.findBestMove(gameState, validMoves)
                if AIMove is None:
                    AIMove = ChessAi.findRandomMove(validMoves)
            gameState.makeMove(AIMove)
            moveMade = True
            print("BOT MOVE: " + str(AIMove.getChessNotation()))
        if moveMade:
            validMoves = gameState.getValidMoves()
            moveMade = False
        drawGameState(screen, gameState, validMoves, sqSelected, moveLogFont)
        #game over
        if gameState.checkmate:
            gameOver = True
            if gameState.whiteToMove:
                drawEndGameText(screen, "Black wins by checkmate")
            else:
                drawEndGameText(screen, "White wins by checkmate")
        elif gameState.stalemate:
            gameOver = True
            drawEndGameText(screen, "Stalemate")
        clock.tick(MAX_FPS)
        pg.display.flip()

"""
Highight selected square and moves
"""

def highlightSquares(screen, gameState, validMoves, sqSelected):
    if sqSelected != ():
        row, col = sqSelected
        if gameState.board[row][col][-1] == ("W" if gameState.whiteToMove else "B"): #sqSelected piece can be moved
            #highlight selected sqr
            s = pg.Surface((SQ_SIZE, SQ_SIZE))
            s.set_alpha(100) #transparency value (0 = transparent, 255 = opaque)
            s.fill(pg.Color("blue"))
            screen.blit(s, (col * SQ_SIZE, row * SQ_SIZE))
            for move in validMoves:
                if move.startRow == row and move.startCol == col:
                    endSqr = gameState.board[move.endRow][move.endCol]
                    if endSqr[-1] == ("W" if not gameState.whiteToMove else "B") or move.isEnpassantMove:
                        s.fill(pg.Color("red"))
                    else:
                        s.fill(pg.Color("yellow"))
                    screen.blit(s, (move.endCol * SQ_SIZE, move.endRow * SQ_SIZE))

"""
Function to handle all the graphics of this program
"""

def drawGameState(screen, gameState, validMoves, sqSelected, moveLogFont):
    drawBoard(screen)  #draw squares on the board
    highlightSquares(screen, gameState, validMoves, sqSelected)
    drawPieces(screen, gameState.board)  #draw pieces on the board
    drawMoveLog(screen, gameState, moveLogFont)


"""
Draw the squares
"""

def drawBoard(screen):
    colors = [pg.Color("white"), pg.Color("grey")]
    for row in range(DIMENSION):
        for column in range(DIMENSION):
            color = colors[((row + column) % 2)]
            pg.draw.rect(screen, color, pg.Rect(column * SQ_SIZE, row * SQ_SIZE, SQ_SIZE, SQ_SIZE))

"""
Draw the pieces on the board using the current GameState.board
"""

def drawPieces(screen, board):
    for row in range(DIMENSION):
        for column in range(DIMENSION):
            piece = board[row][column]
            if piece != "--":
                screen.blit(IMAGES[piece], pg.Rect(column * SQ_SIZE, row * SQ_SIZE, SQ_SIZE, SQ_SIZE))

"""
Draw text on the end game screen
"""

def drawEndGameText(screen, text):
    font = pg.font.SysFont("Helvicitca", 32, False, False)
    textObj = font.render(text, 0, pg.Color("black"))
    textLocation = pg.Rect(0, 0, BOARD_WIDTH, BOARD_HEIGHT).move(BOARD_WIDTH // 2 - textObj.get_width() // 2, BOARD_HEIGHT // 2 - textObj.get_height() // 2)
    screen.blit(textObj, textLocation)

"""
Draw the moveLog
"""

def drawMoveLog(screen, gameState, font):
    moveLogRect = pg.Rect(BOARD_WIDTH,0,MOVE_LOG_PANEL_WIDTH,MOVE_LOG_PANEL_HEIGHT)
    pg.draw.rect(screen, pg.Color("black"), moveLogRect)
    moveLog = gameState.moveLog
    moveTexts = moveLog
    padding = 5
    textX = padding
    textY = padding
    movePair = []
    turnCount = 0
    for i in range(len(moveTexts)):
        movePair.append(moveTexts[i].getChessNotation()[1])
        if len(movePair) == 2:
            turnCount += 1
            textObj = font.render(f"{turnCount}) {movePair[0]} {movePair[1]}", True, pg.Color("white"))
            textLocation = moveLogRect.move(textX, textY)
            screen.blit(textObj, textLocation)
            textY += textObj.get_height()
            if turnCount == 36 and i > 2:
                textY = padding
                textX += 70
            movePair = []

"""
Draw the start menu
"""

def draw_start_menu(screen,):
    screen.fill((0, 0, 0))
    font = pg.font.SysFont('arial', 40)
    title = font.render('My Game', True, (255, 255, 255))
    start_button = font.render('Start', True, (255, 255, 255))
    screen.blit(title, (BOARD_WIDTH+MOVE_LOG_PANEL_WIDTH/2 - title.get_width()/2, BOARD_HEIGHT/2 - title.get_height()/2))
    screen.blit(start_button, (BOARD_WIDTH+MOVE_LOG_PANEL_WIDTH/2 - start_button.get_width()/2, BOARD_HEIGHT/2 + start_button.get_height()/2))
    pg.display.update()

if __name__ == '__main__':
    main()
