"""
Handles user input and displays the current game state
"""

import pygame as p
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
        IMAGES[piece] = p.transform.scale(p.image.load("images/" + piece + ".png"), (SQ_SIZE, SQ_SIZE)) #IMAGES["pB"] will return the black pawn image
