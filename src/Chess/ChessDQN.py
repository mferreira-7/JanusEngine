"""
Plan is to use the other three files/classes to get the required information

WHAT DO I DO:
- Pass information in
- Transform it for internal use
- Get results from the selfplay
- Transform results for external use
- Pass information out

WHAT DO I NEED (chess-specific):
- The Agent (DQN chessbot that makes chess moves based on board positions)
- The Environment (The chess game the passes its board states to the agent)
- The State (The positions of each piece on the board at any one point)
- The Possible Actions (All valid moves the bot can make from the current position)
- The Reward Function (A way to evaluate the agent's performance by assigning each move a score)
- The Reward Function II (I could also just evaluate the board before and after the move instead)

THE IDEA:
- Use python-chess to train a model here
- Once the model is at a sufficient standard I can query it with real-time board position from the ChessMain loop
- Use the model to return its chosen move to ChessAI where I can turn it into a Move object and use ChessEngine's makeMove()
- Repeat this through a full game

EXTRAS:
- I could store the model (somehow) at different stages of the training then use it as a kind-of difficulty system.
"""

import torch
import random
import ChessMain, ChessEngine, ChessAI
import numpy as np
import torch.nn as nn
import torch.optim as optim
from collections import deque

ChessMain.main()