"""
Handles user input and displays the current game state
"""

import pygame as pg
import ChessEngine

WIDTH = HEIGHT = 512  #this could be 400
DIMENSION = 8  #chess board is 8x8
SQ_SIZE = HEIGHT // DIMENSION
MAX_FPS = 15  #possible animations
IMAGES = {}

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
    screen = pg.display.set_mode((WIDTH, HEIGHT))
    clock = pg.time.Clock()
    screen.fill(pg.Color('white'))
    gameState = ChessEngine.GameState()
    validMoves = gameState.getValidMoves()
    moveMade = False #debouncer for when a move is made
    loadImages()  #only once
    running = True
    sqSelected = () #tracks the last click of the user (row, col)
    playerClicks = [] #tracks a pair of player clicks [(6,4), (4,4)]
    while running:
        for event in pg.event.get():
            if event.type == pg.QUIT: #quit handler
                running = False
            elif event.type == pg.MOUSEBUTTONDOWN: #mouse handler
                location = pg.mouse.get_pos() #(x, y) position of mouse
                col = location[0] // SQ_SIZE
                row = location[1] // SQ_SIZE
                if sqSelected == (row, col): #user clicked the same sq twice
                    sqSelected = () #deselect
                    playerClicks = [] #clear clicks
                else:
                    sqSelected = (row, col)
                    playerClicks.append(sqSelected)
                if len(playerClicks) == 2: #2nd click
                    move = ChessEngine.Move(playerClicks[0], playerClicks[1], gameState.board)
                    print(move.getChessNotation())
                    for i in range(len(validMoves)):
                        if move == validMoves[i]:
                            gameState.makeMove(validMoves[i])
                            moveMade = True
                            sqSelected = ()  # reset clicks
                            playerClicks = []
                    if not moveMade:
                        playerClicks = [sqSelected]
            elif event.type == pg.KEYDOWN: #key handler
                if event.key == pg.K_z:
                    gameState.undoMove()
                    moveMade = True
        if moveMade:
            validMoves = gameState.getValidMoves()
            moveMade = False
        drawGameState(screen, gameState)
        clock.tick(MAX_FPS)
        pg.display.flip()

"""
Function to handle all the graphics of this program
"""

def drawGameState(screen, gameState):
    drawBoard(screen)  #draw squares on the board
    drawPieces(screen, gameState.board)  #draw pieces on the board

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

if __name__ == '__main__':
    main()
